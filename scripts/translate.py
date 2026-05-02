#!/usr/bin/env python3
"""
Translate Chinese Markdown sources to English using the OpenAI API.

For each `*.md` file at the repo root and in `pages/` (excluding files listed in
`.blog-syncignore` and any file already ending in `.en.md`), this script:

  1. Parses YAML front matter and Markdown body.
  2. Computes a SHA-256 hash of the body bytes (front matter is excluded so
     that adding a `translationKey` to the source does not invalidate the
     cache).
  3. Looks for a sibling `<stem>.en.md`. If it exists and its `source_hash`
     and `translationKey` match the source, the file is treated as cached and
     skipped.
  4. Otherwise, calls the OpenAI Chat Completions API (gpt-4o, JSON mode) to
     translate the title, body, tags, and to generate a stable kebab-case
     English slug.
  5. Writes `<stem>.en.md` with English front matter (including
     `translationKey`, `slug`, and `source_hash`) and translated body.
  6. If the source file did not have `translationKey`, adds it (= the slug)
     and writes the source back, preserving everything else byte-for-byte.

After the per-file pass, a cleanup pass deletes any orphan `*.en.md` whose
source `*.md` no longer exists.

CLI:
  --dry-run               Plan only; no API calls and no writes.
  --changed-only "a,b,c"  Restrict the translation pass to these source files
                          (paths relative to the repo root). Cleanup always
                          runs.
  --verbose               Log a decision for every file considered.

Environment:
  OPENAI_API_KEY  Required for non-dry-run runs. (In CI the workflow maps the
                  `BLOG_TRANSLATOR` secret to this variable.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = [REPO_ROOT, REPO_ROOT / "pages"]
SYNCIGNORE_PATH = REPO_ROOT / ".blog-syncignore"

OPENAI_MODEL = "gpt-4o"
OPENAI_TIMEOUT_SECS = 60
OPENAI_MAX_ATTEMPTS = 3

# Chunking thresholds (characters). The gpt-4o output cap is 16,384 tokens;
# for Chinese -> English translation the output token count tends to be
# similar in magnitude to the input character count, so we stay conservative.
CHUNK_BODY_THRESHOLD_CHARS = 8000  # bodies larger than this get chunked
CHUNK_MAX_CHARS = 5000             # cap per chunk before emitting

# Front-matter key ordering for English outputs and source rewrites — keep
# diffs stable.
EN_FRONTMATTER_ORDER = [
    "title",
    "date",
    "draft",
    "tags",
    "translationKey",
    "slug",
    "source_hash",
]

logger = logging.getLogger("translate")


# --------------------------------------------------------------------------- #
# Front-matter parsing
# --------------------------------------------------------------------------- #

FRONT_MATTER_RE = re.compile(
    rb"^---\r?\n(.*?)(?:\r?\n)---\r?\n",
    re.DOTALL,
)


@dataclass
class ParsedDoc:
    front_matter: dict
    body: bytes  # raw body bytes (everything after closing ---\n)
    raw: bytes


def parse_doc(path: Path) -> ParsedDoc | None:
    raw = path.read_bytes()
    m = FRONT_MATTER_RE.match(raw)
    if not m:
        logger.warning("no front matter in %s; skipping", path)
        return None
    fm_text = m.group(1).decode("utf-8")
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        logger.warning("invalid YAML in %s: %s; skipping", path, exc)
        return None
    if not isinstance(fm, dict):
        logger.warning("front matter in %s is not a mapping; skipping", path)
        return None
    body = raw[m.end():]
    return ParsedDoc(front_matter=fm, body=body, raw=raw)


def body_sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


# --------------------------------------------------------------------------- #
# Front-matter rendering
# --------------------------------------------------------------------------- #

def _yaml_dump_ordered(fm: dict) -> str:
    """Dump a dict to YAML using a fixed key order for known keys, then
    falling back to insertion order. Ensures stable diffs."""
    ordered: list[tuple[str, object]] = []
    seen: set[str] = set()
    for key in EN_FRONTMATTER_ORDER:
        if key in fm:
            ordered.append((key, fm[key]))
            seen.add(key)
    for key, value in fm.items():
        if key not in seen:
            ordered.append((key, value))

    # yaml.safe_dump doesn't preserve list ordering arguments; build chunks per
    # key to keep order deterministic.
    parts = []
    for key, value in ordered:
        chunk = yaml.safe_dump(
            {key: value},
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=10_000,
        )
        parts.append(chunk)
    return "".join(parts)


def write_doc(path: Path, fm: dict, body: bytes) -> None:
    fm_text = _yaml_dump_ordered(fm).rstrip("\n")
    out = b"---\n" + fm_text.encode("utf-8") + b"\n---\n" + body
    # Normalize CRLF to LF in the front matter region; body is preserved.
    path.write_bytes(out)


# Top-level YAML key match within the front matter block (multiline).
_TOP_LEVEL_KEY_RE_TEMPLATE = r"(?m)^{key}\s*:"


def insert_translation_key_in_source(path: Path, slug: str) -> bool:
    """Insert `translationKey: <slug>` into the source file's front matter
    without re-serializing it. Preserves all other bytes verbatim.

    Returns True if the file was modified, False if `translationKey` was
    already present (or front matter could not be located).
    """
    raw = path.read_bytes()
    m = FRONT_MATTER_RE.match(raw)
    if not m:
        return False
    fm_bytes = m.group(1)
    fm_text = fm_bytes.decode("utf-8")
    # Only check within the front matter block — never the body.
    if re.search(_TOP_LEVEL_KEY_RE_TEMPLATE.format(key="translationKey"), fm_text):
        return False

    # The front matter block matched is `---\n<fm_bytes>\n---\n` (where the
    # trailing `\n---\n` is part of the regex but not the captured group).
    # We want to insert a new line `translationKey: <slug>\n` immediately
    # before the closing `---`. Locate the start of the closing fence in the
    # original bytes by counting from the end of group(1).
    fm_end = m.end(1)  # byte offset just after the captured fm content
    # The next bytes are `\r?\n---\r?\n`. Find the start of the closing `---`.
    # Group(1) excludes the trailing newline before `---`, so we step past
    # that newline to find the `---` start.
    closing_fence_start = fm_end
    # Skip exactly one newline (\r?\n) — the regex `(?:\r?\n)---\r?\n` matched
    # one newline before the fence.
    if raw[closing_fence_start:closing_fence_start + 2] == b"\r\n":
        closing_fence_start += 2
    elif raw[closing_fence_start:closing_fence_start + 1] in (b"\n", b"\r"):
        closing_fence_start += 1
    # closing_fence_start now points at `---`.
    insert = f"translationKey: {slug}\n".encode("utf-8")
    new_raw = raw[:closing_fence_start] + insert + raw[closing_fence_start:]
    path.write_bytes(new_raw)
    return True


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #

def load_syncignore() -> set[str]:
    if not SYNCIGNORE_PATH.exists():
        return set()
    names: set[str] = set()
    for line in SYNCIGNORE_PATH.read_text(encoding="utf-8").splitlines():
        s = line.split("#", 1)[0].strip()
        if s:
            names.add(s)
    return names


def is_translation_output(path: Path) -> bool:
    return path.name.endswith(".en.md")


def english_path_for(source: Path) -> Path:
    # foo.md -> foo.en.md (drop only the trailing .md)
    return source.with_name(source.stem + ".en.md")


def discover_sources(ignore_names: set[str]) -> list[Path]:
    found: list[Path] = []
    for d in SCAN_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if is_translation_output(p):
                continue
            if p.name in ignore_names:
                continue
            found.append(p)
    return found


def discover_translations() -> list[Path]:
    found: list[Path] = []
    for d in SCAN_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.en.md")):
            found.append(p)
    return found


def filter_changed(sources: list[Path], changed: list[Path] | None) -> list[Path]:
    if changed is None:
        return sources
    changed_resolved = {p.resolve() for p in changed}
    return [p for p in sources if p.resolve() in changed_resolved]


# --------------------------------------------------------------------------- #
# OpenAI translation
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT = """You are a professional bilingual (Chinese -> English) translator for a personal blog whose author writes about design, faith, family, and software. Translate the provided Markdown post into natural, idiomatic English suitable for publication.

Rules:
- Preserve all Markdown syntax exactly: headings, lists, code fences, inline code, blockquotes, tables, footnotes, and link/image syntax.
- Translate visible link text and image alt text, but DO NOT alter URLs.
- Translate the title to a natural, concise English title.
- Translate each tag to its English equivalent, lowercase, ASCII when possible.
- Generate a kebab-case English slug from the translated title: lowercase ASCII, words separated by single hyphens, no leading/trailing hyphens, max ~60 characters. Avoid years/dates unless they are essential to the title's meaning. The slug must be stable for the same title.
- Keep proper nouns and brand names (people's names, company names like Apple, Liulishuo, Herman Miller) in their conventional English form.
- Preserve original paragraph breaks. Do not add or remove sections.
- Do not add a translator's note or any meta commentary.

Return ONLY a JSON object with exactly these keys: {"title": string, "body": string, "tags": [string, ...], "slug": string}. The "body" must be the translated Markdown body (no surrounding front matter, no code-fence wrapper)."""


# Used when chunking: title/tags/slug come from one small call, then each
# body chunk is translated by itself with this prompt.
CHUNK_SYSTEM_PROMPT = """You are a professional bilingual (Chinese -> English) translator. You will be given ONE chunk of a longer Markdown blog post. Translate this chunk into natural, idiomatic English.

Rules:
- Preserve all Markdown syntax exactly: headings, lists, code fences, inline code, blockquotes, tables, footnotes, and link/image syntax.
- Translate visible link text and image alt text, but DO NOT alter URLs.
- Keep proper nouns and brand names in their conventional English form.
- Preserve paragraph breaks. Do not add or remove paragraphs.
- Do NOT add any framing text, headings, prefaces, "Translation:" labels, code fences, or meta commentary. Output only the translated Markdown for this chunk.

Return ONLY a JSON object with exactly one key: {"body": string}. The "body" is the translated Markdown for this chunk."""


def _build_user_message(title: str, tags: list, body_text: str) -> str:
    tags_repr = json.dumps(tags or [], ensure_ascii=False)
    return (
        "Translate this blog post.\n\n"
        f"TITLE: {title}\n"
        f"TAGS: {tags_repr}\n"
        "BODY:\n"
        "<<<BODY_START>>>\n"
        f"{body_text}\n"
        "<<<BODY_END>>>\n"
    )


class TruncatedResponseError(RuntimeError):
    """Raised when the OpenAI response was cut off (finish_reason='length').

    Caught by the per-file try/except so the file is reported as failed and
    skipped — we do NOT want to write a half-translated `.en.md`.
    """


def _chat_with_retries(client, system_prompt: str, user_content: str) -> str:
    """Run a chat completion with retries. Returns the message content
    string. Raises TruncatedResponseError if finish_reason == 'length'."""
    from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

    last_exc: Exception | None = None
    for attempt in range(1, OPENAI_MAX_ATTEMPTS + 1):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                timeout=OPENAI_TIMEOUT_SECS,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
            )
            choice = resp.choices[0]
            finish = getattr(choice, "finish_reason", None)
            if finish == "length":
                # Don't retry — a longer attempt won't fit either. Bubble up
                # so the per-file handler marks the file as failed.
                raise TruncatedResponseError(
                    "OpenAI response truncated (finish_reason='length'); "
                    "chunk too large for the model's output cap"
                )
            content = choice.message.content or ""
            # Validate JSON parses before returning so retries can recover
            # from transient malformed responses.
            json.loads(content)
            return content
        except TruncatedResponseError:
            raise
        except (APITimeoutError, APIConnectionError, RateLimitError) as exc:
            last_exc = exc
        except APIStatusError as exc:
            status = getattr(exc, "status_code", None)
            if status in (429, 500, 502, 503, 504):
                last_exc = exc
            else:
                raise
        except json.JSONDecodeError as exc:
            last_exc = exc
        if attempt < OPENAI_MAX_ATTEMPTS:
            backoff = (2 ** (attempt - 1)) + random.random()
            logger.warning(
                "OpenAI call attempt %d failed (%s); retrying in %.1fs",
                attempt, type(last_exc).__name__, backoff,
            )
            time.sleep(backoff)
    assert last_exc is not None
    raise last_exc


def call_openai(client, title: str, tags: list, body_text: str) -> dict:
    """Call OpenAI with retries; return parsed JSON dict.

    Raises TruncatedResponseError if the model's response was cut off."""
    content = _chat_with_retries(
        client,
        SYSTEM_PROMPT,
        _build_user_message(title, tags, body_text),
    )
    return json.loads(content)


def call_openai_chunk(client, body_chunk: str) -> str:
    """Translate a single body chunk. Returns translated Markdown text.

    Raises TruncatedResponseError if the chunk's response was cut off."""
    user_content = (
        "Translate this Markdown chunk, preserving structure. "
        "Do not add framing text.\n\n"
        "<<<CHUNK_START>>>\n"
        f"{body_chunk}\n"
        "<<<CHUNK_END>>>\n"
    )
    content = _chat_with_retries(client, CHUNK_SYSTEM_PROMPT, user_content)
    data = json.loads(content)
    body = data.get("body")
    if not isinstance(body, str) or not body.strip():
        raise RuntimeError("chunk response missing 'body' field")
    return body


# --------------------------------------------------------------------------- #
# Body chunking
# --------------------------------------------------------------------------- #

_PARAGRAPH_SPLIT_RE = re.compile(r"\n{2,}")


def split_body_into_chunks(body_text: str, max_chars: int = CHUNK_MAX_CHARS) -> list[str]:
    """Greedy paragraph-aware splitter.

    Paragraphs are separated by one or more blank lines (`\\n\\n+`). We
    accumulate paragraphs until adding the next one would exceed `max_chars`,
    then emit. A single paragraph larger than `max_chars` is emitted on its
    own (the model has to handle it; if THAT truncates, the file is failed).
    """
    paragraphs = _PARAGRAPH_SPLIT_RE.split(body_text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    sep = "\n\n"
    sep_len = len(sep)
    for para in paragraphs:
        if not current:
            current.append(para)
            current_len = len(para)
            continue
        added = sep_len + len(para)
        if current_len + added > max_chars:
            chunks.append(sep.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += added
    if current:
        chunks.append(sep.join(current))
    return chunks


# --------------------------------------------------------------------------- #
# Slug helpers
# --------------------------------------------------------------------------- #

SLUG_BAD_RE = re.compile(r"[^a-z0-9]+")


def normalize_slug(slug: str) -> str:
    s = (slug or "").strip().lower()
    s = SLUG_BAD_RE.sub("-", s)
    s = s.strip("-")
    if len(s) > 60:
        s = s[:60].rstrip("-")
    return s


def existing_en_slugs(exclude: Path | None = None) -> set[str]:
    """Collect every `slug` value found in any existing `*.en.md` front
    matter, optionally excluding one path (the file we're about to write)."""
    slugs: set[str] = set()
    for en_path in discover_translations():
        if exclude is not None and en_path.resolve() == exclude.resolve():
            continue
        en_doc = parse_doc(en_path)
        if en_doc is None:
            continue
        s = en_doc.front_matter.get("slug")
        if isinstance(s, str) and s:
            slugs.add(s)
    return slugs


def disambiguate_slug(slug: str, taken: set[str]) -> str:
    """If `slug` collides with `taken`, append `-2`, `-3`, ... until unique."""
    if slug not in taken:
        return slug
    n = 2
    while True:
        candidate = f"{slug}-{n}"
        if candidate not in taken:
            return candidate
        n += 1


# --------------------------------------------------------------------------- #
# Per-file processing
# --------------------------------------------------------------------------- #

@dataclass
class Counts:
    translated: int = 0
    cached: int = 0
    deleted: int = 0
    skipped: int = 0
    failed: int = 0
    failed_files: list = field(default_factory=list)


def needs_translation(source_doc: ParsedDoc, en_path: Path) -> tuple[bool, str]:
    """Return (needs, reason)."""
    if not en_path.exists():
        return True, "no english output yet"
    en_doc = parse_doc(en_path)
    if en_doc is None:
        return True, "english output unparseable; will regenerate"
    body_hash = body_sha256(source_doc.body)
    en_hash = en_doc.front_matter.get("source_hash")
    if en_hash != body_hash:
        return True, f"body hash changed ({en_hash} != {body_hash})"
    src_key = source_doc.front_matter.get("translationKey")
    en_key = en_doc.front_matter.get("translationKey")
    if src_key and en_key and src_key != en_key:
        return True, f"translationKey mismatch (src={src_key} en={en_key})"
    return False, "cached"


def process_one(
    source: Path,
    client,
    counts: Counts,
    dry_run: bool,
    verbose: bool,
) -> None:
    rel = source.relative_to(REPO_ROOT)
    doc = parse_doc(source)
    if doc is None:
        counts.skipped += 1
        return

    en_path = english_path_for(source)
    needs, reason = needs_translation(doc, en_path)
    if not needs:
        counts.cached += 1
        if verbose:
            logger.info("CACHED  %s (%s)", rel, reason)
        return

    if verbose:
        logger.info("TRANSLATE %s (%s)", rel, reason)

    if dry_run:
        counts.translated += 1  # report what *would* happen
        return

    title = str(doc.front_matter.get("title") or source.stem)
    raw_tags = doc.front_matter.get("tags") or []
    if not isinstance(raw_tags, list):
        raw_tags = []
    body_text = doc.body.decode("utf-8")

    use_chunking = len(body_text) > CHUNK_BODY_THRESHOLD_CHARS

    try:
        if use_chunking:
            chunks = split_body_into_chunks(body_text, CHUNK_MAX_CHARS)
            total = len(chunks)
            if verbose:
                logger.info(
                    "CHUNKED %s (body=%d chars -> %d chunk(s))",
                    rel, len(body_text), total,
                )
            # Translate title/tags/slug ONCE with a stub body for context.
            stub_body = "(See chunked translation below.)"
            meta = call_openai(client, title, raw_tags, stub_body)
            translated_chunks: list[str] = []
            for i, chunk in enumerate(chunks, start=1):
                if verbose:
                    logger.info(
                        "[CHUNK %d/%d] translating %d chars",
                        i, total, len(chunk),
                    )
                translated_chunks.append(call_openai_chunk(client, chunk))
            result = {
                "title": meta.get("title", ""),
                "body": "\n\n".join(translated_chunks),
                "tags": meta.get("tags", []),
                "slug": meta.get("slug", ""),
            }
        else:
            result = call_openai(client, title, raw_tags, body_text)
    except Exception as exc:
        logger.error("FAILED  %s: %s", rel, exc)
        counts.failed += 1
        counts.failed_files.append(rel)
        return

    en_title = (result.get("title") or "").strip()
    en_body = result.get("body") or ""
    en_tags = result.get("tags") or []
    if not isinstance(en_tags, list):
        en_tags = []
    en_tags = [str(t).strip().lower() for t in en_tags if str(t).strip()]
    slug = normalize_slug(str(result.get("slug") or ""))
    if not en_title or not en_body or not slug:
        logger.error(
            "FAILED  %s: model response missing required fields (title=%r slug=%r body_len=%d)",
            rel, en_title, slug, len(en_body),
        )
        counts.failed += 1
        counts.failed_files.append(rel)
        return

    # Disambiguate against any existing *.en.md slugs so URLs don't collide.
    taken = existing_en_slugs(exclude=en_path)
    final_slug = disambiguate_slug(slug, taken)
    if final_slug != slug:
        logger.info(
            "SLUG    %s: %r already taken, using %r", rel, slug, final_slug,
        )
        slug = final_slug

    body_hash = body_sha256(doc.body)

    en_fm = {
        "title": en_title,
        "date": doc.front_matter.get("date"),
        "draft": bool(doc.front_matter.get("draft", False)),
        "tags": en_tags,
        "translationKey": slug,
        "slug": slug,
        "source_hash": body_hash,
    }
    # Drop None values (e.g. missing date).
    en_fm = {k: v for k, v in en_fm.items() if v is not None}

    en_body_bytes = en_body.encode("utf-8")
    if not en_body_bytes.startswith(b"\n"):
        en_body_bytes = b"\n" + en_body_bytes
    if not en_body_bytes.endswith(b"\n"):
        en_body_bytes = en_body_bytes + b"\n"
    write_doc(en_path, en_fm, en_body_bytes)
    logger.info("WROTE   %s", en_path.relative_to(REPO_ROOT))

    # Add translationKey to the source if missing — surgical insert that
    # preserves the rest of the front matter byte-for-byte (no re-serialize).
    if not doc.front_matter.get("translationKey"):
        if insert_translation_key_in_source(source, slug):
            logger.info("UPDATED %s (added translationKey=%s)", rel, slug)

    counts.translated += 1


# --------------------------------------------------------------------------- #
# Cleanup pass
# --------------------------------------------------------------------------- #

def cleanup_orphans(counts: Counts, dry_run: bool, verbose: bool) -> None:
    for en_path in discover_translations():
        # foo.en.md -> stem is "foo.en"; source is "foo.md"
        stem = en_path.name[: -len(".en.md")]
        source = en_path.with_name(stem + ".md")
        if source.exists():
            continue
        rel = en_path.relative_to(REPO_ROOT)
        if dry_run:
            logger.info("WOULD DELETE %s (orphan)", rel)
        else:
            en_path.unlink()
            logger.info("DELETED %s (orphan)", rel)
        counts.deleted += 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_changed_only(value: str | None) -> list[Path] | None:
    if value is None:
        return None
    raw = value.strip()
    if not raw:
        return None
    paths: list[Path] = []
    for piece in raw.replace("\n", ",").split(","):
        s = piece.strip()
        if not s:
            continue
        p = (REPO_ROOT / s).resolve()
        paths.append(p)
    return paths


def filter_to_eligible_sources(
    candidates: list[Path],
    ignore_names: set[str],
) -> list[Path]:
    """Apply the same eligibility rules used during full discovery."""
    eligible: list[Path] = []
    for p in candidates:
        if not p.exists() or not p.is_file():
            continue
        if p.suffix != ".md":
            continue
        if is_translation_output(p):
            continue
        if p.name in ignore_names:
            continue
        try:
            rel = p.resolve().relative_to(REPO_ROOT)
        except ValueError:
            continue
        # Only files at repo root or in pages/.
        parent = rel.parent
        if str(parent) not in ("", ".", "pages"):
            continue
        eligible.append(p)
    return eligible


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="plan only; no writes or API calls")
    ap.add_argument(
        "--changed-only",
        default=None,
        help="comma-separated source paths (relative to repo root) to consider; "
             "if omitted, scan everything",
    )
    ap.add_argument("--verbose", action="store_true", help="log per-file decisions")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    ignore_names = load_syncignore()
    all_sources = discover_sources(ignore_names)
    changed_paths = parse_changed_only(args.changed_only)
    if changed_paths is not None:
        sources = filter_to_eligible_sources(changed_paths, ignore_names)
        logger.info(
            "changed-only: %d candidate(s) -> %d eligible source(s)",
            len(changed_paths), len(sources),
        )
    else:
        sources = all_sources
        logger.info("scanning all sources: %d file(s)", len(sources))

    counts = Counts()

    client = None
    if not args.dry_run:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not set; refusing to run without --dry-run")
            return 2
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

    for src in sources:
        try:
            process_one(src, client, counts, args.dry_run, args.verbose)
        except Exception as exc:  # pragma: no cover - last-resort guard
            counts.failed += 1
            counts.failed_files.append(str(src.name))
            logger.exception("UNEXPECTED FAILURE on %s: %s", src, exc)

    # Cleanup pass always runs.
    cleanup_orphans(counts, args.dry_run, args.verbose)

    logger.info(
        "summary: translated=%d cached=%d deleted=%d skipped=%d failed=%d (dry_run=%s)",
        counts.translated, counts.cached, counts.deleted,
        counts.skipped, counts.failed, args.dry_run,
    )

    failures_path = os.environ.get("TRANSLATE_FAILURES_FILE")
    if failures_path and counts.failed_files:
        try:
            with open(failures_path, "w", encoding="utf-8") as fh:
                for name in counts.failed_files:
                    fh.write(name + "\n")
        except OSError as exc:
            logger.warning("could not write failures file %s: %s", failures_path, exc)

    if counts.translated == 0 and counts.cached == 0 and counts.deleted == 0 and counts.failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

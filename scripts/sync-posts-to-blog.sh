#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR=${1:?source dir required}
TARGET_DIR=${2:?target dir required}
IGNORE_FILE=${3:-}

DESIRED_LIST=$(mktemp)
NORMALIZED_IGNORE=$(mktemp)
trap 'rm -f "$DESIRED_LIST" "$NORMALIZED_IGNORE"' EXIT

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

if [[ -n "$IGNORE_FILE" && -f "$IGNORE_FILE" ]]; then
  while IFS= read -r raw || [[ -n "$raw" ]]; do
    line=$(trim "${raw%%#*}")
    [[ -z "$line" ]] && continue
    printf '%s\n' "$line" >> "$NORMALIZED_IGNORE"
  done < "$IGNORE_FILE"
fi

should_ignore() {
  local name="$1"
  [[ -s "$NORMALIZED_IGNORE" ]] && grep -Fqx -- "$name" "$NORMALIZED_IGNORE"
}

mkdir -p "$TARGET_DIR"

while IFS= read -r -d '' path; do
  name=$(basename "$path")
  if should_ignore "$name"; then
    continue
  fi

  printf '%s\n' "$name" >> "$DESIRED_LIST"
  cp "$path" "$TARGET_DIR/$name"
done < <(find "$SOURCE_DIR" -maxdepth 1 -type f -name '*.md' -print0)

while IFS= read -r -d '' path; do
  name=$(basename "$path")
  if ! grep -Fqx -- "$name" "$DESIRED_LIST"; then
    rm -f "$path"
  fi
done < <(find "$TARGET_DIR" -maxdepth 1 -type f -name '*.md' -print0)

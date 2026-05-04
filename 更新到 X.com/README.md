# 更新到 X.com — 自动化发布队列

Diff 的 X.com 双语账号内容仓库。**你不写 tweet，Routine 自动从你的 Obsidian vault 生成**。

---

## 怎么用（每天 3 分钟）

### 1. 打开界面

双击 `index.html` 在浏览器中打开。

> ⚠️ 如果浏览器阻止 `file://` 加载（Chrome 偶尔会），改用本地 server：
> ```bash
> cd "更新到 X.com"
> python3 -m http.server 8765
> ```
> 然后访问 http://localhost:8765

### 2. 看今天要发什么

默认显示「📅 今天」tab，左边中文、右边英文。

每张卡片显示：
- 排程时间（Mon May 4, 07:30 · in 2h）
- 内容支柱（building-in-public 等）
- tweet 全文
- 字符数
- 三个按钮

### 3. 发布

**单条 tweet**：
1. 检查内容（Routine 生成的，可能需要小修）
2. 点 `🚀 Open in X` → X.com 打开 compose 框，文字已填好
3. 改好后点发布
4. 回到 UI 点 `✓ Mark sent`

**长 thread**：
1. 点首条的 `🚀 Open in X`
2. 在 X 上发出首条
3. 点 X 的 + 添加第 2 条
4. 回到 UI，点第 2 条的 `📋 Copy 2/15`
5. 在 X 中粘贴 → 重复直到最后
6. 全部发完，回 UI 点 `✓ Mark sent`

### 4. 批量浏览

Tab 切换看：
- 📅 今天 — 今天该发的
- 📆 本周 — 本周一到周日
- 🗓 本月 — 本月所有
- 📚 全部 — 队列里所有
- 📤 未发 — 排过日期但还没标记为已发

---

## 内容从哪里来？

完全自动。Claude Code 的 Routine 按计划运行，扫描你的 Obsidian vault：

```
Documents/
├── diff-blog-source/      ← 已发布博客（高密度素材）
└── notes/Drafts/           ← 草稿（语音转写、半成品）
```

按 `routine/value-criteria.md` 打分（1–10），按 `routine/privacy-filter.md` 过滤敏感内容，按 `routine/tweet-format-rules.md` 加上你 writter 项目里 polisher skill 的语调，自动生成中英文 tweet 写入 `tweets.js`。

**你需要做的**：写你平时的博客 / 草稿（你本来就在做的事）。

**你不需要做的**：写 tweet。

---

## Routine 怎么设置

### 引用 polisher skill 的方式

Routine 不复制 skill。每次运行**直接读你 writter 项目的绝对路径**：

```
/Users/diffwang/NWA/writter/.agents/skills/diff-article-polisher/
  ├── SKILL.md
  └── references/
      ├── style-profile.md
      └── editing-rules.md
```

你在 writter 里更新 skill，Routine 下次运行自动用新版。零同步成本。

> ⚠️ 如果 writter 项目移动位置，需要更新 `routine/PROMPT.md` 顶部的两条路径。

### 第一次设置（用 schedule 技能）

在 Claude Code 里运行：

```
/schedule
```

按提示创建一个 routine：
- **Schedule**: `0 6 * * 0`（每周日 6:00 Dallas time）
- **Prompt**: 让 Claude 读 `routine/PROMPT.md` 然后执行
- **Working directory**: `更新到 X.com/`

模板 prompt（粘进 schedule 的 prompt 字段）：

```
你是 Diff 的 tweet 生成 Routine。请按以下文件执行：

1. 读 /Users/diffwang/NWA/writter/.agents/skills/diff-article-polisher/SKILL.md
2. 读 /Users/diffwang/NWA/writter/.agents/skills/diff-article-polisher/references/style-profile.md
3. 读 当前目录的 routine/PROMPT.md（这是你的主指令）
4. 严格按 routine/PROMPT.md 的 7 个 Step 执行
5. 完成后返回 ≤150 字的总结

不要询问 Diff，直接执行。
完成后写入 tweets.js 和 routine/logs/{date}.md。
```

### 调整频率

- **每周一次**（推荐起步）：`0 6 * * 0`
- **每周两次**：`0 6 * * 0,3`（周日和周三）
- **每天**：`0 6 * * *`（成本会高，等磨合稳定再切）

### 暂停 / 删除

```
/schedule list      # 查看所有 routine
/schedule pause <id>
/schedule delete <id>
```

---

## 文件结构

```
更新到 X.com/
├── index.html            ← 你打开的 UI
├── tweets.js             ← 数据：Routine 写入，UI 读取
├── source-index.json     ← Routine 用，记录已处理文件的 mtime
├── README.md             ← 本文件
├── routine/
│   ├── PROMPT.md         ← Routine 主指令（7 个 Step）
│   ├── value-criteria.md ← 价值评分标准
│   ├── tweet-format-rules.md ← Tweet 写作规则
│   ├── privacy-filter.md ← 隐私过滤规则
│   └── logs/             ← 每次运行的日志
└── threads/              ← 长 thread 的 markdown 备份
```

---

## 已发布状态

存在浏览器 localStorage（key: `pub:{tweet_id}`）。
- ✅ 跨 tab、跨刷新保留
- ❌ 换浏览器 / 清缓存 / 换设备会丢

如果想跨设备同步状态，下个版本可加：把 sent 状态写回 tweets.js 的 `published_at` 字段。说一声就做。

---

## 如果出问题

### UI 显示空白
1. 检查 `tweets.js` 是否存在且语法正确（必须以 `window.TWEETS_DATA = ` 开头）
2. 浏览器 DevTools → Console 看错误
3. 如果是 CORS / file:// 问题，用 `python3 -m http.server`

### Routine 没生成新内容
1. 看 `routine/logs/{最近日期}.md`
2. 检查 source-index.json 是否被正确更新
3. 确认 polisher skill 路径还存在

### 内容不像 Diff 写的
- 看 routine/PROMPT.md 是否被改过
- 在 writter 项目里更新 polisher skill 的 style-profile.md
- 单独跑一次 routine 验证新效果

### 想临时屏蔽某篇文章
- 给文章 frontmatter 加 `tags: [private]`
- 或在 source-index.json 里手动加 `"skipped": "manual"`

---

## 设计原则

这个系统的核心假设是：**你应该花时间写博客和做产品，不应该花时间写 tweet**。

如果某天你发现自己在 UI 里大改 tweet —— 说明 Routine 的规则需要调整，去更新 routine/*.md，而不是改 tweets.js。

如果某条 tweet 让你觉得"这话不像我说的" —— 在 writter 项目更新 polisher skill 的 style-profile.md，下次 Routine 跑的时候就修正了。

工具应该越用越懂你，而不是越用越累你。

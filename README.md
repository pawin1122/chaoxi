<h1 align="center">chaoxi</h1>

<p align="center">
  巨潮网 A 股上市公司公告数据获取 CLI 工具<br/>
  查询 · 下载 PDF · 提取 Markdown — 一条命令搞定
</p>

<p align="center">
  <a href="https://pypi.org/project/chaoxi/"><img src="https://img.shields.io/badge/pypi-v0.2.0-blue.svg" alt="PyPI"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+"></a>
  <a href="https://github.com/pawin1122/chaoxi/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License"></a>
</p>

---

## 📑 目录

- [⚡ 快速开始](#快速开始)
- [✨ 特性](#特性)
- [📦 安装](#安装)
- [🔍 查询](#查询)
- [📥 下载 PDF](#下载-pdf)
- [📝 提取 Markdown](#提取-markdown)
- [📊 输出](#输出)
- [🔧 管理](#管理)
- [📋 参数速查](#参数速查)
- [⚙️ 配置](#配置)
- [📁 输出结构](#输出结构)
- [🙏 致谢](#致谢)

---

## ⚡ 快速开始

```bash
# 查公告
chaoxi --codes 000001

# 下载回购相关 PDF
chaoxi --codes 000001 --keyword 回购 --download -y

# 下载年报并提取 Markdown
chaoxi --codes 601998 --categories 年报 --extract -y
```

[📖 完整使用手册 →](doc/usage.md)

---

## ✨ 特性

- **六维度查询** — 股票代码 · 日期 · 分类 · 板块 · 行业 · 关键词自由组合
- **批量下载** — 异步并发下载 PDF，断点续传，魔数校验，`.part` 原子写入
- **Markdown 提取** — 基于 [pdf-inspector](https://github.com/firecrawl/pdf-inspector) 高性能引擎，PDF 一键转结构化文档
- **Rich 终端输出** — 彩色表格 · 实时进度条 · 四态提取图标（✅ ⚠️ ❌）
- **完善管理** — 日志查看 · 过期数据清理 · API 调试工具

---

## 📦 安装

**前置要求**：Python 3.12+ · [uv](https://docs.astral.sh/uv/) 包管理器

```bash
# 全局安装（推荐）
git clone https://github.com/pawin1122/chaoxi.git
cd chaoxi
uv tool install .
chaoxi --version
```

<details>
<summary>其他安装方式</summary>

**开发安装**（项目目录内使用 `uv run`）：

```bash
git clone https://github.com/pawin1122/chaoxi.git
cd chaoxi
uv sync
uv run chaoxi --help
```

**tar.gz 发行包**：

```bash
tar xzf chaoxi-v0.2.0.tar.gz
cd chaoxi-v0.2.0
uv tool install .    # 全局安装
# 或
uv sync              # 开发安装
```

**升级**：

```bash
cd chaoxi
git pull
uv tool install .
```

</details>

<details>
<summary>AI 编码助手 Skills 安装</summary>

Skill 文件**不包含在安装包内**，需手动复制：

| 助手 | 源文件 | 安装位置 |
|---|---|---|
| OpenCode | `skills/opencode/chaoxi/SKILL.md` | `.opencode/skills/chaoxi/SKILL.md` |
| Claude Code | `skills/claude-code/chaoxi.md` | 按 Claude Code skill 规范存放 |
| Codex | `skills/codex/chaoxi.md` | 按 Codex skill 规范存放 |
| Pi Agent | `skills/pi-agent/chaoxi.md` | 按 Pi Agent skill 规范存放 |

[Skills 目录 →](https://github.com/pawin1122/chaoxi/tree/main/skills)

</details>

---

## 🔍 查询

```bash
# 按股票
chaoxi --codes 000001,600519

# 按日期
chaoxi --start 2026-01-01 --end 2026-06-30

# 按分类（26 类中文名）
chaoxi --categories 年报 --start 2026-01-01

# 按板块
chaoxi --board 创业板 --categories 业绩预告

# 按关键词（标题精确匹配）
chaoxi --keyword 回购

# 组合查询
chaoxi --codes 000001 --keyword 分红 --start 2026-01-01 --end 2026-06-30
```

---

## 📥 下载 PDF

```bash
chaoxi --codes 000001 --download              # 下载（>50 个弹确认）
chaoxi --codes 000001 --download -y           # 跳过确认
chaoxi --codes 000001 --download -y -d ./pdfs # 指定目录
```

---

## 📝 提取 Markdown

`--extract` 隐含 `--download`，下载后自动批量转 Markdown。

```bash
chaoxi --codes 601998 --categories 年报 --extract -y
```

提取后在 `md/` 目录生成 Markdown 文件，终端显示四态结果：

| 状态 | 图标 | 含义 |
|---|---|---|
| 成功 | ✅ | 文本完整提取 |
| 部分 | ⚠️ N页 | 部分页面有乱码 |
| 扫描件 | ❌ | 扫描版 PDF 无法提取文字 |
| 错误 | ❌ | 提取过程异常 |

---

## 📊 输出

```bash
chaoxi --codes 000001 --json | jq .     # stdout JSON
chaoxi --codes 000001 -o ./results      # 指定输出目录
chaoxi --codes 000001 --max-results 100 # 限制数量（最高 3000）
chaoxi --codes 000001 --verbose         # 详细日志
```

---

## 🔧 管理

```bash
# 数据清理
chaoxi clean --older-than 30d  # 清理 30 天前数据
chaoxi clean --max-size 500M   # 限制总大小
chaoxi clean --keep 5          # 保留最近 5 次
chaoxi clean --keep 0          # 删除全部

# 日志管理
chaoxi log --tail 30           # 最近 30 条日志
chaoxi log --today --level error # 今日错误
chaoxi log --clear             # 清空日志

# 调试工具
chaoxi debug test-page         # 测试 cninfo 连通性
chaoxi debug inspect-api       # 查看 API 原始响应
```

---

## 📋 参数速查

| 参数 | 说明 |
|---|---|
| `--codes 000001,600519` | 股票代码，逗号分隔 |
| `--start 2026-01-01` | 公告起始日期（默认 90 天前） |
| `--end 2026-06-30` | 公告结束日期（默认今天） |
| `--categories 年报,半年报` | 分类中文名，26 类可选 |
| `--keyword 回购` | 标题关键词精确匹配 |
| `--board 创业板` | 深主板 / 沪主板 / 创业板 / 科创板 / 北交所 |
| `--industry 制造业` | 行业（API 未全支持） |
| `--download` | 下载 PDF 文件 |
| `--extract` | 下载 PDF 并提取 Markdown（隐含 `--download`） |
| `-y` / `--yes` | 跳过下载/提取确认 |
| `-d ./pdfs` | PDF 存放目录（默认 `{output}/pdfs/`） |
| `-o ./results` | 输出目录（默认自动时间戳） |
| `--json` | stdout JSON 输出 |
| `--max-results 100` | 结果上限 1–3000 |
| `--verbose` | 详细日志 |

---

## ⚙️ 配置

复制 `.env.example` 为 `.env`（可选，全部有默认值）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `CNINFO_TIMEOUT` | `30` | 请求超时秒数 |
| `MAX_CONCURRENT` | `4` | 并发下载数（≤4，否则 403） |
| `CNINFO_REQUEST_INTERVAL` | `0.5` | 请求最低间隔秒数 |
| `CHAOXI_OUTPUT_DIR` | `./chaoxi_output` | 输出根目录 |
| `EXCLUDE_KEYWORDS` | `摘要,确认意见,…` | 标题排除词（含这些词的结果不展示） |

---

## 📁 输出结构

```
chaoxi_output/
└── 20260808_120000/              # 会话目录
    ├── announcements.json        # 公告元数据
    ├── failed_downloads.json     # 下载失败清单
    ├── pdfs/                     # PDF 文件
    │   └── {code}_{id}_{title}.pdf
    └── md/                       # 提取的 Markdown（--extract 时）
        └── {code}_{id}_{title}.md
```

---

## 🙏 致谢

**第三方组件**

- [pdf-inspector](https://github.com/firecrawl/pdf-inspector) by Firecrawl (MIT) — PDF 结构化提取

**设计参考**（未使用源码）

- [use_cninfo](https://github.com/rollysys/use_cninfo) · [announcement_filter](https://github.com/rollysys/announcement_filter) · [Annualreport_tools](https://github.com/legeling/Annualreport_tools) · [CninfoDistributedSpider](https://github.com/flicck/CninfoDistributedSpider) · [cninfo](https://github.com/Christings/cninfo) · [CnInfoReports](https://github.com/tr1s7an/CnInfoReports) · [cninfo_process](https://github.com/gaodechen/cninfo_process) · [cninfo-mcp](https://github.com/youhaozhao/cninfo-mcp) · [cninfo_spider](https://github.com/jingmian/cninfo_spider)

---

## 📖 更多

- [使用手册](doc/usage.md) — 完整参数、行为详解、错误处理
- [开发日志](CHANGELOG.md) — 版本历史与近期规划
- [Skills](https://github.com/pawin1122/chaoxi/tree/main/skills) — AI 编码助手技能文件

---

<p align="center">
  <sub>MIT License · Made with ❤️</sub>
</p>

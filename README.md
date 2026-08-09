# chaoxi

巨潮网（cninfo.com.cn）公告数据获取 CLI 工具。查询上市公司公告、按分类筛选、下载 PDF。

## 安装

### 前置要求

| 项目 | 要求 |
|---|---|
| Python | 3.12+ |
| 包管理器 | [uv](https://docs.astral.sh/uv/)（推荐）或 pip |
| 网络 | 需能访问 `cninfo.com.cn`（巨潮网） |

### 方式一：全局安装（推荐）

安装后 `chaoxi` 命令在任何目录可用：

```bash
git clone https://github.com/pawin1122/chaoxi.git
cd chaoxi
uv tool install .
chaoxi --version
chaoxi --help
```

### 方式二：开发安装

在项目目录内通过 `uv run` 使用：

```bash
git clone https://github.com/pawin1122/chaoxi.git
cd chaoxi
uv sync
uv run chaoxi --help
```

### 方式三：tar.gz 发行包

```bash
tar xzf chaoxi-v0.1.1.tar.gz
cd chaoxi-v0.1.1
uv tool install .    # 全局安装
# 或
uv sync              # 开发安装
```

### 升级

已安装旧版本的用户，在仓库目录内拉取最新代码后重新安装即可：

```bash
cd chaoxi
git pull
uv tool install .
chaoxi --version
```

---

### Skills 安装（AI 编码助手专用）

AI 编码助手的 skill 文件**不包含在安装包内**。如需在 OpenCode、Claude Code 等 AI 编码助手中使用 chaoxi，请从仓库 `skills/` 目录手动复制：

| 助手 | 源文件 | 安装位置 |
|---|---|---|
| OpenCode | `skills/opencode/chaoxi/SKILL.md` | `.opencode/skills/chaoxi/SKILL.md` |
| Claude Code | `skills/claude-code/chaoxi.md` | 按 Claude Code skill 规范存放 |
| Codex | `skills/codex/chaoxi.md` | 按 Codex skill 规范存放 |
| Pi Agent | `skills/pi-agent/chaoxi.md` | 按 Pi Agent skill 规范存放 |

## 快速开始

```bash
chaoxi debug test-page                             # 测试连通性
chaoxi --codes 000001                              # 平安银行近 90 天公告
chaoxi --codes 000001 --keyword 回购 --download -y  # 下载回购相关 PDF
```

## 查询

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

## 下载 PDF

```bash
chaoxi --codes 000001 --download        # 下载（>50 个弹确认）
chaoxi --codes 000001 --download -y     # 跳过确认
chaoxi --codes 000001 --download -y -d ./pdfs  # 指定目录
```

## 输出

```bash
chaoxi --codes 000001 --json | jq .     # stdout JSON
chaoxi --codes 000001 -o ./results      # 指定输出目录
chaoxi --codes 000001 --max-results 100 # 限制数量
chaoxi --codes 000001 --verbose         # 详细日志
```

## 管理

```bash
chaoxi clean --older-than 30d    # 清理 30 天前数据
chaoxi clean --max-size 500M     # 限制总大小
chaoxi clean --keep 5            # 保留最近 5 次
chaoxi clean --keep 0            # 删除全部

chaoxi log --tail 30             # 最近 30 条日志
chaoxi log --today --level error # 今日错误
chaoxi log --clear               # 清空日志

chaoxi debug test-page           # 测试 cninfo 连通
chaoxi debug inspect-api         # 查看 API 原始响应
```

## 参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| `--start` | 90 天前 | 公告起始日期 YYYY-MM-DD |
| `--end` | 今天 | 公告结束日期 YYYY-MM-DD |
| `--codes` | 全市场 | 股票代码，逗号分隔 |
| `--categories` | 全部 26 类 | 中文分类名，逗号分隔 |
| `--keyword` | — | 标题关键词精确匹配 |
| `--board` | 全部 | 深主板/沪主板/创业板/科创板/北交所 |
| `--industry` | — | 行业（v0.2 生效） |
| `--download` | `False` | 开启 PDF 下载 |
| `-y` / `--yes` | `False` | 跳过下载确认 |
| `-d` | `{output}/pdfs/` | PDF 存放目录 |
| `-o` | 自动时间戳 | 输出目录 |
| `--json` | `False` | stdout JSON 输出 |
| `--max-results` | 3000 | 结果上限 1-3000 |
| `--verbose` | `False` | 详细日志 |

## 配置

复制 `.env.example` 为 `.env`（可选，全部有默认值）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `CNINFO_TIMEOUT` | 30 | 请求超时秒数 |
| `MAX_CONCURRENT` | 4 | 并发上限 |
| `CNINFO_REQUEST_INTERVAL` | 0.5 | 请求间隔下限（秒） |
| `CHAOXI_OUTPUT_DIR` | `./chaoxi_output` | 输出根目录 |
| `EXCLUDE_KEYWORDS` | 摘要,确认意见,… | 标题排除词（含这些词的结果不展示） |

## 输出结构

```
chaoxi_output/
└── 20260808_120000/              # 会话目录
    ├── announcements.json        # 公告元数据
    ├── failed_downloads.json     # 下载失败清单
    └── pdfs/                     # PDF 文件
        └── {code}_{id}_{title}.pdf
```

## 更多

- [使用手册](doc/usage.md) — 完整参数、行为详解、错误处理
- [Skills](https://github.com/pawin1122/chaoxi/tree/main/skills) — AI 编码助手技能文件（在 GitHub 仓库获取，不在安装包内）

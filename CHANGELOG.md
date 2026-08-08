# chaoxi 开发日志

## 2026-08-08

### 实机测试修复（3 项）

1. **去掉按天分片**：`_compute_date_shards` 改为返回 `[(start, end)]` 单一 shard。`seDate` 直接传完整日期范围，翻页由 `hasMore` 驱动。修复前查询 30 天=30 次 API 请求+延时。
2. **大小单位修复**：API 返回 `adjunct_size` 为 KB，但 `formatter.py` 按 bytes 格式化→显示 "159B"。改为 `adjunct_size * 1024` 转换后格式化→正确显示 "159.0KB"。
3. **clean --keep 0 语义**：`Cleaner._print_plan` 始终打 "预览模式"（不区分 dry-run）。修复：增加 `dry_run` 参数，非预览时不误标。`--keep 0` 显式分支 `to_delete = dirs`。

**测试**：138/138 全过。实机验证：招商银行 2025 年报秒出，中信银行 30 天 3 条正常。

### 文档完善（2 项）

1. **README 精简 + doc/usage.md**：README 缩减为 85 行入口概览。详细使用手册移入 `doc/usage.md`（402 行）。
2. **inbox/development.md**：新建开发检修手册（485 行），含环境验证、数据流架构图、文件导航表、调试工具、测试指南、日志分析、7 类常见问题定位、代码修改指南。

### v0.1 编码完成 — 4 Tier / 7 Agent 并行编码

按照 `inbox/多子Agent并行编码方案.md` 调度，通过 OpenCode `task` 工具并行启动 7 个子 Agent（deepseek-v4-pro / max 思考），分 4 个 Tier 完成全部编码。

**调度体系**：
- `inbox/公共提示词.md` — 所有子 Agent 共用前缀（含完整共享数据契约、异常体系、配置项、API 接口）
- `inbox/子Agent逻辑流程编排.md` — 7 个 Agent 的专属任务描述（前置依赖、核心约束、验收自检清单）
- `inbox/调度文档.md` — 进度跟踪总表（10 阶段 checklist）
- 约束：项目根目录 `/Users/pawin/Documents/AIUSE/chaoxi`、ego-browser 可实测验证、必须产出任务流程文件

**编码结果**：

| Tier | Agent | 模块 | 产出文件 |
|---|---|---|---|
| 1 | A | 基础设施 | `utils/config.py`, `exceptions.py`, `http_client.py`, `logging.py` |
| 1 | B | 参数解析 | `cli/params.py`, `cli/_constants.py` |
| 2 | C | 查询 | `models.py`, `query/engine.py`, `query/orgid.py`, `query/fetcher.py`, `query/dedup.py` |
| 2 | D | 管理 | `cli/clean.py`, `cli/debug.py`, `cli/log_cmd.py` |
| 3 | E | 下载 | `downloader/downloader.py` |
| 3 | F | 输出 | `output/formatter.py` |
| 4 | G | CLI 入口 | `main.py` |

**验证统计**：
- 源文件：24 个 `.py`，共 1909 行
- 测试：**138/138 passed**（含 test_http_client、test_logging、test_params、test_query、test_downloader、test_formatter）
- 集成导入：`from src.chaoxi.main import app` 通过
- CLI：`chaoxi --help` + `clean`/`debug`/`log` 子命令均正常
- 任务流程文件：7 份齐全（`inbox/_任务流程/Agent-A~G_*.md`）

**旧代码清理**：
- 删除 `crawler/`、`db/`、`debug/` 全部旧模块
- 移除 sqlalchemy、aiosqlite、beautifulsoup4、dateparser 依赖
- 新增 pytest-httpx，requires-python 升至 ≥3.12

### 下一步
- 实机测试：使用真实 cninfo.com.cn API 端到端验证一条查询
- 调试与修复：根据实机测试结果叠代修正

---

## 2026-08-06

### 详细设计复审 + 多子 Agent 并行编码方案

对详细设计进行了第二轮审查（从软件工程详细设计标准出发），最终确认设计质量良好，无编码阻断项。审查过程沉淀为 `inbox/detailed-design/审查问题清单.md`。

**关键产出**：
- `inbox/多子Agent并行编码方案.md` — 4 Tier / 7 Agent 并行编码方案，含：调度机制、共享契约、一致性保障、结果检查与返工策略、集成验证、完整检查清单
- 确认 OpenCode 的子 Agent 能力满足并行需求：Task 工具可同时启动多个 general 子 Agent、Chrome MCP 对子 Agent 透明可用
- 确认 Chrome DevTools MCP 对子 Agent 可调用，可用于编码时自验巨潮 API

### 详细设计审查与修复（软件工程规范对照检查）

对 `inbox/detailed-design/` 全部 10 份文档进行了软件工程详细设计标准审查，发现 **33 个问题**（严重 8 个 / 中等 17 个 / 低 8 个），全部修复并通过 44 个检查点复查。

**严重问题修复（8 个）**：
- 02_查询模块：`_fetch_one_column` 翻页循环代码被错误包裹在 docstring 内 → 修复为独立代码块
- 02_查询模块：板块客户端过滤（`pageColumn`）未出现在 `execute()` 主流程 → 补充步骤2.5
- 03_PDF下载：`asyncio.as_completed` 导致结果顺序随机 → 末尾增排序恢复
- 06_CLI入口：`build_query_config()` 异常在 try/except 保护范围外 → 包裹 try/except
- 06_CLI入口：`@app.command()` 致主命令与子命令冲突 → 改为 `@app.callback(invoke_without_command=True)`
- 07_配置基础设施：随机延时公式算出 0.25~1.0s 与文档声明的 0.5~1.5s 不一致 → 改为 `random.uniform(0.5, 1.5)`
- 08_文件清单：目录树缺失 `models.py` → 补充到目录树和映射表
- 跨文档：`QueryConfig` 归属 `cli/params.py` 致查询/下载模块反向依赖 CLI 层 → 标注设计意图 v0.1 可接受

**中等+低问题修复（25 个）**：
- `--output` 重命名为 `--json`（bool 类型）
- 所有异常 suggestion 统一 `"请…"` 格式
- `LogEngine.read()` 从 async 改为同步
- `PdfDownloader.download()` 返回 `(list, DownloadTracker)` 元组
- 403 全局停止使用 `asyncio.Event`
- 非 TTY 环境下载确认自动跳过
- `get_bytes()` 补充完整重试伪代码
- `_backup_url()` 给明确 `rsplit` 实现
- `Debugger.run()` 调度方法补充
- `Cleaner.clean()` 三参数全 None 时明确报错
- 终端表格列宽限制规格化、排序键明确化
- `.env` 路径注释、日志路径说明、Semaphore 双层保护说明
- 旧结构对照表追加新增文件子表
- 编码顺序表 Tier 4 修正标注

### 下一步
- **编码实现**：设计文档已通过审查，按 Tier 顺序开工

---

## 2026-08-05

### 详细设计完成（5 轮审查 + Chrome 实测验证）

产出 `inbox/detailed-design/` 目录共 10 份文档（00~08 + README），~2512 行。

**Chrome 实测验证 10 项**：在 cninfo.com.cn 通过 DevTools + XHR 拦截验证了 25 类分类代码（修正 10 个猜测）、板块 plate 映射（创业板/科创板无独立 plate，需 pageColumn 客户端过滤）、多分类分隔符（分号 `;`）、trade 参数（中文名直接有效）、备用端点、hasMore 翻页、pageSize 硬限 30 等。

**审查统计**：第1轮43→42、第2轮19→19、第3轮7→7、第4轮6→6、第5轮（参考手册对照）3→3。合计发现 78 个问题，修复 77 个。

**参考手册对照**：按天分片（按月会漏）、hasMore 终止翻页、随机延时（0.5~1.5s）。

### 下一步
- **编码实现**：按 `08_包结构与文件清单.md` 的 4 个 Tier 并行开工

---

## 2026-08-04

### 概要设计完成
- 完成 `inbox/概要设计.md`（706 行），5 轮审查修正 34 项问题
- 13 章：设计目标、架构总览、模块设计（6 模块）、协作流程、接口设计、环境配置、非功能性约束、运行部署、错误处理、设计决策、需求追溯、技术选型、范围界定 + 附录
- 参考手册验证后补充：column/plate 参数映射、orgId 两级缓存、变体公告排除、标题清洗、seDate 分隔符声明
- 风险应对策略：日志驱动的迭代修复（日志→AI定位→模块修复→版本更新）

### 架构迁移记录

**命令对比**：
- `chaoxi announce` → 合并为 `chaoxi` 主命令
- `chaoxi search` → 合并为 `chaoxi --keyword`
- `chaoxi category` → 合并为 `chaoxi --categories`
- `chaoxi attach` → 合并为 `chaoxi --download`
- `chaoxi db` → 删除（不再需要数据库）
- `chaoxi debug` → 保留
- 新增 `chaoxi clean`
- 新增 `chaoxi log`

**原有模块的去留**：
- `crawler/announcements.py` — 重写，整合进查询模块
- `crawler/search.py` — 重写，整合进查询模块
- `crawler/categories.py` — 重写，整合进查询模块
- `crawler/attachments.py` — 重写为下载模块
- `crawler/client.py` — 重写，HTTP 工具
- `db/engine.py` — 删除
- `db/models.py` — 删除
- `db/commands.py` — 删除
- `debug/inspector.py` — 保留并调整，整合进管理模块
- `utils/config.py` — 保留
- `utils/formats.py` — 保留
- `main.py` — 重写，三命令→单命令

### v0.2+ 规划（新增）
- 高级公告分类：`announcement_filter` 11 大类 82 子类分类体系

### 下一步
- **详细设计** → 已于 2026-08-05 完成（见上方记录）

---

## 2026-08-05

### 详细设计完成（6 轮审查 + 实测验证）

**产出物**：`inbox/detailed-design/` 目录下 10 份文档（00~08 + README），共 ~2512 行。

| 文档 | 内容 |
|---|---|
| README.md | 总索引：模块依赖图、编码顺序、数据契约速查、API 接口确认 |
| 00_共享数据模型.md | QueryConfig / RawAnnouncement / Announcement / QueryMeta / AnnouncementList / DownloadTracker（Pydantic v2） |
| 01_参数解析模块.md | build_query_config()、CATEGORY_NAME_MAP(25类)、BOARD_MAP(5板块)、INDUSTRY_LIST(19类) |
| 02_查询模块.md | QueryEngine、OrgIdCache(内存)、AnnouncementFetcher(按天分片+hasMore翻页)、去重/关键词/变体排除 |
| 03_PDF下载模块.md | PdfDownloader(并发4)、重试退避、域名白名单、魔数校验、.part原子写入 |
| 04_输出模块.md | OutputFormatter：终端表格(30行预览) / JSON文件 / stdout管道 三模式 |
| 05_管理模块.md | Cleaner(同步)、Debugger、LogViewer |
| 06_CLI入口.md | Typer app 总调度器、_main_async 流程、异常统一处理 |
| 07_配置与基础设施.md | AppSettings(.env)、CninfoClient(httpx+随机延时+重试)、异常体系、LogEngine(JSONL) |
| 08_包结构与文件清单.md | src/chaoxi/ 文件布局、pyproject.toml 依赖、测试策略、编码顺序 |

### Chrome 实测验证（10 项）

通过 Chrome DevTools + XHR 拦截在 cninfo.com.cn 上完成全部验证：

| 验证项 | 关键发现 |
|---|---|
| V1 分类代码 | 25 类全部确认，修正 10 个猜测代码（半年报=bndbg、董事会=dshgg 等） |
| V2 板块映射 | 创业板/科创板无独立 plate，需 pageColumn 客户端过滤（SZCY/SHKCB） |
| V3 行业参数 | trade=中文名直接有效（如 trade=制造业） |
| V4 多分类分隔符 | **分号 `;`**（与 stock 参数一致），非逗号 |
| V5 备用端点 | 主 URL + 备用 URL 均可用 |
| V6 shortTitle | 100% 存在但 = announcementTitle，无特殊处理价值 |
| V7 pageSize | 硬限 30，传 40 仍返回 30 |
| V8 多股票 | 分号分隔正确，跨交易所需分别请求 szse/sse |
| V9 分页一致性 | 翻页时 totalAnnouncement 不变 |
| V10 变体排除 | 30 样本 0 误伤 |

### 参考手册对照

对照 `参考手册_完整技术汇总.md`（9 个同类项目），3 处修正：
- **按天分片**（参考 3 处独立来源确认按月会漏数据）
- **hasMore 翻页**（API 提供 hasMore 字段，比 len<30 更可靠）
- **随机延时**（random.uniform(0.5,1.5s) 替代固定 0.5s）

### 审查统计

| 轮次 | 发现问题 | 修复 |
|---|---|---|
| 第1轮（基础设施+数据模型） | 43 | 42 |
| 第2轮（第1轮副作用清理） | 19 | 19 |
| 第3轮（需求/概要一致性） | 16→7(过滤概要修改) | 7 |
| 第4轮（代码质量+逻辑一致性） | 6 | 6 |
| 第5轮（参考手册对照） | 3 | 3 |
| **合计** | **87** | **77**（10 项为有意差异标注，1 项待 Chrome 验证后确认） |

### 架构变更（概要→详细）

与概要设计的主要差异（均已标注）：
- orgId 缓存：两级→纯内存（v0.2 恢复磁盘）
- 变体排除：正则+白名单→纯子串匹配（v0.2 引入白名单）
- API 请求日志：per-request→关键事件（可 debug inspect-api 手动查看）
- 概要 §4 场景三：删除 CleanConfig 引用，同步为直接参数传递
- 请求间隔：恢复为 Semaphore+随机延时（严格遵循概要约束）

### 下一步
- **编码实现**：按 `08_包结构与文件清单.md` 的 4 个 Tier 并行开工

---

## 2026-08-03

### 需求分析终稿
- 基于巨潮官网实测 + 参考手册验证，完成 `inbox/需求分析.md`（465 行）
- 核心决策：
  - **单一 `chaoxi` 命令**替代原 announce/search/category 三命令，六维度自由组合
  - **砍掉 SQLite** — 公告正文全在 PDF，数据库无存储价值
  - **砍掉原 db/ 模块** — 不需要持久化层
  - **去重恢复** — 参考手册所有 9 个项目均证实 API 返回重复，必须去重
  - **发现+下载双模式**：模式一仅输出 JSON（含 PDF URL），模式二下载 PDF + 输出 JSON（含本地路径）
  - **输出目录按会话组织**（时间戳），不按股票 — 方便多次查询不混淆
- 查询维度：日期段（默认 90 天可配）、股票代码、分类（25 类）、关键词（客户端精确匹配）、板块、行业
- 技术选型调整：
  - 移除：SQLAlchemy、aiosqlite、BeautifulSoup4、dateparser
  - 保留：Typer、httpx、Rich、Pydantic、uv
  - PyMuPDF 降级为 v0.2+ 备选
- 下载行为规范：
  - 重试策略（网络错误 3 次指数退避，403 不重试）
  - 断点续传（重新执行跳过已下载）
  - 下载前确认（超过阈值提示，`-y` 跳过）
  - PDF 安全校验（魔数 %PDF、Content-Type、.part 临时文件）
  - 失败输出 `failed_downloads.json`
  - 进度条（Rich）
- 缓存清理：`chaoxi clean` 按天数/大小/保留次数
- 15 条事实约束（orgId/翻页/并发/去重/时区转换/旧PDF备用端点等）
- .env 配置完整定义
- v0.2+ 规划：
  - `chaoxi view --id <announcement_id>` — 单篇 PDF 文本/Markdown 输出（基于 PyMuPDF）
  - `chaoxi ... --download --extract` — 下载同时批量提取全量 PDF 为 Markdown，输出到 `md/` 子目录
  - 扫描件 PDF 降级提示（OCR 需外部依赖，暂不纳入）
  - 高级公告分类（如 `announcement_filter` 11 大类 82 子类分类体系，概要设计中识别）

### 巨潮官网实测
- 确认 25 类公告分类体系与实际 API 对齐
- 确认关键词搜索为标题模糊匹配（后端 SQL LIKE），客户端精确过滤更可靠
- 确认公告详情页直接跳转 PDF，无 HTML/文本 API
- 调研和持续督导分类评估后不纳入 MVP

### 架构变更
- **移除 `src/chaoxi/db/`** — 模块不再需要
- 后续概要设计将按模块独立原则重新组织 `src/chaoxi/`

### 下一步
- **概要设计**：围绕需求分析完成 v0.1 MVP 架构设计
  - 原则：各功能尽量独立模块化，方便后续调试与功能替换
  - 参考 `use_cninfo` 的模块化设计（api.py / fetcher.py / parser.py / cache.py 各司其职）

---

## 2026-08-02

### 项目初始化
- 技术选型确认（QA）：Python / Typer / SQLAlchemy ORM / uv
- 创建目录结构：`src/chaoxi/{crawler,db,debug,utils}`, `tests/`, `inbox/`
- 编写 pyproject.toml：依赖 typer, httpx, sqlalchemy, aiosqlite, rich, pydantic, pydantic-settings, beautifulsoup4, dateparser
- 编写 .gitignore, .env.example
- 创建核心模块骨架：
  - `main.py` — CLI入口，注册6个子命令
  - `crawler/client.py` — HTTP客户端（同步+异步）
  - `crawler/announcements.py` — 日期范围公告（mock）
  - `crawler/search.py` — 关键词搜索（mock）
  - `crawler/categories.py` — 内容分类获取（mock）
  - `crawler/attachments.py` — 附件下载（mock）
  - `db/engine.py` — SQLAlchemy引擎+会话
  - `db/models.py` — Announcement 数据模型
  - `db/commands.py` — db init / db stats
  - `debug/inspector.py` — test-page / inspect-api / list-headers
  - `utils/config.py` — pydantic-settings 配置
  - `utils/formats.py` — JSON/Table 格式化输出
- uv sync 安装依赖，修复 build-system 配置（hatchling），创建 README.md
- CLI 验证：6个子命令全部可用，mock 命令执行通过，db init 建表成功

### 参考项目调研
- 从 GitHub 收集了 9 个巨潮网相关开源项目并克隆到 `inbox/ref_*/`
- 生成项目分析提示词模板 `inbox/提示词_参考项目分析.md`
- 使用 3 个子 Agent 并行完成 9 个项目的源码分析
- 生成完整参考手册 `inbox/参考手册_完整技术汇总.md`（2552行，119KB）
- 归档过程文件到 `inbox/_过程文件/`

### 参考手册覆盖内容
- 9 个项目的完整 8 维度分析（概览/技术栈/API/流程/数据结构/复用评分/踩坑/特色）
- 横向对比：API 接口（6个）、技术栈（4项目）、orgId方案、PDF方案、分类方案
- 跨项目踩坑大全：30条（致命5/重要13/注意12）
- 对 chaoxi 的建议：11条技术决策、11个参考代码位置、8个应避免方案、16个5/5模块

### 关键发现
- API 端点：`hisAnnouncement/query` (POST) 是唯一当前有效接口
- orgId 是核心难点：stock 参数必须 `<代码>,<orgId>` 格式
- pageSize 硬限 30，翻页是必须的
- PyMuPDF 是最佳 PDF 方案（286页1-2秒）
- 并发数不能超过 4（否则 403）
- 23 种 category 参数已整理完毕
- **ref_use_cninfo 参考价值极高**：
  - 同为 vibe coding 项目（Claude Opus 4.7 生成），验证了此方法可行
  - 功能高度重叠：日期公告、分类获取、关键词搜索、附件下载
  - 核心差异：它用文件缓存，我们用 SQLite；它做 PDF 全文提取，我们只下载
  - API 调用代码（api.py）、orgId 方案（orgid.py）、缓存设计可直接参考
  - 详细设计阶段可大量照搬其模块设计

### 需求分析
- 生成需求分析草稿 `inbox/需求分析_草稿.md`
- 已确认：4项基础功能 + 4项项目能力 + 技术选型
- 待细化：PDF内容提取、板块范围、存储策略、分类体系、并发等

### 技术选型优化
- 对比参考手册（9项目实测验证），优化初选技术栈：
  - 排除 BeautifulSoup4 — 巨潮是 JSON API，不需要 HTML 解析
  - dateparser → datetime (标准库) — cninfo 返回 epoch ms，够用
  - 新增 PyMuPDF (暂留备选) — PDF 解读由外部工具完成，核心只下载
  - 新增 HTTP 指数退避重试机制（3次）— cninfo-mcp 验证方案
- 需求草稿新增"事实约束"章节：6条硬性约束（orgId/翻页/去重/并发上限/请求间隔/按天分片）

### 其他
- 更新 README.md，含完整项目结构和 AI 续接指引
- 初始化 git 仓库，首次提交

### 下一步
- 需求分析细化（同步/异步、缓存策略、分类方案、去重逻辑等设计决策）
- 确定具体功能边界和技术方案
- 开始实现 API 调用层

---

> **AI 续接指引**：阅读本文档了解上下文 → 查看 `inbox/需求分析.md` 确认需求 → 参考 `inbox/参考手册_完整技术汇总.md` 获取技术方案 → 按"下一步"开始概要设计。

---

## 项目结构

```
chaoxi/
├── pyproject.toml
├── README.md
├── .gitignore
├── .env.example
├── CHANGELOG.md
├── inbox/
│   ├── 需求分析.md                  ← 需求分析终稿
│   ├── 概要设计.md                  ← 概要设计终稿
│   ├── 需求分析_草稿.md             ← 初稿（已废弃）
│   ├── 参考手册_完整技术汇总.md     ← 主要技术参考
│   ├── 提示词_参考项目分析.md       ← Agent 分析模板
│   ├── ref_*/                       ← 9个参考项目源码
│   ├── _过程文件/                   ← 归档
│   └── detailed-design/             ← 详细设计（v0.1 编码前）
│       ├── README.md                ← 总索引
│       ├── 00_共享数据模型.md
│       ├── 01_参数解析模块.md
│       ├── 02_查询模块.md
│       ├── 03_PDF下载模块.md
│       ├── 04_输出模块.md
│       ├── 05_管理模块.md
│       ├── 06_CLI入口.md
│       ├── 07_配置与基础设施.md
│       └── 08_包结构与文件清单.md
├── src/chaoxi/                     ← 待实现（目标结构见 08 文档）
│   ├── main.py
│   ├── models.py
│   ├── exceptions.py
│   ├── http_client.py
│   ├── logging.py
│   ├── cli/
│   │   ├── params.py
│   │   ├── _constants.py
│   │   ├── clean.py
│   │   ├── debug.py
│   │   └── log_cmd.py
│   ├── query/
│   │   ├── engine.py
│   │   ├── orgid.py
│   │   ├── fetcher.py
│   │   └── dedup.py
│   ├── downloader/
│   │   └── downloader.py
│   ├── output/
│   │   └── formatter.py
│   └── utils/
│       └── config.py
└── tests/
```

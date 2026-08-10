# chaoxi 使用手册

> v0.2.0 | 巨潮网（cninfo.com.cn）公告数据获取 CLI 工具

---

## 配置

### 配置方式

工具通过 `pydantic-settings` 加载配置，优先级从高到低：系统环境变量 > `.env` 文件 > 默认值。

`.env` 文件从当前工作目录（CWD）查找。复制模板后编辑：

```bash
cp .env.example .env
```

所有配置项均有默认值，`.env` 非必需。

### 配置项全表

#### API 连接

| 变量 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `CNINFO_BASE_URL` | str | `https://www.cninfo.com.cn/new` | 巨潮 API 基础地址。正常情况下无需修改 |
| `CNINFO_STATIC_URL` | str | `https://static.cninfo.com.cn` | PDF 文件下载地址。正常情况下无需修改 |
| `CNINFO_TIMEOUT` | int | 30 | 单次 HTTP 请求超时秒数。网络慢可适当调大 |

#### 查询控制

| 变量 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `DEFAULT_LOOKBACK_DAYS` | int | 90 | 未指定 `--start` 时的默认回溯天数 |
| `MAX_PAGES` | int | 100 | 翻页安全上限。100 页 × 30 条 = 最多 3000 条。不建议调整 |
| `MAX_CONCURRENT` | int | 4 | 并发 API 请求数上限。实测超过 4 会触发 HTTP 403 限流。不建议调大 |
| `REQUEST_INTERVAL` | float | 0.5 | 两次请求最小间隔秒数。实际延时为 `random.uniform(0.5, 1.5)`，此值为下限 |

#### 下载控制

| 变量 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `DOWNLOAD_CONFIRM_THRESHOLD` | int | 50 | 待下载 PDF 数量超过此值时弹确认提示。设为较大值可减少提示 |
| `EXCLUDE_KEYWORDS` | str | `摘要,确认意见,取消,更正,补充,提示,致歉,修订,英文` | 变体公告排除词。逗号分隔，标题命中任一即排除 |

#### 输出与日志

| 变量 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `CHAOXI_OUTPUT_DIR` | str | `./chaoxi_output` | 输出根目录。查询结果的 JSON 和 PDF 都存放于此目录下 |
| `MAX_LOG_LINES` | int | 500 | 日志行数上限。超出时自动删除前 10% 的旧条目 |

#### 代理

| 变量 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `HTTP_PROXY` | str | — | HTTP 代理地址，如 `http://127.0.0.1:7890` |
| `HTTPS_PROXY` | str | — | HTTPS 代理地址。未设置时使用 `HTTP_PROXY` 的值 |

### 示例 .env

```bash
# 调试：延长超时，增大并发
CNINFO_TIMEOUT=60
MAX_CONCURRENT=4

# 自定义输出位置
CHAOXI_OUTPUT_DIR=/data/cninfo_announcements

# 不排除任何公告
EXCLUDE_KEYWORDS=

# 代理
HTTPS_PROXY=http://127.0.0.1:7890
```

### 排除词说明

`EXCLUDE_KEYWORDS` 用于过滤标题含特定词的公告（如摘要、更正、致歉等变体）。v0.1 为简单子串匹配。

默认排除 9 类：摘要 / 确认意见 / 取消 / 更正 / 补充 / 提示 / 致歉 / 修订 / 英文

已知风险：标题含"说明书"会被排除词"说明"误伤。如需精确匹配，将排除词改为逗号分隔的完整词即可（如 `说明书摘要` 而非 `说明`）。

---

## 命令参考

### 主命令 `chaoxi`

查询巨潮网公告，可选下载 PDF 或提取为 Markdown。

```
chaoxi [OPTIONS]
```

### 子命令

| 命令 | 说明 |
|---|---|
| `chaoxi clean` | 清理历史输出数据 |
| `chaoxi debug` | 调试与排错工具 |
| `chaoxi log` | 查看运行日志 |

---

## 使用场景

### 基础查询

```bash
# 某股票近期公告
chaoxi --codes 000001

# 指定日期范围
chaoxi --codes 000001 --start 2026-06-01 --end 2026-08-01

# 多股票
chaoxi --codes 000001,600519,300750
```

### 分类查询

```bash
# 全市场年报
chaoxi --categories 年报 --start 2026-01-01

# 多分类组合
chaoxi --categories 年报,董事会 --codes 000001

# 板块+分类
chaoxi --board 创业板 --categories 业绩预告
```

### 公告分类完整表

查询时使用中文名（如 `--categories 年报`），工具自动翻译为 API 代码。

| 中文名 | API 代码 |
|---|---|
| 年报 | category_ndbg_szsh |
| 半年报 | category_bndbg_szsh |
| 一季报 | category_yjdbg_szsh |
| 三季报 | category_sjdbg_szsh |
| 业绩预告 | category_yjygjxz_szsh |
| 权益分派 | category_qyfpxzcs_szsh |
| 董事会 | category_dshgg_szsh |
| 监事会 | category_jshgg_szsh |
| 股东会 | category_gddh_szsh |
| 日常经营 | category_rcjy_szsh |
| 公司治理 | category_gszl_szsh |
| 中介报告 | category_zj_szsh |
| 股权变动 | category_gqbd_szsh |
| 股权激励 | category_gqjl_szsh |
| 补充更正 | category_bcgz_szsh |
| 澄清致歉 | category_cqdq_szsh |
| 风险提示 | category_fxts_szsh |
| 首发 | category_sf_szsh |
| 增发 | category_zf_szsh |
| 配股 | category_pg_szsh |
| 公司债 | category_gszq_szsh |
| 可转债 | category_kzzq_szsh |
| 其他融资 | category_qtrz_szsh |
| 解禁 | category_jj_szsh |
| 特别处理和退市 | category_tbclts_szsh |
| 退市整理期 | category_tszlq_szsh |

### 关键词搜索

```bash
# 标题含"回购"
chaoxi --codes 000001 --keyword 回购

# 全市场关键词
chaoxi --keyword 分红 --start 2026-01-01
```

> 关键词为客户端标题精确匹配（`keyword in title`），非后端模糊搜索。

### 板块筛选

```bash
chaoxi --board 深主板 --categories 年报
chaoxi --board 科创板 --start 2026-01-01
```

可选板块：深主板、沪主板、创业板、科创板、北交所。

> 创业板和科创板无独立 `plate` 值，通过客户端 `pageColumn` 过滤。

### 板块完整表

| 中文名 | column | plate | 备注 |
|---|---|---|---|
| 深主板 | szse | sz | |
| 沪主板 | sse | sh | |
| 创业板 | szse | — | 无 plate，客户端 pageColumn=SZCY 过滤 |
| 科创板 | sse | — | 无 plate，客户端 pageColumn=SHKCB 过滤 |
| 北交所 | szse | bj | |

### PDF 下载

```bash
# 查询 + 下载
chaoxi --codes 000001 --keyword 回购 --download

# 跳过确认 + 指定 PDF 目录
chaoxi --codes 000001 --download -y -d ./my_pdfs
```

### PDF 提取

```bash
# 下载并自动提取为 Markdown
chaoxi --codes 601998 --categories 年报 --extract -y

# 提取确认：>30 份 PDF 时弹提示，-y 跳过
chaoxi --codes 000001 --extract -y
```

提取后终端表格新增"提取"列，显示四种状态：
- `✅` — 完整提取（text_based PDF，无乱码）
- `⚠️N页` — 部分乱码（N 页编码异常，已跳过）
- `❌扫描件` — 扫描件/图片型 PDF，无法提取文本
- `❌错误` — 提取过程中异常

### 输出控制

```bash
# JSON 到 stdout（管道模式）
chaoxi --codes 000001 --json | jq '.announcements[0].title'

# 指定输出目录
chaoxi --codes 000001 -o ./results

# 限制结果数量
chaoxi --codes 000001 --max-results 100

# 详细日志
chaoxi --codes 000001 --verbose
```

### 管理

```bash
# 清理 30 天前的数据
chaoxi clean --older-than 30d

# 限制总大小 500MB
chaoxi clean --max-size 500M

# 仅保留最近 5 次
chaoxi clean --keep 5

# 删除全部（保留 0 次）
chaoxi clean --keep 0

# 预览（不删）
chaoxi clean --older-than 30d --dry-run
```

### 调试

```bash
# 测试连通性
chaoxi debug test-page

# 查看 API 原始响应
chaoxi debug inspect-api
```

### 日志

```bash
# 最近 30 条
chaoxi log --tail 30

# 今日错误
chaoxi log --today --level error

# 清空
chaoxi log --clear
```

---

## 参数速查

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `--start` | `YYYY-MM-DD` | 90 天前 | 公告起始日期 |
| `--end` | `YYYY-MM-DD` | 今天 | 公告结束日期 |
| `--codes` | `str` | — | 股票代码，逗号分隔 |
| `--categories` | `str` | 全部 26 类 | 中文分类名，逗号分隔 |
| `--keyword` | `str` | — | 标题关键词 |
| `--board` | `str` | 全部 | 深主板/沪主板/创业板/科创板/北交所 |
| `--industry` | `str` | — | 行业（v0.2 生效） |
| `--download` | `bool` | `False` | 下载 PDF 文件 |
| `--extract` | `bool` | `False` | 下载 PDF 并提取为 Markdown（隐含 --download，与 --download 互斥） |
| `-y` / `--yes` | `bool` | `False` | 跳过下载/提取确认 |
| `-d` / `--download-dir` | `str` | `{output}/pdfs/` | PDF 存放目录 |
| `-o` | `str` | 自动生成时间戳 | 输出目录 |
| `--json` | `bool` | `False` | stdout JSON 输出 |
| `--max-results` | `int` | 3000 | 结果上限（1-3000） |
| `--verbose` | `bool` | `False` | 详细输出 |

---

## 输出结构

```
chaoxi_output/
└── 20260808_120000/              # 时间戳会话目录
    ├── announcements.json        # 公告元数据
    ├── failed_downloads.json     # 下载失败清单（--download 时）
    ├── pdfs/                     # PDF 文件（--download 时）
    │   └── {code}_{id}_{title}.pdf
    └── md/                       # 提取的 Markdown（--extract 时）
        └── {code}_{id}_{title}.md
```

### announcements.json 结构

```json
{
  "query": {
    "start": "2026-01-01",
    "end": "2026-08-08",
    "codes": ["000001"],
    "categories": ["年报"],
    "total": 42,
    "total_raw": 50,
    "total_filtered": 8,
    "api_total": 50,
    "truncated": false,
    "fetched_at": "2026-08-08T12:00:00+08:00"
  },
  "announcements": [
    {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "title": "平安银行股份有限公司2025年年度报告",
      "short_title": "平安银行2025年年度报告",
      "announcement_id": "1225451412",
      "announcement_time": "2026-06-30",
      "announcement_type": "01010503||01",
      "pdf_url": "https://static.cninfo.com.cn/finalpage/2026-06-30/1225451412.PDF",
      "adjunct_size": 286,
      "pdf_path": "pdfs/000001_1225451412_xxx.pdf",
      "status": "downloaded",
      "error": null,
      "md_path": "md/000001_1225451412_xxx.md",
      "extraction": {"status": "success", "pdf_type": "text_based"}
    }
  ]
}
```

字段说明：
- `total`：最终有效公告数（去重+过滤后）
- `total_raw`：API 返回原始条数
- `total_filtered`：被过滤掉的条数
- `api_total`：API 声明的 `totalAnnouncement`
- `truncated`：是否达到翻页上限被截断
- `status`：`"downloaded"` / `"failed"` / `"skipped"` / `null`（未下载）
- `announcement_type`：管道分隔的多分类代码，如 `"01010503||01"`

### failed_downloads.json 结构

```json
{
  "failed_count": 2,
  "failed_downloads": [
    {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "title": "...",
      "pdf_url": "https://static.cninfo.com.cn/...",
      "error": "PDF validation failed"
    }
  ]
}
```

---

## 行为详解

### 查询机制

**日期范围**：seDate 直接传入完整日期范围（如 `2026-01-01~2026-08-08`），
不做日期拆分。翻页由 API 的 hasMore 机制驱动，逐页获取直到全部取完。
如需更精细控制，可多次调用 CLI 缩小日期范围。

**翻页终止**：每片内翻页，终止条件按优先级：
1. 本轮返回空（`len(batch) == 0`）
2. 页数达到 `max_pages=100`（上限 3000 条）
3. API 返回 `hasMore=false`

**跨交易所**：不指定 `--board` 时，自动并发请求深市（`column=szse`）和沪市（`column=sse`），合并结果后去重。

**去重策略**：去重键 `(股票代码, announcement_title.strip(), 附件URL)`。同一公告在 A+H 股两个板块都有记录时只保留一条。`announcementType` 是多分类管道分隔值（如 `"01010503||010112||011719"`），去重不影响它。

**关键词过滤**：两阶段——
1. 后端：API 的 `searchkey` 参数做 SQL LIKE 标题模糊匹配
2. 客户端：`keyword in title` 精确匹配（大小写不敏感）  
客户端精确匹配更可靠，后端 LIKE 是辅助预筛。

**变体排除**：按 `EXCLUDE_KEYWORDS` 列表做标题子串匹配，命中任一排除词即排除。默认排除：摘要、确认意见、取消、更正、补充、提示、致歉、修订、英文。v0.1 为简单子串匹配（如"说明书"会被排除词"说明"误伤），v0.2 将引入白名单机制。

**非 PDF 附件**：API 偶尔返回 DOC/XLS 格式（`adjunctType != "PDF"`），查询阶段自动过滤，不进入结果。

**板块过滤（创业板/科创板）**：创业板（`SZCY`）和科创板（`SHKCB`）无独立 `plate` 值，查询时拉全量后按 `pageColumn` 字段客户端过滤。

**标题清洗**：去除 `<em>`, `</em>` 等 HTML 标签，trim 空白。

**时间转换**：`announcementTime`（epoch 毫秒）→ 北京时间 ISO 日期字符串（`YYYY-MM-DD`）。

**进度显示**：`--verbose` 时显示简洁进度：`查询中 {n} 条...`。同一条消息实时刷新。

### 下载机制

**流程**：
```
检查全局停止信号 → 检查本地已存在 → 域名白名单校验
→ GET 下载 → Content-Type 校验 → .part 写入
→ %PDF- 魔数校验 → 原子重命名 .part→.pdf
```

**并发控制**：`asyncio.Semaphore(4)` — 查询和下载各有独立信号量，均限制 4 并发。超过 4 会触发 HTTP 403。

**重试策略**：
- 网络错误（超时/连接失败）：重试 3 次，指数退避（1s → 2s → 4s），耗尽抛 `NetworkError`
- HTTP 403：**不重试**，立即通过 `asyncio.Event` 全局停止所有下载，抛 `RateLimitError`
- HTTP 500：重试 3 次（同上），耗尽抛 `ApiError`
- HTTP 404：返回空 bytes（`b""`），由下载器尝试备用 URL

**备用 URL**：主 URL（`static.cninfo.com.cn`）返回 404 时，从 `pdf_url` 反解析出 `bulletinId` 和 `announceTime`，构造备用地址：
```
GET {cninfo_base_url}/new/announcement/download?bulletinId={id}&announceTime={YYYY-MM-DD}
```

**校验**：
- **域名白名单**：`pdf_url` 必须以 `https://static.cninfo.com.cn/` 或 `https://www.cninfo.com.cn/` 开头
- **Content-Type**：必须是 `application/pdf`
- **魔数**：文件前 5 字节必须是 `b'%PDF-'`
- 任一不通过 → `status=failed`，记录 `error` 原因

**原子写入**：先写 `.part` 临时文件，校验通过后 `os.rename` 为 `.pdf`。下载中断留下的 `.part` 文件下次执行时忽略。

**断点续传**：重新执行同一查询+下载命令时，已存在的 PDF 跳过（`status=skipped`），只补下失败的。

**下载确认**：PDF 数量 > `DOWNLOAD_CONFIRM_THRESHOLD`（默认 50）时弹提示：
```
⚠ 即将下载 {N} 个 PDF（约 {size} MB），可能触发网站限流或封禁。
是否继续？[y/N]:
```
下载 >50 时追加 AI 处理建议："建议：仅生成 JSON 文件，后续交由 AI 处理 PDF 下载与识别"。
`-y` 强制跳过。非 TTY 环境（管道/脚本）自动跳过。

**结果排序**：`asyncio.as_completed` 返回完成顺序非输入顺序，下载后按原始输入顺序恢复排列。

**失败清单**：失败条目写入 `{output_dir}/failed_downloads.json`，含 `stock_code`、`stock_name`、`title`、`pdf_url`、`error`。

**文件名**：`{stock_code}_{announcement_id}_{safe_title}.pdf`，非法字符 `/:*?"<>|` 替换为 `_`。

### 限流与反爬

- **随机延时**：每次 API 请求前 `random.uniform(0.5, 1.5)` 秒延时。多个同类项目确认随机延时比固定间隔更防爬。
- **Cookie 管理**：首次使用 `CninfoClient` 自动 GET 巨潮首页（`/new/index`）获取 `JSESSIONID`，存入 `httpx.AsyncClient` 的 cookie jar。有效期数小时，足够完成一次完整查询。
- **UA 伪装**：`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36`
- **双层保护**：CninfoClient 内建 `Semaphore(4)` 用于 API 查询限流，PdfDownloader 独立 `Semaphore(4)` 用于 PDF 下载限流。v0.1 查询和下载顺序执行不会冲突。
- **触发 403 后建议等待 5-10 分钟再重试**。`chaoxi debug test-page` 可用于确认恢复。

### 日志系统

- **格式**：JSONL（每行一个 JSON 对象）
- **位置**：`{CHAOXI_OUTPUT_DIR}/.chaoxi.log`（固定在默认输出目录，不受 `-o` 影响）
- **事件类型**：`session_start` / `params_parsed` / `query_done` / `download_done` / `extract_start` / `extract_done` / `session_done` / `session_error`
- **轮回**：超过 `MAX_LOG_LINES`（默认 500）自动删除前 10%
- **并发安全**：`asyncio.Lock` 防并发写入交错

### 错误处理总表

| 异常 | 用户提示 | 行为 |
|---|---|---|
| 股票代码不存在 | `未找到股票"{code}"，请检查代码是否正确。` | 终止（`Exit(1)`） |
| 参数非法 | `错误：{message}` + 修正建议 | 终止（`Exit(1)`） |
| HTTP 403 | `检测到限流 (HTTP 403)，建议等待 5-10 分钟后重试。` | 终止（`Exit(1)`） |
| 网络错误 | `巨潮网当前无响应，请稍后重试。` | 终止（`Exit(1)`） |
| 文件系统错误 | `{message}` | 终止（`Exit(1)`） |
| 无公告 | `未查询到公告。所选日期范围内无数据。` | 正常结束 |
| 结果截断（翻页上限） | `结果已截断（达到单次查询上限 3000 条）。建议缩小查询范围。` | 黄色警告，继续 |
| 结果截断（--max-results） | `本次查询命中 {n} 条公告，已截取前 {m} 条。` | 黄色警告，继续 |
| 单文件下载失败 | 无终端提示（详情在 `failed_downloads.json`） | 继续其余 |
| 全部下载失败 | 返回全 `status=failed` 的 AnnouncementList | CLI 提示后正常结束 |
| 单文件提取失败 | extraction.status 为 failed/error，详情在 JSON | 继续其余 |
| 提取部分乱码 | extraction.status 为 partial，标注乱码页数 | 成功页正常 |

### 硬限制

| 限制项 | 值 | 原因 |
|---|---|---|
| pageSize | 30 | 巨潮 API 硬限，传 40 仍返 30 |
| max_pages | 100 | 100×30=3000，安全上限 |
| max_results | 1-3000 | CLI 参数约束 |
| max_concurrent | 4（API 查询） | 超 4 触发 403 |
| max_concurrent | 4（PDF 下载） | 同上 |
| 日期范围 | 完整区间（不拆分） | API hasMore 翻页，无需日分片 |
| 板块过滤 | 客户端 pageColumn | 创业板/科创板无独立 plate 值 |
| industry | v0.1 不生效 | v0.2 将支持（`trade=中文行业名` 实测有效） |

### 提取机制

**流程**：
```
检查 status==downloaded → 检查 pdf_path 文件存在
→ process_pdf(pdf_path) → 判定提取状态
→ 写入 .md 文件 → 设置 md_path / extraction 字段
```

**提取引擎**：[pdf-inspector](https://github.com/firecrawl/pdf-inspector)（Rust 高性能、纯本地处理、MIT 协议）。

**执行模式**：串行（逐份处理）。pdf-inspector 内部使用 Rust 多线程并行，chaoxi 层面不再并发。

**四种状态**：
- `success`：text_based PDF，完整提取 Markdown
- `partial`：部分页含编码问题（`has_encoding_issues=True`），乱码页已丢弃，其余正常提取
- `failed`：扫描件/图片型 PDF（`pdf_type` 为 scanned/image_based），无法文本提取
- `error`：处理异常（PDF 损坏、超时等）

**确认提示**：待提取 PDF > 30 时弹确认（含页数估算）。`-y` 跳过。

**文件输出**：Markdown 文件写入 `{output_dir}/md/{code}_{id}_{title}.md`，
路径以相对路径记录在 `ann.md_path`。提取状态与元数据记录在 `ann.extraction` 字典中。

---

## 测试

```bash
uv run pytest                    # 全部测试（157 个）
uv run pytest tests/test_query.py -v  # 单个模块
```

测试依赖：pytest-asyncio + pytest-httpx（HTTP mock）。

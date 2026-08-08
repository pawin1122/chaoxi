---
name: chaoxi
description: >-
  Query and download A-share company announcements from cninfo.com.cn (巨潮网).
  Use when the user asks for stock filings, annual reports (年报), quarterly reports
  (一季报/半年报/三季报), board resolutions (董事会/监事会/股东会), keyword searches
  on announcement titles, or PDF downloads of filings. Trigger on 6-digit stock codes
  combined with "announcement", "filing", "report", "公告", or "披露".
  Do not use for general stock analysis, trading advice, investment research,
  or non-A-share markets (HK, US, etc.).
---

# chaoxi — A-Share Filings Client for cninfo.com.cn (巨潮网)

This skill provides access to the `chaoxi` CLI tool, which queries the public
disclosure system at cninfo.com.cn for A-share (沪深北) company announcements.

## Before You Begin

- Run `chaoxi debug test-page` first to verify network connectivity to cninfo.
- The tool must be invoked from the **project root**. Do not `cd` before running.
- All output goes to `./chaoxi_output/{timestamp}/`. Tell the user the exact
  path so they know where their files landed.

## Query Syntax

```
chaoxi [--codes CODE[,CODE...]] [--categories CAT[,CAT...]] [--keyword KEYWORD]
       [--board BOARD] [--start YYYY-MM-DD] [--end YYYY-MM-DD]
       [--json] [--max-results N] [--download] [-y] [-d DIR]
```

### Scoping rule

If no filters are given, the tool queries **all announcements across all boards
and categories from the last 90 days** (up to 3000 results). This is rarely what
the user wants. **Always confirm intent before running a filter-less query.**

### Stock codes (`--codes`)

6-digit string, comma-separated for multiple stocks:

| Code | Company | Board |
|---|---|---|
| `000001` | 平安银行 | 深主板 |
| `600519` | 贵州茅台 | 沪主板 |
| `300750` | 宁德时代 | 创业板 |
| `688981` | 中芯国际 | 科创板 |
| `838275` | 驱动力 | 北交所 |

### Announcement categories (`--categories`)

Use exactly the Chinese names below. Comma-separated for multiple.

Periodic reports:
  年报, 半年报, 一季报, 三季报

Corporate actions:
  权益分派, 董事会, 监事会, 股东会, 股权激励, 股权变动

Capital market:
  首发, 增发, 配股, 公司债, 可转债, 其他融资

Operations & governance:
  日常经营, 公司治理, 中介报告, 业绩预告

Special / regulatory:
  补充更正, 澄清致歉, 风险提示, 解禁, 特别处理和退市, 退市整理期

### Boards (`--board`)

深主板, 沪主板, 创业板, 科创板, 北交所

### Date range (`--start`, `--end`)

Format: `YYYY-MM-DD`. Defaults to [today − 90 days] through today. There is no
hard lower bound — you can query as far back as cninfo's archive allows.

### Keyword (`--keyword`)

**Client-side exact substring match on announcement title.** This is NOT a
server-side full-text or fuzzy search. Keep keywords short and precise
(e.g., `回购`, `分红`, `重组`). If the user expects semantic or fuzzy matching,
explain this limitation before proceeding.

### Max results (`--max-results`)

Integer 1–3000, default 3000. The API returns 30 items per page, so large
queries may involve many sequential paginated requests.

## Downloading PDFs

```
chaoxi --codes 000001 --download -y
chaoxi --codes 000001,600519 --categories 年报 --start 2026-01-01 --download -y
```

- `--download`: enables PDF retrieval.
- `-y` / `--yes`: skips the interactive confirmation prompt.
- `-d DIR`: sets a custom output directory (default: auto-generated timestamp).
- PDFs are saved to `./chaoxi_output/{timestamp}/pdfs/`.
- Concurrent downloads are capped at **4** internally to avoid HTTP 403.

**Safety check:** If a query returns **more than 100 PDFs** and `-y` was not
supplied, warn the user about the download volume before proceeding.

## JSON Output (`--json`)

Use this mode when you need to parse, sort, or filter results programmatically
— for example, feeding them into another analysis step.

```bash
chaoxi --codes 000001 --categories 年报 --start 2026-01-01 --json
```

Key response fields:

| Field | Meaning |
|---|---|
| `query.total` | Final count after deduplication and filtering |
| `query.total_raw` | Raw count from the API before dedup |
| `query.truncated` | `true` if the 3000-result pagination cap was hit |
| `announcements[].status` | `"downloaded"`, `"failed"`, `"skipped"`, or `null` |
| `announcements[].pdf_url` | Direct cninfo static server URL |
| `announcements[].announcement_id` | Unique identifier; can reconstruct PDF URLs |
| `announcements[].adjunct_size` | File size in KB as reported by cninfo |

## Management Commands

```
chaoxi clean --older-than 30d    # Remove sessions older than 30 days
chaoxi clean --keep 5            # Keep only the 5 most recent sessions
chaoxi log --today               # Show today's activity log
chaoxi log --today --level error # Show only errors from today
chaoxi debug test-page           # Connectivity check (run first!)
```

## Use-Case Cheat Sheet

| What the user says | Command to run |
|---|---|
| "查一下平安银行最近的公告" | `chaoxi --codes 000001` |
| "下载XX的年报PDF" | `chaoxi --codes {code} --categories 年报 --start {year}-01-01 --download -y` |
| "创业板最近业绩预告" | `chaoxi --board 创业板 --categories 业绩预告` |
| "搜标题含'回购'的公告" | `chaoxi --codes {code} --keyword 回购` |
| "XX公司董事会决议公告" | `chaoxi --codes {code} --categories 董事会` |
| "全市场今天的年报" | `chaoxi --categories 年报 --start {today}` |
| "导出JSON给我分析" | `chaoxi --codes {code} --json` |

## Hard Limits (Do Not Work Around)

- **30 per page** — API-enforced by cninfo; cannot be changed.
- **3000 max results per query** — if `query.truncated` is `true`, narrow the
  date range or add category filters to get complete data.
- **4 concurrent connections** — the tool enforces this internally. Exceeding
  it triggers HTTP 403 from cninfo. Do not attempt to parallelize with
  external scripts or subprocesses.
- **Client-side keyword matching only** — exact substring on title text. Not a
  server-side full-text index. Short, precise keywords yield the best results.
- **cninfo.com.cn upstream reliability** — the server can be slow or return
  empty pages during peak market hours (9:30–15:00 CST). If results seem
  incomplete, wait and retry.
- **A-share only** — covers 深交所, 上交所, and 北交所. Hong Kong, US, or
  other exchange filings are not supported by this tool.

## What NOT to Do

- Do not use for stock price analysis, trading signals, or investment advice.
- Do not use for non-A-share markets (HKEX, NYSE, NASDAQ, etc.).
- Do not attempt to parse, summarize, or semantically analyze downloaded PDF
  content — the tool only fetches the files, it does not read them.
- Do not run multiple concurrent `chaoxi` processes against the same output
  directory — each session is isolated by timestamp, and concurrent writes
  to the same output will corrupt results.

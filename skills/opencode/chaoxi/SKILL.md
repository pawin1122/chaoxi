---
name: chaoxi
metadata:
  version: "0.2.0"
  requires:
    bins: ["uv", "chaoxi"]
description: >-
  CLI tool for fetching A-share company announcements from cninfo.com.cn (巨潮网).
  Query filings by stock code, category, keyword, board, or date range.
  Download announcement PDFs and extract them to Markdown. Use when the user
  asks about A-share filings, annual reports, quarterly reports, board
  resolutions, shareholder meetings, or requests with stock codes +
  "announcement"/"filing"/"report"/"download"/"extract".
  Do not use for general Q&A, coding, translation, or semantic analysis of filings.
trigger: >-
  cninfo, 巨潮网, A-share announcement, stock filing, annual report,
  quarterly report, shareholder meeting, board resolution, equity distribution,
  IPO filing, A股公告, stock code + announcement/report/PDF
---

# chaoxi — cninfo A-Share Announcements CLI

## Install

```bash
cd /path/to/chaoxi
uv tool install .      # 全局安装（推荐），安装后 chaoxi 命令全局可用
# 或
uv sync                # 开发安装，通过 uv run chaoxi 运行
```

Verify:

```bash
uv run chaoxi --help
uv run chaoxi debug test-page
```

## Capabilities

- Query announcements by stock code (comma-separated for multiple)
- Filter by 26 announcement categories (Chinese names)
- Search by keyword in title (client-side exact match)
- Filter by board (深主板/沪主板/创业板/科创板/北交所)
- Date range queries (default: last 90 days)
- Download announcement PDFs
- Extract PDFs to structured Markdown (via `--extract`)

## Common Commands

```bash
# Single stock
chaoxi --codes 000001

# Multiple stocks
chaoxi --codes 000001,600519

# Market-wide annual reports
chaoxi --categories 年报 --start 2026-01-01

# Category + board
chaoxi --board 创业板 --categories 业绩预告

# Keyword search
chaoxi --codes 000001 --keyword 回购

# Download PDFs
chaoxi --codes 000001 --download -y

# Download and extract PDFs to Markdown
chaoxi --codes 601998 --categories 年报 --extract -y

# JSON output for AI parsing
chaoxi --codes 000001 --json

# Limit results
chaoxi --codes 000001 --max-results 10
```

## Management

```bash
chaoxi clean --older-than 30d    # Clean old sessions
chaoxi clean --keep 5            # Keep last 5 sessions
chaoxi log --today --level error # Today's errors
chaoxi debug test-page           # Connectivity check
```

## All Categories (use Chinese names)

年报, 半年报, 一季报, 三季报, 业绩预告, 权益分派, 董事会,
监事会, 股东会, 日常经营, 公司治理, 中介报告, 股权变动,
股权激励, 补充更正, 澄清致歉, 风险提示, 首发, 增发, 配股,
公司债, 可转债, 其他融资, 解禁, 特别处理和退市, 退市整理期

## Boards

深主板, 沪主板, 创业板, 科创板, 北交所

## All Parameters

| Parameter | Default | Description |
|---|---|---|
| `--start` | 90 days ago | Start date YYYY-MM-DD |
| `--end` | today | End date YYYY-MM-DD |
| `--codes` | all market | Stock codes, comma-separated |
| `--categories` | all 26 | Category names, comma-separated |
| `--keyword` | — | Title keyword (client exact match) |
| `--board` | all | 深主板/沪主板/创业板/科创板/北交所 |
| `--industry` | ignored | v0.2 |
| `--download` | false | Download PDF files |
| `--extract` | false | Download PDFs and extract to Markdown (implies --download, mutually exclusive) |
| `-y` / `--yes` | false | Skip download/extract confirmation |
| `-d` | auto | PDF output directory |
| `-o` | auto timestamp | Output directory |
| `--json` | false | Output JSON to stdout |
| `--max-results` | 3000 | Result limit (1-3000) |
| `--verbose` | false | Verbose logging |

## JSON Output Schema

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
      "title": "年度报告全文",
      "short_title": "年度报告",
      "announcement_id": "1225451412",
      "announcement_time": "2026-06-30",
      "announcement_type": "01010503||01",
      "pdf_url": "https://static.cninfo.com.cn/finalpage/2026-06-30/1225451412.PDF",
      "adjunct_size": 286,
      "pdf_path": "pdfs/000001_1225451412.pdf",
      "status": "downloaded",
      "error": null,
      "md_path": "md/000001_1225451412.md",
      "extraction": {"status": "success", "pdf_type": "text_based"}
    }
  ]
}
```

Fields:
- `total`: final count after dedup + filtering
- `total_raw`: raw API count before dedup
- `truncated`: true if pagination limit reached
- `status`: `"downloaded"` / `"failed"` / `"skipped"` / `null` (not downloaded)
- `md_path`: relative path to extracted Markdown file (only when `--extract` used)
- `extraction`: `{status: "success"|"partial"|"failed"|"error", pdf_type, ...}` — extraction result
- `announcement_type`: pipe-separated category codes

## Typical Use Cases

| User intent | Command |
|---|---|
| Recent filings for a stock | `chaoxi --codes {code}` |
| Annual reports | `chaoxi --codes {code} --categories 年报 --start YYYY-01-01` |
| Quarterly reports | `chaoxi --codes {code} --categories 一季报/半年报/三季报` |
| Board resolutions | `chaoxi --codes {code} --categories 董事会` |
| Shareholder meetings | `chaoxi --codes {code} --categories 股东会` |
| Dividend/equity | `chaoxi --codes {code} --categories 权益分派` |
| Market-wide category | `chaoxi --categories {category} --start {date}` |
| Board-specific | `chaoxi --board 创业板 --categories 业绩预告` |
| Download PDFs | `chaoxi --codes {code} --download -y` |
| Extract PDFs to Markdown | `chaoxi --codes {code} --categories 年报 --extract -y` |
| JSON for analysis | `chaoxi --codes {code} --json` |

## Limits

- pageSize: 30 per page (API hard limit)
- Max results: 3000 per query
- Concurrency: max 4 (HTTP 403 otherwise)
- PDF confirmation: prompts if > 50 files, `-y` to skip (extract prompts if > 30)
- Extracted Markdown: `./chaoxi_output/{timestamp}/md/`
- Output: `./chaoxi_output/{timestamp}/`
- Keyword search: client-side exact match on title, not server-side fuzzy
- Full docs: `doc/usage.md`

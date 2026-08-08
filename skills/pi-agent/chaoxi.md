---
name: chaoxi
description: >
  CLI tool for querying and downloading A-share company announcements from cninfo.com.cn (巨潮网).
  Use when the user mentions stock codes (6-digit), annual/quarterly reports, board resolutions,
  shareholder meetings, performance forecasts, IPO filings, or any A-share filing with keywords
  like "announcement", "filing", "report", "download". Do NOT use for stock price quotes, trading
  analysis, or non-A-share (HK/US/etc.) filings.
---

# chaoxi

Fetch A-share company announcements from cninfo.com.cn (巨潮网).

## Quick Start

```bash
cd {baseDir}/.. && uv sync
```

Verify:

```bash
chaoxi --help
```

## Usage

### Query Announcements

```bash
chaoxi --codes 000001
chaoxi --codes 000001,600519
chaoxi --categories 年报 --start 2026-01-01
chaoxi --board 创业板 --categories 业绩预告
chaoxi --keyword 回购
```

### Download Announcements (PDFs)

```bash
chaoxi --codes 000001 --download -y
```

### JSON Output

```bash
chaoxi --codes 000001 --json
```

### Management

```bash
chaoxi clean --older-than 30d
chaoxi log --today --level error
chaoxi debug test-page
```

## Options

| Flag | Description |
|------|-------------|
| `--codes <codes>` | Comma-separated 6-digit stock codes |
| `--categories <cats>` | Category names (see below) |
| `--keyword <kw>` | Free-text keyword search |
| `--board <board>` | Board name (see below) |
| `--start <date>` | Start date, e.g. `2026-01-01` |
| `--end <date>` | End date, e.g. `2026-06-30` |
| `--download` | Download matching PDFs |
| `-y` | Confirm download without prompt |
| `-d <dir>` | Output directory |
| `-o <path>` | Output file path (for JSON) |
| `--json` | Output as JSON |
| `--max-results <n>` | Max results (default 3000) |
| `--verbose` | Verbose logging |

## Categories (26)

年报, 半年报, 一季报, 三季报, 业绩预告, 权益分派, 董事会, 监事会,
股东会, 日常经营, 公司治理, 中介报告, 股权变动, 股权激励, 补充更正,
澄清致歉, 风险提示, 首发, 增发, 配股, 公司债, 可转债, 其他融资,
解禁, 特别处理和退市, 退市整理期

## Boards

深主板, 沪主板, 创业板, 科创板, 北交所

## Output Format

`--json` returns:

```json
{
  "query": { "codes": ["000001"], "start": "2026-01-01" },
  "total": 42,
  "announcements": [
    {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "title": "2025年年度报告",
      "announcement_id": "1234567890",
      "announcement_time": "2026-03-15T00:00:00",
      "pdf_url": "http://...",
      "adjunct_size": 1234567,
      "pdf_path": null,
      "status": null
    }
  ]
}
```

- `status`: `"downloaded"` / `"failed"` / `"skipped"` / `null`

## Limits

- 30 results per page, 3000 max per query
- 4 concurrent downloads max
- Output directory: `./chaoxi_output/{timestamp}/`

## When to Use

- User asks about A-share company filings, annual/quarterly reports
- User mentions stock codes along with "announcement", "filing", "report"
- User wants to download announcement PDFs from cninfo
- User searches filings by keyword, category, board, or date range

## When NOT to Use

- Stock price quotes, market data, or trading analysis
- HK, US, or other non-A-share market filings
- Semantic analysis of filing content (use the downloaded PDFs + other tools)
- General search or Q&A unrelated to cninfo announcements

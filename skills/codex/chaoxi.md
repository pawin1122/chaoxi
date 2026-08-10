---
name: chaoxi
description: Query and download A-share company announcements from cninfo.com.cn (巨潮网). Extract PDFs to Markdown. Use when the user provides stock codes and needs annual reports, quarterly reports, board resolutions, performance forecasts, repurchase announcements, shareholder meeting notices, or other cninfo filings. Supports filtering by stock code, category, keyword, board, and date range. Supports PDF download and Markdown extraction. Triggers: stock codes, "announcement", "annual report", "filing", "disclosure", "extract", "公告", "年报", "下载".
---

# chaoxi — A-Share Announcement CLI

CLI tool for querying and downloading A-share company announcements from cninfo.com.cn (巨潮网).

## Installation

```bash
uv sync
```

## When to Use

Use `chaoxi` when you need to:
- Query historical announcements for A-share stocks (e.g. 000001, 600519)
- Find announcements by category (annual reports, board resolutions, etc.)
- Search announcement titles by keyword
- Download announcement PDFs
- Extract PDFs to structured Markdown
- Manage locally cached announcement files

## Query Announcements

```bash
chaoxi --codes 000001                              # 单只股票
chaoxi --codes 000001,600519                       # 多只股票
chaoxi --categories 年报 --start 2026-01-01        # 年报，指定起始日期
chaoxi --board 创业板 --categories 业绩预告         # 板块+分类组合
chaoxi --keyword 回购                               # 标题关键词搜索
chaoxi --json                                       # JSON 输出到 stdout
chaoxi --max-results 10                             # 限制返回条数
```

## Download PDFs

```bash
chaoxi --codes 000001 --download -y                 # Download with auto-confirm
chaoxi --codes 000001 --download -y -d ./pdfs       # Custom download directory
```

## Extract PDFs to Markdown

```bash
chaoxi --codes 601998 --categories 年报 --extract -y # Download + extract
```

`--extract` implies `--download`. After downloading, each PDF is converted to Markdown
via `pdf-inspector` and saved to `./chaoxi_output/{timestamp}/md/`.
The terminal shows a new extraction column with four statuses:
✅ success, ⚠️N pages garbled, ❌ scanned, ❌ error.

## Local Cache Management

```bash
chaoxi clean --older-than 30d                       # 清理30天前的缓存
chaoxi clean --keep 5                               # 保留最近5条
chaoxi log --today --level error                    # 查看今日错误日志
chaoxi debug test-page                              # 测试页面连通性
```

## Parameter Reference

| Parameter | Default | Description |
|---|---|---|
| `--start` | 90 days ago | Start date YYYY-MM-DD |
| `--end` | today | End date YYYY-MM-DD |
| `--codes` | all | Comma-separated stock codes |
| `--categories` | all 26 | Chinese category names |
| `--keyword` | — | Exact title match |
| `--board` | all | 深主板/沪主板/创业板/科创板/北交所 |
| `--download` | false | Download PDF files |
| `--extract` | false | Download + extract to Markdown (implies --download) |
| `-y` / `--yes` | false | Skip confirmation prompts |
| `-d` | auto | PDF output directory |
| `-o` | auto | Output directory |
| `--json` | false | Output JSON to stdout |
| `--max-results` | 3000 | 1-3000 |
| `--verbose` | false | Verbose output |

## Categories (26)

年报、半年报、一季报、三季报、业绩预告、权益分派、董事会、监事会、股东会、日常经营、公司治理、中介报告、股权变动、股权激励、补充更正、澄清致歉、风险提示、首发、增发、配股、公司债、可转债、其他融资、解禁、特别处理和退市、退市整理期

## JSON Output Schema

```json
{
  "query": {"start","end","codes","categories","total","total_raw","total_filtered","truncated","fetched_at"},
  "announcements": [{"stock_code","stock_name","title","short_title","announcement_id","announcement_time","announcement_type","pdf_url","adjunct_size","pdf_path","status","error","md_path","extraction"}]
}
```

Key fields:
- `total`: final count after dedup + filtering
- `total_raw`: raw API count
- `truncated`: pagination cap reached
- `status`: `"downloaded"` | `"failed"` | `"skipped"` | `null`
- `md_path`: relative path to extracted `.md` file (`--extract` only)
- `extraction`: `{status: "success"|"partial"|"failed"|"error", pdf_type, garbled_pages?, page_count?, error?}`

## System Limits

- 30 per page, 3000 max results per query
- 4 concurrent connections max (HTTP 403 otherwise)
- Download confirm: prompts if > 50 files, `-y` to skip
- Extract confirm: prompts if > 30 PDFs, `-y` to skip
- Output: `./chaoxi_output/{timestamp}/`
- Markdown: `./chaoxi_output/{timestamp}/md/`

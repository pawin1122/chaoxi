---
name: chaoxi
description: 查询和下载A股上市公司公告。当用户提供股票代码并需要年报、季报、董事会决议、业绩预告、回购公告、股东会通知等巨潮网(cninfo.com.cn)公告时使用。支持按代码、分类、关键词、板块、日期范围检索，支持PDF下载和管理。触发词：股票代码、"公告"、"年报"、"季报"、"董事会"、"下载公告"、"巨潮网"。
---

# 潮汐 (chaoxi) — A股公告查询与下载

CLI 工具，从 cninfo.com.cn（巨潮网）查询和下载 A 股上市公司公告。

## 安装

项目位于当前工作区，使用 uv 管理：

```bash
uv sync
```

## 使用 chaoxi 的时机

在任何任务中，当需要：
- 查询某只A股（如000001、600519）的历史公告
- 查找特定类别公告（年报、季报、业绩预告、董事会决议等）
- 按关键词搜索公告标题
- 下载公告PDF原文
- 管理本地缓存的公告文件

直接调用 `chaoxi` 命令即可。

## 查询公告

```bash
chaoxi --codes 000001                              # 单只股票
chaoxi --codes 000001,600519                       # 多只股票
chaoxi --categories 年报 --start 2026-01-01        # 年报，指定起始日期
chaoxi --board 创业板 --categories 业绩预告         # 板块+分类组合
chaoxi --keyword 回购                               # 标题关键词搜索
chaoxi --json                                       # JSON 输出到 stdout
chaoxi --max-results 10                             # 限制返回条数
```

## 下载公告PDF

```bash
chaoxi --codes 000001 --download -y                 # 下载+跳过确认
chaoxi --codes 000001 --download -y -d ./pdfs       # 指定下载目录
```

## 本地缓存管理

```bash
chaoxi clean --older-than 30d                       # 清理30天前的缓存
chaoxi clean --keep 5                               # 保留最近5条
chaoxi log --today --level error                    # 查看今日错误日志
chaoxi debug test-page                              # 测试页面连通性
```

## 参数速查

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--start` | 90天前 | 起始日期 YYYY-MM-DD |
| `--end` | 今天 | 结束日期 YYYY-MM-DD |
| `--codes` | 全部 | 逗号分隔的股票代码 |
| `--categories` | 全部26类 | 中文分类名 |
| `--keyword` | — | 标题精确匹配 |
| `--board` | 全部 | 深主板/沪主板/创业板/科创板/北交所 |
| `--download` | false | 启用PDF下载 |
| `-y` / `--yes` | false | 跳过确认 |
| `-d` | 自动 | PDF保存目录 |
| `-o` | 自动 | 输出目录 |
| `--json` | false | stdout输出JSON |
| `--max-results` | 3000 | 1-3000 |
| `--verbose` | false | 详细输出 |

## 公告分类（26类）

年报、半年报、一季报、三季报、业绩预告、权益分派、董事会、监事会、股东会、日常经营、公司治理、中介报告、股权变动、股权激励、补充更正、澄清致歉、风险提示、首发、增发、配股、公司债、可转债、其他融资、解禁、特别处理和退市、退市整理期

## JSON 输出结构

```json
{
  "query": {"start","end","codes","categories","total","total_raw","total_filtered","truncated","fetched_at"},
  "announcements": [{"stock_code","stock_name","title","short_title","announcement_id","announcement_time","announcement_type","pdf_url","adjunct_size","pdf_path","status","error"}]
}
```

关键字段：
- `total`：最终条数（去重+过滤后）
- `total_raw`：API原始条数
- `truncated`：达到分页上限
- `status`：`"downloaded"` | `"failed"` | `"skipped"` | `null`

## 系统限制

- 每页30条，每次查询最多3000条
- 最大4并发（超过返回403）
- 输出目录：`./chaoxi_output/{timestamp}/`

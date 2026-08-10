# v0.2.0 版本更新说明

> 发布日期：2026-08-10  
> 版本定位：PDF 结构化转文档功能。下载公告 PDF 后自动提取为 Markdown。

## 新功能

### `--extract` 命令：PDF 转 Markdown

下载公告 PDF 后自动逐份提取为结构化 Markdown 文本，无需外部 PDF 工具。

```bash
# 下载年报并提取为 Markdown
chaoxi --codes 601998 --categories 年报 --extract -y

# 仅下载不提取
chaoxi --codes 601998 --categories 年报 --download -y
```

- `--extract` 隐含 `--download`，两者互斥
- 提取引擎：[pdf-inspector](https://github.com/firecrawl/pdf-inspector)（Firecrawl 出品，MIT 协议，Rust 高性能，纯本地处理）
- 输出：PDF 保留在 `pdfs/`，Markdown 输出到 `md/` 目录

### 提取四态标注

每条公告的提取结果分为四种状态，终端表格与 JSON 一致：

| 状态 | 显示 | 含义 |
|---|---|---|
| `success` | `✅` | 完整提取，text_based PDF |
| `partial` | `⚠️N页` | 部分编码异常，N 页已丢弃 |
| `failed` | `❌扫描件` | 扫描件/图片型 PDF，无法文本提取 |
| `error` | `❌错误` | 提取过程异常 |

JSON 输出新增字段：
- `md_path`：Markdown 文件相对路径
- `extraction`：`{status, pdf_type, garbled_pages?, page_count?, error?}`

### 提取确认提示

待提取 PDF > 30 时弹确认，含 AI 处理建议。`-y` 跳过。

### 下载确认提示增强

PDF > 50 时追加建议文案："建议：仅生成 JSON 文件，后续交由 AI 处理 PDF 下载与识别"。

## 技术要点

- **pdf-inspector 实测**：中信银行（601998）A 股 5 份年报（400+ 页/份），一律 text_based，0.5~10 秒/份，输出 40 万字符高质量 Markdown。H 股含部分无 ToUnicode CMap 字体的乱码，按 partial 标注
- **提取串行执行**：pdf-inspector 内部并行（Rust 多线程），chaoxi 层面不做并发
- **单文件失败兼容**：单个 PDF 提取失败不阻断后续处理

## 改动清单

| 类别 | 文件 | 说明 |
|---|---|---|
| **新增** | `src/chaoxi/extractor.py` | PdfExtractor + ExtractionTracker |
| **修改** | `src/chaoxi/models.py` | Announcement 新增 `md_path` / `extraction` 字段 |
| **修改** | `src/chaoxi/cli/params.py` | QueryConfig 新增 `extract_mode`，`--extract` 与 `--download` 互斥校验 |
| **修改** | `src/chaoxi/main.py` | CLI 新增 `--extract` 参数，主流程新增提取阶段 |
| **修改** | `src/chaoxi/output/formatter.py` | 终端表格新增"提取"列 + 提取汇总 |
| **修改** | `src/chaoxi/downloader/downloader.py` | 下载 >50 确认提示追加 AI 建议 |
| **修改** | `pyproject.toml` | 新增 `pdf-inspector>=0.2.6` 依赖 |
| **修改** | `README.md` | 新增"致谢"节（pdf-inspector + 9 个参考项目） |

## 致谢

- [firecrawl/pdf-inspector](https://github.com/firecrawl/pdf-inspector) — PDF 结构化提取引擎（MIT）
- [rollysys/use_cninfo](https://github.com/rollysys/use_cninfo) 等 9 个参考项目（设计思路借鉴，未使用源码）

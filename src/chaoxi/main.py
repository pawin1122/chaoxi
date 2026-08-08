from __future__ import annotations

import asyncio
import sys
import traceback
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from typer import Option

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from chaoxi.cli.clean import Cleaner
from chaoxi.cli.debug import Debugger
from chaoxi.cli.log_cmd import LogViewer
from chaoxi.cli.params import QueryConfig, build_query_config
from chaoxi.downloader.downloader import PdfDownloader
from chaoxi.exceptions import (
    FileSystemError,
    NetworkError,
    RateLimitError,
    StockNotFoundError,
    ValidationError,
)
from chaoxi.http_client import CninfoClient
from chaoxi.logging import LogEngine
from chaoxi.output.formatter import OutputFormatter
from chaoxi.query.engine import QueryEngine
from chaoxi.utils.config import AppSettings, get_settings

app = typer.Typer(
    name="chaoxi",
    help=(
        "巨潮网公告数据获取工具。\n\n"
        "查询示例：\n"
        "  chaoxi --codes 000001                          # 平安银行近期公告\n"
        "  chaoxi --categories 年报 --start 2026-01-01    # 2026年全市场年报\n"
        "  chaoxi --codes 000001 --keyword 回购 --download # 下载平安银行回购相关公告PDF\n\n"
        "管理命令：\n"
        "  chaoxi clean --older-than 30d  # 清理30天前数据\n"
        "  chaoxi debug test-page          # 测试连通性\n"
        "  chaoxi log --today              # 查看今日日志"
    ),
)


@app.callback(invoke_without_command=True)
def chaoxi(
    ctx: typer.Context,
    start: str | None = Option(None, "--start", help="公告日期起 (YYYY-MM-DD)"),
    end: str | None = Option(None, "--end", help="公告日期止 (YYYY-MM-DD)"),
    codes: str | None = Option(None, "--codes", help="股票代码，逗号分隔"),
    categories: str | None = Option(None, "--categories", help="公告分类，逗号分隔"),
    keyword: str | None = Option(None, "--keyword", help="标题关键词"),
    board: str | None = Option(None, "--board", help="板块（深主板/沪主板/创业板/科创板/北交所）"),
    industry: str | None = Option(None, "--industry", help="行业"),
    download: bool = Option(False, "--download", help="开启 PDF 下载模式"),
    yes: bool = Option(False, "--yes", "-y", help="跳过下载确认提示"),
    download_dir: str | None = Option(None, "--download-dir", "-d", help="PDF 存放目录"),
    o: str | None = Option(None, "-o", help="输出目录"),
    json_stdout: bool = Option(False, "--json", help="输出 JSON 到 stdout（管道模式）"),
    max_results: int = Option(3000, "--max-results", help="结果数量上限 (1-3000)"),
    verbose: bool = Option(False, "--verbose", help="详细输出"),
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    try:
        settings = get_settings()
        config = build_query_config(
            start, end, codes, categories, keyword, board, industry,
            max_results, download, yes, download_dir, json_stdout, o, verbose,
            settings,
        )
    except ValidationError as e:
        Console().print(f"[red]错误：{e.message}[/red]")
        if e.suggestion:
            Console().print(f"[dim]{e.suggestion}[/dim]")
        raise typer.Exit(code=1)
    asyncio.run(_main_async(config, settings))


async def _main_async(config: QueryConfig, settings: AppSettings) -> None:
    logger = LogEngine(settings)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        await logger.write("session_start", session_id, {"args": sys.argv})
        await logger.write("params_parsed", session_id, {"config": config.model_dump(mode="json")})

        async with CninfoClient(settings) as client:
            engine = QueryEngine(config, settings, client)
            result = await engine.execute()
            await logger.write(
                "query_done", session_id,
                {"total": result.query.total, "total_raw": result.query.total_raw},
            )

            if result.query.total == 0:
                Console().print("[yellow]未查询到公告。所选日期范围内无数据。[/yellow]")
                return

            if result.query.truncated:
                Console().print(
                    "[yellow]结果已截断（达到单次查询上限 3000 条）。建议缩小查询范围。[/yellow]"
                )

            if result.query.total >= config.max_results:
                Console().print(
                    f"[yellow]本次查询命中 {result.query.api_total} 条公告，"
                    f"已截取前 {config.max_results} 条（--max-results={config.max_results}）。[/yellow]"
                )

            output_dir = _output_dir(config, settings)

            if config.download_mode:
                pdf_dir = config.download_dir or f"{output_dir}/pdfs"
                downloader = PdfDownloader(
                    client, settings, pdf_dir, output_dir, config.skip_confirm,
                )
                result.announcements, tracker = await downloader.download(result.announcements)
                await logger.write(
                    "download_done", session_id,
                    {"success": tracker.success, "failed": tracker.failed, "skipped": tracker.skipped},
                )

            formatter = OutputFormatter(
                settings,
                None if config.json_stdout else output_dir,
                config.json_stdout,
            )
            await formatter.output(result)

            await logger.write("session_done", session_id, {"status": "ok"})

    except ValidationError as e:
        Console().print(f"[red]错误：{e.message}[/red]")
        if e.suggestion:
            Console().print(f"[dim]{e.suggestion}[/dim]")
        await logger.write("session_error", session_id, {"error": str(e)}, "error")
        raise typer.Exit(code=1)

    except StockNotFoundError as e:
        Console().print(f"[red]{e.message}[/red]")
        await logger.write("session_error", session_id, {"error": str(e)}, "error")
        raise typer.Exit(code=1)

    except RateLimitError as e:
        Console().print(f"[red]{e.message}[/red]")
        await logger.write("session_error", session_id, {"error": str(e)}, "error")
        raise typer.Exit(code=1)

    except NetworkError:
        Console().print("[red]巨潮网当前无响应，请稍后重试。[/red]")
        await logger.write("session_error", session_id, {"error": "NetworkError"}, "error")
        raise typer.Exit(code=1)

    except FileSystemError as e:
        Console().print(f"[red]{e.message}[/red]")
        await logger.write("session_error", session_id, {"error": str(e)}, "error")
        raise typer.Exit(code=1)

    except Exception as e:
        Console().print(f"[red]未知错误：{e}[/red]")
        await logger.write(
            "session_error", session_id,
            {"error": str(e), "traceback": traceback.format_exc()}, "error",
        )
        raise typer.Exit(code=1)

    finally:
        try:
            await logger.write("session_end", session_id, {"status": "terminated"})
        except Exception:
            pass


@app.command()
def clean(
    older_than: str | None = Option(None, "--older-than", help="删除超过N天的目录，如 30d"),
    max_size: str | None = Option(None, "--max-size", help="从最旧删起，直到总大小≤上限，如 500M"),
    keep: int | None = Option(None, "--keep", help="仅保留最近N次"),
    dry_run: bool = Option(False, "--dry-run", help="预览模式"),
) -> None:
    settings = get_settings()
    Cleaner(settings).clean(older_than, max_size, keep, dry_run)


@app.command()
def debug(
    action: str = typer.Argument(..., help="test-page / inspect-api / list-headers"),
) -> None:
    async def _run() -> None:
        async with CninfoClient(get_settings()) as client:
            dbg = Debugger(client)
            await dbg.run(action)

    asyncio.run(_run())


@app.command()
def log(
    tail: int = Option(20, "--tail", help="显示最近N条"),
    today: bool = Option(False, "--today", help="仅今天"),
    session: str | None = Option(None, "--session", help="查看某次会话"),
    level: str | None = Option(None, "--level", help="error/warn/info/debug"),
    clear: bool = Option(False, "--clear", help="清空日志"),
) -> None:
    engine = LogEngine(get_settings())
    viewer = LogViewer(engine)
    if clear:
        viewer.clear()
    else:
        viewer.view(tail, today, session, level)


def _output_dir(config: QueryConfig, settings: AppSettings) -> str:
    if config.output_dir:
        return config.output_dir
    return f"{settings.chaoxi_output_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"

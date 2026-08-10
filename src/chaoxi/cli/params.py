from __future__ import annotations

from datetime import date, datetime, timedelta

from pydantic import BaseModel, Field, model_validator

from chaoxi.cli._constants import BOARD_MAP, CATEGORY_NAME_MAP, INDUSTRY_LIST
from chaoxi.exceptions import ValidationError
from chaoxi.utils.config import AppSettings


class QueryConfig(BaseModel):
    start_date: date
    end_date: date
    stock_codes: list[str] = []
    categories: list[str] = []
    keyword: str | None = None
    board: str | None = None
    industry: str | None = None
    max_results: int = Field(default=3000, ge=1, le=3000)
    download_mode: bool = False
    extract_mode: bool = False
    skip_confirm: bool = False
    download_dir: str | None = None
    output_dir: str | None = None
    json_stdout: bool = False
    verbose: bool = False

    @model_validator(mode="after")
    def check_date_order(self) -> QueryConfig:
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("起始日期不能晚于结束日期")
        return self


def _parse_date_or_default(raw: str | None, default: date, param_name: str) -> date:
    if raw is None:
        return default
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(
            message=f'无效的日期"{raw}"',
            suggestion="请输入 YYYY-MM-DD 格式的日期",
        )


def _parse_codes(raw: str | None) -> list[str]:
    if raw is None:
        return []
    parts = [p.strip() for p in raw.split(",")]
    parts = [p for p in parts if p]
    result: list[str] = []
    seen: set[str] = set()
    for code in parts:
        if not (len(code) == 6 and code.isdigit()):
            raise ValidationError(
                message=f'无效的代码"{code}"',
                suggestion="请输入6位数字股票代码",
            )
        if code not in seen:
            seen.add(code)
            result.append(code)
    return result


def _parse_categories(raw: str | None) -> list[str]:
    if raw is None:
        return []
    parts = [p.strip() for p in raw.split(",")]
    parts = [p for p in parts if p]
    result: list[str] = []
    seen: set[str] = set()
    for cat in parts:
        if cat not in CATEGORY_NAME_MAP:
            cats_hint = "、".join(sorted(CATEGORY_NAME_MAP.keys()))
            raise ValidationError(
                message=f'未知分类"{cat}"',
                suggestion=f"请从以下分类中选择：{cats_hint}",
            )
        if cat not in seen:
            seen.add(cat)
            result.append(cat)
    return result


def _parse_multi_value(
    raw: str | None,
    valid_set: set[str],
    param_name: str,
) -> list[str]:
    if raw is None:
        return []
    parts = [p.strip() for p in raw.split(",")]
    parts = [p for p in parts if p]
    result: list[str] = []
    seen: set[str] = set()
    for val in parts:
        if val not in valid_set:
            hint = "、".join(sorted(valid_set))
            raise ValidationError(
                message=f'未知{param_name}"{val}"',
                suggestion=f"请从以下{param_name}中选择：{hint}",
            )
        if val not in seen:
            seen.add(val)
            result.append(val)
    return result


def build_query_config(
    start: str | None,
    end: str | None,
    codes: str | None,
    categories: str | None,
    keyword: str | None,
    board: str | None,
    industry: str | None,
    max_results: int,
    download: bool,
    extract: bool,
    yes: bool,
    download_dir: str | None,
    json_stdout: bool,
    o: str | None,
    verbose: bool,
    settings: AppSettings,
) -> QueryConfig:
    if max_results < 1 or max_results > 3000:
        raise ValidationError(
            message="--max-results 超出范围",
            suggestion="请输入 1 到 3000 之间的整数",
        )

    if download and extract:
        raise ValidationError(
            message="--download 与 --extract 互斥，请只选择一种。",
            suggestion="--extract 已隐含下载功能，无需同时指定 --download",
        )

    if json_stdout and o is not None:
        raise ValidationError(
            message="--json（stdout 模式）与 -o（文件输出）互斥，请只选择一种。",
        )

    today = date.today()
    end_date = _parse_date_or_default(end, today, "--end")
    default_start = end_date - timedelta(days=settings.default_lookback_days)
    start_date = _parse_date_or_default(start, default_start, "--start")

    parsed_codes = _parse_codes(codes)
    parsed_categories = _parse_categories(categories)

    parsed_board: str | None = None
    if board is not None:
        board = board.strip()
        if board not in BOARD_MAP:
            boards_hint = "/".join(BOARD_MAP.keys())
            raise ValidationError(
                message=f'未知板块"{board}"',
                suggestion=f"请从以下板块中选择：{boards_hint}",
            )
        parsed_board = board

    parsed_industry: str | None = None
    if industry is not None:
        industry = industry.strip()
        industry_set: set[str] = set(INDUSTRY_LIST)
        if industry not in industry_set:
            ind_hint = "、".join(INDUSTRY_LIST)
            raise ValidationError(
                message=f'未知行业"{industry}"',
                suggestion=f"请从以下行业中选择：{ind_hint}",
            )
        parsed_industry = industry

    kw = keyword.strip() if keyword else None

    return QueryConfig(
        start_date=start_date,
        end_date=end_date,
        stock_codes=parsed_codes,
        categories=parsed_categories,
        keyword=kw,
        board=parsed_board,
        industry=parsed_industry,
        max_results=max_results,
        download_mode=download or extract,
        extract_mode=extract,
        skip_confirm=yes,
        download_dir=download_dir,
        output_dir=o,
        json_stdout=json_stdout,
        verbose=verbose,
    )

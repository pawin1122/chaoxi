# v0.1.1 版本更新说明

> 发布日期：2026-08-09  
> 版本定位：Bug 修复 & 补漏，无新功能。

## Bug 修复

- **`request_interval` 配置项不生效**：`.env` 中的 `CNINFO_REQUEST_INTERVAL` 现在真正控制请求间隔下限，不再被硬编码忽略（`http_client.py`）
- **`sys.path` 脏 hack 移除**：删除 `main.py` 中绕过包安装路径的 `sys.path.insert` 语句
- **测试 import 路径统一**：6 个测试文件 24 处 `from src.chaoxi` 全部改为 `from chaoxi`，与源码 import 一致
- **`debug test-page` 404 修复**：`http_client.py` 的 `base_url` 已含 `/new` 路径，但 `_init_cookies()` 和 `test_page()` 重复拼接了 `/new/` 前缀，导致请求了 `/new/new/index`（404）。改为 `/index`，同步修复 12 处测试 mock URL。此问题同时影响 cookie 初始化环节

## 补漏

- **`--industry` 警告加强**：行业筛选参数现由 CLI 入口统一用 Rich 醒目标注未实现，不再依赖 stderr 隐蔽提示
- **下载总量显示**：PDF 下载完成后展示总文件大小（如 "共 2.3MB"），不再仅显示文件计数
- **`--version` 支持**：`chaoxi --version` 可查看当前版本号，通过 Typer `Option(callback=...)` + `is_eager=True` 实现
- **尺寸单位统一**：清理预览与查询表格的文件大小统一使用 1024-based 二进制单位，消除不一致

## 代码清理

- **`LogViewer.clear()` 死分支移除**：删除 never-reachable 的 async else 分支
- **`_compute_date_shards` 伪抽象移除**：去除永远返回单分片的冗余方法及 for 循环脚手架

## 文档

- **README 全面重写**：安装方式改为全局安装 (`uv tool install .`) 优先，新增 Skills 手动部署说明，补充 `CNINFO_REQUEST_INTERVAL` 配置项
- **INSTALL.md 内容整合至 README**
- **Skills 文档修正**：修复安全阈值不匹配 (100→50)、`-o` 参数描述错误、日期格式不一致等 4 处问题
- **版本号升级**：`pyproject.toml`、`__version__.py`、`doc/usage.md` 统一标记 `0.1.1`

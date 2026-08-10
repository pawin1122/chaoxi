# chaoxi v0.1.0 安装说明

## 适用环境

| 项目 | 要求 |
|---|---|
| 操作系统 | macOS / Linux / Windows (WSL) |
| Python | 3.12 或更高版本 |
| 包管理器 | [uv](https://docs.astral.sh/uv/)（推荐）或 pip |
| 网络 | 需能访问 `cninfo.com.cn`（巨潮网） |

## 安装步骤

### 方式一：解压包安装（推荐）

```bash
# 1. 解压
tar xzf chaoxi-v0.1.0.tar.gz
cd chaoxi-v0.1.0

# 2. 安装依赖
uv sync

# 3. 验证
uv run chaoxi --help
uv run chaoxi debug test-page
```

### 方式二：Git 安装

```bash
git clone <repo-url>
cd chaoxi
uv sync
uv run chaoxi --help
```

### 方式三：pip 安装（全局命令）

```bash
tar xzf chaoxi-v0.1.0.tar.gz
cd chaoxi-v0.1.0
pip install .
chaoxi --help
```

## 配置（可选）

```bash
cp .env.example .env
# 编辑 .env 根据需要修改
```

全部配置项有默认值，不配置也可直接使用。

## 快速测试

```bash
# 连通性
chaoxi debug test-page

# 查询平安银行近 90 天公告
chaoxi --codes 000001

# 下载年报
chaoxi --codes 600036 --categories 年报 --download -y

# 查看日志
chaoxi log --tail 30
```

## 文档

| 文件 | 说明 |
|---|---|
| `README.md` | 项目概览 |
| `doc/usage.md` | 完整使用手册 |
| `index.toml` | 全部文件索引 |
| `CHANGELOG.md` | 版本变更记录 |

## 卸载

```bash
# uv 安装：删除项目目录即可
rm -rf chaoxi-v0.1.0

# pip 安装：
pip uninstall chaoxi
```

## 版本

v0.1.0 — 2026-08-08

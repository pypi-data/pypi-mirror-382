# Snail Job Python 配置指南

## 概述

Snail Job Python 使用 `pydantic-settings` 进行配置管理，支持环境变量、`.env` 文件和程序化配置。

## 配置方式

### 1. 环境变量配置（推荐）

```bash
# 设置环境变量
export SNAIL_SERVER_HOST=192.168.1.100
export SNAIL_SERVER_PORT=17888
export SNAIL_LOG_LEVEL=DEBUG

# 运行程序
python your_app.py
```

### 2. .env 文件配置

创建 `.env` 文件：

```env
# 服务器配置
SNAIL_SERVER_HOST=127.0.0.1
SNAIL_SERVER_PORT=17888

# 客户端配置
SNAIL_VERSION=1.1.0
SNAIL_HOST_IP=127.0.0.1
SNAIL_HOST_PORT=17889
SNAIL_NAMESPACE=764d604ec6fc45f68cd92514c40e9e1a
SNAIL_GROUP_NAME=snail_job_demo_group
SNAIL_TOKEN=SJ_Wyz3dmsdbDOkDujOTSSoBjGQP1BMsVnj
SNAIL_LABELS=env:dev,app:demo

# 日志配置
SNAIL_LOG_LEVEL=INFO
SNAIL_LOG_FORMAT=%(asctime)s | %(name)-22s | %(levelname)-8s | %(message)s
SNAIL_LOG_REMOTE_INTERVAL=10
SNAIL_LOG_REMOTE_BUFFER_SIZE=10
SNAIL_LOG_LOCAL_FILENAME=log/snailjob.log
SNAIL_LOG_LOCAL_BACKUP_COUNT=2
```

### 3. 程序化配置

```python
from snailjob.config import configure_settings

# 在导入其他 snailjob 模块之前配置
settings = configure_settings(
    snail_server_host="192.168.1.100",
    snail_log_level="DEBUG",
)

# 现在可以正常使用 snailjob
from snailjob import client_main
client_main()
```

## 正确的使用方式

### ✅ 推荐方式

```python
# 方式1: 使用环境变量
import os
os.environ['SNAIL_SERVER_HOST'] = '192.168.1.100'

from snailjob import client_main
client_main()

# 方式2: 程序化配置
from snailjob.config import configure_settings
configure_settings(snail_server_host="192.168.1.100")

from snailjob import client_main
client_main()
```

## 使用 settings 对象

新版本推荐直接使用 settings 对象访问配置：

```python
from snailjob.config import get_snailjob_settings

# 获取配置实例
settings = get_snailjob_settings()

# 访问配置项
print(f"服务器地址: {settings.snail_server_host}")
print(f"日志级别: {settings.snail_log_level}")

# 每次访问都会获取最新值
configure_settings(snail_server_host="192.168.1.200")
print(f"更新后服务器地址: {settings.snail_server_host}")
```

## 配置参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `snail_server_host` | str | 127.0.0.1 | 服务器主机地址 |
| `snail_server_port` | int | 17888 | 服务器端口 |
| `snail_host_ip` | str | 127.0.0.1 | 客户端主机IP |
| `snail_host_port` | int | 17889 | 客户端端口 |
| `snail_namespace` | str | 764d604ec6fc45f68cd92514c40e9e1a | 命名空间 |
| `snail_group_name` | str | snail_job_demo_group | 组名 |
| `snail_token` | str | SJ_Wyz3dmsdbDOkDujOTSSoBjGQP1BMsVnj | 认证令牌 |
| `snail_labels` | str | env:dev,app:demo | 标签配置 |
| `snail_log_level` | str | INFO | 日志级别 |
| `snail_log_format` | str | %(asctime)s \| %(name)-22s \| %(levelname)-8s \| %(message)s | 日志格式 |
| `snail_log_remote_interval` | int | 10 | 远程日志上报间隔(秒) |
| `snail_log_remote_buffer_size` | int | 10 | 远程日志缓冲区大小 |
| `snail_log_local_filename` | str | log/snailjob.log | 本地日志文件名 |
| `snail_log_local_backup_count` | int | 60 | 本地日志备份数量 |

## 迁移指南

从旧版本迁移到新版本：

### 旧版本（已废弃）

```python
from snailjob.cfg import SNAIL_SERVER_HOST, SNAIL_USE_GRPC
print(SNAIL_SERVER_HOST)
```

### 新版本（推荐）

```python
from snailjob.config import get_snailjob_settings
settings = get_snailjob_settings()
print(settings.snail_server_host)
```

## 最佳实践

1. **在应用启动时配置**：在导入 snailjob 模块之前完成所有配置
2. **使用环境变量**：生产环境推荐使用环境变量
3. **使用 .env 文件**：开发环境可以使用 .env 文件
4. **程序化配置**：需要动态配置时使用 `configure_settings()`
5. **避免重复配置**：配置完成后不要重复调用 `configure_settings()`

## 故障排除

### 配置不生效

检查配置顺序：

```python
# 确保配置在导入之前
from snailjob.config import configure_settings
configure_settings(snail_server_host="192.168.1.100")

# 然后导入其他模块
from snailjob import client_main
```

### 环境变量不生效

检查环境变量名称是否正确（区分大小写）：

```bash
# 正确
export SNAIL_SERVER_HOST=192.168.1.100

# 错误
export snail_server_host=192.168.1.100
```

### .env 文件不生效

检查文件路径和格式：

```python
from pathlib import Path
from dotenv import load_dotenv

# 确保 .env 文件存在
env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)
else:
    print("警告: .env 文件不存在")
```

# Change Log

## 0.1.3 (2025-10-09)

- fix: 每次获取headers时，不该生成一个新的host_id (dhb52, 2025-10-09)
- refactor: settings.py => config.py，与全局变量 settings 做区分 (dhb52, 2025-10-02)
- feat(0.1.3): 增加 snail_labels 验证，端口参数修改为 int 类型。 (dhb52, 2025-10-02)

## 0.1.2 (2025-10-02)

- chore: 去除 `SNAIL_VERSION`, 合并 `system-version` 配置项，使用 frozen=True 对常量配置进行冻结
- feat: 增加 ruff 的 dev 依赖，避免没有全局安装过 ruff 工具
- chore: 去除 `aiohttp` 模式以及 `SNAIL_USE_GRPC` 配置项

## 0.1.1 (2025-10-01)

- feat: 增加本地开发验证方式
- fix: 修正settings.system_version 字段 (dhb52, 2025-10-01)

## 0.1.0 (2025-10-01)

- feat: 增加docker 库开发测试环境
- perf: 优化 protobuf grpc 代码生成脚本 (dhb52, 2025-10-01)
- feat: 采用绝对路径 import (dhb52, 2025-10-01)
- feat: 增加 load_dotenv 加载 .env 文件 (dhb52, 2025-10-01)
- feat: 使用pydantic-settings，实现配置延迟读取，兼容 dotenv (dhb52, 2025-10-01)
- lint: 修复 lint 错误 (dhb52, 2025-10-01)

## 0.0.5 (2025-06-27)

- feat: 同步执行器 (dhb52, 2025-06-27)

## 0.0.4 (2025-05-20)

- feat: 默认包管理器 `uv` (dhb52, 2025-05-20)
- feat: 内置执行器PowerShellExecutor + CMDExecutor (dhb52, 2025-04-07)
- feat: 内置执行器 ShellExecutor (dhb52, 2025-04-07)
- perf: 类型hint 细微调整 (dhb52, 2025-04-07)
- feat: 内置执行器 HttpExecutor (dhb52, 2025-04-07)
- fix: 修正 merge demo 的错误 (dhb52, 2025-02-17)
- fix: 用户代码抛出异常需要上报失败 (dhb52, 2025-02-06)

## 0.0.3 (2024-12-31)

- fix: 在 0.0.0.0 上启动客户端服务器 (dhb52, 2024-12-31)
- fix: 上报 ChangedWfContext (dhb52, 2024-12-31)
- feat: 添加Dockerfile样例 (dhb52, 2024-12-09)
- fix: 对齐服务器master分支 (dhb52, 2024-12-04)
- feat: 默认使用gRPC (dhb52, 2024-12-04)

## 0.0.2 (2024-12-03)

- feat: 支持 MapReduce 执行器、定时任务


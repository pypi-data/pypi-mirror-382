from typing import List

from snailjob.config import get_snailjob_settings
from snailjob.grpc import send_to_server
from snailjob.schemas import (
    DispatchJobResult,
    JobExecutor,
    JobLogTask,
    MapTaskRequest,
    SnailJobRequest,
    StatusEnum,
)

# 全局配置实例
settings = get_snailjob_settings()


def send_heartbeat():
    """注册客户端(心跳)"""
    URI = "/beat"
    payload = SnailJobRequest.build(["PING"])
    return send_to_server(URI, payload.model_dump(), "发送心跳")


def send_dispatch_result(payload: DispatchJobResult) -> StatusEnum:
    """执行结果上报"""
    URI = "/report/dispatch/result"
    return send_to_server(URI, payload.model_dump(), "结果上报")


def send_batch_log_report(payload: List[JobLogTask]) -> StatusEnum:
    """日志批量上报"""
    URI = "/batch/server/report/log"
    return send_to_server(URI, [log.model_dump() for log in payload], "日志批量上报")


def send_batch_map_report(payload: MapTaskRequest) -> StatusEnum:
    """生成同步MAP任务"""
    URI = "/batch/report/job/map/task/v1"
    return send_to_server(URI, payload.model_dump(), "生成同步MAP任务")


def register_executors(payload: List[JobExecutor]) -> StatusEnum:
    """注册执行器"""
    URI = "/register/job/executors"
    return send_to_server(URI, [item.model_dump() for item in payload], "注册执行器")

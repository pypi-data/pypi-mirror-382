import json
from typing import Any

import grpc

from snailjob.config import get_snailjob_settings
from snailjob.grpc import snailjob_pb2, snailjob_pb2_grpc
from snailjob.log import SnailLog
from snailjob.schemas import SnailJobRequest, StatusEnum

# 全局配置实例
settings = get_snailjob_settings()


def send_to_server(uri: str, payload: Any, job_name: str) -> StatusEnum:
    """发送请求到程服务器"""
    request = SnailJobRequest.build(args=[payload])
    try:
        with grpc.insecure_channel(
            f"{settings.snail_server_host}:{settings.snail_server_port}"
        ) as channel:
            stub = snailjob_pb2_grpc.UnaryRequestStub(channel)
            req = snailjob_pb2.GrpcSnailJobRequest(
                reqId=request.reqId,
                metadata=snailjob_pb2.Metadata(
                    uri=uri,
                    headers=settings.snail_headers,
                ),
                body=json.dumps([payload]),
            )
            response = stub.unaryRequest(req)
            assert request.reqId == response.reqId, "reqId 不一致的!"
            if response.status == StatusEnum.YES:
                SnailLog.LOCAL.info(f"{job_name}成功: reqId={request.reqId}")
                try:
                    SnailLog.LOCAL.debug(f"data={payload.model_dump(mode='json')}")
                except Exception:
                    SnailLog.LOCAL.debug(f"data={payload}")
            else:
                SnailLog.LOCAL.error(f"{job_name}失败: {response.message}")
            return response.status
    except grpc.RpcError as ex:
        SnailLog.LOCAL.error(f"无法连接服务器: {ex}")

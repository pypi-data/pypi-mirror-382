import json
import time
from concurrent import futures

import grpc

from snailjob.grpc import snailjob_pb2, snailjob_pb2_grpc
from snailjob.log import SnailLog
from snailjob.schemas import DispatchJobRequest, StopJobRequest

SLEEP_SECONDS = 60


class SnailJobServicer(snailjob_pb2_grpc.UnaryRequestServicer):
    def unaryRequest(
        self,
        request: snailjob_pb2.GrpcSnailJobRequest,
        _: grpc.RpcContext,
    ) -> snailjob_pb2.GrpcResult:
        if request.metadata.uri == "/job/dispatch/v1":
            return SnailJobServicer.dispatch(request)
        elif request.metadata.uri == "/job/stop/v1":
            return SnailJobServicer.stop(request)
        else:
            pass

    @staticmethod
    def dispatch(request: snailjob_pb2.GrpcSnailJobRequest):
        from .. import ExecutorManager

        args = json.loads(request.body)
        dispatchJobRequest = DispatchJobRequest(**args[0])
        result = ExecutorManager.dispatch(dispatchJobRequest)
        return snailjob_pb2.GrpcResult(
            reqId=request.reqId,
            status=result.status,
            message=result.message,
            data=json.dumps(result.data),
        )

    @staticmethod
    def stop(request: snailjob_pb2.GrpcSnailJobRequest):
        from .. import ExecutorManager

        args = json.loads(request.body)
        stopJobRequest = StopJobRequest(**args[0])
        ExecutorManager.stop(stopJobRequest)
        return snailjob_pb2.GrpcResult(
            reqId=request.reqId,
            status=1,
            message="",
            data="true",
        )


def run_grpc_server(port: int):
    """运行客户端服务器

    Args:
        host (str): 主机 (IP, 域名)
        port (int): 服务端口
    """
    server = grpc.server(
        futures.ThreadPoolExecutor(thread_name_prefix="snail-job-server", max_workers=10)
    )
    snailjob_pb2_grpc.add_UnaryRequestServicer_to_server(SnailJobServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    try:
        while True:
            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        SnailLog.LOCAL.info("KeyboardInterrupt, 退出程序")
        server.stop(0)

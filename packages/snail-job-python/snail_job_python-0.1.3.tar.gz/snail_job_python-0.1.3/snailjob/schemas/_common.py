import time
from typing import Any, List

from pydantic import BaseModel, Field


def makeReqId() -> int:
    """生成上报请求 reqId"""
    return int(time.time() * 1000)


class SnailJobRequest(BaseModel):
    """客户端请求类型"""

    reqId: int = Field(..., description="reqID 不能为空")
    args: List[Any] = Field(..., description="args 不能为空")

    @staticmethod
    def build(args: List[Any] = None) -> "SnailJobRequest":
        return SnailJobRequest(reqId=makeReqId(), args=[] if args is None else args)

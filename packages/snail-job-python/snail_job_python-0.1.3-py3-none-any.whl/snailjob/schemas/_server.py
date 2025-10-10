"""数据模型：服务器 ==> 客户端"""

import collections
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, Json, field_validator

from snailjob.schemas._enums import MapReduceStageEnum, StatusEnum


class NettyResult(BaseModel):
    status: StatusEnum = Field(..., description="status 不能为空")
    reqId: int = Field(..., description="reqId 不能为空")
    data: Any = Field({}, description="data 不能为空")
    message: str = Field("", description="data 不能为空")


class DispatchJobRequest(BaseModel):
    namespaceId: str = Field(..., description="namespaceId 不能为空")
    jobId: int = Field(..., description="jobId 不能为空")
    taskBatchId: int = Field(..., description="taskBatchId 不能为空")
    taskId: int = Field(..., description="taskId 不能为空")
    taskName: str = Field(..., description="taskName 不能为空")
    taskType: int = Field(..., description="taskType 不能为空")
    groupName: str = Field(..., description="group 不能为空")
    parallelNum: int = Field(..., description="parallelNum 不能为空")
    executorType: int = Field(..., description="executorType 不能为空")
    executorInfo: str = Field(..., description="executorInfo 不能为空")
    executorTimeout: int = Field(..., description="executorTimeout 不能为空")
    argsStr: Optional[str] = None
    mrStage: Optional[MapReduceStageEnum] = None
    shardingTotal: Optional[int] = None
    shardingIndex: Optional[int] = None
    workflowTaskBatchId: Optional[int] = None
    workflowNodeId: Optional[int] = None
    retryCount: Optional[int] = None
    retryScene: Optional[int] = Field(None, description="重试场景 auto、manual")
    retry: bool = Field(False, description="是否是重试流量")
    wfContext: Json[Dict[str, Any]] = Field(default_factory=collections.defaultdict)
    changeWfContext: Json[Dict[str, Any]] = Field(default_factory=collections.defaultdict)

    @field_validator("namespaceId", "groupName", "executorInfo", mode="before")
    def not_blank(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"{field.alias} 不能为空")
        return v


class StopJobRequest(BaseModel):
    jobId: int = Field(..., description="jobId 不能为空")
    taskBatchId: int = Field(..., description="taskBatchId 不能为空")
    groupName: str = Field(..., description="group 不能为空")

    @field_validator("groupName", mode="before")
    def not_blank(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"{field.alias} 不能为空")
        return v

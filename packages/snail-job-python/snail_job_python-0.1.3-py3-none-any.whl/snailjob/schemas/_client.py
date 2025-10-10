"""数据模型：客户端 ==> 服务器"""

from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from snailjob.schemas._enums import JobTaskBatchStatusEnum, JobTaskTypeEnum, StatusEnum


class Result(BaseModel):
    status: StatusEnum
    message: str = ""
    data: bool = True

    @staticmethod
    def success(message: str = ""):
        return Result(status=StatusEnum.YES, message=message, data=True)

    @staticmethod
    def failure(message: str, status: StatusEnum = StatusEnum.YES):
        return Result(status=status, message=message, data=False)


class ExecuteResult(BaseModel):
    """执行结果"""

    status: StatusEnum
    result: object = None
    message: str = ""

    @staticmethod
    def success(result: object = None):
        return ExecuteResult(
            status=StatusEnum.YES,
            result=result,
            message="任务执行成功",
        )

    @staticmethod
    def failure(result: object = None):
        return ExecuteResult(
            status=StatusEnum.NO,
            result=result,
            message="任务执行失败",
        )


class DispatchJobResult(BaseModel):
    """调度结果信息上报请求体"""

    jobId: int
    taskBatchId: int
    workflowTaskBatchId: Optional[int] = None
    workflowNodeId: Optional[int] = None
    taskId: int
    # 任务类型
    taskType: JobTaskTypeEnum
    groupName: str
    taskStatus: JobTaskBatchStatusEnum
    executeResult: ExecuteResult
    # 重试场景 auto、manual
    retryScene: Optional[int] = None
    # 是否是重试流量
    retry: bool = False
    wfContext: str = None


class TaskLogFieldDTO(BaseModel):
    """日志字段信息"""

    name: str
    value: Optional[str] = None


class JobLogTask(BaseModel):
    """上报日志结构"""

    # 任务信息id
    jobId: int
    # 任务实例id
    taskBatchId: int
    # 调度任务id
    taskId: int
    # 日志类型
    logType: str
    # 命名空间
    namespaceId: str
    # 组名称
    groupName: str
    # 上报时间
    realTime: int
    # 日志模型集合
    fieldList: List[TaskLogFieldDTO]


class JobExecutorInfo(BaseModel):
    """执行器定义信息"""

    executorName: str

    # 定时任务
    jobMethod: Callable = None

    # MapReduce
    mapMethods: Dict[str, Callable] = None
    reduceMethod: Callable = None
    mergeMethod: Callable = None


class MapTaskRequest(BaseModel):
    """分片任务上报请求体"""

    jobId: int = Field(..., description="jobId 不能为空")
    taskBatchId: int = Field(..., description="taskBatchId 不能为空")
    parentId: int = Field(..., description="parentId 不能为空")
    workflowTaskBatchId: Optional[int] = None
    workflowNodeId: Optional[int] = None
    wfContext: Optional[str] = None
    taskName: str = Field(..., description="taskName 不能为空")
    subTask: List[Any] = Field(..., description="subTask 不能为空")


class JobExecutor(BaseModel):
    """定时任务执行器"""

    executorInfo: str = Field(..., description="executorInfo 不能为空")

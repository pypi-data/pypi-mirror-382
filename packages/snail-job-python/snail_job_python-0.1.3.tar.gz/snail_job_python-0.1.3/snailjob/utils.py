import json
from typing import Any, List

from snailjob.args import WfContext
from snailjob.config import get_snailjob_settings
from snailjob.ctx import SnailContextManager
from snailjob.err import SnailJobError
from snailjob.log import SnailLog
from snailjob.rpc import send_batch_map_report
from snailjob.schemas import (
    DispatchJobRequest,
    DispatchJobResult,
    ExecuteResult,
    JobTaskBatchStatusEnum,
    MapTaskRequest,
    StatusEnum,
)

# 全局配置实例
settings = get_snailjob_settings()


def mr_do_map(task_list: List[Any], next_task_name: str) -> ExecuteResult:
    """MapReduce 的 Map 阶段帮助函数，上报分片结果给服务器

    Args:
        task_list (List[Any]): Map任务列表
        next_task_name (str):  下一个任务

    Raises:
        SnailJobError: 校验参数参数

    Returns:
        ExecuteResult: 执行结果
    """
    job_context = SnailContextManager.get_job_context()

    if not next_task_name:
        raise SnailJobError("The next task name can not empty")

    if not task_list:
        raise SnailJobError(f"The task list can not empty {next_task_name}")

    if len(task_list) > 200:
        raise SnailJobError(
            f"[{next_task_name}] map task size is too large, "
            "network maybe overload... please try to split the tasks."
        )

    if settings.root_map == next_task_name:
        raise SnailJobError(f"The Next taskName can not be {settings.root_map}")

    wf_context = json.dumps(job_context.changeWfContext) if job_context.changeWfContext else ""
    request = MapTaskRequest(
        jobId=job_context.jobId,
        taskBatchId=job_context.taskBatchId,
        parentId=job_context.taskId,
        workflowTaskBatchId=job_context.workflowTaskBatchId,
        workflowNodeId=job_context.workflowNodeId,
        wfContext=wf_context,
        taskName=next_task_name,
        subTask=task_list,
    )

    if send_batch_map_report(request) == StatusEnum.YES:
        SnailLog.LOCAL.info(
            f"Map task create successfully!. taskName:[{next_task_name}] "
            f"TaskId:[{job_context.taskId}]"
        )
    else:
        raise SnailJobError(f"Map failed for task: {next_task_name}")

    return ExecuteResult.success()


def build_dispatch_result(
    *,
    request: DispatchJobRequest,
    execute_result: ExecuteResult,
    change_wf_context: WfContext,
) -> DispatchJobResult:
    """构建调度结果信息上报请求体"""
    return DispatchJobResult(
        jobId=request.jobId,
        taskBatchId=request.taskBatchId,
        workflowTaskBatchId=request.workflowTaskBatchId,
        workflowNodeId=request.workflowNodeId,
        taskId=request.taskId,
        taskType=request.taskType,
        groupName=request.groupName,
        taskStatus=(
            JobTaskBatchStatusEnum.SUCCESS
            if execute_result.status == StatusEnum.YES
            else JobTaskBatchStatusEnum.FAIL
        ),
        executeResult=(ExecuteResult.success() if execute_result is None else execute_result),
        retryScene=request.retryScene,
        retry=request.retry,
        wfContext=(json.dumps(change_wf_context.to_dict()) if change_wf_context else ""),
    )

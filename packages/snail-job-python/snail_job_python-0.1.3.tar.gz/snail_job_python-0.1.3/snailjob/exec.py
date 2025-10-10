import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Dict, Optional, Union

from snailjob.args import build_args
from snailjob.ctx import SnailContextManager
from snailjob.deco import MapExecutor, MapReduceExecutor
from snailjob.err import SnailJobError
from snailjob.log import SnailLog
from snailjob.rpc import register_executors, send_dispatch_result
from snailjob.schemas import (
    DispatchJobRequest,
    ExecuteResult,
    ExecutorTypeEnum,
    JobExecutor,
    JobExecutorInfo,
    JobTaskTypeEnum,
    MapReduceStageEnum,
    Result,
    StatusEnum,
    StopJobRequest,
)
from snailjob.utils import build_dispatch_result


class ThreadPoolCache:
    """线程池执行器缓存"""

    _cache_thread_pool: Dict[int, ThreadPoolExecutor] = {}
    _cache_events: Dict[int, threading.Event] = {}
    _lock = threading.RLock()

    @staticmethod
    def create_thread_pool(task_batch_id: int, parallel_num: int) -> ThreadPoolExecutor:
        with ThreadPoolCache._lock:
            if task_batch_id in ThreadPoolCache._cache_thread_pool:
                cache_thread_pool = ThreadPoolCache._cache_thread_pool[task_batch_id]
                if cache_thread_pool._max_workers > 1:
                    return cache_thread_pool

                # HACK: _max_workers 为私有变量, 另外这样是否起到作用
                cache_thread_pool._max_workers = min(
                    parallel_num,
                    cache_thread_pool._max_workers,
                )
                return cache_thread_pool

            thread_pool_executor = ThreadPoolExecutor(
                max_workers=parallel_num,
                thread_name_prefix=f"snail-job-job-{task_batch_id}",
            )
            ThreadPoolCache._cache_thread_pool[task_batch_id] = thread_pool_executor
            ThreadPoolCache._cache_events[task_batch_id] = threading.Event()

            return thread_pool_executor

    @staticmethod
    def get_thread_pool(task_batch_id: int) -> ThreadPoolExecutor:
        with ThreadPoolCache._lock:
            return ThreadPoolCache._cache_thread_pool.get(task_batch_id)

    @staticmethod
    def event_is_set(task_batch_id: int) -> threading.Event:
        with ThreadPoolCache._lock:
            event = ThreadPoolCache._cache_events.get(task_batch_id)
            return event is not None and event.is_set()

    @staticmethod
    def stop_thread_pool(task_batch_id: int):
        with ThreadPoolCache._lock:
            # 1. 发送
            thread_event = ThreadPoolCache._cache_events.get(task_batch_id)
            if thread_event is not None:
                thread_event.set()

            # 2. 关闭线程池，不再接受新任务
            thread_pool_executor = ThreadPoolCache._cache_thread_pool.pop(
                task_batch_id,
                None,
            )
            if thread_pool_executor is not None:
                thread_pool_executor.shutdown(wait=False)


class ExecutorManager:
    """执行管理器"""

    _executors: Dict[str, JobExecutorInfo] = {}

    @staticmethod
    def _select_executor(
        executor_info: JobExecutorInfo,
        taks_type: JobTaskTypeEnum,
        mr_stage: MapReduceStageEnum = None,
        task_name: str = None,
    ) -> Optional[Callable]:
        """根据调度参数选择执行器函数"""
        if (
            taks_type == JobTaskTypeEnum.MAP
            or taks_type == JobTaskTypeEnum.MAP_REDUCE
            and mr_stage == MapReduceStageEnum.MAP
        ):
            if task_name is None:
                raise SnailJobError("Map任务名称不能为空")
            if task_name in executor_info.mapMethods:
                return executor_info.mapMethods[task_name]
            else:
                raise SnailJobError(f"Map任务 [{task_name}] 不存在")
        elif taks_type == JobTaskTypeEnum.MAP_REDUCE:
            if mr_stage == MapReduceStageEnum.REDUCE:
                if executor_info.reduceMethod is None:
                    raise SnailJobError("Reduce任务不存在")
                return executor_info.reduceMethod
            elif mr_stage == MapReduceStageEnum.MERGE_REDUCE:
                if executor_info.mergeMethod is None:
                    raise SnailJobError("Merge任务不存在")
                return executor_info.mergeMethod
        else:
            if executor_info.jobMethod is None:
                raise SnailJobError("执行器不存在")
            return executor_info.jobMethod

    @staticmethod
    def register(executor: Union[Callable, MapExecutor, MapReduceExecutor]):
        """注册执行器

        Args:
            executor (callable): 执行器函数, 必须为 `@job` 装饰的函数，
            或者是`MapExecutor`, `MapReduceExecutor`类型

        Raises:
            SnailJobError: 执行器配置错误
        """
        if callable(executor):
            if not hasattr(executor, "executor_name"):
                raise SnailJobError(f"[{executor.__name__}] 没有使用 @job 装饰器")

            if executor.executor_name in ExecutorManager._executors:
                raise SnailJobError(f"执行器 [{executor.executor_name}] 已经存在")

            ExecutorManager._executors[executor.executor_name] = JobExecutorInfo(
                executorName=executor.executor_name,
                jobMethod=executor,
            )
            SnailLog.LOCAL.info(f"成功注册执行器: {executor.executor_name}")
        elif isinstance(executor, (MapExecutor, MapReduceExecutor)):
            executor_info = executor.executor_info
            ExecutorManager._executors[executor_info.executorName] = executor_info
            SnailLog.LOCAL.info(f"成功注册执行器: {executor_info.executorName}")
        else:
            raise SnailJobError("错误的执行器类型")

    @staticmethod
    def _execute_wrapper(
        job_method: Callable,
        request: DispatchJobRequest,
    ):
        # 设置 context
        SnailContextManager.set_context(request)

        try:
            job_args = build_args(request)
            execute_result: ExecuteResult = job_method(job_args)
            dispatch_result = build_dispatch_result(
                request=request,
                execute_result=execute_result,
                change_wf_context=job_args.change_wf_context,
            )
            send_dispatch_result(dispatch_result)

            # 集群类型任务, 客户端可以主动关闭线程池, batchId 不会有后续的调度
            if request.taskType == JobTaskTypeEnum.CLUSTER:
                ThreadPoolCache.stop_thread_pool(request.taskBatchId)

        except Exception as ex:
            SnailLog.REMOTE.error(str(ex))
            dispatch_result = build_dispatch_result(
                request=request,
                execute_result=ExecuteResult.failure(str(ex)),
                change_wf_context=job_args.change_wf_context,
            )
            send_dispatch_result(dispatch_result)

    @staticmethod
    def dispatch(request: DispatchJobRequest) -> Result:
        """执行任务批次

        Args:
            dispatch_job_request (DispatchJobRequest): 任务调度信息
        """
        try:
            SnailContextManager.set_context(request)
            if request.executorType != ExecutorTypeEnum.PYTHON:
                SnailLog.REMOTE.error("执行器类型必须为 Python")
                return Result.failure("执行器类型必须为 Python")

            executor_info = ExecutorManager._executors.get(request.executorInfo)
            if executor_info is None:
                return Result.failure(f"找不到执行器: {request.executorInfo}")

            if isinstance(request.retryCount, int) and request.retryCount > 0:
                SnailLog.REMOTE.info(f"任务执行/调度失败执行重试. 重试次数:[{request.retryCount}]")

            # 选择执行器函数
            job_method: Callable = None
            job_method = ExecutorManager._select_executor(
                executor_info=executor_info,
                taks_type=request.taskType,
                mr_stage=request.mrStage,
                task_name=request.taskName,
            )
            if job_method is None:
                SnailLog.REMOTE.error("执行器函数不存在")
                return Result.failure("执行器函数不存在")

            # 创建线程池, 执行任务
            thread_pool = ThreadPoolCache.create_thread_pool(
                request.taskBatchId,
                max(1, request.parallelNum),
            )
            thread_pool.submit(partial(ExecutorManager._execute_wrapper, job_method, request))

        except Exception:
            message = f"客户端发生非预期异常. taskBatchId:[{request.taskBatchId}]"
            SnailLog.REMOTE.error(message)
            return Result.failure(message, status=StatusEnum.NO)

        SnailLog.REMOTE.info(f"批次:[{request.taskBatchId}] 任务调度成功.")
        return Result.success()

    @staticmethod
    def stop(request: StopJobRequest):
        """停止任务批次

        Args:
            stop_request (StopJobRequest): 任务停止请求
        """
        ThreadPoolCache.stop_thread_pool(request.taskBatchId)

    @staticmethod
    def register_executors_to_server():
        executors = [
            JobExecutor(executorInfo=executor_info)
            for executor_info in ExecutorManager._executors.keys()
        ]
        register_executors(executors)

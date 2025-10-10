import contextvars
from dataclasses import dataclass

from snailjob.schemas import DispatchJobRequest


@dataclass
class SnailLogContext:
    jobId: int
    taskId: int
    taskBatchId: int


SnailJobContext = DispatchJobRequest


class SnailContextManager:
    _job_context = contextvars.ContextVar("SnailJob_context")
    _log_context = contextvars.ContextVar("SnailLog_context")

    @staticmethod
    def set_job_context(job: SnailJobContext):
        SnailContextManager._job_context.set(job)

    @staticmethod
    def get_job_context() -> SnailJobContext:
        return SnailContextManager._job_context.get()

    @staticmethod
    def set_log_context(log: SnailLogContext):
        SnailContextManager._log_context.set(log)

    @staticmethod
    def get_log_context() -> SnailLogContext:
        return SnailContextManager._log_context.get()

    @staticmethod
    def set_context(args: SnailJobContext):
        # 设置log context
        SnailContextManager.set_log_context(
            SnailLogContext(
                jobId=args.jobId,
                taskId=args.taskId,
                taskBatchId=args.taskBatchId,
            )
        )
        # 设置job context
        SnailContextManager.set_job_context(args)

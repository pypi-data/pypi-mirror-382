import copy
import json
import threading
from dataclasses import dataclass
from typing import Any, Dict

from snailjob.schemas import DispatchJobRequest, JobTaskTypeEnum, MapReduceStageEnum


class WfContext:
    def __init__(self, context: Dict = None):
        self._context = context or {}
        self._lock = threading.Lock()

    @staticmethod
    def from_dict(context: Dict) -> "WfContext":
        return WfContext(copy.deepcopy(context))

    def to_dict(self) -> Dict:
        with self._lock:
            return copy.deepcopy(self._context)

    def __setitem__(self, index: Any, value: Any):
        with self._lock:
            self._context[index] = value

    def __getitem__(self, index: Any) -> Any:
        with self._lock:
            return self._context[index]

    def __delitem__(self, index: Any) -> Any:
        with self._lock:
            del self._context[index]

    def __contains__(self, index):
        with self._lock:
            return index in self._context


@dataclass
class JobArgs:
    job_params: Any = None
    executor_info: str = None
    task_batch_id: int = None
    job_id: int = None
    wf_context: Dict = None
    change_wf_context: WfContext = None

    def append_context(self, key, value):
        if self.change_wf_context is None:
            self.change_wf_context = WfContext()
        self.change_wf_context[key] = value

    def get_wf_context(self, key):
        if not self.wf_context or not key or key not in self.wf_context:
            return None
        return self.wf_context[key]


@dataclass
class MapArgs(JobArgs):
    task_name: str = None
    map_result: Any = None


@dataclass
class ShardingJobArgs(JobArgs):
    sharding_total: int = None
    sharding_index: int = None


@dataclass
class ReduceArgs(JobArgs):
    map_result: Any = None


@dataclass
class MergeReduceArgs(JobArgs):
    reduces: Any = None


def build_args(args: DispatchJobRequest) -> JobArgs:
    argsStr = json.loads(args.argsStr)
    job_params = argsStr["jobParams"] if "jobParams" in argsStr else None
    maps = argsStr["maps"] if "maps" in argsStr else None
    reduces = argsStr["reduces"] if "reduces" in argsStr else None

    if args.taskType == JobTaskTypeEnum.SHARDING:
        return ShardingJobArgs(
            sharding_total=args.shardingTotal,
            sharding_index=args.shardingIndex,
            job_params=job_params,
            executor_info=args.executorInfo,
            task_batch_id=args.taskBatchId,
            job_id=args.jobId,
            wf_context=args.wfContext,
            change_wf_context=WfContext.from_dict({}),
        )
    elif args.taskType in (JobTaskTypeEnum.MAP, JobTaskTypeEnum.MAP_REDUCE):
        if args.mrStage == MapReduceStageEnum.MAP:
            return MapArgs(
                task_name=args.taskName,
                map_result=maps,
                job_params=job_params,
                executor_info=args.executorInfo,
                task_batch_id=args.taskBatchId,
                job_id=args.jobId,
                wf_context=args.wfContext,
                change_wf_context=WfContext.from_dict({}),
            )
        elif args.mrStage == MapReduceStageEnum.REDUCE:
            return ReduceArgs(
                map_result=maps,
                job_params=job_params,
                executor_info=args.executorInfo,
                task_batch_id=args.taskBatchId,
                job_id=args.jobId,
                wf_context=args.wfContext,
                change_wf_context=WfContext.from_dict({}),
            )
        elif args.mrStage == MapReduceStageEnum.MERGE_REDUCE:
            return MergeReduceArgs(
                reduces=reduces,
                job_params=job_params,
                executor_info=args.executorInfo,
                task_batch_id=args.taskBatchId,
                job_id=args.jobId,
                wf_context=args.wfContext,
                change_wf_context=WfContext.from_dict({}),
            )

        raise ValueError(f"Invalid mrStage {args.mrStage}")
    else:
        return JobArgs(
            job_params=job_params,
            executor_info=args.executorInfo,
            task_batch_id=args.taskBatchId,
            job_id=args.jobId,
            wf_context=args.wfContext,
            change_wf_context=WfContext.from_dict({}),
        )

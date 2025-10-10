from snailjob.args import JobArgs, MapArgs, MergeReduceArgs, ReduceArgs, ShardingJobArgs
from snailjob.config import get_snailjob_settings
from snailjob.ctx import SnailContextManager
from snailjob.deco import MapExecutor, MapReduceExecutor, job
from snailjob.err import SnailJobError
from snailjob.exec import ExecutorManager, ThreadPoolCache
from snailjob.log import SnailLog
from snailjob.main import client_main
from snailjob.schemas import ExecuteResult
from snailjob.utils import mr_do_map

# 全局配置实例
settings = get_snailjob_settings()

__all__ = [
    "client_main",
    "job",
    "MapExecutor",
    "MapReduceExecutor",
    "SnailJobError",
    "JobArgs",
    "MapArgs",
    "ShardingJobArgs",
    "ReduceArgs",
    "MergeReduceArgs",
    "ExecuteResult",
    "mr_do_map",
    "ExecutorManager",
    "ThreadPoolCache",
    "SnailLog",
    "SnailContextManager",
]

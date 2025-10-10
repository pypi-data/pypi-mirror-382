from enum import Enum


class StatusEnum(int, Enum):
    """执行结果状态枚举"""

    NO = 0
    YES = 1


class JobTaskTypeEnum(int, Enum):
    """任务类型枚举"""

    CLUSTER = 1
    BROADCAST = 2
    SHARDING = 3
    MAP = 4
    MAP_REDUCE = 5


class JobTaskBatchStatusEnum(int, Enum):
    """任务批次执行状态枚举"""

    WAITING = 1
    RUNNING = 2
    SUCCESS = 3
    FAIL = 4
    STOP = 5
    CANCEL = 6


class ExecutorTypeEnum(int, Enum):
    """执行器类型枚举"""

    JAVA = 1
    PYTHON = 2


class MapReduceStageEnum(int, Enum):
    """MapReduce 执行阶段"""

    MAP = 1
    REDUCE = 2
    MERGE_REDUCE = 3

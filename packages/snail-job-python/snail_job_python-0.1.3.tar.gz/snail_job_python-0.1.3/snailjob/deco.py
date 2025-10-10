from snailjob.config import get_snailjob_settings
from snailjob.schemas import JobExecutorInfo

# 全局配置实例
settings = get_snailjob_settings()


def job(executor_name: str):
    """任务执行器装饰器

    Args:
        executor_name (str): 执行器名称
    """

    def decorator(func):
        func.executor_name = executor_name
        return func

    return decorator


class MapExecutor:
    """Map 执行器"""

    def __init__(self, executor_name: str):
        self.executor_info = JobExecutorInfo(
            executorName=executor_name,
            mapMethods={},
        )

    def map(self, task_name: str = None):
        """Map 执行函数装饰器

        Args:
            task_name (str, optional): 任务名称. 默认为 ROOT_MAP.
        """

        def decorator(func):
            actual_task_name = task_name or settings.root_map
            if actual_task_name in self.executor_info.mapMethods:
                raise ValueError(f"Map任务名称{actual_task_name}已经存在")

            self.executor_info.mapMethods[actual_task_name] = func
            return func

        return decorator


class MapReduceExecutor(MapExecutor):
    """MapReduce执行器"""

    def __init__(self, executor_name: str):
        super(MapReduceExecutor, self).__init__(executor_name)

    def reduce(self):
        """Reduce 执行函数装饰器"""

        def decorator(func):
            if self.executor_info.reduceMethod is not None:
                raise ValueError("Reduce任务已经存在")
            self.executor_info.reduceMethod = func
            return func

        return decorator

    def merge(self):
        """MergeReduce 执行函数装饰器"""

        def decorator(func):
            if self.executor_info.mergeMethod is not None:
                raise ValueError("MergeReduce任务已经存在")
            self.executor_info.mergeMethod = func
            return func

        return decorator

from abc import ABC, abstractmethod
from typing import Any, Dict

from snailjob.log import SnailLog


class AbstractExecutor(ABC):
    @abstractmethod
    def process(self, job_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def log_debug(self, msg: str, *args):
        SnailLog.LOCAL.debug(f"[snail-job] {msg}", *args)

    def log_info(self, msg: str, *args):
        SnailLog.LOCAL.info(f"[snail-job] {msg}", *args)

    def log_warn(self, msg: str, *args):
        SnailLog.LOCAL.info.warning(f"[snail-job] {msg}", *args)

    def log_error(self, msg: str, *args):
        SnailLog.LOCAL.error(f"[snail-job] {msg}", *args)

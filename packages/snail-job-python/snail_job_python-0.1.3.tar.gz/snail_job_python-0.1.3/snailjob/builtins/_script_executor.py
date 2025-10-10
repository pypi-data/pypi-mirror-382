import os
import subprocess
import sys
from abc import abstractmethod
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

from snailjob.builtins import _util
from snailjob.builtins._base import AbstractExecutor
from snailjob.schemas import ExecuteResult

SCRIPT_DOWNLOAD_METHOD = "DOWNLOAD"
SCRIPT_SCRIPT_CODE_METHOD = "SCRIPT_CODE"
SCRIPT_LOCAL_SCRIPT_METHOD = "LOCAL_SCRIPT"


class ScriptParams(BaseModel):
    method: Literal["DOWNLOAD", "SCRIPT_CODE", "LOCAL_SCRIPT"]
    scriptParams: str
    charset: Optional[str] = None


class AbstractScriptExecutor(AbstractExecutor):
    SH_SHELL = "/bin/sh"
    WORKER_DIR = os.path.join(os.path.expanduser("~"), "snailJob/worker/script_processor/")

    # 脚本执行方式
    def process(self, job_id: str, script_params: ScriptParams = None) -> ExecuteResult:
        self.log_info(f"ScriptProcessor start to process, params: {script_params}")
        if not script_params:
            self.log_warn("ScriptParams is null, please check jobParam configuration.")
            return {"success": False, "message": "ScriptParams is null."}

        script_path = self.prepare_script_file(job_id, script_params)
        self.log_info(f"Generate executable file successfully, path: {script_path}")

        if sys.platform == "win32" and self.SH_SHELL == self.get_run_command():
            self.log_warn("Current OS is Windows where shell scripts cannot run.")
            return {"success": False, "message": "Shell scripts cannot run on Windows."}

        if sys.platform != "win32":
            self.set_script_permissions(script_path)

        return self.execute_script(script_path, script_params)

    def prepare_script_file(self, job_id: str, script_params: ScriptParams) -> str:
        script_path = os.path.join(self.WORKER_DIR, self.get_script_name(job_id))
        script_dir = os.path.dirname(script_path)

        # 创建脚本目录
        self.ensure_script_directory(script_dir)

        method = script_params.method
        if method == SCRIPT_LOCAL_SCRIPT_METHOD:
            return self.handle_local_script(script_path, script_params.scriptParams)
        elif method == SCRIPT_DOWNLOAD_METHOD:
            _util.download_file(script_params.scriptParams, script_path)
            return script_path
        elif method == SCRIPT_SCRIPT_CODE_METHOD:
            self.write_script_content(script_path, script_params)
            return script_path
        else:
            raise ValueError("Please correctly choose the script execution method.")

    def ensure_script_directory(self, script_dir: str):
        if not os.path.exists(script_dir):
            self.log_info(f"Script directory does not exist, creating: {script_dir}")
            os.makedirs(script_dir, exist_ok=True)

    def handle_local_script(self, script_path: str, source_path: str) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"File not found: {source_path}")

        with open(source_path, "r") as src, open(script_path, "w") as dst:
            dst.write(src.read())

        return script_path

    def write_script_content(self, script_path: str, script_params: Dict[str, Any]):
        with open(script_path, "w") as f:
            f.write(script_params.scriptParams or "")
        self.log_info(f"Script content written successfully to: {script_path}")

    def set_script_permissions(self, script_path: str):
        try:
            os.chmod(script_path, 0o755)
            self.log_info("chmod 755 authorization complete, ready to start execution~")
        except Exception as e:
            raise RuntimeError("Failed to set script permissions") from e

    def execute_script(self, script_path: str, script_params: ScriptParams) -> ExecuteResult:
        pb = self.get_script_process_builder(script_path)

        try:
            process = subprocess.Popen(
                pb.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            stdout, stderr = process.communicate()
            success = process.returncode == 0
            self.log_debug(f"[STDOUT]: {stdout}\n\n [STDERR]: {stderr}")
            if success:
                return ExecuteResult.success({"stdout": stdout})
            else:
                return ExecuteResult.failure({"stderr": stderr})

        except Exception as e:
            raise RuntimeError("Script execution failed") from e

    @abstractmethod
    def get_script_name(self, job_id: str) -> str:
        pass

    @abstractmethod
    def get_run_command(self) -> str:
        pass

    def get_charset(self) -> str:
        return "utf-8"

    @abstractmethod
    def get_script_process_builder(self, script_path: str) -> subprocess.Popen:
        pass

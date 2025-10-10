import json
import subprocess

from snailjob.args import JobArgs
from snailjob.builtins._script_executor import AbstractScriptExecutor, ScriptParams
from snailjob.deco import job
from snailjob.schemas import ExecuteResult


class AbstractPowerShellExecutor(AbstractScriptExecutor):
    def get_script_name(self, job_id: int) -> str:
        return f"powershell_{job_id}.ps1"

    def get_run_command(self) -> str:
        return "powershell.exe"

    def get_script_process_builder(self, script_path: str) -> subprocess.Popen:
        return subprocess.Popen(
            [self.get_run_command(), "-ExecutionPolicy", "Bypass", "-File", script_path]
        )


class SnailJobPowerShellExecutor(AbstractPowerShellExecutor):
    def job_execute(self, job_args: JobArgs) -> ExecuteResult:
        job_params = job_args.job_params
        script_params = ScriptParams(**json.loads(job_params))
        return self.process(job_args.job_id, script_params)


@job("snailJobPowerShellJobExecutor")
def executor(job_args: JobArgs) -> ExecuteResult:
    return SnailJobPowerShellExecutor().job_execute(job_args)

import json
import subprocess

from snailjob.args import JobArgs
from snailjob.builtins._script_executor import AbstractScriptExecutor, ScriptParams
from snailjob.deco import job


class AbstractShellExecutor(AbstractScriptExecutor):
    def get_script_name(self, job_id: int) -> str:
        return f"shell_{job_id}.sh"

    def get_run_command(self) -> str:
        return self.SH_SHELL

    def get_script_process_builder(self, script_path: str) -> subprocess.Popen:
        return subprocess.Popen(["sh", script_path])


class SnailJobShellExecutor(AbstractShellExecutor):
    def job_execute(self, job_args: JobArgs) -> dict:
        job_params = job_args.job_params
        script_params = ScriptParams(**json.loads(job_params))
        return self.process(job_args.job_id, script_params)


@job("snailJobShellJobExecutor")
def executor(job_args: JobArgs) -> dict:
    return SnailJobShellExecutor().job_execute(job_args)

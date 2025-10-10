import demo_job

from snailjob import ExecutorManager, client_main
from snailjob.builtins import snailjob_http_executor, snailjob_shell_executor

if __name__ == "__main__":
    ExecutorManager.register(demo_job.test_job_executor)
    ExecutorManager.register(demo_job.test_job_executor_failed)
    ExecutorManager.register(demo_job.testWorkflowAnnoJobExecutor1)
    ExecutorManager.register(demo_job.testWorkflowAnnoJobExecutor2)
    ExecutorManager.register(demo_job.testMyMapExecutor)
    ExecutorManager.register(demo_job.testAnnoMapJobExecutor)
    ExecutorManager.register(demo_job.testAnnoMapReduceJobExecutor)
    ExecutorManager.register(snailjob_http_executor)
    ExecutorManager.register(snailjob_shell_executor)

    client_main()

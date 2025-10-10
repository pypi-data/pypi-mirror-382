import time
from dataclasses import dataclass

import snailjob as sj


@sj.job("testJobExecutor")
def test_job_executor(args: sj.JobArgs) -> sj.ExecuteResult:
    sj.SnailLog.REMOTE.info(f"job_params: {args.job_params}")

    # 执行一个超过40秒的任务，如果中间第30秒可以正常发送心跳，说明任务执行不阻塞
    for i in range(40):
        sj.SnailLog.REMOTE.info(f"loop {i}")
        if sj.ThreadPoolCache.event_is_set(args.task_batch_id):
            sj.SnailLog.REMOTE.info("任务已经被中断，立即返回")
            return sj.ExecuteResult.failure()
        time.sleep(1)

    sj.SnailLog.REMOTE.info("sync job1 done")
    return sj.ExecuteResult.success()


@sj.job("testJobExecutorFailed")
def test_job_executor_failed(args: sj.JobArgs):
    sj.SnailLog.LOCAL.info("testJobExecutorFailed, sj.SnailJobError raised")
    raise sj.SnailJobError("这是故意抛出的异常")


@sj.job("testWorkflowAnnoJobExecutor1")
def testWorkflowAnnoJobExecutor1(args: sj.JobArgs) -> sj.ExecuteResult:
    @dataclass
    class FailOrderPo:
        orderId: str = None

    order = FailOrderPo()
    order.orderId = "dhb52"
    sj.SnailLog.REMOTE.info(f"job_params: {args.job_params}")
    args.append_context("name", "testWorkflowAnnoJobExecutor")
    return sj.ExecuteResult.success(order)


@sj.job("testWorkflowAnnoJobExecutor2")
def testWorkflowAnnoJobExecutor2(args: sj.JobArgs) -> sj.ExecuteResult:
    sj.SnailLog.LOCAL.info(f"Name: {args.get_wf_context('name')}")
    return sj.ExecuteResult.success()


testMyMapExecutor = sj.MapExecutor("testMyMapExecutor")


@testMyMapExecutor.map()
def testMyMapExecutor_rootMap(args: sj.MapArgs):
    assert args.task_name == sj.settings.root_map
    return sj.mr_do_map(["1", "2", "3", "4"], "TWO_MAP")


@testMyMapExecutor.map("TWO_MAP")
def testMyMapExecutor_twoMap(args: sj.MapArgs):
    return sj.ExecuteResult.success(args.map_result)


testAnnoMapJobExecutor = sj.MapReduceExecutor("testAnnoMapJobExecutor")


@testAnnoMapJobExecutor.map()
def testAnnoMapJobExecutor_rootMap(args: sj.MapArgs) -> sj.ExecuteResult:
    print(args)
    args.append_context("Month", "2023-01")
    return sj.mr_do_map(["1", "2", "3"], "MONTH_MAP")


@testAnnoMapJobExecutor.map("MONTH_MAP")
def testAnnoMapJobExecutor_monthMap(args: sj.MapArgs) -> sj.ExecuteResult:
    print("MONTH_MAP called")
    args.append_context("Month", "2023-01")
    print(f"type(args) = {type(args)}, {args}")
    return sj.ExecuteResult.success([1, 2])


@testAnnoMapJobExecutor.reduce()
def testAnnoMapJobExecutor_reduce(args: sj.ReduceArgs) -> sj.ExecuteResult:
    print("reduce called")
    print(f"type(args) = {type(args)}, {args}")
    return sj.ExecuteResult.success([[3, 4], [5, 6]])


@testAnnoMapJobExecutor.merge()
def testAnnoMapJobExecutor_merge(args: sj.MergeReduceArgs) -> sj.ExecuteResult:
    print("merge reduce called")
    print(f"type(args) = {type(args)}, {args}")
    return sj.ExecuteResult.success([3, 4])


testAnnoMapReduceJobExecutor = sj.MapReduceExecutor("testAnnoMapReduceJobExecutor")


@testAnnoMapReduceJobExecutor.map()
def testAnnoMapReduceJobExecutor_rootMap(args: sj.MapArgs):
    return sj.mr_do_map(["1", "2", "3", "4", "5", "6"], "MONTH_MAP")


@testAnnoMapReduceJobExecutor.map("MONTH_MAP")
def testAnnoMapReduceJobExecutor_monthMap(args: sj.MapArgs):
    return sj.ExecuteResult.success(int(args.map_result) * 2)


@testAnnoMapReduceJobExecutor.reduce()
def testAnnoMapReduceJobExecutor_reduce(args: sj.ReduceArgs):
    return sj.ExecuteResult.success(sum([int(x) for x in args.map_result]))


@testAnnoMapReduceJobExecutor.merge()
def testAnnoMapReduceJobExecutor_merge(args: sj.MergeReduceArgs):
    return sj.ExecuteResult.success(sum([int(x) for x in args.reduces]))

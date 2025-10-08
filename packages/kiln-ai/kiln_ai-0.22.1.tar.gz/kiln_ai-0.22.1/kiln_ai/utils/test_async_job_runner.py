from typing import List
from unittest.mock import AsyncMock, patch

import pytest

from kiln_ai.utils.async_job_runner import (
    AsyncJobRunner,
    AsyncJobRunnerObserver,
    Progress,
)


@pytest.fixture
def mock_async_run_job_fn_success():
    return AsyncMock(return_value=True)


@pytest.fixture
def mock_async_run_job_fn_failure():
    return AsyncMock(return_value=False)


@pytest.mark.parametrize("concurrency", [0, -1, -25])
def test_invalid_concurrency_raises(concurrency, mock_async_run_job_fn_success):
    with pytest.raises(ValueError):
        AsyncJobRunner(
            concurrency=concurrency,
            jobs=[],
            run_job_fn=mock_async_run_job_fn_success,
        )


# Test with and without concurrency
@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_status_updates(
    concurrency, mock_async_run_job_fn_success
):
    job_count = 50
    jobs = [{"id": i} for i in range(job_count)]

    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=jobs,
        run_job_fn=mock_async_run_job_fn_success,
    )

    # Expect the status updates in order, and 1 for each job
    expected_completed_count = 0
    async for progress in runner.run():
        assert progress.complete == expected_completed_count
        expected_completed_count += 1
        assert progress.errors == 0
        assert progress.total == job_count

    # Verify last status update was complete
    assert expected_completed_count == job_count + 1

    # Verify run_job was called for each job
    assert mock_async_run_job_fn_success.call_count == job_count

    # Verify run_job was called with the correct arguments
    for i in range(job_count):
        mock_async_run_job_fn_success.assert_any_await(jobs[i])


# Test with and without concurrency
@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_status_updates_empty_job_list(
    concurrency, mock_async_run_job_fn_success
):
    empty_job_list = []

    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=empty_job_list,
        run_job_fn=mock_async_run_job_fn_success,
    )

    updates: List[Progress] = []
    async for progress in runner.run():
        updates.append(progress)

    # Verify last status update was complete
    assert len(updates) == 1

    assert updates[0].complete == 0
    assert updates[0].errors == 0
    assert updates[0].total == 0

    # Verify run_job was called for each job
    assert mock_async_run_job_fn_success.call_count == 0


@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_all_failures(
    concurrency, mock_async_run_job_fn_failure
):
    job_count = 50
    jobs = [{"id": i} for i in range(job_count)]

    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=jobs,
        run_job_fn=mock_async_run_job_fn_failure,
    )

    # Expect the status updates in order, and 1 for each job
    expected_error_count = 0
    async for progress in runner.run():
        assert progress.complete == 0
        assert progress.errors == expected_error_count
        expected_error_count += 1
        assert progress.total == job_count

    # Verify last status update was complete
    assert expected_error_count == job_count + 1

    # Verify run_job was called for each job
    assert mock_async_run_job_fn_failure.call_count == job_count

    # Verify run_job was called with the correct arguments
    for i in range(job_count):
        mock_async_run_job_fn_failure.assert_any_await(jobs[i])


@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_partial_failures(concurrency):
    job_count = 50
    jobs = [{"id": i} for i in range(job_count)]

    # we want to fail on some jobs and succeed on others
    jobs_to_fail = set([0, 2, 4, 6, 8, 20, 25])

    # fake run_job that fails
    mock_run_job_partial_success = AsyncMock(
        # return True for jobs that should succeed
        side_effect=lambda job: job["id"] not in jobs_to_fail
    )

    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=jobs,
        run_job_fn=mock_run_job_partial_success,
    )

    # Expect the status updates in order, and 1 for each job
    async for progress in runner.run():
        assert progress.total == job_count

    # Verify last status update was complete
    expected_error_count = len(jobs_to_fail)
    expected_success_count = len(jobs) - expected_error_count
    assert progress.errors == expected_error_count
    assert progress.complete == expected_success_count

    # Verify run_job was called for each job
    assert mock_run_job_partial_success.call_count == job_count

    # Verify run_job was called with the correct arguments
    for i in range(job_count):
        mock_run_job_partial_success.assert_any_await(jobs[i])


@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_partial_raises(concurrency):
    job_count = 50
    jobs = [{"id": i} for i in range(job_count)]

    ids_to_fail = set([10, 25])

    def failure_fn(job):
        if job["id"] in ids_to_fail:
            raise Exception("job failed unexpectedly")
        return True

    # fake run_job that fails
    mock_run_job_partial_success = AsyncMock(side_effect=failure_fn)

    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=jobs,
        run_job_fn=mock_run_job_partial_success,
    )

    # generate all the values we expect to see in progress updates
    complete_values_expected = set([i for i in range(job_count - len(ids_to_fail) + 1)])
    errors_values_expected = set([i for i in range(len(ids_to_fail) + 1)])

    # keep track of all the updates we see
    updates: List[Progress] = []

    # we keep track of the progress values we have actually seen
    complete_values_actual = set()
    errors_values_actual = set()

    # Expect the status updates in order, and 1 for each job
    async for progress in runner.run():
        updates.append(progress)
        complete_values_actual.add(progress.complete)
        errors_values_actual.add(progress.errors)

        assert progress.total == job_count

    # complete values should be all the jobs, except for the ones that failed
    assert progress.complete == job_count - len(ids_to_fail)

    # check that the actual updates and expected updates are equivalent sets
    assert complete_values_actual == complete_values_expected
    assert errors_values_actual == errors_values_expected

    # we should have seen one update for each job, plus one for the initial status update
    assert len(updates) == job_count + 1


@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_cancelled(concurrency, mock_async_run_job_fn_success):
    jobs = [{"id": i} for i in range(10)]
    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=jobs,
        run_job_fn=mock_async_run_job_fn_success,
    )

    with patch.object(
        runner,
        "_run_worker",
        side_effect=Exception("run_worker raised an exception"),
    ):
        # if an exception is raised in the task, we should see it bubble up
        with pytest.raises(Exception, match="run_worker raised an exception"):
            async for _ in runner.run():
                pass


@pytest.mark.parametrize("concurrency", [1, 25])
@pytest.mark.asyncio
async def test_async_job_runner_observers(concurrency):
    class MockAsyncJobRunnerObserver(AsyncJobRunnerObserver[dict[str, int]]):
        def __init__(self):
            self.on_error_calls = []
            self.on_success_calls = []

        async def on_error(self, job: dict[str, int], error: Exception):
            self.on_error_calls.append((job, error))

        async def on_success(self, job: dict[str, int]):
            self.on_success_calls.append(job)

    mock_observer_a = MockAsyncJobRunnerObserver()
    mock_observer_b = MockAsyncJobRunnerObserver()

    jobs = [{"id": i} for i in range(10)]

    async def run_job_fn(job: dict[str, int]) -> bool:
        # we simulate the job 5 and 6 crashing, which should trigger the observers on_error handlers
        if job["id"] == 5 or job["id"] == 6:
            raise ValueError(f"job failed unexpectedly {job['id']}")
        return True

    runner = AsyncJobRunner(
        concurrency=concurrency,
        jobs=jobs,
        run_job_fn=run_job_fn,
        observers=[mock_observer_a, mock_observer_b],
    )

    async for _ in runner.run():
        pass

    assert len(mock_observer_a.on_error_calls) == 2
    assert len(mock_observer_b.on_error_calls) == 2

    # not necessarily in order, but we should have seen both 5 and 6
    assert len(mock_observer_a.on_success_calls) == 8
    assert len(mock_observer_b.on_success_calls) == 8

    # check that 5 and 6 are in the error calls
    for job_idx in [5, 6]:
        # check that 5 and 6 are in the error calls for both observers
        assert any(call[0] == jobs[job_idx] for call in mock_observer_a.on_error_calls)
        assert any(call[0] == jobs[job_idx] for call in mock_observer_b.on_error_calls)

        # check that the error is the correct exception
        assert (
            str(mock_observer_a.on_error_calls[0][1]) == "job failed unexpectedly 5"
            or str(mock_observer_a.on_error_calls[1][1]) == "job failed unexpectedly 6"
        )
        assert (
            str(mock_observer_b.on_error_calls[0][1]) == "job failed unexpectedly 5"
            or str(mock_observer_b.on_error_calls[1][1]) == "job failed unexpectedly 6"
        )

        # check that 5 and 6 are not in the success calls for both observers
        assert not any(
            call == jobs[job_idx] for call in mock_observer_a.on_success_calls
        )
        assert not any(
            call == jobs[job_idx] for call in mock_observer_b.on_success_calls
        )

    # check that the other jobs are in the success calls for both observers
    for job_idx in range(10):
        if job_idx not in [5, 6]:
            assert any(
                call == jobs[job_idx] for call in mock_observer_a.on_success_calls
            )
            assert any(
                call == jobs[job_idx] for call in mock_observer_b.on_success_calls
            )

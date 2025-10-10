import asyncio
import sys
from dataclasses import dataclass, field
from typing import Any, AsyncIterable, Callable, Dict, List, Optional, Sequence

from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

if sys.version_info >= (3, 11):
    from asyncio import TaskGroup
else:
    from taskgroup import TaskGroup

from .exceptions import PipelineError, StageValidationError
from .types import CallbackFunc, PipelineStats, TaskCallbackFunc, TaskFunc
from .utils import extract_exception, setup_logger

logger = setup_logger(__name__)


@dataclass
class Stage:
    """
    A stage in the pipeline that processes items through a sequence of tasks.
    """
    name: str
    workers: int
    tasks: Sequence[TaskFunc]
    retry: str = "per_task"
    task_attempts: int = 3
    task_wait_seconds: float = 1.0
    stage_attempts: int = 3
    on_success: Optional[CallbackFunc] = None
    on_failure: Optional[CallbackFunc] = None
    on_retry: Optional[CallbackFunc] = None
    on_task_start: Optional[TaskCallbackFunc] = None
    on_task_success: Optional[TaskCallbackFunc] = None
    on_task_failure: Optional[TaskCallbackFunc] = None
    on_task_retry: Optional[TaskCallbackFunc] = None

    def validate(self) -> None:
        """
        Validate stage configuration.

        Raises:
            StageValidationError: If configuration is invalid
        """
        if self.retry not in ("per_task", "per_stage"):
            raise StageValidationError(
                f"Invalid retry policy for stage '{self.name}': {self.retry}. "
                f"Must be 'per_task' or 'per_stage'"
            )
        if self.workers < 1:
            raise StageValidationError(
                f"Stage '{self.name}' must have at least 1 worker, got {self.workers}"
            )
        if not self.tasks:
            raise StageValidationError(
                f"Stage '{self.name}' must have at least one task"
            )
        if self.task_attempts < 1:
            raise StageValidationError(
                f"Stage '{self.name}' task_attempts must be at least 1, got {self.task_attempts}"
            )
        if self.stage_attempts < 1:
            raise StageValidationError(
                f"Stage '{self.name}' stage_attempts must be at least 1, got {self.stage_attempts}"
            )


class Pipeline:
    """
    A multi-stage async pipeline with worker pools and flexible retry strategies.
    """

    def __init__(
        self,
        stages: List[Stage],
        preserve_order: bool = True,
        collect_results: bool = True
    ):
        """
        Initialize the pipeline.

        Args:
            stages: List of Stage objects defining the pipeline
            preserve_order: If True, maintain input order in results
            collect_results: If True, collect results from final stage

        Raises:
            PipelineError: If stages list is empty
            StageValidationError: If any stage configuration is invalid
        """
        if not stages:
            raise PipelineError("Pipeline must have at least one stage")

        for stage in stages:
            stage.validate()

        self.stages = stages
        self.preserve_order = preserve_order
        self.collect_results = collect_results

        self._stop_event = asyncio.Event()
        self._queues: List[asyncio.Queue] = [asyncio.Queue() for _ in stages]
        self._results: List[Dict[str, Any]] = []
        self._sequence_counter = 0
        self._items_processed = 0
        self._items_failed = 0
        self._worker_tasks: List[asyncio.Task] = []
        self._shutdown = False

    @property
    def results(self) -> List[Dict[str, Any]]:
        """Get collected results, sorted by sequence if preserve_order is True."""
        if self.preserve_order:
            return sorted(self._results, key=lambda x: x.get("_sequence_id", 0))
        return self._results

    def get_stats(self) -> PipelineStats:
        """
        Get current pipeline statistics.

        Returns:
            PipelineStats with current metrics
        """
        queue_sizes = {
            stage.name: self._queues[i].qsize()
            for i, stage in enumerate(self.stages)
        }

        items_in_flight = sum(queue_sizes.values())

        return PipelineStats(
            items_processed=self._items_processed,
            items_failed=self._items_failed,
            items_in_flight=items_in_flight,
            queue_sizes=queue_sizes
        )

    async def feed(self, items: Sequence[Any]) -> None:
        """
        Feed items into the first stage of the pipeline.

        Args:
            items: Sequence of items to process
        """
        q0 = self._queues[0]
        for item in items:
            payload = self._prepare_payload(item)
            await q0.put((payload, 1))
            logger.debug(f"Enqueued item id={payload['id']}")

    async def feed_async(self, items: AsyncIterable[Any]) -> None:
        """
        Feed items from an async iterable into the first stage.

        Args:
            items: Async iterable of items to process
        """
        q0 = self._queues[0]
        async for item in items:
            payload = self._prepare_payload(item)
            await q0.put((payload, 1))
            logger.debug(f"Enqueued item id={payload['id']}")

    def _prepare_payload(self, item: Any) -> Dict[str, Any]:
        """
        Prepare an item as a payload dict with sequence tracking.

        Args:
            item: Input item

        Returns:
            Payload dictionary
        """
        if isinstance(item, dict):
            payload = {
                "id": item.get("id", self._sequence_counter),
                "value": item.get("value", item),
                "_sequence_id": self._sequence_counter
            }
            for k, v in item.items():
                payload.setdefault(k, v)
        else:
            payload = {
                "id": self._sequence_counter,
                "value": item,
                "_sequence_id": self._sequence_counter
            }

        self._sequence_counter += 1
        return payload

    async def run(self, items: Sequence[Any]) -> List[Dict[str, Any]]:
        """
        Run the pipeline end-to-end with the given items.

        Args:
            items: Items to process through the pipeline

        Returns:
            List of result dictionaries
        """
        await self.feed(items)

        async with TaskGroup() as tg:
            for stage_index, stage in enumerate(self.stages):
                name_prefix = stage.name
                input_q = self._queues[stage_index]
                output_q = (
                    self._queues[stage_index + 1]
                    if stage_index + 1 < len(self._queues)
                    else None
                )

                for i in range(stage.workers):
                    worker_name = f"{name_prefix}-W{i}"
                    task = tg.create_task(
                        self._stage_worker(worker_name, stage_index, stage, input_q, output_q)
                    )
                    self._worker_tasks.append(task)

            for q in self._queues:
                await q.join()

            self._stop_event.set()

        return self.results

    async def add_stage(self, stage: Stage, position: Optional[int] = None) -> None:
        """
        Add a stage to the pipeline dynamically.

        Args:
            stage: Stage to add
            position: Position to insert at (None = append to end)

        Raises:
            StageValidationError: If stage configuration is invalid
            PipelineError: If pipeline is currently running
        """
        if self._worker_tasks:
            raise PipelineError("Cannot add stages while pipeline is running")

        stage.validate()

        if position is None:
            self.stages.append(stage)
            self._queues.append(asyncio.Queue())
        else:
            self.stages.insert(position, stage)
            self._queues.insert(position, asyncio.Queue())

        logger.info(f"Added stage '{stage.name}' at position {position or len(self.stages)-1}")

    async def remove_stage(self, name: str) -> None:
        """
        Remove a stage from the pipeline by name.

        Args:
            name: Name of the stage to remove

        Raises:
            PipelineError: If stage not found or pipeline is running
        """
        if self._worker_tasks:
            raise PipelineError("Cannot remove stages while pipeline is running")

        for i, stage in enumerate(self.stages):
            if stage.name == name:
                self.stages.pop(i)
                self._queues.pop(i)
                logger.info(f"Removed stage '{name}'")
                return

        raise PipelineError(f"Stage '{name}' not found")

    async def shutdown(self) -> None:
        """Shut down the pipeline gracefully."""
        if self._shutdown:
            return

        logger.debug("Shutting down pipeline")
        self._shutdown = True
        self._stop_event.set()

        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        logger.debug("Pipeline shutdown complete")

    async def __aenter__(self) -> "Pipeline":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with automatic shutdown."""
        await self.shutdown()

    async def _stage_worker(
        self,
        name: str,
        stage_index: int,
        stage: Stage,
        input_q: asyncio.Queue,
        output_q: Optional[asyncio.Queue],
    ) -> None:
        """
        Worker loop for a single stage.

        Args:
            name: Worker name
            stage_index: Index of this stage
            stage: Stage configuration
            input_q: Input queue
            output_q: Output queue (None for final stage)
        """
        while not self._stop_event.is_set() or not input_q.empty():
            try:
                payload, attempt = await asyncio.wait_for(input_q.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            item_id = payload.get("id")

            try:
                logger.info(f"[{name}] START stage={stage.name} id={item_id} attempt={attempt}")

                if stage.retry == "per_task":
                    result_value = await self._run_per_task(
                        stage, payload["value"], name, item_id
                    )
                else:
                    result_value = await self._run_per_stage(
                        stage, payload["value"], name, item_id, payload, attempt, input_q
                    )
                    if result_value is None:
                        continue

                payload["value"] = result_value

                if stage.on_success:
                    await stage.on_success({**payload, "stage": stage.name})

                if output_q is not None:
                    await output_q.put((payload, 1))
                else:
                    if self.collect_results:
                        self._results.append({**payload})

                self._items_processed += 1
                logger.info(f"[{name}] END stage={stage.name} id={item_id}")

            except Exception as e:
                original_error = extract_exception(e)
                logger.error(
                    f"[{name}] FAIL stage={stage.name} id={item_id} error={original_error}"
                )
                self._items_failed += 1

                if stage.on_failure:
                    await stage.on_failure(
                        {**payload, "stage": stage.name, "error": str(original_error)}
                    )
            finally:
                input_q.task_done()

    async def _run_per_task(
        self,
        stage: Stage,
        value: Any,
        worker_name: str,
        item_id: Any,
    ) -> Any:
        """
        Execute stage tasks with per-task retry strategy.

        Args:
            stage: Stage configuration
            value: Input value
            worker_name: Name of the worker
            item_id: Item identifier

        Returns:
            Final processed value

        Raises:
            RetryError: If a task exhausts its retries
        """
        current = value

        for idx, task in enumerate(stage.tasks):
            task_name = task.__name__
            wrapped = self._wrap_with_tenacity(
                task, stage, worker_name, item_id, task_name
            )

            if stage.on_task_start:
                await stage.on_task_start(task_name, item_id, current)

            logger.debug(
                f"[{worker_name}] START task {idx+1}/{len(stage.tasks)}={task_name} id={item_id}"
            )

            try:
                current = await wrapped(current)

                logger.debug(
                    f"[{worker_name}] END task {idx+1}/{len(stage.tasks)}={task_name} id={item_id}"
                )

                if stage.on_task_success:
                    await stage.on_task_success(task_name, item_id, current)

            except Exception as e:
                original_error = extract_exception(e)
                logger.error(
                    f"[{worker_name}] FAIL task={task_name} id={item_id} error={original_error}"
                )

                if stage.on_task_failure:
                    await stage.on_task_failure(task_name, item_id, original_error)

                raise

        return current

    async def _run_per_stage(
        self,
        stage: Stage,
        value: Any,
        worker_name: str,
        item_id: Any,
        payload: Dict[str, Any],
        attempt: int,
        input_q: asyncio.Queue,
    ) -> Optional[Any]:
        """
        Execute stage tasks with per-stage retry strategy.

        Args:
            stage: Stage configuration
            value: Input value
            worker_name: Worker name
            item_id: Item identifier
            payload: Full payload dict
            attempt: Current attempt number
            input_q: Input queue for re-queueing

        Returns:
            Final value if successful, None if retried or failed
        """
        current = value

        try:
            for idx, task in enumerate(stage.tasks):
                task_name = task.__name__

                if stage.on_task_start:
                    await stage.on_task_start(task_name, item_id, current)

                logger.debug(
                    f"[{worker_name}] START task {idx+1}/{len(stage.tasks)}="
                    f"{task_name} id={item_id}"
                )

                current = await task(current)

                logger.debug(
                    f"[{worker_name}] END task {idx+1}/{len(stage.tasks)}={task_name} id={item_id}"
                )

                if stage.on_task_success:
                    await stage.on_task_success(task_name, item_id, current)

            return current

        except Exception as e:
            original_error = extract_exception(e)

            if attempt < stage.stage_attempts:
                logger.warning(
                    f"[{worker_name}] RETRY stage={stage.name} id={item_id} "
                    f"attempt={attempt} error={original_error}"
                )

                if stage.on_retry:
                    await stage.on_retry(
                        {
                            **payload,
                            "stage": stage.name,
                            "error": str(original_error),
                            "attempt": attempt
                        }
                    )

                await input_q.put((payload, attempt + 1))
                return None
            else:
                logger.error(
                    f"[{worker_name}] FAIL stage={stage.name} id={item_id} "
                    f"after {attempt} attempts error={original_error}"
                )

                if stage.on_failure:
                    await stage.on_failure(
                        {**payload, "stage": stage.name, "error": str(original_error)}
                    )

                return None

    def _wrap_with_tenacity(
        self,
        task: TaskFunc,
        stage: Stage,
        worker_name: str,
        item_id: Any,
        task_name: str,
    ) -> TaskFunc:
        """
        Wrap a task with tenacity retry logic and callbacks.

        Args:
            task: Task to wrap
            stage: Stage configuration
            worker_name: Worker name
            item_id: Item identifier
            task_name: Task name

        Returns:
            Wrapped task function
        """
        @retry(
            stop=stop_after_attempt(stage.task_attempts),
            wait=wait_fixed(stage.task_wait_seconds)
        )
        async def wrapped(x: Any) -> Any:
            try:
                return await task(x)
            except Exception as e:
                logger.warning(
                    f"[{worker_name}] RETRY task={task_name} id={item_id} error={e}"
                )

                if stage.on_task_retry:
                    await stage.on_task_retry(task_name, item_id, e)

                raise

        return wrapped

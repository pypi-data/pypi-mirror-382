import asyncio
import logging
import datetime
import psutil
import time
from functools import total_ordering
from collections import defaultdict
from contextlib import asynccontextmanager
import signal
from sibi_dst.utils import Logger

@total_ordering
class PrioritizedItem:
    def __init__(self, priority, artifact):
        self.priority = priority
        self.artifact = artifact

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

class ArtifactUpdaterMultiWrapper:
    def __init__(self, wrapped_classes=None, debug=False, **kwargs):
        self.wrapped_classes = wrapped_classes or {}
        self.debug = debug
        self.logger = kwargs.setdefault('logger',Logger.default_logger(logger_name=self.__class__.__name__))
        self.logger.set_level(logging.DEBUG if debug else logging.INFO)

        today = datetime.datetime.today()
        self.today_str = today.strftime('%Y-%m-%d')
        self.current_year_starts_on_str = datetime.date(today.year, 1, 1).strftime('%Y-%m-%d')
        self.parquet_start_date = kwargs.get('parquet_start_date', self.current_year_starts_on_str)
        self.parquet_end_date = kwargs.get('parquet_end_date', self.today_str)

        # track concurrency and locks
        self.locks = {}
        self.worker_heartbeat = defaultdict(float)

        # graceful shutdown handling
        loop = asyncio.get_event_loop()
        self.register_signal_handlers(loop)

        # dynamic scaling config
        self.min_workers = kwargs.get('min_workers', 1)
        self.max_workers = kwargs.get('max_workers', 8)
        self.memory_per_worker_gb = kwargs.get('memory_per_worker_gb', 1)  # default 2GB per worker
        self.monitor_interval = kwargs.get('monitor_interval', 10)  # default monitor interval in seconds
        self.retry_attempts = kwargs.get('retry_attempts', 3)
        self.update_timeout_seconds = kwargs.get('update_timeout_seconds', 600)
        self.lock_acquire_timeout_seconds = kwargs.get('lock_acquire_timeout_seconds', 10)

    def register_signal_handlers(self, loop):
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

    async def shutdown(self):
        self.logger.info("Shutdown signal received. Cleaning up...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info("Shutdown complete.")

    def get_lock_for_artifact(self, artifact):
        artifact_key = artifact.__class__.__name__
        if artifact_key not in self.locks:
            self.locks[artifact_key] = asyncio.Lock()
        return self.locks[artifact_key]

    def get_artifacts(self, data_type):
        if data_type not in self.wrapped_classes:
            raise ValueError(f"Unsupported data type: {data_type}")

        return [
            artifact_class(
                parquet_start_date=self.parquet_start_date,
                parquet_end_date=self.parquet_end_date,
                logger=self.logger,
                debug=self.debug
            )
            for artifact_class in self.wrapped_classes[data_type]
        ]

    def estimate_complexity(self, artifact):
        try:
            if hasattr(artifact, 'get_size_estimate'):
                return artifact.get_size_estimate()
        except Exception as e:
            self.logger.warning(f"Failed to estimate complexity for {artifact}: {e}")
        return 1  # default

    def prioritize_tasks(self, artifacts):
        queue = asyncio.PriorityQueue()
        for artifact in artifacts:
            complexity = self.estimate_complexity(artifact)
            # we invert the complexity to ensure higher complexity -> higher priority
            # if you want high complexity first, store negative complexity in the priority queue
            # or if the smaller number means earlier processing, just keep as is
            queue.put_nowait(PrioritizedItem(complexity, artifact))
        return queue

    async def resource_monitor(self, queue, workers):
        """Monitor system resources and adjust worker count while queue is not empty."""
        while True:
            # break if queue done
            if queue.empty():
                await asyncio.sleep(0.5)
                if queue.empty():
                    break

            try:
                available_memory = psutil.virtual_memory().available
                worker_memory_bytes = self.memory_per_worker_gb * (1024 ** 3)
                max_workers_by_memory = available_memory // worker_memory_bytes

                # figure out how many workers we can sustain
                # note: we also cap by self.max_workers
                optimal_workers = min(psutil.cpu_count(), max_workers_by_memory, self.max_workers)

                # ensure at least self.min_workers is used
                optimal_workers = max(self.min_workers, optimal_workers)

                current_worker_count = len(workers)

                if optimal_workers > current_worker_count:
                    # we can add more workers if queue is not empty
                    diff = optimal_workers - current_worker_count
                    for _ in range(diff):
                        worker_id = len(workers)
                        # create a new worker
                        w = asyncio.create_task(self.worker(queue, worker_id))
                        workers.append(w)
                        self.logger.info(f"Added worker {worker_id}. Total workers: {len(workers)}")
                elif optimal_workers < current_worker_count:
                    # remove some workers
                    diff = current_worker_count - optimal_workers
                    for _ in range(diff):
                        w = workers.pop()
                        w.cancel()
                        self.logger.info(f"Removed a worker. Total workers: {len(workers)}")

                await asyncio.sleep(self.monitor_interval)

            except asyncio.CancelledError:
                # monitor is being shut down
                break
            except Exception as e:
                self.logger.error(f"Error in resource_monitor: {e}")
                await asyncio.sleep(self.monitor_interval)

    @asynccontextmanager
    async def artifact_lock(self, artifact):
        lock = self.get_lock_for_artifact(artifact)
        try:
            await asyncio.wait_for(lock.acquire(), timeout=self.lock_acquire_timeout_seconds)
            yield
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout acquiring lock for artifact: {artifact.__class__.__name__}")
            yield  # continue but no actual lock was acquired
        finally:
            if lock.locked():
                lock.release()

    async def async_update_artifact(self, artifact, **kwargs):
        for attempt in range(self.retry_attempts):
            try:
                async with self.artifact_lock(artifact):
                    self.logger.info(
                        f"Updating artifact: {artifact.__class__.__name__}, Attempt: {attempt + 1} of {self.retry_attempts}" )
                    start_time = time.time()
                    await asyncio.wait_for(
                        asyncio.to_thread(artifact.update_parquet, **kwargs),
                        timeout=self.update_timeout_seconds
                    )
                    elapsed_time = time.time() - start_time
                    self.logger.info(
                        f"Successfully updated artifact: {artifact.__class__.__name__} in {elapsed_time:.2f}s." )
                    return

            except asyncio.TimeoutError:
                self.logger.error(f"Timeout updating artifact {artifact.__class__.__name__}, Attempt: {attempt + 1}")
            except Exception as e:
                self.logger.error(
                    f"Error updating artifact {artifact.__class__.__name__}, Attempt: {attempt + 1}: {e}" )

            # exponential backoff
            await asyncio.sleep(2 ** attempt)

        self.logger.error(f"All retry attempts failed for artifact: {artifact.__class__.__name__}")

    async def worker(self, queue, worker_id, **kwargs):
        """A worker that dynamically pulls tasks from the queue."""
        while True:
            try:
                prioritized_item = await queue.get()
                if prioritized_item is None:
                    break
                artifact = prioritized_item.artifact
                # heartbeat
                self.worker_heartbeat[worker_id] = time.time()

                await self.async_update_artifact(artifact, **kwargs)

            except asyncio.CancelledError:
                self.logger.info(f"Worker {worker_id} shutting down gracefully.")
                break
            except Exception as e:
                self.logger.error(f"Error in worker {worker_id}: {e}")
            finally:
                queue.task_done()

    async def process_tasks(self, queue, initial_workers, **kwargs):
        """Start a set of workers and a resource monitor to dynamically adjust them."""
        # create initial workers
        workers = []
        for worker_id in range(initial_workers):
            w = asyncio.create_task(self.worker(queue, worker_id, **kwargs))
            workers.append(w)

        # start resource monitor
        monitor_task = asyncio.create_task(self.resource_monitor(queue, workers))

        # wait until queue is done
        try:
            await queue.join()
        finally:
            # cancel resource monitor
            monitor_task.cancel()
            # all workers done
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

    async def update_data(self, data_type, **kwargs):
        self.logger.info(f"Processing wrapper group: {data_type} with {kwargs}")
        artifacts = self.get_artifacts(data_type)
        queue = self.prioritize_tasks(artifacts)

        # compute initial worker count (this can be low if memory is low initially)
        initial_workers = self.calculate_initial_workers(len(artifacts))
        self.logger.info(f"Initial worker count: {initial_workers} for {len(artifacts)} artifacts")

        total_start_time = time.time()
        await self.process_tasks(queue, initial_workers, **kwargs)
        total_time = time.time() - total_start_time
        self.logger.info(f"Total processing time: {total_time:.2f} seconds.")

    def calculate_initial_workers(self, artifact_count: int) -> int:
        """Compute the initial number of workers before resource_monitor can adjust."""
        self.logger.info("Calculating initial worker count...")
        available_memory = psutil.virtual_memory().available
        self.logger.info(f"Available memory: {available_memory / (1024 ** 3):.2f} GB")
        worker_memory_bytes = self.memory_per_worker_gb * (1024 ** 3)
        self.logger.info(f"Memory per worker: {worker_memory_bytes / (1024 ** 3):.2f} GB")
        max_workers_by_memory = available_memory // worker_memory_bytes
        self.logger.info(f"Max workers by memory: {max_workers_by_memory}")
        # also consider CPU count and artifact_count
        initial = min(psutil.cpu_count(), max_workers_by_memory, artifact_count, self.max_workers)
        self.logger.info(f"Optimal workers: {initial} CPU: {psutil.cpu_count()} Max Workers: {self.max_workers}")
        return max(self.min_workers, initial)


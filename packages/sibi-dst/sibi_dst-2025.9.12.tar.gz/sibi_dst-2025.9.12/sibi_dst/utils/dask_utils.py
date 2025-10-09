from __future__ import annotations

import asyncio
from typing import List, Any, Dict

import dask
#dask.config.set({"distributed.worker.daemon": False})
import dask.dataframe as dd

def _to_int_safe(x) -> int:
    """
    Convert scalar-like to int safely.
    Handles numpy scalars, pandas Series/DataFrame outputs.
    """
    if hasattr(x, "item"):        # numpy scalar, pandas scalar
        return int(x.item())
    if hasattr(x, "iloc"):        # Series-like
        return int(x.iloc[0])
    return int(x)

def dask_is_probably_empty(ddf: dd.DataFrame) -> bool:
    return getattr(ddf, "npartitions", 0) == 0 or len(ddf._meta.columns) == 0


def dask_is_empty_truthful(ddf: dd.DataFrame) -> bool:
    n = ddf.map_partitions(len).sum().compute()
    return int(n) == 0


def dask_is_empty(ddf: dd.DataFrame, *, sample: int = 4) -> bool:
    if dask_is_probably_empty(ddf):
        return True

    k = min(max(sample, 1), ddf.npartitions)
    probes = dask.compute(*[
        ddf.get_partition(i).map_partitions(len) for i in range(k)
    ], scheduler="threads")

    if any(_to_int_safe(n) > 0 for n in probes):
        return False
    if k == ddf.npartitions and all(_to_int_safe(n) == 0 for n in probes):
        return True

    return dask_is_empty_truthful(ddf)

class UniqueValuesExtractor:
    @staticmethod
    def _compute_to_list_sync(series) -> List[Any]:
        """Run in a worker thread when Dask-backed."""
        if hasattr(series, "compute"):
            return series.compute().tolist()
        return series.tolist()

    async def compute_to_list(self, series) -> List[Any]:
        # Offload potential Dask .compute() to a thread to avoid blocking the event loop
        return await asyncio.to_thread(self._compute_to_list_sync, series)

    async def extract_unique_values(self, df, *columns: str) -> Dict[str, List[Any]]:
        async def one(col: str):
            ser = df[col].dropna().unique()
            return col, await self.compute_to_list(ser)

        pairs = await asyncio.gather(*(one(c) for c in columns))
        return dict(pairs)

from contextlib import suppress
from dask.distributed import Client, LocalCluster, get_client
import os

class DaskClientMixin:
    """
    Provides shared Dask client lifecycle management.
    Ensures reuse of an existing client if available,
    or creates a local in-process Dask cluster for fallback.
    """

    def _init_dask_client(
        self,
        dask_client=None,
        logger=None,
        *,
        n_workers: int = 1,
        threads_per_worker: int = 1,
        processes: bool = False,
        asynchronous: bool = False,
        memory_limit: str = "auto",
        #dashboard_address: str | None = None,
        local_directory: str | None = None,
        silence_logs: str = "info",
        resources: dict | None = None,
        timeout: int = 30,
    ):
        self.dask_client = dask_client
        self.own_dask_client = False
        self.logger = logger

        if self.dask_client is None:
            with suppress(ValueError, RuntimeError):
                # Try to attach to an existing client (common in shared Dask setups)
                self.dask_client = get_client()

        if self.dask_client is None:
            # Default to half of logical cores if not specified
            n_workers = n_workers or max(2, os.cpu_count() // 2)

            cluster = LocalCluster(
                n_workers=n_workers,
                threads_per_worker=threads_per_worker,
                processes=processes,
                asynchronous=asynchronous,
                memory_limit=memory_limit,
                local_directory=local_directory,
                silence_logs=silence_logs,
                resources=resources,
                timeout=timeout,
            )

            self.dask_client = Client(cluster)
            self.own_dask_client = True

            if self.logger:
                self.logger.info(
                    f"Started local Dask cluster with {n_workers} workers × {threads_per_worker} threads "
                    f"({memory_limit} memory per worker). Dashboard: {self.dask_client.dashboard_link}"
                )
        else:
            if self.logger:
                self.logger.debug(
                    f"Using existing Dask client: {self.dask_client.dashboard_link}"
                )

    def _close_dask_client(self):
        """Close the Dask client if this instance created it."""
        if getattr(self, "own_dask_client", False) and self.dask_client is not None:
            try:
                cluster = getattr(self.dask_client, "cluster", None)
                self.dask_client.close()
                if cluster is not None:
                    cluster.close()
                if self.logger:
                    self.logger.info("Closed local Dask client and cluster.")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error while closing Dask client: {e}")

# from contextlib import suppress
# from dask.distributed import Client, get_client
#
# class DaskClientMixin:
#     """
#     Provides shared Dask client lifecycle management.
#     Ensures reuse of existing client when available, otherwise creates a lightweight local one.
#     """
#
#     def _init_dask_client(self, dask_client=None, logger=None):
#         self.dask_client = dask_client
#         self.own_dask_client = False
#         self.logger = logger
#
#         if self.dask_client is None:
#             with suppress(ValueError, RuntimeError):
#                 # Try to attach to an existing active client if running inside a Dask context
#                 self.dask_client = get_client()
#
#         if self.dask_client is None:
#             # Start a local in-process scheduler for fallback
#             self.dask_client = Client(processes=False)
#             self.own_dask_client = True
#             if self.logger:
#                 self.logger.info(f"Started local Dask client: {self.dask_client.dashboard_link}")
#         else:
#             if self.logger:
#                 self.logger.debug(f"Using existing Dask client: {self.dask_client.dashboard_link}")
#
#     def _close_dask_client(self):
#         """Close client only if this instance created it."""
#         if getattr(self, "own_dask_client", False) and self.dask_client is not None:
#             try:
#                 self.dask_client.close()
#                 if self.logger:
#                     self.logger.info("Closed local Dask client.")
#             except Exception as e:
#                 if self.logger:
#                     self.logger.warning(f"Error while closing Dask client: {e}")
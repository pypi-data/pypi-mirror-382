import asyncio
import multiprocessing
import logging
from typing import List, Dict, Any, Set
from .core import Target
from .factory import ScraperFactory

log = logging.getLogger("spidur.runner")


def _run_batch(batch: List[Target], out: Any, seen: Set[str]):
    """
    Internal helper to run a batch of scrapers concurrently in an async loop.
    Executed in a separate process by multiprocessing.
    """

    async def _inner():
        for target in batch:
            log.info(f"[spidur] Running scraper: {target.name}")
            scraper = ScraperFactory.create(target)
            try:
                results = await scraper.fetch_round(seen)
                out[target.name] = results or []
            except Exception as e:
                log.exception(f"[spidur] Error in scraper '{target.name}': {e}")
                out[target.name] = []

    asyncio.run(_inner())


class Runner:
    """Parallel runner to execute multiple scrapers concurrently across CPU cores."""

    @classmethod
    def run(
        cls, targets: List[Target], seen: Set[str] | None = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        if not targets:
            return {}

        seen = seen or set()
        num_cores = multiprocessing.cpu_count()
        batch_size = max(1, len(targets) // num_cores)
        batches = [
            targets[i : i + batch_size] for i in range(0, len(targets), batch_size)
        ]

        with multiprocessing.Manager() as manager:
            out = manager.dict()
            jobs = [
                multiprocessing.Process(target=_run_batch, args=(batch, out, seen))
                for batch in batches
            ]

            for job in jobs:
                job.start()
            for job in jobs:
                job.join()

            return dict(out)

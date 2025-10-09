import asyncio, time, random
from typing import Any, Dict, Optional
from dataclasses import dataclass
from loguru import logger







@dataclass
class _PlannedJob:
    key: str
    payload: Dict[str, Any]
    run_at_monotonic: float


class Planner:
    """
    Planner :
     - schedule(key, payload, interval, jitter) schedule serial task
     - start() run.
     - close() shutdown.
     - reset() reset all without worker
     - full_reset() reset full
    """
    def __init__(
        self,
        on_expire,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        process_interval: float = 2.0,
        max_proc: int = 2000
    ):
        
        if not asyncio.iscoroutinefunction(on_expire):
            raise TypeError("on_expire should be coroutine function")
        self.on_expire = on_expire
        self.loop = loop or asyncio.get_event_loop()
        self._queue: "asyncio.Queue[_PlannedJob]" = asyncio.Queue(maxsize=max_proc)
        self._last_sched: Dict[str, float] = {}      # key -> monotonic last scheduled run time
        self._timers: Dict[str, asyncio.Task] = {}   # key -> timer task (only last)
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False
        self._shutdown = False
        self.process_interval = float(process_interval)


    @property
    def running(self) -> bool:
        return self._running and not self._shutdown

    @property
    def stopped(self) -> bool:
        return self._shutdown


    async def start(self):
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop(), name="attack-planner-worker")


    async def close(self):
        
        self._shutdown = True
        for t in list(self._timers.values()):
            if not t.done():
                t.cancel()
        self._timers.clear()
        
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()
        
        except asyncio.QueueEmpty:
            pass
        
        
        if self._worker_task:
            await self._queue.put(_PlannedJob("__SENTINEL__", {}, time.monotonic()))
            try:
                await self._worker_task
            except Exception:
                pass
            self._worker_task = None
        
        self._last_sched.clear()


    async def reset(self):
        for t in list(self._timers.values()):
            if not t.done():
                t.cancel()
            
        self._timers.clear()
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()

        except asyncio.QueueEmpty:
            pass
        self._last_sched.clear()


    async def full_reset(self):
        await self.close()
        await self.start()


    async def schedule_after_last(self, key: str, payload: Dict[str, Any], *, interval: float = 1.0, jitter: float = 0.0):
 
        now = time.monotonic()
        last = self._last_sched.get(key, now)
        base = max(now, last)
        j = random.uniform(-jitter, jitter) if jitter and jitter > 0 else 0.0
        run_at = base + max(0.0, float(interval) + j)
        # update last scheduled time
        self._last_sched[key] = run_at

        # cancel previous timer for same key (we only care about last scheduled timer)
        prev = self._timers.get(key)
        if prev and not prev.done():
            prev.cancel()

        # schedule timer that will put planned job into the queue at run_at
        async def _timer():
            try:
                to_wait = run_at - time.monotonic()
                if to_wait > 0:
                    await asyncio.sleep(to_wait)
                if self._shutdown:
                    return
                await self._queue.put(_PlannedJob(key=key, payload=payload, run_at_monotonic=run_at))
            except asyncio.CancelledError:
                return
            except Exception:
                return
            finally:
                # remove timer reference when done
                self._timers.pop(key, None)

        t = asyncio.create_task(_timer(), name=f"attack-planner-timer-{key}")
        self._timers[key] = t
        return True



    async def _worker_loop(self):

        while True:
            job = await self._queue.get()
            if job.key == "__SENTINEL__":
                break
            try:
                await self.on_expire (job.key, job.payload)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                # swallow to avoid killing worker; log externally if desired
                try:
                    
                    logger.exception("AttackPlanner: attack_cb raised: %s", e)
                except Exception:
                    pass
            # enforce interval between processing jobs
            if self.process_interval > 0:
                try:
                    await asyncio.sleep(self.process_interval)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass
        return

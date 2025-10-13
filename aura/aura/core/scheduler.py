import logging
import signal
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Protocol, Set, Tuple

from aura.core import monitor, runner, store
from aura.core.job import Job, JobState

if TYPE_CHECKING:
    class HeuristicPluginProtocol(Protocol):
        def select(
            self, 
            candidates: List[Job], 
            running: List[Job], 
            capacity_total: int,
            cap_build: int = 0,
            cap_solve: int = 0
        ) -> List[Job]:
            """Select jobs to run based on heuristic."""
            ...


class Scheduler:
    """
    Job scheduler that manages lifecycle, applies heuristics, and runs build/solve in parallel.
    
    Manages Jobs discovery, phase selection (build/solve), plugin consultation for job selection,
    and dispatches runner operations with real parallelism using separate limits for each phase.
    """
    
    def __init__(
        self,
        demand_root: Path,
        plugin: "HeuristicPluginProtocol",
        max_build: int = 1,
        max_solve: int = 1,
        poll_interval: float = 0.2,
    ) -> None:
        """
        Initialize scheduler.
        
        Args:
            demand_root: Root directory to discover family directories
            plugin: Heuristic plugin for job selection
            max_build: Maximum concurrent build jobs
            max_solve: Maximum concurrent solve jobs
            poll_interval: Sleep interval between scheduler iterations in seconds
        """
        self.demand_root = Path(demand_root)
        self.plugin = plugin
        self.max_build = max_build
        self.max_solve = max_solve
        self.poll_interval = poll_interval
        
        # Internal state
        self._jobs: List[Job] = []
        self._jobs_by_id: Dict[str, Job] = {}  # O(1) lookup for jobs
        self._executor = ThreadPoolExecutor(max_workers=max_build + max_solve)
        self._running_futures: Dict[Future, Tuple[str, str]] = {}  # future -> (job_id, phase)
        self._running_by_phase: Dict[str, Set[str]] = {
            "build": set(),
            "solve": set()
        }
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
        self._stop_requested = False
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self._logger.info(f"Received signal {signum}, requesting graceful shutdown...")
            self._stop_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def discover_jobs(self) -> List[Job]:
        """
        Scan demand_root; for each direct subdirectory, create a Job and return the list.
        Also populate the jobs_by_id map for O(1) lookup.
        
        Returns:
            List of discovered jobs
        """
        jobs = []
        jobs_by_id = {}
        
        if not self.demand_root.exists():
            self._logger.warning(f"Demand root directory does not exist: {self.demand_root}")
            return jobs
            
        for family_dir in self.demand_root.iterdir():
            if family_dir.is_dir():
                try:
                    job = Job(family_dir=family_dir)
                    jobs.append(job)
                    jobs_by_id[job.id] = job
                    self._logger.info(f"Discovered job {job.id} for family {family_dir.name}")
                except Exception as e:
                    self._logger.error(f"Failed to create job for {family_dir}: {e}")
        
        # Update the jobs_by_id map
        self._jobs_by_id = jobs_by_id
        return jobs
    
    def run(self) -> None:
        """
        Main loop:
        - while there are pending/running jobs and not stopped:
          - self.run_once()
          - configurable sleep interval
        """
        # Discover initial jobs
        self._jobs = self.discover_jobs()
        self._logger.info(f"Starting scheduler with {len(self._jobs)} jobs")
        
        while self._has_pending_or_running_jobs() and not self._stop_requested:
            self.run_once()
            time.sleep(self.poll_interval)
        
        if self._stop_requested:
            self._logger.info("Scheduler stopping due to signal - waiting for running jobs to complete")
            # Wait for running jobs to complete
            while self._running_futures:
                time.sleep(self.poll_interval)
                self._process_completed_futures()
            
        self._logger.info("Scheduler finished - no more pending or running jobs")
        self._executor.shutdown(wait=True)
    
    def run_once(self) -> None:
        """
        Single iteration:
        - Scan completed futures, call _on_phase_finished().
        - Collect 'candidates' (jobs ready for next phase).
        - Calculate remaining capacity separated: build and solve.
        - Ask plugin: select(candidates, running, capacity_total, cap_build, cap_solve) and filter by phase/capacity.
        - For each chosen, _start_next_phase(job).
        """
        with self._lock:
            # Process completed futures
            self._process_completed_futures()
            
            # Don't start new jobs if stop was requested
            if self._stop_requested:
                return
            
            # Collect candidates (jobs ready for next phase)
            candidates = []
            running_jobs = []
            
            for job in self._jobs:
                if job.id in self._running_by_phase["build"] or job.id in self._running_by_phase["solve"]:
                    running_jobs.append(job)
                else:
                    next_phase = self._phase_for(job)
                    if next_phase:
                        candidates.append(job)
            
            if not candidates:
                return
                
            # Calculate capacities
            running_build = len(self._running_by_phase["build"])
            running_solve = len(self._running_by_phase["solve"])
            cap_build = self.max_build - running_build
            cap_solve = self.max_solve - running_solve
            capacity_total = cap_build + cap_solve
            
            if capacity_total <= 0:
                return
                
            # Ask plugin to select jobs with separate capacities
            selected_jobs = self.plugin.select(
                candidates, running_jobs, capacity_total, cap_build, cap_solve
            )
            
            # Start phases respecting capacity limits
            for job in selected_jobs:
                phase = self._phase_for(job)
                if not phase:
                    continue
                    
                # Check if we have capacity for this phase (recalculate as we might have started others)
                current_build = len(self._running_by_phase["build"])
                current_solve = len(self._running_by_phase["solve"])
                
                if phase == "build" and current_build >= self.max_build:
                    continue
                if phase == "solve" and current_solve >= self.max_solve:
                    continue
                    
                self._start_next_phase(job)
    
    def _process_completed_futures(self) -> None:
        """Process all completed futures and update job states."""
        completed_futures = [f for f in self._running_futures.keys() if f.done()]
        
        for future in completed_futures:
            job_id, phase = self._running_futures.pop(future)
            self._running_by_phase[phase].discard(job_id)
            
            # Find the job using O(1) lookup
            job = self._jobs_by_id.get(job_id)
            if job is None:
                self._logger.error(f"Job {job_id} not found for completed {phase} future")
                continue
                
            try:
                result = future.result()
                success = result.get("ok", False)
                self._on_phase_finished(job, phase, success, result)
            except Exception as e:
                self._logger.error(f"Exception in {phase} for job {job_id}: {e}")
                self._on_phase_finished(job, phase, False, {"error": str(e)})
    
    def _phase_for(self, job: Job) -> Optional[str]:
        """
        Return 'build' if state==CREATED, 'solve' if state==BUILT; otherwise None/''.
        
        Args:
            job: Job to determine phase for
            
        Returns:
            Next phase for the job or None if no next phase
        """
        if job.state == JobState.CREATED:
            return "build"
        elif job.state == JobState.BUILT:
            return "solve"
        else:
            return None
    
    def _start_next_phase(self, job: Job) -> None:
        """
        Dispatch correct phase via ThreadPoolExecutor:
        - build → runner.run_build(job)
        - solve → runner.run_solve(job)
        Register Future in self._running_futures[future] = (job.id, phase).
        Update running counters by phase.
        Also call store.record_event(job, phase, 'started', initial_meta).
        """
        phase = self._phase_for(job)
        if not phase:
            return
            
        # Record start event
        initial_meta = {
            "job_id": job.id,
            "family_dir": str(job.family_dir),
            "phase": phase
        }
        store.record_event(job, phase, "started", initial_meta)
        
        # Submit to executor
        if phase == "build":
            future = self._executor.submit(runner.run_build, job)
        elif phase == "solve":
            future = self._executor.submit(runner.run_solve, job)
        else:
            self._logger.error(f"Unknown phase: {phase}")
            return
            
        # Track the future
        self._running_futures[future] = (job.id, phase)
        self._running_by_phase[phase].add(job.id)
        
        self._logger.info(f"Started {phase} for job {job.id}")
    
    def _on_phase_finished(self, job: Job, phase: str, ok: bool, meta: Dict) -> None:
        """
        - Update running phase counters.
        - Call store.record_event(job, phase, 'finished', meta).
        - If ok and phase=='build' and job.state==BUILT → leave to enter as solve candidate next cycle.
        - If ok and phase=='solve' → job.state should be SOLVED (already marked in runner).
        - If failure → job.state should be FAILED; don't retry.
        - Call monitor.extract_metrics(job) if exists and include in store (optional).
        """
        # Record finish event
        finish_meta = dict(meta)
        finish_meta.update({
            "success": ok,
            "job_id": job.id,
            "phase": phase
        })
        
        # Try to extract metrics if monitor has the method
        try:
            if hasattr(monitor, 'extract_metrics'):
                metrics = monitor.extract_metrics(job)
                finish_meta["metrics"] = metrics
        except Exception as e:
            self._logger.warning(f"Failed to extract metrics for job {job.id}: {e}")
        
        store.record_event(job, phase, "finished", finish_meta)
        
        if ok:
            if phase == "build" and job.state == JobState.BUILT:
                self._logger.info(f"Job {job.id} build completed successfully - ready for solve")
            elif phase == "solve" and job.state == JobState.SOLVED:
                self._logger.info(f"Job {job.id} solve completed successfully")
        else:
            self._logger.error(f"Job {job.id} {phase} failed")
    
    def _has_pending_or_running_jobs(self) -> bool:
        """Check if there are jobs pending or running."""
        with self._lock:
            # Check if any futures are running
            if self._running_futures:
                return True
                
            # Check if any jobs are ready for next phase
            for job in self._jobs:
                if self._phase_for(job) is not None:
                    return True
                    
            return False

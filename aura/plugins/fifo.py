"""
FIFO (First In, First Out) heuristic plugin.

This plugin implements a simple FIFO scheduling heuristic that prioritizes
jobs based on their creation time while respecting phase-specific capacity limits.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..core.job import Job, JobState
else:
    # Import at runtime to avoid circular imports
    from ..core.job import JobState


class FifoHeuristic:
    """
    FIFO heuristic that selects jobs in creation order.
    
    This heuristic sorts candidates by creation time (oldest first) and selects
    jobs while respecting the capacity limits for each phase (build/solve).
    """
    
    def name(self) -> str:
        """Return the name of this heuristic plugin."""
        return "fifo"
    
    def select(
        self,
        candidates: list["Job"],
        running: list["Job"],
        capacity_total: int,
        cap_build: int,
        cap_solve: int,
    ) -> list["Job"]:
        """
        Select jobs using FIFO heuristic with phase capacity limits.
        
        Args:
            candidates: List of jobs ready for their next phase
            running: List of jobs currently running (to be excluded)
            capacity_total: Total remaining capacity across all phases
            cap_build: Remaining capacity for build phase
            cap_solve: Remaining capacity for solve phase
            
        Returns:
            List of selected jobs (subset of candidates) in FIFO order
        """
        if not candidates or capacity_total <= 0:
            return []
        
        # Create set of running job IDs for fast lookup
        running_ids = {job.id for job in running}
        
        # Filter out already running jobs
        available_candidates = [
            job for job in candidates 
            if job.id not in running_ids
        ]
        
        if not available_candidates:
            return []
        
        # Sort candidates by creation time (FIFO - oldest first)
        sorted_candidates = sorted(
            available_candidates,
            key=lambda job: job.created_at or job.id  # Fallback to ID if created_at is None
        )
        
        selected = []
        remaining_total = capacity_total
        remaining_build = cap_build
        remaining_solve = cap_solve
        
        # Iterate through sorted candidates and select based on phase capacity
        for job in sorted_candidates:
            if remaining_total <= 0:
                break
                
            next_phase = self._determine_next_phase(job)
            
            if next_phase == "build" and remaining_build > 0:
                selected.append(job)
                remaining_build -= 1
                remaining_total -= 1
            elif next_phase == "solve" and remaining_solve > 0:
                selected.append(job)
                remaining_solve -= 1
                remaining_total -= 1
            # If job doesn't have a valid next phase or no capacity, skip it
        
        return selected
    
    def _determine_next_phase(self, job: "Job") -> Optional[str]:
        """
        Determine the next phase for a job (replicated from scheduler logic).
        
        Args:
            job: Job to determine next phase for
            
        Returns:
            'build' if state==CREATED, 'solve' if state==BUILT, None otherwise
        """
        if job.state == JobState.CREATED:
            return "build"
        elif job.state == JobState.BUILT:
            return "solve"
        else:
            return None

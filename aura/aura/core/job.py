from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING
import logging
import uuid

if TYPE_CHECKING:
    from aura.core.monitor import MetricsCollector

logger = logging.getLogger(__name__)


class JobState(Enum):
    CREATED = "CREATED"
    BUILDING = "BUILDING"
    BUILT = "BUILT"
    SOLVING = "SOLVING"
    SOLVED = "SOLVED"
    FAILED = "FAILED"


@dataclass
class Job:
    family_dir: Path
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proto_path: Optional[Path] = None
    output_dir: Optional[Path] = None
    state: JobState = JobState.CREATED
    created_at: Optional[datetime] = None
    build_started_at: Optional[datetime] = None
    build_finished_at: Optional[datetime] = None
    solve_started_at: Optional[datetime] = None
    solve_finished_at: Optional[datetime] = None
    # Container tracking for precise metrics
    current_container_id: Optional[str] = None
    build_container_id: Optional[str] = None
    solve_container_id: Optional[str] = None
    
    # Continuous metrics collection
    _metrics_collector: Optional["MetricsCollector"] = field(default=None, init=False, repr=False)
    
    def __post_init__(self) -> None:
        """
        Post-initialization to normalize paths, create directories, and set timestamps.
        """
        # Normalize paths
        self.family_dir = Path(self.family_dir).resolve()
        
        # Set default proto_path if not provided
        if self.proto_path is None:
            self.proto_path = self.family_dir / "model.pb"
        else:
            self.proto_path = Path(self.proto_path).resolve()
            
        # Set default output_dir if not provided
        if self.output_dir is None:
            self.output_dir = self.family_dir / "output"
        else:
            self.output_dir = Path(self.output_dir).resolve()
            
        # Create directories if they don't exist
        self.family_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def output_log(self) -> Path:
        """Path to the output log file."""
        return self.output_dir / "output.log"
    
    @property
    def error_log(self) -> Path:
        """Path to the error log file."""
        return self.output_dir / "error.log"
    
    @property
    def cpu_csv(self) -> Path:
        """Path to the CPU usage CSV file."""
        return self.output_dir / "cpu_output.csv"
    
    @property
    def mem_csv(self) -> Path:
        """Path to the memory usage CSV file."""
        return self.output_dir / "memory_output.csv"
    
    def mark_build_started(self) -> None:
        """Mark the job as starting the build phase."""
        self.state = JobState.BUILDING
        self.build_started_at = datetime.now()
    
    def mark_build_finished(self, success: bool) -> None:
        """
        Mark the job as finished the build phase.
        """
        self.build_finished_at = datetime.now()
        if success:
            self.state = JobState.BUILT
        else:
            self.state = JobState.FAILED
        
        # Clear current container ID as phase is finished
        self.current_container_id = None
    
    def mark_solve_started(self) -> None:
        """Mark the job as starting the solve phase."""
        self.state = JobState.SOLVING
        self.solve_started_at = datetime.now()
    
    def mark_solve_finished(self, success: bool) -> None:
        """
        Mark the job as finished the solve phase.
        """
        self.solve_finished_at = datetime.now()
        if success:
            self.state = JobState.SOLVED
        else:
            self.state = JobState.FAILED
        
        # Clear current container ID as phase is finished
        self.current_container_id = None
    
    def set_container_id(self, container_id: str, phase: str) -> None:
        """
        Set container ID for the current running phase.
        
        Args:
            container_id: Docker container ID
            phase: Current phase ('build' or 'solve')
        """
        self.current_container_id = container_id
        
        if phase == "build":
            self.build_container_id = container_id
        elif phase == "solve":
            self.solve_container_id = container_id
    
    def clear_container_id(self) -> None:
        """Clear current container ID when phase finishes."""
        self.current_container_id = None
    
    def start_metrics_collection(self, container_id: str, phase: str) -> None:
        """
        Start continuous metrics collection for the current phase.
        
        Args:
            container_id: Docker container ID to monitor
            phase: Current phase ('build' or 'solve')
        """
        # Import here to avoid circular import
        from aura.core.monitor import MetricsCollector
        from aura.config import get_runs_dir
        
        # Stop any existing collector
        self.stop_metrics_collection()
        
        # Create CSV file path for granular metrics
        runs_dir = Path(get_runs_dir())
        csv_file = runs_dir / f"{self.id}_{phase}_metrics.csv"
        
        # Start new collector
        try:
            self._metrics_collector = MetricsCollector(container_id, csv_file=csv_file)
            self._metrics_collector.start()
            self.set_container_id(container_id, phase)
            logger.info(f"Started metrics collection for job {self.id} container {container_id} (CSV: {csv_file})")
        except Exception as e:
            logger.error(f"Failed to start metrics collection for job {self.id}: {e}")
            self._metrics_collector = None
    
    def stop_metrics_collection(self) -> Dict:
        """
        Stop continuous metrics collection and return collected stats.
        
        Returns:
            Dictionary with collected metrics statistics
        """
        if self._metrics_collector is None:
            return {
                "cpu": {"max": None, "mean": None, "min": None, "count": 0},
                "memory": {"max": None, "mean": None, "min": None, "count": 0},
                "collection": {"samples_count": 0, "method": "none"}
            }
        
        try:
            # Get stats before stopping
            stats = self._metrics_collector.get_stats()
            
            # Stop the collector
            self._metrics_collector.stop()
            self._metrics_collector = None
            
            logger.info(f"Stopped metrics collection for job {self.id}, collected {stats['collection']['samples_count']} samples")
            return stats
            
        except Exception as e:
            logger.error(f"Error stopping metrics collection for job {self.id}: {e}")
            self._metrics_collector = None
            return {
                "cpu": {"max": None, "mean": None, "min": None, "count": 0},
                "memory": {"max": None, "mean": None, "min": None, "count": 0},
                "collection": {"samples_count": 0, "method": "error"}
            }
    
    def get_current_metrics(self) -> Dict:
        """
        Get current metrics without stopping collection.
        
        Returns:
            Dictionary with current metrics statistics
        """
        if self._metrics_collector is None:
            return {
                "cpu": {"max": None, "mean": None, "min": None, "count": 0},
                "memory": {"max": None, "mean": None, "min": None, "count": 0},
                "collection": {"samples_count": 0, "method": "none"}
            }
        
        try:
            return self._metrics_collector.get_stats()
        except Exception as e:
            logger.error(f"Error getting current metrics for job {self.id}: {e}")
            return {
                "cpu": {"max": None, "mean": None, "min": None, "count": 0},
                "memory": {"max": None, "mean": None, "min": None, "count": 0},
                "collection": {"samples_count": 0, "method": "error"}
            }
    
    def get_container_id_for_phase(self, phase: str) -> Optional[str]:
        """
        Get container ID for a specific phase.
        
        Args:
            phase: Phase name ('build' or 'solve')
            
        Returns:
            Container ID for the phase or None if not available
        """
        if phase == "build":
            return self.build_container_id
        elif phase == "solve":
            return self.solve_container_id
        else:
            return self.current_container_id
    
    def cleanup_model(self) -> dict:
        """
        Clean up the model.pb file to save disk space after solve completion.
        
        This method should be called after a successful solve, as the model file
        is no longer needed and can be quite large (300-400MB).
        
        Returns:
            Dictionary with cleanup results containing 'success', 'file_size_mb', 
            'file_existed' and optional 'error' information.
        """
        logger = logging.getLogger(__name__)
        result = {
            'success': False,
            'file_existed': False,
            'file_size_mb': 0.0,
            'path': str(self.proto_path)
        }
        
        try:
            if self.proto_path and self.proto_path.exists():
                result['file_existed'] = True
                
                # Get file size in MB before deletion
                file_size_bytes = self.proto_path.stat().st_size
                result['file_size_mb'] = round(file_size_bytes / (1024 * 1024), 2)
                
                # Delete the file
                self.proto_path.unlink()
                result['success'] = True
                
                logger.info(
                    f"Successfully cleaned up model file for job {self.id}: "
                    f"{result['file_size_mb']}MB saved from {self.proto_path}"
                )
                
            else:
                # File doesn't exist, consider it successful cleanup
                result['success'] = True
                logger.debug(f"Model file already absent for job {self.id}: {self.proto_path}")
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            logger.error(
                f"Failed to cleanup model file for job {self.id} at {self.proto_path}: {e}"
            )
        
        return result


def new_job(family_dir: Path | str, id: Optional[str] = None) -> Job:
    job_id = id if id is not None else str(uuid.uuid4())
    return Job(family_dir=family_dir, id=job_id)

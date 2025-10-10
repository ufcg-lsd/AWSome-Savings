import logging
import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict

from dotenv import load_dotenv

if TYPE_CHECKING:
    from .job import Job

# Load environment variables
load_dotenv()

# Get optimizer image from environment
OPTIMIZER_IMAGE = os.getenv("OPTIMIZER_IMAGE")
if not OPTIMIZER_IMAGE:
    raise RuntimeError("OPTIMIZER_IMAGE environment variable is required but not set")

logger = logging.getLogger(__name__)


def _check_docker_available() -> None:
    """Check if docker command is available."""
    try:
        subprocess.run(
            ["docker", "--version"], 
            check=True, 
            capture_output=True, 
            text=True
        )
    except FileNotFoundError:
        raise RuntimeError("Docker is not available. Please install Docker to run the optimizer.")
    except subprocess.CalledProcessError:
        raise RuntimeError("Docker command failed. Please check Docker installation.")


def _build_docker_command(job: Job, script_name: str) -> list[str]:
    """Build docker run command for the given job and script."""
    return [
        "docker", "run", "--rm",
        "-v", f"{job.family_dir}:/optimizer-files",
        "-v", f"{job.family_dir}:/optimizer-proto", 
        "-v", f"{job.output_dir}:/optimizer-logs",
        OPTIMIZER_IMAGE,
        "/bin/sh", "-c",
        f"/optimizer/{script_name} /optimizer-files /optimizer-logs /optimizer-proto/model.pb"
    ]


def _run_docker_command(cmd: list[str]) -> tuple[int, float]:
    """
    Run docker command and return exit code and duration.
    
    Returns:
        Tuple of (exit_code, duration_in_seconds)
    """
    start_time = time.monotonic()
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        exit_code = result.returncode
    except Exception as e:
        logger.error(f"Error running docker command: {e}")
        exit_code = 1
    
    end_time = time.monotonic()
    duration = end_time - start_time
    
    return exit_code, duration


def run_build(job: Job) -> Dict:
    """
    Run build phase for the given job.
    
    Args:
        job: Job instance to run build for
        
    Returns:
        Dictionary with execution metadata
    """
    _check_docker_available()
    
    # Ensure output directory exists
    job.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mark build started
    job.mark_build_started()
    
    try:
        # Build docker command
        cmd = _build_docker_command(job, "run_build.sh")
        cmd_str = shlex.join(cmd)
        
        logger.info(f"Running build command: {cmd_str}")
        
        # Execute command
        exit_code, duration = _run_docker_command(cmd)
        
        # Determine success
        success = (exit_code == 0)
        
        # Mark build finished
        job.mark_build_finished(success)
        
        return {
            "ok": success,
            "exit_code": exit_code,
            "duration_sec": duration,
            "image": OPTIMIZER_IMAGE,
            "cmd": cmd_str,
            "logs": {
                "output": str(job.output_log),
                "error": str(job.error_log)
            },
            "metrics": {
                "cpu": str(job.cpu_csv),
                "memory": str(job.mem_csv)
            }
        }
        
    except Exception as e:
        # Mark build as failed
        job.mark_build_finished(False)
        logger.error(f"Build failed with exception: {e}")
        raise


def run_solve(job: Job) -> Dict:
    """
    Run solve phase for the given job.
    
    Args:
        job: Job instance to run solve for
        
    Returns:
        Dictionary with execution metadata
    """
    _check_docker_available()
    
    # Ensure output directory exists
    job.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mark solve started
    job.mark_solve_started()
    
    try:
        # Build docker command
        cmd = _build_docker_command(job, "run_solve.sh")
        cmd_str = shlex.join(cmd)
        
        logger.info(f"Running solve command: {cmd_str}")
        
        # Execute command
        exit_code, duration = _run_docker_command(cmd)
        
        # Determine success
        success = (exit_code == 0)
        
        # Mark solve finished
        job.mark_solve_finished(success)
        
        return {
            "ok": success,
            "exit_code": exit_code,
            "duration_sec": duration,
            "image": OPTIMIZER_IMAGE,
            "cmd": cmd_str,
            "logs": {
                "output": str(job.output_log),
                "error": str(job.error_log)
            },
            "metrics": {
                "cpu": str(job.cpu_csv),
                "memory": str(job.mem_csv)
            }
        }
        
    except Exception as e:
        # Mark solve as failed
        job.mark_solve_finished(False)
        logger.error(f"Solve failed with exception: {e}")
        raise

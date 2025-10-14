import logging
import re
import shlex
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Tuple

from aura.config import get_config

if TYPE_CHECKING:
    from aura.core.job import Job

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


def _build_docker_command(job: "Job", script_name: str) -> Tuple[list[str], str]:
    """
    Build docker run command for the given job and script.
    
    Returns:
        Tuple of (command_list, container_name)
    """
    config = get_config()
    
    # Create unique container name for tracking
    phase = script_name.replace("run_", "").replace(".sh", "")
    container_name = f"aura-{job.id[:8]}-{phase}"
    
    cmd = [
        "docker", "run", "--rm",
        "--name", container_name,
        "-v", f"{job.family_dir}:{config.families_mount}",
        "-v", f"{job.family_dir}:{config.proto_mount}", 
        "-v", f"{job.output_dir}:{config.logs_mount}",
        config.optimizer_image,
        "/bin/sh", "-c",
        f"/optimizer/{script_name} {config.families_mount} {config.logs_mount} {config.proto_mount}/model.pb"
    ]
    
    return cmd, container_name


def _run_docker_command_with_tracking(cmd: list[str], container_name: str, job: "Job", phase: str) -> tuple[int, float, str, Dict]:
    """
    Run docker command with continuous metrics collection.
    
    Starts metrics streaming, waits for container completion, then stops
    collection and returns execution metadata along with collected metrics.
    
    Returns:
        Tuple of (exit_code, duration_in_seconds, container_id, metrics_stats)
    """
    start_time = time.monotonic()
    container_id = ""
    
    try:
        # Start the docker container
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give container a moment to start, then get its ID
        time.sleep(0.1)  # Brief pause to ensure container is registered
        
        try:
            # Get container ID using container name
            get_id_cmd = ["docker", "ps", "-aqf", f"name=^{container_name}$"]
            id_result = subprocess.run(get_id_cmd, capture_output=True, text=True, check=False)
            if id_result.returncode == 0 and id_result.stdout.strip():
                container_id = id_result.stdout.strip()
                # Start continuous metrics collection
                job.start_metrics_collection(container_id, phase)
                logger.debug(f"Started metrics collection for job {job.id} container {container_id}")
        except Exception as e:
            logger.warning(f"Could not capture container ID for job {job.id}: {e}")
        
        # Wait for container to complete
        stdout, stderr = process.communicate()
        duration = time.monotonic() - start_time
        
        # Stop metrics collection and get final stats
        metrics_stats = job.stop_metrics_collection()
        
        if stderr and process.returncode != 0:
            logger.error(f"Docker command failed: {stderr}")
        
        return process.returncode, duration, container_id, metrics_stats
        
    except Exception as e:
        duration = time.monotonic() - start_time
        logger.error(f"Failed to run docker command: {e}")
        raise


def run_build(job: "Job") -> Dict:
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
        cmd, container_name = _build_docker_command(job, "run_build.sh")
        cmd_str = shlex.join(cmd)
        
        logger.info(f"Running build command: {cmd_str}")
        
        # Execute command with container tracking and metrics collection
        exit_code, duration, container_id, metrics_stats = _run_docker_command_with_tracking(cmd, container_name, job, "build")
        
        # Determine success
        success = (exit_code == 0)
        
        # Mark build finished
        job.mark_build_finished(success)
        
        return {
            "ok": success,
            "exit_code": exit_code,
            "duration_sec": duration,
            "image": get_config().optimizer_image,
            "cmd": cmd_str,
            "container_id": container_id,
            "container_name": container_name,
            "logs": {
                "output": str(job.output_log),
                "error": str(job.error_log)
            },
            "metrics": {
                "cpu": str(job.cpu_csv),
                "memory": str(job.mem_csv)
            },
            "streaming_metrics": metrics_stats
        }
        
    except Exception as e:
        # Mark build as failed
        job.mark_build_finished(False)
        logger.error(f"Build failed with exception: {e}")
        raise


def run_solve(job: "Job") -> Dict:
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
        cmd, container_name = _build_docker_command(job, "run_solve.sh")
        cmd_str = shlex.join(cmd)
        
        logger.info(f"Running solve command: {cmd_str}")
        
        # Execute command with container tracking and metrics collection
        exit_code, duration, container_id, metrics_stats = _run_docker_command_with_tracking(cmd, container_name, job, "solve")
        
        # Determine success
        success = (exit_code == 0)
        
        # Mark solve finished
        job.mark_solve_finished(success)
        
        return {
            "ok": success,
            "exit_code": exit_code,
            "duration_sec": duration,
            "image": get_config().optimizer_image,
            "cmd": cmd_str,
            "container_id": container_id,
            "container_name": container_name,
            "logs": {
                "output": str(job.output_log),
                "error": str(job.error_log)
            },
            "metrics": {
                "cpu": str(job.cpu_csv),
                "memory": str(job.mem_csv)
            },
            "streaming_metrics": metrics_stats
        }
        
    except Exception as e:
        # Mark solve as failed
        job.mark_solve_finished(False)
        logger.error(f"Solve failed with exception: {e}")
        raise

"""
Event storage system for job orchestration.

This module provides a simple JSONL-based event storage system that records
job lifecycle events for monitoring and analysis purposes.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from .job import Job

# Base directory for orchestrator run logs
RUNS_DIR = Path("./orchestrator_runs")


def record_event(
    job: "Job", 
    phase: str, 
    kind: str, 
    meta: Optional[Dict] = None
) -> None:
    """
    Record a job event to JSONL storage.
    
    Events are stored in ./orchestrator_runs/<job_id>.jsonl with one JSON
    object per line containing event metadata and timestamps.
    
    Args:
        job: Job instance the event relates to
        phase: Phase name ('build', 'solve', etc.)
        kind: Event kind ('started', 'finished', etc.)
        meta: Optional additional metadata to include in the event
    """
    # Ensure runs directory exists
    RUNS_DIR.mkdir(exist_ok=True)
    
    # Prepare event data
    event_data = {
        "ts": datetime.now().isoformat(),
        "job_id": job.id,
        "family": job.family_dir.name,
        "phase": phase,
        "kind": kind,
        "state_at_write": job.state.value if job.state else None,
    }
    
    # Safely merge metadata if provided
    if meta:
        # Create a copy to avoid modifying the original
        merged_meta = dict(meta)
        event_data["meta"] = merged_meta
    else:
        event_data["meta"] = {}
    
    # Determine log file path
    log_file = RUNS_DIR / f"{job.id}.jsonl"
    
    # Append event as JSON line
    with open(log_file, 'a', encoding='utf-8') as f:
        json.dump(event_data, f, ensure_ascii=False)
        f.write('\n')


def get_job_events(job_id: str) -> list[Dict]:
    """
    Read all events for a specific job.
    
    Args:
        job_id: ID of the job to read events for
        
    Returns:
        List of event dictionaries in chronological order
    """
    log_file = RUNS_DIR / f"{job_id}.jsonl"
    
    if not log_file.exists():
        return []
    
    events = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
    except Exception:
        # Return empty list if file cannot be read
        return []
    
    return events


def list_job_ids() -> list[str]:
    """
    List all job IDs that have recorded events.
    
    Returns:
        List of job IDs (without .jsonl extension)
    """
    if not RUNS_DIR.exists():
        return []
    
    job_ids = []
    for log_file in RUNS_DIR.glob("*.jsonl"):
        job_ids.append(log_file.stem)
    
    return sorted(job_ids)


def cleanup_old_runs(keep_latest: int = 100) -> int:
    """
    Clean up old run logs, keeping only the most recent ones.
    
    Args:
        keep_latest: Number of most recent job logs to keep
        
    Returns:
        Number of log files removed
    """
    if not RUNS_DIR.exists():
        return 0
    
    log_files = list(RUNS_DIR.glob("*.jsonl"))
    
    if len(log_files) <= keep_latest:
        return 0
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Remove oldest files
    files_to_remove = log_files[keep_latest:]
    removed_count = 0
    
    for log_file in files_to_remove:
        try:
            log_file.unlink()
            removed_count += 1
        except Exception:
            # Skip files that can't be removed
            continue
    
    return removed_count

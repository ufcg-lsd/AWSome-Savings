"""
Monitoring utilities for extracting performance metrics from job logs.

This module provides functions to extract CPU and memory usage statistics
from CSV files generated during job execution.
"""

import csv
import json
import logging
import statistics
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from aura.core.job import Job

logger = logging.getLogger(__name__)


def extract_metrics(job: "Job") -> Dict[str, Dict[str, Optional[float]]]:
    """
    Extract CPU and memory usage statistics from job.
    
    Attempts to get precise metrics from Docker stats if container_id is available,
    otherwise falls back to reading CSV files generated during job execution.
    
    Args:
        job: Job instance containing container ID or paths to metric CSV files
        
    Returns:
        Dictionary with structure:
        {
          "cpu": {"max": float | None, "mean": float | None},
          "memory": {"max": float | None, "mean": float | None}
        }
        
        Returns None for max/mean if no data available.
    """
    # Try to get metrics from container stats first (more accurate)
    if job.current_container_id:
        logger.debug(f"Extracting container metrics for job {job.id} container {job.current_container_id}")
        container_stats = _extract_container_stats(job.current_container_id)
        if container_stats["cpu"]["max"] is not None or container_stats["memory"]["max"] is not None:
            return container_stats
        logger.debug(f"Container stats unavailable for {job.current_container_id}, falling back to CSV")
    
    # Fallback to CSV parsing (legacy method)
    logger.debug(f"Extracting CSV metrics for job {job.id}")
    cpu_stats = _extract_csv_stats(job.cpu_csv)
    memory_stats = _extract_csv_stats(job.mem_csv)
    
    return {
        "cpu": cpu_stats,
        "memory": memory_stats
    }


def _extract_container_stats(container_id: str) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Extract CPU and memory usage statistics from Docker container stats.
    
    Uses 'docker stats' command to get real-time resource usage metrics
    for the specified container.
    
    Args:
        container_id: Docker container ID
        
    Returns:
        Dictionary with structure matching extract_metrics:
        {
          "cpu": {"max": float | None, "mean": float | None},
          "memory": {"max": float | None, "mean": float | None}
        }
    """
    default_stats = {
        "cpu": {"max": None, "mean": None},
        "memory": {"max": None, "mean": None}
    }
    
    try:
        # Get single snapshot of container stats using JSON format
        cmd = [
            "docker", "stats", "--no-stream", "--format", "{{json .}}", 
            container_id
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            logger.warning(f"Failed to get docker stats for container {container_id}: {result.stderr}")
            return default_stats
        
        output = result.stdout.strip()
        if not output:
            logger.debug(f"No stats output for container {container_id}")
            return default_stats
        
        # Parse JSON output
        try:
            stats_data = json.loads(output)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse docker stats JSON for container {container_id}: {e}")
            return default_stats
        
        # Extract CPU percentage
        cpu_perc = None
        cpu_perc_str = stats_data.get("CPUPerc", "").replace('%', '')
        if cpu_perc_str:
            try:
                cpu_perc = float(cpu_perc_str)
            except ValueError:
                logger.debug(f"Could not parse CPU percentage: {cpu_perc_str}")
        
        # Extract memory usage (format: "59.04MiB / 31.33GiB")
        mem_usage_mb = None
        mem_usage_str = stats_data.get("MemUsage", "")
        if mem_usage_str:
            try:
                mem_current = mem_usage_str.split(' / ')[0].strip()
                mem_usage_mb = _parse_memory_size(mem_current)
            except (ValueError, IndexError):
                logger.debug(f"Could not parse memory usage: {mem_usage_str}")
        
        # For single snapshot, max and mean are the same
        return {
            "cpu": {
                "max": cpu_perc,
                "mean": cpu_perc
            },
            "memory": {
                "max": mem_usage_mb,
                "mean": mem_usage_mb
            }
        }
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout getting docker stats for container {container_id}")
    except Exception as e:
        logger.error(f"Error getting docker stats for container {container_id}: {e}")
    
    return default_stats


def _parse_memory_size(size_str: str) -> Optional[float]:
    """
    Parse memory size string to MB.
    
    Handles formats like "1.5GiB", "512MiB", "2.1GB", etc.
    
    Args:
        size_str: Memory size string from docker stats
        
    Returns:
        Memory size in MB, or None if parsing fails
    """
    try:
        size_str = size_str.strip()
        
        # Extract number and unit
        import re
        match = re.match(r'^([0-9.]+)\s*([A-Za-z]+)$', size_str)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2).upper()
        
        # Convert to MB
        if unit in ['B', 'BYTES']:
            return value / (1024 * 1024)
        elif unit in ['KB', 'KIB']:
            return value / 1024
        elif unit in ['MB', 'MIB']:
            return value
        elif unit in ['GB', 'GIB']:
            return value * 1024
        elif unit in ['TB', 'TIB']:
            return value * 1024 * 1024
        else:
            logger.debug(f"Unknown memory unit: {unit}")
            return None
            
    except Exception as e:
        logger.debug(f"Error parsing memory size '{size_str}': {e}")
        return None


def extract_historical_metrics(job: "Job", phase: str) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Extract historical metrics for a completed job phase.
    
    This function is designed to extract metrics after a job phase has completed,
    using the stored container ID for that specific phase.
    
    Args:
        job: Job instance
        phase: Phase name ('build' or 'solve')
        
    Returns:
        Dictionary with CPU and memory metrics, or fallback to CSV if container unavailable
    """
    container_id = job.get_container_id_for_phase(phase)
    
    if container_id:
        logger.debug(f"Extracting historical container metrics for job {job.id} phase {phase}")
        # Try to get final stats from the container (may not work if container is removed)
        container_stats = _extract_container_stats(container_id)
        if container_stats["cpu"]["max"] is not None or container_stats["memory"]["max"] is not None:
            return container_stats
    
    # Fallback to CSV parsing
    logger.debug(f"Extracting historical CSV metrics for job {job.id} phase {phase}")
    cpu_stats = _extract_csv_stats(job.cpu_csv)
    memory_stats = _extract_csv_stats(job.mem_csv)
    
    return {
        "cpu": cpu_stats,
        "memory": memory_stats
    }


def _extract_csv_stats(csv_path: Path) -> Dict[str, Optional[float]]:
    """
    Extract max and mean statistics from the first numeric column of a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Dictionary with "max" and "mean" keys, values are float or None
    """
    stats = {"max": None, "mean": None}
    
    if not csv_path.exists():
        return stats
    
    try:
        numeric_values = _read_numeric_column(csv_path)
        
        if numeric_values:
            stats["max"] = max(numeric_values)
            stats["mean"] = statistics.mean(numeric_values)
            
    except Exception:
        # Return None values if any error occurs during processing
        pass
    
    return stats


def _read_numeric_column(csv_path: Path) -> List[float]:
    """
    Read the first numeric column from a CSV file.
    
    Defensively handles unknown headers and tries to find the first column
    that contains numeric data.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of numeric values from the first numeric column found
    """
    numeric_values = []
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        # Try to detect if file has a header
        sample = csvfile.read(1024)
        csvfile.seek(0)
        
        sniffer = csv.Sniffer()
        has_header = sniffer.has_header(sample)
        
        reader = csv.reader(csvfile)
        
        # Skip header if detected
        if has_header:
            try:
                next(reader)
            except StopIteration:
                return numeric_values
        
        # Find the first numeric column by trying each column
        first_row = None
        try:
            first_row = next(reader)
        except StopIteration:
            return numeric_values
        
        # Reset to beginning after header (if any)
        csvfile.seek(0)
        reader = csv.reader(csvfile)
        if has_header:
            next(reader)
        
        # Try each column to find the first numeric one
        if first_row:
            for col_index in range(len(first_row)):
                csvfile.seek(0)
                reader = csv.reader(csvfile)
                if has_header:
                    next(reader)
                
                column_values = []
                try:
                    for row in reader:
                        if col_index < len(row):
                            value_str = row[col_index].strip()
                            if value_str:  # Skip empty values
                                # Try to convert to float
                                try:
                                    value = float(value_str)
                                    column_values.append(value)
                                except ValueError:
                                    # This column is not numeric, try next column
                                    break
                    
                    # If we successfully parsed at least one number from this column
                    if column_values:
                        return column_values
                        
                except Exception:
                    # Try next column if this one fails
                    continue
    
    return numeric_values


def _is_numeric_string(value: str) -> bool:
    """
    Check if a string represents a numeric value.
    
    Args:
        value: String to check
        
    Returns:
        True if the string can be converted to float, False otherwise
    """
    try:
        float(value.strip())
        return True
    except (ValueError, AttributeError):
        return False

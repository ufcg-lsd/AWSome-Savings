"""
Monitoring utilities for extracting performance metrics from job logs.

This module provides functions to extract CPU and memory usage statistics
from CSV files generated during job execution.
"""

import csv
import json
import logging
import re
import statistics
import subprocess
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from aura.core.job import Job

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Continuous metrics collector that streams docker stats in real-time during job execution.
    
    This collector uses 'docker stats' streaming mode to capture metrics as they're generated,
    providing much lower latency (~100ms vs ~1.5s) and reduced overhead compared to polling.
    """
    
    def __init__(self, container_id: str, csv_file: Optional[Path] = None):
        """
        Initialize metrics collector for a specific container.
        
        Args:
            container_id: Docker container ID to monitor
            csv_file: Optional path to save granular metrics CSV
        """
        self.container_id = container_id
        self.csv_file = csv_file
        self._stop_event = threading.Event()
        self._thread = None
        self._process = None
        self._lock = threading.Lock()
        
        # Store collected metrics
        self._cpu_samples: List[float] = []
        self._memory_samples: List[float] = []  # in MB
        self._timestamps: List[float] = []
        
        # CSV writing
        self._csv_writer = None
        self._csv_handle = None
        self._last_csv_write_time = 0.0  # Timestamp of last CSV write for throttling
        
        self._is_running = False
        
    def start(self) -> None:
        """Start continuous metrics streaming in background thread."""
        if self._is_running:
            logger.warning(f"MetricsCollector for {self.container_id} is already running")
            return
        
        # Initialize CSV file if specified
        if self.csv_file:
            self._init_csv_file()
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._thread.start()
        self._is_running = True
        csv_info = f" (CSV: {self.csv_file})" if self.csv_file else ""
        logger.info(f"Started metrics streaming for container {self.container_id}{csv_info}")
        
    def stop(self) -> None:
        """Stop metrics streaming and cleanup processes."""
        if not self._is_running:
            return
            
        self._stop_event.set()
        
        # Terminate docker stats process
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                self._process.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing docker stats process for {self.container_id}")
                self._process.kill()
            except Exception as e:
                logger.error(f"Error stopping docker stats process: {e}")
        
        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        # Close CSV file
        self._close_csv_file()
            
        self._is_running = False
        samples_count = len(self._cpu_samples)
        csv_info = f" (saved to {self.csv_file})" if self.csv_file else ""
        logger.info(f"Stopped metrics streaming for container {self.container_id}, collected {samples_count} samples{csv_info}")
        
    def get_stats(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Get computed statistics from collected metrics.
        
        Returns:
            Dictionary with max/mean/min/count stats for CPU and memory
        """
        with self._lock:
            cpu_stats = self._compute_stats(self._cpu_samples, "CPU %")
            memory_stats = self._compute_stats(self._memory_samples, "Memory MB")
            
            return {
                "cpu": cpu_stats,
                "memory": memory_stats,
                "collection": {
                    "samples_count": len(self._cpu_samples),
                    "duration_seconds": (self._timestamps[-1] - self._timestamps[0]) if len(self._timestamps) >= 2 else None,
                    "method": "streaming"
                }
            }
    
    def _init_csv_file(self) -> None:
        """Initialize CSV file for granular metrics storage."""
        try:
            # Ensure directory exists
            self.csv_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Open CSV file and write header
            self._csv_handle = open(self.csv_file, 'w', newline='', encoding='utf-8')
            self._csv_writer = csv.writer(self._csv_handle)
            
            # Write CSV header (1-second granularity)
            self._csv_writer.writerow([
                'timestamp',           # ISO format timestamp  
                'container_id',        # Container ID
                'cpu_percent',         # CPU percentage
                'memory_mb',           # Memory usage in MB
                'elapsed_seconds'      # Seconds since collection started (1s intervals)
            ])
            self._csv_handle.flush()
            
            logger.debug(f"Initialized CSV metrics file: {self.csv_file}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CSV file {self.csv_file}: {e}")
            self._csv_writer = None
            self._csv_handle = None
    
    def _write_csv_sample(self, cpu_perc: float, memory_mb: float, timestamp: float) -> None:
        """
        Write a single metrics sample to CSV file with 1-second granularity throttling.
        
        Only writes to CSV if at least 1 second has passed since the last write,
        preventing overly large files for long-running jobs.
        """
        if not self._csv_writer or not self._csv_handle:
            return
        
        # Throttle CSV writes to maximum 1 per second
        if self._last_csv_write_time > 0.0 and (timestamp - self._last_csv_write_time) < 1.0:
            return  # Skip this sample - not enough time has passed
            
        try:
            from datetime import datetime
            
            # Convert monotonic timestamp to datetime
            current_time = datetime.now()
            
            # Calculate elapsed seconds from first timestamp
            if self._timestamps:
                elapsed = timestamp - self._timestamps[0]
            else:
                elapsed = 0.0
            
            # Write CSV row
            self._csv_writer.writerow([
                current_time.isoformat(),      # Human-readable timestamp
                self.container_id,             # Container ID
                round(cpu_perc, 2),            # CPU percentage
                round(memory_mb, 2),           # Memory in MB
                round(elapsed, 2)              # Elapsed seconds
            ])
            self._csv_handle.flush()  # Ensure data is written immediately
            
            # Update last write timestamp
            self._last_csv_write_time = timestamp
            
            logger.debug(f"CSV sample written for {self.container_id}: CPU={cpu_perc}%, Memory={memory_mb}MB")
            
        except Exception as e:
            logger.error(f"Failed to write CSV sample: {e}")
    
    def _close_csv_file(self) -> None:
        """Close CSV file and cleanup resources."""
        try:
            if self._csv_handle:
                self._csv_handle.close()
                self._csv_handle = None
                self._csv_writer = None
                logger.debug(f"Closed CSV metrics file: {self.csv_file}")
        except Exception as e:
            logger.error(f"Error closing CSV file: {e}")
    
    def _stream_loop(self) -> None:
        """Main streaming loop that runs in background thread."""
        logger.debug(f"Starting metrics streaming loop for {self.container_id}")
        
        try:
            # Start docker stats in streaming mode
            cmd = [
                "docker", "stats", "--format", "{{json .}}", 
                self.container_id
            ]
            
            self._process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            logger.debug(f"Started docker stats process for {self.container_id}")
            
            # Stream metrics line by line
            while not self._stop_event.is_set():
                try:
                    # Read line with timeout to allow checking stop event
                    line = self._read_line_with_timeout(timeout=1.0)
                    
                    if line is None:
                        continue  # Timeout, check stop event
                    
                    if not line.strip():
                        continue  # Empty line, skip
                        
                    # Parse metrics from JSON line
                    cpu_perc, memory_mb = self._parse_stats_line(line)
                    
                    # Store metrics with thread safety
                    with self._lock:
                        timestamp = time.monotonic()
                        if cpu_perc is not None:
                            self._cpu_samples.append(cpu_perc)
                        if memory_mb is not None:
                            self._memory_samples.append(memory_mb)
                        self._timestamps.append(timestamp)
                    
                    # Write to CSV if both metrics are valid and CSV is enabled
                    if cpu_perc is not None and memory_mb is not None and self.csv_file:
                        self._write_csv_sample(cpu_perc, memory_mb, timestamp)
                    
                    logger.debug(f"Streamed sample for {self.container_id}: CPU={cpu_perc}%, Memory={memory_mb}MB")
                    
                except Exception as e:
                    logger.error(f"Error processing metrics stream for {self.container_id}: {e}")
                    # Don't break - container might recover
                    time.sleep(0.5)  # Brief pause before retry
            
        except Exception as e:
            logger.error(f"Error starting metrics stream for {self.container_id}: {e}")
        finally:
            logger.debug(f"Metrics streaming loop ended for {self.container_id}")
    
    def _read_line_with_timeout(self, timeout: float) -> Optional[str]:
        """
        Read line from docker stats process with timeout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Line from stdout or None if timeout/error
        """
        if not self._process or self._process.poll() is not None:
            return None  # Process ended
        
        try:
            # Use select/poll for timeout (Unix-like systems)
            import select
            
            ready, _, _ = select.select([self._process.stdout], [], [], timeout)
            if ready:
                line = self._process.stdout.readline()
                return line if line else None
            else:
                return None  # Timeout
                
        except ImportError:
            # Fallback for systems without select (Windows)
            try:
                line = self._process.stdout.readline()
                return line if line else None
            except Exception:
                return None
        except Exception as e:
            logger.debug(f"Error reading from docker stats: {e}")
            return None
    
    def _parse_stats_line(self, line: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse metrics from a single docker stats JSON line.
        
        Args:
            line: JSON line from docker stats (may contain ANSI escape codes)
            
        Returns:
            Tuple of (cpu_percentage, memory_mb) or (None, None) if failed
        """
        try:
            # Clean ANSI escape codes from docker stats output
            clean_line = self._clean_ansi_codes(line.strip())
            
            # Skip empty lines or lines that don't look like JSON
            if not clean_line or not clean_line.startswith('{'):
                return None, None
                
            # Skip lines with placeholder values (docker stats initial output)
            if '"--"' in clean_line or '"CPUPerc":"--"' in clean_line:
                logger.debug(f"Skipping placeholder stats line for {self.container_id}")
                return None, None
            
            stats_data = json.loads(clean_line)
            
            # Extract CPU percentage
            cpu_perc = None
            cpu_perc_str = stats_data.get("CPUPerc", "").replace('%', '')
            if cpu_perc_str and cpu_perc_str != "--":
                try:
                    cpu_perc = float(cpu_perc_str)
                except ValueError:
                    pass
            
            # Extract memory usage
            memory_mb = None
            mem_usage_str = stats_data.get("MemUsage", "")
            if mem_usage_str and mem_usage_str != "-- / --":
                try:
                    mem_current = mem_usage_str.split(' / ')[0].strip()
                    memory_mb = _parse_memory_size(mem_current)
                except (ValueError, IndexError):
                    pass
            
            # Only return valid data (not None values)
            if cpu_perc is not None and memory_mb is not None:
                logger.debug(f"Parsed valid stats for {self.container_id}: CPU={cpu_perc}%, Mem={memory_mb}MB")
                return cpu_perc, memory_mb
            else:
                return None, None
            
        except json.JSONDecodeError as e:
            logger.debug(f"Invalid JSON in docker stats output: {e} | Line: {line[:100]}")
            return None, None
        except Exception as e:
            logger.debug(f"Error parsing stats line: {e}")
            return None, None
    
    def _clean_ansi_codes(self, text: str) -> str:
        """
        Remove ANSI escape codes from text.
        
        Docker stats in streaming mode includes ANSI codes for terminal display:
        - ESC[H (move cursor to home)
        - ESC[K (clear line) 
        - ESC[J (clear screen)
        
        Args:
            text: Raw text from docker stats
            
        Returns:
            Clean text without ANSI codes
        """
        # Remove ANSI escape sequences
        # Pattern matches: ESC[...letter (where letter is any alphabetic character)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        
        # Also remove other common control characters
        clean_text = clean_text.replace('\x1B[H', '')  # Home cursor
        clean_text = clean_text.replace('\x1B[K', '')  # Clear line
        clean_text = clean_text.replace('\x1B[J', '')  # Clear screen
        
        return clean_text.strip()
    
    def _compute_stats(self, samples: List[float], unit: str) -> Dict[str, Optional[float]]:
        """Compute statistics from collected samples."""
        if not samples:
            return {"max": None, "mean": None, "min": None, "count": 0}
        
        try:
            return {
                "max": max(samples),
                "mean": statistics.mean(samples),
                "min": min(samples),
                "count": len(samples)
            }
        except Exception as e:
            logger.error(f"Error computing stats for {unit}: {e}")
            return {"max": None, "mean": None, "min": None, "count": len(samples)}


def extract_metrics(job: "Job") -> Dict[str, Dict[str, Optional[float]]]:
    """
    Extract CPU and memory usage statistics from job.
    
    Priority order:
    1. Collected streaming metrics (if available and recent)
    2. Real-time container stats (if container still running)
    3. CSV files (fallback method)
    
    Args:
        job: Job instance containing metrics data
        
    Returns:
        Dictionary with structure:
        {
          "cpu": {"max": float | None, "mean": float | None},
          "memory": {"max": float | None, "mean": float | None}
        }
    """
    # Priority 1: Use collected streaming metrics if available
    if hasattr(job, '_metrics_collector') and job._metrics_collector:
        logger.debug(f"Extracting current streaming metrics for job {job.id}")
        streaming_stats = job.get_current_metrics()
        if streaming_stats["collection"]["samples_count"] > 0:
            return {
                "cpu": {
                    "max": streaming_stats["cpu"]["max"],
                    "mean": streaming_stats["cpu"]["mean"]
                },
                "memory": {
                    "max": streaming_stats["memory"]["max"], 
                    "mean": streaming_stats["memory"]["mean"]
                }
            }
    
    # Priority 2: Try real-time container stats if container still running
    if job.current_container_id:
        logger.debug(f"Extracting real-time container metrics for job {job.id} container {job.current_container_id}")
        container_stats = _extract_container_stats(job.current_container_id)
        if container_stats["cpu"]["max"] is not None or container_stats["memory"]["max"] is not None:
            return {
                "cpu": {
                    "max": container_stats["cpu"]["max"],
                    "mean": container_stats["cpu"]["mean"]
                },
                "memory": {
                    "max": container_stats["memory"]["max"],
                    "mean": container_stats["memory"]["mean"]
                }
            }
        logger.debug(f"Container stats unavailable for {job.current_container_id}, falling back to CSV")
    
    # Priority 3: Fallback to CSV parsing (legacy method)
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

"""
Monitoring utilities for extracting performance metrics from job logs.

This module provides functions to extract CPU and memory usage statistics
from CSV files generated during job execution.
"""

import csv
import statistics
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union

if TYPE_CHECKING:
    from .job import Job


def extract_metrics(job: "Job") -> Dict[str, Dict[str, Optional[float]]]:
    """
    Extract CPU and memory usage statistics from job CSV files.
    
    Reads job.cpu_csv and job.mem_csv (if they exist) and calculates
    max and mean of the first numeric column found in each file.
    
    Args:
        job: Job instance containing paths to metric CSV files
        
    Returns:
        Dictionary with structure:
        {
          "cpu": {"max": float | None, "mean": float | None},
          "memory": {"max": float | None, "mean": float | None}
        }
        
        Returns None for max/mean if file doesn't exist or no numeric data found.
    """
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

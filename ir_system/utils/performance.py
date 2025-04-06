"""
Performance Tracking Module.

Provides utilities for tracking and reporting performance metrics.
"""

import os
import time
import sys
import gc
import psutil
from typing import Callable, Any, Dict, Optional, Tuple


def get_memory_usage() -> float:
    """Get current memory usage of the process.

    Returns:
        Current memory usage in megabytes (MB)
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convert to MB


def time_execution(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """Measure function execution time.

    Args:
        func: Function to measure
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Function result and execution time (seconds) tuple
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


def print_memory_stats(label: str) -> None:
    """Print memory usage statistics.

    Args:
        label: Label for the memory statistics
    """
    # Force garbage collection
    gc.collect()
    
    # Get memory usage
    memory_mb = get_memory_usage()
    
    print(f"{label} Memory Usage: {memory_mb:.2f} MB")


class PerformanceTracker:
    """Performance tracking class for measuring execution time and memory usage."""
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.timers = {}
        self.start_times = {}
        self.memory_snapshots = {}
        
    def start_timer(self, name: str) -> None:
        """Start a named timer.

        Args:
            name: Timer name
        """
        self.start_times[name] = time.time()
        
    def stop_timer(self, name: str) -> float:
        """Stop a named timer and record the duration.

        Args:
            name: Timer name

        Returns:
            Duration in seconds
        """
        if name not in self.start_times:
            print(f"Warning: Timer '{name}' was never started")
            return 0
            
        duration = time.time() - self.start_times[name]
        self.timers[name] = duration
        return duration
        
    def take_memory_snapshot(self, name: str) -> float:
        """Take a memory usage snapshot.

        Args:
            name: Snapshot name

        Returns:
            Memory usage in MB
        """
        memory_usage = get_memory_usage()
        self.memory_snapshots[name] = memory_usage
        return memory_usage
        
    def get_timer(self, name: str) -> Optional[float]:
        """Get a timer's duration.

        Args:
            name: Timer name

        Returns:
            Duration in seconds or None if timer doesn't exist
        """
        return self.timers.get(name)
        
    def get_memory_snapshot(self, name: str) -> Optional[float]:
        """Get a memory snapshot.

        Args:
            name: Snapshot name

        Returns:
            Memory usage in MB or None if snapshot doesn't exist
        """
        return self.memory_snapshots.get(name)
        
    def print_report(self) -> None:
        """Print a report of all timers and memory snapshots."""
        print("\nPerformance Report:")
        print("-" * 50)
        
        if self.timers:
            print("Execution Times:")
            for name, duration in sorted(self.timers.items()):
                print(f"  {name}: {duration:.4f} seconds")
                
        if self.memory_snapshots:
            print("\nMemory Usage:")
            snapshots = sorted(self.memory_snapshots.items())
            for i, (name, usage) in enumerate(snapshots):
                print(f"  {name}: {usage:.2f} MB")
                
                # Print memory change if not the first snapshot
                if i > 0:
                    prev_name, prev_usage = snapshots[i-1]
                    change = usage - prev_usage
                    change_sign = "+" if change >= 0 else ""
                    print(f"    Change from {prev_name}: {change_sign}{change:.2f} MB")
        
        print("-" * 50) 
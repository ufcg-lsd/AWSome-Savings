"""
Plugin system for heuristic algorithms.

This module defines the protocol interface for heuristic plugins and provides
a dynamic loader to instantiate plugins by name.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
import importlib
import logging

if TYPE_CHECKING:
    from aura.core.job import Job

logger = logging.getLogger(__name__)


@runtime_checkable
class HeuristicPluginProtocol(Protocol):
    """
    Protocol for heuristic plugins that select jobs to run.
    
    All heuristic plugins must implement this interface to be compatible
    with the scheduler system.
    """
    
    def name(self) -> str:
        """Return the name/identifier of this heuristic plugin."""
        ...
    
    def select(
        self,
        candidates: list["Job"],
        running: list["Job"],
        capacity_total: int,
        cap_build: int,
        cap_solve: int,
    ) -> list["Job"]:
        """
        Select jobs to run based on heuristic logic.
        
        Args:
            candidates: List of jobs ready for their next phase
            running: List of jobs currently running
            capacity_total: Total remaining capacity across all phases
            cap_build: Remaining capacity for build phase
            cap_solve: Remaining capacity for solve phase
            
        Returns:
            List of selected jobs to start (subset of candidates)
        """
        ...


def load_plugin(name: str) -> HeuristicPluginProtocol:
    """
    Load a heuristic plugin by name.
    
    Args:
        name: Name of the plugin to load ("fifo", "greedy", etc.)
        
    Returns:
        Instance of the requested heuristic plugin
        
    Raises:
        ValueError: If the plugin name is unknown or unsupported
        ImportError: If the plugin module cannot be imported
        AttributeError: If the plugin class is not found in the module
    """
    # Map of supported plugin names to their module/class
    plugin_map = {
        "fifo": ("fifo", "FifoHeuristic"),
        "greedy": ("greedy", "GreedyHeuristic"),  # When it exists
    }
    
    if name not in plugin_map:
        available_plugins = ", ".join(plugin_map.keys())
        raise ValueError(
            f"Unknown heuristic plugin '{name}'. "
            f"Available plugins: {available_plugins}"
        )
    
    module_name, class_name = plugin_map[name]
    
    try:
        # Dynamic import: from .{module_name} import {class_name}
        module = importlib.import_module(f".{module_name}", package=__name__)
        plugin_class = getattr(module, class_name)
        
        # Instantiate the plugin
        plugin_instance = plugin_class()
        
        # Verify it implements the protocol
        if not isinstance(plugin_instance, HeuristicPluginProtocol):
            raise TypeError(
                f"Plugin {class_name} does not implement HeuristicPluginProtocol"
            )
        
        logger.info(f"Successfully loaded heuristic plugin: {name}")
        return plugin_instance
        
    except ImportError as e:
        if "greedy" in str(e) and name == "greedy":
            raise ImportError(
                f"Greedy heuristic plugin is not implemented yet. "
                f"Available plugins: fifo"
            ) from e
        raise ImportError(f"Failed to import plugin module '{module_name}': {e}") from e
        
    except AttributeError as e:
        raise AttributeError(
            f"Plugin class '{class_name}' not found in module '{module_name}': {e}"
        ) from e

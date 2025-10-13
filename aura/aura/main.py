"""
Aura - AWS Optimizer Orchestrator

Main entry point for the Aura orchestrator that manages job scheduling
and execution for AWS optimization workloads.
"""

import argparse
import logging
import sys
from pathlib import Path

from aura.config import get_config, reload_config
from aura import plugins
from aura.core.scheduler import Scheduler


def setup_logging(config_level: str = "INFO", config_format: str = None) -> None:
    """Configure logging using configuration settings."""
    level = getattr(logging, config_level.upper(), logging.INFO)
    format_str = config_format or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    # Load config to get defaults
    try:
        config = get_config()
        default_max_build = config.default_max_build
        default_max_solve = config.default_max_solve
        default_poll_interval = config.default_poll_interval
    except Exception:
        # Fallback defaults if config can't be loaded
        default_max_build = 1
        default_max_solve = 1
        default_poll_interval = 0.2
    
    parser = argparse.ArgumentParser(
        description="Aura - AWS Optimizer Orchestrator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--demand-root',
        type=Path,
        required=True,
        help='Root directory containing family demand directories'
    )
    
    parser.add_argument(
        '--plugin',
        type=str,
        default='fifo',
        help='Heuristic plugin to use for job scheduling'
    )
    
    parser.add_argument(
        '--max-build',
        type=int,
        default=default_max_build,
        help='Maximum number of concurrent build jobs'
    )
    
    parser.add_argument(
        '--max-solve',
        type=int,
        default=default_max_solve,
        help='Maximum number of concurrent solve jobs'
    )
    
    parser.add_argument(
        '--poll-interval',
        type=float,
        default=default_poll_interval,
        help='Scheduler polling interval in seconds'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration YAML file (default: configs/config.yaml)'
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the Aura orchestrator."""
    # Parse command line arguments first
    args = parse_args()
    
    # Load configuration (with optional custom config path)
    try:
        if args.config:
            config = reload_config(args.config)
        else:
            config = get_config()
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Setup logging using config
    setup_logging(config.log_level, config.log_format)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AURA orchestrator")
    logger.info(f"Demand root: {args.demand_root}")
    logger.info(f"Plugin: {args.plugin}")
    logger.info(f"Max build jobs: {args.max_build}")
    logger.info(f"Max solve jobs: {args.max_solve}")
    logger.info(f"Poll interval: {args.poll_interval}s")
    logger.info(f"Optimizer image: {config.optimizer_image}")
    logger.info(f"Runs directory: {config.runs_dir}")
    
    try:
        # Validate demand root directory
        if not args.demand_root.exists():
            logger.error(f"Demand root directory does not exist: {args.demand_root}")
            sys.exit(1)
        
        if not args.demand_root.is_dir():
            logger.error(f"Demand root is not a directory: {args.demand_root}")
            sys.exit(1)
        
        # Load heuristic plugin
        logger.info(f"Loading heuristic plugin: {args.plugin}")
        plugin = plugins.load_plugin(args.plugin)
        logger.info(f"Loaded plugin: {plugin.name()}")
        
        # Create and configure scheduler
        scheduler = Scheduler(
            demand_root=args.demand_root,
            plugin=plugin,
            max_build=args.max_build,
            max_solve=args.max_solve,
            poll_interval=args.poll_interval
        )
        
        # Discover jobs
        logger.info("Discovering jobs...")
        jobs = scheduler.discover_jobs()
        logger.info(f"Discovered {len(jobs)} jobs")
        
        if not jobs:
            logger.warning("No jobs found. Exiting.")
            return
        
        # Run scheduler
        logger.info("Starting scheduler...")
        scheduler.run()
        
        logger.info("Scheduler completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

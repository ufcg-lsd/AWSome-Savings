"""
Aura - AWS Optimizer Orchestrator

Main entry point for the Aura orchestrator that manages job scheduling
and execution for AWS optimization workloads.
"""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import plugins
from .core.scheduler import Scheduler


def setup_logging() -> None:
    """Configure logging with INFO level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
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
        default=1,
        help='Maximum number of concurrent build jobs'
    )
    
    parser.add_argument(
        '--max-solve',
        type=int,
        default=1,
        help='Maximum number of concurrent solve jobs'
    )
    
    parser.add_argument(
        '--poll-interval',
        type=float,
        default=0.2,
        help='Scheduler polling interval in seconds'
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the Aura orchestrator."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    args = parse_args()
    
    logger.info("Starting Aura orchestrator")
    logger.info(f"Demand root: {args.demand_root}")
    logger.info(f"Plugin: {args.plugin}")
    logger.info(f"Max build jobs: {args.max_build}")
    logger.info(f"Max solve jobs: {args.max_solve}")
    logger.info(f"Poll interval: {args.poll_interval}s")
    
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

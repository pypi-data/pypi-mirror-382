#!/usr/bin/env python3
"""
XWQuery Interactive Console Runner

Entry point script for running the interactive console.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.xwnode_console.console import main


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="XWQuery Interactive Console - Test and demo tool for XWQuery operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run with default settings
  python run.py --seed 42          # Run with specific random seed
  python run.py --verbose          # Run with verbose output
  python run.py --file queries.xwq # Execute queries from file (future)

Commands in console:
  .help              - Show help
  .collections       - List collections
  .show <name>       - Show collection sample
  .examples [type]   - Show example queries
  .exit              - Exit console
        """
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for data generation (default: 42)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Execute queries from file (not yet implemented)'
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    
    if args.file:
        print("File execution not yet implemented")
        print("Run without --file for interactive mode")
        sys.exit(1)
    
    try:
        main(seed=args.seed, verbose=args.verbose)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


#!/usr/bin/env python3
"""
XWQuery Interactive Console

Main console implementation for interactive XWQuery testing.
"""

import sys
import os
import time
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Lazy imports - only load XWNode components when needed
# This follows DEV_GUIDELINES.md: "Lazy Loading pattern - Load data only when needed"
# Avoids loading xwsystem dependencies (like lxml) until actually required

from . import data, utils, query_examples


class XWQueryConsole:
    """Interactive XWQuery Console."""
    
    def __init__(self, seed: int = 42, verbose: bool = False):
        """
        Initialize console.
        
        Args:
            seed: Random seed for data generation
            verbose: Enable verbose output
        """
        self.seed = seed
        self.verbose = verbose
        self.node = None
        self.engine = None
        self.parser = None
        self.history = []
        self.collections = {}
        
        self._setup()
    
    def _setup(self):
        """Set up console with data and components."""
        if self.verbose:
            print("Loading data...")
        
        # Load test data
        self.collections = data.load_all_collections(self.seed)
        
        # Lazy initialization - only load XWNode when actually needed
        # Currently using mock execution, so XWNode is not required yet
        # This follows DEV_GUIDELINES.md lazy loading principle
        self.node = None
        self.engine = None
        self.parser = None
        
        if self.verbose:
            stats = data.get_collection_stats(self.collections)
            print(f"Loaded {sum(stats.values())} total records across {len(stats)} collections")
    
    def _ensure_xwnode_loaded(self):
        """Lazy load XWNode components when needed for real execution."""
        if self.node is None:
            # Import only when needed - use relative imports to work without installation
            import sys
            from pathlib import Path
            
            # Ensure src is in path
            src_path = Path(__file__).parent.parent.parent / 'src'
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            
            from exonware.xwnode import XWNode
            from exonware.xwnode.queries.executors.engine import ExecutionEngine
            from exonware.xwnode.queries.executors.contracts import ExecutionContext
            from exonware.xwnode.queries.strategies.xwquery import XWQueryScriptStrategy
            
            # Create XWNode and load collections
            self.node = XWNode(mode='HASH_MAP')
            for name, collection_data in self.collections.items():
                self.node.set(name, collection_data)
            
            # Initialize execution engine
            self.engine = ExecutionEngine()
            
            # Initialize parser
            self.parser = XWQueryScriptStrategy()
            
            if self.verbose:
                print("[DEBUG] XWNode components loaded")
    
    def run(self):
        """Run the interactive console."""
        utils.print_banner()
        
        stats = data.get_collection_stats(self.collections)
        utils.print_collections_info(stats)
        
        utils.print_help()
        
        print("Ready! Type your XWQuery script or a command (starting with '.'):\n")
        
        while True:
            try:
                query = input("XWQuery> ").strip()
                
                if not query:
                    continue
                
                if query.startswith('.'):
                    self._handle_command(query)
                else:
                    self._execute_query(query)
                
                # Add to history
                self.history.append(query)
            
            except (KeyboardInterrupt, EOFError):
                print("\n\nExiting XWQuery Console. Goodbye!")
                break
            except Exception as e:
                print(utils.format_error(e))
                if self.verbose:
                    import traceback
                    traceback.print_exc()
    
    def _handle_command(self, command: str):
        """Handle special console commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        
        if cmd == '.help':
            utils.print_help()
        
        elif cmd == '.collections':
            stats = data.get_collection_stats(self.collections)
            utils.print_collections_info(stats)
        
        elif cmd == '.show':
            if not arg:
                print("Usage: .show <collection_name>")
                return
            
            if arg in self.collections:
                utils.print_collection_sample(arg, self.collections[arg], sample_size=10)
            else:
                print(f"Collection '{arg}' not found")
                print(f"Available: {', '.join(self.collections.keys())}")
        
        elif cmd == '.examples':
            if arg:
                query_examples.print_examples(arg)
            else:
                utils.print_examples_list()
        
        elif cmd == '.clear':
            utils.clear_screen()
            utils.print_banner()
        
        elif cmd == '.exit' or cmd == '.quit':
            print("\nExiting XWQuery Console. Goodbye!")
            sys.exit(0)
        
        elif cmd == '.history':
            print("\nQuery History:")
            for i, h in enumerate(self.history[-20:], 1):
                print(f"{i}. {h}")
        
        elif cmd == '.random':
            desc, query = query_examples.get_random_example()
            print(f"\nRandom Example: {desc}")
            print(f"{query}\n")
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type .help for available commands")
    
    def _execute_query(self, query: str):
        """
        Parse and execute a query using the real XWQuery execution engine.
        
        Args:
            query: XWQuery script to execute
        """
        try:
            start_time = time.time()
            
            # Lazy load XWNode components for real execution
            self._ensure_xwnode_loaded()
            
            if self.verbose:
                print(f"[DEBUG] Executing query with real engine: {query}")
            
            # Use REAL ExecutionEngine!
            result = self.engine.execute(query, self.node)
            
            execution_time = time.time() - start_time
            
            # Display results
            result_data = result.data if hasattr(result, 'data') else result
            print("\n" + utils.format_results(result_data))
            print("\n" + utils.format_execution_time(execution_time))
            print()
        
        except Exception as e:
            print(utils.format_error(e))
            if self.verbose:
                import traceback
                traceback.print_exc()
    


def main(seed: int = 42, verbose: bool = False):
    """
    Main entry point for console.
    
    Args:
        seed: Random seed for data generation
        verbose: Enable verbose output
    """
    console = XWQueryConsole(seed=seed, verbose=verbose)
    console.run()


if __name__ == '__main__':
    main()


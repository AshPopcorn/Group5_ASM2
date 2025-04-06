"""
Main program entry module.

Provides the main entry point for the program, handling command line calls and executing appropriate operations.
"""

import sys
import traceback
from typing import List, Optional

from ir_system.cli.commands import parse_args, index_command, search_command


def main(args: Optional[List[str]] = None) -> int:
    """Main function, processes command line arguments and calls the appropriate mode.

    Args:
        args: Command line argument list, if None uses sys.argv[1:]

    Returns:
        Exit code (0 means success)
    """
    try:
        parsed_args = parse_args(args)
        
        if parsed_args.command == 'index':
            return index_command(parsed_args)
        elif parsed_args.command == 'search':
            return search_command(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
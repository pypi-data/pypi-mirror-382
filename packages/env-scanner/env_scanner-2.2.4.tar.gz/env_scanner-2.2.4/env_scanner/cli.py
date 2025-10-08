"""
Command-line interface for env-scanner.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from .scanner import EnvScanner
from .generator import EnvExampleGenerator
from . import __version__


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def scan_command(args: argparse.Namespace) -> int:
    """
    Execute the scan command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    setup_logging(args.verbose)
    
    # Create scanner
    scanner = EnvScanner(
        project_path=args.path,
        exclude_dirs=args.exclude.split(',') if args.exclude else None
    )
    
    # Perform scan
    print(f"Scanning project at: {scanner.project_path}")
    env_vars = scanner.scan_directory(use_ast=not args.regex_only)
    
    if not env_vars:
        print("\nNo environment variables found.")
        return 0
    
    # Print summary
    scanner.print_summary()
    
    # Generate .env-example if requested
    if not args.no_generate:
        output_path = args.output or (scanner.project_path / '.env-example')
        
        generator = EnvExampleGenerator.from_scanner(
            scanner,
            output_path=output_path,
            add_comments=not args.no_comments,
            group_by_prefix=not args.no_grouping,
            include_header=not args.no_header
        )
        
        if args.preview:
            generator.preview()
            response = input("Save this file? (y/N): ").strip().lower()
            if response != 'y':
                print("Cancelled.")
                return 0
        
        saved_path = generator.save()
        print(f"\n✓ Generated .env-example file at: {saved_path}")
    
    return 0


def generate_command(args: argparse.Namespace) -> int:
    """
    Execute the generate command (scan + generate in one step).
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    # Use scan command with generation enabled
    args.no_generate = False
    return scan_command(args)


def list_command(args: argparse.Namespace) -> int:
    """
    Execute the list command (just list variables, don't generate file).
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    setup_logging(args.verbose)
    
    scanner = EnvScanner(
        project_path=args.path,
        exclude_dirs=args.exclude.split(',') if args.exclude else None
    )
    
    print(f"Scanning project at: {scanner.project_path}")
    env_vars = scanner.scan_directory(use_ast=not args.regex_only)
    
    if not env_vars:
        print("\nNo environment variables found.")
        return 0
    
    print(f"\nFound {len(env_vars)} environment variables:")
    for var in sorted(env_vars):
        print(f"  {var}")
    
    if args.show_locations:
        print("\nVariable locations:")
        for var in sorted(env_vars):
            if var in scanner.var_locations:
                print(f"\n  {var}:")
                for loc in scanner.var_locations[var]:
                    print(f"    {loc['file']}:{loc['line']}")
    
    return 0


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='env-scanner',
        description='Scan Python projects for environment variables and generate .env-example files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory and generate .env-example
  env-scanner
  
  # Scan specific directory
  env-scanner scan /path/to/project
  
  # Just list variables without generating file
  env-scanner list
  
  # Generate with custom output path
  env-scanner scan --output .env.template
  
  # Preview before saving
  env-scanner scan --preview
  
  # Exclude specific directories
  env-scanner scan --exclude venv,build,dist
        """
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'env-scanner {__version__}'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command (default)
    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan project and generate .env-example file'
    )
    scan_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the Python project (default: current directory)'
    )
    scan_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output path for .env-example file (default: <project>/.env-example)'
    )
    scan_parser.add_argument(
        '-e', '--exclude',
        type=str,
        help='Comma-separated list of directories to exclude (e.g., venv,build,dist)'
    )
    scan_parser.add_argument(
        '--no-generate',
        action='store_true',
        help='Only scan, do not generate .env-example file'
    )
    scan_parser.add_argument(
        '--no-comments',
        action='store_true',
        help='Do not add descriptive comments to variables'
    )
    scan_parser.add_argument(
        '--no-grouping',
        action='store_true',
        help='Do not group variables by prefix'
    )
    scan_parser.add_argument(
        '--no-header',
        action='store_true',
        help='Do not add header to .env-example file'
    )
    scan_parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview the generated file before saving'
    )
    scan_parser.add_argument(
        '--regex-only',
        action='store_true',
        help='Use only regex patterns (skip AST parsing)'
    )
    scan_parser.set_defaults(func=scan_command)
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List environment variables found in project'
    )
    list_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the Python project (default: current directory)'
    )
    list_parser.add_argument(
        '-e', '--exclude',
        type=str,
        help='Comma-separated list of directories to exclude'
    )
    list_parser.add_argument(
        '-l', '--show-locations',
        action='store_true',
        help='Show file locations where variables are used'
    )
    list_parser.add_argument(
        '--regex-only',
        action='store_true',
        help='Use only regex patterns (skip AST parsing)'
    )
    list_parser.set_defaults(func=list_command)
    
    # Generate command (alias for scan)
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate .env-example file (same as scan)'
    )
    generate_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the Python project (default: current directory)'
    )
    generate_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output path for .env-example file'
    )
    generate_parser.add_argument(
        '-e', '--exclude',
        type=str,
        help='Comma-separated list of directories to exclude'
    )
    generate_parser.add_argument(
        '--no-comments',
        action='store_true',
        help='Do not add descriptive comments'
    )
    generate_parser.add_argument(
        '--no-grouping',
        action='store_true',
        help='Do not group variables by prefix'
    )
    generate_parser.add_argument(
        '--no-header',
        action='store_true',
        help='Do not add header'
    )
    generate_parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview before saving'
    )
    generate_parser.add_argument(
        '--regex-only',
        action='store_true',
        help='Use only regex patterns'
    )
    generate_parser.set_defaults(func=generate_command)
    
    return parser


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # If no command specified, default to scan
    if not args.command:
        args.command = 'scan'
        args.path = '.'
        args.output = None
        args.exclude = None
        args.no_generate = False
        args.no_comments = False
        args.no_grouping = False
        args.no_header = False
        args.preview = False
        args.regex_only = False
        args.func = scan_command
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 1
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())



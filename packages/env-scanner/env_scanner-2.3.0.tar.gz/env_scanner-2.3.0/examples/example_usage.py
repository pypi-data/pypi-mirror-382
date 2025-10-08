"""
Example usage of env-scanner package.

This file demonstrates how to use the EnvScanner and EnvExampleGenerator classes.
"""

from pathlib import Path
from env_scanner import EnvScanner, EnvExampleGenerator


def example_basic_scan():
    """Basic example: Scan current directory."""
    print("Example 1: Basic Scan")
    print("-" * 50)
    
    scanner = EnvScanner(project_path='.')
    env_vars = scanner.scan_directory()
    
    print(f"Found {len(env_vars)} environment variables:")
    for var in sorted(env_vars):
        print(f"  - {var}")
    print()


def example_scan_with_exclusions():
    """Example: Scan with custom exclusions."""
    print("Example 2: Scan with Exclusions")
    print("-" * 50)
    
    scanner = EnvScanner(
        project_path='.',
        exclude_dirs=['venv', 'build', 'dist', 'tests']
    )
    env_vars = scanner.scan_directory()
    
    print(f"Found {len(env_vars)} environment variables (excluding test directories)")
    print()


def example_detailed_results():
    """Example: Get detailed scan results."""
    print("Example 3: Detailed Results")
    print("-" * 50)
    
    scanner = EnvScanner(project_path='.')
    scanner.scan_directory()
    
    results = scanner.get_results()
    
    print(f"Project: {results['project_path']}")
    print(f"Total variables: {results['count']}")
    print(f"\nVariables with locations:")
    
    for var in sorted(results['variables'])[:5]:  # Show first 5
        print(f"\n  {var}:")
        if var in results['locations']:
            for loc in results['locations'][var][:2]:  # Show first 2 locations
                print(f"    - {loc['file']}:{loc['line']}")
    print()


def example_generate_env_example():
    """Example: Scan and generate .env-example file."""
    print("Example 4: Generate .env-example File")
    print("-" * 50)
    
    # Scan the project
    scanner = EnvScanner(project_path='.')
    scanner.scan_directory()
    
    # Generate .env-example
    generator = EnvExampleGenerator.from_scanner(
        scanner,
        output_path='.env-example',
        add_comments=True,
        group_by_prefix=True,
        include_header=True
    )
    
    # Preview the content
    print("Preview of generated file:")
    generator.preview()
    
    # Save the file
    saved_path = generator.save()
    print(f"Saved to: {saved_path}")
    print()


def example_custom_generation():
    """Example: Custom generation settings."""
    print("Example 5: Custom Generation")
    print("-" * 50)
    
    # Manually specify variables
    env_vars = {
        'DATABASE_URL',
        'DATABASE_NAME',
        'API_KEY',
        'API_SECRET',
        'DEBUG',
        'PORT',
        'SECRET_KEY',
    }
    
    # Create generator with custom settings
    generator = EnvExampleGenerator(
        env_vars=env_vars,
        output_path='.env.custom',
        add_comments=False,
        group_by_prefix=False,
        include_header=False
    )
    
    # Get content without saving
    content = generator.generate_content()
    print("Custom generated content:")
    print(content)
    print()


def example_regex_only_scan():
    """Example: Scan using only regex (faster, less accurate)."""
    print("Example 6: Regex-Only Scan")
    print("-" * 50)
    
    scanner = EnvScanner(project_path='.')
    env_vars = scanner.scan_directory(use_ast=False)
    
    print(f"Found {len(env_vars)} environment variables using regex only")
    print()


def example_custom_patterns():
    """Example: Add custom detection patterns."""
    print("Example 7: Custom Detection Patterns")
    print("-" * 50)
    
    # Add custom pattern for a custom config system
    custom_patterns = [
        r'Config\.get\(["\']([A-Z_][A-Z0-9_]*)["\']',
    ]
    
    scanner = EnvScanner(
        project_path='.',
        include_patterns=custom_patterns
    )
    env_vars = scanner.scan_directory()
    
    print(f"Found {len(env_vars)} variables with custom patterns")
    print()


def example_specific_directory():
    """Example: Scan a specific subdirectory."""
    print("Example 8: Scan Specific Directory")
    print("-" * 50)
    
    # Scan only the 'src' directory if it exists
    src_path = Path('.') / 'src'
    if src_path.exists():
        scanner = EnvScanner(project_path=src_path)
        env_vars = scanner.scan_directory()
        
        print(f"Found {len(env_vars)} variables in src/ directory")
    else:
        print("src/ directory not found")
    print()


def main():
    """Run all examples."""
    print("=" * 50)
    print("ENV-SCANNER USAGE EXAMPLES")
    print("=" * 50)
    print()
    
    try:
        example_basic_scan()
        example_scan_with_exclusions()
        example_detailed_results()
        example_custom_generation()
        example_regex_only_scan()
        example_custom_patterns()
        example_specific_directory()
        
        # This one generates a file, so ask first
        response = input("Generate .env-example file? (y/N): ").strip().lower()
        if response == 'y':
            example_generate_env_example()
        
        print("=" * 50)
        print("Examples completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()



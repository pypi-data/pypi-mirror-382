# Examples

This directory contains example usage of the env-scanner package.

## Running the Examples

First, make sure you have the package installed:

```bash
pip install -e .
```

Then run the example:

```bash
python examples/example_usage.py
```

## Example File

- **example_usage.py** - Comprehensive examples showing all features:
  - Basic scanning
  - Scanning with exclusions
  - Getting detailed results
  - Generating .env-example files
  - Custom generation settings
  - Regex-only scanning
  - Custom detection patterns
  - Scanning specific directories

## Quick Example

```python
from env_scanner import EnvScanner, EnvExampleGenerator

# Scan your project
scanner = EnvScanner(project_path='.')
env_vars = scanner.scan_directory()

print(f"Found {len(env_vars)} environment variables")

# Generate .env-example
generator = EnvExampleGenerator.from_scanner(scanner)
generator.save()
print("Generated .env-example file!")
```


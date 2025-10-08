# Contributing to Env Scanner

Thank you for your interest in contributing to env-scanner! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Python version and OS
- Any relevant code samples or error messages

### Suggesting Features

Feature requests are welcome! Please create an issue with:
- A clear description of the feature
- Use cases and examples
- Any implementation ideas (optional)

### Pull Requests

1. **Fork the repository** and create a new branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, documented code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Run with coverage
   pytest --cov=env_scanner
   
   # Check code style
   flake8 env_scanner tests
   black --check env_scanner tests
   mypy env_scanner
   ```

4. **Commit your changes**
   - Write clear commit messages
   - Reference related issues
   ```bash
   git commit -m "Add feature: describe what you added"
   ```

5. **Push to your fork and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **In your PR description, include:**
   - What changes you made
   - Why you made them
   - Any related issues
   - Screenshots (if applicable)

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/env-scanner.git
   cd env-scanner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**
   ```bash
   pytest
   ```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Add type hints where possible

### Example

```python
def scan_file(self, file_path: Path, use_ast: bool = True) -> Set[str]:
    """
    Scan a single Python file for environment variables.
    
    Args:
        file_path: Path to the Python file
        use_ast: Whether to use AST parsing
        
    Returns:
        Set of environment variable names found
    """
    # Implementation
    pass
```

## Testing

- Write tests for all new functionality
- Maintain or improve code coverage
- Use pytest fixtures for common test setups
- Test edge cases and error conditions

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_scanner.py

# Specific test
pytest tests/test_scanner.py::TestEnvScanner::test_scan_directory

# With coverage
pytest --cov=env_scanner --cov-report=html

# Verbose output
pytest -v
```

## Project Structure

```
env-scanner/
├── env_scanner/      # Main package
│   ├── __init__.py         # Package initialization
│   ├── scanner.py          # EnvScanner class
│   ├── generator.py        # EnvExampleGenerator class
│   └── cli.py              # CLI interface
├── tests/                  # Test files
│   ├── test_scanner.py
│   ├── test_generator.py
│   └── test_cli.py
├── examples/               # Example usage
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── setup.py
├── setup.cfg
└── pyproject.toml
```

## Documentation

- Update README.md if adding new features
- Add docstrings to new functions/classes
- Update CHANGELOG.md with your changes
- Add examples for significant new features

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub Discussions
- Reach out to the maintainers

## Recognition

Contributors will be acknowledged in the README and release notes!

---

Thank you for contributing to env-scanner! 🎉



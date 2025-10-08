# Publishing to PyPI - Complete Guide

This guide will walk you through publishing your env-scanner package to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on:
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

2. **Install build tools**:
```bash
pip install --upgrade build twine
```

## Step 1: Prepare Your Package

### 1.1 Update Package Metadata

Edit the following files and replace placeholder values:

**setup.py** - Update:
- `author="Your Name"` → Your actual name
- `author_email="your.email@example.com"` → Your email
- `url="https://github.com/yourusername/env-scanner"` → Your GitHub URL

**setup.cfg** - Update the same fields

**pyproject.toml** - Update the same fields

**LICENSE** - Update copyright with your name and year

### 1.2 Verify Package Info

Check that all metadata is correct:
```bash
python setup.py check
```

## Step 2: Build Your Package

Clean any previous builds:
```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info

# Build the package
python -m build
```

This creates two files in the `dist/` directory:
- `env-scanner-0.1.0.tar.gz` (source distribution)
- `env_scanner-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test Your Package Locally

Before uploading, test the package locally:

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install your package
pip install dist/env_scanner-0.1.0-py3-none-any.whl

# Test it works
env-scanner --version
env-scanner list .

# Deactivate and remove test env
deactivate
rm -rf test_env
```

## Step 4: Upload to Test PyPI (Optional but Recommended)

Test PyPI is a separate instance for testing packages before the real upload.

### 4.1 Create `.pypirc` file

Create `~/.pypirc` with your credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_PYPI_API_TOKEN_HERE

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_PYPI_API_TOKEN_HERE
```

**Get API Tokens:**
- Test PyPI: https://test.pypi.org/manage/account/token/
- PyPI: https://pypi.org/manage/account/token/

### 4.2 Upload to Test PyPI

```bash
# Check the package first
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*
```

### 4.3 Test Installation from Test PyPI

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ env-scanner

# Test it
env-scanner --version

# Cleanup
deactivate
rm -rf test_env
```

## Step 5: Upload to Production PyPI

Once you've verified everything works on Test PyPI:

```bash
# Upload to production PyPI
twine upload dist/*
```

You'll see output like:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading env_scanner-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
Uploading env-scanner-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View at:
https://pypi.org/project/env-scanner/0.1.0/
```

## Step 6: Verify Installation

Your package is now live! Anyone can install it:

```bash
pip install env-scanner
```

Test it yourself:
```bash
# Create fresh environment
python -m venv verify_env
source verify_env/bin/activate

# Install from PyPI
pip install env-scanner

# Test
env-scanner --version
env-scanner --help

# Cleanup
deactivate
rm -rf verify_env
```

## Updating Your Package

When you make changes and want to release a new version:

1. **Update version number** in:
   - `env_scanner/__init__.py` (change `__version__`)
   - This automatically updates setup.py and setup.cfg

2. **Update CHANGELOG.md** with changes

3. **Create a git tag**:
```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

4. **Build and upload**:
```bash
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*
```

## Quick Reference Commands

```bash
# Full publishing workflow
rm -rf build/ dist/ *.egg-info              # Clean
python -m build                              # Build
twine check dist/*                           # Verify
twine upload --repository testpypi dist/*   # Test upload
twine upload dist/*                          # Production upload
```

## Troubleshooting

### Error: "File already exists"
- You can't overwrite versions on PyPI
- Increment the version number and rebuild

### Error: "Invalid distribution"
- Run `twine check dist/*` to see what's wrong
- Common issues: Missing README, invalid metadata

### Error: "Package name already taken"
- Choose a different name
- Update name in setup.py, setup.cfg, and pyproject.toml

### Can't authenticate
- Make sure you're using API tokens, not password
- Token should start with `pypi-`
- Check `.pypirc` file format

## Security Best Practices

1. **Never commit `.pypirc`** with tokens to git
2. **Use API tokens** instead of passwords
3. **Scope tokens** to specific projects when possible
4. **Rotate tokens** periodically
5. **Use 2FA** on your PyPI account

## Alternative: Using GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI token as a GitHub secret named `PYPI_API_TOKEN`.

## Resources

- PyPI: https://pypi.org
- Test PyPI: https://test.pypi.org
- Python Packaging Guide: https://packaging.python.org
- Twine Documentation: https://twine.readthedocs.io

---

Good luck with your first PyPI package! 🚀


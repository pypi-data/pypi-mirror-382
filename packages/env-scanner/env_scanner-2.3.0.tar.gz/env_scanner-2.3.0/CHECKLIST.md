# Pre-Publishing Checklist

Complete this checklist before publishing to PyPI.

## ✏️ Update Package Information

- [ ] Update `setup.py`:
  - [ ] Change `author="Your Name"` to your actual name
  - [ ] Change `author_email="your.email@example.com"` to your email
  - [ ] Change GitHub URL from `yourusername` to your actual username

- [ ] Update `setup.cfg`:
  - [ ] Same author and email changes
  - [ ] Update URLs

- [ ] Update `pyproject.toml`:
  - [ ] Same author and email changes
  - [ ] Update URLs

- [ ] Update `LICENSE`:
  - [ ] Change "Your Name" to your name
  - [ ] Update year if needed

## 🔑 Set Up PyPI Accounts

- [ ] Create Test PyPI account: https://test.pypi.org/account/register/
- [ ] Create Production PyPI account: https://pypi.org/account/register/
- [ ] Enable 2FA on both accounts (recommended)
- [ ] Generate API token for Test PyPI: https://test.pypi.org/manage/account/token/
- [ ] Generate API token for Production PyPI: https://pypi.org/manage/account/token/

## 📝 Create ~/.pypirc File

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_PYPI_TOKEN_HERE

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_PRODUCTION_PYPI_TOKEN_HERE
```

- [ ] Created `~/.pypirc`
- [ ] Added Test PyPI token
- [ ] Added Production PyPI token
- [ ] Set permissions: `chmod 600 ~/.pypirc`

## 🧪 Test Your Package

- [ ] Run tests: `pytest`
- [ ] Check coverage: `pytest --cov`
- [ ] Test CLI locally: `env-scanner --version`
- [ ] Test CLI on sample project: `env-scanner list .`

## 📦 Build Your Package

- [ ] Install build tools: `pip install --upgrade build twine`
- [ ] Clean old builds: `rm -rf build/ dist/ *.egg-info`
- [ ] Build package: `python -m build`
- [ ] Check package: `twine check dist/*`

## 🧪 Test on Test PyPI (Recommended)

- [ ] Upload to Test PyPI: `twine upload --repository testpypi dist/*`
- [ ] Install from Test PyPI:
  ```bash
  pip install --index-url https://test.pypi.org/simple/ env-scanner
  ```
- [ ] Test installed package works

## 🚀 Publish to Production PyPI

- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify on PyPI website: https://pypi.org/project/env-scanner/
- [ ] Test installation: `pip install env-scanner`
- [ ] Test the installed package works

## 📢 Post-Publishing

- [ ] Create GitHub release with same version number
- [ ] Update README with installation instructions
- [ ] Share on social media (optional)
- [ ] Add to awesome lists (optional)

## 🔄 For Future Updates

When releasing a new version:

1. [ ] Update version in `env_scanner/__init__.py`
2. [ ] Update `CHANGELOG.md`
3. [ ] Create git tag: `git tag -a v0.2.0 -m "Version 0.2.0"`
4. [ ] Push tag: `git push origin v0.2.0`
5. [ ] Build and upload new version

---

## Quick Publish Commands

```bash
# Option 1: Use the script (easiest)
./publish.sh

# Option 2: Manual commands
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Production
```

---

**Remember:** You can't delete or modify a version once uploaded to PyPI. Test thoroughly first!


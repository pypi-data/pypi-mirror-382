# SmartTest CLI - Quick Start Guide

## 🚀 Testing Locally (Right Now!)

> **⚠️ IMPORTANT**: Always activate your virtual environment first!
> ```bash
> source venv/bin/activate
> ```

### Option 1: Quick Test (No Installation)

```bash
# Test the CLI directly
export SMARTTEST_TOKEN="your_pat_token_here"
python smarttest.py run --help

# Run a scenario (if you have one)
python smarttest.py run --scenario-id 123
```

### Option 2: Install for Development (Recommended)

```bash
# Install in editable mode
pip install -e ".[dev]"

# Now you can use 'smarttest' command anywhere
smarttest --help
smarttest --scenario-id 123
```

### Option 3: Use the Test Script

```bash
# Activate virtual environment first!
source venv/bin/activate

# Run comprehensive local tests
./scripts/test_local.sh
```

This script will:
- ✅ Install dependencies
- ✅ Verify CLI works
- ✅ Run test suite
- ✅ Build the package
- ✅ Verify package quality

---

## 📦 Publishing to PyPI

### First Time Setup

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Create PyPI accounts:**
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

3. **Get API tokens:**
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - Production PyPI: https://pypi.org/manage/account/token/

4. **Configure `~/.pypirc`:**
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-YOUR_PRODUCTION_TOKEN

   [testpypi]
   username = __token__
   password = pypi-YOUR_TEST_TOKEN
   ```

   ```bash
   chmod 600 ~/.pypirc  # Secure it
   ```

### Publishing Workflow

#### Step 1: Test on Test PyPI

```bash
# Use the automated script
./scripts/publish.sh test

# Or manually:
python -m build
twine upload --repository testpypi dist/*
```

#### Step 2: Verify Test PyPI Installation

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    smarttest-cli

# Test it
smarttest --help
deactivate
```

#### Step 3: Publish to Production PyPI

```bash
# Use the automated script (includes safety checks)
./scripts/publish.sh prod

# Or manually:
twine upload dist/*
```

---

## 🏷️ Version Management

### Bump Version

```bash
# Update version to 0.2.0
./scripts/bump_version.sh 0.2.0

# This will:
# - Update pyproject.toml
# - Show you the changes
# - Optionally commit and tag
# - Guide you through next steps
```

### Manual Version Update

```toml
# Edit pyproject.toml
[project]
version = "0.2.0"  # Change this
```

```bash
# Commit and tag
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin main --tags
```

---

## 🔧 Common Commands

### Development

```bash
# Install in editable mode
pip install -e ".[dev]"

# Run tests
python test_cli.py

# Test the command
smarttest --help
```

### Building

```bash
# Clean build
rm -rf dist/ build/ *.egg-info/

# Build package
python -m build

# Check package
twine check dist/*
```

### Publishing

```bash
# Test PyPI
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*

# Or use scripts
./scripts/publish.sh test   # Test PyPI
./scripts/publish.sh prod   # Production PyPI
```

---

## 🎯 Complete Workflow Example

### Making and Publishing a Change

```bash
# 1. Make your code changes
vim cli/main.py

# 2. Test locally
pip install -e ".[dev]"
smarttest --help
python test_cli.py

# 3. Bump version
./scripts/bump_version.sh 0.2.0

# 4. Publish to Test PyPI
./scripts/publish.sh test

# 5. Test installation from Test PyPI
python -m venv test_env
source test_env/bin/activate
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    smarttest-cli
smarttest --help
deactivate

# 6. If all good, publish to Production
./scripts/publish.sh prod

# 7. Push to git
git push origin main --tags
```

---

## 🧪 Testing Different Installation Methods

### Test 1: Editable Install

```bash
pip install -e ".[dev]"
smarttest --help
```

### Test 2: From Built Wheel

```bash
python -m build
pip install dist/smarttest_cli-0.1.0-py3-none-any.whl
smarttest --help
```

### Test 3: From Test PyPI

```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    smarttest-cli
smarttest --help
```

### Test 4: From Production PyPI

```bash
pip install smarttest-cli
smarttest --help
```

---

## 📋 Pre-Publishing Checklist

Before publishing, verify:

- [ ] All tests pass: `python test_cli.py`
- [ ] CLI works: `smarttest --help`
- [ ] Version updated in `pyproject.toml`
- [ ] Package builds: `python -m build`
- [ ] Package validates: `twine check dist/*`
- [ ] Tested on Test PyPI
- [ ] Git committed and tagged
- [ ] README is up-to-date
- [ ] No sensitive data in code

---

## 🆘 Troubleshooting

### "Command not found: smarttest"

```bash
# Reinstall
pip install -e . --force-reinstall

# Check it's in PATH
which smarttest

# Use Python module directly
python -m cli.main --help
```

### "Package already exists" error

```bash
# You've already published this version
# Bump the version first
./scripts/bump_version.sh 0.2.0
```

### "Invalid credentials" when uploading

```bash
# Check ~/.pypirc exists and has correct tokens
cat ~/.pypirc

# Or use environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
twine upload dist/*
```

### Import errors after installation

```bash
# Check what's installed
pip show smarttest-cli
pip list | grep smarttest

# Reinstall with verbose
pip install smarttest-cli -v
```

---

## 📚 More Information

For detailed documentation, see:
- **Testing & Publishing Guide**: `docs/CLI_TESTING_AND_PUBLISHING.md`
- **CLI README**: `cli/README.md`
- **Implementation Summary**: `CLI_IMPLEMENTATION_SUMMARY.md`

---

## ✨ TL;DR - Just Get It Done

```bash
# 1. Quick local test
pip install -e ".[dev]"
smarttest --help

# 2. Run automated test
./scripts/test_local.sh

# 3. Publish to Test PyPI
./scripts/publish.sh test

# 4. Publish to Production
./scripts/publish.sh prod
```

Done! 🎉





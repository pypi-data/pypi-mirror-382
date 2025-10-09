# 🚀 Publishing Shelldog to PyPI

This guide will walk you through publishing Shelldog to PyPI so anyone can install it with `pip install shelldog`.

## 📋 Prerequisites

1. **PyPI Account**: Create accounts on both:
   - **TestPyPI** (for testing): https://test.pypi.org/account/register/
   - **PyPI** (production): https://pypi.org/account/register/

2. **Install Required Tools**:
```bash
pip install --upgrade pip
pip install --upgrade build twine setuptools wheel
```

## 🏗️ Project Structure

Make sure your project structure looks like this:

```
shelldog/
├── shelldog/
│   ├── __init__.py
│   ├── cli.py
│   ├── logger.py
│   └── shell_hook.py
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── MANIFEST.in
├── .gitignore
└── PUBLISHING_GUIDE.md (this file)
```

## 🔧 Step-by-Step Publishing Process

### Step 1: Update Version Information

Before publishing, update the version in both files:

**In `setup.py`**:
```python
version="0.1.0",  # Change this for each release
```

**In `shelldog/__init__.py`**:
```python
__version__ = "0.1.0"  # Keep in sync with setup.py
```

**In `pyproject.toml`**:
```toml
version = "0.1.0"  # Keep in sync
```

### Step 2: Update Your Information

Replace placeholders in `setup.py` and `pyproject.toml`:
- `ansumanbhujabala@gmail.com` → Your actual email
- `https://github.com/Ansumanbhujabal/shelldog` → Your actual GitHub URL

### Step 3: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf shelldog.egg-info
```

### Step 4: Build the Package

```bash
# Build distribution files
python -m build

# This creates:
# dist/shelldog-0.1.0-py3-none-any.whl
# dist/shelldog-0.1.0.tar.gz
```

You should see output like:
```
Successfully built shelldog-0.1.0.tar.gz and shelldog-0.1.0-py3-none-any.whl
```

### Step 5: Test Your Package Locally

Before uploading, test if your package works:

```bash
# Install locally
pip install dist/shelldog-0.1.0-py3-none-any.whl

# Test it
shelldog --help
shelldog bark
shelldog follow

# Uninstall after testing
pip uninstall shelldog
```

### Step 6: Upload to TestPyPI (Recommended First)

TestPyPI is a separate instance of PyPI for testing. Always test here first!

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: Your TestPyPI username
# Password: Your TestPyPI password (or API token)
```

**Using API Token (Recommended)**:
1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token
3. Use `__token__` as username
4. Use the token (including `pypi-` prefix) as password

### Step 7: Test Installation from TestPyPI

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps shelldog

# Test it
shelldog --help
shelldog bark

# If it works, you're ready for production!
pip uninstall shelldog
```

### Step 8: Upload to Production PyPI 🎉

If everything works on TestPyPI:

```bash
# Upload to real PyPI
python -m twine upload dist/*

# Enter your PyPI credentials
# Username: Your PyPI username (or __token__)
# Password: Your PyPI password (or API token)
```

**Using API Token (Recommended)**:
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Use `__token__` as username
4. Use the token as password

### Step 9: Verify Publication

1. Visit your package page: `https://pypi.org/project/shelldog/`
2. Try installing it globally:

```bash
pip install shelldog

# Test it
shelldog --help
shelldog bark
```

## 🎊 You're Published!

Your package is now live! Anyone can install it with:
```bash
pip install shelldog
```

## 🔄 Updating Your Package

When you make changes and want to release a new version:

1. **Update the version number** in:
   - `setup.py`
   - `pyproject.toml`
   - `shelldog/__init__.py`

2. **Clean and rebuild**:
   ```bash
   rm -rf build/ dist/ *.egg-info
   python -m build
   ```

3. **Upload to TestPyPI first** (optional but recommended):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

## 📝 Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **0.1.0** → Initial release
- **0.1.1** → Bug fixes
- **0.2.0** → New features (backward compatible)
- **1.0.0** → First stable release

## 🔐 Security Best Practices

### Use API Tokens Instead of Passwords

Create a `.pypirc` file in your home directory:

```bash
nano ~/.pypirc
```

Add this content:
```ini
[testpypi]
username = __token__
password = pypi-your-test-token-here

[pypi]
username = __token__
password = pypi-your-production-token-here
```

Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

Now you won't be prompted for credentials!

## 🐛 Troubleshooting

### "File already exists" Error

You can't upload the same version twice. Update your version number!

### "Invalid distribution file" Error

Make sure you're in the project root directory and run:
```bash
rm -rf build/ dist/ *.egg-info
python -m build
```

### "Package name already taken"

Choose a different name or add a prefix/suffix (e.g., `shelldog-tracker`)

### Import Errors After Installation

Make sure your `__init__.py` properly exports classes:
```python
from .logger import ShelldogLogger
from .shell_hook import ShellHook

__all__ = ["ShelldogLogger", "ShellHook"]
```

## 📚 Useful Commands

```bash
# Check your package for issues
twine check dist/*

# View package information
pip show shelldog

# Uninstall
pip uninstall shelldog

# Install specific version
pip install shelldog==0.1.0

# Install from local file
pip install dist/shelldog-0.1.0-py3-none-any.whl
```

## 🎯 Quick Reference

```bash
# Complete release workflow
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
python -m twine upload --repository testpypi dist/*  # Test first!
python -m twine upload dist/*                        # Production
```

## 🌟 After Publishing

1. **Update GitHub**: Push your code and create a release
2. **Tag the release**: `git tag v0.1.0 && git push --tags`
3. **Share**: Tweet, blog, share with the community!
4. **Monitor**: Watch for issues and feedback

## 📖 Additional Resources

- PyPI Publishing Guide: https://packaging.python.org/tutorials/packaging-projects/
- Setuptools Documentation: https://setuptools.pypa.io/
- Twine Documentation: https://twine.readthedocs.io/

---

## 🐕 Good luck publishing Shelldog!

```
    /\_/\  
   ( ^.^ ) 
    > ^ <   "Woof! Ready to share me with the world!"
```

Remember: **Always test on TestPyPI first!** 🧪
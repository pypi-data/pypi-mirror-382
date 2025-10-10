# Distribution Guide for Smart Commit

## Directory Structure

Your final project structure should look like this:

```
smart-gcm/
├── smart_commit/
│   ├── __init__.py
│   ├── cli.py
│   ├── commit.py
│   └── utils.py
├── setup.py
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── LICENSE
├── .gitignore
└── DISTRIBUTION.md (this file)
```

## Prerequisites

1. Install required tools:
```bash
pip install --upgrade pip setuptools wheel twine build
```

2. Create accounts:
   - [PyPI Account](https://pypi.org/account/register/) (production)
   - [TestPyPI Account](https://test.pypi.org/account/register/) (testing)

## Step 1: Prepare Your Package

1. **Update metadata** in `setup.py` and `pyproject.toml`:
   - Replace `"Your Name"` with your actual name
   - Replace `"your.email@example.com"` with your email
   - Replace `"aakashvarma"` with your GitHub username
   - Update the repository URL

2. **Update version number** in:
   - `smart_commit/__init__.py`
   - `setup.py`
   - `pyproject.toml`

3. **Verify all files are present** according to the structure above

## Step 2: Build the Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the distribution packages
python -m build
```

This creates two files in the `dist/` directory:
- `smart-gcm-0.1.0.tar.gz` (source distribution)
- `smart_commit-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test on TestPyPI (Optional but Recommended)

1. **Upload to TestPyPI:**
```bash
twine upload --repository testpypi dist/*
```

2. **Test installation from TestPyPI:**
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps smart-gcm
```

3. **Test the command:**
```bash
gcm --help
```

4. **Uninstall test version:**
```bash
pip uninstall smart-gcm
```

## Step 4: Upload to PyPI (Production)

1. **Upload to PyPI:**
```bash
twine upload dist/*
```

You'll be prompted for your PyPI credentials.

2. **Verify upload:**
Visit https://pypi.org/project/smart-gcm/

## Step 5: Installation Instructions for Users

After publishing, users can install with:

```bash
pip install smart-gcm
```

## Using API Tokens (Recommended)

Instead of using username/password each time, create API tokens:

1. **For PyPI:**
   - Go to https://pypi.org/manage/account/token/
   - Create a token with scope for this project
   - Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE
```

2. **For TestPyPI:**
   - Go to https://test.pypi.org/manage/account/token/
   - Add TestPyPI section to `~/.pypirc`:

```ini
[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

## Updating Your Package

1. Make your changes
2. Update version numbers in all three files
3. Commit changes to Git
4. Create a Git tag:
```bash
git tag v0.1.1
git push origin v0.1.1
```
5. Rebuild and upload:
```bash
rm -rf build/ dist/ *.egg-info/
python -m build
twine upload dist/*
```

## Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Examples:
- `0.1.0` - Initial release
- `0.1.1` - Bug fix
- `0.2.0` - New feature
- `1.0.0` - First stable release

## Troubleshooting

### Package name already exists
If `smart-gcm` is taken, choose a different name:
1. Rename directory to `smart_commit_yourname`
2. Update all references in setup files
3. Update the command in entry_points to `gcm-yourname`

### Upload fails with authentication error
- Verify your credentials
- Try using API tokens instead of username/password
- Check `.pypirc` permissions

### Module not found after installation
- Ensure `smart_commit/__init__.py` exists
- Verify package structure matches documentation
- Try: `pip install --force-reinstall smart-gcm`

## Best Practices

1. **Always test locally first:**
   ```bash
   pip install -e .
   gcm
   ```

2. **Test on TestPyPI before production**

3. **Keep version numbers in sync** across all files

4. **Write a changelog** (CHANGELOG.md) documenting changes

5. **Tag releases in Git:**
   ```bash
   git tag -a v0.1.0 -m "Initial release"
   git push origin v0.1.0
   ```

6. **Add GitHub Actions** for automated testing and deployment

7. **Document breaking changes** clearly in README and changelog

## Quick Reference Commands

```bash
# Local development install
pip install -e .

# Build package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install smart-gcm

# Uninstall
pip uninstall smart-gcm
```

## GitHub Actions (Optional Automation)

Create `.github/workflows/publish.yml` for automated publishing:

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
    - name: Set up Python
      uses: actions/setup-python@v4
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

Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Support and Documentation

- **PyPI Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **setuptools Documentation**: https://setuptools.pypa.io/

## Need Help?

- Check PyPI packaging guide: https://packaging.python.org/tutorials/packaging-projects/
- Ask on Stack Overflow with tags: [python], [pip], [pypi]
- Check this project's issues on GitHub
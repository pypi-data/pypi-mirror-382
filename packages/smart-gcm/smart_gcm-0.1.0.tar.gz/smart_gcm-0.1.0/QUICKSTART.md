# Quick Start Guide

## For End Users (Installing the Package)

### 1. Install
```bash
pip install smart-gcm
```

### 2. Get Gemini API Key
1. Visit https://makersuite.google.com/app/apikey
2. Create an API key
3. Set environment variable:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Use
```bash
# Stage your changes
git add .

# Run smart commit
gcm
```

---

## For Developers (Building from Source)

### 1. Clone and Setup
```bash
# Create project directory
mkdir smart-gcm
cd smart-gcm

# Create the structure (copy all provided files into this directory)
```

### 2. Local Testing
```bash
# Install in editable mode
pip install -e .

# Test it
git add .
gcm
```

### 3. Build for Distribution
```bash
# Install build tools
pip install --upgrade build twine

# Build the package
python -m build

# This creates dist/ with:
# - smart-gcm-0.1.0.tar.gz
# - smart_commit-0.1.0-py3-none-any.whl
```

### 4. Test on TestPyPI (Optional)
```bash
# Upload to test server
twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ smart-gcm

# Test
gcm
```

### 5. Publish to PyPI
```bash
# Upload to real PyPI
twine upload dist/*

# Now anyone can install with:
# pip install smart-gcm
```

---

## File Checklist

Before publishing, ensure you have all these files:

```
smart-gcm/
├── smart_commit/           ✓ Package directory
│   ├── __init__.py        ✓ Package info
│   ├── cli.py             ✓ Command line interface
│   ├── commit.py          ✓ Message generation
│   └── utils.py           ✓ Utilities
├── setup.py               ✓ Setup configuration
├── pyproject.toml         ✓ Modern config
├── MANIFEST.in            ✓ Include non-Python files
├── README.md              ✓ User documentation
├── LICENSE                ✓ MIT License
├── .gitignore             ✓ Git ignores
├── DISTRIBUTION.md        ✓ Publishing guide
└── QUICKSTART.md          ✓ This file
```

---

## Common Issues

### "No module named 'smart_commit'"
- Make sure `__init__.py` exists in `smart_commit/` directory
- Try: `pip install --force-reinstall smart-gcm`

### "GEMINI_API_KEY not set"
- Export the variable in your shell
- Add to shell profile for persistence

### "No staged changes found"
- Run `git add <files>` before `gcm`

### Command `gcm` not found
- Ensure package is installed: `pip list | grep smart-gcm`
- Try: `python -m smart_commit.cli`
- Reinstall: `pip uninstall smart-gcm && pip install smart-gcm`

---

## Quick Commands Reference

```bash
# Development
pip install -e .              # Install locally
python -m smart_commit.cli    # Run directly

# Building
python -m build               # Build package
twine check dist/*            # Verify package

# Publishing
twine upload --repository testpypi dist/*  # Test
twine upload dist/*                         # Production

# Using
git add .                     # Stage changes
gcm                          # Generate commit
```

---

## Environment Setup Script

Save this as `setup_env.sh` and run once:

```bash
#!/bin/bash

# Setup script for smart-gcm

echo "Setting up smart-gcm environment..."

# Check if GEMINI_API_KEY is already set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "GEMINI_API_KEY not found in environment."
    echo -n "Enter your Gemini API key: "
    read -s api_key
    echo
    
    # Detect shell
    if [ -n "$ZSH_VERSION" ]; then
        shell_config="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        shell_config="$HOME/.bashrc"
    else
        shell_config="$HOME/.profile"
    fi
    
    # Add to shell config
    echo "export GEMINI_API_KEY=\"$api_key\"" >> "$shell_config"
    echo "✓ Added GEMINI_API_KEY to $shell_config"
    echo "Run: source $shell_config"
else
    echo "✓ GEMINI_API_KEY already configured"
fi

# Install package if not installed
if ! command -v gcm &> /dev/null; then
    echo "Installing smart-gcm..."
    pip install smart-gcm
    echo "✓ smart-gcm installed"
else
    echo "✓ smart-gcm already installed"
fi

echo ""
echo "Setup complete! Usage:"
echo "  1. Stage changes: git add ."
echo "  2. Run: gcm"
```

Make executable and run:
```bash
chmod +x setup_env.sh
./setup_env.sh
```
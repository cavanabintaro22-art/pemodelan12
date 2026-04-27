---
description: "Diagnose and fix pip install failures when building wheels for Python packages like gensim"
name: "Fix Pip Install Wheel Build Errors"
argument-hint: "Provide the error message from pip install command"
agent: "agent"
tools: [run_in_terminal, install_python_packages, get_python_environment_details]
---

# Fix Pip Install Wheel Build Errors

This prompt helps diagnose and resolve common pip install failures where building wheels fails, particularly for packages that require compilation or specific build dependencies.

## Common Causes and Fixes:

1. **Missing Build Dependencies**:
   - For packages like `gensim`, `scipy`, `numpy`: Install `Cython` first
   - System-level: Install `build-essential`, `python3-dev` (Linux) or equivalent
   - Run: `pip install Cython` before installing the failing package

2. **Pre-install Core Dependencies**:
   - Install `numpy` and `scipy` first, as many ML packages depend on them
   - Use: `pip install numpy scipy` before other packages

3. **Use No-Build-Isolation**:
   - Try: `pip install --no-build-isolation <package>`
   - This uses existing installed packages during build

4. **Update Pip and Setuptools**:
   - Run: `pip install --upgrade pip setuptools wheel`

5. **Check Python Version Compatibility**:
   - Ensure the package supports your Python version
   - Consider using conda: `conda install <package>`

6. **For Specific Packages**:
   - **gensim**: `pip install Cython` then `pip install gensim`
   - **PyTorch/Torch**: Use official install command from their site
   - **hdbscan**: May need `cython` and `numpy`

## Steps to Follow:

1. **Analyze the Error**: Look for keywords like "Failed building wheel", "error: command 'gcc' failed", "Cython required"

2. **Install Build Tools**:
   - Linux: `sudo apt-get install build-essential python3-dev`
   - macOS: Install Xcode command line tools

3. **Install Dependencies**:
   - `pip install Cython numpy scipy`

4. **Retry Installation**:
   - `pip install <package>` or with `--no-build-isolation`

5. **Alternative**: Use conda or pre-built wheels if available

Provide the full error output for more specific guidance.
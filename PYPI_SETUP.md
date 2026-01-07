# PyPI Publishing Guide for pyascfdl

This guide will help you build and publish the `pyascfdl` package to PyPI.

## Prerequisites

Install the necessary build tools:

```bash
pip install --upgrade pip
pip install build twine
```

## Building the Package

1. **Clean previous builds** (if any):

```bash
rm -rf dist/ build/ *.egg-info
```

2. **Build the distribution packages**:

```bash
python -m build
```

This will create two files in the `dist/` directory:
- A source distribution (`.tar.gz`)
- A wheel distribution (`.whl`)

3. **Verify the built packages**:

```bash
ls -lh dist/
```

You should see:
- `pyascfdl-0.1.0.tar.gz`
- `pyascfdl-0.1.0-py3-none-any.whl`

## Testing the Package Locally

Before publishing, test the package locally:

```bash
# Create a test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the package from the wheel
pip install dist/pyascfdl-0.1.0-py3-none-any.whl

# Test importing
python -c "import fdl; print(fdl.__name__)"

# Run the example
python -c "
import fdl
fdl_doc = fdl.AscFramingDecisionList()
print('Package works!')
"

# Cleanup
deactivate
rm -rf test_env
```

## Publishing to TestPyPI (Recommended First)

TestPyPI is a separate instance of PyPI for testing purposes.

1. **Create a TestPyPI account** at https://test.pypi.org/account/register/

2. **Create an API token** at https://test.pypi.org/manage/account/token/

3. **Upload to TestPyPI**:

```bash
python -m twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your TestPyPI API token (including the `pypi-` prefix)

4. **Test installation from TestPyPI**:

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps pyascfdl
```

Note: Use `--no-deps` because TestPyPI may not have all dependencies.

## Publishing to PyPI (Production)

Once you've tested on TestPyPI:

1. **Create a PyPI account** at https://pypi.org/account/register/

2. **Create an API token** at https://pypi.org/manage/account/token/

3. **Upload to PyPI**:

```bash
python -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token (including the `pypi-` prefix)

4. **Verify the upload**:

Visit https://pypi.org/project/pyascfdl/

5. **Test installation**:

```bash
pip install pyascfdl
```

## Version Updates

When releasing a new version:

1. **Update the version** in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or whatever the new version is
   ```

2. **Update CHANGELOG** (if you have one) with release notes

3. **Clean and rebuild**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```

4. **Upload the new version**:
   ```bash
   python -m twine upload dist/*
   ```

## Using API Tokens (Recommended)

Instead of entering credentials each time, you can configure them:

Create/edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YourActualTokenHere

[testpypi]
username = __token__
password = pypi-YourTestPyPITokenHere
```

Set permissions:
```bash
chmod 600 ~/.pypirc
```

Then you can upload without entering credentials:
```bash
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

## Package Verification Checklist

Before publishing, verify:

- [ ] `pyproject.toml` has correct metadata (version, description, author, etc.)
- [ ] `README.md` is up-to-date and renders correctly on PyPI
- [ ] `LICENSE` file is present
- [ ] All dependencies are listed in `pyproject.toml`
- [ ] Package builds without errors (`python -m build`)
- [ ] Package installs and imports correctly from the wheel
- [ ] Example code runs successfully
- [ ] Version number follows semantic versioning (MAJOR.MINOR.PATCH)

## Troubleshooting

**Error: File already exists**
- You can't upload the same version twice. Increment the version number.

**Error: Invalid or non-existent authentication**
- Double-check your API token
- Ensure you're using `__token__` as the username
- Make sure the token includes the `pypi-` prefix

**ImportError after installation**
- Check that `package-dir` and `packages.find` are correct in `pyproject.toml`
- Verify the package structure matches the configuration

**Missing dependencies**
- Ensure all required packages are listed in `dependencies` in `pyproject.toml`

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Documentation](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Setuptools Documentation](https://setuptools.pypa.io/)

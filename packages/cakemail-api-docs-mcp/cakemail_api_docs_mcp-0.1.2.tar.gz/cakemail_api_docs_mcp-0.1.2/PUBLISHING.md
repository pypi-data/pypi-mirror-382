# Publishing to PyPI

This guide explains how to publish the Cakemail MCP Server to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org
2. **API Token**: Generate an API token from https://pypi.org/manage/account/token/
3. **Test PyPI Account** (optional but recommended): Create at https://test.pypi.org

## Setup

### 1. Configure PyPI credentials

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

**Security Note**: Never commit API tokens to git!

### 2. Verify package quality

```bash
# Run all tests
uv run pytest tests/ -v

# Check code quality
uv run ruff check src/ tests/
uv run mypy src/

# Verify test coverage
uv run pytest tests/ --cov=src/cakemail_mcp --cov-report=term-missing
```

All checks must pass before publishing.

## Publishing Process

### Step 1: Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### Step 2: Build the Package

```bash
uv run python -m build
```

This creates:
- `dist/cakemail_mcp_server-0.1.0-py3-none-any.whl` (wheel)
- `dist/cakemail_mcp_server-0.1.0.tar.gz` (source distribution)

### Step 3: Verify Package

```bash
uv run twine check dist/*
```

Should show: ✅ PASSED for both files

### Step 4: Test on Test PyPI (Recommended)

```bash
uv run twine upload --repository testpypi dist/*
```

Then test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps cakemail-api-docs-mcp
```

Test the command:

```bash
cakemail-api-docs-mcp --version
cakemail-api-docs-mcp --help
```

### Step 5: Publish to PyPI

```bash
uv run twine upload dist/*
```

You'll see output like:

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading cakemail_mcp_server-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.5/12.5 kB • 00:00
Uploading cakemail_mcp_server-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.2/15.2 kB • 00:00

View at:
https://pypi.org/project/cakemail-api-docs-mcp/0.1.0/
```

### Step 6: Verify Installation

Wait a few minutes for PyPI to process, then test:

```bash
# Create a fresh virtual environment
python3 -m venv test-env
source test-env/bin/activate

# Install from PyPI
pip install cakemail-api-docs-mcp

# Test
cakemail-api-docs-mcp --version
cakemail-api-docs-mcp --help

# Cleanup
deactivate
rm -rf test-env
```

### Step 7: Test with Claude Code

```bash
claude mcp add cakemail -- uvx cakemail-api-docs-mcp
```

Restart Claude Desktop and verify the 🔌 icon appears.

## Post-Publication

### 1. Create GitHub Release

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Go to GitHub → Releases → Draft a new release:
- Tag: v0.1.0
- Title: "Cakemail MCP Server v0.1.0"
- Description: Copy from CHANGELOG.md

### 2. Update Documentation

Update links in README.md to point to PyPI package:

```markdown
[![PyPI version](https://badge.fury.io/py/cakemail-api-docs-mcp.svg)](https://pypi.org/project/cakemail-api-docs-mcp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/cakemail-api-docs-mcp.svg)](https://pypi.org/project/cakemail-api-docs-mcp/)
```

### 3. Announce

- Share on social media
- Post in MCP community forums
- Update Cakemail developer documentation

## Version Bumping (Future Releases)

1. Update version in `src/cakemail_mcp/__init__.py`
2. Update version in `pyproject.toml`
3. Update CHANGELOG.md with new changes
4. Follow publishing process above

## Troubleshooting

### "File already exists" error

You cannot re-upload the same version. Bump the version number and rebuild.

### Authentication failed

Check your API token in `~/.pypirc` is correct.

### Package validation errors

Run `uv run twine check dist/*` for details.

### Import errors after installation

Ensure `pyproject.toml` has correct package configuration:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/cakemail_mcp"]
```

## Security Checklist

Before publishing:

- [ ] No API keys or secrets in code
- [ ] No `.env` files in package
- [ ] No test credentials in tests
- [ ] All dependencies are from trusted sources
- [ ] README has security contact information

## Automation (Future)

Consider setting up:
- GitHub Actions for automatic publishing on tag push
- Dependabot for dependency updates
- Automated version bumping

## Support

For publishing issues:
- PyPI Help: https://pypi.org/help/
- Twine Docs: https://twine.readthedocs.io/
- Packaging Guide: https://packaging.python.org/

---

**Current Status**: ✅ Package built and validated - Ready to publish!

**Package Details**:
- Name: `cakemail-api-docs-mcp`
- Version: `0.1.0`
- Files: wheel (11KB) + source (392KB)
- Python: >=3.11

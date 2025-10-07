# Publishing to NPM

This guide explains how to publish the Cakemail MCP Server to npm as a wrapper package.

## Why NPM + PyPI?

Publishing to **both** NPM and PyPI gives users maximum flexibility:

- **NPM**: Users can run `npx cakemail-api-docs-mcp` (JavaScript ecosystem)
- **PyPI**: Users can run `uvx cakemail-api-docs-mcp` (Python ecosystem)
- Both work with `claude mcp add`

## How It Works

The npm package is a **lightweight wrapper** that:
1. Detects if `uvx` or `pipx` is available
2. Runs the Python package via `uvx cakemail-api-docs-mcp`
3. Falls back to `pipx` if `uvx` isn't available
4. Shows helpful error messages if neither is available

**Benefits**:
- Users don't need to know Python
- Works seamlessly with `npx`
- Compatible with Claude Desktop's `claude mcp add` command

## Prerequisites

1. **NPM Account**: Create at https://www.npmjs.com
2. **Access Token**: Generate from https://www.npmjs.com/settings/[username]/tokens
3. **Node.js**: Version 18+ installed

## Setup

### 1. Login to NPM

```bash
npm login
```

Enter your:
- Username
- Password
- Email
- One-time password (if 2FA enabled)

### 2. Verify Package Contents

```bash
# Check what will be published
npm pack --dry-run
```

Should include:
- `package.json`
- `bin/cakemail-api-docs-mcp.js`

## Publishing Process

### Step 1: Verify Package

```bash
# Check package.json is valid
npm pkg get name version
# Should output: {"name":"cakemail-api-docs-mcp","version":"0.1.0"}

# Test the wrapper locally
node bin/cakemail-api-docs-mcp.js --version
```

### Step 2: Publish to NPM

```bash
npm publish
```

You'll see:
```
npm notice
npm notice 📦  cakemail-api-docs-mcp@0.1.0
npm notice === Tarball Contents ===
npm notice 2.0kB bin/cakemail-api-docs-mcp.js
npm notice 614B  package.json
npm notice === Tarball Details ===
npm notice name:          cakemail-api-docs-mcp
npm notice version:       0.1.0
npm notice filename:      cakemail-api-docs-mcp-0.1.0.tgz
npm notice package size:  1.2 kB
npm notice unpacked size: 2.6 kB
npm notice total files:   2
npm notice
+ cakemail-api-docs-mcp@0.1.0
```

### Step 3: Verify Installation

```bash
# Test with npx (downloads and runs)
npx cakemail-api-docs-mcp@0.1.0 --version

# Should output: cakemail-api-docs-mcp 0.1.0
```

### Step 4: Test with Claude Code

```bash
claude mcp add cakemail -- npx cakemail-api-docs-mcp
```

Restart Claude Desktop and verify the 🔌 icon appears.

## Installation Methods for Users

After publishing, users can install in multiple ways:

### Method 1: NPX (No Installation)
```bash
claude mcp add cakemail -- npx cakemail-api-docs-mcp
```
**Best for**: Quick setup, no local installation needed

### Method 2: Global NPM Install
```bash
npm install -g cakemail-api-docs-mcp
claude mcp add cakemail cakemail-api-docs-mcp
```
**Best for**: Users who prefer npm ecosystem

### Method 3: UVX (Python)
```bash
claude mcp add cakemail -- uvx cakemail-api-docs-mcp
```
**Best for**: Python developers

### Method 4: PIP (Python)
```bash
pip install cakemail-api-docs-mcp
claude mcp add cakemail cakemail-api-docs-mcp
```
**Best for**: Traditional Python workflow

## Configuration

All methods support the same configuration:

```json
{
  "mcpServers": {
    "cakemail": {
      "command": "npx",
      "args": ["cakemail-api-docs-mcp"],
      "env": {
        "OPENAPI_SPEC_PATH": "https://api.cakemail.dev/openapi.json",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Dual Publishing Strategy

**Recommended**: Publish to BOTH PyPI and NPM

### 1. Publish Python Package to PyPI
```bash
uv run python -m build
uv run twine upload dist/*
```

### 2. Publish NPM Wrapper to NPM
```bash
npm publish
```

### Benefits of Dual Publishing
- ✅ JavaScript developers can use `npx`
- ✅ Python developers can use `uvx` or `pip`
- ✅ Both ecosystems get the same functionality
- ✅ Maximum compatibility with MCP tools
- ✅ Users choose their preferred package manager

## Version Management

When releasing new versions:

### 1. Update Versions in BOTH
```bash
# Python version
# Edit: src/cakemail_mcp/__init__.py
# Edit: pyproject.toml

# NPM version
npm version patch  # or minor, or major
```

### 2. Publish Both Packages
```bash
# PyPI
uv run python -m build
uv run twine upload dist/*

# NPM
npm publish
```

### 3. Tag Git Release
```bash
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
```

## Troubleshooting

### "Package name already taken"

The name `cakemail-api-docs-mcp` must be available. If taken, try:
- `@cakemail/mcp-server`
- `cakemail-api-mcp`

### "Permission denied"

```bash
chmod +x bin/cakemail-api-docs-mcp.js
```

### Testing Wrapper Locally

```bash
# Link package locally
npm link

# Test it
cakemail-api-docs-mcp --version

# Unlink when done
npm unlink -g cakemail-api-docs-mcp
```

### NPM Publish Fails

Check:
- Logged in: `npm whoami`
- Version not taken: Check https://www.npmjs.com/package/cakemail-api-docs-mcp
- Valid package.json: `npm pkg fix`

## Best Practices

### 1. Keep Versions Synchronized
- NPM and PyPI versions should match
- Update both when releasing

### 2. Test Both Installation Methods
```bash
# Test NPM
npx cakemail-api-docs-mcp@latest --version

# Test PyPI
uvx cakemail-api-docs-mcp --version
```

### 3. Document Both Methods
In README.md, show both installation options

### 4. Set up npm Scripts (Optional)
```json
{
  "scripts": {
    "test": "node bin/cakemail-api-docs-mcp.js --help",
    "prepublishOnly": "chmod +x bin/cakemail-api-docs-mcp.js"
  }
}
```

## Comparison: Installation Methods

| Method | Command | Package Manager | Users |
|--------|---------|----------------|-------|
| NPX | `npx cakemail-api-docs-mcp` | npm | JavaScript devs |
| UVX | `uvx cakemail-api-docs-mcp` | uv | Python devs |
| NPM Global | `npm i -g` then run | npm | npm users |
| PIP | `pip install` then run | pip | pip users |

**All methods** work with `claude mcp add`!

## Security Notes

- ✅ Wrapper only executes `uvx` or `pipx` - no arbitrary code
- ✅ No dependencies in npm package
- ✅ Small package size (~2.6 KB)
- ✅ Source code visible in npm registry

## Automation

Consider setting up GitHub Actions for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to NPM and PyPI
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - uses: actions/setup-python@v5
      - run: npm publish
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
```

---

**Current Status**: ✅ NPM package ready to publish!

**Package Details**:
- Name: `cakemail-api-docs-mcp`
- Version: `0.1.0`
- Size: ~2.6 KB
- Files: `package.json`, `bin/cakemail-api-docs-mcp.js`

**Next Steps**:
1. `npm login`
2. `npm publish`
3. Test with `npx cakemail-api-docs-mcp --version`

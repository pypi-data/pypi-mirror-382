#!/usr/bin/env node

/**
 * NPM wrapper for Cakemail API Documentation MCP Server
 *
 * This package wraps the Python implementation which must be installed separately.
 * For now, this runs the local Python implementation directly.
 */

const { spawn } = require('child_process');
const { platform } = require('os');
const path = require('path');
const fs = require('fs');

// Try to find local installation first
function findLocalInstall() {
  const possiblePaths = [
    path.join(__dirname, '..', 'src', 'cakemail_mcp', '__main__.py'),
    path.join(process.cwd(), 'src', 'cakemail_mcp', '__main__.py'),
  ];

  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return path.dirname(path.dirname(p));
    }
  }
  return null;
}

// Check if uvx is available
function hasCommand(cmd) {
  return new Promise((resolve) => {
    const check = spawn(cmd, ['--version'], { shell: true });
    check.on('error', () => resolve(false));
    check.on('exit', (code) => resolve(code === 0));
  });
}

async function main() {
  const args = process.argv.slice(2);

  // Try local development installation first
  const localPath = findLocalInstall();
  if (localPath) {
    console.error('Running from local development installation...');
    const pythonCmd = platform() === 'win32' ? 'python' : 'python3';
    const server = spawn(pythonCmd, ['-m', 'cakemail_mcp', ...args], {
      stdio: 'inherit',
      shell: platform() === 'win32',
      cwd: localPath
    });
    server.on('exit', (code) => process.exit(code || 0));
    return;
  }

  // Try uvx (if package is published to PyPI)
  if (await hasCommand('uvx')) {
    console.error('Starting via uvx...');
    const server = spawn('uvx', ['cakemail-api-docs-mcp', ...args], {
      stdio: 'inherit',
      shell: platform() === 'win32'
    });

    server.on('exit', (code) => {
      if (code !== 0) {
        console.error('\n❌ Error: Package not found on PyPI yet.');
        console.error('\nThe Python package "cakemail-api-docs-mcp" has not been published to PyPI yet.');
        console.error('\nFor now, please install from source:');
        console.error('  git clone https://github.com/cakemail/cakemail-api-documentation-mcp.git');
        console.error('  cd cakemail-api-documentation-mcp');
        console.error('  pip install -e .');
        console.error('\nThen configure Claude to use the local installation:');
        console.error('  See INSTALLATION.md for details');
      }
      process.exit(code || 0);
    });
    return;
  }

  // Try system Python installation
  if (await hasCommand('cakemail-api-docs-mcp')) {
    console.error('Starting from system installation...');
    const server = spawn('cakemail-api-docs-mcp', args, {
      stdio: 'inherit',
      shell: platform() === 'win32'
    });
    server.on('exit', (code) => process.exit(code || 0));
    return;
  }

  // Nothing worked
  console.error('\n❌ Error: Cakemail MCP Server not found.');
  console.error('\nThe Python package is not yet published to PyPI.');
  console.error('\nPlease install from source:');
  console.error('  git clone https://github.com/cakemail/cakemail-api-documentation-mcp.git');
  console.error('  cd cakemail-api-documentation-mcp');
  console.error('  pip install -e .');
  console.error('\nOr install uv and wait for PyPI publication:');
  console.error('  curl -LsSf https://astral.sh/uv/install.sh | sh');
  process.exit(1);
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});

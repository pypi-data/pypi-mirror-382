# DAKSH

Documentation & Artifact Knowledge Synchronization Hub - A CLI tool for updating project prompts and development configuration.

## Installation

### Python (Recommended)

#### Using pip
```bash
# Install from PyPI
pip install daksh

# Or install from GitHub
pip install git+https://github.com/divamidesignlabs/daksh.git
```

#### Using uvx (Python 3.11+)
```bash
# Run directly without installation
uvx daksh update-prompts

# Or install with uv
uv tool install daksh
```

#### Development Installation
```bash
git clone https://github.com/divamidesignlabs/daksh
cd daksh
uv pip install -e .
```

### Node.js

#### Using npx (Recommended)
```bash
# Run directly without installation
npx daksh-ai update-prompts
```

#### Global Installation
```bash
# Install globally
npm install -g daksh-ai

# Then use anywhere
daksh update-prompts
```

#### Development Installation
```bash
git clone https://github.com/divamidesignlabs/daksh
cd daksh
npm link
```

## Usage

### Basic Command
Update your project with the latest development prompts and configuration:

```bash
# Python
daksh update-prompts

# Node.js (if installed globally)
daksh update-prompts

# Node.js (using npx)
npx daksh-ai update-prompts
```

### Preview Changes (Dry Run)
See what files would be updated without making changes:

```bash
# Python
daksh update-prompts --dry-run

# Node.js
daksh update-prompts --dry-run
# or
npx daksh-ai update-prompts --dry-run
```

### Help
```bash
# Python
daksh --help

# Node.js
daksh --help
# or
npx daksh-ai --help
```

## What It Does

The `update-prompts` command will add/update the following files in your project:

- `.daksh/` - Prompt templates and guidelines
- `.vscode/settings.json` - VS Code configuration for prompts
- `.github/copilot-instructions.md` - GitHub Copilot instructions
- `mkdocs.yml` - Documentation configuration
- `docs/overrides/extra.css` - Documentation styling
- `overrides/` - MkDocs overrides
- `docs/index.md` - Documentation index (if it doesn't exist)

After running the command, you'll see a summary of all files that were added or updated.
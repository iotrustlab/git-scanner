# git-scanner

A fast and efficient CLI tool to scan and analyze GitHub repositories.

## 🚀 Get Started

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Set your GitHub token
export GITHUB_TOKEN='your_github_token'

# Scan a repository
python git_scanner.py microsoft/vscode

# Scan all repositories of an organization
python git_scanner.py microsoft
```

## Setup Guide

1. **Python Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`
   ```

2. **Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **GitHub Token:**
   - Create a token at: GitHub → Settings → Developer settings → Tokens (classic)
   - Set it in your environment:
     ```bash
     export GITHUB_TOKEN='your_token'
     ```

## Usage Examples

Scan a specific repository:
```bash
python git_scanner.py microsoft/vscode
```

Scan all repositories and export to CSV:
```bash
python git_scanner.py microsoft --format csv --output microsoft_repos
```

Include private repositories:
```bash
python git_scanner.py microsoft --private
```

## Options

```bash
python git_scanner.py [owner] [options]

Options:
  --repo REPO     Target specific repository
  --format        Output format: table, csv, json, excel (default: table)
  --output        Custom output filename
  --private       Include private repositories
  --token         Override GitHub token
```

## Output Formats

- **Table:** Clean console output (default)
- **CSV:** Comma-separated values
- **JSON:** Structured data format
- **Excel:** Multi-sheet workbook

## Repository Stats

- Basic: Stars, forks, watchers
- Activity: Last commit, open issues
- Meta: Language, license, visibility
- Size and creation date

## Requirements

- Python 3.8+
- GitHub Token (public_repo or repo scope)
- Required packages in requirements.txt

## Building from Source

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Build Steps
Windows:
```batch
.\build.bat

macOS/Linux:
```bash
chmod +x build.sh
./build.sh
```

The executable will be generated in the `release/` directory.

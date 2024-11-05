# git-scanner

A friendly CLI tool that helps you analyze GitHub repositories and their issues. Perfect for getting insights into repository health and activity.

## Quick Start

```bash
# Set up your environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install what you need
pip install -r requirements.txt

# Set your GitHub token
export GITHUB_TOKEN='your_github_token'

# Try it out!
python git_scanner.py microsoft/vscode  # Look at a specific repo
python git_scanner.py microsoft         # Check all repos in an organization
```

## What Can It Do?

### Repository Analysis

```bash
# Basic repo scanning
python git_scanner.py microsoft/vscode

# Get stats for all repos and save to Excel
python git_scanner.py microsoft --format excel --output microsoft_stats

# Include private repos (if your token has access)
python git_scanner.py microsoft --private
```

### Issue Tracking (New!)

```bash
# See all issues in a repo
python git_scanner.py microsoft/vscode --repo vscode --issues

# Export issues to a folder
python git_scanner.py microsoft/vscode --repo vscode --issues --output vscode_issues
```

## Output Options

You can get your results in several formats:

- **Table**: Nice clean console output (default)
- **CSV**: Good for spreadsheets
- **JSON**: Perfect for data processing
- **Excel**: Professional reports with auto-formatted columns

For issues, you'll get:

- A metadata summary
- NDJSON file with issue details
- Separate folders for large issue content

## What You'll See

### Repository Stats

- Stars, forks, and watchers
- Open/closed issues and PRs
- Average time to resolve issues
- Latest activity timestamps
- Languages used
- Repository size
- License info

### Issue Details (New!)

- Issue status (open/closed)
- Creation and update dates
- Labels and assignees
- Full issue descriptions
- Comment counts
- Issue URLs

## Setting Up

1. You'll need:
   - Python 3.8 or newer
   - A GitHub token (get it from GitHub → Settings → Developer settings → Tokens)

2. Set up your token:

   ```bash
   export GITHUB_TOKEN='your_token'
   # or use it directly:
   python git_scanner.py microsoft --token your_token
   ```

## Common Commands

```bash
# Basic repository scanning
python git_scanner.py microsoft/vscode

# All commands available
python git_scanner.py --help

# Repository stats with different outputs
python git_scanner.py microsoft --format csv
python git_scanner.py microsoft --format json
python git_scanner.py microsoft --format excel

# Working with issues
python git_scanner.py microsoft/vscode --repo vscode --issues
```

## Tips

- Use `--private` if you need to see private repositories
- The tool handles rate limiting automatically
- For large organizations, be patient - it'll fetch everything systematically
- Issue exports are organized to handle large amounts of content
- Use `Ctrl+C` to stop if you need to

That's it! The tool aims to be simple but powerful. If you run into any problems or need help, feel free to open an issue on GitHub.
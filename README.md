# git-scanner

A command-line tool for analyzing GitHub repositories and their issues to help assess repository health and activity.

## Getting Started

There are two ways to use git-scanner: downloading the pre-built executable or running from source.

### Using Pre-built Executables (Simplest)

1. Download the executable for your system from our [latest release](v1.1.0):
   - Linux: `git-scanner-linux` (41.2 MB)
   - macOS: `git-scanner-macos` (28.9 MB)
   - Windows: `git-scanner-windows.exe` (39.1 MB)

2. For convenience, you might want to rename it to just `git-scanner`:

   ```bash
   # Linux/macOS
   mv git-scanner-linux git-scanner    # or git-scanner-macos on Mac
   chmod +x git-scanner

   # Windows
   rename git-scanner-windows.exe git-scanner.exe
   ```

Note: We don't have an installer yet, so you'll need to run the executable from wherever you download it. You can move it to a convenient location or add its directory to your PATH.

### Running From Source

If you prefer to run from source:

```bash
# 1. Set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Before You Start

You'll need a GitHub token. Export it as an environment variable:

```bash
export GITHUB_TOKEN='your_github_token'
```

## Basic Usage

If you're using the executable:

```bash
./git-scanner turtlebot --repo turtlebot4   # Linux/macOS
git-scanner.exe turtlebot --repo turtlebot4  # Windows
```

If you're running from source:

```bash
python git_scanner.py turtlebot --repo turtlebot4
```

## What You Can Do

### Repository Analysis

```bash
# Look at a specific repo
git-scanner turtlebot --repo turtlebot4

# Check all repos in an organization
git-scanner turtlebot

# Include private repos (if your token has access)
git-scanner turtlebot --private
```

### Issue Tracking

```bash
# Export all issues from a repo
git-scanner turtlebot --repo turtlebot4 --issues
```

### Different Output Formats

```bash
git-scanner turtlebot --format [table|csv|json|excel] --output filename
```

## What You'll Get

### Repository Stats

- Basic stats (stars, forks, watchers)
- Issue and PR counts
- Activity information
- Technical details (languages, size, license)

### Issue Details

- Status and timeline info
- Labels and assignees
- Full issue content
- Related metadata

## Good to Know

- The tool handles GitHub's rate limits automatically
- For big organizations, it might take a while to fetch everything
- Hit `Ctrl+C` if you need to stop

Having trouble? Found a bug? Please open an issue on GitHub - we'd love to help!
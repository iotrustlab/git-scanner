import requests
from datetime import datetime, timezone, timedelta
import argparse
import humanize
import os
import sys
import pandas as pd
from tabulate import tabulate
import concurrent.futures
from tqdm import tqdm
from statistics import mean, median
from collections import defaultdict

class GitHubAuth:
    @staticmethod
    def get_token():
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("\n❌ No GITHUB_TOKEN environment variable found.")
            print("Either:")
            print("1. Set the environment variable: export GITHUB_TOKEN='your_token'")
            print("2. Or provide token via argument: --token YOUR_TOKEN")
            sys.exit(1)
        return token

class GitHubStats:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        self.headers["Accept"] = "application/vnd.github.v3+json"

    def get_all_repos(self, owner, include_private=True):
        if '/' in owner:
            print("Please provide only the organization/user name, not a specific repository.")
            sys.exit(1)

        page = 1
        repos = []
        while True:
            url = f"{self.base_url}/users/{owner}/repos" if '/' not in owner else f"{self.base_url}/orgs/{owner}/repos"
            params = {
                'page': page,
                'per_page': 100,
                'type': 'all' if include_private else 'public'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        return repos

    def get_repo_issues_and_prs(self, owner, repo):
        """Get detailed issue and PR statistics."""
        try:
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            pulls_url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            
            all_issues = []
            page = 1
            while True:
                params = {'state': 'all', 'page': page, 'per_page': 100}
                response = requests.get(issues_url, headers=self.headers, params=params)
                response.raise_for_status()
                issues = response.json()
                if not issues:
                    break
                all_issues.extend(issues)
                page += 1

            all_prs = []
            page = 1
            while True:
                params = {'state': 'all', 'page': page, 'per_page': 100}
                response = requests.get(pulls_url, headers=self.headers, params=params)
                response.raise_for_status()
                prs = response.json()
                if not prs:
                    break
                all_prs.extend(prs)
                page += 1

            pure_issues = [issue for issue in all_issues if 'pull_request' not in issue]
            
            now = datetime.now(timezone.utc)
            
            open_issues = [i for i in pure_issues if i['state'] == 'open']
            closed_issues = [i for i in pure_issues if i['state'] == 'closed']
            
            open_prs = [pr for pr in all_prs if pr['state'] == 'open']
            merged_prs = [pr for pr in all_prs if pr.get('merged_at')]
            closed_prs = [pr for pr in all_prs if pr['state'] == 'closed' and not pr.get('merged_at')]

            if pure_issues:
                first_issue_date = min([
                    datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    for issue in pure_issues
                ])
                days_since_first_issue = max((now - first_issue_date).days, 1)
            else:
                days_since_first_issue = 1

            issue_resolution_times = []
            for issue in closed_issues:
                created = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                closed = datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                issue_resolution_times.append((closed - created).days)

            pr_resolution_times = []
            for pr in merged_prs + closed_prs:
                created = datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                closed = datetime.strptime(pr['closed_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                pr_resolution_times.append((closed - created).days)

            avg_issue_resolution = mean(issue_resolution_times) if issue_resolution_times else 0
            avg_pr_resolution = mean(pr_resolution_times) if pr_resolution_times else 0
            
            return {
                'issues': {
                    'total': len(pure_issues),
                    'open': len(open_issues),
                    'closed': len(closed_issues),
                    'avg_resolution_days': avg_issue_resolution,
                    'last_issue_date': max([issue['created_at'] for issue in pure_issues]) if pure_issues else None
                },
                'pulls': {
                    'total': len(all_prs),
                    'open': len(open_prs),
                    'merged': len(merged_prs),
                    'rejected': len(closed_prs),
                    'avg_resolution_days': avg_pr_resolution,
                    'last_pr_date': max([pr['created_at'] for pr in all_prs]) if all_prs else None
                }
            }
        except Exception as e:
            print(f"Error fetching issues/PRs for {owner}/{repo}: {str(e)}")
            return None

    def get_repo_stats(self, owner, repo):
        """Get comprehensive repository statistics."""
        try:
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            commits_url = f"{repo_url}/commits"
            
            repo_response = requests.get(repo_url, headers=self.headers)
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            if not repo_data:
                return None
                
            commits_response = requests.get(f"{commits_url}?per_page=1", headers=self.headers)
            commits_response.raise_for_status()
            last_commit = commits_response.json()[0] if commits_response.json() else None
            
            issue_pr_stats = self.get_repo_issues_and_prs(owner, repo) or {
                'issues': {'total': 0, 'open': 0, 'closed': 0, 'avg_resolution_days': 0, 'last_issue_date': None},
                'pulls': {'total': 0, 'open': 0, 'merged': 0, 'rejected': 0,
                         'avg_resolution_days': 0, 'last_pr_date': None}
            }

            try:
                last_commit_date = datetime.strptime(
                    last_commit["commit"]["author"]["date"], 
                    "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc) if last_commit else None
            except (TypeError, KeyError):
                last_commit_date = None

            return {
                "name": repo_data.get("name", "Unknown"),
                "description": repo_data.get("description", "No description"),
                "language": repo_data.get("language", "Not specified"),
                "created_at": datetime.strptime(repo_data.get("created_at", "2000-01-01T00:00:00Z"), "%Y-%m-%dT%H:%M:%SZ"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "last_commit": humanize.naturaltime(
                    datetime.now(timezone.utc) - last_commit_date
                ) if last_commit_date else "Never",
                "total_issues": issue_pr_stats['issues']['total'],
                "open_issues": issue_pr_stats['issues']['open'],
                "closed_issues": issue_pr_stats['issues']['closed'],
                "issue_resolution_time_avg": round(issue_pr_stats['issues']['avg_resolution_days'], 1),
                "total_prs": issue_pr_stats['pulls']['total'],
                "open_prs": issue_pr_stats['pulls']['open'],
                "merged_prs": issue_pr_stats['pulls']['merged'],
                "rejected_prs": issue_pr_stats['pulls']['rejected'],
                "pr_resolution_time_avg": round(issue_pr_stats['pulls']['avg_resolution_days'], 1),
                "size_kb": repo_data.get("size", 0),
                "default_branch": repo_data.get("default_branch", "main"),
                "license": repo_data.get("license", {}).get("name", "Not specified") if repo_data.get("license") else "Not specified",
                "is_template": repo_data.get("is_template", False),
                "visibility": repo_data.get("visibility", "unknown")
            }
                
        except Exception as e:
            print(f"Error fetching stats for {owner}/{repo}: {str(e)}")
            return None

def format_number(num):
    """Format numbers for better readability."""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}k"
    return str(num)

def display_stats(stats):
    """Display repository statistics in a clean, compact format."""
    if not stats:
        print("No repository statistics available.")
        return

    # Filter out .github repository
    stats = [repo for repo in stats if repo['name'] != '.github']
    
    # Sort repositories by stars
    sorted_stats = sorted(stats, key=lambda x: x['stars'], reverse=True)
    
    # Create table data
    table_data = []
    for repo in sorted_stats:
        stars = format_number(repo['stars'])
        forks = format_number(repo['forks'])
        issues = f"{repo['total_issues']} | {repo['open_issues']}"
        prs = f"{repo['total_prs']} | {repo['merged_prs']}"
        
        table_data.append([
            repo['name'][:40],
            f"{stars:>4}",
            f"{forks:>4}",
            f"{issues:>9}",
            f"{prs:>9}",
            repo['last_commit']
        ])

    headers = [
        "Repository",
        "Stars",
        "Forks",
        "Issues (Total | Open)",
        "PRs (Total | Merged)",
        "Last Commit"
    ]

    print("\nRepository Analysis")
    print(tabulate(
        table_data,
        headers=headers,
        tablefmt="simple",
        numalign="right",
        stralign="left",
        colalign=("left", "right", "right", "center", "center", "left")
    ))

    # Summary statistics with emojis
    total_stars = sum(repo['stars'] for repo in stats)
    total_forks = sum(repo['forks'] for repo in stats)
    total_issues = sum(repo['total_issues'] for repo in stats)
    total_prs = sum(repo['total_prs'] for repo in stats)
    
    print("\nSummary Statistics")
    summary_data = [
        ["📦 Repositories", f"{len(stats):>5}", "⭐ Stars", f"{format_number(total_stars):>5}"],
        ["📝 Issues", f"{format_number(total_issues):>5} ({sum(r['open_issues'] for r in stats)} open)", 
         "🔀 PRs", f"{format_number(total_prs):>5} ({sum(r['merged_prs'] for r in stats)} merged)"],
        ["🔄 Forks", f"{format_number(total_forks):>5}"]
    ]
    
    print(tabulate(summary_data, tablefmt="plain", colalign=("left", "right", "left", "right")))

    # Most active repositories
    active_repos = sorted(stats, key=lambda x: x['total_issues'] + x['total_prs'], reverse=True)[:3]
    if any(repo['total_issues'] + repo['total_prs'] > 0 for repo in active_repos):
        print("\n🔥 Most Active Repositories:")
        for repo in active_repos:
            if repo['total_issues'] + repo['total_prs'] > 0:
                print(f"• {repo['name']}: {repo['total_issues']} issues, {repo['total_prs']} PRs")

def export_stats(stats, format='csv', filename=None):
    """Export repository statistics to a file."""
    if not stats:
        print("No statistics to export.")
        return

    # Filter out .github repository for exports
    stats = [repo for repo in stats if repo['name'] != '.github']

    # Create timestamp for filename
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"github_stats_{timestamp}"

    try:
        # Convert to DataFrame
        df = pd.DataFrame(stats)
        
        # Reorder columns for better readability
        columns_order = [
            'name', 'description', 'language', 'visibility',
            'stars', 'forks', 'watchers',
            'total_issues', 'open_issues', 'closed_issues',
            'total_prs', 'merged_prs', 'rejected_prs', 'open_prs',
            'issue_resolution_time_avg', 'pr_resolution_time_avg',
            'created_at', 'last_commit',
            'size_kb', 'default_branch', 'license',
            'is_template'
        ]
        
        # Only include columns that exist
        df = df[[col for col in columns_order if col in df.columns]]
        
        # Export based on format
        if format == 'csv':
            output_file = f"{filename}.csv"
            df.to_csv(output_file, index=False)
        elif format == 'json':
            output_file = f"{filename}.json"
            df.to_json(output_file, orient='records', indent=2)
        elif format == 'excel':
            output_file = f"{filename}.xlsx"
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Repository Stats')
                # Auto-adjust column widths
                for column in df:
                    column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
                    col_idx = df.columns.get_loc(column)
                    writer.sheets['Repository Stats'].column_dimensions[chr(65 + col_idx)].width = min(column_width, 50)
        
        print(f"\n📁 Statistics exported to {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error exporting statistics: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub repository statistics")
    parser.add_argument("owner", help="Repository owner/organization")
    parser.add_argument("--repo", help="Specific repository name (optional)")
    parser.add_argument("--token", help="GitHub personal access token")
    parser.add_argument("--format", choices=['csv', 'json', 'excel'], help="Export format")
    parser.add_argument("--output", help="Output filename (without extension)")
    parser.add_argument("--private", action="store_true", 
                       help="Include private repositories (requires appropriate token permissions)")
    
    args = parser.parse_args()
    
    try:
        token = args.token or GitHubAuth.get_token()
        github_stats = GitHubStats(token)
        
        if args.repo:
            print(f"\nFetching statistics for {args.owner}/{args.repo}...")
            stats = [github_stats.get_repo_stats(args.owner, args.repo)]
            if not stats[0]:
                print(f"❌ Failed to fetch statistics for {args.owner}/{args.repo}")
                sys.exit(1)
        else:
            print(f"\nFetching repository list for {args.owner}...")
            repos = github_stats.get_all_repos(args.owner, include_private=args.private)
            if not repos:
                print(f"❌ No repositories found for {args.owner}")
                sys.exit(1)
                
            print(f"Found {len(repos)} repositories")
            
            # Fetch stats for all repositories
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_repo = {
                    executor.submit(
                        github_stats.get_repo_stats, 
                        repo["owner"]["login"], 
                        repo["name"]
                    ): repo for repo in repos
                }
                
                stats = []
                with tqdm(total=len(repos), desc="Fetching repository stats") as pbar:
                    for future in concurrent.futures.as_completed(future_to_repo):
                        repo_stats = future.result()
                        if repo_stats:
                            stats.append(repo_stats)
                        pbar.update(1)

        # Display stats
        if stats:
            display_stats(stats)
            
            # Export if format is specified
            if args.format:
                export_stats(stats, format=args.format, filename=args.output)
        else:
            print("❌ No statistics available to display")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
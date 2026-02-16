#!/usr/bin/env python3
"""
GitHub Repository Survey Tool with GitHub API Integration

This script surveys GitHub repositories to identify which ones use:
- GitHub Milestones (issue tracking milestones)
- GitHub Projects (project boards/planning)

Usage:
    python survey_repos_github.py owner/repo1 owner/repo2 ...
    python survey_repos_github.py --file repos.txt
    
Environment Variables:
    GITHUB_TOKEN - GitHub personal access token (optional, increases rate limits)

The script will output a report showing which repositories use each feature.
"""

import sys
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error


@dataclass
class RepoSurveyResult:
    """Results from surveying a single repository"""
    owner: str
    repo: str
    has_milestones: bool
    milestone_count: int
    has_projects: bool
    project_count: int
    error: Optional[str] = None


class GitHubAPIClient:
    """Simple GitHub API client"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
    
    def _make_request(self, endpoint: str) -> Any:
        """Make a GET request to GitHub API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Repo-Survey-Tool'
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"Repository not found or not accessible")
            elif e.code == 403:
                raise PermissionError(f"API rate limit exceeded or access denied")
            else:
                raise Exception(f"HTTP {e.code}: {e.reason}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_milestones(self, owner: str, repo: str) -> List[Dict]:
        """Get all milestones for a repository"""
        # Get both open and closed milestones
        all_milestones = []
        
        # Get open milestones
        try:
            open_milestones = self._make_request(f"/repos/{owner}/{repo}/milestones?state=open&per_page=100")
            all_milestones.extend(open_milestones)
        except:
            pass
        
        # Get closed milestones
        try:
            closed_milestones = self._make_request(f"/repos/{owner}/{repo}/milestones?state=closed&per_page=100")
            all_milestones.extend(closed_milestones)
        except:
            pass
        
        return all_milestones
    
    def get_projects(self, owner: str, repo: str) -> List[Dict]:
        """Get all projects for a repository"""
        # Note: Projects API requires special accept header
        endpoint = f"/repos/{owner}/{repo}/projects"
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Accept': 'application/vnd.github.inertia-preview+json',  # Projects API preview
            'User-Agent': 'GitHub-Repo-Survey-Tool'
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Repository might not have projects enabled
                return []
            elif e.code == 410:
                # Projects classic is deprecated, try new projects
                return []
            else:
                return []
        except:
            return []


class RepoSurveyor:
    """Survey GitHub repositories for Milestone and Project usage"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.results: List[RepoSurveyResult] = []
        self.github = GitHubAPIClient(github_token)
    
    def survey_repository(self, owner: str, repo: str) -> RepoSurveyResult:
        """
        Survey a single repository for Milestone and Project usage.
        """
        result = RepoSurveyResult(
            owner=owner,
            repo=repo,
            has_milestones=False,
            milestone_count=0,
            has_projects=False,
            project_count=0,
            error=None
        )
        
        try:
            # Check for milestones
            milestones = self.github.get_milestones(owner, repo)
            result.milestone_count = len(milestones)
            result.has_milestones = result.milestone_count > 0
            
            # Check for projects
            projects = self.github.get_projects(owner, repo)
            result.project_count = len(projects)
            result.has_projects = result.project_count > 0
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def survey_repositories(self, repo_specs: List[str]) -> List[RepoSurveyResult]:
        """
        Survey multiple repositories.
        
        Args:
            repo_specs: List of repository specifications in format "owner/repo"
        
        Returns:
            List of survey results
        """
        for spec in repo_specs:
            if '/' not in spec:
                print(f"Warning: Skipping invalid repo spec '{spec}' (expected format: owner/repo)", file=sys.stderr)
                continue
            
            owner, repo = spec.split('/', 1)
            print(f"Surveying {owner}/{repo}...", file=sys.stderr)
            result = self.survey_repository(owner, repo)
            self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a text report of survey results"""
        lines = []
        lines.append("=" * 80)
        lines.append("GitHub Repository Survey Report")
        lines.append("=" * 80)
        lines.append("")
        
        if not self.results:
            lines.append("No repositories surveyed.")
            return "\n".join(lines)
        
        # Summary
        total = len(self.results)
        with_milestones = sum(1 for r in self.results if r.has_milestones)
        with_projects = sum(1 for r in self.results if r.has_projects)
        with_both = sum(1 for r in self.results if r.has_milestones and r.has_projects)
        with_errors = sum(1 for r in self.results if r.error)
        
        lines.append(f"Total repositories surveyed: {total}")
        lines.append(f"Repositories using Milestones: {with_milestones}")
        lines.append(f"Repositories using Projects: {with_projects}")
        lines.append(f"Repositories using both: {with_both}")
        if with_errors > 0:
            lines.append(f"Repositories with errors: {with_errors}")
        lines.append("")
        
        # Repositories using Milestones
        lines.append("-" * 80)
        lines.append("Repositories Using Milestones")
        lines.append("-" * 80)
        milestone_repos = [r for r in self.results if r.has_milestones]
        if milestone_repos:
            for result in milestone_repos:
                lines.append(f"  {result.owner}/{result.repo} - {result.milestone_count} milestone(s)")
        else:
            lines.append("  None")
        lines.append("")
        
        # Repositories using Projects
        lines.append("-" * 80)
        lines.append("Repositories Using Projects")
        lines.append("-" * 80)
        project_repos = [r for r in self.results if r.has_projects]
        if project_repos:
            for result in project_repos:
                lines.append(f"  {result.owner}/{result.repo} - {result.project_count} project(s)")
        else:
            lines.append("  None")
        lines.append("")
        
        # Detailed results
        lines.append("-" * 80)
        lines.append("Detailed Results")
        lines.append("-" * 80)
        for result in self.results:
            lines.append(f"\nRepository: {result.owner}/{result.repo}")
            if result.error:
                lines.append(f"  Error: {result.error}")
            else:
                lines.append(f"  Milestones: {'Yes' if result.has_milestones else 'No'} ({result.milestone_count})")
                lines.append(f"  Projects: {'Yes' if result.has_projects else 'No'} ({result.project_count})")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def export_json(self) -> str:
        """Export results as JSON"""
        return json.dumps([asdict(r) for r in self.results], indent=2)


def load_repos_from_file(filename: str) -> List[str]:
    """Load repository specifications from a file (one per line)"""
    repos = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    repos.append(line)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    return repos


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python survey_repos_github.py owner/repo1 owner/repo2 ...")
        print("  python survey_repos_github.py --file repos.txt")
        print("  python survey_repos_github.py --json owner/repo1 owner/repo2 ...")
        print("")
        print("Environment Variables:")
        print("  GITHUB_TOKEN - GitHub personal access token (optional, increases rate limits)")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    output_json = False
    repos = []
    
    if '--json' in args:
        output_json = True
        args.remove('--json')
    
    if '--file' in args:
        file_idx = args.index('--file')
        if file_idx + 1 >= len(args):
            print("Error: --file requires a filename argument", file=sys.stderr)
            sys.exit(1)
        filename = args[file_idx + 1]
        repos = load_repos_from_file(filename)
    else:
        repos = args
    
    if not repos:
        print("Error: No repositories specified", file=sys.stderr)
        sys.exit(1)
    
    # Survey repositories
    surveyor = RepoSurveyor()
    surveyor.survey_repositories(repos)
    
    # Output results
    if output_json:
        print(surveyor.export_json())
    else:
        print(surveyor.generate_report())


if __name__ == '__main__':
    main()

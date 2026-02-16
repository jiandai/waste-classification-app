#!/usr/bin/env python3
"""
GitHub Repository Survey Tool

This script surveys GitHub repositories to identify which ones use:
- GitHub Milestones (issue tracking milestones)
- GitHub Projects (project boards/planning)

Usage:
    python survey_repos.py owner/repo1 owner/repo2 ...
    python survey_repos.py --file repos.txt

The script will output a report showing which repositories use each feature.
"""

import sys
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class RepoSurveyResult:
    """Results from surveying a single repository"""
    owner: str
    repo: str
    has_milestones: bool
    milestone_count: int
    has_projects: bool
    project_count: int
    error: str = None


class RepoSurveyor:
    """Survey GitHub repositories for Milestone and Project usage"""
    
    def __init__(self):
        self.results: List[RepoSurveyResult] = []
    
    def survey_repository(self, owner: str, repo: str) -> RepoSurveyResult:
        """
        Survey a single repository for Milestone and Project usage.
        
        Note: This is a placeholder that shows the structure.
        In practice, this would use GitHub API calls via:
        - GitHub MCP server tools (if available in environment)
        - PyGithub library
        - Direct REST API calls
        """
        # Placeholder for demonstration
        # In real implementation, would make API calls here
        
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
            # TODO: Implement actual API calls
            # Example pseudo-code:
            # milestones = github_api.get_milestones(owner, repo)
            # result.milestone_count = len(milestones)
            # result.has_milestones = result.milestone_count > 0
            
            # projects = github_api.get_projects(owner, repo)
            # result.project_count = len(projects)
            # result.has_projects = result.project_count > 0
            
            pass
            
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
                print(f"Warning: Skipping invalid repo spec '{spec}' (expected format: owner/repo)")
                continue
            
            owner, repo = spec.split('/', 1)
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
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    return repos


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python survey_repos.py owner/repo1 owner/repo2 ...")
        print("  python survey_repos.py --file repos.txt")
        print("  python survey_repos.py --json owner/repo1 owner/repo2 ...")
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
            print("Error: --file requires a filename argument")
            sys.exit(1)
        filename = args[file_idx + 1]
        repos = load_repos_from_file(filename)
    else:
        repos = args
    
    if not repos:
        print("Error: No repositories specified")
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

# GitHub Repository Survey Tool

A utility to survey GitHub repositories and identify which ones use Milestones and/or Projects for project management.

## Purpose

This tool helps teams and organizations understand how they are using GitHub's built-in project management features across their repositories:

- **Milestones**: Issue tracking milestones for organizing work into releases or sprints
- **Projects**: Project boards for kanban-style planning and task management

## Features

- Survey multiple repositories in a single run
- Support for both individual repository arguments and batch file input
- JSON output option for programmatic processing
- Detailed reporting with counts and summaries
- Works with or without a GitHub token (token recommended for higher rate limits)

## Installation

No additional dependencies required! The script uses only Python standard library modules.

Requirements:
- Python 3.7 or higher

## Usage

### Basic Usage

Survey individual repositories:
```bash
python3 survey_repos_github.py owner/repo1 owner/repo2 owner/repo3
```

### Using a File

Create a file with repository specifications (one per line):
```bash
# repos.txt
facebook/react
microsoft/vscode
python/cpython
```

Then run:
```bash
python3 survey_repos_github.py --file repos.txt
```

### JSON Output

For programmatic processing, use the `--json` flag:
```bash
python3 survey_repos_github.py --json owner/repo1 owner/repo2
```

### With GitHub Token

To avoid rate limits (recommended for surveying many repositories):
```bash
export GITHUB_TOKEN=your_token_here
python3 survey_repos_github.py --file repos.txt
```

## Output Examples

### Standard Report

```
================================================================================
GitHub Repository Survey Report
================================================================================

Total repositories surveyed: 3
Repositories using Milestones: 1
Repositories using Projects: 2
Repositories using both: 1

--------------------------------------------------------------------------------
Repositories Using Milestones
--------------------------------------------------------------------------------
  owner/repo1 - 5 milestone(s)

--------------------------------------------------------------------------------
Repositories Using Projects
--------------------------------------------------------------------------------
  owner/repo1 - 2 project(s)
  owner/repo2 - 1 project(s)

--------------------------------------------------------------------------------
Detailed Results
--------------------------------------------------------------------------------

Repository: owner/repo1
  Milestones: Yes (5)
  Projects: Yes (2)

Repository: owner/repo2
  Milestones: No (0)
  Projects: Yes (1)

Repository: owner/repo3
  Milestones: No (0)
  Projects: No (0)

================================================================================
```

### JSON Output

```json
[
  {
    "owner": "owner",
    "repo": "repo1",
    "has_milestones": true,
    "milestone_count": 5,
    "has_projects": true,
    "project_count": 2,
    "error": null
  },
  {
    "owner": "owner",
    "repo": "repo2",
    "has_milestones": false,
    "milestone_count": 0,
    "has_projects": true,
    "project_count": 1,
    "error": null
  }
]
```

## GitHub API Rate Limits

- **Without authentication**: 60 requests per hour
- **With authentication**: 5,000 requests per hour

Each repository survey uses 2-3 API requests (one for milestones, one for projects). For large surveys, use a GitHub personal access token.

### Creating a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Repo Survey Tool")
4. Select scopes:
   - `repo` (if surveying private repositories)
   - `public_repo` (if only surveying public repositories)
5. Generate and copy the token
6. Set it as an environment variable:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

## Use Cases

1. **Audit project management practices**: Understand which teams are using which features
2. **Migration planning**: Identify repositories that need to migrate from Milestones to Projects or vice versa
3. **Standardization**: Ensure consistent use of project management tools across an organization
4. **Reporting**: Generate reports for management on tool adoption
5. **Discovery**: Find repositories actively using specific features for best practices

## Limitations

- Surveys GitHub Projects Classic (the older project board feature)
- Does not survey the newer GitHub Projects (introduced in 2021, generally available since 2022) which uses a GraphQL-based API
- Limited to 100 milestones per repository (pagination not implemented)
- Limited to 100 projects per repository (pagination not implemented)
- Cannot access private repositories without appropriate token permissions

## Troubleshooting

### "API rate limit exceeded"
- Use a GitHub personal access token (see above)
- Wait for the rate limit to reset (check `X-RateLimit-Reset` header)

### "Repository not found or not accessible"
- Verify the repository name is correct (format: `owner/repo`)
- If the repository is private, ensure your token has appropriate permissions
- Check that the repository exists and hasn't been renamed or deleted

### "API request failed"
- Check your internet connection
- Verify GitHub API is accessible (not blocked by firewall)
- Ensure the GitHub API is not experiencing outages

## License

This tool is part of the waste-classification-app repository. See the main repository LICENSE for details.

## Contributing

Contributions welcome! Potential improvements:
- Add support for new GitHub Projects (beta)
- Implement pagination for repositories with 100+ milestones/projects
- Add caching to avoid redundant API calls
- Support for organization-wide surveys
- Export to CSV format
- Add filtering options (e.g., only show repos with milestones)

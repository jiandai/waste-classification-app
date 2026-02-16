# GitHub Repository Survey Tool - Demo

This document demonstrates the usage of the GitHub Repository Survey Tool.

## Quick Demo

### 1. Survey a Single Repository

```bash
$ python3 survey_repos_github.py jiandai/waste-classification-app
```

Output:
```
Surveying jiandai/waste-classification-app...
================================================================================
GitHub Repository Survey Report
================================================================================

Total repositories surveyed: 1
Repositories using Milestones: 0
Repositories using Projects: 0
Repositories using both: 0

--------------------------------------------------------------------------------
Repositories Using Milestones
--------------------------------------------------------------------------------
  None

--------------------------------------------------------------------------------
Repositories Using Projects
--------------------------------------------------------------------------------
  None

--------------------------------------------------------------------------------
Detailed Results
--------------------------------------------------------------------------------

Repository: jiandai/waste-classification-app
  Milestones: No (0)
  Projects: No (0)

================================================================================
```

### 2. Survey Multiple Repositories

```bash
$ python3 survey_repos_github.py facebook/react microsoft/vscode
```

This will survey both repositories and provide a combined report.

### 3. Use a File for Batch Surveying

Create a file `repos.txt`:
```
facebook/react
microsoft/vscode
python/cpython
torvalds/linux
```

Then run:
```bash
$ python3 survey_repos_github.py --file repos.txt
```

### 4. Get JSON Output

For programmatic processing:
```bash
$ python3 survey_repos_github.py --json jiandai/waste-classification-app
```

Output:
```json
[
  {
    "owner": "jiandai",
    "repo": "waste-classification-app",
    "has_milestones": false,
    "milestone_count": 0,
    "has_projects": false,
    "project_count": 0,
    "error": null
  }
]
```

## Use Cases

### Audit Your Organization's Repositories

Survey all repositories in your organization to see which ones are using project management features:

```bash
# Create a list of your repos
echo "myorg/repo1
myorg/repo2
myorg/repo3" > my_repos.txt

# Survey them
python3 survey_repos_github.py --file my_repos.txt
```

### Migration Planning

Identify repositories that need to migrate from one tool to another:

```bash
# Find all repos using Milestones but not Projects
python3 survey_repos_github.py --json --file repos.txt | \
  jq '.[] | select(.has_milestones == true and .has_projects == false)'
```

### Generate Reports

Create a CSV report for management:

```bash
# Survey and format as CSV
python3 survey_repos_github.py --json --file repos.txt | \
  jq -r '["owner","repo","milestones","projects"], (.[] | [.owner, .repo, .has_milestones, .has_projects]) | @csv'
```

## Tips

1. **Use a GitHub Token**: Set `GITHUB_TOKEN` environment variable to avoid rate limits
2. **Batch Processing**: Survey repositories in batches to stay within rate limits
3. **Save Results**: Redirect output to a file for later analysis
4. **Error Handling**: Check the `error` field in JSON output for failed surveys

See [SURVEY_TOOL_README.md](./SURVEY_TOOL_README.md) for complete documentation.

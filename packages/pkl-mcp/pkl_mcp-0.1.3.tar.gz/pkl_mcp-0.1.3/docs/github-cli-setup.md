# GitHub CLI Setup and Operations

This document provides comprehensive guidance for setting up and using GitHub CLI with the pkl-mcp project.

## Overview

GitHub CLI (`gh`) is integrated into this project to streamline repository operations, pull request management, and release workflows. While optional, it significantly improves the development experience.

## Installation

### macOS

**Using Homebrew (Recommended):**
```bash
brew install gh
```

**Using MacPorts:**
```bash
sudo port install gh
```

### Linux

**Ubuntu/Debian:**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**CentOS/RHEL/Fedora:**
```bash
sudo dnf install gh
```

**Arch Linux:**
```bash
sudo pacman -S github-cli
```

### Windows

**Using Chocolatey:**
```bash
choco install gh
```

**Using Scoop:**
```bash
scoop install gh
```

**Using winget:**
```bash
winget install --id GitHub.cli
```

### Verification

After installation, verify GitHub CLI is available:
```bash
gh --version
```

## Authentication

### Initial Setup

1. **Web-based Authentication (Recommended):**
   ```bash
   gh auth login --web
   ```
   
   This opens your web browser for secure authentication and automatically configures the necessary scopes.

2. **Token-based Authentication:**
   ```bash
   # Create a personal access token at https://github.com/settings/tokens
   # Then authenticate with the token
   gh auth login --with-token < token.txt
   ```

### Required Scopes

For full functionality with this project, ensure your authentication includes:

- **`repo`**: Full repository access (required for private repositories)
- **`workflow`**: GitHub Actions workflow management
- **`read:org`**: Read organization membership (if working with organization repositories)

### Verification

Check your authentication status:
```bash
gh auth status
```

Expected output should show:
- ✓ Logged in to github.com as [username]
- ✓ Git operations for github.com configured to use https protocol
- ✓ Token scopes: repo, workflow

## Project Integration

### Local Build Script Integration

The local build script (`scripts/local-build.sh`) automatically checks GitHub CLI authentication:

```bash
./scripts/local-build.sh
```

If GitHub CLI is not authenticated, you'll see a warning but the build will continue. For full functionality, ensure authentication is complete.

### GitHub Helper Commands

The project includes a comprehensive helper script for GitHub operations:

```bash
./scripts/github-helpers.sh
```

## Common Operations

### Repository Management

**Create a new repository:**
```bash
./scripts/github-helpers.sh create-repo my-package-name
```

**View repository information:**
```bash
./scripts/github-helpers.sh repo-info
```

### Pull Request Workflow

**Create a pull request:**
```bash
# First, create and switch to a feature branch
git checkout -b feature/my-new-feature

# Make your changes and commit them
git add .
git commit -m "Add new feature"

# Create pull request
./scripts/github-helpers.sh create-pr "Add new feature" "Detailed description of the feature"
```

**List open pull requests:**
```bash
./scripts/github-helpers.sh list-prs
```

**Merge a pull request:**
```bash
./scripts/github-helpers.sh merge-pr 123
```

### Release Management

**Create a release:**
```bash
./scripts/github-helpers.sh create-release v1.0.0 "First stable release"
```

**List releases:**
```bash
./scripts/github-helpers.sh list-releases
```

### GitHub Actions Integration

**Check workflow status:**
```bash
./scripts/github-helpers.sh workflow-status
```

**Trigger a workflow:**
```bash
./scripts/github-helpers.sh run-workflow ci.yml
```

## Troubleshooting

### Authentication Issues

**Problem:** `gh auth status` shows not authenticated
```bash
# Solution: Re-authenticate
gh auth logout
gh auth login --web --scopes "repo,workflow"
```

**Problem:** Permission denied errors
```bash
# Solution: Refresh token with required scopes
gh auth refresh --scopes "repo,workflow"
```

### Repository Access Issues

**Problem:** Cannot access repository
```bash
# Check if repository exists and you have access
gh repo view

# If repository doesn't exist, create it
./scripts/github-helpers.sh create-repo your-repo-name
```

**Problem:** Git operations fail with authentication errors
```bash
# Configure git to use GitHub CLI for authentication
gh auth setup-git
```

### Network and Proxy Issues

**Problem:** GitHub CLI cannot connect through corporate proxy
```bash
# Configure proxy settings
export HTTPS_PROXY=http://proxy.company.com:8080
export HTTP_PROXY=http://proxy.company.com:8080

# Or configure git proxy
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy http://proxy.company.com:8080
```

### Token Expiration

**Problem:** Authentication token has expired
```bash
# Check token status
gh auth status

# Refresh the token
gh auth refresh

# If refresh fails, re-authenticate
gh auth login --web
```

## Security Best Practices

### Token Management

1. **Use web authentication when possible** - it's more secure than manual token creation
2. **Regularly rotate tokens** - refresh authentication periodically
3. **Use minimal required scopes** - don't grant unnecessary permissions
4. **Store tokens securely** - GitHub CLI handles this automatically

### Repository Security

1. **Use private repositories** for sensitive code
2. **Enable branch protection** for main branches
3. **Require status checks** before merging
4. **Use signed commits** when possible

### Workflow Security

1. **Review workflow permissions** in GitHub Actions
2. **Use secrets** for sensitive data in workflows
3. **Limit workflow triggers** to necessary events
4. **Audit workflow runs** regularly

## Advanced Configuration

### Custom GitHub Enterprise

If using GitHub Enterprise Server:
```bash
gh auth login --hostname your-github-enterprise.com
```

### Multiple Accounts

GitHub CLI supports multiple accounts:
```bash
# Switch between accounts
gh auth switch --hostname github.com
gh auth switch --hostname your-enterprise.com
```

### Configuration Files

GitHub CLI configuration is stored in:
- **macOS/Linux:** `~/.config/gh/`
- **Windows:** `%AppData%\GitHub CLI\`

### Environment Variables

Useful environment variables:
- `GH_TOKEN`: Personal access token
- `GH_HOST`: GitHub hostname (for Enterprise)
- `GH_REPO`: Default repository
- `GH_EDITOR`: Preferred editor for GitHub CLI

## Integration with Development Workflow

### Pre-commit Integration

The project's pre-commit hooks work seamlessly with GitHub CLI operations. The recommended workflow:

1. Make changes on a feature branch
2. Run local build validation: `./scripts/local-build.sh`
3. Commit changes (pre-commit hooks run automatically)
4. Push branch and create PR: `./scripts/github-helpers.sh create-pr`
5. Merge after CI passes: `./scripts/github-helpers.sh merge-pr`

### Release Workflow

For releasing new versions:

1. Ensure all changes are merged to main
2. Run local build validation: `./scripts/local-build.sh`
3. Create release: `./scripts/github-helpers.sh create-release v1.0.0`
4. GitHub Actions automatically publishes to PyPI

## Support and Resources

- **GitHub CLI Documentation:** https://cli.github.com/manual/
- **GitHub CLI Repository:** https://github.com/cli/cli
- **GitHub API Documentation:** https://docs.github.com/en/rest
- **Personal Access Tokens:** https://github.com/settings/tokens

For project-specific issues with GitHub CLI integration, check the helper script:
```bash
./scripts/github-helpers.sh --help
```
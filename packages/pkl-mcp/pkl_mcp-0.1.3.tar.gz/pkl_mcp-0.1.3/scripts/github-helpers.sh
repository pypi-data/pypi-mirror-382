#!/bin/bash

# GitHub CLI helper commands for pkl-mcp package
# Provides convenient commands for common GitHub operations
# Requirements: 7.1, 7.2, 7.3, 7.4

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✅${NC} ${1}"
}

print_error() {
    echo -e "${RED}❌${NC} ${1}"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} ${1}"
}

print_info() {
    echo -e "${CYAN}ℹ️${NC} ${1}"
}

# Function to check GitHub CLI authentication
check_gh_auth() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed."
        print_info "Install it from: https://cli.github.com/"
        exit 1
    fi

    # Check if any account is authenticated and active
    if ! gh auth status 2>&1 | grep -q "Active account: true"; then
        print_error "GitHub CLI is not authenticated or no active account found."
        print_info "Run '$0 auth-login' to authenticate."
        echo ""
        print_info "Current status:"
        gh auth status 2>&1 || true
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo -e "${PURPLE}GitHub CLI Helper Commands for pkl-mcp${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  auth-status     Check GitHub CLI authentication status"
    echo "  auth-login      Authenticate with GitHub (web browser)"
    echo "  create-repo     Create a new private repository"
    echo "  repo-info       Show current repository information"
    echo "  create-pr       Create a pull request from current branch"
    echo "  list-prs        List open pull requests"
    echo "  merge-pr        Merge a pull request by number"
    echo "  create-release  Create a new release with tag"
    echo "  list-releases   List all releases"
    echo "  workflow-status Show GitHub Actions workflow status"
    echo "  run-workflow    Trigger a workflow run"
    echo ""
    echo "Examples:"
    echo "  $0 auth-status"
    echo "  $0 create-repo my-package"
    echo "  $0 create-pr \"Add new feature\" \"Implements feature X with tests\""
    echo "  $0 create-release v1.0.0 \"First release\""
    echo ""
}

# Command: Check authentication status
cmd_auth_status() {
    print_step "Checking GitHub CLI authentication status"
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        print_info "Install from: https://cli.github.com/"
        return 1
    fi

    # Check if any account is authenticated and active
    if gh auth status 2>&1 | grep -q "Active account: true"; then
        print_success "GitHub CLI is properly authenticated"
        echo ""
        print_info "Authentication details:"
        gh auth status 2>&1 | grep -A1 -B1 "Active account: true" || true
        echo ""
        gh auth status 2>&1 | grep "Token scopes:" || true
    else
        print_error "GitHub CLI is not authenticated or no active account found"
        print_info "Run: $0 auth-login"
        echo ""
        print_info "Current status:"
        gh auth status 2>&1 || true
        return 1
    fi
}

# Command: Authenticate with GitHub
cmd_auth_login() {
    print_step "Authenticating with GitHub CLI"
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        print_info "Install from: https://cli.github.com/"
        return 1
    fi

    print_info "Opening web browser for authentication..."
    print_info "This will authenticate with GitHub and enable repository operations."
    
    if gh auth login --web --scopes "repo,workflow"; then
        print_success "Successfully authenticated with GitHub"
        cmd_auth_status
    else
        print_error "Authentication failed"
        return 1
    fi
}

# Command: Create repository
cmd_create_repo() {
    local repo_name="${1:-}"
    
    if [ -z "$repo_name" ]; then
        print_error "Repository name is required"
        print_info "Usage: $0 create-repo <repository-name>"
        return 1
    fi

    check_gh_auth
    
    print_step "Creating private repository: $repo_name"
    
    if gh repo create "$repo_name" --private --description "Python PyPI package with modern tooling" --gitignore Python --license MIT; then
        print_success "Repository '$repo_name' created successfully"
        print_info "Repository URL: https://github.com/$(gh api user --jq .login)/$repo_name"
        
        # Optionally clone the repository
        read -p "Clone the repository locally? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gh repo clone "$repo_name"
            print_success "Repository cloned to ./$repo_name"
        fi
    else
        print_error "Failed to create repository"
        return 1
    fi
}

# Command: Show repository information
cmd_repo_info() {
    check_gh_auth
    
    print_step "Repository information"
    
    if gh repo view; then
        print_success "Repository information retrieved"
    else
        print_error "Failed to get repository information"
        print_info "Make sure you're in a git repository with GitHub remote"
        return 1
    fi
}

# Command: Create pull request
cmd_create_pr() {
    local title="${1:-}"
    local body="${2:-}"
    
    if [ -z "$title" ]; then
        print_error "Pull request title is required"
        print_info "Usage: $0 create-pr \"<title>\" \"[body]\""
        return 1
    fi

    check_gh_auth
    
    print_step "Creating pull request: $title"
    
    # Check if we're on a branch other than main/master
    current_branch=$(git branch --show-current)
    if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
        print_error "Cannot create PR from main/master branch"
        print_info "Create a feature branch first: git checkout -b feature/your-feature"
        return 1
    fi

    # Push current branch if it doesn't exist on remote
    if ! git ls-remote --exit-code --heads origin "$current_branch" &> /dev/null; then
        print_info "Pushing branch '$current_branch' to remote..."
        git push -u origin "$current_branch"
    fi

    local pr_args=("--title" "$title")
    if [ -n "$body" ]; then
        pr_args+=("--body" "$body")
    fi

    if gh pr create "${pr_args[@]}"; then
        print_success "Pull request created successfully"
        gh pr view --web
    else
        print_error "Failed to create pull request"
        return 1
    fi
}

# Command: List pull requests
cmd_list_prs() {
    check_gh_auth
    
    print_step "Listing open pull requests"
    
    if gh pr list; then
        print_success "Pull requests listed"
    else
        print_error "Failed to list pull requests"
        return 1
    fi
}

# Command: Merge pull request
cmd_merge_pr() {
    local pr_number="${1:-}"
    
    if [ -z "$pr_number" ]; then
        print_error "Pull request number is required"
        print_info "Usage: $0 merge-pr <pr-number>"
        print_info "Use '$0 list-prs' to see available PRs"
        return 1
    fi

    check_gh_auth
    
    print_step "Merging pull request #$pr_number"
    
    # Show PR details first
    print_info "Pull request details:"
    gh pr view "$pr_number"
    
    echo ""
    read -p "Merge this pull request? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if gh pr merge "$pr_number" --squash --delete-branch; then
            print_success "Pull request #$pr_number merged successfully"
        else
            print_error "Failed to merge pull request"
            return 1
        fi
    else
        print_info "Merge cancelled"
    fi
}

# Command: Create release
cmd_create_release() {
    local tag="${1:-}"
    local title="${2:-}"
    
    if [ -z "$tag" ]; then
        print_error "Release tag is required"
        print_info "Usage: $0 create-release <tag> \"[title]\""
        print_info "Example: $0 create-release v1.0.0 \"First stable release\""
        return 1
    fi

    check_gh_auth
    
    print_step "Creating release: $tag"
    
    # Validate tag format (should start with 'v' for version tags)
    if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
        print_warning "Tag '$tag' doesn't follow semantic versioning (vX.Y.Z)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Release creation cancelled"
            return 0
        fi
    fi

    local release_args=("$tag")
    if [ -n "$title" ]; then
        release_args+=("--title" "$title")
    fi

    # Generate release notes automatically
    release_args+=("--generate-notes")

    if gh release create "${release_args[@]}"; then
        print_success "Release '$tag' created successfully"
        print_info "This will trigger the publish workflow if configured"
        gh release view "$tag" --web
    else
        print_error "Failed to create release"
        return 1
    fi
}

# Command: List releases
cmd_list_releases() {
    check_gh_auth
    
    print_step "Listing releases"
    
    if gh release list; then
        print_success "Releases listed"
    else
        print_error "Failed to list releases"
        return 1
    fi
}

# Command: Show workflow status
cmd_workflow_status() {
    check_gh_auth
    
    print_step "GitHub Actions workflow status"
    
    if gh run list --limit 10; then
        print_success "Workflow runs listed"
    else
        print_error "Failed to get workflow status"
        return 1
    fi
}

# Command: Run workflow
cmd_run_workflow() {
    local workflow="${1:-ci.yml}"
    
    check_gh_auth
    
    print_step "Triggering workflow: $workflow"
    
    if gh workflow run "$workflow"; then
        print_success "Workflow '$workflow' triggered successfully"
        print_info "Check status with: $0 workflow-status"
    else
        print_error "Failed to trigger workflow"
        print_info "Available workflows:"
        gh workflow list
        return 1
    fi
}

# Main command dispatcher
main() {
    local command="${1:-}"
    
    if [ -z "$command" ]; then
        show_usage
        exit 0
    fi

    case "$command" in
        "auth-status")
            cmd_auth_status
            ;;
        "auth-login")
            cmd_auth_login
            ;;
        "create-repo")
            cmd_create_repo "${2:-}"
            ;;
        "repo-info")
            cmd_repo_info
            ;;
        "create-pr")
            cmd_create_pr "${2:-}" "${3:-}"
            ;;
        "list-prs")
            cmd_list_prs
            ;;
        "merge-pr")
            cmd_merge_pr "${2:-}"
            ;;
        "create-release")
            cmd_create_release "${2:-}" "${3:-}"
            ;;
        "list-releases")
            cmd_list_releases
            ;;
        "workflow-status")
            cmd_workflow_status
            ;;
        "run-workflow")
            cmd_run_workflow "${2:-}"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
# Git Guide for DasTern Project

This guide covers Git basics and the Git Flow workflow used in the DasTern project.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Git Flow Workflow](#git-flow-workflow)
3. [Basic Commands](#basic-commands)
4. [Branching Strategy](#branching-strategy)
5. [Working with Remote](#working-with-remote)
6. [Merging & Pull Requests](#merging--pull-requests)
7. [Handling Conflicts](#handling-conflicts)
8. [Common Scenarios](#common-scenarios)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Configure Git (First Time)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

### Clone the Repository
```bash
git clone https://github.com/your-org/DasTern.git
cd DasTern
```

---

## Git Flow Workflow

DasTern uses **Git Flow**, a structured branching model:

```
main (Production)
  ↑
  └── merge develop (only when ready for release)
  
develop (Integration/Staging)
  ↑
  └── all team members merge here
  
feature/feature-name (Your work)
  └── work on this, then merge to develop
```

### Branch Hierarchy

| Branch | Purpose | Protected |
|--------|---------|-----------|
| `main` | Production-ready code | ✅ Yes |
| `develop` | Integration branch for team | ✅ Yes |
| `feature/*` | Individual feature branches | ❌ No |

---

## Basic Commands

### Status & Information
```bash
# Check current branch and changes
git status

# View all branches (local and remote)
git branch -a

# Show commit history
git log --oneline -10

# Show changes in current branch
git diff

# Show who changed what
git blame filename.py
```

### Viewing Commits
```bash
# Pretty log with branch visualization
git log --oneline --graph --all --decorate

# See commits from specific author
git log --author="Your Name"

# See commits from last 7 days
git log --since="7 days ago"
```

### Creating & Switching Branches
```bash
# Create a new branch
git branch feature/new-feature

# Switch to a branch
git checkout feature/new-feature

# Create and switch in one command
git checkout -b feature/new-feature

# Delete local branch
git branch -d feature/old-feature

# Force delete local branch
git branch -D feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature
```

### Staging & Committing
```bash
# Stage specific file
git add filename.py

# Stage all changes
git add .

# Stage with interactive selection
git add -p

# Commit with message
git commit -m "Add feature description"

# Commit with detailed message (opens editor)
git commit

# Amend last commit
git commit --amend --no-edit

# Amend last commit and change message
git commit --amend -m "New message"
```

---

## Branching Strategy

### For Feature Development

**Step 1: Create feature branch from develop**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication
```

**Step 2: Work on your feature**
```bash
# Make changes
git add .
git commit -m "Add login functionality"
```

**Step 3: Push to remote**
```bash
git push origin feature/user-authentication
```

**Step 4: Create Pull Request (PR)**
- Go to GitHub/GitLab
- Create PR from `feature/user-authentication` → `develop`
- Add description of changes
- Request code review

**Step 5: After approval, merge via UI**
- GitHub/GitLab handles the merge
- Delete the branch after merging

### Branch Naming Conventions

Use clear, descriptive names:

```bash
# Feature branches
feature/user-authentication
feature/payment-integration
feature/profile-update

# Bug fixes
bugfix/login-error
bugfix/null-pointer-exception

# Hotfixes (emergency fixes for main)
hotfix/security-patch
hotfix/critical-bug

# Documentation
docs/api-documentation
docs/setup-guide
```

---

## Working with Remote

### Fetching & Pulling
```bash
# Fetch changes from remote (doesn't merge)
git fetch origin

# Pull changes and merge (fetch + merge)
git pull origin develop

# Pull with rebase instead of merge
git pull --rebase origin develop
```

### Pushing
```bash
# Push current branch to remote
git push origin feature/my-feature

# Push all branches
git push origin --all

# Push and set upstream (first push)
git push -u origin feature/my-feature

# Push tags
git push origin v1.0.0

# Force push (⚠️ use cautiously!)
git push --force origin feature/my-feature
```

### Tracking Remote Branches
```bash
# See which local branches track remotes
git branch -vv

# Set tracking for existing branch
git branch -u origin/develop develop

# Automatically track remote when pulling
git checkout --track origin/feature/new-feature
```

---

## Merging & Pull Requests

### Pull Request Workflow (Recommended)

**For Team Collaboration:**

1. **Create feature branch and push**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

2. **Open Pull Request on GitHub/GitLab**
   - Go to repository
   - Click "New Pull Request"
   - Select: `feature/new-feature` → `develop`
   - Add title and description
   - Request reviewers

3. **Address review comments**
   ```bash
   # Make requested changes
   git add .
   git commit -m "Address review comments"
   git push origin feature/new-feature  # PR updates automatically
   ```

4. **Merge via GitHub/GitLab UI**
   - Click "Merge" after approval
   - Delete branch after merging

### Direct Merge (If No Code Review Needed)

```bash
# Switch to develop
git checkout develop

# Update develop with latest changes
git pull origin develop

# Merge your feature
git merge feature/my-feature

# Push the merge
git push origin develop

# Delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

### Release to Main

**Only merge develop → main when ready for production:**

```bash
# Switch to main
git checkout main

# Ensure main is up to date
git pull origin main

# Merge develop
git merge develop

# Push to main
git push origin main

# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## Handling Conflicts

### Understanding Conflicts

Conflicts occur when the same lines are modified in different ways:

```
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> branch-name
```

### Resolving Conflicts

**Step 1: Identify conflicts**
```bash
git status
```

**Step 2: Manually edit files**
- Open conflicted files
- Remove conflict markers
- Choose which changes to keep
- Edit to create final version

**Step 3: Mark as resolved**
```bash
git add resolved-file.py
```

**Step 4: Complete the merge**
```bash
git commit -m "Resolve merge conflicts"
```

### Aborting a Merge

If merge goes wrong:
```bash
git merge --abort
```

### Using Merge Tools

For visual conflict resolution:
```bash
git mergetool
```

---

## Common Scenarios

### Scenario 1: Sync Your Branch with Latest Develop

```bash
git checkout rayu
git fetch origin
git merge origin/develop
# or rebase (linear history)
git rebase origin/develop
```

### Scenario 2: Undo Last Commit (Not Pushed)

```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

### Scenario 3: Undo Pushed Commit

```bash
# Create new commit that reverses changes
git revert HEAD

# Push the revert
git push origin develop
```

### Scenario 4: Stash Work in Progress

```bash
# Save work without committing
git stash

# List stashed changes
git stash list

# Apply stashed changes
git stash apply

# Apply and remove stash
git stash pop

# Remove specific stash
git stash drop stash@{0}
```

### Scenario 5: Cherry-pick Specific Commits

```bash
# Apply commit from another branch
git cherry-pick abc123def

# Cherry-pick multiple commits
git cherry-pick abc123def..xyz789abc
```

### Scenario 6: View Unpushed Commits

```bash
# See commits in your branch not in develop
git log origin/develop..HEAD

# See commits in develop not in your branch
git log HEAD..origin/develop
```

---

## Best Practices

### ✅ Do

- **Pull before push**: Always `git pull` before `git push`
  ```bash
  git pull origin develop
  git push origin develop
  ```

- **Commit frequently**: Smaller, logical commits are better
  ```bash
  git commit -m "Fix: Resolve null pointer in auth service"
  ```

- **Write meaningful commit messages**: Describe WHAT and WHY
  ```bash
  # Good
  git commit -m "Add JWT token validation for API security"
  
  # Bad
  git commit -m "fix"
  ```

- **Use branches for features**: Never work directly on main/develop
  ```bash
  git checkout -b feature/my-feature
  ```

- **Review before merging**: Use pull requests for code review
  
- **Keep branches up to date**: Regularly merge/rebase with develop
  ```bash
  git pull origin develop
  ```

- **Tag releases**: Mark production releases
  ```bash
  git tag -a v1.0.0 -m "Production release"
  ```

### ❌ Don't

- **Don't force push to main or develop**
  ```bash
  # Avoid this on shared branches
  git push --force origin develop
  ```

- **Don't commit sensitive data** (passwords, API keys)
  - Use `.gitignore`
  - Use environment variables

- **Don't have large commits mixing unrelated changes**
  - Commit related changes together

- **Don't merge without reviewing**
  - Always request code review via PR

- **Don't rewrite history on shared branches**
  - Use `rebase` only on personal branches

---

## Troubleshooting

### Problem: "Permission denied" when pushing

**Solution:**
```bash
# Verify SSH key
ssh -T git@github.com

# If no SSH key, use HTTPS or generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
```

### Problem: Merge conflicts

**Solution:**
```bash
# See conflict markers
git diff

# Manually resolve files
# Then mark as resolved
git add .
git commit -m "Resolve conflicts"
```

### Problem: Accidentally committed to wrong branch

**Solution:**
```bash
# Get the commit hash
git log

# Revert the commit
git revert abc123def
git push origin branch-name

# Or reset if not pushed
git reset --soft HEAD~1
git checkout -b correct-branch
git commit -m "message"
```

### Problem: Need to undo a pushed commit

**Solution:**
```bash
# Create a revert commit
git revert abc123def
git push origin develop

# ⚠️ Don't use force push on shared branches
```

### Problem: Lost commits - can't find them

**Solution:**
```bash
# See all commit history including deleted
git reflog

# Recover a commit
git checkout abc123def
# Create a branch to save it
git checkout -b recovered-branch
```

### Problem: File tracked but shouldn't be

**Solution:**
```bash
# Remove from Git but keep in filesystem
git rm --cached filename

# Add to .gitignore
echo "filename" >> .gitignore

# Commit
git commit -m "Remove tracked file"
```

### Problem: Large file causes push to fail

**Solution:**
```bash
# Check file size
du -h large-file

# Remove large file
git rm large-file
git commit -m "Remove large file"

# Use Git LFS for large files
git lfs install
git lfs track "*.psd"
git add .gitattributes
git add large-file
git commit -m "Add large file with LFS"
```

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Check status | `git status` |
| View branches | `git branch -a` |
| Create branch | `git checkout -b feature/name` |
| Switch branch | `git checkout develop` |
| Add changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin branch-name` |
| Pull | `git pull origin branch-name` |
| Merge | `git merge feature/name` |
| View history | `git log --oneline -10` |
| Undo commit | `git reset --soft HEAD~1` |
| Stash changes | `git stash` |
| Apply stash | `git stash apply` |
| Delete branch | `git branch -d feature/name` |
| Tag release | `git tag -a v1.0.0 -m "msg"` |

---

## Resources

- [Git Official Documentation](https://git-scm.com/doc)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Git Flow Cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)
- [Interactive Git Learning](https://learngitbranching.js.org/)

---

## Questions or Issues?

If you encounter problems:
1. Check this guide
2. Search GitHub/GitLab issues
3. Ask the team in Discord/Slack
4. Check the `git log` for history

Happy coding! 🚀

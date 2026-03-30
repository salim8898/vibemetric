# Branch Protection Setup Guide

After pushing the code to GitHub, configure branch protection rules to enforce PR-based workflow.

## Steps to Configure

1. Go to your repository: https://github.com/salim8898/vibemetric
2. Click **Settings** → **Branches** → **Add branch protection rule**
3. Configure the following settings:

### Branch Name Pattern
```
main
```

### Protection Rules

#### Require Pull Request Reviews
- ✅ **Require a pull request before merging**
  - Required approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (optional, if you add CODEOWNERS file)

#### Require Status Checks
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - **Required checks:**
    - `test (3.9)` - Python 3.9 tests
    - `test (3.10)` - Python 3.10 tests
    - `test (3.11)` - Python 3.11 tests
    - `test (3.12)` - Python 3.12 tests
    - `lint` - Code quality checks

#### Additional Settings
- ✅ **Require conversation resolution before merging**
- ✅ **Require linear history** (optional - enforces rebase/squash)
- ✅ **Do not allow bypassing the above settings** (even for admins)
- ⚠️ **Allow force pushes** - DISABLED
- ⚠️ **Allow deletions** - DISABLED

### For Repository Admins
- ✅ **Include administrators** - Apply rules to admins too (recommended)

## Workflow After Setup

### For Contributors
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and commit
4. Push to your fork: `git push origin feature/my-feature`
5. Open a Pull Request to `main`
6. Wait for CI checks to pass
7. Request review from maintainers
8. Address review feedback
9. Maintainer merges after approval

### For Maintainers (You)
1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit
3. Push branch: `git push origin feature/my-feature`
4. Open a Pull Request
5. Wait for CI checks to pass
6. Merge your own PR (or get review from trusted contributor)

## Alternative: Rulesets (New GitHub Feature)

GitHub now offers "Rulesets" as a more flexible alternative to branch protection:

1. Go to **Settings** → **Rules** → **Rulesets** → **New ruleset**
2. Choose **Branch ruleset**
3. Configure similar rules with more granular control

## Testing the Setup

After configuration:
1. Try to push directly to main: `git push origin main`
   - Should be **blocked** ✅
2. Create a PR with failing tests
   - Should be **blocked from merging** ✅
3. Create a PR with passing tests
   - Should be **mergeable after review** ✅

## Notes

- First push to `main` will be allowed (to initialize the repo)
- After that, all changes must go through PRs
- CI runs automatically on every PR
- You can temporarily disable protection if needed for emergency fixes

# Git Workflow & Commit Strategy

## Overview

This project follows **Git Flow with Conventional Commits** for professional collaboration and automated changelog generation.

---

## Branch Strategy

### Main Branches

**`main`** — Production-ready code
- Reflects the latest release state
- All merges must come through Pull Requests with code review
- Requires all tests to pass before merge

**`master`** — Legacy branch (from initial setup)
- Will be deprecated; use `main` for all new work

### Task Branches

Task-based feature branches created for each major work item:

| Branch | Task | Commits | Status |
|--------|------|---------|--------|
| `task/1-data-analysis-preprocessing` | Data cleaning, EDA, geolocation, feature engineering, imbalance handling | 5 | ✅ Complete |
| `task/2-model-building-training` | Data prep, baseline, ensemble, comparison, artifacts | 5 | ✅ Complete |
| `task/3-model-explainability` | SHAP analysis, summary plot, force plots, interpretation, recommendations | 5 | ✅ Complete |

---

## Commit Message Format

All commits follow **Conventional Commits** specification for clarity and automated tooling support.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **`feat`** — New feature (triggers minor version bump)
- **`fix`** — Bug fix (triggers patch version bump)
- **`docs`** — Documentation changes only
- **`style`** — Code style changes (formatting, whitespace, semicolons)
- **`refactor`** — Code refactoring without feature changes
- **`perf`** — Performance improvements
- **`test`** — Test additions or updates
- **`chore`** — Build, dependency, or tooling changes

### Scope

The area of the codebase affected:
- `data-preprocessing` — Data cleaning and transformation
- `eda` — Exploratory data analysis
- `geolocation` — IP-to-country enrichment
- `feature-engineering` — Feature creation
- `modeling` — Model training and evaluation
- `shap` — SHAP-based explainability
- `docs` — Documentation updates

### Subject

- Imperative mood ("add" not "added" or "adds")
- No period at the end
- Under 50 characters
- Clear and descriptive

### Body (Optional)

- Explain what and why, not how
- Wrap at 72 characters
- Separated from subject by blank line

### Footer (Optional)

- Reference issues or breaking changes
- Example: `Closes #123` or `Fixes #456`

---

## Commit History

### Task 1: Data Analysis & Preprocessing (5 commits)

```
0037a2c feat(data-preprocessing): implement comprehensive data cleaning pipeline
9605393 feat(eda): add exploratory data analysis notebooks
ffbb7ad feat(geolocation): implement IP-to-country enrichment pipeline
9318a36 feat(feature-engineering): create temporal and behavioral features
32073e6 feat(imbalance-handling): implement SMOTE resampling with validation
```

**What's Included:**
- StandardScaler normalization and one-hot encoding
- 50+ EDA visualizations with class imbalance analysis
- IP-to-integer conversion and pd.merge_asof range lookup
- Temporal (hour_of_day, day_of_week) and behavioral features
- SMOTE resampling with validation and no data leakage

---

### Task 2: Model Building & Training (5 commits)

```
27dadca feat(modeling): implement stratified train-test split pipeline
045dea8 feat(baseline-model): train and evaluate Logistic Regression
7c71430 feat(ensemble-model): train XGBoost with hyperparameter tuning
5f3491f feat(model-comparison): create comprehensive metrics comparison
d711ae1 feat(model-artifacts): save trained models for deployment
```

**What's Included:**
- Stratified 80/20 train-test split preserving class distribution
- Logistic Regression baseline with AUC-PR, F1, ROC-AUC metrics
- XGBoost ensemble with grid search hyperparameter tuning
- Comprehensive metrics comparison table
- Serialized model artifacts for inference

---

### Task 3: Model Explainability (5 commits)

```
ea38934 feat(shap-analysis): implement SHAP-based feature importance
95ad016 feat(shap-visualization): create global SHAP summary plot
97d4fd3 feat(shap-force-plots): generate force plots for key predictions
e531c13 feat(fraud-drivers): identify and document top fraud prediction signals
c8d7db6 feat(business-recommendations): translate SHAP insights to actionable strategies
```

**What's Included:**
- SHAP value computation and feature importance ranking
- Global SHAP summary plot visualization
- Individual force plots (TP, FP, FN cases)
- Top 5 fraud driver analysis
- 4 business recommendations with impact quantification

---

## Pull Request Workflow

### Creating a PR

1. **Push your task branch:**
   ```bash
   git push origin task/your-task-name
   ```

2. **Create PR on GitHub:**
   - Title: Follow conventional commit format
   - Description: Include what, why, and testing done
   - Link to issue: Use `Closes #123` in description

3. **Example PR Description:**
   ```markdown
   # Description
   Implements comprehensive SHAP-based explainability for fraud detection model.
   
   ## Related Issue
   Closes #12
   
   ## What Changed
   - Added SHAP summary plot (global feature importance)
   - Generated force plots for 3+ prediction cases (TP, FP, FN)
   - Identified top 5 fraud drivers
   - Created 4 actionable business recommendations
   
   ## Testing
   - [x] Code runs without errors
   - [x] SHAP plots generated successfully
   - [x] Force plots match documentation
   - [x] Recommendations grounded in data
   
   ## Checklist
   - [x] Code follows style guide
   - [x] Comments added for complex logic
   - [x] Documentation updated
   - [x] Tests added/updated (if applicable)
   ```

### Review & Merge

1. **Code Review:** At least one approval required
2. **Status Checks:** All CI/CD tests must pass
3. **Merge:** Use "Squash and merge" or "Create a merge commit" (not "Rebase")
4. **Delete Branch:** After merge, delete the task branch to keep repo clean

---

## Command Reference

### Creating & Switching Branches

```bash
# Create and checkout new branch
git checkout -b task/new-feature

# Switch to existing branch
git checkout main
git checkout task/1-data-analysis-preprocessing

# List all branches
git branch -a
```

### Committing with Conventional Format

```bash
# Simple commit
git commit -m "feat(data-preprocessing): add missing value handling"

# Detailed commit with body
git commit -m "feat(modeling): train XGBoost with hyperparameter tuning

- Implement grid search over n_estimators and max_depth
- Apply 5-fold cross-validation
- Save best model with joblib
- Document tuning results"
```

### Pushing to Remote

```bash
# Push current branch
git push origin task/1-data-analysis-preprocessing

# Push all branches
git push --all

# Force push (use with caution)
git push --force-with-lease origin main
```

### Viewing Commit History

```bash
# Simple log
git log --oneline

# Detailed log with branches
git log --all --graph --oneline --decorate

# Commits on specific branch
git log origin/task/1-data-analysis-preprocessing --oneline

# Commits since last tag
git log v1.0.0..HEAD --oneline
```

### Syncing with Remote

```bash
# Fetch latest from remote
git fetch origin

# Pull latest changes
git pull origin main

# Rebase on latest main
git rebase origin/main
```

---

## Best Practices

### DO

✅ **Write meaningful commit messages** — Future you and your team will thank you  
✅ **Make small, focused commits** — Easier to review and revert if needed  
✅ **Commit frequently** — Capture progress and reasoning  
✅ **Use task branches** — Keep work organized by feature/task  
✅ **Review before pushing** — Use `git diff` to check changes  
✅ **Use Pull Requests** — Enable code review and discussion  
✅ **Squash WIP commits** — Clean history before merging  

### DON'T

❌ **Don't commit secrets** — Use `.gitignore` for API keys, credentials  
❌ **Don't force-push to main** — Risk losing history  
❌ **Don't mix multiple features** — One feature per branch  
❌ **Don't forget to pull** — Avoid merge conflicts  
❌ **Don't write vague messages** — "fixed stuff" doesn't explain anything  
❌ **Don't skip testing** — Ensure code works before committing  

---

## CI/CD Integration

### GitHub Actions Workflow

All merges to `main` trigger the `.github/workflows/unittests.yml` workflow:

```yaml
name: Unit Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
```

**Status Requirements:**
- ✅ All tests must pass
- ✅ No linting errors
- ✅ Code coverage maintained

---

## Versioning Strategy

When releasing major milestones:

```bash
# Tag a release
git tag -a v1.0.0 -m "Release 1.0: Initial fraud detection system"

# Push tags to remote
git push origin v1.0.0

# View all tags
git tag -l
```

**Version Format:** `v<major>.<minor>.<patch>`
- `v1.0.0` — Major: Production-ready fraud detection
- `v1.1.0` — Minor: New feature or dataset support
- `v1.0.1` — Patch: Bug fixes or documentation updates

---

## Troubleshooting

### Accidentally committed to main?

```bash
# Move last commit to new branch
git branch feature/new-feature
git reset --hard origin/main
git checkout feature/new-feature
```

### Need to undo a commit?

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### Merge conflicts?

```bash
# View conflicts
git status

# Resolve conflicts in editor, then:
git add .
git commit -m "chore: resolve merge conflicts"
git push
```

### Rebase onto main?

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease origin task/your-branch
```

---

## Summary

| Category | Standard |
|----------|----------|
| **Commit Type** | Conventional Commits (feat, fix, docs, etc.) |
| **Scope** | Feature area (data-preprocessing, modeling, shap) |
| **Branch Pattern** | `task/<number>-<description>` |
| **Merge Strategy** | Pull Request with code review |
| **History Style** | Linear, readable commit graph |
| **Automation** | GitHub Actions CI/CD on all PRs |

This workflow ensures a clean, professional repository that's easy to navigate, maintain, and collaborate on.

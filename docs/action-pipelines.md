# GitHub Actions Pipelines

Symposion uses GitHub Actions to automate testing, quality checks, and documentation deployment. These workflows ensure code quality and keep documentation up-to-date on every push.

---

## Overview

Two main workflows handle continuous integration and deployment:

1. **pytest** — Automated testing on multiple Python versions
2. **pages** — Documentation deployment to GitHub Pages

---

## Workflow Locations

All workflows are stored in `.github/workflows/`:

```
.github/
└── workflows/
    ├── pytest.yml      # Testing pipeline
    └── pages.yml       # Documentation deployment
```

---

## Pytest Workflow

**File:** [.github/workflows/pytest.yml](.github/workflows/pytest.yml)

### Purpose
Automatically run tests on every push and pull request to ensure code quality across supported Python versions.

### Triggers

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

- Runs on **push** to `main` or `develop`
- Runs on **pull request** to `main` or `develop`
- Can be triggered manually via workflow_dispatch

### Test Matrix

Tests run on multiple Python versions to ensure compatibility:

| Python Version | Status |
|---|---|
| 3.9 | ✅ Tested |
| 3.10 | ✅ Tested |
| 3.11 | ✅ Tested |
| 3.12 | ✅ Tested |
| 3.13 | ✅ Tested (main) |

### Workflow Steps

1. **Checkout Code**
   ```
   Fetch the repository
   ```

2. **Setup Python**
   ```
   Install Python ${{ matrix.python-version }}
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -e .          # Install symposion package
   pip install pytest        # Install test runner
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v --tb=short
   ```
   - Verbose output (`-v`)
   - Short traceback format (`--tb=short`)
   - Runs all tests in `tests/` directory

5. **Coverage Report** (Python 3.13 only)
   ```bash
   pip install pytest-cov
   pytest tests/ --cov=symposion --cov-report=xml
   ```
   - Generates code coverage on the latest Python version
   - XML report for CI analysis

### Viewing Test Results

After a workflow runs:

1. Go to **Actions** tab on GitHub
2. Click the workflow run
3. View logs for each step
4. Check for failures and error messages

**Red ❌** = Test failed, check logs  
**Green ✅** = All tests passed

---

## Pages Workflow

**File:** [.github/workflows/pages.yml](.github/workflows/pages.yml)

### Purpose
Automatically build and deploy documentation to GitHub Pages on every push to `main`.

### Triggers

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

- Runs on **push** to `main` branch
- Can be triggered manually

### Workflow Steps

1. **Checkout Code**
   ```
   Fetch the repository
   ```

2. **Setup Pages**
   ```
   Configure GitHub Pages environment
   ```

3. **Build with Jekyll**
   ```
   Source: ./docs
   Destination: ./_site
   ```
   - Reads Markdown files from `docs/`
   - Builds static HTML site
   - Uses Jekyll theme from `docs/_config.yml`

4. **Upload Artifact**
   ```
   Upload built site to GitHub Pages
   ```

5. **Deploy**
   ```
   Deploy artifact and publish live
   ```

### Documentation Source

All documentation lives in `docs/`:

```
docs/
├── _config.yml                 # Jekyll configuration
├── index.md                    # Homepage
├── architecture.md             # System design
├── intent-taxonomy.md          # Message intents
├── action-pipelines.md         # This file
├── PLAN.md                     # Development plan
├── roadmap.md                  # Future roadmap
├── agents/                     # Individual agent docs
│   ├── athen.md
│   ├── clio.md
│   ├── daed.md
│   ├── heph.md
│   ├── herm.md
│   ├── met.md
│   └── nem.md
└── assets/                     # Images and resources
```

### Setting Up GitHub Pages

To enable deployment:

1. **Repository Settings** → **Pages**
2. Set **Source** to `Deploy from a branch`
3. Set **Branch** to `main`
4. Set **Folder** to `/ (root)`
5. Save

The Pages workflow will then deploy to `https://<username>.github.io/Symposion/`

### Viewing Deployed Docs

After a successful Pages deployment:

1. Go to **Actions** tab
2. Click the `Deploy GitHub Pages` run
3. Click the deployment link in the job summary
4. Or visit: `https://<username>.github.io/Symposion/`

---

## Monitoring Workflows

### Status Badge

Add a badge to your README to show workflow status:

```markdown
[![Pytest](https://github.com/<username>/Symposion/actions/workflows/pytest.yml/badge.svg)](https://github.com/<username>/Symposion/actions/workflows/pytest.yml)

[![Pages](https://github.com/<username>/Symposion/actions/workflows/pages.yml/badge.svg)](https://github.com/<username>/Symposion/actions/workflows/pages.yml)
```

### Notifications

- **Push failures** → GitHub email notification
- **PR failures** → Comment on pull request
- **Manual check** → Go to Actions tab

---

## Troubleshooting

### Tests Failing

1. Check workflow logs for error messages
2. Run tests locally:
   ```bash
   pip install -e .
   pytest tests/ -v
   ```
3. Fix issues and push again

### Pages Not Updating

1. Verify `.github/workflows/pages.yml` exists
2. Check Pages settings point to `main` branch
3. Ensure `docs/` folder exists
4. Check for Jekyll build errors in workflow logs

### Slow Tests

- Tests running on 5 Python versions takes ~2-3 minutes
- Consider reducing to 3.10, 3.12, 3.13 for faster feedback
- Edit `pytest.yml` matrix section to adjust

---

## Customizing Workflows

### Add a New Workflow

1. Create `.github/workflows/my-workflow.yml`
2. Define triggers (`on:`)
3. Define jobs (`jobs:`)
4. Commit and push
5. GitHub auto-detects and runs it

### Modify Python Versions

Edit `pytest.yml`:

```yaml
matrix:
  python-version: ['3.10', '3.12', '3.13']  # Only test these
```

### Add Linting or Type Checking

Extend `pytest.yml` with additional steps:

```yaml
- name: Run Pylint
  run: |
    pip install pylint
    pylint symposion/
```

---

## See Also

- **Parent:** [Architecture](./architecture.md)
- **Sibling:** [Intent Taxonomy](./intent-taxonomy.md)
- **External:** [GitHub Actions Documentation](https://docs.github.com/en/actions)


# PyPI Publishing Setup

This document explains how to set up PyPI publishing for this repository.

## Prerequisites

1. A PyPI account (create one at https://pypi.org/account/register/)
2. Repository admin access to configure secrets

## Setup Steps

### 1. Create a PyPI API Token

1. Log in to PyPI at https://pypi.org
2. Go to your account settings: https://pypi.org/manage/account/
3. Scroll down to "API tokens" section
4. Click "Add API token"
5. Give it a descriptive name (e.g., "replaykit-github-actions")
6. Set the scope to "Entire account" (or specific to the `replaykit` project once it's created)
7. Click "Add token"
8. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

### 2. Add the Secret to GitHub

1. Go to your repository: https://github.com/zkhan93/replaykit
2. Click on "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Name: `PYPI_API_TOKEN`
6. Value: Paste the API token you copied from PyPI (including the `pypi-` prefix)
7. Click "Add secret"

## Publishing a Release

The workflow is configured to automatically publish to PyPI when you push a version tag:

```bash
# Update version in pyproject.toml first
# Then create and push a tag
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Action will:
1. ✅ Run ruff linting and formatting checks
2. ✅ Build the package
3. ✅ Publish to PyPI automatically

## Workflow Details

- **Linting**: Runs on every push and PR to `main`
- **Building**: Runs after successful linting
- **Publishing**: Only runs when a tag starting with `v` is pushed (e.g., `v0.1.0`, `v1.2.3`)

## Testing the Workflow

Before creating a real release, you can:

1. Push to `main` branch - this will run linting and build (but not publish)
2. Create a pull request - this will run linting and build
3. Create a test tag - this will run the full workflow including publishing

## Troubleshooting

### "Invalid or non-existent authentication information"
- Check that the `PYPI_API_TOKEN` secret is set correctly
- Ensure the token hasn't expired
- Verify the token has the correct permissions

### "Project name already exists"
- If someone else has registered `replaykit` on PyPI, you'll need to choose a different name
- Update the `name` field in `pyproject.toml`
- Consider names like `replaykit-automation` or similar

### "Version already exists"
- You cannot republish the same version
- Increment the version number in `pyproject.toml`
- Create a new tag with the updated version


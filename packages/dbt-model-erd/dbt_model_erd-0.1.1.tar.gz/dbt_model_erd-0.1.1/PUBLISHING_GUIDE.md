# Publishing Guide for Maintainers

This guide is for **maintainers** publishing new versions of dbt-model-erd.

## Prerequisites

Publishing is automated via GitHub Actions. You just need to:
1. Update version numbers
2. Create a git tag
3. Create a GitHub release

The CI/CD pipeline handles the rest automatically.

---

## Release Process

### 1. Update Version Number

Update version in **two places**:

**`__init__.py`:**
```python
__version__ = "0.2.0"  # Update this
```

**`setup.py`:**
```python
setup(
    name="dbt-model-erd",
    version="0.2.0",  # Update this
    ...
)
```

### 2. Run Tests & Quality Checks

```bash
# Run all tests
make test

# Run linting
make lint

# Run formatting
make format

# Check coverage
make coverage
```

All checks must pass before releasing.

### 3. Update Documentation

- [ ] Update CHANGELOG.md (create if doesn't exist)
- [ ] Update README.md if needed
- [ ] Update examples/ if API changed

### 4. Commit and Tag

```bash
# Commit version changes
git add __init__.py setup.py
git commit -m "Bump version to 0.2.0"
git push origin main

# Create and push tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 5. Create GitHub Release

1. Go to: https://github.com/entechlog/dbt-erd/releases/new
2. Select tag: `v0.2.0`
3. Release title: `v0.2.0`
4. Description: See template below
5. Click "Publish release"

**GitHub Actions will automatically:**
- Build the package
- Run tests
- Publish to PyPI

### Release Description Template

```markdown
## What's Changed

### New Features
- Feature 1 description
- Feature 2 description

### Bug Fixes
- Fix 1 description
- Fix 2 description

### Documentation
- Doc update 1
- Doc update 2

### Breaking Changes (if any)
- Breaking change description

**Full Changelog**: https://github.com/entechlog/dbt-erd/compare/v0.1.0...v0.2.0
```

---

## Versioning Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **Patch (0.1.X)**: Bug fixes, minor changes
  - Example: 0.1.0 → 0.1.1

- **Minor (0.X.0)**: New features, backward compatible
  - Example: 0.1.0 → 0.2.0

- **Major (X.0.0)**: Breaking changes
  - Example: 0.9.0 → 1.0.0

---

## Verify Release

After release is published:

1. **Check PyPI**: https://pypi.org/project/dbt-erd/
2. **Test installation**:
   ```bash
   pip install --upgrade dbt-erd
   python -m dbt_erd --version
   ```
3. **Monitor GitHub Actions**: Ensure workflow completed successfully

---

## Hotfix Process

For urgent bug fixes:

```bash
# Create hotfix branch
git checkout -b hotfix/0.1.1

# Make fixes and test
# ... fix code ...
make test

# Update version to 0.1.1
# Commit, tag, and release as normal
git commit -m "Hotfix: critical bug"
git tag -a v0.1.1 -m "Hotfix release 0.1.1"
git push origin hotfix/0.1.1
git push origin v0.1.1

# Create release on GitHub
# Then merge back to main
```

---

## Rollback Process

If a release has critical issues:

1. **Remove PyPI release** (contact PyPI support if needed)
2. **Delete GitHub release and tag**:
   ```bash
   git tag -d v0.2.0
   git push origin :refs/tags/v0.2.0
   ```
3. **Release patched version** (e.g., v0.2.1)

---

## Troubleshooting

### "PyPI publish failed"
- Check GitHub Actions logs
- Verify PYPI_API_TOKEN secret is set correctly
- Ensure version number isn't already published

### "Tests failed in CI"
- Check which tests failed in GitHub Actions
- Run tests locally: `make test`
- Fix issues before releasing

### "Tag already exists"
- Delete and recreate tag:
  ```bash
  git tag -d v0.2.0
  git push origin :refs/tags/v0.2.0
  git tag -a v0.2.0 -m "Release version 0.2.0"
  git push origin v0.2.0
  ```

---

## Post-Release Checklist

- [ ] Verify package on PyPI
- [ ] Test installation: `pip install dbt-erd`
- [ ] Update project board/issues
- [ ] Announce on dbt Slack (#tools-and-integrations)
- [ ] Post on social media (LinkedIn, Twitter)
- [ ] Monitor for issues/bug reports

---

## Notes

- **First-time setup** (PyPI account, API tokens) is handled separately by project owner
- **Contributors** don't need PyPI access - just submit PRs
- **Automated publishing** is configured via `.github/workflows/publish.yml`
- **Manual publishing** should only be done if automation fails

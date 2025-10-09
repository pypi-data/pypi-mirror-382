# Quick Release Guide

## 🚀 How to Release a New Version

With the new dynamic versioning workflow, releasing is super simple!

---

## ✅ Simple 2-Step Process

### Step 1: Create and Push Tag
```bash
# Choose your version (following semantic versioning)
VERSION=0.1.1  # or 0.2.0, 1.0.0, etc.

# Create tag
git tag v$VERSION

# Push tag to trigger workflow
git push origin v$VERSION
```

### Step 2: Create GitHub Release
```bash
# Using GitHub CLI
gh release create v$VERSION \
  --title "v$VERSION - Short Description" \
  --notes "## Changes
- Fixed bug in message interceptor
- Improved performance
- Updated documentation"
```

**That's it!** 🎉

---

## 🤖 What Happens Automatically

The workflow will:

1. ✅ **Extract version** from tag (`v0.1.1` → `0.1.1`)
2. ✅ **Update pyproject.toml** with new version
3. ✅ **Build package** with correct version
4. ✅ **Verify** package filenames match version
5. ✅ **Publish to PyPI** as `observatory-mcp==0.1.1`
6. ✅ **Attach packages** to GitHub release

---

## 📋 Full Example

Let's release version `0.1.2`:

```bash
# 1. Create tag
git tag v0.1.2

# 2. Push tag
git push origin v0.1.2

# 3. Create release
gh release create v0.1.2 \
  --title "v0.1.2 - Performance Improvements" \
  --notes "## Improvements
- Optimized message processing (2x faster)
- Reduced memory usage by 30%
- Fixed edge case in privacy manager

## Bug Fixes
- Resolved issue with async event queue
- Fixed type annotation warnings

## Documentation
- Updated README with new examples
- Added troubleshooting guide"
```

### Monitor Progress:
```bash
# Watch workflow in real-time
gh run watch

# Or view in browser
gh run view --web
```

### Verify Publication:
```bash
# Check on PyPI (wait ~2 minutes)
pip index versions observatory-mcp

# Test installation
pip install observatory-mcp==0.1.2

# Verify version
python -c "import observatory_mcp; print(observatory_mcp.__version__)"
# Output: 0.1.2
```

---

## 📚 Semantic Versioning Guide

### Version Format: MAJOR.MINOR.PATCH

#### PATCH (0.1.0 → 0.1.1)
**Bug fixes and minor changes**
```bash
git tag v0.1.1
# Example: Fixed a bug, typo correction, small improvement
```

#### MINOR (0.1.1 → 0.2.0)
**New features (backward compatible)**
```bash
git tag v0.2.0
# Example: Added new feature, new API endpoint
```

#### MAJOR (0.2.0 → 1.0.0)
**Breaking changes**
```bash
git tag v1.0.0
# Example: Changed API, removed deprecated code, not backward compatible
```

---

## 🎯 Real-World Examples

### Example 1: Bug Fix Release
```bash
# Current version: 0.1.0
# Found a bug, need to release fix

git tag v0.1.1
git push origin v0.1.1

gh release create v0.1.1 \
  --title "v0.1.1 - Bug Fix" \
  --notes "Fixed message interceptor race condition"
```

### Example 2: Feature Release
```bash
# Current version: 0.1.1
# Added new sampling strategies

git tag v0.2.0
git push origin v0.2.0

gh release create v0.2.0 \
  --title "v0.2.0 - New Sampling Features" \
  --notes "## New Features
- Custom sampling strategies
- Adaptive sampling based on error rates
- Per-method sampling configuration"
```

### Example 3: Major Release
```bash
# Current version: 0.9.0
# Ready for 1.0!

git tag v1.0.0
git push origin v1.0.0

gh release create v1.0.0 \
  --title "v1.0.0 - Production Ready! 🎉" \
  --notes "## 🎉 First Stable Release!

This release marks the first production-ready version.

## What's New
- Stable API (no more breaking changes in 1.x)
- Complete documentation
- 90%+ test coverage
- Battle-tested in production

## Breaking Changes from 0.x
- Renamed \`wrap_server()\` to \`monitor()\`
- Changed config structure
- See migration guide for details"
```

---

## ⚠️ Important Notes

### 1. Version in pyproject.toml
**You don't need to update it manually!** The workflow does it automatically.

```toml
# In your repo, this might say:
version = "0.1.0"

# But when you release v0.1.2, the workflow:
# - Automatically updates it to "0.1.2"
# - Builds with version "0.1.2"
# - Publishes as "0.1.2"
```

### 2. Tag Format
**Must start with 'v'**
- ✅ `v0.1.1`
- ✅ `v1.0.0`
- ❌ `0.1.1` (missing 'v')
- ❌ `release-0.1.1` (wrong prefix)

### 3. Can't Re-publish Same Version
Once a version is on PyPI, you **cannot replace it**. If you need to fix something:
```bash
# Wrong: Try to re-release 0.1.1
git tag v0.1.1  # Won't work if already published

# Right: Bump to 0.1.2
git tag v0.1.2  # New version
```

---

## 🔍 Monitoring Releases

### Watch Workflow
```bash
# Real-time watch
gh run watch

# List recent runs
gh run list --limit 5

# View specific run
gh run view <run-id> --log
```

### Check PyPI
```bash
# List all versions
pip index versions observatory-mcp

# Check package page
open https://pypi.org/project/observatory-mcp/

# View download stats
open https://pypistats.org/packages/observatory-mcp
```

---

## 🆘 Troubleshooting

### Workflow Failed?
```bash
# View logs
gh run view --log

# Common issues:
# 1. Version already exists on PyPI
#    → Bump to next version

# 2. Tests failing
#    → Fix tests, commit, create new tag

# 3. Tag format wrong
#    → Delete tag, create correct format:
#      git tag -d v0.1.1
#      git push origin :refs/tags/v0.1.1
#      git tag v0.1.2
```

### Re-run Failed Workflow?
```bash
# After fixing the issue:
gh run rerun <run-id>

# Or create a new patch version:
git tag v0.1.2  # If v0.1.1 failed
```

---

## 📝 Pre-Release Checklist

Before creating a release:

- [ ] All tests passing locally
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)
- [ ] Version number decided (following semver)
- [ ] Release notes prepared

---

## 🎉 Summary

### Old Way (Manual):
```bash
1. Edit pyproject.toml
2. Commit changes
3. Push to GitHub
4. Create tag
5. Push tag
6. Create release
7. Wait for workflow
8. Check PyPI
```

### New Way (Automatic):
```bash
1. git tag v0.1.1 && git push origin v0.1.1
2. gh release create v0.1.1 --title "v0.1.1" --notes "Bug fixes"
3. ✅ Done! (Workflow handles the rest)
```

**60% fewer steps, fully automated, no manual version updates!** 🚀

---

## 💡 Pro Tips

### Tip 1: Use Release Templates
Create a template for release notes:
```bash
# Save as .github/RELEASE_TEMPLATE.md
gh release create v0.1.1 --notes-file .github/RELEASE_TEMPLATE.md
```

### Tip 2: Automate CHANGELOG
```bash
# Generate changelog from commits
git log v0.1.0..HEAD --oneline > CHANGES.txt
```

### Tip 3: Test First on Test PyPI
```bash
# Manual workflow trigger for test PyPI
gh workflow run publish.yml \
  --ref main \
  -f pypi-repo=testpypi
```

---

**Need help?** Check the workflow logs or create an issue on GitHub!

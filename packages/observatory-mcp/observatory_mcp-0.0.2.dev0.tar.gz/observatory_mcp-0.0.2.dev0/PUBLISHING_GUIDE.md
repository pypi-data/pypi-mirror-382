# PyPI Publishing Guide for observatory-mcp

## ⚠️ IMPORTANT: Your Workflow Won't Trigger Yet!

You pushed a **tag** (`v0.1.0`), but the workflow requires a **GitHub Release**. Just pushing a tag doesn't trigger the publish workflow!

---

## 🔍 Current Issue

### Your `publish.yml` triggers on:
```yaml
on:
  release:
    types: [published]  # ← Needs a GitHub Release, not just a tag!
```

### What you did:
```bash
git tag v0.1.0
git push origin v0.1.0  # ← This only pushes a tag
```

### What's missing:
You need to create a **GitHub Release** from that tag!

---

## ✅ Solution: Create a GitHub Release

### **Option 1: Using GitHub CLI (gh)** (Recommended)

```bash
# Create a release from the v0.1.0 tag
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "🎉 Initial release of Observatory MCP Python SDK

## Features
- 2-line integration for MCP servers
- Smart sampling and privacy controls
- Comprehensive analytics
- 82% test coverage
- Full type safety (mypy compliant)

## Installation
\`\`\`bash
pip install observatory-mcp
\`\`\`

See README.md for full documentation." \
  --repo amannhq/observatory-python-sdk

# This will:
# ✅ Create a GitHub Release
# ✅ Trigger the publish.yml workflow
# ✅ Build and publish to PyPI automatically
```

---

### **Option 2: Using GitHub Web UI**

1. Go to: `https://github.com/amannhq/observatory-python-sdk/releases/new`
2. Select tag: `v0.1.0` (from dropdown)
3. Release title: `v0.1.0 - Initial Release`
4. Description: (Add release notes)
5. Click **"Publish release"**

This will automatically trigger the workflow!

---

### **Option 3: Manual Publishing** (If you don't want GitHub Actions)

```bash
cd /Users/amannhq/Desktop/Me/observatory/sdk/python-sdk

# 1. Build the package
python -m build

# 2. Upload to PyPI (requires PyPI API token)
twine upload dist/*
# Enter your PyPI credentials when prompted
```

---

## 🔒 Required: PyPI Trusted Publishing Setup

Your workflow uses **trusted publishing** (no passwords needed!), but you need to configure it first.

### Steps to Enable Trusted Publishing:

#### 1. Go to PyPI
Visit: https://pypi.org/manage/account/publishing/

#### 2. Add a New Publisher
- **PyPI Project Name**: `observatory-mcp`
- **Owner**: `amannhq`
- **Repository**: `observatory-python-sdk`
- **Workflow**: `publish.yml`
- **Environment**: (leave blank)

#### 3. Save

Now GitHub Actions can publish without storing secrets! 🎉

---

## 📋 What Your Workflow Does

```yaml
# Triggers:
on:
  release:
    types: [published]  # ← Runs when you create a GitHub Release
  workflow_dispatch:     # ← Can also manually trigger

# Steps:
1. Checkout code
2. Setup Python 3.11
3. Install build tools (pip, build, twine)
4. Build package (python -m build)
5. Check package quality (twine check)
6. Publish to PyPI (using trusted publishing)
7. Attach dist files to GitHub Release
```

---

## 🚀 Complete Publishing Checklist

### Before Publishing:
- [x] All tests passing (61/61 ✓)
- [x] Code formatted (black ✓)
- [x] Linting clean (ruff ✓)
- [x] Type checking passing (mypy ✓)
- [x] Version bumped in `pyproject.toml` (0.1.0 ✓)
- [x] CHANGELOG updated
- [x] Tag created (`v0.1.0` ✓)
- [ ] **PyPI trusted publishing configured** ⚠️
- [ ] **GitHub Release created** ⚠️

### To Publish:
1. Configure PyPI trusted publishing (see above)
2. Create GitHub Release from `v0.1.0` tag
3. Wait for workflow to complete (~2-3 minutes)
4. Verify: `pip install observatory-mcp`

---

## 🔄 Check Workflow Status

### View Workflow Runs:
```bash
# Using gh CLI
gh run list --repo amannhq/observatory-python-sdk

# Or visit:
# https://github.com/amannhq/observatory-python-sdk/actions
```

### Watch Workflow in Real-time:
```bash
# After creating the release:
gh run watch --repo amannhq/observatory-python-sdk
```

---

## ⚙️ Alternative: Change Trigger to Tag Push

If you want the workflow to run on tag push (instead of releases), modify `publish.yml`:

```yaml
# Change this:
on:
  release:
    types: [published]

# To this:
on:
  push:
    tags:
      - 'v*.*.*'  # Triggers on v1.0.0, v0.1.0, etc.
```

But **GitHub Releases are recommended** because:
- ✅ Better for users (release notes, assets)
- ✅ More control (can draft before publishing)
- ✅ Shows up in "Releases" section
- ✅ Generates changelogs automatically

---

## 🔍 Verify Publication

After workflow completes:

```bash
# 1. Check PyPI (wait 1-2 minutes)
curl https://pypi.org/pypi/observatory-mcp/json | jq '.info.version'
# Should return: "0.1.0"

# 2. Try installing
python -m venv test_env
source test_env/bin/activate
pip install observatory-mcp

# 3. Verify import
python -c "import observatory_mcp; print(observatory_mcp.__version__)"
# Should print: 0.1.0
```

---

## 🆘 Troubleshooting

### Workflow doesn't run
- ❌ **Cause**: Just pushed a tag, not a release
- ✅ **Fix**: Create a GitHub Release from the tag

### Workflow fails with "403 Forbidden"
- ❌ **Cause**: Trusted publishing not configured
- ✅ **Fix**: Configure on PyPI (see above)

### Package name already taken
- ❌ **Cause**: Someone else owns `observatory-mcp`
- ✅ **Fix**: Choose a different name (e.g., `observatory-mcp-client`)

### Can't create release
- ❌ **Cause**: Tag doesn't exist on remote
- ✅ **Fix**: `git push origin v0.1.0`

---

## 📊 Expected Timeline

After creating GitHub Release:

```
0:00  - Release created → Workflow triggered
0:30  - Tests running
1:00  - Building package
1:30  - Publishing to PyPI
2:00  - ✅ Package available on PyPI
2:30  - pip install works
```

---

## 🎯 Quick Commands

### Create Release (Recommended)
```bash
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "Initial release of Observatory MCP SDK" \
  --repo amannhq/observatory-python-sdk
```

### Watch Workflow
```bash
gh run watch --repo amannhq/observatory-python-sdk
```

### Verify Publication
```bash
pip install observatory-mcp
python -c "import observatory_mcp; print(observatory_mcp.__version__)"
```

---

## 📝 Summary

**Current Status:**
- ✅ Tag pushed: `v0.1.0`
- ❌ Release created: **NO** ← This is why workflow didn't run
- ❌ Published to PyPI: **NO**

**Next Steps:**
1. Configure PyPI trusted publishing
2. Create GitHub Release from `v0.1.0` tag
3. Wait for workflow to complete
4. Verify with `pip install observatory-mcp`

**Quick Fix:**
```bash
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release"
```

This will trigger the workflow and publish to PyPI automatically! 🚀

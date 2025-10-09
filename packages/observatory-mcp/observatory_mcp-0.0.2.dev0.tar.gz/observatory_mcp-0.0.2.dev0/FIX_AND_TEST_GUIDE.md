# Fix and Test Guide

## 🎯 Current Situation

### What's Happening:
- ✅ **observatory-mcp v0.1.0** is successfully published on PyPI
- ❌ Workflow keeps trying to re-upload v0.1.0 (fails with "filename already used")
- ❌ Old tags (v0.1.0, v0.1.1) were created before dynamic versioning workflow was added

### Why v0.1.1 Failed:
Your v0.1.1 release was created BEFORE you pushed the dynamic versioning workflow update, so it still built v0.1.0 from `pyproject.toml`.

---

## ✅ Quick Fix: Test with v0.1.2

Follow these steps to test the new dynamic versioning workflow:

### Step 1: Clean Up Old Tags
```bash
cd /Users/amannhq/Desktop/Me/observatory/sdk/python-sdk

# Delete old tags locally
git tag -d v0.1.0
git tag -d v0.1.1

# Delete from remote
git push origin :refs/tags/v0.1.0
git push origin :refs/tags/v0.1.1
```

### Step 2: Create v0.1.2 Tag
```bash
# Create new tag
git tag v0.1.2

# Push to remote
git push origin v0.1.2
```

### Step 3: Create GitHub Release
```bash
gh release create v0.1.2 \
  --title "v0.1.2 - Test Dynamic Versioning" \
  --notes "Testing automatic version management:
- Workflow extracts version from tag
- Automatically updates pyproject.toml
- Builds with correct version
- Publishes to PyPI" \
  --repo amannhq/observatory-python-sdk
```

### Step 4: Watch Workflow
```bash
# Watch in real-time
gh run watch --repo amannhq/observatory-python-sdk
```

---

## 🔍 What to Look For

### The workflow should:
1. ✅ **Extract version**: `v0.1.2` → `0.1.2`
2. ✅ **Update pyproject.toml**: `version = "0.1.2"`
3. ✅ **Build packages**:
   - `observatory_mcp-0.1.2-py3-none-any.whl`
   - `observatory_mcp-0.1.2.tar.gz`
4. ✅ **Verify filenames** match version
5. ✅ **Publish to PyPI** successfully
6. ✅ **Attach to release**

### In the logs, you should see:
```
📦 Release version: 0.1.2
🔄 Updating version to 0.1.2 in pyproject.toml
✅ Version updated in pyproject.toml
🔨 Building version 0.1.2
📦 Built packages:
  observatory_mcp-0.1.2-py3-none-any.whl
  observatory_mcp-0.1.2.tar.gz
🔍 Verifying built package has version 0.1.2
✅ Wheel file has correct version: observatory_mcp-0.1.2-py3-none-any.whl
✅ Tarball has correct version: observatory_mcp-0.1.2.tar.gz
✅ All package files have correct version!
```

---

## ✅ Verify Success

After the workflow completes:

### 1. Check PyPI
```bash
pip index versions observatory-mcp
# Should show: 0.1.0, 0.1.2
```

### 2. Test Installation
```bash
pip install observatory-mcp==0.1.2
python -c "import observatory_mcp; print(observatory_mcp.__version__)"
# Output: 0.1.2
```

### 3. Check Package Page
```bash
open https://pypi.org/project/observatory-mcp/
# Should show version 0.1.2
```

---

## 🎯 One-Line Commands

### Quick Test:
```bash
# All in one:
cd /Users/amannhq/Desktop/Me/observatory/sdk/python-sdk && \
git tag -d v0.1.0 v0.1.1 && \
git push origin :refs/tags/v0.1.0 :refs/tags/v0.1.1 && \
git tag v0.1.2 && \
git push origin v0.1.2 && \
gh release create v0.1.2 \
  --title "v0.1.2 - Test Dynamic Versioning" \
  --notes "Testing automatic version management" \
  --repo amannhq/observatory-python-sdk
```

Then watch:
```bash
gh run watch --repo amannhq/observatory-python-sdk
```

---

## 🔧 If It Still Fails

### Check Workflow File is Updated:
```bash
# View the workflow on GitHub
gh workflow view publish.yml --repo amannhq/observatory-python-sdk

# Should show the "Extract version from tag" step
```

### View Full Logs:
```bash
gh run view --log --repo amannhq/observatory-python-sdk
```

### Debug Version Extraction:
The workflow does:
```bash
# For tag v0.1.2:
VERSION=${GITHUB_REF#refs/tags/v}  # Removes "refs/tags/v"
# Result: VERSION=0.1.2
```

---

## 📊 Expected Outcome

### Success Indicators:
1. ✅ Workflow completes with all green checkmarks
2. ✅ PyPI shows `observatory-mcp==0.1.2`
3. ✅ `pip install observatory-mcp==0.1.2` works
4. ✅ GitHub release has attached `.whl` and `.tar.gz` files
5. ✅ Package metadata shows correct version

### What You'll Have:
- ✅ Dynamic versioning working (tag → package version)
- ✅ Two versions on PyPI: 0.1.0, 0.1.2
- ✅ Confidence in the release process

---

## 🎉 After Success

Once v0.1.2 works, you can release future versions easily:

```bash
# For version 0.1.3:
git tag v0.1.3 && git push origin v0.1.3
gh release create v0.1.3 --title "v0.1.3" --notes "Bug fixes"

# For version 0.2.0:
git tag v0.2.0 && git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes "New features"

# For version 1.0.0:
git tag v1.0.0 && git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0 🎉" --notes "Production ready!"
```

---

## ❓ FAQ

### Q: Why not just fix v0.1.1?
**A:** You can't re-publish the same version to PyPI. Once 0.1.0 is published, it's permanent. We need a new version number.

### Q: What happened to v0.1.0?
**A:** It's already successfully published and working! The "error" is actually confirming success.

### Q: Do I need to manually update pyproject.toml?
**A:** No! The workflow does it automatically from the git tag.

### Q: Will this work for all future releases?
**A:** Yes! Just create a tag and release - the workflow handles the rest.

---

## 📝 Summary

**Problem:** Workflow keeps trying to upload v0.1.0 which already exists  
**Root Cause:** Old tags created before dynamic versioning workflow  
**Solution:** Clean up and test with v0.1.2  
**Future:** Just tag and release - everything is automatic!

---

**Ready to test?** Run the commands above and watch it work! 🚀

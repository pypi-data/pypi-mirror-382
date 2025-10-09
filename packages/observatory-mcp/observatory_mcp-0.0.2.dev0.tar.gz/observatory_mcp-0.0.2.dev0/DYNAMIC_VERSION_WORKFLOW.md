# Dynamic Version Workflow

## ✅ Improved: Version Management from Git Tags

The workflow now **automatically handles versions** from git tags, so you don't need to manually update `pyproject.toml` before each release!

---

## 🎯 How It Works

### The Problem (Before):
```
1. Update version in pyproject.toml: version = "0.1.1"
2. Commit and push
3. Create git tag: v0.1.1
4. Create GitHub release
```

❌ **Risk**: Tag and pyproject.toml version could get out of sync  
❌ **Manual**: Extra step to update version file  
❌ **Error-prone**: Easy to forget to update version  

---

### The Solution (Now):
```
1. Create git tag: v0.1.1
2. Create GitHub release
```

✅ **Automatic**: Workflow extracts version from tag  
✅ **Single source of truth**: Git tag is authoritative  
✅ **Verified**: Built packages checked for correct version  

---

## 🔧 What the Workflow Does

### Step 1: Extract Version from Tag
```yaml
- name: Extract version from tag
  id: get_version
  run: |
    if [[ "${{ github.event_name }}" == "release" ]]; then
      # Extract version from release tag (remove 'v' prefix)
      VERSION=${GITHUB_REF#refs/tags/v}
      echo "version=$VERSION" >> $GITHUB_OUTPUT
      echo "📦 Release version: $VERSION"
    fi
```

**Example:**
- Git tag: `v0.1.1`
- Extracted version: `0.1.1`

---

### Step 2: Update pyproject.toml
```yaml
- name: Update version in pyproject.toml
  if: github.event_name == 'release'
  run: |
    VERSION="${{ steps.get_version.outputs.version }}"
    sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
```

**Result:**
```toml
# Before
version = "0.1.0"

# After (automatically updated)
version = "0.1.1"
```

---

### Step 3: Build Package
```yaml
- name: Build package
  run: |
    echo "🔨 Building version ${{ steps.get_version.outputs.version }}"
    python -m build
```

**Creates:**
- `observatory_mcp-0.1.1-py3-none-any.whl`
- `observatory_mcp-0.1.1.tar.gz`

---

### Step 4: Verify Version
```yaml
- name: Verify package version
  run: |
    VERSION="${{ steps.get_version.outputs.version }}"
    
    # Check wheel filename has correct version
    if ls dist/*-$VERSION-*.whl; then
      echo "✅ Wheel file has correct version"
    else
      echo "❌ ERROR: Version mismatch!"
      exit 1
    fi
```

**Catches errors like:**
- Tag says `v0.1.1` but package built as `0.1.0`
- Prevents publishing wrong version

---

## 🚀 New Release Workflow

### Simple 3-Step Process:

#### 1. Create Tag
```bash
git tag v0.1.1
git push origin v0.1.1
```

#### 2. Create Release
```bash
gh release create v0.1.1 \
  --title "v0.1.1 - Bug Fixes" \
  --notes "See CHANGELOG.md for details"
```

#### 3. Done! ✅
The workflow automatically:
- ✅ Extracts version `0.1.1` from tag `v0.1.1`
- ✅ Updates `pyproject.toml` to version `0.1.1`
- ✅ Builds `observatory_mcp-0.1.1-*.whl`
- ✅ Verifies package version matches tag
- ✅ Publishes to PyPI as `observatory-mcp==0.1.1`
- ✅ Attaches packages to GitHub release

---

## 📊 Workflow Steps Overview

```
┌─────────────────────────────────────┐
│ 1. Git Tag Created: v0.1.1         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. GitHub Release Created          │
└──────────────┬──────────────────────┘
               │
               ▼ (Workflow Triggered)
┌─────────────────────────────────────┐
│ 3. Extract Version: 0.1.1          │
│    (Remove 'v' prefix from tag)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Update pyproject.toml            │
│    version = "0.1.1"                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Build Package                    │
│    - observatory_mcp-0.1.1.whl     │
│    - observatory_mcp-0.1.1.tar.gz  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. Verify Filenames Match           │
│    ✅ 0.1.1 == 0.1.1                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 7. Publish to PyPI                  │
│    observatory-mcp==0.1.1           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 8. Attach to GitHub Release         │
│    ✅ Complete!                      │
└─────────────────────────────────────┘
```

---

## ✅ Benefits

### 1. Single Source of Truth
**Git tag is the authoritative version**
- No manual file updates needed
- No risk of version mismatch
- Clear version history in git

### 2. Automatic Validation
**Built-in checks prevent mistakes**
- Verifies package filenames match tag version
- Fails fast if versions don't match
- Ensures consistency

### 3. Simpler Process
**Fewer steps, less error-prone**
```bash
# Old way (3 files to update):
1. Edit pyproject.toml
2. Edit CHANGELOG.md
3. Commit and push
4. Create tag
5. Create release

# New way (just tag and release):
1. Create tag: v0.1.1
2. Create release
✅ Done!
```

### 4. Better Logging
**Clear visibility into what's happening**
```
📦 Release version: 0.1.1
🔄 Updating version to 0.1.1 in pyproject.toml
✅ Version updated in pyproject.toml
🔨 Building version 0.1.1
📦 Built packages:
  - observatory_mcp-0.1.1-py3-none-any.whl
  - observatory_mcp-0.1.1.tar.gz
🔍 Verifying built package has version 0.1.1
✅ Wheel file has correct version
✅ Tarball has correct version
✅ All package files have correct version!
```

---

## 🎯 Usage Examples

### Example 1: Patch Release (Bug Fix)
```bash
# Current version: 0.1.0
# New version: 0.1.1

git tag v0.1.1
git push origin v0.1.1

gh release create v0.1.1 \
  --title "v0.1.1 - Bug Fixes" \
  --notes "- Fixed message interceptor bug
- Improved error handling"
```

✅ **Result:** `observatory-mcp==0.1.1` published to PyPI

---

### Example 2: Minor Release (New Features)
```bash
# Current version: 0.1.1
# New version: 0.2.0

git tag v0.2.0
git push origin v0.2.0

gh release create v0.2.0 \
  --title "v0.2.0 - New Features" \
  --notes "- Added custom sampling strategies
- New privacy controls
- Performance improvements"
```

✅ **Result:** `observatory-mcp==0.2.0` published to PyPI

---

### Example 3: Major Release
```bash
# Current version: 0.2.0
# New version: 1.0.0

git tag v1.0.0
git push origin v1.0.0

gh release create v1.0.0 \
  --title "v1.0.0 - Production Ready!" \
  --notes "🎉 First stable release!

## Breaking Changes
- Renamed `wrap_server()` to `monitor()`

## Features
- Stable API
- Full documentation
- Production tested"
```

✅ **Result:** `observatory-mcp==1.0.0` published to PyPI

---

## 🔍 Version Format

### Required Format:
```
v<MAJOR>.<MINOR>.<PATCH>
```

### Examples:
- ✅ `v0.1.0` → Extracts to `0.1.0`
- ✅ `v0.1.1` → Extracts to `0.1.1`
- ✅ `v0.2.0` → Extracts to `0.2.0`
- ✅ `v1.0.0` → Extracts to `1.0.0`
- ✅ `v1.2.3` → Extracts to `1.2.3`

### Invalid:
- ❌ `0.1.0` (missing 'v' prefix)
- ❌ `v0.1` (missing patch version)
- ❌ `release-0.1.0` (wrong prefix)

---

## 🛠️ Manual Version Override

For manual workflow triggers, the version is read from `pyproject.toml`:

```bash
# Manually trigger workflow
gh workflow run publish.yml \
  --ref main \
  -f pypi-repo=testpypi
```

**Uses:** Version from `pyproject.toml` (not from tag)

---

## ⚠️ Important Notes

### 1. pyproject.toml Can Be Outdated
Since the version is updated automatically during the release workflow, the `pyproject.toml` in your repo can have an old version. **This is normal!**

```toml
# pyproject.toml in repo (may be outdated)
version = "0.1.0"

# But when you release v0.1.1:
# - Workflow updates it to "0.1.1"
# - Builds with version "0.1.1"
# - Publishes as "0.1.1"
```

### 2. Optional: Keep pyproject.toml Updated
If you want to keep it updated in the repo:

```bash
# After release, pull the updated file
git pull origin main

# Or manually update it
sed -i 's/^version = .*/version = "0.1.1"/' pyproject.toml
git add pyproject.toml
git commit -m "chore: update version to 0.1.1 [skip ci]"
git push
```

But **this is optional** - the workflow handles it automatically!

### 3. Verification Prevents Mistakes
The verification step catches:
- Wrong version in pyproject.toml before tagging
- Sed command failure
- Build issues
- Filename mismatches

---

## 🎉 Summary

### Old Workflow:
```bash
1. Edit pyproject.toml → version = "0.1.1"
2. git add pyproject.toml
3. git commit -m "chore: bump version to 0.1.1"
4. git push
5. git tag v0.1.1
6. git push origin v0.1.1
7. gh release create v0.1.1
```

### New Workflow:
```bash
1. git tag v0.1.1
2. git push origin v0.1.1
3. gh release create v0.1.1
```

✅ **60% fewer steps**  
✅ **No manual file edits**  
✅ **Automatic verification**  
✅ **Single source of truth: git tags**

---

## 📝 Quick Reference

### Release a New Version:
```bash
# 1. Tag
git tag v0.1.1 && git push origin v0.1.1

# 2. Release
gh release create v0.1.1 --title "v0.1.1" --notes "Bug fixes"

# 3. Done! (Workflow handles the rest)
```

### Check Workflow:
```bash
# Watch in real-time
gh run watch

# View logs
gh run view --log
```

### Verify Published:
```bash
# Check PyPI
pip index versions observatory-mcp

# Test install
pip install observatory-mcp==0.1.1
```

---

**Status:** ✅ Dynamic version handling enabled  
**Benefit:** Simplified release process with automatic version management  
**Reliability:** Built-in verification prevents version mismatches

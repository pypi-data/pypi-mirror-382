# LZaaS CLI Release Guide

## 🔍 PyPI Upload Mystery - SOLVED!

**The v1.0.0 package on PyPI was uploaded via GitHub Actions, but with a version mismatch:**

- **Git Tag**: `v0.9.0-test` (invalid semantic version)
- **PyPI Package**: `lzaas-cli 1.0.0` (from hardcoded setup.py)
- **Root Cause**: setuptools_scm couldn't parse the invalid tag, so it fell back to the hardcoded version

## ✅ Current State (Fixed)

1. **✅ Codecov Rate Limiting**: Fixed with `CODECOV_TOKEN` parameter
2. **✅ Dynamic Versioning**: Implemented with setuptools_scm
3. **✅ Invalid Tag**: Removed `v0.9.0-test` from local and remote
4. **✅ Hardcoded Version**: Removed from setup.py

## 🚀 How to Release v1.0.0 Properly

### Step 1: Commit Current Changes
```bash
git add .
git commit -m "feat: implement dynamic versioning and fix codecov integration

- Replace hardcoded version with setuptools_scm
- Add CODECOV_TOKEN support to prevent rate limiting
- Remove invalid v0.9.0-test tag
- Prepare for proper v1.0.0 release"
git push origin main
```

### Step 2: Create Proper v1.0.0 Tag
```bash
# Create and push the v1.0.0 tag
git tag v1.0.0
git push origin v1.0.0
```

### Step 3: Automatic Release Process
The GitHub Actions release workflow will automatically:
1. **Trigger** on the `v1.0.0` tag
2. **Build** the package with version `1.0.0` (from git tag)
3. **Upload** to PyPI using the `PYPI_API_TOKEN` secret
4. **Create** GitHub release with changelog

## 🔧 Version Management System

### How It Works
- **No Tags**: `0.0.postN+dirty` (development versions)
- **With Tag**: `1.0.0` (release versions)
- **Post-Release**: `1.0.1.devN+gHASH` (development after release)

### Tag Format Requirements
- ✅ `v1.0.0` - Valid semantic version
- ✅ `v1.2.3-alpha1` - Valid pre-release
- ❌ `v1.0.0-test` - Invalid (setuptools_scm can't parse)

## 🏢 Organizational Migration

### Current Status
- **PyPI Package**: Under your personal account
- **GitHub Repo**: Under SPITZKOP organization
- **API Token**: Personal token in GitHub secrets

### Required Actions (After SPITZKOP PyPI Approval)
1. Generate organization-scoped PyPI API token
2. Update GitHub secret: `PYPI_API_TOKEN`
3. Transfer package ownership to SPITZKOP organization

## 📋 Pre-Release Checklist

- [x] Fix codecov rate limiting
- [x] Implement dynamic versioning
- [x] Remove invalid tags
- [x] Test version generation
- [ ] Commit all changes
- [ ] Create v1.0.0 tag
- [ ] Verify release workflow
- [ ] Update documentation

## 🎯 Release Commands

```bash
# 1. Final commit
git add .
git commit -m "feat: prepare v1.0.0 release with production-ready workflows"
git push origin main

# 2. Create release tag
git tag v1.0.0
git push origin v1.0.0

# 3. Monitor release
# Check GitHub Actions: https://github.com/SPITZKOP/lzaas-cli/actions
# Verify PyPI upload: https://pypi.org/project/lzaas-cli/

# 4. Test installation
pip install lzaas-cli==1.0.0
lzaas --version
```

## 🔍 Troubleshooting

### If Release Fails
1. Check GitHub Actions logs
2. Verify `PYPI_API_TOKEN` secret exists
3. Ensure tag follows `v*` pattern
4. Check for any CI test failures

### Version Issues
```bash
# Check current version
python3 setup.py --version

# Check git tags
git tag --list

# Check setuptools_scm output
python3 -c "import setuptools_scm; print(setuptools_scm.get_version())"
```

## 🎉 Success Criteria

A successful v1.0.0 release will have:
- ✅ GitHub release created automatically
- ✅ PyPI package uploaded as `lzaas-cli 1.0.0`
- ✅ Version matches git tag exactly
- ✅ All CI tests passing
- ✅ Documentation updated

The system is now production-ready with proper version control and automated releases!

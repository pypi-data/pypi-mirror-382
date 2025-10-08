# PyPI Package Management Guide

## Overview

This guide covers managing the LZaaS CLI package on PyPI, including removal of existing versions and best practices for version management.

## Current Situation

- **Package Name**: `lzaas-cli`
- **Current Version on PyPI**: `1.0.0` (uploaded accidentally with invalid git tag)
- **Repository**: https://github.com/SPITZKOP/lzaas-cli
- **PyPI URL**: https://pypi.org/project/lzaas-cli/

## Removing the Current Package from PyPI

### Option 1: Delete Specific Version (Recommended)

You can delete the problematic `1.0.0` version while keeping the package name reserved:

1. **Log into PyPI**:
   - Go to https://pypi.org/account/login/
   - Use your PyPI credentials

2. **Navigate to Package Management**:
   - Go to https://pypi.org/manage/project/lzaas-cli/
   - Click on "Manage" for the lzaas-cli project

3. **Delete Version 1.0.0**:
   - Find version `1.0.0` in the releases list
   - Click "Options" → "Delete"
   - Confirm the deletion

### Option 2: Delete Entire Package (Nuclear Option)

⚠️ **Warning**: This will completely remove the package and make the name available to others.

1. **Go to Package Settings**:
   - Navigate to https://pypi.org/manage/project/lzaas-cli/settings/
   - Scroll to "Delete project"

2. **Delete Package**:
   - Type the package name exactly: `lzaas-cli`
   - Click "Delete project"

## Version Management Best Practices

### Semantic Versioning Support

The current setuptools_scm configuration supports:

```python
use_scm_version={
    "version_scheme": "post-release",
    "local_scheme": "dirty-tag",
    "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+?)(?P<suffix>.*)?$"
}
```

### Supported Tag Formats

✅ **Valid Tags**:
- `v1.0.0` → Version: `1.0.0`
- `v1.0.0-alpha` → Version: `1.0.0a0`
- `v1.0.0-beta` → Version: `1.0.0b0`
- `v1.0.0-rc1` → Version: `1.0.0rc1`
- `v0.9.0-test` → Version: `0.9.0.dev0`
- `v1.0.1-fix` → Version: `1.0.1.dev0`

❌ **Invalid Tags** (that caused the original issue):
- Tags with invalid semantic version format
- Tags that don't match the regex pattern

### Pre-release Version Examples

```bash
# Alpha release
git tag v1.0.0-alpha
git push origin v1.0.0-alpha
# Results in: 1.0.0a0

# Beta release
git tag v1.0.0-beta
git push origin v1.0.0-beta
# Results in: 1.0.0b0

# Release candidate
git tag v1.0.0-rc1
git push origin v1.0.0-rc1
# Results in: 1.0.0rc1

# Development/test versions
git tag v1.0.1-fix
git push origin v1.0.1-fix
# Results in: 1.0.1.dev0
```

## Release Process

### 1. Development Releases

For testing and development:

```bash
# Create a development tag
git tag v1.0.0-dev
git push origin v1.0.0-dev

# This will trigger CI and upload to PyPI as: 1.0.0.dev0
```

### 2. Pre-release Versions

For alpha, beta, or release candidates:

```bash
# Alpha
git tag v1.0.0-alpha
git push origin v1.0.0-alpha

# Beta
git tag v1.0.0-beta
git push origin v1.0.0-beta

# Release Candidate
git tag v1.0.0-rc1
git push origin v1.0.0-rc1
```

### 3. Production Releases

For final releases:

```bash
# Production release
git tag v1.0.0
git push origin v1.0.0

# This will trigger CI and upload to PyPI as: 1.0.0
```

## Automated Release Workflow

The GitHub Actions workflow (`.github/workflows/release.yml`) automatically:

1. **Triggers on tag push**: Any tag matching `v*` pattern
2. **Builds package**: Uses setuptools_scm for version detection
3. **Runs tests**: Ensures quality before release
4. **Uploads to PyPI**: Uses `PYPI_API_TOKEN` secret
5. **Creates GitHub Release**: With auto-generated changelog

## Troubleshooting

### Version Not Detected Correctly

```bash
# Check what setuptools_scm detects
cd sse-landing-zone/lzaas-cli
python3 setup.py --version

# If issues, check git tags
git tag -l
git describe --tags
```

### PyPI Upload Failures

Common issues and solutions:

1. **Version already exists**:
   - Delete the version from PyPI first
   - Or increment the version number

2. **Invalid credentials**:
   - Check `PYPI_API_TOKEN` secret in GitHub
   - Regenerate token if needed

3. **Package name conflicts**:
   - Ensure package name is available
   - Consider using organization prefix

## Security Considerations

### PyPI API Token

- **Scope**: Limit to specific project only
- **Rotation**: Rotate tokens regularly
- **Storage**: Store only in GitHub Secrets
- **Access**: Limit to necessary workflows only

### Package Verification

Before each release:

1. **Test installation**: `pip install lzaas-cli==<version>`
2. **Verify functionality**: Run basic CLI commands
3. **Check dependencies**: Ensure all deps are available
4. **Security scan**: Use tools like `safety` or `bandit`

## Recovery Procedures

### If Wrong Version is Published

1. **Immediate action**: Delete the version from PyPI
2. **Fix the issue**: Correct tag/version in repository
3. **Re-release**: Create new tag with correct version
4. **Communicate**: Notify users if necessary

### If Package is Compromised

1. **Delete package**: Remove from PyPI immediately
2. **Investigate**: Determine scope of compromise
3. **Rotate credentials**: Change all API tokens
4. **Re-publish**: After security review

## Monitoring and Maintenance

### Regular Tasks

- **Monitor downloads**: Track package usage
- **Update dependencies**: Keep deps current
- **Security updates**: Apply patches promptly
- **Version cleanup**: Remove old pre-release versions

### Metrics to Track

- Download statistics
- Version adoption rates
- Issue reports related to packaging
- Security vulnerability reports

## Contact and Support

For PyPI-related issues:

- **PyPI Support**: https://pypi.org/help/
- **GitHub Issues**: https://github.com/SPITZKOP/lzaas-cli/issues
- **Team Contact**: platform@company.com

---

**Last Updated**: January 2025
**Version**: 1.0.0

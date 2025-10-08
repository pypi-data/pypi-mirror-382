# GitHub Pages Troubleshooting Guide

## Current Issue: 404 Error on https://spitzkop.github.io/lzaas-cli/

### Problem Description
The GitHub Pages site is showing a 404 error, indicating that either:
1. GitHub Pages is not properly configured in repository settings
2. The deployment workflow hasn't run successfully
3. The site content wasn't deployed correctly

### Solution Steps

#### 1. Enable GitHub Pages in Repository Settings

**Manual Steps Required:**
1. Go to https://github.com/SPITZKOP/lzaas-cli/settings/pages
2. Under "Source", select **"GitHub Actions"** (not "Deploy from a branch")
3. Save the settings

#### 2. Verify Workflow Permissions

Ensure the repository has the correct permissions:
1. Go to https://github.com/SPITZKOP/lzaas-cli/settings/actions
2. Under "Workflow permissions", select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**

#### 3. Check Workflow Status

Monitor the deployment:
1. Go to https://github.com/SPITZKOP/lzaas-cli/actions
2. Look for "Deploy Documentation" workflow runs
3. Check if any runs failed and review error logs

#### 4. Files Added to Fix Common Issues

- **`.nojekyll`**: Prevents Jekyll processing, allows files starting with underscores
- **Updated workflow**: Uses latest GitHub Pages actions with proper artifact handling

### Expected Workflow Behavior

When working correctly, the workflow should:

1. **Build Step**:
   - Create `_site` directory
   - Generate comprehensive `index.html` with navigation
   - Copy all documentation files (README, docs/, etc.)
   - Upload as Pages artifact

2. **Deploy Step**:
   - Deploy the artifact to GitHub Pages
   - Make site available at https://spitzkop.github.io/lzaas-cli/

### Troubleshooting Commands

```bash
# Check if workflow ran
gh run list --repo SPITZKOP/lzaas-cli

# View specific workflow run
gh run view <run-id> --repo SPITZKOP/lzaas-cli

# Trigger workflow manually
gh workflow run "Deploy Documentation" --repo SPITZKOP/lzaas-cli
```

### Common Issues and Solutions

#### Issue: "pages build and deployment" failing
**Solution**: Ensure GitHub Pages source is set to "GitHub Actions" in settings

#### Issue: 404 on deployed site
**Solutions**:
- Check if `index.html` exists in the artifact
- Verify `.nojekyll` file is present
- Ensure workflow completed successfully

#### Issue: Workflow not triggering
**Solutions**:
- Push changes to `main` branch
- Check workflow file syntax
- Verify repository permissions

#### Issue: Permission denied during deployment
**Solutions**:
- Enable "Read and write permissions" in Actions settings
- Check if `GITHUB_TOKEN` has sufficient permissions

### Manual Verification Steps

After fixing settings, verify:

1. **Workflow Execution**:
   ```bash
   # This commit should trigger the workflow
   git add .
   git commit -m "fix: add .nojekyll and troubleshooting guide for GitHub Pages"
   git push origin main
   ```

2. **Check Deployment**:
   - Wait 2-3 minutes for workflow to complete
   - Visit https://spitzkop.github.io/lzaas-cli/
   - Should see the documentation landing page

3. **Verify Content**:
   - Landing page should load with navigation cards
   - Links should work (README.md, docs/USER_GUIDE.md, etc.)
   - Site should be responsive and styled

### Expected Site Structure

```
https://spitzkop.github.io/lzaas-cli/
├── index.html (landing page)
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── RELEASE_GUIDE.md
├── PRODUCTION_LIFECYCLE_GUIDE.md
└── docs/
    ├── USER_GUIDE.md
    └── QUICK_REFERENCE.md
```

### Contact Information

If issues persist:
- Check GitHub Status: https://www.githubstatus.com/
- Repository Issues: https://github.com/SPITZKOP/lzaas-cli/issues
- GitHub Pages Documentation: https://docs.github.com/en/pages

---

**Last Updated**: January 2025
**Status**: Troubleshooting in progress

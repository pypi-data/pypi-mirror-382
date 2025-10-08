# LZaaS CLI - Getting Started Guide

Welcome to the **Landing Zone as a Service (LZaaS) CLI** - your command-line interface for managing AWS account migrations through Infrastructure as Code principles.

## 📋 **Table of Contents**

- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Initial Configuration](#initial-configuration)
- [Basic Usage](#basic-usage)
- [Command Reference](#command-reference)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## 🚀 **Installation**

LZaaS CLI can be installed in two ways: from PyPI (recommended for users) or from source (for development).

### **Option 1: Install from PyPI (Recommended)**

This is the easiest way to install LZaaS CLI. The package is automatically published to PyPI with each release.

```bash
# Create and activate a virtual environment (recommended)
python -m venv lzaas-env
source lzaas-env/bin/activate  # On Windows: lzaas-env\Scripts\activate

# Install LZaaS CLI from PyPI
pip install lzaas-cli

# Verify installation
lzaas --version
```

### **Option 2: Install from Source Repository**

For development or to get the latest features before they're released:

```bash
# Create and activate a virtual environment (recommended)
python -m venv lzaas-env
source lzaas-env/bin/activate  # On Windows: lzaas-env\Scripts\activate

# Clone the repository
git clone https://github.com/Cloud-Cockpit/sse-landing-zone.git
cd sse-landing-zone/lzaas-cli

# Install in development mode
pip install -e .

# Verify installation
lzaas --version
```

### **Virtual Environment Best Practices**

**Always use a virtual environment** to avoid conflicts with other Python packages:

```bash
# Create virtual environment
python -m venv lzaas-env

# Activate virtual environment
# On macOS/Linux:
source lzaas-env/bin/activate

# On Windows:
lzaas-env\Scripts\activate

# When done, deactivate
deactivate
```

---

## 📋 **Prerequisites**

Before using LZaaS CLI, ensure you have:

### **1. Python Environment**
- Python 3.8 or higher
- pip package manager

### **2. AWS Access**
- AWS CLI configured with appropriate credentials
- AWS SSO session (if using SSO)
- Permissions to access AWS Organizations

### **3. AWS Organizations Setup**
- Access to AWS Organizations in your management account
- Organizational Units (OUs) configured
- Accounts to migrate between OUs

### **4. GitHub Access (for future releases)**
- GitHub account with repository access
- Personal Access Token (for GitHub API operations)

---

## ⚙️ **Initial Configuration**

### **Step 1: Verify AWS Access**

Ensure your AWS credentials are properly configured:

```bash
# Check AWS configuration
aws sts get-caller-identity

# If using SSO, login first
aws sso login --profile your-profile
```

### **Step 2: Initialize LZaaS Configuration**

```bash
# Initialize LZaaS configuration
lzaas config init

# This will prompt you for:
# - AWS profile name
# - AWS region
# - GitHub organization (for future releases)
# - Repository settings
```

### **Step 3: Validate Configuration**

```bash
# Check your configuration
lzaas config show

# Validate AWS connectivity
lzaas config validate
```

### **Step 4: Test Basic Functionality**

```bash
# List available Organizational Units
lzaas migrate list-ous

# Check migration status
lzaas migrate status
```

---

## 🎯 **Basic Usage**

### **Account Migration Planning**

The primary function of LZaaS CLI v1.0.0 is to plan and preview account migrations:

```bash
# Plan a migration (dry-run mode)
lzaas migrate simple --source ACCOUNT_NAME --target TARGET_OU --dry-run

# Example: Move SPITZKOP account to Sandbox OU
lzaas migrate simple --source spitzkop --target sandbox --dry-run
```

### **Understanding the Output**

When you run a migration command, you'll see:

1. **Migration Plan Table**: Shows source account, current location, target OU
2. **Repository Changes**: Lists files that would be modified
3. **Process Flow**: Step-by-step explanation of what would happen
4. **Terraform Preview**: Shows the exact Terraform code that would be generated
5. **Pull Request Details**: Shows the branch name and PR description

### **Example Output**

```
🔄 Infrastructure as Code Account Migration
All changes will be made through Git repository updates

        🏗️ Infrastructure as Code Migration Plan
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field            ┃ Value                            ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Source Account   │ SPITZKOP (198610579545)          │
│ Current Location │ Root                             │
│ Target OU        │ Sandbox (ou-lcnt-dmpxlwlu)       │
│ Repository       │ Cloud-Cockpit/sse-landing-zone   │
│ Method           │ Git-based Infrastructure as Code │
└──────────────────┴──────────────────────────────────┘

📝 Repository Changes:
  ~ terraform/live/account-factory/lzaas-account-198610579545.tf (create/update)
  ~ terraform/live/account-factory/lzaas-metadata.tf (update)
  ~ terraform/live/account-factory/.lzaas-managed (update)

🔍 DRY RUN MODE - No changes will be made
```

---

## 📚 **Command Reference**

### **Configuration Commands**

```bash
# Initialize configuration
lzaas config init

# Show current configuration
lzaas config show

# Validate configuration and AWS access
lzaas config validate

# Update specific configuration values
lzaas config set github.organization "your-org"
lzaas config set aws.profile "your-profile"
```

### **Migration Commands**

```bash
# Plan account migration (dry-run)
lzaas migrate simple --source ACCOUNT --target OU --dry-run

# List available Organizational Units
lzaas migrate list-ous

# Check migration status
lzaas migrate status

# Filter status by account or OU
lzaas migrate status --account-id 123456789012
lzaas migrate status --ou "Development"
```

### **Account Management Commands**

```bash
# Create new account request
lzaas account create --name "MyAccount" --email "admin@example.com" --ou "Development"

# List account requests
lzaas account list

# Show account request details
lzaas account show REQUEST_ID

# Update account request
lzaas account update REQUEST_ID --status "approved"
```

### **Template Commands**

```bash
# List available templates
lzaas template list

# Show template details
lzaas template show TEMPLATE_NAME

# Validate template
lzaas template validate TEMPLATE_NAME
```

### **Status and Information Commands**

```bash
# Show CLI version
lzaas --version

# Show help for any command
lzaas COMMAND --help

# Show general help
lzaas --help
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **AWS Authentication Errors**

```bash
# Error: "The SSO session associated with this profile has expired"
aws sso login --profile your-profile

# Error: "Unable to locate credentials"
aws configure list
aws configure set profile.your-profile.region eu-west-3
```

#### **Permission Errors**

```bash
# Error: "Access denied to Organizations"
# Ensure your AWS user/role has these permissions:
# - organizations:ListAccounts
# - organizations:ListOrganizationalUnitsForParent
# - organizations:ListRoots
# - organizations:DescribeAccount
# - organizations:DescribeOrganizationalUnit
```

#### **Configuration Issues**

```bash
# Reset configuration
rm ~/.lzaas/config.yaml
lzaas config init

# Check configuration file location
lzaas config show --debug
```

#### **Installation Issues**

```bash
# If installation fails, try upgrading pip
pip install --upgrade pip

# Install with verbose output
pip install -v lzaas-cli

# For development installation issues
pip install -e . --verbose
```

### **Debug Mode**

Enable debug mode for detailed logging:

```bash
# Run any command with debug output
lzaas --debug migrate simple --source spitzkop --target sandbox --dry-run

# Set debug environment variable
export LZAAS_DEBUG=1
lzaas migrate list-ous
```

### **Getting Help**

```bash
# Command-specific help
lzaas migrate --help
lzaas config --help

# Show all available commands
lzaas --help

# Check version and build info
lzaas --version
```

---

## 🎯 **Next Steps**

### **After Installation**

1. **Configure AWS Access**: Ensure your AWS credentials are properly set up
2. **Initialize LZaaS**: Run `lzaas config init` to set up your configuration
3. **Explore Your Organization**: Use `lzaas migrate list-ous` to see your OU structure
4. **Plan a Migration**: Try a dry-run migration to see how it works

### **Learning More**

- **User Guide**: Read the comprehensive [User Guide](USER_GUIDE.md)
- **Quick Reference**: Check the [Quick Reference](QUICK_REFERENCE.md) for command shortcuts
- **Architecture**: Understand the [system architecture](../README.md#architecture)

### **Contributing**

- **Report Issues**: Use GitHub Issues for bug reports and feature requests
- **Contribute Code**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
- **Documentation**: Help improve documentation and examples

### **What's Coming in Future Releases**

- **Full GitHub Integration**: Actual repository modifications and PR creation
- **Advanced Migration Workflows**: Complex multi-account migrations
- **Enhanced Templates**: More sophisticated account templates
- **Monitoring Dashboard**: Real-time migration status tracking

---

## 📞 **Support**

- **Documentation**: [LZaaS CLI Documentation](../README.md)
- **Issues**: [GitHub Issues](https://github.com/Cloud-Cockpit/sse-landing-zone/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cloud-Cockpit/sse-landing-zone/discussions)

---

**Welcome to LZaaS CLI v1.0.0!** 🚀

You're now ready to start planning and managing your AWS account migrations through Infrastructure as Code principles. The v1.0.0 release provides comprehensive planning and preview capabilities, with full GitHub integration coming in future releases.

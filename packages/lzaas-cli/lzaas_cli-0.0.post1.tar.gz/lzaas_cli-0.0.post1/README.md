# LZaaS CLI

🚀 **Landing Zone as a Service - Command Line Interface**

A powerful CLI tool for managing AWS Account Factory (AFT) through GitOps Infrastructure as Code principles.

![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![LZaaS](https://img.shields.io/badge/LZaaS-v1.0.0-green.svg)

## Overview

LZaaS CLI v1.0.0 provides a streamlined interface for:
- **Account Migration Planning**: Plan and preview AWS account migrations between Organizational Units
- **Beautiful CLI Interface**: Rich tables, animations, and comprehensive dry-run capabilities
- **AWS Organizations Integration**: Discover accounts and OUs automatically
- **Infrastructure as Code**: Generate Terraform previews and Pull Request details
- **Migration Status Monitoring**: Track ongoing and completed migrations

## 🚀 Quick Start

### Option 1: Install from PyPI (Recommended)

```bash
# Create and activate virtual environment
python -m venv lzaas-env
source lzaas-env/bin/activate  # On Windows: lzaas-env\Scripts\activate

# Install from PyPI
pip install lzaas-cli

# Initialize configuration
lzaas config init

# Test with a dry-run migration
lzaas migrate simple --source spitzkop --target sandbox --dry-run

# Create your first account
lzaas account create --template dev --email dev@company.com --client-id your-team
```

### Option 2: Install from Source (Development)

```bash
# Create and activate virtual environment
python -m venv lzaas-env
source lzaas-env/bin/activate  # On Windows: lzaas-env\Scripts\activate

# Clone the repository
git clone https://github.com/Cloud-Cockpit/sse-landing-zone.git
cd sse-landing-zone/lzaas-cli

# Install in development mode
pip install -e .

# Using install script
./install-lzaas.sh

# Initialize configuration
lzaas config init

# Test with a dry-run migration
lzaas migrate simple --source spitzkop --target sandbox --dry-run

# Create your first account
lzaas account create --template dev --email dev@company.com --client-id your-team
```

### Uinstall LZaaS CLI
```bash
./uninstall-lzaas.sh
```

## 📚 Documentation

- **[Getting Started Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/GETTING_STARTED.md)** - Complete installation and setup guide
- **[User Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/USER_GUIDE.md)** - Comprehensive usage documentation
- **[Quick Reference](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/QUICK_REFERENCE.md)** - Command cheat sheet

See the development [Installation Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/INSTALLATION_GUIDE.md) for development environment detailed setup instructions.

### Technical Documentation
- [Installation Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/INSTALLATION_GUIDE.md)
- [Migration Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/MIGRATION_GUIDE.md)
- [LZaaS Internals](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/ARCHITECTURE.md)
- [Release Notes](https://github.com/SPITZKOP/lzaas-cli/blob/main/RELEASE_NOTES.md)

## ✨ Key Features

### Beautiful Migration Planning

```bash
# Plan account migration with beautiful output
lzaas migrate simple --source spitzkop --target sandbox --dry-run
```

**Example Output:**
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

🔍 DRY RUN MODE - No changes will be made
```

### AWS Organizations Discovery

```bash
# List all available Organizational Units
lzaas migrate list-ous

# Check migration status
lzaas migrate status
```

### Configuration Management

```bash
# Initialize configuration
lzaas config init

# Show current configuration
lzaas config show

# Validate AWS connectivity
lzaas config validate
```

## 📋 Essential Commands

### Migration Commands
```bash
# Plan account migration (dry-run mode)
lzaas migrate simple --source ACCOUNT_NAME --target TARGET_OU --dry-run

# List available Organizational Units
lzaas migrate list-ous

# Check migration status
lzaas migrate status

# Filter status by account or OU
lzaas migrate status --account-id 123456789012
lzaas migrate status --ou "Development"
```

### Configuration Commands
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

### Account Management Commands
```bash
# Create new account request
lzaas account create --name "MyAccount" --email "admin@example.com" --ou "Development"

# List account requests
lzaas account list

# Show account request details
lzaas account show REQUEST_ID
```

### Template Commands
```bash
# List available templates
lzaas template list

# Show template details
lzaas template show TEMPLATE_NAME

# Validate template
lzaas template validate TEMPLATE_NAME
```

### Information Commands
```bash
# Show CLI version
lzaas --version

# Show help for any command
lzaas COMMAND --help

# Show general help
lzaas --help
```

## 🏗️ Architecture

LZaaS CLI v1.0.0 follows Infrastructure as Code principles:

```
LZaaS CLI → AWS Organizations → Migration Planning → Terraform Preview → GitHub PR (mock)
```

### v1.0.0 Features:
- ✅ **Complete Migration Planning**: Full dry-run capabilities with beautiful output
- ✅ **AWS Organizations Integration**: Real account and OU discovery
- ✅ **Terraform Preview Generation**: Shows exact code that would be created
- ✅ **Mock GitHub Integration**: Demonstrates PR workflow without actual changes
- ✅ **Account ID-based Naming**: Terraform-compatible file naming
- ✅ **Rich CLI Interface**: Tables, animations, and progress indicators

### Coming in Future Releases:
- 🔄 **Full GitHub Integration**: Actual repository modifications and PR creation
- 🔄 **Advanced Migration Workflows**: Complex multi-account migrations
- 🔄 **Enhanced Templates**: More sophisticated account configurations
- 🔄 **Monitoring Dashboard**: Real-time migration status tracking

## ⚙️ Prerequisites

- **Python 3.8+** with pip
- **AWS CLI** configured with appropriate credentials
- **AWS SSO session** (if using SSO)
- **AWS Organizations access** in your management account
- **Organizational Units** configured for migration targets

## 🔧 Configuration

### AWS Authentication

```bash
# Check AWS configuration
aws sts get-caller-identity

# If using SSO, login first
aws sso login --profile your-profile
```

### LZaaS Configuration

```bash
# Initialize LZaaS configuration
lzaas config init

# This will prompt you for:
# - AWS profile name
# - AWS region
# - GitHub organization (for future releases)
# - Repository settings
```

## 🎯 Account Templates

| Template | Purpose | Security Level | Use Case |
|----------|---------|----------------|----------|
| `dev` | Development | Standard | Feature development, testing |
| `staging` | Pre-production | Production-like | UAT, integration testing |
| `production` | Live workloads | Maximum | Production deployments |
| `sandbox` | Experimentation | Basic | Learning, individual testing |

## 🔍 Troubleshooting

### Common Issues

**AWS Authentication Errors:**
```bash
# Error: "The SSO session associated with this profile has expired"
aws sso login --profile your-profile
```

**Permission Errors:**
```bash
# Ensure your AWS user/role has these permissions:
# - organizations:ListAccounts
# - organizations:ListOrganizationalUnitsForParent
# - organizations:ListRoots
# - organizations:DescribeAccount
# - organizations:DescribeOrganizationalUnit
```

**Configuration Issues:**
```bash
# Reset configuration
rm ~/.lzaas/config.yaml
lzaas config init
```

### Debug Mode

```bash
# Run any command with debug output
lzaas --debug migrate simple --source spitzkop --target sandbox --dry-run
```

## 📞 Support

- **Getting Started**: [Getting Started Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/GETTING_STARTED.md)
- **User Guide**: [Complete User Guide](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/USER_GUIDE.md)
- **Quick Reference**: [Command Reference](https://github.com/SPITZKOP/lzaas-cli/blob/main/docs/QUICK_REFERENCE.md)
- **Issues**: [GitHub Issues](https://github.com/SPITZKOP/lzaas-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SPITZKOP/lzaas-cli/discussions)

### Access Documentation via CLI
```bash
# Complete user guide with business logic
lzaas docs user-guide

# Quick command reference
lzaas docs quick-reference

# Installation instructions
lzaas docs installation

# List all available documentation
lzaas docs list
```

## 🎉 What's New in v1.0.0

- ✅ **Beautiful CLI Interface**: Rich tables, animations, and comprehensive output
- ✅ **Complete Migration Planning**: Full dry-run capabilities with Terraform previews
- ✅ **AWS Organizations Integration**: Real-time account and OU discovery
- ✅ **Infrastructure as Code**: Generate complete Terraform code and PR details
- ✅ **Account ID-based Architecture**: Terraform-compatible file naming and structure
- ✅ **Mock GitHub Integration**: Demonstrates full workflow without actual changes
- ✅ **Comprehensive Documentation**: Getting started guide and user documentation

## 📈 Version Information

**Current Version**: v1.0.0 (October 7, 2025)

**Installation Methods**:
- **PyPI Package**: `pip install lzaas-cli` (gets v1.0.0)
- **Source Repository**: `pip install -e .` (gets v0.0.post19+dirty for development)

**Version Display**: The CLI dynamically retrieves version information, so you'll see the correct version whether installed from PyPI or source.

---

**💡 Pro Tip**: Start with the [Getting Started Guide](docs/GETTING_STARTED.md) for complete installation instructions, configuration setup, and your first migration planning session!

**🚀 Ready to get started?** Install LZaaS CLI and plan your first account migration in minutes!

# LZaaS CLI Quick Reference

🚀 **Command Cheat Sheet for LZaaS CLI**

*Version: 1.1.0 | Date: October 1, 2025*

---

## 🎯 **Essential Commands**

```bash
# System Information
lzaas info                              # Show system status
lzaas docs --user-guide                 # Open complete user guide

# Account Management
lzaas account create --template dev --email dev@company.com --client-id team-alpha
lzaas account list                      # List all accounts
lzaas account list --client-id team-alpha  # Filter by client
lzaas account status --request-id dev-2025-001  # Check request status

# Templates
lzaas template list                     # List available templates
lzaas template show --name dev          # Show template details

# Migration
lzaas migrate list-ous                  # List organizational units
lzaas migrate existing-ou --account-id 123456789012 --target-ou "Development" --dry-run

# System Status
lzaas status pipeline                   # Check AFT pipeline health
```

---

## 📋 **Command Syntax**

### **Account Commands**
```bash
lzaas account create --template <TEMPLATE> --email <EMAIL> --client-id <CLIENT>
lzaas account list [--client-id <CLIENT>] [--status <STATUS>]
lzaas account status --account-id <ACCOUNT_ID> | --request-id <REQUEST_ID>
```

### **Template Commands**
```bash
lzaas template list [--detailed]
lzaas template show --name <TEMPLATE_NAME> [--examples]
```

### **Migration Commands**
```bash
lzaas migrate list-ous [--hierarchy]
lzaas migrate existing-ou --account-id <ID> --target-ou <OU> [--dry-run]
```

### **Status Commands**
```bash
lzaas status pipeline [--watch] [--pipeline-name <NAME>]
lzaas info [--detailed]
```

---

## 🏗️ **Account Templates**

| Template | Purpose | Security Level | Use Case |
|----------|---------|----------------|----------|
| `dev` | Development | Standard | Feature development, testing |
| `staging` | Pre-production | Production-like | UAT, integration testing |
| `production` | Live workloads | Maximum | Production deployments |
| `sandbox` | Experimentation | Basic | Learning, individual testing |

---

## ⚙️ **AWS Profile Configuration**

```bash
# Set default profile
export AWS_PROFILE=lzaas-production

# Use specific profile
lzaas --profile lzaas-dev account list

# Configure SSO (recommended)
aws configure sso
aws sso login --profile lzaas-production

# Configure access keys
aws configure --profile lzaas-dev
```

---

## 🔄 **Common Workflows**

### **Create New Account**
```bash
lzaas template list                     # 1. Check available templates
lzaas account create --template dev --email dev@company.com --client-id team-alpha  # 2. Create account
lzaas status --request-id <request-id>  # 3. Monitor progress
lzaas account list --client-id team-alpha  # 4. Verify creation
```

### **Migrate Existing Account**
```bash
lzaas migrate list-ous                  # 1. List target OUs
lzaas migrate existing-ou --account-id 123456789012 --target-ou "Development" --dry-run  # 2. Preview
lzaas migrate existing-ou --account-id 123456789012 --target-ou "Development"  # 3. Execute
lzaas account status --account-id 123456789012  # 4. Verify
```

---

## 🚨 **Troubleshooting**

| Issue | Quick Fix |
|-------|-----------|
| "AWS credentials not found" | `aws sts get-caller-identity` then `aws configure` |
| "GitHub Integration Pending" | Contact LZaaS administrator |
| "Access Denied" | Check AWS profile permissions |
| Account creation stuck | `lzaas status pipeline` |

---

## 📚 **Getting Help**

```bash
lzaas --help                           # General help
lzaas account --help                   # Account commands help
lzaas docs --user-guide                # Complete user guide
lzaas info                             # System status
```

---

**💡 Tip**: Use `lzaas docs --user-guide` for the complete documentation with business logic explanations and detailed examples.

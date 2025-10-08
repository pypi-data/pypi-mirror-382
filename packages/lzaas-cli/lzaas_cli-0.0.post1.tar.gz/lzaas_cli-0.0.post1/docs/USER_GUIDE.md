# LZaaS CLI User Guide

🚀 **Landing Zone as a Service - Complete User Documentation**

*Version: 1.1.0 | Date: October 1, 2025*

---

## 🎯 **What is LZaaS?**

**LZaaS (Landing Zone as a Service)** is a managed cloud service that provides automated AWS account lifecycle management. We host and manage the entire control plane (AFT infrastructure, account factory, governance, security baselines), while you use our CLI to interact with the service to create and manage your cloud accounts.

### **Service Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    LZaaS Control Plane                     │
│                   (Managed by Us)                          │
├─────────────────────────────────────────────────────────────┤
│ • AWS Account Factory (AFT)                                │
│ • Multi-Account Landing Zone                               │
│ • Security & Compliance Baselines                          │
│ • Centralized Governance & Policies                        │
│ • Account Lifecycle Management                             │
│ • Monitoring & Audit Logging                               │
└─────────────────────────────────────────────────────────────┘
                              ↕️
                    LZaaS CLI (Your Interface)
                              ↕️
┌─────────────────────────────────────────────────────────────┐
│                    Your AWS Accounts                       │
│                  (Managed by LZaaS)                        │
├─────────────────────────────────────────────────────────────┤
│ • Development Accounts                                      │
│ • Staging Accounts                                          │
│ • Production Accounts                                       │
│ • Sandbox Accounts                                          │
│ • Custom Account Types                                      │
└─────────────────────────────────────────────────────────────┘
```

### **What You Get**

- ✅ **Automated Account Creation**: Request accounts with simple CLI commands
- ✅ **Security by Default**: Pre-configured security baselines and compliance
- ✅ **Governance**: Centralized policies and organizational controls
- ✅ **Account Templates**: Standardized configurations for different use cases
- ✅ **Lifecycle Management**: Create, modify, migrate, and decommission accounts
- ✅ **Audit & Compliance**: Complete audit trails and compliance reporting
- ✅ **Multi-Environment Support**: Development, staging, production workflows

---

## 🚀 **Getting Started**

### **Prerequisites**

Before using LZaaS CLI, ensure you have:

1. **LZaaS CLI Installed** (see [Installation Guide](../docs/LZAAS_INSTALLATION_GUIDE.md))
2. **AWS Credentials Configured** (see AWS Configuration section below)
3. **Access Permissions** to the LZaaS service (provided by your administrator)

### **Quick Start Workflow**

```bash
# 1. Check system status
lzaas info

# 2. List available account templates
lzaas template list

# 3. Create your first account
lzaas account create --template dev --email dev@yourcompany.com --client-id your-team

# 4. Monitor account creation progress
lzaas status --request-id <request-id>

# 5. List your accounts
lzaas account list
```

---

## ⚙️ **AWS Configuration**

### **Understanding AWS Profiles in LZaaS**

The `--profile` parameter in LZaaS CLI serves a specific purpose in our managed service architecture:

#### **What AWS Profiles Are Used For:**

1. **Authentication to LZaaS Control Plane**: Your AWS profile authenticates you to our LZaaS service
2. **Cross-Account Access**: The profile provides access to the centralized management account where AFT runs
3. **Service Interaction**: All LZaaS operations go through our control plane, not directly to your target accounts

#### **Profile Architecture:**

```
Your Local AWS Profile → LZaaS Control Plane → Target AWS Accounts
     (Authentication)      (Service Logic)      (Account Management)
```

### **AWS Configuration Options**

#### **Option 1: AWS SSO (Recommended for Organizations)**

```bash
# Configure AWS SSO
aws configure sso

# Example SSO configuration
SSO start URL: https://yourcompany.awsapps.com/start
SSO region: eu-west-3
Account ID: 123456789012
Role name: LZaaSUserRole
CLI default client region: eu-west-3
CLI default output format: json
CLI profile name: lzaas-production

# Use with LZaaS CLI
lzaas --profile lzaas-production account list
```

#### **Option 2: Access Keys (For Development/Testing)**

```bash
# Configure access keys
aws configure --profile lzaas-dev

# You'll be prompted for:
AWS Access Key ID: AKIA...
AWS Secret Access Key: ...
Default region name: eu-west-3
Default output format: json

# Use with LZaaS CLI
lzaas --profile lzaas-dev account list
```

#### **Option 3: Environment Variables**

```bash
# Set environment variables
export AWS_PROFILE=lzaas-production
export AWS_REGION=eu-west-3

# LZaaS CLI will automatically use these
lzaas account list
```

### **Profile Switching Examples**

```bash
# Use different profiles for different environments
lzaas --profile lzaas-dev account list          # Development environment
lzaas --profile lzaas-staging account list      # Staging environment
lzaas --profile lzaas-production account list   # Production environment

# Or set default profile
export AWS_PROFILE=lzaas-production
lzaas account list  # Uses production profile
```

### **Required Permissions**

Your AWS profile needs the following permissions to interact with LZaaS:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/aft-request-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "codepipeline:GetPipelineState",
                "codepipeline:GetPipelineExecution"
            ],
            "Resource": "arn:aws:codepipeline:*:*:pipeline/aft-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "organizations:ListAccounts",
                "organizations:DescribeAccount"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 📋 **Command Reference**

### **Account Management**

#### **`lzaas account create`**
Create a new AWS account using predefined templates.

```bash
# Basic account creation
lzaas account create --template dev --email dev@company.com --client-id team-alpha

# With custom configuration
lzaas account create \
  --template production \
  --email prod@company.com \
  --client-id team-beta \
  --account-name "Production Environment" \
  --ou-name "Production"

# Options:
#   --template     Account template to use (required)
#   --email        Account email address (required)
#   --client-id    Client/team identifier (required)
#   --account-name Custom account name (optional)
#   --ou-name      Target Organizational Unit (optional)
```

**Business Logic**: This command creates a standardized AWS account with pre-configured security baselines, governance policies, and organizational structure based on the selected template.

#### **`lzaas account list`**
List all accounts accessible to your profile.

```bash
# List all accounts
lzaas account list

# Filter by client
lzaas account list --client-id team-alpha

# Filter by status
lzaas account list --status ACTIVE

# Options:
#   --client-id    Filter by client identifier
#   --status       Filter by account status (ACTIVE, PENDING, SUSPENDED)
#   --template     Filter by account template
```

**Business Logic**: Shows accounts you have access to based on your permissions and organizational structure.

#### **`lzaas account status`**
Get detailed status of a specific account or request.

```bash
# Check account status
lzaas account status --account-id 123456789012

# Check request status
lzaas account status --request-id dev-2025-001

# Options:
#   --account-id   AWS account ID
#   --request-id   Account request identifier
```

**Business Logic**: Provides real-time status of account provisioning, including AFT pipeline progress, security baseline application, and any issues.

### **Template Management**

#### **`lzaas template list`**
List available account templates.

```bash
# List all templates
lzaas template list

# Show detailed template information
lzaas template list --detailed
```

**Business Logic**: Templates define standardized account configurations including security policies, organizational placement, and resource baselines.

#### **`lzaas template show`**
Display detailed information about a specific template.

```bash
# Show template details
lzaas template show --name dev

# Show template with example usage
lzaas template show --name production --examples
```

**Business Logic**: Helps you understand what resources, policies, and configurations will be applied when using a specific template.

### **Migration Operations**

#### **`lzaas migrate existing-ou`**
Migrate existing AWS accounts into LZaaS management.

```bash
# Dry run migration (recommended first)
lzaas migrate existing-ou \
  --account-id 123456789012 \
  --target-ou "Development" \
  --dry-run

# Execute migration
lzaas migrate existing-ou \
  --account-id 123456789012 \
  --target-ou "Development"

# Options:
#   --account-id   Existing AWS account ID
#   --target-ou    Target Organizational Unit
#   --dry-run      Preview changes without executing
```

**Business Logic**: Brings existing AWS accounts under LZaaS management, applying security baselines and governance policies while preserving existing resources.

#### **`lzaas migrate list-ous`**
List available Organizational Units for migration.

```bash
# List all OUs
lzaas migrate list-ous

# Show OU hierarchy
lzaas migrate list-ous --hierarchy
```

**Business Logic**: Shows the organizational structure where accounts can be placed, helping you choose the appropriate OU for migration.

### **System Status**

#### **`lzaas status pipeline`**
Check AFT pipeline status and health.

```bash
# Check overall pipeline status
lzaas status pipeline

# Monitor pipeline in real-time
lzaas status pipeline --watch

# Check specific pipeline
lzaas status pipeline --pipeline-name aft-account-provisioning
```

**Business Logic**: Monitors the health of the Account Factory infrastructure that processes your account requests.

#### **`lzaas info`**
Display system information and health status.

```bash
# Show system overview
lzaas info

# Include detailed diagnostics
lzaas info --detailed
```

**Business Logic**: Provides a quick health check of all LZaaS components and your access status.

---

## 🏗️ **Account Templates**

### **Available Templates**

#### **Development Template (`dev`)**
- **Purpose**: Development and testing environments
- **Security Level**: Standard security with developer access
- **Resources**: Basic compute, storage, and networking
- **Policies**: Relaxed policies for experimentation
- **Cost Controls**: Budget alerts and spending limits

#### **Staging Template (`staging`)**
- **Purpose**: Pre-production testing and validation
- **Security Level**: Production-like security with limited access
- **Resources**: Production-equivalent infrastructure
- **Policies**: Production policies with testing exceptions
- **Cost Controls**: Moderate budget controls

#### **Production Template (`production`)**
- **Purpose**: Live production workloads
- **Security Level**: Maximum security and compliance
- **Resources**: High-availability, scalable infrastructure
- **Policies**: Strict governance and change controls
- **Cost Controls**: Comprehensive cost monitoring

#### **Sandbox Template (`sandbox`)**
- **Purpose**: Individual developer experimentation
- **Security Level**: Isolated with basic security
- **Resources**: Limited compute and storage
- **Policies**: Minimal restrictions for learning
- **Cost Controls**: Strict spending limits

### **Template Selection Guide**

```bash
# For new feature development
lzaas account create --template dev --email dev-feature-x@company.com

# For user acceptance testing
lzaas account create --template staging --email uat@company.com

# For production deployment
lzaas account create --template production --email prod@company.com

# For individual learning/testing
lzaas account create --template sandbox --email john.doe@company.com
```

---

## 🔄 **Common Workflows**

### **Workflow 1: New Project Setup**

```bash
# 1. Create development account
lzaas account create --template dev --email dev-project-alpha@company.com --client-id project-alpha

# 2. Monitor creation progress
lzaas status --request-id dev-2025-001

# 3. Once ready, create staging account
lzaas account create --template staging --email staging-project-alpha@company.com --client-id project-alpha

# 4. Finally, create production account
lzaas account create --template production --email prod-project-alpha@company.com --client-id project-alpha
```

### **Workflow 2: Existing Account Migration**

```bash
# 1. List available OUs
lzaas migrate list-ous

# 2. Preview migration (dry run)
lzaas migrate existing-ou --account-id 123456789012 --target-ou "Development" --dry-run

# 3. Execute migration
lzaas migrate existing-ou --account-id 123456789012 --target-ou "Development"

# 4. Verify migration
lzaas account status --account-id 123456789012
```

### **Workflow 3: Account Lifecycle Management**

```bash
# 1. List current accounts
lzaas account list --client-id your-team

# 2. Check account health
lzaas account status --account-id 123456789012

# 3. Monitor system status
lzaas status pipeline

# 4. Review available templates for new accounts
lzaas template list
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"GitHub Integration Pending"**
**Symptom**: `lzaas info` shows GitHub Integration as "Pending"

**Cause**: AFT requires GitHub repositories for account customizations and workflows.

**Solution**: Contact your LZaaS administrator to complete GitHub repository setup. This is a one-time configuration on the control plane.

#### **"AWS credentials not found"**
**Symptom**: CLI commands fail with credential errors

**Solutions**:
```bash
# Check current AWS configuration
aws sts get-caller-identity

# Configure AWS profile
aws configure --profile lzaas-production

# Or use SSO
aws sso login --profile lzaas-production

# Set environment variable
export AWS_PROFILE=lzaas-production
```

#### **"Access Denied" errors**
**Symptom**: Commands fail with permission errors

**Solution**: Verify your AWS profile has the required LZaaS permissions. Contact your administrator to ensure proper IAM roles are assigned.

#### **"Account creation stuck"**
**Symptom**: Account creation appears to hang

**Diagnosis**:
```bash
# Check pipeline status
lzaas status pipeline

# Check specific request
lzaas status --request-id your-request-id
```

**Solution**: If pipeline shows errors, contact support with the request ID.

### **Getting Help**

```bash
# Command-specific help
lzaas account create --help
lzaas template --help
lzaas migrate --help

# System information
lzaas info

# Access this user guide
lzaas docs --user-guide
```

### **Support Channels**

- **Documentation**: Run `lzaas docs --user-guide` for this complete guide
- **Command Help**: Use `--help` with any command for detailed options
- **System Status**: Use `lzaas info` to check service health
- **Administrator**: Contact your LZaaS administrator for access issues

---

## 📚 **Additional Resources**

### **Documentation Hierarchy**

- **[User Guide](USER_GUIDE.md)** - This comprehensive guide (you are here)
- **[Installation Guide](../docs/LZAAS_INSTALLATION_GUIDE.md)** - CLI installation and setup
- **[Quick Reference](QUICK_REFERENCE.md)** - Command cheat sheet
- **[API Reference](API_REFERENCE.md)** - Future API documentation

### **Version Information**

- **Current Version**: 1.1.0
- **Release Date**: October 1, 2025
- **Compatibility**: AWS AFT 1.10+
- **Supported Regions**: eu-west-3, us-east-1, us-west-2

### **Service Level Agreement**

- **Account Creation**: 15-30 minutes typical
- **Migration Operations**: 5-15 minutes typical
- **Support Response**: 4 hours business days
- **Service Availability**: 99.9% uptime SLA

---

## 🔄 **What's Next?**

### **Future Releases**

#### **v1.2.0 (Q1 2025)**
- Web-based GUI for account management
- Enhanced reporting and analytics
- Multi-region account support
- Advanced cost optimization features

#### **v2.0.0 (Q2 2025)**
- Self-service portal
- Resource provisioning within accounts
- Advanced automation workflows
- AI-powered recommendations

### **Getting Started Checklist**

- [ ] Install LZaaS CLI using the installation guide
- [ ] Configure AWS credentials (SSO recommended)
- [ ] Run `lzaas info` to verify connectivity
- [ ] List available templates with `lzaas template list`
- [ ] Create your first account with `lzaas account create`
- [ ] Monitor progress with `lzaas status`
- [ ] Explore migration capabilities with `lzaas migrate list-ous`

---

**🎉 You're ready to start using LZaaS! Begin with `lzaas info` to check your setup.**

*For technical support or questions about this documentation, contact your LZaaS administrator.*

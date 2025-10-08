# LZaaS Migration Guide

🔄 **Complete Guide for Existing Account Management and OU Migrations**

*LZaaS Version: 1.1.0 | Date: October 01, 2025*
*LZaaS CLI Version: 1.0.0 | Date: October 01, 2025*

## Overview

This guide addresses the critical gap in existing account management that was identified in the original LZaaS solution. The enhanced LZaaS CLI now provides comprehensive tools for managing existing AWS accounts, including the specific use case of moving the **Spitzkop account** to the **Sandbox OU**.

## 🎯 Migration Scenarios

### Scenario 1: Direct OU Move (Recommended for Spitzkop)
**Use Case**: Move existing account to different OU without creating new account
**Command**: `lzaas migrate existing-ou`
**Best For**: Simple OU reorganization, compliance requirements

### Scenario 2: AFT-Managed Migration
**Use Case**: Create new AFT-managed account and migrate resources
**Command**: `lzaas migrate account`
**Best For**: Full Landing Zone compliance, resource modernization

## 🚀 Quick Start: Spitzkop Account Migration

### Step 1: List Available OUs
```bash
# First, see all available Organizational Units
lzaas migrate list-ous

# Expected output:
# 🏗️ Root: Root (r-xxxx)
# ├─ Core (ou-xxxx-core)
# ├─ Security (ou-xxxx-security)
# ├─ Sandbox (ou-xxxx-sandbox)
# ├─ Production (ou-xxxx-prod)
# └─ Development (ou-xxxx-dev)
```

### Step 2: Dry Run the Migration
```bash
# Test the migration without making changes
lzaas migrate existing-ou \
  --account-id 198610579545 \
  --target-ou Sandbox \
  --dry-run

# This shows exactly what would be executed
```

### Step 3: Execute the Migration
```bash
# Move Spitzkop account to Sandbox OU
lzaas migrate existing-ou \
  --account-id 198610579545 \
  --target-ou Sandbox

# Confirm when prompted
```

### Step 4: Verify the Move
```bash
# Check the account is in the correct OU
aws organizations list-parents --child-id 198610579545
```

## 📋 Complete Migration Commands Reference

### 1. Direct OU Migration Commands

#### Basic OU Move
```bash
lzaas migrate existing-ou --account-id <ACCOUNT_ID> --target-ou <OU_NAME>
```

#### With Dry Run
```bash
lzaas migrate existing-ou --account-id <ACCOUNT_ID> --target-ou <OU_NAME> --dry-run
```

#### List All OUs
```bash
lzaas migrate list-ous
```

### 2. AFT-Managed Migration Commands

#### Create New AFT Account (Migration)
```bash
lzaas migrate account \
  --account-id <EXISTING_ID> \
  --account-name "Account Name" \
  --email account@company.com \
  --target-ou <OU_NAME> \
  --client-id <CLIENT>
```

#### With Dry Run
```bash
lzaas migrate account \
  --account-id <EXISTING_ID> \
  --account-name "Account Name" \
  --email account@company.com \
  --target-ou <OU_NAME> \
  --client-id <CLIENT> \
  --dry-run
```

## 🔧 Technical Implementation Details

### Direct OU Move Process
1. **Validation**: Account ID format, OU existence
2. **Discovery**: Current account location and details
3. **OU Resolution**: Find target OU by name
4. **Execution**: AWS Organizations `move_account` API
5. **Verification**: Confirm successful move

### AFT Migration Process
1. **Request Creation**: Generate migration request in DynamoDB
2. **AFT Pipeline**: Trigger Account Factory pipeline
3. **New Account**: Create AFT-managed account in target OU
4. **Resource Migration**: Manual or automated resource transfer
5. **Decommission**: Optional cleanup of original account

## 🛡️ Security and Permissions

### Required IAM Permissions

#### For Direct OU Moves
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "organizations:DescribeAccount",
        "organizations:ListParents",
        "organizations:ListOrganizationalUnitsForParent",
        "organizations:ListRoots",
        "organizations:MoveAccount"
      ],
      "Resource": "*"
    }
  ]
}
```

#### For AFT Migrations
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/aft-request-*"
    }
  ]
}
```

## 📊 Migration Decision Matrix

| Criteria | Direct OU Move | AFT Migration |
|----------|----------------|---------------|
| **Speed** | ⚡ Immediate | 🕐 15-30 minutes |
| **Complexity** | 🟢 Simple | 🟡 Moderate |
| **AFT Compliance** | ❌ No | ✅ Yes |
| **Resource Impact** | 🟢 None | 🟡 Manual migration needed |
| **Rollback** | 🟢 Easy | 🔴 Complex |
| **Cost** | 🟢 Free | 💰 New account costs |

## 🎯 Spitzkop Account Migration: Step-by-Step

### Current State Analysis
```bash
# Check current account details
aws organizations describe-account --account-id 198610579545

# Check current OU
aws organizations list-parents --child-id 198610579545
```

### Migration Execution
```bash
# 1. Verify target OU exists
lzaas migrate list-ous | grep -i sandbox

# 2. Dry run the migration
lzaas migrate existing-ou \
  --account-id 198610579545 \
  --target-ou Sandbox \
  --dry-run

# 3. Execute the migration
lzaas migrate existing-ou \
  --account-id 198610579545 \
  --target-ou Sandbox

# 4. Verify success
aws organizations list-parents --child-id 198610579545
```

### Post-Migration Checklist
- [ ] Account appears in Sandbox OU in AWS Console
- [ ] Service Control Policies (SCPs) applied correctly
- [ ] IAM permissions and access patterns verified
- [ ] Billing and cost allocation updated
- [ ] Documentation and inventory systems updated
- [ ] Team notifications sent

## 🔄 Alternative: Terraform-Style Migration

If you prefer the original Terraform approach you mentioned, you can still use it alongside LZaaS:

### Manual DynamoDB Entry (Not Recommended)
```json
{
  "id": "spitzkop-migration-2025-01-10",
  "control_tower_parameters": {
    "AccountEmail": "eugene.ngontang@spitzkop.io",
    "AccountName": "Spitzkop",
    "ManagedOrganizationalUnit": "Sandbox"
  },
  "account_tags": {
    "client": "Spitzkop",
    "environment": "sandbox",
    "migration": "true",
    "original_account_id": "198610579545"
  }
}
```

### LZaaS CLI Equivalent (Recommended)
```bash
lzaas migrate account \
  --account-id 198610579545 \
  --account-name "Spitzkop" \
  --email "eugene.ngontang@spitzkop.io" \
  --target-ou Sandbox \
  --client-id spitzkop
```

## 🚨 Important Considerations

### Direct OU Move Limitations
- **SCPs**: New policies may apply immediately
- **Cross-Account Access**: May be affected by OU change
- **Billing**: Cost allocation may change
- **Compliance**: Ensure new OU meets requirements

### AFT Migration Considerations
- **Dual Accounts**: Temporary period with both accounts
- **Resource Migration**: Manual effort required
- **DNS/Networking**: Update configurations
- **Access Management**: Reconfigure IAM and SSO

## 🔍 Troubleshooting

### Common Issues

#### "Target OU not found"
```bash
# List all OUs to find correct name
lzaas migrate list-ous

# OU names are case-sensitive
# Use exact name from the list
```

#### "Insufficient permissions"
```bash
# Check your AWS credentials
aws sts get-caller-identity

# Verify IAM permissions for Organizations
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names organizations:MoveAccount \
  --resource-arns "*"
```

#### "Account move failed"
```bash
# Check for SCP restrictions
aws organizations list-policies-for-target \
  --target-id 198610579545 \
  --filter SERVICE_CONTROL_POLICY

# Verify account is not the management account
aws organizations describe-organization
```

## 📈 Monitoring and Validation

### Post-Migration Verification
```bash
# 1. Verify OU placement
aws organizations list-parents --child-id 198610579545

# 2. Check applied SCPs
aws organizations list-policies-for-target \
  --target-id 198610579545 \
  --filter SERVICE_CONTROL_POLICY

# 3. Test account access
aws sts assume-role \
  --role-arn "arn:aws:iam::198610579545:role/OrganizationAccountAccessRole" \
  --role-session-name "migration-test"
```

### Monitoring Commands
```bash
# Check account status
lzaas status overview

# Monitor AFT pipeline (if using AFT migration)
lzaas status pipelines

# List all migration requests
lzaas account list --client-id spitzkop
```

## 🎉 Success Criteria

### Direct OU Move Success
- ✅ Account appears in target OU
- ✅ SCPs applied correctly
- ✅ Access patterns maintained
- ✅ No service disruptions

### AFT Migration Success
- ✅ New account created in target OU
- ✅ AFT customizations applied
- ✅ Resources migrated successfully
- ✅ Original account decommissioned

## 📞 Support and Next Steps

### Getting Help
- **CLI Help**: `lzaas migrate --help`
- **Verbose Output**: `lzaas --verbose migrate existing-ou ...`
- **Documentation**: Review `LZAAS_AUTOMATION_STRATEGY.md`

### Future Enhancements (v1.2.0)
- **Automated Resource Migration**: AWS Application Migration Service integration
- **Batch Migrations**: Multiple accounts at once
- **Migration Templates**: Predefined migration patterns
- **Rollback Automation**: Automated rollback procedures

---

## 🔗 Related Documentation

- **LZaaS CLI Guide**: `lzaas-cli/README.md`
- **Release Notes**: `LZAAS_V1_1_0_RELEASE_NOTES.md`
- **Architecture**: `LZAAS_AUTOMATION_STRATEGY.md`
- **AFT Setup**: `AFT_DEPLOYMENT_VERIFICATION.md`

---

**Ready to migrate?** Start with a dry run to see exactly what will happen:

```bash
lzaas migrate existing-ou --account-id 198610579545 --target-ou Sandbox --dry-run
```

For questions or support, contact the platform team or review the comprehensive documentation provided.

"""
AFT Manager - Core AWS Account Factory operations
Handles DynamoDB operations, GitHub integration, and AFT pipeline management
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
import yaml
from botocore.exceptions import ClientError, NoCredentialsError

from lzaas.core.models import AccountRequest, AFTStatus

# Set up logger
logger = logging.getLogger(__name__)


class AFTManager:
    """Manages AFT operations and DynamoDB interactions"""

    def __init__(self, profile: str = "default", region: str = "eu-west-3"):
        self.profile = profile
        self.region = region
        self.table_name = "lzaas-account-requests"

        # Initialize AWS clients
        try:
            session = boto3.Session(profile_name=profile, region_name=region)
            self.dynamodb = session.resource("dynamodb")
            self.codepipeline = session.client("codepipeline")
            self.stepfunctions = session.client("stepfunctions")
            self.s3 = session.client("s3")
        except (NoCredentialsError, ClientError) as e:
            raise Exception(f"AWS authentication failed: {str(e)}")

    def _get_table(self):
        """Get or create DynamoDB table"""
        try:
            table = self.dynamodb.Table(self.table_name)
            # Test table access
            table.load()
            return table
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Table doesn't exist, create it
                return self._create_table()
            else:
                raise Exception(f"DynamoDB error: {str(e)}")

    def _create_table(self):
        """Create DynamoDB table for account requests"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "request_id", "AttributeType": "S"},
                    {"AttributeName": "client_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "client-status-index",
                        "KeySchema": [
                            {"AttributeName": "client_id", "KeyType": "HASH"},
                            {"AttributeName": "status", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "BillingMode": "PAY_PER_REQUEST",
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )

            # Wait for table to be created
            table.wait_until_exists()
            return table

        except ClientError as e:
            raise Exception(f"Failed to create DynamoDB table: {str(e)}")

    def create_account_request(self, account_request: AccountRequest) -> Dict[str, Any]:
        """Create a new account request"""
        try:
            table = self._get_table()

            # Store in DynamoDB
            table.put_item(Item=account_request.to_dict())

            # TODO: Create GitHub repository files for AFT
            # This would involve:
            # 1. Creating account request YAML file
            # 2. Committing to aft-account-request repository
            # 3. Triggering AFT pipeline

            return {
                "success": True,
                "request_id": account_request.request_id,
                "message": "Account request created successfully",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_account_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get account request by ID"""
        try:
            table = self._get_table()
            response = table.get_item(Key={"request_id": request_id})
            return response.get("Item")
        except Exception as e:
            raise Exception(f"Failed to get account request: {str(e)}")

    def list_account_requests(
        self,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List account requests with optional filters"""
        try:
            table = self._get_table()

            if client_id and status:
                # Use GSI for client_id and status filter
                response = table.query(
                    IndexName="client-status-index",
                    KeyConditionExpression="client_id = :client_id AND #status = :status",
                    ExpressionAttributeNames={"#status": "status"},
                    ExpressionAttributeValues={
                        ":client_id": client_id,
                        ":status": status,
                    },
                    Limit=limit,
                )
                return response.get("Items", [])
            elif client_id:
                # Use GSI for client_id filter only
                response = table.query(
                    IndexName="client-status-index",
                    KeyConditionExpression="client_id = :client_id",
                    ExpressionAttributeValues={":client_id": client_id},
                    Limit=limit,
                )
                return response.get("Items", [])
            else:
                # Scan table (less efficient but works for all cases)
                scan_kwargs: Dict[str, Any] = {"Limit": limit}

                if status:
                    scan_kwargs["FilterExpression"] = "#status = :status"
                    scan_kwargs["ExpressionAttributeNames"] = {"#status": "status"}
                    scan_kwargs["ExpressionAttributeValues"] = {":status": status}

                response = table.scan(**scan_kwargs)
                return response.get("Items", [])

        except Exception as e:
            raise Exception(f"Failed to list account requests: {str(e)}")

    def update_account_request(
        self, request_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update account request"""
        try:
            table = self._get_table()

            # Add updated timestamp
            updates["updated_date"] = datetime.utcnow().isoformat()

            # Build update expression
            update_expression: str = "SET "
            expression_values: Dict[str, Any] = {}
            expression_names: Dict[str, str] = {}

            for key, value in updates.items():
                if key == "status":
                    # Status is a reserved word in DynamoDB
                    update_expression += "#status = :status, "
                    expression_names["#status"] = "status"
                    expression_values[":status"] = value
                else:
                    update_expression += f"{key} = :{key}, "
                    expression_values[f":{key}"] = value

            # Remove trailing comma and space
            update_expression = update_expression.rstrip(", ")

            kwargs = {
                "Key": {"request_id": request_id},
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expression_values,
                "ReturnValues": "ALL_NEW",
            }

            if expression_names:
                kwargs["ExpressionAttributeNames"] = expression_names

            response = table.update_item(**kwargs)

            return {"success": True, "updated_item": response.get("Attributes")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_account_request(self, request_id: str) -> Dict[str, Any]:
        """Delete account request"""
        try:
            table = self._get_table()
            table.delete_item(Key={"request_id": request_id})

            return {"success": True, "message": f"Account request {request_id} deleted"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_aft_status(self, request_id: str) -> Optional[AFTStatus]:
        """Get AFT pipeline status for a request"""
        try:
            # This would query AFT's DynamoDB tables or Step Functions
            # For now, return mock status based on our request
            request = self.get_account_request(request_id)
            if not request:
                return None

            # Mock AFT status - in real implementation, this would query AFT resources
            return AFTStatus(
                request_id=request_id,
                pipeline_status=str(request.get("status", "unknown")),
                account_id=(
                    str(request.get("account_id"))
                    if request.get("account_id")
                    else None
                ),
                last_updated=(
                    str(request.get("updated_date"))
                    if request.get("updated_date")
                    else None
                ),
            )

        except Exception as e:
            raise Exception(f"Failed to get AFT status: {str(e)}")

    def create_aft_repository_files(
        self, account_request: AccountRequest
    ) -> Dict[str, Any]:
        """Create AFT repository files for account request"""
        try:
            # Generate AFT-compatible YAML
            aft_request = account_request.to_aft_request()

            # Create account request file content
            account_file_content = yaml.dump(aft_request, default_flow_style=False)

            # TODO: Implement GitHub API integration to:
            # 1. Create/update file in aft-account-request repository
            # 2. Commit changes
            # 3. Trigger AFT pipeline

            return {
                "success": True,
                "file_content": account_file_content,
                "message": "AFT repository files prepared (GitHub integration pending)",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_aft_pipelines(self) -> List[Dict[str, Any]]:
        """List AFT CodePipeline executions"""
        try:
            # Get AFT-related pipelines
            pipelines = []

            response = self.codepipeline.list_pipelines()
            for pipeline in response.get("pipelines", []):
                pipeline_name = pipeline["name"]
                if "aft" in pipeline_name.lower():
                    # Get pipeline execution history
                    executions = self.codepipeline.list_pipeline_executions(
                        pipelineName=pipeline_name, maxResults=5
                    )

                    pipelines.append(
                        {
                            "name": pipeline_name,
                            "executions": executions.get(
                                "pipelineExecutionSummaries", []
                            ),
                        }
                    )

            return pipelines

        except Exception as e:
            raise Exception(f"Failed to list AFT pipelines: {str(e)}")

    # Migration-specific methods
    def find_account_by_name(self, account_name: str) -> Optional[Dict[str, Any]]:
        """Find AWS account by name using Organizations API"""
        try:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
            organizations = session.client("organizations")

            # List all accounts in the organization
            paginator = organizations.get_paginator("list_accounts")

            for page in paginator.paginate():
                for account in page["Accounts"]:
                    if account["Name"].lower() == account_name.lower():
                        return account

            return None

        except Exception as e:
            raise Exception(f"Failed to find account by name: {str(e)}")

    def find_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Find AWS account by ID using Organizations API"""
        try:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
            organizations = session.client("organizations")

            # Get account details
            response = organizations.describe_account(AccountId=account_id)
            return response.get("Account")

        except ClientError as e:
            if e.response["Error"]["Code"] == "AccountNotFoundException":
                return None
            raise Exception(f"Failed to find account by ID: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to find account by ID: {str(e)}")

    def find_ou_by_name(self, ou_name: str) -> Optional[Dict[str, Any]]:
        """Find Organizational Unit by name"""
        try:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
            organizations = session.client("organizations")

            # Get root ID first
            roots = organizations.list_roots()["Roots"]
            if not roots:
                return None

            root_id = roots[0]["Id"]

            # Search for OU recursively
            def search_ou_recursive(parent_id: str) -> Optional[Dict[str, Any]]:
                try:
                    paginator = organizations.get_paginator(
                        "list_organizational_units_for_parent"
                    )

                    for page in paginator.paginate(ParentId=parent_id):
                        for ou in page["OrganizationalUnits"]:
                            if ou["Name"].lower() == ou_name.lower():
                                return ou

                            # Search recursively in child OUs
                            child_result = search_ou_recursive(ou["Id"])
                            if child_result:
                                return child_result

                    return None
                except Exception:
                    return None

            return search_ou_recursive(root_id)

        except Exception as e:
            raise Exception(f"Failed to find OU by name: {str(e)}")

    def get_account_parent(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get the parent OU or root for an account"""
        try:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
            organizations = session.client("organizations")

            # List parents for the account
            response = organizations.list_parents(ChildId=account_id)
            parents = response.get("Parents", [])

            if not parents:
                return None

            parent = parents[0]  # Account should have only one parent

            # Get parent details
            if parent["Type"] == "ROOT":
                roots = organizations.list_roots()["Roots"]
                for root in roots:
                    if root["Id"] == parent["Id"]:
                        return {"Id": root["Id"], "Name": "Root", "Type": "ROOT"}
            elif parent["Type"] == "ORGANIZATIONAL_UNIT":
                ou_response = organizations.describe_organizational_unit(
                    OrganizationalUnitId=parent["Id"]
                )
                ou = ou_response["OrganizationalUnit"]
                return {
                    "Id": ou["Id"],
                    "Name": ou["Name"],
                    "Type": "ORGANIZATIONAL_UNIT",
                }

            return parent

        except Exception as e:
            raise Exception(f"Failed to get account parent: {str(e)}")

    def get_organizational_structure(self) -> Dict[str, Any]:
        """Get the complete organizational structure"""
        try:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
            organizations = session.client("organizations")

            # Get root
            roots = organizations.list_roots()["Roots"]
            if not roots:
                return {"root": None, "ous": []}

            root = roots[0]

            # Get all OUs recursively
            def get_ous_recursive(
                parent_id: str, level: int = 0
            ) -> List[Dict[str, Any]]:
                ous = []
                try:
                    paginator = organizations.get_paginator(
                        "list_organizational_units_for_parent"
                    )

                    for page in paginator.paginate(ParentId=parent_id):
                        for ou in page["OrganizationalUnits"]:
                            ou_info = {
                                "id": ou["Id"],
                                "name": ou["Name"],
                                "level": level,
                            }
                            ous.append(ou_info)

                            # Get child OUs
                            child_ous = get_ous_recursive(ou["Id"], level + 1)
                            ous.extend(child_ous)

                except Exception as e:
                    # Log the error but continue processing other OUs
                    # This is typically due to permission issues or API throttling
                    logger.debug(
                        f"Failed to list organizational units for parent {parent_id}: {e}"
                    )

                return ous

            all_ous = get_ous_recursive(root["Id"])

            return {"root": {"id": root["Id"], "name": root["Name"]}, "ous": all_ous}

        except Exception as e:
            raise Exception(f"Failed to get organizational structure: {str(e)}")

    def prepare_migration_changes(
        self,
        account_info: Dict[str, Any],
        target_ou: Dict[str, Any],
        current_parent: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare Git repository changes for account migration with corrected architecture"""
        try:
            # Generate the changes that would be made to repository files
            account_name = account_info["Name"]
            account_id = account_info["Id"]
            target_ou_name = target_ou["Name"]

            # Use account ID as unique identifier (no client name assumptions)
            changes = {
                "files": {
                    f"terraform/live/account-factory/lzaas-account-{account_id}.tf": "create/update",
                    f"terraform/live/account-factory/lzaas-metadata.tf": "update",
                    f"terraform/live/account-factory/.lzaas-managed": "update",
                },
                "terraform_content": self._generate_account_terraform(
                    account_info, target_ou
                ),
                "metadata_content": self._generate_lzaas_metadata(
                    account_info, target_ou
                ),
                "managed_files_content": self._generate_managed_files_list(account_id),
                "terraform_preview": self._generate_terraform_preview(
                    account_info, target_ou
                ),
                "pr_details": {
                    "branch_name": f"migrate-{account_id}-to-{target_ou_name.lower()}",
                    "title": f"Migrate account {account_id} ({account_name}) to {target_ou_name} OU",
                    "description": f"""
# Account Migration

**Account**: {account_name} ({account_id})
**Source**: {current_parent.get('Name', 'Unknown')}
**Target**: {target_ou_name}

## Changes
- Create/update `lzaas-account-{account_id}.tf` with new OU assignment
- Update LZaaS metadata and tracking files
- Trigger AFT pipeline for account migration

## Files Modified
- `terraform/live/account-factory/lzaas-account-{account_id}.tf`
- `terraform/live/account-factory/lzaas-metadata.tf`
- `terraform/live/account-factory/.lzaas-managed`

## Migration Process
This PR will trigger the AFT pipeline to move the account to the new OU.
The migration will be processed automatically when this PR is merged.

Generated by LZaaS CLI v{self._get_cli_version()}
                    """,
                },
            }

            return changes

        except Exception as e:
            raise Exception(f"Failed to prepare migration changes: {str(e)}")

    def _generate_account_terraform(
        self, account_info: Dict[str, Any], target_ou: Dict[str, Any]
    ) -> str:
        """Generate Terraform content for account-specific file"""
        account_name = account_info["Name"]
        account_id = account_info["Id"]
        target_ou_name = target_ou["Name"]
        timestamp = datetime.utcnow().isoformat()
        operation_id = self._generate_operation_id()

        return f"""# lzaas-account-{account_id}.tf
# Generated by LZaaS CLI - DO NOT EDIT MANUALLY
# Account: {account_name} ({account_id})
# Last Updated: {timestamp}

resource "aws_organizations_account" "account_{account_id}" {{
  name      = "{account_name}"
  email     = "admin@{account_name.lower()}.example.com"
  parent_id = "{target_ou['Id']}"  # {target_ou_name} OU

  tags = {{
    AccountId     = "{account_id}"
    AccountName   = "{account_name}"
    Environment   = "{target_ou_name.lower()}"
    ManagedBy     = "LZaaS"
    LastMigration = "{timestamp}"
    OperationId   = "{operation_id}"
  }}
}}

# Output for monitoring and reference
output "account_{account_id}_details" {{
  description = "Account details for {account_name} ({account_id})"
  value = {{
    account_id   = aws_organizations_account.account_{account_id}.id
    account_name = aws_organizations_account.account_{account_id}.name
    parent_ou    = aws_organizations_account.account_{account_id}.parent_id
    environment  = "{target_ou_name.lower()}"
  }}
}}
"""

    def _generate_lzaas_metadata(
        self, account_info: Dict[str, Any], target_ou: Dict[str, Any]
    ) -> str:
        """Generate LZaaS metadata file content"""
        account_name = account_info["Name"]
        account_id = account_info["Id"]
        timestamp = datetime.utcnow().isoformat()
        operation_id = self._generate_operation_id()

        return f"""# LZaaS Operational Metadata
# This file tracks LZaaS CLI operations and should not be edited manually

locals {{
  lzaas_operations = {{
    last_migration = {{
      account_id    = "{account_id}"
      account_name  = "{account_name}"
      target_ou     = "{target_ou['Name']}"
      target_ou_id  = "{target_ou['Id']}"
      timestamp     = "{timestamp}"
      cli_version   = "{self._get_cli_version()}"
      operation_id  = "{operation_id}"
    }}

    managed_accounts = [
      "{account_id}"
      # Additional account IDs will be added here as they are managed by LZaaS
    ]
  }}
}}

# Output operational metadata for monitoring
output "lzaas_last_operation" {{
  description = "Details of the last LZaaS operation"
  value       = local.lzaas_operations.last_migration
}}
"""

    def _generate_managed_files_list(self, account_id: str) -> str:
        """Generate the .lzaas-managed file content"""
        timestamp = datetime.utcnow().isoformat()

        return f"""# Files managed by LZaaS CLI - DO NOT EDIT MANUALLY
# This file tracks which files are automatically managed by the LZaaS CLI
# to prevent Git conflicts between human and automated changes

managed_files:
  - lzaas-account-{account_id}.tf
  - lzaas-metadata.tf
  - .lzaas-managed

last_updated: "{timestamp}"
cli_version: "{self._get_cli_version()}"

# Guidelines for developers:
# - Never manually edit files listed above
# - Use 'lzaas' commands to modify account configurations
# - Human-maintained files: main.tf, variables.tf, terraform.tfvars
# - For questions about LZaaS-managed files, use: lzaas docs
"""

    def _generate_terraform_preview(
        self, account_info: Dict[str, Any], target_ou: Dict[str, Any]
    ) -> str:
        """Generate Terraform preview for display purposes"""
        account_name = account_info["Name"]
        account_id = account_info["Id"]
        target_ou_name = target_ou["Name"]
        timestamp = datetime.utcnow().isoformat()

        return f"""
# Account Migration: {account_name} -> {target_ou_name}
# File: lzaas-account-{account_id}.tf

resource "aws_organizations_account" "account_{account_id}" {{
  name      = "{account_name}"
  email     = "admin@{account_name.lower()}.example.com"
  parent_id = "{target_ou['Id']}"

  tags = {{
    AccountId     = "{account_id}"
    AccountName   = "{account_name}"
    Environment   = "{target_ou_name.lower()}"
    ManagedBy     = "LZaaS"
    LastMigration = "{timestamp}"
  }}
}}
"""

    def _generate_operation_id(self) -> str:
        """Generate a unique operation ID for tracking"""
        import uuid

        return str(uuid.uuid4())[:8]

    def execute_git_migration(
        self,
        account_info: Dict[str, Any],
        target_ou: Dict[str, Any],
        repo_changes: Dict[str, Any],
        github_config: Dict[str, Any],
        aft_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute Git-based migration by creating PR (v1.0.0 - Mock Implementation)"""
        try:
            # v1.0.0 MOCK IMPLEMENTATION
            # This provides a complete preview of what would happen without actual changes
            # Real GitHub integration will be implemented in the next release

            account_name = account_info["Name"]
            account_id = account_info["Id"]
            target_ou_name = target_ou["Name"]
            branch_name = repo_changes["pr_details"]["branch_name"]

            # MOCK RESPONSE - Beautiful output, no actual repository modifications
            mock_pr_url = f"https://github.com/{github_config['organization']}/{aft_config['account_request_repo_name']}/pull/123"
            mock_commit_sha = "abc123def456"

            return {
                "success": True,  # Success for v1.0.0 mock functionality
                "mock": True,  # Clearly indicate this is mock behavior
                "branch_name": branch_name,
                "pr_url": mock_pr_url,
                "commit_sha": mock_commit_sha,
                "message": f"✅ Migration plan prepared for {account_name} ({account_id}) -> {target_ou_name}",
                "note": "v1.0.0: Dry-run and planning functionality complete. GitHub integration coming in next release.",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_migration_status(
        self, account_id: Optional[str] = None, ou_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get migration status and ongoing operations"""
        try:
            # Mock migration status data
            # In real implementation, this would query AFT DynamoDB tables

            ongoing_migrations: List[Dict[str, Any]] = []
            recent_migrations: List[Dict[str, Any]] = []

            # Mock some data for demonstration
            if (
                not account_id
            ):  # Only show mock data when not filtering by specific account
                recent_migrations = [
                    {
                        "account_name": "example-dev",
                        "account_id": "123456789012",
                        "source_ou": "Development",
                        "target_ou": "Sandbox",
                        "status": "SUCCESS",
                        "completed_at": "2025-01-07T10:30:00Z",
                    }
                ]

            return {
                "ongoing_migrations": ongoing_migrations,
                "recent_migrations": recent_migrations,
            }

        except Exception as e:
            raise Exception(f"Failed to get migration status: {str(e)}")

    def _get_cli_version(self) -> str:
        """Get the current CLI version dynamically"""
        try:
            from lzaas import __version__

            return __version__
        except ImportError:
            return "unknown"

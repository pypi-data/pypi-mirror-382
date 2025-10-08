#!/usr/bin/env python3
"""
LZaaS System Health Checker
Real-time status checking for AFT infrastructure and integrations
"""

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import boto3
import requests

from lzaas.cli.commands.config import config_manager


class SystemHealthChecker:
    """Checks the health of LZaaS system components"""

    def __init__(self):
        self.config = config_manager.load_config()
        self.credentials = config_manager.load_credentials()

    def check_aws_connectivity(self) -> Tuple[str, str, str]:
        """Check AWS connectivity and credentials"""
        try:
            # Use configured credentials if available
            if "aws" in self.credentials:
                session = boto3.Session(
                    aws_access_key_id=self.credentials["aws"]["access_key_id"],
                    aws_secret_access_key=self.credentials["aws"]["secret_access_key"],
                    aws_session_token=self.credentials["aws"].get("session_token"),
                    region_name=self.config.get("general", {}).get(
                        "default_region", "us-east-1"
                    ),
                )
            else:
                # Fall back to default credential chain (includes SSO)
                session = boto3.Session(
                    profile_name=self.config.get("general", {}).get(
                        "aws_profile", "default"
                    ),
                    region_name=self.config.get("general", {}).get(
                        "default_region", "us-east-1"
                    ),
                )

            # Test STS to verify credentials
            sts = session.client("sts")
            identity = sts.get_caller_identity()

            # Check if using SSO
            profile_name = session.profile_name or "default"
            auth_method = "SSO" if self._is_sso_profile(profile_name) else "Credentials"

            return (
                "✅ Connected",
                f"Account: {identity.get('Account', 'Unknown')} ({auth_method})",
                "green",
            )

        except Exception as e:
            error_msg = str(e)
            if "sso" in error_msg.lower() or "token" in error_msg.lower():
                return "❌ Failed", "SSO token expired - run 'aws sso login'", "red"
            return "❌ Failed", f"Error: {error_msg[:50]}...", "red"

    def _is_sso_profile(self, profile_name: str) -> bool:
        """Check if the AWS profile uses SSO"""
        try:
            import configparser
            import os

            config_path = os.path.expanduser("~/.aws/config")
            if not os.path.exists(config_path):
                return False

            config = configparser.ConfigParser()
            config.read(config_path)

            section_name = (
                f"profile {profile_name}" if profile_name != "default" else "default"
            )
            if section_name in config:
                return "sso_start_url" in config[section_name]
            return False
        except Exception:
            return False

    def check_dynamodb_table(self) -> Tuple[str, str, str]:
        """Check AFT DynamoDB table accessibility"""
        try:
            if "aws" in self.credentials:
                session = boto3.Session(
                    aws_access_key_id=self.credentials["aws"]["access_key_id"],
                    aws_secret_access_key=self.credentials["aws"]["secret_access_key"],
                    aws_session_token=self.credentials["aws"].get("session_token"),
                    region_name=self.config.get("general", {}).get(
                        "default_region", "us-east-1"
                    ),
                )
            else:
                session = boto3.Session(
                    region_name=self.config.get("general", {}).get(
                        "default_region", "us-east-1"
                    )
                )

            dynamodb = session.client("dynamodb")

            # Try to list tables to verify access
            response = dynamodb.list_tables()
            tables = response.get("TableNames", [])

            # Look for AFT-related tables
            aft_tables = [
                t for t in tables if "aft" in t.lower() or "account" in t.lower()
            ]

            if aft_tables:
                return "✅ Ready", f"Found {len(aft_tables)} AFT tables", "green"
            else:
                return "⚠️ Warning", "No AFT tables found", "yellow"

        except Exception as e:
            return "❌ Failed", f"Error: {str(e)[:50]}...", "red"

    def check_github_integration(self) -> Tuple[str, str, str]:
        """Check GitHub integration status"""
        try:
            github_config = self.config.get("github", {})
            github_creds = self.credentials.get("github", {})

            if not github_config.get("organization"):
                return "⚠️ Pending", "Organization not configured", "yellow"

            if not github_creds.get("token"):
                return "⚠️ Pending", "Token not configured", "yellow"

            # Test GitHub API connectivity
            headers = {
                "Authorization": f"token {github_creds['token']}",
                "Accept": "application/vnd.github.v3+json",
            }

            org = github_config["organization"]
            response = requests.get(
                f"https://api.github.com/orgs/{org}", headers=headers, timeout=10
            )

            if response.status_code == 200:
                return "✅ Connected", f"Organization: {org}", "green"
            elif response.status_code == 401:
                return "❌ Failed", "Invalid token", "red"
            elif response.status_code == 404:
                return "❌ Failed", "Organization not found", "red"
            else:
                return "⚠️ Warning", f"HTTP {response.status_code}", "yellow"

        except requests.RequestException as e:
            return "❌ Failed", f"Network error: {str(e)[:30]}...", "red"
        except Exception as e:
            return "❌ Failed", f"Error: {str(e)[:30]}...", "red"

    def check_aft_infrastructure(self) -> Tuple[str, str, str]:
        """Check AFT infrastructure deployment status"""
        try:
            aft_config = self.config.get("aft", {})

            # Check if required AFT configuration is present
            required_fields = [
                "management_account_id",
                "aft_management_account_id",
                "account_request_repo_name",
            ]

            missing_fields = [f for f in required_fields if not aft_config.get(f)]

            if missing_fields:
                return "⚠️ Pending", f"Missing: {', '.join(missing_fields)}", "yellow"

            # If we have AWS connectivity, try to check CloudFormation stacks
            if "aws" in self.credentials:
                session = boto3.Session(
                    aws_access_key_id=self.credentials["aws"]["access_key_id"],
                    aws_secret_access_key=self.credentials["aws"]["secret_access_key"],
                    aws_session_token=self.credentials["aws"].get("session_token"),
                    region_name=self.config.get("general", {}).get(
                        "default_region", "us-east-1"
                    ),
                )

                cf = session.client("cloudformation")

                # Look for AFT-related stacks
                response = cf.list_stacks(
                    StackStatusFilter=[
                        "CREATE_COMPLETE",
                        "UPDATE_COMPLETE",
                        "UPDATE_ROLLBACK_COMPLETE",
                    ]
                )

                aft_stacks = [
                    s
                    for s in response.get("StackSummaries", [])
                    if "aft" in s["StackName"].lower()
                ]

                if aft_stacks:
                    return "✅ Deployed", f"Found {len(aft_stacks)} AFT stacks", "green"
                else:
                    return "⚠️ Pending", "No AFT stacks found", "yellow"
            else:
                return "✅ Configured", "Configuration complete", "green"

        except Exception as e:
            return "❌ Failed", f"Error: {str(e)[:50]}...", "red"

    def check_template_system(self) -> Tuple[str, str, str]:
        """Check template system status"""
        try:
            # Check if template files exist
            template_dir = Path(__file__).parent.parent / "templates"

            if not template_dir.exists():
                return "❌ Failed", "Template directory not found", "red"

            template_files = list(template_dir.glob("*.json"))

            if not template_files:
                return "⚠️ Warning", "No template files found", "yellow"

            # Validate template files
            valid_templates = 0
            for template_file in template_files:
                try:
                    with open(template_file, "r") as f:
                        json.load(f)
                    valid_templates += 1
                except json.JSONDecodeError:
                    pass

            if valid_templates == len(template_files):
                return "✅ Ready", f"{valid_templates} templates available", "green"
            else:
                return (
                    "⚠️ Warning",
                    f"{valid_templates}/{len(template_files)} templates valid",
                    "yellow",
                )

        except Exception as e:
            return "❌ Failed", f"Error: {str(e)[:50]}...", "red"

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "aws_connectivity": self.check_aws_connectivity(),
            "aft_infrastructure": self.check_aft_infrastructure(),
            "github_integration": self.check_github_integration(),
            "dynamodb": self.check_dynamodb_table(),
            "template_system": self.check_template_system(),
        }

    def get_configuration_status(self) -> Dict[str, bool]:
        """Get configuration completeness status"""
        config_status = {}

        # Check general configuration
        general = self.config.get("general", {})
        config_status["general_configured"] = bool(
            general.get("default_region") and general.get("output_format")
        )

        # Check AFT configuration
        aft = self.config.get("aft", {})
        required_aft = [
            "management_account_id",
            "aft_management_account_id",
            "account_request_repo_name",
        ]
        config_status["aft_configured"] = all(aft.get(field) for field in required_aft)

        # Check GitHub configuration
        github = self.config.get("github", {})
        github_creds = self.credentials.get("github", {})
        config_status["github_configured"] = bool(
            github.get("organization") and github_creds.get("token")
        )

        # Check AWS credentials - consider both explicit credentials AND profiles
        has_explicit_creds = "aws" in self.credentials
        has_profile_config = bool(
            self.config.get("general", {}).get("aws_profile", "default") != "default"
        )
        config_status["aws_credentials"] = has_explicit_creds or has_profile_config

        return config_status

    def get_aws_auth_status(self) -> Tuple[str, str]:
        """Get AWS authentication status with detailed info"""
        has_explicit_creds = "aws" in self.credentials
        profile_name = self.config.get("general", {}).get("aws_profile", "default")

        if has_explicit_creds:
            return "✅ Configured", "Using explicit credentials"
        elif profile_name != "default":
            auth_method = "SSO" if self._is_sso_profile(profile_name) else "Profile"
            return "✅ Configured", f"Using {auth_method} profile: {profile_name}"
        else:
            return "⚠️ Using Default", "Using default credential chain"


# Global instance
system_checker = SystemHealthChecker()

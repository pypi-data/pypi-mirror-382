"""
Data Models for LZaaS CLI
Account requests, templates, and AFT operations
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AccountRequest:
    """Account request data model"""

    request_id: str
    template: str
    email: str
    name: str
    client_id: str
    ou: str
    vpc_cidr: str
    requested_by: str
    status: str
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    account_id: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.utcnow().isoformat()
        if not self.updated_date:
            self.updated_date = self.created_date

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DynamoDB storage"""
        return asdict(self)

    def to_aft_request(self) -> Dict[str, Any]:
        """Convert to AFT-compatible format"""
        return {
            "control_tower_parameters": {
                "AccountEmail": self.email,
                "AccountName": self.name,
                "ManagedOrganizationalUnit": self.ou,
                "SSOUserEmail": self.email,
                "SSOUserFirstName": "Admin",
                "SSOUserLastName": "User",
            },
            "account_tags": {
                "Environment": self.template.title(),
                "Owner": self.requested_by,
                "Client": self.client_id,
                "RequestId": self.request_id,
                "Template": self.template,
            },
            "account_customizations_name": f"{self.template}-customizations",
            "custom_fields": {
                "vpc_cidr": self.vpc_cidr,
                "template": self.template,
                "client_id": self.client_id,
                "request_id": self.request_id,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountRequest":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class AFTStatus:
    """AFT pipeline status information"""

    request_id: str
    pipeline_status: str
    account_id: Optional[str] = None
    pipeline_execution_id: Optional[str] = None
    last_updated: Optional[str] = None
    error_details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AccountTemplate:
    """Account template definition"""

    name: str
    description: str
    ou: str
    vpc_cidr: str
    features: list
    cost_estimate: str
    customizations: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Template definitions
ACCOUNT_TEMPLATES = {
    "dev": AccountTemplate(
        name="Development Account",
        description="Standard development environment with basic resources",
        ou="Development",
        vpc_cidr="10.1.0.0/16",
        features=["VPC Flow Logs", "CloudTrail", "Basic Monitoring"],
        cost_estimate="$50-100/month",
        customizations={
            "enable_flow_logs": True,
            "backup_retention": 7,
            "monitoring_level": "basic",
        },
    ),
    "prod": AccountTemplate(
        name="Production Account",
        description="Production environment with enhanced security and monitoring",
        ou="Production",
        vpc_cidr="10.2.0.0/16",
        features=["Enhanced Monitoring", "Backup Policies", "Security Controls"],
        cost_estimate="$200-500/month",
        customizations={
            "enable_flow_logs": True,
            "backup_retention": 30,
            "monitoring_level": "enhanced",
            "security_controls": True,
        },
    ),
    "sandbox": AccountTemplate(
        name="Sandbox Account",
        description="Experimental environment with minimal restrictions",
        ou="Sandbox",
        vpc_cidr="10.3.0.0/16",
        features=["Basic Resources", "Auto-cleanup Policies"],
        cost_estimate="$20-50/month",
        customizations={
            "enable_flow_logs": False,
            "backup_retention": 3,
            "monitoring_level": "minimal",
            "auto_cleanup": True,
        },
    ),
    "client": AccountTemplate(
        name="Client Account",
        description="Customizable account for external clients",
        ou="Clients",
        vpc_cidr="10.4.0.0/16",
        features=["Client Isolation", "Custom Branding", "Dedicated Support"],
        cost_estimate="$100-300/month",
        customizations={
            "enable_flow_logs": True,
            "backup_retention": 14,
            "monitoring_level": "standard",
            "client_isolation": True,
            "custom_branding": True,
        },
    ),
}

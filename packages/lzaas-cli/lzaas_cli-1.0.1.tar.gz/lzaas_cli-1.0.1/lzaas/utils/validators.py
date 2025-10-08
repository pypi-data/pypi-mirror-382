"""
Validation utilities for LZaaS CLI
Email, account names, and other input validation
"""

import ipaddress
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_account_name(name: str) -> bool:
    """Validate AWS account name format"""
    if not name:
        return False

    # AWS account name requirements:
    # - 1-50 characters
    # - Letters, numbers, spaces, hyphens, periods, apostrophes
    if len(name) < 1 or len(name) > 50:
        return False

    # Allow letters, numbers, spaces, hyphens, periods, apostrophes
    pattern = r"^[a-zA-Z0-9\s\-\.']+$"
    return bool(re.match(pattern, name))


def validate_vpc_cidr(cidr: str) -> bool:
    """Validate VPC CIDR block format"""
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)

        # AWS VPC CIDR requirements:
        # - Must be between /16 and /28
        # - Must be in private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
        prefix_length = network.prefixlen
        if prefix_length < 16 or prefix_length > 28:
            return False

        # Check if it's in private IP ranges
        private_ranges = [
            ipaddress.IPv4Network("10.0.0.0/8"),
            ipaddress.IPv4Network("172.16.0.0/12"),
            ipaddress.IPv4Network("192.168.0.0/16"),
        ]

        for private_range in private_ranges:
            if network.subnet_of(private_range):
                return True

        return False

    except (ipaddress.AddressValueError, ValueError):
        return False


def validate_request_id(request_id: str) -> bool:
    """Validate request ID format"""
    if not request_id:
        return False

    # Request ID format: template-YYYY-MM-DD-xxxxxxxx
    pattern = r"^(dev|prod|sandbox|client)-\d{4}-\d{2}-\d{2}-[a-f0-9]{8}$"
    return bool(re.match(pattern, request_id))


def validate_client_id(client_id: str) -> bool:
    """Validate client ID format"""
    if not client_id:
        return False

    # Client ID: alphanumeric, hyphens, underscores, 1-50 characters
    if len(client_id) < 1 or len(client_id) > 50:
        return False

    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, client_id))


def validate_ou_name(ou_name: str) -> bool:
    """Validate Organizational Unit name"""
    if not ou_name:
        return False

    # OU name: 1-128 characters, letters, numbers, spaces, hyphens, periods
    if len(ou_name) < 1 or len(ou_name) > 128:
        return False

    pattern = r"^[a-zA-Z0-9\s\-\.]+$"
    return bool(re.match(pattern, ou_name))


def sanitize_account_name(name: str) -> str:
    """Sanitize account name to meet AWS requirements"""
    if not name:
        return ""

    # Remove invalid characters
    sanitized = re.sub(r"[^a-zA-Z0-9\s\-\.']+", "", name)

    # Trim to 50 characters
    sanitized = sanitized[:50]

    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def get_validation_errors(data: dict) -> list:
    """Get all validation errors for account request data"""
    errors = []

    # Required fields
    required_fields = ["email", "name", "template"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    # Email validation
    if data.get("email") and not validate_email(data["email"]):
        errors.append("Invalid email address format")

    # Account name validation
    if data.get("name") and not validate_account_name(data["name"]):
        errors.append(
            "Invalid account name format (1-50 chars, letters/numbers/spaces/hyphens/periods/apostrophes only)"
        )

    # Template validation
    valid_templates = ["dev", "prod", "sandbox", "client"]
    if data.get("template") and data["template"] not in valid_templates:
        errors.append(f"Invalid template. Must be one of: {', '.join(valid_templates)}")

    # VPC CIDR validation
    if data.get("vpc_cidr") and not validate_vpc_cidr(data["vpc_cidr"]):
        errors.append("Invalid VPC CIDR (must be /16-/28 in private IP ranges)")

    # Client ID validation
    if data.get("client_id") and not validate_client_id(data["client_id"]):
        errors.append(
            "Invalid client ID format (1-50 chars, alphanumeric/hyphens/underscores only)"
        )

    # OU validation
    if data.get("ou") and not validate_ou_name(data["ou"]):
        errors.append(
            "Invalid OU name format (1-128 chars, letters/numbers/spaces/hyphens/periods only)"
        )

    return errors

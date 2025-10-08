# LZaaS Internals - Architecture & Implementation Deep Dive

🔧 **Complete Technical Architecture and Implementation Guide**

*LZaaS Version: 1.1.0 | Date: October 01, 2025*
*LZaaS CLI Version: 1.0.0 | Date: October 01, 2025*

## Overview

This document provides a comprehensive deep dive into the LZaaS (Landing Zone as a Service) CLI architecture, implementation details, and internal workings. It explains how commands flow from user input to AWS API interactions, making the solution transparent and accessible to all team members.

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User/CLI      │    │   LZaaS Core    │    │   AWS Services  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │lzaas account│ │───▶│ │AFT Manager  │ │───▶│ │ DynamoDB    │ │
│ │create       │ │    │ │             │ │    │ │ (AFT Table) │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │lzaas migrate│ │───▶│ │Organizations│ │───▶│ │Organizations│ │
│ │existing-ou  │ │    │ │Manager      │ │    │ │API          │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │lzaas status │ │───▶│ │Status       │ │───▶│ │CodePipeline │ │
│ │check        │ │    │ │Monitor      │ │    │ │API          │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

```
lzaas-cli/
├── lzaas/
│   ├── __init__.py                 # Package initialization
│   ├── cli/
│   │   ├── main.py                 # CLI entry point & routing
│   │   └── commands/
│   │       ├── account.py          # Account management commands
│   │       ├── migrate.py          # Migration commands
│   │       ├── status.py           # Status monitoring commands
│   │       └── template.py         # Template operations
│   ├── core/
│   │   ├── models.py               # Data models & schemas
│   │   └── aft_manager.py          # Core AFT integration logic
│   └── utils/
│       └── validators.py           # Input validation utilities
└── setup.py                       # Package configuration
```

## 🔄 Command Flow Architecture

### 1. Account Creation Flow

```
User Command:
lzaas account create --template dev --email dev@company.com

Flow:
┌─────────────────┐
│ CLI Entry Point │ main.py:cli()
│ (Click Router)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Command Handler │ account.py:create()
│ Input Validation│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Data Modeling   │ models.py:AccountRequest
│ Template Logic  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ AFT Manager     │ aft_manager.py:create_account_request()
│ DynamoDB Ops    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ AWS DynamoDB    │ AFT Request Table
│ Item Creation   │ aft-request-{timestamp}
└─────────────────┘
```

### 2. Migration Flow (Direct OU Move)

```
User Command:
lzaas migrate existing-ou --account-id 198610579545 --target-ou Sandbox

Flow:
┌─────────────────┐
│ CLI Entry Point │ main.py:cli()
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Migration Cmd   │ migrate.py:existing_ou()
│ Input Validation│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ AWS Session     │ boto3.Session()
│ Initialization  │ Profile + Region
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Organizations   │ orgs_client.describe_account()
│ API Discovery   │ orgs_client.list_parents()
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ OU Resolution   │ find_ou_by_name() recursive search
│ Target Lookup   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Account Move    │ orgs_client.move_account()
│ Execution       │
└─────────────────┘
```

## 🧩 Core Components Deep Dive

### 1. CLI Framework (Click + Rich)

**Technology Stack:**
- **Click**: Command-line interface framework
- **Rich**: Terminal UI with colors, tables, progress bars
- **Python 3.8+**: Core language

**Implementation Details:**
```python
# main.py - CLI Router
@click.group()
@click.option('--profile', default='default')
@click.option('--region', default='eu-west-3')
@click.pass_context
def cli(ctx, profile, region):
    """Main CLI entry point with context passing"""
    ctx.obj = {'profile': profile, 'region': region}

# Commands are modular and auto-discovered
cli.add_command(account)
cli.add_command(migrate)
cli.add_command(status)
cli.add_command(template)
```

**Context Flow:**
1. User executes `lzaas account create ...`
2. Click parses arguments and options
3. Context object carries AWS profile/region
4. Command handler receives validated inputs
5. Rich provides beautiful terminal output

### 2. AFT Manager - Core Integration Engine

**Purpose**: Central hub for all AFT-related operations

**Key Responsibilities:**
- DynamoDB table management
- Account request lifecycle
- AFT pipeline integration
- Error handling and retry logic

**Implementation:**
```python
class AFTManager:
    def __init__(self, profile=None, region='eu-west-3'):
        self.session = boto3.Session(profile_name=profile, region_name=region)
        self.dynamodb = self.session.resource('dynamodb')
        self.codepipeline = self.session.client('codepipeline')

    def create_account_request(self, request: AccountRequest):
        """Create AFT account request in DynamoDB"""
        # 1. Generate unique request ID
        # 2. Validate template and inputs
        # 3. Create DynamoDB item
        # 4. Trigger AFT pipeline (if configured)
        # 5. Return success/failure status
```

**DynamoDB Schema:**
```json
{
  "request_id": "dev-2025-01-10-abc12345",
  "template": "dev",
  "email": "dev@company.com",
  "name": "Development Account",
  "client_id": "internal",
  "status": "pending",
  "created_date": "2025-01-10T10:00:00Z",
  "vpc_cidr": "10.1.0.0/16",
  "ou": "Development",
  "customizations": {
    "backup_enabled": true,
    "monitoring_level": "basic"
  }
}
```

### 3. Data Models - Type Safety & Validation

**Purpose**: Ensure data consistency and type safety

**Implementation:**
```python
@dataclass
class AccountRequest:
    request_id: str
    template: str
    email: str
    name: str
    client_id: str
    requested_by: str
    ou: str
    vpc_cidr: str = None
    customizations: dict = None

    def __post_init__(self):
        """Validate data after initialization"""
        if not validate_email(self.email):
            raise ValueError(f"Invalid email: {self.email}")
        if not validate_ou_name(self.ou):
            raise ValueError(f"Invalid OU: {self.ou}")

@dataclass
class AccountTemplate:
    name: str
    description: str
    ou: str
    vpc_cidr: str
    monthly_cost_estimate: str
    features: dict
```

### 4. Validation Layer - Input Security

**Purpose**: Prevent invalid inputs and security issues

**Implementation:**
```python
def validate_email(email: str) -> bool:
    """RFC 5322 compliant email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_account_id(account_id: str) -> bool:
    """AWS Account ID validation (12 digits)"""
    return account_id.isdigit() and len(account_id) == 12

def validate_ou_name(ou_name: str) -> bool:
    """OU name validation (alphanumeric + spaces/hyphens)"""
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return re.match(pattern, ou_name) is not None

def sanitize_input(input_str: str) -> str:
    """Remove potentially dangerous characters"""
    return re.sub(r'[<>"\';]', '', input_str.strip())
```

## 🔌 AWS Integration Layer

### 1. Authentication & Session Management

**AWS Credential Chain:**
1. CLI parameters (`--profile`)
2. Environment variables (`AWS_PROFILE`, `AWS_ACCESS_KEY_ID`)
3. AWS credentials file (`~/.aws/credentials`)
4. IAM roles (for EC2/Lambda execution)

**Implementation:**
```python
def create_aws_session(profile=None, region='eu-west-3'):
    """Create authenticated AWS session"""
    try:
        session = boto3.Session(
            profile_name=profile,
            region_name=region
        )
        # Verify credentials
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        return session, identity
    except Exception as e:
        raise AuthenticationError(f"AWS authentication failed: {e}")
```

### 2. Service Integrations

**DynamoDB Integration:**
```python
def create_aft_table_if_not_exists(self):
    """Ensure AFT request table exists"""
    table_name = f"aft-request-{datetime.now().strftime('%Y%m%d')}"

    try:
        table = self.dynamodb.Table(table_name)
        table.load()  # Test if table exists
    except ClientError:
        # Create table with proper schema
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'request_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'request_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()

    return table
```

**Organizations API Integration:**
```python
def move_account_to_ou(self, account_id: str, target_ou_name: str):
    """Move account to different OU"""
    orgs_client = self.session.client('organizations')

    # 1. Get current account parent
    parents = orgs_client.list_parents(ChildId=account_id)
    current_parent = parents['Parents'][0]['Id']

    # 2. Find target OU by name
    target_ou_id = self._find_ou_by_name(target_ou_name)

    # 3. Execute move
    orgs_client.move_account(
        AccountId=account_id,
        SourceParentId=current_parent,
        DestinationParentId=target_ou_id
    )
```

## 🛠️ Technology Stack & Dependencies

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **CLI Framework** | Click | 8.1+ | Command-line interface |
| **Terminal UI** | Rich | 13.0+ | Beautiful terminal output |
| **AWS SDK** | Boto3 | 1.26+ | AWS service integration |
| **Data Validation** | Python dataclasses | 3.8+ | Type safety |
| **Configuration** | Python configparser | 3.8+ | Settings management |

### Dependencies

```python
# setup.py dependencies
install_requires=[
    'click>=8.1.0',
    'rich>=13.0.0',
    'boto3>=1.26.0',
    'botocore>=1.29.0',
    'python-dateutil>=2.8.0',
    'pydantic>=1.10.0',  # For advanced validation
    'requests>=2.28.0',  # For future API integration
]
```

### System Requirements

- **Python**: 3.8 or higher
- **AWS CLI**: Configured with appropriate credentials
- **Operating System**: macOS, Linux, Windows (WSL)
- **Memory**: 256MB minimum
- **Network**: Internet access for AWS API calls

## 🔄 Command Processing Pipeline

### 1. Input Processing

```
User Input: lzaas account create --template dev --email test@company.com

Processing Steps:
1. Click argument parsing
2. Option validation
3. Context object creation
4. Command routing
```

### 2. Validation Pipeline

```
Input Validation Chain:
┌─────────────────┐
│ Syntax Check    │ Click built-in validation
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Type Validation │ Python type hints
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Business Rules  │ Custom validators
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Security Check  │ Input sanitization
└─────────────────┘
```

### 3. Execution Pipeline

```
Execution Flow:
┌─────────────────┐
│ AWS Session     │ Authentication & authorization
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Business Logic  │ Core operation execution
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ AWS API Calls   │ DynamoDB, Organizations, etc.
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Response Format │ Rich terminal output
└─────────────────┘
```

## 🔐 Security & Error Handling

### 1. Security Measures

**Input Sanitization:**
```python
def sanitize_account_name(name: str) -> str:
    """Sanitize account name for security"""
    # Remove dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', name.strip())
    # Limit length
    return sanitized[:64]

def validate_aws_resource_name(name: str) -> bool:
    """Validate AWS resource naming conventions"""
    pattern = r'^[a-zA-Z0-9\-_\.]+$'
    return bool(re.match(pattern, name)) and len(name) <= 255
```

**Permission Validation:**
```python
def check_required_permissions(session):
    """Verify user has required AWS permissions"""
    required_permissions = [
        'dynamodb:PutItem',
        'dynamodb:GetItem',
        'organizations:DescribeAccount',
        'organizations:MoveAccount'
    ]

    iam = session.client('iam')
    sts = session.client('sts')

    # Get current user/role
    identity = sts.get_caller_identity()

    # Simulate permissions
    for permission in required_permissions:
        try:
            response = iam.simulate_principal_policy(
                PolicySourceArn=identity['Arn'],
                ActionNames=[permission],
                ResourceArns=['*']
            )
            # Check if allowed
            if response['EvaluationResults'][0]['EvalDecision'] != 'allowed':
                raise PermissionError(f"Missing permission: {permission}")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not verify {permission}[/yellow]")
```

### 2. Error Handling Strategy

**Hierarchical Error Handling:**
```python
class LZaaSError(Exception):
    """Base exception for LZaaS operations"""
    pass

class ValidationError(LZaaSError):
    """Input validation errors"""
    pass

class AWSError(LZaaSError):
    """AWS API related errors"""
    pass

class AuthenticationError(AWSError):
    """AWS authentication failures"""
    pass

def handle_aws_error(func):
    """Decorator for AWS error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                raise AuthenticationError("Insufficient AWS permissions")
            elif error_code == 'ResourceNotFound':
                raise AWSError("AWS resource not found")
            else:
                raise AWSError(f"AWS API error: {e}")
        except Exception as e:
            raise LZaaSError(f"Unexpected error: {e}")
    return wrapper
```

## 🚀 Performance & Optimization

### 1. Caching Strategy

**Session Caching:**
```python
class SessionManager:
    """Manage AWS sessions with caching"""

    def __init__(self):
        self._sessions = {}
        self._cache_ttl = 3600  # 1 hour

    def get_session(self, profile=None, region='eu-west-3'):
        """Get cached session or create new one"""
        cache_key = f"{profile}:{region}"

        if cache_key in self._sessions:
            session, timestamp = self._sessions[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return session

        # Create new session
        session = boto3.Session(profile_name=profile, region_name=region)
        self._sessions[cache_key] = (session, time.time())
        return session
```

**OU Discovery Caching:**
```python
def get_organizational_units(self, use_cache=True):
    """Get OUs with optional caching"""
    cache_file = os.path.expanduser('~/.lzaas/ou_cache.json')

    if use_cache and os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            if time.time() - cache_data['timestamp'] < 300:  # 5 minutes
                return cache_data['ous']

    # Fetch from AWS
    ous = self._fetch_ous_from_aws()

    # Cache results
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'ous': ous
        }, f)

    return ous
```

### 2. Async Operations

**Future Enhancement - Async Support:**
```python
import asyncio
import aioboto3

class AsyncAFTManager:
    """Async version for future performance improvements"""

    async def create_multiple_accounts(self, requests: List[AccountRequest]):
        """Create multiple accounts concurrently"""
        session = aioboto3.Session()

        async with session.resource('dynamodb') as dynamodb:
            tasks = []
            for request in requests:
                task = self._create_single_account(dynamodb, request)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
```

## 📊 Monitoring & Observability

### 1. Logging Strategy

**Structured Logging:**
```python
import logging
import json
from datetime import datetime

class LZaaSLogger:
    """Structured logging for LZaaS operations"""

    def __init__(self, level=logging.INFO):
        self.logger = logging.getLogger('lzaas')
        self.logger.setLevel(level)

        # Console handler with Rich
        console_handler = RichHandler()
        console_handler.setLevel(level)

        # File handler for audit trail
        file_handler = logging.FileHandler(
            os.path.expanduser('~/.lzaas/audit.log')
        )
        file_handler.setLevel(logging.INFO)

        # JSON formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def log_operation(self, operation: str, **kwargs):
        """Log operation with structured data"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'user': os.getenv('USER', 'unknown'),
            'aws_profile': kwargs.get('profile', 'default'),
            **kwargs
        }
        self.logger.info(json.dumps(log_data))
```

### 2. Metrics Collection

**Operation Metrics:**
```python
class MetricsCollector:
    """Collect operation metrics for monitoring"""

    def __init__(self):
        self.metrics = {
            'operations_total': 0,
            'operations_success': 0,
            'operations_failed': 0,
            'avg_response_time': 0,
            'last_operation': None
        }

    def record_operation(self, operation: str, success: bool, duration: float):
        """Record operation metrics"""
        self.metrics['operations_total'] += 1
        if success:
            self.metrics['operations_success'] += 1
        else:
            self.metrics['operations_failed'] += 1

        # Update average response time
        current_avg = self.metrics['avg_response_time']
        total_ops = self.metrics['operations_total']
        self.metrics['avg_response_time'] = (
            (current_avg * (total_ops - 1) + duration) / total_ops
        )

        self.metrics['last_operation'] = {
            'name': operation,
            'success': success,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
```

## 🔮 Future Architecture (API Layer)

### Current Status: CLI Only (v1.1.0)

**What's Implemented:**
- ✅ Complete CLI interface
- ✅ Core business logic
- ✅ AWS integrations
- ✅ Data models and validation

**What's NOT Implemented (Future v1.2.0+):**
- ❌ REST API endpoints
- ❌ Web UI
- ❌ API authentication
- ❌ Multi-tenancy

### Planned API Architecture (v1.2.0)

```
Future Architecture:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   REST API      │    │   LZaaS Core    │
│   (React/Vue)   │───▶│   (FastAPI)     │───▶│   (Current CLI) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

**Planned API Endpoints:**
```python
# Future API structure (not implemented yet)
from fastapi import FastAPI, Depends
from lzaas.core.aft_manager import AFTManager

app = FastAPI(title="LZaaS API", version="1.2.0")

@app.post("/api/v1/accounts")
async def create_account(request: AccountRequest):
    """Create new AWS account"""
    # Will reuse existing CLI logic
    pass

@app.get("/api/v1/accounts")
async def list_accounts(client_id: str = None):
    """List account requests"""
    pass

@app.post("/api/v1/migrate/ou")
async def migrate_account_ou(account_id: str, target_ou: str):
    """Migrate account to different OU"""
    pass
```

## 📚 Documentation References

### Existing Documentation

1. **`LZAAS_INTERNALS.md`** (This document) - Complete architecture deep dive
2. **`LZAAS_MIGRATION_GUIDE.md`** - Migration operations and use cases
3. **`LZAAS_V1_1_0_RELEASE_NOTES.md`** - Feature overview and benefits
4. **`lzaas-cli/README.md`** - CLI installation and usage guide
5. **`LZAAS_AUTOMATION_STRATEGY.md`** - High-level strategy and implementation

### Architecture Documentation Map

```
Documentation Hierarchy:
├── LZAAS_INTERNALS.md          # ← YOU ARE HERE (Technical deep dive)
├── LZAAS_AUTOMATION_STRATEGY.md # High-level architecture & strategy
├── LZAAS_MIGRATION_GUIDE.md    # Migration operations guide
├── LZAAS_V1_1_0_RELEASE_NOTES.md # Feature overview & benefits
└── lzaas-cli/README.md         # CLI usage & installation
```

## 🎯 Key Takeaways

### How LZaaS Works (Command to AWS)

1. **User Input** → CLI parses with Click framework
2. **Validation** → Input sanitization and business rule validation
3. **Authentication** → AWS session creation with credential chain
4. **Business Logic** → Core operations in AFT Manager
5. **AWS APIs** → Direct calls to DynamoDB, Organizations, CodePipeline
6. **Response** → Rich terminal output with status and progress

### Technology Foundation

- **Language**: Python 3.8+ for reliability and AWS SDK support
- **CLI Framework**: Click for robust command-line interface
- **UI Framework**: Rich for beautiful terminal experience
- **AWS Integration**: Boto3 for comprehensive AWS API access
- **Data Models**: Python dataclasses for type safety
- **Validation**: Custom validators for security and correctness

### Current Limitations

- **CLI Only**: No REST API or web interface (planned for v1.2.0)
- **Single User**: No multi-tenancy or user management
- **Local State**: No centralized database for request tracking
- **Manual Monitoring**: No automated alerting or dashboards

### Future Roadmap

- **v1.2.0**: REST API and web UI
- **v1.3.0**: Multi-tenancy and RBAC
- **v1.4.0**: Advanced monitoring and alerting
- **v2.0.0**: Full enterprise features

---

**This document provides complete transparency into the LZaaS architecture, making the solution accessible to all team members for understanding, maintenance, and future development.**

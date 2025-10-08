# LZaaS CLI Installation Guide

🛠️ **Complete Installation Instructions for LZaaS CLI**

*LZaaS Version: 1.1.0 | Date: October 01, 2025*
*LZaaS CLI Version: 1.0.0 | Date: October 01, 2025*

## 🧹 **Clean Installation Process**

### **Step 1: Uninstall Previous Installations (Recommended)**

If you previously attempted to install LZaaS CLI or have any conflicting installations, run the uninstallation script first to ensure a clean setup:

```bash
# From the repository root directory

# Run the comprehensive uninstallation script
./uninstall-lzaas.sh
```

**What the uninstallation script does:**
- ✅ Removes LZaaS from system Python installations (`pip3`, `pip`)
- ✅ Removes LZaaS from user Python installations (`pip3 --user`, `pip --user`)
- ✅ Removes virtual environments (`lzaas-env`, `venv`, `.venv`, etc.)
- ✅ Cleans binary files from common locations (`/usr/local/bin`, `~/.local/bin`, etc.)
- ✅ Cleans shell configuration files (`.bashrc`, `.zshrc`, `.profile`, etc.)
- ✅ Removes Python cache and build artifacts (`__pycache__`, `.egg-info`, etc.)
- ✅ Creates backups of modified configuration files with timestamps
- ✅ Provides interactive shell configuration reload

**Sample uninstall output:**
```
🧹 LZaaS CLI Uninstallation Script

[INFO] Starting LZaaS CLI uninstallation...
[INFO] Checking system Python installations...
[SUCCESS] Removed lzaas from pip3
[INFO] Removing virtual environments...
[SUCCESS] Removed /path/to/lzaas-env
[INFO] Cleaning shell configuration files...
[SUCCESS] Cleaned /Users/username/.zshrc
[SUCCESS] LZaaS CLI uninstallation completed!
```

### **Step 2: Fresh Installation**
**(Recommended)**

After cleaning up previous installations, proceed with the automated installation:

## 🚨 **Installation Issue Explanation**

### **What Happened During Your Installation**

The error you encountered is a **common Python dependency conflict**:

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
aiobotocore 2.12.3 requires botocore<1.34.70,>=1.34.41, but you have botocore 1.40.43 which is incompatible.
```

**Root Cause:**
- Your system has `aiobotocore 2.12.3` installed (probably from another AWS tool)
- `aiobotocore` requires `botocore<1.34.70` (older version)
- LZaaS CLI installed `botocore 1.40.43` (newer version)
- This creates a **version conflict** between packages

**Why This Happens:**
- **Global Python environment** has multiple AWS tools installed
- **Different tools** require different versions of the same dependencies
- **pip's dependency resolver** can't satisfy all requirements simultaneously

### **The Solution: Virtual Environment**

**Yes, you should absolutely install LZaaS CLI in a virtual environment!** This is the **recommended best practice** for Python applications.

## 🐍 **Virtual Environment Installation (Recommended)**

### **Option 1: Using Python venv (Built-in)**

#### **Step 1: Create Virtual Environment**
```bash
# Navigate to your project directory
cd ~/path/to/your/project

# Create virtual environment
python3 -m venv lzaas-env

# Alternative if python3 is not available
python -m venv lzaas-env
```

#### **Step 2: Activate Virtual Environment**
```bash
# On macOS/Linux
source lzaas-env/bin/activate

# On Windows
lzaas-env\Scripts\activate

# You should see (lzaas-env) in your terminal prompt
```

#### **Step 3: Install LZaaS CLI**
```bash
# Ensure you're in the virtual environment (see (lzaas-env) in prompt)

# Install in development mode
pip install -e .

# Or install from setup.py
pip install .
```

#### **Step 4: Verify Installation**
```bash
# Check if lzaas command is available
lzaas --help

# Check installed packages
pip list | grep lzaas
```

#### **Step 5: Deactivate When Done**
```bash
# Deactivate virtual environment
deactivate
```

### **Option 2: Using Conda (If You Have Anaconda/Miniconda)**

#### **Step 1: Create Conda Environment**
```bash
# Create new conda environment with Python 3.8+
conda create -n lzaas-env python=3.9

# Activate the environment
conda activate lzaas-env
```

#### **Step 2: Install LZaaS CLI**
```bash
# Navigate to CLI directory and install LZaaS CLI
pip install -e .
```

#### **Step 3: Verify Installation**
```bash
# Test the CLI
lzaas --help

# Check environment
conda list | grep lzaas
```

#### **Step 4: Deactivate When Done**
```bash
# Deactivate conda environment
conda deactivate
```

## 🔧 **Complete Installation Script**

### **Automated Installation Script**

Create this script to automate the installation:

```bash
#!/bin/bash
# install-lzaas.sh

set -e  # Exit on any error

echo "🚀 Installing LZaaS CLI in Virtual Environment"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv lzaas-env

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source lzaas-env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install LZaaS CLI
echo "🛠️ Installing LZaaS CLI..."
cd lzaas-cli
pip install -e .

# Verify installation
echo "✅ Verifying installation..."
lzaas --help

echo ""
echo "🎉 LZaaS CLI installed successfully!"
echo ""
echo "To use LZaaS CLI:"
echo "1. Activate environment: source lzaas-env/bin/activate"
echo "2. Run commands: lzaas --help"
echo "3. Deactivate when done: deactivate"
```

**Make it executable and run:**
```bash
chmod +x install-lzaas.sh
./install-lzaas.sh
```

## 🎯 **Daily Usage Workflow**

### **Starting a LZaaS Session**
```bash
# Navigate to your project
cd ~/path/to/your/project

# Activate virtual environment
source lzaas-env/bin/activate

# Now you can use LZaaS CLI
lzaas account list
lzaas template list
lzaas migrate existing-ou --help
```

### **Ending a LZaaS Session**
```bash
# Deactivate virtual environment
deactivate
```

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue 1: "lzaas command not found"**
```bash
# Solution: Make sure virtual environment is activated
source lzaas-env/bin/activate

# Verify activation (should see (lzaas-env) in prompt)
which python
which lzaas
```

#### **Issue 2: "Permission denied"**
```bash
# Solution: Don't use sudo with virtual environments
# Instead, ensure proper ownership
chown -R $USER:$USER lzaas-env/
```

#### **Issue 3: "Module not found"**
```bash
# Solution: Reinstall in virtual environment
pip uninstall lzaas-cli
pip install -e .
```

#### **Issue 4: "AWS credentials not found"**
```bash
# Solution: Configure AWS credentials
aws configure

# Or set environment variables
export AWS_PROFILE=your-profile
export AWS_REGION=eu-west-3
```

### **Dependency Conflict Resolution**

If you still encounter conflicts:

```bash
# Option 1: Clean install
pip uninstall boto3 botocore aiobotocore
pip install -e .

# Option 2: Force reinstall
pip install --force-reinstall boto3 botocore

# Option 3: Use specific versions
pip install boto3==1.40.43 botocore==1.40.43
```

## 📋 **Environment Setup Checklist**

### **Prerequisites**
- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] AWS CLI configured (optional but recommended)
- [ ] Git installed (for cloning repositories)

### **Installation Steps**
- [ ] Create virtual environment
- [ ] Activate virtual environment
- [ ] Navigate to lzaas-cli directory
- [ ] Install LZaaS CLI with `pip install -e .`
- [ ] Verify installation with `lzaas --help`
- [ ] Configure AWS credentials if needed

### **Testing Steps**
- [ ] Test basic commands: `lzaas --help`
- [ ] Test template listing: `lzaas template list`
- [ ] Test account listing: `lzaas account list`
- [ ] Test migration help: `lzaas migrate --help`

## 🎯 **Best Practices**

### **Virtual Environment Management**
1. **Always use virtual environments** for Python projects
2. **Name environments descriptively** (e.g., `lzaas-env`, `project-env`)
3. **Keep environments isolated** - one per project
4. **Document environment requirements** in README files
5. **Use requirements.txt** for reproducible installations

### **LZaaS CLI Usage**
1. **Always activate environment** before using LZaaS
2. **Configure AWS credentials** properly
3. **Use dry-run options** for testing
4. **Keep CLI updated** with `pip install --upgrade lzaas-cli`
5. **Check documentation** with `--help` flags

## 🚀 **Quick Start After Installation**

Once installed in virtual environment:

```bash
# Activate environment
source lzaas-env/bin/activate

# Configure AWS (if not done already)
aws configure

# Test LZaaS CLI
lzaas --help

# List available templates
lzaas template list

# Check account requests
lzaas account list

# Test migration capabilities
lzaas migrate list-ous

# Example: Create development account
lzaas account create --template dev --email dev@company.com --client-id internal

# Example: Migrate existing account (dry-run first)
lzaas migrate existing-ou --account-id 198610579545 --target-ou Sandbox --dry-run
```

## 📚 **Additional Resources**

- **LZaaS CLI Documentation**: `lzaas-cli/README.md`
- **Architecture Guide**: `LZAAS_INTERNALS.md`
- **Migration Guide**: `LZAAS_MIGRATION_GUIDE.md`
- **Release Notes**: `LZAAS_V1_1_0_RELEASE_NOTES.md`

---

**The virtual environment approach will completely resolve the dependency conflicts and provide a clean, isolated environment for LZaaS CLI usage.**

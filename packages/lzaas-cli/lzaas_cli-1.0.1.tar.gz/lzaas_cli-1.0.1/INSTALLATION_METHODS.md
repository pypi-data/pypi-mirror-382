# LZaaS CLI Installation Methods Guide

## 🎯 **Overview**

This guide explains the different ways to install and run the LZaaS CLI, helping you choose the best method for your use case.

## 📋 **Installation Method Comparison**

| Method | Use Case | Isolation | Development | Recommended |
|--------|----------|-----------|-------------|-------------|
| **Virtual Environment** | Testing, Development | ✅ Isolated | ✅ Safe | **⭐ RECOMMENDED** |
| **Install Scripts** | Production, End Users | ✅ Manages venv | ✅ Easy | **⭐ RECOMMENDED** |
| **System-wide pip** | Quick testing | ❌ Global install | ⚠️ Conflicts | ⚠️ Use with caution |
| **Development mode** | Active development | ✅ Editable | ✅ Live changes | For developers only |

## 🔥 **Method 1: Virtual Environment (RECOMMENDED)**

**Best for**: Testing, development, learning, avoiding conflicts

### **Why Virtual Environment?**
- **Isolation**: Keeps LZaaS CLI separate from your system Python
- **Safety**: No risk of conflicting with other Python packages
- **Clean**: Easy to remove completely when done
- **Professional**: Industry standard practice

### **Installation Steps**
```bash
# 1. Create virtual environment
python -m venv lzaas-test-env

# 2. Activate virtual environment
# On macOS/Linux:
source lzaas-test-env/bin/activate
# On Windows:
lzaas-test-env\Scripts\activate

# 3. Install LZaaS CLI from GitHub
pip install git+https://github.com/SPITZKOP/lzaas-cli.git

# 4. Verify installation
lzaas --version
lzaas --help

# 5. When done testing, deactivate
deactivate

# 6. To remove completely
rm -rf lzaas-test-env
```

### **Daily Usage**
```bash
# Activate when you want to use LZaaS
source lzaas-test-env/bin/activate

# Use LZaaS commands
lzaas account list
lzaas template show dev

# Deactivate when done
deactivate
```

## ⭐ **Method 2: Install Scripts (RECOMMENDED)**

**Best for**: End users, production environments, easy management

### **Why Install Scripts?**
- **Automated**: Handles virtual environment creation automatically
- **User-friendly**: Simple one-command installation
- **Global access**: Makes `lzaas` command available system-wide
- **Easy removal**: Clean uninstall with one command

### **Installation Steps**
```bash
# 1. Navigate to CLI directory
cd sse-landing-zone/lzaas-cli

# 2. Run install script
./install.sh

# The script automatically:
# - Creates a virtual environment in ~/.lzaas-cli-env
# - Installs the CLI in the virtual environment
# - Creates a global lzaas command wrapper
# - Shows usage instructions

# 3. Verify installation
lzaas --version
lzaas --help
```

### **What the Install Script Does**
```bash
# Creates: ~/.lzaas-cli-env/ (virtual environment)
# Creates: /usr/local/bin/lzaas (global command wrapper)
# Installs: LZaaS CLI in isolated environment
# Result: lzaas command available globally, but isolated
```

### **Uninstallation**
```bash
# Navigate to CLI directory
cd sse-landing-zone/lzaas-cli

# Run uninstall script
./uninstall.sh

# This removes:
# - The virtual environment (~/.lzaas-cli-env)
# - The global command wrapper (/usr/local/bin/lzaas)
# - All traces of LZaaS CLI
```

## ⚠️ **Method 3: System-wide Installation (USE WITH CAUTION)**

**Best for**: Quick testing only, experienced Python users

### **Why Be Cautious?**
- **No isolation**: Installs directly to system Python
- **Potential conflicts**: May interfere with other packages
- **Harder to remove**: Leaves traces in system Python
- **Not recommended**: For production or long-term use

### **Installation Steps**
```bash
# Install directly to system Python
pip install git+https://github.com/SPITZKOP/lzaas-cli.git

# Verify installation
lzaas --version
lzaas --help

# To uninstall
pip uninstall lzaas-cli
```

## 🔧 **Method 4: Development Mode (FOR DEVELOPERS)**

**Best for**: CLI development, contributing to the project

### **What is Development Mode?**
- **Editable install**: Changes to code reflect immediately
- **No reinstall needed**: Modify code and test instantly
- **Development workflow**: Perfect for CLI development

### **Installation Steps**
```bash
# 1. Clone or navigate to CLI source
cd sse-landing-zone/lzaas-cli

# 2. Create virtual environment (recommended)
python -m venv dev-env
source dev-env/bin/activate

# 3. Install in development mode
pip install -e .

# 4. Now any changes to the code are immediately available
# Edit files in lzaas/ directory and test immediately
lzaas --version  # Reflects your changes instantly
```

### **Development Workflow**
```bash
# Make changes to CLI code
vim lzaas/cli/main.py

# Test changes immediately (no reinstall needed)
lzaas --help

# Changes are reflected instantly!
```

## 🆚 **pip install -e vs pip install git+**

### **pip install -e . (Development Mode)**
```bash
# What it does:
# - Creates a link to your local source code
# - Changes to source code reflect immediately
# - Perfect for development and testing changes
# - Requires local source code directory

cd sse-landing-zone/lzaas-cli
pip install -e .
```

### **pip install git+ (Remote Install)**
```bash
# What it does:
# - Downloads and installs from GitHub
# - Creates a static installation
# - No connection to source code
# - Perfect for end users

pip install git+https://github.com/SPITZKOP/lzaas-cli.git
```

## 🎯 **Recommendations by Use Case**

### **For Testing LZaaS CLI**
```bash
# Use Method 1: Virtual Environment
python -m venv lzaas-test-env
source lzaas-test-env/bin/activate
pip install git+https://github.com/SPITZKOP/lzaas-cli.git
```

### **For End Users**
```bash
# Use Method 2: Install Scripts
cd sse-landing-zone/lzaas-cli
./install.sh
```

### **For CLI Development**
```bash
# Use Method 4: Development Mode
cd sse-landing-zone/lzaas-cli
python -m venv dev-env
source dev-env/bin/activate
pip install -e .
```

### **For Quick Testing (Advanced Users)**
```bash
# Use Method 3: System-wide (with caution)
pip install git+https://github.com/SPITZKOP/lzaas-cli.git
```

## 🔍 **Troubleshooting**

### **Command Not Found**
```bash
# If 'lzaas' command not found:

# For virtual environment:
source lzaas-test-env/bin/activate

# For install scripts:
# Check if /usr/local/bin is in your PATH
echo $PATH | grep /usr/local/bin

# Add to PATH if missing:
export PATH="/usr/local/bin:$PATH"
```

### **Permission Errors**
```bash
# If install script fails with permission errors:
sudo ./install.sh

# Or install to user directory:
pip install --user git+https://github.com/SPITZKOP/lzaas-cli.git
```

### **Python Version Issues**
```bash
# Ensure Python 3.8+ is used:
python --version

# Use specific Python version:
python3.9 -m venv lzaas-test-env
```

## 📚 **Next Steps**

After installation, verify everything works:

```bash
# Check version
lzaas --version

# View help
lzaas --help

# Test basic commands
lzaas template list
lzaas info

# View documentation
lzaas docs user-guide
```

## 🎓 **Educational Summary**

- **Virtual environments** are Python best practice for isolation
- **Install scripts** provide user-friendly automation
- **Development mode** enables live code editing
- **System-wide installs** should be avoided for most use cases
- **Choose the method** that matches your experience level and use case

Choose the installation method that best fits your needs and experience level!

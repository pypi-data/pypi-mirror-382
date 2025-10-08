#!/bin/bash

# LZaaS CLI Uninstallation Script
# This script removes all traces of LZaaS CLI installations

set -e

echo "🧹 LZaaS CLI Uninstallation Script"
echo "=================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to remove pip package
remove_pip_package() {
    local package_name="$1"
    local pip_cmd="$2"

    if $pip_cmd show "$package_name" >/dev/null 2>&1; then
        print_status "Removing $package_name from $pip_cmd..."
        $pip_cmd uninstall -y "$package_name" 2>/dev/null || true
        print_success "Removed $package_name from $pip_cmd"
    else
        print_status "$package_name not found in $pip_cmd"
    fi
}

# Function to remove from PATH
remove_from_path() {
    local path_to_remove="$1"
    local shell_config="$2"

    if [ -f "$shell_config" ] && grep -q "$path_to_remove" "$shell_config"; then
        print_status "Removing $path_to_remove from $shell_config..."
        # Create backup
        cp "$shell_config" "${shell_config}.backup.$(date +%Y%m%d_%H%M%S)"
        # Remove the path
        grep -v "$path_to_remove" "$shell_config" > "${shell_config}.tmp" && mv "${shell_config}.tmp" "$shell_config"
        print_success "Removed from $shell_config"
    fi
}

print_status "Starting LZaaS CLI uninstallation..."
echo

# Check if we're in the correct directory (lzaas-cli root)
if [ ! -f "setup.py" ] || [ ! -d "lzaas" ]; then
    print_warning "Not in lzaas-cli root directory, but continuing with cleanup..."
fi

# 1. Remove from system Python (pip3)
print_status "Checking system Python installations..."
if command_exists pip3; then
    remove_pip_package "lzaas" "pip3"
    remove_pip_package "lzaas-cli" "pip3"
fi

if command_exists pip; then
    remove_pip_package "lzaas" "pip"
    remove_pip_package "lzaas-cli" "pip"
fi

# 2. Remove from user Python installations
print_status "Checking user Python installations..."
if command_exists pip3; then
    remove_pip_package "lzaas" "pip3 --user"
    remove_pip_package "lzaas-cli" "pip3 --user"
fi

if command_exists pip; then
    remove_pip_package "lzaas" "pip --user"
    remove_pip_package "lzaas-cli" "pip --user"
fi

# 3. Remove virtual environments
print_status "Removing virtual environments..."

# Common virtual environment names
venv_names=("lzaas-env" "lzaas-venv" "venv" ".venv" "env" ".env")
current_dir=$(pwd)

for venv_name in "${venv_names[@]}"; do
    venv_path="$current_dir/$venv_name"
    if [ -d "$venv_path" ]; then
        print_status "Removing virtual environment: $venv_path"
        rm -rf "$venv_path"
        print_success "Removed $venv_path"
    fi
done

# 4. Remove from common binary locations
print_status "Checking common binary locations..."

binary_locations=(
    "/usr/local/bin/lzaas"
    "/usr/bin/lzaas"
    "$HOME/.local/bin/lzaas"
    "$HOME/bin/lzaas"
)

for location in "${binary_locations[@]}"; do
    if [ -f "$location" ]; then
        print_status "Removing binary: $location"
        rm -f "$location" 2>/dev/null || sudo rm -f "$location" 2>/dev/null || true
        print_success "Removed $location"
    fi
done

# 5. Remove from PATH in shell configuration files
print_status "Cleaning shell configuration files..."

shell_configs=(
    "$HOME/.bashrc"
    "$HOME/.bash_profile"
    "$HOME/.zshrc"
    "$HOME/.profile"
    "$HOME/.zprofile"
)

for config in "${shell_configs[@]}"; do
    if [ -f "$config" ]; then
        # Remove any lines containing lzaas paths
        if grep -q "lzaas" "$config"; then
            print_status "Cleaning $config..."
            cp "$config" "${config}.backup.$(date +%Y%m%d_%H%M%S)"
            grep -v "lzaas" "$config" > "${config}.tmp" && mv "${config}.tmp" "$config"
            print_success "Cleaned $config"
        fi
    fi
done

# 6. Remove Python cache and build artifacts (only if in lzaas-cli directory)
if [ -f "setup.py" ] && [ -d "lzaas" ]; then
    print_status "Removing Python cache and build artifacts..."

    cache_locations=(
        "build"
        "dist"
        "lzaas.egg-info"
        "lzaas_cli.egg-info"
        "__pycache__"
        "lzaas/__pycache__"
    )

    for location in "${cache_locations[@]}"; do
        if [ -d "$location" ]; then
            print_status "Removing cache: $location"
            rm -rf "$location"
            print_success "Removed $location"
        fi
    done

    # Find and remove any remaining __pycache__ directories
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -type f -delete 2>/dev/null || true
fi

# 7. Check for any remaining lzaas commands
print_status "Checking for remaining lzaas installations..."

if command_exists lzaas; then
    lzaas_location=$(which lzaas 2>/dev/null || true)
    if [ -n "$lzaas_location" ]; then
        print_warning "lzaas command still found at: $lzaas_location"
        print_warning "You may need to manually remove it or restart your shell"
    fi
else
    print_success "No lzaas command found in PATH"
fi

# 8. Display summary
echo
print_success "LZaaS CLI uninstallation completed!"
echo
print_status "Summary of actions taken:"
echo "  ✓ Removed from system Python installations"
echo "  ✓ Removed from user Python installations"
echo "  ✓ Removed virtual environments"
echo "  ✓ Removed binary files"
echo "  ✓ Cleaned shell configuration files"
echo "  ✓ Removed Python cache and build artifacts"
echo
print_status "Next steps:"
echo "  1. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
echo "  2. Run: ./install.sh to install LZaaS CLI in a clean virtual environment"
echo
print_warning "Note: Shell configuration backups were created with timestamp suffixes"
print_warning "If you experience issues, you can restore from these backups"
echo

# Optional: Ask if user wants to restart shell
read -p "Would you like to reload your shell configuration now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Reloading shell configuration..."
    if [ -n "$ZSH_VERSION" ]; then
        source ~/.zshrc 2>/dev/null || true
    elif [ -n "$BASH_VERSION" ]; then
        source ~/.bashrc 2>/dev/null || true
    fi
    print_success "Shell configuration reloaded"
fi

print_success "Uninstallation script completed successfully!"

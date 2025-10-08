# Contributing to LZaaS CLI

🎉 Thank you for your interest in contributing to the LZaaS CLI! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

### Our Standards

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Collaborative**: Work together towards common goals
- **Be Professional**: Maintain professional communication

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- AWS CLI (for testing)
- Basic understanding of AWS services and CLI development

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/lzaas-cli.git
   cd lzaas-cli
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -e .
   pip install pytest pytest-cov flake8 black isort mypy
   ```

3. **Verify Installation**
   ```bash
   # Test the CLI
   lzaas --version
   lzaas --help
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix issues and improve stability
- **Feature Enhancements**: Add new functionality
- **Documentation**: Improve guides, examples, and API docs
- **Testing**: Add or improve test coverage
- **Performance**: Optimize code and improve efficiency

### Before You Start

1. **Check Existing Issues**: Look for existing issues or discussions
2. **Create an Issue**: For significant changes, create an issue first
3. **Discuss Approach**: Get feedback on your proposed solution
4. **Follow Standards**: Adhere to coding standards and conventions

## Pull Request Process

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest tests/

# Run linting
flake8 lzaas
black --check lzaas
isort --check-only lzaas

# Run type checking
mypy lzaas --ignore-missing-imports
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add account template validation

- Add validation for custom account templates
- Include comprehensive error messages
- Add unit tests for validation logic"
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Pull Request Guidelines

- **Clear Title**: Use descriptive titles
- **Detailed Description**: Explain what and why
- **Link Issues**: Reference related issues
- **Test Coverage**: Include tests for new code
- **Documentation**: Update docs if needed

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, CLI version
- **Steps to Reproduce**: Clear, step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error output
- **Additional Context**: Any relevant information

### Feature Requests

For feature requests, please provide:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Additional Context**: Examples, mockups, etc.

## Development Workflow

### Code Style

We use the following tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Branch Naming

- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation updates
- `refactor/description`: Code refactoring

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lzaas --cov-report=html

# Run specific test file
pytest tests/test_account.py

# Run specific test
pytest tests/test_account.py::test_create_account
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies (AWS services)

### Test Structure

```python
def test_feature_description():
    """Test description explaining what is being tested."""
    # Arrange
    setup_test_data()

    # Act
    result = function_under_test()

    # Assert
    assert result == expected_value
```

## Documentation

### Types of Documentation

- **User Guide**: Complete user-facing documentation
- **API Reference**: Function and class documentation
- **Contributing Guide**: This document
- **README**: Project overview and quick start

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Follow markdown best practices

### Building Documentation

```bash
# Generate API documentation
# (Add specific commands when documentation generation is set up)

# Preview documentation locally
# (Add preview commands)
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create release tag
4. GitHub Actions handles PyPI release

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Documentation**: Check the User Guide first

### Maintainer Response

- We aim to respond to issues within 48 hours
- Pull requests are reviewed within one week
- Complex changes may require additional discussion

## Recognition

Contributors are recognized in:

- Release notes
- Contributors section in README
- GitHub contributor statistics

## License

By contributing to LZaaS CLI, you agree that your contributions will be licensed under the MIT License.

---

## Quick Reference

### Common Commands

```bash
# Development setup
python -m venv venv && source venv/bin/activate
pip install -e . && pip install pytest flake8 black isort mypy

# Code quality
black lzaas && isort lzaas && flake8 lzaas && mypy lzaas

# Testing
pytest --cov=lzaas

# Git workflow
git checkout -b feature/my-feature
git add . && git commit -m "feat: description"
git push origin feature/my-feature
```

### Resources

- [Python Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

Thank you for contributing to LZaaS CLI! 🚀

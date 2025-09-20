# Contributing to TrueNAS VM Manager

Thank you for your interest in contributing to TrueNAS VM Manager! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## 🤝 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- **Be respectful** and inclusive in all interactions
- **Be collaborative** and help others learn and grow
- **Be patient** with newcomers and different skill levels
- **Be constructive** in feedback and criticism
- **Focus on the best outcome** for the community and project

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.8+** installed
- **Git** for version control
- **Access to a TrueNAS SCALE system** for testing
- **Basic knowledge** of Python, YAML, and JSON

### First Steps

1. **Fork the repository** on GitHub
2. **Star the project** if you find it useful
3. **Read the documentation** in the `docs/` directory
4. **Browse existing issues** to understand current needs
5. **Join discussions** to introduce yourself

## 🛠️ Development Setup

### 1. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/truenas-vm-manager.git
cd truenas-vm-manager
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 mypy pytest pytest-cov
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your TrueNAS details
nano .env
```

### 4. Verify Setup

```bash
# Test configuration loading
python -c "from truenas_vm_manager import load_configuration; print('✅ Setup complete')"

# Run basic tests
python -m pytest tests/ -v
```

### 5. Set Up Git Hooks (Recommended)

```bash
# Create pre-commit hook for code formatting
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running code formatting..."
black truenas-vm-manager.py
flake8 truenas-vm-manager.py
EOF

chmod +x .git/hooks/pre-commit
```

## 🎯 How to Contribute

There are many ways to contribute to the project:

### 🐛 Report Bugs

- **Search existing issues** before creating new ones
- **Use the issue template** for bug reports
- **Provide detailed information**:
  - TrueNAS SCALE version
  - Python version
  - Complete error messages
  - Steps to reproduce
  - Configuration files (remove sensitive data)

### 💡 Suggest Features

- **Check existing feature requests** first
- **Describe the use case** clearly
- **Explain the expected behavior**
- **Consider implementation complexity**

### 📝 Improve Documentation

- **Fix typos** and grammatical errors
- **Add examples** for complex scenarios
- **Improve clarity** of explanations
- **Add missing documentation**

### 🔧 Submit Code Changes

- **Start small** with bug fixes or small features
- **Follow coding standards**
- **Include tests** for new functionality
- **Update documentation** as needed

## 📐 Coding Standards

### Python Style

We follow **PEP 8** with some specific guidelines:

```python
# Good: Clear, descriptive names
def create_vm_specification(name: str, cores: int, memory: int) -> Dict[str, Any]:
    """Create VM specification from parameters."""
    pass

# Good: Type hints for all functions
def load_configuration(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load and validate configuration from YAML file."""
    pass

# Good: Docstrings for all public methods
class VMManager:
    """Manages VM operations on TrueNAS systems."""
    
    def connect(self) -> None:
        """Establish connection to TrueNAS API."""
        pass
```

### Code Formatting

Use **Black** for automatic code formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Linting

Use **Flake8** for style checking:

```bash
# Run linter
flake8 truenas-vm-manager.py

# Configuration in setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

### Type Checking

Use **MyPy** for type checking:

```bash
# Run type checker
mypy truenas-vm-manager.py

# Configuration in setup.cfg
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Error Handling

Follow consistent error handling patterns:

```python
# Good: Specific exceptions with clear messages
try:
    response = self.client.call("vm.create", vm_spec)
except Exception as e:
    raise TrueNASError(f"VM creation failed: {e}")

# Good: Proper cleanup on failure
try:
    self._create_vm_devices(vm_id, vm_name, vm_config, vnc_port, storage_config)
except Exception as e:
    # Clean up partially created resources
    self._cleanup_vm(vm_id)
    raise TrueNASError(f"Device creation failed: {e}")
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── test_template_manager.py
├── test_vm_manager.py
├── test_configuration.py
├── fixtures/
│   ├── config.yaml
│   └── templates/
└── integration/
    └── test_full_workflow.py
```

### Unit Tests

Write unit tests for all new functionality:

```python
import pytest
from unittest.mock import Mock, patch
from truenas_vm_manager import TemplateManager, TrueNASError

class TestTemplateManager:
    def test_create_vm_spec(self):
        """Test VM specification creation."""
        tm = TemplateManager()
        spec = tm.create_vm_spec("test-vm", 4, 4, 8192)
        
        assert spec["name"] == "test-vm"
        assert spec["cores"] == 4
        assert spec["memory"] == 8192

    def test_invalid_template_path(self):
        """Test handling of invalid template paths."""
        with pytest.raises(TrueNASError, match="Template file not found"):
            TemplateManager(Path("/nonexistent"))
```

### Integration Tests

Create integration tests for end-to-end workflows:

```python
@pytest.mark.integration
class TestVMWorkflow:
    def test_create_and_destroy_vm(self):
        """Test complete VM lifecycle."""
        # This test requires actual TrueNAS connection
        pass
```

### Running Tests

```bash
# Run unit tests only
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=truenas_vm_manager --cov-report=html

# Run integration tests (requires TrueNAS)
pytest tests/integration/ -v -m integration

# Run specific test
pytest tests/test_template_manager.py::TestTemplateManager::test_create_vm_spec -v
```

### Test Configuration

Use test fixtures for consistent test data:

```python
# tests/fixtures/test_config.yaml
storage:
  pool_path: "test-pool/vms"
  cdrom_path: "/tmp/test.iso"

controlplane:
  count: 1
  memory: 1024
  cpu: 1
  disk:
    system: 10
  network:
    system: br-test
```

## 📚 Documentation

### Documentation Standards

- **Use clear, simple language**
- **Provide practical examples**
- **Include code snippets** where helpful
- **Update related documentation** when making changes

### Documentation Types

1. **API Documentation** (`docs/API.md`)
   - Method signatures and parameters
   - Return values and exceptions
   - Usage examples

2. **Architecture Documentation** (`docs/ARCHITECTURE.md`)
   - System design and components
   - Data flow and interactions

3. **User Documentation** (`README.md`, `docs/EXAMPLES.md`)
   - Installation and setup
   - Configuration examples
   - Common use cases

4. **Troubleshooting** (`docs/TROUBLESHOOTING.md`)
   - Common issues and solutions
   - Debug procedures

### Writing Documentation

```markdown
# Good: Clear headings and structure
## Method: create_vm_spec()

Creates a VM specification from template parameters.

### Parameters
- `name` (str): VM name
- `cores` (int): CPU cores

### Returns
- `Dict[str, Any]`: VM specification

### Example
```python
spec = template_manager.create_vm_spec("my-vm", 4, 8192)
```

### Updating Documentation

- **Update docstrings** when changing method signatures
- **Add examples** for new features
- **Update README** for significant changes
- **Check links** and references

## 🔄 Pull Request Process

### Before Submitting

1. **Create feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following coding standards

3. **Test thoroughly**:
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Check code style
   black --check .
   flake8 .
   mypy truenas-vm-manager.py
   ```

4. **Update documentation** as needed

5. **Commit with clear messages**:
   ```bash
   git commit -m "Add support for custom VM templates
   
   - Add template validation for custom templates
   - Update configuration loader to handle template paths
   - Add tests for custom template functionality
   - Update documentation with examples"
   ```

### Pull Request Guidelines

1. **Use descriptive title** that summarizes the change
2. **Fill out the PR template** completely
3. **Reference related issues** using "Fixes #123" or "Addresses #456"
4. **Provide clear description** of changes and rationale
5. **Include testing instructions** if applicable

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on actual TrueNAS system
4. **Documentation review** if applicable
5. **Approval** from maintainers
6. **Merge** by maintainers

## 🐞 Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- TrueNAS SCALE version:
- Python version:
- VM Manager version:

**Configuration**
```yaml
# Your config.yaml (remove sensitive data)
```

**Logs**
```
# Relevant log output with --log-level DEBUG
```

**Additional context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features.

**Use case**
Explain how this would be used.

**Additional context**
Any other context, mockups, etc.
```

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested

## 👥 Community

### Getting Help

- **GitHub Discussions** for questions and ideas
- **GitHub Issues** for bugs and feature requests
- **Documentation** for usage and API reference

### Communication Guidelines

- **Be respectful** and professional
- **Search before asking** to avoid duplicates
- **Provide context** when asking questions
- **Help others** when you can

### Recognition

Contributors are recognized in:
- **CHANGELOG.md** for notable contributions
- **GitHub contributors** page
- **Release notes** for significant features

## 🏷️ Release Process

### Versioning

We use **Semantic Versioning** (semver):

- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. **Prepare release branch**
2. **Update CHANGELOG.md**
3. **Update version numbers**
4. **Test release candidate**
5. **Create release tag**
6. **Update documentation**

## 📝 Development Workflow

### Typical Development Cycle

```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Develop and test
# ... make changes ...
pytest tests/ -v
black .
flake8 .

# 4. Commit changes
git add .
git commit -m "Add my feature"

# 5. Push and create PR
git push origin feature/my-feature
# Create pull request on GitHub

# 6. Address review feedback
# ... make changes ...
git add .
git commit -m "Address review comments"
git push origin feature/my-feature

# 7. After merge, cleanup
git checkout main
git pull upstream main
git branch -d feature/my-feature
```

### Long-term Development

For larger features:

1. **Create design document** in `docs/designs/`
2. **Discuss approach** in GitHub Discussions
3. **Break into smaller PRs** when possible
4. **Keep feature branch updated** with main

## 🎉 Thank You!

Thank you for contributing to TrueNAS VM Manager! Every contribution, whether it's code, documentation, bug reports, or feature suggestions, helps make the project better for everyone.

**Happy coding!** 🚀
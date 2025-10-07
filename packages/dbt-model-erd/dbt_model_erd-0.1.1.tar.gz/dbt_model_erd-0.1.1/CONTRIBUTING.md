# Contributing to dbt-model-erd

Thank you for your interest in contributing to dbt-model-erd! We welcome contributions from the community.

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Git
- Basic understanding of dbt and ER diagrams

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dbt-model-erd.git
   cd dbt-model-erd
   ```

3. **Install in development mode**:
   ```bash
   python setup.py install --user
   # OR with dev dependencies
   pip install -e ".[dev]"
   ```

4. **Install development tools**:
   ```bash
   pip install pytest pytest-cov ruff
   ```

5. **Run tests** to make sure everything works:
   ```bash
   make test
   # OR
   pytest tests/
   ```

---

## 🔧 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/your-bug-fix
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions/improvements
- `refactor/` - Code refactoring

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
make test

# Run linting
make lint

# Run formatting
make format

# Check coverage
make coverage
```

### 4. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: add support for bridge tables"
# OR
git commit -m "fix: handle missing YAML gracefully"
# OR
git commit -m "docs: update installation instructions"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding tests
- `refactor:` - Code refactoring
- `style:` - Formatting, missing semicolons, etc
- `chore:` - Updating build tasks, package manager configs, etc

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then go to GitHub and create a Pull Request.

---

## 📝 Pull Request Guidelines

### Before Submitting

- ✅ All tests pass
- ✅ Code is linted and formatted
- ✅ New tests added for new features
- ✅ Documentation updated
- ✅ CHANGELOG.md updated (if applicable)

### PR Description Should Include

1. **What** - What does this PR do?
2. **Why** - Why is this change needed?
3. **How** - How does it work?
4. **Testing** - How was it tested?

**Example:**
```markdown
## What
Adds support for detecting bridge/junction tables

## Why
Users with many-to-many relationships need bridge table support

## How
- Added bridge table detection logic in model_analyzer.py
- Updated diagram generator to handle bridge tables
- Added configuration option for bridge table patterns

## Testing
- Added 5 unit tests for bridge table detection
- Tested with sample dbt project
- All existing tests still pass
```

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_model_analyzer.py

# Specific test
pytest tests/test_model_analyzer.py::test_extract_refs_from_sql

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures from `conftest.py`

**Example:**
```python
def test_new_feature(sample_config):
    """Test description."""
    # Arrange
    input_data = "test input"

    # Act
    result = your_function(input_data, sample_config)

    # Assert
    assert result == expected_output
```

---

## 📚 Documentation

### Updating Documentation

When adding features, update:
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- Docstrings in code
- Example config files in `examples/`

### Docstring Format

```python
def function_name(param1, param2):
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong
    """
    pass
```

---

## 🎨 Code Style

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 100 characters
- Use Ruff for linting and formatting

### Formatting

```bash
# Auto-format code
make format

# Check formatting
make lint
```

### Code Quality

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions focused and small
- Avoid deep nesting (max 3 levels)
- Use meaningful variable names

---

## 🐛 Reporting Issues

### Before Creating an Issue

1. **Search existing issues** - It might already be reported
2. **Try latest version** - The issue might be fixed
3. **Reproduce** - Make sure you can consistently reproduce it

### Creating a Good Issue

Include:
- **Clear title** - Summarize the problem
- **Description** - What happened vs what you expected
- **Steps to reproduce** - Minimal steps to reproduce the issue
- **Environment** - Python version, OS, dbt-erd version
- **Error messages** - Full error messages and stack traces
- **Sample code** - Minimal code that reproduces the issue

**Template:**
```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Run `python -m dbt_erd --model-path ...`
2. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- dbt-erd version: 0.1.0
- Python version: 3.9
- OS: Ubuntu 22.04

## Error Message
```
Full error message here
```

## Sample Code
Minimal code to reproduce
```

---

## 💡 Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** first
2. **Describe the use case** - Why do you need this?
3. **Propose a solution** - How might it work?
4. **Consider alternatives** - What other approaches exist?

---

## 🏗️ Project Structure

```
dbt-erd/
├── .github/
│   └── workflows/        # CI/CD workflows
├── examples/             # Example configurations
├── tests/               # Test files
│   ├── data/           # Test data
│   └── test_*.py       # Test modules
├── __init__.py         # Package init
├── config.py           # Configuration handling
├── dbt_erd.py         # Main entry point
├── mermaid_generator.py # Diagram generation
├── mermaid_renderer.py  # HTML rendering
├── model_analyzer.py    # dbt model analysis
├── utils.py            # Utility functions
├── yaml_manager.py     # YAML operations
├── setup.py            # Package setup
├── README.md           # Main documentation
├── CONTRIBUTING.md     # This file
└── LICENSE             # MIT License
```

---

## 📋 Versioning and Releases

### Dynamic Versioning with setuptools-scm

This project uses **automatic versioning** based on git tags - **no manual version updates needed!**

- Version is automatically determined from git tags using `setuptools-scm`
- **DO NOT** manually edit version numbers in `setup.py` or anywhere else
- Version format follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

### Creating a Release (Maintainers Only)

1. Ensure all tests pass on `main` branch
2. Update `CHANGELOG.md` with release notes
3. Create and push a git tag:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
4. Create a GitHub release from the tag
5. The `publish.yml` workflow automatically publishes to PyPI

**Version examples:**
- `v1.2.3` → Package version `1.2.3`
- `v2.0.0` → Package version `2.0.0`
- Development builds use commit hash: `1.2.3.post1.dev5+gabc123`

### Branch Protection and CI Requirements

To maintain code quality, **branch protection rules should be enabled** on the `main` branch:

#### Setting up Branch Protection (Repository Admins)

1. Go to **Settings** → **Branches** → **Branch protection rules**
2. Add or edit rule for `main` branch:

   ✅ **Require a pull request before merging**
   - Require approvals: 1+ reviewer(s)

   ✅ **Require status checks to pass before merging**
   - Require branches to be up to date
   - **Required status checks** (select all or a subset):
     - `test (ubuntu-latest, 3.8)`
     - `test (ubuntu-latest, 3.9)`
     - `test (ubuntu-latest, 3.10)`
     - `test (ubuntu-latest, 3.11)`
     - `test (windows-latest, 3.8)`
     - `test (windows-latest, 3.9)`
     - `test (windows-latest, 3.10)`
     - `test (windows-latest, 3.11)`
     - `test (macos-latest, 3.8)`
     - `test (macos-latest, 3.9)`
     - `test (macos-latest, 3.10)`
     - `test (macos-latest, 3.11)`

   > **Tip**: You can require only Ubuntu tests if you want faster CI while still ensuring quality.

   ✅ **Require conversation resolution before merging**

   ✅ **Do not allow bypassing** (recommended)

3. Save changes

This ensures:
- ✅ All tests pass before merge
- ✅ Code is reviewed
- ✅ Bugs are caught before production
- ✅ CI failures block merges

---

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other unethical or unprofessional conduct

---

## 📧 Questions?

- **GitHub Discussions**: https://github.com/entechlog/dbt-erd/discussions
- **GitHub Issues**: https://github.com/entechlog/dbt-erd/issues
- **dbt Slack**: #tools-and-integrations channel

---

## 🙏 Thank You!

Your contributions make dbt-erd better for everyone. We appreciate your time and effort!

# Contributing to OpenFinOps

Thank you for your interest in contributing to OpenFinOps! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

We love feature suggestions! Please create an issue with:
- A clear description of the feature
- Why it would be useful
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Update documentation** as needed
5. **Run tests** to ensure everything works
6. **Submit a pull request**

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/openfinops.git
cd openfinops

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

## 📝 Coding Standards

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting (line length 100)
- Use [Ruff](https://github.com/astral-sh/ruff) for linting
- Add type hints where appropriate

### Documentation
- Write clear docstrings for all public functions/classes
- Use Google-style docstrings
- Update README.md if adding user-facing features
- Add examples for new features

### Testing
- Write unit tests for all new code
- Maintain or improve code coverage
- Test on Python 3.8+
- Include integration tests where appropriate

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Reference issue numbers when applicable

Example:
```
Add cost attribution by team feature

- Implement team-based cost tracking
- Add API endpoint for team metrics
- Update dashboard to show team costs

Fixes #123
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_observability.py

# Run with verbose output
pytest -v
```

## 📦 Project Structure

```
openfinops/
├── src/openfinops/           # Source code
│   ├── observability/        # Observability modules
│   ├── vizlychart/           # Visualization library
│   ├── dashboard/            # Dashboard components
│   └── cli.py                # CLI interface
├── tests/                    # Test files
├── examples/                 # Example scripts
├── docs/                     # Documentation
└── agents/                   # Cloud telemetry agents
```

## 🔍 Code Review Process

1. All submissions require review
2. We look for:
   - Code quality and style
   - Test coverage
   - Documentation
   - Performance impact
   - Security considerations

3. Reviewers may request changes
4. Once approved, maintainers will merge

## 📋 Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows the project style
- [ ] Tests pass locally
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] PR description clearly explains the changes

## 🌟 Recognition

Contributors will be:
- Listed in the project contributors
- Mentioned in release notes for significant contributions
- Invited to become maintainers for sustained contributions

## 📞 Questions?

- Open an issue for questions
- Join our discussions on GitHub
- Email: durai@infinidatum.net

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to OpenFinOps! 🎉

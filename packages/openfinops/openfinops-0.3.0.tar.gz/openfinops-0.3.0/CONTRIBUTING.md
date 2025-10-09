# Contributing to OpenFinOps

Thank you for your interest in contributing to OpenFinOps! We welcome contributions from the community.

## 🤝 How to Contribute

We welcome contributions of all kinds! Whether you're fixing bugs, adding features, improving documentation, or building plugins, we're grateful for your help.

### Ways to Contribute

1. **🐛 Report Bugs** - Help us improve quality
2. **💡 Suggest Features** - Share your ideas
3. **🔧 Submit Code** - Fix bugs or implement features
4. **📝 Improve Docs** - Enhance documentation
5. **🔌 Build Plugins** - Extend OpenFinOps functionality
6. **🧪 Write Tests** - Improve test coverage
7. **💬 Help Others** - Answer questions in Discussions

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Logs or error messages (if applicable)

### Suggesting Features

We love feature suggestions! Please create an issue with:
- A clear description of the feature
- Why it would be useful
- Use cases or examples
- Any implementation ideas you have
- Willingness to contribute (if applicable)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Update documentation** as needed
5. **Run tests** to ensure everything works
6. **Submit a pull request** with a clear description

### Building Plugins

OpenFinOps has a powerful plugin system! You can extend functionality by creating:
- **Telemetry Plugins**: Custom data collectors
- **Attribution Plugins**: Custom cost attribution logic
- **Recommendation Plugins**: Custom optimization rules
- **Dashboard Plugins**: Custom dashboard widgets
- **Integration Plugins**: External tool integrations

📚 **Plugin Development Guide**: See [docs/PLUGIN_ARCHITECTURE.md](docs/PLUGIN_ARCHITECTURE.md) for complete documentation.

**Quick Start**:
```python
from openfinops.plugins import TelemetryPlugin, PluginMetadata

class MyTelemetryPlugin(TelemetryPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            author="Your Name",
            description="My custom telemetry plugin",
            plugin_type=PluginType.TELEMETRY,
        )

    def collect_telemetry(self):
        # Your implementation
        pass
```

**Publish Your Plugin**:
1. Create Python package
2. Publish to PyPI as `openfinops-plugin-<name>`
3. Tag repository with `openfinops-plugin`
4. Share in GitHub Discussions

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
│   ├── plugins/              # Plugin system (🚧 In Development)
│   ├── insights/             # Persona-specific insights (🚧 Planned)
│   ├── notifications/        # Notification system (🚧 Planned)
│   └── cli.py                # CLI interface
├── tests/                    # Test files
├── examples/                 # Example scripts
├── docs/                     # Documentation
│   ├── PLUGIN_ARCHITECTURE.md      # Plugin development guide
│   └── IMPLEMENTATION_QUICKSTART.md # Implementation guide
├── agents/                   # Cloud telemetry agents
└── ROADMAP_2025.md          # Strategic roadmap
```

## 📚 Important Documentation

Before contributing, please review:
- **[ROADMAP_2025.md](ROADMAP_2025.md)** - Strategic initiatives and priorities
- **[docs/PLUGIN_ARCHITECTURE.md](docs/PLUGIN_ARCHITECTURE.md)** - Plugin development guide
- **[docs/IMPLEMENTATION_QUICKSTART.md](docs/IMPLEMENTATION_QUICKSTART.md)** - Implementation guide for contributors

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

## 🎯 Good First Issues

Looking for a place to start? Check issues labeled:
- `good-first-issue` - Easy issues for newcomers
- `help-wanted` - Issues where we need help
- `documentation` - Documentation improvements
- `plugin-idea` - Plugin suggestions

## 🗺️ Current Priorities (Q1 2025)

From our [2025 Roadmap](ROADMAP_2025.md):

1. **Plugin Architecture** (P0 - Critical)
   - Establish extensibility framework
   - Enable community plugins
   - Create plugin marketplace

2. **Persona-Specific Insights** (P0 - Critical)
   - Context-aware notifications
   - Role-based insights
   - Intelligent alerting

3. **FinOps-as-Code** (P0 - Critical)
   - Terraform provider
   - Pulumi SDK
   - YAML configuration

See [ROADMAP_2025.md](ROADMAP_2025.md) for full details.

## 📞 Questions?

- **GitHub Discussions**: [Ask questions or share ideas](https://github.com/openfinops/openfinops/discussions)
- **GitHub Issues**: [Report bugs or request features](https://github.com/openfinops/openfinops/issues)
- **Email**: durai@infinidatum.net
- **Community Calls**: Monthly (schedule TBD)

## 🌟 Recognition

Contributors will be:
- Listed in project CONTRIBUTORS.md
- Mentioned in release notes for significant contributions
- Invited to become maintainers for sustained contributions
- Featured in community showcases for innovative plugins

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to OpenFinOps! 🎉

**Let's build the future of FinOps together!** 🚀

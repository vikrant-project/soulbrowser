# Contributing to Soul Browser

Thank you for your interest in contributing to Soul Browser! We welcome contributions from the community.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming environment.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Soul Browser version
   - Platform (OS, architecture)
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Describe:
   - Use case
   - Proposed solution
   - Alternatives considered

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run linting (`ruff check .`)
6. Commit with descriptive message
7. Push to your fork
8. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/soulbrowser.git
cd soulbrowser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small
- Write tests for new features

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues when applicable (`Fixes #123`)

## Architecture

```
soulbrowser/
├── __init__.py      # Public API
├── browser.py       # Core browser launch functions
├── config.py        # Configuration and constants
├── download.py      # Binary download management
├── privacy/         # Privacy protection modules
├── adblock/         # Ad blocking
├── performance/     # Performance optimization
├── security/        # Security features
├── automation/      # Automation tools
├── devtools/        # Developer tools
├── web3/            # Web3 integration
├── ai/              # AI features
└── human/           # Human-like behavior
```

## Testing

- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- All tests: `pytest`

## Questions?

- Open a [Discussion](https://github.com/vikrant-project/soulbrowser/discussions)
- Email: soulbrowser@soulbrowser.dev

Thank you for contributing!

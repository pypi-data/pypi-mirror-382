# Contributing to TinyEdgeLLM

We welcome contributions from the community! This document outlines the process for contributing to TinyEdgeLLM.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/krish567366/tinyedgellm.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -e .[dev]`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest tests/`
4. Format code: `black tinyedgellm/ tests/`
5. Lint code: `flake8 tinyedgellm/ tests/`
6. Commit your changes: `git commit -m "Add your commit message"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Code Style

- Use Black for code formatting
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting a PR
- Aim for >80% code coverage

## Documentation

- Update documentation for any new features
- Use clear, concise language
- Include code examples where appropriate

## Issues

- Use GitHub issues to report bugs or request features
- Provide detailed information including:
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (OS, Python version, etc.)

## License

By contributing to TinyEdgeLLM, you agree that your contributions will be licensed under the MIT License.
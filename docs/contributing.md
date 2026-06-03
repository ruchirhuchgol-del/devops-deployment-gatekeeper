# Contributing to DevSecOps Deployment Gatekeeper

Thank you for your interest in contributing to the DevSecOps Deployment Gatekeeper! We welcome contributions from the community to help improve the project.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Write tests for your changes
6. Run the test suite to ensure everything works
7. Submit a pull request

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. Run tests to ensure everything is working:
   ```bash
   python tests/run_tests.py
   ```

## Code Style

We follow the PEP 8 style guide for Python code. Please ensure your code adheres to these standards.

### Naming Conventions
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants

### Documentation
- All public methods and classes should have docstrings
- Use Google-style docstrings
- Include type hints for function parameters and return values

## Testing

All contributions must include appropriate tests. We use the unittest framework for testing.

### Writing Tests
1. Place tests in the `tests/` directory
2. Name test files `test_*.py`
3. Follow the existing test structure
4. Use descriptive test method names
5. Include both positive and negative test cases

### Running Tests
```bash
python tests/run_tests.py
```

Or run individual test files:
```bash
python -m pytest tests/test_agents.py
```

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation if you've changed functionality
3. Add yourself to the contributors list (if you want to be listed)
4. Submit a pull request with a clear description of your changes

### Pull Request Guidelines
- Keep pull requests focused on a single feature or bug fix
- Include a clear description of what the pull request does
- Reference any related issues
- Ensure your code follows the project's style guidelines

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. Include as much detail as possible, including:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Environment information (Python version, OS, etc.)

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## Questions?

If you have any questions about contributing, feel free to open an issue or contact the maintainers.
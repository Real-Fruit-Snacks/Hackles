# Contributing to Hackles

Thank you for your interest in contributing to Hackles! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Real-Fruit-Snacks/hackles.git
   cd hackles
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Run tests to verify setup:
   ```bash
   pytest tests/
   ```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for function signatures
- Keep lines under 100 characters
- Use descriptive variable and function names

## Adding New Queries

1. Create a new file in the appropriate category folder under `hackles/queries/`
2. Use the `@register_query` decorator:
   ```python
   @register_query(
       name="Query Name",
       category="Category",
       default=True,
       severity=Severity.HIGH
   )
   def get_query_name(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
       """Query docstring"""
       # Implementation
       return result_count
   ```
3. Follow the existing patterns in similar query files
4. Add abuse templates to `hackles/abuse/templates/` if applicable

## Adding Abuse Templates

Create a YAML file in `hackles/abuse/templates/`:

```yaml
name: AttackName
description: Brief description of the attack
commands:
  - tool: ToolName
    command: "command with <PLACEHOLDER> values"
    description: What this command does
opsec:
  - Security consideration
references:
  - https://example.com/reference
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit with a descriptive message
6. Push to your fork
7. Open a Pull Request

## Testing

- Write tests for new functionality
- Ensure existing tests pass
- Run the test suite:
  ```bash
  pytest tests/ -v
  pytest tests/ --cov=hackles --cov-report=html  # With coverage
  ```

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- BloodHound CE version
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages

## Questions?

Open an issue for questions or discussion about potential contributions.

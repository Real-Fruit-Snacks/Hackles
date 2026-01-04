## Description

Brief description of the changes in this PR.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] New security query
- [ ] New abuse template
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] CI/CD or build changes

## Related Issues

Fixes #(issue number)

<!-- Or use: Closes #, Resolves #, Related to # -->

## Changes Made

- Change 1
- Change 2
- Change 3

## New Query Details (if applicable)

If adding a new security query:

- **Query Name:**
- **Category:** (ACL Abuse / ADCS / Credentials / Delegation / etc.)
- **Severity:** (CRITICAL / HIGH / MEDIUM / LOW / INFO)
- **Description:** What does this query detect?

## Testing

### How to Test

1. Step 1
2. Step 2
3. Expected result

### Test Results

```bash
# Output from running the feature/fix
```

## Checklist

### Code Quality

- [ ] My code follows the existing code style of this project
- [ ] I have added/updated docstrings for new functions
- [ ] I have updated the CHANGELOG.md (if applicable)
- [ ] My changes generate no new warnings

### Testing

- [ ] I have run `pytest tests/` and all tests pass
- [ ] I have added tests for new functionality (if applicable)
- [ ] I have tested with multiple output formats (--json, --csv, --html) if relevant

### Documentation

- [ ] I have updated the README.md if needed
- [ ] I have updated CLAUDE.md if adding new patterns/conventions
- [ ] I have added abuse templates for new attack queries (if applicable)

### Security

- [ ] I have not committed any sensitive data (credentials, API keys, etc.)
- [ ] New queries do not expose sensitive information inappropriately
- [ ] Abuse templates include appropriate OPSEC warnings

## Screenshots (if applicable)

<!-- Add screenshots of new output or UI changes -->

## Additional Notes

<!-- Any other information reviewers should know -->

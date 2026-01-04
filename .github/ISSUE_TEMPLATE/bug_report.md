---
name: Bug Report
about: Report a bug or unexpected behavior in Hackles
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of the bug.

## Command Used

```bash
python -m hackles [your command here]
```

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened. Include any error messages or tracebacks.

## Steps to Reproduce

1. Run command '...'
2. With these arguments '...'
3. See error

## Error Output

```
Paste the full error message or traceback here
```

## Environment

- **Hackles Version:** (run `python -c "import hackles; print(hackles.__version__)"`)
- **Python Version:** (run `python --version`)
- **Operating System:** (e.g., Ubuntu 22.04, Windows 11, macOS 14)
- **BloodHound CE Version:** (check BloodHound UI or docker image tag)
- **Neo4j Version:** (run `CALL dbms.components() YIELD name, versions` in Neo4j Browser)

## BloodHound Data

- **Data Collection Tool:** (SharpHound / BloodHound.py / AzureHound)
- **Collection Version:** (if known)
- **Domain Count:** (single domain / multi-domain / forest)

## Additional Context

Add any other context about the problem here. For example:
- Does this only happen with certain query categories?
- Does it work with different output formats (--json, --csv)?
- Have you tried with `--debug` flag for more details?

## Checklist

- [ ] I have checked existing issues for duplicates
- [ ] I have included the full error message/traceback
- [ ] I have tried with `--debug` flag to get more information
- [ ] I can reproduce this issue consistently

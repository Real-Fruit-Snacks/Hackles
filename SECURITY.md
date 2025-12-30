# Security Policy

## Scope

Hackles is a security assessment tool designed for authorized penetration testing and security research. It queries BloodHound Community Edition's Neo4j database to identify Active Directory misconfigurations and attack paths.

**This tool is intended for:**
- Authorized penetration testers
- Security researchers
- Red team operators
- System administrators auditing their own environments

## Reporting a Vulnerability

If you discover a security vulnerability in Hackles, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email the maintainer directly with details of the vulnerability
3. Include steps to reproduce the issue
4. Allow reasonable time for a fix before public disclosure

## Security Considerations

### Credentials

- Never commit Neo4j credentials to version control
- Use environment variables for sensitive values:
  ```bash
  export NEO4J_PASSWORD="your-password"
  python -m hackles -p "$NEO4J_PASSWORD" -a
  ```

### Network Security

- Hackles connects to Neo4j over the Bolt protocol (default port 7687)
- Ensure your Neo4j instance is not exposed to untrusted networks
- Use TLS/SSL for production Neo4j deployments

### Output Files

- Query results may contain sensitive Active Directory information
- Protect output files (JSON, CSV, HTML reports) appropriately
- Do not share BloodHound data without authorization

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Responsible Use

This tool is provided for legitimate security testing purposes only. Users are responsible for:

- Obtaining proper authorization before testing
- Complying with all applicable laws and regulations
- Following their organization's security policies
- Protecting any sensitive data discovered during assessments

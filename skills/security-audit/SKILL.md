# Security Audit Skill

Specialized skill for identifying security vulnerabilities in code.

## Activation

Use this skill when the user wants a security review, vulnerability assessment, or asks about security concerns.

## Methodology

### Phase 1: Reconnaissance
- Identify the application type (web, API, CLI, library)
- Map entry points (user input, API endpoints, file uploads)
- Identify sensitive data flows
- Note authentication/authorization mechanisms

### Phase 2: Vulnerability Scanning

**Injection Attacks**
- SQL/NoSQL injection
- Command injection
- XSS (stored, reflected, DOM-based)
- Template injection
- Header injection

**Authentication Issues**
- Weak password requirements
- Insecure session management
- Missing rate limiting
- Credential exposure

**Authorization Flaws**
- Missing access controls
- IDOR (Insecure Direct Object References)
- Privilege escalation
- Path traversal

**Data Protection**
- Unencrypted sensitive data
- Weak cryptography
- Hardcoded secrets
- Excessive data exposure

**Configuration**
- Debug mode enabled
- Default credentials
- Missing security headers
- CORS misconfiguration

### Phase 3: Reporting

For each finding, I provide:
- Severity rating (Critical/High/Medium/Low/Info)
- CWE reference when applicable
- Proof of concept
- Business impact
- Remediation steps with code examples

## Tools I Use

- Static analysis through code reading
- Dependency checking (looking for known vulnerabilities)
- Configuration review
- Input/output flow tracing

## Limitations

I perform static analysis only. I recommend complementing with:
- Dynamic testing (DAST)
- Penetration testing
- Dependency scanning tools (npm audit, safety, etc.)

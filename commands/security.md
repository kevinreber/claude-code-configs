# Security Audit

Perform a security-focused code review.

## Instructions

Audit: $ARGUMENTS

### OWASP Top 10 Checklist

#### 1. Injection
- [ ] SQL injection
- [ ] NoSQL injection
- [ ] Command injection
- [ ] LDAP injection
- [ ] XPath injection

#### 2. Broken Authentication
- [ ] Weak password policies
- [ ] Missing MFA
- [ ] Session fixation
- [ ] Credential stuffing vulnerability

#### 3. Sensitive Data Exposure
- [ ] Unencrypted sensitive data
- [ ] Weak cryptography
- [ ] Missing HTTPS
- [ ] Sensitive data in logs

#### 4. XML External Entities (XXE)
- [ ] Unsafe XML parsing
- [ ] DTD processing enabled

#### 5. Broken Access Control
- [ ] Missing authorization checks
- [ ] IDOR vulnerabilities
- [ ] Privilege escalation paths
- [ ] CORS misconfiguration

#### 6. Security Misconfiguration
- [ ] Default credentials
- [ ] Unnecessary features enabled
- [ ] Missing security headers
- [ ] Verbose error messages

#### 7. Cross-Site Scripting (XSS)
- [ ] Reflected XSS
- [ ] Stored XSS
- [ ] DOM-based XSS
- [ ] Missing output encoding

#### 8. Insecure Deserialization
- [ ] Untrusted data deserialization
- [ ] Missing integrity checks

#### 9. Using Components with Known Vulnerabilities
- [ ] Outdated dependencies
- [ ] Unpatched libraries

#### 10. Insufficient Logging & Monitoring
- [ ] Missing security event logging
- [ ] No alerting on suspicious activity

### Additional Checks
- Secrets in code or config
- Insecure randomness
- Race conditions
- Path traversal
- Open redirects
- SSRF vulnerabilities

## Output Format

```markdown
## Security Audit Report: [Target]

### Executive Summary
[Overall security posture assessment]

### Critical Findings
| ID | Vulnerability | Location | Severity | CVSS |
|----|--------------|----------|----------|------|
| 1  | SQL Injection | file:line | Critical | 9.8 |

### Detailed Findings

#### [VULN-001] SQL Injection
- **Severity**: Critical
- **Location**: `src/db/queries.ts:45`
- **Description**: User input directly concatenated into SQL query
- **Impact**: Full database access, data exfiltration
- **Remediation**: Use parameterized queries
- **Example Fix**:
  ```typescript
  // Before (vulnerable)
  query(`SELECT * FROM users WHERE id = ${userId}`)

  // After (safe)
  query('SELECT * FROM users WHERE id = ?', [userId])
  ```

### Recommendations
1. [Priority-ordered security improvements]

### Compliance Notes
[Relevant compliance considerations: GDPR, HIPAA, etc.]
```

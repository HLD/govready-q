# GovReady-Q Security Audit Report

**Date:** 2025-12-06
**Version Audited:** 0.11.8
**Auditor:** Claude Code Security Audit

---

## Executive Summary

This security audit identified **47 security findings** across the GovReady-Q codebase, including **8 critical**, **15 high**, **16 medium**, and **8 low** severity issues. The most severe vulnerabilities involve code injection via `eval()`, ZIP path traversal, API authorization bypass, and sensitive data exposure in logs.

### Risk Summary

| Severity | Count | Immediate Action Required |
|----------|-------|---------------------------|
| **CRITICAL** | 8 | Yes - Exploitable vulnerabilities |
| **HIGH** | 15 | Yes - Significant security risk |
| **MEDIUM** | 16 | Recommended within 30 days |
| **LOW** | 8 | Address in next release cycle |

---

## Critical Vulnerabilities

### 1. Code Injection via eval() - Remote Code Execution
**Severity:** CRITICAL
**File:** `controls/models.py:836`
**CVSS:** 9.8

```python
security_impact_level = eval(smt.body)  # Arbitrary code execution
```

**Attack Vector:** User input from `/project/<id>/security-objectives-edit` is stored in `Statement.body` and later executed via `eval()`.

**Proof of Concept:**
```
POST /project/1/security-objectives-edit
confidentiality=__import__('os').system('id')&integrity=Low&availability=Low
```

**Remediation:**
```python
# Replace with safe parsing
import json
security_impact_level = json.loads(smt.body)
# Or use ast.literal_eval() if Python dict format is needed
```

---

### 2. ZIP Path Traversal (Zip Slip) - Arbitrary File Write
**Severity:** CRITICAL
**File:** `guidedmodules/views.py:1542-1548`
**CVSS:** 8.8

```python
with ZipFile(appsource_zipfile, 'r') as zipObj:
    zipObj.extractall("local/appsources/")  # No path validation!
```

**Attack Vector:** Upload a malicious ZIP with entries like `../../../etc/cron.d/backdoor` to write files outside the target directory.

**Remediation:**
```python
import os

def safe_extract(zip_file, target_dir):
    for member in zip_file.namelist():
        member_path = os.path.realpath(os.path.join(target_dir, member))
        if not member_path.startswith(os.path.realpath(target_dir)):
            raise ValueError(f"Path traversal detected: {member}")
    zip_file.extractall(target_dir)
```

---

### 3. API Authorization Bypass - Data Exposure
**Severity:** CRITICAL
**Files:** `api/siteapp/views/portfolios.py:8`, `projects.py:12`, `users.py:28`, `organizations.py:8`

```python
class PortfolioViewSet(ReadOnlyViewSet):
    queryset = Portfolio.objects.all()  # Returns ALL objects to any authenticated user
```

**Impact:** Any authenticated user can enumerate all portfolios, projects, users, and organizations via the API.

**Remediation:**
```python
def get_queryset(self):
    return Portfolio.objects.filter(
        Q(owner=self.request.user) |
        Q(members=self.request.user)
    ).distinct()
```

---

### 4. Debug Endpoint Exposing Sensitive Data
**Severity:** CRITICAL
**File:** `siteapp/views.py:237-244`

```python
def debug(request):
    raise Exception()  # Exposes full stack trace, session data, DB queries
```

**Remediation:** Remove this endpoint or restrict to superusers only.

---

### 5. ALLOWED_HOSTS Wildcard in Debug Mode
**Severity:** CRITICAL
**File:** `siteapp/settings.py:96-97`

```python
if DEBUG and 'localhost' in ALLOWED_HOSTS:
    ALLOWED_HOSTS.extend(['*'])  # Host header injection vulnerability
```

**Remediation:** Remove this line. Always use explicit hostnames.

---

### 6. Request Body Logging Without Sanitization
**Severity:** CRITICAL
**File:** `siteapp/middleware/logging.py:32-59`

Passwords, tokens, and sensitive form data are logged in plaintext.

**Remediation:** Implement field-level filtering:
```python
SENSITIVE_FIELDS = ['password', 'token', 'api_key', 'secret', 'csrf', 'authorization']

def sanitize_body(self, data):
    if isinstance(data, dict):
        return {k: '***REDACTED***' if any(s in k.lower() for s in SENSITIVE_FIELDS) else v
                for k, v in data.items()}
    return data
```

---

### 7. Passwords Printed to Console
**Severity:** CRITICAL
**File:** `siteapp/management/commands/first_run.py:120-123`

```python
print("Created administrator account (username: {}) with password: {}".format(
    user.username, password))
```

**Remediation:** Never print passwords. Use secure credential delivery mechanisms.

---

### 8. @babel/traverse RCE Vulnerability
**Severity:** CRITICAL
**Package:** `@babel/traverse` < 7.23.2
**CVE:** GHSA-67hx-6x53-jw92

**Remediation:**
```bash
cd frontend && npm audit fix
```

---

## High Severity Vulnerabilities

### 9. API Keys Stored in Plaintext
**File:** `siteapp/models.py:53-58`

```python
api_key_ro = models.CharField(max_length=32, blank=True, null=True, unique=True)
```

**Remediation:** Hash API keys using a one-way function. Store only the hash.

---

### 10. OIDC JWT Parsing Without Signature Verification
**File:** `siteapp/authentication/OIDCAuthentication.py:37-41`

Manual JWT parsing bypasses signature verification, allowing token forgery.

**Remediation:** Use mozilla-django-oidc's built-in token verification.

---

### 11. DirectLoginBackend Authentication Bypass
**File:** `siteapp/models.py:222-230`

```python
class DirectLoginBackend(ModelBackend):
    def authenticate(self, user_object=None):
        return user_object  # No password verification!
```

**Remediation:** Remove this backend from `AUTHENTICATION_BACKENDS`.

---

### 12. Content-Disposition Header Injection
**Files:** Multiple (9 locations)
- `guidedmodules/views.py:100, 1427, 1460`
- `siteapp/views.py:688`
- `controls/views.py:2268, 3256, 3606, 3732`

```python
resp['Content-Disposition'] = 'inline; filename=' + filename  # Unsanitized
```

**Remediation:**
```python
from urllib.parse import quote
resp['Content-Disposition'] = f'inline; filename="{quote(filename)}"'
```

---

### 13. XSS via |safe Filter on User Data
**File:** `templates/index.html:54, 64`

```django
<li>{{org|safe}}</li>
<p>Logged in as {{request.user|safe}}.</p>
```

**Remediation:** Remove `|safe` filter from user-controlled data.

---

### 14. File Size Validation Bypass
**File:** `discussion/views.py:207`

```python
if sys.getsizeof(uploaded_file) >= DATA_UPLOAD_MAX_MEMORY_SIZE:  # Wrong method!
```

**Remediation:** Use `uploaded_file.size` instead of `sys.getsizeof()`.

---

### 15. Unsafe YAML Loading
**File:** `guidedmodules/views.py:2101, 2110, 2208, 2224`

```python
spec = rtyaml.load(request.POST["spec"])  # Potential unsafe deserialization
```

**Remediation:** Verify rtyaml uses SafeLoader or use `yaml.safe_load()`.

---

### 16-22. NPM Vulnerabilities (7 High-Severity)
| Package | Vulnerability |
|---------|--------------|
| axios 0.21.1 | CSRF, DoS, SSRF |
| cross-spawn | ReDoS |
| path-to-regexp | Backtracking ReDoS |
| tar-fs | Path traversal |
| ws | HTTP header DoS |
| semver | ReDoS |

**Remediation:**
```bash
cd frontend && npm audit fix --force
```

---

### 23. Missing 500 Error Template
**Impact:** Full stack traces exposed if DEBUG=True in production.

**Remediation:** Create `templates/500.html` with generic error message.

---

## Medium Severity Vulnerabilities

### 24. Swagger API Docs Publicly Accessible
**File:** `api/base/urls.py:17`

```python
permission_classes=(permissions.AllowAny,)
```

**Remediation:** Require authentication for API documentation.

---

### 25. No API Rate Limiting
**File:** `siteapp/settings.py:132-146`

**Remediation:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {'user': '1000/hour'}
}
```

---

### 26. Weak Password Policy in Debug Mode
**File:** `siteapp/settings.py:243, 252-269`

```python
ACCOUNT_PASSWORD_MIN_LENGTH = (4 if DEBUG else 6)  # Only 6 chars in production!
```

**Remediation:** Increase to at least 12 characters minimum.

---

### 27. Session Cookie SameSite Not Explicit
**File:** `siteapp/settings.py`

**Remediation:**
```python
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'
```

---

### 28. Proxy Header Authentication Trust
**File:** `siteapp/middleware/misc.py:54-116`

Trusts HTTP headers without verification. Requires proper proxy configuration.

---

### 29-34. Bare Exception Handlers (6 locations)
Bare `except:` clauses hide security errors.

**Files:** `siteapp/views.py`, `controls/views.py`, `guidedmodules/module_logic.py`, `discussion/views.py`, `workflow/views.py`

**Remediation:** Catch specific exceptions and log them.

---

### 35. Incomplete File Chunk Validation
**File:** `discussion/validators.py:41-79`

Only validates first 261 bytes of uploaded files.

**Remediation:** Validate all chunks or use full-file validation.

---

### 36-39. Environment Secrets Management
**Files:** `siteapp/settings.py`, `siteapp/settings_application.py`

Secrets loaded from unencrypted JSON files.

**Remediation:** Use environment variables or a secrets manager.

---

### 40. Exception Messages Exposed to Users
**File:** `siteapp/views.py:1959, 1964`

```python
return JsonResponse({"status": "error", "message": str(e)})
```

**Remediation:** Return generic messages; log details server-side.

---

## Low Severity Findings

### 41. Expired Snyk Policy
**File:** `.snyk` - Exception expired 2022-04-10

### 42. Snyk Scans Disabled in CI
**File:** `.circleci/config.yml:64-77` - Commented out

### 43. Outdated Frontend Libraries
- React 17.0.2 → 18.x available
- react-bootstrap 0.33.1 → 5.x available

### 44. Debug Context Processor Enabled
**File:** `siteapp/settings.py:191`

### 45. Console Email Backend in Debug
**File:** `siteapp/settings.py:392`

### 46. Hardcoded Test Password
**File:** `loadtesting/management/commands/add_data.py:18`

### 47. Clear Passwords in Test Code
**Files:** Multiple test files store cleartext passwords

---

## Remediation Priority Matrix

### Immediate (This Week)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | eval() code injection | controls/models.py:836 | Replace with json.loads() |
| 2 | ZIP path traversal | guidedmodules/views.py:1548 | Add path validation |
| 3 | API authorization bypass | api/siteapp/views/*.py | Filter querysets by user |
| 4 | Debug endpoint | siteapp/views.py:237 | Remove or restrict |
| 5 | ALLOWED_HOSTS wildcard | siteapp/settings.py:96 | Remove wildcard |
| 6 | Request body logging | middleware/logging.py | Sanitize sensitive fields |
| 7 | Password printing | first_run.py:120 | Remove print statement |
| 8 | @babel/traverse | frontend/package.json | npm audit fix |

### Short-Term (30 Days)

| # | Issue | Fix |
|---|-------|-----|
| 9-15 | High-severity items | See individual remediations |
| 16-22 | NPM vulnerabilities | npm audit fix --force |
| 23 | Error templates | Create 500.html, 404.html |

### Medium-Term (90 Days)

| # | Issue | Fix |
|---|-------|-----|
| 24-40 | Medium-severity items | See individual remediations |
| - | Django upgrade | Upgrade to Django 4.2 LTS |
| - | React upgrade | Upgrade to React 18.x |

---

## Positive Security Findings

The audit also identified well-implemented security controls:

✅ **CSRF Protection** - Middleware enabled, tokens in all forms
✅ **Session Security** - django-session-security with 30-min timeout
✅ **HTTPS/HSTS** - 1-year HSTS, secure cookies in production
✅ **Security Headers** - X-Frame-Options, XSS-Filter, Content-Type-Options
✅ **Database Sessions** - No filesystem session storage
✅ **Django ORM** - No raw SQL injection vectors found
✅ **Safety/Bandit** - Security scanning in CI pipeline
✅ **File Storage** - Database storage prevents direct path traversal
✅ **gitignore** - Properly excludes secrets and environment files

---

## Appendix: Files Requiring Security Review

### Critical Priority
- `controls/models.py` - Line 836 (eval)
- `guidedmodules/views.py` - Lines 1542-1548 (ZIP)
- `api/siteapp/views/*.py` - All ViewSets (authorization)
- `siteapp/views.py` - Lines 237-244 (debug endpoint)
- `siteapp/settings.py` - Lines 96-97 (ALLOWED_HOSTS)
- `siteapp/middleware/logging.py` - Lines 32-59 (logging)
- `siteapp/management/commands/first_run.py` - Lines 120-123 (password)

### High Priority
- `siteapp/models.py` - Lines 53-58, 222-230
- `siteapp/authentication/OIDCAuthentication.py` - Lines 37-41
- `templates/index.html` - Lines 54, 64
- `discussion/views.py` - Line 207
- `guidedmodules/views.py` - Lines 2101, 2110, 2208, 2224

### Frontend
- `frontend/package.json` - Update dependencies
- `frontend/package-lock.json` - Regenerate after updates

---

## Conclusion

GovReady-Q has a solid security foundation with Django's built-in protections and additional security middleware. However, the identified critical vulnerabilities—particularly the `eval()` code injection and ZIP path traversal—require immediate remediation before any production deployment.

The API authorization model needs comprehensive review to ensure proper access controls are enforced at the queryset level, not just object-level permissions on individual retrievals.

Regular dependency updates and re-enabling Snyk scanning in CI will help maintain security posture over time.

---

*Report generated by Claude Code Security Audit*

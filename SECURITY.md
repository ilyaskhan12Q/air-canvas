# Security Policy 🔒

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Active support  |
| < 1.0   | ❌ No longer supported |

---

## 🚨 Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, report them privately using one of these methods:

### Option A — GitHub Private Vulnerability Reporting (preferred)
1. Go to the repository on GitHub
2. Click **Security** → **Advisories** → **Report a vulnerability**
3. Fill in the details and submit

### Option B — Email
Send a report to **security@your-domain.example** with:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations

We will acknowledge receipt within **48 hours** and aim to provide a resolution timeline within **7 days**.

---

## 🛡️ Security Scope

### In scope
- Remote code execution via crafted input
- Denial of service via webcam/frame processing
- Dependency vulnerabilities in `requirements.txt`
- Data leakage from session state

### Out of scope
- Social engineering
- Physical access to a user's machine
- Issues in third-party libraries that are already publicly disclosed (please report those upstream)

---

## 🔐 Dependency Security

We use GitHub's **Dependabot** to automatically flag outdated or vulnerable dependencies.  
You can also audit manually:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

---

## 🏆 Responsible Disclosure

We follow a **90-day coordinated disclosure** policy. After a fix is shipped, we will:
1. Publish a **GitHub Security Advisory**
2. Credit the reporter (unless anonymity is requested)
3. Add an entry to `CHANGELOG.md`

Thank you for helping keep Air Canvas safe! 🙏

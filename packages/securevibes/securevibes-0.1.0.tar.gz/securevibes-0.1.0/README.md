# 🛡️ SecureVibes

**AI-Native Platform to Secure Vibecoded Applications**

SecureVibes leverages Claude Agent SDK's autonomous orchestration to find security vulnerabilities in your code. Claude intelligently coordinates specialized agents for comprehensive, context-aware vulnerability detection.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.2-green.svg)](https://github.com/anshumanbh/securevibes/releases)
[![Tests](https://img.shields.io/badge/tests-74%20passed-success.svg)](https://github.com/anshumanbh/securevibes)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ Features

### True Agent Architecture
- **🤖 Autonomous Orchestration**: Claude intelligently coordinates agents
- **📐 Assessment Agent**: Maps your codebase architecture
- **🎯 Threat Modeling Agent**: Architecture-driven STRIDE threat analysis
- **🔍 Code Review Agent**: Security thinking methodology to find vulnerabilities
- **📊 Report Generator**: Compiles comprehensive scan results

### What It Finds
- 🔴 **Critical**: SQL Injection, Command Injection, RCE
- 🟠 **High**: XXE, SSRF, Authentication Bypass
- 🟡 **Medium**: XSS, CSRF, Weak Crypto
- 🟢 **Low**: Information Disclosure, Misconfigurations

### Results Include
- ✅ Exact file paths and line numbers
- ✅ Vulnerable code snippets
- ✅ CWE IDs for tracking
- ✅ Remediation recommendations
- ✅ Evidence of exploitability

---

## 🚀 Quick Start

```bash
# Install
pip install securevibes

# Set API key (get yours from https://console.anthropic.com/)
export CLAUDE_API_KEY="your-api-key-here"

# Scan your project
securevibes scan .

# View results
securevibes report
```

---

## 📊 Example Output

```bash
$ securevibes scan /path/to/pygoat

╭────────────────────────────────────╮
│ 🛡️  SecureVibes Multi-Agent Scanner  │
│ AI-Powered Vulnerability Detection │
╰────────────────────────────────────╯

━━━ Phase 1/3: Architecture Assessment ━━━
🤖 [Assessment] Starting analysis...
✅ [Assessment] Complete

━━━ Phase 2/3: Threat Modeling ━━━
🤖 [Threat Modeling] Starting analysis...
✅ [Threat Modeling] Complete - Identified 20 threats

━━━ Phase 3/3: Security Code Review ━━━
🤖 [Code Review] Starting analysis...
✅ [Code Review] Complete - Found 10 confirmed vulnerabilities

================================================================================
📊 Scan Results
================================================================================

  📁 Files scanned:   88
  ⏱️  Scan time:       42.87s
  🐛 Issues found:    10
     🔴 Critical:     8
     🟠 High:         2
     🟡 Medium:       0
     🟢 Low:          0

                              🔍 Detected Vulnerabilities
╭─────┬────────────┬──────────────────────────────────┬─────────────────────────╮
│ #   │ Severity   │ Issue                            │ Location                │
├─────┼────────────┼──────────────────────────────────┼─────────────────────────┤
│ 1   │ CRITICAL   │ SQL Injection in user login      │ views.py:157            │
│ 2   │ CRITICAL   │ Command Injection via subprocess │ views.py:423            │
│ 3   │ CRITICAL   │ Remote Code Execution via YAML   │ views.py:553            │
│ ... │ ...        │ ...                              │ ...                     │
╰─────┴────────────┴──────────────────────────────────┴─────────────────────────╯

💾 Full report: .securevibes/scan_results.json
```

---

## 🎯 Usage

### Basic Commands

```bash
# Full security scan
securevibes scan .

# View results
securevibes report

# Individual phases (optional)
securevibes assess .        # Phase 1: Architecture mapping
securevibes threat-model .  # Phase 2: STRIDE analysis
securevibes review .        # Phase 3: Vulnerability validation
```

### Common Options

```bash
# Export results as JSON
securevibes scan . --format json --output results.json

# Filter by severity
securevibes scan . --severity high

# Use different model
securevibes scan . --model claude-3-5-haiku-20241022

# Quiet mode
securevibes scan . --quiet
```

For complete CLI reference and all options, see [CLI Documentation](docs/CLI.md)

---

## 🐍 Python API

For programmatic access:

```python
import asyncio
from securevibes import SecurityScanner

async def main():
    scanner = SecurityScanner(
        api_key="your-api-key",  # or use CLAUDE_API_KEY env var
        model="claude-3-5-sonnet-20241022"
    )
    
    result = await scanner.scan("/path/to/repo")
    
    print(f"Found {len(result.issues)} vulnerabilities")
    print(f"Critical: {result.critical_count}")
    print(f"High: {result.high_count}")
    
    for issue in result.issues:
        print(f"\n[{issue.severity.value.upper()}] {issue.title}")
        print(f"  File: {issue.file_path}:{issue.line_number}")
        print(f"  CWE: {issue.cwe_id}")
        print(f"  Fix: {issue.recommendation}")

asyncio.run(main())
```

---

## ⚙️ Configuration

SecureVibes is configurable via environment variables:

```bash
# Configure agent models (default: sonnet)
export SECUREVIBES_CODE_REVIEW_MODEL="opus"  # For maximum accuracy

# Configure max reasoning turns (default: 50)
export SECUREVIBES_MAX_TURNS=75  # For large codebases

# Run scan
securevibes scan .
```

**Quick Configuration:**
- **Models**: Choose `haiku` (fast/cheap), `sonnet` (balanced), or `opus` (thorough/expensive)
- **Max Turns**: Increase for complex codebases (75-100), decrease for simple ones (25-40)

For complete configuration options and optimization tips, see [ARCHITECTURE.md](docs/ARCHITECTURE.md#configuration)

---

## 🏗️ How It Works

SecureVibes uses a **multi-agent architecture** where Claude autonomously orchestrates 4 specialized agents:

1. **Assessment Agent** → Analyzes architecture → `SECURITY.md`
2. **Threat Modeling Agent** → Applies STRIDE → `THREAT_MODEL.json`
3. **Code Review Agent** → Validates vulnerabilities → `VULNERABILITIES.json`
4. **Report Generator** → Compiles results → `scan_results.json`

**Key Benefits:**
- ✅ Claude intelligently adapts to your codebase
- ✅ Agents build on each other's findings
- ✅ Security thinking methodology (not just pattern matching)
- ✅ Concrete evidence with file paths and line numbers

For detailed architecture, agent descriptions, and data flow, see [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🔒 Privacy & Security

### Data Handling

**What SecureVibes Sends to Anthropic:**
- Your source code files
- Relative file paths within scanned repository

**What SecureVibes Does NOT Send:**
- Absolute paths containing usernames
- Environment variables or secrets
- Git history or metadata
- Files outside scanned directory

**Your API Key:** Stored locally, only used for Anthropic authentication

### Important Notes

⚠️ SecureVibes sends your code to Anthropic's Claude API for analysis.

Before scanning:
1. Review [Anthropic's Privacy Policy](https://www.anthropic.com/legal/privacy)
2. Don't scan proprietary code unless you've reviewed data handling
3. Consider scanning only public portions of sensitive codebases

---

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Multi-agent system design and workflow
- **[Testing Guide](docs/TESTING.md)** - Test suite documentation and coverage
- **[Development Guide](docs/DEVELOPMENT.md)** - Development setup and agent details
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to SecureVibes
- **[Changelog](docs/CHANGELOG.md)** - Version history and release notes
- **[Claude SDK Guide](docs/claude-agent-sdk-guide.md)** - Claude Agent SDK reference

---

## 🤝 Contributing

Contributions are welcome! We appreciate bug reports, feature requests, and code contributions.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run tests (`pytest tests/ -v`)
5. Format code (`black securevibes tests --line-length=100`)
6. Commit changes (`git commit -m 'feat: add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

Please read our **[Contributing Guide](docs/CONTRIBUTING.md)** and **[Code of Conduct](docs/CODE_OF_CONDUCT.md)** before submitting.

---

## 🔒 Security

Found a security vulnerability? Please review our **[Security Policy](docs/SECURITY.md)** for responsible disclosure guidelines.

**⚠️ Do not open public issues for security vulnerabilities.**

---

## 🔄 Recent Changes

### v0.3.2 (Latest) - Critical Bug Fixes & Testing
- 🐛 **Fixed catastrophic false negative bug** (0 → 28 vulnerabilities reported)
- ✨ Added cost tracking and display
- 🧪 Added 44 regression tests (74 total, 100% pass rate)
- 🔧 Upgraded report-generator model (Haiku → Sonnet)
- 📊 Improved data validation and integrity

### True Agent Architecture
- 🎯 **Major Refactor**: Proper Claude Agent SDK implementation
- ✨ Agents now defined as `AgentDefinition` configurations
- 🤖 Claude autonomously orchestrates workflow
- 🗑️ Removed manual orchestrator (anti-pattern)
- 📦 Simplified codebase structure

See full **[Changelog](docs/CHANGELOG.md)** for details.
- 🚀 Better performance and flexibility

### v0.2.x
- Initial multi-agent implementation
- Manual orchestration via OrchestratorAgent
- File-based communication between agents

---

## 📜 License

**AGPL-3.0** - See [LICENSE](LICENSE)

This ensures SecureVibes stays free and open. If you use it in a service, you must open-source your modifications. Fair is fair! 🤝

---

## 👤 Author

Built by [@anshumanbh](https://github.com/anshumanbh)

🌟 Star the repo to follow along!

---

## 🙏 Acknowledgments

- Powered by [Claude](https://www.anthropic.com/claude) by Anthropic
- Built with [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- Inspired by traditional SAST tools but reimagined with AI

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/anshumanbh/securevibes/issues)
- **Discussions**: [GitHub Discussions](https://github.com/anshumanbh/securevibes/discussions)
- **Security**: Email anshuman.bhartiya@gmail.com

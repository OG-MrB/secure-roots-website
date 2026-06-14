---
layout: post
title: "Your AI Coding Assistant Is Production Infrastructure—Treat It Like It"
date: 2026-05-13 09:00:00 -0700
categories: [Cybercrime & Threat Awareness]
image: /img/your-ai-coding-assistant-is-production-infrastructure.png
description: "AI coding assistants run shell commands, read your filesystem, and use your credentials. The default configuration of every major vendor is a security incident waiting to happen. Here's the baseline every CISO should require before they ship code."
publish_social: true
---

The pitch is irresistible. Plug in an AI coding assistant. Watch it ship features. Sleep better.

The default configuration, on the other hand, is a security incident waiting to happen. And the gap between "works out of the box" and "production-ready" is wider than most teams realize—because the people selling these tools are optimizing for first-run delight, not for your audit posture.

We've been saying this for months internally. A widely-circulated LinkedIn post made the same case last week and it's been making the rounds with security leaders ever since. We agree with the diagnosis. This post is what we'd add to the prescription.

---

## What Your AI Coding Assistant Can Actually Do

Take Claude Code, GitHub Copilot, Cursor, Windsurf, or any of the agentic peers. Out of the box, with the defaults vendors ship, a typical AI coding assistant can:

- **Run shell commands.** Not just `ls` and `git status`. Anything the user can run. `rm -rf`, `curl | sh`, `psql -c "DROP TABLE …"`.
- **Read your filesystem.** Not just the project directory. With default permissions, it can read `~/.ssh/`, `~/.aws/`, `~/Library/Keychains/`, your browser cookie database, your `.env` files.
- **Use your credentials.** Whatever the running user has access to—cloud roles, GitHub tokens, database passwords—the agent has access to.
- **Modify files.** Including ones it didn't read first.
- **Reach out to the internet.** Defaults often allow `WebFetch(domain:*)`—anything, anywhere.
- **Call MCP tools.** Connections to Gmail, Slack, Jira, GitHub, Linear, your CI system, your databases.
- **Install packages.** `npm install`, `pip install`, `brew install`—real attack surface, real supply-chain exposure.

That is not a productivity tool. That is production infrastructure with delegated authority. A new full-stack engineer doesn't get this much trust on day one. Your AI agent does.

---

## The Incidents Are Already Public

This isn't theoretical. In July 2025, an autonomous AI agent at a major dev-tools company executed a chain of operations that deleted a production database during what should have been a code-freeze window. The instruction "don't write to production" did not prevent the deletion. The audit trail to reconstruct what happened was incomplete. The agent was operating with credentials that should never have been in its session in the first place.

In January 2025, security researchers at Wiz discovered DeepSeek's ClickHouse database exposed to the internet with no authentication, leaking chat history and operational data. The defenders never knew it was exposed. The attackers needed nothing more than `curl`.

In late 2024, the LangChain Python REPL agent CVE (CVE-2023-29374, since hardened) showed how a single tool the AI was permitted to call could be coaxed into arbitrary code execution by an attacker controlling part of the input.

The pattern: **the failure mode is not "the AI made one bad decision."** The failure mode is "the AI made 200 decisions in 10 minutes because there was no governor, no audit, no kill switch, and no human in the loop."

---

## What a Real Baseline Looks Like

We organize the controls into eight families. Each maps to NIST SP 800-53 Rev 5, NIST AI Risk Management Framework 1.0, OWASP Top 10 for LLM Applications, and the AI-specific clauses of ISO/IEC 42001. Compressed:

1. **Identity & Access.** The agent's authority is explicit and minimal. No `Bash(*)`. No `WebFetch(domain:*)`. No `$HOME`-level filesystem reads. MCP tokens scoped to the smallest verb that does the job—a search-only Gmail token, a read-only Slack token. Production credentials never reach a development agent.

2. **Secrets Management.** No `.env` in repos. No keys in permission-rule text. No credentials in audit logs. Vault by default—KeePassXC for solo operators, 1Password Teams or HashiCorp Vault for organizations. Quarterly rotation, immediate rotation on exposure.

3. **Input/Output Validation.** PreToolUse hooks scan every file write for secret patterns (`sk-ant-`, `sk-proj-`, `AKIA…`, `ghp_`, JWTs, RSA headers). They block, log, and surface a reason. Bash commands are linted against a dangerous-pattern list before they run. Tool results are scanned for prompt-injection markers before the agent acts on them.

4. **Logging & Audit.** Every tool call generates one append-only JSON line: timestamp, session, tool name, args hash, args (with secrets redacted), exit code, response size. The log file is integrity-hashed weekly. For regulated workloads, the JSONL is shipped to your SIEM with detection rules tuned to the high-risk events.

5. **Network Egress Control.** Per-domain `WebFetch` allowlists. MCP traffic through an inspectable proxy. OSINT and scanning work routed through a VPN endpoint—never the operator's home IP. DNS sinkhole for known exfil destinations.

6. **Filesystem Boundary.** Project-root scoped reads. Hard deny on `~/.ssh/`, `~/.aws/`, browser cookie databases, password-manager files. Symlinks resolved before allowlist check.

7. **Supply Chain.** MCP servers provenance-verified. Plugins reviewed. Claude CLI / Copilot extension / Cursor version pinned. Model selection policy documented. Hook scripts version-controlled and code-reviewed before deploy.

8. **Incident Response & Kill Switch.** Documented procedure to terminate the agent session, revoke credentials it touched, preserve the audit log, and snapshot filesystem state. Rehearsed quarterly. Customer-disclosure templates pre-drafted.

---

## The Ten Controls Every CISO Should Require

If you want a shorter list to send your engineering leaders, this is the one:

1. The AI agent does not have `$HOME`-level filesystem access.
2. No secrets in `.env` files committed to any repo (`git log --all -- .env` returns nothing).
3. No API keys embedded in permission rule text or hook scripts.
4. PreToolUse hook blocks writes containing known secret patterns.
5. PreToolUse hook blocks `curl | sh`, `rm -rf /`, `mkfs`, `dd of=/dev/*`.
6. PostToolUse hook logs every tool call to an append-only JSONL with secret-pattern redaction.
7. `WebFetch` is allowlisted per-domain; no wildcard egress.
8. MCP tokens are scoped read-only or to specific verbs—no `admin`, no `write_all`.
9. Production credentials are unreachable from development agents.
10. The kill procedure is one page, rehearsed quarterly, and available in print.

If you can answer "yes, demonstrably" to all ten, you're at Baseline Tier 2 maturity. If you can't, you're not.

---

## What Secure Roots Is Doing

Before we sell this engagement, we ran it on ourselves. The day this work started, an audit of the founder's `~/.claude/` and `~/Desktop/SecureRoots/` revealed:

- An `.env` with live Anthropic and OpenAI API keys (locally, never committed—but exactly the pattern attackers harvest from compromised machines).
- A 2022-era project directory with a plaintext AWS access key, AWS secret key, and a Windows administrator password.
- Three live API keys embedded in Claude Code permission-rule text from past sessions, plus a real test credential of the form `email:password`.
- Two-hundred-forty-six permission patterns accumulated across two years of use, including wildcard Python execution, macOS Keychain enumeration, and full Chrome control with arbitrary JavaScript execution.
- Zero hooks. Zero audit log. Zero kill switch.

We rotated, scoped, hooked, and logged. We wrote the configuration package, the operator policy, the incident runbook, and the SIEM detection rules. The internal triage record is the first appendix in the engagement evidence we provide to clients.

The point is not that this is hard. The point is that even practitioners who write about this for a living don't have it done unless they consciously do it. The default is permissive; permissive is the same as wrong, once it stops being a toy.

---

## Where This Lands for Your Environment

For LA-area defense subcontractors preparing for CMMC L2, this maps directly to the AC, AU, CM, IA, and IR practice families. For medical and dental practices, it maps to HIPAA Security Rule §164.308 administrative safeguards and §164.312 technical safeguards. For CA state and county agencies, it maps to the StateRAMP Moderate baseline through the underlying NIST 800-53 Rev 5 controls.

The framework is one document. The engagement to apply it comes in three shapes: a free 90-minute discovery scorecard, a 40-hour fixed-fee Mini Hardening for SMB teams, and a vCISO retainer for organizations that want continuous coverage. For state and county procurements, we structure it as a phased Assessment / Remediation / Operational SOW with option years.

The future of AI-assisted development is not just faster. It needs to be safer, governed, observable, and revocable. None of those are optional, and none of them happen by accident.

[**Contact Secure Roots →**](/contact/)

---

### References

- Anthropic — Claude Code settings and hooks documentation: docs.claude.com/en/docs/claude-code/
- NIST SP 800-53 Rev 5 — Security and Privacy Controls for Information Systems and Organizations
- NIST AI Risk Management Framework 1.0
- ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management system
- OWASP Top 10 for Large Language Model Applications 2025: genai.owasp.org/llm-top-10/
- Model Context Protocol specification: modelcontextprotocol.io
- HIPAA Security Rule, 45 CFR §164 Subpart C
- CMMC Model 2.0
- Wiz Research — DeepSeek ClickHouse exposure disclosure, January 2025
- LangChain Python REPL agent OS command execution — CVE-2023-29374
- Secure Roots — AI/LLM Governance Baseline 1.0 (internal framework, anonymized excerpts available under NDA)

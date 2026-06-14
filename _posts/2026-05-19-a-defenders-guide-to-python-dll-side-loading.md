---
layout: post
title: "When Trusted Software Loads the Attacker's Code: A Defender's Guide to Python DLL Side-Loading"
date: 2026-05-19 09:00:00 -0700
categories: [Cybercrime & Threat Awareness]
image: /img/a-defenders-guide-to-python-dll-side-loading.png
description: "Attackers increasingly run their code inside your trusted, signed applications using DLL side-loading and embedded Python. Here is how the technique works at a high level, and the detection and hardening steps a small team can apply this week."
publish_social: false
---

A lot of security spending assumes the malware will look like malware. A strange executable. An unsigned binary. A file with a name no one recognizes. Your tools watch for that, and they should.

Modern intrusions increasingly do not look like that. The file on disk is a real, signed, well-known application. It launches normally. The malicious part is a library it loads on the way up, sitting quietly in the same folder, riding the trust of the program that loaded it. A growing share of that malicious code is now Python, executed inside a process that has every reason to look legitimate.

This post explains the technique at the level a defender needs, then spends most of its length on the part that matters: how a small team detects it and makes it harder, without buying anything new.

---

## How DLL Side-Loading Works, In Plain Terms

When a Windows program starts, it needs supporting libraries (DLLs) to run. To find them, Windows follows a defined search order. For many applications, one of the first places it looks is the folder the program itself launched from.

That search order is the opening. If an attacker can place a malicious DLL with the right name next to a legitimate, signed executable, the legitimate program will load and run the attacker's library, because it looked in its own folder first and found a match. The process is signed and trusted. The code running inside it is not. This is DLL side-loading, catalogued in the MITRE ATT&CK framework as Hijack Execution Flow: DLL Side-Loading (T1574.002), and the Windows DLL search order it abuses is documented publicly by Microsoft.

The Python angle is a refinement, not a different idea. CPython ships as an embeddable runtime. An attacker can deliver a trusted application alongside a Python runtime library and a script, and use side-loading so the script executes inside the trusted process. Offensive tooling has productized this pattern; the Black Hills Information Security tool "Pyramid" is a well-known public example that loads an embedded Python interpreter into a process and runs Python entirely in memory, which keeps the actual logic off disk where file-based scanning would see it. Loading and executing code from memory rather than a dropped file maps to Reflective Code Loading (T1620), and the Python execution itself to Command and Scripting Interpreter: Python (T1059.006).

We are deliberately not publishing a build-it walkthrough. The technique is public and well-understood by attackers already. What is underused is the defense, so that is where the rest of this goes.

---

## Why This Slips Past Common Defenses

Three properties make this effective, and each one points at a detection idea.

- **The process is trusted.** Allowlists and reputation systems that key on the executable see a known-good, signed binary. They are not wrong about the file. They are looking at the wrong layer.
- **The malicious code can avoid disk.** When the real logic runs as in-memory Python, signature-based file scanning has little to inspect. Detection has to move to behavior and to what gets loaded, not just what gets written.
- **It blends with normal Python.** Plenty of legitimate software embeds Python. The signal is not "Python ran." The signal is "Python ran somewhere it has no business running, loaded from a place it should not be."

The defensive thesis follows directly: you cannot reliably catch this by judging the executable. You catch it by watching which libraries trusted processes load, from where, and whether that pairing makes sense.

---

## Detection: What to Look For This Week

You do not need a new platform for most of this. You need the right telemetry turned on and a few specific questions asked of it.

### Turn On Module-Load Visibility

- Deploy Sysmon with a maintained configuration. Sysmon Event ID 7 records image and DLL loads, including the loaded module's path and signature status. A widely used, well-commented community baseline (commonly referred to as the SwiftOnSecurity Sysmon configuration) is a reasonable starting point and is free. Without module-load logging, most of the hunts below are not possible.
- Confirm your endpoint protection or EDR records library loads and surfaces unsigned or unknown-hash modules. Many products collect this but do not alert on it by default.

### Ask These Specific Questions

- **Is a signed, trusted binary loading an unsigned or unknown DLL from a user-writable directory?** Side-loading frequently stages the malicious library in a path the user can write: a Downloads folder, a temp directory, `%APPDATA%`, or a "portable app" folder. A reputable application loading an unsigned DLL out of `C:\Users\...\Downloads\` is a strong lead.
- **Is a Python runtime library loading inside a process that is not a Python application?** An embedded interpreter library (for example, a `python3xx.dll`) loaded by a program that has no legitimate reason to embed Python is worth a hard look, especially if no corresponding `python.exe` is involved.
- **Is the loaded DLL name legitimate but the path or signature wrong?** Compare the module name against where it should normally live and who should normally sign it. A correctly named system or vendor DLL loading from an unexpected directory is a classic side-loading footprint, sometimes described as a phantom or relocated DLL.
- **Did a trusted process start making network connections or spawning command shells shortly after an unusual module load?** The load is the setup. Out-of-character network egress or child processes from a normally quiet application is the payoff, and the correlation is a high-confidence signal.

### Build a Small Baseline

You cannot spot "abnormal" without a sense of "normal." Spend an afternoon listing the handful of legitimate applications in your environment that genuinely embed Python or load DLLs from non-system paths. That short allowlist turns an overwhelming stream of module-load events into a much smaller set of exceptions worth reviewing.

---

## Hardening: Make the Technique Expensive

Detection tells you it happened. The following make it less likely to work at all, and none require new licensing for most small environments.

- **Block execution from user-writable locations.** Application control that prevents executables and DLLs from running out of Downloads, temp, and per-user profile paths removes the most common staging ground. Windows Defender Application Control and AppLocker can both enforce this; start in audit mode to measure impact before enforcing.
- **Move toward application allowlisting.** CISA has long recommended application allowlisting as a high-impact control. Even a partial rollout on high-value systems (finance workstations, administrator endpoints, servers) meaningfully constrains where untrusted code can run.
- **Be deliberate about "portable" applications.** Self-contained apps that run from a single folder are convenient and are also the natural delivery vehicle for a bundled malicious DLL. Treat unsanctioned portable apps as something to detect and discourage, not background noise.
- **Turn on script and command logging.** Enable PowerShell script-block and module logging, and command-line process auditing. Even when the malicious logic is in-memory Python, the surrounding activity (how it arrived, what it spawns) often surfaces here.
- **Reduce standing local administrator rights.** Many side-loading chains are far less effective without the ability to write to protected locations or install services. Least privilege on the endpoint is unglamorous and remains one of the most effective controls available.

---

## The Honest Framing

DLL side-loading is not exotic and not new. It is well-documented, actively used by both criminal and state-aligned actors, and effective precisely because it borrows trust your tools have correctly assigned to legitimate software. The Python and in-memory variants raise the bar further by keeping the meaningful code off disk.

The takeaway for a resource-constrained team is not "buy a side-loading product." It is a shift in where you look. Stop asking only "is this executable bad" and start asking "does it make sense that this trusted process just loaded that library, from that location." Most of the telemetry to answer that is free. Most of the hardening uses controls you already have. What is usually missing is the decision to turn them on and the small baseline that makes the alerts mean something.

---

## What Secure Roots Is Doing

We help clients operationalize exactly this shift: validating that module-load telemetry (Sysmon Event ID 7 or the EDR equivalent) is collected and retained, writing a starter set of hunts for trusted-process-loads-untrusted-library and embedded-Python-where-it-does-not-belong, building the short legitimate-software baseline that suppresses the noise, and staging an application-control rollout in audit mode before enforcement so it does not break the business. The work is scoped to fit a small team and to lean on tools the client already owns.

If you want to know whether you could even see this technique in your environment today, that is a question we can answer quickly.

[Contact Secure Roots](/contact/)

---

### References

- MITRE ATT&CK: Hijack Execution Flow: DLL Side-Loading (T1574.002), Reflective Code Loading (T1620), Command and Scripting Interpreter: Python (T1059.006). attack.mitre.org
- Microsoft, Dynamic-Link Library Search Order, learn.microsoft.com (documented Windows DLL search behavior the technique abuses).
- Black Hills Information Security, "Pyramid" project, public documentation and repository (cited as a well-known public example of in-memory embedded-Python execution; referenced for defensive context only).
- Sysmon documentation, Microsoft Sysinternals, learn.microsoft.com (Event ID 7, image/DLL load logging).
- SwiftOnSecurity Sysmon configuration, public community baseline (commonly used free starting configuration).
- CISA guidance on application allowlisting and reducing administrative privileges, cisa.gov.
- Microsoft documentation, Windows Defender Application Control and AppLocker (application control and audit-mode rollout).

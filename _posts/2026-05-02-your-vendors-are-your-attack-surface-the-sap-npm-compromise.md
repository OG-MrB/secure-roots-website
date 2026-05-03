---
layout: post
title: "Your Vendors Are Your Attack Surface: The SAP npm Compromise and the New Supply Chain Reality"
date: 2026-05-02 16:39:40 -0700
categories: [Cybercrime & Threat Awareness]
image: /img/your-vendors-are-your-attack-surface-the-sap-npm-compromise.png
description: "On April 29, attackers compromised four official SAP npm packages with 572,000 weekly downloads, stealing developer credentials and cloud secrets. Here's why every organization needs to treat third-party code and access as a primary attack surface—right now."
publish_social: false
---

On April 29, 2026, four official SAP npm packages were quietly weaponized. Not a typosquat. Not an abandoned project hijacked from a dead maintainer. Official packages—`mbt`, `@cap-js/db-service`, `@cap-js/postgres`, and `@cap-js/sqlite`—pulled roughly 572,000 times every week by developers who had every reason to trust them.

The attackers, a group tracked as TeamPCP running a campaign dubbed "Mini Shai-Hulud," embedded malicious preinstall scripts into those packages. The moment a developer ran `npm install`, the script executed. It harvested GitHub tokens, npm credentials, AWS keys, Azure secrets, GCP service accounts, Kubernetes tokens, and GitHub Actions secrets—then exfiltrated them through attacker-controlled repositories created under the victims' own GitHub accounts.

The same campaign hit the PyPI `Lightning` package (versions 2.6.2 and 2.6.3) and the `intercom-client` npm package, which alone sees about 360,000 weekly downloads. TeamPCP isn't new. They've previously compromised packages tied to Checkmarx, Bitwarden, Telnyx, LiteLLM, and Aqua Security's Trivy. This is a campaign with operational discipline, repeat success, and a growing victim list.

If you're reading this and thinking "we don't use SAP packages, we're fine"—that's exactly the wrong takeaway.

---

## This Is the Pattern, Not the Exception

Supply chain attacks have evolved from notable incidents into a continuous threat category. Look at the trajectory:

- **SolarWinds (2020)** showed that a trusted update mechanism could be turned into a delivery vehicle for nation-state malware reaching 18,000 organizations.
- **3CX (2023)** demonstrated that a compromised software vendor could ship a backdoored desktop client to hundreds of thousands of customers without anyone noticing for weeks.
- **MOVEit (2023)** proved that a single vulnerability in a widely deployed file transfer product could cascade into one of the largest data breach events in history, hitting thousands of downstream organizations.
- **Okta (2022, 2023)** reminded everyone that identity providers and the support tools around them are themselves high-value supply chain targets.
- **XZ Utils (2024)** revealed how a patient adversary could spend years building maintainer trust on an open-source project before planting a backdoor that nearly reached the Linux distributions running half the internet.

Each of these was treated as a watershed moment. Each one was followed by another. The SAP npm compromise is not the end of this story—it's the latest chapter in a book that keeps getting longer.

The pattern is clear: **attackers don't need to breach your perimeter when they can breach the people and code you already trust.**

---

## Why This Threat Is Different

Traditional security thinking treats vendors and dependencies as background infrastructure. You vet them at onboarding, get a SOC 2 report, sign a contract, and move on. The vendor is a checkbox in a procurement workflow.

Supply chain attackers exploit exactly that mental model. They know your developers will run `npm install` without reading the changelog. They know your IT team will apply vendor updates because that's what good IT teams do. They know your finance team will accept a routing number change from a known supplier because the email came from the right address. The trust you've extended to your vendors is the same trust the attacker hijacks.

And the scope of that trust is enormous. A modern application doesn't have a dozen dependencies—it has hundreds, often thousands once you count transitive dependencies. Every one of those packages is maintained by someone you've never met, hosted on infrastructure you don't control, and pulled into your build pipeline by automation that runs faster than any human review.

The SAP attack worked because preinstall scripts execute automatically. No user interaction required. No warning. The first time a developer noticed anything was when secrets started showing up in attacker-controlled repos.

---

## This Isn't Hypothetical to Us

Through the SolarWinds period, I worked alongside a major municipal client. Like every organization with a vendor footprint that touched the affected products, they had to verify, contain, and respond—at scale, under pressure, with the news cycle moving faster than the technical investigation. The lesson from that period is the lesson from every supply chain event since: by the time you're reading the headline, the question isn't *whether* you have exposure. It's whether you're already looking for it.

That's the posture we bring to the environments we support today. We assume the next compromise is in transit. We watch for the indicators that matter—unexpected outbound connections to code-hosting platforms, anomalous package installation activity, secrets appearing in places they shouldn't, credential usage patterns that don't match the developer's normal behavior. We pay close attention to the build pipelines, the developer endpoints, and the third-party access paths that are most often abused in these campaigns.

A campaign like the SAP compromise is a reminder of something more fundamental than any specific IOC list: **you cannot detect what you cannot recognize as abnormal.** Almost no defender had TeamPCP-specific indicators in advance—the malicious packages were published live, and the public IOCs followed disclosure, not the other way around. What separates the organizations that catch this kind of attack quickly from the ones that catch it weeks later is rarely a more exotic threat feed. It is whether they have already done the work to understand what *normal* looks like in their own environment.

That is why we put so much weight on **baselining network and endpoint activity** as a foundational control. When you know which build servers normally talk to which package registries, which developer machines normally push to which GitHub orgs, which cloud accounts normally call which APIs, and what the day-to-day rhythm of those flows actually looks like, you have something no IOC feed will ever give you: the ability to notice when something deviates. A new outbound connection from a build host to a freshly created GitHub repository under a developer's own account isn't suspicious in the abstract—it becomes suspicious because it doesn't match the baseline.

The threat is real, it's current, and it's growing. The work isn't to promise it will never reach you. The work is to know your environment well enough to see it the moment it does.

---

## Questions to Ask This Week

If you're running a small or mid-market business, you don't need a Fortune 500 security budget to make meaningful progress on supply chain risk. You need to ask the right questions of the right people, and you need to start now.

**Ask your MSP or IT provider:**

- What is your patch and update verification process when a vendor pushes a new release? Do you wait, test, or auto-deploy?
- Do you maintain a Software Bill of Materials (SBOM) for the systems you manage on our behalf?
- If a tool you deploy to our environment was found to be compromised tomorrow, how quickly could you identify which of our systems are affected?
- What egress monitoring do you have in place for the systems you manage?

**Ask your software vendors:**

- Do you publish an SBOM for your product? Will you share it with us?
- What is your process for verifying the integrity of third-party libraries you ship in your software?
- How are you authenticating updates pushed to our environment? Code signing? Certificate pinning?
- What is your incident notification commitment if you discover a compromise in your supply chain?

**Ask your development team (or the team that builds your custom software):**

- Are we pinning dependency versions, or are we pulling "latest"?
- Do we have lockfiles committed and enforced in CI?
- Are we running preinstall and postinstall scripts in our build pipelines, and do we have any controls on what those scripts can do?
- Where are our developer credentials stored—on developer laptops, in environment variables, in a secrets manager?
- If a developer's machine pulled a poisoned package last week, what credentials would have been exposed, and have we rotated them?

**Ask your finance and operations teams:**

- When a vendor requests a change to payment information, banking details, or contact information, what is our verification process?
- Do we require out-of-band confirmation—a phone call to a known number—before any vendor change is processed?
- If a vendor's email account was compromised tomorrow, would our process catch a fraudulent invoice or routing change?

If any of these questions produce blank stares, you've found your starting point.

---

## Concrete Controls That Reduce Real Risk

Beyond the questions, here are the controls we recommend organizations implement or verify within the next 30 days:

- **Baseline normal network and endpoint activity—then alert on the deviations.** Before you spend another dollar on threat intelligence, make sure you have a reliable picture of what *normal* looks like. Which servers talk to which destinations on which ports. Which developer machines push to which Git providers. Which cloud accounts call which APIs and on what cadence. Which processes are normally spawned by your build runners. Once that baseline exists, the anomalous outbound connection, the unexpected GitHub repo creation, the rogue process at 3 AM all become visible. Without it, you are looking for a needle in a haystack you have never measured.
- **Pin and lock your dependencies.** Use lockfiles. Don't pull `latest`. Know exactly what versions of what packages are running in your production environment.
- **Maintain an SBOM.** For every application you build or operate, you should know what's in it. When the next compromise is announced, you should be able to answer "are we affected?" in minutes, not days.
- **Disable or sandbox install scripts where you can.** npm and other ecosystems support flags to skip preinstall and postinstall scripts. Where the workflow allows, use them.
- **Monitor egress for unexpected destinations.** The SAP attackers exfiltrated to GitHub repos under the victims' own accounts. That's hard to spot if you're not watching for it. Build detections for unusual outbound connections from developer machines and build infrastructure—especially to code-hosting platforms.
- **Rotate developer credentials proactively.** If any developer in your organization has installed a package from a compromised maintainer in the past 90 days, assume their machine-resident credentials may be exposed. Rotate GitHub tokens, npm tokens, cloud keys, and any long-lived secrets accessible from developer endpoints.
- **Move secrets out of developer machines.** Secrets managers, hardware-backed keys, and short-lived credentials dramatically reduce the blast radius when a developer machine is compromised through a poisoned package.
- **Require out-of-band verification for vendor changes.** Banking changes, contact changes, configuration changes pushed by a vendor—none of these should be processed solely on the basis of an inbound email or message.
- **Inventory third-party access to your environment.** Every MSP, every consultant, every SaaS integration with API access. Know what they can reach. Reduce standing access. Move to just-in-time access where possible.

---

## What Secure Roots Is Doing

We're actively monitoring our clients' environments for the indicators of compromise associated with the SAP npm campaign and the broader TeamPCP activity. That includes watching for anomalous GitHub egress, monitoring for the specific package versions involved, scanning for credentials that may have been exposed through developer endpoints, and validating that our clients' build pipelines aren't running compromised dependencies.

For organizations that aren't our clients yet—if you don't know whether your developers pulled any of the affected packages in the past two weeks, that's the first call to make this week. If you don't have egress monitoring on your build infrastructure, that's the second. If your vendor change process can be defeated by a convincing email, that's the third.

The supply chain isn't somewhere out there. It's already inside your environment. The only question is whether you're watching it as carefully as the attackers are.

**[Contact Secure Roots →](/contact/)**
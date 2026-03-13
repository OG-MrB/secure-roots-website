---
layout: post
title: "The Cavalry Isn't Coming: Your Wartime Cybersecurity Checklist"
date: 2026-03-12 10:00:00 -0700
categories: [Cybercrime & Threat Awareness]
image: /img/wartime_cyber_checklist.png
description: "With Iran-aligned cyber operations escalating and CISA operating at a fraction of its capacity, American businesses are largely on their own. Here's what your organization needs to do this week—not this quarter."
publish_social: true
---

You've seen the headlines. Iran-aligned hackers are retaliating after Operation Epic Fury. Dozens of hacktivist groups have mobilized. U.S. defense contractors, hospitals, financial institutions, and critical infrastructure operators are in the crosshairs.

But here's the part most articles won't tell you: the agency built to help you through exactly this kind of moment is operating with one arm tied behind its back.

---

## The Safety Net Has a Hole in It

CISA—the Cybersecurity and Infrastructure Security Agency—is the federal government's front door for cybersecurity guidance, threat intelligence sharing, and incident response coordination. When a nation-state adversary turns its attention to American businesses, CISA is supposed to be the agency that sounds the alarm, shares indicators of compromise, and helps organizations harden their defenses.

Right now, CISA has lost roughly a third of its workforce. Budget proposals have targeted nearly $500 million in cuts. The counter-ransomware initiative has been impacted. Stakeholder engagement and industry partnership programs have been slashed. The agency's temporary director was reassigned to another division of DHS. Cybersecurity assessments and trainings have been paused.

This isn't a political statement. It's a situational reality that changes your risk calculus.

When the federal cybersecurity agency is stretched thin during an active conflict with a capable cyber adversary, the practical implication for your organization is simple: **you need to act as if no one is coming to help.** Because right now, at the speed these threats move, they probably aren't.

---

## What You're Actually Up Against

Iranian cyber operations aren't what most people picture. These aren't lone hackers in basements. These are structured programs run by intelligence services, military units, and organized proxy groups—and they've been building capability for over a decade.

Since Operation Epic Fury launched on February 28, an "Electronic Operations Room" has coordinated activity across dozens of pro-Iran hacktivist groups. The tactics range from website defacements and DDoS attacks to credential harvesting, data theft, and hack-and-leak campaigns designed to create fear and operational disruption.

But here's what matters for your planning: **the most dangerous Iranian cyber actors don't announce themselves.** While hacktivist groups are claiming DDoS attacks on social media, state-sponsored groups like APT34 (OilRig) and APT42 are quietly probing networks, exploiting known VPN vulnerabilities, and using stolen credentials to move laterally through systems. Their objectives aren't vandalism—they're access, persistence, and the ability to cause damage on command.

The sectors facing the highest direct targeting risk include defense, government contractors, financial services, energy, healthcare, and any organization with ties to Israel. But if you think your company is too small or too unrelated to be a target, consider this: Iranian actors have historically targeted supply chains to reach their actual objectives. Your company might not be the target—but your access to a target's network might be.

---

## Your Wartime Checklist: What to Do This Week

This isn't a strategic roadmap. This is a list of things your team should verify or implement within the next seven days. None of these require new budget. All of them reduce your exposure to the specific tactics Iranian-aligned actors are known to use.

### Patch These First

Iranian cyber actors have repeatedly exploited a specific set of vulnerabilities. If you have any of the following in your environment, patch them now—not next maintenance window, now:

- **VPN appliances**: Pulse Secure/Ivanti, Fortinet FortiOS, Citrix NetScaler, and F5 BIG-IP have all been exploited in documented Iranian campaigns. If you're running any of these and haven't applied the latest security updates, you have an open door.
- **Microsoft Exchange**: ProxyShell and ProxyLogon vulnerabilities remain some of the most exploited entry points for Iranian actors.
- **Log4j**: Still being exploited. Still unpatched in many environments.

If you don't know whether these exist in your environment, that's the first problem to solve.

### Lock Down Remote Access

- Enforce multi-factor authentication on every remote access point. Not just VPN—RDP, cloud admin portals, email, everything. Iranian actors exploit default and stolen credentials as a primary tactic (MITRE T1078, T1110). MFA is the single most effective control against this.
- Audit all active VPN accounts. Disable any that aren't currently needed. Reduce the attack surface.
- If you're still using single-factor authentication on anything externally facing, fix it today.

### Review Your Vendor and Supply Chain Access

- Identify every third party with remote access to your network. MSPs, software vendors, IT consultants—anyone with credentials or a tunnel into your environment.
- Verify that their access is scoped to the minimum necessary. Remove standing access where possible and move to just-in-time access models.
- Ask your critical vendors directly: have they reviewed their own exposure to these threats? If they can't answer that question, you have a supply chain risk.

### Monitor for the Right Things

- Alert on the use of unauthorized remote access tools: AnyDesk, TeamViewer, ngrok, and similar. Iranian actors and their proxies use legitimate tools to maintain access and avoid detection.
- Watch for brute force activity against externally facing services, especially outside business hours.
- Monitor for new or unexpected administrative accounts. If a new Domain Admin appears that nobody created, you may already be compromised.
- Review DNS logs for connections to known Iranian infrastructure. Threat intelligence feeds from vendors like Palo Alto Unit 42, Mandiant, and CrowdStrike are publishing updated indicators of compromise specific to this conflict.

### Prepare for the Worst

- Test your backups. Not "verify they exist"—actually restore something. Iranian-aligned actors have deployed wiper malware in past conflicts. If your backups aren't offline, immutable, and tested, they may not survive an attack.
- Dust off your incident response plan. Does your team know who to call at 2 AM on a Saturday? Do you have retainers in place with an IR firm? Do you have a communication plan for customers and partners if you get hit?
- Run a 30-minute tabletop exercise with your leadership team. Scenario: it's Monday morning, your systems are down, your data is being leaked on Telegram, and a hacktivist group is claiming credit. What do you do first? If no one has an answer, you have work to do.

### Brief Your People

- Send a company-wide advisory reminding employees to be vigilant about phishing, especially emails referencing the conflict, military news, or government communications. Iranian actors have used current events as lures in spearphishing campaigns for years.
- Remind your finance team to verify any unusual wire transfer or vendor change requests through a secondary channel. Voice calls to known numbers—not replies to the email that made the request.
- If you have employees with ties to the defense sector, government contracting, or Israeli business partnerships, they should be considered higher-risk targets for social engineering.

---

## A Note on Threat Intelligence

If your organization subscribes to a threat intelligence platform, now is the time to use it. Palo Alto's Unit 42, SentinelOne, SOCRadar, Check Point, and Mandiant have all published detailed threat briefs specific to the current Iranian cyber escalation, including indicators of compromise, targeted sectors, and observed TTPs.

If you don't have a threat intelligence subscription, CISA's Iran threat overview page still provides foundational guidance and published advisories. Even with reduced capacity, the advisories that are published remain valuable.

---

## The Real Risk Isn't the Attack—It's the Assumption

The most dangerous assumption any organization can make right now is that this doesn't apply to them. That they're too small. Too unrelated. Too far from the conflict.

Iranian cyber strategy doesn't require every target to be strategic. Disruption at scale—hitting hospitals, banks, manufacturers, service providers—creates fear, erodes confidence, and amplifies the political message. You don't have to be a defense contractor to be useful to that objective.

The organizations that come through this period intact won't be the ones with the biggest security budgets. They'll be the ones that took a hard look at their fundamentals this week—patching, MFA, backups, access controls—and made sure the basics were solid.

You don't need a nation-state defense budget. You need to not be the easy target.

---

## What Secure Roots Is Doing Right Now

We're actively working with our clients to conduct rapid risk assessments focused on Iranian threat actor TTPs. This includes vulnerability scanning against known exploited CVEs, MFA gap analysis, backup validation, and abbreviated tabletop exercises designed to test incident response readiness in under an hour.

If your organization needs help getting through this checklist—or if you want a professional assessment of your current exposure—we're here.

**[Contact Secure Roots →](/contact/)**

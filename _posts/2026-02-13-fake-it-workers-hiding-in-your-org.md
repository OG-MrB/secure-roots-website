---
layout: post
title: "The Employee Who Doesn't Exist: How Fake IT Workers Are Infiltrating Organizations—and How to Stop Them"
date: 2026-02-13 10:00:00 -0700
categories: [Cybercrime & Threat Awareness]
image: /img/fake_it_worker_2.png
description: "North Korean operatives are getting hired as remote IT workers at companies worldwide. Learn how to detect fake employees in your organization using real-world detection strategies from the field."
---

They pass the interview. They clear the background check. They show up on Slack, push code to GitHub, and collect a paycheck every two weeks. But the person behind the screen isn't who they claim to be—and the salary you're paying is funding a foreign government's weapons program.

This isn't a movie plot. It's happening right now, at companies of every size, across every industry.

---

## The Threat Is Real—and It's Growing

North Korean operatives, directed by the DPRK regime, are fraudulently obtaining remote IT positions at companies worldwide. They use stolen identities, AI-generated resumes, deepfake video, and U.S.-based accomplices who host "laptop farms"—residences where dozens of company-issued devices sit, remotely controlled by workers operating from China, Russia, and elsewhere.

The numbers are staggering. According to the U.S. Department of Justice, coordinated enforcement actions in 2025 revealed schemes impacting more than 136 U.S. companies and generating millions in illicit revenue funneled directly to North Korea's weapons programs. The FBI has established dedicated victim notification and information portals for affected companies. An Arizona woman was sentenced to over eight years in prison for running a laptop farm that serviced more than 300 companies and generated over $17 million for the regime. In a separate case, five individuals pleaded guilty to enabling North Korean IT worker fraud, with one defendant alone placing workers at 64 U.S. companies through a single front company.

And these are just the cases we know about.

In a January 2026 episode of the SANS Institute podcast *Blueprint: Build the Best in Cyber Defense*, cybersecurity investigator Zak Stufflebeam shared a detailed case study of uncovering multiple counterfeit IT employees within a single organization. His investigation revealed a pattern of suspicious indicators—from AI-generated resumes and rehearsed interview responses to unusual VPN activity and unauthorized access requests. The full talk, *"Infiltration Alert! How to Catch Fake IT Employees in Your Network"*, is essential viewing for anyone responsible for hiring or network security.

---

## What We've Seen in the Field

At Secure Roots, this isn't a theoretical concern—we've encountered these patterns firsthand at organizations we support.

One of the most effective detection strategies we've implemented involves monitoring for unauthorized remote access tools. We set up detections that alert on the use of tools like AnyDesk, TeamViewer, Google Meet screen sharing, and similar remote desktop software. When those alerts fire, we investigate. What we've found, more than once, is employees sharing their screens—or full remote access to their machines—with individuals who have no authorization to access company systems.

Sometimes it's a well-meaning employee getting help from a friend. But sometimes it's something else entirely: a hired "employee" who can't actually do the work, relying on an outside party to perform their job duties while they collect the paycheck. That outside party could be anyone, anywhere in the world.

This is one of the core tactics in the DPRK IT worker playbook, and it's why monitoring for remote access tool usage isn't optional—it's a frontline defense.

---

## Red Flags Every Organization Should Watch For

Whether you're a small business with ten employees or an enterprise with ten thousand, these warning signs apply. Based on FBI advisories, Stufflebeam's investigation, and our own field experience, here's what to look for.

**During Hiring:**

Inconsistencies between a candidate's resume, LinkedIn profile, and interview performance are a major indicator. AI-generated resumes are increasingly polished, but the person behind them may struggle with basic technical questions when asked to go off-script. Watch for candidates who refuse to turn on their camera, request that company laptops be shipped to addresses that don't match their stated location, or insist on communicating through non-company platforms.

**After Onboarding:**

Monitor for remote desktop and screen-sharing tools being installed or used outside of approved channels. Track VPN connections from unusual geolocations—especially connections that seem inconsistent with the employee's stated residence. Watch for access patterns that don't match normal working hours, or multiple audio/video sessions running concurrently on a single endpoint. Pay attention to employees who request access to code repositories, cloud storage, or sensitive systems beyond what their role requires.

**Financial Indicators:**

Requests for payment through non-standard channels, digital payment services linked to foreign accounts, or reluctance to provide standard tax documentation are all warning signs the FBI has highlighted in its advisories.

---

## What You Can Do Right Now

You don't need a massive security budget to start defending against this threat. Here are practical steps you can implement today.

**1. Verify identity at every stage.** Don't just check a box during onboarding. Require live video verification during interviews—ask candidates to hold up their ID on camera. Use E-Verify for employment eligibility. Re-verify identity periodically, not just at hire.

**2. Monitor remote access tools.** Build detections for AnyDesk, TeamViewer, Chrome Remote Desktop, and similar tools. Alert on their installation or usage, and investigate every alert. If an employee is sharing screen access with someone outside the organization, you need to know about it.

**3. Cross-reference applicant data.** Check your HR systems for duplicate resume content, reused phone numbers, or overlapping email addresses across different applicants. North Korean operatives often recycle identity components across multiple applications.

**4. Restrict laptop shipping.** Require that company devices are shipped only to verified addresses that match the employee's confirmed identity. Better yet, require in-person pickup or use an identity verification service at the delivery point.

**5. Enforce least privilege.** Limit access to what each role actually requires. Monitor for access requests that go beyond scope, especially to source code repositories, cloud accounts, and sensitive internal systems. As the FBI noted, North Korean workers have been caught copying company code repos to personal accounts and cloud storage for exfiltration—and later using that stolen data to extort their employers.

**6. Train your hiring teams.** HR staff, hiring managers, and technical interviewers need to know this threat exists. Share the FBI's advisories. Watch Stufflebeam's SANS talk as a team. Make it part of your security culture, not just your SOC's problem.

---

## This Isn't Just a Big-Company Problem

Small and midsize businesses are targets too—often easier ones. Smaller organizations typically have fewer identity verification controls, less network monitoring, and leaner HR teams that may not catch the inconsistencies. If you have remote workers and you're not actively verifying who's behind the keyboard, you have a gap.

The FBI's IC3 has published multiple public service announcements specifically addressing this threat and encouraging all organizations to report suspicious activity. If you suspect a fraudulent worker, report it at ic3.gov.

---

## Conclusion

The fake IT worker threat is one of the most underestimated risks in cybersecurity today. It exploits the trust we place in our own hiring processes—and it funds some of the most dangerous programs on the planet.

But it's also a threat you can detect and defend against with the right awareness, the right monitoring, and the right culture. Start with identity verification. Build your remote access detections. Train your people. And don't assume it can't happen to you—because the adversary is already counting on that assumption.

---

**References & Resources:**

- Zak Stufflebeam, *"Infiltration Alert! How to Catch Fake IT Employees in Your Network"*, SANS Institute Blueprint Podcast, January 5, 2026. [Watch on YouTube](https://www.youtube.com/watch?v=U0MjVKlYL7M)
- FBI Internet Crime Complaint Center, *"North Korean IT Workers Conducting Data Extortion"*, January 2025. [Read the PSA](https://www.ic3.gov/PSA/2025/PSA250123)
- U.S. Department of Justice, *"Justice Department Announces Coordinated, Nationwide Actions to Combat North Korean Remote IT Workers"*, July 2025. [Read the announcement](https://www.justice.gov/opa/pr/justice-department-announces-coordinated-nationwide-actions-combat-north-korean-remote)
- FBI Cyber Division, *"DPRK IT Workers"* advisory page. [View on FBI.gov](https://www.fbi.gov/wanted/cyber/dprk-it-workers)

*If your organization needs help building detections for unauthorized remote access tools or strengthening your hiring verification process, [contact Secure Roots](/contact/). We've been in the trenches on this one.*

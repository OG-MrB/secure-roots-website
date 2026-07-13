# MailerLite setup, the one part I can't do for you

I can't create accounts on your behalf (that requires your own login/password), so this is the one manual step. Everything else (landing pages, lead magnets, forms, CSP) is already built and live-ready.

## 1. Create the account (5 min)

1. Go to https://www.mailerlite.com and sign up with **info@secureroots.io**.
2. Free plan covers 1,000 subscribers / 12,000 emails per month, which is well past where we are today.
3. Verify your email when prompted.

## 2. Connect secureroots.io as a verified sending domain (15 min)

1. In MailerLite: Settings > Domains > Add domain > `secureroots.io`.
2. MailerLite will give you 3-4 DNS records (SPF, DKIM, sometimes a tracking CNAME).
3. Add those records at wherever secureroots.io's DNS is managed (likely the same place CNAME for GitHub Pages is set). If you're not sure where that is, check the domain registrar you used to buy secureroots.io.
4. DNS propagation takes 15 min to a few hours. MailerLite will show "Verified" once it's done.

**Do this even if you plan to keep sending cold outreach from Gmail.** This step is only for the opt-in list, it doesn't touch your Gmail sending at all.

## 3. Create one group and one form (10 min)

1. Subscribers > Groups > New group. Name it "Website Leads."
2. Forms > Embedded forms > Create a new embedded form.
   - Name: "Lead Magnet Signup"
   - Fields: Email (required). Optionally add a hidden field or custom field called `source` if you want MailerLite itself to store which page they came from (the current form already POSTs `source` to me via FormSubmit, so this is optional polish, not required to launch).
   - Assign to the "Website Leads" group.
   - Enable **double opt-in** (this is the default and the correct setting, do not turn it off).
3. Click Embed > copy the HTML/JS embed code.

## 4. Give me the embed code

Paste the embed snippet back to me (or drop it in a file at `secure-roots-website/_includes/mailerlite-embed.html`) and I'll swap it into `_includes/lead-magnet-form.html` in place of the current FormSubmit fallback, across all four landing pages and the footer, in one pass.

## 5. Set up the welcome automation (10 min, once the form is connected)

1. Automations > New automation > Trigger: "Subscriber joins a group" > Website Leads.
2. Step 1: Send the matching lead magnet PDF immediately (attach a link to the PDF, hosted at `secureroots.io/downloads/` once I convert the checklists, or a Google Drive link in the meantime).
3. Step 2 (Day 3): short value-add email.
4. Step 3 (Day 7): case study or social proof.
5. Step 4 (Day 14): soft CTA to book the free 30-minute risk review.

Copy for all four steps, per vertical, is in `WELCOME_SEQUENCES.md` in this same folder. Paste directly into MailerLite's automation editor.

## What's already done and doesn't need you

- Four landing pages live: `/hipaa/`, `/law-firms/`, `/cmmc/`, `/nonprofits/`
- A new "Mission Shield" service section on `/services/`
- Lead magnets: HIPAA checklist, lawyer confidentiality checklist (existing), new CMMC checklist, nonprofit Cyber Health Check offer
- CSP updated to allow MailerLite's script/form domains once you're ready to swap the embed in
- Every form already includes a source tag so leads are traceable by vertical even before MailerLite groups exist
- CAN-SPAM opt-out language on the lead-magnet forms

## Current state (works today, before you touch MailerLite)

The forms currently submit via FormSubmit to `info@secureroots.io`, so **nothing is broken while you set up MailerLite**. You'll get an email per signup with the source tag until the MailerLite embed replaces it.

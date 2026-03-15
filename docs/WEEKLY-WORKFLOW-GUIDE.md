# 📋 Weekly Newsletter — Step-by-Step Workflow Guide

This is your complete weekly playbook. Follow these steps each week to produce and publish your newsletter.

---

## 🔧 One-Time Setup (Do This First)

### Step 1: Generate Hashnode API Token
1. Go to → https://hashnode.com/settings/developer
2. Click **"Generate New Token"** → name it `newsletter-cicd`
3. **Copy the token** — save it somewhere safe (you won't see it again)

### Step 2: Find Your Hashnode Publication ID
1. Open PowerShell and run:
```powershell
$token = "PASTE_YOUR_TOKEN_HERE"
$body = @{ query = '{ me { publications(first:5) { edges { node { id title url } } } } }' } | ConvertTo-Json
$response = Invoke-RestMethod -Uri "https://gql.hashnode.com" -Method POST -Body $body -ContentType "application/json" -Headers @{ Authorization = $token }
$response.data.me.publications.edges | ForEach-Object { $_.node } | Format-Table id, title, url
```
2. Copy the `id` value next to `kaustubhtech.hashnode.dev`

### Step 3: Add Secrets to GitHub
1. Go to → https://github.com/kaustubh93-dev/weekly-newsletter/settings/secrets/actions
2. Click **"New repository secret"** → add:
   - Name: `HASHNODE_TOKEN` → Value: your token from Step 1
   - Name: `HASHNODE_PUBLICATION_ID` → Value: your publication ID from Step 2

✅ **One-time setup done! You won't need to do this again.**

---

## 📰 Weekly Workflow (Every Week)

### 🗓️ Monday/Tuesday — Pick Topic & Research

**What you do:** Choose this week's topic and gather materials.

Topic ideas (rotate through these):
- 🔧 Tips & Tricks for Windows Server
- 💻 Handy PowerShell Scripts
- 📚 Learning Resources & Tools
- 📢 Updates & Announcements
- 🔍 Case Studies & Incident Reviews

Gather your research materials:
- Microsoft Learn docs, KB articles
- PDFs, Word docs, screenshots
- Links to relevant resources
- Your own notes & experiences

---

### 🗓️ Tuesday/Wednesday — Create Edition & Draft Content

**Step 1: Open terminal in your repo folder**
```powershell
cd D:\Personal\Vs-dev-codebase\icici-weekly-newsletter
```

**Step 2: Create a new edition folder**
```powershell
python scripts/new_edition.py --week 2026-W13 --title "Your Topic Title Here"
```
This creates:
```
editions/2026-W13/
├── metadata.yml     ← Edit tags & category
├── content.md       ← Your research goes here
├── assets/          ← Drop images here
└── output/          ← AI-generated outputs go here
```

**Step 3: Add your research to `content.md`**
- Open `editions/2026-W13/content.md` in VS Code
- Paste your research notes, key points, links, reference text
- Drop any screenshots/diagrams into `editions/2026-W13/assets/`

**Step 4: Update `metadata.yml`**
- Verify title and subtitle
- Add relevant tags (e.g., `active-directory`, `hyper-v`, `performance`)
- Set the right category

---

### 🗓️ Wednesday/Thursday — Generate 3 Outputs with Claude AI

You'll use Claude AI 3 times to generate 3 different outputs from your content.

#### Output 1: HTML Email Newsletter

**Open Claude and paste this:**
```
I have newsletter content that I need formatted as an HTML email.

Here are my formatting instructions:
[Paste the contents of prompts/email-format-prompt.md]

Here is my email template:
[Paste the contents of templates/email-base.html]

Here is my content:
[Paste the contents of editions/2026-W13/content.md]

Here is my metadata:
[Paste the contents of editions/2026-W13/metadata.yml]

Please generate the complete HTML email newsletter.
```

→ **Save Claude's output as:** `editions/2026-W13/output/newsletter.html`

#### Output 2: Hashnode Blog Post

**Open Claude and paste this:**
```
I need this content formatted as a Hashnode blog post in Markdown.

Here are my formatting instructions:
[Paste the contents of prompts/blog-format-prompt.md]

Here is my content:
[Paste the contents of editions/2026-W13/content.md]

Here is my metadata:
[Paste the contents of editions/2026-W13/metadata.yml]

Please generate the complete Hashnode blog post with frontmatter.
```

→ **Save Claude's output as:** `editions/2026-W13/output/blog-post.md`

#### Output 3: LinkedIn Post

**Open Claude and paste this:**
```
I need a LinkedIn post promoting this blog article.

Here are my formatting instructions:
[Paste the contents of prompts/linkedin-format-prompt.md]

Here is my content summary:
[Paste the key points from content.md or blog-post.md]

My Hashnode blog URL will be: https://kaustubhtech.hashnode.dev/[slug-from-metadata]

Please generate the LinkedIn post.
```

→ **Save Claude's output as:** `editions/2026-W13/output/linkedin-post.txt`

---

### 🗓️ Thursday — Review & Preview

**Step 1: Preview the HTML email in your browser**
```powershell
start editions\2026-W13\output\newsletter.html
```
- Check formatting, tables, code blocks
- Verify all links work
- Make sure it looks good on a narrow window (simulates mobile)

**Step 2: Preview the blog post**
- Open `blog-post.md` in VS Code with Markdown preview (Ctrl+Shift+V)
- Check headings, code blocks, Mermaid diagrams
- Verify frontmatter is correct

**Step 3: Check the LinkedIn post**
- Open `linkedin-post.txt`
- Verify it's under 1300 characters
- Check hashtags are relevant

**Step 4: Run the validator**
```powershell
python scripts/validate_outputs.py --edition editions/2026-W13
```
- Fix any ❌ errors before proceeding
- ⚠️ warnings are advisory — review but not blocking

---

### 🗓️ Thursday/Friday — Publish Everything

#### A. Push to GitHub (triggers CI/CD)

```powershell
# Create a branch for this edition
git checkout -b edition/2026-W13

# Stage and commit
git add editions/2026-W13/
git commit -m "Add edition 2026-W13: Your Topic Title"

# Push the branch
git push origin edition/2026-W13
```

Now go to GitHub:
1. Open → https://github.com/kaustubh93-dev/weekly-newsletter/pulls
2. Click **"Compare & pull request"** for your branch
3. Review the PR — CI will automatically validate your outputs
4. **Merge the PR** to `main`

**What happens automatically after merge:**
- ✅ Blog post is published as a **draft** on Hashnode
- ✅ A GitHub Release is created with the edition tag

#### B. Send the Email (Manual)

1. Open **Outlook** → New Email
2. Open `editions/2026-W13/output/newsletter.html` in your browser
3. **Select All** (Ctrl+A) in the browser → **Copy** (Ctrl+C)
4. **Paste** (Ctrl+V) into the Outlook email body
5. Set recipients (your distribution list)
6. Set subject line: `Windows Server Weekly #N: Your Topic Title`
7. **Send** ✉️

#### C. Publish the Hashnode Blog (Manual Review)

1. Go to → https://hashnode.com/kaustubhtech/dashboard
2. Click **"Drafts"** — your article should be there
3. Review the draft — check formatting, images, links
4. Click **"Publish"** when satisfied ✅

#### D. Post on LinkedIn (Manual)

1. Open → https://www.linkedin.com
2. Click **"Start a post"**
3. Open `editions/2026-W13/output/linkedin-post.txt`
4. **Copy and paste** the text into LinkedIn
5. Replace the Hashnode URL placeholder with the actual published URL
6. **Post** 💼

---

## 📊 Quick Reference: Week at a Glance

| Day | Task | Time |
|-----|------|------|
| Mon/Tue | Pick topic, gather research | ~30 min |
| Tue/Wed | Create edition, draft content.md | ~45 min |
| Wed/Thu | Generate 3 outputs with Claude AI | ~30 min |
| Thu | Review, preview, validate | ~20 min |
| Thu/Fri | Push to GitHub, send email, publish blog, post LinkedIn | ~20 min |

**Total weekly effort: ~2.5 hours**

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Validator fails with ❌ errors | Fix the issues mentioned, re-run validator |
| CI/CD doesn't trigger | Check you merged to `main`, check GitHub Actions tab |
| Hashnode draft not appearing | Verify secrets are set correctly in GitHub Settings |
| HTML email looks broken in Outlook | Use "Paste as HTML" or paste from browser preview |
| `new_edition.py` says folder exists | You already created this week's edition — check `editions/` |

---

## 🗂️ File Cheat Sheet

| What you need | Where to find it |
|---------------|-----------------|
| Create new edition | `python scripts/new_edition.py --week YYYY-WNN --title "..."` |
| Email formatting prompt | `prompts/email-format-prompt.md` |
| Blog formatting prompt | `prompts/blog-format-prompt.md` |
| LinkedIn formatting prompt | `prompts/linkedin-format-prompt.md` |
| HTML email template | `templates/email-base.html` |
| Validate outputs | `python scripts/validate_outputs.py --edition editions/YYYY-WNN` |
| Test Hashnode publish | `python scripts/publish_hashnode.py --edition editions/YYYY-WNN --dry-run` |

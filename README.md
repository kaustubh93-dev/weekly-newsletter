# weekly-newsletter

## 🎯 What is this?

A weekly newsletter pipeline focused on **Windows Server administration** — tips, PowerShell scripts, learning resources, and incident reviews.

**One content source → Three outputs:**
| Output | Destination | How |
|--------|------------|-----|
| 📧 HTML Email | Outlook | Manual copy-paste |
| 📝 Blog Post | [kaustubhtech.hashnode.dev](https://kaustubhtech.hashnode.dev/) | Auto-draft via CI/CD, manual publish |
| 💼 LinkedIn Post | LinkedIn | Manual post from generated text |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git
- [Hashnode Personal Access Token](https://hashnode.com/settings/developer)

### Setup
```bash
# Clone the repo
git clone https://github.com/<your-username>/weekly-newsletter.git
cd weekly-newsletter

# Install Python dependencies
pip install -r scripts/requirements.txt
```

### Configure Secrets (GitHub)
Go to **Settings → Secrets and variables → Actions** and add:
| Secret | Value |
|--------|-------|
| `HASHNODE_TOKEN` | Your Hashnode PAT |
| `HASHNODE_PUBLICATION_ID` | Your publication ID (see below) |

**Finding your Hashnode Publication ID:**
1. Go to your Hashnode dashboard
2. Open browser DevTools → Network tab
3. Look for GraphQL requests — the `publicationId` field contains your ID

---

## 📋 Weekly Workflow

### 1️⃣ Create a New Edition
```bash
python scripts/new_edition.py --week 2026-W12 --title "Mastering Windows Event Logs"
```
This creates:
```
editions/2026-W12/
├── metadata.yml        # Edit: title, tags, category
├── content.md          # Your main content goes here
├── assets/             # Drop images, diagrams here
└── output/
    ├── newsletter.html # Generated HTML email
    ├── blog-post.md    # Generated Hashnode blog
    └── linkedin-post.txt # Generated LinkedIn text
```

### 2️⃣ Research & Draft Content
- Gather your research materials (docs, PDFs, links, screenshots)
- Use Claude AI with the prompts in `prompts/` to draft `content.md`
- Drop images into `assets/`

### 3️⃣ Generate All 3 Outputs
Use Claude AI with the formatting prompts:
1. **Email**: Feed `content.md` + `prompts/email-format-prompt.md` → save as `output/newsletter.html`
2. **Blog**: Feed `content.md` + `prompts/blog-format-prompt.md` → save as `output/blog-post.md`
3. **LinkedIn**: Feed `content.md` + `prompts/linkedin-format-prompt.md` → save as `output/linkedin-post.txt`

### 4️⃣ Review & Push
```bash
# Preview the email in browser
start output/newsletter.html

# Commit and push
git checkout -b edition/2026-W12
git add editions/2026-W12/
git commit -m "Add edition 2026-W12: Mastering Windows Event Logs"
git push origin edition/2026-W12
```

### 5️⃣ Open PR & Merge
- Open a PR to `main`
- CI validates HTML, markdown, and metadata
- Merge the PR

### 6️⃣ CI/CD Does the Rest
- ✅ Hashnode draft is auto-created
- ✅ GitHub Release is tagged
- 📧 Copy `newsletter.html` into Outlook and send
- 💼 Copy `linkedin-post.txt` and post on LinkedIn
- 📝 Go to Hashnode dashboard, review draft, hit Publish

---

## 📁 Project Structure

```
weekly-newsletter/
├── .github/workflows/          # CI/CD pipelines
│   ├── publish-newsletter.yml  # Post-merge: Hashnode draft + Release
│   └── validate-pr.yml         # PR checks: validate outputs
├── templates/                  # Reusable HTML/MD templates
├── prompts/                    # Claude AI formatting prompts
├── scripts/                    # Python automation scripts
├── editions/                   # Weekly newsletter editions
│   └── YYYY-WNN/              # One folder per week
├── archive/                    # Legacy newsletters (pre-automation)
├── README.md
└── CHANGELOG.md
```

---

## 📰 Newsletter Topics Coverage

Each weekly edition covers one or more of:
- 🔧 **Tips & Tricks** for Windows Server
- 💻 **Handy PowerShell Scripts**
- 📚 **Learning Resources & Tools**
- 📢 **Updates & Announcements**
- 🔍 **Case Studies & Incident Reviews**

---

## 🏷️ Edition Archive

| Week | Title | Email | Blog | LinkedIn |
|------|-------|-------|------|----------|
| *Editions will be listed here as they are published* |

---

## 📄 License

This project is for internal use. Newsletter content is © Microsoft / Kaustubh.

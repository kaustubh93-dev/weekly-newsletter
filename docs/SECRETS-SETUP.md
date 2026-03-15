# 🔐 Secrets & Configuration Setup Guide

## Step 1: Generate Hashnode Personal Access Token (PAT)

1. Go to [hashnode.com/settings/developer](https://hashnode.com/settings/developer)
2. Click **"Generate New Token"**
3. Give it a name like `newsletter-cicd`
4. Copy the token immediately — it won't be shown again!
5. Save it somewhere secure (password manager)

## Step 2: Find Your Hashnode Publication ID

### Option A: Via Hashnode Dashboard
1. Go to your blog dashboard: [hashnode.com/kaustubhtech/dashboard](https://hashnode.com/kaustubhtech/dashboard)
2. Click **Settings** → **General**
3. The Publication ID is displayed at the bottom of the page

### Option B: Via API Query
Run this in your terminal (replace `YOUR_TOKEN`):

```bash
curl -s -X POST https://gql.hashnode.com \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_TOKEN" \
  -d '{"query":"{ me { publications(first:5) { edges { node { id title url } } } } }"}' | python -m json.tool
```

Look for the `id` field next to your blog URL.

### Option C: Via PowerShell
```powershell
$token = "YOUR_TOKEN"
$body = @{ query = '{ me { publications(first:5) { edges { node { id title url } } } } }' } | ConvertTo-Json
$response = Invoke-RestMethod -Uri "https://gql.hashnode.com" -Method POST -Body $body -ContentType "application/json" -Headers @{ Authorization = $token }
$response.data.me.publications.edges | ForEach-Object { $_.node } | Format-Table id, title, url
```

## Step 3: Add Secrets to GitHub Repository

1. Go to your repo on GitHub: `https://github.com/<username>/icici-weekly-newsletter`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add:

| Secret Name | Value |
|-------------|-------|
| `HASHNODE_TOKEN` | Your PAT from Step 1 |
| `HASHNODE_PUBLICATION_ID` | Your Publication ID from Step 2 |

## Step 4: Verify Setup (Local Test)

Test locally before relying on CI/CD:

```powershell
# Set environment variables temporarily
$env:HASHNODE_TOKEN = "your-token-here"
$env:HASHNODE_PUBLICATION_ID = "your-publication-id-here"

# Dry run (no actual publishing)
python scripts/publish_hashnode.py --edition editions/2026-W12 --dry-run

# Real test (creates a draft on Hashnode)
python scripts/publish_hashnode.py --edition editions/2026-W12
```

After the real test, go to your Hashnode dashboard → Drafts to verify the post appeared.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` | Token is invalid or expired — regenerate it |
| `Publication not found` | Wrong Publication ID — re-check with the API query |
| `Rate limited` | Wait a few minutes and retry (rare with weekly cadence) |
| `CI/CD not triggering` | Check that secrets are set at repo level, not org level |

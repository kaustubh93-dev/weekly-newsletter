#!/usr/bin/env python3
"""
new_edition.py — Scaffold a new weekly newsletter edition folder.

Usage:
    python scripts/new_edition.py --week 2026-W12 --title "Mastering Windows Event Logs"
    python scripts/new_edition.py --week 2026-W12 --title "Mastering Windows Event Logs" --category "Tips & Tricks"
"""

import argparse
import os
import re
import sys
from datetime import datetime


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def create_edition(week: str, title: str, subtitle: str = "", category: str = "Tips & Tricks"):
    """Create a new edition folder with scaffolded files."""

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    edition_path = os.path.join(repo_root, "editions", week)

    if os.path.exists(edition_path):
        print(f"❌ Edition folder already exists: {edition_path}")
        sys.exit(1)

    # Create directories
    os.makedirs(os.path.join(edition_path, "assets"), exist_ok=True)
    os.makedirs(os.path.join(edition_path, "output"), exist_ok=True)

    # Calculate edition number from existing editions
    editions_dir = os.path.join(repo_root, "editions")
    existing = [d for d in os.listdir(editions_dir) if os.path.isdir(os.path.join(editions_dir, d)) and d != week]
    edition_number = len(existing) + 1

    if not subtitle:
        subtitle = f"Weekly Windows Server Digest — Edition #{edition_number}"

    slug = slugify(title)
    today = datetime.now().strftime("%Y-%m-%d")

    # Create metadata.yml
    metadata_content = f"""# Edition Metadata
title: "{title}"
subtitle: "{subtitle}"
slug: "{slug}"
edition_number: {edition_number}
week: "{week}"
date: "{today}"
category: "{category}"
series: "Windows Server Weekly"
tags:
  - windows-server
  - powershell
  - sysadmin
# Add more tags relevant to this edition's topic:
#  - active-directory
#  - hyper-v
#  - failover-clustering
#  - performance
#  - security

# Cover image for Hashnode (optional - use hosted URL)
cover_image: ""

# Author info
author: "Kaustubh"
"""
    with open(os.path.join(edition_path, "metadata.yml"), "w", encoding="utf-8") as f:
        f.write(metadata_content)

    # Create content.md
    content_md = f"""# {title}

> Edition #{edition_number} | {week} | {today}

## Research Notes & Source Materials

<!-- Drop your research here: paste from docs, PDFs, links, notes -->
<!-- Claude AI will use this to generate the 3 outputs -->



---

## Key Points to Cover

- 
- 
- 

---

## PowerShell Script Idea

```powershell
# Script idea for this edition
```

---

## References & Links

- 
- 

---

## Images / Screenshots

<!-- List images dropped into the assets/ folder -->
<!-- e.g., ![diagram](assets/architecture-diagram.png) -->

"""
    with open(os.path.join(edition_path, "content.md"), "w", encoding="utf-8") as f:
        f.write(content_md)

    # Create placeholder output files
    output_files = {
        "output/newsletter.html": "<!-- Generate this using: prompts/email-format-prompt.md + content.md -->\n",
        "output/blog-post.md": "<!-- Generate this using: prompts/blog-format-prompt.md + content.md -->\n",
        "output/linkedin-post.txt": "# Generate this using: prompts/linkedin-format-prompt.md + content.md\n",
    }
    for filepath, placeholder in output_files.items():
        with open(os.path.join(edition_path, filepath), "w", encoding="utf-8") as f:
            f.write(placeholder)

    # Create .gitkeep for assets
    with open(os.path.join(edition_path, "assets", ".gitkeep"), "w") as f:
        pass

    print(f"✅ Edition created: {edition_path}")
    print(f"   📁 metadata.yml   — Edit title, tags, category")
    print(f"   📝 content.md     — Add your research & content here")
    print(f"   🖼️  assets/        — Drop images here")
    print(f"   📤 output/        — Generated outputs go here")
    print(f"\n📋 Next steps:")
    print(f"   1. Add research materials to content.md")
    print(f"   2. Drop images into assets/")
    print(f"   3. Use Claude AI with prompts/ to generate outputs")
    print(f"   4. Review outputs, commit, and push!")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new weekly newsletter edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/new_edition.py --week 2026-W12 --title "Mastering Windows Event Logs"
  python scripts/new_edition.py --week 2026-W12 --title "Pagefile Deep Dive" --category "Case Study"
        """
    )
    parser.add_argument("--week", required=True, help="Week identifier (e.g., 2026-W12)")
    parser.add_argument("--title", required=True, help="Newsletter title")
    parser.add_argument("--subtitle", default="", help="Newsletter subtitle (auto-generated if empty)")
    parser.add_argument("--category", default="Tips & Tricks",
                        choices=["Tips & Tricks", "PowerShell Scripts", "Learning Resources",
                                 "Updates & Announcements", "Case Study", "Incident Review"],
                        help="Content category")

    args = parser.parse_args()

    # Validate week format
    if not re.match(r'^\d{4}-W\d{2}$', args.week):
        print(f"❌ Invalid week format: {args.week}. Expected format: YYYY-WNN (e.g., 2026-W12)")
        sys.exit(1)

    create_edition(args.week, args.title, args.subtitle, args.category)


if __name__ == "__main__":
    main()

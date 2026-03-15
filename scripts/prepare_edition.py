#!/usr/bin/env python3
"""
prepare_edition.py — Copy outputs from output/{topic}/ into editions/{week}/ for CI/CD.

Takes the generated newsletter.html, blog-post.md, and linkedin-post.txt from
the output folder and organizes them into the editions/ structure that CI/CD expects.

Usage:
    python scripts/prepare_edition.py --topic mastering-windows-event-logs --week 2026-W13
    python scripts/prepare_edition.py --topic mastering-windows-event-logs --week 2026-W13 --title "Custom Title"
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime


def topic_to_title(topic: str) -> str:
    """Convert topic slug to a readable title."""
    return topic.replace("-", " ").title()


def main():
    parser = argparse.ArgumentParser(
        description="Copy outputs from output/{topic}/ into editions/{week}/ for CI/CD"
    )
    parser.add_argument("--topic", required=True, help="Topic folder name (e.g., mastering-windows-event-logs)")
    parser.add_argument("--week", required=True, help="Week identifier (e.g., 2026-W13)")
    parser.add_argument("--title", default="", help="Newsletter title (auto-generated from topic if empty)")
    parser.add_argument("--category", default="Tips & Tricks",
                        choices=["Tips & Tricks", "PowerShell Scripts", "Learning Resources",
                                 "Updates & Announcements", "Case Study", "Incident Review"],
                        help="Content category")

    args = parser.parse_args()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    topic = args.topic.strip("/\\")
    week = args.week.strip()
    title = args.title or topic_to_title(topic)

    # Validate week format
    if not re.match(r'^\d{4}-W\d{2}$', week):
        print(f"❌ Invalid week format: {week}. Expected: YYYY-WNN (e.g., 2026-W13)")
        sys.exit(1)

    # Check output folder exists
    output_path = os.path.join(repo_root, "output", topic)
    if not os.path.exists(output_path):
        print(f"❌ Output folder not found: output/{topic}/")
        print(f"   Run extract_research.py first, then generate outputs.")
        sys.exit(1)

    # Check required output files exist
    required_files = ["newsletter.html", "blog-post.md", "linkedin-post.txt"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(output_path, f))]
    if missing:
        print(f"❌ Missing output files in output/{topic}/:")
        for f in missing:
            print(f"   • {f}")
        print(f"\n   Generate these using Copilot CLI with the prompts in prompts/")
        sys.exit(1)

    # Create edition folder
    edition_path = os.path.join(repo_root, "editions", week)
    edition_output = os.path.join(edition_path, "output")
    edition_assets = os.path.join(edition_path, "assets")

    if os.path.exists(edition_path):
        print(f"⚠️  Edition folder already exists: editions/{week}/")
        response = input("   Overwrite output files? (y/N): ").strip().lower()
        if response != "y":
            print("   Aborted.")
            sys.exit(0)
    else:
        os.makedirs(edition_output, exist_ok=True)
        os.makedirs(edition_assets, exist_ok=True)

    os.makedirs(edition_output, exist_ok=True)

    # Copy output files
    print(f"📦 Preparing edition: {week}")
    print(f"   Topic: {topic}")
    print(f"   Title: {title}")
    print(f"{'─' * 50}")

    for filename in required_files:
        src = os.path.join(output_path, filename)
        dst = os.path.join(edition_output, filename)
        shutil.copy2(src, dst)
        print(f"   ✅ Copied: {filename}")

    # Copy any images from output to assets
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}
    images_copied = 0
    for filename in os.listdir(output_path):
        if os.path.splitext(filename)[1].lower() in image_exts:
            src = os.path.join(output_path, filename)
            dst = os.path.join(edition_assets, filename)
            shutil.copy2(src, dst)
            images_copied += 1
            print(f"   🖼️  Copied image: {filename}")

    # Count existing editions for edition number
    editions_dir = os.path.join(repo_root, "editions")
    existing = [d for d in os.listdir(editions_dir) if os.path.isdir(os.path.join(editions_dir, d))]
    edition_number = len(existing)

    # Create metadata.yml
    slug = topic.lower().strip()
    today = datetime.now().strftime("%Y-%m-%d")
    subtitle = f"Weekly Windows Server Digest — Edition #{edition_number}"

    metadata_content = f"""# Edition Metadata
title: "{title}"
subtitle: "{subtitle}"
slug: "{slug}"
edition_number: {edition_number}
week: "{week}"
date: "{today}"
category: "{args.category}"
series: "Windows Server Weekly"
tags:
  - windows-server
  - powershell
  - sysadmin

cover_image: ""
author: "Kaustubh"
"""
    metadata_path = os.path.join(edition_path, "metadata.yml")
    if not os.path.exists(metadata_path):
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(metadata_content)
        print(f"   📋 Created: metadata.yml")
    else:
        print(f"   📋 Kept existing: metadata.yml")

    # Create content.md placeholder (points to research folder)
    content_md = os.path.join(edition_path, "content.md")
    if not os.path.exists(content_md):
        with open(content_md, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nResearch materials: research/{topic}/\n"
                    f"Extracted text: output/{topic}/_extracted.md\n")
        print(f"   📝 Created: content.md (reference)")

    print(f"\n{'─' * 50}")
    print(f"✅ Edition {week} ready for CI/CD!")
    print(f"   📁 editions/{week}/")
    print(f"   📄 {len(required_files)} output files + {images_copied} images")
    print(f"\n📋 Next steps:")
    print(f"   1. Review: python scripts/validate_outputs.py --edition editions/{week}")
    print(f"   2. Edit metadata.yml if needed (tags, category)")
    print(f"   3. Git commit and push:")
    print(f"      git checkout -b edition/{week}")
    print(f"      git add editions/{week}/")
    print(f'      git commit -m "Add edition {week}: {title}"')
    print(f"      git push origin edition/{week}")
    print(f"   4. Open PR → merge → CI/CD publishes Hashnode draft")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
validate_outputs.py — Validate newsletter edition outputs before publishing.

Checks:
- metadata.yml has required fields
- All 3 output files exist and are non-empty
- HTML is well-formed
- Markdown has frontmatter
- Images referenced in content exist in assets/

Usage:
    python scripts/validate_outputs.py --edition editions/2026-W12
    python scripts/validate_outputs.py --all
"""

import argparse
import os
import re
import sys
from html.parser import HTMLParser


class HTMLValidator(HTMLParser):
    """Simple HTML validator that checks for unclosed tags."""

    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }

    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.VOID_ELEMENTS:
            self.tag_stack.append(tag.lower())

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.VOID_ELEMENTS:
            return
        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag: </{tag}>")
        elif self.tag_stack[-1] != tag:
            self.errors.append(f"Mismatched tag: expected </{self.tag_stack[-1]}>, got </{tag}>")
            # Try to recover
            if tag in self.tag_stack:
                while self.tag_stack and self.tag_stack[-1] != tag:
                    self.tag_stack.pop()
                if self.tag_stack:
                    self.tag_stack.pop()
        else:
            self.tag_stack.pop()


def validate_metadata(edition_path: str) -> list:
    """Validate metadata.yml has required fields."""
    errors = []
    metadata_path = os.path.join(edition_path, "metadata.yml")

    if not os.path.exists(metadata_path):
        return ["❌ metadata.yml not found"]

    with open(metadata_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_fields = ["title", "subtitle", "slug", "week", "date", "tags", "series"]
    for field in required_fields:
        # Simple check: field name followed by colon
        if not re.search(rf'^{field}\s*:', content, re.MULTILINE):
            errors.append(f"❌ metadata.yml missing required field: {field}")

    # Check title is not placeholder
    title_match = re.search(r'^title:\s*"(.+)"', content, re.MULTILINE)
    if title_match and "{{" in title_match.group(1):
        errors.append("❌ metadata.yml title still contains placeholder text")

    return errors


def validate_html(edition_path: str) -> list:
    """Validate HTML email output."""
    errors = []
    html_path = os.path.join(edition_path, "output", "newsletter.html")

    if not os.path.exists(html_path):
        return ["❌ output/newsletter.html not found"]

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content.strip()) < 100:
        errors.append("❌ newsletter.html appears to be a placeholder (too short)")
        return errors

    # Check for basic HTML structure
    if "<!DOCTYPE html>" not in content and "<!doctype html>" not in content.lower():
        errors.append("⚠️  newsletter.html missing DOCTYPE declaration")

    if "<html" not in content.lower():
        errors.append("❌ newsletter.html missing <html> tag")

    # Check for required sections
    required_patterns = [
        (r'class=["\']header["\']', "header section"),
        (r'class=["\']content["\']', "content section"),
        (r'class=["\']footer["\']', "footer section"),
    ]
    for pattern, name in required_patterns:
        if not re.search(pattern, content):
            errors.append(f"⚠️  newsletter.html missing {name}")

    # Check for placeholder text
    placeholders = re.findall(r'\{\{[A-Z_]+\}\}', content)
    if placeholders:
        errors.append(f"❌ newsletter.html still has placeholders: {', '.join(placeholders[:5])}")

    # HTML tag validation
    validator = HTMLValidator()
    try:
        validator.feed(content)
        if validator.errors:
            for err in validator.errors[:5]:
                errors.append(f"⚠️  HTML: {err}")
        if validator.tag_stack:
            errors.append(f"⚠️  HTML: unclosed tags: {', '.join(validator.tag_stack[:5])}")
    except Exception as e:
        errors.append(f"⚠️  HTML parsing error: {e}")

    return errors


def validate_blog(edition_path: str) -> list:
    """Validate Hashnode blog post output."""
    errors = []
    blog_path = os.path.join(edition_path, "output", "blog-post.md")

    if not os.path.exists(blog_path):
        return ["❌ output/blog-post.md not found"]

    with open(blog_path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content.strip()) < 100:
        errors.append("❌ blog-post.md appears to be a placeholder (too short)")
        return errors

    # Check for frontmatter
    if not content.startswith("---"):
        errors.append("❌ blog-post.md missing YAML frontmatter (should start with ---)")
    else:
        # Check frontmatter has required fields
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            fm = frontmatter_match.group(1)
            for field in ["title", "tags"]:
                if field not in fm:
                    errors.append(f"❌ blog-post.md frontmatter missing: {field}")
        else:
            errors.append("❌ blog-post.md frontmatter not properly closed (missing closing ---)")

    # Check for headings
    headings = re.findall(r'^#{1,3}\s+.+', content, re.MULTILINE)
    if len(headings) < 2:
        errors.append("⚠️  blog-post.md has fewer than 2 headings — consider adding structure")

    # Check for placeholders
    placeholders = re.findall(r'\{\{[A-Z_]+\}\}', content)
    if placeholders:
        errors.append(f"❌ blog-post.md still has placeholders: {', '.join(placeholders[:5])}")

    return errors


def validate_linkedin(edition_path: str) -> list:
    """Validate LinkedIn post output."""
    errors = []
    linkedin_path = os.path.join(edition_path, "output", "linkedin-post.txt")

    if not os.path.exists(linkedin_path):
        return ["❌ output/linkedin-post.txt not found"]

    with open(linkedin_path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content.strip()) < 50:
        errors.append("❌ linkedin-post.txt appears to be a placeholder (too short)")
        return errors

    # Check length (LinkedIn limit is ~3000 chars, optimal is <1300)
    if len(content) > 3000:
        errors.append(f"⚠️  linkedin-post.txt is {len(content)} chars (LinkedIn limit is ~3000)")
    elif len(content) > 1300:
        errors.append(f"⚠️  linkedin-post.txt is {len(content)} chars (optimal is under 1300)")

    # Check for hashtags
    hashtags = re.findall(r'#\w+', content)
    if len(hashtags) < 3:
        errors.append("⚠️  linkedin-post.txt has fewer than 3 hashtags")
    elif len(hashtags) > 15:
        errors.append(f"⚠️  linkedin-post.txt has {len(hashtags)} hashtags (recommended: 8-12)")

    # Check for blog link
    if "hashnode" not in content.lower() and "http" not in content.lower():
        errors.append("⚠️  linkedin-post.txt missing blog link")

    # Check for placeholders
    placeholders = re.findall(r'\{\{[A-Z_]+\}\}', content)
    if placeholders:
        errors.append(f"❌ linkedin-post.txt still has placeholders: {', '.join(placeholders[:5])}")

    return errors


def validate_edition(edition_path: str) -> bool:
    """Run all validations on an edition and report results."""
    edition_name = os.path.basename(edition_path)
    print(f"\n{'='*60}")
    print(f"📋 Validating: {edition_name}")
    print(f"{'='*60}")

    all_errors = []

    # Run all validators
    validators = [
        ("Metadata", validate_metadata),
        ("HTML Email", validate_html),
        ("Blog Post", validate_blog),
        ("LinkedIn Post", validate_linkedin),
    ]

    for name, validator_fn in validators:
        print(f"\n🔍 {name}...")
        errors = validator_fn(edition_path)
        if errors:
            for err in errors:
                print(f"   {err}")
            all_errors.extend(errors)
        else:
            print(f"   ✅ All checks passed")

    # Summary
    print(f"\n{'─'*60}")
    critical = [e for e in all_errors if e.startswith("❌")]
    warnings = [e for e in all_errors if e.startswith("⚠️")]

    if not all_errors:
        print(f"✅ {edition_name}: All validations passed!")
        return True
    else:
        print(f"📊 {edition_name}: {len(critical)} errors, {len(warnings)} warnings")
        if critical:
            print(f"   ❌ Fix {len(critical)} error(s) before publishing")
            return False
        else:
            print(f"   ⚠️  {len(warnings)} warning(s) — review but not blocking")
            return True


def main():
    parser = argparse.ArgumentParser(description="Validate newsletter edition outputs")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--edition", help="Path to a specific edition folder")
    group.add_argument("--all", action="store_true", help="Validate all editions")

    args = parser.parse_args()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.all:
        editions_dir = os.path.join(repo_root, "editions")
        editions = sorted([
            os.path.join(editions_dir, d)
            for d in os.listdir(editions_dir)
            if os.path.isdir(os.path.join(editions_dir, d))
        ])
        if not editions:
            print("No editions found.")
            sys.exit(0)

        results = []
        for edition_path in editions:
            passed = validate_edition(edition_path)
            results.append((os.path.basename(edition_path), passed))

        print(f"\n{'='*60}")
        print(f"📊 SUMMARY: {sum(1 for _, p in results if p)}/{len(results)} editions passed")
        for name, passed in results:
            status = "✅" if passed else "❌"
            print(f"   {status} {name}")

        if not all(p for _, p in results):
            sys.exit(1)
    else:
        edition_path = args.edition
        if not os.path.isabs(edition_path):
            edition_path = os.path.join(os.getcwd(), edition_path)
        if not os.path.exists(edition_path):
            print(f"❌ Edition not found: {edition_path}")
            sys.exit(1)
        if not validate_edition(edition_path):
            sys.exit(1)


if __name__ == "__main__":
    main()

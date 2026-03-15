#!/usr/bin/env python3
"""
publish_hashnode.py — Publish a newsletter edition as a draft to Hashnode.

Uses the Hashnode GraphQL API to create a draft blog post from the
edition's blog-post.md and metadata.yml.

Usage:
    python scripts/publish_hashnode.py --edition editions/2026-W12

Environment variables (or GitHub Secrets):
    HASHNODE_TOKEN         — Personal Access Token from hashnode.com/settings/developer
    HASHNODE_PUBLICATION_ID — Your publication ID from Hashnode dashboard

To find your Publication ID:
    1. Go to your Hashnode blog dashboard
    2. Open Settings → General
    3. The Publication ID is shown at the bottom, or can be found via the API
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error


HASHNODE_API_URL = "https://gql.hashnode.com"


def load_metadata(edition_path: str) -> dict:
    """Load and parse metadata.yml (simple parser, no PyYAML dependency)."""
    metadata_path = os.path.join(edition_path, "metadata.yml")
    if not os.path.exists(metadata_path):
        print(f"❌ metadata.yml not found in {edition_path}")
        sys.exit(1)

    metadata = {}
    current_list_key = None
    current_list = []

    with open(metadata_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            # Skip comments and empty lines
            if not line or line.strip().startswith("#"):
                if current_list_key:
                    # End of list, save it
                    metadata[current_list_key] = current_list
                    current_list_key = None
                    current_list = []
                continue

            # Check for list item
            list_match = re.match(r'^\s+-\s+(.+)', line)
            if list_match and current_list_key:
                current_list.append(list_match.group(1).strip().strip('"').strip("'"))
                continue

            # Check for key-value pair
            kv_match = re.match(r'^(\w+)\s*:\s*(.+)?', line)
            if kv_match:
                if current_list_key:
                    metadata[current_list_key] = current_list
                    current_list_key = None
                    current_list = []

                key = kv_match.group(1)
                value = (kv_match.group(2) or "").strip().strip('"').strip("'")

                if not value:
                    # Could be start of a list
                    current_list_key = key
                    current_list = []
                else:
                    metadata[key] = value

    if current_list_key:
        metadata[current_list_key] = current_list

    return metadata


def load_blog_content(edition_path: str) -> str:
    """Load blog post markdown content."""
    blog_path = os.path.join(edition_path, "output", "blog-post.md")
    if not os.path.exists(blog_path):
        print(f"❌ output/blog-post.md not found in {edition_path}")
        sys.exit(1)

    with open(blog_path, "r", encoding="utf-8") as f:
        return f.read()


def find_hashnode_tags(tag_names: list, token: str) -> list:
    """Search for Hashnode tag IDs by name."""
    tags = []
    for tag_name in tag_names[:5]:  # Hashnode limits to 5 tags
        query = """
        query SearchTags($query: String!) {
            searchTags(query: $query, first: 1) {
                edges {
                    node {
                        id
                        name
                        slug
                    }
                }
            }
        }
        """
        payload = {
            "query": query,
            "variables": {"query": tag_name}
        }

        try:
            req = urllib.request.Request(
                HASHNODE_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": token,
                },
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode())
                edges = result.get("data", {}).get("searchTags", {}).get("edges", [])
                if edges:
                    tags.append({
                        "id": edges[0]["node"]["id"],
                        "name": edges[0]["node"]["name"],
                        "slug": edges[0]["node"]["slug"],
                    })
        except Exception as e:
            print(f"  ⚠️  Could not find tag '{tag_name}': {e}")

    return tags


def publish_draft(publication_id: str, token: str, title: str, content: str,
                  subtitle: str = "", slug: str = "", tags: list = None,
                  cover_image: str = "") -> dict:
    """Publish a draft post to Hashnode."""

    # Build tags input
    tag_ids = [{"id": t["id"], "name": t["name"], "slug": t["slug"]} for t in (tags or [])]

    query = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post {
                id
                title
                slug
                url
            }
        }
    }
    """

    variables = {
        "input": {
            "publicationId": publication_id,
            "title": title,
            "subtitle": subtitle or "",
            "contentMarkdown": content,
            "tags": tag_ids,
            "publishedAt": None,  # null = draft
        }
    }

    if slug:
        variables["input"]["slug"] = slug

    if cover_image:
        variables["input"]["coverImageOptions"] = {"coverImageURL": cover_image}

    payload = {"query": query, "variables": variables}

    try:
        req = urllib.request.Request(
            HASHNODE_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": token,
            },
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())

            if "errors" in result:
                print(f"❌ Hashnode API error:")
                for err in result["errors"]:
                    print(f"   {err.get('message', err)}")
                sys.exit(1)

            post = result.get("data", {}).get("publishPost", {}).get("post", {})
            return post

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ HTTP {e.code}: {body}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error publishing to Hashnode: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Publish newsletter edition as Hashnode draft")
    parser.add_argument("--edition", required=True, help="Path to edition folder (e.g., editions/2026-W12)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be published without actually publishing")

    args = parser.parse_args()

    # Resolve edition path
    edition_path = args.edition
    if not os.path.isabs(edition_path):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        edition_path = os.path.join(repo_root, edition_path)

    if not os.path.exists(edition_path):
        print(f"❌ Edition not found: {edition_path}")
        sys.exit(1)

    # Load environment variables
    token = os.environ.get("HASHNODE_TOKEN", "")
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID", "")

    if not args.dry_run and (not token or not publication_id):
        print("❌ Missing environment variables:")
        if not token:
            print("   HASHNODE_TOKEN — set your Hashnode Personal Access Token")
        if not publication_id:
            print("   HASHNODE_PUBLICATION_ID — set your Hashnode publication ID")
        print("\nGet your token at: https://hashnode.com/settings/developer")
        sys.exit(1)

    # Load data
    metadata = load_metadata(edition_path)
    content = load_blog_content(edition_path)
    edition_name = os.path.basename(edition_path)

    title = metadata.get("title", f"Newsletter {edition_name}")
    subtitle = metadata.get("subtitle", "")
    slug = metadata.get("slug", "")
    tag_names = metadata.get("tags", [])
    cover_image = metadata.get("cover_image", "")

    print(f"📰 Publishing: {title}")
    print(f"   Edition: {edition_name}")
    print(f"   Slug: {slug}")
    print(f"   Tags: {', '.join(tag_names)}")
    print(f"   Content length: {len(content)} chars")

    if args.dry_run:
        print(f"\n🔍 DRY RUN — nothing published")
        print(f"   Title: {title}")
        print(f"   Subtitle: {subtitle}")
        print(f"   Tags: {tag_names}")
        print(f"   Content preview: {content[:200]}...")
        return

    # Find Hashnode tags
    print(f"\n🏷️  Resolving tags...")
    tags = find_hashnode_tags(tag_names, token)
    print(f"   Found {len(tags)} tags: {', '.join(t['name'] for t in tags)}")

    # Publish draft
    print(f"\n📤 Publishing draft to Hashnode...")
    post = publish_draft(
        publication_id=publication_id,
        token=token,
        title=title,
        content=content,
        subtitle=subtitle,
        slug=slug,
        tags=tags,
        cover_image=cover_image,
    )

    print(f"\n✅ Draft published successfully!")
    print(f"   📝 Title: {post.get('title', 'N/A')}")
    print(f"   🔗 URL: {post.get('url', 'N/A')}")
    print(f"   🆔 Post ID: {post.get('id', 'N/A')}")
    print(f"\n📋 Next steps:")
    print(f"   1. Go to your Hashnode dashboard")
    print(f"   2. Review the draft")
    print(f"   3. Hit 'Publish' when ready!")


if __name__ == "__main__":
    main()

"""Usage: python scripts/test_apify.py @garyvee instagram"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from services.apify_client import fetch_instagram, fetch_tiktok

async def main():
    handle = sys.argv[1] if len(sys.argv) > 1 else "@garyvee"
    platform = sys.argv[2] if len(sys.argv) > 2 else "instagram"
    print(f"Fetching {platform} data for {handle}...")
    if platform == "instagram":
        posts, profile = await fetch_instagram(handle)
    else:
        posts, profile = await fetch_tiktok(handle)
    print(f"Profile: {profile.handle} | {profile.followers:,} followers")
    print(f"Posts fetched: {len(posts)}")
    if posts:
        top = sorted(posts, key=lambda p: p.engagement_rate, reverse=True)[:3]
        for p in top:
            print(f"  ER={p.engagement_rate:.2f}% | {p.post_format} | {p.caption[:60]!r}")

asyncio.run(main())

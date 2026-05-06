"""
Usage:
  python scripts/cache_demo.py --handle garyvee --platform instagram
  python scripts/cache_demo.py --handle khaby.lame --platform tiktok
"""
import asyncio, sys, os, json, argparse, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv; load_dotenv()
from agents.crew import analyze
from streaming.sse import ProgressEvent

async def emit(event: ProgressEvent):
    print(f"  [{event.pct}%] {event.message}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", required=True)
    parser.add_argument("--platform", default="instagram")
    args = parser.parse_args()

    print(f"Caching {args.platform} / @{args.handle}...")
    rec = await analyze(args.handle, args.platform, emit=emit)

    out_dir = pathlib.Path(__file__).parent.parent / "cache" / "demo_accounts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.platform}_{args.handle.lstrip('@')}.json"
    out_path.write_text(rec.model_dump_json(indent=2))
    print(f"\nSaved to {out_path}")

asyncio.run(main())

"""Command-line entry point for the dialogue-shorts factory.

  python -m factory avatars                 # (re)generate the avatar library
  python -m factory demo                    # render the first seed script
  python -m factory make --pair couple      # generate + render one new short
  python -m factory batch --count 5         # mass-produce N shorts
  python -m factory batch --count 3 --publish
"""
from __future__ import annotations

import argparse
import os
import time
import traceback
from pathlib import Path

from . import script_gen
from .config import ROOT, load_settings
from .pipeline import render_video
from .script_model import load_scripts


def _slug_dir(base: str) -> str:
    d = ROOT / "output" / base
    n, cand = 1, d
    while cand.exists():
        cand = ROOT / "output" / f"{base}-{n}"
        n += 1
    return str(cand)


def cmd_avatars(_args) -> None:
    from .avatars import ROLES, avatar_png
    s = load_settings()
    for r in ROLES:
        print(avatar_png(r, s))


def cmd_demo(_args) -> None:
    s = load_settings()
    sc = load_scripts(ROOT / "scripts" / "seed_scripts.json")[0]
    res = render_video(sc, s, out_dir=str(ROOT / "output" / "demo"))
    print(f"\n✅ {res.video}  ({res.duration:.1f}s)")


def _make_one(settings, pair, topic, publish: bool):
    sc = script_gen.generate(settings, pair=pair, topic=topic)
    res = render_video(sc, settings, out_dir=_slug_dir(sc.id))
    print(f"✅ {res.video}  ({res.duration:.1f}s)")
    if publish:
        from .publish import publish as do_publish
        import json
        meta = json.loads(Path(res.metadata_path).read_text(encoding="utf-8"))
        info = do_publish(res.video, res.thumbnail, meta, settings)
        if info:
            print(f"   📤 {info.get('url')}")
    return res


def cmd_make(args) -> None:
    s = load_settings()
    _make_one(s, args.pair, args.topic, args.publish)


def cmd_batch(args) -> None:
    s = load_settings()
    made = 0
    while made < args.count:
        try:
            _make_one(s, args.pair, args.topic, args.publish)
            made += 1
        except Exception:
            traceback.print_exc()
        if made < args.count and args.sleep:
            time.sleep(args.sleep)
    print(f"\n🎬 done: {made}/{args.count} shorts")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="factory", description="Korean dialogue shorts factory")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("avatars").set_defaults(func=cmd_avatars)
    d = sub.add_parser("demo")
    d.add_argument("--format", choices=["call", "scene"], default=None)
    d.set_defaults(func=cmd_demo)

    m = sub.add_parser("make")
    m.add_argument("--pair", default=None, help="dad_daughter, couple, grandma_grandchild, ...")
    m.add_argument("--topic", default=None)
    m.add_argument("--format", choices=["call", "scene"], default=None)
    m.add_argument("--publish", action="store_true")
    m.set_defaults(func=cmd_make)

    b = sub.add_parser("batch")
    b.add_argument("--count", type=int, default=3)
    b.add_argument("--pair", default=None)
    b.add_argument("--topic", default=None)
    b.add_argument("--format", choices=["call", "scene"], default=None)
    b.add_argument("--publish", action="store_true")
    b.add_argument("--sleep", type=float, default=0)
    b.set_defaults(func=cmd_batch)

    args = p.parse_args(argv)
    if getattr(args, "format", None):
        os.environ["VIDEO_FORMAT"] = args.format
    args.func(args)


if __name__ == "__main__":
    main()

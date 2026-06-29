"""Format B — split-screen "scene" base frame (richer than the call UI).

Top half = speaker A in a cozy room, bottom half = speaker B in a different
room, each with a character + a name badge. Title overlays the top. The
per-speaker caption and the active/inactive dimming are added by the compositor.

Characters are the avatar PNGs enlarged; drop AI-illustrated (e.g. Pixar-style)
PNGs into assets/avatars/ with AVATAR_PROVIDER=files for a premium look.
"""
from __future__ import annotations

import base64
import os
import subprocess
from pathlib import Path

from . import layout as L
from .avatars import avatar_png
from .config import ROOT, Settings
from .script_model import Script

RENDER_JS = ROOT / "tools" / "render_html.js"
S = L.SCENE


def _data_uri(p: str) -> str:
    return "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()


def _room(which: str, char_uri: str, label: str, cy: int, label_cy: int) -> str:
    top = 0 if which == "top" else S["half_h"]
    if which == "top":
        wall = "linear-gradient(160deg,#f6e7d2,#e6cbab)"
        floor, couch, accent = "#cba47c", "#b98e63", "#d98c5f"
    else:
        wall = "linear-gradient(160deg,#dde8ef,#b9cedd)"
        floor, couch, accent = "#9fb1be", "#7f97a6", "#5b86a6"
    char_w = int(S["char_h"] * 400 / 480)
    return f"""
    <div class="half" style="top:{top}px; background:{wall}">
      <div class="floor" style="background:{floor}"></div>
      <div class="tv"></div>
      <div class="pic"></div>
      <div class="plant"><span class="leaves"></span><span class="pot"></span></div>
      <div class="couch" style="background:{couch}"></div>
    </div>
    <img class="char" src="{char_uri}"
         style="left:540px; top:{cy}px; height:{S['char_h']}px; width:{char_w}px"/>
    <div class="badge" style="top:{label_cy}px; background:{accent}">{label}</div>"""


def build_html(script: Script, img_a: str, img_b: str, settings: Settings) -> str:
    a, b = script.char("A"), script.char("B")
    uri_a, uri_b = _data_uri(img_a), _data_uri(img_b)
    title = "<br>".join(script.title_en.split("\n"))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{{margin:0;padding:0}}
  #stage{{position:relative;width:{L.W}px;height:{L.H}px;background:#000;overflow:hidden;
    font-family:'{settings.caption_font}','DejaVu Sans',sans-serif}}
  .half{{position:absolute;left:0;width:{L.W}px;height:{S['half_h']}px;overflow:hidden}}
  .floor{{position:absolute;left:0;bottom:0;width:100%;height:190px;opacity:0.95}}
  .tv{{position:absolute;left:90px;top:120px;width:300px;height:180px;background:#22272e;
    border:10px solid #11151a;border-radius:14px;box-shadow:0 10px 24px rgba(0,0,0,.25)}}
  .pic{{position:absolute;right:120px;top:140px;width:120px;height:150px;background:#fff7ea;
    border:12px solid #caa97f;border-radius:6px;transform:rotate(-2deg)}}
  .plant .leaves{{position:absolute;right:70px;top:430px;width:120px;height:120px;
    background:radial-gradient(circle at 40% 40%,#6fae6a,#3f7e44);border-radius:50% 50% 45% 55%}}
  .plant .pot{{position:absolute;right:92px;top:540px;width:76px;height:70px;
    background:#b9663f;border-radius:6px 6px 12px 12px}}
  .couch{{position:absolute;left:50%;transform:translateX(-50%);bottom:60px;
    width:760px;height:240px;border-radius:60px 60px 28px 28px;box-shadow:0 14px 30px rgba(0,0,0,.22)}}
  .char{{position:absolute;transform:translate(-50%,-50%);
    filter:drop-shadow(0 16px 20px rgba(0,0,0,.35))}}
  .badge{{position:absolute;left:50%;transform:translate(-50%,-50%);color:#1a1a1a;
    font-size:46px;font-weight:800;padding:8px 34px;border-radius:40px;
    box-shadow:0 6px 16px rgba(0,0,0,.3);white-space:nowrap}}
  .divider{{position:absolute;left:0;top:{S['half_h']-3}px;width:100%;height:6px;
    background:rgba(0,0,0,.55)}}
  .titlewrap{{position:absolute;left:0;top:{S['title_top']}px;width:100%;text-align:center;z-index:5}}
  .kicker{{color:#fff;font-size:34px;font-weight:700;letter-spacing:6px;opacity:.85;
    text-shadow:0 2px 8px rgba(0,0,0,.8)}}
  .title{{color:#FFE53B;font-size:84px;font-weight:800;line-height:1.08;margin-top:8px;
    letter-spacing:-1px;text-shadow:0 4px 18px rgba(0,0,0,.85),0 0 4px rgba(0,0,0,.8)}}
  .recpill{{position:absolute;right:34px;top:34px;display:flex;align-items:center;gap:12px;
    background:rgba(0,0,0,.45);padding:10px 22px;border-radius:30px;z-index:6}}
  .recpill .dot{{width:18px;height:18px;border-radius:50%;background:#ff3b3b;box-shadow:0 0 12px #ff3b3b}}
  .recpill span{{color:#fff;font-size:30px;font-weight:700;letter-spacing:2px}}
</style></head><body>
  <div id="stage">
    {_room('top', uri_a, a.label, S['charA_cy'], S['labelA_cy'])}
    {_room('bottom', uri_b, b.label, S['charB_cy'], S['labelB_cy'])}
    <div class="divider"></div>
    <div class="recpill"><span class="dot"></span><span>REC</span></div>
    <div class="titlewrap"><div class="kicker">TODAY'S CALL</div><div class="title">{title}</div></div>
  </div>
</body></html>"""


def render_base(script: Script, settings: Settings, out_dir: str) -> str:
    img_a = str(avatar_png(script.char("A").role, settings))
    img_b = str(avatar_png(script.char("B").role, settings))
    html = build_html(script, img_a, img_b, settings)
    html_path = Path(out_dir) / "frame_scene.html"
    html_path.write_text(html, encoding="utf-8")
    out_png = Path(out_dir) / "frame_scene.png"
    env = dict(os.environ)
    env.setdefault("NODE_PATH", subprocess.run(
        ["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(
        ["node", str(RENDER_JS), "--html", str(html_path), "--out", str(out_png),
         "--width", str(L.W), "--height", str(L.H), "--selector", "#stage"],
        check=True, env=env, capture_output=True, text=True)
    return str(out_png)

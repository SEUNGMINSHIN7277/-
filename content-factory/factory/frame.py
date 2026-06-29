"""Render the static call-recording UI frame to a PNG (via Playwright).

Everything that does NOT change over time lives here: black background, phone
status bar, video-player controls, the title, both speaker avatars + labels,
and the bottom REC bar. The animated waveform, per-line caption and
active-speaker highlight are layered on afterwards by compositor.py.
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


def _icons_top() -> str:
    # status bar (time + signal/wifi/battery) and player controls row
    return f"""
    <div class="statusbar">
      <span class="clock">12:15</span>
      <span class="sysicons">
        <svg width="34" height="24"><g fill="#e9e9e9">
          <rect x="0" y="14" width="5" height="8" rx="1"/><rect x="7" y="10" width="5" height="12" rx="1"/>
          <rect x="14" y="6" width="5" height="16" rx="1"/><rect x="21" y="2" width="5" height="20" rx="1"/></g></svg>
        <svg width="30" height="24" viewBox="0 0 24 24" fill="#e9e9e9"><path d="M12 18.5a2 2 0 110 .01zM4 11a11 11 0 0116 0l-2 2a8 8 0 00-12 0z"/></svg>
        <svg width="40" height="24"><rect x="1" y="5" width="32" height="15" rx="3" fill="none" stroke="#e9e9e9" stroke-width="2"/>
          <rect x="34" y="9" width="3" height="7" rx="1" fill="#e9e9e9"/><rect x="3" y="7" width="26" height="11" rx="1" fill="#e9e9e9"/></svg>
      </span>
    </div>
    <div class="controls">
      <span class="left">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="#f0f0f0"><path d="M8 5v14l11-7z"/></svg>
        <svg width="38" height="38" viewBox="0 0 24 24" fill="#f0f0f0"><path d="M3 10v4h4l5 5V5L7 10H3zm13.5 2a4.5 4.5 0 00-2.5-4v8a4.5 4.5 0 002.5-4z"/></svg>
      </span>
      <span class="right">
        <svg width="44" height="30" viewBox="0 0 28 18"><rect x="1" y="1" width="26" height="16" rx="4" fill="none" stroke="#f0f0f0" stroke-width="2"/>
          <text x="14" y="13" font-size="9" fill="#f0f0f0" text-anchor="middle" font-family="Arial" font-weight="700">CC</text></svg>
        <svg width="30" height="38" viewBox="0 0 24 24" fill="#f0f0f0"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#f0f0f0" stroke-width="2.4">
          <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>
      </span>
    </div>"""


def _data_uri(img_path: str) -> str:
    raw = Path(img_path).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def _avatar_block(which: str, img_src: str, label: str) -> str:
    box = L.avatar_box(which)
    cx = box[0] + box[2] // 2
    lx, ly = L.label_pos(which)
    return f"""
    <img class="avatar" id="av{which}" src="{img_src}"
         style="left:{cx}px; top:{box[1] + box[3] // 2}px; width:{box[2]}px; height:{box[3]}px"/>
    <div class="label" style="left:{lx}px; top:{ly}px">{label}</div>"""


def _rec_bar() -> str:
    bars = "".join(
        f'<span style="height:{h}px"></span>'
        for h in [8, 16, 26, 14, 30, 20, 36, 22, 30, 12, 24, 16, 28, 10, 18, 26, 14, 20, 8]
    )
    return f"""
    <div class="recbar" style="left:{L.REC['cx']}px; top:{L.REC['cy']}px">
      <span class="recdot"></span><span class="rectxt">REC</span>
      <span class="rectime">0:00</span>
      <div class="recwave">{bars}</div>
    </div>"""


def build_html(script: Script, img_a: str, img_b: str, settings: Settings) -> str:
    title_lines = script.title_en.split("\n")
    title_html = "<br>".join(title_lines)
    a, b = script.char("A"), script.char("B")
    # Map A/B to whichever occupies top_left vs bottom_right.
    top = a if a.corner == "top_left" else b
    bot = b if a.corner == "top_left" else a
    uri_a, uri_b = _data_uri(img_a), _data_uri(img_b)
    top_img = uri_a if top.id == "A" else uri_b
    bot_img = uri_b if bot.id == "B" else uri_a

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
  html,body {{ margin:0; padding:0; }}
  #stage {{ position:relative; width:{L.W}px; height:{L.H}px; background:#000;
    overflow:hidden; font-family:'{settings.caption_font}','DejaVu Sans',sans-serif; }}
  .statusbar {{ position:absolute; top:14px; left:0; width:100%; display:flex;
    justify-content:space-between; align-items:center; padding:0 34px; box-sizing:border-box; }}
  .clock {{ color:#fff; font-size:34px; font-weight:600; }}
  .sysicons {{ display:flex; align-items:center; gap:12px; }}
  .controls {{ position:absolute; top:74px; left:0; width:100%; display:flex;
    justify-content:space-between; align-items:center; padding:0 30px; box-sizing:border-box; }}
  .controls .left, .controls .right {{ display:flex; align-items:center; gap:26px; }}
  .title {{ position:absolute; left:50%; top:{L.TITLE['top']}px; transform:translateX(-50%);
    width:{L.TITLE['max_w']}px; text-align:center; color:{('#' + settings.title_color)};
    font-size:{L.TITLE['size']}px; font-weight:800; line-height:1.12;
    text-shadow:0 4px 14px rgba(0,0,0,0.6); letter-spacing:-1px; }}
  .avatar {{ position:absolute; transform:translate(-50%,-50%);
    filter:drop-shadow(0 12px 22px rgba(0,0,0,0.45)); }}
  .label {{ position:absolute; transform:translate(-50%,-50%); color:#fff;
    font-size:46px; font-weight:800; text-shadow:0 3px 10px rgba(0,0,0,0.7); }}
  .recbar {{ position:absolute; transform:translate(-50%,-50%); display:flex;
    align-items:center; gap:16px; }}
  .recdot {{ width:22px; height:22px; border-radius:50%; background:#ff3b3b;
    box-shadow:0 0 14px #ff3b3b; }}
  .rectxt {{ color:#fff; font-size:34px; font-weight:700; letter-spacing:2px; }}
  .rectime {{ color:#cfcfcf; font-size:34px; font-weight:600; margin-right:10px; }}
  .recwave {{ display:flex; align-items:center; gap:6px; height:40px; }}
  .recwave span {{ width:6px; background:#bdbdbd; border-radius:3px; }}
</style></head><body>
  <div id="stage">
    {_icons_top()}
    <div class="title">{title_html}</div>
    {_avatar_block('A' if top.id == 'A' else 'B', top_img, top.label)}
    {_avatar_block('B' if bot.id == 'B' else 'A', bot_img, bot.label)}
    {_rec_bar()}
  </div>
</body></html>"""


def render_base(script: Script, settings: Settings, out_dir: str) -> str:
    img_a = str(avatar_png(script.char("A").role, settings))
    img_b = str(avatar_png(script.char("B").role, settings))
    html = build_html(script, img_a, img_b, settings)
    html_path = Path(out_dir) / "frame.html"
    html_path.write_text(html, encoding="utf-8")
    out_png = Path(out_dir) / "frame.png"
    env = dict(os.environ)
    env.setdefault("NODE_PATH", subprocess.run(
        ["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    res = subprocess.run(
        ["node", str(RENDER_JS), "--html", str(html_path), "--out", str(out_png),
         "--width", str(L.W), "--height", str(L.H), "--selector", "#stage"],
        env=env, capture_output=True, text=True,
    )
    if res.returncode != 0 or not Path(out_png).exists():
        raise RuntimeError(
            "frame render via node/Playwright failed. Ensure Node + Playwright "
            "Chromium are installed.\n"
            f"--- node stderr ---\n{res.stderr[-1800:]}\n--- node stdout ---\n{res.stdout[-400:]}"
        )
    return str(out_png)


if __name__ == "__main__":
    from .config import load_settings
    from .script_model import load_scripts
    s = load_settings()
    sc = load_scripts(ROOT / "scripts" / "seed_scripts.json")[0]
    print(render_base(sc, s, str(ROOT / "output")))

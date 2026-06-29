"""Cute flat-illustration avatars per role, as SVG -> PNG (via Playwright).

These are intentionally simple, consistent, recognizable cartoon characters so
the channel has a stable look. To upgrade quality later, set
AVATAR_PROVIDER=files and drop PNGs named <role>.png into assets/avatars/, or
wire an image-gen provider in providers.py.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

from .config import ROOT, Settings

AVATAR_DIR = ROOT / "assets" / "avatars"
RENDER_JS = ROOT / "tools" / "render_html.js"

# Per-role styling knobs.
ROLES: dict[str, dict] = {
    "little_girl":  {"skin": "#FFE0C2", "hair": "#5A3D2B", "shirt": "#FF8FB1", "scale": 0.86, "eyes": 1.18, "blush": True,  "hairstyle": "pigtails", "acc": None},
    "little_boy":   {"skin": "#FFE0C2", "hair": "#3A2C25", "shirt": "#FFD24A", "scale": 0.86, "eyes": 1.18, "blush": True,  "hairstyle": "tuft",     "acc": None},
    "teen_girl":    {"skin": "#FAD7B6", "hair": "#2E2620", "shirt": "#76C7A8", "scale": 0.95, "eyes": 1.05, "blush": True,  "hairstyle": "long",     "acc": None},
    "teen_boy":     {"skin": "#F4C8A0", "hair": "#241C18", "shirt": "#FF9F45", "scale": 0.95, "eyes": 1.05, "blush": False, "hairstyle": "short",    "acc": None},
    "young_woman":  {"skin": "#FAD2B0", "hair": "#3A2620", "shirt": "#5BC0BE", "scale": 1.0,  "eyes": 1.02, "blush": True,  "hairstyle": "long",     "acc": None},
    "young_man":    {"skin": "#F2C49A", "hair": "#2A211C", "shirt": "#3D5A80", "scale": 1.0,  "eyes": 1.0,  "blush": False, "hairstyle": "short",    "acc": None},
    "mom":          {"skin": "#F7CDA8", "hair": "#46342B", "shirt": "#FF9E7A", "scale": 1.0,  "eyes": 1.0,  "blush": True,  "hairstyle": "bob",      "acc": None},
    "dad":          {"skin": "#F0BE92", "hair": "#2A211C", "shirt": "#6E7681", "scale": 1.02, "eyes": 0.98, "blush": False, "hairstyle": "short",    "acc": "glasses"},
    "grandma":      {"skin": "#EFD3BC", "hair": "#C9C4BE", "shirt": "#B9A7D6", "scale": 1.0,  "eyes": 0.96, "blush": True,  "hairstyle": "bun",      "acc": "glasses"},
    "grandpa":      {"skin": "#E9CDB4", "hair": "#BFBAB4", "shirt": "#7FA98B", "scale": 1.02, "eyes": 0.96, "blush": False, "hairstyle": "bald",     "acc": "glasses_mustache"},
}

W, H = 400, 480


def _hair_back(p: dict) -> str:
    """Hair drawn BEHIND the head (length, pigtails, bun)."""
    hs, c = p["hairstyle"], p["hair"]
    cd = _darken(c, 0.9)
    if hs == "long":
        return (f'<path d="M104 210 Q88 372 134 436 Q200 452 266 436 Q312 372 296 210 '
                f'Q292 150 200 150 Q108 150 104 210 Z" fill="{c}"/>'
                f'<path d="M104 210 Q98 320 120 400 Q116 300 126 210 Z" fill="{cd}" opacity="0.5"/>')
    if hs == "bob":
        return (f'<path d="M110 208 Q100 332 142 372 Q200 388 258 372 Q300 332 290 208 '
                f'Q286 156 200 156 Q114 156 110 208 Z" fill="{c}"/>')
    if hs == "pigtails":
        return (f'<ellipse cx="98" cy="258" rx="34" ry="48" fill="{c}"/>'
                f'<ellipse cx="302" cy="258" rx="34" ry="48" fill="{c}"/>')
    if hs == "bun":
        return f'<ellipse cx="200" cy="98" rx="31" ry="29" fill="{c}"/>'
    return ""


def _hair_cap(p: dict) -> str:
    """Hair drawn ON TOP of the head (crown coverage + fringe)."""
    hs, c = p["hairstyle"], p["hair"]
    if hs == "bald":
        # thin side fringe near the temples only
        return (f'<path d="M122 252 Q112 214 130 200 Q130 232 140 252 Z" fill="{c}"/>'
                f'<path d="M278 252 Q288 214 270 200 Q270 232 260 252 Z" fill="{c}"/>')
    deep = hs in ("pigtails", "tuft", "long", "bob", "bun", "short")
    fringe_y = 214 if deep else 204
    cap = (f'<path d="M112 250 Q106 146 200 138 Q294 146 288 250 '
           f'Q288 196 200 {fringe_y} Q112 196 112 250 Z" fill="{c}"/>')
    extra = ""
    if hs == "tuft":
        extra = f'<path d="M186 144 Q200 108 214 144 Q200 150 186 144 Z" fill="{c}"/>'
    elif hs == "pigtails":
        extra = ('<circle cx="98" cy="216" r="15" fill="#FF5C8A"/>'
                 '<circle cx="302" cy="216" r="15" fill="#FF5C8A"/>')
    return cap + extra


def _accessory(p: dict) -> str:
    acc = p.get("acc")
    if not acc:
        return ""
    out = ""
    if "glasses" in acc:
        out += ('<g stroke="#2b2b2b" stroke-width="6" fill="none">'
                '<rect x="120" y="208" width="68" height="52" rx="16"/>'
                '<rect x="212" y="208" width="68" height="52" rx="16"/>'
                '<path d="M188 230 L212 230"/></g>')
    if "mustache" in acc:
        out += ('<path d="M164 302 Q200 292 236 302 Q218 320 200 317 Q182 320 164 302 Z" '
                'fill="#9c968e"/>')
    return out


def build_svg(role: str) -> str:
    p = ROLES.get(role, ROLES["young_man"])
    s = p["scale"]
    eye = p["eyes"]
    blush = (
        '<ellipse cx="138" cy="300" rx="26" ry="16" fill="#FF9DB3" opacity="0.6"/>'
        '<ellipse cx="262" cy="300" rx="26" ry="16" fill="#FF9DB3" opacity="0.6"/>'
        if p["blush"] else ""
    )
    er = 17 * eye   # eye radius
    pr = 9 * eye    # pupil radius
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <radialGradient id="cheek" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="{p['skin']}"/>
      <stop offset="100%" stop-color="{_darken(p['skin'], 0.92)}"/>
    </radialGradient>
  </defs>
  <g transform="translate(200,260) scale({s}) translate(-200,-260)">
    <!-- body / shoulders -->
    <path d="M96 470 Q96 388 200 372 Q304 388 304 470 Z" fill="{p['shirt']}"/>
    <path d="M96 470 Q96 388 200 372 Q304 388 304 470 Z" fill="black" opacity="0.05"/>
    {_hair_back(p)}
    <!-- ears -->
    <ellipse cx="112" cy="262" rx="20" ry="26" fill="{p['skin']}"/>
    <ellipse cx="288" cy="262" rx="20" ry="26" fill="{p['skin']}"/>
    <!-- head -->
    <path d="M120 250 Q120 150 200 150 Q280 150 280 250 Q280 350 200 360 Q120 350 120 250 Z" fill="url(#cheek)"/>
    {_hair_cap(p)}
    {blush}
    <!-- eyes -->
    <ellipse cx="162" cy="262" rx="{er}" ry="{er+3}" fill="#fff"/>
    <ellipse cx="238" cy="262" rx="{er}" ry="{er+3}" fill="#fff"/>
    <circle cx="164" cy="266" r="{pr}" fill="#26201c"/>
    <circle cx="236" cy="266" r="{pr}" fill="#26201c"/>
    <circle cx="167" cy="262" r="3.2" fill="#fff"/>
    <circle cx="239" cy="262" r="3.2" fill="#fff"/>
    <!-- brows -->
    <path d="M146 236 Q162 228 180 234" stroke="{_darken(p['hair'],0.8)}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M220 234 Q238 228 254 236" stroke="{_darken(p['hair'],0.8)}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- nose + mouth -->
    <path d="M198 286 Q200 296 206 298" stroke="#caa07e" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M174 318 Q200 342 226 318" stroke="#9b4a3a" stroke-width="6" fill="none" stroke-linecap="round"/>
    {_accessory(p)}
  </g>
</svg>'''


def _darken(hex_color: str, factor: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, min(255, int(c * factor))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _render_png(svg: str, out_png: Path) -> Path:
    html = (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<style>html,body{{margin:0;background:transparent}}'
            f'#a{{width:{W}px;height:{H}px}}</style></head>'
            f'<body><div id="a">{svg}</div></body></html>')
    tmp = out_png.with_suffix(".html")
    tmp.write_text(html, encoding="utf-8")
    env = dict(os.environ)
    env.setdefault("NODE_PATH", subprocess.run(
        ["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    res = subprocess.run(
        ["node", str(RENDER_JS), "--html", str(tmp), "--out", str(out_png),
         "--width", str(W), "--height", str(H), "--selector", "#a", "--transparent"],
        env=env, capture_output=True, text=True,
    )
    if res.returncode != 0 or not out_png.exists():
        raise RuntimeError(
            "avatar render via node/Playwright failed. Make sure Node + "
            "Playwright Chromium are installed (`npm install` + "
            "`npx playwright install --with-deps chromium`).\n"
            f"--- node stderr ---\n{res.stderr[-1800:]}\n--- node stdout ---\n{res.stdout[-400:]}"
        )
    tmp.unlink(missing_ok=True)
    return out_png


def avatar_png(role: str, settings: Settings | None = None) -> Path:
    """Return a PNG path for the role, generating + caching it if needed."""
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    provider = (settings.avatar_provider if settings else "svg")
    if provider == "files":
        custom = AVATAR_DIR / f"{role}.png"
        if custom.exists():
            return custom
        # fall through to svg if a custom file isn't supplied
    svg = build_svg(role)
    digest = hashlib.md5(svg.encode()).hexdigest()[:8]
    out = AVATAR_DIR / f"{role}_{digest}.png"
    if not out.exists():
        _render_png(svg, out)
    return out


if __name__ == "__main__":  # quick gen of all roles
    for r in ROLES:
        print(avatar_png(r))

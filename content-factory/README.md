# 🎬 Dialogue Shorts Factory

Automate **cute & funny Korean phone-call skits with English subtitles** — the
"dad & daughter / couple / grandma & grandson" call-recording format — and
mass-produce them on autopilot for an overseas (English-speaking) audience.

- **Audio** is Korean TTS (different voice per character; toddler lines are
  spelled phonetically so the voice sounds babyish and cute).
- **Everything on screen is English** (title, labels, subtitles) so it travels
  worldwide — and so the renderer needs no CJK fonts.
- **100% original content** (AI-written scripts + AI voices + generated
  avatars). Nothing is ripped from other channels, so your channel won't get
  demonetized/terminated for reused content. *(That is the whole point of doing
  it this way — see "Why original" below.)*

One command renders a finished 1080×1920 MP4 + thumbnail + upload metadata.

---

## What a video looks like

A black "call recording" screen: phone status bar + player controls on top, a
bold yellow title, the two speakers as cute avatars in opposite corners, a live
audio **waveform** in the middle, the **active speaker highlighted** (the other
dims), and big **kinetic English subtitles** color-coded per speaker, over a
REC bar. Run `python -m factory demo` and watch `output/demo/`.

---

## How it works (pipeline)

```
script_gen ─► audio (multi-voice Korean TTS) ─► frame (call-UI PNG)
     │                    │                            │
     │                    ▼                            ▼
     │             per-line timeline            subtitles (English ASS)
     └────────────────────┴──────────────┬─────────────┘
                                          ▼
                       compositor (ffmpeg): base + live waveform
                       + active-speaker highlight + subtitles + audio
                                          ▼
                          final.mp4 + thumbnail + metadata.json
                                          ▼
                                 publish (YouTube)  [optional]
```

Module map (`factory/`):

| File | Job |
|------|-----|
| `script_gen.py` | Write an original skit with Claude (or rotate the seed library) |
| `script_model.py` | Script / Character / Line data model + validation |
| `voices.py` | role → provider voice (+ pitch/rate for cuteness) |
| `tts.py` | per-line Korean TTS (ElevenLabs / Azure / Google / offline demo) |
| `audio.py` | stitch lines into one track + a sync timeline |
| `avatars.py` | cute flat SVG avatars per role → PNG (Playwright) |
| `frame.py` | the static call-UI frame → PNG (Playwright) |
| `subtitles.py` | timed English ASS captions, colored per speaker |
| `compositor.py` | ffmpeg: combine everything into the final MP4 |
| `metadata.py` | title / description / hashtags / thumbnail |
| `pipeline.py` | render one video end-to-end |
| `publish/` | YouTube upload |
| `cli.py` | `avatars` / `demo` / `make` / `batch` |

---

## Setup

### 1. System deps
```bash
cd content-factory
pip install -r requirements.txt          # python deps (+ bundled ffmpeg)
npm install                              # playwright + chromium for rendering
```
(No system ffmpeg or root needed — `imageio-ffmpeg` ships a static binary.)

### 2. Config + secrets
```bash
cp .env.example .env        # fill in keys
# edit config.yaml to pick providers (llm/tts/avatar/publish)
```

### 3. Try it offline (no keys)
```bash
python -m factory avatars   # generate the avatar library
python -m factory demo      # renders the first seed script -> output/demo/
```
With **no API keys**, scripts come from the hand-written seed library and the
voice is a placeholder tone (so you can see layout/timing). Add keys for real
scripts + real Korean voices.

---

## 💸 Run it for $0 (zero-capital mode — the default)

Every step has a free path, so you can launch with **no money and no credit card**:

| Need | Free option | Key? | Notes |
|------|-------------|------|-------|
| Korean voices | **edge-tts** (Microsoft Edge voices) | ❌ none | same ko-KR neural voices as Azure, $0 — this is the default |
| Korean voices (offline) | **espeak-ng** (bundled) | ❌ none | robotic but 100% offline; auto-fallback so audio is **never silent** |
| Scripts | **Gemini free tier** (Google AI Studio) | free key, no card | `https://aistudio.google.com/apikey` |
| Scripts (no key at all) | **seed library** | ❌ none | 4 hand-written skits that rotate |
| Avatars | generated SVG | ❌ | free |
| Rendering / running | ffmpeg + Playwright on your PC | ❌ | free; schedule with cron |
| Music | YouTube Audio Library / Pixabay | ❌ | optional, royalty-free |
| Upload | YouTube Data API | free | OAuth once |

So the literal cost per video is **$0**. (edge-tts uses Microsoft's public Edge
read-aloud endpoint — no key, but it's an unofficial endpoint, so treat it as a
free convenience that could rate-limit; the paid options below are drop-in if
you ever outgrow it.)

### Paid upgrades (only if you want to)

| Need | Provider | Cost |
|------|----------|------|
| Voices (max quality / variety) | ElevenLabs | from $5/mo |
| Voices | Azure / Google Cloud TTS | ~$16 / 1M chars (≈ <$0.01/video) |
| Scripts (top quality) | Anthropic Claude | ~$0.01–0.05 / script |

A ~45s skit is ~250 Korean characters, so even paid TTS is a fraction of a cent.

---

## Commands

```bash
python -m factory avatars                      # (re)build avatar library
python -m factory demo                         # render a seed script
python -m factory make                         # generate + render ONE new short
python -m factory make --pair couple           # force a character pair
python -m factory make --topic "lost the TV remote"
python -m factory batch --count 5              # mass-produce 5 shorts
python -m factory batch --count 5 --publish    # ...and upload them
```

Character pairs: `dad_daughter`, `mom_son`, `couple`,
`grandma_grandchild`, `grandpa_grandchild`, `siblings`.

### Two visual formats

```bash
python -m factory demo --format call    # phone call-recording UI (default)
python -m factory demo --format scene   # split-screen room scene (Format B)
```
- **call** — black "call recording" screen, diagonal avatars, center waveform.
- **scene** — top/bottom split, each speaker in a cozy room with a name badge.
  For a premium Pixar-style look, set `avatar_provider: files` and drop
  AI-illustrated character PNGs into `assets/avatars/`.

---

## Run it while you sleep 😴

The factory is built for unattended mass production. Two easy options:

**Cron (recommended):** post a few videos a day.
```cron
# 3 fresh shorts uploaded every day at 9am (edit path/python as needed)
0 9 * * *  cd /path/to/content-factory && /usr/bin/python3 -m factory batch --count 3 --publish >> output/cron.log 2>&1
```

**Continuous batch:**
```bash
python -m factory batch --count 50 --sleep 30   # 50 shorts, 30s apart
```

Tip: keep uploads `private` until you've eyeballed a dozen, then flip
`YOUTUBE_PRIVACY=public` (or publish private + schedule them in YT Studio).

---

## 🎤 You never record anything — the voice is 100% automatic

The Korean voice is AI text-to-speech, generated for you. There is no manual
recording, ever. On any machine with normal internet, `edge-tts` produces
**natural neural Korean voices automatically** (free, no key). The only time
you hear a robotic voice is in a locked-down environment with no network — then
the code auto-falls back to offline `espeak` so it's still audible.

### Cloud automation (natural voice, zero local setup)

Don't want to install anything? Run it in the cloud, where the internet is open
so the natural voice "just works":

- **GitHub Actions** — included at `.github/workflows/shorts.yml`. Push this
  repo to GitHub, open the **Actions** tab → *Make Korean Shorts* → **Run
  workflow** (pick count / pair / format). It builds the videos with the
  natural edge-tts voice and you download them as an artifact. Uncomment the
  `schedule:` block to auto-produce daily — literally "while you sleep".
  - Optional secret `GEMINI_API_KEY` → unlimited fresh scripts (else seed library).
  - Optional secret `AZURE_SPEECH_KEY`/`GOOGLE_TTS_API_KEY` → guarantees the
    natural voice even if Microsoft rate-limits the runner.
- **Google Colab / any VPS / your laptop** — `pip install -r requirements.txt`,
  `npm install`, then `python -m factory batch ...`. Natural voice, automatic.

## Customize

- **Look:** colors / fonts / pacing / dim level in `config.yaml`.
- **Stories:** add your own to `scripts/seed_scripts.json` (same schema the
  model emits), or steer the model with `--topic`.
- **Voices:** override any role via `VOICE_<PROVIDER>_<ROLE>` env (see `.env.example`).
- **Better avatars:** set `avatar_provider: files` and drop nicer PNGs named
  `<role>.png` (e.g. AI-illustrated Pixar-style characters) into
  `assets/avatars/` — they'll be used automatically. Transparent background,
  ~400×480, head-and-shoulders.
- **Music:** set `MUSIC_PATH` to a royalty-free bed; it's ducked under voices.

---

## Why "original" (read this before you ship)

The classic mistake with this genre is re-uploading other people's clips. That
gets your channel **demonetized or terminated** for reused content, and your
"passive" channel dies in its sleep. This factory sidesteps that entirely:
every script, voice, and avatar is generated, so the videos are **yours**.

Keep scripts genuinely original (the model is told never to quote copyrighted
material). Use royalty-free music only. Then the channel can run forever.

---

## Roadmap / upgrade paths

- **Format B (rich 3D scene):** swap flat avatars for AI-generated Pixar-style
  characters in a room (the split-screen style) — wire an image-gen provider in
  `avatars.py` and a second `frame.py` layout.
- **Word-level captions:** set `USE_WHISPER=1` to time each word from the real
  audio for karaoke-style highlighting.
- **More platforms:** add TikTok / Reels uploaders under `publish/`.
- **A/B titles & thumbnails**, trend-aware topic seeding, multi-channel.

---

*Built to be run unattended. Make it cute, keep it original, let it run.* 🌙

# THINKR MD — Brand Kit (for social: Instagram / Facebook reels, carousels, ads)

**Red override (Nov 2026):** the brand red is a true red, not the orange-red in the original color sheet / logo file (#F0361C / #EC3013). Social uses **#E31B23**.

## Identity
- **Brand name:** THINKR MD · wordmark "THINKR" with the **R in THINKR Red**
- **Instagram handle:** @thinkrmd
- **Logo mark:** square spiral, entirely ink (Ink on light / Mist on dark); only the "head" square is red (geometry in `scripts/base_light.py` → `mark()`)
- **Tagline:** "Get your edge back. Keep it for life." / "Normal isn't the goal. Your best is."
- **Angle:** science-first prevention for brain & body; evidence you can see; against bro-science and overpromising

## Fonts
- **Figtree** — headlines (ExtraBold), wordmark (Black), body (Medium)
- **JetBrains Mono** — labels, numbers, data callouts (ALL CAPS)
- **Instrument Serif** (italic) — emotional accent line (e.g., "but not proven.", tagline)
- Instrument Serif lacks symbols like ≠ — use words

## Colors — videos use a WHITE / GREY (light) background
| Role | Name | Hex |
|---|---|---|
| Background | Paper | #faf9f7 |
| Cards / panels | Linen | #f3f2ef (or White #ffffff) |
| Lines / inactive | Stone | #d9d8d3 |
| Main text, logo mark | Ink | #111215 |
| Secondary text | Slate | #5d6068 |
| Buttons, logo R & head | THINKR Red | #E31B23 |
| Red text on light | Red Deep | #B5121B |
| Meters & checks ONLY (data shapes, not small text) | Lime | #8fb800 |

Dark set (Night #0c0d10, Night 2 #15171c, Graphite #2a2d35, Mist #eceef2, Steel #9aa0ab) is for accent sections only.

**Rules:** red = action (CTAs, logo); lime = data only — never small text on light. Label style = small red square + mono Slate caps.

## Visuals — kie.ai
**Images:** Nano Banana Pro (`nano-banana-pro`), 9:16, 2K, png (~18 credits each), returns 1536×2752.
Prompt style suffix: "Clean minimal scientific editorial style, seamless off-white and pale grey background, soft diffused studio light, gentle shadows, white and light grey palette with true red (#E31B23) as the only accent color. Subject centered in the middle of the frame with generous empty background space in the top third and bottom quarter. Vertical 9:16. No text, no letters, no labels, no logos, no watermark."

**Motion:** Seedance 2 Fast (`bytedance/seedance-2-fast`), `{prompt, first_frame_url, generate_audio: false, resolution: "720p", aspect_ratio: "9:16", duration: 4–15}` → 720×1280 @ 24 fps.
Motion prompt suffix: "Keep the exact composition, lighting, colors and clean white-grey studio background of the image. Smooth, slow, subtle, premium motion. No text, no new objects, no camera cuts."
**Observed cost:** ~25 credits/s at 720p (42 s ≈ 1,040 credits ≈ $5.20).

**API:** `POST https://api.kie.ai/api/v1/jobs/createTask` (Bearer key) → poll `GET /api/v1/jobs/recordInfo?taskId=` → `resultJson.resultUrls`; balance `GET /api/v1/chat/credit`. Key in `~/kie/.env` as `KIE_API_KEY=…` (override path with `KIE_ENV_FILE`). Results host: `tempfile.aiquickdraw.com`.

## Reel template
- 1080×1920, 30 fps; text out of bottom ~380 px and top ~250 px
- Top-left spiral mark + wordmark; segmented progress bar (Stone track, Lime fill)
- Scene: mono label → Figtree headline → footage (center) → subtext; Paper gradients over top 700 px and 1300–1920 px
- End card (~3 s): spiral mark · THINKR wordmark · "MD · @thinkrmd" · red pill "Save · Share · Follow" · serif "Get your edge back."

## Voiceover
- ElevenLabs **George – Warm, Captivating Storyteller** (voice_id JBFqnCBsd6RMkjVDRZzb), model eleven_v4
- Spell acronyms phonetically ("B-P-C one fifty-seven", "V-E-G-F-R-2")

## Compliance
- Health posts end with "Educational only. Not medical advice." + key source
- No efficacy, dosing, or "FDA-approved" claims for unapproved compounds; state evidence level honestly (animal vs. human)

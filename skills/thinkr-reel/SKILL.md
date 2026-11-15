---
name: thinkr-reel
description: Make a THINKR MD (@thinkrmd) science-explainer Instagram/Facebook reel — research, script, ElevenLabs voice, kie.ai images + Seedance motion, branded text overlays, end card.
---

# THINKR MD science reel

End-to-end workflow for a ~30–45 s vertical (1080×1920) educational reel for THINKR MD. The topic comes from the user (a peptide, supplement, nutrient, health claim...).

Everything this skill needs is in this folder:
- `reference/brand-kit.md` — colors, fonts, logo, prompt styles, kie.ai settings + real costs, voice, compliance. **Read it first and follow it.**
- `scripts/base_light.py` — base renderer: palette, fonts, spiral logo + wordmark, progress bar, label chips, text helpers, end card `s_brand`.
- `scripts/render_photo.py` — scene definitions (`SCENES`) and per-scene footage placement (`PLAN`), shown for the BPC-157 reel. Rewrite both for each new topic.
- `scripts/render_video.py` — composites the text layer over Seedance clips `clip_<n>.mp4`.
- `scripts/kie.py` — kie.ai API client (reads `KIE_API_KEY` from `~/kie/.env`, or the file in `$KIE_ENV_FILE`).
- `scripts/setup_fonts.sh` — installs pycairo/fonttools and the brand fonts.

Work in a scratch directory: copy `scripts/*.py` there so imports resolve. Keep a task list: research → script → voice → images → motion → composite → check → deliver.

## 1. Research + script
- Search the web on the topic first: current regulatory status, mechanism, and **how strong the human evidence is**. Cite sources to the user.
- Science-first, honest tone: say what's animal/cell vs. human. No dosing, no efficacy claims, never "FDA-approved" for unapproved compounds.
- Script ≈ 75–95 words in 7–8 lines: hook question → what it is → "in the lab it does N things" → one line per mechanism → reality check (evidence level) → takeaway + "Follow for more science-first breakdowns."
- Spell acronyms phonetically in the voice script.
- If the user is present, show them the script before spending credits.

## 2. Voiceover (ElevenLabs)
- Generate with model `eleven_v4`, voice George `JBFqnCBsd6RMkjVDRZzb` unless told otherwise (≈500 credits per take).
- Get the MP3 into the working directory. If the sandbox can't reach `elevenlabsusercontent.com`, download it through a browser and copy it in.
- Find line breaks with `ffmpeg -i vo.mp3 -af silencedetect=noise=-38dB:d=0.18 -f null -`. Set scene boundaries just before each line starts and snap them to 30 fps frames. End card = +3.0 s. Save the durations as `durs.json`.

## 3. Scene images (kie.ai Nano Banana Pro)
- Check the balance with `python3 kie.py`. Never print the API key.
- Submit one `createTask` per content scene (not the end card): `{model: "nano-banana-pro", input: {prompt: <subject> + <style suffix>, aspect_ratio: "9:16", resolution: "2K", output_format: "png"}}`.
- Poll `recordInfo` until `success`; save the `resultUrls` (they're needed as `first_frame_url` in step 4).
- Download the images. `tempfile.aiquickdraw.com` may be blocked from the sandbox; if so, fetch them through a browser.
- Make a contact sheet and look at it before moving on.

## 4. Motion (kie.ai Seedance 2 Fast)
- **Tell the user the cost first:** ~25 credits per second at 720p.
- Submit one `createTask` per scene: `{model: "bytedance/seedance-2-fast", input: {prompt: <one line of motion> + <motion suffix>, first_frame_url: <image URL>, generate_audio: false, resolution: "720p", aspect_ratio: "9:16", duration: max(4, ceil(scene_len))}}`.
- For dense grids or detailed subjects, ask only for a gentle camera move.
- Download as `clip_<n>.mp4`. Check the **last** frame of each clip: push-ins can grow the subject into the headline zone. Fix this with that scene's `PLAN` entry `(clip, scale, dy)`.

## 5. Composite + assemble
- Run `bash setup_fonts.sh` once.
- Edit `SCENES` and `PLAN` in `render_photo.py` for the new topic. Reuse `headline_scene(label, headline, sub, sub2)` for most scenes.
- Preview stills: `python3 render_photo.py durs.json stills`, then look at them.
- Render each scene, in parallel if possible: `python3 render_video.py durs.json <i>` → `vscene_<i+1>.mp4`. The "Broken pipe" message from the clip reader is expected when a clip is longer than its scene.
- Concatenate with the concat demuxer and `-c copy`. Mux the voice with `loudnorm=I=-14:TP=-1.5`, a fade-out at the end, padding to full length and an explicit `-t <total>`.
- The last content scene carries "Educational only. Not medical advice." plus the key source. The end card is `s_brand`.

## 6. Check + deliver
- Pull frames at 3–4 timestamps across the finished video and view them. Fix any overlaps before delivering.
- Report the credits actually used (ElevenLabs + kie.ai) and the remaining kie.ai balance.
- Provide an Instagram caption: science-first, honest about the evidence level, a disclaimer line and 5–7 hashtags.
- Don't embed commercial songs. Suggest adding licensed audio in Instagram's Reels editor, or mix in a file the user supplies under the voice.
- If the brand changes (voice, colors, prompts, costs), update `reference/brand-kit.md`.

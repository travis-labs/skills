# skills
Claude Skills by travis-labs.

| Skill | What it does |
|---|---|
| [`thinkr-reel`](skills/thinkr-reel/SKILL.md) | Makes a THINKR MD (@thinkrmd) science-explainer Instagram/Facebook reel: research, script, ElevenLabs voice, kie.ai images + Seedance motion, branded overlays, end card. |

## Install
- **Claude Code (one project):** copy `skills/<name>/` to `.claude/skills/<name>/` in that repo.
- **Claude Code (all projects):** copy it to `~/.claude/skills/<name>/`.
- **claude.ai:** zip the `skills/<name>/` folder and upload it under Settings → Capabilities → Skills.

Secrets (e.g. the kie.ai API key) are never stored here; scripts read them from local files such as `~/kie/.env`.

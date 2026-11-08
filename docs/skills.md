# AI Agent Skills & Maintenance Guide

This project is built using **[HyperFrames](https://hyperframes.heygen.com)** — an open-source, code-driven framework for turning HTML, CSS, media, and seekable animations into deterministic MP4 videos.

It is designed to be maintained either directly by human developers or collaboratively with **AI Coding Agents** (Claude Code, Cursor, GitHub Copilot, Codex, Antigravity).

---

## 🤖 Supported Agent Skills

When using an AI coding agent with this repository, the agent can leverage four native HyperFrames skills:

| Skill | Purpose | When to Use |
| :--- | :--- | :--- |
| `/hyperframes` | Core Composition Contract | Read first for creating, modifying, timing, or inspecting scenes. |
| `/hyperframes-cli` | CLI Commands & Workflow | Guides previewing, checking, snapshotting, and rendering. |
| `/hyperframes-registry` | Component Library | Search and install ready-made visual blocks and UI elements. |
| `/media-use` | Media Pipeline & Sound | Audio mixing, volume ducking, voiceovers, and asset treatments. |

### Installing / Updating Skills
To install or refresh the core HyperFrames skills for your agent environment:
```bash
npx skills add heygen-com/hyperframes
```

---

## ⏱️ The Deterministic Audio-First Contract

This project adheres to HyperFrames' deterministic render contract:

1. **Audio as the Master Clock:**
   - Visual transitions, subtitle timings, and scene cuts are locked to `full_voiceover.wav` through `timing.json`.
   - Never rely on non-deterministic functions (`Date.now()`, `Math.random()`, or network `fetch()`).

2. **Every Scene is a Timed Clip:**
   - Top-level visual elements must have `class="clip"`, `data-start`, and `data-duration`.
   - Example:
     ```html
     <div id="scene-1" class="clip" data-start="0" data-duration="12.11" data-track-index="1">
       <!-- Visuals -->
     </div>
     ```

3. **Paused Root Timeline Registration:**
   - GSAP timelines must be registered on `window.__timelines`:
     ```js
     const tl = gsap.timeline({ paused: true });
     window.__timelines = window.__timelines || {};
     window.__timelines["main"] = tl;
     ```
   - Child timelines added to the root must not be paused so they seek predictably.

---

## 🎙️ Kokoro-ONNX Voice Pipeline

Voiceover audio is generated using **Kokoro-ONNX v1.0** with the `af_heart` voice:

* **Script:** `generate_voiceover.py`
* **Output:** `audio/full_voiceover.wav` + `audio/scene_{1..7}.wav` + `timing.json`
* **Models:** Auto-downloaded from GitHub Releases into `models/` on first run.

If you edit the script text in `generate_voiceover.py`, run:
```bash
npm run voiceover
```
This regenerates the audio files and updates `timing.json` with the exact duration and 30fps frame counts.

---

## 🔍 Validation & Quality Assurance Gate

Before pushing or rendering any change to HTML compositions, always run:
```bash
npm run check
```
This single command validates:
- **Lint:** HTML markup, data attributes, asset references.
- **Runtime:** Checks headless Chrome for JavaScript errors or failed network requests.
- **Layout & Motion:** Ensures every scene moves under seek.
- **Contrast:** Verifies WCAG AA accessibility compliance for mobile readability.
- **Craft:** Validates non-empty first frame (social media thumbnail friendliness) and readable font sizes.

To inspect rendered frames visually without rendering the full video:
```bash
npm run snapshot
```
Snapshot PNGs are saved to `.hyperframes/artifacts/snapshots/` and can be reviewed immediately.


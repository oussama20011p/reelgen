---
name: aiedit
description: Build a premium Arabic 9:16 short-form reel in HyperFrames from a single raw talking-head video named `rawreel.*`. Use when the user asks to edit, cut, caption, or "make a reel" from a rawreel file, wants Egyptian/Arabic word-timed captions with full-screen editorial motion-design interludes, or invokes /aiedit. Covers inspection, transcription, silence removal, semantic shot planning, warm paper editorial design, Arabic RTL typography, Studio preview approval, and final H.264/AAC render.
---

# aiedit — Arabic editorial reel builder (HyperFrames)

You are the senior Arabic short-form editor, motion designer, and HyperFrames
implementer for this task.

The project folder contains exactly one raw talking-head video whose filename
begins with `rawreel` (`rawreel.mp4`, `rawreel.mov`, …). There is no reference
video, no SRT, no storyboard, and no separate B-roll. Everything needed is
specified here or in `references/`. **Never ask the user to attach a reference
video or subtitle file.**

Inspect, transcribe, edit, design, animate, validate, preview, and render a
premium Arabic 9:16 reel. Do not return only recommendations, code snippets, a
storyboard, or an EDL — **build the complete working HyperFrames project.**
There is exactly one intended pause: the Studio-preview approval gate before
rendering.

## 1. Framework (non-negotiable)

HyperFrames is the source of truth for composition, source-range editing,
captions, graphic interludes, animation, audio, Studio preview, validation, and
rendering. Do not swap the project to a pure Remotion implementation; Remotion
is allowed only as a subordinate helper if the installed HyperFrames workflow
explicitly calls for it.

Read the installed skills in this order before building:

1. `/hyperframes`
2. `/general-video` — this job is a footage remix: silence removal, hard cuts,
   reframes, captions, full-screen editorial interludes
3. `/hyperframes-core`
4. `/hyperframes-creative`
5. `/hyperframes-animation`
6. `/hyperframes-keyframes`
7. `/hyperframes-studio`
8. `/media-use`
9. `/hyperframes-audio` — dialogue processing and any mixing
10. `/hyperframes-registry` — **before** hand-building any named texture, effect,
    or transition
11. `/hyperframes-cli`

Refresh the supported `general-video` workflow first. Build inside a new child
folder such as `hyperframes-reel-edit/`. **Never overwrite or modify the
original `rawreel` file.**

If the HyperFrames skills or CLI are not installed or cannot run, stop and
report that concrete blocker (see §7).

## 2. Inspect before designing

Locate the single `rawreel.*`, then:

1. `ffprobe` it and record duration, width/height, frame rate, video/audio
   codecs, audio sample rate, channel count.
2. Confirm it is a vertical talking-head reel. Preserve the native frame rate
   where practical; delivery canvas is 1080×1920, 9:16.
3. Generate contact sheets across the whole source at 1–2 fps to understand
   framing, gestures, facial movement, negative space, lighting, and viable
   crop positions.
4. Analyze the waveform and detect silence/breath intervals. Never cut from
   numeric silence detection alone — verify against speech and visible gesture.
5. Extract dialogue and produce a highly accurate Egyptian/Arabic transcript
   with word-level timestamps. Use the supported HyperFrames/media transcription
   workflow when available, otherwise a reliable local Whisper-compatible
   method.

Save these inspectable artifacts in the project:

| File | Contents |
| --- | --- |
| `transcript.json` | word-level tokens with `text`, `start`, `end` |
| `captions.srt` | corrected Arabic cue transcript |
| `source-analysis.md` | metadata, silence ranges, content summary, semantic beats |
| `timing-map.json` | every retained source range → new output start/end after silence removal |

Review the Arabic transcript manually against the audio. Correct model names,
English technical words, and Egyptian dialect errors. **Never animate or publish
an unverified hallucinated transcript.**

## 3. The editing style

The reel alternates between two worlds. Full detail — palette, fonts, captions,
motion vocabulary — is in `references/style-system.md`; read it before writing
any scene markup.

**World A — restrained talking head.** Presenter dominant, clean hard cuts, a
small number of motivated crop changes across three states (1.00× base, ~1.08×
emphasis, ~1.14–1.17× close). Change crop on a new claim, contrast, punchline,
or CTA — not every sentence. Animate an inner visual/crop wrapper, never the
timed `.clip` element. Keep eyes, chin, and active hands safe; derive x/y offsets
from the real footage rather than assuming a centered face. Natural color: no
oversharpened face, crushed blacks, or orange skin.

**World B — full-screen editorial interludes.** Not stock inserts: designed 9:16
scenes that replace the presenter for meaningful stretches. Warm tactile
paper/cream background, one strong monochrome symbolic object, large Arabic
kinetic typography with extreme but controlled hierarchy, one dominant keyword
plus smaller supporting context, progressive assembly synced to the spoken
phrase, and a clear entrance → build → readable hold → decisive exit/cut.

The central object must come from the actual transcript (automation → conveyor
or connected modules; thinking → decision tree; warning → fractured card or
redaction mark; result → rising route or publication card; steps → stacked
numbered modules; CTA → oversized keyword plus comment-bubble outline). Do not
reuse the same object in every scene. No robots, neon brains, circuit boards,
sci-fi HUDs, particle fields, or unrelated stock clips.

Build visuals in HTML/CSS/SVG whenever truthful. If a symbolic image or icon is
genuinely required, resolve or generate it through `/media-use`, freeze it
locally, and record provenance. **No render-time network requests.**

## 4. Plan the cut

Read `references/scene-planning.md` for the pacing targets, the required
narrative rhythm, the opening-hook treatment, the five beat types (hook, input,
list, payoff, CTA), and the silence-removal rules. Write the resulting
content-specific plan to `STORYBOARD.md`, quoting the exact verified transcript
phrases that drive each scene alongside post-trim output times.

Headline targets: ~45–55% talking head / ~45–55% graphic interlude; roughly 4–6
semantic scenes for a 20–35 s reel; interludes 1.8–2.5 s (short), 2.8–4.0 s
(normal), ≤ ~4.5 s (longest list/process). Content meaning decides every
boundary — never alternate on a fixed clock.

## 5. Implementation contract

- Delivery canvas 1080×1920, 9:16; H.264 + AAC MP4 as `final_reel.mp4`.
- Use the source's measured frame rate when suitable; otherwise 30000/1001 fps,
  and report the conversion.
- Readable Studio tracks: A-roll picture, dialogue audio, graphic scenes,
  captions, optional SFX. A sub-composition per major graphic scene.
- `class="clip"` with the supported `data-*` timing attributes. Source editing
  uses `data-media-start` (source offset), `data-duration` (retained source
  length), `data-start` (authored output placement). If audio is separated, its
  ranges and placements must match the picture edits exactly.
- Synchronous, paused, registered, seek-safe timelines. No autoplay-dependent
  critical motion.
- No `Date.now()`, `performance.now()`, unseeded `Math.random()`, infinite
  loops, or timer-driven render-critical animation. No render-time network.
- Never animate `display`, `visibility`, or `autoAlpha` on a `.clip` — animate a
  child wrapper.
- IDs unique across the assembled document.
- Social safe zones: essential text within ~x=80–1000 and y=140–1650, CTA
  comfortably above the bottom platform controls.
- Audio: original dialogue is authoritative; conservative cleanup only;
  normalize near −14 LUFS integrated with peaks ≤ −1 dBTP and no pumping. Do not
  add a music track that was not supplied — voice-only beats unlicensed music.
  Subtle locally resolved SFX are allowed only for meaningful actions (graphic
  cut, path completion, UI click, CTA lockup), well under the dialogue.

## 6. Verification and the single approval gate

Work the full checklist in `references/qa-checklist.md`. In short:

1. Produce `BRIEF.md`, `source-analysis.md`, the verified transcript artifacts,
   `STORYBOARD.md`, and `timing-map.json`.
2. Build the complete project — do not stop after planning.
3. Search the HyperFrames catalog before hand-building any named effect.
4. `hyperframes lint` after the first structural pass and after major timing
   changes.
5. Final `hyperframes check` gate; resolve every lint, runtime, layout, font,
   motion, and contrast error.
6. Keyframe diagnostics on the opening push, every punch-in/reframe, every
   visual handoff.
7. Snapshot inspection at all the boundaries listed in the checklist.
8. Review the multi-scene animation map.
9. Confirm no black flashes, missing-font frames, broken Arabic shaping, clipped
   captions, sub-composition mount flashes, lingering B-roll, reset tails, or
   A/V desync.
10. **Open the final HyperFrames Studio preview and give the user the preview URL
    for approval. This is the only intended pause.**
11. After approval, render delivery quality to `final_reel.mp4`.
12. Verify with `ffprobe`: 1080×1920, expected fps, H.264, AAC, nonzero size,
    duration matching the root composition.

Then deliver the project folder, `final_reel.mp4`, `captions.srt`,
`transcript.json`, `timing-map.json`, and the concise report described in the
checklist.

## 7. Blockers you must not hide

Stop and report a concrete blocker instead of pretending success when:

- no `rawreel.*` exists, or several ambiguous candidates do;
- the video or audio cannot be decoded;
- Arabic transcription stays materially uncertain after review;
- no installed system font renders Arabic legibly with correct shaping, or the
  shaping/font loading is wrong;
- the HyperFrames skills or CLI cannot run;
- a required factual visual cannot be created without inventing evidence;
- `hyperframes check` still reports an unresolved error.

The bar is a premium editorial reel, not a subtitle template: immediate
talking-head hook, fast opening push, small word-timed captions, decisive
full-screen editorial interludes, warm tactile paper, symbolic monochrome
visuals, high-contrast Arabic hierarchy, restrained warm/cool accents, hard
cuts, clean audio, confident final CTA. This is a personal, unbranded treatment
— no organization name, logo, website, watermark, or invented brand identity.

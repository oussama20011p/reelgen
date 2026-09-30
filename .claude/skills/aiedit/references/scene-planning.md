# Scene planning — pacing, beats, hook, silence removal

## Ratio and duration

- ~45–55% talking-head footage, ~45–55% full-screen editorial interludes.
- Adapt to the transcript. Do not force B-roll over an emotional or
  credibility-critical statement that benefits from seeing the presenter.
- Interlude duration: short 1.8–2.5 s; normal 2.8–4.0 s; longest list/process
  scene ≤ ~4.5 s unless the speech genuinely requires more.
- Roughly 4–6 semantic scenes for a 20–35 s reel. Group adjacent speech into
  purposeful beats — never one scene per sentence or subtitle line.

## Required narrative rhythm

1. Open on the presenter for ~0.7–1.2 s.
2. Hard-cut on the hook's proof/claim into the first full-screen interlude.
3. Return to the presenter for context or credibility.
4. Second interlude for the mechanism, input, process, or contrast.
5. Longest graphic scene for a list, transformation, or sequence of benefits.
6. Return to the presenter for the payoff/result.
7. Keep the presenter visible through the CTA setup, then optionally cut to a
   final designed CTA card on the spoken keyword.

Never alternate mechanically every N seconds — content meaning sets boundaries.

## Opening hook

The first second must feel deliberately edited.

- Start on the presenter.
- Fast elegant push-in from base crop to ~1.10–1.13× over 0.55–0.85 s with a
  strong ease-out.
- Do not bounce or snap back to 1.00×.
- Introduce the first small word-timed caption during the push.
- First full-screen graphic cut lands on the strongest claim or named
  tool/result in the hook, normally within the first 1.0–2.0 s.
- Never open on a logo, black frame, empty background, generic title card, or
  slow fade.

## Beat types

After transcription, divide the narration into semantic beats and build a
custom plan from the actual words.

**A — Hook or surprising claim.** Begin on the presenter; move to a graphic
scene when the key claim/tool/result is spoken. One oversized keyword, one short
supporting phrase, one symbolic object.

**B — Input / "what I did".** Presenter for the personal statement; graphic
process when inputs are named. Layout: source frame/card + prompt/document +
arrow/path → output.

**C — List of features or actions.** The longest editorial interlude. Build 3–5
modules one at a time. The active module is oversized and warm-accented;
completed modules settle to ink, cream, or the cool accent. Must not look like a
generic SaaS dashboard.

**D — Payoff / finished result.** Return to the presenter for credibility.
Medium crop or subtle punch-out for resolution. Highlight the result phrase
across one or two caption states.

**E — CTA.** Presenter visible through the setup. On the spoken CTA keyword,
either a motivated punch-in or a hard cut to the final graphic card: oversized
keyword, one minimal relevant outline icon, one short Arabic instruction. Hold
the completed card 12–18 frames after the final spoken word. Never end on black.

Write the content-specific plan into `STORYBOARD.md`, quoting the exact verified
transcript phrases driving each scene and including post-trim output times.

## Silence removal and source editing

Use waveform, transcript, and visible mouth/gesture motion together.

- Remove leading and trailing dead air.
- For internal silence longer than ~220–280 ms, consider trimming while keeping
  2–4 frames of natural room.
- Do not delete every breath or micro-pause.
- Never cut inside a spoken syllable.
- Do not cut off a hand movement that visually completes a sentence.
- Hard cuts between retained source ranges; audio/video sync exact.
- Keep dialogue uninterrupted under full-screen editorial scenes.

Implement through separate HyperFrames media elements using `data-media-start`,
`data-duration`, and `data-start`. Separated audio must match picture ranges
exactly.

## B-roll without supplied B-roll

Do not stop because no B-roll files were supplied. Create replacements from:
HTML/CSS/SVG editorial compositions; simple local icons/illustrations via
`/media-use`; locally extracted stills or crop details from `rawreel`; generic
truthful UI metaphors derived from the narration; locally generated symbolic
media only where it materially improves the scene.

Do not download copyrighted social clips, scrape random images, fabricate real
product screenshots/metrics/customer results, use frames from a nonexistent
reference video, or depend on network media during preview or rendering.

If a specific factual visual cannot be made truthfully without an unavailable
asset, use a clear abstract diagram or typography treatment instead of inventing
evidence.

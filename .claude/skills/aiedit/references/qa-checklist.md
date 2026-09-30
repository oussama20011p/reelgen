# QA checklist, approval gate, delivery report

## Validation sequence

1. Produce `BRIEF.md`, `source-analysis.md`, verified transcript artifacts,
   `STORYBOARD.md`, `timing-map.json`.
2. Build the complete project — never stop after planning.
3. Search the HyperFrames catalog (`/hyperframes-registry`) before hand-building
   any named effect or transition.
4. Run `hyperframes lint` after the first structural pass and again after major
   timing changes.
5. Run the final `hyperframes check` gate; resolve every lint, runtime, layout,
   font, motion, and contrast error.
6. Run keyframe diagnostics for the opening push, every punch-in/reframe, and
   every visual handoff.

## Snapshots to inspect

- exact first frame
- 25%, 50%, 75%, 100% of the opening push-in
- every hard-cut boundary ±1 frame
- midpoint and completed state of every full-screen interlude
- every list/module state
- CTA final hold
- final-minus-hold and the exact final frame

Then review the multi-scene animation map.

## Defects that block approval

- black flashes
- missing-font frames
- broken Arabic shaping
- clipped captions
- sub-composition mount flashes
- lingering B-roll
- reset tails (animations returning to their initial state at the end)
- output/audio desynchronization

## Approval gate

Open the final HyperFrames Studio preview and give the user the preview URL.
**This is the only intended pause.** Do not render before approval.

## Render and verify

After approval, render delivery quality to `final_reel.mp4`, then `ffprobe` it
and confirm: 1080×1920, expected fps, H.264 video, AAC audio, nonzero size, and
duration matching the root composition.

## Delivery

- the complete HyperFrames project folder
- `final_reel.mp4`
- `captions.srt`
- `transcript.json`
- `timing-map.json`
- a concise report listing:
  - original and final duration
  - removed source ranges
  - number of semantic scenes
  - actual A-roll / graphic ratio
  - exact fonts and weights used
  - registry / media dependencies used
  - validation status

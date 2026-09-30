# Style system — color, type, captions, motion

## Color

Personal, unbranded editorial treatment. Warm palette below is a flexible
starting point; small adjustments to harmonize with the footage are fine, but
preserve the functional hierarchy.

```css
--paper: #E9E0D3;
--paper-dark: #D4C8B8;
--paper-light: #F6F0E7;
--cream: #FFFDF7;
--ink: #1B1D1E;
--ink-soft: #3A3D3E;
--accent-warm: #E66A21;
--accent-warm-dark: #C85218;
--accent-cool: #2A8791;
--accent-cool-dark: #216A72;
--accent-gold: #D8A44A;
```

- Paper / cream / ink are the dominant visual world.
- Burnt orange is the main emphasis color.
- Muted teal is a less frequent secondary accent.
- Muted gold is a rare micro-accent, never the theme.
- Avoid neon-purple "AI" visuals, rainbow palettes, heavy glassmorphism, glossy
  corporate templates.
- Subtle paper grain is allowed only if resolved locally through `/media-use` or
  a suitable registry primitive.

## Fonts

No font files are supplied. Discover a good Arabic family already installed.
Preferred candidates in order of availability and visual suitability:

1. `Cairo`
2. `Tajawal`
3. `Noto Kufi Arabic`
4. `Noto Sans Arabic`
5. `IBM Plex Sans Arabic`
6. `Segoe UI`
7. `Arial`

Never assume a font is installed because its name appears above. Test with
`document.fonts.check()` or the OS font inventory, pick the first strong Arabic
display family genuinely available, and record the selected family in the
delivery report.

- Real heavy/bold weight for display headlines when available.
- Bold or semibold for captions and supporting headings.
- Medium/regular for smaller explanatory copy.
- Do not synthesize a weight that renders poorly.
- CSS fallback stack starts with the verified selected family, then other
  verified Arabic-capable system fonts.
- Keep rendering local and deterministic — no web fonts at render time.
- Confirm the font loads and renders joined Arabic correctly in the actual
  HyperFrames preview before approval.

## Arabic RTL shaping

**Never put `dir="rtl"` on `<html>`.** `hyperframes lint` flags this as
`html_dir_attribute_breaks_render`: it looks correct in preview and snapshots
but renders a fully blank/black video — a silent failure. Keep `lang="ar"` on
`<html>` and scope `direction: rtl` (or `dir="rtl"`) to the individual
text-containing elements. Arabic still shapes correctly through the browser's
own bidi algorithm.

- `direction: rtl` on text elements only, never on `<html>`.
- Whole-word spans.
- Correct Unicode shaping and punctuation.
- Natural Arabic line breaks.
- No individual-letter splitting or animation.
- Animate complete shaped words or lines only.

## Declaring the fonts to the renderer

An installed system font is not enough. `hyperframes lint` raises
`font_family_without_font_face` for any family used without an `@font-face`
declaration, and the renderer silently falls back to a generic font. For an
OS-installed family with no downloadable file, declare it with `src: local(...)`
— the declaration alone satisfies the check:

```css
@font-face { font-family: 'Cairo';            src: local('Cairo'); }
@font-face { font-family: 'Tajawal';          src: local('Tajawal'); }
@font-face { font-family: 'Noto Kufi Arabic'; src: local('Noto Kufi Arabic'); }
@font-face { font-family: 'Noto Sans Arabic'; src: local('Noto Sans Arabic'); }
```

Declare only families you verified are actually installed, in the same order as
the CSS fallback stack.

## Captions

Never display large full-sentence subtitle blocks copied from the transcript.

### On talking-head sections

- Word timing derived from the verified `transcript.json`.
- 1–4 words on screen at a time.
- Positioned around 64–70% of frame height — over the torso, above platform UI.
- Selected system Arabic font, bold or semibold, compact line height, **no
  opaque background pill**.
- Default color cream `#FFFDF8`; context/prior words may drop to 45–60% opacity.
- Highlight only one genuinely important word with the warm accent; the cool
  accent more rarely still.
- Animate with a 2–4 frame opacity/vertical settle, or a clean hard replacement.
- No bouncing karaoke, per-letter wobble, overshoot on every word, or captions
  over the face.

### On full-screen graphic interludes

- No second conventional subtitle layer.
- The spoken phrase becomes the designed typography of the scene.
- Reveal semantic chunks at the exact spoken moment.
- Preserve every important factual claim; invent no new facts.

## Motion language

Energy comes from hierarchy changes, progressive assembly, and decisive cuts —
not nonstop movement. Use 2–4 intentional motion rules per graphic scene, drawn
from: masked line/word rise; short staggered assembly; scale settle; path or
connector draw; small object rotation/pose change; restrained camera drift;
semantic shared-element handoff.

Timing at the measured project frame rate:

- entrance: ~6–12 frames
- small stagger gap: 2–5 frames
- readable proof/hold: ~10–20 frames
- hard cuts preferred over decorative dissolves

One focal object and one dominant phrase at a time.

Avoid: continuous random motion; glitch (unless the transcript specifically
justifies disruption/error); liquid morphs; chrome 3D text; excessive parallax;
fake depth from scaling alone; spinning logos; particle fields; transition-pack
variety; ending animations that reset to their initial state.

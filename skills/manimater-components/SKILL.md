---
name: manimater-components
description: Use the Manimater open-source Manim component library (manimater-components). Use when the user wants to animate or explain a concept with Manim, build or validate a storyboard JSON from reusable components, look up which of the 90+ components (electrical, power, signals, microelectronics, machine learning, computer science, finance, physics, chemistry, databases) fits a topic, preview a component, or write and contribute a new component to the library. Also use when someone who does not code wants to describe an animation and get a component to contribute.
---

# manimater-components

A library of tested Manim components driven by JSON. A **component** is a name plus parameters; it never needs animation
code from you. Repository: https://github.com/bishnt/manimater-components (MIT). The Manimater app uses the same library.

Two things you may be asked to do:

1. **Use** components: pick the right ones for a topic, write a valid storyboard, preview it.
2. **Add** a component: write one that follows the rules, test it, and get it contributed.

Figure out which one the user wants. If they describe an animation that no existing component can do, go to "Add a component".

## 1. Use components

### Find the right component

1. Read [references/catalog.md](references/catalog.md): every component with a one-line description and its parameters.
   (If you are inside a clone of the repo, `catalog.json` at the root has full parameter details and an `example` for each.)
2. Pick the component whose description matches the *idea* to show, not just the topic. Prefer one specific component
   over a generic one (`synchronous_motor` over `bullet_points` for a motor explanation), and combine a few for a story:
   `title_card`, then the concept components, then `callout` as the final takeaway.
3. Read the chosen component's entry in `catalog.json` for its exact parameter names, types, `choices` and `example`.

### Write a storyboard

A storyboard is JSON; the library checks it for you:

```json
{ "title": "How a synchronous motor works",
  "scenes": [
    { "component": "title_card", "params": { "title": "Synchronous motors" }, "narration": "Why does this motor never slip?" },
    { "component": "synchronous_motor", "params": { "poles": 2, "frequency_hz": 50 }, "narration": "The rotor locks onto the rotating field." },
    { "component": "callout", "params": { "text": "Speed is fixed by frequency and pole count.", "kind": "takeaway" }, "narration": "So speed depends only on frequency." }
  ] }
```

Rules the validator enforces: at most 12 scenes, strings up to 300 characters, lists up to 8 items, unknown parameters are
dropped, required parameters must be present, `choices` must match. **Never invent a component name or a parameter**;
if one is missing, say so and offer to write a new component.

### Validate and preview

```bash
pip install -e ".[dev]"                       # in a clone; needs ffmpeg, Cairo and Pango for Manim
python - <<'PY'
import json
from manimate.storyboard import validate
sb, errors = validate(json.load(open("storyboard.json")))
print(errors or "valid")
PY
python -m manimate.preview <component>                        # renders previews/<component>.mp4 from its example
python -m manimate.preview <component> --params '{"...": 1}'  # with your own parameters
python -m manimate.preview --list
```

If you cannot run code in this environment, produce the storyboard JSON and the exact commands, and say plainly that you
have not validated or rendered it.

## 2. Add a component

Read [references/component-template.py](references/component-template.py) first. It is a complete, working component.

### Decide

- **One idea, reusable.** "How a transformer works" is a whole video; "attention weights between two words" is a component.
  Parameters (numbers, labels, lists) should make it useful for many examples.
- Check [references/catalog.md](references/catalog.md) so you do not duplicate an existing component.
- Ask the user for anything you cannot decide yourself (who it is for, what should be adjustable) but no more than two
  questions; otherwise make sensible choices and state them.

### Write it

Save as `manimate/components/community/<name>.py` (snake_case, unique). It is registered automatically. Follow the template
exactly, and these rules:

1. At most 5 parameters, each with a description (an AI reads it), a default or `required=True`, and a `validator` that
   returns a plain-English message for bad input. Clamp, trim, fall back; never crash on odd input.
2. The `example` dict must be valid and must render.
3. Maths, algorithms and layout are **plain Python functions without Manim**, so they can be unit-tested.
4. Only `manimate.theme` colours (`theme.ACCENT`, ...), never hex. Short, plain on-screen text. `ctx.fit(...)` so nothing
   leaves the stage.
5. Fade the finished picture in as a whole with one `FadeIn`, then animate what carries the meaning. Use the time you are
   given (`ctx.remaining`, `Ctx.beat`). Use `ctx.play` / `ctx.wait`, never `scene.play`.
6. Pure drawing code: no network, files, subprocesses, `eval`, `exec`, `getattr`, or dunder access. Imports are limited to
   `manim`, `numpy`, the standard library and the library's own modules. CI and a bot reject anything else.
7. Wrapping a Manim plugin is allowed only if it is MIT or Creative Commons licensed; follow `docs/WRITING_A_COMPONENT.md`.

Write a test for the plain-Python logic in `tests/community/test_<name>.py` (edge cases: empty, one item, the maximum, long
labels). The generic test already dry-runs every community component's example.

### Check it

```bash
python -m manimate.preview <name>
python -m pytest tests/community
python -m manimate.catalog > catalog.json
python scripts/gen_docs.py
```

Report what you ran and what happened. If you could not run anything, say so.

### Contribute it

Tell the user, in plain words, which path fits them:

- **They can use git/GitHub:** fork the repo, create a branch named `component/<name>` (a new component always goes on
  its own such branch, one component per pull request), commit the component, its test and the regenerated
  `catalog.json` and docs, and open a pull request titled `feat(community): add <name>`. See `CONTRIBUTING.md` (the rules
  CI enforces, the checklist and the five design questions to answer in the description).
- **They do not code (most people):** give them the Python file in one code block (and the test in a second), and tell
  them to open the **New component (from an LLM)** issue form at
  https://github.com/bishnt/manimater-components/issues/new?template=new-component.yml and paste the code in. A bot checks
  it without running it and opens the pull request for them, credited to them; a maintainer reviews it.

End with a three-line summary the user can paste into the form: what it teaches, the parameters, and the failure cases you
handled.

## Boundaries

- Do not claim a component exists unless it is in the catalog. Do not claim a render looks right unless you rendered it.
- Do not copy code from other repositories into a contribution unless it is MIT or compatible and you say where it is from.
  manim-eng's source, docs and examples must not be used as AI training data (see `docs/THIRD_PARTY.md`).

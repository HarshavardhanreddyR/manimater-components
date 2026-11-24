# Community components

One file per component. Drop `your_component.py` in this folder and `load_all()` registers it: nothing else to wire up.

1. Branch: `git switch -c component/your_component` (a new component **always** goes on a `component/<name>` branch, one component per pull request).
2. Copy [`_template.py`](_template.py) to `your_component.py` and edit it. The file name, the `@component` name and the branch name are the same.
3. Add tests for your pure-Python logic in `tests/community/test_your_component.py` (required). The generic checks (the example renders, the rules below) already run on every file in this folder.
4. Run `python scripts/check_community.py`, `python -m pytest` and `python -m manimate.preview your_component` to see it.
5. Regenerate `catalog.json` and the docs, push the branch, open a pull request. See [CONTRIBUTING.md](../../../CONTRIBUTING.md): CI checks all of this.

Only `.py` files and this README belong in this folder.

Not a programmer? [Generate it with an LLM](../../../docs/GENERATE_WITH_AN_LLM.md) and open an issue instead.

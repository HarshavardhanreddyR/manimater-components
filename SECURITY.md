# Security

Components are pure drawing code and are run by services that render videos for other people, so security matters here.

- Components must not read files, use the network, spawn processes, or use `eval`/`exec`. CI enforces the obvious cases
  for everything in `manimate/components/community/`, and maintainers review every pull request.
- Parameters are validated against the catalog before a component runs; keep validators strict.
- The static check also blocks reading or writing files through the allowed libraries (for example `numpy.load`, `ImageMobject`,
  `SVGMobject`, Manim's `config`), and CI runs contributed code only with a read-only token and no secrets.

## Known limits

The static check reads Python, not the strings inside it. A LaTeX string passed to `Tex`/`MathTex` is compiled by LaTeX, which can
read files with `\input` unless it is told not to. A service that renders other people's components should compile LaTeX with
shell escape disabled and paranoid file access (`openin_any=p`, `openout_any=p`), run renders in a container with no network and a
read-only file system, and apply time and memory limits. A maintainer still reads every contribution.

To report a vulnerability, please do **not** open a public issue. Use GitHub's
[private vulnerability reporting](https://github.com/bishnt/manimater-components/security/advisories/new) for this repository.

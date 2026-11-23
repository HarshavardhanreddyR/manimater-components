# Maintaining the repository

How the checks fit together, what to switch on in GitHub, and how to handle each kind of pull request.

## The checks

| Workflow / job | Trigger | Runs contributor code? | Purpose |
|---|---|---|---|
| `CI` → **Static checks** | pull request, push to `main`, weekly | no (reads source only) | `scripts/check_community.py`, lint, compile |
| `CI` → **Workflow lint** | same | no | actionlint, every action pinned to a SHA |
| `CI` → **Tests** (3.11, 3.12) | same | yes, read-only token, no secrets | pytest, dry run of every component, generated files up to date |
| `CI` → **Render new and changed components** | pull request | yes, same limits | real video per added/changed component, uploaded as an artifact |
| `CI` → **Package builds and installs** | same | no | wheel builds and imports from a clean environment |
| `CI` → **Slow renders** | `main`, weekly | trusted code only | real renders of the `slow` tests |
| `CI` → **CI passed** | always | no | the one summary check to require |
| **PR policy** | `pull_request_target` | **never** (metadata and `git diff` only) | branch name, title, description, one component per PR, file hygiene |
| **Regenerate catalog** | manual | the branch's code (read it first) | regenerates `catalog.json` and docs on a contribution branch |
| **Component from issue** | issue labelled `component-submission` | never (static parse only) | turns an LLM submission into a `component/` pull request |

`PR policy` uses `pull_request_target` deliberately: the rules come from `main`, so a pull request cannot weaken them by
editing the script. Never add a step to that workflow that checks out, installs, imports or runs the pull request's code.

## Switch on the gate (one time, repository admin)

The checks only protect `main` once they are *required*. The ruleset in [`.github/rulesets/main.json`](../.github/rulesets/main.json)
requires pull requests, one approving review from a code owner, squash merges, linear history, and the two checks **CI passed**
and **PR policy**, with the branch up to date before merging. The up-to-date rule matters here: two component pull
requests both edit `catalog.json`, so each can be green alone and still break `main` once both merge.

```bash
gh api repos/Manimater/manimater-components/rulesets --method POST --input .github/rulesets/main.json
```

Check the existing "ruleset" (it only blocks deletion and force-push) afterwards and remove duplicates. The bypass in the
file lets repository admins merge their own pull requests (`bypass_mode: pull_request`), so a solo maintainer is not
locked out while others still need a review. Remove it once there are two maintainers.

Also recommended under **Settings**:

- Actions → General → *Fork pull request workflows*: require approval for **all outside collaborators** (not only first-time contributors).
- Actions → General → *Workflow permissions*: read-only by default (already so). Do not allow Actions to approve pull requests.
- General → Pull Requests: allow squash merging only, and *Automatically delete head branches*.
- Code security: turn on Dependabot alerts and secret scanning with push protection.

## Handling pull requests

- **A contributor's component** (`component/<name>`, from a fork): wait for **CI passed** and **PR policy**, watch the video from the
  `component-previews` artifact of the *Render* job, read `manimate/components/community/<name>.py`, check the five design questions.
- **From the issue bot** (`component/issue-<n>-<name>`): read the code first (it has only been checked statically), run
  **Regenerate catalog** on the branch, then **close and reopen the pull request** so CI and PR policy run on the final commit
  (bot-created pull requests and bot pushes do not trigger them).
- **Dependabot**: grouped weekly; action updates change the pinned SHA and the version comment together.
- **A rule that is wrong for one pull request**: add the `policy-override` label (maintainers only) and say why in a comment.
  The label waives the PR policy only. It does not waive CI.

## Secrets

Do not paste a personal access token into an issue, a pull request, a chat, or a commit. If one has been shared, revoke it at
https://github.com/settings/tokens and create a new one with the least access needed (fine-grained, this repository only).

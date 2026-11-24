# Keeping the app in sync

[Manimater](https://github.com/bishnt/manimater) renders videos with this library. In the app this repository's root is the
`renderer/` folder (`manimate/`, `examples/`, `tests/` sit one level down).

## Library to app (automatic)

When a pull request is merged into `main` here, the **Sync to app** workflow copies exactly the files that change touched
into a branch of the app and opens a pull request there (`sync/components-<sha>`). It adds, updates and deletes those files
and nothing else, so app-only files next to them are never touched. A maintainer reviews and merges that pull request in the app.

Which paths are synced is the list in [`.github/sync-paths.txt`](../.github/sync-paths.txt) (default: `manimate/`, `examples/`,
`tests/`). Edit it to change what is proposed; a change to the list is reviewed like any other change to `.github/`.
**Do not move or rename synced files casually**: the app has its own copy at the same relative path.

### One-time setup (repository admin)

The workflow does nothing until it can write to the app, so it is safe to merge before this is done.

1. Create a **fine-grained personal access token** (or a GitHub App) that can reach **only the app repository**, with
   *Contents: read and write* and *Pull requests: read and write*.
2. Add it here as the Actions secret **`APP_REPO_TOKEN`** (Settings → Secrets and variables → Actions).
3. If the app repository is not `bishnt/manimater`, add the Actions variable **`APP_REPO`** (for example `Manimater/manimater`).

Never paste the token into an issue, a pull request or a chat. Use **Run workflow** on *Sync to app* to retry after setup.

## App to library (manual)

A component change made in the app is **not** mirrored automatically from here. Open a pull request in this repository with the
same change (for a new component, from a `component/<n>` branch, as in [CONTRIBUTING.md](../CONTRIBUTING.md)), so the two stay
identical.

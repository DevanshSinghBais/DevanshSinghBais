# Profile README maintenance

## Editing profile content

The profile README lives at the root of the `DevanshSinghBais/DevanshSinghBais` repository. Keep project descriptions tied to each project's own README or implementation. Label exploratory tools separately from technologies used in code, and remove or qualify any claim that can no longer be supported. Use `README.md` for the public summary and `PROFILE_IMPLEMENTATION_CHECKLIST.md` to record verification state.

The hero is `assets/terminal-hero.svg`. Keep its colors aligned with the profile palette: `#0D1117`, `#161B22`, `#39FF88`, `#00D9A6`, `#F0F6FC`, `#8B949E`, and `#30363D`. Avoid adding page-level CSS or scripts; GitHub renders Markdown, a limited set of HTML, and SVG images.

Run the dependency-free local checks from the repository root:

```sh
python scripts/validate_profile.py
```

The validation workflow runs the same script on pushes to `main` and `profile-redesign`, pull requests targeting `main`, and manual dispatches. It checks local README references, requested stack coverage, SVG XML, the 120 checklist entries, and workflow conventions. It does not make network requests to third-party services.

## Contribution snake

`.github/workflows/snake.yml` uses Platane/snk to generate light and dark SVG files in `dist/`, then publishes them to the dedicated `output` branch. It runs on pushes to `main`, once daily, or by manual dispatch from `main`. The generated files are not committed to the README branch. A successful first run creates the `output` branch.

For this to publish, repository Actions settings must allow workflows to run and the repository `GITHUB_TOKEN` must have **read and write** repository permissions. The workflow itself requests only `contents: write`. If the snake image is missing, check the latest **Generate contribution snake** run, confirm it ran from `main`, then check the Actions permissions and whether branch rules prevent the `output` branch update. Re-run it from `main` after correcting settings.

## Open-source contribution feed

`.github/workflows/update-open-source.yml` searches GitHub for up to five recent public pull requests authored by `DevanshSinghBais`, excluding this profile repository. It replaces the content between the single `OSS_START` and `OSS_END` markers in the README and commits only when the content changes. It runs daily or by manual dispatch from `main`.

The workflow uses the repository's built-in `GITHUB_TOKEN`; no personal token or committed secret is required. Its job requests `contents: write`, `issues: read`, and `pull-requests: read`. If the feed does not update, check that both markers appear exactly once and in order, inspect the workflow run for GitHub Search API rate limits, and verify that the token's repository permissions permit the requested access.

## External image services

The GitHub statistics and language cards are served by `github-readme-stats.vercel.app`, an external service. GitHub may rate-limit it, or the service may be unavailable; their absence does not affect the README text. The contribution snake is served from this repository's `output` branch and becomes available after its first successful workflow run. There is no streak card or portfolio-demo link because a dependable endpoint or working deployment has not been verified.

## Before publishing profile edits

Review the generated Markdown and all project links, run the local validator, and check the target branch. This redesign is prepared on `profile-redesign`; the profile page changes only after a pull request is merged into `main`. Workflow runs also require the workflow files to be on `main`.

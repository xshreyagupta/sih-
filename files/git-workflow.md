# Git Workflow

Keep it simple — this is a hackathon, not a company. Trunk-ish with short feature branches,
no long-lived `develop` branch (that's one extra merge hop the team doesn't need in 24-48h).

## Branches

```
main                        — always demoable/working
├── feature/cv-<short-desc>
├── feature/tracking-<short-desc>
├── feature/geo-events-<short-desc>
├── feature/backend-<short-desc>
├── feature/intelligence-<short-desc>
└── feature/frontend-<short-desc>
```

- Each member works almost exclusively inside their own top-level directory
  (`cv/`, `tracking/`, `geo_events/`, `backend/`, `intelligence/`, `frontend/`) → branches
  rarely conflict with each other because paths don't overlap.
- Branch naming: `feature/<module>-<short-description>`, e.g. `feature/backend-events-api`.

## Commits
- Conventional-ish: `cv: add pothole class mapping`, `backend: implement POST /events`.
  Prefix = module name. Keeps `git log` scannable across 6 people.

## Pull requests
- Open a PR into `main` as soon as something runs, even partially — small, frequent PRs beat
  one giant end-of-hackathon PR.
- **Self-merge is fine** for changes entirely inside your own module directory (low risk,
  keeps velocity up).
- **Requires one reviewer** for any PR touching a shared path: `data/contracts/**`, `docs/**`,
  `docker-compose.yml`, `.env.example`. Reviewer = whichever teammate is most affected
  (e.g. Backend owner reviews contract changes; whoever relies on the doc reviews doc PRs).
- If you need to change the Event schema or API contract: post in the team channel first,
  get a thumbs-up, then PR — because 3+ other people's code depends on it.

## Conflict handling
- Because directories are owned 1:1, conflicts should be rare. If they happen inside
  `data/contracts/` or `docs/`, resolve live (call/screen-share) rather than over Git — these
  are small text files, faster to agree verbally than to merge blind.

## Merge cadence
- Merge to `main` early and often (multiple times a day). Don't batch — a broken `main` for
  hours blocks the two people (CV, Tracking) who feed everyone else.
- Before the final demo: freeze `main`, no risky merges within the last ~1 hour, only
  bugfixes.

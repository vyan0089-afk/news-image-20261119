# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/vyan0089-afk/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/vyan0089-afk/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Sum up 19 November's world news in one image: a program that renders the day's top stories — the Trump–Xi–Putin talks in Shenzhen, the world court's Myanmar genocide verdict, Anthropic's record IPO, GTA VI's global rollout, and more — into one 1024x1024 newspaper front page a reader can take in at a glance.

v2 (2026-11-20) rebuilds the page from scratch as a denser front page: **38 stories (15 main stories + 23 briefs)**, a masthead ("THE NINETEENTH — THE WORLD IN ONE DAY"), a deck, a region strip, and a footer with sources. Every story is verified against web reporting; a DATECHECK line names the big 18 November stories that were deliberately left out.

## Run it

```sh
python3 generate.py            # rebuild entry.png from transcript.txt
MAKEFUN_OUTPUT_DIR=out python3 main.py   # kit-style local run
```

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards

## What is in this folder

- `transcript.txt` — source of truth. Line 1 is the date; lines 2–5 are
  page furniture (MASTHEAD, DECK, DATECHECK, FOOTER); then 15 main
  stories in importance order, an "ALSO ON THURSDAY" divider, and 23
  briefs — **38 stories total**, all verified against web reporting on
  19–20 Nov 2026 (Trump–Xi–Putin Shenzhen talks, ICJ Myanmar verdict,
  Anthropic IPO, GTA VI rollout, COP31 draft, Cyclone Akvan, and 32
  more). No fabricated numbers; disputed claims are attributed, not
  stated as fact; stories that broke on 18 Nov are named in DATECHECK
  and left out.
- `generate.py` — build-time renderer (Pillow + DejaVu, this machine
  only). Reads `transcript.txt`, renders `entry.png` 1024x1024,
  deterministic. Every word and picture in the image comes from the
  transcript — no extra text, logos, or watermarks; every picture on
  the page was drawn by the program, no photographs.
- `entry.png` — the rendered image (1024x1024, 185,330 bytes,
  sha256 `547f99a2667abdfd97fd63bf292d5fb5fbbc138615e61a0ad9872344a9a05d32`).
- `main.py` — the graded entrypoint (stdlib-only Python 3.13).
  Copies `entry.png` to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR`).
- `LICENSE` — MIT (from the kit starter).

## Why main.py only copies

The kit's actual gate (verified from `RULES.txt` / `competition.yaml`,
not from memory) is: image **at most 1024x1024 px and at most 1 MiB**,
program `main.py` (Python 3.13) or `main.ts` (Node 22), **standard
library only**, no network, runs twice and both runs must write the
same bytes, output `/output/entry.png`. The grader container has no
Pillow and no guaranteed fonts, so a renderer inside `main.py` could
not reproduce these pixels. The kit itself says "the simplest entry
is a repository holding the image and a one-line program that copies
it there". That is what `main.py` does; `generate.py` + `transcript.txt`
are kept in the repo so the build is reproducible and auditable.

## Test results (v2, 2026-11-20)

- `python3 generate.py` run twice: identical
  sha256 `547f99a2667abdfd97fd63bf292d5fb5fbbc138615e61a0ad9872344a9a05d32`
- `MAKEFUN_OUTPUT_DIR=out python3 main.py` run twice: identical,
  same sha256 as `entry.png`
- Dimensions 1024x1024, 185,330 bytes (< 1,048,576)
- Pixels differing from the most common colour: 43.0% (> 10%)
- Visual check: all 38 stories readable, no clipped/overflowing text

v1 (2026-11-19, superseded): 11 stories, entry.png 135,272 bytes,
sha256 `9685ffe36365909e42276162d866099778a6f61392e8012db2f9f1f1a72ad98e`,
65.5% pixels differ. v1 was submitted 2026-11-19 11:19 WIB
(submission 01a1f208-4801-71c1-ad85-e91f735e8be4); v2 is a resubmission
aiming higher than the live top 3 (~99.2%).

Bounty: `news-image-20261119` — $250 USDC, 50 places
(1st $50, 2nd $30, 3rd $15, 4th–10th $5, 11th–50th $3).
Deadline: **Saturday 21 November 2026, 07:00 WIB**
(2026-11-21T00:00:00Z per `competition.yaml` in the kit).

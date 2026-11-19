# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/vyan0089-afk/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/vyan0089-afk/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Sum up 19 November's world news in one image: a program that renders the day's top stories — GTA VI's global rollout, the Trump–Xi–Putin talks in Shenzhen, Anthropic's record IPO, US–Iran strikes across the Gulf, Israel's Gaza ground operation, the Crimean Bridge attack, and more — into one 1024x1024 PNG a reader can take in at a glance.

## Run it

```sh
python3 generate.py            # rebuild entry.png from transcript.txt
MAKEFUN_OUTPUT_DIR=out python3 main.py   # kit-style local run
```

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards

## What is in this folder

- `transcript.txt` — source of truth. Line 1 is the date; each following
  line is one story, `TITLE | one-line summary`, in importance order.
  11 stories, all verified against web reporting on 19 Nov 2026
  (GTA VI rollout, Trump–Xi–Putin Shenzhen talks, Anthropic IPO,
  US–Iran Gulf strikes, Gaza Yellow Line operation, Crimean Bridge,
  Nvidia, EU Ukraine loan, Van Gogh record sale, ICJ Rohingya verdict,
  Fed minutes). No fabricated numbers; where an event was priced/
  announced on 18 Nov and first traded/reported on 19 Nov, the wording
  says so (e.g. Anthropic "begins trading", IPO "priced at $83").
- `generate.py` — build-time renderer (Pillow + DejaVu, this machine
  only). Reads `transcript.txt`, renders `entry.png` 1024x1024,
  deterministic. Every word in the image comes from the transcript —
  no extra text, logos, or watermarks.
- `entry.png` — the rendered image (1024x1024, 135,272 bytes).
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

## Test results (2026-11-19)

- `python3 generate.py` run twice: identical
  sha256 `9685ffe36365909e42276162d866099778a6f61392e8012db2f9f1f1a72ad98e`
- `MAKEFUN_OUTPUT_DIR=out python3 main.py` run twice: identical,
  same sha256 as `entry.png`
- Dimensions 1024x1024, 135,272 bytes (< 1,048,576)
- Pixels differing from the most common colour: 65.5% (> 10%)
- Visual check: all 11 stories readable, no clipped/overflowing text

Bounty: `news-image-20261119` — $250 USDC, 50 places
(1st $50, 2nd $30, 3rd $15, 4th–10th $5, 11th–50th $3).
Deadline: **Saturday 21 November 2026, 07:00 WIB**
(2026-11-21T00:00:00Z per `competition.yaml` in the kit).

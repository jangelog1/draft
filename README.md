# Draft Board — RPB & Mad Wives

Phone-first live draft board for two CBS leagues. One page, no build step, GitHub Pages.
→ https://jangelog1.github.io/draft

- **RPB** — Rogers Park Bowl, 10 teams, half-PPR, keeper, D/ST doubled. Draft order ships in `data/keepers-rpb.json`.
- **MWV** — Mad Wives, 12 teams, full-PPR, clean redraft, FLEX. **No draft order ships** — CBS had not scheduled it. Set it in ⚙︎ Setup.

Themed to match FFA's own draft tool — colours, tier bands, tinted pills and the player-notes
modal were measured off the rendered site, not guessed.

## Layout

- **iPad / desktop (>=1024px):** board on the left, a sticky 320px rail on the right with My Team
  (positional counter + lineup slot grid + bench), the queue, and the keepers list.
- **Draft Board tab** hides the rail and takes the full width, so all 10 (or 12) columns fit without
  scrolling sideways. Each column header carries that team's outstanding starting slots.
- **Phone:** the rail collapses to one tappable summary at the top of the page.

## How it works

Enter picks **in order**, one tap each. The app derives which seat each pick belongs to from the
snake ladder, so you never type a team name. Keepers are pre-placed and their overall picks never
come up on the clock.

- Missed a name? Tap **⤼ skip** — a `?` placeholder consumes the slot so every downstream seat stays correct.
- Wrong name, or repairing a `?`? **Tap the cell** and search for who actually went there.
- **↩ undo** pops the last pick, repeatable, no confirm.

**Live Helper** — the ✦ button bottom-right. Strategy tab gives a recommended next pick with the
`L` column (picks he is expected to last) and WON'T LAST / 50/50 / SHOULD LAST badges, plus run
risk and your strategy read. Watch List is per-upcoming-pick target groups. The **Dynamic** pill
above the board shows the real need multiplier — toggle it off and the recommendations reorder.

Kickers and defenses are held out of every recommendation until they are forced. RPB doubles D/ST
scoring, so defenses carry inflated VBD and the raw engine put three of them in the top three at
pick 5.02. The Rankings board still lists them at full value.

**Tap any row** for the player card: market ADP vs FFA rank, Pop / SOS / Value / auction $ / VBD /
tier, and FFA's own written notes. **Tier bands** are FFA's own. **Queue** a player from the card
and he shows in the rail.

State is per-league localStorage (`dr-picks-RPB` / `dr-picks-MWV`). Nothing is sent anywhere.
**Install to the home screen** — Safari clears storage for sites you have only visited.

## Data

| Source | What | Refresh |
|---|---|---|
| `thefantasyfootballadvice.com/api/redraft-rankings` + `/projections` | ADP, projections (both `ppr` and `hppr`, so one fetch serves both leagues) | live, every 5 min |
| `data/ffa-ranks-{rpb,mwv}.json` | FFA Rank, Value, SOS, auction $ — **not in the API** | the `ffa-redraft-rankings` skill (exports both league CSVs in one run) |
| `data/ffa-tiers.json` | FFA's 14 tier boundaries + their Pop letter grade per player | re-scraped from FFA's rendered board |
| `data/keepers-rpb.json` | RPB draft order + **predicted** keepers | **edit in Settings** — CBS publishes nothing (its keepers page is blank), so the app is the source of truth |
| `data/notes.json` | Player notes — FFA stances (`love`/`like`/`watch`/`fade`/`avoid`), 28 must-draft + 9 shy-away calls with a `why`, plus per-league video-intel verdicts | rebuilt from `ffa-intel.json`, `ffa-calls.json` and `plan-{rpb,mwv}.json`; must/shy reconciled against FFA's change-log pages |
| `data/plan-rpb.json` | The Monte Carlo plan — branches A/B/C, take zone, Bowers rule, traps, standing conclusions, contingencies | hand-edited; mirrored in `index.html`'s `PLAN` const and drift-checked by `draft_day.py --check` |

**Regenerate both `ffa-ranks` files the morning of each draft.** ADP is live but $/SOS/Value are
from the CSV, and a stale snapshot reads as one coherent opinion when it isn't.

The FFA API serves no prose at all (`/api/projections` is pure stats), so notes cannot be fetched
live — they are hand-curated and shipped.

Use the apex host for the API, never `tools.` — that subdomain 307-redirects without an
`access-control-allow-origin` header and a browser fetch dies at the redirect.

## Checks

- `check()` in the console — snake math at every round boundary, keeper cells, no double-booked cell, clock == `live[k]`.
- `?sim=120` — fills N picks off the ADP board into a throwaway key so the whole grid is eyeballable. Never touches the real draft.
- `?lg=MWV` — open a specific league.
- `?reset=1` — empty that league's entered picks and start at 1.01. Keepers, draft order and queue survive. The param drops itself so a reload cannot wipe twice.
- The ↻ button re-pulls the API **and** every committed snapshot, so a pushed data update reaches an installed iPad without a force-quit.

## Draft-day knowledge

`DRAFT-DAY.md` is the one page to open on draft day — pick ladder, the Monte Carlo plan,
contingencies, block windows, every team's needs, live FFA must/shy lists, and how to read the
FantasyPros simulator. It is **generated**: edit the JSON, never the markdown.

```bash
python3 draft_day.py           # rewrite DRAFT-DAY.md
python3 draft_day.py --check   # verify the pick ladder + plan/app drift, write nothing
```

Reads `data/keepers-rpb.json`, `data/notes.json`, `data/plan-rpb.json`. The check asserts the
snake ladder, that keeper picks never come up live, that you hold 15 picks, that every take-zone
name in `plan-rpb.json` also appears in `index.html`, and that the `nextRd>=2` gate on the Bowers
rule is still in the app — taking Bowers at 1.02 costs −81.8.

### Simulations

Sharp room + must-own-a-back-by-round-2 are the defaults. The unmodified engine left 3.3 of 9
opponents with zero RBs after two rounds, so any board built without that rule understates round-2
RB demand by ~3 picks.

| file | what it answers |
|---|---|
| mc5 | 14 strategies × both keepers, full grid |
| mc6 | Plan A/B/C for the double-RB open × room strength |
| mc7 | RB cutoff at 2.09; the Bowers question |
| mc8 | Where Bowers goes, what he costs the team that takes him |
| mc9 | Rounds 1–2 board (**superseded by mc11** — built on the uncorrected engine) |
| mc10 | The RB-scarcity correction itself |
| **mc11** | **Rounds 1–2 board on the corrected engine — current** |
| **mc12** | **5.02: anchor RB vs the FFA must-draft list — 17,280 paired drafts** |

`mc.py` is the broken first attempt, kept as a record. Rounds 3–4 are still unsimulated; mc12 is
the first look past 2.09 and covers pick five only.

### Standing preferences

- Sharp room is the default for every sim, by explicit instruction.
- **Nothing gets removed from the app** — add and combine, don't strip.
- Commits: Conventional Commits, explain the *why*, `Co-Authored-By: Claude Opus 5`.
- Opus 5 for sim design and statistical judgment; Sonnet 5 is the right tier for single-file HTML/JS edits.

### Settled — do not re-open unprompted

- Keeper is **Etienne**, decided. The Burden case exists in mc5; he chose. FFA added Etienne to its
  shy-away list on 2026-08-03 — noted, does not change the R10 keep, but it does mean RB2 is soft.
- MWV has **no draft order** — CBS never scheduled it. Use the Settings order editor once slots are known.
- The sims and FFA's Strategy Lab heatmap have near-zero rank correlation. FFA's is real drafts.
- Only **paired** sim comparisons are valid; absolute scores and win rates mean nothing.

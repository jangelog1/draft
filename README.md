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
| `data/keepers-rpb.json` | RPB draft order + keepers | **edit in Settings** — CBS publishes nothing (its keepers page is blank), so the app is the source of truth |
| `data/notes.json` | Player notes — 94 FFA stances (`love`/`like`/`watch`/`fade`/`avoid`), 25 must-draft + 5 shy-away calls with a `why`, plus per-league video-intel verdicts | rebuilt from `ffa-intel.json`, `ffa-calls.json` and `plan-{rpb,mwv}.json` |

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
- The ↻ button re-pulls the API **and** every committed snapshot, so a pushed data update reaches an installed iPad without a force-quit.

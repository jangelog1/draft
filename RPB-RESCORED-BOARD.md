# FFA projections, scored under RPB's actual rules

Built **2026-08-07**. Regenerate with:

```bash
python3 ~/draft/sims/rpb_score.py --csv
```

**Full board: [`RPB-BOARD.csv`](RPB-BOARD.csv) — all 723 players**, sortable, with overall rank,
position rank, RPB points, vanilla half-PPR points, the delta, VBD, and FFA's ADP rank.

## What this is

FFA's **Detailed Projections** (stat lines — PYDS/PTDS/INT/CAR/RUYDS/RUTDS/REC/REYDS/RETDS) scored
under the RPB rules read off `rpbowl.football.cbssports.com/rules` on 2026-08-07. Nick's view of
the players is untouched; only the rulebook changed. `data/ffa-proj-2026.json` holds the inputs.

Exact: everything scaling off a season total. Modelled: the +3 yardage-game bonuses (normal
approximation) and TD-distance bonuses (flat expected value). `--no-bonus` shows the exact-only
board; the order barely moves.

**Individual punt/kick return yards and return TDs ARE now priced**, from
`data/return-roles-2026.json` — RPB scores them and no projection source does. That file covers one
researched player so far; see §5. Widening it is the largest remaining edge.

## Replacement levels under RPB

10 teams, no FLEX, keepers removed from the pool.

| pos | drafted | replacement is | pts |
|---|---|---|---|
| QB | 4 (six teams keep one) | Jayden Daniels | 390.3 |
| RB | 18 | D'Andre Swift | 199.0 |
| WR | 26 | Jameson Williams | 172.7 |
| TE | 9 | Dalton Kincaid | 116.6 |

## Overall top 30 by VBD

| # | pos | player | RPB | VBD |
|---|---|---|---|---|
| 1 | **RB1** | **Jahmyr Gibbs** | 363.0 | **+164.0** |
| 2 | **RB2** | **Bijan Robinson** | 362.5 | **+163.5** |
| 3 | WR1 | Ja'Marr Chase | 308.9 | +136.2 |
| 4 | WR2 | Puka Nacua | 304.6 | +131.9 |
| 5 | WR3 | Jaxon Smith-Njigba | 267.1 | +94.4 |
| 6 | **TE1** | **Brock Bowers** | 210.3 | **+93.7** |
| 7 | RB3 | Jonathan Taylor | 291.0 | +92.0 |
| 8 | WR4 | Amon-Ra St. Brown | 260.3 | +87.6 |
| 9 | RB4 | Christian McCaffrey | 283.4 | +84.4 |
| 10 | WR5 | Justin Jefferson | 245.0 | +72.3 |
| 11 | TE2 | Trey McBride | 185.1 | +68.5 |
| 12 | WR6 | CeeDee Lamb | 240.6 | +67.8 |
| 13 | RB5 | James Cook | 264.4 | +65.4 |
| 14 | TE3 | Colston Loveland | 179.6 | +63.0 · KEPT |
| 15 | RB6 | Ashton Jeanty | 259.1 | +60.2 |
| 16 | TE4 | Tyler Warren | 161.3 | +44.7 |
| 17 | WR7 | A.J. Brown | 212.3 | +39.6 |
| 18 | WR8 | Drake London | 211.2 | +38.5 |
| 19 | WR9 | Nico Collins | 209.1 | +36.3 |
| 20 | RB7 | Saquon Barkley | 234.8 | +35.8 |
| 21 | RB8 | Ken Walker | 232.9 | +33.9 |
| 22 | WR10 | Malik Nabers | 205.6 | +32.9 |
| 23 | RB9 | Derrick Henry | 231.0 | +32.0 |
| 24 | WR11 | George Pickens | 204.5 | +31.8 |
| 25 | RB10 | Omarion Hampton | 230.3 | +31.3 |
| 26 | RB11 | Chase Brown | 229.9 | +30.9 |
| 27 | **QB1** | **Josh Allen** | 420.3 | **+30.0** |
| 28 | TE5 | Tucker Kraft | 145.5 | +28.9 |
| 29 | RB12 | Devon Achane | 227.6 | +28.6 |
| 30 | TE6 | Sam LaPorta | 141.8 | +25.3 |

---

# Does the strategy change?

**Mostly no — and the two places it moves, it moves in the plan's favour.** Skill-position order is
nearly identical to FFA's own half-PPR order: no RB, WR or TE inside the top 60 moves more than
**two** position ranks. RPB's rules are a level shift, not a re-ranking.

## 1. The Bowers rule gets BIGGER — +57.9, not +36.8

Bowers is **TE1 at +93.7 VBD, 6th overall**. The best take-zone back is Barkley at +35.8.

**Taking Bowers over the back at 2.09 is worth +57.9**, not the +36.8 the plan carries. The old
number came from the sims' own VBD on different projections; this one is FFA's projection under
your rules. The TE cliff is why: Bowers 210.3, McBride 185.1, then Loveland is kept and Warren
drops to 161.3. You start one TE and nine of ten teams need one.

**No change to the instruction. The instruction just got a much bigger number behind it.**

## 2. "Never QB before round 4" is now much harder-edged

**Josh Allen is +30.0 VBD — below Saquon Barkley at +35.8, and 27th overall.**

RPB adds 31–61 points to every quarterback (0.05/yd passing instead of 0.04, plus 300-yard game
bonuses). That makes QB scores look enormous. It does **not** make them valuable, because it lifts
every QB at once and six teams already keep one, so replacement level rises with them.

The whole QB1-to-replacement gap is 30 points ≈ **1.8 points a week**. Allen, Burrow, Herbert,
Jackson, Daniels, Hurts and Prescott are separated by 33 points in total.

**Verdict: wait even more comfortably than the plan says. 7.02 is right.**

## 3. Your league quietly de-values rushing QBs

The only position where order really moves. Passing yards go 0.04 → 0.05; rushing yards stay 0.1.
So volume pocket passers gain and konami-code QBs gain least.

| | half-PPR | RPB | move |
|---|---|---|---|
| Justin Herbert | QB7 | **QB3** | +4 |
| Joe Burrow | QB5 | **QB2** | +3 |
| Caleb Williams | QB8 | QB5 | +3 |
| **Lamar Jackson** | QB2 | **QB6** | **−4** |
| Jayden Daniels | QB4 | QB7 | −3 |
| Jalen Hurts | QB6 | QB8 | −2 |

Gains: Prescott +60.7, Burrow +60.3, Herbert +57.2. Malik Willis gains least at +31.6.

Nick's QB list leans mobile (Hurts, Daniels, Lamar). **Your scoring leans the other way.** At 7.02,
prefer the pocket volume arm over the rusher when they're close — Burrow and Herbert are the two
your rules like most.

## 4. The take zone: order shuffles, conclusion holds

| RPB rank | back | VBD | was (half-PPR) |
|---|---|---|---|
| RB7 | Saquon Barkley | +35.8 | RB7 |
| RB8 | Ken Walker | +33.9 | RB8 |
| **RB9** | **Derrick Henry** | +32.0 | **RB11** ⬆ |
| RB10 | Omarion Hampton | +31.3 | RB10 |
| **RB11** | **Chase Brown** | +30.9 | **RB9** ⬇ |
| RB12 | Devon Achane | +28.6 | RB12 · removed, FFA shy-away |

**Henry and Chase Brown swap.** RPB's 100-yard-game and long-TD bonuses reward Henry's big-play
profile and do nothing for Chase Brown's reception volume.

**Do not act on it.** The gap is **1.1 points over a whole season** — noise. And the FFA layer
breaks the tie the other way: Chase Brown is must-draft, Henry is an explicit "watch, not a buy"
(declining targets, last year's RB8 finish inflated by one Week 17 four-TD game). **Keep taking
Chase Brown ahead of Henry.**

The shelf itself is confirmed: RB7 through RB12 span **7.2 points**. Genuinely flat, exactly as the
plan says. Take whichever survives.

## 5. Parker Washington — the biggest single edge in your setup

**VERDICT REVERSED 2026-08-07 (same day).** The first cut of this board had him at WR29, −6.3 VBD,
below replacement, and recommended dropping him. That was wrong: the board was not pricing return
work.

**RPB scores individual returns and no projection source does.** Punt return yards 0.1/yd with a +3
bonus at 100 in a game, kick return 0.05/yd with +3 at 150, any return TD 6 plus distance bonuses.
FFA, FantasyPros and CBS all omit it.

**Washington was Jacksonville's primary punt returner in 2025 and an elite one:** 341 punt return
yards (**5th in the NFL**), 13.6 per return (6th), and he **led the league in punt return
touchdowns** — the first Jaguar ever to house multiple returns in a season. Verified against
RotoWire, Big Cat Country, SI/Jaguar Report and ESPN camp coverage.

Priced conservatively in `data/return-roles-2026.json` — 300 yards and 0.5 return TDs, well under
what he actually did — the scorer now has him at:

| | RPB pts | VBD | position |
|---|---|---|---|
| before returns | 162.1 | −6.3 | WR29 |
| **after returns** | **196.1** | **+23.4** | **WR13** |

| scenario | return pts | VBD |
|---|---|---|
| 2025 repeated exactly | +50.1 | +43.8 |
| conservative (used) | +34.0 | +23.4 |
| bear — loses the job midseason | +17.0 | +10.7 |

**Even the bear case is positive.** His FFA ADP is **73**; his board neighbours DeVonta Smith
(197.4) and Chris Olave (195.1) both go around **ADP 28**. That is a 45-pick arbitrage that exists
only because every ranking in the league prices him without the returns.

**Nick's case is entirely independent and stacks on top of this.** He never mentions returns — he
calls Washington Jacksonville's lead receiver, a round-6 take a round ahead of ADP, ranked above
Odunze, rotating Z and F on an offense that averaged 33+ points over its final nine weeks. FFA's own
projection agrees, giving him more receptions and yards than Brian Thomas Jr.

**The risk, stated plainly:** he is expecting a full-time offensive workload for the first time, and
teams routinely pull a full-time starter off punt returns to limit exposure. His own words are
soft — *"I'm just open for the opportunity, whatever it is."* Jacksonville's receiver room also now
includes Jakobi Meyers alongside Brian Thomas Jr. and Travis Hunter.

### This generalises, and nobody else in the league is doing it

`data/return-roles-2026.json` currently contains **one researched player**. Every other designated
returner in the NFL is mispriced by every board in this league, including this one. An empty entry
in that file means "not looked at yet", never "no return value". **Widening it is the highest-value
research left before draft day.**

## 6. Burden and Evans are fine

- **Luther Burden III** — WR19, +18.7 VBD, 39th overall. Solid at 4.09.
- **Mike Evans** — WR23, +14.8 VBD, 47th overall. Solid at 5.02, and the half-PPR TD-regression
  case is intact.

## 7. Temper the sweep's two late names

From this morning's FantasyPros sweep, on RPB numbers:

- **Jonathon Brooks** — RB30, **−47.4 VBD**
- **Keaton Mitchell** — RB40, **−71.8 VBD**

Both are deep-bench lottery tickets, not value picks. The sweep's case for them was corroboration
between two lists, not projected points. Draft them late as upside, and do not reach.

## 8. Etienne, for the record

**RB21, 198.8 pts, VBD −0.2** — precisely at replacement level. The keeper decision is unchanged
(keep him on regret, not points), and the plan's warning that he is the weakest cell in the roster
is confirmed almost exactly.

---

## Still open

- **`Managers may not do add/drops`** is on your rules page. If it is live, streaming is impossible
  and the entire 15.02 D/ST logic inverts — you would want the best *unit*, earlier. The same page
  lists an Add Fee of $5.00, which contradicts it. **Unresolved, and it is the biggest open
  question in the plan.**
- **`Season Ends: Week 22`** contradicts the "RPB has no playoffs" assumption used to wave off
  Nick's Week 15–17 schedule cautions.
- **Return-yardage scoring** — see §5.
- **K and D/ST** are not in this board; FFA does not project them. D/ST lives in `DST-STREAMING.md`.

# D/ST streaming — RPB (D/ST scores DOUBLE)

Generated 2026-08-07 from FantasyPros. **Re-check before week 1 — see the warning below.**

## ⚠ The week-1 numbers are barely cooked

FantasyPros' week-1 D/ST page reads **"Consensus of 2 Experts (4 available)"**. Two people have
posted week-1 rankings in early August. By kickoff that will be 40+ and the order will move a lot.
Treat everything below as a starting shape, not a decision.

## Who to actually trust on D/ST

FantasyPros grades 150+ analysts per position. 2025 D/ST accuracy leaders:

| D/ST rank | Analyst |
|---|---|
| 1 | Ted Chmyz — Fantasy Football Blueprint |
| 2 | Mick Ciallela — Fantrax |
| 3 | Kyle Krajewski — First Seed Sports |
| 4 | Zach Brunner — FlurrySports |
| 5 | Kyle Cunningham-Rhoads — The Analyst |
| 7 | Marc Shannep — Fantasy Knockout |
| 8 | Joe Bond — Fantasy Six Pack |
| 9 | Nick Mariano — RotoBaller |
| 10 | Chris Kennedy — Dr. Roto |
| **15** | **Nick Zylak — Fantasy Football Advice** (your guy) |

**Read this with suspicion.** Ted Chmyz is #1 at D/ST while sitting 63rd at QB and 64th at RB —
that is one season of noise on the most volatile position in fantasy, not proven defensive skill.
**Use the consensus, not a person.** Aggregating 90+ rankers is the whole reason the accuracy
scores exist. If you want to narrow it, the `Experts` dropdown on the rankings page lets you build
a custom consensus from the names above.

## Week 1 board (consensus, 2026-08-06)

| # | Defense | Opponent | Matchup | Grade | Proj |
|---|---|---|---|---|---|
| 1 | **Jacksonville** | vs CLE | ★★★★★ | **A+** | **8.8** |
| 2 | Houston | vs BUF | ★★ | A | 8.0 |
| 3 | Denver | at KC | ★★★ | A | 7.8 |
| 4 | Baltimore | at IND | ★ | A− | 7.7 |
| 5 | LA Rams | vs SF | ★ | B+ | 7.5 |
| 6 | LA Chargers | vs ARI | ★★★★ | B | 7.4 |
| 7 | Philadelphia | vs WAS | ★★★★ | B+ | 7.2 |
| 8 | Minnesota | vs GB | ★ | B | 7.0 |
| 9 | Seattle | vs NE | ★★★ | B | 6.8 |
| 10 | Pittsburgh | vs ATL | ★★★ | B− | 6.7 |
| 11 | Buffalo | at HOU | ★★ | B− | 6.6 |
| 12 | Detroit | vs NO | ★★★★ | C+ | 6.4 |
| 13 | Tennessee | vs NYJ | ★★★★★ | C | 6.3 |
| 14 | Green Bay | at MIN | ★★★★★ | C | 6.2 |
| 15 | Cleveland | at JAC | ★★ | C | 6.1 |

**Stars are the matchup. The letter is the start/sit grade.** They diverge on purpose — Tennessee
has a five-star matchup and a C grade because the matchup is soft but the unit is not good.
Jacksonville is the only defense that is top of both.

**Week 1 pick: Jacksonville vs Cleveland.** Best projection, best matchup, best grade.

## Season-long, per FFA's own board

Rams · Seahawks · Texans · Eagles · Chargers · Broncos · Jaguars · Steelers · Vikings · Patriots

## What streaming means for your draft

**Take the best week-1 matchup at 15.02 and churn from there.** (An earlier draft of this file said
13.02, and a later one said "still take *a* defense by 14.09". Both are superseded — 15.02 is the
answer, and it is the same answer in `DRAFT-DAY.md`.)

Two things to weigh against it:

- **RPB doubles D/ST scoring.** Streaming gains double, and so does the cost of a bad week.
- **The round-14 cliff is variance, not a law.** Mock 2 had six defenses gone by 14.09; mock 3 had
  *zero* gone at pick 102 and the top two still only 64% by 13.02. Count the board every round from
  11 rather than assuming either outcome, and take one when the top defenses cross ~60%. Absent that
  signal, 15.02.

---

# Scoring the defenses under RPB's REAL rules

```bash
python3 sims/dst_rank.py             # season + weeks 1-3 + the 3-week stream plan
python3 sims/dst_rank.py --week 2    # one week only
python3 sims/dst_rank.py --formula   # the formula and its sources
python3 sims/dst_rank.py --selftest  # check the line arithmetic
```

`data/dst-scoring-rpb.json` now holds **RPB's actual CBS settings** (screenshotted 2026-08-07,
`VERIFIED: true`). Two things about them changed the whole picture.

## 1. There is no literal 2x — it is baked into the categories

RPB gets its doubled D/ST by inflating the values, not by multiplying: interceptions and fumble
recoveries pay **3** where CBS default is 2, forced fumbles pay **1 on top of** the recovery, and
the points-allowed tiers run all the way to **+20**. Yards allowed pays **nothing**.

The multiplier in the config is therefore set to **1.0 on purpose**. Applying a 2x on top of these
values would double-count. The app's old `dstMult: 2` was an approximation of this, not a rule.

## 2. The tiers compress every good defense together

| PA in a game | Points |
|---|---|
| 0-3 | 20 |
| 4-6 | 18 |
| 7-9 | 16 |
| 10-13 | 10 |
| **14-20** | **8** |
| 21-27 | 4 |
| 28-34 | 0 |
| 35-41 | -4 |
| 42+ | -8 |

**Every defense in the top ten allows 16-19 points a game.** They all land in the same 14-20 tier,
all collect the same 8 points a week from it, and the only thing separating them is sacks and
turnovers. In the *projections* that is worth about a point a week — but see below: the real 2025
spread was 3.9. The tiers compress the projections; they do not compress the season.

## Season — real scoring

| # | Defense | RPB pts | per week |
|---|---|---|---|
| 1 | Rams | 315.2 | 18.5 |
| 2 | Texans | 315.2 | 18.5 |
| 3 | Seahawks | 310.8 | 18.3 |
| 4 | Broncos | 307.4 | 18.1 |
| 5 | Steelers | 306.4 | 18.0 |
| 6 | Jaguars | 302.0 | 17.8 |
| 7 | Vikings | 301.0 | 17.7 |
| 8 | Patriots | 297.6 | 17.5 |
| 9 | Ravens | 296.6 | 17.4 |
| 10 | Browns | 295.6 | 17.4 |

**CORRECTED 2026-08-07.** These projected numbers show 1st to 10th at 1.1 pts/week, but that is an artifact of
preseason projections regressing everyone to the mean. Angelo's ACTUAL 2025 results in this league spread
**3.9 points a game** — Texans 18.00 down to Browns 14.12. See `data/dst-actuals-2025.json`. Trust the actuals
for how wide the position really is; trust the projections only for who changed personnel.

## Weeks 1-3 — real scoring, real lines

Re-pulled **2026-08-07**. Weeks 2 and 3 used to be a proxy off week-1 implied totals; they are now
actual look-ahead lines (Yahoo Sports full-season board), stored raw in `data/dst-weeks-2026.json`
and converted to implied totals by the script rather than by hand.

**Week 1** — these are firm.

| # | Defense | vs | RPB pts | Opp implied |
|---|---|---|---|---|
| **1** | **Jaguars** | Browns | **23.7** | 16.5 |
| 2 | Steelers | Falcons | 20.3 | 19.5 |
| 3 | Seahawks | Patriots | 19.6 | 20.5 |
| 4 | Rams | 49ers | 18.1 | 22.5 |
| 5 | Texans | Bills | 17.7 | 23.0 |
| 6 | Broncos | Chiefs | 17.3 | 23.0 |
| 7 | Ravens | Colts | 17.1 | 22.5 |
| 8 | Vikings | Packers | 16.9 | 23.0 |
| 9 | Patriots | Seahawks | 16.0 | 24.0 |
| 10 | Browns | Jaguars | 15.9 | 24.0 |

**Week 2** — look-ahead, will move.

| # | Defense | vs | RPB pts | Opp implied |
|---|---|---|---|---|
| **1** | **Seahawks** | Cardinals | **23.3** | 17.2 |
| 2 | Rams | Giants | 20.9 | 19.5 |
| 3 | Patriots | Steelers | 19.8 | 19.5 |
| 4 | Ravens | Saints | 19.7 | 19.5 |
| 5 | Broncos | Jaguars | 19.4 | 20.5 |
| 6 | Texans | Bengals | 18.5 | 22.0 |
| 7 | Jaguars | Broncos | 17.0 | 23.0 |
| 8 | Steelers | Patriots | 16.5 | 24.0 |

**Week 3** — look-ahead, will move.

| # | Defense | vs | RPB pts | Opp implied |
|---|---|---|---|---|
| **1** | **Rams** | Broncos | **19.0** | 21.5 |
| 2 | Seahawks | Commanders | 18.7 | 21.5 |
| 3 | Browns | Panthers | 18.7 | 20.5 |
| 4 | Texans | Colts | 18.5 | 22.0 |
| 5 | Jaguars | Patriots | 17.8 | 22.0 |
| 6 | Vikings | Buccaneers | 16.9 | 23.0 |

**Weeks 1-3 combined — this is the draft-day board.**

| # | Defense | 3-week total | per week |
|---|---|---|---|
| **1** | **Seahawks** | **61.6** | 20.5 |
| 2 | Jaguars | 58.4 | 19.5 |
| 3 | Rams | 58.0 | 19.3 |
| 4 | Texans | 54.8 | 18.3 |
| 5 | Broncos | 53.3 | 17.8 |
| 6 | Steelers | 53.0 | 17.7 |
| 7 | Patriots | 52.2 | 17.4 |
| 8 | Ravens | 52.1 | 17.4 |
| 9 | Browns | 50.5 | 16.8 |
| 10 | Vikings | 49.8 | 16.6 |

**Jacksonville owns the best single week; Seattle owns the stretch.** Jaguars are the top week-1
play by 3.4 points and then fall to 7th in week 2 (at Denver) — a one-week rental. Seattle is top-3
in all three weeks. If you draft one defense at 15.02 and want to hold it through the opening month,
**take Seattle**; if you are genuinely churning weekly, take Jacksonville for week 1 and move.

**Houston is still the trap.** Best unit in the league in your actual 2025 results (18.00/game) and
it does not show up in the top five of any of the three weeks — Bills, Bengals and Colts is a hard
opening draw. A great unit in bad spots.

## The conclusion this forces

**Stream. Do not pay for a defense.**

Using **2025 actuals** rather than projections, recomputed 2026-08-07 from the files themselves:

| what | spread | from |
|---|---|---|
| Season-long talent gap, best to 9th | **3.9 pts/game** | `dst-actuals-2025.json` — Texans 18.00, Browns 14.12 |
| Week-1 matchup swing, full slate | **5.9 pts/game** | `dst-weeks-2026.json` — week-1 implied totals 16.5 to 23.0, league-avg unit |
| Week-1 matchup swing, JAX outlier removed | **4.2 pts/game** | same, starting from 18.0 |

**The matchup is worth about 1.1x to 1.5x the unit — the same order of magnitude, not twice and
certainly not six times.** Earlier versions of this file said six (off compressed projections) and
then twice (off an unrecomputed estimate). The numbers above are computed, not carried over.

Three things follow, and the third is the one that actually settles the draft question:

1. **A good unit in a good spot beats a great unit in a bad one** — but only just. Defenses are not
   interchangeable.
2. **An *average* matchup edge buys almost nothing.** Take the JAX-vs-CLE outlier out and the
   matchup advantage nearly collapses into the unit gap. Stream for outlier spots, not for
   marginal ones.
3. **You cannot buy the unit gap in August anyway.** Projections show a 1.1-pt spread where reality
   delivered 3.9 — they compress away the exact thing an early D/ST pick would be paying for. The
   matchup is legible in advance; the unit is not. That, not interchangeability, is why the pick
   waits until 15.02.

The one caveat: this only covers 4for4's top ten. Defenses outside it allow more points and start
dropping into the 21-27 tier, which costs 4 points a game — that gap is real. Stream among good
defenses, not among all of them.

## Formula

```
season = sacks x 1 + INT x 3 + fumble_rec x 3 + forced_fumble x 1
       + defensive_TD x 6 + safety x 2 + blocked_kick x 2
       + 17 x tier_bonus(points_allowed / 17)
       (no multiplier - it is already in the category values)

week   = (season / 17) x (22.0 / opponent_implied_team_total)
```

Opponent implied team total = `game_total/2 -/+ spread/2`. Best single predictor of D/ST scoring.
It is **computed from the stored line**, not typed in. The old `dst-week1-2026.json` stored implied
totals by hand and had Dolphins/Raiders inverted — it recorded Miami's own 18.5 as the Raiders'
offense when Las Vegas is actually implied at 22.0. `--selftest` now pins that game.

Two sources disagreed on who was favored in two week-1 games. Resolved by majority and recorded in
`dst-weeks-2026.json` → `conflicts`: **Titans -2.5 at home** over the Jets (FanDuel/ESPN/FOX beat
the EDS board), and **Raiders -3.5 at home** over Miami (EDS/ESPN/FOX beat FanDuel Research).

## Sources

| What | Where | Pulled |
|---|---|---|
| **RPB D/ST scoring settings** | **CBS league settings page (screenshot)** | **2026-08-07** |
| Season stat lines (PA, yards, sacks, forced TO) | 4for4 DEF projections | 2026-08-07 |
| **Week-1 spreads and totals** | **EDS implied-totals board + FanDuel Research, cross-checked vs ESPN and FOX** | **2026-08-07** |
| **Week-2 and Week-3 look-ahead lines** | **Yahoo Sports full-season odds board** | **2026-08-07** |
| Week-1 D/ST consensus + matchup grades | FantasyPros (only 2 experts posted) | 2026-08-06 |
| Cross-check, unit-based | CBS Sports D/ST — stale, updated Jan 4 | 2026-08-07 |
| Expert accuracy by position | FantasyPros accuracy scores | 2026-08-07 |

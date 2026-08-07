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

Your plan currently spends **13.02 on the Rams**. If you are genuinely streaming all year, do not —
take the best week-1 matchup at **15.02 or 16.09** and churn from there. That frees a real pick.

Two things to weigh against it:

- **RPB doubles D/ST scoring.** Streaming gains double, and so does the cost of a bad week.
- **The round-14 cliff is real.** In three mocks the defense board drained hard in round 14 — six
  gone in one round, eight inside two. Wait too long and you are streaming from the leftovers
  rather than choosing. If you plan to stream, still take *a* defense by 14.09.

---

# Scoring the defenses under RPB's own rules

```bash
python3 sims/dst_rank.py            # week 1 + full season, top 10 each
python3 sims/dst_rank.py --formula  # the formula and its sources
```

## ⚠ One input is still missing

`data/dst-scoring-rpb.json` currently holds **CBS defaults, not RPB's real settings**. Nobody has
ever read the league's actual D/ST scoring into this repo — the app only ever carried a flat
`dstMult: 2`. The script prints a loud warning until `VERIFIED` is set to true.

**Get it from:** CBS league site → League → Settings → Scoring → Team Defense/Special Teams.
Paste the numbers in, flip `VERIFIED` to true, re-run. That is the only step left.

## Why a flat 2x was never enough

Doubling scales every defense identically, so it cannot change the ORDER — it only made the gaps
look bigger. Recomputing from the raw stat line does change the order, and the reason is tier
boundaries:

- **Steelers** allow 288 points = **16.9 a game** → lands in the `<= 17` tier, **+1.0 a week**
- **Jaguars** allow 290 points = **17.1 a game** → lands in the `<= 27` tier, **0.0**

Two points of scoring defense across a whole season, and it swings **34 RPB points**. That is the
entire gap between 5th and 6th. Which tiers RPB actually uses is therefore the single most
important unknown here — it matters far more than whose projections you start from.

## Formula

```
season = sacks x W_sack + INT x W_int + fumble_rec x W_fum
       + defensive_TD x W_td + safety x W_saf + blocked_kick x W_blk
       + 17 x tier_bonus(points_allowed / 17)
       then x multiplier

week 1 = (season / 17) x (22.0 / opponent_implied_team_total)
```

Opponent implied team total = `game_total/2 -/+ spread/2`. It is the best single predictor of D/ST
scoring and the part of this that is hardest to get and most reliable.

## Sources

| What | Where | Pulled |
|---|---|---|
| Season stat lines (PA, yards, sacks, forced TO) | 4for4 DEF projections | 2026-08-07 |
| Week-1 spreads and totals | FanDuel Research week-1 odds | 2026-08-07 |
| Week-1 D/ST consensus + matchup grades | FantasyPros (only 2 experts posted) | 2026-08-06 |
| Cross-check, unit-based | CBS Sports D/ST — **stale, updated Jan 4** | 2026-08-07 |
| Expert accuracy by position | FantasyPros accuracy scores | 2026-08-07 |

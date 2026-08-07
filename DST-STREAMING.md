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

# Scoring the defenses under RPB's REAL rules

```bash
python3 sims/dst_rank.py            # week 1 + full season, top 10 each
python3 sims/dst_rank.py --formula  # the formula and its sources
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
turnovers. Over a season that is worth about a point a week.

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

## Week 1 — real scoring

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

## The conclusion this forces

**Stream. Do not pay for a defense.**

Using **2025 actuals** rather than projections:

- Season-long talent gap, best to 9th: **3.9 points a game**
- Additional spread from week-1 matchup: **3.9 points a game**

**The matchup is worth about twice the unit — meaningful, not overwhelming.** An earlier version of
this file said six times, off compressed projections. Both factors matter and they are the same
order of magnitude, so the rule is: **a good unit in a good spot beats a great unit in a bad one,
and beats a mediocre unit in a great one.** Draft at 15.02, stream on matchup, but do not conclude
defenses are interchangeable — they are not.

The one caveat: this only covers 4for4's top ten. Defenses outside it allow more points and start
dropping into the 21-27 tier, which costs 4 points a game — that gap is real. Stream among good
defenses, not among all of them.

## Formula

```
season = sacks x 1 + INT x 3 + fumble_rec x 3 + forced_fumble x 1
       + defensive_TD x 6 + safety x 2 + blocked_kick x 2
       + 17 x tier_bonus(points_allowed / 17)
       (no multiplier - it is already in the category values)

week 1 = (season / 17) x (22.0 / opponent_implied_team_total)
```

Opponent implied team total = `game_total/2 -/+ spread/2`. Best single predictor of D/ST scoring.

## Sources

| What | Where | Pulled |
|---|---|---|
| **RPB D/ST scoring settings** | **CBS league settings page (screenshot)** | **2026-08-07** |
| Season stat lines (PA, yards, sacks, forced TO) | 4for4 DEF projections | 2026-08-07 |
| Week-1 spreads and totals | FanDuel Research week-1 odds | 2026-08-07 |
| Week-1 D/ST consensus + matchup grades | FantasyPros (only 2 experts posted) | 2026-08-06 |
| Cross-check, unit-based | CBS Sports D/ST — stale, updated Jan 4 | 2026-08-07 |
| Expert accuracy by position | FantasyPros accuracy scores | 2026-08-07 |

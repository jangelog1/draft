# RPB draft simulators

Monte Carlo draft sims for Rogers Park Bowl. Run from anywhere:

```bash
python3 ~/draft/sims/mc4.py 400        # all 14 Strategy Lab archetypes, round by round
python3 ~/draft/sims/mc3.py 400        # timing sweeps (when to take D/ST, QB, TE)
python3 ~/draft/sims/mc2.py 1500       # keeper A/B, paired
```

`mc4.py` is the current one. `mc.py` is the first version and is **wrong** — its opponents drafted
on raw ADP while Angelo's seat optimised VBD, which produced a fake 99.7% win rate. Kept only as a
record of the mistake.

## League truth encoded in all of them
10 teams, 16 rounds, snake, half-PPR, **D/ST doubled**, starters QB1/RB2/WR3/TE1/K1/DST1, **no
flex**, Angelo at **seat 2**, 13 keepers consuming their owners' picks. Build is 6RB/6WR/1QB/1TE/
1K/1DST = exactly 16.

## Data
- **Projections/ADP**: `ffa_api_<date>.json` here, or `/tmp/ffa_api.json` if fresher. Refresh with
  `curl -s https://thefantasyfootballadvice.com/api/redraft-rankings -o ~/draft/sims/ffa_api_$(date +%F).json`
  The scripts pick `/tmp` first, else the newest local snapshot.
- **Keepers/draft order**: read live from `../data/keepers-rpb.json`, so editing the app's ledger
  changes the sims automatically.

## How to read the output — this matters
The simulated opponents draft **worse than Angelo's real room**. Absolute scores and win rates are
inflated and mean nothing. Only **paired** comparisons are valid: same seed, same opponents, one
variable changed. Every conclusion below came from paired runs across multiple seeds.

## Findings so far (2026-08-06)
- **Double RB at 1.02 + 2.09 beats taking the better player at 2.09 by +8.6 pts** (8 seeds, CI
  +8.2 to +8.9). Mechanism: picks 19 and 22 are three apart, so deferring WR costs 2 pts, while RB
  falls 220 → 145 by round 11.
- **Don't reach for D/ST or K.** D/ST #1→#10 is only 40 pts, K is 19. Forcing D/ST in round 1 costs
  179. Doubling lifts every defense equally — it makes them look big, not scarce.
- **Keeper under strict double-RB: Burden by ~1 pt** (Etienne starts 0% — no flex, he's RB3).
  Injuries make Burden *better* (−4.7 to −7.7 at 15–30% rates), which refuted the "Etienne is
  insurance" theory. Under any non-double-RB plan Etienne is **+7.2**. Genuinely close; unresolved.
- My sim and FFA's Strategy Lab heatmap have **near-zero rank correlation**. Likely causes: RPB's
  no-flex/doubled-D/ST rules, and that the `Double*` archetypes need two QBs/TEs which this build
  forbids. FFA's heatmap is real drafts — do not treat these sims as overriding it.

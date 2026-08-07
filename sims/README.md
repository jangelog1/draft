# RPB draft simulators

Monte Carlo draft sims for Rogers Park Bowl. Run from anywhere:

```bash
python3 ~/draft/sims/mc8.py 300        # Bowers: who gets him, what he costs them, take him if he falls
python3 ~/draft/sims/mc7.py 300        # RB cutoff at 2.09, and the elite-TE question
python3 ~/draft/sims/mc6.py 300        # plan A/B/C for the double-RB open, x room strength
python3 ~/draft/sims/mc5.py 250        # 14 strategies x both keepers, full grid
python3 ~/draft/sims/mc4.py 400        # all 14 Strategy Lab archetypes, round by round
python3 ~/draft/sims/mc3.py 400        # timing sweeps (when to take D/ST, QB, TE)
python3 ~/draft/sims/mc2.py 1500       # keeper A/B, paired
```

## Room strength — the default is SHARP
Angelo's standing instruction (2026-08-06): **simulate against an above-average room every time.**
`mc6.ROOMS` defines three, by (adp_weight lo/hi, noise lo/hi):

| room | adp_weight | noise | use |
|---|---|---|---|
| soft | .15-.75 | 6-16 | the mc2-mc5 baseline. Retained ONLY to reconcile older findings. |
| **sharp** | **.05-.35** | **2-6** | **the default. Quote these numbers.** |
| elite | .00-.15 | 1-3 | ceiling case, near-pure VBD |

The soft room leaves value on the board and flatters every plan. Several mc2-mc5 conclusions shrink
or invert once the room is sharp — see the findings below. When in doubt, run sharp.

`mc8.py` is the current one. `mc.py` is the first version and is **wrong** — its opponents drafted
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

### Three things these sims structurally cannot see (added 2026-08-07)

Every "0%" and "never" below is a statement about the model, not about the world. Two of them have
already fired in live mocks.

1. **A player cannot fall.** Opponents draft close to ADP, so anyone whose ADP precedes your pick is
   gone by definition. This is why Bowers "never reaches pick 19" in 52,200 drafts and has reached
   2.09 in five of five real ones, and why mc12 could never test Breece Hall at 5.02.
2. **A run cannot happen.** Opponents have no positional aversion and no herd behaviour, so the RB
   block "never" drains past RB12 — and drained entirely by 2.08 twice in a row live.
3. **The FFA must/shy lists do not exist in here.** Left alone the sim takes Devon Achane 31% at
   2.09 and Christian Watson 59% at 6.09, both shy-away. Sim output always needs the FFA layer
   applied on top by hand.

Use the sims for *which plan is better on an average board*. Use the live Pick Predictor for *is
this specific man still here*.

## Findings so far (2026-08-06)
- **Double RB at 1.02 + 2.09 beats taking the better player at 2.09 by +8.6 pts** (8 seeds, CI
  +8.2 to +8.9). Mechanism: picks 19 and 22 are three apart, so deferring WR costs 2 pts, while RB
  falls 220 → 145 by round 11.
- **Don't reach for D/ST or K.** D/ST #1→#10 is only 40 pts, K is 19. Forcing D/ST in round 1 costs
  179. Doubling lifts every defense equally — it makes them look big, not scarce.
- **Keeper under strict double-RB: Burden by ~1 pt** (Etienne starts 0% — no flex, he's RB3).
  Injuries make Burden *better* (−4.7 to −7.7 at 15–30% rates), which refuted the "Etienne is
  insurance" theory. Under any non-double-RB plan Etienne is **+7.2**. Genuinely close; unresolved.
## RB scarcity — the CPU engine under-drafts backs (mc10, 2026-08-06)
Angelo's hunch: nobody leaves the first two rounds without a running back. He was right and the
engine was wrong — the unmodified mc4 CPU left **3.3 of 9 opponents RB-less after two rounds**,
because raw VBD says the WRs are worth more and it has no scarcity belief on top of that.

`mc10.py` adds two knobs. **`MUST_RB` (a team with zero backs must take one at its round-2 pick) is
now the default assumption** — it is a hard behavioural rule with no free parameter. `RB_MULT` (an
RB value premium through round 3) is available but uncalibrated; treat it as sensitivity analysis,
not truth. Boards produced by mc9 without MUST_RB understate how many backs go in round 2 by ~3.

## Findings added 2026-08-06 (mc5-mc8, sharp room unless noted)
- **Keeper: Etienne, on regret not on points.** Full 14-strategy x 2-keeper grid: the two best cells
  are within 0.7 pts, but Etienne's worst case is −1.2 and Burden's is −34.2. Etienne wins 9 of 14
  strategies; Burden wins meaningfully in only the triple-RB scripts.
- **The double-RB edge is a soft-room artifact.** vs pure value it is +7.2 soft, **+2.8 sharp**,
  −4.5 elite. Still right for this league, but small.
- **Order inside picks 1-3 barely matters; getting two backs inside them matters a lot.**
  RB,WR,RB beats RB,RB,WR by +2.1. Only one early back costs −11.8. *Forcing* the back back at
  4.09+5.02 to fix it costs **−32.4** — the recovery is worse than the miss.
- ~~**The RB block survives to 2.09 even when the room hoards backs.**~~ **REFUTED BY LIVE MOCKS
  2026-08-06/07.** The sim said: with MUST_RB on, Barkley goes ~2.05 and Hampton ~2.06, but the best
  back left at 2.09 is RB7-9 64% / RB10-12 36% / **RB13+ 0%**, even at a +50% RB premium — "the
  Achane cutoff never binds". In the real mocks **every take-zone back was gone by 2.08, in
  back-to-back drafts.** RB13+ was not 0%, it was the actual outcome twice. The sim's RB-vs-WR coin
  flip at 2.09 (+2.4 to −1.0 across all four settings) is still fine; its claim about *availability*
  is not. See the "every take-zone back is gone" contingency in `../DRAFT-DAY.md`.
- **RB cutoff at 2.09 was Devon Achane (RB12); it is now Derrick Henry.** Forced sweep: RB7-12 all
  within 5 pts of pivoting to WR; RB13 (Jeremiyah Love) drops to −14.5, RB20 to −29.2. The cliff is
  in the projections — RB7-12 are a flat 25-29 VBD block, RB13 is 15.9. **Achane was removed from
  the take zone 2026-08-07** on the FFA layer, not the VBD one: he is shy-away and the fade is
  RPB-format-specific. He still marks where the VBD shelf ends; he is no longer a name to take.
- ~~**Bowers never reaches pick 19.**~~ **REFUTED BY LIVE MOCKS.** The sim said 0 of 52,200 drafts:
  VBD-weighted rooms take him at 5-11 (median 9, usually Achim at slot 9); held past round 1 he goes
  at pick 11 to Anthony 99.4% of the time. **He has fallen to 2.09 in five of five real mocks.** The
  cause is structural, not luck: the sim's opponents draft close to ADP and have no positional
  aversion, while a real room with nine of ten teams needing a TE still will not spend a top-12 pick
  on one. Treat "Bowers at 2.09" as the expected case, not the miracle case.
- **Taking Bowers is not a mistake for the room — it is a bargain.** Cost to the team that does it:
  −74 at pick 1, −49 at pick 3-4, ~0 by pick 9, and **+15 to +42 anywhere in picks 12-18**. The lone
  exception is DREADS (−25), who already keep Colston Loveland and would be doubling up at TE.
- **If Bowers falls to 2.09, take him: +36.8 over the back.** The +36.8 is solid. The "~0
  probability" that used to qualify it was wrong — see above. This is the largest single edge in
  the draft and it is a likely branch, not a lottery ticket.
- Angelo taking Bowers himself at 1.02 costs **−81.8** (Bowers 85.5 VBD vs Gibbs 150.9 / Bijan
  145.3). Reaching for the next TE at 2.09 (Tyler Warren) costs −9.1. Punt to Kittle at 6.09.
- My sim and FFA's Strategy Lab heatmap have **near-zero rank correlation**. Likely causes: RPB's
  no-flex/doubled-D/ST rules, and that the `Double*` archetypes need two QBs/TEs which this build
  forbids. FFA's heatmap is real drafts — do not treat these sims as overriding it.

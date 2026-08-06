#!/usr/bin/env python3
"""RPB — the full grid: every Strategy Lab archetype x both round-10 keeper candidates.

mc4 answered "which strategy" with Etienne pinned. mc2 answered "which keeper" with one generic
strategy. Neither answers the real question, which is joint: the keeper that wins depends on the
plan, and the plan that wins may depend on the keeper. This runs all 28 cells.

Paired by construction: every cell walks the same SEEDS in the same order, so cell-to-cell
differences are the variable, not the luck. Per-seed means are kept so the keeper delta gets a
spread across seeds instead of a single number.

Absolute scores are inflated — the simulated room drafts worse than Angelo's real one
(see sims/README.md). Only the deltas mean anything.
"""
import json, random, statistics as st, sys, collections
from multiprocessing import Pool

import mc4
from mc4 import TEAMS, ROUNDS, MYSLOT, STRATS, STARTERS, slot_of, ladder, lineup, cpu_pick, my_pick

MINE    = "Real Midway Monsters®"
KEEPERS = {"Etienne": "Travis Etienne Jr.", "Burden": "Luther Burden III"}
SEEDS   = [2468, 1234, 777, 31337, 90210, 8675309]


def one_cell(arg):
    """(strategy, keeper) -> per-seed (mean starting points, mean rank, best-roster %)."""
    strat, who, n = arg
    players = mc4.load()
    idx = {p["name"]: p for p in players}
    if KEEPERS[who] not in idx:
        raise SystemExit(f"{KEEPERS[who]} is not in the FFA snapshot — keeper grid is meaningless")
    k = json.load(open(mc4.KEEP))
    order = [e["team"] for e in k["draftOrder"]]
    keep = [dict(x) for x in k["keepers"] if x["team"] != MINE] + \
           [{"team": MINE, "round": 10, "player": KEEPERS[who]}]
    assert len(keep) == 13, f"{len(keep)} keepers, expected 13"
    script, notb, _ffa = STRATS[strat]
    live, pre = ladder(keep, order)

    kept, kpos = KEEPERS[who], idx[KEEPERS[who]]["pos"]
    per_seed = []
    for seed in SEEDS:
        rng = random.Random(seed)
        scores, ranks, starts = [], [], 0
        for _ in range(n):
            style = {s: (rng.uniform(.15, .75), rng.uniform(6, 16)) for s in range(1, TEAMS + 1)}
            rost = {s: list(pre.get(s, [])) for s in range(1, TEAMS + 1)}
            rpos = {s: collections.Counter({p: 0 for p in STARTERS}) for s in range(1, TEAMS + 1)}
            taken = set()
            for s in rost:
                for nm in rost[s]:
                    if nm in idx:
                        rpos[s][idx[nm]["pos"]] += 1
                        taken.add(nm)
            avail = [p for p in players if p["name"] not in taken]
            myn = 0
            for ov in live:
                if not avail: break
                s = slot_of(ov)
                if s == MYSLOT:
                    myn += 1
                    p = my_pick(avail, rpos[s], ov, myn, script, notb)
                else:
                    aw, nz = style[s]
                    p = cpu_pick(avail, rpos[s], ov, rng, aw, nz)
                rost[s].append(p["name"]); rpos[s][p["pos"]] += 1; avail.remove(p)
            sc = {s: lineup(rost[s], idx) for s in rost}
            mine = sc[MYSLOT]
            scores.append(mine)
            ranks.append(sorted(sc.values(), reverse=True).index(mine) + 1)
            # does the keeper actually crack the starting lineup, or is he a bench body?
            samepos = sorted((idx[nm]["pts"] for nm in rost[MYSLOT]
                              if nm in idx and idx[nm]["pos"] == kpos), reverse=True)
            if idx[kept]["pts"] in samepos[:STARTERS[kpos]]: starts += 1
        per_seed.append((st.mean(scores), st.mean(ranks), 100 * ranks.count(1) / n,
                         100 * starts / n))
    return strat, who, per_seed


def ci(diffs):
    """Crude normal CI on the per-seed mean difference. 6 seeds, so this is a spread, not gospel."""
    m = st.mean(diffs)
    if len(diffs) < 2: return m, m, m
    se = st.stdev(diffs) / len(diffs) ** 0.5
    return m, m - 1.96 * se, m + 1.96 * se


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    jobs = [(s, w, N) for s in STRATS for w in KEEPERS]
    with Pool() as pool:
        results = pool.map(one_cell, jobs)
    grid = {(s, w): r for s, w, r in results}

    tot = N * len(SEEDS)
    print(f"=== RPB grid: {len(STRATS)} strategies x 2 keepers, {tot} drafts per cell "
          f"({len(SEEDS)} seeds x {N}), {len(jobs) * tot} drafts total ===")
    print("Seat 2, 6RB/6WR/1QB/1TE/1K/1DST, no flex, D/ST doubled, 13 keepers.")
    print("Scores are inflated vs the real room — read the columns against each other, not alone.\n")

    def mu(cellkey, i=0): return st.mean([x[i] for x in grid[cellkey]])

    rows = []
    for s in STRATS:
        e, b = mu((s, "Etienne")), mu((s, "Burden"))
        d = [x[0] - y[0] for x, y in zip(grid[(s, "Etienne")], grid[(s, "Burden")])]
        m, lo, hi = ci(d)
        rows.append((s, e, b, max(e, b), m, lo, hi,
                     mu((s, "Etienne"), 1), mu((s, "Burden"), 1),
                     mu((s, "Etienne"), 2), mu((s, "Burden"), 2)))
    rows.sort(key=lambda r: -r[3])

    print(f"{'strategy':<20}{'Etienne':>9}{'Burden':>9}{'best':>9}   {'keeper edge (E-B), 95% CI':<30}{'FFA slot2':>10}")
    for s, e, b, best, m, lo, hi, *_ in rows:
        ffa = STRATS[s][2]
        f = f"{ffa:+.1f}%" if ffa is not None else "n/a"
        who = "Etienne" if m > 0 else "Burden "
        print(f"{s:<20}{e:>9.1f}{b:>9.1f}{best:>9.1f}   {who} {abs(m):>5.1f}  [{lo:+.1f},{hi:+.1f}]{'':<4}{f:>10}")

    print(f"\n{'strategy':<20}{'mean rank E':>12}{'mean rank B':>12}"
          f"{'Etienne starts%':>17}{'Burden starts%':>16}")
    for s, e, b, best, m, lo, hi, re_, rb, we, wb in rows:
        print(f"{s:<20}{re_:>12.2f}{rb:>12.2f}{mu((s,'Etienne'),3):>17.1f}{mu((s,'Burden'),3):>16.1f}")

    # Best cell overall, and the keeper question answered where it actually matters: at the top.
    best_cell = max(((s, w) for s in STRATS for w in KEEPERS), key=lambda c: mu(c))
    print(f"\nBest single cell: {best_cell[0]} keeping {best_cell[1]}  ({mu(best_cell):.1f} pts, "
          f"mean rank {mu(best_cell,1):.2f})")

    top = rows[0][0]
    d = [x[0] - y[0] for x, y in zip(grid[(top, "Etienne")], grid[(top, "Burden")])]
    m, lo, hi = ci(d)
    print(f"Under the winning strategy ({top}): Etienne - Burden = {m:+.1f} pts [{lo:+.1f},{hi:+.1f}]")

    # How often does the keeper choice flip the strategy ranking?
    ranks_e = sorted(STRATS, key=lambda s: -mu((s, "Etienne")))
    ranks_b = sorted(STRATS, key=lambda s: -mu((s, "Burden")))
    print(f"Top 3 with Etienne: {ranks_e[:3]}")
    print(f"Top 3 with Burden : {ranks_b[:3]}")

    json.dump({f"{s}|{w}": grid[(s, w)] for s in STRATS for w in KEEPERS},
              open("/tmp/grid.json", "w"), indent=1)
    print("\nper-seed cells -> /tmp/grid.json")

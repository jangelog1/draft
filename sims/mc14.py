#!/usr/bin/env python3
"""Opening order: after RB at 1.02 and the tight end at 2.09, when do the receivers come?

Angelo's question after the 2026-08-06 live mocks: "So Bowers 2nd pick and RB 3rd pick? Wait for
WR?" Branch B2 says take a take-zone back at 3.02 over the higher-ranked receiver. That settles one
pick. It does not say how long you can then leave the receivers alone.

Every variant holds 1.02 = RB and 2.09 = TE fixed and only changes the order of the next four
picks (3.02, 4.09, 5.02, 6.09). Paired seeds, identical opponents. Absolute points are meaningless
— only the gaps between variants are real.

Caveat carried from mc13: the engine cannot make a player fall, so the tight end at 2.09 is
whoever the board actually offers, not Bowers. The TE slot is constant across every variant, so the
RB/WR ordering comparison stays valid even though the level does not.
"""
import collections, statistics as st, sys
from multiprocessing import Pool

import mc6, mc8, mc12, mc13

# 1.02 and 2.09 are fixed. These are picks 3 through 6: 3.02, 4.09, 5.02, 6.09.
ORDERS = {
    "RB,TE then RB WR WR WR  (his idea)": ["RB", "TE", "RB", "WR", "WR", "WR"],
    "RB,TE then WR RB WR WR  (plan)":     ["RB", "TE", "WR", "RB", "WR", "WR"],
    "RB,TE then RB RB WR WR":             ["RB", "TE", "RB", "RB", "WR", "WR"],
    "RB,TE then WR WR RB RB":             ["RB", "TE", "WR", "WR", "RB", "RB"],
    "RB,TE then RB WR RB WR":             ["RB", "TE", "RB", "WR", "RB", "WR"],
    "RB,TE then value (no script)":       ["RB", "TE"],
}


def make(script):
    def plan(n, avail, rpos, rk, st_):
        return script[n - 1] if n <= len(script) else None
    return plan


def job(arg):
    name, seed, n = arg
    return name, seed, mc13.run_full(n, seed, make(ORDERS[name]))[3]


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    jobs = [(nm, sd, N) for nm in ORDERS for sd in mc12.SEEDS]
    with Pool() as pool:
        out = pool.map(job, jobs)

    cell = collections.defaultdict(list)
    for nm, sd, sc in out:
        cell[(nm, sd)] = sc

    base = "RB,TE then WR RB WR WR  (plan)"
    total = N * len(mc12.SEEDS)
    print(f"=== when do the receivers come? {total:,} drafts per order, paired opponents ===")
    print("1.02 = RB and 2.09 = TE fixed in every line. Only picks 3-6 change.\n")
    print(f"{'order of picks 3,4,5,6':<38}{'pts':>9}{'vs plan':>10}{'beats plan':>12}")
    rows = sorted(ORDERS, key=lambda k: -st.mean([st.mean(cell[(k, s)]) for s in mc12.SEEDS]))
    for nm in rows:
        mine = [st.mean(cell[(nm, s)]) for s in mc12.SEEDS]
        d = [st.mean(cell[(nm, s)]) - st.mean(cell[(base, s)]) for s in mc12.SEEDS]
        win = 100 * sum(1 for x in d if x > 0) / len(d)
        print(f"{nm:<38}{st.mean(mine):>9.1f}{st.mean(d):>+10.1f}{win:>11.0f}%")

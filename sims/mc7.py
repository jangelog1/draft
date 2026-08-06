#!/usr/bin/env python3
"""RPB — two questions mc6 raised but did not answer.

1. WHERE IS THE RB CUTOFF AT 2.09 (overall pick 19)? mc6 showed a top-12 RB is always there and the
   best WR always out-VBDs him, so "take the RB" cannot be an unconditional rule forever — somewhere
   down the RB board it stops being right. This sweeps the cutoff by RB rank and finds the flip.

2. THE BROCK BOWERS STRATEGY. He is TE1 by 22 VBD over TE2, and TE3 (Loveland) is a keeper and off
   the board entirely, so the tight-end cliff in this league is unusually steep. Worth a top-20 pick?

Reuses mc6's plan engine and room model; only the plans and the instrumentation are new.
Etienne is the round-10 keeper throughout.
"""
import json, statistics as st, sys, collections
from multiprocessing import Pool

import mc4, mc6
from mc6 import best_rank, best_vbd, ROOMS

BOWERS, MCBRIDE = "Brock Bowers", "Trey McBride"
mc6.WATCH = [BOWERS, MCBRIDE]

def has(avail, name): return any(p["name"] == name for p in avail)


# ---- 1. RB cutoff sweep: take the back at 2.09 only if a top-K RB is on the board ----

def make_cut(k):
    """RB at 1.02. At 2.09 take the second back only if the best RB left is top-K at his position;
    otherwise take the WR and buy the back at 3.02. K=99 is 'always RB', K=0 is 'never'."""
    def f(n, avail, rpos, rk, st_):
        if n == 1: return "RB"
        if n == 2:
            st_["fired"] = best_rank(avail, "RB", rk) <= k
            return "RB" if st_["fired"] else "WR"
        if n == 3: return "WR" if st_["fired"] else "RB"
        return "WR" if n <= 5 else None
    return f

CUTS = [0, 6, 8, 99]

# The cutoff above never binds — the board always serves an RB7/RB8 at 2.09, so "only take a top-12
# back" and "always take the back" are the same plan. To find where the cutoff actually IS, force
# the choice: take the Nth-best RB on the board at 2.09 and sweep N. The control is taking the WR
# instead and buying a back at 3.02.
RANKS = [7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20]

def make_rank(g):
    """At 2.09 take the best available RB who ranks g or worse at his position — i.e. pretend the
    board only left you an RB#g. Then WR,WR,WR. Sweeping g walks down the RB board."""
    def f(n, avail, rpos, rk, st_):
        if n == 1: return "RB"
        if n == 2:
            rbs = sorted((p for p in avail if p["pos"] == "RB" and rk[p["name"]] >= g),
                         key=lambda p: rk[p["name"]])
            return rbs[0] if rbs else "RB"
        return "WR" if n <= 5 else None
    return f


# ---- 2. Bowers plans ----

def bowers_at_2(n, avail, rpos, rk, st_):
    """Take Bowers at 2.09 if he is there, else the second RB. TE bumps RB2 to 3.02."""
    if n == 1: return "RB"
    if n == 2:
        st_["te"] = has(avail, BOWERS)
        return "TE" if st_["te"] else "RB"
    if n == 3: return "RB" if st_.get("te") else "WR"
    return "WR" if n <= 5 else None

def bowers_at_3(n, avail, rpos, rk, st_):
    """Double RB first, then Bowers/McBride at 3.02 if either survived."""
    if n <= 2: return "RB"
    if n == 3 and (has(avail, BOWERS) or has(avail, MCBRIDE)): return "TE"
    return "WR" if n <= 5 else None

def te_at_2_any(n, avail, rpos, rk, st_):
    """Force a TE at 2.09 whoever is best — the naive 'elite TE' read."""
    return ["RB", "TE", "RB", "WR", "WR"][n - 1] if n <= 5 else None

def bowers_at_1(n, avail, rpos, rk, st_):
    """Bowers at 1.02. He is ADP 18, so this is a reach by ~16 picks — included to price it."""
    return ["TE", "RB", "RB", "WR", "WR"][n - 1] if n <= 5 else None


PLANS = {f"cut RB<={k:>2}": make_cut(k) for k in CUTS}
PLANS["A  RB,RB,WR,WR,WR"]   = mc6.plan_A          # baseline, = cut RB<=99
PLANS["TE Bowers @2.09"]     = bowers_at_2
PLANS["TE Bowers/McB @3.02"] = bowers_at_3
PLANS["TE any @2.09"]        = te_at_2_any
PLANS["TE Bowers @1.02"]     = bowers_at_1
PLANS.update({f"RB#{g:<2} @2.09": make_rank(g) for g in RANKS})
mc6.PLANS = PLANS                                  # module level so spawned workers see it

USE_ROOMS = ["soft (mc4/mc5 baseline)", "sharp (above average)"]
SHARP = "sharp (above average)"
MAIN = [f"cut RB<={k:>2}" for k in CUTS] + ["A  RB,RB,WR,WR,WR", "TE Bowers @2.09",
        "TE Bowers/McB @3.02", "TE any @2.09", "TE Bowers @1.02"]


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    jobs = [(p, r, N) for p in MAIN for r in USE_ROOMS] + \
           [(f"RB#{g:<2} @2.09", SHARP, N) for g in RANKS]      # rank sweep: sharp room only
    with Pool() as pool: out = pool.map(mc6.one_cell, jobs)
    cells = {(p, r): (ps, bp, pp, tg, mp) for p, r, ps, bp, pp, tg, mp in out}
    tot = N * len(mc6.SEEDS)
    BASE = "A  RB,RB,WR,WR,WR"

    def mean(p, r): return st.mean([x[0] for x in cells[(p, r)][0]])
    def delta(p, r):
        a = [x[0] for x in cells[(BASE, r)][0]]; b = [x[0] for x in cells[(p, r)][0]]
        d = [y - x for x, y in zip(a, b)]
        m = st.mean(d); se = st.stdev(d) / len(d) ** 0.5
        return f"{m:>+7.1f} [{m-1.96*se:+.1f},{m+1.96*se:+.1f}]"

    print(f"=== RB cutoff at 2.09 and the Bowers question — {tot} drafts/cell, "
          f"{len(jobs)*tot} total, Etienne kept ===\n")

    tg = cells[(BASE, "sharp (above average)")][3]; d = tg["seen|2"]
    print("Who is the best RB left when you are on the clock at 2.09 (sharp room):")
    best = [(k.split("|")[2], v) for k, v in tg.items()
            if isinstance(k, str) and k.startswith("bestRB|2|")]
    for nm, c in sorted(best, key=lambda x: -x[1])[:8]:
        print(f"   {100*c/d:>5.1f}%  {nm}")

    print(f"\n--- 1a. Conditional cutoff. 'cut RB<=K' = take the back at 2.09 only if the best RB "
          f"left ranks K or better ---")
    print(f"{'plan':<20}" + "".join(f"{r:>26}" for r in USE_ROOMS) + "   vs baseline (sharp)")
    for p in [f"cut RB<={k:>2}" for k in CUTS] + [BASE]:
        print(f"{p:<20}" + "".join(f"{mean(p,r):>26.1f}" for r in USE_ROOMS) + "   " + delta(p, SHARP))

    print(f"\n--- 1b. FORCED sweep: take RB#g at 2.09, sharp room. Control is 'cut RB<= 0' "
          f"(= WR at 2.09, back at 3.02) ---")
    ctrl = mean("cut RB<= 0", SHARP)
    print(f"{'plan':<16}{'typical back':<26}{'pts':>9}{'vs WR-pivot':>13}   {'vs baseline':>24}")
    for g in RANKS:
        p = f"RB#{g:<2} @2.09"
        bp = cells[(p, SHARP)][1]
        who = bp[2].most_common(1)[0][0] if 2 in bp else "?"
        print(f"{p:<16}{who:<26}{mean(p,SHARP):>9.1f}{mean(p,SHARP)-ctrl:>+13.1f}   {delta(p,SHARP):>24}")

    print(f"\n--- 2. Brock Bowers ---")
    for r in USE_ROOMS:
        tg = cells[(BASE, r)][3]
        print(f"  {r}: Bowers still on the board at "
              + ", ".join(f"pick {i} {100*tg.get(f'avail|{i}|'+BOWERS,0)/tg[f'seen|{i}']:.0f}%"
                          for i in mc6.WATCH_PICKS)
              + f"  |  McBride at 3.02 {100*tg.get(f'avail|3|'+MCBRIDE,0)/tg['seen|3']:.0f}%")
    print(f"\n{'plan':<22}" + "".join(f"{r:>26}" for r in USE_ROOMS) + "   vs baseline (sharp)")
    for p in [BASE, "TE Bowers @2.09", "TE Bowers/McB @3.02", "TE any @2.09", "TE Bowers @1.02"]:
        print(f"{p:<22}" + "".join(f"{mean(p,r):>26.1f}" for r in USE_ROOMS)
              + "   " + delta(p, "sharp (above average)"))

    json.dump({f"{p}|{r}": v[0] for (p, r), v in cells.items()},
              open("/tmp/cutoff.json", "w"), indent=1)
    print("\nper-seed cells -> /tmp/cutoff.json")

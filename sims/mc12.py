#!/usr/bin/env python3
"""5.02 — does an anchor RB outrank the FFA must-draft list?

The question came out of the 2026-08-06 mock: following the must list at 5.02 took Luther Burden
and let Breece Hall go at 99%, and Hall's RPB verdict calls him a BUY with a top-3 ceiling. Hall
would have filled the RB2 slot that Etienne only nominally fills, since FFA now lists Etienne as
shy-away.

Everything before 5.02 is held identical so the only thing being measured is pick five. Two
openings are run because the plan's opening and the one the room actually produces are not the
same thing:

  plan      RB, RB, WR, WR   — plan A as written, assuming the take zone survives to 2.09
  observed  RB, TE, WR, QB   — what happened in all three mocks: the take zone drained by 2.08,
                               Bowers fell to 2.09, and Josh Allen was still there at 4.09

Paired: identical seeds, identical opponent styles, so only the policy differs. Absolute scores
mean nothing here (simulated opponents draft worse than his room) — only the gaps do.
"""
import json, collections, statistics as st, sys, os
from multiprocessing import Pool

import mc4, mc6, mc8, mc10

RB_MULT, MUST_RB = 1.00, True          # the corrected room: everyone owns a back by end of round 2
NOTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "notes.json")


def key(n):
    return "".join(c for c in str(n).lower() if c.isalnum())


def must_names():
    """FFA's must-draft calls, minus anyone a rival keeps — those never reach the board."""
    d = json.load(open(NOTES))
    k = json.load(open(mc4.KEEP))
    kept = {key(x["player"]) for x in k["keepers"] if x["team"] != mc10.MINE}
    out = set()
    for v in d["shared"].values():
        if v.get("call") == "must" and key(v["name"]) not in kept:
            out.add(key(v["name"]))
    return out


MUSTS = must_names()


def best_must(avail, rpos, pos=None):
    """Highest-VBD available must-draft player we still have room for."""
    c = [p for p in avail if key(p["name"]) in MUSTS
         and rpos[p["pos"]] < mc6.MYBUILD[p["pos"]]
         and (pos is None or p["pos"] == pos)]
    return max(c, key=lambda p: p["vbd"]) if c else None


def best_rb(avail, rpos):
    c = [p for p in avail if p["pos"] == "RB" and rpos["RB"] < mc6.MYBUILD["RB"]]
    return max(c, key=lambda p: p["vbd"]) if c else None


# ---- the five policies for pick 5. Each returns a position, an exact player, or None. ----

def p_value(avail, rpos, st_):
    """Control — no rule at all, the value engine decides."""
    return None

def p_must(avail, rpos, st_):
    """What we did in the mock: the must list wins, whatever the position."""
    m = best_must(avail, rpos)
    st_["fired"] = m is not None
    return m

def p_must_wr(avail, rpos, st_):
    """Narrower: only a must-draft WR, which is literally the Burden decision."""
    m = best_must(avail, rpos, "WR")
    st_["fired"] = m is not None
    return m

def p_rb(avail, rpos, st_):
    """Anchor RB always — the alternative Angelo is asking about."""
    return "RB"

def make_p_hybrid(margin):
    """Take the back unless the best must-draft player beats him by more than `margin` VBD.
    margin=0 is 'RB on a tie'; a large margin collapses to the must list."""
    def f(avail, rpos, st_):
        rb, m = best_rb(avail, rpos), best_must(avail, rpos)
        if rb is None: return m
        if m is None: return rb
        took_rb = rb["vbd"] >= m["vbd"] - margin
        st_["fired"] = took_rb
        return rb if took_rb else m
    return f


def make_p_named(name):
    """The literal decision Angelo is asking about: take THIS back if he is on the board at 5.02,
    otherwise fall back to the must list. Also records how often he is even available, because a
    policy that fires in 20% of drafts cannot move the mean much either way."""
    want = key(name)
    def f(avail, rpos, st_):
        hit = next((p for p in avail if key(p["name"]) == want), None)
        if hit is not None and rpos[hit["pos"]] < mc6.MYBUILD[hit["pos"]]:
            st_["named_hit"] = st_.get("named_hit", 0) + 1
            return hit
        return best_must(avail, rpos)
    return f


POLICIES = {
    "value (control)":      p_value,
    "Breece Hall if there": make_p_named("Breece Hall"),
    "must-draft list":      p_must,
    "must-draft WR only":   p_must_wr,
    "anchor RB":            p_rb,
    "hybrid margin 0":      make_p_hybrid(0),
    "hybrid margin 10":     make_p_hybrid(10),
    "hybrid margin 25":     make_p_hybrid(25),
}

OPENINGS = {
    "plan     RB,RB,WR,WR": ["RB", "RB", "WR", "WR"],
    "observed RB,TE,WR,QB": ["RB", "TE", "WR", "QB"],
}


def make_plan(opening, pick5):
    def plan(n, avail, rpos, rk, st_):
        if n <= len(opening):
            return opening[n - 1]
        if n == len(opening) + 1:
            return pick5(avail, rpos, st_)
        return None                                  # everything after 5.02 is pure value
    return plan


# mc10.run returns the MEAN of n drafts, not the sample, so one seed is one observation. More
# seeds is the only way to tighten the estimate — and because every policy sees the identical
# seed, the paired difference per seed is what carries the signal.
SEEDS = mc8.SEEDS + [7717, 424242, 13, 555, 98765, 31415, 27182, 60606,
                     101010, 22222, 33333, 44444, 5150, 8008, 12321, 99999, 24680, 13579]


def job(arg):
    open_name, pol_name, seed, n = arg
    plan = make_plan(OPENINGS[open_name], POLICIES[pol_name])
    _, _, _, mean = mc10.run(n, seed, plan, RB_MULT, MUST_RB)
    return open_name, pol_name, seed, mean


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    jobs = [(o, p, sd, N) for o in OPENINGS for p in POLICIES for sd in SEEDS]
    with Pool() as pool:
        res = pool.map(job, jobs)

    cell = {(o, p, sd): m for o, p, sd, m in res}
    total = N * len(SEEDS)
    print(f"=== 5.02: anchor RB vs the FFA must-draft list ===")
    print(f"{total:,} drafts per cell ({len(SEEDS)} seeds x {N}), identical opponents per seed.")
    print(f"{len(MUSTS)} must-draft names live (rival keepers removed).")
    print("Paired deltas: every policy is scored against the SAME seed, so the spread below is")
    print("the spread of the difference, not of the raw score. Absolute points mean nothing.\n")

    for o in OPENINGS:
        print(f"  opening: {o}")
        print(f"    {'policy at 5.02':<22}{'pts':>9}{'vs control':>12}{'vs must list':>14}"
              f"{'win% vs must':>14}")
        rank = sorted(POLICIES, key=lambda p: -st.mean([cell[(o, p, s)] for s in SEEDS]))
        for p in rank:
            mine = [cell[(o, p, s)] for s in SEEDS]
            d_ctl = [cell[(o, p, s)] - cell[(o, "value (control)", s)] for s in SEEDS]
            d_mst = [cell[(o, p, s)] - cell[(o, "must-draft list", s)] for s in SEEDS]
            win = 100 * sum(1 for x in d_mst if x > 0) / len(d_mst)
            print(f"    {p:<22}{st.mean(mine):>9.1f}{st.mean(d_ctl):>+12.1f}"
                  f"{st.mean(d_mst):>+14.1f}{win:>13.0f}%")
        # The headline number, stated as a paired difference with its own spread.
        d = [cell[(o, "anchor RB", s)] - cell[(o, "must-draft list", s)] for s in SEEDS]
        lo, hi = min(d), max(d)
        print(f"    -> anchor RB minus must list: {st.mean(d):+.1f} "
              f"(per-seed range {lo:+.1f} to {hi:+.1f}, "
              f"RB wins {100*sum(1 for x in d if x>0)/len(d):.0f}% of seeds)\n")

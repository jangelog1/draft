#!/usr/bin/env python3
"""The whole draft, all 15 picks, run thousands of times.

Everything before this only ever looked at the opening. mc11 stopped at 2.09, mc12 answered one
question about pick five. This plays every pick Angelo owns, start to finish, and reports what he
actually ends up with — which players show up at which pick, how often the plan's own names are
still there, and how much the finished roster scores.

Runs the plan as written (RB at 1.02, RB at 2.09, then WR/value) against the corrected room, where
every team must own a back by the end of round two. Same paired-seed method as mc12: absolute
scores are meaningless because simulated opponents draft worse than his real room, so everything is
reported as a spread across seeds rather than a single number.
"""
import json, random, collections, statistics as st, sys, os
from multiprocessing import Pool

import mc4, mc6, mc8, mc10, mc12
from mc4 import (TEAMS, ROUNDS, MYSLOT, STARTERS, CPUBUILD,
                 slot_of, snake, ladder, lineup)

MINE, KEEPER, ROOM = mc10.MINE, mc10.KEEPER, mc10.ROOM
RB_MULT, MUST_RB = 1.00, True
SEEDS = mc12.SEEDS


def run_full(n, seed, myplan):
    """Mirrors mc10.run but records every one of Angelo's 15 picks, not just rounds 1-2."""
    aw_lo, aw_hi, nz_lo, nz_hi = ROOM
    players = mc4.load()
    idx = {p["name"]: p for p in players}
    rk = mc6.rank_within_pos(players)
    k = json.load(open(mc4.KEEP))
    order = [e["team"] for e in k["draftOrder"]]
    keep = [dict(x) for x in k["keepers"] if x["team"] != MINE] + \
           [{"team": MINE, "round": 10, "player": KEEPER}]
    live, pre = ladder(keep, order)
    r2 = {snake(2, s): s for s in range(1, TEAMS + 1)}

    rng = random.Random(seed)
    mine_by_pick = collections.defaultdict(collections.Counter)   # pick no -> player -> count
    pos_by_pick = collections.defaultdict(collections.Counter)    # pick no -> position -> count
    must_hit = collections.Counter()                              # pick no -> times it was a must-draft
    scores, starters_by = [], collections.Counter()

    for _ in range(n):
        style = {s: (rng.uniform(aw_lo, aw_hi), rng.uniform(nz_lo, nz_hi))
                 for s in range(1, TEAMS + 1)}
        rost = {s: list(pre.get(s, [])) for s in range(1, TEAMS + 1)}
        rpos = {s: collections.Counter({p: 0 for p in STARTERS}) for s in range(1, TEAMS + 1)}
        taken = set()
        for s in rost:
            for nm in rost[s]:
                if nm in idx: rpos[s][idx[nm]["pos"]] += 1; taken.add(nm)
        avail = [p for p in players if p["name"] not in taken]
        myn, st_ = 0, {}
        for ov in live:
            if not avail: break
            s = slot_of(ov)
            if s == MYSLOT:
                myn += 1
                p = mc6.my_pick(avail, rpos[s], ov, myn, myplan, rk, st_)
                mine_by_pick[myn][p["name"]] += 1
                pos_by_pick[myn][p["pos"]] += 1
                if mc12.key(p["name"]) in mc12.MUSTS: must_hit[myn] += 1
            else:
                aw, nz = style[s]
                p = mc10.cpu_pick(avail, rpos[s], ov, rng, aw, nz, rb_mult_now(ov),
                                  MUST_RB and r2.get(ov) == s and rpos[s]["RB"] == 0)
            rost[s].append(p["name"]); rpos[s][p["pos"]] += 1; avail.remove(p)
        scores.append(lineup(rost[MYSLOT], idx))
        # How many of the nine starting slots ended up genuinely filled (lineup() docks 40 a hole).
        got = collections.Counter(idx[nm]["pos"] for nm in rost[MYSLOT] if nm in idx)
        starters_by[sum(min(got[p], c) for p, c in STARTERS.items())] += 1
    return mine_by_pick, pos_by_pick, must_hit, scores, starters_by


def rb_mult_now(ov):
    return RB_MULT if ov <= mc10.PREMIUM_THRU else 1.0


def observed(n, avail, rpos, rk, st_):
    """What the room actually hands him. In all three 2026-08-06 mocks the take zone drained by
    2.08 and Bowers fell to 2.09, so the real opening is RB, TE, WR, QB, then value. Worth running
    because plan A's board assumes a second back at 2.09 that has not once been there."""
    return ["RB", "TE", "WR", "QB"][n - 1] if n <= 4 else None


PLANS = {"plan A as written  (RB at 2.09)": mc6.plan_A,
         "what actually happens (TE at 2.09)": observed}


def job(arg):
    seed, n, plan_name = arg
    return plan_name, run_full(n, seed, PLANS[plan_name])


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    jobs = [(sd, N, pn) for pn in PLANS for sd in SEEDS]
    with Pool() as pool:
        out = pool.map(job, jobs)

    total = N * len(SEEDS)
    picks = ["1.02","2.09","3.02","4.09","5.02","6.09","7.02","8.09","9.02",
             "11.02","12.09","13.02","14.09","15.02","16.09"]

    print(f"=== EVERY PICK, START TO FINISH — {total:,} full drafts per plan "
          f"({len(SEEDS)} rooms x {N}) ===")
    print("16 rounds, 16 players. Round 10 is Etienne, so 15 picks you actually make.\n")

    summary = {}
    for pn in PLANS:
        mine = collections.defaultdict(collections.Counter)
        pos = collections.defaultdict(collections.Counter)
        must = collections.Counter(); scores = []; filled = collections.Counter()
        for name, (mb, pb, mh, sc, fb) in out:
            if name != pn: continue
            for i, c in mb.items(): mine[i] += c
            for i, c in pb.items(): pos[i] += c
            must += mh; scores += sc; filled += fb
        summary[pn] = scores
        print(f"  {pn}")
        print(f"  {'pick':<8}{'position':<22}{'who you usually get':<44}{'must-draft'}")
        for i in range(1, 16):
            pl = picks[i-1]
            pos_s = " ".join(f"{q} {round(100*c/total)}%" for q, c in pos[i].most_common(2))
            nm_s = " / ".join(f"{n2} {round(100*c/total)}%" for n2, c in mine[i].most_common(2))
            print(f"  {pl:<8}{pos_s:<22}{nm_s[:42]:<44}{round(100*must[i]/total):>3}%")
        s = sorted(scores)
        print(f"  season points: bad year {s[int(.10*len(s))]:.0f} | "
              f"typical {s[len(s)//2]:.0f} | good year {s[int(.90*len(s))]:.0f}")
        print(f"  all nine starters filled {round(100*filled[9]/total)}% | "
              f"must-draft players landed {sum(must.values())/total:.1f} of 15\n")

    a, b = list(PLANS)
    da, db = st.mean(summary[a]), st.mean(summary[b])
    print(f"  difference between the two plans: {db-da:+.1f} points "
          f"({'the realistic one is better' if db>da else 'the written plan is better'})")

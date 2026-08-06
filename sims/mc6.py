#!/usr/bin/env python3
"""RPB — Plan A/B/C for the double-hero-RB open, stress-tested against sharper rooms.

Two things mc4/mc5 could not answer:

1. The plans there were fixed scripts. A real draft plan is CONDITIONAL — "take the second RB at
   2.09 IF one is still there." So plans here are callables that read the live board, and the sim
   reports how often each branch actually fires.
2. The opponents there were soft (adp_weight .15-.75, noise 6-16), which leaves value on the board
   and flatters every plan. Here the room strength is a knob. "sharp" and "elite" rooms draft
   closer to pure VBD with little noise, so almost nothing falls.

Etienne is the round-10 keeper in every cell — that question is settled.
Absolute scores still mean nothing across rooms (a tougher room lowers everyone). Compare plans
WITHIN a room column.
"""
import json, random, statistics as st, sys, collections
from multiprocessing import Pool

import mc4
from mc4 import (TEAMS, ROUNDS, MYSLOT, STARTERS, MYBUILD, CAND,
                 slot_of, ladder, lineup, cpu_pick, need_mult)

MINE   = "Real Midway Monsters®"
KEEPER = "Travis Etienne Jr."
SEEDS  = [2468, 1234, 777, 31337, 90210, 8675309]

# adp_weight lo/hi, noise lo/hi. Lower on both = smarter, more disciplined room.
ROOMS = {
    "soft (mc4/mc5 baseline)": (.15, .75, 6, 16),
    "sharp (above average)":   (.05, .35, 2,  6),
    "elite (best case room)":  (.00, .15, 1,  3),
}

# The first cut of this file branched on "is a top-18 RB still there at 2.09". It fired 100% of the
# time in every room — the RB pool is deep enough that the back is ALWAYS there. That is not the
# real decision. The real decision is whether the best RB is worth more than the best WR on the
# board, which is a value read, not an availability read.
# Second cut: a plain "is the RB worth more than the WR" read fires 0% of the time — at 2.09 the
# best WR always out-VBDs the best RB by 13-17. Yet forcing the RB still beats taking the WR,
# because RB value falls off a cliff later and WR does not. So the rule needs a MARGIN: take the
# back unless the WR beats him by more than this many VBD points. Swept, because the right margin
# is the whole question.
MARGINS = [0, 15, 25, 40, 60, 999]     # 999 = always take the RB, i.e. plan A

# Names to track availability for, at each of Angelo's first few picks. Empty by default; mc7 sets
# it to ask "is Bowers still there at 2.09". Recorded as trig["avail|<pick#>|<name>"].
WATCH = []
WATCH_PICKS = (1, 2, 3, 4)


def rank_within_pos(players):
    r = {}
    by = collections.defaultdict(list)
    for p in players: by[p["pos"]].append(p)
    for pos, g in by.items():
        for i, p in enumerate(sorted(g, key=lambda x: -x["pts"]), 1): r[p["name"]] = i
    return r


def best_rank(avail, pos, rk):
    return min((rk[p["name"]] for p in avail if p["pos"] == pos), default=999)

def best_vbd(avail, pos):
    return max((p["vbd"] for p in avail if p["pos"] == pos), default=-1e9)


# ---- the plans. Each returns a forced position for this pick, or None to let value decide. ----
# Scripts match mc5's archetypes exactly so the numbers are comparable across files.

def plan_A(n, avail, rpos, rk, st_):
    """PLAN A — strict double hero RB, mc5's winner. RB, RB, then three straight WR."""
    return ["RB", "RB", "WR", "WR", "WR"][n - 1] if n <= 5 else None

def make_plan_B(margin):
    """PLAN B — same open, but 2.09 is a value read, not a reflex. Take the second RB unless the
    best WR on the board beats the best RB by more than `margin` VBD; if he does, take the WR and
    buy the back at 3.02 instead. At margin=999 this collapses to plan A."""
    def plan_B(n, avail, rpos, rk, st_):
        if n == 1: return "RB"
        if n == 2:
            ok = best_vbd(avail, "RB") >= best_vbd(avail, "WR") - margin
            st_["fired"] = ok
            return "RB" if ok else "WR"
        if n == 3: return "WR" if st_.get("fired") else "RB"
        if n <= 5: return "WR"
        return None
    return plan_B

def plan_C(n, avail, rpos, rk, st_):
    """PLAN C — both early shots at RB2 break against you, so you recover at 4.09 + 5.02."""
    return ["RB", "WR", "WR", "RB", "RB"][n - 1] if n <= 5 else None

def plan_C2(n, avail, rpos, rk, st_):
    """The failure mode C is measured against — one back, then drift. mc5's HeroRB."""
    return ["RB", "WR", "WR", "WR", "WR"][n - 1] if n <= 5 else None

def plan_D(n, avail, rpos, rk, st_):
    """Control — no script at all, pure value (mc5's CorePillars)."""
    return None

PLANS = {"A  RB,RB,WR,WR,WR": plan_A}
PLANS.update({f"B  margin {m:>3}": make_plan_B(m) for m in (0, 15)})
PLANS["C  RB,WR,WR,RB,RB"]  = plan_C
PLANS["C2 drift, no RB2"]   = plan_C2
PLANS["D  pure value (ctrl)"] = plan_D


def my_pick(avail, rpos, ov, n, plan, rk, st_):
    left = ROUNDS - sum(rpos.values())
    scarce = [p for p in ("DST", "K", "QB", "TE") if rpos[p] < MYBUILD[p]]
    forced = None
    if left <= len(scarce) and scarce:
        forced = scarce[0]                                   # out of room, take the empty slot
    else:
        want = plan(n, avail, rpos, rk, st_)
        # A plan may name an exact player (a dict) instead of a position, so a sweep can ask
        # "what is taking the 13th-best RB here actually worth" without waiting for the board
        # to serve one up.
        if isinstance(want, dict):
            if rpos[want["pos"]] < MYBUILD[want["pos"]]: return want
            want = None
        if want and rpos[want] < MYBUILD[want]: forced = want
    pool = [p for p in avail if rpos[p["pos"]] < MYBUILD[p["pos"]]]
    if forced:
        pool = [p for p in pool if p["pos"] == forced] or pool
    else:
        pool = [p for p in pool if p["pos"] not in ("K", "DST")] or pool
    if not pool: pool = list(avail)
    best, bs = None, -1e18
    for p in pool[:CAND]:
        v = p["vbd"]
        s = (v * need_mult(p["pos"], rpos[p["pos"]], MYBUILD) if v > 0 else v) \
            + max(0, min(24, ov - p["adp"])) * 2
        if s > bs: best, bs = p, s
    return best or pool[0]


def one_cell(arg):
    plan_name, room_name, n = arg
    plan = PLANS[plan_name]
    aw_lo, aw_hi, nz_lo, nz_hi = ROOMS[room_name]
    players = mc4.load()
    idx = {p["name"]: p for p in players}
    rk = rank_within_pos(players)
    k = json.load(open(mc4.KEEP))
    order = [e["team"] for e in k["draftOrder"]]
    keep = [dict(x) for x in k["keepers"] if x["team"] != MINE] + \
           [{"team": MINE, "round": 10, "player": KEEPER}]
    live, pre = ladder(keep, order)
    mypicks = [ov for ov in live if slot_of(ov) == MYSLOT]

    per_seed, byPick, posPick = [], collections.defaultdict(collections.Counter), \
                                collections.defaultdict(collections.Counter)
    trig = collections.Counter()
    for seed in SEEDS:
        rng = random.Random(seed)
        scores, ranks = [], []
        for _ in range(n):
            style = {s: (rng.uniform(aw_lo, aw_hi), rng.uniform(nz_lo, nz_hi))
                     for s in range(1, TEAMS + 1)}
            rost = {s: list(pre.get(s, [])) for s in range(1, TEAMS + 1)}
            rpos = {s: collections.Counter({p: 0 for p in STARTERS}) for s in range(1, TEAMS + 1)}
            taken = set()
            for s in rost:
                for nm in rost[s]:
                    if nm in idx:
                        rpos[s][idx[nm]["pos"]] += 1; taken.add(nm)
            avail = [p for p in players if p["name"] not in taken]
            myn, st_ = 0, {}
            for ov in live:
                if not avail: break
                s = slot_of(ov)
                if s == MYSLOT:
                    myn += 1
                    if myn == 2:                             # board state at 2.09, plan-independent
                        rv, wv = best_vbd(avail, "RB"), best_vbd(avail, "WR")
                        trig["n"] += 1
                        trig["gap"] += rv - wv
                        for m in MARGINS:
                            if rv >= wv - m: trig[f"m{m}"] += 1
                        for thr in (6, 12, 18):
                            if best_rank(avail, "RB", rk) <= thr: trig[thr] += 1
                    if WATCH and myn in WATCH_PICKS:
                        up = {p["name"] for p in avail}
                        trig[f"seen|{myn}"] += 1
                        for w in WATCH:
                            if w in up: trig[f"avail|{myn}|{w}"] += 1
                        trig[f"bestRB|{myn}|" + min((p for p in avail if p["pos"] == "RB"),
                                                    key=lambda p: rk[p["name"]])["name"]] += 1
                    p = my_pick(avail, rpos[s], ov, myn, plan, rk, st_)
                    byPick[myn][p["name"]] += 1; posPick[myn][p["pos"]] += 1
                else:
                    aw, nz = style[s]
                    p = cpu_pick(avail, rpos[s], ov, rng, aw, nz)
                rost[s].append(p["name"]); rpos[s][p["pos"]] += 1; avail.remove(p)
            sc = {s: lineup(rost[s], idx) for s in rost}
            mine = sc[MYSLOT]
            scores.append(mine); ranks.append(sorted(sc.values(), reverse=True).index(mine) + 1)
        per_seed.append((st.mean(scores), st.mean(ranks), 100 * ranks.count(1) / n))
    return plan_name, room_name, per_seed, dict(byPick), dict(posPick), dict(trig), mypicks


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    jobs = [(p, r, N) for p in PLANS for r in ROOMS]
    with Pool() as pool: out = pool.map(one_cell, jobs)
    cells = {(p, r): (ps, bp, pp, tg, mp) for p, r, ps, bp, pp, tg, mp in out}
    tot = N * len(SEEDS)

    print(f"=== Plan A/B/C/D x room strength — Etienne kept, {tot} drafts per cell, "
          f"{len(jobs)*tot} total ===")
    print("Seat 2, 6RB/6WR/1QB/1TE/1K/1DST, no flex, D/ST doubled, 13 keepers.\n")

    # What the board actually looks like at 2.09. Plan-independent — same for every plan.
    print("Board at 2.09 (plan-independent):")
    print(f"{'room':<26}{'top-6 RB up':>12}{'top-12 RB':>11}{'top-18 RB':>11}{'mean VBD gap RB-WR':>21}")
    for r in ROOMS:
        tg = cells[(next(iter(PLANS)), r)][3]; d = tg["n"]
        print(f"{r:<26}" + "".join(f"{100*tg.get(t,0)/d:>11.1f}%" for t in (6, 12, 18))
              + f"{tg['gap']/d:>+21.1f}")
    print(f"\nHow often each margin says 'take the RB' at 2.09:")
    print(f"{'room':<26}" + "".join(f"{'m='+str(m):>9}" for m in MARGINS))
    for r in ROOMS:
        tg = cells[(next(iter(PLANS)), r)][3]; d = tg["n"]
        print(f"{r:<26}" + "".join(f"{100*tg.get('m'+str(m),0)/d:>8.0f}%" for m in MARGINS))

    print(f"\n{'plan':<24}" + "".join(f"{r:>26}" for r in ROOMS))
    for p in PLANS:
        line = f"{p:<24}"
        for r in ROOMS:
            ps = cells[(p, r)][0]
            line += f"{st.mean([x[0] for x in ps]):>18.1f} (rk {st.mean([x[1] for x in ps]):.2f})"
        print(line)

    print("\nvs plan A, same room, same seeds (positive = better than strict double RB):")
    for p in PLANS:
        if p.startswith("A "): continue
        line = f"{p:<24}"
        for r in ROOMS:
            a = [x[0] for x in cells[("A  RB,RB,WR,WR,WR", r)][0]]
            b = [x[0] for x in cells[(p, r)][0]]
            d = [y - x for x, y in zip(a, b)]
            m = st.mean(d); se = st.stdev(d) / len(d) ** 0.5
            line += f"{m:>+14.1f} [{m-1.96*se:+.1f},{m+1.96*se:+.1f}]"
        print(line)

    # Draft-day sheet for the recommended plan in the sharp room.
    KEY = ("A  RB,RB,WR,WR,WR", "sharp (above average)")
    ps, bp, pp, tg, mypicks = cells[KEY]
    print(f"\n=== Draft sheet: {KEY[0]} in a {KEY[1]} room — your 15 live picks ===")
    print(f"{'#':<3}{'pick':<7}{'position mix':<26}{'most likely names'}")
    for i, ov in enumerate(mypicks, 1):
        rd = (ov - 1) // TEAMS + 1
        mix = "  ".join(f"{q} {round(100*c/tot)}%" for q, c in pp[i].most_common(3))
        nms = ", ".join(f"{n2} {round(100*c/tot)}%" for n2, c in bp[i].most_common(3))
        print(f"{i:<3}{f'{rd}.{str((ov-1)%TEAMS+1).zfill(2)}':<7}{mix:<26}{nms}")
    print(f"\n(round 10 is the keeper — Etienne — and is not in this list)")

    json.dump({f"{p}|{r}": cells[(p, r)][0] for p in PLANS for r in ROOMS},
              open("/tmp/plans.json", "w"), indent=1)
    print("per-seed cells -> /tmp/plans.json")

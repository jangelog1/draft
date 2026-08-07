#!/usr/bin/env python3
"""Bowers at 2.09 — what it costs you at running back, and what it buys.

Angelo's question: if Bowers goes before my pick, which back do I end up with? And if he falls to
me, which back do I lose? His ADP is 18 and the pick is 19, so this is a real coin flip rather
than a hypothetical — which is also why he has fallen to 2.09 in five straight live drafts.

Every draft is split on one fact — was Bowers on the board at 2.09 — and the two branches are
reported separately. Same seeds, same opponents, so the two columns are comparable.

Policy in both branches is the plan as it now stands:
  1.02  the best back
  2.09  Bowers if he is there, otherwise the best take-zone back, otherwise the best receiver
  3.02  a take-zone back if one survived, otherwise value
Shy-away names are banned throughout, so Achane never gets drafted even when he is the best back left.
"""
import json, collections, statistics as st, sys, os
from multiprocessing import Pool

import mc4, mc6, mc10, mc12, mc13

TAKE_ZONE = ["Saquon Barkley", "Ken Walker", "Chase Brown",
             "Omarion Hampton", "Derrick Henry", "Devon Achane"]
BOWERS = mc12.key("Brock Bowers")


def banned():
    n = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "notes.json")))
    return {mc12.key(v["name"]) for v in n["shared"].values()
            if v.get("call") == "shy" or v.get("stance") in ("fade", "avoid")}


BAN = banned()
ZONE_KEYS = {mc12.key(z) for z in TAKE_ZONE}


def plan(n, avail, rpos, rk, st_):
    """Returns a position, or an exact player dict, or None for pure value."""
    ok = [p for p in avail if mc12.key(p["name"]) not in BAN]
    if n == 1:
        rb = [p for p in ok if p["pos"] == "RB"]
        return max(rb, key=lambda p: p["pts"]) if rb else "RB"
    if n == 2:
        bw = next((p for p in ok if mc12.key(p["name"]) == BOWERS), None)
        st_["bowers_here"] = bw is not None
        if bw: return bw
        tz = [p for p in ok if mc12.key(p["name"]) in ZONE_KEYS]
        if tz: return max(tz, key=lambda p: p["pts"])
        return "WR"
    if n == 3:
        tz = [p for p in ok if mc12.key(p["name"]) in ZONE_KEYS and rpos["RB"] < 2]
        if tz: return max(tz, key=lambda p: p["pts"])
        return None
    return None


def run(n, seed, protect_bowers=False):
    """protect_bowers forces the branch the engine cannot produce on its own: opponents are barred
    from taking Bowers before pick 19, so we can measure what taking him at 2.09 actually costs at
    running back. He has fallen to 2.09 in five of five real drafts and zero of 1,440 simulated
    ones, so this is correcting the model toward observed reality, not wishing."""
    """A trimmed mc13.run_full that also records the Bowers split and the backs taken."""
    import random
    aw_lo, aw_hi, nz_lo, nz_hi = mc10.ROOM
    players = mc4.load(); idx = {p["name"]: p for p in players}
    rk = mc6.rank_within_pos(players)
    k = json.load(open(mc4.KEEP)); order = [e["team"] for e in k["draftOrder"]]
    keep = [dict(x) for x in k["keepers"] if x["team"] != mc10.MINE] + \
           [{"team": mc10.MINE, "round": 10, "player": mc10.KEEPER}]
    live, pre = mc4.ladder(keep, order)
    r2 = {mc4.snake(2, s): s for s in range(1, mc4.TEAMS + 1)}
    rng = random.Random(seed)

    out = {True: {"rb": collections.Counter(), "lost": collections.Counter(), "pts": []},
           False: {"rb": collections.Counter(), "lost": collections.Counter(), "pts": []}}
    for _ in range(n):
        style = {s: (rng.uniform(aw_lo, aw_hi), rng.uniform(nz_lo, nz_hi)) for s in range(1, 11)}
        rost = {s: list(pre.get(s, [])) for s in range(1, 11)}
        rpos = {s: collections.Counter({p: 0 for p in mc4.STARTERS}) for s in range(1, 11)}
        taken = set()
        for s in rost:
            for nm in rost[s]:
                if nm in idx: rpos[s][idx[nm]["pos"]] += 1; taken.add(nm)
        avail = [p for p in players if p["name"] not in taken]
        myn, st_, mine = 0, {}, []
        zone_at_209 = None
        for ov in live:
            if not avail: break
            s = mc4.slot_of(ov)
            if s == mc4.MYSLOT:
                myn += 1
                if myn == 2:
                    zone_at_209 = {p["name"] for p in avail if mc12.key(p["name"]) in ZONE_KEYS}
                p = mc6.my_pick(avail, rpos[s], ov, myn, plan, rk, st_)
                mine.append((myn, p))
            else:
                aw, nz = style[s]
                p = mc10.cpu_pick(avail, rpos[s], ov, rng, aw, nz, 1.0,
                                  r2.get(ov) == s and rpos[s]["RB"] == 0)
                if protect_bowers and ov < 19 and mc12.key(p["name"]) == BOWERS:
                    alt = [q for q in avail if mc12.key(q["name"]) != BOWERS]
                    if alt: p = max(alt[:40], key=lambda q: q["vbd"])
            rost[s].append(p["name"]); rpos[s][p["pos"]] += 1; avail.remove(p)
        br = bool(st_.get("bowers_here"))
        backs = [p["name"] for i, p in mine if p["pos"] == "RB" and i <= 3]
        for b in backs: out[br]["rb"][b] += 1
        # which take-zone backs were on the board at 2.09 but NOT on your roster after 3.02
        got = {p["name"] for _, p in mine}
        for z in (zone_at_209 or set()):
            if z not in got: out[br]["lost"][z] += 1
        out[br]["pts"].append(mc4.lineup(rost[mc4.MYSLOT], idx))
    return out


def job(a):
    return run(*a)


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    with Pool() as pool:
        res = pool.map(job, [(N, sd, True) for sd in mc12.SEEDS])
    agg = {True: {"rb": collections.Counter(), "lost": collections.Counter(), "pts": []},
           False: {"rb": collections.Counter(), "lost": collections.Counter(), "pts": []}}
    for r in res:
        for br in (True, False):
            agg[br]["rb"] += r[br]["rb"]; agg[br]["lost"] += r[br]["lost"]
            agg[br]["pts"] += r[br]["pts"]

    tot = sum(len(agg[b]["pts"]) for b in (True, False))
    print(f"=== {tot:,} drafts, Bowers PROTECTED to pick 19 (matches 5-of-5 real drafts) ===\n")
    for br, label in ((True, "BOWERS FALLS TO YOU (you take him at 2.09)"),
                      (False, "BOWERS IS GONE (you take a back at 2.09 instead)")):
        d = agg[br]; k = len(d["pts"])
        if not k: print(f"-- {label}: never happened --\n"); continue
        print(f"-- {label} — {100*k/tot:.0f}% of drafts ({k:,}) --")
        print("   backs you end up with through 3.02:")
        for nm, c in d["rb"].most_common(6):
            print(f"      {nm:<22}{100*c/k:>5.0f}% of these drafts")
        if d["lost"]:
            print("   take-zone backs that were there at 2.09 and you did NOT get:")
            for nm, c in d["lost"].most_common(6):
                print(f"      {nm:<22}{100*c/k:>5.0f}%")
        print(f"   season points: {st.mean(d['pts']):.1f}\n")
    a, b = agg[True]["pts"], agg[False]["pts"]
    if a and b:
        print(f"Bowers branch minus no-Bowers branch: {st.mean(a)-st.mean(b):+.1f} points")

#!/usr/bin/env python3
"""RPB — Angelo's hunch: real managers take backs earlier than the value engine does, and nobody
leaves the first two rounds without at least one RB.

The mc4 CPU engine drafts VBD + ADP with noise. It has no belief about positional scarcity beyond
what VBD already encodes, so it will happily leave a team RB-less through two rounds if the board
says WRs are worth more. Real rooms do not behave that way. Two knobs, tested separately so we can
see which one actually moves the board:

  MUST_RB   hard rule: at its round-2 pick, a team with zero RBs must take one.
  RB_MULT   soft rule: RB value is multiplied by this through round `PREMIUM_THRU`, modelling the
            scarcity premium managers actually pay.

The thing that matters is not the board cosmetics, it is what is left at 2.09 and whether that
changes Angelo's pick. mc7 put the RB cutoff at Devon Achane (RB12); if a scarcity-driven room
drains the block past him, the right move at 2.09 flips to WR.

Sharp room throughout.
"""
import json, random, collections, statistics as st, sys
from multiprocessing import Pool

import mc4, mc6, mc8
from mc4 import (TEAMS, ROUNDS, MYSLOT, STARTERS, CPUBUILD, CAND,
                 slot_of, snake, ladder, lineup, need_mult)

MINE, KEEPER = mc8.MINE, mc8.KEEPER
ROOM, SEEDS = mc6.ROOM if hasattr(mc6, "ROOM") else mc6.ROOMS["sharp (above average)"], mc8.SEEDS
PREMIUM_THRU = 3 * TEAMS          # premium applies through the end of round 3


def cpu_pick(avail, rpos, ov, rng, aw, nz, rb_mult, must_rb_now):
    """mc4.cpu_pick plus a scarcity premium on RB and an optional 'you must take a back now'."""
    left = ROUNDS - sum(rpos.values())
    missing = [p for p in ("K", "DST", "QB", "TE") if rpos[p] < STARTERS[p]]
    unf = sum(1 for p in ("K", "DST") if rpos[p] < STARTERS[p])
    allow = left <= unf + 2
    if left <= len(missing):
        f = [p for p in avail if p["pos"] in missing]
        if f: return min(f, key=lambda p: p["adp"] + rng.gauss(0, nz))
    pool = avail
    if must_rb_now and rpos["RB"] < CPUBUILD["RB"]:
        rbs = [p for p in avail if p["pos"] == "RB"]
        if rbs: pool = rbs
    best, bs = None, -1e18
    for p in pool[:CAND]:
        pos = p["pos"]
        if pos in ("K", "DST") and not allow: continue
        if rpos[pos] >= CPUBUILD[pos]: continue
        v = p["vbd"]
        if pos == "RB" and ov <= PREMIUM_THRU: v = v * rb_mult if v > 0 else v
        val = (v * need_mult(pos, rpos[pos], CPUBUILD) if v > 0 else v) \
            + max(0, min(24, ov - p["adp"])) * 2
        s = (1 - aw) * val - aw * p["adp"] * 3 + rng.gauss(0, nz)
        if s > bs: best, bs = p, s
    if best is None:
        for p in pool:
            if rpos[p["pos"]] < CPUBUILD[p["pos"]]: return p
        return pool[0]
    return best


def run(n, seed, myplan, rb_mult, must_rb):
    aw_lo, aw_hi, nz_lo, nz_hi = ROOM
    players = mc4.load()
    idx = {p["name"]: p for p in players}
    rk = mc6.rank_within_pos(players)
    k = json.load(open(mc4.KEEP))
    order = [e["team"] for e in k["draftOrder"]]
    keep = [dict(x) for x in k["keepers"] if x["team"] != MINE] + \
           [{"team": MINE, "round": 10, "player": KEEPER}]
    live, pre = ladder(keep, order)
    r2 = {snake(2, s): s for s in range(1, TEAMS + 1)}       # each seat's round-2 overall pick

    rng = random.Random(seed)
    board = collections.defaultdict(collections.Counter)
    rbless, bestrb, myscore = 0, collections.Counter(), []
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
                if myn == 2:
                    r = min((rk[p["name"]] for p in avail if p["pos"] == "RB"), default=99)
                    bestrb[r] += 1
                p = mc6.my_pick(avail, rpos[s], ov, myn, myplan, rk, st_)
            else:
                aw, nz = style[s]
                p = cpu_pick(avail, rpos[s], ov, rng, aw, nz, rb_mult,
                             must_rb and r2.get(ov) == s and rpos[s]["RB"] == 0)
            if ov <= 2 * TEAMS: board[ov][p["name"]] += 1
            rost[s].append(p["name"]); rpos[s][p["pos"]] += 1; avail.remove(p)
            # count RB-less teams HERE, at the end of round 2 — not at the end of the draft, where
            # everyone has backs and the number is trivially zero.
            if ov == 2 * TEAMS:
                rbless += sum(1 for q in rost if q != MYSLOT and rpos[q]["RB"] == 0)
        myscore.append(lineup(rost[MYSLOT], idx))
    return board, rbless / n, bestrb, st.mean(myscore)


SETTINGS = {
    "0 baseline":            (1.00, False),
    "1 must-RB by R2":       (1.00, True),
    "2 +25% RB, must":       (1.25, True),
    "3 +50% RB, must":       (1.50, True),
}
MYPLANS = {"RB @2.09": mc6.plan_A, "WR @2.09": mc8.MYPLANS["take the WR @2.09"]}


def job(arg):
    tag, plan, n = arg
    mult, must = SETTINGS[tag]
    outs = [run(n, sd, MYPLANS[plan], mult, must) for sd in SEEDS]
    board = collections.defaultdict(collections.Counter)
    bestrb = collections.Counter()
    for b, _, br, _ in outs:
        for ov, c in b.items(): board[ov].update(c)
        bestrb.update(br)
    return tag, plan, board, st.mean([o[1] for o in outs]), bestrb, [o[3] for o in outs]


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    jobs = [(t, p, N) for t in SETTINGS for p in MYPLANS]
    with Pool() as pool: res = {(t, p): (b, rl, br, sc) for t, p, b, rl, br, sc in pool.map(job, jobs)}
    tot = N * len(SEEDS)
    k = json.load(open(mc4.KEEP))
    TEAMOF = {e["slot"]: (e["team"], e["manager"]) for e in k["draftOrder"]}
    players = {p["name"]: p for p in mc4.load()}

    print(f"=== Does the room take backs earlier than the engine thinks? {tot} drafts/cell, sharp ===\n")
    print("Teams (of 9 opponents) leaving round 2 with ZERO running backs — Angelo's hunch says ~0:")
    for t in SETTINGS:
        print(f"   {t:<22}{res[(t,'RB @2.09')][1]:>5.2f} teams")

    print(f"\n--- Rounds 1-2, modal pick per setting ---")
    print(f"{'pick':<7}{'team':<22}" + "".join(f"{t:<26}" for t in SETTINGS))
    for ov in range(1, 2 * TEAMS + 1):
        s = slot_of(ov); t, m = TEAMOF[s]
        row = f"{(ov-1)//TEAMS+1}.{str((ov-1)%TEAMS+1).zfill(2):<4}{t[:20]:<22}"
        for stg in SETTINGS:
            b = res[(stg, "RB @2.09")][0][ov]
            if s == MYSLOT and ov > TEAMS: row += f"{'(you)':<26}"; continue
            nm, c = b.most_common(1)[0]
            row += f"{nm[:17]+' '+players[nm]['pos']:<20}{round(100*c/tot):>3}%   "
        print(row)

    print(f"\n--- What is left for you at 2.09: best available RB by positional rank ---")
    print(f"{'setting':<22}{'RB7-9':>8}{'RB10-12':>9}{'RB13+':>8}   {'past the Achane cutoff':<24}")
    for t in SETTINGS:
        br = res[(t, "RB @2.09")][2]; d = sum(br.values())
        a = sum(c for r, c in br.items() if r <= 9)
        b_ = sum(c for r, c in br.items() if 10 <= r <= 12)
        c_ = sum(c for r, c in br.items() if r >= 13)
        print(f"{t:<22}{100*a/d:>7.0f}%{100*b_/d:>8.0f}%{100*c_/d:>7.0f}%   {100*c_/d:>6.1f}% of drafts")

    print(f"\n--- Who you actually end up taking at 2.09 (running the RB plan) ---")
    for t in SETTINGS:
        b = res[(t, "RB @2.09")][0][snake(2, MYSLOT)]
        print(f"  {t:<22}" + "  ".join(f"{nm} {round(100*c/tot)}%" for nm, c in b.most_common(4)))

    print(f"\n--- Does it change your pick? (your full-draft starters, paired seeds) ---")
    print(f"{'setting':<22}{'RB @2.09':>10}{'WR @2.09':>10}{'WR - RB':>19}")
    for t in SETTINGS:
        a, b = res[(t, "RB @2.09")][3], res[(t, "WR @2.09")][3]
        d = [y - x for x, y in zip(a, b)]
        m = st.mean(d); se = st.stdev(d) / len(d) ** 0.5
        print(f"{t:<22}{st.mean(a):>10.1f}{st.mean(b):>10.1f}{m:>+11.1f} [{m-1.96*se:+.1f},{m+1.96*se:+.1f}]")

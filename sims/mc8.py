#!/usr/bin/env python3
"""RPB — the Bowers questions. Default room is SHARP (above average) everywhere, per Angelo.

Three things mc7 could not reach, because it could only watch the draft happen:

  Q1  If a team burns a round-2 pick on Bowers, what does it cost THAT team?
      -> force each seat that picks ahead of Angelo in round 2 to take him, score that seat,
         compare against the same seat in the same leagues without the force.
  Q2  Who actually ends up with Bowers, and at what pick?
      -> tally the seat and overall pick in the unforced baseline.
  Q3  If Bowers somehow falls to 2.09, does Angelo take him over the back?
      -> he never falls on his own (0 of 52,200 in mc7), so hold him off the CPUs until Angelo's
         second pick and then price the three choices. This is a CONDITIONAL answer: it says what
         to do given he is there, not how likely that is (it is ~0).

Etienne is the round-10 keeper throughout.
"""
import json, random, statistics as st, sys, collections
from multiprocessing import Pool

import mc4, mc6
from mc4 import TEAMS, ROUNDS, MYSLOT, STARTERS, MYBUILD, slot_of, snake, ladder, lineup, cpu_pick

MINE   = "Real Midway Monsters®"
KEEPER = "Travis Etienne Jr."
BOWERS = "Brock Bowers"
ROOM   = mc6.ROOMS["sharp (above average)"]      # above average, always — no soft-room results here
SEEDS  = mc6.SEEDS


def plan_take_bowers(n, avail, rpos, rk, st_):
    """RB at 1.02, Bowers at 2.09, back to RB at 3.02, then WR."""
    if n == 1: return "RB"
    if n == 2:
        b = next((p for p in avail if p["name"] == BOWERS), None)
        if b: return b
        return "RB"
    if n == 3: return "RB"
    return "WR" if n <= 5 else None

def plan_wr_pivot(n, avail, rpos, rk, st_):
    """The mc6 winner: RB, WR, RB, WR, WR."""
    return ["RB", "WR", "RB", "WR", "WR"][n - 1] if n <= 5 else None

MYPLANS = {
    "take Bowers @2.09": plan_take_bowers,
    "take the RB @2.09": mc6.plan_A,                    # RB,RB,WR,WR,WR
    "take the WR @2.09": plan_wr_pivot,
}


def run(n, seed, myplan, hold_until=None, force=None, room=ROOM):
    """force = (seat, round, player_name): that seat takes that player at its pick in that round.
       hold_until = overall pick before which no CPU may take Bowers."""
    aw_lo, aw_hi, nz_lo, nz_hi = room
    players = mc4.load()
    idx = {p["name"]: p for p in players}
    rk = mc6.rank_within_pos(players)
    k = json.load(open(mc4.KEEP))
    order = [e["team"] for e in k["draftOrder"]]
    keep = [dict(x) for x in k["keepers"] if x["team"] != MINE] + \
           [{"team": MINE, "round": 10, "player": KEEPER}]
    live, pre = ladder(keep, order)
    force_ov = snake(force[1], force[0]) if force else None

    rng = random.Random(seed)
    seat_scores = collections.defaultdict(list)
    bowers_seat, bowers_ov = collections.Counter(), collections.Counter()
    board = collections.defaultdict(collections.Counter)   # overall pick -> who got taken there
    fired = 0
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
            elif force_ov == ov and any(q["name"] == force[2] for q in avail):
                p = idx[force[2]]; fired += 1
            else:
                aw, nz = style[s]
                pool = avail
                if hold_until and ov < hold_until:
                    pool = [q for q in avail if q["name"] != BOWERS] or avail
                p = cpu_pick(pool, rpos[s], ov, rng, aw, nz)
            if p["name"] == BOWERS:
                bowers_seat[s] += 1; bowers_ov[ov] += 1
            if ov <= 2 * TEAMS: board[ov][p["name"]] += 1
            rost[s].append(p["name"]); rpos[s][p["pos"]] += 1; avail.remove(p)
        for s in rost: seat_scores[s].append(lineup(rost[s], idx))
    return ({s: st.mean(v) for s, v in seat_scores.items()}, bowers_seat, bowers_ov, fired / n,
            board)


def job(arg):
    tag, n, myplan_name, hold, force = arg
    outs = [run(n, sd, MYPLANS[myplan_name], hold, force) for sd in SEEDS]
    seats = {s: [o[0][s] for o in outs] for s in range(1, TEAMS + 1)}
    bs, bo = collections.Counter(), collections.Counter()
    for o in outs: bs.update(o[1]); bo.update(o[2])
    return tag, seats, bs, bo, st.mean([o[3] for o in outs])


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    k = json.load(open(mc4.KEEP))
    TEAMOF = {e["slot"]: (e["team"], e["manager"]) for e in k["draftOrder"]}
    # He is gone in round 1 in this model (picks 6-10), so a round-2 force never fires. Force each
    # seat at its ROUND-1 pick instead, and report fired% so a no-op force cannot read as "free".
    AHEAD = [s for s in range(1, TEAMS + 1) if s != MYSLOT]

    jobs = [("baseline", N, "take the RB @2.09", None, None)]
    jobs += [(f"force{s}", N, "take the RB @2.09", None, (s, 1, BOWERS)) for s in AHEAD]
    jobs += [(f"held:{p}", N, p, snake(2, MYSLOT), None) for p in MYPLANS]
    # ADP world. This room is VBD-heavy and grabs Bowers in round 1; his published ADP is 18, i.e.
    # round 2, immediately ahead of Angelo. Hold him past round 1 and ask the same two questions.
    R2AHEAD = [s for s in range(1, TEAMS + 1) if 10 < snake(2, s) < snake(2, MYSLOT)]
    jobs += [("adp:baseline", N, "take the RB @2.09", TEAMS + 1, None)]
    jobs += [(f"adp:force{s}", N, "take the RB @2.09", snake(2, s), (s, 2, BOWERS))
             for s in R2AHEAD]
    with Pool() as pool: res = {t: (a, b, c, f) for t, a, b, c, f in pool.map(job, jobs)}
    tot = N * len(SEEDS)

    print(f"=== Bowers: who gets him, what he costs them, and what to do if he falls ===")
    print(f"Sharp (above average) room, {tot} drafts per cell, Etienne kept.\n")

    # ---- Q2 ----
    _, bs, bo, _f = res["baseline"]
    d = sum(bs.values())
    print(f"Q2. WHERE BOWERS GOES ({d} drafts):")
    print(f"{'slot':<6}{'team':<26}{'manager':<10}{'takes him':>11}")
    for s, c in bs.most_common():
        t, m = TEAMOF[s]
        print(f"{s:<6}{t:<26}{m:<10}{100*c/d:>10.1f}%")
    ovs = sorted(bo.elements())
    print(f"   overall pick: median {ovs[len(ovs)//2]}, range {ovs[0]}-{ovs[-1]}  "
          f"(your picks are 2 and 19)")

    # ---- Q1 ----
    print(f"\nQ1. WHAT TAKING BOWERS IN ROUND 1 COSTS THE TEAM THAT DOES IT:")
    print(f"{'slot':<6}{'team':<26}{'pick':>6}{'fired':>8}{'normal':>10}{'w/ Bowers':>11}{'cost':>9}")
    base = res["baseline"][0]
    for s in AHEAD:
        b, f = base[s], res[f"force{s}"][0][s]
        dd = [y - x for x, y in zip(b, f)]
        t, m = TEAMOF[s]
        print(f"{s:<6}{t:<26}{snake(1,s):>6}{100*res[f'force{s}'][3]:>7.0f}%{st.mean(b):>10.1f}"
              f"{st.mean(f):>11.1f}{st.mean(dd):>+9.1f}")

    # ---- Q3 ----
    print(f"\nQ3. IF HE FALLS TO YOU AT 2.09 (forced: CPUs may not take him before pick "
          f"{snake(2, MYSLOT)}):")
    ref = st.mean(res["held:take the RB @2.09"][0][MYSLOT])
    for p in MYPLANS:
        v = res[f"held:{p}"][0][MYSLOT]
        dd = [x - y for x, y in zip(v, res["held:take the RB @2.09"][0][MYSLOT])]
        m = st.mean(dd)
        se = st.stdev(dd) / len(dd) ** 0.5 if len(dd) > 1 else 0
        print(f"   {p:<22}{st.mean(v):>9.1f}{m:>+9.1f} [{m-1.96*se:+.1f},{m+1.96*se:+.1f}]")

    print(f"\nQ1b/Q2b. ADP WORLD — Bowers held past round 1 (his ADP is 18, so this is the "
          f"realistic case):")
    _, bs2, bo2, _ = res["adp:baseline"]
    d2 = sum(bs2.values())
    for s, c in bs2.most_common():
        t, m = TEAMOF[s]
        print(f"   {100*c/d2:>5.1f}%  slot {s:<3}{t:<26}{m}")
    o2 = sorted(bo2.elements())
    print(f"   overall pick: median {o2[len(o2)//2]}, range {o2[0]}-{o2[-1]}")
    print(f"{'slot':<6}{'team':<26}{'R2 pick':>9}{'fired':>8}{'normal':>10}{'w/ Bowers':>11}{'cost':>9}")
    for s in R2AHEAD:
        b, f = res["adp:baseline"][0][s], res[f"adp:force{s}"][0][s]
        dd = [y - x for x, y in zip(b, f)]
        t, m = TEAMOF[s]
        print(f"{s:<6}{t:<26}{snake(2,s):>9}{100*res[f'adp:force{s}'][3]:>7.0f}%"
              f"{st.mean(b):>10.1f}{st.mean(f):>11.1f}{st.mean(dd):>+9.1f}")

    json.dump({t: {str(s): v for s, v in a.items()} for t, (a, _, _, _) in res.items()},
              open("/tmp/bowers.json", "w"), indent=1)
    print("\nper-seed cells -> /tmp/bowers.json")

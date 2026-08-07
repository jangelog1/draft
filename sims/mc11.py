#!/usr/bin/env python3
"""RPB rounds 1-2, pick by pick — rerun on the corrected opponent model.

mc9 produced the first version of this board on the unmodified engine, which left 3.3 of 9
opponents with no running back after two rounds. Angelo called that wrong; mc10 confirmed it and
added the rule that a team with zero backs must take one at its round-2 pick. This is the same
board, regenerated through that corrected engine, so the round-2 names are the ones a real room
would actually produce.

Sharp (above average) room. Angelo runs plan A (RB at 1.02, RB at 2.09).
"""
import json, collections, statistics as st, sys
from multiprocessing import Pool

import mc4, mc6, mc8, mc10
from mc4 import TEAMS, MYSLOT, slot_of

MUST_RB, RB_MULT = True, 1.00


def job(seed_n):
    seed, n = seed_n
    board, rbless, bestrb, _ = mc10.run(n, seed, mc6.plan_A, RB_MULT, MUST_RB)
    return board, rbless, bestrb


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    with Pool() as pool:
        out = pool.map(job, [(sd, N) for sd in mc8.SEEDS])
    board = collections.defaultdict(collections.Counter)
    bestrb = collections.Counter()
    rbless = []
    for b, rl, br in out:
        for ov, c in b.items(): board[ov].update(c)
        bestrb.update(br); rbless.append(rl)
    tot = N * len(mc8.SEEDS)

    k = json.load(open(mc4.KEEP))
    TEAMOF = {e["slot"]: (e["team"], e["manager"]) for e in k["draftOrder"]}
    players = {p["name"]: p for p in mc4.load()}

    print(f"=== RPB rounds 1-2 — corrected room, {tot} simulated drafts ===")
    print(f"Sharp opponents + every team must own a back by the end of round 2.")
    print(f"Teams leaving round 2 with zero RBs: {st.mean(rbless):.2f} of 9 "
          f"(was 3.30 before the fix).\n")

    for ov in range(1, 2 * TEAMS + 1):
        s = slot_of(ov)
        rd, inrd = (ov - 1) // TEAMS + 1, (ov - 1) % TEAMS + 1
        t, m = TEAMOF[s]
        me = "   <<< YOU" if s == MYSLOT else ""
        print(f"{rd}.{str(inrd).zfill(2)}  pick {ov:<3} {t} ({m}){me}")
        for nm, c in board[ov].most_common(4):
            p = players[nm]
            print(f"        {100*c/tot:>5.1f}%  {nm:<26}{p['pos']:<4} {p['pts']:>6.0f} pts  "
                  f"adp {p['adp']:>5.0f}")
        if rd == 1 and inrd == TEAMS: print()

    print("\n=== positional shape ===")
    for ov in range(1, 2 * TEAMS + 1):
        pos = collections.Counter()
        for nm, c in board[ov].items(): pos[players[nm]["pos"]] += c
        s = slot_of(ov); t, _ = TEAMOF[s]
        mix = "  ".join(f"{q} {round(100*c/tot)}%" for q, c in pos.most_common(3))
        print(f"{(ov-1)//TEAMS+1}.{str((ov-1)%TEAMS+1).zfill(2)}  {t:<26}{mix}")

    d = sum(bestrb.values())
    print(f"\n=== best RB left when you are on the clock at 2.09 (by positional rank) ===")
    for r, c in sorted(bestrb.items()):
        print(f"   RB{r:<3}{100*c/d:>6.1f}%")

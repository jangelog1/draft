#!/usr/bin/env python3
"""RPB — the first two rounds, pick by pick, for all ten teams. Sharp room.

Every seat runs the same value engine mc4 gives the CPUs: VBD, positional need against its own
roster build, ADP discipline and noise varying by manager. Keepers are pre-loaded, so a team that
already keeps a QB is not shopping for one. Angelo's seat runs plan A (RB at 1.02, RB at 2.09).

What each row reports is a DISTRIBUTION, not a prediction: over 1800 drafts, how often each player
came off the board at that exact pick. A 40% name is the modal pick, not a lock.
"""
import json, collections, statistics as st, sys
from multiprocessing import Pool

import mc4, mc6, mc8
from mc4 import TEAMS, MYSLOT, slot_of

PLAN = "take the RB @2.09"          # = mc6.plan_A, the double-RB open


def job(seed_n):
    seed, n = seed_n
    return mc8.run(n, seed, mc8.MYPLANS[PLAN])[4]


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    with Pool() as pool:
        boards = pool.map(job, [(sd, N) for sd in mc8.SEEDS])
    board = collections.defaultdict(collections.Counter)
    for b in boards:
        for ov, c in b.items(): board[ov].update(c)
    tot = N * len(mc8.SEEDS)

    k = json.load(open(mc4.KEEP))
    TEAMOF = {e["slot"]: (e["team"], e["manager"]) for e in k["draftOrder"]}
    kept = collections.defaultdict(list)
    slot_of_team = {e["team"]: e["slot"] for e in k["draftOrder"]}
    for x in k["keepers"]:
        if x["team"] != mc8.MINE: kept[slot_of_team[x["team"]]].append(f"{x['player']} ({x['pos']})")
    kept[MYSLOT].append("Travis Etienne Jr. (RB)")
    players = {p["name"]: p for p in mc4.load()}

    print(f"=== RPB rounds 1-2, sharp room, {tot} simulated drafts ===")
    print("Each row: how often that player was the pick at that exact slot.\n")
    for ov in range(1, 2 * TEAMS + 1):
        s = slot_of(ov)
        rd, inrd = (ov - 1) // TEAMS + 1, (ov - 1) % TEAMS + 1
        t, m = TEAMOF[s]
        me = "  <<< YOU" if s == MYSLOT else ""
        head = f"{rd}.{str(inrd).zfill(2)}  pick {ov:<3} {t} ({m}){me}"
        print(head)
        for nm, c in board[ov].most_common(4):
            p = players[nm]
            print(f"        {100*c/tot:>5.1f}%  {nm:<26}{p['pos']:<4} {p['pts']:>6.0f} pts  "
                  f"adp {p['adp']:>5.0f}")
        if rd == 1 and inrd == TEAMS: print()

    print("\n=== positional shape of the first two rounds ===")
    for ov in range(1, 2 * TEAMS + 1):
        pos = collections.Counter()
        for nm, c in board[ov].items(): pos[players[nm]["pos"]] += c
        s = slot_of(ov); t, _ = TEAMOF[s]
        mix = "  ".join(f"{q} {round(100*c/tot)}%" for q, c in pos.most_common(3))
        print(f"{(ov-1)//TEAMS+1}.{str((ov-1)%TEAMS+1).zfill(2)}  {t:<26}{mix}")

    print("\n=== who each team already keeps (this is what they are NOT shopping for) ===")
    for s in range(1, TEAMS + 1):
        t, m = TEAMOF[s]
        print(f"  slot {s:<3}{t:<26}{'; '.join(kept[s]) or '(none)'}")

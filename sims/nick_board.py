#!/usr/bin/env python3
"""Nick's (FFA) draft philosophy, applied to RPB's rules, pick by pick.

Answers "who does Nick take at each of my 16 rounds". Not a simulation — a rules engine. It walks
Angelo's real pick ladder and at each pick applies, in order:

  1. RPB's own structure   2 RB / 3 WR / 1 TE / 1 QB / 1 K / 1 DST, no FLEX, D/ST scores double,
                           Etienne is the round-10 keeper so that pick never comes up.
  2. Nick's hard rules     RB early (the cliff is real) · TE early or late, NEVER rounds 6-10 ·
                           no QB in rounds 1-3 · shy-away names are banned outright ·
                           no K or D/ST before round 13.
  3. Nick's format caveat  His "three backs in the first four rounds" thesis is built for 12-team
                           PPR with a FLEX. RPB starts two backs and has no FLEX, so the third
                           back is capped to a bench slot rather than treated as a starter. Likewise
                           his TE rule is early OR late — taking Bowers in round 2 spends the early
                           option, so no second tight end is ever drafted.
  4. Availability          A player is offered only if his ADP is within reach of that pick, and
                           anyone a rival keeps never appears at all.

Where Nick and RPB disagree the RPB rule wins, and the line is printed so the conflict is visible.
"""
import json, collections, os, sys
import mc4

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.join(HERE, "..", "data", "notes.json")
MINE = "Real Midway Monsters®"
PICKS = [(1,2),(2,9),(3,2),(4,9),(5,2),(6,9),(7,2),(8,9),(9,2),
         (11,2),(12,9),(13,2),(14,9),(15,2),(16,9)]
STARTERS = {"QB":1,"RB":2,"WR":3,"TE":1,"K":1,"DST":1}
BUILD    = {"QB":1,"RB":5,"WR":7,"TE":1,"K":1,"DST":1}
TAKE_ZONE = ["Saquon Barkley","Ken Walker","Chase Brown","Omarion Hampton","Derrick Henry","Devon Achane"]

# His most concrete stated build, from the 2026-08-07 must-draft WR video: back, back, then these
# three in rounds four, five and six. "If I avoided wide receiver until round four and ended up with
# Burden, Evans and Parker Washington, I would be jumping for joy."
WR_BLOCK = {4: "Luther Burden III", 5: "Mike Evans", 6: "Parker Washington"}

# Half-PPR preference inside the take zone. "In half PPR I have Ken Walker over Chase Brown. Once you
# flip on full PPR, the certainty there for the receptions is too great." RPB is half-PPR.
ZONE_ORDER = ["Saquon Barkley","Ken Walker","Chase Brown","Omarion Hampton","Derrick Henry"]



def key(x):
    return "".join(c for c in str(x).lower() if c.isalnum())


def load():
    players = mc4.load()
    notes = json.load(open(NOTES))
    keep = json.load(open(mc4.KEEP))
    shared = notes["shared"]
    must  = {key(v["name"]) for v in shared.values() if v.get("call") == "must"}
    shy   = {key(v["name"]) for v in shared.values() if v.get("call") == "shy"}
    fade  = {key(v["name"]) for v in shared.values() if v.get("stance") in ("fade","avoid")}
    note  = {key(v["name"]): (v.get("note") or v.get("why") or "") for v in shared.values()}
    kept  = {key(x["player"]) for x in keep["keepers"] if x["team"] != MINE}
    fmt = notes.get("rpbFormat", {})
    up   = {n: w for n, w in fmt.get("up", {}).items()}
    down = {n: w for n, w in fmt.get("down", {}).items()}
    return players, must, shy | fade, note, kept, up, down


def ovr(rd, pk):
    return (rd - 1) * 10 + pk


def pick_for(rd, pk, avail, have, must, banned, note, UP, DOWN):
    """Nick's rules, in the order he actually applies them."""
    o = ovr(rd, pk)
    # Only offer players the board could plausibly still hold at this pick.
    pool = [p for p in avail if p["adp"] >= o - 6 and key(p["name"]) not in banned]
    room = lambda p: have[p["pos"]] < BUILD[p["pos"]]
    pool = [p for p in pool if room(p)]
    if not pool:
        return None, "board exhausted"

    left = len(PICKS) - sum(1 for _ in range(0))          # placeholder, real count passed by caller
    need_dst = have["DST"] < 1
    need_k   = have["K"] < 1

    # --- forced end-of-draft slots: D/ST then K, never before round 13 ---
    if rd >= 15 and need_dst:
        d = [p for p in pool if p["pos"] == "DST"]
        if d: return max(d, key=lambda p: p["pts"]), "D/ST — RPB doubles D/ST scoring, take the best left"
    if rd >= 16 and need_k:
        kk = [p for p in pool if p["pos"] == "K"]
        if kk: return max(kk, key=lambda p: p["pts"]), "kicker last, always"
    if rd >= 13 and need_dst and rd >= 13:
        d = [p for p in pool if p["pos"] == "DST"]
        if d and rd >= 13:
            return max(d, key=lambda p: p["pts"]), "D/ST — defenses vanish in round 14, move at 13"
    if rd >= 15 and need_k:
        kk = [p for p in pool if p["pos"] == "K"]
        if kk: return max(kk, key=lambda p: p["pts"]), "kicker — the run starts round 15"

    skill = [p for p in pool if p["pos"] not in ("K","DST")]
    if not skill:
        return max(pool, key=lambda p: p["pts"]), "only K/DST left"

    # A demoted player has to clear the next man by a real margin, not a rounding error.
    def adj(p):
        """Nick's own half-PPR language, as points. A player he only likes for a full-PPR
        reception floor is worth less here; one he calls a 0.5/standard buy is worth more."""
        return p["pts"] + (10 if p["name"] in UP else 0) - (14 if p["name"] in DOWN else 0)

    def best(lst):
        return max(lst, key=adj) if lst else None

    # --- round 1: Nick takes the back. The cliff is real. ---
    if rd == 1:
        rb = best([p for p in skill if p["pos"] == "RB"])
        if rb: return rb, "R1 — Nick's #1 thesis: attack a high-volume starting back early"

    # --- Bowers: the elite-TE anchor, round 2 or later, never round 1 ---
    bw = next((p for p in skill if key(p["name"]) == key("Brock Bowers")), None)
    if bw and rd >= 2 and have["TE"] == 0:
        return bw, "Bowers — 'elite R2 anchor TE, the early-TE play'. Early or late, never the middle"

    # --- take-zone back: a set of players, not a round ---
    tz = [p for p in skill if p["name"] in TAKE_ZONE and have["RB"] < 2]
    if tz and rd <= 4:
        ranked = sorted(tz, key=lambda q: ZONE_ORDER.index(q["name"]) if q["name"] in ZONE_ORDER else 99)
        return ranked[0], "take-zone back — his half-PPR order, and the dead zone starts right below"

    # --- the round 4-5-6 receiver block, by name, exactly as he lays it out ---
    want = WR_BLOCK.get(rd)
    if want:
        hit = next((p for p in skill if p["name"] == want and have["WR"] < BUILD["WR"]), None)
        if hit:
            return hit, f"the round 4-5-6 block — he names him at round {rd}"

    # --- QB: never rounds 1-3. Nick wants a top-8 arm at a discount. ---
    if have["QB"] == 0:
        qb = [p for p in skill if p["pos"] == "QB"]
        if qb and rd >= 7:
            return best(qb), "QB — 'if you don't get Allen, just wait'. Rounds 6-8 is his window"

    # Nick's TE rule is early OR late, not both. Bowers in round 2 IS the early play, so the
    # late Kittle/Andrews double-dip does not apply — RPB starts one TE and has no FLEX, so a
    # second one never enters a lineup. No TE2 branch on purpose.

    # --- otherwise best player available, with starters weighted first ---
    unfilled = [pos for pos in ("RB","WR") if have[pos] < STARTERS[pos]]
    if unfilled:
        c = [p for p in skill if p["pos"] in unfilled]
        if c:
            b = best(c)
            tag = "must-draft" if key(b["name"]) in must else "best available"
            return b, f"fills a starting {b['pos']} — {tag}"
    b = best(skill)
    tag = "must-draft" if key(b["name"]) in must else "best player available"
    return b, tag


if __name__ == "__main__":
    players, must, banned, note, kept, UP, DOWN = load()
    avail = [p for p in players if key(p["name"]) not in kept]
    have = collections.Counter({p: 0 for p in STARTERS})
    have["TE"] = 0

    print("=== NICK'S BOARD, RUN THROUGH RPB'S RULES — slot 2 ===")
    print("10 teams · half-PPR · 2RB/3WR/1TE/1QB/1K/1DST · no FLEX · D/ST doubled")
    print("Round 10 is Travis Etienne, your keeper — it is not a pick.\n")
    print(f"{'pick':<7}{'pos':<5}{'player':<24}{'why Nick takes him'}")
    print("-" * 100)
    for rd, pk in PICKS:
        p, why = pick_for(rd, pk, avail, have, must, banned, note, UP, DOWN)
        if p is None:
            print(f"{rd}.{pk:02d}   -- board exhausted --"); continue
        avail.remove(p); have[p["pos"]] += 1
        star = " *" if key(p["name"]) in must else "  "
        if p["name"] in UP:   why = f"{why}   [RPB+] {UP[p['name']][:70]}"
        if p["name"] in DOWN: why = f"{why}   [RPB-] {DOWN[p['name']][:70]}"
        print(f"{rd}.{pk:02d}{star}  {p['pos']:<5}{p['name']:<24}{why}")
        if rd == 9:
            print(f"{'10.09':<7}{'RB':<5}{'Travis Etienne Jr.':<24}KEEPER — costs your round-10 pick")
            have["RB"] += 1
    print("\n* = on FFA's must-draft list")
    print("\nfinal roster:", " ".join(f"{k}{v}" for k, v in sorted(have.items()) if v))

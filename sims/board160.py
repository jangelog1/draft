#!/usr/bin/env python3
"""The 160-pick RPB draft board, in the order players should come off.

    python3 board160.py            # print it
    python3 board160.py --csv      # write ../RPB-DRAFT-160.csv
    python3 board160.py --selftest

COMPOSITION, as asked for: exactly 10 QB, 10 TE, 10 K and 10 D/ST; the remaining 120 slots are
running backs and receivers. Keepers are excluded — they never reach the draft — so every name here
is one you can actually pick. 160 slots against 147 real picks leaves ~13 of cushion at the bottom.

ORDERING
  QB, RB, WR and TE are ordered by VBD (points above the last player at that position who gets
  drafted), which is the only honest way to compare across positions. That comes from rpb_score.py:
  FFA's own projections scored under RPB's rules, with return work priced in.

  K and D/ST are DELIBERATELY NOT ordered by VBD, and this is the one override in the file. Their
  VBD is enormous and meaningless: with 32 defenses for 10 starting slots, CBS's projections put the
  Texans +93 over the 11th defense, which would rank them 6th overall. That number is real and
  useless, because preseason projections cannot tell you which defense will actually finish first —
  the 2025 actuals spread 3.9 pts/week where projections show 1.1 (see DST-STREAMING.md). So K and
  D/ST are pinned to the last two rounds, matching the plan and mc13's finding that this is what
  actually happens. Within those rounds they are ordered by projected points.
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
SLOTS, TEAMS = 160, 10
CAP = {"QB": 10, "TE": 10, "K": 10, "DST": 10}


def load():
    board = list(csv.DictReader((ROOT / "RPB-BOARD.csv").open()))
    for r in board:
        r["vbd"], r["rpb"] = float(r["vbd"]), float(r["rpb"])
        r["kept"] = r["kept"] == "True"
    kd = json.loads((D / "cbs-k-dst-2026.json").read_text())
    # Nick's must/shy lists. The points board cannot see them, and it will happily rank a
    # shy-away player highly -- Rashee Rice and Devon Achane both land inside the top 30 on
    # value alone. The tag is the FFA layer riding on top, exactly as it does in DRAFT-DAY.md.
    notes = json.loads((D / "notes.json").read_text())["shared"]
    tag = {}
    for v in notes.values():
        if v.get("call") in ("must", "shy"):
            tag[v["name"].lower()] = "MUST" if v["call"] == "must" else "SHY"
    def ffa(name):
        n = name.lower()
        for kk, vv in tag.items():
            if kk.split()[0] == n.split()[0] and kk.split()[-1].strip(".") == n.split()[-1].strip("."):
                return vv
        return ""
    for r in board:
        r["ffa"] = ffa(r["name"])
    return [r for r in board if not r["kept"]], kd


def build():
    live, kd = load()
    skill = [r for r in live if r["pos"] in ("QB", "RB", "WR", "TE")]
    skill.sort(key=lambda r: -r["vbd"])

    picked, seen = [], {"QB": 0, "TE": 0}
    n_skill = SLOTS - CAP["K"] - CAP["DST"]
    for r in skill:
        if len(picked) >= n_skill:
            break
        if r["pos"] in seen:
            if seen[r["pos"]] >= CAP[r["pos"]]:
                continue
            seen[r["pos"]] += 1
        picked.append(dict(name=r["name"], pos=r["pos"], team=r["team"], rpb=r["rpb"],
                           vbd=r["vbd"], adp=r["hpprAdp"], ffa=r.get("ffa", "")))

    for d in kd["defenses"][:CAP["DST"]]:
        picked.append(dict(name=d["name"], pos="DST", team=d["team"], rpb=d["rpb"], vbd="", adp="", ffa=""))
    for k in kd["kickers"][:CAP["K"]]:
        picked.append(dict(name=k["name"], pos="K", team=k["team"], rpb=k["rpb"], vbd="", adp="", ffa=""))

    for i, p in enumerate(picked, 1):
        rd, j = divmod(i - 1, TEAMS)
        p["rank"] = i
        p["slot"] = f"{rd + 1}.{j + 1:02d}"
        p["mine"] = (rd % 2 == 0 and j == 1) or (rd % 2 == 1 and j == TEAMS - 2)
    return picked


def selftest():
    b = build()
    assert len(b) == SLOTS, len(b)
    from collections import Counter
    c = Counter(p["pos"] for p in b)
    for pos, cap in CAP.items():
        assert c[pos] == cap, f"{pos}: {c[pos]} != {cap}"
    assert c["RB"] + c["WR"] == SLOTS - sum(CAP.values()) == 120
    # K and D/ST must live in the last two rounds, never earlier.
    assert all(p["rank"] > 140 for p in b if p["pos"] in ("K", "DST"))
    # Skill players must be in non-increasing VBD order.
    v = [p["vbd"] for p in b if p["pos"] in ("QB", "RB", "WR", "TE")]
    assert all(a >= z for a, z in zip(v, v[1:])), "skill board is not sorted by VBD"
    assert any(p.get("ffa") == "SHY" for p in b), "FFA tags did not attach"
    # No keeper may appear — they never reach the draft.
    kept = {x["player"] for x in json.loads((D / "keepers-rpb.json").read_text())["keepers"]}
    assert not (kept & {p["name"] for p in b}), kept & {p["name"] for p in b}
    print("selftest OK")


# ---------------------------------------------------------------------------
# The TARGET board: what to actually draft from, as opposed to what players are
# worth. Three things separate it from the value board above.
#
#   1. Shy-aways are REMOVED, not demoted. Nick's fades are not tie-breakers.
#   2. Nobody sits far below his ADP. If the room will take him 30 picks before
#      his value says, listing him at his value rank just means losing him. Each
#      player is pulled up to min(valueRank, adp + CUSHION).
#   3. Must-drafts get a one-round bump, which is exactly how Nick words it
#      himself -- "round six, a round ahead of his round-seven ADP".
#
# The bump is deliberately ONE round. Reaching further costs more than the FFA
# layer is worth; the take-zone shelf is 7.2 points wide and a round of ADP is
# worth about that.
MUST_BUMP, ADP_CUSHION = 10, 5
# A must-draft bump breaks ties and near-ties. It must never overturn a large value gap: Bowers is
# a must-draft at +93.7 and Gibbs is +164, and no amount of Nick liking a tight end makes that a
# 70-point argument. A player may therefore only jump ahead of players within VBD_TOL of him.
VBD_TOL = 25.0
# One plan rule is not derivable from VBD and has to be enforced by name. Taking Bowers at 1.02 over
# an elite back cost -81.8 across paired sims; his +57.9 edge only exists once the top of the RB
# board is gone. draft_day.py asserts the same gate on index.html.
ROUND2_ONLY = {"Brock Bowers"}
# Nick's must-draft list carries seven quarterbacks, and bumping all of them drags QB into round 2.
# That is exactly backwards here: six teams keep a quarterback, only four are drafted, and the whole
# QB1-to-replacement gap is 30 points (1.8/week). The tier cannot run dry, so a QB is never worth
# reaching for. The plan's standing rule -- never a QB before round 4 -- is enforced as a floor.
POS_FLOOR = {"QB": 4}


def targets():
    live, kd = load()
    skill = [r for r in live if r["pos"] in ("QB", "RB", "WR", "TE") and r.get("ffa") != "SHY"]
    skill.sort(key=lambda r: -r["vbd"])
    for i, r in enumerate(skill, 1):
        adp = float(r["hpprAdp"]) if r["hpprAdp"] not in ("", "999") else 999.0
        r["_v"] = i
        r["_d"] = min(i, adp + ADP_CUSHION) - (MUST_BUMP if r.get("ffa") == "MUST" else 0)
    # Floor each player at the earliest slot his own value can justify.
    vbds = [r["vbd"] for r in skill]
    for r in skill:
        earliest = next(j for j, v in enumerate(vbds, 1) if v <= r["vbd"] + VBD_TOL)
        r["_d"] = max(r["_d"], earliest)
        if r["name"] in ROUND2_ONLY:
            r["_d"] = max(r["_d"], TEAMS + 1)
        if r["pos"] in POS_FLOOR:
            r["_d"] = max(r["_d"], (POS_FLOOR[r["pos"]] - 1) * TEAMS + 1)
    skill.sort(key=lambda r: (r["_d"], -r["vbd"]))

    picked, seen = [], {"QB": 0, "TE": 0}
    for r in skill:
        if len(picked) >= SLOTS - CAP["K"] - CAP["DST"]:
            break
        if r["pos"] in seen:
            if seen[r["pos"]] >= CAP[r["pos"]]:
                continue
            seen[r["pos"]] += 1
        picked.append(dict(name=r["name"], pos=r["pos"], team=r["team"], rpb=r["rpb"],
                           vbd=r["vbd"], adp=r["hpprAdp"], ffa=r.get("ffa", ""), valueRank=r["_v"]))
    for d in kd["defenses"][:CAP["DST"]]:
        picked.append(dict(name=d["name"], pos="DST", team=d["team"], rpb=d["rpb"],
                           vbd="", adp="", ffa="", valueRank=""))
    for k in kd["kickers"][:CAP["K"]]:
        picked.append(dict(name=k["name"], pos="K", team=k["team"], rpb=k["rpb"],
                           vbd="", adp="", ffa="", valueRank=""))
    for i, p in enumerate(picked, 1):
        rd, j = divmod(i - 1, TEAMS)
        p["rank"] = i
        p["slot"] = f"{rd + 1}.{j + 1:02d}"
        p["mine"] = (rd % 2 == 0 and j == 1) or (rd % 2 == 1 and j == TEAMS - 2)
    return picked


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    tgt = "--targets" in sys.argv
    board = targets() if tgt else build()
    if "--csv" in sys.argv:
        dest = ROOT / ("RPB-TARGETS-160.csv" if tgt else "RPB-DRAFT-160.csv")
        cols = (["rank", "slot", "pos", "name", "team", "rpb", "vbd", "adp", "ffa", "valueRank", "mine"]
                if tgt else ["rank", "slot", "pos", "name", "team", "rpb", "vbd", "adp", "ffa", "mine"])
        with dest.open("w") as f:
            f.write(",".join(cols) + "\n")
            for p in board:
                f.write(",".join(str(p[c]).replace(",", " ") for c in cols) + "\n")
        print(f"wrote {dest} — {len(board)} players")
        sys.exit(0)
    rd = 0
    for p in board:
        r = (p["rank"] - 1) // TEAMS + 1
        if r != rd:
            rd = r
            print(f"\n--- ROUND {rd} ---")
        star = " <<< YOU" if p["mine"] else ""
        mark = {"MUST": " *", "SHY": " X"}.get(p.get("ffa", ""), "  ")
        v = f"{p['vbd']:+7.1f}" if p["vbd"] != "" else "      —"
        print(f"{p['rank']:>4} {p['slot']:<6} {p['pos']:<4} {p['name'][:24]:<25}{p['team']:<5}"
              f"{p['rpb']:>7.1f}{v}{mark}{star}")

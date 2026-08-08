#!/usr/bin/env python3
"""Score FFA's own projections under RPB's actual scoring rules.

The point: keep Nick's view of the players (FFA's stat-line projections are the input) and change
only the SCORING (RPB's CBS settings). Nothing here re-ranks a player on opinion — it re-prices the
same projected stat line under a different rulebook.

    python3 rpb_score.py QB          # one position, the board
    python3 rpb_score.py QB --movers # what RPB scoring does vs vanilla half-PPR
    python3 rpb_score.py --selftest

INPUTS
  ../data/ffa-proj-2026.json    FFA Detailed Projections — stat lines, 723 players
  ../data/keepers-rpb.json      who never reaches the draft

WHAT IS EXACT AND WHAT IS MODELLED
  EXACT — everything that scales off a season total: passing/rushing/receiving yards, every TD,
  interceptions, receptions. This is the great majority of every score.

  MODELLED — the three bonus families, because they depend on the per-GAME distribution and FFA
  projects season totals only:
    * +3 for a 300-yard passing game, +3 for a 100-yard rushing or receiving game. Estimated with a
      normal approximation around the per-game mean. The standard deviations below are the only
      free parameters in this file.
    * TD distance bonuses (+1 at 40yd, +2 at 60, +3 at 80). Applied as a flat expected value per TD
      from league-average long-TD rates.
  Run with --no-bonus to see the exact-only board. The ORDER barely moves; the bonuses are worth a
  few points, not tens.

  NOT MODELLED AT ALL — individual kick/punt return yards and return TDs, which RPB scores
  (IPRYd 0.1/yd +3 at 100, IKRYd 0.05/yd +3 at 150, return TD 6 + distance). FFA does not project
  returns, so a designated returner is UNDERVALUED by this board. That is a real edge and it is
  called out rather than silently absorbed.
"""
import json, math, sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
GAMES = 17

# RPB, from the CBS league rules page (rpbowl.football.cbssports.com/rules), read 2026-08-07.
RPB = dict(passYd=0.05, passTD=4.0, passInt=-3.0,
           rushYd=0.10, rushTD=6.0, recYd=0.10, recTD=6.0, rec=0.5, fumLost=-3.0)
# Vanilla half-PPR, for the comparison only. The differences that matter: passing yards are 0.04
# here and 0.05 in RPB, and an interception is -2 here and -3 in RPB.
HALF = dict(passYd=0.04, passTD=4.0, passInt=-2.0,
            rushYd=0.10, rushTD=6.0, recYd=0.10, recTD=6.0, rec=0.5, fumLost=-2.0)

# Per-game standard deviations for the yardage-bonus model. Rough, and deliberately visible.
SD = {"pass": 75.0, "rush": 35.0, "rec": 35.0}
# Expected distance-bonus points per touchdown, from league-average long-TD rates.
TD_BONUS = {"pass": 0.14, "rush": 0.05, "rec": 0.20}


def _phi(z):
    """P(Z > z) for a standard normal."""
    return 0.5 * math.erfc(z / math.sqrt(2))


def games_over(total, threshold, sd):
    """Expected number of games clearing a yardage threshold, normal approx around the mean."""
    if total <= 0:
        return 0.0
    return GAMES * _phi((threshold - total / GAMES) / sd)


def score(p, rules, bonus=True):
    s = (p["passYd"] * rules["passYd"] + p["passTD"] * rules["passTD"]
         + p["passInt"] * rules["passInt"]
         + p["rushYd"] * rules["rushYd"] + p["rushTD"] * rules["rushTD"]
         + p["recYd"] * rules["recYd"] + p["recTD"] * rules["recTD"]
         + p["rec"] * rules["rec"])
    if bonus and rules is RPB:
        s += 3.0 * games_over(p["passYd"], 300, SD["pass"])
        s += 3.0 * games_over(p["rushYd"], 100, SD["rush"])
        s += 3.0 * games_over(p["recYd"], 100, SD["rec"])
        s += (p["passTD"] * TD_BONUS["pass"] + p["rushTD"] * TD_BONUS["rush"]
              + p["recTD"] * TD_BONUS["rec"])
    if rules is RPB:
        # Return work is RPB scoring the half-PPR baseline does not have, bonus flag or not.
        s += p.get("retPts", 0.0)
    return s


def return_points(r):
    """RPB pays individual return work. Nobody's projections include it — see return-roles-2026.json.

    Punt return TDs are almost always long, so the distance bonus is applied as a flat +2.
    """
    pts = r.get("puntRetYd", 0) * 0.1 + r.get("kickRetYd", 0) * 0.05
    pts += (r.get("puntRetTD", 0) + r.get("kickRetTD", 0)) * (6.0 + 2.0)
    return pts


def load():
    proj = json.loads((D / "ffa-proj-2026.json").read_text())["players"]
    for p in proj:
        p.setdefault("fumLost", 0.0)
        p.setdefault("retPts", 0.0)
    returns = json.loads((D / "return-roles-2026.json").read_text())["players"]
    by_name = {key(p["name"]): p for p in proj}
    for r in returns:
        p = by_name.get(key(r["name"]))
        if p is None:
            print(f"!! return-roles lists {r['name']}, who is not in the FFA projections", file=sys.stderr)
            continue
        p["retPts"] = return_points(r)
    keep = json.loads((D / "keepers-rpb.json").read_text())
    return proj, keep


def key(n):
    return "".join(c for c in n.lower() if c.isalpha() or c == " ").replace(" jr", "").strip()


def kept_names(keep):
    return {key(x["player"]) for x in keep["keepers"]}


TEAMS = 10
STARTERS = {"QB": 1, "RB": 2, "WR": 3, "TE": 1}


def drafted_at(pos, keep):
    """How many of a position actually get drafted = league starting slots minus the kept ones.

    This is what sets replacement level, and it is the whole reason QB is cheap in RPB: six teams
    keep a quarterback, so only four are ever drafted and the fifth-best is free.
    """
    kept = sum(1 for x in keep["keepers"] if x["pos"] == pos)
    return max(TEAMS * STARTERS[pos] - kept, 1)


def selftest():
    proj, keep = load()
    allen = next(p for p in proj if p["name"] == "Josh Allen")
    # 3959 pass yd, 30 pass TD, 12 INT, 538 rush yd, 11.5 rush TD
    base = score(allen, RPB, bonus=False)
    exact = 3959 * .05 + 30 * 4 + 12 * -3 + 538 * .1 + 11.5 * 6
    assert abs(base - exact) < 1e-6, f"{base} != {exact}"
    # RPB must pay a pocket passer more than half-PPR does, purely on the yardage rate.
    assert score(allen, RPB, bonus=False) > score(allen, HALF, bonus=False)
    # A receiver with no return role must score identically under both rulebooks — RPB only differs
    # on passing yards, interceptions, fumbles and returns, none of which he accumulates.
    wr = next(p for p in proj if p["name"] == "Puka Nacua")
    assert wr["retPts"] == 0.0
    assert abs(score(wr, RPB, bonus=False) - score(wr, HALF, bonus=False)) < 1e-9
    # A returner must NOT: 300 punt return yards and half a return TD is 34 points RPB pays and
    # vanilla half-PPR does not. This is the whole Parker Washington argument.
    pw = next(p for p in proj if p["name"].startswith("Parker Washington"))
    assert abs(pw["retPts"] - 34.0) < 1e-6, pw["retPts"]
    assert score(pw, RPB, bonus=False) - score(pw, HALF, bonus=False) > 30
    # Bonus model sanity: more yards must never mean fewer bonus games.
    assert games_over(4500, 300, SD["pass"]) > games_over(3000, 300, SD["pass"])
    assert games_over(0, 100, SD["rush"]) == 0.0
    print("selftest OK")


def full_board(proj, keep, bonus=True):
    """Every player, scored, with VBD measured against his own position's replacement level."""
    gone = kept_names(keep)
    by_pos = {}
    for p in proj:
        if p["pos"] in STARTERS:
            by_pos.setdefault(p["pos"], []).append(p)

    out = []
    for pos, players in by_pos.items():
        rows = sorted(((p, score(p, RPB, bonus), score(p, HALF, bonus=False)) for p in players),
                      key=lambda t: -t[1])
        half_rank = {id(p): i for i, (p, _, _) in
                     enumerate(sorted(rows, key=lambda t: -t[2]), 1)}
        live = [t for t in rows if key(t[0]["name"]) not in gone]
        need = drafted_at(pos, keep)
        repl = live[need][1] if len(live) > need else live[-1][1]
        for i, (p, r, h) in enumerate(rows, 1):
            out.append(dict(name=p["name"], pos=pos, team=p["team"], posRank=i,
                            halfPosRank=half_rank[id(p)], rpb=round(r, 1), half=round(h, 1),
                            delta=round(r - h, 1), vbd=round(r - repl, 1),
                            kept=key(p["name"]) in gone, hpprAdp=p.get("hpprAdp", 0)))
    out.sort(key=lambda d: -d["vbd"])
    for i, d in enumerate(out, 1):
        d["overallRank"] = i
    return out


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)

    if "--csv" in sys.argv:
        proj, keep = load()
        board = full_board(proj, keep, bonus="--no-bonus" not in sys.argv)
        cols = ["overallRank", "pos", "posRank", "halfPosRank", "name", "team",
                "rpb", "half", "delta", "vbd", "hpprAdp", "kept"]
        dest = Path(__file__).resolve().parent.parent / "RPB-BOARD.csv"
        with dest.open("w") as f:
            f.write(",".join(cols) + "\n")
            for d in board:
                f.write(",".join(str(d[c]).replace(",", " ") for c in cols) + "\n")
        print(f"wrote {dest} — {len(board)} players")
        sys.exit(0)

    pos = next((a.upper() for a in sys.argv[1:] if not a.startswith("-")), "QB")
    bonus = "--no-bonus" not in sys.argv
    proj, keep = load()
    gone = kept_names(keep)

    rows = []
    for p in proj:
        if p["pos"] != pos:
            continue
        r = score(p, RPB, bonus)
        h = score(p, HALF, bonus=False)
        rows.append((p, r, h, key(p["name"]) in gone))
    rows.sort(key=lambda t: -t[1])

    if "--movers" in sys.argv:
        half_order = {id(p): i for i, (p, _, _, _) in
                      enumerate(sorted(rows, key=lambda t: -t[2]), 1)}
        print(f"{pos} — what RPB's rules do to FFA's own order (+ = helped by RPB)\n")
        print(f"{'RPB':<5}{'HALF':<6}{'MOVE':<7}{'PLAYER':<24}{'RPB pts':>9}{'vs half':>9}")
        for i, (p, r, h, _) in enumerate(rows[:30], 1):
            j = half_order[id(p)]
            mv = j - i
            print(f"{i:<5}{j:<6}{('+' if mv>0 else '')+str(mv):<7}{p['name'][:23]:<24}{r:>9.1f}{r-h:>+9.1f}")
        sys.exit(0)

    live = [t for t in rows if not t[3]]
    need = drafted_at(pos, keep)
    repl = live[need][1] if len(live) > need else live[-1][1]

    print(f"{pos} — FFA projections scored under RPB rules"
          f"{'' if bonus else '  (EXACT ONLY, bonuses off)'}\n")
    print(f"{'#':<4}{'PLAYER':<24}{'TM':<5}{'RPB':>8}{'half':>8}{'Δ':>7}{'VBD':>8}  status")
    for i, (p, r, h, kept) in enumerate(rows[:28], 1):
        tag = "KEPT — off the board" if kept else ""
        print(f"{i:<4}{p['name'][:23]:<24}{p['team']:<5}{r:>8.1f}{h:>8.1f}{r-h:>+7.1f}"
              f"{r-repl:>8.1f}  {tag}")
    print(f"\nreplacement = the best {pos} nobody drafts "
          f"({need} go in a 10-team RPB draft) = {repl:.1f} pts")
    print("VBD is points above that. Kept players are shown but excluded from replacement.")

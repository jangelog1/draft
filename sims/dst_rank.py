#!/usr/bin/env python3
"""Rank defenses under RPB's own scoring — season, and week by week.

Everything else in this repo scored D/ST by taking someone else's projection and doubling it. That
is fine for magnitudes and useless for ORDER, because a flat multiplier moves every defense the
same amount. This recomputes from the raw projected stat line — sacks, turnovers, points allowed —
using RPB's scoring rules, so a league that pays heavily for turnovers ranks differently from one
that pays for shutouts.

    python3 dst_rank.py             # season + weeks 1-3 + the 3-week stream plan
    python3 dst_rank.py --week 2    # one week only
    python3 dst_rank.py --formula   # show the formula and inputs, rank nothing
    python3 dst_rank.py --selftest  # check the arithmetic

INPUTS
  ../data/dst-scoring-rpb.json       RPB's D/ST scoring rules (VERIFIED from CBS, 2026-08-07)
  ../data/dst-projections-2026.json  4for4 season stat lines — TOP 10 TEAMS ONLY, see the caveat
  ../data/dst-weeks-2026.json        raw Vegas lines for weeks 1-3

WEEKLY METHOD
  There is no public per-defense per-week stat projection, so a week is scored from the opponent's
  Vegas implied team total, which is the best available predictor of D/ST scoring. A defense's
  season rate is scaled by how much softer or harder that week's opponent is than a league-average
  offense (~22.0 implied points). Low opponent total = boost, high = penalty. This is a model, not
  a projection anyone published — the implied totals underneath it are the hard part and they are
  real.

  The implied totals are COMPUTED here from the published line rather than stored by hand. The old
  dst-week1-2026.json stored them by hand and had one game inverted for months.
"""
import json, sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
LEAGUE_AVG_IMPLIED = 22.0          # rough mean implied team total across a full slate
GAMES = 17


def load():
    return (json.loads((D / "dst-scoring-rpb.json").read_text()),
            json.loads((D / "dst-projections-2026.json").read_text()),
            json.loads((D / "dst-weeks-2026.json").read_text()))


def implied(game):
    """(away_implied, home_implied) from total and spread. The favorite gets the half-spread."""
    half, edge = game["total"] / 2, game["spread"] / 2
    if game["fav"] == game["home"]:
        return half - edge, half + edge
    if game["fav"] == game["away"]:
        return half + edge, half - edge
    raise ValueError(f"{game['fav']} is not in {game['away']} at {game['home']}")


def matchups(games):
    """{defense: (opponent, opponent's implied total)} for one week's slate."""
    out = {}
    for g in games:
        a, h = implied(g)
        out[g["home"]] = (g["away"], a)      # home defense faces the away offense
        out[g["away"]] = (g["home"], h)
    return out


def pa_points(pa_per_game, tiers):
    """Points-allowed bonus for a single game at that average."""
    for t in tiers:
        if pa_per_game <= t["max"]:
            return t["pts"]
    return tiers[-1]["pts"]


def season_points(t, rules):
    """Recompute a season total from the raw stat line under RPB rules."""
    e = rules["perEvent"]
    # 4for4 gives combined forced turnovers; split them the way they historically land,
    # a little under two-thirds interceptions. Both are worth the same in most CBS setups,
    # so the split only matters if a league prices them differently.
    ints = t["to"] * 0.6
    fums = t["to"] * 0.4
    pts = t["sacks"] * e["sack"] + ints * e["interception"] + fums * e["fumbleRecovery"]
    # RPB pays the forced fumble separately from the recovery, so a fumble the defense both
    # forces and recovers is worth 4 rather than 3. Most recovered fumbles are self-forced.
    pts += fums * e.get("forcedFumble", 0.0)
    # Defensive touchdowns are not in the 4for4 line. League-average is roughly 3 a season;
    # applying the same figure to everyone keeps it from distorting the ORDER.
    pts += 3.0 * e["defensiveTD"]
    pts += GAMES * pa_points(t["pa"] / GAMES, rules["pointsAllowedTiers"])
    return pts * rules.get("multiplier", 1.0)


def week_points(season_pts, opp_implied):
    """Scale a season rate by how soft that week's opponent is versus league average."""
    return (season_pts / GAMES) * (LEAGUE_AVG_IMPLIED / opp_implied)


def week_board(byteam, games):
    """[(defense, opponent, projected points, opponent implied)] best first."""
    rows = [(d, opp, week_points(byteam[d], imp), imp)
            for d, (opp, imp) in matchups(games).items() if d in byteam]
    return sorted(rows, key=lambda r: -r[2])


def selftest():
    rules, proj, wk = load()
    # The line arithmetic, against a game whose implied totals three sources agree on.
    jax = next(g for g in wk["weeks"]["1"] if g["home"] == "Jaguars")
    away, home = implied(jax)
    assert (away, home) == (16.5, 24.0), f"Browns/Jaguars implied {away}/{home}, expected 16.5/24.0"
    # Favorite direction: the away favorite must get the HIGHER total.
    bills = next(g for g in wk["weeks"]["1"] if g["away"] == "Bills")
    a, h = implied(bills)
    assert a > h, "an away favorite should carry the higher implied total"
    # The game the old file got backwards. Miami's DEFENSE faces a Raiders offense at 22.0.
    for wknum, games in wk["weeks"].items():
        assert len(games) == 16, f"week {wknum} has {len(games)} games, expected 16"
        m = matchups(games)
        assert len(m) == 32, f"week {wknum} covers {len(m)} teams, expected 32"
    assert matchups(wk["weeks"]["1"])["Dolphins"] == ("Raiders", 22.0)
    # Scoring: softer opponent must project higher for the same unit.
    assert week_points(300, 16.5) > week_points(300, 23.0)
    # Points-allowed tiers are ordered and the lookup picks the first that fits.
    assert pa_points(2, rules["pointsAllowedTiers"]) > pa_points(30, rules["pointsAllowedTiers"])
    print("selftest OK")


if __name__ == "__main__":
    rules, proj, wk = load()

    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)

    if not rules.get("VERIFIED"):
        print("!! " + "=" * 76)
        print("!! dst-scoring-rpb.json is NOT VERIFIED — these are CBS defaults, not RPB's rules.")
        print("!! " + rules["_where"])
        print("!! Set VERIFIED:true once the real numbers are in. Order below may be wrong.")
        print("!! " + "=" * 76 + "\n")

    if "--formula" in sys.argv:
        e = rules["perEvent"]
        print("FORMULA — RPB D/ST points")
        print(f"  sacks x {e['sack']} + INT x {e['interception']} + fumble rec x {e['fumbleRecovery']}")
        print(f"  + defensive TD x {e['defensiveTD']} + safety x {e['safety']} + blocked kick x {e['blockedKick']}")
        print("  + per-game points-allowed tier bonus:")
        for t in rules["pointsAllowedTiers"]:
            print(f"      <= {t['max']:>3} pts allowed -> {t['pts']:+.1f}")
        print(f"  all of it x {rules.get('multiplier',1)} (RPB doubles D/ST through the values, not a multiplier)")
        print("\nweek = (season points / 17) x (22.0 / opponent implied team total)")
        print("opponent implied team total = total/2 -/+ spread/2, computed from the stored line")
        print("\nSOURCES")
        print(" ", proj["source"]); print(" ", wk["source"])
        sys.exit(0)

    season = sorted(((t["team"], season_points(t, rules)) for t in proj["teams"]),
                    key=lambda r: -r[1])
    byteam = dict(season)

    print("FULL SEASON — RPB scoring, top 10\n")
    print(f"{'#':<3}{'DEFENSE':<12}{'RPB pts':>9}{'per wk':>9}")
    for i, (t, p) in enumerate(season[:10], 1):
        if i == 7: print("   " + "-" * 28 + "  cliff")
        print(f"{i:<3}{t:<12}{p:>9.1f}{p/GAMES:>9.1f}")
    print("\n  These are PROJECTIONS and they compress: 1st to 10th is only ~1.1 pts/week here,")
    print("  where your real 2025 results spread 3.9. Trust this list for who changed personnel,")
    print("  not for how far apart they are. See data/dst-actuals-2025.json.")

    weeks = [a.split("=")[1] for a in sys.argv if a.startswith("--week=")] or \
            ([sys.argv[sys.argv.index("--week") + 1]] if "--week" in sys.argv else
             sorted(wk["weeks"], key=int))

    totals, seen, ran = {}, {}, []
    for w in weeks:
        games = wk["weeks"].get(str(w))
        if not games:
            print(f"\nno lines stored for week {w}"); continue
        ran.append(str(w))
        rows = week_board(byteam, games)
        for d, _, p, _ in rows:
            totals[d] = totals.get(d, 0.0) + p
            seen[d] = seen.get(d, 0) + 1
        soft = "  (LOOK-AHEAD line — will move a lot)" if str(w) != "1" else ""
        print(f"\nWEEK {w} — RPB scoring{soft}\n")
        print(f"{'#':<3}{'DEFENSE':<12}{'vs':<12}{'RPB pts':>9}{'opp impl':>10}")
        for i, (t, o, p, imp) in enumerate(rows[:10], 1):
            print(f"{i:<3}{t:<12}{o:<12}{p:>9.1f}{imp:>10.1f}")

    # Only defenses with a line in every week ran are comparable on a combined total.
    if len(ran) > 1:
        run = sorted(((d, p) for d, p in totals.items() if seen[d] == len(ran)), key=lambda r: -r[1])
        print(f"\nWEEKS {'-'.join(ran)} COMBINED — who to draft at 15.02\n")
        print(f"{'#':<3}{'DEFENSE':<12}{'total':>9}{'per wk':>9}")
        for i, (t, p) in enumerate(run[:10], 1):
            print(f"{i:<3}{t:<12}{p:>9.1f}{p/len(ran):>9.1f}")

    print("\nCoverage is limited to the defenses in dst-projections-2026.json (top 10 only).")
    print("Widen that file to widen every board above.")

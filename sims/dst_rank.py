#!/usr/bin/env python3
"""Rank defenses under RPB's own scoring — week 1 and full season.

Everything else in this repo scored D/ST by taking someone else's projection and doubling it. That
is fine for magnitudes and useless for ORDER, because a flat multiplier moves every defense the
same amount. This recomputes from the raw projected stat line — sacks, turnovers, points allowed —
using RPB's scoring rules, so a league that pays heavily for turnovers ranks differently from one
that pays for shutouts.

    python3 dst_rank.py            # both boards
    python3 dst_rank.py --formula  # show the formula and inputs, rank nothing

INPUTS
  ../data/dst-scoring-rpb.json     RPB's D/ST scoring rules   <- the one that still needs verifying
  ../data/dst-projections-2026.json  4for4 season stat lines
  ../data/dst-week1-2026.json      Vegas implied totals + FantasyPros week-1 projections

WEEK 1 METHOD
  There is no public per-defense week-1 stat projection, so week 1 is scored from the opponent's
  Vegas implied team total, which is the best available predictor of D/ST scoring. A defense's
  season rate is scaled by how much softer or harder its week-1 opponent is than a league-average
  offense (~22.0 implied points). Defenses facing a low total get a boost, high total a penalty.
  This is a model, not a projection anyone published — the implied totals underneath it are the
  hard part and they are real.
"""
import json, sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
LEAGUE_AVG_IMPLIED = 22.0          # rough mean implied team total across the week-1 slate
GAMES = 17


def load():
    return (json.loads((D / "dst-scoring-rpb.json").read_text()),
            json.loads((D / "dst-projections-2026.json").read_text()),
            json.loads((D / "dst-week1-2026.json").read_text()))


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


def week1_points(season_pts, opp_implied):
    """Scale a season rate by how soft the week-1 opponent is versus league average."""
    per_game = season_pts / GAMES
    return per_game * (LEAGUE_AVG_IMPLIED / opp_implied)


if __name__ == "__main__":
    rules, proj, wk1 = load()

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
        print(f"  all of it x {rules.get('multiplier',1)} (RPB doubles D/ST)")
        print("\nWEEK 1 = (season points / 17) x (22.0 / opponent implied team total)")
        print("\nSOURCES")
        print(" ", proj["source"]); print(" ", wk1["source"])
        sys.exit(0)

    season = [(t["team"], season_points(t, rules)) for t in proj["teams"]]
    season.sort(key=lambda r: -r[1])
    print("FULL SEASON — RPB scoring, top 10\n")
    print(f"{'#':<3}{'DEFENSE':<12}{'RPB pts':>9}{'per wk':>9}")
    for i, (t, p) in enumerate(season[:10], 1):
        if i == 7: print("   " + "-" * 28 + "  cliff")
        print(f"{i:<3}{t:<12}{p:>9.1f}{p/GAMES:>9.1f}")

    byteam = dict(season)
    rows = []
    for g in wk1["games"]:
        s = byteam.get(g["def"])
        if s is None:                      # not in the top-10 season file
            continue
        rows.append((g["def"], g["opp"], week1_points(s, g["oppImplied"]), g["oppImplied"]))
    rows.sort(key=lambda r: -r[2])
    print("\nWEEK 1 — RPB scoring, top 10\n")
    print(f"{'#':<3}{'DEFENSE':<12}{'vs':<12}{'RPB pts':>9}{'opp impl':>10}")
    for i, (t, o, p, imp) in enumerate(rows[:10], 1):
        print(f"{i:<3}{t:<12}{o:<12}{p:>9.1f}{imp:>10.1f}")
    print("\nWeek 1 covers only defenses present in both files. Add more teams to")
    print("dst-projections-2026.json to widen it.")

#!/usr/bin/env python3
"""Clean FantasyPros custom-cheat-sheet import list: one player per line, rank order, nothing else.

    python3 sims/fp_import.py > RPB-FP-IMPORT.txt

FantasyPros' importer matches ONE PLAYER PER LINE. Headers, separators and note lines all become
bogus rows, and some of them silently match the wrong player -- "NICK: ... Lions dome" matched the
Detroit Lions D/ST, and a "KEY" header matched a Denver safety named Devon Key. So this emits names
only. Keep RPB-TARGETS-NOTES.txt open beside the draft as the reading copy.
"""
import csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# FantasyPros spells a handful of these differently from FFA. Anything not listed here that the
# importer flags can be fixed in its own dropdown -- it tells you which rows failed.
ALIAS = {
    "Ken Walker": "Kenneth Walker III",
    "Travis Etienne Jr.": "Travis Etienne",
    "Harold Fannin Jr.": "Harold Fannin",
    "Cam Little": "Cameron Little",
}
DST = {"Texans": "Houston Texans", "Broncos": "Denver Broncos", "Eagles": "Philadelphia Eagles",
       "Rams": "Los Angeles Rams", "Seahawks": "Seattle Seahawks", "Vikings": "Minnesota Vikings",
       "Steelers": "Pittsburgh Steelers", "Lions": "Detroit Lions",
       "Chargers": "Los Angeles Chargers", "Falcons": "Atlanta Falcons"}

for r in csv.DictReader((ROOT / "RPB-TARGETS-160.csv").open()):
    n = r["name"]
    if r["pos"] == "DST":
        n = DST[n.replace(" D/ST", "")]
    print(ALIAS.get(n, n))

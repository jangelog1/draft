#!/usr/bin/env python3
"""Two draft-day artifacts from the target board.

    python3 sims/cheatsheet.py          # combined ranked list with inline advice (print/read)
    python3 sims/cheatsheet.py --notes  # Player<TAB>note, short enough for FantasyPros My Notes

FantasyPros' My Notes field is Premium and MANUAL -- you double-click a cell and type. There is no
spreadsheet import for notes, only importing from another of your own cheat sheets. So --notes is
deliberately limited to the players where a note changes a decision, not all 160.
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "RPB-TARGETS-160.csv").open()))
plan = json.loads((ROOT / "data/plan-rpb.json").read_text())
TAKE = set(plan["takeZone"])

# Hand-written because these are decisions, not data. Kept under ~120 chars to fit a note cell.
NOTE = {
 "Jahmyr Gibbs":"1.02 TAKE THE BACK. +164 VBD, biggest edge in the draft. Bijan if Gibbs gone.",
 "Bijan Robinson":"1.02 TAKE THE BACK. +164 VBD. Handcuff is Brian Robinson Jr (R14).",
 "Amon-Ra St. Brown":"Only WR Nick breaks RB-RB for -- and ONLY outside top 4. You pick 1.02, so NOT you.",
 "Brock Bowers":"THE PICK IF HE FALLS TO 2.09. +57.9 over the best back. NEVER at 1.02 (-81.8).",
 "Tyler Warren":"BOWERS FALLBACK. +44.7 at ADP 59 = your 6.09. Take him if Bowers went.",
 "Saquon Barkley":"TAKE ZONE. Nick's #1 R2 back. Playoff-SOS knock does NOT apply -- RPB has no playoffs.",
 "Kenneth Walker III":"TAKE ZONE. FORMAT SPLIT: Nick prefers Walker over Chase Brown in HALF PPR. That's you.",
 "Chase Brown":"TAKE ZONE + must-draft. Full-PPR pick per Nick; Walker edges him in your half-PPR.",
 "Omarion Hampton":"TAKE ZONE. If you get him, Keaton Mitchell (R14) is the handcuff double-dip.",
 "Derrick Henry":"TAKE ZONE but take him LAST of the five. Watch, not a buy -- declining targets.",
 "Parker Washington":"BIGGEST EDGE. Punt returner: 5th in NFL ret yds, LED league in ret TDs. RPB pays that, FFA doesn't. +34 pts nobody prices. Take 6.09.",
 "Mike Evans":"5.02. Half-PPR format split IN YOUR FAVOUR -- Nick fades him in full PPR, buys at 0.5.",
 "David Montgomery":"Replaces Etienne's old role and better. ADP 55 -- will NOT reach 7.02. Take 6.09 if only 1 RB.",
 "Josh Allen":"Highest raw total (420) and it does not matter -- only +30 over the QB you get anyway. NEVER before R4.",
 "Joe Burrow":"7.02 QB. Your 0.05/yd passing favours pocket arms. 20.2 hppr/wk.",
 "Justin Herbert":"7.02 QB fallback. Same 20.2 hppr/wk as Burrow. ADP 74 -- he lasts.",
 "Lamar Jackson":"Ceiling QB but RPB de-values rushing QBs. Fell QB2 -> QB6 under your scoring.",
 "Jayden Daniels":"CONFLICT in Nick's notes -- newer camp news downgrades him (WAS cutting no-huddle). Recency wins.",
 "Zay Flowers":"MWV ONLY. TD caps hurt him in half-PPR. Do NOT draft at rank in RPB.",
 "Travis Etienne Jr.":"Your OLD keeper, now in the pool. Exactly replacement level (-0.2). New Orleans in 2026.",
 "George Kittle":"Late TE door. +17.6 at ADP 107 = your 11.02. Only if Bowers AND Warren gone.",
 "Dallas Goedert":"Must-draft TE at ADP 125. AJ Brown's exit frees 120+ targets. Pure insurance.",
 "Breece Hall":"Nick MOVED HIM DOWN in half PPR too. Edge of the dead zone. Don't pay R3 price.",
 "Kyren Williams":"DEAD ZONE. Corum could take 50/50. Volume is perceived, not locked.",
 "Javonte Williams":"DEAD ZONE. Zero receiving role. Priced like more than he is.",
 "Bucky Irving":"Nick's #1 REGRET back. Committee + injury. ADP 56, worth #76. Let him go.",
 "Tony Pollard":"Must-draft but BELOW replacement (-24.9). R8 upside only, never a reach.",
 "Jonathon Brooks":"Backs up Chuba Hubbard (Nick SHY). Graded standalone value. R9-10 discount.",
 "Keaton Mitchell":"Hampton's handcuff AND must-draft -- the only double-dip. Take ONLY if you got Hampton.",
 "Jayden Higgins":"Starting Z opposite Nico Collins, who has missed time every year. R12-13 contingent upside.",
 "Jordan Mason":"Must-draft but -70.8. Lead back reports, Aaron Jones fading. Late dart only.",
 "Travis Hunter":"Nick calls him a last-round STEAL. Highest TPRR upside on the board.",
 "Kenneth Gainwell":"ADP 343, worth #136. Free handcuff -- the biggest ADP gap on the board.",
 "Houston Texans":"Best unit on CBS projections, but draws BUF/CIN/IND to open. A great unit in bad spots.",
 "Seattle Seahawks":"THE ACTUAL D/ST PICK. 61.6 over weeks 1-3, top-3 all three weeks. dst_rank.py's answer.",
 "Denver Broncos":"CBS ranks them 2nd but weeks 1-3 matchups are middling. Seattle is the better hold.",
 "Cameron Dicker":"16.09. Nick is 70th of 150+ at kicker. Take a good offense's leg and stop thinking.",
}
ROUND_HEAD = {
 1:"TAKE THE BACK", 2:"BOWERS WINDOW - the only real decision, at 2.09",
 3:"WRAP PICK - set predictor to TWO ROUNDS", 4:"QB legal but still wait. RB DEAD ZONE STARTS",
 5:"WRAP PICK - two rounds on the predictor", 6:"PARKER WASHINGTON WINDOW",
 7:"QB - tier holds, six teams keep one", 8:"LAST REAL RUNNING BACKS - cliff after this",
 9:"WRAP PICK - bench and upside", 10:"YOUR KEEPER: Luther Burden III consumes 10.09",
 11:"START COUNTING DEFENSES EVERY ROUND", 12:"lottery tickets, all below replacement",
 13:"watch the D/ST board", 14:"LAST SKILL PICK", 15:"D/ST", 16:"KICKER",
}

if "--notes" in sys.argv:
    print("PLAYER\tNOTE")
    for r in rows:
        n = NOTE.get(r["name"])
        if n:
            print(f"{r['name']}\t{n}")
    sys.exit(0)

rd = 0
for r in rows:
    cur = int(r["slot"].split(".")[0])
    if cur != rd:
        rd = cur
        print(f"\n--- ROUND {rd}  {ROUND_HEAD[rd]} ---")
    tag = " *MUST" if r["ffa"] == "MUST" else ""
    you = " <<<YOU" if r["mine"] == "True" else ""
    tz  = " [TAKE ZONE]" if r["name"] in TAKE else ""
    adv = NOTE.get(r["name"], "")
    line = f"{r['rank']:>3}. {r['name']:<24}{r['pos']:<4}{r['team']:<5}{r['rpb']:>7}{tag}{tz}{you}"
    print(line if not adv else f"{line}\n     -> {adv}")

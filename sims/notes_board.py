import csv, json, textwrap, pathlib
"""Annotated target board — the 160 picks with Nick's notes and the plan's warnings attached.

    python3 sims/notes_board.py > RPB-TARGETS-NOTES.txt

Reads RPB-TARGETS-160.csv (build it first with board160.py --targets --csv), data/notes.json for
Nick's per-player takes, and data/plan-rpb.json for the take zone. Round headers carry the
strategic beats: where the dead zone starts, which picks are wraps, when the Bowers window opens.
"""
ROOT = pathlib.Path.home()/"draft"
rows = list(csv.DictReader((ROOT/"RPB-TARGETS-160.csv").open()))
notes = json.load((ROOT/"data/notes.json").open())["shared"]
plan  = json.load((ROOT/"data/plan-rpb.json").open())
TAKE  = set(plan["takeZone"])

def look(nm):
    n=nm.lower()
    for v in notes.values():
        a,b=v["name"].lower().split()[0], v["name"].lower().split()[-1].strip(".")
        if a==n.split()[0] and b==n.split()[-1].strip("."): return v
    return {}

HEAD = {
 1:"ROUND 1 - TAKE THE BACK. Gibbs and Bijan are +164 VBD, the two biggest edges on the board.\n        You pick 1.02, so you get whichever one 1.01 leaves. Do not overthink it.\n        Amon-Ra is the ONLY receiver Nick breaks RB-RB for, and only outside the top 4.",
 2:"ROUND 2 - THE ONLY REAL DECISION OF YOUR DRAFT, at 2.09.\n        Bowers is listed 2.01 because that is where he SHOULD go. He has fallen to 2.09\n        in five of five real mocks. If he is there, take him - worth +57.9 over the best back.\n        If he is gone: take a take-zone back, and Tyler Warren becomes your TE at 6.09.",
 3:"ROUND 3 - WRAP PICK. 16 players come off between 2.09 and 3.02, so set the FantasyPros\n        Pick Predictor to TWO ROUNDS here or the number lies to you.\n        The take zone is a dead heat: Barkley / Walker / Chase Brown / Hampton all 13.1 hppr/wk.",
 4:"ROUND 4 - QB BECOMES LEGAL HERE, and that is the only reason QBs appear.\n        You should still wait to 7.02. Allen is +30 VBD, BELOW Barkley at +36.\n        The RB dead zone begins now: after Montgomery there is nothing until round 8.",
 5:"ROUND 5 - WRAP PICK. Two rounds on the predictor again.\n        Mike Evans is the half-PPR format split in your favour - Nick fades him in full PPR.",
 6:"ROUND 6 - PARKER WASHINGTON WINDOW. He is the single biggest edge in your setup\n        and the room does not know it. If Bowers went in R2, Tyler Warren or Kittle instead.",
 7:"ROUND 7 - QB. Six teams keep one, only four get drafted, so the tier cannot run dry.\n        Burrow and Herbert both project 20.2 hppr/wk and your scoring likes pocket arms.",
 8:"ROUND 8 - THE LAST REAL RUNNING BACKS. Pollard, Stevenson, Jaylen Warren all ~9.9 hppr/wk.\n        After this round it is 8.7 and a cliff. Do not expect more later.",
 9:"ROUND 9 - WRAP PICK. Bench and upside from here.",
 10:"ROUND 10 - YOUR KEEPER CONSUMES 10.09. Luther Burden III, WR19, +18.7 VBD.\n        (Keeper ROUND still unconfirmed - assumed 10, like-for-like with Etienne.)",
 11:"ROUND 11 - Handcuffs and upside. Start counting defenses from here every round.",
 12:"ROUND 12 - Pure lottery tickets now. Everything is below replacement.",
 13:"ROUND 13 - Watch the D/ST board. Mock 3 had the top two at 64% gone by 13.02.",
 14:"ROUND 14 - LAST SKILL PICK. If defenses are draining hard, take one here instead.",
 15:"ROUND 15 - D/ST. Ordered by CBS season projection, but the WEEKLY MATCHUP matters more.\n        sims/dst_rank.py says SEATTLE for the opening stretch (61.6 over weeks 1-3).\n        CBS and 4for4 disagree hard on defenses - CBS has Jacksonville 23rd, 4for4 had them 6th.",
 16:"ROUND 16 - KICKER. Nick ranks 70th of 150+ at this position. Nobody is good at it.\n        Take a good offense's kicker and stop thinking.",
}

out=[]
out.append("RPB TARGET BOARD - 160 picks, with notes")
out.append("FFA projections scored under RPB's rules. Shy-aways removed. Must-drafts bumped one round.")
out.append("Rebuild: python3 ~/draft/sims/board160.py --targets --csv")
out.append("")
out.append("KEY   *MUST = Nick's must-draft   [YOU] = your pick   val# = rank on pure points")
out.append("="*100)
rd=0
for r in rows:
    cur=int(r["slot"].split(".")[0])
    if cur!=rd:
        rd=cur; out.append(""); out.append("="*100); out.append(HEAD[rd]); out.append("="*100)
    must=" *MUST" if r["ffa"]=="MUST" else ""
    you=" [YOU]" if r["mine"]=="True" else ""
    vbd=f"{float(r['vbd']):+.1f}" if r["vbd"] else "  -  "
    val=f"val#{r['valueRank']}" if r["valueRank"] else ""
    out.append(f"{r['slot']:<6} {r['pos']:<4} {r['name']:<24}{r['team']:<5}{r['rpb']:>7} VBD {vbd:>7}  {val:<8}{must}{you}")
    n=look(r["name"]); bits=[]
    if r["ffa"]=="MUST" and r["valueRank"] and int(r["valueRank"])>int(r["rank"]):
        bits.append(f"BUMPED from {r['valueRank']} to {r['rank']} on Nick's must-draft list.")
    if r["name"] in TAKE: bits.append("TAKE ZONE - one of five backs to take through round 3 over a higher-ranked WR.")
    if r["adp"] and r["valueRank"]:
        a,v=float(r["adp"]),int(r["valueRank"])
        if a-v>=25: bits.append(f"VALUE GAP: ranked {v} but ADP {a:.0f} - he lasts, do not reach.")
        elif v-a>=20: bits.append(f"SCARCE: ADP {a:.0f} but only worth #{v} - the room takes him early. Let him go.")
    w=(n.get("videoNote") or n.get("why") or n.get("note") or "").strip()
    if w: bits.append("NICK: "+w)
    if r["vbd"] and float(r["vbd"])<0 and r["ffa"]=="MUST":
        bits.append("CAUTION: below replacement on points. Late upside only - do not reach.")
    for b in bits:
        for line in textwrap.wrap(b, 92): out.append("       "+line)
EX={"Brock Bowers":"THE PICK OF THE DRAFT IF HE FALLS. +57.9 over the best back. NEVER at 1.02 - that costs -81.8.",
    "Parker Washington":"RETURNS: he was 5th in the NFL in punt return yards and LED the league in punt return TDs. RPB pays 0.1/return yard and 6 per return TD. FFA projects none of it - that is +34 pts and the reason he is here. RISK: full-time offensive role may take him off returns.",
    "Travis Etienne Jr.":"YOUR OLD KEEPER, now back in the pool. Exactly replacement level (-0.2). New Orleans in 2026.",
    "Derrick Henry":"Take him LAST of the five take-zone backs. Nick calls him a watch, not a buy - declining targets, last year's RB8 finish inflated by one Week 17 four-TD game.",
    "Josh Allen":"Highest raw total on the board (420.3) and it does not matter. Only +30 over the QB you get anyway.",
    "Chase Brown":"Beats Derrick Henry on Nick's list even though RPB's bonuses rank Henry 1.1 pts higher. That gap is noise; the must-draft list breaks the tie.",
    "David Montgomery":"Replaces exactly what Etienne used to do, and better (+5.8 vs -0.2). ADP 55 - will NOT reach 7.02.",
    "Keaton Mitchell":"Omarion Hampton's handcuff AND must-draft - the only double-dip on the board. Take him only if you landed Hampton.",
    "Jonathon Brooks":"Backs up Chuba Hubbard, who is on Nick's SHY list. FantasyPros grades Brooks standalone-value.",
    "Tyler Warren":"YOUR BOWERS FALLBACK. +44.7 VBD at ADP 59 - that is your 6.09 exactly.",
    "George Kittle":"The late TE door. +17.6 at ADP 107, which is your 11.02.",
   }
i=0
final=[]
for line in out:
    final.append(line)
    for k,v in EX.items():
        if line.startswith(tuple(f"{n}." for n in "0123456789")) and f" {k:<24}" in line:
            for w in textwrap.wrap(">>> "+v, 92): final.append("       "+w)
print("\n".join(final))

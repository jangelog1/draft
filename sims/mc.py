#!/usr/bin/env python3
"""Monte Carlo draft sim for RPB — Etienne vs Luther Burden III as the round-10 keeper.

League truth (matches the app exactly): 10 teams, 16 rounds, snake, half-PPR, D/ST scoring doubled,
starters QB1/RB2/WR3/TE1/K1/DST1 and NO flex. Angelo is seat 2. 13 keepers consume their owners'
picks in the stated round, so those overall picks never come up.

What is modelled: the market (ADP with noise), positional need, and roster construction.
What is NOT: injuries, weekly variance, waivers, trades, bye conflicts. So the output is
draft-day starting-lineup strength, not a season prediction. Treated as such in the reporting.
"""
import json, random, statistics as st, sys, collections

import os as _os, glob as _glob
_HERE = _os.path.dirname(_os.path.abspath(__file__))
def _api():
    """Live projections. /tmp is wiped on reboot, so fall back to the newest committed snapshot
    in this directory. Re-fetch with:
        curl -s https://thefantasyfootballadvice.com/api/redraft-rankings -o sims/ffa_api_<date>.json"""
    if _os.path.exists("/tmp/ffa_api.json"): return "/tmp/ffa_api.json"
    snaps = sorted(_glob.glob(_os.path.join(_HERE, "ffa_api_*.json")))
    if not snaps: raise SystemExit("no FFA snapshot — see _api() docstring to refetch")
    return snaps[-1]
API  = _api()
KEEP = _os.path.join(_HERE, "..", "data", "keepers-rpb.json")
TEAMS, ROUNDS, MYSLOT = 10, 16, 2
STARTERS = {"QB":1,"RB":2,"WR":3,"TE":1,"K":1,"DST":1}
DST_MULT = 2
BUILD    = {"QB":1,"RB":5,"WR":6,"TE":1,"K":1,"DST":1}   # target roster the app uses
REPL     = {p: STARTERS[p]*TEAMS for p in STARTERS}

def norm(p):
    p = str(p or "").upper()
    return "DST" if p.replace("/","") == "DST" else p

def load():
    raw = json.load(open(API))["data"]
    players = {}
    for r in raw:
        if r.get("hppr") is None or not r.get("player_name"):
            continue
        pos = norm(r["pos"])
        adp = r.get("adp")
        if adp is not None and adp >= 999:      # FFA's undrafted placeholder, not a real ADP
            adp = None
        pts = r["hppr"] * (DST_MULT if pos == "DST" else 1)
        players[r["player_name"]] = {"name": r["player_name"], "pos": pos, "pts": pts, "adp": adp}
    # VBD = points above the last startable player at that position
    by = collections.defaultdict(list)
    for p in players.values():
        by[p["pos"]].append(p)
    for pos, g in by.items():
        g.sort(key=lambda x: -x["pts"])
        n = REPL.get(pos, 12)
        repl = g[n-1]["pts"] if len(g) >= n else (g[-1]["pts"] if g else 0)
        for p in g:
            p["vbd"] = p["pts"] - repl
    # players with no ADP still have to be draftable; park them past the end of the draft
    worst = max((p["adp"] for p in players.values() if p["adp"]), default=200)
    for p in players.values():
        if p["adp"] is None:
            p["adp"] = worst + 60
    return players

def snake(rd, slot):  return (rd-1)*TEAMS+slot if rd % 2 else rd*TEAMS-slot+1
def slot_of(ov):      return ((ov-1) % TEAMS)+1 if ((ov-1)//TEAMS+1) % 2 else TEAMS-((ov-1) % TEAMS)

def ladder(keepers, order):
    slot_for = {t: i+1 for i, t in enumerate(order)}
    consumed, pre = set(), collections.defaultdict(list)
    for k in keepers:
        s, rd = slot_for[k["team"]], int(str(k["round"]))
        consumed.add(snake(rd, s))
        pre[s].append(k["player"])
    return [ov for ov in range(1, TEAMS*ROUNDS+1) if ov not in consumed], pre

def need_mult(pos, have):
    t = BUILD[pos]
    return 1 + 0.35*(1-have/t) if have < t else 0.75**(have-t+1)

def lineup_points(roster, players):
    """Best legal starting lineup. No flex, so it is a straight take-the-best-N per slot."""
    total, by = 0.0, collections.defaultdict(list)
    for nm in roster:
        p = players.get(nm)
        if p: by[p["pos"]].append(p["pts"])
    for pos, n in STARTERS.items():
        s = sorted(by.get(pos, []), reverse=True)[:n]
        total += sum(s)
        if len(s) < n:                       # unfilled starting slot is a real, punishing hole
            total -= 40 * (n - len(s))
    return total

def cpu_pick(avail, roster_pos, ov, rng, noise):
    """Market behaviour: ADP order, jittered, with hard roster sanity."""
    picks_left = ROUNDS - sum(roster_pos.values())
    must = [p for p in ("K","DST","QB","TE") if roster_pos[p] < STARTERS[p]]
    cand = []
    for p in avail:
        pos = p["pos"]
        if roster_pos[pos] >= BUILD[pos]:        continue   # nobody drafts a 4th QB
        if pos in ("K","DST") and picks_left > len(must)+1: continue  # not this early
        cand.append(p)
    if not cand:
        cand = list(avail)
    if picks_left <= len(must):                  # forced to fill the last mandatory slots
        f = [p for p in cand if p["pos"] in must]
        if f: cand = f
    cand.sort(key=lambda p: p["adp"] + rng.gauss(0, noise))
    return cand[0]

def my_pick(avail, roster_pos, ov, rng):
    """Angelo's engine, same as the app: VBD x positional need, K/DST held until forced."""
    picks_left = ROUNDS - sum(roster_pos.values())
    unfilled = sum(1 for p in ("K","DST") if roster_pos[p] < STARTERS[p])
    allow_kdst = picks_left <= unfilled + 2
    best, bs = None, -1e9
    for p in avail:
        pos = p["pos"]
        if pos in ("K","DST") and not allow_kdst:   continue
        if roster_pos[pos] >= BUILD[pos]:           continue
        v = p["vbd"]
        s = (v*need_mult(pos, roster_pos[pos]) if v > 0 else v) + max(0, min(24, ov-p["adp"]))*2
        if s > bs: best, bs = p, s
    if best is None:
        best = max(avail, key=lambda p: p["vbd"])
    return best

def run(players, keepers, order, n_sims, noise, seed):
    rng = random.Random(seed)
    live, pre = ladder(keepers, order)
    mine_scores, ranks, roster_log = [], [], collections.Counter()
    for _ in range(n_sims):
        avail = {k: v for k, v in players.items()}
        rosters   = {s: list(pre.get(s, [])) for s in range(1, TEAMS+1)}
        roster_pos = {s: collections.Counter({p:0 for p in STARTERS}) for s in range(1, TEAMS+1)}
        for s in rosters:
            for nm in rosters[s]:
                if nm in avail:
                    roster_pos[s][avail[nm]["pos"]] += 1
                    del avail[nm]
        for ov in live:
            s = slot_of(ov)
            pool = list(avail.values())
            if not pool: break
            p = my_pick(pool, roster_pos[s], ov, rng) if s == MYSLOT else cpu_pick(pool, roster_pos[s], ov, rng, noise)
            rosters[s].append(p["name"]); roster_pos[s][p["pos"]] += 1; del avail[p["name"]]
        scores = {s: lineup_points(rosters[s], players) for s in rosters}
        mine   = scores[MYSLOT]
        mine_scores.append(mine)
        ranks.append(sorted(scores.values(), reverse=True).index(mine)+1)
        for nm in rosters[MYSLOT]:
            roster_log[nm] += 1
    return mine_scores, ranks, roster_log

def summarise(tag, scores, ranks, n):
    return {
        "scenario": tag,
        "mean_starting_pts": round(st.mean(scores), 1),
        "median": round(st.median(scores), 1),
        "p10": round(sorted(scores)[int(.10*len(scores))], 1),
        "p90": round(sorted(scores)[int(.90*len(scores))], 1),
        "best_roster_rate": round(100*sum(1 for r in ranks if r == 1)/n, 1),
        "top3_rate": round(100*sum(1 for r in ranks if r <= 3)/n, 1),
        "mean_rank": round(st.mean(ranks), 2),
    }

if __name__ == "__main__":
    N     = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    NOISE = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    players = load()
    kdoc  = json.load(open(KEEP))
    order = [e["team"] for e in kdoc["draftOrder"]]
    base  = kdoc["keepers"]
    MINE  = "Real Midway Monsters®"

    scen = {}
    for tag, who in (("Etienne (real)", "Travis Etienne Jr."), ("Burden III", "Luther Burden III")):
        ks = [dict(k) for k in base if k["team"] != MINE] + [{"team": MINE, "round": 10, "player": who}]
        assert len(ks) == 13, len(ks)
        assert who in players, f"{who} not on the board"
        scen[tag] = run(players, ks, order, N, NOISE, seed=hash(tag) & 0xffff)

    print(f"=== RPB Monte Carlo — {N} drafts per scenario, ADP noise sd={NOISE} ===\n")
    rows = []
    for tag, (sc, rk, log) in scen.items():
        rows.append(summarise(tag, sc, rk, N))
    for r in rows:
        print(f"{r['scenario']:<16} starters {r['mean_starting_pts']:>7} pts  "
              f"(p10 {r['p10']}, p90 {r['p90']})   best roster {r['best_roster_rate']:>4}%   "
              f"top3 {r['top3_rate']:>4}%   mean rank {r['mean_rank']}")
    a, b = rows[0], rows[1]
    print(f"\nDelta (Etienne − Burden): {round(a['mean_starting_pts']-b['mean_starting_pts'],1)} pts, "
          f"{round(a['best_roster_rate']-b['best_roster_rate'],1)} pts of best-roster rate")

    # where does Etienne end up when he is NOT the keeper?
    print("\n--- who Angelo actually ends up with, top 14 by frequency ---")
    for tag, (_, _, log) in scen.items():
        print(f"\n{tag}:")
        for nm, c in log.most_common(14):
            p = players[nm]
            print(f"   {100*c/N:>5.1f}%  {nm:<26} {p['pos']:<4} adp {p['adp']:>5.1f}  {p['pts']:>6.1f} pts")

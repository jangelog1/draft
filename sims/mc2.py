#!/usr/bin/env python3
"""RPB Monte Carlo v2 — Etienne vs Luther Burden III at the round-10 keeper slot.

v1 gave Angelo a 99.7% best-roster rate, which is not a finding, it is a broken opponent model:
the CPUs drafted on raw ADP while his seat optimised VBD, so both scenarios pinned at the ceiling
and the comparison could not discriminate. v2 gives every seat the same value-aware engine and
varies their ADP-adherence, so the league is a real fight and the keeper difference is what moves.

Modelled: market ADP with per-team noise, positional need, roster legality, the real 13-keeper
ladder, half-PPR, doubled D/ST, no flex, Angelo at seat 2.
NOT modelled: injuries, weekly variance, byes, waivers, trades. This measures draft-day starting
lineup strength — not a season.
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
BUILD    = {"QB":2,"RB":5,"WR":6,"TE":2,"K":1,"DST":1}
DST_MULT, REPL = 2, {p: STARTERS[p]*TEAMS for p in STARTERS}
CAND = 70          # only the top-N plausible players are ever considered; keeps it honest and fast

def norm(p):
    p = str(p or "").upper()
    return "DST" if p.replace("/","") == "DST" else p

def load():
    players = []
    for r in json.load(open(API))["data"]:
        if r.get("hppr") is None or not r.get("player_name"): continue
        pos = norm(r["pos"]); adp = r.get("adp")
        if adp is not None and adp >= 999: adp = None
        players.append({"name":r["player_name"], "pos":pos,
                        "pts":r["hppr"]*(DST_MULT if pos=="DST" else 1), "adp":adp})
    by = collections.defaultdict(list)
    for p in players: by[p["pos"]].append(p)
    for pos,g in by.items():
        g.sort(key=lambda x:-x["pts"]); n=REPL.get(pos,12)
        repl = g[n-1]["pts"] if len(g)>=n else (g[-1]["pts"] if g else 0)
        for p in g: p["vbd"] = p["pts"]-repl
    worst = max((p["adp"] for p in players if p["adp"]), default=200)
    for p in players:
        if p["adp"] is None: p["adp"] = worst+60
    players.sort(key=lambda p: p["adp"])
    return players

def snake(rd,s): return (rd-1)*TEAMS+s if rd%2 else rd*TEAMS-s+1
def slot_of(ov): return ((ov-1)%TEAMS)+1 if ((ov-1)//TEAMS+1)%2 else TEAMS-((ov-1)%TEAMS)

def ladder(keepers, order):
    sf={t:i+1 for i,t in enumerate(order)}
    used,pre=set(),collections.defaultdict(list)
    for k in keepers:
        s,rd=sf[k["team"]],int(str(k["round"])); used.add(snake(rd,s)); pre[s].append(k["player"])
    return [ov for ov in range(1,TEAMS*ROUNDS+1) if ov not in used], pre

def need_mult(pos,have):
    t=BUILD[pos]
    return 1+0.35*(1-have/t) if have<t else 0.75**(have-t+1)

def lineup(roster, idx):
    tot=0.0; by=collections.defaultdict(list)
    for nm in roster:
        p=idx.get(nm)
        if p: by[p["pos"]].append(p["pts"])
    for pos,n in STARTERS.items():
        s=sorted(by.get(pos,[]),reverse=True)[:n]; tot+=sum(s)
        if len(s)<n: tot-=40*(n-len(s))
    return tot

def pick(avail, rpos, ov, rng, adp_weight, noise):
    """One engine for everyone. adp_weight=0 is a pure value drafter, 1 is a pure ADP drafter."""
    left=ROUNDS-sum(rpos.values())
    unfilled=sum(1 for p in ("K","DST") if rpos[p]<STARTERS[p])
    allow=left<=unfilled+2
    best,bs=None,-1e18
    for p in avail[:CAND]:
        pos=p["pos"]
        if pos in ("K","DST") and not allow: continue
        if rpos[pos]>=BUILD[pos]: continue
        v=p["vbd"]
        val=(v*need_mult(pos,rpos[pos]) if v>0 else v)+max(0,min(24,ov-p["adp"]))*2
        # ADP drafters chase the board; value drafters chase VBD. Everyone gets noise.
        s=(1-adp_weight)*val - adp_weight*p["adp"]*3 + rng.gauss(0,noise)
        if s>bs: best,bs=p,s
    if best is None:
        for p in avail:
            if rpos[p["pos"]]<BUILD[p["pos"]]: return p
        return avail[0]
    return best

def run(players, keepers, order, n, seed):
    rng=random.Random(seed); live,pre=ladder(keepers,order)
    idx={p["name"]:p for p in players}
    scores,ranks,log=[],[],collections.Counter()
    # heterogeneous league: some managers draft the board, some draft value
    for _ in range(n):
        style={s:(rng.uniform(.15,.75), rng.uniform(6,16)) for s in range(1,TEAMS+1)}
        style[MYSLOT]=(0.0, 0.0)                       # Angelo runs the app's engine, no noise
        avail=list(players)
        rost={s:list(pre.get(s,[])) for s in range(1,TEAMS+1)}
        rpos={s:collections.Counter({p:0 for p in STARTERS}) for s in range(1,TEAMS+1)}
        taken=set()
        for s in rost:
            for nm in rost[s]:
                if nm in idx: rpos[s][idx[nm]["pos"]]+=1; taken.add(nm)
        avail=[p for p in avail if p["name"] not in taken]
        for ov in live:
            if not avail: break
            s=slot_of(ov); aw,nz=style[s]
            p=pick(avail,rpos[s],ov,rng,aw,nz)
            rost[s].append(p["name"]); rpos[s][p["pos"]]+=1; avail.remove(p)
        sc={s:lineup(rost[s],idx) for s in rost}
        mine=sc[MYSLOT]; scores.append(mine)
        ranks.append(sorted(sc.values(),reverse=True).index(mine)+1)
        for nm in rost[MYSLOT]: log[nm]+=1
    return scores,ranks,log

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 1500
    players=load(); k=json.load(open(KEEP)); order=[e["team"] for e in k["draftOrder"]]
    MINE="Real Midway Monsters®"; base=k["keepers"]
    out={}
    for tag,who in (("Etienne","Travis Etienne Jr."),("Burden III","Luther Burden III")):
        ks=[dict(x) for x in base if x["team"]!=MINE]+[{"team":MINE,"round":10,"player":who}]
        assert len(ks)==13
        out[tag]=run(players,ks,order,N,seed=1234)      # SAME seed = same opponents, fair pairing
    print(f"=== RPB Monte Carlo v2 — {N} paired drafts per scenario ===")
    print("(identical seed, so both scenarios face the same 1500 leagues)\n")
    idx={p["name"]:p for p in players}
    for tag,(sc,rk,_) in out.items():
        srt=sorted(sc)
        print(f"{tag:<11} starters {st.mean(sc):>7.1f} pts  (p10 {srt[int(.1*N)]:.0f} / p90 {srt[int(.9*N)]:.0f})  "
              f"best {100*sum(1 for r in rk if r==1)/N:>5.1f}%  top3 {100*sum(1 for r in rk if r<=3)/N:>5.1f}%  "
              f"mean rank {st.mean(rk):.2f}")
    a,b=out["Etienne"][0],out["Burden III"][0]
    wins=sum(1 for x,y in zip(a,b) if x>y); ties=sum(1 for x,y in zip(a,b) if x==y)
    print(f"\nHead to head on the SAME league: Etienne better in {100*wins/N:.1f}% of drafts, "
          f"Burden better in {100*(N-wins-ties)/N:.1f}%, tied {100*ties/N:.1f}%")
    print(f"Mean difference: {st.mean(a)-st.mean(b):+.1f} starting points in Etienne's favour")
    d=[x-y for x,y in zip(a,b)]
    print(f"Difference spread: p10 {sorted(d)[int(.1*N)]:+.0f}, median {st.median(d):+.0f}, p90 {sorted(d)[int(.9*N)]:+.0f}")
    print("\n--- what Angelo's roster looks like, top 12 ---")
    for tag,(_,_,log) in out.items():
        print(f"\n{tag}:")
        for nm,c in log.most_common(12):
            p=idx[nm]; print(f"   {100*c/N:>5.1f}%  {nm:<25} {p['pos']:<4} adp {p['adp']:>5.0f}  {p['pts']:>6.0f} pts")
    # where does Etienne go when he is not kept?
    _,_,blog=out["Burden III"]
    print(f"\nEtienne on Angelo's roster in the Burden world: {100*blog.get('Travis Etienne Jr.',0)/N:.1f}% "
          "(he is a free agent there, so the room can take him)")

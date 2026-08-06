#!/usr/bin/env python3
"""RPB — every Strategy Lab archetype, run round by round at Angelo's seat 2.

Build fixed to his instruction: 6 RB + 6 WR + 1 QB + 1 TE + 1 K + 1 DST = 16 exactly.
Etienne is the round-10 keeper and counts as one of the six backs, so 15 live picks.

Each strategy is expressed two ways, matching how the archetypes actually work:
  script    - forced positions for the opening picks (HeroRB, DoubleHeroWR, EliteTE, ...)
  notBefore - a position that may not be taken before pick N (the DoubleLate* family)
Everything after the script is the value engine filling the remaining build caps, with K and D/ST
held to the end because the sweep showed reaching for them costs 19-40 points and buys nothing.

FFA's own Strategy Lab numbers for SLOT 2 are carried alongside for comparison. Those come from
real drafts; mine come from this simulator. Where they disagree, say so rather than pick a winner.
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
MYBUILD  = {"QB":1,"RB":6,"WR":6,"TE":1,"K":1,"DST":1}
CPUBUILD = {"QB":2,"RB":5,"WR":6,"TE":2,"K":1,"DST":1}
DST_MULT, REPL, CAND = 2, {p: STARTERS[p]*TEAMS for p in STARTERS}, 70

# name: (opening script, notBefore, FFA Strategy Lab % at SLOT 2 from Angelo's screenshot)
STRATS = {
 "DoubleLateQBandTE": ([],                              {"QB":8,"TE":8},  +3.4),
 "HeroWR":            (["WR","RB","RB","WR","WR"],      {},               +3.1),
 "RobustRB":          (["RB","RB","RB","WR","WR"],      {},               +3.1),
 "EliteTE":           (["TE","RB","WR","WR","WR"],      {},               +3.0),
 "DoubleHeroRB":      (["RB","RB","WR","WR","WR"],      {},               +3.0),
 "DoubleLateTE":      ([],                              {"TE":8},         +2.9),
 "DoubleLateQB":      ([],                              {"QB":8},         +2.9),
 "EarlyQB":           (["RB","QB","WR","WR","WR"],      {},               +2.1),
 "HeroRB":            (["RB","WR","WR","WR","WR"],      {},               +1.9),
 "CorePillars":       ([],                              {},              +1.7),
 "ModifiedRBZero":    (["WR","WR","RB","WR","WR"],      {},               +0.0),
 "WRZero":            (["RB","RB","RB","RB","RB"],      {},               -0.0),
 "DoubleHeroWR":      (["WR","WR","RB","RB","WR"],      {},               -1.0),
 "RBZero":            (["WR","WR","WR","WR","WR"],      {"RB":7},         None),
}

def norm(p):
    p=str(p or "").upper(); return "DST" if p.replace("/","")=="DST" else p

def load():
    ps=[]
    for r in json.load(open(API))["data"]:
        if r.get("hppr") is None or not r.get("player_name"): continue
        pos=norm(r["pos"]); adp=r.get("adp")
        if adp is not None and adp>=999: adp=None
        ps.append({"name":r["player_name"],"pos":pos,
                   "pts":r["hppr"]*(DST_MULT if pos=="DST" else 1),"adp":adp})
    by=collections.defaultdict(list)
    for p in ps: by[p["pos"]].append(p)
    for pos,g in by.items():
        g.sort(key=lambda x:-x["pts"]); n=REPL.get(pos,12)
        repl=g[n-1]["pts"] if len(g)>=n else (g[-1]["pts"] if g else 0)
        for p in g: p["vbd"]=p["pts"]-repl
    worst=max((p["adp"] for p in ps if p["adp"]),default=200)
    for p in ps:
        if p["adp"] is None: p["adp"]=worst+60
    ps.sort(key=lambda p:p["adp"]); return ps

def snake(rd,s): return (rd-1)*TEAMS+s if rd%2 else rd*TEAMS-s+1
def slot_of(ov): return ((ov-1)%TEAMS)+1 if ((ov-1)//TEAMS+1)%2 else TEAMS-((ov-1)%TEAMS)

def ladder(keepers,order):
    sf={t:i+1 for i,t in enumerate(order)}; used=set(); pre=collections.defaultdict(list)
    for k in keepers:
        s,rd=sf[k["team"]],int(str(k["round"])); used.add(snake(rd,s)); pre[s].append(k["player"])
    return [ov for ov in range(1,TEAMS*ROUNDS+1) if ov not in used],pre

def need_mult(pos,have,build):
    t=build[pos]; return 1+0.35*(1-have/t) if have<t else 0.75**(have-t+1)

def lineup(roster,idx):
    tot=0.0; by=collections.defaultdict(list)
    for nm in roster:
        p=idx.get(nm)
        if p: by[p["pos"]].append(p["pts"])
    for pos,n in STARTERS.items():
        s=sorted(by.get(pos,[]),reverse=True)[:n]; tot+=sum(s)
        if len(s)<n: tot-=40*(n-len(s))
    return tot

def cpu_pick(avail,rpos,ov,rng,aw,nz):
    left=ROUNDS-sum(rpos.values())
    missing=[p for p in ("K","DST","QB","TE") if rpos[p]<STARTERS[p]]
    unf=sum(1 for p in ("K","DST") if rpos[p]<STARTERS[p]); allow=left<=unf+2
    if left<=len(missing):
        f=[p for p in avail if p["pos"] in missing]
        if f: return min(f,key=lambda p:p["adp"]+rng.gauss(0,nz))
    best,bs=None,-1e18
    for p in avail[:CAND]:
        pos=p["pos"]
        if pos in ("K","DST") and not allow: continue
        if rpos[pos]>=CPUBUILD[pos]: continue
        v=p["vbd"]
        val=(v*need_mult(pos,rpos[pos],CPUBUILD) if v>0 else v)+max(0,min(24,ov-p["adp"]))*2
        s=(1-aw)*val-aw*p["adp"]*3+rng.gauss(0,nz)
        if s>bs: best,bs=p,s
    if best is None:
        for p in avail:
            if rpos[p["pos"]]<CPUBUILD[p["pos"]]: return p
        return avail[0]
    return best

def my_pick(avail,rpos,ov,n,script,notb):
    left=ROUNDS-sum(rpos.values())
    short=[p for p in MYBUILD if rpos[p]<MYBUILD[p]]
    scarce=[p for p in ("DST","K","QB","TE") if rpos[p]<MYBUILD[p]]
    forced=None
    if left<=len(scarce) and scarce: forced=scarce[0]          # run out of room, take the slot
    elif n<=len(script) and rpos[script[n-1]]<MYBUILD[script[n-1]]: forced=script[n-1]
    pool=[p for p in avail if rpos[p["pos"]]<MYBUILD[p["pos"]]]
    if forced:
        pool=[p for p in pool if p["pos"]==forced] or pool
    else:
        pool=[p for p in pool if p["pos"] not in ("K","DST")] or pool
        pool=[p for p in pool if not (p["pos"] in notb and n<notb[p["pos"]])] or pool
    if not pool: pool=list(avail)
    best,bs=None,-1e18
    for p in pool[:CAND]:
        v=p["vbd"]
        s=(v*need_mult(p["pos"],rpos[p["pos"]],MYBUILD) if v>0 else v)+max(0,min(24,ov-p["adp"]))*2
        if s>bs: best,bs=p,s
    return best or pool[0]

def run(players,keepers,order,n,seed,script,notb):
    rng=random.Random(seed); live,pre=ladder(keepers,order); idx={p["name"]:p for p in players}
    scores=[]; byPick=collections.defaultdict(collections.Counter); posPick=collections.defaultdict(collections.Counter)
    mypicks=[ov for ov in live if slot_of(ov)==MYSLOT]
    for _ in range(n):
        style={s:(rng.uniform(.15,.75),rng.uniform(6,16)) for s in range(1,TEAMS+1)}
        rost={s:list(pre.get(s,[])) for s in range(1,TEAMS+1)}
        rpos={s:collections.Counter({p:0 for p in STARTERS}) for s in range(1,TEAMS+1)}
        taken=set()
        for s in rost:
            for nm in rost[s]:
                if nm in idx: rpos[s][idx[nm]["pos"]]+=1; taken.add(nm)
        avail=[p for p in players if p["name"] not in taken]; myn=0
        for ov in live:
            if not avail: break
            s=slot_of(ov)
            if s==MYSLOT:
                myn+=1; p=my_pick(avail,rpos[s],ov,myn,script,notb)
                byPick[myn][p["name"]]+=1; posPick[myn][p["pos"]]+=1
            else:
                aw,nz=style[s]; p=cpu_pick(avail,rpos[s],ov,rng,aw,nz)
            rost[s].append(p["name"]); rpos[s][p["pos"]]+=1; avail.remove(p)
        scores.append(lineup(rost[MYSLOT],idx))
    return scores,byPick,posPick,mypicks

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 400
    players=load(); k=json.load(open(KEEP)); order=[e["team"] for e in k["draftOrder"]]
    MINE="Real Midway Monsters®"
    keep=[dict(x) for x in k["keepers"] if x["team"]!=MINE]+[{"team":MINE,"round":10,"player":"Travis Etienne Jr."}]
    res={}
    for name,(script,notb,ffa) in STRATS.items():
        sc,bp,pp,mypicks=run(players,keep,order,N,2468,script,notb)
        res[name]=(st.mean(sc),sc,bp,pp,ffa)
    base=res["CorePillars"][0]
    print(f"=== ALL 14 STRATEGIES — seat 2, Etienne kept, 6RB/6WR, {N} drafts each, identical opponents ===\n")
    print(f"{'strategy':<20}{'my sim pts':>11}{'vs CorePillars':>16}{'FFA slot-2':>12}")
    for nm,(mu,sc,bp,pp,ffa) in sorted(res.items(),key=lambda kv:-kv[1][0]):
        f=f"{ffa:+.1f}%" if ffa is not None else "  n/a"
        print(f"{nm:<20}{mu:>11.1f}{mu-base:>+16.1f}{f:>12}")
    out={}
    for nm,(mu,sc,bp,pp,ffa) in res.items():
        rows=[]
        for i,ov in enumerate(mypicks,1):
            rd=(ov-1)//TEAMS+1
            rows.append({"n":i,"pick":f"{rd}.{str((ov-1)%TEAMS+1).zfill(2)}","round":rd,
                "pos":[[p,round(100*c/N)] for p,c in pp[i].most_common(2)],
                "names":[[n2,round(100*c/N)] for n2,c in bp[i].most_common(3)]})
        out[nm]={"mean":round(mu,1),"ffa_slot2":ffa,"rounds":rows}
    json.dump(out,open("/tmp/strategies.json","w"),indent=1)
    print("\nfull round-by-round for all 14 -> /tmp/strategies.json")

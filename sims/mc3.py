#!/usr/bin/env python3
"""RPB Monte Carlo v3 — Angelo's stated build, and WHEN to take each scarce slot.

Build is fixed by his instruction: 6 RB + 6 WR + 1 QB + 1 TE + 1 K + 1 DST = 16, exactly the
roster. Etienne is the round-10 keeper and counts as one of the six backs, so he makes 15 live
picks. With the counts fixed there is nothing left to choose but ORDER, which is what this sweeps.

Same league truth as the app: 10 teams, snake, half-PPR, D/ST DOUBLED, starters QB1/RB2/WR3/TE1/
K1/DST1, no flex, Angelo at seat 2, 13 keepers consuming their owners' picks.

Not modelled: injuries, weekly variance, byes, waivers, trades. Draft-day starting strength only.
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
MYBUILD  = {"QB":1,"RB":6,"WR":6,"TE":1,"K":1,"DST":1}      # his instruction, sums to 16
CPUBUILD = {"QB":2,"RB":5,"WR":6,"TE":2,"K":1,"DST":1}
DST_MULT, REPL, CAND = 2, {p: STARTERS[p]*TEAMS for p in STARTERS}, 70

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
    unf=sum(1 for p in ("K","DST") if rpos[p]<STARTERS[p])
    allow=left<=unf+2
    # Hard force: once the picks remaining equal the starting slots still empty, the room takes
    # them. Without this the CPUs finished without a kicker or defense and ate the -40 penalty,
    # which handed Angelo a 100% win rate that was an artefact, not a finding.
    if left<=len(missing):
        forced=[p for p in avail if p["pos"] in missing]
        if forced: return min(forced,key=lambda p:p["adp"]+rng.gauss(0,nz))
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

def my_pick(avail,rpos,ov,my_n,dst_at,k_at,qb_at,te_at):
    """my_n = which of Angelo's own picks this is (1-based). *_at = force that slot on that pick."""
    forced=None
    if my_n==dst_at: forced="DST"
    elif my_n==k_at: forced="K"
    elif my_n==qb_at: forced="QB"
    elif my_n==te_at: forced="TE"
    picks_left=ROUNDS-sum(rpos.values())
    # anything still unfilled and now unavoidable must be taken
    must=[p for p in MYBUILD if rpos[p]<MYBUILD[p]]
    if picks_left<=len(must) and forced is None:
        scarce=[p for p in ("DST","K","QB","TE") if rpos[p]<MYBUILD[p]]
        if scarce: forced=scarce[0]
    pool=[p for p in avail if rpos[p["pos"]]<MYBUILD[p["pos"]]]
    if forced: pool=[p for p in pool if p["pos"]==forced] or pool
    else:      pool=[p for p in pool if p["pos"] not in ("K","DST")] or pool
    if not pool: pool=list(avail)
    best,bs=None,-1e18
    for p in pool[:CAND]:
        v=p["vbd"]
        s=(v*need_mult(p["pos"],rpos[p["pos"]],MYBUILD) if v>0 else v)+max(0,min(24,ov-p["adp"]))*2
        if s>bs: best,bs=p,s
    return best or pool[0]

def run(players,keepers,order,n,seed,dst_at=99,k_at=99,qb_at=99,te_at=99):
    rng=random.Random(seed); live,pre=ladder(keepers,order); idx={p["name"]:p for p in players}
    scores,ranks,log,rounds_taken=[],[],collections.Counter(),collections.defaultdict(list)
    for _ in range(n):
        style={s:(rng.uniform(.15,.75),rng.uniform(6,16)) for s in range(1,TEAMS+1)}
        rost={s:list(pre.get(s,[])) for s in range(1,TEAMS+1)}
        rpos={s:collections.Counter({p:0 for p in STARTERS}) for s in range(1,TEAMS+1)}
        taken=set()
        for s in rost:
            for nm in rost[s]:
                if nm in idx: rpos[s][idx[nm]["pos"]]+=1; taken.add(nm)
        avail=[p for p in players if p["name"] not in taken]
        myn=0
        for ov in live:
            if not avail: break
            s=slot_of(ov)
            if s==MYSLOT:
                myn+=1; p=my_pick(avail,rpos[s],ov,myn,dst_at,k_at,qb_at,te_at)
                rounds_taken[p["pos"]].append((ov-1)//TEAMS+1)
            else:
                aw,nz=style[s]; p=cpu_pick(avail,rpos[s],ov,rng,aw,nz)
            rost[s].append(p["name"]); rpos[s][p["pos"]]+=1; avail.remove(p)
        sc={s:lineup(rost[s],idx) for s in rost}
        mine=sc[MYSLOT]; scores.append(mine)
        ranks.append(sorted(sc.values(),reverse=True).index(mine)+1)
        for nm in rost[MYSLOT]: log[nm]+=1
    return scores,ranks,log,rounds_taken

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 400
    players=load(); k=json.load(open(KEEP)); order=[e["team"] for e in k["draftOrder"]]
    MINE="Real Midway Monsters®"
    keep=[dict(x) for x in k["keepers"] if x["team"]!=MINE]+[{"team":MINE,"round":10,"player":"Travis Etienne Jr."}]
    idx={p["name"]:p for p in players}
    print(f"=== D/ST TIMING SWEEP — Etienne kept, build 6RB/6WR/1QB/1TE/1K/1DST, {N} drafts each ===")
    print("'my pick #N' is Angelo's own Nth selection. He has 15 (keeper takes one).\n")
    print(" force DST at   round   starters   best%   top3%   mean rank")
    res={}
    for n_at in list(range(1,16))+[99]:
        sc,rk,log,rt=run(players,keep,order,N,seed=2468,dst_at=n_at)
        rd=st.median(rt["DST"]) if rt["DST"] else None
        res[n_at]=(st.mean(sc),100*sum(1 for r in rk if r==1)/N,100*sum(1 for r in rk if r<=3)/N,st.mean(rk),rd)
        lbl=f"my pick #{n_at}" if n_at!=99 else "engine default"
        print(f" {lbl:<14} {str(int(rd)) if rd else '-':>5}   {res[n_at][0]:>8.1f}  {res[n_at][1]:>5.1f}  {res[n_at][2]:>6.1f}   {res[n_at][3]:>6.2f}")
    best=max(res.items(),key=lambda kv:kv[1][0])
    print(f"\nBEST: force D/ST at my pick #{best[0]} -> {best[1][0]:.1f} pts "
          f"({best[1][0]-res[99][0]:+.1f} vs the engine's default)")

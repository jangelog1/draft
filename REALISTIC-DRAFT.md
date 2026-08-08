# The realistic aggressive draft — RPB, slot 2

Built 2026-08-07 from `RPB-TARGETS-160.csv` + FFA ADP. "Realistic" means every name here is one
ADP says will actually still be on the board at that pick. Rebuild the inputs with
`python3 sims/board160.py --targets --csv`.

**Keeper: Luther Burden III (WR, consumes 10.09).** So you enter needing QB / 2 RB / 2 more WR /
TE / K / DST.

| pick | ov | TAKE | pos | ADP | VBD | why |
|---|---|---|---|---|---|---|
| **1.02** | 2 | **Bijan Robinson** | RB | 2 | +163.7 | Gibbs goes 1.01. +164 is the biggest edge in the draft — no decision here. |
| **2.09** | 19 | **Brock Bowers** | TE | 17 | **+93.7** | See "the 2.09 gamble" below. Take him. |
| **3.02** | 22 | **Ken Walker III** or **Derrick Henry** | RB | 20 | +34 | The only take-zone backs whose ADP survives to 22. Barkley (14), Chase Brown (16), Hampton (17) are gone. |
| **4.09** | 39 | **Emeka Egbuka** | WR | 35 | +15.4 | MUST. Won't last to 5.02. 76/1279/12 pace before injury; new OC talking Cooper Kupp role. |
| **5.02** | 42 | **Ladd McConkey** | WR | 38 | +16.2 | Elite TPRR in 12-personnel. Mike Evans (ADP 50) survives to 6.09 — take McConkey now, Evans later. |
| **6.09** | 59 | **David Montgomery** | RB | 55 | +6.1 | MUST. Your RB2. Will NOT reach 7.02. Gets the ball every time Houston is inside the five. |
| **7.02** | 62 | **Parker Washington** | WR | 73 | +23.4 | MUST. **The biggest edge you have.** Do not wait to 8.09 — 6 picks past his ADP is a real risk. |
| **8.09** | 79 | **Justin Herbert** | QB | 74 | +9.8 | MUST. Six teams keep a QB so the tier holds this long. 20.2 hppr/wk, same as Burrow. |
| **9.02** | 82 | **Jordyn Tyson** | WR | 79 | −14.8 | Bench WR with a real role. |
| ~~10.09~~ | — | **BURDEN — keeper** | WR | — | +18.7 | — |
| **11.02** | 102 | **Jayden Reed** | WR | 98 | −26.2 | Consolidated GB target share after Doubs/Wicks left. |
| **12.09** | 119 | **Jacory Croskey-Merritt** | RB | 114 | −69.8 | RB depth. The pool is dead here — take a body. |
| **13.02** | 122 | **Matthew Golden** | WR | 123 | −45.1 | Upside dart. |
| **14.09** | 139 | **Kenneth Gainwell** | RB | 343 | −58.0 | Biggest ADP gap on the board — worth #136, drafted at 343. Free handcuff. |
| **15.02** | 142 | **Seattle Seahawks D/ST** | DST | — | — | 61.6 over weeks 1-3, top-3 all three weeks. Not the Broncos. |
| **16.09** | 159 | **Cameron Dicker** | K | — | — | Nick is 70th of 150+ at kicker. Stop thinking. |

**Final roster:** QB Herbert · RB Bijan + Montgomery · WR Burden + Egbuka + McConkey + Washington ·
TE Bowers · DST Seattle · K Dicker, plus Tyson/Reed/Golden/Croskey-Merritt/Gainwell on the bench.

---

## Why this and not something else

### The 2.09 gamble — the one place I overruled the model

Only **two picks** separate your 2.09 and 3.02. The optimiser noticed that and suggested taking
Saquon Barkley at 2.09 and Bowers at 3.02 — getting **both**, because Bowers' ADP of 17 means he
"should" survive two more picks.

**Don't do it.** Both picks in that gap belong to **Rod (NCF)**, and Rod needs **1 TE**. He is the
single most likely man in the league to take Bowers, and he picks twice before you're back. Bowers
is +93.7 — nearly three times the best back available. Risking a 93-point edge to gain a 36-point
one, against the one opponent who needs exactly that position, is a bad trade.

Take Bowers at 2.09. If he somehow lasts to 3.02 anyway, you got lucky and you take a back at 2.09.

### Why no take-zone back until 3.02, and why that's fine

Every take-zone back has an ADP of 14–20 and your second pick is overall **19**. In back-to-back
real mocks, **all five drained by 2.08**. Realistically only Ken Walker or Derrick Henry survives
to 3.02.

That's survivable because RPB starts **two** RBs and no FLEX. Your plan's own finding: forcing a
back at 4.09+5.02 to fix a thin backfield costs **−32.4**, worse than living with it. So you take
Bijan, one mid back at 3.02, Montgomery at 6.09, and stop.

### Why Washington at 7.02 and not later

His ADP is 73; 7.02 is overall 62. That's an 11-pick reach — deliberate. Waiting to 8.09 (overall
79) puts you **6 picks past his ADP**, and he is the single largest un-priced edge in your setup
(+34 points of return scoring nobody else models). Don't be clever with the one pick where you
know something the room doesn't.

### Why QB at 8.09 and not earlier

Six of ten teams keep a quarterback, so only four are drafted. QB1-to-replacement is **1.8 points
a week**. Herbert at ADP 74 lands at 8.09 with room to spare, and he projects the same 20.2
hppr/wk as Burrow. Every pick you spend on a QB before round 7 is a pick spent on your league's
cheapest position.

### The two risks in this roster

1. **RB is thin.** Bijan + Montgomery is your starting pair, and the bench backs are dart throws.
   That is a deliberate consequence of taking Bowers over a second back — and it is the correct
   trade at +93.7, but it means a Bijan injury hurts badly.
2. **Washington's return job.** If Jacksonville pulls him off punt returns once he's a full-time
   receiver, he drops from +23.4 to about +10.7. Still positive, no longer a steal.

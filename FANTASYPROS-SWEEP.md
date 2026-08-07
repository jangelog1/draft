# FantasyPros research sweep — RPB

Run **2026-08-07**. First time this sweep has ever run; it had been the oldest outstanding item.

Pulled through the in-app browser (JS-rendered tables — `WebFetch` returns empty shells for all of
these). **The logged-in Chrome session was unavailable** — the Chrome MCP is still fully blocked,
`This site is blocked` on every call including `tabs_context_mcp`, unchanged from last session. So
these are the free-tier views, which cut off partway down each report. What that cost is noted per
section.

---

## 1. Expert accuracy — the headline finding

**Nick Zylak (Fantasy Football Advice) ranked #10 overall out of 150+ analysts in 2025 draft
accuracy.** Your guy is legitimately top-ten. Per-position, lower is better:

| position | Nick's rank |
|---|---|
| **RB** | **11** |
| **DST** | **15** |
| **TE** | **15** |
| QB | 22 |
| WR | 22 |
| K | **70** |

Read this against how you actually use him:

- **His RB-early thesis is his strongest position.** RB is his best skill rank, and it is the thesis
  the whole draft plan is built on. That is the correlation you want.
- **D/ST 15 is good, and `DST-STREAMING.md` already said so** — but that file also warns not to
  follow any single ranker on D/ST. Still true. Nick at 15 is a tiebreaker, not a source; the Vegas
  implied totals in `dst_rank.py` outrank him.
- **Ignore him completely at kicker.** 70th of 150+. 16.09 is a coin flip; do not spend thought on
  it.
- **QB 22 / WR 22 are mid.** His WR calls carry your 4.09/5.02/6.09 block, so weight the *format*
  reasoning (Evans in half-PPR) over the raw ranking.

Top of the board for context: Justin Boone (Yahoo) 1st, Patrick Thorman (Establish the Run) 2nd,
Jamie Calandro (RotoBaller) 3rd.

*Gated after 10 rows — which is exactly enough, since Nick is 10th.*

---

## 2. RB handcuffs — for the backs you will actually own

The interactive chart cuts off after ten teams alphabetically (Arizona–Denver). The rest comes from
FantasyPros' May 2026 handcuff article, which is tiered.

**Your plausible backs and their handcuffs:**

| your back | team | handcuff | tier | note |
|---|---|---|---|---|
| Bijan Robinson (1.02) | ATL | **Brian Robinson Jr.** | 2 — should lead committee | 12th-round ADP. Early-down only, no pass-catching. |
| Jahmyr Gibbs (1.02 alt) | DET | **Isiah Pacheco** | 2 | "Declining role; losing snaps to other backups" — a weak handcuff. |
| Saquon Barkley | PHI | **Tank Bigsby** | 3 — zeroes or heroes | Non-pass-catcher, often behind Will Shipley. Bad handcuff. |
| Ken Walker III | KC | **Emmett Johnson** | 3 | Fifth-rounder, and a Kareem Hunt return looms. Messy. |
| Chase Brown | CIN | **Samaje Perine** | 2 | 26th-round ADP. Veteran, unlikely to see 20+ touches. |
| Omarion Hampton | LAC | **Keaton Mitchell** | 2 | **See below — this one matters.** |
| Derrick Henry | BAL | **Justice Hill** | 4 — is the juice worth the squeeze | 21st-round ADP, pass-down specialist, "minimal injury-contingent upside". |

### The two that change a pick

**Keaton Mitchell is both Omarion Hampton's handcuff AND on your FFA must-draft list.** That is the
only place in this sweep where the handcuff chart and Nick's list point at the same man. If Hampton
is the take-zone back you land, Mitchell late is a genuine double-dip rather than a dead bench
spot. Caveat FantasyPros gives: 5'8", 179 lbs — explosive but undersized.

**Jonathon Brooks (CAR) is Tier 0 "standalone value" and also FFA must-draft** — and the starter he
backs up is **Chuba Hubbard, who is on your FFA shy-away list**. Nick is fading the starter and
buying the backup on the same depth chart, and FantasyPros independently grades that backup as
having value even without an injury. 8th-round ADP. That is a coherent, corroborated target, not a
handcuff lottery ticket.

### Two data problems in the source, flagged not smoothed over

- The article lists **Zach Charbonnet (SEA) backing up Kenneth Walker III** in Tier 1, while the
  current rankings page has **Walker on Kansas City** with Emmett Johnson behind him. The article is
  from May and is stale on Walker's team. Trust the rankings page.
- The article lists **"Alvin Kamara (NO) | Travis Etienne"** in Tier 3, which is incoherent — Etienne
  is your Jacksonville keeper and Kamara is a Saint. Tier 0 separately lists **Chris Rodriguez Jr.
  (JAX)** as having standalone value. **Etienne's handcuff situation did not resolve in this sweep.**
  Given he is your R10 keeper and already below the RB replacement line, this is worth one direct
  look before draft day.

---

## 3. Fantasy points leaders (2025, half-PPR)

Gated after 8 rows, so this is a cross-check rather than a report.

**It confirms the number the plan is built on: Josh Allen finished 2025 at 374.6 points**, first
overall. `plan-rpb.json` quotes "Josh Allen (374 pts)" — verified.

The rest of what showed: Drake Maye 359.0, Stafford 358.4, Trevor Lawrence 350.2, Prescott 323.8,
Caleb Williams 323.2, **Jonathan Taylor 316.3 (the only non-QB in the top 8)**, Bo Nix 315.8.

Six of the top eight scorers in 2025 were quarterbacks — and **six of ten RPB teams keep a QB**.
That is the same fact from two directions, and it is why the QB tier survives to 7.02.

---

## 4. Snap count analysis — NOT OBTAINED

The report renders only Philadelphia and then hits "Create a free account to unlock". This is the
one report of the four that a free-tier view genuinely cannot deliver, and it needs your logged-in
session.

**Blocker: the Chrome MCP.** Still returning `This site is blocked` on every call, including
`tabs_context_mcp`, exactly as recorded in the last handoff. It has now failed across two sessions.
Restarting Chrome and/or the extension is the next thing to try, and it is your action, not one I
can take.

---

## 5. ECR-vs-ADP on the names in your plan

From the 2026 consensus board (92 experts, Aug 7). Positive = experts rank him ahead of where he is
being drafted (the market is late on him); negative = the market is drafting him ahead of where
experts rank him.

**Falling — the market is ahead of the experts:**

| player | ECR vs ADP | relevance |
|---|---|---|
| **Devon Achane** | **−16** | RB12, and the market is 16 picks ahead of consensus. Independent support for removing him from the take zone. |
| Jeremiyah Love | −18 | The pivot-from back. Already outside the zone. |
| Ashton Jeanty | −9 | FFA must-draft. Being drafted well ahead of consensus. |
| **Omarion Hampton** | **−9** | Take-zone back. You are paying up if you take him at rank. |
| Josh Jacobs | −10 | |
| Breece Hall | −10 | The 5.02 anchor-RB temptation the plan already rejects. |

**Rising — the experts are ahead of the market:**

| player | ECR vs ADP | relevance |
|---|---|---|
| Zay Flowers | +15 | **MWV only.** Your `rpbFormat` block explicitly fades him in half-PPR. Do not act on this in RPB. |
| DeVonta Smith | +15 | |
| Nico Collins | +14 | The WR you took at 3.02 in the 08-06 mock. |
| A.J. Brown | +14 | Now New England. |
| Emeka Egbuka | +10 | FFA must-draft. |
| Brock Bowers | +8 | TE1, ranked 17th overall. |

**Bowers is ranked 17th overall by consensus and your pick 2.09 is overall pick 19.** That is the
arithmetic behind why he keeps falling to you — he is not falling far at all. The sims claimed he
never reaches pick 19 in 52,200 drafts; consensus says pick 17 is his home. Two picks of variance,
not a miracle. `sims/README.md` has been corrected accordingly.

---

## Bye weeks for the take zone

Worth a glance since RPB has no FLEX and only two RB slots.

Barkley 10 · Ken Walker 5 · Chase Brown 6 · Hampton 7 · Henry 13 · (Bijan 11, Gibbs 6, Etienne — check)

Gibbs bye 6 and Chase Brown bye 6 collide. So do Bijan 11 and nothing else in the zone. No
disqualifying stack, but if you open Gibbs then Chase Brown you are starting one RB in week 6.

---

## What to do with this

1. **Add Keaton Mitchell and Jonathon Brooks to the late-round shortlist** — both are FFA must-draft
   AND independently graded by FantasyPros, which no other name on the must-draft list can claim.
   Brooks especially: 8th-round ADP, standalone value, backing up a man Nick is fading.
2. **Stop thinking about the kicker.** Nick is 70th at K; nobody is good at it.
3. **Resolve Etienne's backfield** before draft day — the source contradicted itself and he is your
   keeper.
4. **Fix the Chrome MCP** if you want snap counts.

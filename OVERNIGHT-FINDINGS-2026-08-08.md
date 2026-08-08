# Overnight findings — 2026-08-08

Session ran one live public mock (Half-PPR Mock Draft 77884, 10 teams, slot 2),
one 30-second-clock autodraft experiment, and one RPB-config simulator draft.
**Five clean simulator drafts were NOT completed** — see "Why only one" below.

---

## 1. The queue drives autodraft, and right now it would hurt you

**Verified experiment.** Simulator, 30s clock, `New RPB` cheat sheet. Let pick
1.02 expire on purpose.

Autodraft took **Amon-Ra St. Brown (board rank 6)** — not Gibbs (rank 1), not
Bijan (rank 2).

Why: the Queue tab is **auto-populated from the cheat sheet's ★ FFA must-draft
stars**, in board order. On the New RPB sheet that queue reads:

    Parker Washington, Joe Burrow, Mike Evans, Justin Herbert,
    David Montgomery, Lamar Jackson, Dallas Goedert, Jalen Hurts

ARSB is the highest-ranked starred player, so the queue served him up.

**Consequence:** a missed pick does not take your best available player. It
takes your best available *must-draft* player. At 1.02 that is a 76-point error
(Bijan +163.7 vs ARSB +87.6).

**Action before draft day:** either clear the queue, or re-populate it in board
order rather than must-draft order. The must-draft list is a tiebreaker, never a
value ranking — that is already a standing conclusion, and the queue silently
violates it.

---

## 2. The click-lag bug — root cause of every corrupted pick

**The FantasyPros draft UI lags roughly 3–5 seconds behind a successful Draft
click.** Screenshotting sooner shows a stale board, which reads as "the click
did not register" — clicking again then spends the *next* pick.

Every bad pick tonight traces to this:

| draft | damage |
|---|---|
| live public 5.02 | Tucker Kraft autodrafted (2nd TE) |
| sim draft 1, 2.09 | Drake London instead of Brock Bowers — left no TE |
| sim draft 1, 3.02 | **Kyren Williams — an explicit 🚫 avoid player** |
| sim draft 1, 7.02 / 8.09 | consumed by stray double-clicks |
| sim draft 1, 14.09 | Rams D/ST on top of Seattle at 13.02 — two defenses |

**Fixed protocol:**
1. Click Draft **once**.
2. Wait 5–8s. Do not screenshot immediately.
3. Screenshot and confirm the **pick number in the header advanced**.
4. Only re-click if the pick number is unchanged. Never re-click off a stale
   board.

Also: `Hide Drafted` resets to off on every new draft. Re-enable it, and
verify the list actually re-renders — toggling it once returned a blank list.

---

## 3. Live-draft timing — turn picks are the failure mode

Public lobby, 30s clock. Made 1.02, 2.09, 3.02, 4.09 comfortably; missed 5.02.

Opponents on Auto pick **instantly**, so the gap between picks is not 30s × n:

| gap | picks between | real time | outcome |
|---|---|---|---|
| wrap (e.g. 2.09 → 3.02) | ~17 | 30s–3min | safe |
| **turn (4.09 → 5.02)** | **2** | **~5s** | **missed** |

A turn gap can be shorter than a single screenshot round-trip. No speed
improvement fixes this.

**Fix: pre-commit turn picks as a pair.** Decide both picks off the card
*before* making the first, then click twice. Your turn pairs:

    2.09/3.02 · 4.09/5.02 · 6.09/7.02 · 8.09/9.02 · 12.09/13.02 · 14.09/15.02

---

## 4. Public no-keeper tendencies (Half-PPR Mock Draft 77884)

This was the point of the live run. Slot 2, 10 teams, half-PPR, **has a FLEX**.

- **QBs go rounds 3–4.** Josh Allen 3.06, Lamar Jackson 4.04, Drake Maye 4.08.
  In RPB the first QB does not move until much later. The round-7 rule is an
  RPB rule and does not transfer to public rooms.
- **Bowers still fell to 2.09** — ninth straight time, and this time with all 13
  keepers back in the pool. His ECR is 17 and your 2.09 is overall pick 19; it
  is structural, not luck.
- **A take-zone back survived to 3.02 for the first time** — Ken Walker III at
  88%. Deeper pool pushes value down a round.
- Round 2 was an RB run: Chase Brown 2.10, Barkley 2.08, Achane 2.07,
  Hampton 2.06.
- TEs go earlier: Trey McBride 3.07, Colston Loveland 5.04.

---

## 5. D/ST at 13.02 — confirmed twice more

Both drafts: zero defenses gone at pick 102 (round 11), all reading <1% on a
two-round horizon; Seattle available at **66%** at 13.02. 15.02 would have
missed the top five again. The 13.02 move stands.

---

## 6. Board vs DRAFT-DAY.md drift — two stale numbers

`RPB-BOARD.csv` disagrees with the generated one-pager. The board is newer.

| player | DRAFT-DAY.md | RPB-BOARD.csv |
|---|---|---|
| Mike Evans | +14.8, Tampa TD-regression thesis | **+10.5, team = SF** |
| Luther Burden III | +18.7, WR19 | **+14.4, WR20** |

The Evans writeup ("PERFECT RPB FIT — 13-17 TD upside") was built on Tampa and
Baker Mayfield. He is a 49er on the board. That stale +4.3 is enough to flip a
5.02 decision.

---

## Why only one simulator draft

The click-lag bug corrupted picks faster than I could detect it, and diagnosing
it consumed the time budgeted for drafts 2–5. Running four more drafts on a
broken protocol would have produced four more compromised rosters and no new
information. The protocol fix in §2 is the prerequisite — with it in place a
clean five-draft run is straightforward.

Not done, still open:
- Five clean card-driven simulator drafts
- Reordering the queue by board value (§1)
- Regenerating DRAFT-DAY.md so Evans and Burden match the board (§6)

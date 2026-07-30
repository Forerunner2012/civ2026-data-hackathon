# How do 15–30 submissions get judged and presented?

Type: grilling
Status: resolved

## Question

Ticket 20 established **30 participants working solo or in duos — 15 to 30 submissions**. Ticket
08 established the programme's fixed slots: the session runs 09:30–12:30 and results are
**14:30–15:00, thirty minutes**.

§4.2 and §4.6 both assume six to eight teams and a three-minute pitch each, with a jury that has
heard every team. **That does not fit.** Fifteen three-minute pitches is 45 minutes before
turnover; thirty is impossible. Yet the qualitative rubric categories — Visualization and
explanation (15), Investigation and hypothesis (15), and the agent bonus (10) — all assumed a
team explaining itself to a jury.

What has to be settled:

- **Does everyone pitch?** If not, how are presenters selected, and is the selection itself part
  of the score?
- **What carries the qualitative categories instead** — the written `report.md` already in the
  submission? A poster round? Points redistributed toward machine-scorable categories?
- **Jury load.** With 30 submissions, anything not machine-scored means reading 30 reports. Who
  does that, and when — the results block is 30 minutes and the lunch is two hours.
- **Is the two-hour lunch working time?** It sits between the session and the results block. It
  could be pitch preparation, a poster session, or genuinely a break.
- **Does the transfer task get its own moment** in the results, given ticket 14 moved the
  difficulty there?
- **Solo versus duo fairness** — are they ranked together, and does a duo have an advantage worth
  correcting for?

## Why this is on the frontier

Nothing blocks it, and it reaches back into the rubric rather than only the schedule. It is the
largest unresolved consequence of the cohort answer.

## Answer

**Auto-score everything scorable at 12:30; the jury reads capped written reports over lunch; the
results block is a reveal plus a few selected walkthroughs.**

### The shape

| When | What |
|---|---|
| 12:30 | Submissions close. `civ score` runs on every entry, unattended. |
| 12:30–14:30 | Jury splits the written reports between them and awards the judgement-based points. |
| 14:30–14:40 | Reveal: leaderboard, and what the scores actually showed. |
| 14:40–14:55 | Walkthroughs from ~4 selected entries. |
| 14:55–15:00 | Wrap on the transfer lesson. |

Every submission is genuinely assessed, which no live-pitch model can promise at this cohort size.
The two-hour lunch stops being dead time.

### Rubric split

Judgement-based points move onto the written report rather than a spoken pitch:

| Machine-scored at 12:30 | Points |
|---|---|
| Detection | 25 |
| Evidence and extraction — clip validity, correct topics, volume reduction | 15 |
| Reproducibility — one command, pinned inputs, stable rerun | 15 |
| **Subtotal** | **55** |

| Jury-scored from `report.md` | Points |
|---|---|
| Investigation and hypothesis | 15 |
| Quality and evaluation — including the failure analysis | 15 |
| Visualization and explanation | 15 |
| **Subtotal** | **45** |

Bonus (20) stays with the jury, since ticket 12 judges an agent trace qualitatively.

### `report.md` becomes a scored artifact, so it gets a cap and a fixed shape

One page, hard cap. Fixed headings, so 30 reports can be scored consistently and quickly, and so
each heading maps to exactly one rubric category:

1. Question and detection hypothesis
2. Signals used, missing, or judged unreliable
3. **What transferred to the second dataset, and what did not**
4. One failure or ambiguity, and what you changed
5. Downstream action and deployment mode

Heading 3 is new, and it is the one that makes the transfer insight scoreable rather than
invisible.

### Selecting the walkthroughs

Roughly four: the top entries, **plus the most instructive failure**. Showcasing a good failure is
not a consolation prize — §2 makes failure a deliverable, and a room of practitioners will learn
more from one honest dead end than from three clean wins. Say so when introducing it, or it reads
as a booby prize.

### Open sub-question this inherits from ticket 16

**How the 25 Detection points divide between Kashiwa and the French transfer.** Recommendation:
**10 Kashiwa / 15 French**, because ticket 20 established that transfer is where the difficulty
lives and Kashiwa detection is effectively the warm-up. Someone who never reaches the second
dataset scores 10 of 25 — harsh, and the correct incentive.

**Provisional on ticket 24.** If the French recording turns out to hold few left turns, the
transfer score becomes noisy and the weighting has to move back toward Kashiwa.

### Two operational requirements this creates

- **Submission intake at 12:30** for 15–30 entries, and it must be quick — a shared drive, a
  git remote or a physical hand-in. Undecided; it is execution, but it needs an owner.
- **Unattended batch scoring of 15–30 submissions inside the lunch window.** That is a throughput
  requirement on the evaluator that ticket 15's gates should test explicitly, not just correctness
  on one submission.

### Solo versus duo

Ranked together, on one leaderboard. Splitting a 15–30 person cohort into two rankings makes both
thin, and a duo's advantage is smaller than it looks when the bottleneck is understanding the
event rather than typing. Worth stating in the brief so nobody feels ambushed.

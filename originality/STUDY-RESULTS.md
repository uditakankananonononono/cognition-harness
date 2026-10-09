# Known-operator selection ambiguity stress study

October 9, 2026. Final report with scoped wording/arithmetic review. Descriptive results only.

## Result

Disagreement retention did not separate from fixed retention on any of the 512
synthetic task instances: both selected the same finalist on every task, obtained
3737/4096 correct final-case outputs and passed all eight final cases on 422/512
tasks. First-representative retention obtained 3732/4096 correct case outputs and
also passed 422/512 tasks. First versus either other method exchanged 58 task wins
and 58 task losses. This study supports no accuracy advantage for disagreement
retention. The five-case difference against first is not evidence of a method advantage
or statistical significance. The 58/58 task split comes from deterministic
eligibility and tie-break rules: first favors earlier grammar representatives,
leaving identity/zero late in collision buckets; fixed/disagreement expose those
lower-complexity expressions, so the shared ranking selects them instead of
abs/positive/negative. Ranking and tie-break rules set the outcome.

This is a **descriptive known-operator selection ambiguity stress study**, not a
test of invention, AGI, independent transfer, arbitrary-source execution, pruning
speed, secure execution or memory savings. The shared development-fit/complexity
ranking largely determined outcomes. Prior exploratory feedback had already shown
little method separation; this redesign followed that feedback and is not an
untouched preregistration made without prior performance evidence.

## Frozen contract and custody

Frozen source tip: `81c34a6531a1e6a1087e34f17ed00da816b0a5b1`, on the
`exploration-ledger` branch of
https://github.com/uditakankananonononono/cognition-harness .
The frozen v2.1 contract is `originality/STUDY-REDESIGN-V2.md`; the source/pool
manifest is `originality/RUNNER-PROPOSED-MANIFEST.json`, status `frozen`.
These paths identify repository artifacts, not invented web-page URLs.
The final status-only commit changed no contract, runner or pinned file bytes.

The contract defines exact-target identity recovery as follows:

> Exact-target identity recovery means the finalist expression is the same grammar
> entry as the instance target BY INDEX. Find the finalist's unique entry in the
> fixed ordered grammar above and compare its index to the target index. Null
> finalist is failure for both identity recovery and final-case correctness.
> Equivalent-on-finals is the separate all-8-cases pass metric and is not target
> identity recovery.

The eight developer-known targets, in fixed index order, are:

| Index | Operator | Semantics |
|---|---|---|
| 0 | add +1 | x+1 |
| 1 | add -1 | x-1 |
| 2 | neg | -x |
| 3 | abs | absolute value of x |
| 4 | positive | max(0,x) |
| 5 | negative | min(0,x) |
| 6 | identity | x |
| 7 | zero | 0 |

An evaluator separate from builder and gate constructed the private final pack
only after source freeze. The evaluator reports Python 3.10.12, an independent
oracle without importing `study_runner.interpret`, no old-pack reuse and no
filtered/replaced samples. Builder received aggregate results and custody hashes
only, not the seed, final pack or final-case data. The author has not independently
inspected those private artifacts; custody and scores below are evaluator-reported
through the parent, not builder-reproduced final measurements.

The specified PRNG was Python `random.Random` (Mersenne Twister), with a private
integer seed hash-committed as the UTF-8 decimal integer string. Target index,
dev-count 1..4 and instance ordinal 0..15 fixed the generation order. Development
inputs were sampled without replacement from -32..32, then eight final inputs
were sampled from the ascending-order remainder. Thus there were 64 instances
per target, 128 per dev-count, 512 tasks and 4096 final cases per method.
These correlated synthetic constructions are not independent real-world trials.
Eight targets x 64 instances are templated: the effective diversity behind 422/512
is closer to eight target blocks than 512 independent tasks. This is a design
warning, not a computed effective sample size. First's identity/zero blocks each
have 35/64 passes, not wholly failed blocks; it also misses some abs/positive
instances. Fixed/disagreement partially fail abs/positive/negative blocks.

## Methods and logical costs

All methods generated the same eight known expressions, retained a full shared
archive and executed every expression on the development inputs and public pool.
They differed in eligibility: first representative per development-output bucket;
first K per bucket; or maximum-disagreement probe partition with first source per
output group, capped at K. K=4 per bucket. One finalist used development mismatches,
then complexity (identity/zero 0, other operators 1), then grammar order.
The public pool contained -8,-3,-1,0,1,2,5,8. Public probes had no expected answers.
Public probes and private finals shared the integer domain; overlap is a limitation,
not proof of independent transfer. Neither final inputs nor answers ranked finalists.

Execution cap was 1024 scalar calls/task/method; canonical ledger cap was 32768
bytes/task/method. Logical ledger-byte limits do not bound temporary vectors,
enclosing receipts, heap memory or CPU. No arbitrary-source sandbox is tested.
All methods paying for the full pool means this is selection-policy comparison,
not evidence of pruning compute savings.

## Stage A: selection-only aggregates before scoring

There were zero cap exits and zero null finalists. All three finalists agreed on
382 tasks; exactly two agreed on 130; all three distinct occurred on zero tasks.
First/fixed disagreed on 130/512 (25.3906%); first/disagreement also 130/512;
fixed/disagreement disagreed on zero tasks. The 130-task subset was fixed before
expected-answer scoring, not chosen from successful outcomes.

| Target index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Tasks with method disagreement | 0 | 0 | 0 | 10 | 34 | 28 | 29 | 29 |

| Development input count | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Tasks with method disagreement | 69 | 40 | 13 | 8 |

| Charged total | First | Fixed | Disagreement |
|---|---:|---:|---:|
| Generation | 4096 | 4096 | 4096 |
| Dev scalar execution | 10240 | 10240 | 10240 |
| Probe scalar execution | 32768 | 32768 | 32768 |
| Pool scan requests | 32768 | 32768 | 32768 |
| Canonical ledger bytes, summed across tasks | 1214806 | 1371622 | 1376258 |
| Unused scalar execution budget | 481280 | 481280 | 481280 |

Ledger-byte totals are summed serialized receipt sizes, not simultaneous memory
footprints, storage-duration measures or speed measurements.

## Stage B: locked final scoring

| Metric | First | Fixed | Disagreement |
|---|---:|---:|---:|
| Correct cases /4096 | 3732 | 3737 | 3737 |
| Case accuracy, reported to 4dp | 0.9111 | 0.9124 | 0.9124 |
| All-8-cases task passes /512 | 422 | 422 | 422 |
| Exact target index recovery /512 | 422 | 422 | 422 |

Identity recovery equaled task-pass count in every reported cell. That is an
observed equality, not a redefinition of the two metrics.

| Paired task pass: left vs right | Left win | Tie | Left loss |
|---|---:|---:|---:|
| First vs fixed | 58 | 396 | 58 |
| First vs disagreement | 58 | 396 | 58 |
| Fixed vs disagreement | 0 | 512 | 0 |

On the prespecified disagreement subset of 130 tasks (1040 final cases), first
case accuracy was 0.7163 with 58 task passes; fixed and disagreement each obtained
0.7212 with 58 task passes. First versus either other method: 58 wins, 14 ties,
58 losses. Fixed versus disagreement: 0 wins, 130 ties, 0 losses.

### By target

All entries are task passes out of 64. Exact target index recovery is identical
in each reported cell.

| Target | First | Fixed | Disagreement |
|---|---:|---:|---:|
| 0: add +1 | 64 | 64 | 64 |
| 1: add -1 | 64 | 64 | 64 |
| 2: neg | 64 | 64 | 64 |
| 3: abs | 46 | 36 | 36 |
| 4: positive | 50 | 30 | 30 |
| 5: negative | 64 | 36 | 36 |
| 6: identity | 35 | 64 | 64 |
| 7: zero | 35 | 64 | 64 |

First also failed some abs and positive tasks; its failures were not limited to
identity/zero. Fixed/disagreement traded those identity/zero gains for losses on
abs/positive/negative. No target-wise positive result overrides the overall null.

### By development input count

| Dev count | First task passes /128 | Fixed/disagreement passes /128 | First case accuracy | Fixed/disagreement case accuracy |
|---|---:|---:|---:|---:|
| 1 | 78 | 80 | 0.7871 | 0.8047 |
| 2 | 100 | 102 | 0.9043 | 0.9043 |
| 3 | 119 | 118 | 0.9648 | 0.9639 |
| 4 | 125 | 122 | 0.9883 | 0.9766 |

## Custody receipt identifiers

These are full identifiers reported by the evaluator. Private bytes are not in
this report, source repository or builder workspace. Hashes identify integrity
receipts, not independent authentication or proof of secrecy.

| Item | SHA256 or git commit |
|---|---|
| Seed commitment | `78a1f61c39bdec9b0181e151dbf8fe0f6f181b81b3c71304594bca6888a049cd` |
| Private pack | `462bde2658b257a66f3c219f14656e5c5cbae9cf7355d4821b3f14a4648e363a` |
| Generator | `94980a242dedfad09069ddb5064c55df2f94625b447753e84acd93edaad8f304` |
| Stage A receipt | `c2eab3d5212b0876cbf27f34f72bda0c4ebbe3bec6e61c8254daea0196c29c52` |
| Stage A aggregate | `6a3279dd8a55a40c1025a29d974eb0452cff2d668b538beb3605aece25f79eec` |
| Stage B aggregate | `ec07765dc4cb82d6f576db88dcf76ede30be6ad61555b9d9853a0ff21dc53f84` |
| Frozen source git commit | `81c34a6531a1e6a1087e34f17ed00da816b0a5b1` |
| Public pool | `56a72e0bd095588f6cbfd514c84c2bf26bcd82da6802f47a9ecf38c0f0b5a88e` |

### Per-method custody addendum

| Method | Stage A selection SHA256 | Stage B aggregate SHA256 | Private per-case receipt SHA256 |
|---|---|---|---|
| First | `de6431d8efacd4e12765f0abace83698cca9277bdea1e5d8acf919c42b621d38` | `c720c41a8da141e5e4aed184b317bc6f2205e065e4b0b1ac3ebbb8568c596bee` | `2310421064f4e675570da057ccc0cb0a6c1af35ac1f2abb2e49d6ae0f8675ab9` |
| Fixed | `896837b829d94638d88330b08f80a9618f5bd303c3084431c920f2c819201704` | `e19145ed4b924ee22ddd03902503348c7b5c020b953be5f3956f497403ff03ac` | `0eb61beae1667f18df03ba159c798e5f5daac91c5889372778a1039442dc3b7f` |
| Disagreement | `1e64a94384600245fba8643702eb3437daf17cc565186c5636fef7caf0c0786b` | `e19145ed4b924ee22ddd03902503348c7b5c020b953be5f3956f497403ff03ac` | `0eb61beae1667f18df03ba159c798e5f5daac91c5889372778a1039442dc3b7f` |

Evaluator's exact caveat: fixed/disagreement Stage B and per-case hashes are
identical because their finalists never differed; the per-case receipts were
recomputed deterministically from the pinned pack at request time, not saved
during the Stage B run. These recomputed receipts are not contemporaneous
saved-run receipts. Their hashes were supplied in a later aggregate-only custody
addendum; private per-case receipt bytes are evaluator-only. Neither builder nor gate can
inspect those bytes. Scoped report review confirms wording and arithmetic fidelity,
not independently inspected private-case scoring provenance.

## Conclusion and boundary

The harness accounted for identical scalar execution charges and selected one
finalist with no cap exits on this synthetic study. Fixed and disagreement were
indistinguishable in selected finalists and reported outcomes. First versus either
traded 58 task wins for 58 losses because deterministic bucket eligibility and
shared complexity/grammar ranking selected different known operators. Retention
policy bought nothing measurable between fixed and disagreement on this suite;
fixed versus first differed by only five of 4096 cases (about 0.12 percentage
points), with identical task-pass totals. The ranking is the measured lever.
This is a null for the proposed disagreement-selection
advantage in this design, not proof that all disagreement methods cannot help.

Local mechanics review and independent aggregate scoring are different evidence.
The ledger still has no authentication, durable crash/race guarantees or verified
structured probe-cost provenance. Whole-receipt forgery can remain internally
consistent. Nothing here establishes learning, new operations, originality,
model/runtime superiority, statistical significance, generalization or AGI.
No activation or main-branch merge follows this report. Report wording/arithmetic received parent-reported SCOPED PASS, with the additions
recorded here. That review does not remove evaluator-only custody limits. Separating
methods would need ambiguity that the ranking cannot resolve; this suite is not it.

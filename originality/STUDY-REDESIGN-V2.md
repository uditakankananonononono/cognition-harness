# Selection ambiguity stress study v2, proposed

NOT FROZEN. No evaluator pack constructed or scored by builder. Runner mechanics
at e41ff6c received parent-reported SCOPED PASS, not an accuracy/benefit verdict.

## Why this is a redesign

Independent gate reported exploratory simulation results: little selection
separation and no disagreement advantage. Those results are already exposed.
This redesign is therefore a descriptive stress study selected AFTER exploratory
feedback, not preregistration uncontaminated by prior performance evidence. Do not
present a new evaluator pack as proof of previously unknown generalization.
We drop claims of improved retention accuracy, invention and pruning savings.
Question: how often do known-operator selection rules differ under ambiguous dev
examples, and when does the shared complexity preference hurt exact correctness?
A null or worse disagreement result remains a valid result, not grounds to retune.

## Fixed proposed task construction: 512 instances

Independent evaluator constructs pack ONLY AFTER gate-approved source freeze.
Use eight known GRAMMAR targets, 64 instances per target, allocated equally across
1,2,3,4 development inputs (16 instances per target per dev-count). This includes
abs, negation, positive/negative-part targets where lower-complexity identity/zero
can be wrong despite fitting some development evidence. No target is hidden from
builder by name; only final instances/answers are under separate custody.

Evaluator samples distinct integer dev inputs uniformly without replacement from
-32..32 using a private fixed-seed PRNG, then draws 8 distinct final inputs per
instance uniformly without replacement from remaining inputs. The evaluator pins
seed/generator/pack hashes privately before method execution. Dev/final disjointness
is per instance; tasks may repeat inputs across instances. Do not reject samples
based on ambiguity, selected finalist or outcome. The 512 tasks are correlated
synthetic constructions, not 512 independently sampled real-world problems.

Public probe pool stays the exact 8-input file already proposed. Its inputs may
overlap dev/final domain; unlabeled probe overlap is a declared limitation. No
fresh-transfer or unseen-operation claim. Old final packs must not be used.

## Methods, budgets and single finalist

Use unchanged e41ff6c runner, except documentation-only receipt wording correction.
Grammar/order, typed integer semantics and ranking are as implemented. K=4 per dev
bucket, execution cap=1024, ledger cap=32768. Each method generates all 8 known
expressions and computes all dev/pool vectors. Cap exits count as failures, with
null finalist, not excluded tasks. Exactly one finalist ranks by dev mismatches,
then complexity (identity/zero 0, all others 1), then grammar order. This shared
ranking can make method eligibility irrelevant or select a worse candidate.
Do not change it after the evaluator pack is built.

The shared full archive/pool scan means this is selection-policy comparison, NOT
pruning-efficiency, restoration-memory savings or secure source execution evidence.
Logical ledger caps do not bound Python temporary vectors, output receipt bytes,
CPU or heap memory. Runner executes trusted finite operators, no arbitrary source.

## Stage A: selection-only receipt, before expected-answer scoring

For all 512 task instances, evaluator runs each method with only dev pairs and
public pool. Write a pinned receipt including source/config/pool/pack identifiers,
charged generation/dev_scalar/probe_scalar/pool_scan/ledger_bytes, status, finalist
source hash and eligible-source-hash list. It must not contain final-case answers.
Before scoring publish aggregate counts:
- all three finalist hashes equal; all three distinct; exactly two equal;
- pairwise finalist-hash disagreement share (first-fixed,first-disagreement,
  fixed-disagreement), with nulls reported separately;
- selection-only disagreement counts by target and dev-count;
- cap exits and actual costs, including unused executions.
If methods never differ, retain that degeneracy and do not advertise an accuracy
comparison as a meaningful test of retention. No adaptive replacement tasks.

## Stage B: locked descriptive final scoring

Evaluator independently interprets each selected expression on its private final
inputs and compares exact integer outputs with its own target/reference outputs.
Do NOT import the builder interpret() as the answer oracle. Check independent
oracle on developer-known fixtures before scoring, without sending final cases.

Report all 512 tasks and 4096 cases per method, cap exits included as failures.
Report case accuracy, all-8-cases task pass count and exact-target expression
identity recovery as separate metrics. Equal expressions on finite cases need not
be target identity recovery. Include paired task-pass win/tie/loss counts for each
method pair, results on the pre-scoring method-disagreement subset, and breakdowns
by target/dev-count. Do not select only positive subsets. No significance/transfer
claim, no speed superiority. Retain failures and null results.

## Custody and remaining decision

A separate evaluator, neither builder nor gate, must explicitly accept the
construction and oracle plan. Gate checks source/protocol/pool freeze bytes first.
No final data in git/bundles; evaluator retains private pack and private per-case
receipt, sends public-safe aggregates and hash-backed custody receipt afterward.
Builder sees no final input/expected-answer file and does not build the final pack.

This v2 supersedes the 16-task plan in RUNNER-PROPOSAL-V1.md. Acceptance by gate
and evaluator remains unresolved. No experiment is announced complete or frozen.

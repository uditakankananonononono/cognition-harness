# Integer DSL runner proposal v1

Builder-tested plumbing, not frozen study. Parent-reported mechanics SCOPED PASS
covers ledger ancestor 50b8e56 only, not this runner. No performance result.

Narrowed from arbitrary generated source execution to a finite trusted integer DSL:
8 developer-known expressions in declared GRAMMAR order. Each operation is total
on integer inputs -32..32, producing integers -64..64. JSON bools are refused.
Errors in invalid configurations refuse before running; execution/ledger cap
exhaustion returns no finalist and the charged counts. No arbitrary Python eval,
worker sandbox, new grammar synthesis or unknown-operation discovery is claimed.

All three methods generate and retain the same eight candidates, compute every
candidate on all dev inputs and all eight pinned public pool inputs, charging all
scalar executions and scan requests, even when a method does not use the pool.
This controls actual scalar execution counts, but intentionally tests selection,
not pruning speed or compute savings. Generation count is 8, K default 4 per dev
bucket, scalar execution cap 1024, canonical ledger cap 32768 bytes. Receipt-byte
cap covers ledger only, not the enclosing runner receipt/temporary in-memory
vectors. Python memory/CPU/pool-file reads are NOT bounded by these logical caps.
The shared retained archive makes ledger cost comparable, but prevents conclusions
about the alternative's total memory advantage. These are deliberate study limits.

Exactly one finalist: minimum dev mismatches, then expression complexity
(identity/zero=0, other known operators=1), then declared grammar index. The pool
and final answers do not enter this ranking. Methods differ only in eligibility.
Method first retains first per bucket; fixed retains first K; disagreement retains
first per distinct output group at its most diverse public probe, max K per bucket.
K is per bucket, not global. A selection vector hash records all eligible sources.
No method can inspect final inputs/answers inside run(). This API alone is not a
custody guarantee: independent final-pack handling is mandatory outside the runner.

Negative finding, developer-known unit fixture, not unseen final data: dev pairs
(0,0),(1,1) cannot distinguish abs from identity; first keeps abs whereas output
diversity preserves identity and the common lower-complexity tie rule picks it.
On developer fixture x=-2, abs is correct for abs target and identity is wrong.
We keep this tradeoff rather than tuning ranking after final exposure. A failed
first test guessed a different negative fixture; its failure is retained in
receipts/runner-first-failed-run.txt. The corrected abs fixture passes. No study
scoring has occurred. 28 controls now pass in a new run (8 partition,12 ledger,8
runner); these do not establish generalization or secure execution.

Before freeze, evaluator must accept or reject this narrow proposal:
- New private final study: 16 task instances, 2 developer-known operators per
  grammar expression; evaluator selects 1..4 valid distinct dev pairs and 8
  disjoint final inputs per instance from -32..32. All operators are known to
  builder, no operation-discovery claim. No pair duplication within an instance.
- Exact integer per-case accuracy and task-all-cases pass count for each method;
  cap exits score zero and remain in denominators. Retain paired per-task deltas,
  all nulls and failures. Descriptive results only, not inferential significance.
- Evaluator must hold final tasks and expected values, construct them only after
  source/protocol/pool gate freeze, and independently evaluate exactly the emitted
  one finalist. Share only aggregate receipts, not final pack/source with builder.
- Final inputs and public probes can overlap as unlabeled integer domains; pool
  exclusion is not independent-transfer evidence. Do not reuse old final packs.

These evaluator choices are PROPOSED, not settled by builder or freeze-approved.
A formal frozen manifest must pin all source/test/pool/protocol bytes with this
scope, including failure semantics. No final scoring until gate/evaluator acceptance.

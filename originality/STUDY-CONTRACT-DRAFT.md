# Disagreement retention study contract, draft v1

Not frozen, not scored, not reviewed. The original eight-test partition prototype
is unchanged. The new source ledger is a local mechanics layer, not an empirical
study or a durable/authenticated store. Prior methods already include equivalence
refinement and disagreement probes. Novelty and performance remain unestablished.

## Testable question

Under equal caps, does retaining pruned candidate bytes and recovering candidates
when public probe outputs split a development bucket improve final-task correctness
versus first representative or fixed-order diversity? It may not. Correctness must
be measured by a separate evaluator, never inferred from disagreement.

## Methods to freeze before study execution

1. First representative of each typed development-output bucket, in generation order.
2. Fixed diversity: first K sources per bucket in the same order.
3. Disagreement: consider every retained source's outputs on the same public probe
   pool; choose maximum distinct typed outputs, lowest pool index breaks ties;
   retain the first source per resulting bucket, with the same K total selection cap.

All methods share source grammar/order, development cases, probe input pool,
scalar execution cap, selected-candidate cap and complete canonical receipt-byte
cap. Unused budget cannot become hidden extra searches. Charge generation,
development executions, all probe-pool scans, final candidate execution requests,
and bytes separately. Log charged and unused counts per method; equal cap is not
equal actual consumption. Current split() receives precomputed vectors and does
not execute or account for their production. It cannot serve as the study runner.

Public probes have inputs only, no expected answers. Probe evaluation must use
fresh isolated workers with limits. No code execution belongs in the ledger.
Before freezing, specify grammar and source order, pool bytes/hash, exact caps,
K, typing/error semantics, operation charges, finalist selection without final
answers, and whether all finalists or exactly one are scored. These are OPEN.
Different selection cardinality would confound accuracy and must not be hidden.

## Independent evaluator custody

The gate must approve a source/protocol/pool pin before a new evaluator constructs
or scores final cases. Evaluator owns final inputs/answers. Builder gets aggregate
results only after source freeze. Old M7/M8 and logistics final sets are spent and
must not be presented as unseen. Do not add final packs to any git bundle/repo.
Evaluator checks the source pin, full selection history, cap exits, nulls and failures.

Final task-count, sampling domain, generator and exact metrics are OPEN for an
independent evaluator. Pilot results will be descriptive; no statistical transfer,
unknown-operation discovery, learning, AGI, novelty or superiority claim follows.

## Mandatory negative conditions

- Candidates agree on all public probes: no split/no accuracy gain may result.
- A split retains a worse candidate: disagreement is not correctness evidence.
- Receipt byte cap or execution cap prevents retention: report cap exit, do not drop it.
- A pruned source cannot be recovered: explicit recovery failure, never a fabricated hash.
- Type-disparate outputs (bool vs int) must remain separate.
- Tampered source, event order, unknown source, invalid state transition: reject.

## Current deliverable boundary

retention_ledger.py retains exact source strings plus sequential reasons/events,
counts all serialized receipt bytes, and permits explicit prune/restore transitions.
Replay validation detects local event/status/hash inconsistency. A party able to
rewrite the entire receipt can forge a consistent replacement; no authentication,
append-only file durability, crash/race protection, sandbox or hidden-data exclusion
is implemented. The protocol hash is an identifier, not proof of a reviewed freeze.
Reasons currently carry probe/pool/decision labels as text, not structured verified
cost/pool records. Integration and experiment accounting remain future work.

The new tests are mechanics evidence only. Gate review must precede calling this
increment verified; study freeze and empirical verdict require separate reviews.

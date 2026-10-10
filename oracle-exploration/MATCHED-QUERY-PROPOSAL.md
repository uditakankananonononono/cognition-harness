# Matched development-query comparison, proposal

Not frozen, not scored. The prior 512-task retention null remains unchanged.
This increment adds a fixed-order label-query comparator to the reviewed prototype.
Both policies have the same full public-pool scan, oracle and logical cap access.
Adaptive picks maximum separated candidate pairs; fixed picks first unused pool
input even if the full scan shows no separation there. Full scans are deliberately
charged to both to isolate input choice, not compare efficient implementation cost.
Singletons stop without padding useless queries. Caps are equal, actual costs may
differ, and charged/unused counts must be retained per policy.

Developer-known abs/identity fixture with dev (0,0),(1,1), pool (2,-2), cap one
label: adaptive queries -2 and resolves abs; fixed queries 2 and stays ambiguous.
With cap two labels, fixed resolves too. This is an engineered unit fixture, not
empirical benefit evidence; it motivated this comparator before any final scoring.
There is no unlabeled-policy comparison pretending labeled information is free.

Proposed future study scope: descriptive known-expression query selection under
a trusted development-label reference, not invention or independent transfer.
Compare unresolved/null share, exact target-index recovery, final-case/task accuracy,
actual scalar executions/scans/oracle attempts and unused budget. Include all cap,
invalid/no-candidate/oracle-failure outcomes. No ranking fallback for either policy.

Before freezing, specify task construction, target order/dev counts/task count,
public-pool permutation sampling and pool bytes/hash, execution/query caps, private
seed commitment and evaluator independent oracle/custody. Distinguish two roles:
1. Labeled development query service consumes only allowed public pool inputs.
2. Final evaluator holds final inputs/answers; the development oracle must NOT
   answer arbitrary final-pack questions. Query inputs can share the declared
   integer domain, but final labels never flow to method selection.
All query outputs are expected development disclosures under the experiment;
private final cases remain hidden. No network callback in this mechanics code.

The same 8 known expressions are toy domain, callbacks trusted/unsandboxed,
receipts mutable, partial remaining_indices on generation-cap exit. Logical caps
are not time/memory/side-effect containment. No study claims or freeze from tests.
24 mechanics controls in NEW matched-policy receipt; original 18-test receipt
retained unchanged. Independent review is required before landing this increment.

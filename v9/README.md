# v9: operator invention vs operator menu

October 10, 2026. Frozen study, all receipts retained. Pending independent review.
No AGI, novelty, learned-model, or generalization claim. The mutation grammar is
builder-chosen; this measures open compositional search against a fixed repair menu
under an identical frozen judge, gate and sandbox.

## Question

Can a proposer that searches the composition closure of AST-level primitive
transforms repair programs whose fix is not in any predefined operator set -
verifiably beating the incumbent M1 menu proposer on a frozen suite? The search
space (133 deduplicated one-step children from the baseline alone, composing
multiplicatively with depth) is far beyond exact enumeration at survey scale,
meeting the closure gate of stateful-design/CLOSED-MEALY-FEASIBILITY.md.

## Frozen protocol

Freeze commit precedes all scoring. Manifest pin
e7f12875f0931942f408b0e74106c718cde9eebe08fb0a2ac30cbf116a18c631 (v9/frozen/).
Five task families x 16 hand-authored eval cases (80 total, exact JSON equality);
dev set 10 cases (2 per task), inputs disjoint from eval. Answer-key literals
verified against independent reference implementations by tests.py before scoring.
Baseline bugs are NOT text-matched by the incumbent's 3 operators (verified:
tests.py MenuControl). Judge verifies the manifest before and after scoring;
gate = strict total gain AND no per-task regression. Frozen eval scored ONCE per
arm by a separate process (judge.py). Proposers see dev cases only.

## Arms

- menu: incumbent M1 proposer, verbatim logic (3 named textual operators,
  dev hill-climb, 3 rounds).
- beam: beam search over AST primitive transforms (int-constant swap within
  {-2..3}, comparison/arith/bool op swap, same-arity call-function swap within
  a 6-name set, in-scope variable rename, call argument swap). Width 8, depth 6,
  execution cap 4000, deterministic ranking (dev passed desc, source sha asc).
- beam-macro: beam plus macro-operator reuse: any mutation that improves dev
  score is recorded as a (kind, old, new) macro and re-applied at all matching
  sites module-wide in later expansions. Tests cross-site/cross-task transfer
  of learned repairs.

## Results (receipts/study.json, receipts/study-measurement.json, dev-history-*.json)

Baseline on frozen eval: 28/80 (clamp 8, second 9, count 7, running 3, first 1).

| arm | changed | dev best /10 | executions | frozen passed /80 | per-task | gate |
|---|---|---|---|---|---|---|
| menu | no | n/a (no operator applied) | 1 | 28 | 8/9/7/3/1 | FAIL |
| beam | yes | 9 | 4000 (cap hit) | 68 | 16/16/16/16/4 | PASS |
| beam-macro | yes | 9 | 4000 (cap hit) | 68 | 16/16/16/16/4 | PASS |

Verified win: beam beats menu by +40 frozen cases under the identical frozen
judge; menu cannot modify this baseline at all. Four of five bugs fully fixed
(16/16 each). The count_even fix found by search (`n % 2 < 1`) is NOT the
hand-authored reference fix (`== 0`) but is extensionally correct on all
integers (frozen 16/16 including negatives): search found an unanticipated
correct repair. 3999 trials retained; 64 invalid (syntax/runtime), all recorded.

Null: beam-macro extracted 17 macros but produced identical frozen results and
identical execution counts. No verified separation; macro reuse is NOT kept as
an improvement. Retained as a null result, not hidden.

Known limit (documented, not fixed): first_above needs two coordinated edits
(`>=`→`>` AND `return limit`→`return v`); neither intermediate improves dev, so
greedy beam ranking prunes the lineage. Beam settled for a 1-mutation local
optimum (`v != limit`, frozen 4/16). Follow-up: plateau-tolerant search
(diversity retention or neutral-move budget) is the next experiment (v10).

## Reproduce

Linux, Python 3.10+, bubblewrap with user namespaces. Standard library only.

    python3 tests.py
    python3 run_study.py "$(cat receipts/frozen-pin.txt)"

Do not re-run freeze.py; it overwrites generated candidate/receipt paths.
No activation follows either command. All artifacts are local review-only.

## Next meaningful step

Independent review: check freeze ancestry, re-run all scores/controls, probe the
mutation engine for eval leakage (none exists by construction: eval bytes enter
only judge.py's namespace), and confirm the gate arithmetic. v10 (plateau
tolerance) must freeze its own suite before scoring and report against this
baseline as incumbent.

## Follow-up arm (added after v9 study close): v10 graded-fitness challenger

Graded-fitness beam (v10 challenger) run once on THIS frozen suite: 71/80, gate
PASS (first_above 4/16 -> 7/16; others unchanged). +3 vs binary beam's 68/80:
small verified gain here, but the same challenger scored 39/80 vs binary's 40/80
on v10's purpose-built plateau suite - no general separation. Full verdict in
v10/README.md. Receipts: receipts/graded-measurement.json, dev-history-graded.json.

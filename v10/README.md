# v10: fitness shaping for plateau crossing

October 10, 2026. Frozen study, all receipts retained. Pending independent review.
No AGI, novelty, or learned-model claim. Honest headline: MIXED - the challenger
shows a small verified gain on the v9 suite and no gain on the purpose-built
plateau suite. Not kept as an incumbent replacement; retained as evidence.

## Question

v9 documented that binary dev pass/fail ranking cannot cross neutral plateaus
(first_above needed 2 coordinated edits; the intermediate gives no pass signal).
Does adding a graded value-distance fitness (fitness.py: numeric/string/list/dict
distance between actual and expected DEV outputs, tie-breaking equal pass counts)
let the same beam search cross such plateaus - verifiably beating v9's binary
ranking under identical search space, budgets, judge, gate and sandbox?

## Two measurements

A. v9 frozen suite (pin e7f12875...; direct comparison with v9 beam's 68/80):
   graded beam -> 71/80, gate PASS. first_above 4/16 -> 7/16; other tasks
   unchanged at 16/16. best dev 9/10 (one None/4 categorical mismatch, distance
   10, gives no gradient). +3 frozen cases: small verified gain. Receipts in
   v9/receipts/graded-measurement.json and dev-history-graded.json.

B. v10 purpose-built plateau suite (pin 9c7f30b8...; 5 tasks x 16 frozen cases;
   every bug needs >=2 coordinated edits; plateau property machine-checked by
   tests.py: NO single edit improves dev over baseline):

| arm | dev best /10 | execs | frozen /80 | per-task (scale/interval/sign/mid/evens) | gate |
|---|---|---|---|---|---|
| baseline | 1 | - | 22 | 1/4/15/0/2 | - |
| beam-binary (v9) | 5 | 4000 (cap) | 40 | 1/8/15/0/16 | PASS |
| beam-graded (v10) | 5 | 4000 (cap) | 39 | 16/4/15/1/3 | PASS |

## Verdict

No verified separation on the plateau suite (39 vs 40 - a 1-case difference is
not evidence of a method advantage). Each arm crossed a DIFFERENT plateau:
graded crossed scale_offset (numeric distance gradient worked as designed);
binary crossed evens_list and partly in_open_interval (sha-order retention luck
at width 8). Graded was actively misdirected on evens_list: distance preferred
list-length-preserving wrong predicates. in_open_interval (boolean outputs,
3-edit plateau) gave no gradient to either arm, as predicted at design time;
neither crossed it. sign3 (x=0 edge) not fixed by either.

Combined interpretation: distance shaping provides real but task-dependent
signal; it is not a general plateau solution. The binding constraint in both
studies is plateau RETENTION under width 8 + 4000-exec cap, not the fitness
ranking. Next experiment (v11) should attack retention directly: behavioral
dedup (collapse children with identical dev-output vectors - large observed
waste from commuting/neutral edits) and/or plateau widening, measured against
both v9 and v10 frozen suites. A combined passed+distance+novelty ranking is
the other candidate. Keep-rule: binary beam remains the incumbent proposer.

## Reproduce

    python3 tests.py   # 13 controls incl. machine-checked plateau property
    python3 resume_study.py   # or run_study.py "$(cat receipts/frozen-pin.txt)"

Freeze precedes scoring; MANIFEST excludes itself (self-inclusion bug fixed
during construction, documented here). Do not re-run freeze.py.

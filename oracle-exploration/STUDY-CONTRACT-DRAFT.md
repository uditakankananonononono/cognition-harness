# Matched labeled-query study, draft v1

Not frozen or scored. Known active-query heuristic versus fixed-order query choice,
with identical trusted development-label opportunity. No novelty/AGI claim. The
previous retention null and frozen artifacts remain unchanged.

## Prior exposure and question

The prototype was motivated by the preceding null and a favorable engineered abs
fixture; verifier feedback exposed a fixed-only counterexample. Builder subsequently
found the known negation fixture dev (0,0), pool (1,-3): adaptive chooses -3,
negation/abs remain, fixed queries 1 and resolves negation. Both consume equal
charges. This negative is retained as a control, not a final task. The design is
therefore AFTER exploratory evidence, not an untouched preregistration.

Question: for known finite integer targets, how often do adaptive and fixed query
selection resolve a singleton under equal development-label caps? Greedy pair-count
can win or lose; no adaptive >= fixed hypothesis is guaranteed. No speed savings
in a design deliberately forcing full pool scans for both methods.

## Proposed independent construction

Eight known targets in exact GRAMMAR index order:
0 x+1; 1 x-1; 2 -x; 3 abs(x); 4 max(0,x); 5 min(0,x); 6 x; 7 0.
512 instances: 64 per target, 16 each at dev-count 1,2,3,4.
For each instance and each query cap 0,1,2, run both policies fresh: 3072 runs.
Same instance/dev pairs/pool permutation for both policies and all caps.
Templated target blocks, not 512 independent real-world trials. Descriptive only.

Source public pool proposed fixed set [-8,-3,-1,0,1,2,5,8]; evaluator independently
permutes it once per instance. Pool order matters to fixed and adaptive ties, so
this removes a single favorable manually fixed ordering. Publish the set file and
hash BEFORE source freeze. Per-instance permutations derived by evaluator from
private seeded PRNG; each run receipt already records full pool hash and config.
Pool set is known; order by instance is development-visible, not final-case data.

Independent evaluator uses Python random.Random with privately hash-committed
integer seed (UTF-8 decimal string), one PRNG instance, target/dev-count/ordinal
order. Proposed generation steps per instance: dev = sample(range(-32,33), d),
pool = sample(public_pool, len(public_pool)), final = sample(ascending remainder
of range(-32,33) excluding dev inputs AND every public-pool input, 8).
Excluding pool inputs from final inputs prevents query-input reuse as final scoring
cases; this finite integer domain is still not independent transfer.
Evaluator pins generator/Python version/seed/pack before method execution.
No filtered/replaced samples based on method choices or correctness.

## Oracle boundary and caps

Development callback knows the selected instance's target semantics only; it
returns reference outputs for inputs in that instance's declared public pool and
refuses anything else. This is a deliberate extra labeled-development channel.
It never exposes final inputs/labels to the method, and must not read final pack
inside callback. Evaluator independently writes its reference interpreter from
above semantics, never imports ambiguity.evaluate as the answer oracle.
No remote/network or paid callback. Callback is trusted, unsandboxed mechanics;
this study must not be described as secure hosted oracle access.

Execution cap=1024; query cap independently 0,1,2. Both methods full-scan all
unused pool inputs each round; exact scalar/scan/oracle charges and unused caps
retained. Singleton stops without padding queries. Adaptive selects maximum
separated unordered candidate pairs, lowest pool index tie; fixed selects first
unused input even when scan shows it uninformative. No ranking fallback.
Only singleton selected; unresolved, no-candidate, invalid label, callback failure
and cap exits are no-finalist outcomes and remain in all denominators. No claim
that equal caps mean equal actual charges or memory/CPU bounds.

## Two-stage evaluator receipts

Stage A locks all selected-index/status/query-count/charge receipts BEFORE final
expected-answer scoring. Report both-resolved, adaptive-only, fixed-only, neither,
selected-target identity by index, cap outcomes and pairwise finalist difference
by query cap/target/dev-count; retain every non-selected status. Ground the oracle
label transcript integrity in private evaluator receipts, not mutable builder dicts.

Stage B scores exactly emitted singletons against evaluator private final reference
outputs. Null finalist fails all 8 cases and task/identity metrics. Report exact
case numerator/denominator, all-8 task passes, target-index recovery separately,
paired wins/ties/losses and costs for all tasks; do not choose favorable subsets.
Cap0,1,2 each have 512 tasks/4096 cases/policy. No significance/generalization.

Custody: a separate evaluator, not builder/gate, constructs final pack only after
accepted source/config/public-pool freeze. Keep seed, pack and private per-case
receipts evaluator-only; builder/gate receive aggregates and hashes. Save per-method
selection and per-case receipts DURING actual runs, not recompute at request time;
return their SHA256s plus pack/seed/generator/aggregate hashes. No private pack in git.

## Before freeze

Gate must review amended source/control and this protocol; evaluator must accept
construction, independent oracle and custody. Public pool bytes/hash and source/
contract manifest still need creation AFTER review choices settle. Final tip status
flip only after acceptance. No final study run is authorized by this draft alone.

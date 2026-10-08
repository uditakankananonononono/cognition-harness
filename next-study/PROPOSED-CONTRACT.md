# Proposed data-repair pilot contract, not a frozen result

Scope: pure local JSON-record transformations. No user/private data, network, accounts, model, spending or code activation. No AGI or scientific novelty claim. Proposed new evaluation is independent-custody if evaluator can keep final task instances and answers outside builder workspace.

## Interface

Candidate implements solve(spec, records) -> JSON result. Evaluator passes spec and records to candidate worker at scoring time, not to the builder beforehand. No answer bytes passed. Tasks are specified transformations, not guessing undocumented intent. Template transfer means new spec compositions/edge mechanisms within a declared finite contract; it does not mean inventing an unknown operator.

Records are lists of string-keyed dicts; values JSON null/bool/string/int/finite-float/list/dict. Preserve exact scalar JSON types. No missing field equals null by default. Inputs bounded at 100 records, depth<=5, strings<=1000 characters. Known operators: select fields, rename fields, row filtering (exact typed equality or declared numeric comparison), stable sort, typed stable dedup, and group-count. Policies must explicitly resolve missing fields, rename collision, bool-vs-number, sort ties and duplicate identity. Error output is a declared code, not traceback. Transformation order is explicit, immutable and part of task spec. Unsupported operator must return unsupported, not silently skip.

## Candidate arms and budget

A0 identity baseline: returns records unchanged, no synthesis.
A1 finite search baseline: proposes bounded pipeline configurations from known operations and development examples, deterministic ordering, 200 candidate trials maximum across development adaptation; every proposal compiled to task code and evaluated, failed trials retained. Freeze exact grammar/order before task release. No model.
A2 spec-directed source synthesis: generates Python code for the explicitly declared contract from spec. No direct reference-answer copying, arbitrary eval/exec, network or host file access. It can compose declared operators, not invent new semantics. Generated source and schema validation are separate from execution. Freeze generator bytes before release.

Proposed compute: each arm maximum 200 candidate trials and 60 worker minutes across registered development process and final scoring combined, 60 seconds maximum per worker run; stop at first limit. Standard library only, bubblewrap required; CPU/memory/output caps to be measured and frozen during feasibility preparation. No model arm unless separately scoped/verified. No extra stochastic seeds because all arms are deterministic. Account screening/compile/validation/judge work separately, not falsely equal-cost.

## Evaluator custody request

Independent evaluator authors twelve task instances over at least four policy/schema templates. Four development instances released with inputs/answers/specs; eight final instances retained, including at least two template mechanisms absent from released dev instances but within explicit contract. Final answers derived by separate implementation plus conservation/type invariants. Builder may inspect full dev pack only AFTER method/interface protocol is frozen. Evaluator retains final specs/data/answers until methods/candidates are committed. Candidate sees final spec/input only inside isolated execution. Review lane must not relay final cases or answers to builder.

Before release, evaluator checks exact task/input duplicates and structural template identity, seals hashes of all tasks/references/judge and issues public-safe receipt listing counts, template split, version/hash and license/authorship provenance, not final examples. Seal is in evaluator custody, not a claim from builder git time. No references into builder's method repository that leak final data. Exposure retires final set for future fresh claims.

## Measurement and allowed claims

Primary macro-average task exact-typed accuracy, report case counts per task/template; preservation gate against baseline-passed deterministic cases, forbidden effects reject separately. Claims stay descriptive with eight final instances and dependent cases; no reliable broad significance claim. Task-level paired differences and costs retained. A failed template or unsupported policy ships as a loss. Baseline may pass identity-like cases; do not tune tasks to erase that.

Fresh claim, if custody actually holds: named frozen methods evaluated once on evaluator-held task instances and new compositions/policies within this contract. Not model general intelligence, unknown operator invention, scientific novelty, real-world user-data success or cost-normalized superiority. If builder learns final data early, mark reused/author-visible and retire fresh claim.

## Feasibility before freeze

Evaluator and builder agree precise schema/error codes, maximum resource caps, source ownership and final submission procedure. Builder implements methods without task-specific final examples. Independent reviewer validates judge with false-pass/type/tamper/timeout controls. Record method bytes, generator settings, grammar, all resources and budget in a NEW immutable protocol; main receives pin/hash before any task scoring. This proposal alone starts no scoring.

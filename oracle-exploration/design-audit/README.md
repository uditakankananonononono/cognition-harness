# Public design-time ceiling audit

Builder calculation, pending independent review. Not a frozen study, unseen task result, or performance claim.
All 8 known targets; all 1-input and 2-input dev subsets from integers -8..8.
Public pool is every nonzero integer -8..8, excluding observed dev inputs per instance.
Adaptive uses the ascending-order pool tie rule here; random-order expectation is exact over possible first inputs, not simulated trials.

| Dev count | Total public constructions | Ambiguous | Any one-query ceiling | Adaptive resolved | Expected random-first resolved |
|---|---:|---:|---:|---:|---:|
| 1 | 136 | 96 | 91 | 90 | 1483/30 (49.4333) |
| 2 | 1088 | 396 | 396 | 396 | 3344/15 (222.9333) |

The counts apply ONLY to ambiguous constructions; singletons are not counted as one-query resolutions.
One-input constructions are 91/96 ceiling-feasible; two-input ambiguous constructions are 396/396.
Changing dev inputs fixes cap1 feasibility but does NOT make this toy domain an unresolved scientific question.
Every public construction can be calculated exactly, and the operators remain sign-linear. A seeded private study would mainly sample these known structural outcomes.

Recommendation: do not run another private synthetic study just to re-estimate a public finite calculation.
Keep this audit as a design diagnosis; no v3 frozen protocol is proposed now. A meaningful new lane would require a new domain or a different research question, with broader execution and grounding work, not relabeling this table as AGI progress.

Limitations: builder interpreter reused for this audit, not independent oracle; exhaustive only on declared domain/dev counts; fixed ascending adaptive tie order, not all pool permutations; no final scoring/custody claims; no runtime/label-quality/generalization result.

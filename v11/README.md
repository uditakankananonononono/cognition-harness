# v11: behavioral-dedup retention (IN PROGRESS - arms not yet scored)

October 10, 2026. Code committed and mechanics-checked (150-exec smoke: 52
distinct behaviors retained; stat bug found and fixed during the check). The
full frozen study runs next: arms dedup-binary and dedup-graded on BOTH the v9
suite (pin e7f12875...) and the v10 plateau suite (pin 9c7f30b8...), same
budgets (width 8, depth 6, cap 4000), same judge/gate. Incumbent: v9 binary
beam. Keep-rule: an arm must verifiably beat the incumbent on both suites.

Hypothesis (from v9/v10 receipts): the binding constraint is plateau retention,
not ranking - width-8 slots are wasted on behaviorally identical children
(commuting arg swaps, dead renames). proposer3.beam groups scored children by
their exact dev behavior vector and retains one representative per behavior, so
every slot is a distinct behavior. v10's distance tie-break is kept as the
graded arm.

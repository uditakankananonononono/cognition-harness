# CLOSED: small resettable Mealy domain

October 10, 2026. Public design diagnosis only, not learner performance or novelty.
No learner, audit-code prototype, private target pack or seeded study was built.

The proposed class was deterministic complete Mealy machines with <=2 states,
actions {a,b}, outputs {0,1}, start state0 and trusted reset. Builder contributed
analytic table counts, history-sensitive aa/ab examples, unreachable-state identity
aliasing, and a conservative product-state bound. Counts:4 labeled one-state tables
and256 labeled two-state tables; raw tables are not distinct behaviors.

The independent verifier's exhaustive calculation, relayed by main, corrected and
tightened the public design result:
- 148 reachable behavioral equivalence classes.
- Tight distinguishing-sequence horizon3, rather than builder's conservative<=4.
- Exhaustive nonempty action words through horizon3:14 resets,34 actions and34
  observations, sufficient for exact behavioral identification in this class.
- Builder's horizon4 ceiling30 resets/98 actions was unnecessarily loose.

Builder has not rerun or inspected the verifier's exhaustive implementation here;
the class count and tight horizon are explicitly verifier-reported findings, not
builder reproduction. The reset/action word arithmetic was calculated locally.
The earlier A/D examples both describe the identical one-state all-zero machine;
they are not a distinct identification pair. A/B and C/D illustrate sequence history,
and unreachable-state E/A illustrate implementation ambiguity, not method gains.

Status: stateful-Mealy lane CLOSED. This class is small enough for exact public
enumeration. A learner or seeded benchmark would re-estimate a published finite
calculation, not answer an unresolved identification question. No further code or
performance comparison on this domain. No hidden implementation identity, general
learning, independent transfer, novelty or AGI result follows.

This closes the narrowly defined <=2-state resettable domain only, not all stateful
identification research. A future proposal must state a question exact enumeration
cannot answer at survey scale before design/build work, with materially different
assumptions/domain and explicit observability/oracle/cost boundaries.

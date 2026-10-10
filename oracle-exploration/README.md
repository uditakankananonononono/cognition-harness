# Development-oracle ambiguity refinement, mechanics prototype

October 10, 2026. Builder-tested, pending independent review. Separate exploration
increment; the October 9 frozen study and its null result are unchanged.

## Concrete change

The prior study's unlabeled disagreement retention never separated from fixed
retention because shared ranking settled ambiguity. This prototype asks an explicitly
provided development-label oracle at a candidate-disagreement input and eliminates
inconsistent grammar entries. It returns a finalist ONLY for a singleton version
space. Remaining ambiguity is explicit; no complexity fallback hides it.

This is a known version-space/active-learning idea, not a novelty claim:
query-by-committee prior https://mlanthology.org/colt/1992/seung1992colt-query/
and refinement prior https://arxiv.org/html/1710.07740 were identified during the
preceding lane. These are provenance leads, not a new literature review here.
No learned model, arbitrary invention, AGI, new operations or generalization claim.

## Mechanism and charge semantics

Eight known grammar entries, copied into this separate trusted finite interpreter:
x+1,x-1,-x,abs(x),max(0,x),min(0,x),x,0. Integer input domain -32..32.
Development pairs: 1..16, distinct integer inputs; integer outputs -64..64.
Public pool: 0..65 distinct valid integers, caller-provided order.

Build the exact-consistent version space using all grammar/dev executions.
For each unlabeled pool input not already observed, evaluate all surviving entries.
Choose input maximizing separated unordered candidate pairs; lowest pool index
breaks ties. Ask the explicitly supplied development oracle once. A valid integer
label filters the version space. Repeat until singleton, exhaustion, failure or
pool cannot separate. Query cap defaults 1 (0..8 allowed). Execution cap defaults
1024 (0..100000 allowed). Configuration hash includes actual dev/pool hashes,
grammar, caps and selection/finalist rules; it is NOT a source freeze/authentication.

Charges include generation attempts, actual dev/probe scalar calls, considered
pool inputs and oracle attempts. Oracle attempts are charged before callback;
failed/invalid callbacks are not retried. Cap failure returns no finalist; partial
remaining indices may be incomplete when generation cap exits and must not be
interpreted as the complete consistent space. Per-query before/after indices,
label, input, status and round probe scores are recorded. Receipt fields can be
changed or forged by a caller; no durable/authenticated custody is implied.

## What this costs and assumes

An oracle is EXTRA information. Any comparison must match label-query opportunity
and total logical budgets; improvement over no-label retention cannot be presented
as a free method advantage. A fair later design compares adaptive disagreement
input selection versus fixed-order input selection under the same query caps and
trusted label access, including failed labels/ambiguous/no-candidate/cap outcomes.
No experiment, freeze or independent final scoring is done in this increment.

The oracle must be a separately authorized development reference, never a private
final-pack oracle. The callable can do arbitrary actions and is NOT sandboxed,
timed out, isolated or resource-limited by this module. Do not attach network,
paid, user-facing or final-data services under this prototype. Tests use only local
known deterministic fixture callbacks. Exception text is not copied to receipts.
Wrong-but-valid labels can select the wrong expression: a test records that limit.
Trusted exact-consistent grammar assumption can fail, yielding no candidate.
No heap, receipt-byte, wall-clock or CPU bound is implemented; logical execution
counts are not a security/resource guarantee. No source retention ledger integration.

## Evidence

18 new mechanics controls pass, new receipt in receipts/mechanics-run.txt. Includes
abs/identity ambiguity with a labeled negative probe; zero/two queries; no-ranking
fallback; no-separation pools; execution caps; failed/invalid labels charged once;
inconsistent labels; intentionally wrong oracle; ties; input type refusal and
unchanged inputs. These are developer-known unit fixtures, not unseen performance.

Run: python3 -m unittest discover -s oracle-exploration -p 'test_*.py' -v
No prior frozen tests/receipts are overwritten by this command.

Next obligation: independent mechanics review. A later empirical study needs its
own pinned public pool/config/source, fair query-budget protocol and evaluator
custody; builder must never inspect its final pack. No branch push before review.

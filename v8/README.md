# M8 semantic-pruned synthesis on reused data

Freeze6d6b5c1fa0492a46b2711f01a8a6b9060466d240, pin63a9b95d22eb6809373f3f084c754bbb87673653229851b7a5246b456dc1391d, protocol hashae9782f7cc707077238b95d50c70901ac54329fd5a6397d00bb7d9d84f111613. Protocol locked before scoring. M7 dev/eval bytes reused exactly and explicitly known from negative M7 result. This is a known-benchmark search-mechanism follow-on, NOT a new unseen or blind discovery.

Same finite expression grammar/cost<=5. Before scoring proposed expressions for targets, semantic pruning keeps first representative per dev-output vector without using expected labels. Other expressions with same dev vector discarded; later cost compositions use retained representatives. Fixed interpreter handles only x/int literals, abs,+,-,*. Every retained vector crosschecked via inputs-only isolated real candidate worker. Final selection actual worker dev score, lower cost, lexical tie; eval only after selection. Source/trial/vectors/representatives retained.

Actual each task960 constructions,4800 scalar screening executions,149 worker candidates. Totals2880 constructions,14400 scalar screens,447 worker candidates. Neither10000 construction nor512 semantic cap hit; cost<=5 pool completed. Extra screening compute explicitly differs from M7; no equal-cost/runtime-superiority claim. Cost model counts-1 as a grammar terminal, not unary Python AST node.

Selected abs(x),(-1+(x*x)),(2+(x*3)); each dev5/5. Builder pending-review eval168/168 all tasks56; named baseline2/168 (quadratic2), aggregate+preservation true; identity false. This does not rewrite M7: its frozen56/168 rejected result unchanged. M8 improves on this REUSED known suite under different pruning/budget semantics, not general invention/generalization or empirical broad superiority. Dev-vector equivalence need not hold elsewhere; first representative selection can discard a better generalizing expression.

Twelve controls pass: pins, caps/counts, unique vectors/first representatives, worker vector crosschecks, reconstructed source hashes, dev-only selection, gates, exact M7 data-byte identity, interpreter behavior/refusal, typed invalid reporting. Independent review still required; no activation.

Limits: bounded handcrafted finite arithmetic grammar and interpreter; synthetic integer valid domains; no LLM/arbitrary invention/AGI/generalization/speedup; author knows reused target/answers, judge author-visible; candidate worker inputs-only; git timestamps do not prove no private scoring; no cgroup/kernel/covert-channel guarantees; no activation authority. No arbitrary hostile expression execution outside known grammar. Scores on reused data do not constitute new held-out model evaluation.

Reproduce: python3 v8/agent.py "$(cat v8/receipts/frozen-pin.txt)"; python3 v8/tests.py. Stdlib+namespace-capable bwrap. Full history contains unchanged v7 references used in tests. Fresh checkout. All screening/worker trials retained; no protocol edits after execution.

## Independent review and frozen wording clarification

Main relayed PASS-WITH-NOTES for M8e40d29ae: real bubblewrap rerun reproduced selected expressions and receipts byte-for-byte, all2880 screening constructions/447 worker reports/504 eval rows independently rescored,12 controls passed. Cleared as known-benchmark follow-on, NOT unseen discovery.

Append-only clarification: frozen protocol's 'baseline0' names the baseline implementation's constant0 outputs, not its pass count. Measured baseline score is2/168, not0/168. Original frozen bytes/pin remain unchanged; this note removes the wording ambiguity without rewriting preregistration.

Carry on every claim: reused author-known M7 benchmark; first-dev-vector representative may hide off-domain differences;14400 extra scalar screens means NOT cost-normalized superiority or speedup; finite handwritten grammar, no general-invention/AGI claim; freeze records ordering, not absence of private tuning; no activation.

Interpreter's parser accepts unary-minus beyond terminal-1 and ignores abs AST kwargs, but proposer only creates the specified grammar. No arbitrary-parser-security claim is cleared.

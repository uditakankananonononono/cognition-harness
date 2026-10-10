# Ambiguous-start matched-label study, v2 proposal

Not frozen. Supersedes the draft v1 construction. Known-expression developer
controls establish POSSIBILITY of adaptive-only and random-order-only resolution,
not measured rates or dominance. All methodology choices follow exposed exploratory
feedback. No novelty/generalization/significance claim.

## Construction and population

Six targets, original grammar indices 2..7, semantics -x,abs(x),max(0,x),min(0,x),
x,0. Initial dev is exactly [(0,0)] for every instance. This deterministic ambiguity
rule leaves all six candidates consistent. Add+1/add-1 are excluded because their
output at zero uniquely identifies them; no aggregate can be called eight-target
accuracy. All instances are informative at start, but only SIX target blocks.
There are no random dev draws and dev input 0 is DISJOINT from every pool below.
This intentionally ambiguous stress population is not a neutral sampled workload.

Three pre-listed pool sets, all exclude 0:
P0 [-8,-4,-2,-1,1,2,4,8]
P1 [-7,-5,-3,-1,1,3,5,7]
P2 [-6,-4,-2,2,4,6]
Sets are sign-balanced alternative magnitude grids, not claimed neutral. P1 includes
known counterexample values -3/1; P0 and P2 omit -3. All known operators are
sign-linear; alternative magnitudes may yield duplicate information, so pools are
sensitivity checks, not independent replications. Do not combine them as independent
sample evidence. Lock every set byte/hash before execution; no outcome replacements.

64 independently drawn pool permutations per target/set, with replacement:
6 targets x 3 pools x 64 = 1152 instances. Same pool permutation per paired method
and caps 0,1,2. Both policies start fresh each run, 6912 runs. Fixed policy is named
RANDOM-ORDER BASELINE, because evaluator randomly permutes the declared pool.
All methods receive equal trusted-label caps and full unused-pool scan opportunity.
Actual charges and early exits may differ. Cap0 is a structural unresolved tie and
is reported as a diagnostic, never evidence of comparative performance.

## Primary metric and descriptive decision rule

Primary: paired singleton-resolution rate difference adaptive minus random-order
baseline at cap1, with exact resolved counts on all 1152 instances, also per pool
(384 instances) and per target (192 instances). Report adaptive-only, baseline-only,
both, neither; all no-finalist/status failures stay in denominators.
Support is restricted to THIS intentional ambiguity design: positive pooled paired
difference AND strictly positive difference in each of the three pools. Negative:
strictly negative pooled difference. Otherwise descriptive null/mixed. No p-value,
statistical significance, transfer or superiority claim. A positive pooled number
with a nonpositive pool is mixed, not support. Counterexample controls only prove
possible failure. Report caps0/2 as secondary, no post-hoc primary substitution.

Final target-index recovery is separate from resolved share. With truthful consistent
oracle it should coincide. Stage B is only consistency check, not independent new
accuracy information or a separate gain: score emitted singleton on eight private
inputs disjoint from dev and entire pool, nulls fail. All targets/negative outcomes
retained. Final reference interpreter independently implemented by evaluator, not
ambiguity.evaluate. No new operation is discovered.

## Offline ceiling

Before scoring, evaluator computes per-instance target-specific optimistic ceiling:
exists a subset of at most cap pool inputs whose truthful TARGET outputs distinguish
that target from every other initially consistent grammar entry? Enumerate all
subsets at caps0/1/2 with evaluator's independent interpreter. This knows the target
and is an OFFLINE ORACLE UPPER BOUND, not an executable target-blind strategy or
minimax tree guarantee. Report ceiling-resolvable denominator, both methods' shortfall
from ceiling, and unresolved despite ceiling per cap/target/pool. Do not charge its
computation to methods; report separately as evaluator diagnostic overhead.

## Exact generation sequence and commitments

Evaluator executes both methods, generation and scoring; builder never executes
methods on private study instances. Python version pinned to 3.10.12 unless evaluator
objects BEFORE freeze. Seed is an integer s, instantiated EXACTLY rng=random.Random(s),
not Random(str(s)). Seed hash = SHA256(str(s).encode('utf-8')). One PRNG instance.
Loop target index ascending2..7, pool index0..2, ordinal0..63. Per instance:
1. pool_order=rng.sample(pool_set,len(pool_set))
2. remainder=[x for x in range(-32,33) if x != 0 and x not in pool_set]
3. final_inputs=rng.sample(remainder,8)
No other rng calls; method order adaptive then fixed, caps0 then1 then2, no rng used
by method. No filtered/replaced samples. Independent oracle callback answers only
public pool inputs and never reads private final inputs/answers.

Before methods run, evaluator provides public commitment receipt containing seed
hash, generator/source/contract/public-set/pack hashes, Python version, and SHA256
of canonical JSON test vector for FIRST THREE instances (pool orders+final-input
vectors). Vector bytes remain private because they include final inputs; evaluator
independently verifies them, only hash goes public. A separate PUBLIC synthetic-seed
fixture (s=0, first three pool orders only) must be published with bytes/hash to
check call sequence without exposing private seed/finals. Test-vector artifacts
still need evaluator generation/acceptance BEFORE freezing.

Parent publishes commitment receipt to public exploration ledger and returns commit
and observed GitHub URL. An independent verifier reads that public commit via live
source, verifies hashes, records its observed UTC time and sends an explicit
START-ALLOWED acknowledgment to evaluator. Evaluator MUST wait for that acknowledgment
before executing any methods. Timestamp claims from git author/committer metadata
are not a time anchor. Public source observation plus pre-run verifier handshake
anchors ordering, not cryptographic trusted timestamp/immutable-ledger proof. Save
start/end UTC process timestamps as supporting records only. If public publication
or independent readback unavailable, BLOCK; do not run privately then backfill.

## Custody and receipts

Separate evaluator owns private seed/pack/reference outputs; builder/gate get only
aggregates/hashes. Save each per-method/cap selection and per-case receipt DURING
run, not recompute afterward. Hash contemporaneous bytes; public-safe aggregates
contain denominators/status counts/charges/ceiling metrics, private receipts do not
enter git. Callback trusted/unsandboxed; method receipt dict is not authentication.
Execution cap1024, query caps0/1/2; no resource/security/memory guarantees.

Pending before freeze: gate review of v2, separate evaluator scope/oracle/custody
acceptance, pinned set bytes and manifests, public synthetic fixture and private
vector hash verification, final source freeze. Then separate commitment handshake,
then actual execution. This proposal alone is not an execution permission or freeze.

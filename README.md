# Cognition harness: local milestone 1

This is a bounded, deterministic source-repair agent, not AGI, not a language model, and not a general self-improver. No network/API/model is used by the repair loop. Nothing is integrated, pushed, or activated in a product.

## Seed provenance

Read Sugarcode's self_improve engine, sandbox, gate, templates, testsynth and safety code at cloned HEAD ea9ca4077c4cd067a9b36dc4876d26ec3a17f708 from https://github.com/uditakankananonononono/sugarcode-ai.git . The existing pipeline detects gaps, generates template features and its own tests, then requires approval. It does not rewrite existing module source or judge gains on independent frozen outputs. This prototype reuses those design principles, not its source code or weak generated-test oracle. Independently ran 15 selected seed tests in a virtualenv: 15 pass. Initial host --user installation caused 7 failures/8 passes because the seed's scrubbed HOME hid pytest; the unmodified venv rerun resolves this environment issue. No all-repository claim.

## Frozen protocol

Freeze commit 1b30a86bd15005207e7eee32ec264c09dd794687 precedes all scoring. Manifest SHA256 b3503affda9150a12328f8e4d235d6dff5f37afdf6c05b07567c24ee5589b0bb. See frozen/protocol.json, eval.json, dev.json, MANIFEST.json. Forty-eight equal-weight exact-output cases, 16 each: Unicode whitespace token normalization, stable unique values, integer closed-interval union. Development set has one separate example per task. No cases are statistically sampled. Valid input domains only. Expected outputs are literal hand-authored values, not computed with candidate code.

Before/after scoring the judge verifies the manifest against the supplied pin. Inputs, but no expected answers, enter the candidate namespace. Byte hashes refer to the actual bytes copied into that namespace. All case failures and outputs are retained.

## Architecture

agent.py reads only the dev set, proposes changes from three predefined textual repair operators, executes and selects by exact dev score, and writes a new version of its task implementation. Search budget: three rounds. It cannot invent new operators. Frozen eval is scored once after proposal selection by judge.py in a separate process. isolation.py executes in bubblewrap namespaces with no host workspace, no expected-answer files, no networking, read-only runtime/code, scrubbed environment, CPU/memory/file limits, and wall timeout. worker.py returns values; judge compares against fixed answers on the host. The gate requires strict total gain and no task score decrease. Even a passing measurement remains pending independent review; no activation mechanism is present.

This separate scoring process is architectural independence from the proposer, NOT independent outside-agent review. Both programs and answers were authored by one builder and all are inspectable by that builder. No tamper-resistant lock against the parent user/host is claimed. Runtime library mounts, /proc, /dev and same-kernel isolation mean this is not a hardened hostile-code service. Bubblewrap missing/failing refuses execution. No cgroup, host-kernel security, crash-proof durable ledger, registry-race or covert-channel guarantees.

## First measured result

Baseline: 24/48. Repaired candidate: 48/48 (+24 cases, +50 percentage points) in this synthetic suite. Three dev steps improve 0/3 -> 1/3 -> 2/3 -> 3/3. Candidate fixes whitespace splitting, first-occurrence deduplication and touching-interval merging. These are deliberately buggy baselines and known fixes, not novel discoveries or empirical AGI evidence. Wall times are not optimization results and no speedup is claimed.

Negative control: canonical 16/16, unique 1/16, merge 16/16 = 33/48. Total improves versus 24/48, but unique regresses versus baseline, so gate rejects. Initial control used sorted uniqueness and scored 42/48 with NO regression below baseline, so it correctly passed the gate. That initial receipt is retained separately. The control was strengthened after this exploratory observation; the protocol, evaluation cases, baseline and selected candidate were unchanged. No post-hoc protocol modification is hidden.

See receipts/measurement.json for case-level actual/expected outputs, source hashes and gate outcomes, and receipts/dev-history.json for every dev trial. Twelve unittest controls pass: hash/suite tamper, baseline integrity, equal/invalid/regressive promotion, syntax/CPU/memory failures, host-canary invisibility and network refusal. These probes establish tested local behaviors, not broad hostile-code safety.

## Reproduce

Linux, Python 3.10+, bubblewrap with user namespaces required. Standard library only for this harness.

    python3 agent.py "$(cat receipts/frozen-pin.txt)"
    python3 tests.py

Do not re-run freeze.py to bless modified inputs. It is retained as the original fixture construction recipe only. A re-run overwrites generated candidate/receipt paths, so use a fresh checkout for independent verification. No activation follows either command. All artifacts are local review-only.

## Next meaningful step

External reviewer checks freeze ancestry, literal expected outputs and unchanged candidate bytes, reruns all scores/controls, and tries invalid-output/sandbox escape probes. Only then can this milestone be called independently reviewed. A later frozen experiment should add unseen valid inputs and more than a predefined repair menu; model or expanded-operator behavior must be a separate named experiment, with retained unsuccessful trials and no moving benchmark.

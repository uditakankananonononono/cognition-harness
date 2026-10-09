# RECONSTRUCTED local review CLI

Original unpublished commit2ac3b826 and bundle4c6668ec were lost during workspace resets. These files are a NEW reconstruction on the grounded published base88f1deea, not byte-identical recovery, not the old receipt, and not already independently reviewed. No old tests rerun to fabricate their receipt; receipts/tests.txt is a NEW run on this reconstructed source.

    python3 -m harness_cli verify --root METHODS --manifest MANIFEST --pin SHA256
    python3 -m harness_cli submit --root METHODS --manifest MANIFEST --pin SHA256 --selection SELECTION --out NEW_RECEIPT

Standard library, no candidate execution/model/API/email/spending/network/activation. Manifest requires root-relative regular files, lowercase SHA256 and separate pin; refuses symlinks/parent traversal/duplicates/tamper,4MiB/file. Selection exact keys method_manifest_sha256,arm,variant,purpose; A0/A1/A2, integer0..31 (not bool), onlyA1 nonzero, independent_review only. Receipt created once0600, source rechecked before write, pending_independent_review/not_authorized. Reconstruction explicitly marked in emitted receipt too. No new benchmark/capability improvement claim.

Limitations retained: intermediate-directory race/TOCTOU possible (not atomic directory-descriptor traversal); no parent-directory fsync/crash durability promise, no authentication/owner grant, no kernel/cgroup/covert-channel guarantee or never-raises outside handled shapes. Separate pin source must be trusted. Older manifests with../entries are not silently accepted. Any activation review remains separate. Fresh independent review required on this new tip/hash.

# V3c boundary closure, NOT frozen

Supersedes conflicting V2/V3 byte/depth rules only. No pack authored or pilot scores.

Unicode scalar policy: recursively reject any parsed string/object key containing a surrogate code pointU+D800..DFFF as invalid_wire. Python JSON combines valid escaped high-low pairs into a Unicode scalar, allowed. Unpaired or reversed pairs invalid_wire. In-memory record validation refuses surrogate strings/keys as invalid_records. Spec surrogate value/name invalid_spec via valid-spec bounds. No normalization applied.

Canonical byte accounting: compact JSON ensure_ascii=False,separators(',',':'),allow_nan=False, then UTF-8 bytes. Wire1MiB counts actual raw incoming bytes, not reserialization; spec64KiB counts canonical serialization. Spec depth root container0, children+1; semantics container-height minus1 implements boundary; max6. Record object root0 child+1 max5 input/every intermediate/final. Result envelope does not add record depth.

Output: lower per-case complete serialized result envelope cap128KiB(131072), all arms/generator apply before return, overflow error envelope code output_limit. Worker aggregate stdout/stderr file caps2MiB(2097152) rather than prior1MiB; max10 cases*128KiB=1.25MiB plus fixed metrics wrapper headroom, fits2MiB. Each worker item has exact output and wall_seconds fields; headroom>=0.75MiB. No final task may exceed public-valid bounds without reference output_limit. Batch input remains<=12MiB including encoding overhead. RLIMIT_FSIZE2MiB exact probe required before final freeze; old1MiB results retained, not claimed new2MiB test.

A1 variant0 and A2 share semantics.py operator bodies. They are NOT independent algorithms: known-policy selection versus source composition using same implementation. Judge/reference independent implementation still required; never compare these arms as unrelated discoveries.

Custody label: evaluator-retained, procedural author-hidden custody; access-control separation not independently verified. No fresh independent-transfer/novelty claim. No final cases/answers accessible to builder. No pilot scoring before freeze and sealed receipt.

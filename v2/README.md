# M2 exploratory result: not fully unseen

Freeze 31ca38186d6d64b82dc7d7e1c9901249fa34ac8e, pin 0dd606a1db83bb01ee2d63de8cfdcf684486342cd5bc3bfbd55b2101f99ecd6d. AST-body search tests 12 canonical, 5 unique and 8 interval-union bodies on 24 development examples. Tie goes to first body. Eval 360 separate-seed inputs yields baseline 136/360 (0,21,115), selected 355/360 (120,120,115), control 240/360 (120,5,115), gates true/false. The five merge losses are retained, not fed to the proposer. Development ties failed to distinguish < and <=; this is a concrete limitation of sparse dev feedback.

15/17 controls pass. Two failed: perfect-score assertion (355, not the assumed 360) and exact input disjointness (8 overlaps, mostly empty inputs). Separate seeds do not establish unseen inputs. This exploratory result is not claimed independently reviewed or fully unseen; all artifacts remain unchanged. Any disjoint-input retry is a new freeze/experiment, not a rewrite of this run.

M1 limits carried verbatim: frozen 48 exact-output cases only, 3 known repair-menu items, synthetic hand-authored cases, host judge reads answers (not author-blind), git timestamps don't prove absence of private pre-freeze scoring, no runtime/cgroup/covert-channel guarantees, no activation authority.

M2 scope differs: 360 seeded synthetic cases, 25 known AST grammar bodies, no model/general code invention/AGI. No outside review or activation yet. All host-generated expected outputs share builder authorship. The independent interval oracle uses overlap-graph components rather than the greedy sweep; tests of that oracle still need outside checking.

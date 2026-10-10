import unittest
from ambiguity import resolve, evaluate

class RefinementTests(unittest.TestCase):
    def test_known_abs_identity_ambiguity_resolved_by_labeled_negative_probe(self):
        seen=[]
        def oracle(x): seen.append(x); return abs(x)
        r=resolve([[0,0],[1,1]],[-2,2],oracle)
        self.assertEqual(r['status'],'selected'); self.assertEqual(r['finalist']['index'],3)
        self.assertEqual(seen,[-2]); self.assertEqual(r['charged']['dev_scalar'],16)
        self.assertEqual(r['charged']['probe_scalar'],6); self.assertEqual(r['charged']['oracle_attempts'],1)
        self.assertEqual(r['queries'][0]['after_indices'],[3])
    def test_identify_identity_with_same_probe_and_different_label(self):
        r=resolve([[0,0],[1,1]],[-2,2],lambda x:x)
        self.assertEqual(r['finalist']['index'],6)
    def test_no_query_for_already_singleton(self):
        def oracle(x): self.fail('must not query')
        r=resolve([[2,3]],[-2,2],oracle)
        self.assertEqual(r['finalist']['index'],0);self.assertEqual(r['charged']['oracle_attempts'],0)
    def test_query_cap_zero_is_explicit_ambiguous_no_fallback(self):
        r=resolve([[0,0],[1,1]],[-2,2],lambda x:abs(x),query_cap=0)
        self.assertEqual(r['status'],'query_cap_ambiguous');self.assertIsNone(r['finalist'])
        self.assertEqual(r['charged']['probe_scalar'],0)
    def test_pool_cannot_separate_and_empty_pool(self):
        for pool in ([0,1,2],[]):
            r=resolve([[0,0],[1,1]],pool,lambda x:abs(x))
            self.assertEqual(r['status'],'pool_cannot_separate');self.assertIsNone(r['finalist'])
            self.assertEqual(r['charged']['oracle_attempts'],0)
    def test_execution_cap_charge_no_oracle_or_finalist(self):
        for cap in (0,3,16,20):
            seen=[];r=resolve([[0,0],[1,1]],[-2,2],lambda x:seen.append(x),execution_cap=cap)
            self.assertEqual(r['status'],'execution_cap_exhausted');self.assertIsNone(r['finalist'])
            self.assertEqual(r['charged']['dev_scalar']+r['charged']['probe_scalar'],cap);self.assertEqual(seen,[])
    def test_failed_callback_charged_not_retried_no_error_text(self):
        calls=[]
        def oracle(x): calls.append(x);raise ValueError('secret must not enter receipt')
        r=resolve([[0,0],[1,1]],[-2,2],oracle,query_cap=2)
        self.assertEqual(r['status'],'oracle_failed');self.assertEqual(len(calls),1)
        self.assertEqual(r['charged']['oracle_attempts'],1);self.assertNotIn('secret',str(r))
    def test_invalid_labels_exact_types(self):
        for answer in (True,1.0,'2',None,{},65,-65):
            r=resolve([[0,0],[1,1]],[-2,2],lambda x:answer)
            self.assertEqual(r['status'],'oracle_invalid');self.assertIsNone(r['finalist'])
            self.assertEqual(r['charged']['oracle_attempts'],1)
    def test_inconsistent_label_can_eliminate_everything(self):
        r=resolve([[0,0],[1,1]],[-2,2],lambda x:33)
        self.assertEqual(r['status'],'no_consistent_candidate');self.assertEqual(r['remaining_indices'],[])
    def test_wrong_oracle_can_select_wrong_candidate_not_self_verifying(self):
        r=resolve([[0,0],[1,1]],[-2,2],lambda x:x)
        self.assertEqual(r['finalist']['index'],6);self.assertEqual(r['correctness'],'not_final_scored')
        # If real target was abs, caller's wrong oracle supplied false assurance.
        self.assertNotEqual(evaluate(r['finalist']['index'],-2),abs(-2))
    def test_tie_uses_lowest_pool_index(self):
        r=resolve([[0,0],[1,1]],[-3,-2],lambda x:abs(x))
        self.assertEqual(r['queries'][0]['pool_index'],0);self.assertEqual(r['queries'][0]['input'],-3)
    def test_dev_inputs_never_queried(self):
        r=resolve([[0,0],[1,1]],[0,1,-2],lambda x:abs(x))
        self.assertEqual(r['charged']['pool_scan'],1);self.assertEqual(r['queries'][0]['input'],-2)
    def test_two_query_path(self):
        r=resolve([[0,0]],[-2,2],lambda x:0,query_cap=2)
        self.assertEqual(r['status'],'selected');self.assertEqual(r['finalist']['index'],7)
        self.assertEqual(r['charged']['oracle_attempts'],2)
        self.assertEqual(len({q['input'] for q in r['queries']}),2)
    def test_one_query_budget_may_remain_ambiguous(self):
        r=resolve([[0,0]],[-2,2],lambda x:0,query_cap=1)
        self.assertEqual(r['status'],'query_cap_ambiguous');self.assertIsNone(r['finalist'])
    def test_dev_inconsistency_no_query(self):
        r=resolve([[0,44]],[-2,2],lambda x:0)
        self.assertEqual(r['status'],'no_consistent_candidate');self.assertEqual(r['charged']['oracle_attempts'],0)
    def test_invalid_inputs(self):
        for dev in ([],[[True,0]],[[0,True]],[[33,0]],[[0,0],[0,0]]):
            with self.assertRaises(ValueError):resolve(dev,[-2,2],lambda x:0)
        for pool in ([True],[-33],[0,0],{},[0]*66):
            with self.assertRaises(ValueError):resolve([[0,0]],pool,lambda x:0)
        for kw in ({'query_cap':True},{'query_cap':9},{'execution_cap':True},{'execution_cap':-1}):
            with self.assertRaises(ValueError):resolve([[0,0]],[-2,2],lambda x:0,**kw)
    def test_determinism_and_inputs_unchanged(self):
        dev=[[0,0],[1,1]];pool=[-2,2]
        self.assertEqual(resolve(dev,pool,abs),resolve(dev,pool,abs))
        self.assertEqual(dev,[[0,0],[1,1]]);self.assertEqual(pool,[-2,2])
    def test_grammar_and_domain_validation(self):
        for index,x in ((True,0),(-1,0),(8,0),(0,True),(0,33)):
            with self.assertRaises(ValueError):evaluate(index,x)

if __name__=='__main__':unittest.main(verbosity=2)

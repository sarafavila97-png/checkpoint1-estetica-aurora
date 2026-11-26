"""Reporting must not inflate precision, hide missing costs or compare unmatched cases."""
import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'scripts/report_metrics.py'
class Metrics(unittest.TestCase):
 def setUp(self):
  self.assertTrue(P.exists(),'metrics implementation not yet present')
  spec=importlib.util.spec_from_file_location('metrics',P);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
 def rows(self):return [dict(case_id=str(i),correct=i<4,cost=.02,judge_score=5,error_category=None if i<4 else 'unsupported') for i in range(5)]
 def test_four_of_five_is_eighty_not_judge_score(self):
  r=self.m.summarize_runs(self.rows());self.assertEqual(r['precision_pct'],80);self.assertEqual(r['error_categories'],{'unsupported':1});self.assertEqual(r['projected_cost_1000'],20)
 def test_missing_cost_is_unknown_not_zero(self):
  rows=self.rows();rows[0]['cost']=None;r=self.m.summarize_runs(rows)
  self.assertIsNone(r['total_cost']);self.assertIsNone(r['projected_cost_1000']);self.assertAlmostEqual(r['known_cost_subtotal'],.08);self.assertEqual(r['cost_coverage'],4)
 def test_empty_has_no_precision(self):
  r=self.m.summarize_runs([]);self.assertIsNone(r['precision_pct']);self.assertIsNone(r['projected_cost_1000'])
 def test_invalid_values_rejected(self):
  for bad in [dict(correct='false'),dict(correct=True,cost=-1),dict(correct=True,cost=float('nan'))]:
   with self.subTest(bad=bad),self.assertRaises(ValueError):self.m.summarize_runs([bad])
 def test_ab_requires_five_matched_unique_cases(self):
  rows=[dict(r,architecture=a,run_id=a+r['case_id']) for a in ['A','B'] for r in self.rows()]
  r=self.m.compare_ab(rows);self.assertEqual(r['precision_delta_points'],0);self.assertEqual(r['A']['runs'],5)
  for broken in [rows[:-1],rows+[rows[0]],rows[:5]+[dict(r,case_id='other'+r['case_id']) for r in rows[5:]]]:
   with self.assertRaises(ValueError):self.m.compare_ab(broken)
 def test_missing_cost_prevents_cost_winner(self):
  rows=[dict(r,architecture=a,run_id=a+r['case_id']) for a in ['A','B'] for r in self.rows()];rows[-1]['cost']=None
  self.assertIsNone(self.m.compare_ab(rows)['projected_cost_delta_1000'])

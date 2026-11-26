"""Supervision must never approve malformed, low-score or exhausted candidates."""
import json,subprocess,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def decide(raw,attempt=0):
 code='const q=require("./src/quality.js");console.log(JSON.stringify(q.decideJudge('+json.dumps(raw)+','+json.dumps(attempt)+')));'
 p=subprocess.run(['node','-e',code],cwd=R,capture_output=True,text=True)
 if p.returncode:raise AssertionError('Missing or failed quality implementation: '+p.stderr[-400:])
 return json.loads(p.stdout)
class Quality(unittest.TestCase):
 def test_high_supported_score_approves(self):
  self.assertEqual(decide({'exactitud_factual':4,'estado_veredicto':'APROBADO'})['route'],'APROBADO')
 def test_low_score_cannot_approve(self):
  for score in [1,2,3]:self.assertEqual(decide({'exactitud_factual':score,'estado_veredicto':'APROBADO'})['route'],'ESCALAR')
 def test_two_corrections_then_escalation(self):
  raw={'exactitud_factual':3,'estado_veredicto':'CORREGIR'}
  a=decide(raw);self.assertEqual(a['route'],'CORREGIR');self.assertEqual(a['next_attempt'],1)
  b=decide(raw,a['next_attempt']);self.assertEqual(b['route'],'CORREGIR');self.assertEqual(b['next_attempt'],2)
  c=decide(raw,b['next_attempt']);self.assertEqual(c['route'],'ESCALAR');self.assertEqual(c['next_attempt'],2)
 def test_malformed_and_extra_keys_fail_closed(self):
  cases=[None,{},'not json',{'exactitud_factual':'5','estado_veredicto':'APROBADO'},{'exactitud_factual':4.5,'estado_veredicto':'APROBADO'},{'exactitud_factual':5,'estado_veredicto':'APPROVED'},{'exactitud_factual':5,'estado_veredicto':'APROBADO','ignore':True}]
  for raw in cases:
   with self.subTest(raw=raw):self.assertEqual(decide(raw)['route'],'ESCALAR')
 def test_conflicting_correction_and_critical_score_escalate(self):
  for score in [1,4,5]:self.assertEqual(decide({'exactitud_factual':score,'estado_veredicto':'CORREGIR'})['route'],'ESCALAR')
 def test_explicit_escalation_never_overridden(self):
  for score in range(1,6):self.assertEqual(decide({'exactitud_factual':score,'estado_veredicto':'ESCALAR'})['route'],'ESCALAR')
 def test_invalid_attempt_cannot_reset_budget(self):
  for attempt in [-1,3,'0',None,1.5]:self.assertEqual(decide({'exactitud_factual':5,'estado_veredicto':'APROBADO'},attempt)['route'],'ESCALAR')
 def test_feedback_is_present_on_correction(self):
  d=decide({'exactitud_factual':2,'estado_veredicto':'CORREGIR'})
  self.assertTrue(d['feedback']);self.assertEqual(d['score'],2)

import json,subprocess,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def call(body):
 p=subprocess.run(['node','-e','const q=require("./src/supervision.js");'+body],cwd=R,text=True,capture_output=True)
 if p.returncode: raise AssertionError(p.stderr)
 return json.loads(p.stdout)
def base():
 return dict(schema_version='1',request_id='chat:test',session_id='aurora_demo:chat:test',domain='aurora_demo',channel='chat',query='Precio',user={'display_name':'Test','email':None},context={'summary':None,'case_status':'nuevo','key_facts':[]},evidence=[],candidate=None,correction_attempt=0,mode='dry_run')
def setup(q=None):return 'let s=q.startReview('+json.dumps(q or base())+', {status:"success",request_id:"chat:test",output:"No sé.",evidence:[]});'
class SupervisionState(unittest.TestCase):
 def test_resets_untrusted_attempt_and_freezes_context(self):
  r=base();r['correction_attempt']=2
  out=call(setup(r)+'console.log(JSON.stringify(s));')
  self.assertEqual(out['request']['correction_attempt'],0);self.assertEqual(out['request']['candidate'],'No sé.')
 def test_mismatched_supervisor_result_escalates(self):
  out=call(setup()+'console.log(JSON.stringify(q.acceptJudge(s,{request_id:"wrong",candidate:"No sé.",judge:{exactitud_factual:5,estado_veredicto:"APROBADO"}})));')
  self.assertEqual(out['decision']['route'],'ESCALAR')
 def test_correction_cannot_change_evidence_counter_or_identity(self):
  out=call(setup()+'s=q.acceptJudge(s,{request_id:s.request.request_id,domain:s.request.domain,channel:s.request.channel,candidate:s.request.candidate,judge:{exactitud_factual:2,estado_veredicto:"CORREGIR"}});console.log(JSON.stringify(q.correctCandidate(s,{text:"Desconozco ese dato.",request_id:"evil",correction_attempt:0,evidence:["evil"]})));')
  self.assertEqual(out['request']['correction_attempt'],1);self.assertEqual(out['request']['evidence'],[]);self.assertEqual(out['request']['request_id'],'chat:test')
 def test_third_correction_is_impossible(self):
  out=call(setup()+'for(let i=0;i<3;i++){s=q.acceptJudge(s,{request_id:s.request.request_id,domain:s.request.domain,channel:s.request.channel,candidate:s.request.candidate,judge:{exactitud_factual:3,estado_veredicto:"CORREGIR"}});if(s.decision.route==="CORREGIR")s=q.correctCandidate(s,{text:"No sé."});}console.log(JSON.stringify(s));')
  self.assertEqual(out['decision']['route'],'ESCALAR');self.assertEqual(out['request']['correction_attempt'],2)
 def test_telegram_judge_cannot_approve_invalid_speech(self):
  r=base();r.update(channel='telegram',session_id='aurora_demo:telegram:test')
  out=call(setup(r)+'s.request.candidate="Mira https://example.com";console.log(JSON.stringify(q.acceptJudge(s,{request_id:s.request.request_id,domain:s.request.domain,channel:s.request.channel,candidate:s.request.candidate,judge:{exactitud_factual:5,estado_veredicto:"APROBADO"}})));')
  self.assertEqual(out['decision']['route'],'ESCALAR')
 def test_human_edit_validates_request_and_channel(self):
  out=call(setup()+'console.log(JSON.stringify([q.humanDecision(s,{request_id:"wrong",decision:"approve"}),q.humanDecision(s,{request_id:"chat:test",decision:"edit",edited_answer:"Revisado."}),q.humanDecision(s,{request_id:"chat:test",decision:"reject"})]));')
  self.assertEqual(out[0]['status'],'needs_human');self.assertEqual(out[1]['output'],'Revisado.');self.assertEqual(out[2]['status'],'rejected')
 def test_missing_candidate_or_provider_failure_never_succeeds(self):
  out=call(setup()+'console.log(JSON.stringify(q.correctCandidate(s,{error:"timeout"})));')
  self.assertEqual(out['decision']['route'],'ESCALAR')

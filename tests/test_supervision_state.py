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

class CitationRegression(unittest.TestCase):
 def state(self,channel='chat'):
  r=base();r.update(domain='outer_agent',channel=channel,session_id='outer_agent:'+channel+':test')
  e=dict(source_id='pdf:7',source_kind='outer_agent_pdf',text='Plan documentado: desde 100.',section='OA-01.1',page_start=2,page_end=2,score=.8,source_version='v1')
  return 'let s=q.startReview('+json.dumps(r)+','+json.dumps(dict(request_id=r['request_id'],status='success',output='Plan desde 100.\nFuente: Outer_Agent_Fuente_Organizacional_v1.pdf, p. 2 (OA-01.1).',evidence=[e]))+');'
 def test_plain_rewrite_retains_verified_citation_before_next_judge(self):
  out=call(self.state()+'s.decision={route:"CORREGIR"};s=q.correctCandidate(s,{text:"El plan parte de 100.",source_ids:["inventado"]});console.log(JSON.stringify(s));')
  self.assertIn('Fuente: Outer_Agent_Fuente_Organizacional_v1.pdf, p. 2',out['request']['candidate'])
  self.assertEqual(out['citation_source_ids'],['pdf:7'])
 def test_final_gate_rejects_removed_or_forged_citation(self):
  out=call(self.state()+'s.request.candidate="Plan desde 100. Fuente inventada.";console.log(JSON.stringify(q.acceptJudge(s,{request_id:s.request.request_id,domain:s.request.domain,channel:s.request.channel,candidate:s.request.candidate,judge:{exactitud_factual:5,estado_veredicto:"APROBADO"}})));')
  self.assertEqual(out['decision']['route'],'ESCALAR')
 def test_compacted_voice_has_verified_spoken_source_and_still_fits(self):
  out=call(self.state('telegram')+'console.log(JSON.stringify(q.compactCandidate(s,{text:"El plan parte de 100."})));')
  self.assertIn('Fuente: documento Outer Agent, página 2.',out['request']['candidate'])
  self.assertLessEqual(len(out['request']['candidate']),200)
  self.assertEqual(out['citation_source_ids'],['pdf:7'])
 def test_unknown_source_id_cannot_be_rendered(self):
  out=call(self.state()+'s.citation_source_ids=["inventado"];console.log(JSON.stringify(q.finalizeCandidate(s)));')
  self.assertEqual(out['decision']['route'],'ESCALAR')

class MemoryRecallCitationRegression(unittest.TestCase):
 def recall(self,mutation=''):
  r=base();r.update(domain='outer_agent',session_id='outer_agent:chat:test',query='¿Qué color prefiero?');r['context']['summary']={'asunto_principal':'Preferencia','puntos_clave':['Prefiere coral'],'accion_requerida':'Recordar'};r['context']['key_facts']=['Prefiere coral']
  return 'const request='+json.dumps(r)+';const memory={branch:"existing",record_id:"rec123",fields:{Session_ID:request.session_id},context:request.context};const provenance={source:"validated_session_summary",session_id:request.session_id,record_id:"rec123"};let trusted={route:"MEMORY_RECALL",memory};'+mutation+'let s=q.startReview(request,{request_id:request.request_id,status:"success",output:"Prefieres coral.",evidence:[],memory_provenance:provenance},trusted);'
 def test_validated_memory_recall_accepted_without_pdf_citation(self):
  out=call(self.recall()+'console.log(JSON.stringify(q.acceptJudge(s,{request_id:s.request.request_id,domain:s.request.domain,channel:s.request.channel,candidate:s.request.candidate,judge:{exactitud_factual:5,estado_veredicto:"APROBADO"}})));')
  self.assertEqual(out['decision']['route'],'APROBADO');self.assertEqual(out['response_category'],'memory_recall')
 def test_fabricated_or_wrong_session_provenance_is_not_exception(self):
  for mutation in ['trusted=null;','provenance.session_id="outer_agent:chat:other";','provenance.record_id="recOTHER";','trusted.route="OUTER_AGENT_INFO";']:
   out=call(self.recall(mutation)+'console.log(JSON.stringify(s));')
   self.assertEqual(out['decision']['route'],'ESCALAR')

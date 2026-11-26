import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG={'file_id':'dfl-test','source_version':'v1','page_count':10,'top_k':3,'minimum_score':0.5}
CHUNK={'content':'Roadmap cuesta $2500; moneda no especificada.','score':0.008,'rerank_score':0.82,'static_fields':{'parsed_directory_file_id':'dfl-test','page_range_start':4,'page_range_end':4,'chunk_index':3}}
def call(fn,*args):
 s='try{console.log(JSON.stringify(require("./src/retrieval.js")['+json.dumps(fn)+'](...'+json.dumps(args)+')))}catch(e){console.log(JSON.stringify({error:e.message}))}'
 return json.loads(subprocess.run(['node','-e',s],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
class Retrieval(unittest.TestCase):
 def test_router_cannot_cross_business_domains(self):
  self.assertEqual(call('domainRoute','AURORA_INFO','outer_agent'),'CLARIFY')
  self.assertEqual(call('domainRoute','OUTER_AGENT_INFO','aurora_demo'),'CLARIFY')
  self.assertEqual(call('domainRoute','OUTER_AGENT_INFO','outer_agent'),'OUTER_AGENT_INFO')
  self.assertEqual(call('domainRoute','invented','outer_agent'),'HUMAN')
 def test_real_rerank_score_not_hybrid_score_controls_filter(self):
  r=call('normalizeRetrieval',{'results':[CHUNK]},CONFIG,'outer_agent');self.assertEqual(r['evidence'][0]['score'],.82)
  r=call('normalizeRetrieval',{'results':[dict(CHUNK,score=.99,rerank_score=.003)]},CONFIG,'outer_agent');self.assertEqual(r['evidence'],[])
 def test_domain_isolation(self):
  self.assertIn('error',call('normalizeRetrieval',{'results':[CHUNK]},CONFIG,'aurora_demo'))
 def test_empty_and_provider_faults(self):
  self.assertEqual(call('normalizeRetrieval',{'results':[]},CONFIG,'outer_agent')['evidence'],[])
  for d in [{'error':'401'},{'error':'429'},{'error':'timeout'},{'results':'not-array'}]:self.assertIn('error',call('normalizeRetrieval',d,CONFIG,'outer_agent'))
 def test_no_fabricated_metadata_or_scores(self):
  for c in [dict(CHUNK,static_fields={}),dict(CHUNK,rerank_score=None),dict(CHUNK,static_fields=dict(CHUNK['static_fields'],parsed_directory_file_id='other')),dict(CHUNK,static_fields=dict(CHUNK['static_fields'],page_range_end=11))]:
   self.assertIn('error',call('normalizeRetrieval',{'results':[c]},CONFIG,'outer_agent'))
 def test_top_k_and_citations(self):
  evidence=call('normalizeRetrieval',{'results':[CHUNK]*4},CONFIG,'outer_agent')['evidence'];self.assertEqual(len(evidence),3)
  answer=call('groundedAnswer',{'supported':True,'answer':'El Roadmap cuesta $2500; la moneda no está especificada.','source_ids':['dfl-test:3']},evidence)
  self.assertIn('p. 4',answer['answer']);self.assertIn('Outer_Agent_Fuente_Organizacional_v1.pdf',answer['answer'])
  self.assertIn('error',call('groundedAnswer',{'supported':True,'answer':'dato','source_ids':['invented']},evidence))
 def test_no_se_is_literal_and_cannot_invent_source(self):
  r=call('groundedAnswer',{'supported':False,'answer':'invented','source_ids':[]},[]);self.assertEqual(r['answer'],'No sé. No está documentado en la fuente disponible.')
  self.assertIn('error',call('groundedAnswer',{'supported':True,'answer':'invented','source_ids':['dfl-test:3']},[]))
 def test_tool_observation_requires_valid_json(self):
  self.assertEqual(call('toolEvidence',[{'action':{'tool':'Consultar_documentacion_Outer_Agent'},'observation':json.dumps([{'ok':True,'evidence':[]}])}]),[])
  self.assertIn('error',call('toolEvidence',[]))

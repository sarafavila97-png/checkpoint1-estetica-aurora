import json, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def policy(fn,*args):
    script='const p=require("./src/contracts.js");try{console.log(JSON.stringify(p['+json.dumps(fn)+'](...'+json.dumps(args)+')))}catch(e){console.log(JSON.stringify({error:e.message}))}'
    result=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True)
    return json.loads(result.stdout) if result.returncode==0 else {'error':'implementation missing'}
class Contracts(unittest.TestCase):
    def request(self,**extra):
        return dict(schema_version='1',request_id='chat:r1',session_id='aurora_demo:chat:a',domain='aurora_demo',channel='chat',query='Precio manicure',user={'display_name':'Test','email':None},context={'summary':None,'case_status':'nuevo','key_facts':[]},evidence=[],candidate=None,correction_attempt=0,mode='dry_run',**extra)
    def test_request_roundtrip(self):
        self.assertEqual(policy('validateRequest',self.request()),self.request())
    def test_no_binary_handoff(self):
        self.assertIn('binary',policy('validateRequest',self.request(binary={'data':'private'}))['error'])
    def test_worker_contract_rejects_wrong_domain(self):
        result={'schema_version':'1','request_id':'chat:r1','status':'success','domain':'outer_agent','result':{'answer':'x','evidence':[],'proposed_action':'none'},'error':None}
        self.assertIn('domain',policy('validateResult',result,self.request())['error'])
    def test_error_result(self):
        r=policy('failure',self.request(),'WORKER_TIMEOUT','Worker no disponible')
        self.assertEqual(r.get('status'),'error'); self.assertEqual(r.get('result',{}).get('answer'),'');self.assertEqual(r.get('error',{}).get('code'),'WORKER_TIMEOUT')
    def test_missing_session_rejected(self):
        r=self.request();r['session_id']='';self.assertIn('session',policy('validateRequest',r)['error'])
    def test_unknown_domain_rejected(self):
        r=self.request();r['domain']='mixed';self.assertIn('domain',policy('validateRequest',r)['error'])
class Bundle(unittest.TestCase):
    def read(self,name):
        p=ROOT/'submissions/m02/workflows'/name
        self.assertTrue(p.exists(),f'missing workflow {name}')
        return json.loads(p.read_text())
    def test_two_workers_have_declared_trigger_and_result(self):
        for f in ['workers/aurora_knowledge.json','workers/response_writer.json']:
            w=self.read(f)
            self.assertTrue(any(n['type']=='n8n-nodes-base.executeWorkflowTrigger' for n in w['nodes']))
            self.assertTrue(any(n['name']=='WorkerResult' for n in w['nodes']))
            self.assertFalse(any(n['type']=='n8n-nodes-base.gmail' for n in w['nodes']))
    def test_wait_enabled_for_both_workers(self):
        w=self.read('aurora_manager.json');calls=[n for n in w['nodes'] if n['type']=='n8n-nodes-base.executeWorkflow']
        self.assertEqual(len(calls),2)
        self.assertTrue(all(n['parameters']['options']['waitForSubWorkflow'] for n in calls))
        self.assertTrue(all(n['onError']=='continueRegularOutput' for n in calls))
class DomainEvidence(unittest.TestCase):
    def test_cross_domain_evidence_rejected(self):
        q=Contracts().request();q['evidence']=[{'source_id':'oa','source_kind':'outer_agent_pdf','text':'Training $1500','section':None,'page_start':None,'page_end':None,'score':None,'source_version':'1'}]
        self.assertIn('evidence domain',policy('validateRequest',q).get('error',''))
    def test_payload_projection_native_set(self):
        w=json.loads((ROOT/'submissions/m02/workflows/aurora_manager.json').read_text())
        for n in w['nodes']:
            if n['name'].startswith('Payload minimo'):
                self.assertEqual(n['type'],'n8n-nodes-base.set')

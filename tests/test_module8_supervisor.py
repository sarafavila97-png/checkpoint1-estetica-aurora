import json, subprocess, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def workflow(): return json.loads((R/'drafts/module8/supervisor.json').read_text())
def run_node(name,item,prepared=None):
    node=next(n for n in workflow()['nodes'] if n['name']==name)
    script='const fn=new Function("$input","$",'+json.dumps(node['parameters']['jsCode'])+');console.log(JSON.stringify(fn({first:()=>({json:'+json.dumps(item)+'})},()=>({first:()=>({json:'+json.dumps(prepared)+'})}))));'
    p=subprocess.run(['node','-e',script],capture_output=True,text=True)
    if p.returncode: raise AssertionError(p.stderr)
    return json.loads(p.stdout)[0]['json']
def request():
    return dict(schema_version='1',request_id='chat:m8',session_id='aurora_demo:chat:a',domain='aurora_demo',channel='chat',query='Precio',user={'display_name':'Test','email':None},context={'summary':None,'case_status':'nuevo','key_facts':[]},evidence=[],candidate='No sé.',correction_attempt=0,mode='dry_run')
class Supervisor(unittest.TestCase):
    def test_missing_candidate_fails_before_model(self):
        q=request(); q['candidate']=None
        result=run_node('Preparar supervision',{'request':q})
        self.assertFalse(result['valid']); self.assertEqual(result['decision']['route'],'ESCALAR')
    def test_projection_excludes_routing_and_counter_from_model_data(self):
        q=request();q['correction_attempt']=2
        result=run_node('Preparar supervision',{'request':q})
        self.assertTrue(result['valid'])
        self.assertEqual(set(result['judge_input']),{'consulta_original','contexto_airtable','evidencia_recuperada','respuesta_propuesta','dominio'})
        self.assertEqual(result['request']['correction_attempt'],2)
    def test_model_failure_and_malformed_output_escalate(self):
        prepared=run_node('Preparar supervision',{'request':request()})
        for item in [{'error':'provider unavailable'},{'output':'bad JSON'},{'output':{'exactitud_factual':5,'estado_veredicto':'APROBADO','extra':1}}]:
            self.assertEqual(run_node('Validar veredicto',item,prepared)['decision']['route'],'ESCALAR')
    def test_manager_counter_controls_exhaustion(self):
        q=request();q['correction_attempt']=2
        prepared=run_node('Preparar supervision',{'request':q})
        result=run_node('Validar veredicto',{'output':{'exactitud_factual':3,'estado_veredicto':'CORREGIR'}},prepared)
        self.assertEqual(result['decision']['route'],'ESCALAR')
        self.assertEqual(result['candidate'],q['candidate'])
    def test_approved_candidate_is_returned_unchanged(self):
        q=request();q['candidate']='No sé. No está documentado.'
        prepared=run_node('Preparar supervision',{'request':q})
        result=run_node('Validar veredicto',{'output':{'exactitud_factual':4,'estado_veredicto':'APROBADO'}},prepared)
        self.assertEqual(result['decision']['route'],'APROBADO')
        self.assertEqual(result['candidate'],q['candidate'])
        self.assertEqual(result['request_id'],q['request_id'])
    def test_correction_returns_feedback_and_next_counter(self):
        prepared=run_node('Preparar supervision',{'request':request()})
        result=run_node('Validar veredicto',{'output':{'exactitud_factual':2,'estado_veredicto':'CORREGIR'}},prepared)
        self.assertEqual(result['decision']['route'],'CORREGIR')
        self.assertEqual(result['decision']['next_attempt'],1)
        self.assertTrue(result['decision']['feedback'])
    def test_native_model_parser_and_fail_closed_route(self):
        w=workflow();n={x['name']:x for x in w['nodes']}
        self.assertEqual(n['Juez factual']['onError'],'continueRegularOutput')
        schema=json.loads(n['Veredicto JSON']['parameters']['inputSchema'])
        self.assertFalse(schema['additionalProperties']);self.assertEqual(len(schema['required']),2)
        self.assertEqual(w['connections']['Solicitud valida']['main'][1][0]['node'],'Entrada invalida')
        self.assertEqual(w['connections']['Modelo juez']['ai_languageModel'][0][0]['node'],'Juez factual')
        self.assertEqual(w['connections']['Veredicto JSON']['ai_outputParser'][0][0]['node'],'Juez factual')
        self.assertFalse(w['active']);self.assertEqual(w['settings']['saveDataSuccessExecution'],'none')
        self.assertFalse(any('telegram' in x['type'] or 'gmail' in x['type'] or x['type']=='n8n-nodes-base.wait' for x in w['nodes']))

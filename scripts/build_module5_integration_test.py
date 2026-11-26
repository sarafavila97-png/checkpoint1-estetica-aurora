"""Two development integration cases; held-out questions are not read here."""
import copy,json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent/'work/implementation-private/module5-drafts'
m=json.loads((ROOT/'workflows/aurora_manager.json').read_text());n={x['name']:x for x in m['nodes']}
def code(name,js,x):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,name)),name=name,type='n8n-nodes-base.code',typeVersion=2,position=[x,300],parameters={'jsCode':js})
qs=[]
for i,query in enumerate(['Qué servicios ofrece Outer Agent y cuáles son sus precios publicados?','Cuál es la masa exacta del agujero negro central de la galaxia Messier 87?']):
 qs.append({'request':{'schema_version':'1','request_id':f'chat:m5-integration-{i+1}','session_id':f'outer_agent:chat:m5-integration-{i+1}','domain':'outer_agent','channel':'chat','query':query,'user':{'display_name':'Prueba documental','email':None},'context':{'summary':None,'case_status':'nuevo','key_facts':[]},'evidence':[],'candidate':None,'correction_attempt':0,'mode':'dry_run'}})
manual=copy.deepcopy(n['Prueba manual']);manual['position']=[0,300]
call=copy.deepcopy(n['Execute Worker conocimiento']);call.update(name='Probar agente documental',position=[500,300]);call['parameters']['workflowId']={'__rl':True,'value':'Yy3L0fXMzvDOizyj','mode':'id'};call['parameters']['mode']='each'
nodes=[manual,code('Dos consultas de desarrollo','return '+json.dumps([{'json':q} for q in qs],ensure_ascii=False)+';',240),call,code('Resultados de integracion',"return $input.all().map((item,i)=>{const r=item.json;return {json:{case_id:r.request_id,status:r.status,answer:r.result?.answer,evidence:r.result?.evidence,error:r.error,passed:r.status==='success'&&(r.request_id.endsWith('-1')?r.result.evidence.length>0:r.result.answer==='No sé. No está documentado en la fuente disponible.')}}});",800)]
w=dict(name='Aurora M5 - Integracion documental desarrollo',nodes=nodes,connections={},settings=m['settings'],active=False,pinData={})
for a,b in zip(nodes,nodes[1:]):w['connections'][a['name']]={'main':[[dict(node=b['name'],type='main',index=0)]]}
(P/'integration_test.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')

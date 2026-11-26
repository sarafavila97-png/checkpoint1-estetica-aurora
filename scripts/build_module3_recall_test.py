"""Cold-buffer recall: copy only validated durable summary to a fresh synthetic session."""
import copy,json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent/'work/implementation-private/module3-drafts'
m=json.loads((OUT/'aurora_manager.json').read_text());n={x['name']:x for x in m['nodes']}
r=json.loads((OUT/'memory_read.json').read_text());create=copy.deepcopy(next(x for x in r['nodes'] if x['name']=='Crear sesion'))
w={'name':'Aurora M3 - Recuerdo sin buffer','nodes':[],'connections':{},'settings':m['settings'],'active':False,'pinData':{}}
def code(name,s,x):return {'id':str(uuid.uuid5(uuid.NAMESPACE_URL,name)),'name':name,'type':'n8n-nodes-base.code','typeVersion':2,'position':[x,300],'parameters':{'jsCode':s}}
def call(name,ref,x):
 a=copy.deepcopy(n['Leer memoria']);a.update(name=name,id=str(uuid.uuid5(uuid.NAMESPACE_URL,name)),position=[x,300]);a['parameters']['workflowId']['value']=ref;return a
q={'schema_version':'1','request_id':'chat:m3-cold-E1','session_id':'aurora_demo:chat:m3-real-C','domain':'aurora_demo','channel':'chat','query':'¿Qué color de esmalte dije que prefiero?','user':{'display_name':'Prueba Coral','email':None},'context':{'summary':None,'case_status':'nuevo','key_facts':[]},'evidence':[],'candidate':None,'correction_attempt':0,'mode':'dry_run'}
manual=copy.deepcopy(n['Prueba manual']);manual['position']=[0,300]
create.update(name='Restaurar resumen sintetico',position=[900,300],id=str(uuid.uuid5(uuid.NAMESPACE_URL,'restore-summary')))
w['nodes']=[manual,code('Sesion con resumen','return [{json:{request:'+json.dumps(q,ensure_ascii=False)+'}}];',200),call('Leer resumen validado','oap8j98XvShrjhr7',430),code('Preparar sesion sin buffer',"const d=$input.first().json;if(!d.ok||!d.request.context.summary)throw Error('Missing validated source summary');const request={...d.request,session_id:'aurora_demo:chat:m3-cold-E'};const f={...d.memory.fields,Session_ID:request.session_id,'Fecha de actualización':new Date().toISOString()};const meta=JSON.parse(f['Datos clave']);meta.accepted_message_count=0;meta.last_request_ids=[];f['Datos clave']=JSON.stringify(meta);return [{json:{request,fields:f}}];",670),create,code('Consultar preferencia',"const d=$input.first().json;if(d.error||!d.id)throw Error('Restore failed');return [{json:{request:$('Preparar sesion sin buffer').first().json.request}}];",1120),call('Manager recuerdo','Dkz9Ehr9wyuzQJVU',1350),code('Verificar recuerdo persistente',"const r=$input.first().json;const id=$('Restaurar resumen sintetico').first().json.id;if(r.status!=='success'||!r.output.toLowerCase().includes('coral')||r.memory_status!=='saved'||r.memory_provenance?.source!=='validated_session_summary'||r.memory_provenance.record_id!==id)throw Error('Recall failed: '+JSON.stringify(r));return [{json:{status:'PASS',session_id:'aurora_demo:chat:m3-cold-E',record_id:id,answer:r.output,provenance:r.memory_provenance,short_buffer_before_test:'empty: fresh Session_ID, only durable fields copied',restoration:'synthetic test fixture copied from validated C summary; no conversation copied'}}];",1600)]
for a,b in zip(w['nodes'],w['nodes'][1:]):w['connections'][a['name']]={'main':[[{'node':b['name'],'type':'main','index':0}]]}
(OUT/'memory_cold_recall.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Cold-buffer recall fixture generated; not run.')

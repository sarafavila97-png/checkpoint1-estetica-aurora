"""Prepare fixed matched A/B cases; no execution, no expected claims sent to models."""
import json,copy,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
cases=json.loads((R/'evaluation/module8-cases.json').read_text())['cases'];assert len(cases)==5
settings=json.loads((R/'drafts/module8/aurora_manager.json').read_text())['settings']
settings.update(saveDataErrorExecution='all',saveDataSuccessExecution='all',saveManualExecutions=True)
def node(name,t,p,x,v=1,**kw):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'m8-harness:'+name)),name=name,type=t,typeVersion=v,position=[x,300],parameters=p,**kw)
def code(name,js,x):return node(name,'n8n-nodes-base.code',{'jsCode':js},x,2)
def save(name,nodes,file):
 w=dict(name=name,nodes=nodes,connections={},settings=settings,active=False,pinData={})
 for a,b in zip(nodes,nodes[1:]):w['connections'][a['name']]={'main':[[dict(node=b['name'],type='main',index=0)]]}
 (D/file).write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
def request(c,arm):return dict(schema_version='1',request_id='chat:m8-official-'+arm+'-'+c['case_id'],session_id=c['domain']+':chat:m8-official-'+arm+'-'+c['case_id'],domain=c['domain'],channel='chat',query=c['query'],user={'display_name':'Evaluacion sintetica','email':None},context={'summary':None,'case_status':'nuevo','key_facts':[]},evidence=[],candidate=None,correction_attempt=0,mode='dry_run')
inputs=[{'json':{'request':request(c,arm),'arm':arm}} for c in cases for arm in ['A','B']]
m=json.loads((R/'drafts/module8/aurora_manager.json').read_text());call=copy.deepcopy(next(n for n in m['nodes'] if n['name']=='Supervisor 0'));call.update(id='m8-official-call',name='Ejecutar caso medido',position=[500,300]);call['parameters']['workflowId']['value']='5UvufWORP48dwMtT';call['parameters']['mode']='each';call['parameters']['workflowInputs']['value']['arm']='={{ $json.arm }}';call['parameters']['workflowInputs']['schema'].append({'id':'arm','displayName':'arm','type':'string','required':False,'display':True,'canBeUsedToMatch':True})
manual=node('Prueba manual','n8n-nodes-base.manualTrigger',{},0)
result=code('Exportar diez resultados',"const rows=$input.all().map(i=>i.json);const report={harness_execution_id:String($execution.id),captured_at:new Date().toISOString(),runs:rows};return [{json:{runs:rows.length,run_ids:rows.map(r=>r.run_id),independent_scoring:'pending',usage_capture:'pending'},binary:{data:{data:Buffer.from(JSON.stringify(report,null,2)).toString('base64'),mimeType:'application/json',fileName:'m8-official-results.json',fileExtension:'json'}}}];",800)
seed_requests=[{'json':{'request':request(c,arm)}} for c in cases if c['case_id']=='M8-02' for arm in ['A','B']]
readback=copy.deepcopy(call);readback.update(id='m8-readback',name='Releer memorias sembradas',position=[500,700]);readback['parameters']['workflowId']['value']='oap8j98XvShrjhr7';readback['parameters']['workflowInputs']['value'].pop('arm');readback['parameters']['workflowInputs']['schema']=[f for f in readback['parameters']['workflowInputs']['schema'] if f['id']=='request']
expected=next(c['initial_context'] for c in cases if c['case_id']=='M8-02')
check=code('Confirmar contexto previo',"const rows=$input.all().map(i=>i.json),expected="+json.dumps(expected,ensure_ascii=False)+";if(rows.length!==2||rows.some(r=>r.ok!==true||JSON.stringify(r.request.context)!==JSON.stringify(expected)||JSON.parse(r.memory.fields['Datos clave']).accepted_message_count!==0))throw Error('MEMORY_PRECONDITION_FAILED_NO_OFFICIAL_RUNS');return [{json:{verified:true,records:rows.map(r=>({session_id:r.request.session_id,record_id:r.memory.record_id,context:r.request.context}))}}];",750)
result['parameters']['jsCode']=result['parameters']['jsCode'].replace('runs:rows','seed_readback:$("Confirmar contexto previo").first().json,runs:rows')
save('Aurora M8 - Diez corridas oficiales A y B',[manual,code('Memorias a verificar','return '+json.dumps(seed_requests,ensure_ascii=False)+';',240),readback,check,code('Casos congelados','return '+json.dumps(inputs,ensure_ascii=False)+';',1000),call,result],'m8_official_harness.json')
# Only two synthetic memory preference records are seeded. No model calls.
seed=[{'json':{'request':request(c,arm),'context':c['initial_context']}} for c in cases if c['case_id']=='M8-02' for arm in ['A','B']]
lib=(R/'src/memory.js').read_text().split('module.exports=')[0]
prepare=code('Preparar dos memorias',lib+'\nconst rows='+json.dumps(seed,ensure_ascii=False)+";return rows.map(i=>{const q=i.json.request,c=i.json.context,f=newRecord(q.session_id,q.user.display_name);validateSummary(c.summary);f['Resumen consolidado']=JSON.stringify(c.summary);const m=JSON.parse(f['Datos clave']);m.key_facts=c.key_facts;f['Datos clave']=JSON.stringify(m);return {json:{request:q,fields:f}}});",240)
source=json.loads((P/'module3-drafts/memory_read.json').read_text());create=copy.deepcopy(next(n for n in source['nodes'] if n['name']=='Crear sesion'));create.update(id='m8-seed-create',name='Crear memoria sintetica',position=[500,300])
verify=code('Comprobar dos altas',"const rows=$input.all().map(i=>i.json);if(rows.length!==2||rows.some(r=>r.error||!r.id))throw Error('SEED_NOT_CONFIRMED_RECONCILE_NO_RETRY');return [{json:{status:'PASS',records:rows.map(r=>({record_id:r.id,session_id:r.fields?.Session_ID||r.Session_ID})),model_calls:0}}];",800)
save('Aurora M8 - Preparar memoria sintetica evaluacion',[manual,prepare,create,verify],'m8_seed_memory.json')
print('Prepared 10 fixed cases and separate two-record memory seed; neither executed.')

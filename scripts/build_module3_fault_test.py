"""Controlled native Airtable unavailable-table fault in an isolated read-worker copy."""
import copy,json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent/'work/implementation-private/module3-drafts'
w=json.loads((OUT/'memory_read.json').read_text());w['name']='Aurora M3 - Fallo Airtable aislado'
m=json.loads((OUT/'aurora_manager.json').read_text());n={x['name']:x for x in m['nodes']}
def code(name,s,x,y=900):return {'id':str(uuid.uuid5(uuid.NAMESPACE_URL,name)),'name':name,'type':'n8n-nodes-base.code','typeVersion':2,'position':[x,y],'parameters':{'jsCode':s}}
def call(name,x):
 a=copy.deepcopy(n['Leer memoria']);a.update(name=name,id=str(uuid.uuid5(uuid.NAMESPACE_URL,name)),position=[x,900]);return a
for item in w['nodes']:
 if item['type']=='n8n-nodes-base.airtable':item['parameters']['table']['value']='tbl00000000000000'
q={'schema_version':'1','request_id':'chat:m3-fault-C','session_id':'aurora_demo:chat:m3-real-C','domain':'aurora_demo','channel':'chat','query':'Prueba de dependencia, sin llamar LLM','user':{'display_name':'Prueba Coral','email':None},'context':{'summary':None,'case_status':'nuevo','key_facts':[]},'evidence':[],'candidate':None,'correction_attempt':0,'mode':'dry_run'}
manual=copy.deepcopy(n['Prueba manual']);manual['position']=[0,900]
w['nodes'] += [manual,code('Entrada de fallo','return [{json:{request:'+json.dumps(q,ensure_ascii=False)+'}}];',220),call('Estado antes',440),code('Consulta aislada',"const d=$input.first().json;if(!d.ok||d.memory.branch!=='existing')throw Error('Baseline missing');return [{json:{request:d.request}}];",660),code('Comprobar error tipado',"const r=$input.first().json;if(r.ok!==false||r.error?.code!=='MEMORY_READ_ERROR')throw Error('Fault was not contained');return [{json:{request:$('Consulta aislada').first().json.request}}];",1800),call('Estado despues',2020),code('Resultado de fallo',"const before=$('Estado antes').first().json,after=$input.first().json;if(!after.ok||before.memory.record_id!==after.memory.record_id||JSON.stringify(before.memory.fields)!==JSON.stringify(after.memory.fields))throw Error('Persistent memory changed');return [{json:{status:'PASS',failure:'unavailable Airtable table in isolated worker copy',error_code:$('Validar lectura').first().json.error.code,record_id:after.memory.record_id,persistent_fields:'unchanged',llm_calls:0}}];",2240)]
def edge(a,b):w['connections'][a]={'main':[[{'node':b,'type':'main','index':0}]]}
for a,b in [('Prueba manual','Entrada de fallo'),('Entrada de fallo','Estado antes'),('Estado antes','Consulta aislada'),('Consulta aislada','Validar sesion'),('No Operation, do nothing','Comprobar error tipado'),('Comprobar error tipado','Estado despues'),('Estado despues','Resultado de fallo')]:edge(a,b)
(OUT/'memory_fault_test.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Fault clone generated; original workers untouched. Not run.')

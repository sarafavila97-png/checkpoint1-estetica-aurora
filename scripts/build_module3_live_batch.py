"""Six-turn real-model integration check; use a fresh session for each deliberate rerun."""
import copy,json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent/'work/implementation-private';OUT=P/'module3-drafts'
base=json.loads((OUT/'aurora_manager.json').read_text());bn={n['name']:n for n in base['nodes']}
w={'name':'Aurora M3 - Seis turnos reales','nodes':[],'connections':{},'settings':base['settings'],'active':False,'pinData':{}}
def node(name,typ,p,x,y=300,v=1,**kw):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'m3-real:'+name)),name=name,type=typ,parameters=p,typeVersion=v,position=[x,y],**kw)
def code(name,s,x):return node(name,'n8n-nodes-base.code',{'jsCode':s},x,v=2)
def edge(a,b):w['connections'].setdefault(a,{'main':[[]]})['main'][0].append({'node':b,'type':'main','index':0})
def call(name,ref,x):
 n=copy.deepcopy(bn['Leer memoria']);n.update(id=str(uuid.uuid5(uuid.NAMESPACE_URL,name)),name=name,position=[x,300]);n['parameters']['workflowId']['value']=ref;return n
request={'schema_version':'1','request_id':'','session_id':'aurora_demo:chat:m3-real-C','domain':'aurora_demo','channel':'chat','query':'','user':{'display_name':'Prueba Coral','email':None},'context':{'summary':None,'case_status':'nuevo','key_facts':[]},'evidence':[],'candidate':None,'correction_attempt':0,'mode':'dry_run'}
queries=['Me interesa el manicure de Estética Aurora. Mi preferencia personal es esmalte coral. ¿Cuánto cuesta?', '¿Cuánto dura el manicure de Estética Aurora?', '¿Cuál es el horario de Estética Aurora?', '¿Puedo reservar contigo un manicure en Estética Aurora?', '¿Qué medios de pago acepta Estética Aurora?', 'Para el manicure de Estética Aurora, ¿qué color de esmalte dije que prefiero?']
w['nodes'].append(node('Iniciar seis turnos','n8n-nodes-base.manualTrigger',{},0));prev='Iniciar seis turnos';results=[]
for i,query in enumerate(queries,1):
 label=f'{i:02}';x=250+(i-1)*1200;q=copy.deepcopy(request);q.update(request_id=f'chat:m3-real-C{i}',query=query)
 fixture='Turno '+label;run='Manager '+label;prep='Preparar lectura '+label;read='Leer registro '+label;check='Verificar '+label
 w['nodes'] += [code(fixture,'return [{json:{request:'+json.dumps(q,ensure_ascii=False)+'}}];',x),call(run,'Dkz9Ehr9wyuzQJVU',x+220),code(prep,"const r=$input.first().json;if(!['success','needs_human'].includes(r.status)||r.memory_status!=='saved')throw Error('Manager did not persist: '+JSON.stringify(r));return [{json:{request:$('"+fixture+"').first().json.request}}];",x+440),call(read,'oap8j98XvShrjhr7',x+660),code(check,"const r=$input.first().json;if(!r.ok||r.memory.branch!=='existing')throw Error('Memory unavailable');const f=r.memory.fields,m=JSON.parse(f['Datos clave']);if(m.accepted_message_count!=="+str(i%6)+"||m.last_request_ids.length!=="+str(i)+")throw Error('Counter mismatch');const summary=f['Resumen consolidado'];if("+str(i)+"===6&&(!summary||!summary.toLowerCase().includes('coral')))throw Error('First-turn preference absent from generated summary');return [{json:{turn:"+str(i)+",status:'PASS',record_id:r.memory.record_id,count:m.accepted_message_count,summary:summary||'empty',answer:$('"+run+"').first().json.output}}];",x+880)]
 for a,b in [(prev,fixture),(fixture,run),(run,prep),(prep,read),(read,check)]:edge(a,b)
 prev=check;results.append(check)
w['nodes'].append(code('Resultados seis turnos','return ['+','.join("{json:$('"+n+"').first().json}" for n in results)+'];',7600));edge(prev,'Resultados seis turnos')
(OUT/'memory_live_batch.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Generated six-turn live-model test draft. Not yet run.')

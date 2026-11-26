"""Synthetic text-only evaluation clones, with native model nodes in one execution.
No expected answers enter the workflow. Public production workflows are unchanged.
"""
import copy,json,re,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
env=json.loads((P/'module8-environment.json').read_text())
def load(p):return json.loads((R/p).read_text())
def inline(w,call_name,worker,prefix):
 call=next(n for n in w['nodes'] if n['name']==call_name)
 assert call['parameters']['workflowInputs']['value']=={'request':'={{ $json.request }}'},call_name
 child=load(worker);names={n['name']:(n['name'] if n['type'].endswith('Tool') or 'toolWorkflow' in n['type'] else prefix+n['name']) for n in child['nodes']}
 triggers=[n for n in child['nodes'] if n['type']=='n8n-nodes-base.executeWorkflowTrigger'];assert len(triggers)==1
 # Rename references only; preserve prompts, tools, models and parameter values.
 def renamed(value):
  if isinstance(value,dict):return {k:renamed(v) for k,v in value.items()}
  if isinstance(value,list):return [renamed(v) for v in value]
  if isinstance(value,str):
   for old,new in names.items():
    value=value.replace("$('"+old+"')","$('"+new+"')").replace('$("'+old+'")','$("'+new+'")')
   return value
  return value
 copied=[]
 for n in child['nodes']:
  n=renamed(copy.deepcopy(n));old=n['name'];n['name']=names[old];n['id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'m8-eval:'+n['name']))
  if n['type']=='n8n-nodes-base.executeWorkflowTrigger':
   n.update(type='n8n-nodes-base.code',typeVersion=2,parameters={'jsCode':'return $input.all().map(i=>({json:{request:i.json.request}}));'})
  copied.append(n)
 successors=w['connections'].pop(call_name,{}).get('main',[[]])[0]
 for types in w['connections'].values():
  for ports in types.values():
   for port in ports:
    for e in port:
     if e['node']==call_name:e['node']=names[triggers[0]['name']]
 for origin,types in child['connections'].items():
  w['connections'][names[origin]]={kind:[[{**e,'node':names[e['node']]} for e in port] for port in ports] for kind,ports in types.items()}
 for n in child['nodes']:
  if n['type']=='n8n-nodes-base.code' and not child['connections'].get(n['name'],{}).get('main'):
   w['connections'][names[n['name']]]={'main':[copy.deepcopy(successors)]}
 w['nodes']=[n for n in w['nodes'] if n['name']!=call_name]+copied
for arm in ['AB']:
 w=load('drafts/module8/aurora_manager.json');w['name']='Aurora M8 - Evaluacion textual A y B'
 for call,file,prefix in [('Execute Worker conocimiento','drafts/module6/aurora_knowledge.json','Aurora / '),('Execute Worker redaccion','workflows/workers/response_writer.json','Writer / '),('Execute Worker Outer Agent','drafts/module6/outer_agent_knowledge.json','Outer / ')]+[(f'Supervisor {i}','drafts/module8/supervisor.json',f'Juez {i} / ') for i in range(3)]:inline(w,call,file,prefix)
 # Child references in decision code now refer to final validator output only.
 # Original decision reads Candidato final, so it remains unchanged.
 for n in w['nodes']:
  if n['name']=='Worker Input':n['parameters']['workflowInputs']['values'].append({'name':'arm','type':'string'})
  if n['name'].startswith('Switch veredicto '):n['parameters']['output']=n['parameters']['output'].replace('$json.decision.route === \"CORREGIR\"',"$json.decision.route === \"CORREGIR\" && $('Preparar consulta').first().json.evaluation_arm === 'B'")
  if n['name']=='Consulta sintetica':n['parameters']['jsCode']='return [{json:{request:'+json.dumps(dict(schema_version='1',request_id='chat:m8-dev-inline-'+arm,session_id='aurora_demo:chat:m8-dev-inline-'+arm,domain='aurora_demo',channel='chat',query='Precio manicure',user={'display_name':'Prueba sintetica','email':None},context={'summary':None,'case_status':'nuevo','key_facts':[]},evidence=[],candidate=None,correction_attempt=0,mode='dry_run'),ensure_ascii=False)+'}}];'
  if n['name']=='Preparar consulta':n['parameters']['jsCode']=n['parameters']['jsCode'].replace('request:validateRequest(r)',"started_at:Date.now(),evaluation_arm:$input.first().json.arm==='A'?'A':'B',request:validateRequest({...r,mode:'dry_run'})")
  if n['name']=='Revision en vivo':n['parameters']['conditions']['conditions'][0]['leftValue']='={{ false }}'
  if n['type']=='@n8n/n8n-nodes-langchain.lmChatOpenAi':n['credentials']={'openAiApi':{'id':None,'name':'','__aiGatewayManaged':True}}
  if n['type']=='n8n-nodes-base.googleSheetsTool':n['credentials']={'googleSheetsOAuth2Api':env['sheets_credential']}
  if n['type']=='n8n-nodes-base.slack':n.pop('credentials',None);n['disabled']=True
 audit={'id':'m8-evaluation-audit','name':'Medicion evaluacion','type':'n8n-nodes-base.code','typeVersion':2,'position':[4600,4000],'parameters':{'jsCode':"const p=$('Preparar consulta').first().json,r=$input.first().json;const q=$('Aplicar memoria').first().json.request;return [{json:{...r,run_id:String($execution.id),architecture:p.evaluation_arm,elapsed_ms:Date.now()-p.started_at,evaluation_input:{query:q.query,domain:q.domain,context:q.context},cost:null}}];"}}
 w['nodes'].append(audit)
 for terminal in ['Final con memoria','Retornar sin escritura','Cierre con fallo de memoria']:
  w['connections'][terminal]={'main':[[{'node':'Medicion evaluacion','type':'main','index':0}]]}
 # Text-only synthetic runs retained solely to capture actual model usage.
 w['settings'].update(saveDataErrorExecution='all',saveDataSuccessExecution='all',saveManualExecutions=True,saveExecutionProgress=False)
 raw=json.dumps(w,ensure_ascii=False)
 for k,v in env['bindings'].items():raw=raw.replace(k,v)
 assert not re.findall(r'REPLACE_[A-Z0-9_]+',raw)
 (D/f'm8_evaluation_{arm}.json').write_text(json.dumps(json.loads(raw),ensure_ascii=False,indent=2)+'\n')
 print(arm,len(w['nodes']),'nodes; inactive, synthetic text only, no delivery')

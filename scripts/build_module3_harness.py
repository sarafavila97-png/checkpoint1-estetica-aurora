"""Private synthetic read/write integration harness; no model calls or outbound delivery."""
import json,copy,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R.parent/'work/implementation-private/module3-drafts'
base=json.loads((R/'submissions/m02/workflows/aurora_manager.json').read_text())
def node(name,typ,p,x,v=1):return {'id':str(uuid.uuid5(uuid.NAMESPACE_URL,'aurora-m3-harness:'+name)),'name':name,'type':typ,'typeVersion':v,'position':[x,300],'parameters':p}
def code(n,s,x):return node(n,'n8n-nodes-base.code',{'jsCode':s},x,2)
q={'schema_version':'1','request_id':'chat:m3-A1','session_id':'aurora_demo:chat:m3-A','domain':'aurora_demo','channel':'chat','query':'Precio manicure','user':{'display_name':'Prueba A','email':None},'context':{'summary':None,'case_status':'nuevo','key_facts':[]},'evidence':[],'candidate':None,'correction_attempt':0,'mode':'dry_run'}
callbase=next(n for n in base['nodes'] if n['type']=='n8n-nodes-base.executeWorkflow')
def call(name,ref,x,request,summary=False):
 n=copy.deepcopy(callbase);n.update(name=name,id=str(uuid.uuid5(uuid.NAMESPACE_URL,name)),position=[x,300]);n['parameters']['workflowId']={'__rl':True,'value':ref,'mode':'id'};n['parameters']['workflowInputs']['value']={'request':request};n['parameters']['workflowInputs']['schema']=[{'id':'request','displayName':'request','type':'object','required':True,'display':True,'canBeUsedToMatch':True}]
 if summary:n['parameters']['workflowInputs']['value']['summary']='={{ $("Caso sintetico").first().json.summary }}';n['parameters']['workflowInputs']['schema'].append({'id':'summary','displayName':'summary','type':'object','required':False,'display':True,'canBeUsedToMatch':True})
 return n
nodes=[node('Prueba manual','n8n-nodes-base.manualTrigger',{},0),code('Caso sintetico','return [{json:'+json.dumps({'request':q,'summary':None},ensure_ascii=False)+'}];',220),call('Leer antes','oap8j98XvShrjhr7',440,'={{ $json.request }}'),code('Exigir lectura','const d=$input.first().json;if(!d.ok)throw Error(JSON.stringify(d.error||d));return [{json:d}];',660),call('Escribir mensaje','f9IIvpgiyEKgiYTX',880,'={{ $json.request }}',True),call('Leer despues','oap8j98XvShrjhr7',1100,'={{ $("Caso sintetico").first().json.request }}'),code('Resultado observado','return [{json:{case_id:$("Caso sintetico").first().json.request.request_id,before:$("Leer antes").first().json,write:$("Escribir mensaje").first().json,after:$input.first().json}}];',1320)]
cons={a['name']:{'main':[[{'node':b['name'],'type':'main','index':0}]]} for a,b in zip(nodes,nodes[1:])}
w={'name':'Aurora M3 - Pruebas memoria','nodes':nodes,'connections':cons,'settings':base['settings'],'active':False,'pinData':{}}
(O/'memory_harness.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Private harness written')

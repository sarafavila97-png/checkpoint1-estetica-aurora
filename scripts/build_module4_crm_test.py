"""Private synthetic CRM sequence. No LLM calls or outbound messages."""
import json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent/'work/implementation-private'
w=json.loads((P/'m4-crm-first-export.json').read_text())
nodes=[{'id':'manual','name':'Prueba manual','type':'n8n-nodes-base.manualTrigger','typeVersion':1,'position':[0,300],'parameters':{}}];edges=[];last='Prueba manual'
for i,name in enumerate(['Aurora M4 Sintetico','','Aurora M4 Actualizado']):
 req={'request_id':'gmail:m4-crm-sequence-'+str(i+1),'email':'aurora-m4-crm-20261126@example.com','display_name':name,'mode':'draft_only'}
 a='Entrada '+str(i+1);b='CRM '+str(i+1)
 nodes += [{'id':a,'name':a,'type':'n8n-nodes-base.set','typeVersion':3.4,'position':[240+i*480,300],'parameters':{'assignments':{'assignments':[{'id':'request','name':'request','type':'object','value':json.dumps(req)}]},'options':{}}}, {'id':b,'name':b,'type':'n8n-nodes-base.executeWorkflow','typeVersion':1.3,'position':[480+i*480,300],'parameters':{'workflowId':{'__rl':True,'value':w['id'],'mode':'id'},'workflowInputs':{'mappingMode':'defineBelow','value':{'request':'={{ $json.request }}'},'matchingColumns':[],'schema':[{'id':'request','displayName':'request','type':'object','required':False,'display':True,'defaultMatch':False,'canBeUsedToMatch':True}],'attemptToConvertTypes':False,'convertFieldsToString':False},'options':{'waitForSubWorkflow':True}},'onError':'continueRegularOutput'}]
 edges += [(last,a),(a,b)];last=b
body="const rows=[1,2,3].map(i=>$('CRM '+i).first().json);const ids=rows.map(r=>r.contact_id);const ok=rows.every(r=>r.ok===true&&r.status==='success')&&ids.every(id=>id&&id===ids[0])&&rows[0].action==='created'&&rows[1].action==='found'&&rows[2].action==='updated';return [{json:{test_id:'m4-crm-create-found-update',pass:ok,results:rows,no_external_messages:true,llm_calls:0}}];"
nodes.append({'id':'proof','name':'Verificar resultados','type':'n8n-nodes-base.code','typeVersion':2,'position':[1800,300],'parameters':{'jsCode':body}});edges.append((last,'Verificar resultados'))
out={'name':'Aurora M4 - Prueba CRM sintetica','nodes':nodes,'connections':{a:{'main':[[{'node':b,'type':'main','index':0}]]} for a,b in edges},'settings':w['settings'],'active':False,'pinData':{}}
(P/'module4-drafts/crm_sequence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Synthetic sequence ready; execute once, then inspect final proof.')

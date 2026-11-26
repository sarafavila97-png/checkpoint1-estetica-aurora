"""Synthetic messages through the real inbox child; never poll Gmail or send mail."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent/'work/implementation-private'
env=json.loads((P/'module4-environment.json').read_text())
base={'id':'m4-blocked','threadId':'synthetic-thread','from':'Prueba <aurora-guard@example.com>','subject':'Consulta manicure','text':'Precio de manicure'}
cases=[('auto-submitted',{'headers':{'Auto-Submitted':'auto-replied'}}),('autoreply',{'headers':{'X-Autoreply':'yes'}}),('precedence',{'headers':{'Precedence':'bulk'}}),('noreply',{'from':'noreply@example.com'}),('out-of-office',{'subject':'Out of office: prueba'}),('undeliverable',{'subject':'Undeliverable: prueba'}),('invalid-sender',{'from':'bad-address'})]
nodes=[{'id':'manual','name':'Prueba manual','type':'n8n-nodes-base.manualTrigger','typeVersion':1,'position':[0,300],'parameters':{}}];edges=[];last='Prueba manual'
for i,(case,override) in enumerate(cases):
 a='Mensaje '+str(i+1);b='Filtro '+str(i+1);mail={**base,**override,'id':'m4-'+case}
 nodes += [{'id':a,'name':a,'type':'n8n-nodes-base.set','typeVersion':3.4,'position':[240+i*480,300],'parameters':{'assignments':{'assignments':[{'id':'mail','name':'mail','type':'object','value':json.dumps(mail)}]},'options':{}}},{'id':b,'name':b,'type':'n8n-nodes-base.executeWorkflow','typeVersion':1.3,'position':[480+i*480,300],'parameters':{'workflowId':{'__rl':True,'value':'wtvU9RXoJigPHsIG','mode':'id'},'workflowInputs':{'mappingMode':'defineBelow','value':{'mail':'={{ $json.mail }}'},'matchingColumns':[],'schema':[{'id':'mail','displayName':'mail','type':'object','required':False,'display':True,'defaultMatch':False,'canBeUsedToMatch':True}],'attemptToConvertTypes':False,'convertFieldsToString':False},'options':{'waitForSubWorkflow':True}},'onError':'continueRegularOutput'}];edges += [(last,a),(a,b)];last=b
body="const results="+json.dumps([c[0] for c in cases])+".map((case_id,i)=>({case_id,...$('Filtro '+(i+1)).first().json}));return [{json:{test_id:'m4-inbox-guards',pass:results.every(r=>r.status==='blocked'&&r.llm_calls===0),results,external_messages_sent:0}}];"
nodes.append({'id':'proof','name':'Verificar filtros','type':'n8n-nodes-base.code','typeVersion':2,'position':[4000,300],'parameters':{'jsCode':body}});edges.append((last,'Verificar filtros'))
w={'name':'Aurora M4 - Prueba filtros correo','nodes':nodes,'connections':{a:{'main':[[{'node':b,'type':'main','index':0}]]} for a,b in edges},'settings':json.loads((P/'m4-crm-first-export.json').read_text())['settings'],'active':False,'pinData':{}}
(P/'module4-drafts/inbox_guards_test.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')

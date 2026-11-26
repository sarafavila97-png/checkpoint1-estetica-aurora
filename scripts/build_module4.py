"""Generate inactive M4 drafts; hosted validation is required before promotion."""
import json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'drafts/module4';OUT.mkdir(parents=True,exist_ok=True)
LIB=(ROOT/'src/inbox.js').read_text().split('module.exports=')[0]
SETTINGS=json.loads((ROOT/'workflows/aurora_manager.json').read_text())['settings']
def node(name,typ,p,x,y=300,v=1,**extra):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'aurora-m4:'+name)),name=name,type=typ,typeVersion=v,position=[x,y],parameters=p,**extra)
def code(name,body,x,y=300):return node(name,'n8n-nodes-base.code',{'jsCode':LIB+'\n'+body},x,y,2)
def iff(name,expr,x,y=300):return node(name,'n8n-nodes-base.if',{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':2},'conditions':[{'id':name,'leftValue':expr,'rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}},x,y,2.2)
def save(name,nodes,edges,file):
 w={'name':name,'nodes':nodes,'connections':{},'settings':SETTINGS,'active':False,'pinData':{}}
 for a,b,*o in edges:
  out=o[0] if o else 0;ports=w['connections'].setdefault(a,{}).setdefault('main',[])
  while len(ports)<=out:ports.append([])
  ports[out].append({'node':b,'type':'main','index':0})
 (OUT/file).write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
 return w
def search(name,x,y=300):return node(name,'n8n-nodes-base.hubspot',{'authentication':'oAuth2','resource':'contact','operation':'search','returnAll':False,'limit':2,'filterGroupsUi':{'filterGroupsValues':[{'filtersUi':{'filterValues':[{'propertyName':'email|string','type':'string','operator':'EQ','value':"={{ $('Validar CRM').first().json.email }}"}]}}]},'additionalFields':{'properties':['email','firstname']}},x,y,2.2,alwaysOutputData=True,onError='continueRegularOutput')
trigger=node('CRM Input','n8n-nodes-base.executeWorkflowTrigger',{'workflowInputs':{'values':[{'name':'request','type':'object'}]}},0,v=1.1)
validate=code('Validar CRM',"const q=$input.first().json.request;if(!/^gmail:[^\\s]+$/.test(q.request_id)||!['dry_run','draft_only'].includes(q.mode))throw Error('INVALID_CRM_REQUEST');const email=parseSender(q.email).email;return [{json:{request_id:q.request_id,email,display_name:String(q.display_name||'').slice(0,100),mode:q.mode}}];",240)
plan=code('Plan CRM',"const q=$('Validar CRM').first().json;try{const rows=$input.all().map(i=>i.json);if(rows.some(r=>r.error))throw Error('CRM_LOOKUP_ERROR');const p=crmPlan(q.email,q.display_name,rows.filter(r=>r.id));return [{json:{...q,ok:true,...p}}];}catch(e){return [{json:{ok:false,status:'error',request_id:q.request_id,error:'CRM_LOOKUP_ERROR'}}];}",720)
upsert=node('Crear o actualizar contacto','n8n-nodes-base.hubspot',{'authentication':'oAuth2','resource':'contact','operation':'upsert','email':'={{ $json.email }}','additionalFields':{'firstName':'={{ $json.display_name || "" }}'},'options':{}},1440,v=2.2,onError='continueRegularOutput')
ack=code('Confirmar CRM',"const p=$('Plan CRM').first().json,r=$input.first().json;return [{json:r.error||!(r.vid||r.id)?{ok:false,status:'error',request_id:p.request_id,error:'CRM_WRITE_UNCERTAIN'}:{ok:true,status:'success',request_id:p.request_id,contact_id:String(r.vid||r.id),action:p.action==='create'?'created':'updated'}}];",1680)
returned=code('Contacto existente o simulacion',"const p=$input.first().json;return [{json:p.ok?{ok:true,status:'success',request_id:p.request_id,contact_id:p.contact_id||null,action:p.mode==='dry_run'?'skipped':'found'}:{ok:false,status:'error',request_id:p.request_id,error:'CRM_LOOKUP_ERROR'}}];",1440,620)
reconcile=code('Resultado reconciliado',"const q=$('Validar CRM').first().json;try{const rows=$input.all().map(i=>i.json);if(rows.some(r=>r.error))throw Error('READ_FAILED');const p=crmPlan(q.email,'',rows.filter(r=>r.id));if(!p.contact_id)throw Error('CONTACT_NOT_FOUND');return [{json:{ok:true,status:'success',request_id:q.request_id,contact_id:p.contact_id,action:'found',reconciled:true,update_confirmed:false}}];}catch(e){return [{json:{ok:false,status:'error',request_id:q.request_id,error:'CRM_WRITE_UNCERTAIN',requires_human:true}}];}",2400,520)
save('Aurora M4 - CRM contacto',[trigger,validate,search('Buscar contacto por email',480),plan,iff('Escribir contacto','={{ $json.ok === true && $json.mode === "draft_only" && ["create","update"].includes($json.action) }}',960),upsert,ack,returned,iff('Escritura confirmada','={{ $json.ok === true }}',1920),node('CRM Result','n8n-nodes-base.noOp',{},2640),search('Reconciliar una vez',2160,520),reconcile],[('CRM Input','Validar CRM'),('Validar CRM','Buscar contacto por email'),('Buscar contacto por email','Plan CRM'),('Plan CRM','Escribir contacto'),('Escribir contacto','Crear o actualizar contacto'),('Escribir contacto','Contacto existente o simulacion',1),('Crear o actualizar contacto','Confirmar CRM'),('Confirmar CRM','Escritura confirmada'),('Escritura confirmada','CRM Result'),('Escritura confirmada','Reconciliar una vez',1),('Reconciliar una vez','Resultado reconciliado'),('Resultado reconciliado','CRM Result'),('Contacto existente o simulacion','CRM Result')],'crm_contact.json')
print('M4 CRM draft generated; credential binding, live tests, inbox/ledger and delivery pending.')

# Gmail is an inactive draft-only adapter. The M3 manager remains frozen and computes
# in dry_run mode; this adapter owns all external draft/CRM effects.
def setnode(name,fields,x,y=300):return node(name,'n8n-nodes-base.set',{'assignments':{'assignments':[{'id':k,'name':k,'value':v,'type':t} for k,(v,t) in fields.items()]},'includeOtherFields':False,'options':{}},x,y,3.4,onError='continueRegularOutput')
def execute(name,target,x):return node(name,'n8n-nodes-base.executeWorkflow',{'workflowId':{'__rl':True,'value':target,'mode':'id'},'workflowInputs':{'mappingMode':'defineBelow','value':{'request':'={{ $json.request }}'},'matchingColumns':[],'schema':[{'id':'request','displayName':'request','type':'object','required':False,'display':True,'defaultMatch':False,'canBeUsedToMatch':True}],'attemptToConvertTypes':False,'convertFieldsToString':False},'options':{'waitForSubWorkflow':True}},x,v=1.3,onError='continueRegularOutput')
COLS=['request_id','status','contact_id','draft_id','delivery_id','updated_at']
def table(name,op,x,values=None,y=300):
 p={'resource':'row','operation':op,'dataTableId':{'__rl':True,'value':'REPLACE_RECEIPT_TABLE_ID','mode':'id'}}
 if op in ['get','update']:p.update(matchType='allConditions',filters={'conditions':[{'keyName':'request_id','condition':'eq','keyValue':"={{ 'gmail:' + $('Limpiar correo').first().json.message_id }}"}]})
 if op=='get':p.update(returnAll=False,limit=2)
 else:p.update(columns={'mappingMode':'defineBelow','value':values,'matchingColumns':[],'schema':[{'id':c,'displayName':c,'type':'string','required':False,'display':True,'defaultMatch':False,'canBeUsedToMatch':True} for c in COLS],'attemptToConvertTypes':False,'convertFieldsToString':False},options={})
 return node(name,'n8n-nodes-base.dataTable',p,x,y,1.1,alwaysOutputData=True,onError='continueRegularOutput')
mailtrigger=node('Gmail Trigger','n8n-nodes-base.gmailTrigger',{'pollTimes':{'item':[{'mode':'everyMinute'}]},'simple':False,'filters':{'q':'label:AURORA_TEST -in:drafts'},'options':{'downloadAttachments':False}},0,v=1.3)
guard=iff('Correo permitido','={{ (() => {'+LIB+';return allowInbound($json);})() }}',240)
clean=setnode('Limpiar correo',{k:('={{ (() => {'+LIB+';return cleanMail($json).'+k+';})() }}','string') for k in ['From','Subject','BodyText','message_id','thread_id','display_name']},480)
stop=code('Detenido sin acciones',"return [{json:{status:'blocked',reason:'Mensaje automatico o remitente invalido',llm_calls:0}}];",720,800)
check=iff('Correo valido','={{ !$json.error && !!$json.From && !!$json.message_id && !!$json.thread_id && !!$json.BodyText }}',720)
receipt=code('Decidir recibo',"const m=$('Limpiar correo').first().json;try{const rows=$input.all().map(i=>i.json);if(rows.some(r=>r.error))throw Error('LEDGER_UNAVAILABLE');return [{json:receiptDecision('gmail:'+m.message_id,rows.filter(r=>r.id))}];}catch(e){return [{json:{action:'review',reason:'Registro de recibos no disponible'}}];}",1200)
claim=table('Reservar recibo','insert',1680,{'request_id':"={{ 'gmail:' + $('Limpiar correo').first().json.message_id }}",'status':'processing','contact_id':'','draft_id':'','delivery_id':'','updated_at':'={{ $now.toISO() }}'})
ack=code('Confirmar reserva',"const r=$input.first().json;return [{json:{ok:!r.error&&!!r.id&&r.status==='processing',receipt_id:r.id||null}}];",1920)
crmrequest="={{ {request_id:'gmail:'+$('Limpiar correo').first().json.message_id,email:$('Limpiar correo').first().json.From,display_name:$('Limpiar correo').first().json.display_name,mode:'draft_only'} }}"
request="={{ (()=>{const m=$('Limpiar correo').first().json;return {schema_version:'1',request_id:'gmail:'+m.message_id,session_id:'aurora_demo:gmail:'+m.thread_id,domain:'aurora_demo',channel:'gmail',query:m.BodyText,user:{display_name:m.display_name,email:m.From},context:{summary:null,case_status:'nuevo',key_facts:[]},evidence:[],candidate:null,correction_attempt:0,mode:'dry_run'};})() }}"
# All error/review routes stop before delivery. Receipt stays processing and requires reconciliation.
review=code('Revisar sin enviar',"const d=$input.first().json;return [{json:{status:d.action==='replay'?'completed':'needs_human',delivery:d.action==='replay'?'borrador_existente':'sin_envio',draft_id:d.draft_id||null,review:reviewPayload({request_id:'gmail:'+$('Limpiar correo').first().json.message_id,domain:'aurora_demo',status:'needs_human',reason:'Revisar recibo, CRM o respuesta antes de continuar',record_reference:null})}}];",3120,820)
draft=node('Crear borrador','n8n-nodes-base.gmail',{'resource':'draft','operation':'create','subject':"={{ $('Limpiar correo').first().json.Subject }}",'emailType':'text','message':'={{ $json.output }}','options':{'threadId':"={{ $('Limpiar correo').first().json.thread_id }}",'sendTo':"={{ $('Limpiar correo').first().json.From }}"}},4080,v=2.1,onError='continueRegularOutput')
dresult=code('Resultado borrador',"return [{json:draftResult($input.first().json)}];",4320)
update=table('Finalizar recibo','update',4560,{'status':'={{ $json.status }}','draft_id':'={{ $json.draft_id || "" }}','contact_id':"={{ $('CRM contacto').first().json.contact_id || '' }}",'updated_at':'={{ $now.toISO() }}'})
final=code('Resultado entrega',"const d=$('Resultado borrador').first().json,rows=$input.all().map(i=>i.json);const ok=rows.length===1&&!rows[0].error&&rows[0].request_id==='gmail:'+$('Limpiar correo').first().json.message_id&&rows[0].status===d.status;return [{json:{status:ok?d.status:'delivery_unknown',draft_id:d.draft_id,delivery:ok?d.delivery:'requiere_revision',external_messages_sent:0}}];",4800)
nodes=[mailtrigger,guard,clean,stop,check,table('Leer recibo','get',960),receipt,iff('Recibo nuevo','={{ $json.action === "start" }}',1440),claim,ack,iff('Reserva confirmada','={{ $json.ok === true }}',2160),setnode('Payload CRM',{'request':(crmrequest,'object')},2400),execute('CRM contacto','REPLACE_CRM_WORKFLOW_ID',2640),iff('CRM correcto','={{ $json.ok === true && $json.status === "success" && !!$json.contact_id }}',2880),setnode('Payload manager',{'request':(request,'object')},3120),execute('Manager Aurora','REPLACE_MANAGER_WORKFLOW_ID',3360),iff('Respuesta apta','={{ $json.status === "success" && typeof $json.output === "string" && $json.output.trim().length > 0 }}',3600),draft,dresult,update,final,review]
edges=[('Gmail Trigger','Correo permitido'),('Correo permitido','Limpiar correo'),('Correo permitido','Detenido sin acciones',1),('Limpiar correo','Correo valido'),('Correo valido','Leer recibo'),('Correo valido','Detenido sin acciones',1),('Leer recibo','Decidir recibo'),('Decidir recibo','Recibo nuevo'),('Recibo nuevo','Reservar recibo'),('Recibo nuevo','Revisar sin enviar',1),('Reservar recibo','Confirmar reserva'),('Confirmar reserva','Reserva confirmada'),('Reserva confirmada','Payload CRM'),('Reserva confirmada','Revisar sin enviar',1),('Payload CRM','CRM contacto'),('CRM contacto','CRM correcto'),('CRM correcto','Payload manager'),('CRM correcto','Revisar sin enviar',1),('Payload manager','Manager Aurora'),('Manager Aurora','Respuesta apta'),('Respuesta apta','Crear borrador'),('Respuesta apta','Revisar sin enviar',1),('Crear borrador','Resultado borrador'),('Resultado borrador','Finalizar recibo'),('Finalizar recibo','Resultado entrega')]
nodes += [node('Entrada de prueba','n8n-nodes-base.executeWorkflowTrigger',{'workflowInputs':{'values':[{'name':'mail','type':'object'}]}},0,600,1.1),code('Desenvolver prueba',"return [{json:$input.first().json.mail}];",120,600)]
edges += [('Entrada de prueba','Desenvolver prueba'),('Desenvolver prueba','Correo permitido')]
# Per-message worker never polls Gmail; .first() references are safe only within
# this single-item child execution, enforced by the parent's mode=each.
nodes=[n for n in nodes if n['name']!='Gmail Trigger']
edges=[e for e in edges if e[0]!='Gmail Trigger']
nodes += [iff('Necesita notificacion','={{ $json.status === "needs_human" }}',3360,820),setnode('Payload aviso',{'request':('={{ $json.review }}','object')},3600,820),execute('Notificar revision Slack','REPLACE_SLACK_REVIEW_WORKFLOW_ID',3840),code('Resultado revision',"const r=$('Revisar sin enviar').first().json,s=$input.first().json;return [{json:{...r,notification:{accepted:s.ok===true&&!s.error,delivery_id:s.message_timestamp||s.ts||s.message?.ts||null}}}];",4080,820),node('Repeticion sin notificacion','n8n-nodes-base.noOp',{},3600,1080)]
edges += [('Revisar sin enviar','Necesita notificacion'),('Necesita notificacion','Payload aviso'),('Necesita notificacion','Repeticion sin notificacion',1),('Payload aviso','Notificar revision Slack'),('Notificar revision Slack','Resultado revision')]
w=save('Aurora M4 - Procesar correo individual',nodes,edges,'gmail_message.json')
permail=execute('Procesar correo individual','REPLACE_GMAIL_MESSAGE_WORKFLOW_ID',960)
permail['parameters']['mode']='each'
permail['parameters']['workflowInputs']['value']={'mail':'={{ $json }}'}
permail['parameters']['workflowInputs']['schema'][0].update(id='mail',displayName='mail')
ingress=save('Aurora M4 - Entrada Gmail borradores',[mailtrigger,guard,clean,check,stop,permail],[('Gmail Trigger','Correo permitido'),('Correo permitido','Limpiar correo'),('Correo permitido','Detenido sin acciones',1),('Limpiar correo','Correo valido'),('Correo valido','Procesar correo individual'),('Correo valido','Detenido sin acciones',1)],'gmail_inbox.json')
# Environment binding is private; no secrets are read from the browser.
private=ROOT.parent/'work/implementation-private'
envfile=private/'module4-environment.json'
if envfile.exists():
 env=json.loads(envfile.read_text())
 for filename,workflow in [('gmail_message.json',w),('gmail_inbox.json',ingress)]:
  raw=json.dumps(workflow)
  for k,v in env['bindings'].items():raw=raw.replace(k,v)
  live=json.loads(raw)
  for n in live['nodes']:
   if n['type'] in ['n8n-nodes-base.gmail','n8n-nodes-base.gmailTrigger']:n['credentials']={'gmailOAuth2':env['gmail_credential']}
  (private/'module4-drafts'/filename).write_text(json.dumps(live,ensure_ascii=False,indent=2)+'\n')
print('M4 Gmail draft generated; inactive, no send node, live ledger/draft tests pending.')

# User-authorized educational review notices go only to the verified operator.
# Incoming data cannot choose a destination or carry email bodies/attachments.
slack_input=node('Solicitud revision','n8n-nodes-base.executeWorkflowTrigger',{'workflowInputs':{'values':[{'name':'request','type':'object'}]}},0,v=1.1)
minimal=setnode('Payload minimo',{k:('={{ (()=>{'+LIB+';return reviewPayload($json.request).'+k+';})() }}','string') for k in ['request_id','domain','status','reason','record_reference']},240)
slack=node('Slack revision','n8n-nodes-base.slack',{'authentication':'oAuth2','resource':'message','operation':'post','select':'user','user':{'__rl':True,'value':'REPLACE_SLACK_REVIEW_USER_ID','mode':'id'},'messageType':'text','text':'={{ JSON.stringify($json) }}','otherOptions':{'includeLinkToWorkflow':False}},720,v=2.3,onError='continueRegularOutput')
sw=save('Aurora M4 - Revision Slack preparada',[slack_input,minimal,iff('Envio autorizado',"={{ $json.status === 'needs_human' && $json.domain === 'aurora_demo' && /^gmail:[a-zA-Z0-9:_-]{1,100}$/.test($json.request_id) }}",480),slack,node('Revision preparada sin enviar','n8n-nodes-base.noOp',{},720,600)],[('Solicitud revision','Payload minimo'),('Payload minimo','Envio autorizado'),('Envio autorizado','Slack revision'),('Envio autorizado','Revision preparada sin enviar',1)],'slack_review.json')
if envfile.exists():
 live=json.loads(json.dumps(sw).replace('REPLACE_SLACK_REVIEW_USER_ID','U0BMT2H2BGW'))
 for n in live['nodes']:
  if n['type']=='n8n-nodes-base.slack':n['credentials']={'slackOAuth2Api':{'id':'qI9voByN5D15txqB','name':'Slack account'}}
 (private/'module4-drafts/slack_review.json').write_text(json.dumps(live,ensure_ascii=False,indent=2)+'\n')

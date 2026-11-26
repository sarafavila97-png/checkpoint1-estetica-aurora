"""Generate M3 drafts privately. Hosted exports remain authoritative."""
import copy,json,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'work/implementation-private/module3-drafts'
ENV=json.loads((OUT.parent/'module3-environment.json').read_text())
LIB=(ROOT/'src/memory.js').read_text().split('module.exports=')[0]
FIELDS=['Session_ID','Fecha de actualización','Resumen consolidado','Estado del caso','Datos clave']
SETTINGS=json.loads((ROOT/'workflows/aurora_manager.json').read_text())['settings']
def node(name,typ,p,x,y=300,v=1,**extra):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'aurora-m3:'+name)),name=name,type=typ,typeVersion=v,position=[x,y],parameters=p,**extra)
def code(name,body,x,y=300):return node(name,'n8n-nodes-base.code',{'jsCode':LIB+'\n'+body},x,y,2)
def trigger(inputs):return node('Memory Input','n8n-nodes-base.executeWorkflowTrigger',{'inputSource':'workflowInputs','workflowInputs':{'values':[{'name':n,'type':t} for n,t in inputs]}},0,v=1.1)
def airtable(name,op,x,values=None):
 p={'authentication':'airtableOAuth2Api','resource':'record','operation':op,'base':{'__rl':True,'value':ENV['base_id'],'mode':'id'},'table':{'__rl':True,'value':ENV['table_id'],'mode':'id'},'options':{}}
 if op=='search':p.update(filterByFormula='={{ $json.filter }}',returnAll=False,limit=2,options={'fields':FIELDS})
 else:p['columns']={'mappingMode':'defineBelow','value':values,'matchingColumns':['id'] if op=='update' else [],'schema':[{'id':f,'displayName':f,'type':'string','required':False,'display':True,'defaultMatch':False,'canBeUsedToMatch':True} for f in (['id'] if op=='update' else [])+FIELDS],'attemptToConvertTypes':False,'convertFieldsToString':False}
 return node(name,'n8n-nodes-base.airtable',p,x,v=2.1,credentials={'airtableOAuth2Api':{'id':ENV['credential_id'],'name':'Aurora Airtable'}},alwaysOutputData=True,onError='continueRegularOutput')
def iff(name,expr,x):return node(name,'n8n-nodes-base.if',{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':2},'conditions':[{'id':name,'leftValue':expr,'rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}},x,v=2.2)
def save(name,nodes,edges,file):
 branch='Sesion nueva' if file=='memory_read.json' else 'Escritura validada'
 nodes.append(node('No Operation, do nothing','n8n-nodes-base.noOp',{},1120,600))
 edges.append((branch,'No Operation, do nothing',1))
 w={'name':name,'nodes':nodes,'connections':{},'settings':SETTINGS,'active':False,'pinData':{}}
 for a,b,*o in edges:
  out=o[0] if o else 0;ports=w['connections'].setdefault(a,{}).setdefault('main',[])
  while len(ports)<=out:ports.append([])
  ports[out].append({'node':b,'type':'main','index':0})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/file).write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
 public=copy.deepcopy(w)
 for n in public['nodes']:
  n.pop('credentials',None)
  if n['type']=='n8n-nodes-base.airtable':
   n['parameters']['base']['value']='REPLACE_AIRTABLE_BASE_ID'
   n['parameters']['table']['value']='REPLACE_MEMORY_TABLE_ID'
 draft=ROOT/'drafts/module3';draft.mkdir(parents=True,exist_ok=True)
 (draft/file).write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
request="const q=$('Validar sesion').first().json.request;"
prepare=code('Validar sesion',"const q=$input.first().json.request; session(q.session_id); if(!q.session_id.startsWith(q.domain+':'+q.channel+':'))throw Error('session mismatch');return [{json:{request:q,filter:sessionFilter(q.session_id)}}];",220)
normalize=code('Validar lectura',request+"try{const items=$input.all().map(i=>i.json);if(items.some(i=>i.error))throw Error('AIRTABLE_UNAVAILABLE');const rows=items.filter(i=>i.id).map(i=>({id:i.id,fields:i.fields||Object.fromEntries(FIELDS.filter(k=>k in i).map(k=>[k,i[k]]))})); for(const r of rows){r.fields['Resumen consolidado']??='';} const memory=readSession(q.session_id,rows);return [{json:{ok:true,request:{...q,context:memory.context},memory}}];}catch(e){return [{json:{ok:false,request:q,error:{code:'MEMORY_READ_ERROR',message:'No se pudo recuperar memoria aislada'}}}];}",680)
# Airtable omits empty fields; defaults only for the intentionally empty summary.
new=code('Preparar alta',"const d=$input.first().json;return [{json:{...d,fields:newRecord(d.request.session_id,d.request.user.display_name)}}];",1120)
create=airtable('Crear sesion','create',1340,{f:'={{ $json.fields['+json.dumps(f,ensure_ascii=False)+'] }}' for f in FIELDS})
created=code('Confirmar alta',"const d=$('Preparar alta').first().json,r=$input.first().json;if(r.error||!r.id)return [{json:{ok:false,request:d.request,error:{code:'MEMORY_CREATE_ERROR',message:'Alta no confirmada; reconciliar antes de reintentar'}}}];return [{json:{ok:true,request:d.request,memory:{branch:'new',record_id:r.id,fields:d.fields,context:d.request.context}}}];",1560)
# Error and existing branches preserve the typed read result and do not write.
newif=iff('Sesion nueva','={{ $json.ok === true && $json.memory.branch === "new" }}',900)
save('Aurora M3 - Memoria leer',[trigger([('request','object')]),prepare,airtable('Buscar Session_ID','search',440),normalize,newif,new,create,created],[('Memory Input','Validar sesion'),('Validar sesion','Buscar Session_ID'),('Buscar Session_ID','Validar lectura'),('Validar lectura','Sesion nueva'),('Sesion nueva','Preparar alta'),('Preparar alta','Crear sesion'),('Crear sesion','Confirmar alta')],'memory_read.json')
# Update searches again; record_id is never accepted from an arbitrary caller.
wprep=code('Validar escritura',"const d=$input.first().json; session(d.request.session_id);if(!d.request.session_id.startsWith(d.request.domain+':'+d.request.channel+':'))throw Error('session mismatch');return [{json:{...d,filter:sessionFilter(d.request.session_id)}}];",220)
plan=code('Planificar escritura',"const d=$('Validar escritura').first().json;try{const items=$input.all().map(i=>i.json);if(items.some(i=>i.error))throw Error('AIRTABLE_UNAVAILABLE');const rows=items.filter(i=>i.id).map(i=>({id:i.id,fields:i.fields||Object.fromEntries(FIELDS.filter(k=>k in i).map(k=>[k,i[k]]))}));for(const r of rows)r.fields['Resumen consolidado']??='';const state=readSession(d.request.session_id,rows);if(state.branch!=='existing')throw Error('memory missing');const p=acceptMessage(state.fields,d.request.request_id,d.summary??null);return [{json:{ok:true,request_id:d.request.request_id,record_id:state.record_id,...p}}];}catch(e){return [{json:{ok:false,write:false,request_id:d.request.request_id,error:{code:'MEMORY_WRITE_ERROR',message:'Memoria no actualizada; revisar entrada o dependencia'}}}];}",680)
update=airtable('Actualizar resumen validado','update',1120,{'id':'={{ $json.record_id }}',**{f:'={{ $json.fields['+json.dumps(f,ensure_ascii=False)+'] }}' for f in FIELDS}})
confirm=code('Confirmar escritura',"const p=$('Planificar escritura').first().json,r=$input.first().json;return [{json:r.error||r.id!==p.record_id?{ok:false,request_id:p.request_id,error:{code:'MEMORY_WRITE_ERROR',message:'Actualizacion no confirmada'}}:{ok:true,request_id:p.request_id,record_id:r.id,fields:p.fields,updated:true}}];",1340)
save('Aurora M3 - Memoria escribir',[trigger([('request','object'),('summary','object')]),wprep,airtable('Releer Session_ID','search',440),plan,iff('Escritura validada','={{ $json.ok === true && $json.write === true }}',900),update,confirm],[('Memory Input','Validar escritura'),('Validar escritura','Releer Session_ID'),('Releer Session_ID','Planificar escritura'),('Planificar escritura','Escritura validada'),('Escritura validada','Actualizar resumen validado'),('Actualizar resumen validado','Confirmar escritura')],'memory_write.json')
print('M3 private drafts generated; hosted import, settings, tests and manager integration pending.')

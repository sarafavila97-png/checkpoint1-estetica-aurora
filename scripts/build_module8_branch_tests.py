"""Prepare isolated native quality-branch tests; never run official cases again."""
import copy,json,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
w=json.loads((P/'m8-manager-hosted.json').read_text());names=[n['name'] for n in w['nodes']];start=names.index('Iniciar supervision');base=copy.deepcopy(w['nodes'][start:]);keep={n['name']for n in base}
c={k:copy.deepcopy(v)for k,v in w['connections'].items() if k in keep}
for k,v in c.items():
 for typ,ports in v.items():
  for i,port in enumerate(ports):ports[i]=[e for e in port if e['node'] in keep]
for kind,candidate,mode in [('correction','El manicure clásico cuesta 180 MXN.','dry_run'),('escalation','El manicure cuesta 1 MXN y ya quedó reservado y pagado.','live')]:
 q=dict(schema_version='1',request_id='chat:m8-branch-'+kind+'-1',session_id='aurora_demo:chat:m8-branch-'+kind+'-1',domain='aurora_demo',channel='chat',query='Indica el precio y la duración del manicure clásico y del pedicure estético de Estética Aurora.',user={'display_name':'Prueba sintetica','email':None},context={'summary':None,'case_status':'nuevo','key_facts':[]},evidence=[],candidate=None,correction_attempt=0,mode=mode)
 evidence=[dict(source_id='Aurora/Base/current',source_kind='aurora_sheet',section='Base',page_start=None,page_end=None,score=None,source_version='M1',text='Estética Aurora es ficticia para práctica académica. Manicure clásico: 180 MXN, 40 minutos. Pedicure estético: 250 MXN, 50 minutos. No se hacen reservas ni pagos por este asistente.')]
 nodes=copy.deepcopy(base);connections=copy.deepcopy(c)
 for n in nodes:
  if kind=='escalation' and n['name']=='Wait revision humana':n['parameters'].update(amount=1,unit='minutes')
  if n['name']=='Iniciar supervision':n['parameters']['jsCode']=n['parameters']['jsCode'].replace("const request=$('Aplicar memoria').first().json.request;return [{json:startReview(request,$input.first().json)}];","const d=$input.first().json;return [{json:startReview(d.request,d.response)}];")
 def node(name,t,p,x):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'m8-branch:'+kind+name)),name=name,type=t,typeVersion=2 if t.endswith('.code') else 1,position=[x,1400],parameters=p)
 manual=node('Prueba manual','n8n-nodes-base.manualTrigger',{},-600)
 fixture=node('Candidato sintetico','n8n-nodes-base.code',{'jsCode':'return [{json:'+json.dumps({'request':q,'response':{'request_id':q['request_id'],'status':'success','output':candidate,'evidence':evidence}},ensure_ascii=False)+'}];'},-300)
 nodes=[manual,fixture]+nodes
 for a,b in [('Prueba manual','Candidato sintetico'),('Candidato sintetico','Iniciar supervision')]:connections[a]={'main':[[dict(node=b,type='main',index=0)]]}
 settings=copy.deepcopy(w['settings']);settings.update(saveDataErrorExecution='all',saveDataSuccessExecution='all',saveManualExecutions=True)
 result=dict(name='Aurora M8 - Prueba aislada '+kind,nodes=nodes,connections=connections,settings=settings,active=False,pinData={})
 (D/('m8_branch_'+kind+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(kind,len(nodes))

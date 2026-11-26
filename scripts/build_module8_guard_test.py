"""Native graph integration with explicitly injected judge/rewrite fixtures; zero model calls."""
import json,copy,uuid,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
base=json.loads((D/'m8_branch_correction.json').read_text());nodes=[];connections={}
def edge(a,b,index=0):connections.setdefault(a,{'main':[[]]})['main'][0].append(dict(node=b,type='main',index=index))
for case in ['exhaustion','malformed']:
 w=copy.deepcopy(base);prefix=case+' / '
 for n in w['nodes']:
  if n['name'].startswith('Supervisor '):
   judge={'exactitud_factual':3,'estado_veredicto':'CORREGIR'} if case=='exhaustion' else {'exactitud_factual':'5','estado_veredicto':'APROBADO','extra':'invalid'}
   n.update(type='n8n-nodes-base.code',typeVersion=2,parameters={'jsCode':"const q=$input.first().json.request;return [{json:{request_id:q.request_id,domain:q.domain,channel:q.channel,candidate:q.candidate,judge:"+json.dumps(judge)+"}}];"});n.pop('credentials',None)
  if n['name'].startswith('Corregir '):n.update(type='n8n-nodes-base.code',typeVersion=2,parameters={'jsCode':"return [{json:{text:'Respuesta sintética reescrita para verificar el límite de dos correcciones.'}}];"})
  if n['name']=='Candidato sintetico':n['parameters']['jsCode']=n['parameters']['jsCode'].replace('chat:m8-branch-correction-1','chat:m8-guard-'+case+'-1')
 remove={n['name'] for n in w['nodes'] if n['name']=='Prueba manual' or n['name'].startswith('Modelo Corregir ')}
 for n in w['nodes']:
  if n['name'] in remove:continue
  raw=json.dumps(n,ensure_ascii=False)
  for old in [x['name'] for x in w['nodes']]:raw=raw.replace("$('"+old+"')","$('"+prefix+old+"')")
  n=json.loads(raw);n['name']=prefix+n['name'];n['id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'m8-guard:'+n['name']));n['position'][1]+=0 if case=='exhaustion' else 4000;nodes.append(n)
 for src,types in w['connections'].items():
  if src in remove:continue
  for typ,ports in types.items():
   connections.setdefault(prefix+src,{})[typ]=[[dict(e,node=prefix+e['node'])for e in port if e['node'] not in remove]for port in ports]
 edge('Prueba manual',prefix+'Candidato sintetico')
 for end in ['Respuesta aprobada M8','Revision pendiente sin entrega']:edge(prefix+end,'Unir resultados',0 if case=='exhaustion' else 1)
nodes.insert(0,dict(id='guard-manual',name='Prueba manual',type='n8n-nodes-base.manualTrigger',typeVersion=1,position=[-900,1400],parameters={}))
nodes.append(dict(id='guard-merge',name='Unir resultados',type='n8n-nodes-base.merge',typeVersion=3,position=[5000,4000],parameters={'mode':'append','numberInputs':2}))
code="const rows=$input.all().map(i=>i.json);const e=rows.find(r=>r.request_id.includes('exhaustion')),m=rows.find(r=>r.request_id.includes('malformed'));if(rows.length!==2||e.status!=='needs_human'||e.quality.attempt!==2||e.quality.history.length!==3||m.status!=='needs_human'||m.quality.attempt!==0)throw Error('GUARD_ASSERTION_FAILED');return [{json:{status:'PASS',test_scope:'Injected judge/rewrite fixtures through real native state transitions and Switch nodes; zero model/provider calls',results:rows,model_calls:0,external_notifications:0}}];"
nodes.append(dict(id='guard-assert',name='Verificar limites',type='n8n-nodes-base.code',typeVersion=2,position=[5300,4000],parameters={'jsCode':code}));edge('Unir resultados','Verificar limites')
w=dict(name='Aurora M8 - Guardas con decisiones inyectadas',nodes=nodes,connections=connections,settings=base['settings'],active=False,pinData={})
(D/'m8_guard_test.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n');print(len(nodes),'nodes')

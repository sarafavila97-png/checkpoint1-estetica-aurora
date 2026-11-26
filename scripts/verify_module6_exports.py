"""Compare live audio configuration with source; normalize documented defaults only."""
import argparse,copy,hashlib,json,re
from pathlib import Path
from verify_module5_exports import params as base_params
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private'
PAIRS=[('m6-transcribe-hosted.json','voice_transcribe.json'),('m6-delivery-hosted.json','telegram_delivery.json'),('m6-aurora-hosted.json','aurora_knowledge.json'),('m6-outer-hosted.json','outer_agent_knowledge.json'),('m6-manager-hosted.json','aurora_manager.json'),('m6-ingress-hosted.json','telegram_voice.json')]
def sanitized_host(host,bindings):
 for n in host['nodes']:
  unresolved=re.findall(r'REPLACE_[A-Z0-9_]+',json.dumps(n['parameters']))
  assert not unresolved,('unresolved live binding',n['name'],sorted(set(unresolved)))
 w={k:copy.deepcopy(host[k]) for k in ['name','nodes','connections','settings']};w.update(active=False,pinData={})
 for n in w['nodes']:n.pop('credentials',None)
 raw=json.dumps(w)
 for k,v in bindings.items():raw=raw.replace(v,k)
 return json.loads(raw)
def params(n):
 p=base_params(n)
 if n['type']=='n8n-nodes-base.dataTable':
  p.setdefault('resource','row');p.setdefault('operation','insert')
  if p['operation']=='get':p.setdefault('returnAll',False)
  for c in p.get('filters',{}).get('conditions',[]):c.setdefault('condition','eq')
 if n['type']=='n8n-nodes-base.telegram':
  p.setdefault('resource','message')
  if p['resource']=='file':p.setdefault('operation','get');p.setdefault('download',True)
  if p.get('binaryData'):p.setdefault('binaryPropertyName','data')
 if n['type']=='@n8n/n8n-nodes-langchain.openAi' and p.get('resource')=='audio':p.setdefault('binaryPropertyName','data')
 return p
def verify(adopt=False,available=False):
 env=json.loads((P/'module6-environment.json').read_text());manifest=[]
 for src,dst in PAIRS:
  if available and not (P/src).exists():continue
  host=json.loads((P/src).read_text());draft=json.loads((R/'drafts/module6'/dst).read_text())
  w=sanitized_host(host,env['bindings']);a={n['name']:n for n in w['nodes']};b={n['name']:n for n in draft['nodes']}
  assert a.keys()==b.keys(),dst;assert w['connections']==draft['connections'],(dst,'graph')
  for name,n in a.items():
   assert n['type']==b[name]['type'] and n['typeVersion']==b[name]['typeVersion'],(dst,name,'type')
   assert params(n)==params(b[name]),(dst,name,'parameters',params(n),params(b[name]))
   assert n.get('onError')==b[name].get('onError'),(dst,name,'error policy')
  s=w['settings'];assert s['executionTimeout']==180 and s['saveDataErrorExecution']=='none' and s['saveDataSuccessExecution']=='none' and s['saveManualExecutions'] is False and s['saveExecutionProgress'] is False and s['callerPolicy']=='workflowsFromSameOwner' and s['availableInMCP'] is False
  assert not host.get('active') and not host.get('pinData')
  out=R/'workflows/module6'/dst
  if adopt:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
  assert json.loads(out.read_text())==w
  manifest.append({'file':'workflows/module6/'+dst,'hosted_id':host['id'],'nodes':len(a),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'verification':'exact sanitized hosted snapshot with documented native-default equivalence'})
  print('PASS',dst,len(a),'nodes')
 if not available:
  out=R/'evidence/module6/hosted-export-manifest.json'
  if adopt:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(manifest,indent=2)+'\n')
  assert json.loads(out.read_text())==manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--adopt',action='store_true');p.add_argument('--available',action='store_true');a=p.parse_args();verify(a.adopt,a.available)

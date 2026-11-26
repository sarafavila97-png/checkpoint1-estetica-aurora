"""Verify score-preserving M5 adaptation against actual hosted exports."""
import argparse,copy,hashlib,json
from pathlib import Path
from verify_module3_exports import normalized_params
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent/'work/implementation-private'
PAIRS=[('m5-retrieval-hosted.json','outer_agent_retrieval.json'),('m5-agent-hosted.json','outer_agent_knowledge.json'),('m5-manager-hosted.json','aurora_manager.json')]
def clean(host):
 w={k:copy.deepcopy(host[k]) for k in ['name','nodes','connections','settings']};w.update(active=False,pinData={})
 for n in w['nodes']:n.pop('credentials',None)
 raw=json.dumps(w)
 for k,v in json.loads((P/'module5-environment.json').read_text())['bindings'].items():raw=raw.replace(v,k)
 return json.loads(raw)
def params(n):
 p=normalized_params(n)
 if n['type']=='@n8n/n8n-nodes-langchain.toolWorkflow':p.setdefault('source','database')
 if n['type']=='n8n-nodes-base.set':p.setdefault('includeOtherFields',False)
 if n['type']=='n8n-nodes-base.httpRequest':p.setdefault('sendHeaders',False)
 return p
def verify(adopt):
 manifest=[]
 for private,f in PAIRS:
  host=json.loads((P/private).read_text());w=clean(host);draft=json.loads((ROOT/'drafts/module5'/f).read_text());a={n['name']:n for n in w['nodes']};b={n['name']:n for n in draft['nodes']}
  assert a.keys()==b.keys(),f;assert w['connections']==draft['connections'],(f,'graph')
  for name,n in a.items():
   assert n['type']==b[name]['type'] and n['typeVersion']==b[name]['typeVersion'],(f,name,'type')
   assert params(n)==params(b[name]),(f,name,'parameters')
   assert n.get('onError')==b[name].get('onError'),(f,name,'error policy')
  s=w['settings'];assert s['executionTimeout']==180 and s['saveDataErrorExecution']=='none' and s['saveDataSuccessExecution']=='none' and s['saveManualExecutions'] is False and s['callerPolicy']=='workflowsFromSameOwner' and s['availableInMCP'] is False
  assert not host.get('active') and not host.get('pinData')
  out=ROOT/'workflows/module5'/f
  if adopt:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
  assert json.loads(out.read_text())==w
  manifest.append({'file':'workflows/module5/'+f,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'hosted_id':host['id'],'nodes':len(a),'verification':'exact sanitized hosted snapshot; draft parameter equivalence after documented native default normalization'})
  print('PASS',f,len(a),'nodes')
 out=ROOT/'evidence/module5/hosted-export-manifest.json'
 if adopt:out.write_text(json.dumps(manifest,indent=2)+'\n')
 assert json.loads(out.read_text())==manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--adopt',action='store_true');verify(p.parse_args().adopt)

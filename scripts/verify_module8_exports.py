"""Verify M8 hosted snapshots; only documented native defaults normalize."""
import json,copy,hashlib
from pathlib import Path
from verify_module6_exports import params as base_params,sanitized_host
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private'
def params(n):
 p=base_params(n)
 # n8n editor materializes mapper UI metadata; defineBelow executes value, not matchingColumns.
 if n['type']=='n8n-nodes-base.executeWorkflow' and p.get('workflowInputs',{}).get('mappingMode')=='defineBelow':
  m=p['workflowInputs'];m.pop('matchingColumns',None)
  for f in m.get('schema',[]):
   f.setdefault('defaultMatch',False);f.setdefault('removed',False)
 if n['type']=='n8n-nodes-base.wait':p.setdefault('resume','timeInterval')
 if n['type']=='n8n-nodes-base.gmail':p.setdefault('operation','create');p.setdefault('emailType','text')
 if n['type']=='n8n-nodes-base.executeWorkflowTrigger':
  for field in p.get('workflowInputs',{}).get('values',[]):field.setdefault('type','string')
 return p
def verify(available=False):
 env=json.loads((P/'module8-environment.json').read_text());manifest=[]
 for src,file in [('m8-supervisor-hosted.json','supervisor.json'),('m8-manager-hosted.json','aurora_manager.json'),('m8-delivery-hosted.json','telegram_delivery.json'),('m8-message-hosted.json','gmail_message.json'),('m8-inbox-hosted.json','gmail_inbox.json'),('m8-ingress-hosted.json','telegram_voice.json')]:
  if available and not (P/src).exists():continue
  h=json.loads((P/src).read_text());w=sanitized_host(h,env['bindings']);d=json.loads((R/'drafts/module8'/file).read_text())
  a={n['name']:n for n in w['nodes']};b={n['name']:n for n in d['nodes']};assert a.keys()==b.keys();assert w['connections']==d['connections']
  for name,n in a.items():
   assert params(n)==params(b[name]),(file,name,params(n),params(b[name]))
   assert (n['type'],n['typeVersion'],n.get('onError'))==(b[name]['type'],b[name]['typeVersion'],b[name].get('onError'))
  s=h['settings'];assert s['executionTimeout']==(300 if file=='aurora_manager.json' else 180)
  assert s['saveDataErrorExecution']=='none' and s['saveDataSuccessExecution']=='none' and s['saveManualExecutions'] is False and s['saveExecutionProgress'] is False and s['callerPolicy']=='workflowsFromSameOwner' and s['availableInMCP'] is False
  assert not h.get('active') and not h.get('pinData')
  out=R/'workflows/module8'/file;out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
  manifest.append(dict(file='workflows/module8/'+file,hosted_id=h['id'],nodes=len(a),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),verified=True));print('PASS',file,len(a),'nodes')
 out=R/'evidence/module8';out.mkdir(exist_ok=True);(out/'hosted-export-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--available',action='store_true');verify(parser.parse_args().available)

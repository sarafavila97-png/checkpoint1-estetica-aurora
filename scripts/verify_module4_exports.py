"""Freeze sanitized hosted M4 snapshots; verify graph, parameters and privacy."""
import argparse,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT.parent/'work/implementation-private'
PAIRS=[('m4-crm-first-export.json','crm_contact.json'),('m4-message-integrated.json','gmail_message.json'),('m4-ingress-hosted-verified.json','gmail_inbox.json'),('m4-slack-hosted-verified.json','slack_review.json')]
def sanitized(host):
 w={k:copy.deepcopy(host[k]) for k in ['name','nodes','connections','settings']};w.update(active=False,pinData={})
 env=json.loads((PRIVATE/'module4-environment.json').read_text())
 for n in w['nodes']:n.pop('credentials',None)
 raw=json.dumps(w)
 for placeholder,value in env['bindings'].items():raw=raw.replace(value,placeholder)
 raw=raw.replace('U0BMT2H2BGW','REPLACE_SLACK_REVIEW_USER_ID')
 return json.loads(raw)
def params(n,crm=False):
 p=copy.deepcopy(n['parameters']);t=n['type']
 if t=='n8n-nodes-base.set':p.setdefault('includeOtherFields',False)
 if t=='n8n-nodes-base.executeWorkflowTrigger':p.setdefault('inputSource','workflowInputs')
 if t=='n8n-nodes-base.executeWorkflow':p.setdefault('source','database')
 if t=='n8n-nodes-base.hubspot':
  p.setdefault('resource','contact');p.setdefault('operation','upsert')
  if p['operation']=='search':
   p.setdefault('returnAll',False)
   for g in p['filterGroupsUi']['filterGroupsValues']:
    for f in g['filtersUi']['filterValues']:f.setdefault('operator','EQ')
 if t=='n8n-nodes-base.dataTable':
  p.setdefault('resource','row');p.setdefault('operation','insert')
  if p['operation']=='get':p.setdefault('returnAll',False)
  for c in p.get('filters',{}).get('conditions',[]):c.setdefault('condition','eq')
 if t=='n8n-nodes-base.gmail':p.setdefault('operation','create');p.setdefault('emailType','text')
 if t=='n8n-nodes-base.slack':
  p.setdefault('resource','message');p.setdefault('operation','post');p.setdefault('messageType','text')
 # The CRM snapshot embeds an earlier, unused cleanMail helper. CRM only calls
 # parseSender/crmPlan; canonical snapshot retains exact hosted code.
 if crm and 'jsCode' in p:p['jsCode']=p['jsCode'].replace("display_name:sender.name||String(m.display_name||'').slice(0,100)","display_name:sender.name")
 return p
def verify(adopt=False):
 manifest=[]
 for private,filename in PAIRS:
  host=json.loads((PRIVATE/private).read_text());clean=sanitized(host);draft=json.loads((ROOT/'drafts/module4'/filename).read_text())
  actual={n['name']:n for n in clean['nodes']};expected={n['name']:n for n in draft['nodes']}
  assert actual.keys()==expected.keys(),filename+': nodes'
  assert clean['connections']==draft['connections'],filename+': graph'
  for name,a in actual.items():
   b=expected[name];assert a['type']==b['type'] and a['typeVersion']==b['typeVersion'],(filename,name,'type')
   assert params(a,filename=='crm_contact.json')==params(b,filename=='crm_contact.json'),(filename,name,'parameters')
   assert a.get('onError')==b.get('onError'),(filename,name,'error policy')
  s=clean['settings'];assert s['executionTimeout']==180 and s['saveDataErrorExecution']=='none' and s['saveDataSuccessExecution']=='none' and s['saveManualExecutions'] is False
  assert s['callerPolicy']=='workflowsFromSameOwner' and s['availableInMCP'] is False
  assert not host.get('active') and not host.get('pinData')
  out=ROOT/'workflows/module4'/filename
  if adopt:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(clean,ensure_ascii=False,indent=2)+'\n')
  assert json.loads(out.read_text())==clean
  manifest.append({'file':'workflows/module4/'+filename,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'nodes':len(actual),'hosted_id':host['id'],'verification':'Exact sanitized hosted snapshot; generated parameters equivalent under documented default/dead-helper normalization'})
  print('PASS',filename,len(actual),'nodes, hosted parity and privacy')
 p=ROOT/'evidence/module4/hosted-export-manifest.json'
 if adopt:p.write_text(json.dumps(manifest,indent=2)+'\n')
 assert json.loads(p.read_text())==manifest
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--adopt',action='store_true');verify(parser.parse_args().adopt)

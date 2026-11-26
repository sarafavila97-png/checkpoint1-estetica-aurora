"""Adopt/verify sanitized M3 hosted exports, keeping generated drafts distinct."""
import argparse,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT.parent/'work/implementation-private'
PAIRS=[('m3-manager-hosted-verified.json','aurora_manager.json','aurora_manager.json'),('m3-knowledge-hosted-corrected.json','workers/aurora_knowledge.json','aurora_knowledge.json'),('m3-read-hosted-verified.json','workers/memory_read.json','memory_read.json'),('m3-write-hosted-verified.json','workers/memory_write.json','memory_write.json')]
def sanitized(host):
 w={k:copy.deepcopy(host[k]) for k in ['name','nodes','connections','settings']};w.update(active=False,pinData={})
 for n in w['nodes']:
  n.pop('credentials',None)
  if n['type']=='n8n-nodes-base.googleSheetsTool':n['parameters']['documentId']['value']='REPLACE_AURORA_SHEET_ID'
  if n['type']=='n8n-nodes-base.airtable':
   n['parameters']['base']['value']='REPLACE_AIRTABLE_BASE_ID';n['parameters']['table']['value']='REPLACE_MEMORY_TABLE_ID'
 return w
def normalized_params(n):
 p=copy.deepcopy(n['parameters']);t=n['type']
 if t=='@n8n/n8n-nodes-langchain.chainLlm':p.setdefault('batching',{})
 if t=='n8n-nodes-base.executeWorkflowTrigger':p.setdefault('inputSource','workflowInputs')
 if t=='n8n-nodes-base.executeWorkflow':p.setdefault('source','database')
 if t=='n8n-nodes-base.airtable':p.setdefault('resource','record')
 if t=='@n8n/n8n-nodes-langchain.memoryManager':
  p.setdefault('mode','load')
  if p['mode']=='insert':
   p.setdefault('insertMode','insert')
   for m in p.get('messages',{}).get('messageValues',[]):m.setdefault('hideFromUI',False)
  if p['mode']=='load':p.setdefault('simplifyOutput',True)
 return p
def verify(adopt=False):
 manifest=[]
 for private,public,draft in PAIRS:
  host=json.loads((PRIVATE/private).read_text());clean=sanitized(host);generated=json.loads((ROOT/'drafts/module3'/draft).read_text())
  actual={n['name']:n for n in clean['nodes']};expected={n['name']:n for n in generated['nodes']}
  assert actual.keys()==expected.keys(),public+': node names'
  assert clean['connections']==generated['connections'],public+': graph'
  for name in actual:
   a,b=actual[name],expected[name]
   assert a['type']==b['type'] and a['typeVersion']==b['typeVersion'],(public,name,'type')
   assert normalized_params(a)==normalized_params(b),(public,name,'parameters')
   assert a.get('onError')==b.get('onError'),(public,name,'error policy')
  settings=clean['settings'];assert settings['executionTimeout']==180
  assert settings['saveDataErrorExecution']=='none' and settings['saveDataSuccessExecution']=='none' and settings['saveManualExecutions'] is False
  assert settings.get('saveExecutionProgress',False) is False
  assert settings['callerPolicy']=='workflowsFromSameOwner' and settings['availableInMCP'] is False
  assert not host.get('pinData') and not host.get('active')
  for n in actual.values():
   if n['type']=='n8n-nodes-base.executeWorkflow':
    assert n['parameters']['workflowInputs']['value']['request']=='={{ $json.request }}'
    assert n['parameters']['options']['waitForSubWorkflow'] is True
  path=ROOT/'workflows'/public
  if adopt:
   path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(clean,ensure_ascii=False,indent=2)+'\n')
  assert json.loads(path.read_text())==clean,public+': exact hosted parity'
  manifest.append({'file':public,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nodes':len(actual),'hosted_id':host['id'],'verification':'exact sanitized hosted snapshot; draft parameters equivalent after documented n8n default omission normalization'})
  print('PASS',public,len(actual),'nodes, hosted parity, draft equivalence, privacy and wait settings')
 p=ROOT/'evidence/module3/hosted-export-manifest.json'
 if adopt:p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 assert json.loads(p.read_text())==manifest
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--adopt',action='store_true');verify(parser.parse_args().adopt)

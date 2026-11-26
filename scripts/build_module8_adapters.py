"""Evolve adapters to the quality gate without changing historical checkpoints."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for source,target,name,replacements in [
 ('module4/gmail_message.json','gmail_message.json','Aurora M8 - Correo con control factual',{'REPLACE_MANAGER_WORKFLOW_ID':'REPLACE_QUALITY_MANAGER_WORKFLOW_ID'}),
 ('module4/gmail_inbox.json','gmail_inbox.json','Aurora M8 - Entrada Gmail inactiva',{'REPLACE_GMAIL_MESSAGE_WORKFLOW_ID':'REPLACE_QUALITY_GMAIL_MESSAGE_WORKFLOW_ID'}),
 ('module6/telegram_voice.json','telegram_voice.json','Aurora M8 - Entrada Telegram supervisada',{'REPLACE_CURRENT_MANAGER_WORKFLOW_ID':'REPLACE_QUALITY_MANAGER_WORKFLOW_ID','REPLACE_TELEGRAM_DELIVERY_WORKFLOW_ID':'REPLACE_APPROVED_DELIVERY_WORKFLOW_ID'}),
]:
 text=(R/'drafts'/source).read_text()
 for old,new in replacements.items():text=text.replace(old,new)
 w=json.loads(text);w['name']=name;w['active']=False;w['pinData']={}
 if target=='gmail_message.json':
  # Manager only evaluates; this adapter owns exactly one notice and the review pause.
  w['nodes'].append(dict(id='m8-gmail-review-wait',name='Wait revision Gmail',type='n8n-nodes-base.wait',typeVersion=1.1,position=[3840,820],parameters={'resume':'timeInterval','amount':24,'unit':'hours'}))
  w['connections']['Notificar revision Slack']={'main':[[dict(node='Wait revision Gmail',type='main',index=0)]]}
  w['connections']['Wait revision Gmail']={'main':[[dict(node='Resultado revision',type='main',index=0)]]}
  # Read the notification result explicitly after resume, not the Wait item's payload.
  result=next(n for n in w['nodes'] if n['name']=='Resultado revision')
  result['parameters']['jsCode']=result['parameters']['jsCode'].replace("s=$input.first().json", "s=$('Notificar revision Slack').first().json")
 (R/'drafts/module8'/target).write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Prepared quality-gated Gmail and Telegram adapters; no hosted changes.')

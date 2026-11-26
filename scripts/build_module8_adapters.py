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
 (R/'drafts/module8'/target).write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Prepared quality-gated Gmail and Telegram adapters; no hosted changes.')

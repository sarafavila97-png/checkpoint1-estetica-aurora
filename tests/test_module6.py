import json,unittest,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from verify_module6_exports import sanitized_host
def load(name): return json.loads((R/'drafts/module6'/name).read_text())
def nodes(w): return {n['name']:n for n in w['nodes']}
class VoiceGraphs(unittest.TestCase):
 def test_live_marker_rejected_but_public_substitution_allowed(self):
  h={'name':'test','nodes':[{'name':'Sheet','parameters':{'documentId':{'value':'REPLACE_SHEET_ID'}}}],'connections':{},'settings':{}}
  with self.assertRaises(AssertionError):sanitized_host(h,{'REPLACE_SHEET_ID':'real-sheet-id'})
  h['nodes'][0]['parameters']['documentId']['value']='real-sheet-id'
  public=sanitized_host(h,{'REPLACE_SHEET_ID':'real-sheet-id'})
  self.assertEqual(public['nodes'][0]['parameters']['documentId']['value'],'REPLACE_SHEET_ID')
 def test_native_agents_receive_voice_instruction_and_channel(self):
  for f in ['aurora_knowledge.json','outer_agent_knowledge.json']:
   w=load(f);a=next(n for n in w['nodes'] if n['type']=='@n8n/n8n-nodes-langchain.agent')
   s=a['parameters']['options']['systemMessage']
   self.assertIn('200 caracteres Unicode',s);self.assertIn('$json.request.channel',s)
   self.assertIn('No incluyas URLs',s);self.assertIn('emojis',s)
 def test_audio_child_has_no_persistence_or_wait(self):
  w=load('voice_transcribe.json');n=nodes(w)
  self.assertTrue(n['Get File']['parameters']['download'])
  self.assertEqual(n['Whisper es']['parameters']['options']['language'],'es')
  self.assertEqual(n['Whisper es']['parameters']['binaryPropertyName'],'data')
  self.assertEqual(w['connections']['Whisper es']['main'][0][0]['node'],'Transcripcion valida')
  self.assertFalse(any(x['type'] in ['n8n-nodes-base.wait','n8n-nodes-base.airtable','n8n-nodes-base.executeWorkflow'] for x in w['nodes']))
  self.assertNotIn('binary:',n['Solo texto']['parameters']['jsCode'])
 def test_audio_workflows_disable_saved_executions(self):
  for f in ['voice_transcribe.json','telegram_delivery.json','telegram_voice.json','aurora_knowledge.json','outer_agent_knowledge.json','aurora_manager.json']:
   w=load(f);s=w['settings']
   self.assertFalse(w['active']);self.assertFalse(w['pinData'])
   self.assertEqual(s['saveDataSuccessExecution'],'none');self.assertEqual(s['saveDataErrorExecution'],'none')
   self.assertFalse(s['saveManualExecutions']);self.assertFalse(s['saveExecutionProgress'])
 def test_receipt_precedes_audio_download_and_manager_is_current(self):
  w=load('telegram_voice.json');n=nodes(w)
  self.assertEqual(w['connections']['Reserva confirmada']['main'][0][0]['node'],'Transcribir voz')
  self.assertEqual(n['Manager actual']['parameters']['workflowId']['value'],'REPLACE_CURRENT_MANAGER_WORKFLOW_ID')
  self.assertTrue(n['Transcribir voz']['parameters']['options']['waitForSubWorkflow'])
  self.assertFalse(any(x['type']=='n8n-nodes-base.wait' for x in w['nodes']))
 def test_delivery_validates_before_tts_and_never_retries_send(self):
  w=load('telegram_delivery.json');n=nodes(w)
  self.assertEqual(w['connections']['Texto hablado valido']['main'][0][0]['node'],'Modo envio autorizado')
  self.assertEqual(w['connections']['Modo envio autorizado']['main'][0][0]['node'],'ElevenLabs español')
  self.assertFalse(n['Send Audio'].get('retryOnFail',False))
  self.assertEqual(n['Send Audio']['parameters']['binaryPropertyName'],'data')
  self.assertEqual(n['ElevenLabs español']['parameters']['additionalOptions']['model']['value'],'eleven_multilingual_v2')
  self.assertEqual(json.loads(n['ElevenLabs español']['parameters']['additionalOptions']['voiceSettings'])['stability'],0.5)
 def test_ingress_is_text_only_and_does_not_call_delivery_on_error(self):
  w=load('telegram_voice.json');n=nodes(w)
  self.assertEqual(w['connections']['Respuesta aprobada']['main'][1][0]['node'],'Revision sin envio')
  self.assertFalse(n['Telegram Trigger']['parameters']['additionalFields'].get('download',False))
  self.assertEqual(n['Entregar voz']['parameters']['workflowId']['value'],'REPLACE_TELEGRAM_DELIVERY_WORKFLOW_ID')

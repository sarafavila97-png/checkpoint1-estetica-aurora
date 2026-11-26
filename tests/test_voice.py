import json,subprocess,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def call(fn,*args):
 p=subprocess.run(['node','-e','const m=require("./src/voice.js");console.log(JSON.stringify(m['+json.dumps(fn)+'](...'+json.dumps(args)+')));'],cwd=R,text=True,capture_output=True)
 if p.returncode:raise AssertionError('Voice implementation unavailable: '+p.stderr[-200:])
 return json.loads(p.stdout)
class Voice(unittest.TestCase):
 def fixture(self):return {'update_id':123,'message':{'chat':{'id':456},'voice':{'file_id':'synthetic-file','duration':12,'file_size':1000}}}
 def test_allowed_voice_returns_only_metadata(self):
  u=self.fixture();u['binary']={'data':'never-forward'};r=call('voiceInput',u,['456'])
  self.assertTrue(r['ok']);self.assertEqual(set(r),{'ok','update_id','chat_id','file_id'});self.assertEqual(r['chat_id'],'456')
 def test_unlisted_chat_rejected_before_download(self):self.assertFalse(call('voiceInput',self.fixture(),['999'])['ok'])
 def test_missing_and_excessive_audio_rejected(self):
  for field,value in [('duration',None),('duration',31),('file_size',None),('file_size',5242881),('file_id','')]:
   u=self.fixture();u['message']['voice'][field]=value
   with self.subTest(field=field,value=value):self.assertFalse(call('voiceInput',u,['456'])['ok'])
 def test_missing_update_cannot_bypass_deduplication_key(self):
  u=self.fixture();u.pop('update_id');self.assertFalse(call('voiceInput',u,['456'])['ok'])
 def test_empty_or_failed_transcription_stops(self):
  for d in [None,{}, {'text':'  '},{'text':'hola','error':'failure'}]:self.assertFalse(call('transcriptText',d)['ok'])
  self.assertEqual(call('transcriptText',{'text':' Hola. '})['text'],'Hola.')
 def test_unicode_characters_and_no_truncation(self):
  self.assertTrue(call('speechText','á'*200)['ok']);r=call('speechText','á'*201);self.assertFalse(r['ok']);self.assertNotIn('text',r)
 def test_links_bullets_emoji_and_markdown_rejected(self):
  for s in ['Visita https://example.com','Visita www.example.com','Visita ejemplo.dev','- Servicio','• Servicio','1. Servicio','Hola 😀','Hola 🇲🇽','Hola 1️⃣','**Hola**','[Hola](example.com)','Hola\nMundo']:
   with self.subTest(s=s):self.assertFalse(call('speechText',s)['ok'])
 def test_spanish_plain_reply_allowed(self):
  s='El manicure cuesta 180 MXN. Fuente: Aurora.'
  self.assertEqual(call('speechText',s),{'ok':True,'text':s,'characters':len(s)})

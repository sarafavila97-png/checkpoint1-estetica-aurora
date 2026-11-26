"""Prepare one bounded invalid-audio contingency test, without customer delivery."""
import json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
w=json.loads((P/'m6-transcribe-hosted.json').read_text());n={x['name']:x for x in w['nodes']}
print('Transcription nodes:',list(n))
manual=dict(id='invalid-manual',name='Prueba manual',type='n8n-nodes-base.manualTrigger',typeVersion=1,position=[0,300],parameters={})
def code(name,js,x):return dict(id='invalid-'+name,name=name,type='n8n-nodes-base.code',typeVersion=2,position=[x,300],parameters={'jsCode':js})
source=code('Audio corrupto sintetico',"return [{json:{},binary:{data:{data:Buffer.from('not an audio file').toString('base64'),mimeType:'audio/wav',fileName:'invalid.wav',fileExtension:'wav'}}}];",240)
whisper=copy.deepcopy(n['Whisper es']);whisper['position']=[480,300]
valid=copy.deepcopy(n['Transcripcion valida']);valid['position']=[720,300]
fallback=code('Contingencia sin entrega',"return [{json:{status:'needs_human',reason:'TRANSCRIPTION_FAILED',output:'No pude entender el audio. Envía tu consulta por escrito o solicita revisión humana.',llm_calls:0,tts_calls:0,telegram_messages:0,binary_retained_in_result:false}}];",960)
unexpected=code('Resultado inesperado',"return [{json:{status:'unexpected_transcript',output:'Provider returned text for deliberately invalid bytes; inspect original run.',llm_calls:0,tts_calls:0,telegram_messages:0}}];",960);unexpected['position']=[960,600]
nodes=[manual,source,whisper,valid,fallback,unexpected];c={}
for a,b,port in [('Prueba manual','Audio corrupto sintetico',0),('Audio corrupto sintetico','Whisper es',0),('Whisper es','Transcripcion valida',0),('Transcripcion valida','Resultado inesperado',0),('Transcripcion valida','Contingencia sin entrega',1)]:
 ports=c.setdefault(a,{}).setdefault('main',[])
 while len(ports)<=port:ports.append([])
 ports[port].append(dict(node=b,type='main',index=0))
result=dict(name='Aurora M6 - Audio corrupto contingencia',nodes=nodes,connections=c,settings=w['settings'],active=False,pinData={})
(D/'corrupt_audio_test.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

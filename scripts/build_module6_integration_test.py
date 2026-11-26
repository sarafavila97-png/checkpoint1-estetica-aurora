"""Private synthetic audio harness; never publishes embedded audio or sends Telegram."""
import base64,copy,json,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
def node(name,typ,p,x,v=1,**kw):return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'m6-test:'+name)),name=name,type=typ,typeVersion=v,position=[x,300],parameters=p,**kw)
def code(name,js,x):return node(name,'n8n-nodes-base.code',{'jsCode':js},x,2)
def load(f):return json.loads((D/f).read_text())
ingress=load('telegram_voice.json');n={x['name']:x for x in ingress['nodes']}
trans=load('voice_transcribe.json');t={x['name']:x for x in trans['nodes']}
delivery=load('telegram_delivery.json');d={x['name']:x for x in delivery['nodes']}
env=json.loads((P/'module6-environment.json').read_text())
audio=base64.b64encode((P/'m6-synthetic-question.wav').read_bytes()).decode()
manual=node('Prueba manual','n8n-nodes-base.manualTrigger',{},0)
source=code('Audio sintetico privado','return [{json:{started_at:Date.now()},binary:{data:{data:'+json.dumps(audio)+',mimeType:"audio/wav",fileName:"synthetic-question.wav",fileExtension:"wav"}}}];',240)
whisper=copy.deepcopy(t['Whisper es']);whisper['position']=[480,300]
valid=copy.deepcopy(t['Transcripcion valida']);valid['position']=[720,300]
request=code('Request de voz',"const text=$input.first().json.text.trim();return [{json:{request:{schema_version:'1',request_id:'telegram:600001',session_id:'aurora_demo:telegram:m6-synthetic-component-1',domain:'aurora_demo',channel:'telegram',query:text,user:{display_name:'Prueba sintetica',email:null},context:{summary:null,case_status:'nuevo',key_facts:[]},evidence:[],candidate:null,correction_attempt:0,mode:'dry_run'}}}];",960)
manager=copy.deepcopy(n['Manager actual']);manager['position']=[1200,300]
ok=copy.deepcopy(n['Respuesta aprobada']);ok['position']=[1440,300]
payload=code('Payload entrega sin envio',"const d=$input.first().json;return [{json:{request:{request_id:'telegram:600001',chat_id:"+json.dumps(env['bindings']['REPLACE_TELEGRAM_CHAT_ID'])+",domain:'aurora_demo',mode:'dry_run',status:d.status,output:d.output,evidence:d.evidence||[]}}}];",1680)
prepare=copy.deepcopy(n['Entregar voz']);prepare['parameters']['workflowInputs']['value']['request']='={{ $json.request }}';prepare['position']=[1920,300]
speech_ok=copy.deepcopy(d['Texto hablado valido']);speech_ok['position']=[2160,300];speech_ok['parameters']['conditions']['conditions'][0]['leftValue']='={{ $json.status === "completed" && $json.delivery === "dry_run" && typeof $json.text === "string" && $json.characters <= 200 }}'
tts=copy.deepcopy(d['ElevenLabs español']);tts['position']=[2400,300]
result=code('Resultado sin binario',"const d=$input.first(),p=$('Entregar voz').first().json,m=$('Manager actual').first().json;let bytes=null;if(d.binary?.data&&!d.json.error){const buffer=await this.helpers.getBinaryDataBuffer(0,'data');bytes=buffer.length;}return [{json:{test:'m6-synthetic-components',transcript:$('Request de voz').first().json.request.query,manager_status:m.status,manager_output:m.output,spoken_text:p.text,characters:p.characters,audio_generated:bytes>0,audio_bytes:bytes,elapsed_ms:Date.now()-$('Audio sintetico privado').first().json.started_at,telegram_messages_sent:0,telegram_get_file_exercised:false,webhook_registered:false,audio_retained_in_result:false,cost:null}}];",2640)
failed=code('Fallo conservado',"return [{json:{test:'m6-synthetic-components',status:'failed',telegram_messages_sent:0,error:'One component failed; inspect transient node output',cost:null}}];",2400);failed['position']=[2400,700]
w=dict(name='Aurora M6 - Prueba componentes audio sin envio',nodes=[manual,source,whisper,valid,request,manager,ok,payload,prepare,speech_ok,tts,result,failed],connections={},settings=ingress['settings'],active=False,pinData={})
for a,b,port in [('Prueba manual','Audio sintetico privado',0),('Audio sintetico privado','Whisper es',0),('Whisper es','Transcripcion valida',0),('Transcripcion valida','Request de voz',0),('Transcripcion valida','Fallo conservado',1),('Request de voz','Manager actual',0),('Manager actual','Respuesta aprobada',0),('Respuesta aprobada','Payload entrega sin envio',0),('Respuesta aprobada','Fallo conservado',1),('Payload entrega sin envio','Entregar voz',0),('Entregar voz','Texto hablado valido',0),('Texto hablado valido','ElevenLabs español',0),('Texto hablado valido','Fallo conservado',1),('ElevenLabs español','Resultado sin binario',0)]:
 ports=w['connections'].setdefault(a,{}).setdefault('main',[])
 while len(ports)<=port:ports.append([])
 ports[port].append(dict(node=b,type='main',index=0))
(D/'audio_component_test.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Private synthetic component harness prepared; not executed, no Telegram send node.')

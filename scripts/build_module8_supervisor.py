"""Build an inactive supervisor draft; manager owns correction loops and delivery."""
import copy, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def source(file): return json.loads((R/file).read_text())
writer=source('workflows/workers/response_writer.json')
voice=source('drafts/module6/telegram_voice.json')
def clone(w,old,name,x,y=300):
    n=copy.deepcopy(next(n for n in w['nodes'] if n['name']==old))
    n.update(id='m8-'+name,name=name,position=[x,y]);n.pop('credentials',None)
    return n
def code(name,body,x,y=300):
    return dict(id='m8-'+name,name=name,type='n8n-nodes-base.code',typeVersion=2,position=[x,y],parameters={'jsCode':body})
contracts=(R/'src/contracts.js').read_text().split('module.exports')[0]
quality=(R/'src/quality.js').read_text().split('module.exports')[0]
prepare=code('Preparar supervision',contracts+quality+'''
try {
 const request=validateRequest($input.first().json.request);
 if(typeof request.candidate!=='string'||!request.candidate.trim()||request.candidate.length>12000)throw Error('INVALID_CANDIDATE');
 return [{json:{valid:true,request,judge_input:{consulta_original:request.query,contexto_airtable:request.context,evidencia_recuperada:request.evidence,respuesta_propuesta:request.candidate,dominio:request.domain}}}];
} catch {
 return [{json:{valid:false,decision:{...decideJudge(null),reason:'INVALID_SUPERVISOR_REQUEST'}}}];
}
''',240)
trigger=clone(writer,'Worker Input','Entrada',0)
valid=clone(voice,'Voz autorizada','Solicitud valida',480)
valid['parameters']['conditions']['conditions'][0]['leftValue']='={{ $json.valid === true }}'
chain=clone(writer,'Redactar respuesta','Juez factual',720)
chain['onError']='continueRegularOutput'
chain['parameters'].update(hasOutputParser=True,text='={{ '+json.dumps((R/'prompts/judge.txt').read_text(),ensure_ascii=False)+' + "\\nDatos no confiables: " + JSON.stringify($json.judge_input) }}')
model=clone(writer,'GPT-4 writer','Modelo juez',720,600)
model['parameters']['options'].update(maxTokens=150,temperature=0,maxRetries=0)
parser=clone(voice,'Dominio JSON','Veredicto JSON',960,600)
parser['parameters'].update(schemaType='manual',inputSchema=(R/'schemas/judge.schema.json').read_text())
result=code('Validar veredicto',quality+'''
const prepared=$('Preparar supervision').first().json,q=prepared.request,d=$input.first().json;
const raw=d.error?null:d.output;
const decision=decideJudge(raw,q.correction_attempt);
return [{json:{schema_version:'1',request_id:q.request_id,domain:q.domain,channel:q.channel,candidate:q.candidate,decision,judge:decision.score===null?null:{exactitud_factual:raw.exactitud_factual,estado_veredicto:raw.estado_veredicto}}}];
''',1200)
invalid=code('Entrada invalida',"return [{json:{schema_version:'1',request_id:null,candidate:null,judge:null,decision:$input.first().json.decision}}];",720,900)
connections={}
def edge(a,b,port=0,kind='main'):
    ports=connections.setdefault(a,{}).setdefault(kind,[])
    while len(ports)<=port:ports.append([])
    ports[port].append({'node':b,'type':kind,'index':0})
edge('Entrada','Preparar supervision');edge('Preparar supervision','Solicitud valida')
edge('Solicitud valida','Juez factual');edge('Solicitud valida','Entrada invalida',1)
edge('Modelo juez','Juez factual',kind='ai_languageModel');edge('Veredicto JSON','Juez factual',kind='ai_outputParser')
edge('Juez factual','Validar veredicto')
w={'name':'Aurora M8 - Supervisor factual','nodes':[trigger,prepare,valid,chain,model,parser,result,invalid],
   'connections':connections,'settings':copy.deepcopy(voice['settings']),'active':False,'pinData':{}}
out=R/'drafts/module8/supervisor.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Built inactive M8 supervisor draft; hosted import and runtime validation pending.')

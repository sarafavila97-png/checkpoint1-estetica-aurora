"""Create isolated no-model P2 fixtures; no official evaluations or notifications."""
import copy,json,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private/module6-drafts';P.mkdir(parents=True,exist_ok=True)
def node(name,kind,parameters,x=0):
 return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'m8-p2:'+name)),name=name,type='n8n-nodes-base.'+kind,typeVersion=2 if kind=='code' else 1,position=[x,0],parameters=parameters)
def edge(name):return {'main':[[{'node':name,'type':'main','index':0}]]}
settings=dict(executionOrder='v1',executionTimeout=180,saveDataErrorExecution='none',saveDataSuccessExecution='none',saveManualExecutions=False,saveExecutionProgress=False,callerPolicy='workflowsFromSameOwner',availableInMCP=False)
manual=node('Prueba manual','manualTrigger',{})
manager=json.loads((R/'drafts/module8/aurora_manager.json').read_text())
lib=next(n['parameters']['jsCode'] for n in manager['nodes'] if n['name']=='Iniciar supervision').split("const d=$('Aplicar memoria')")[0]
script=r'''
const checks=[];
for(const channel of ['chat','telegram']){
 const request={schema_version:'1',request_id:'p2:'+channel,session_id:'outer_agent:'+channel+':p2',domain:'outer_agent',channel,query:'Precio del plan',user:{display_name:'Prueba sintetica',email:null},context:{summary:null,case_status:'nuevo',key_facts:[]},evidence:[],candidate:null,correction_attempt:0,mode:'dry_run'};
 const evidence=[{source_id:'fixture:2',source_kind:'outer_agent_pdf',text:'Plan desde 100; precio ilustrativo.',section:'OA-01.1',page_start:2,page_end:2,score:0.8,source_version:'fixture'}];
 let state=startReview(request,{request_id:request.request_id,status:'success',output:'Plan desde 100.\nFuente: Outer_Agent_Fuente_Organizacional_v1.pdf, p. 2 (OA-01.1).',evidence});
 function judged(s,score,route){return acceptJudge(s,{request_id:s.request.request_id,domain:s.request.domain,channel:s.request.channel,candidate:s.request.candidate,judge:{exactitud_factual:score,estado_veredicto:route}});}
 state=judged(state,3,'CORREGIR');
 state=correctCandidate(state,{text:'El plan parte de 100; precio ilustrativo.',source_ids:['forged']});
 if(channel==='telegram')state=compactCandidate(state,{text:'Plan desde 100; precio ilustrativo.'});
 state=finalizeCandidate(state);
 const approved=judged(state,5,'APROBADO');
 const tampered={...state,request:{...state.request,candidate:'Plan desde 100.'}};
 const blocked=judged(tampered,5,'APROBADO');
 if(approved.decision.route!=='APROBADO'||blocked.decision.route!=='ESCALAR'||state.citation_source_ids.join()!=='fixture:2')throw Error('CITATION_REGRESSION');
 if(channel==='telegram'&&!speechText(state.request.candidate).ok)throw Error('INVALID_SPEECH');
 checks.push({channel,correction_attempt:state.request.correction_attempt,candidate:state.request.candidate,source_ids:state.citation_source_ids,approved:approved.decision.route,tampered:blocked.decision.reason});
}
const request={schema_version:'1',request_id:'p2:recall',session_id:'outer_agent:chat:p2-recall',domain:'outer_agent',channel:'chat',query:'¿Qué color prefiero?',user:{display_name:'Prueba',email:null},context:{summary:{asunto_principal:'Preferencia',puntos_clave:['Prefiere coral'],accion_requerida:'Recordar'},case_status:'nuevo',key_facts:['Prefiere coral']},evidence:[],candidate:null,correction_attempt:0,mode:'dry_run'};
const provenance={source:'validated_session_summary',session_id:request.session_id,record_id:'recFixture'};
const response={request_id:request.request_id,status:'success',output:'Prefieres coral.',evidence:[],memory_provenance:provenance};
const trusted={route:'MEMORY_RECALL',memory:{branch:'existing',record_id:'recFixture',fields:{Session_ID:request.session_id},context:request.context}};
const recall=startReview(request,response,trusted);
const wrong=startReview(request,{...response,memory_provenance:{...provenance,session_id:'outer_agent:chat:other'}},trusted);
const fabricated=startReview(request,response);
const withPdf=startReview(request,{...response,evidence:[{source_id:'fixture:2',source_kind:'outer_agent_pdf',text:'Fact',section:'OA-01.1',page_start:2,page_end:2,score:0.8,source_version:'fixture'}]},trusted);
if(recall.response_category!=='memory_recall'||recall.decision!==null||wrong.decision?.route!=='ESCALAR'||fabricated.decision?.route!=='ESCALAR'||withPdf.response_category==='memory_recall'||!withPdf.request.candidate.includes('Fuente:'))throw Error('MEMORY_PROVENANCE_REGRESSION');
checks.push({case:'validated_memory_recall',category:recall.response_category,candidate:recall.request.candidate,wrong_session:wrong.decision.reason,fabricated:fabricated.decision.reason,pdf_evidence_category:withPdf.response_category});
return [{json:{status:'passed',checks,model_calls:0,notifications:0,delivery:'not_sent'}}];
'''
w=dict(name='Aurora M8 - P2 citas sin modelos',nodes=[manual,node('Comprobar citas','code',{'jsCode':lib+script},260)],connections={'Prueba manual':edge('Comprobar citas')},settings=settings,active=False,pinData={})
(P/'m8_p2_citations.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
g=json.loads((R/'drafts/module8/gmail_message.json').read_text());by={n['name']:n for n in g['nodes']}
fixture=node('Revisar sin enviar','code',{'jsCode':"return [{json:{request_id:'gmail:p2-wait',status:'needs_human',delivery:'not_sent',review:{request_id:'gmail:p2-wait',domain:'aurora_demo',status:'needs_human',reason:'SYNTHETIC_ESCALATION',record_reference:'local fixture'}}}];"},260)
stub=node('Notificar revision Slack','code',{'jsCode':"return [{json:{ok:true,message_timestamp:'synthetic-no-slack',stub:true,started_at:Date.now()}}];"},1000)
wait=copy.deepcopy(by['Wait revision Gmail']);wait['parameters'].update(amount=1,unit='seconds')
result=copy.deepcopy(by['Resultado revision'])
assertion=node('Comprobar pausa sin borrador','code',{'jsCode':"const r=$input.first().json,s=$('Notificar revision Slack').first().json,elapsed_ms=Date.now()-s.started_at;if(elapsed_ms<900||r.status!=='needs_human'||r.delivery!=='not_sent'||r.notification.accepted!==true||r.draft_id)throw Error('GMAIL_REVIEW_REGRESSION');return [{json:{status:'passed',elapsed_ms,review_status:r.status,notification_stub_invocations:$('Notificar revision Slack').all().length,real_notifications:0,drafts:0,delivery:r.delivery}}];"},1800)
names=['Necesita notificacion','Payload aviso','Repeticion sin notificacion']
nodes=[manual,fixture]+[copy.deepcopy(by[n]) for n in names]+[stub,wait,result,assertion]
c={k:copy.deepcopy(g['connections'][k]) for k in ['Revisar sin enviar','Necesita notificacion','Payload aviso','Notificar revision Slack','Wait revision Gmail']}
c['Prueba manual']=edge('Revisar sin enviar');c['Resultado revision']=edge('Comprobar pausa sin borrador')
w=dict(name='Aurora M8 - P2 pausa Gmail sin aviso real',nodes=nodes,connections=c,settings=settings,active=False,pinData={})
(P/'m8_p2_gmail_wait.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Prepared two no-model fixtures in',P)

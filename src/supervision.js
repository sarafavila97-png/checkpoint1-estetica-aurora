'use strict';
const {validateRequest}=require('./contracts');
const {decideJudge}=require('./quality');
const {speechText}=require('./voice');
const clone=v=>JSON.parse(JSON.stringify(v));
function escalated(state,reason){return {...state,decision:{...decideJudge(null,state.request?.correction_attempt??0),reason}};}
function candidateValid(q,value){return typeof value==='string'&&!!value.trim()&&value.length<=12000&&(q.channel!=='telegram'||speechText(value).ok);}
// The source IDs are frozen manager state, never fields accepted from a rewrite.
function citationSuffix(state){
 const q=state.request;
 if(q.domain!=='outer_agent')return '';
 const ids=state.citation_source_ids;
 if(!Array.isArray(ids))throw Error('MISSING_CITATION_STATE');
 if(!ids.length)return '';
 const selected=ids.map(id=>{
  const e=q.evidence.find(e=>e.source_id===id);
  if(!e||e.source_kind!=='outer_agent_pdf'||!Number.isFinite(e.score)||e.score<0.5||!Number.isInteger(e.page_start)||!Number.isInteger(e.page_end)||e.page_start<1||e.page_end<e.page_start)throw Error('UNSUPPORTED_CITATION');
  return e;
 });
 if(q.channel==='telegram'){
  const pages=[...new Set(selected.map(e=>e.page_start===e.page_end?String(e.page_start):e.page_start+' a '+e.page_end))];
  return ' Fuente: documento Outer Agent, '+(pages.length===1&&!pages[0].includes(' a ')?'página ':'páginas ')+pages.join(', ')+'.';
 }
 const refs=selected.map(e=>'Outer_Agent_Fuente_Organizacional_v1.pdf, '+(e.page_start===e.page_end?'p. '+e.page_start:'pp. '+e.page_start+'–'+e.page_end)+(e.section?' ('+e.section+')':''));
 return '\nFuente: '+[...new Set(refs)].join('; ')+'.';
}
function finalizeCandidate(state){
 if(state.decision?.route==='ESCALAR')return state;
 const q=state.request;
 if(q.domain!=='outer_agent'||(state.response_category==='memory_recall'&&q.evidence.length===0))return state;
 try{
  const suffix=citationSuffix(state);
  const body=q.candidate.replace(/\s*Fuente:[\s\S]*$/i,'').trim();
  if(!body||(!suffix&&!/^No sé(?:[.!?\s]|$)/i.test(body)))return escalated(state,'MISSING_CITATION');
  return {...state,request:{...q,candidate:body+suffix}};
 }catch{return escalated(state,'UNSUPPORTED_CITATION');}
}
function citationValid(state){
 if(state.request.domain!=='outer_agent')return true;
 const prepared=finalizeCandidate(state);
 return prepared.decision?.route!=='ESCALAR'&&prepared.request.candidate===state.request.candidate;
}
function compactCandidate(state,result){
 if(result?.error||typeof result?.text!=='string'||!result.text.trim())return escalated(state,'COMPACTION_FAILED');
 const next=finalizeCandidate({...state,request:{...clone(state.request),candidate:result.text.trim()}});
 return next.decision?.route==='ESCALAR'?next:candidateValid(next.request,next.request.candidate)?next:escalated(next,'COMPACTION_FAILED');
}
function validatedMemoryRecall(q,response,trusted){
 const p=response.memory_provenance,m=trusted?.memory;
 return q.evidence.length===0&&trusted?.route==='MEMORY_RECALL'&&
  p&&Object.keys(p).sort().join('|')==='record_id|session_id|source'&&p.source==='validated_session_summary'&&
  p.session_id===q.session_id&&typeof p.record_id==='string'&&!!p.record_id.trim()&&
  m?.branch==='existing'&&m.record_id===p.record_id&&m.fields?.Session_ID===q.session_id&&
  JSON.stringify(m.context)===JSON.stringify(q.context)&&
  (q.context.summary!==null||q.context.key_facts.length>0);
}
function startReview(request,response,trusted=null){
 const q=clone(validateRequest(request));q.correction_attempt=0;
 if(!response||response.request_id!==q.request_id||response.status!=='success'||typeof response.output!=='string'||!response.output.trim())return escalated({request:q,history:[]},'UPSTREAM_NOT_SUCCESS');
 q.candidate=response.output;q.evidence=clone(response.evidence||[]);validateRequest(q);
 const recalled=validatedMemoryRecall(q,response,trusted);
 return finalizeCandidate({request:q,history:[],decision:null,response_category:recalled?'memory_recall':'domain_answer',...(recalled?{memory_provenance:clone(response.memory_provenance)}:{}),citation_source_ids:q.domain==='outer_agent'?[...new Set(q.evidence.map(e=>e.source_id))]:[]});
}
function acceptJudge(state,result){
 const q=state.request;
 if(!result||result.error||result.request_id!==q.request_id||result.domain!==q.domain||result.channel!==q.channel||result.candidate!==q.candidate)return escalated(state,'SUPERVISOR_CORRELATION_FAILED');
 if(!citationValid(state))return escalated(state,'CITATION_VALIDATION_FAILED');
 if(!candidateValid(q,q.candidate))return escalated(state,'CHANNEL_VALIDATION_FAILED');
 const decision=decideJudge(result.judge,q.correction_attempt);
 return {...state,decision,history:[...state.history,{attempt:q.correction_attempt,candidate:q.candidate,score:decision.score,route:decision.route,reason:decision.reason}]};
}
function correctCandidate(state,result){
 if(state.decision?.route!=='CORREGIR'||state.request.correction_attempt>=2)return escalated(state,'CORRECTION_NOT_PERMITTED');
 const candidate=result?.error?null:result?.text;
 if(typeof candidate!=='string'||!candidate.trim()||candidate.length>12000)return escalated(state,'CORRECTION_FAILED');
 return finalizeCandidate({...state,request:{...clone(state.request),candidate:candidate.trim(),correction_attempt:state.request.correction_attempt+1},decision:null});
}
function humanDecision(state,body){
 const q=state.request;
 const rejected=reason=>({request_id:q.request_id,status:'needs_human',output:'La solicitud requiere revisión humana.',delivery:'not_sent',reason});
 if(!body||body.request_id!==q.request_id||!['approve','edit','reject'].includes(body.decision))return rejected('INVALID_HUMAN_DECISION');
 if(body.decision==='reject')return {...rejected('HUMAN_REJECTED'),status:'rejected'};
 const candidate=body.decision==='edit'?body.edited_answer:q.candidate;
 if(!candidateValid(q,candidate))return rejected('INVALID_HUMAN_CANDIDATE');
 return {request_id:q.request_id,status:'success',output:candidate,evidence:q.evidence,delivery:'approved_for_adapter',quality:{source:'authenticated_human',action:body.decision,attempt:q.correction_attempt}};
}
module.exports={startReview,acceptJudge,correctCandidate,humanDecision,candidateValid,finalizeCandidate,compactCandidate,citationValid,citationSuffix};

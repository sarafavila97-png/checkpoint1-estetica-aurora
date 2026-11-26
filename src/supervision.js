'use strict';
const {validateRequest}=require('./contracts');
const {decideJudge}=require('./quality');
const {speechText}=require('./voice');
const clone=v=>JSON.parse(JSON.stringify(v));
function escalated(state,reason){return {...state,decision:{...decideJudge(null,state.request?.correction_attempt??0),reason}};}
function candidateValid(q,value){return typeof value==='string'&&!!value.trim()&&value.length<=12000&&(q.channel!=='telegram'||speechText(value).ok);}
function startReview(request,response){
 const q=clone(validateRequest(request));q.correction_attempt=0;
 if(!response||response.request_id!==q.request_id||response.status!=='success'||typeof response.output!=='string'||!response.output.trim())return escalated({request:q,history:[]},'UPSTREAM_NOT_SUCCESS');
 q.candidate=response.output;q.evidence=clone(response.evidence||[]);validateRequest(q);
 return {request:q,history:[],decision:null};
}
function acceptJudge(state,result){
 const q=state.request;
 if(!result||result.error||result.request_id!==q.request_id||result.domain!==q.domain||result.channel!==q.channel||result.candidate!==q.candidate)return escalated(state,'SUPERVISOR_CORRELATION_FAILED');
 if(!candidateValid(q,q.candidate))return escalated(state,'CHANNEL_VALIDATION_FAILED');
 const decision=decideJudge(result.judge,q.correction_attempt);
 return {...state,decision,history:[...state.history,{attempt:q.correction_attempt,candidate:q.candidate,score:decision.score,route:decision.route,reason:decision.reason}]};
}
function correctCandidate(state,result){
 if(state.decision?.route!=='CORREGIR'||state.request.correction_attempt>=2)return escalated(state,'CORRECTION_NOT_PERMITTED');
 const candidate=result?.error?null:result?.text;
 if(typeof candidate!=='string'||!candidate.trim()||candidate.length>12000)return escalated(state,'CORRECTION_FAILED');
 return {...state,request:{...clone(state.request),candidate:candidate.trim(),correction_attempt:state.request.correction_attempt+1},decision:null};
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
module.exports={startReview,acceptJudge,correctCandidate,humanDecision,candidateValid};

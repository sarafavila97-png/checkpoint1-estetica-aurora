'use strict';
const NO_SE='No sé. No está documentado en la fuente disponible.';
function normalizeRetrieval(raw,cfg,domain){
 if(domain!=='outer_agent')throw Error('RETRIEVAL_DOMAIN_MISMATCH');
 if(!raw||raw.error||!Array.isArray(raw.results))throw Error('RETRIEVAL_UNAVAILABLE');
 if(!cfg||!Number.isInteger(cfg.top_k)||cfg.top_k<1||cfg.top_k>10||!Number.isFinite(cfg.minimum_score)||cfg.minimum_score<0)throw Error('INVALID_RETRIEVAL_CONFIG');
 const evidence=[];
 for(const r of raw.results.slice(0,cfg.top_k)){
  if(typeof r.rerank_score!=='number'||!Number.isFinite(r.rerank_score))throw Error('MISSING_RERANK_SCORE');
  if(r.rerank_score<cfg.minimum_score)continue;
  const f=r.static_fields||{};
  if(f.parsed_directory_file_id!==cfg.file_id||!Number.isInteger(f.page_range_start)||!Number.isInteger(f.page_range_end)||f.page_range_start<1||f.page_range_end<f.page_range_start||f.page_range_end>cfg.page_count||!Number.isInteger(f.chunk_index)||f.chunk_index<0)throw Error('UNVERIFIABLE_SOURCE');
  if(typeof r.content!=='string'||!r.content.trim())throw Error('EMPTY_CHUNK');
  const headings=[...r.content.matchAll(/OA-\d{2}\.\d+/g)].map(m=>m[0]);
  evidence.push({source_id:cfg.file_id+':'+f.chunk_index,source_kind:'outer_agent_pdf',text:Array.from(r.content).slice(0,12000).join(''),section:[...new Set(headings)].join(', ')||null,page_start:f.page_range_start,page_end:f.page_range_end,score:r.rerank_score,source_version:cfg.source_version});
 }
 return {ok:true,evidence,top_k:cfg.top_k,minimum_score:cfg.minimum_score,score_field:'rerank_score'};
}
function toolEvidence(steps){
 const matching=(steps||[]).filter(s=>s.action?.tool==='Consultar_documentacion_Outer_Agent');
 if(matching.length!==1)throw Error('RETRIEVAL_TOOL_CALL_COUNT');
 let o=matching[0].observation;if(typeof o==='string')o=JSON.parse(o);
 if(Array.isArray(o)){if(o.length!==1)throw Error('INVALID_TOOL_RESULT');o=o[0];}
 if(o?.json)o=o.json;
 if(o?.ok!==true||!Array.isArray(o.evidence))throw Error('RETRIEVAL_TOOL_FAILED');
 return o.evidence;
}
function groundedAnswer(output,evidence){
 if(!output||Object.keys(output).sort().join('|')!=='answer|source_ids|supported'||typeof output.supported!=='boolean'||typeof output.answer!=='string'||!Array.isArray(output.source_ids))throw Error('INVALID_GROUNDED_ANSWER');
 if(!output.supported)return {answer:NO_SE,evidence:[]};
 if(!output.answer.trim()||!output.source_ids.length)throw Error('MISSING_CITATION');
 const selected=[...new Set(output.source_ids)].map(id=>{
  const e=evidence.find(e=>e.source_id===id);
  if(!e||e.source_kind!=='outer_agent_pdf'||!Number.isFinite(e.score)||e.score<0.5||!Number.isInteger(e.page_start)||!Number.isInteger(e.page_end))throw Error('UNSUPPORTED_CITATION');return e;
 });
 const citations=selected.map(e=>'Outer_Agent_Fuente_Organizacional_v1.pdf, '+(e.page_start===e.page_end?'p. '+e.page_start:'pp. '+e.page_start+'–'+e.page_end)+(e.section?' ('+e.section+')':''));
 return {answer:output.answer.trim()+'\nFuente: '+[...new Set(citations)].join('; ')+'.',evidence:selected};
}
function domainRoute(route,domain){
 if(!['aurora_demo','outer_agent'].includes(domain))throw Error('INVALID_DOMAIN');
 if(!['AURORA_INFO','OUTER_AGENT_INFO','MEMORY_RECALL','HUMAN','CLARIFY'].includes(route))return 'HUMAN';
 if((route==='AURORA_INFO'&&domain!=='aurora_demo')||(route==='OUTER_AGENT_INFO'&&domain!=='outer_agent'))return 'CLARIFY';
 return route;
}
module.exports={normalizeRetrieval,toolEvidence,groundedAnswer,domainRoute,NO_SE};

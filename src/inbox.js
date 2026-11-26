// Deterministic boundary checks; business intent remains the manager's job.
function headersOf(m) {
  const out={};
  for(const source of [m.payload?.headers,m.headers]) {
    const pairs=Array.isArray(source)?source.map(h=>[h.name,h.value]):Object.entries(source||{});
    for(const [k,v] of pairs)out[String(k).toLowerCase()]=String(v??'');
  }
  return out;
}
function senderValue(m){const h=headersOf(m);const f=m.from??m.From??h.from??'';return typeof f==='object'?String(f.text??f.value?.[0]?.address??''):String(f);}
function allowInbound(m) {
  const h=headersOf(m),subject=String(m.subject??m.Subject??h.subject??'');
  return !(h['auto-submitted']&&h['auto-submitted'].trim().toLowerCase()!=='no') &&
    !('x-autoreply' in h) && !('x-autorespond' in h) &&
    !/\b(bulk|list|junk)\b/i.test(h.precedence||'') &&
    !/(no[._-]?reply|mailer-daemon)/i.test(senderValue(m)) &&
    !/(auto[ -]?reply|out of office|undeliverable)/i.test(subject);
}
function parseSender(raw) {
  if(/[\r\n,;]/.test(raw))throw Error('INVALID_SENDER');
  const match=raw.trim().match(/^(?:([^<>]*)<([^<>]+)>|([^<>\s]+))$/);
  if(!match)throw Error('INVALID_SENDER');
  const email=(match[2]||match[3]).trim().toLowerCase();
  if(!/^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}$/i.test(email))throw Error('INVALID_SENDER');
  return {email,name:(match[1]||'').trim().replace(/^"|"$/g,'').slice(0,100)};
}
function htmlText(s){return String(s).replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1\s*>/gi,'').replace(/<[^>]*>/g,' ').replace(/&(?:amp|lt|gt|quot|apos|nbsp);/g,x=>({'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&apos;':"'",'&nbsp;':' '}[x])).replace(/\s+/g,' ').trim();}
function cleanMail(m) {
  if(!allowInbound(m))throw Error('AUTOMATIC_MESSAGE_BLOCKED');
  const sender=parseSender(senderValue(m)),h=headersOf(m);
  const message_id=String(m.id??m.message_id??''),thread_id=String(m.threadId??m.thread_id??'');
  if(!message_id||!thread_id||/[\r\n]/.test(message_id+thread_id))throw Error('MISSING_MAIL_ID');
  const body=m.text??m.textPlain??m.BodyText??null;
  return {From:sender.email,Subject:String(m.subject??m.Subject??h.subject??'').replace(/[\r\n]/g,' ').slice(0,300),BodyText:Array.from(body===null?htmlText(m.html??''):String(body)).slice(0,4000).join(''),message_id,thread_id,display_name:sender.name||String(m.display_name||'').slice(0,100)};
}
function crmPlan(email,displayName,rows) {
  email=parseSender(email).email;
  if(!Array.isArray(rows)||rows.length>1)throw Error('AMBIGUOUS_CONTACT');
  if(rows.length===0)return {action:'create',email,display_name:String(displayName||'').slice(0,100)};
  const r=rows[0];if(!r.id||String(r.properties?.email||'').toLowerCase()!==email)throw Error('CONTACT_MISMATCH');
  const name=String(displayName||'').trim().slice(0,100);
  return {action:name&&name!==r.properties?.firstname?'update':'found',contact_id:String(r.id),email,...(name?{display_name:name}:{})};
}
function receiptDecision(request_id,rows) {
  if(!/^gmail:[^\s]+$/.test(request_id)||!Array.isArray(rows)||rows.length>1)throw Error('INVALID_RECEIPT');
  if(rows.length===0)return {action:'start',request_id};
  const r=rows[0];if(r.request_id!==request_id)throw Error('RECEIPT_MISMATCH');
  if(r.status==='completed'&&r.draft_id)return {action:'replay',request_id,draft_id:r.draft_id,contact_id:r.contact_id||null};
  return {action:'review',request_id,reason:'Existing incomplete receipt; reconcile before retry'};
}
function reviewPayload(d){return {request_id:String(d.request_id),domain:String(d.domain),status:String(d.status),reason:Array.from(String(d.reason||'')).slice(0,200).join(''),record_reference:d.record_reference?String(d.record_reference):null};}
function draftResult(d){return d&&!d.error&&typeof d.id==='string'&&d.id?{status:'completed',draft_id:d.id,delivery:'borrador_creado'}:{status:'delivery_unknown',draft_id:null,delivery:'requiere_revision'};}
module.exports={headersOf,senderValue,allowInbound,parseSender,htmlText,cleanMail,crmPlan,receiptDecision,reviewPayload,draftResult};

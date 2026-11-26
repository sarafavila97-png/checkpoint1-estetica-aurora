"""Deterministic hosted persistence cases; supplied summaries are fixtures, not LLM evidence."""
import runpy,copy,json
from pathlib import Path
h=runpy.run_path(str(Path(__file__).with_name('build_module3_harness.py')))
node,code,call=h['node'],h['code'],h['call'];q=h['q'];O=h['O'];base=h['base']
summary={'asunto_principal':'Consulta de manicure','puntos_clave':['Manicure clásico: 180 MXN; negocio ficticio'], 'accion_requerida':'Consultar disponibilidad con recepción'}
cases=[('B1','B',None,1,'updated')]+[(f'A{i}','A',None,i,'updated') for i in range(2,6)]+[('A6','A',None,5,'needs_summary'),('A6','A',dict(summary,extra='invalid'),5,'error'),('A6','A',summary,0,'updated'),('A6','A',summary,0,'duplicate'),('B2','B',None,2,'updated')]
nodes=[node('Prueba lote','n8n-nodes-base.manualTrigger',{},0)];edges=[];previous='Prueba lote';checks=[]
for i,(rid,sess,summ,count,expect) in enumerate(cases):
 label=f'{i+1:02d}';fixture=f'Caso {label}';before=f'Leer antes {label}';guard=f'Validar lectura {label}';write=f'Escribir {label}';after=f'Leer despues {label}';check=f'Comprobar {label}'
 req=copy.deepcopy(q);req.update(request_id='chat:m3-'+rid,session_id='aurora_demo:chat:m3-'+sess,user={'display_name':'Prueba '+sess,'email':None})
 f=code(fixture,'return [{json:'+json.dumps({'request':req,'summary':summ},ensure_ascii=False)+'}];',200+i*1400)
 a=call(before,'oap8j98XvShrjhr7',420+i*1400,'={{ $json.request }}')
 g=code(guard,'const d=$input.first().json;if(!d.ok)throw Error("MEMORY_READ_FAILED");return [{json:d}];',640+i*1400)
 w=call(write,'f9IIvpgiyEKgiYTX',860+i*1400,'={{ $json.request }}',True);w['parameters']['workflowInputs']['value']['summary']='={{ $("'+fixture+'").first().json.summary }}'
 b=call(after,'oap8j98XvShrjhr7',1080+i*1400,'={{ $("'+fixture+'").first().json.request }}')
 body='const a=$input.first().json,w=$('+json.dumps(write)+').first().json,b=$('+json.dumps(before)+').first().json; if(!a.ok)throw Error("READ_AFTER_FAILED");const fields=a.memory.fields;const m=JSON.parse(fields["Datos clave"]);const expected='+json.dumps(expect)+';if(m.accepted_message_count!=='+str(count)+')throw Error("COUNT_MISMATCH");if(expected==="updated"&&!w.updated)throw Error("UPDATE_MISSING");if(expected==="duplicate"&&!w.duplicate)throw Error("DEDUPE_MISSING");if(expected==="needs_summary"&&!w.needs_summary)throw Error("SUMMARY_GATE_MISSING");if(expected==="error"&&w.ok!==false)throw Error("INVALID_SUMMARY_ACCEPTED");if(a.memory.record_id!==b.memory.record_id)throw Error("RECORD_CHANGED");return [{json:{case_id:'+json.dumps(label+'-'+rid+'-'+expect)+',status:"PASS",record_id:a.memory.record_id,session_id:fields.Session_ID,count:m.accepted_message_count,summary:fields["Resumen consolidado"],write_status:expected}}];'
 c=code(check,body,1300+i*1400);nodes.extend([f,a,g,w,b,c]);seq=[previous,fixture,before,guard,write,after,check];edges.extend(zip(seq,seq[1:]));previous=check;checks.append(check)
final=code('Resultados del lote','return '+json.dumps(checks)+'.map(n=>({json:$(n).first().json}));',200+len(cases)*1400);nodes.append(final);edges.append((previous,final['name']))
cons={a:{'main':[[{'node':b,'type':'main','index':0}]]} for a,b in edges}
w={'name':'Aurora M3 - Lote persistencia','nodes':nodes,'connections':cons,'settings':base['settings'],'active':False,'pinData':{}}
(O/'memory_batch.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print(f'Private batch: {len(cases)} persistence cases; {len(nodes)} nodes. Fixture summaries, no model calls.')

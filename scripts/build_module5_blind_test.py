"""Build a five-case evaluation, passing questions only (never expectations) to agent."""
import runpy,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];s=runpy.run_path(str(ROOT/'scripts/build_module5_integration_test.py'));w=copy.deepcopy(s['w']);template=copy.deepcopy(s['qs'][0]['request'])
source=ROOT.parent.parent/'realtime-voice-chat/outputs/outer-agent-source/pruebas_reservadas_NO_INDEXAR.json';cases=json.loads(source.read_text())['pruebas'][:5];assert len(cases)==5
inputs=[]
for case in cases:
 q=copy.deepcopy(template);q.update(request_id='chat:m5-blind-'+case['id'],session_id='outer_agent:chat:m5-blind-'+case['id'],query=case['pregunta']);inputs.append({'json':{'request':q}})
w['name']='Aurora M5 - Cinco pruebas reservadas congeladas';w['nodes'][1]['parameters']['jsCode']='return '+json.dumps(inputs,ensure_ascii=False)+';';w['nodes'][2]['parameters']['workflowId']['value']='mAqLqfynaua8kF3K'
w['nodes'][3]['parameters']['jsCode']="const results=$input.all().map(x=>x.json);const report={harness_execution_id:$execution.id,captured_at:new Date().toISOString(),cases:results};return [{json:{count:results.length,statuses:results.map(r=>({request_id:r.request_id,status:r.status})),evaluation:'independent correctness review pending'},binary:{data:{data:Buffer.from(JSON.stringify(report,null,2)).toString('base64'),mimeType:'application/json',fileName:'m5-blind-results.json',fileExtension:'json'}}}];"
s['P'].joinpath('blind_test.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n');print('Five questions only; no expected answers in workflow.')

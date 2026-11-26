import json,subprocess,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def run(steps):
 p=subprocess.run(['node','-e','try{const m=require("./src/knowledge.js");console.log(JSON.stringify({ok:true,evidence:m.sheetEvidence('+json.dumps(steps)+')}))}catch(e){console.log(JSON.stringify({ok:false,error:e.message}))}'],cwd=R,text=True,capture_output=True)
 return json.loads(p.stdout)
def step(obs):return [{'action':{'tool':'Consultar_informacion_estetica'},'observation':obs}]
class Knowledge(unittest.TestCase):
 def test_empty_observations_never_become_evidence(self):
  for obs in ['', '""', '[]', [], None, {}, {'error':'unavailable'}]:
   with self.subTest(obs=obs):self.assertFalse(run(step(obs))['ok'])
 def test_only_actual_sheet_rows_are_accepted(self):
  rows=[{'clave':'manicure','categoria':'servicio','informacion':'Manicure clásico','precio_mxn':180,'duracion_min':40}]
  for obs in [rows,json.dumps(rows)]:
   r=run(step(obs));self.assertTrue(r['ok']);self.assertEqual(json.loads(r['evidence'][0]['text']),rows)
 def test_wrong_tool_and_missing_columns_rejected(self):
  self.assertFalse(run([{'action':{'tool':'other'},'observation':[{'clave':'x','informacion':'x'}]}])['ok'])
  self.assertFalse(run(step([{'text':'180 MXN'}]))['ok'])
 def test_multiple_calls_and_error_rows_rejected(self):
  self.assertFalse(run(step([{'clave':'x','informacion':'x'}])*2)['ok'])
  self.assertFalse(run(step([{'clave':'x','informacion':'x','error':'failed'}]))['ok'])

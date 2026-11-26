import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(name):return json.loads((R/'drafts/module8'/name).read_text())
class QualityGraph(unittest.TestCase):
 def test_all_candidates_enter_gate_before_memory(self):
  w=load('aurora_manager.json')
  for name in ['Entregar respuesta','Respuesta desde memoria','Fallback humano']:
   self.assertEqual(w['connections'][name]['main'][0][0]['node'],'Iniciar supervision')
 def test_bounded_correction_graph_has_three_judges_two_rewrites(self):
  w=load('aurora_manager.json');n={x['name']:x for x in w['nodes']};c=w['connections']
  self.assertEqual(len([k for k in n if k.startswith('Supervisor ')]),3)
  self.assertEqual(len([k for k in n if k.startswith('Corregir ')]),2)
  for i in range(3):
   switch=n[f'Switch veredicto {i}'];self.assertEqual(switch['parameters']['numberOutputs'],3)
   self.assertEqual(c[f'Switch veredicto {i}']['main'][2][0]['node'],'Escalar revision')
  self.assertEqual(c['Switch veredicto 2']['main'][1][0]['node'],'Escalar revision')
  incoming=[a for a,types in c.items() for ports in types.values() for port in ports for e in port if e['node']=='Iniciar supervision']
  self.assertEqual(set(incoming),{'Entregar respuesta','Respuesta desde memoria','Fallback humano'})
 def test_compaction_is_before_judge_and_delivery_has_no_model(self):
  w=load('aurora_manager.json');c=w['connections']
  for i in range(3):
   self.assertEqual(c[f'Validar compacto {i}']['main'][0][0]['node'],f'Candidato final {i}')
   self.assertEqual(c[f'Apto para juez {i}']['main'][0][0]['node'],f'Supervisor {i}')
  d=load('telegram_delivery.json')
  self.assertFalse(any('langchain' in n['type'] for n in d['nodes']))
  self.assertEqual(d['connections']['Validar entrega']['main'][0][0]['node'],'Preparar texto hablado')
 def test_wait_is_text_only_without_autoapproval_endpoint(self):
  w=load('aurora_manager.json');n={x['name']:x for x in w['nodes']};c=w['connections']
  self.assertEqual(n['Wait revision humana']['parameters'],{'resume':'timeInterval','amount':24,'unit':'hours'})
  self.assertEqual(c['Wait revision humana']['main'][0][0]['node'],'Revision pendiente sin entrega')
  self.assertNotIn('resumeUrl',json.dumps(w));self.assertNotIn('getBinaryDataBuffer',json.dumps(w))
  alert=n['Notificar revision M8']['parameters']['text'];self.assertNotIn('candidate',alert);self.assertNotIn('evidence',alert)
 def test_connections_have_existing_nodes_and_no_delivery_actions(self):
  w=load('aurora_manager.json');names={n['name'] for n in w['nodes']}
  for source,types in w['connections'].items():
   self.assertIn(source,names)
   for ports in types.values():
    for port in ports:
     for e in port:self.assertIn(e['node'],names)
  self.assertFalse(any(n['type'] in ['n8n-nodes-base.telegram','n8n-nodes-base.gmail','@elevenlabs/n8n-nodes-elevenlabs.elevenLabs'] for n in w['nodes']))

class GmailEscalationRegression(unittest.TestCase):
 def test_review_notifies_once_then_waits_without_path_to_draft(self):
  w=load('gmail_message.json');n={x['name']:x for x in w['nodes']};c=w['connections']
  self.assertIn('Wait revision Gmail',n)
  self.assertEqual(n['Wait revision Gmail']['parameters'],{'resume':'timeInterval','amount':24,'unit':'hours'})
  self.assertEqual(c['Notificar revision Slack']['main'][0][0]['node'],'Wait revision Gmail')
  self.assertEqual(c['Wait revision Gmail']['main'][0][0]['node'],'Resultado revision')
  seen=set();pending=['Revisar sin enviar']
  while pending:
   name=pending.pop()
   if name in seen:continue
   seen.add(name)
   pending += [e['node'] for ports in c.get(name,{}).values() for port in ports for e in port]
  self.assertNotIn('Crear borrador',seen)
  self.assertEqual([x for x in seen if x=='Notificar revision Slack'],['Notificar revision Slack'])
  self.assertIn("mode:'dry_run'",json.dumps(n['Payload manager']))
  self.assertFalse(any(x.get('binary') for x in w['nodes']))

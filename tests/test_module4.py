import json, subprocess, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def call(fn, *args):
    script = 'const m=require("./src/inbox.js");try{console.log(JSON.stringify(m['+json.dumps(fn)+'](...'+json.dumps(args)+')))}catch(e){console.log(JSON.stringify({error:e.message}))}'
    r = subprocess.run(['node','-e',script],cwd=ROOT,text=True,capture_output=True,check=True)
    return json.loads(r.stdout)
MAIL={'id':'msg-001','threadId':'thread-001','from':'Prueba <aurora-test@example.com>','subject':'Manicure','text':'Precio de manicure'}
class Inbox(unittest.TestCase):
    def test_auto_reply_stops_before_agent(self):
        cases=[{'headers':{'Auto-Submitted':'auto-replied'}},{'headers':[{'name':'X-Autoreply','value':'yes'}]}, {'headers':{'Precedence':'bulk'}}, {'from':'NoReply@example.com'},{'subject':'Out of office: Vacation'},{'subject':'Undeliverable: Message'}]
        for override in cases:
            with self.subTest(override=override):self.assertFalse(call('allowInbound',dict(MAIL,**override)))
        self.assertTrue(call('allowInbound',dict(MAIL,headers={'Auto-Submitted':'no'})))
    def test_invalid_from_stops_before_crm(self):
        for sender in ['', 'a@example.com,b@example.com', 'a@example.com\r\nBcc: victim@example.com']:
            self.assertIn('error',call('cleanMail',dict(MAIL,from_=sender,**{'from':sender})))
    def test_parent_child_normalization_preserves_sender_name(self):
        once=call('cleanMail',MAIL)
        self.assertEqual(call('cleanMail',once),once)
    def test_payload_drops_html_binary(self):
        m=dict(MAIL);m.pop('text');m.update(html='<script>bad()</script><p>Hola &amp; adiós</p>'+'x'*5000,binary={'file':'private'},headers={'secret':'discard'})
        r=call('cleanMail',m)
        self.assertEqual(set(r),{'From','Subject','BodyText','message_id','thread_id','display_name'})
        self.assertLessEqual(len(r['BodyText']),4000);self.assertNotIn('bad()',r['BodyText']);self.assertTrue(r['BodyText'].startswith('Hola & adiós'))
    def test_lookup_precedes_create(self):
        self.assertEqual(call('crmPlan','test@example.com','Test',[])['action'],'create')
        self.assertEqual(call('crmPlan','test@example.com','',[{'id':'1','properties':{'email':'test@example.com','firstname':'Existing'}}])['action'],'found')
        self.assertEqual(call('crmPlan','test@example.com','Test',[{'id':'1','properties':{'email':'test@example.com'}}])['action'],'update')
        self.assertIn('error',call('crmPlan','test@example.com','Test',[{'id':'1','properties':{'email':'other@example.com'}}]))
    def test_replay_no_second_contact(self):
        r={'request_id':'gmail:msg-001','status':'completed','draft_id':'draft1','contact_id':'contact1'}
        self.assertEqual(call('receiptDecision','gmail:msg-001',[r])['action'],'replay')
        for status in ['processing','delivery_unknown']:
            self.assertEqual(call('receiptDecision','gmail:msg-001',[dict(r,status=status)])['action'],'review')
        self.assertIn('error',call('receiptDecision','gmail:msg-001',[r,r]))
    def test_slack_payload_allowlist(self):
        r=call('reviewPayload',{'request_id':'gmail:x','domain':'aurora_demo','status':'needs_human','reason':'x'*300,'record_reference':'1','body':'private','email':'private'})
        self.assertEqual(set(r),{'request_id','domain','status','reason','record_reference'})
        self.assertEqual(len(r['reason']),200)
    def test_draft_failure_does_not_claim_success(self):
        self.assertEqual(call('draftResult',{'error':'timeout'})['status'],'delivery_unknown')
        self.assertEqual(call('draftResult',{'id':'r1'})['status'],'completed')

class InboxGraph(unittest.TestCase):
    def test_slack_requires_review_and_fixed_recipient(self):
        w=json.loads((ROOT/'drafts/module4/slack_review.json').read_text());n={n['name']:n for n in w['nodes']}
        self.assertIn("$json.status === 'needs_human'",n['Envio autorizado']['parameters']['conditions']['conditions'][0]['leftValue'])
        self.assertEqual(n['Slack revision']['parameters']['select'],'user')
        self.assertEqual(n['Slack revision']['parameters']['user']['value'],'REPLACE_SLACK_REVIEW_USER_ID')
        self.assertEqual(n['Slack revision']['type'],'n8n-nodes-base.slack')
        self.assertFalse(n['Payload minimo']['parameters']['includeOtherFields'])
        fields=n['Payload minimo']['parameters']['assignments']['assignments']
        self.assertEqual({f['name'] for f in fields},{'request_id','domain','status','reason','record_reference'})
    def test_gmail_review_invokes_slack_but_replay_bypasses_it(self):
        w=json.loads((ROOT/'drafts/module4/gmail_message.json').read_text());n={n['name']:n for n in w['nodes']}
        self.assertEqual(w['connections']['Revisar sin enviar']['main'][0][0]['node'],'Necesita notificacion')
        self.assertEqual(n['Necesita notificacion']['parameters']['conditions']['conditions'][0]['leftValue'],'={{ $json.status === "needs_human" }}')
        self.assertEqual(n['Notificar revision Slack']['parameters']['workflowInputs']['value']['request'],'={{ $json.request }}')
        self.assertEqual(w['connections']['Necesita notificacion']['main'][1][0]['node'],'Repeticion sin notificacion')
    def test_batch_isolated_per_message(self):
        w=json.loads((ROOT/'drafts/module4/gmail_inbox.json').read_text());n={n['name']:n for n in w['nodes']}
        self.assertEqual(n['Procesar correo individual']['parameters']['mode'],'each')
        self.assertTrue(n['Procesar correo individual']['parameters']['options']['waitForSubWorkflow'])
        self.assertEqual(n['Procesar correo individual']['parameters']['workflowInputs']['value']['mail'],'={{ $json }}')
    def test_saved_manager_output_enters_draft_branch(self):
        w=json.loads((ROOT/'drafts/module4/gmail_message.json').read_text());n={n['name']:n for n in w['nodes']}
        response={'request_id':'gmail:x','status':'success','output':'El manicure cuesta 180 MXN.','evidence':[],'delivery':'dry_run','memory_status':'saved'}
        expr=n['Respuesta apta']['parameters']['conditions']['conditions'][0]['leftValue'][3:-2].strip()
        script='const $json='+json.dumps(response)+';console.log(JSON.stringify('+expr+'));'
        self.assertTrue(json.loads(subprocess.run(['node','-e',script],capture_output=True,text=True,check=True).stdout))
        self.assertEqual(n['Crear borrador']['parameters']['message'],'={{ $json.output }}')
    def test_guard_and_receipt_precede_side_effects(self):
        w=json.loads((ROOT/'drafts/module4/gmail_inbox.json').read_text());n={n['name']:n for n in w['nodes']}
        self.assertEqual(w['connections']['Gmail Trigger']['main'][0][0]['node'],'Correo permitido')
        self.assertEqual(n['Correo permitido']['type'],'n8n-nodes-base.if')
        self.assertEqual(n['Limpiar correo']['type'],'n8n-nodes-base.set')
        self.assertFalse(n['Limpiar correo']['parameters']['includeOtherFields'])
        w=json.loads((ROOT/'drafts/module4/gmail_message.json').read_text());n={n['name']:n for n in w['nodes']}
        self.assertEqual(w['connections']['Reservar recibo']['main'][0][0]['node'],'Confirmar reserva')
        self.assertEqual(w['connections']['Reserva confirmada']['main'][0][0]['node'],'Payload CRM')
        self.assertEqual(n['Crear borrador']['parameters']['resource'],'draft')
        self.assertEqual(n['Crear borrador']['parameters']['operation'],'create')
        self.assertFalse(any(n['type']=='n8n-nodes-base.gmail' and n['parameters'].get('operation')=='send' for n in w['nodes']))
    def test_crm_error_reconciles_once_without_second_write(self):
        w=json.loads((ROOT/'drafts/module4/crm_contact.json').read_text())
        self.assertEqual(w['connections']['Escritura confirmada']['main'][1][0]['node'],'Reconciliar una vez')
        self.assertEqual(w['connections']['Resultado reconciliado']['main'][0][0]['node'],'CRM Result')

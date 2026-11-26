"""Render module reports from frozen exports and authentic browser captures."""
from pathlib import Path
from html import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1]
S=R.parent/'work/implementation-private/screenshots'
W,H=landscape(A3)
INK=colors.HexColor('#173047'); TEAL=colors.HexColor('#007f80')
def para(c,t,x,y,w,size=13):
 p=Paragraph(t,ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=size*1.35,textColor=INK)); _,h=p.wrap(w,H);p.drawOn(c,x,y-h);return y-h-12

def head(c,n,title,module=3,total=3):
 c.setFillColor(TEAL);c.rect(0,H-13,W,13,fill=1,stroke=0)
 c.setFillColor(INK);c.setFont('Helvetica-Bold',24);c.drawString(40,H-55,title)
 c.setFont('Helvetica',11);c.drawString(40,H-78,f'Estética Aurora | Sara Adan | Módulo {module} | 26 noviembre 2026')
 c.setFont('Helvetica',9);c.drawString(40,23,'Repositorio: github.com/sarafavila97-png/checkpoint1-estetica-aurora');c.drawRightString(W-40,23,f'{n} / {total}')

def pic(c,name,x,y,w,h):
 im=ImageReader(str(S/name)); iw,ih=im.getSize();scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;c.drawImage(im,x+(w-dw)/2,y+(h-dh)/2,dw,dh)

def table(c,rows,x,y,widths):
 style=ParagraphStyle('cell',fontName='Helvetica',fontSize=11,leading=14,textColor=INK)
 data=[[Paragraph(escape(v),style) for v in row] for row in rows]
 t=Table(data,colWidths=widths);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e1eeee')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#cbd5dc'))]));_,h=t.wrap(sum(widths),H);t.drawOn(c,x,y-h);return y-h-15

def m3():
 path=R/'submissions/m03/PreEntrega_Modulo3_SaraAdan.pdf';path.parent.mkdir(parents=True,exist_ok=True)
 c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle('Preentrega Módulo 3 - Memoria persistente - Sara Adan')
 head(c,1,'01 / Canvas completo y ciclo de memoria')
 pic(c,'m3-manager.png',40,185,W-80,H-290)
 y=178
 y=para(c,'<b>Lectura antes del agente.</b> El manager consulta Airtable por Session_ID. La rama IF distingue sesión nueva de existente. El contexto validado se inyecta antes de clasificar la intención y delegar; un fallo de lectura devuelve MEMORY_READ_ERROR.',40,y,W-80)
 y=para(c,'<b>Escritura después de responder.</b> Cada entrada aceptada cuenta una vez. Al sexto mensaje entrante, el modelo resume seis intercambios y la memoria consolidada previa; solo un JSON válido reemplaza el resumen y reinicia el contador. Los reintentos reconocidos no lo incrementan.',40,y,W-80)
 para(c,'Vista general real del canvas. Los JSON completos y las conexiones están en submissions/m03/workflows; el manifiesto de exportación y las observaciones de pruebas están en submissions/m03/evidence.',40,y,W-80,10)
 c.showPage();head(c,2,'02 / Prompt de resumen, contrato y pruebas')
 y=H-110
 prompt=(R/'prompts/summarizer.txt').read_text().strip()
 y=para(c,'<b>Texto del prompt</b>',40,y,W-80,15)
 y=para(c,escape(prompt).replace('\n','<br/>'),40,y,W-80,13)
 y=para(c,'<b>Datos añadidos por el nodo Resumir sesion:</b> Datos JSON: + JSON.stringify($json.summary_input). Incluye previous_summary, key_facts, messages, current_query, current_answer y coverage. La expresión exacta, incluidos sus escapes, se conserva en aurora_manager.json.',40,y,W-80,11)
 y=para(c,'<b>Modelo:</b> gpt-4o; temperatura 0.1; máximo 550 tokens; timeout 45 s; sin reintentos automáticos. Parser estructurado y validación adicional: exactamente tres claves, sin propiedades extra; cadenas no vacías de hasta 200 caracteres; máximo cinco puntos.',40,y,W-80,12)
 rows=[['Prueba observada','Resultado y alcance'],['Seis turnos con resumen real','Contadores 1–5; turno 6 vuelve a 0. El resumen conserva la preferencia de esmalte coral del primer turno.'],['Recuerdo sin buffer','Sesión nueva restaurada solo con campos durables; responde «Preferiste el esmalte coral». Simulación de restauración, no reinicio real del servidor.'],['Aislamiento, duplicados y JSON inválido','Sesiones A/B separadas; reintento no incrementa; resumen inválido conserva el estado anterior.'],['Fallo de dependencia','MEMORY_READ_ERROR sin llamada al modelo; resumen existente intacto.'],['Regresión de datos comerciales','Dos llamadas finales con evidencia de Sheets: manicure 180 MXN y 40 minutos. La prueba preliminar indicó 45 sin fuente; se añadió guardia de evidencia y se repitió.']]
 y=table(c,rows,40,y,[240,W-320])
 para(c,'Evidencia: persistence-batch-observation.json, live-summary-observation.json, cold-recall-observation.json, dependency-fault-observation.json y business-regression-observation.json. Son transcripciones de resultados observados en n8n; no se presentan como exportaciones crudas de ejecuciones.',40,y,W-80,10)
 c.showPage();head(c,3,'03 / Base de datos y metadatos')
 rows=[['Campo exacto','Tipo en Airtable','Uso'],['Session_ID','Texto de una línea','Clave lógica dominio:canal:sesión; búsqueda exacta. Más de un registro coincidente se rechaza.'],['Fecha de actualización','Fecha y hora','Marca temporal ISO al persistir.'],['Resumen consolidado','Texto largo','Objeto JSON validado: asunto_principal, puntos_clave, accion_requerida. Vacío hasta el primer resumen.'],['Estado del caso','Selección única','nuevo, en_curso, requiere_revision o cerrado.'],['Datos clave','Texto largo','JSON: display_name, accepted_message_count, last_request_ids, key_facts.']]
 y=table(c,rows,40,H-110,[190,155,W-425])
 y=para(c,'<b>Metadatos:</b> display_name hasta 100 caracteres; contador entre 0 y 5; hasta 20 request_id recientes sin duplicados; hasta cinco hechos clave de 200 caracteres. La deduplicación cubre esa ventana reciente, no un registro ilimitado. Las conversaciones completas no se guardan en Airtable.',40,y,W-80,12)
 y=para(c,'<b>Separación de contexto:</b> el dominio y el canal forman parte de Session_ID. La memoria se delimita como datos no confiables; se escapan caracteres de delimitación. El recuerdo personal usa el resumen validado; precios y duraciones exigen evidencia actual de Sheets.',40,y,W-80,12)
 pic(c,'m3-airtable.png',40,55,W-80,max(100,y-65))
 c.save();print(path)


def m2(draft=True):
 path=R/('tmp/pdfs/m02-report-draft.pdf' if draft else 'submissions/m02/preentrega_modulo2_adan_sara.pdf')
 path.parent.mkdir(parents=True,exist_ok=True)
 c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle('Preentrega Módulo 2 - Orquestación - Sara Adan')
 pages=[
 ('01 / Manager y delegación','m2-manager.png','El manager valida la solicitud, clasifica la intención y delega secuencialmente. AURORA_INFO consulta conocimiento y después redacción; CLARIFY solicita precisión; HUMAN deriva a revisión. Una salida del router inválida toma la contingencia segura.','El flujo conserva la separación de responsabilidades: el manager decide la ruta; el worker de conocimiento obtiene evidencia; el redactor prepara la respuesta. El manager devuelve el resultado al canal de entrada.'),
 ('02 / Worker de conocimiento','m2-knowledge.png','Subworkflow independiente con Execute Workflow Trigger. Recibe únicamente el objeto request. El agente consulta la herramienta nativa Google Sheets y devuelve un WorkerResult normalizado con respuesta, evidencia, acción propuesta y error.','La evidencia se identifica como aurora_sheet y pertenece al dominio aurora_demo. La información es ficticia para la práctica. No se reservan citas, procesan pagos ni inventan descuentos.'),
 ('03 / Worker de redacción','m2-writer.png','Subworkflow independiente con Execute Workflow Trigger. Redacta utilizando únicamente la evidencia recibida y devuelve un contrato WorkerResult. No añade hechos ni ejecuta acciones externas.','El manejo de error nativo continúa hacia la normalización: WRITER_ERROR y proposed_action=review. El manager no presenta una respuesta fallida como válida.'),
 ('04 / Payload mínimo y espera','m2-wait-contract.png','Antes de cada Execute Workflow, un nodo visual Set/Edit Fields conserva solo request. El mapeo es request = {{ $json.request }} y Wait For Sub-Workflow Completion está activado. Cada worker recibe un objeto tipado.','El parser del router admite exactamente AURORA_INFO, CLARIFY o HUMAN. WorkerResult incluye schema_version, request_id, status, domain, result y error; result contiene answer, evidence y proposed_action. Los contratos se validan antes de continuar.'),
 ('05 / Evidencia de éxito','m2-success.png','Prueba chat:m2-001: consulta de precio de manicure. Resultado success, respuesta 180 MXN con evidencia de Aurora/Base/0. Se observó la secuencia manager, conocimiento y redacción.','La entrega de esta prueba fue dry_run: valida la orquestación, no un envío externo. La salida completa está en submissions/m02/evidence/m2-001-output.json. No se atribuye a esta ejecución un correo enviado.'),
 ('06 / Error interno controlado','m2-worker-error.png','Captura de una copia aislada del redactor con entrada sintética: M2_CONTROLLED_WRITER_FAILURE se lanza antes de invocar el LLM. El worker devuelve status=error, WRITER_ERROR, retryable=false y proposed_action=review. El worker original no se modificó.','La captura no corresponde a la ejecución histórica del manager. Aquella prueba, transcrita en worker-internal-error-observation.json, devolvió revisión humana; después se restauró el prompt y pasó la regresión. La nueva captura se documenta en isolated-worker-error-capture.json. La paridad del worker original se verificó por separado.')]
 for i,(title,img,a,b) in enumerate(pages,1):
  head(c,i,title,2,7)
  if (S/img).exists():pic(c,img,40,190,W-80,H-295)
  else:
   if not draft:raise RuntimeError('Required authentic screenshot missing: '+img)
   para(c,'BORRADOR: falta captura auténtica '+escape(img),60,H/2,W-120,22)
  y=para(c,escape(a),40,175,W-80,13);para(c,escape(b),40,y,W-80,12)
  c.showPage()
 head(c,7,'07 / Validación y reproducción',2,7)
 rows=[['Caso','Observación'],['Consulta de precio','180 MXN, evidencia Sheets y success.'],['Mensaje ambiguo: Hola','CLARIFY; solicita el servicio de interés.'],['Solicitud de reserva','HUMAN; no ejecuta ninguna reserva.'],['ID de worker inexistente','WORKER_ERROR; contingencia del manager.'],['Fallo dentro del redactor','WRITER_ERROR estructurado; revisión humana; configuración restaurada.']]
 y=table(c,rows,40,H-120,[250,W-330])
 for text in [
 '<b>Importación.</b> Importar primero los dos workers y luego el manager; volver a enlazar los IDs de subworkflow. Asignar las credenciales de OpenAI y Sheets, y sustituir REPLACE_AURORA_SHEET_ID. Los tres JSON están en submissions/m02/workflows.',
 '<b>Paridad.</b> Los snapshots corresponden a las exportaciones alojadas probadas, con credenciales excluidas y el ID de la hoja sustituido. El manifiesto hosted-export-manifest.json registra las huellas. El verificador scripts/verify_module2_exports.py compara configuración y conexiones.',
 '<b>Operación.</b> Workflows guardados e inactivos, timeout de 180 segundos. Las pruebas se ejecutaron de forma controlada. Las capturas son evidencia visual de la UI; las observaciones JSON son transcripciones y se etiquetan como tales.',
 '<b>Alcance.</b> Este checkpoint demuestra la orquestación y sus contratos. Las versiones posteriores incorporan memoria e integraciones sin reemplazar este snapshot de entrega.'
 ]:y=para(c,text,40,y,W-80,13)
 c.save();print(path)

if __name__=='__main__':
 import sys
 if '--m2' in sys.argv:m2('--final' not in sys.argv)
 else:m3()

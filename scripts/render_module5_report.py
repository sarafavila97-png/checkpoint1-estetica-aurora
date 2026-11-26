"""Render M5's five evidence sections; require authentic source/prompt captures."""
import argparse
import json
from html import escape
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from render_module_reports import R, W, H, head, para, table


def picture(c, path, bottom=190):
    im = ImageReader(str(path))
    iw, ih = im.getSize()
    scale = min((W-80)/iw, (H-bottom-105)/ih)
    dw, dh = iw*scale, ih*scale
    c.drawImage(im, (W-dw)/2, bottom+(H-bottom-105-dh)/2, dw, dh)


def render(source_images, prompt_image):
    evidence = R/'evidence/module5'
    captures = evidence/'screenshots'
    required = source_images+[prompt_image, captures/'native-retriever-controls.png', captures/'score-preserving-config.png']
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    results = json.loads((evidence/'blind-evaluation.json').read_text())
    assert len(results['cases']) == 5
    assert sum(x['correct'] for x in results['cases']) == results['correct_count']
    out = R/'submissions/m05/PreEntrega_Modulo5_SaraAdan.pdf'
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=(W,H))
    c.setTitle('PreEntrega Módulo 5 — Outer Agent — Sara Adan')
    total = len(source_images)+7
    page = 0

    def start(title):
        nonlocal page
        if page:
            c.showPage()
        page += 1
        head(c,page,title,5,total)

    for i, path in enumerate(source_images,1):
        start(f'01 / Fuente documental y parsing — captura {i}')
        picture(c,path)
        y=para(c,'<b>Documento:</b> Outer_Agent_Fuente_Organizacional_v1.pdf, diez páginas, síntesis académica en español de nueve páginas públicas de una organización real. Seleccionado por sus servicios, condiciones publicadas, tablas y preguntas frecuentes. Versión del 25 de noviembre de 2026, pendiente de ratificación comercial del propietario.',40,175,W-80,12)
        para(c,'Captura auténtica de LlamaCloud. El corpus conserva títulos y contenido tabular para recuperar información con páginas verificables. No contiene las preguntas reservadas ni sus respuestas esperadas. La copia del PDF fuente se entrega en source/.',40,y,W-80,12)

    start('02 / Integración de LlamaCloud')
    picture(c,captures/'native-retriever-controls.png')
    y=para(c,'<b>Integración documental.</b> El índice de LlamaCloud concentra la fuente de Outer Agent. El conector instalado permite seleccionar índice, consulta y Top-K. La recuperación implementada usa el endpoint oficial mediante un adaptador que conserva puntuaciones, páginas y metadatos para validar cada respuesta.',40,175,W-80,12)
    para(c,'El Tools Agent accede al adaptador mediante una herramienta lateral de workflow. La consulta se fija por el sistema y el filtro de puntuación se aplica de forma determinista antes de devolver evidencia al agente. La página siguiente muestra la configuración efectiva.',40,y,W-80,12)

    start('02 / Recuperación con puntuaciones y páginas')
    picture(c,captures/'score-preserving-config.png')
    y=para(c,'<b>Configuración congelada:</b> Top-K = 3; Minimum Score = 0,5 aplicado a rerank_score devuelto por el endpoint oficial. En desarrollo, resultados pertinentes puntuaron 0,70–0,82 y una consulta ajena menos de 0,004. No es una probabilidad ni una garantía general de exactitud.',40,175,W-80,12)
    para(c,'El score híbrido y rerank_score tienen escalas distintas: enviar score_threshold=0.5 a la API eliminó resultados pertinentes. El adaptador conserva la respuesta, filtra rerank_score y valida archivo, rango de páginas y chunk antes de permitir citas. Top-K 3 acota los tokens de contexto y su costo; el umbral 0,5 filtra fragmentos de menor relevancia, con el riesgo de reducir cobertura. Ambos valores se congelaron antes de la prueba ciega, cuyo resultado observado se conserva: 2/5 (40%).',40,y,W-80,12)

    start('03 / System Prompt: configuración alojada')
    picture(c,prompt_image,150)
    para(c,'Captura auténtica del prompt del agente. El texto íntegro se reproduce en la página siguiente. El modelo usa solo evidencia recuperada en el turno, distingue dominios y entrega un objeto estructurado; un paso determinista añade las referencias verificadas.',40,135,W-80,12)

    start('03 / System Prompt íntegro y contrato')
    prompt=(R/'prompts/outer_agent_rag.txt').read_text().strip()
    y=para(c,escape(prompt).replace('\n','<br/>'),40,H-110,W-80,12)
    y=para(c,'<b>Contexto añadido por el nodo:</b> después del texto base se concatena CONTEXTO NO CONFIABLE y $json.context_prompt, que contiene la memoria delimitada. La expresión exacta se conserva en el export alojado y en la captura anterior.',40,y,W-80,11)
    y=para(c,'<b>Contrato:</b> supported (boolean), answer (string), source_ids (array); sin propiedades adicionales. Los IDs deben existir en la evidencia de la llamada real. El sistema agrega documento y páginas; no acepta páginas generadas por el modelo. Un fallo no se transforma en una respuesta comercial.',40,y,W-80,12)
    assert y>55, ('prompt overflow',y)

    start('04 / Reporte de Validación — cinco pruebas ciegas')
    y=para(c,f'<b>Precisión medida: {results["correct_count"]}/5 = {results["precision"]:.0%}.</b> Primera ronda, configuración y prompt congelados. El agente recibió únicamente preguntas. Se conservaron fallos; no se ajustó el umbral ni se sustituyeron ejecuciones después de abrir los casos.',40,H-110,W-80,13)
    short={
      'T1':('Sin fragmento entregado; derivación humana.','Escalamiento innecesario. La tabla documenta el crédito de 2.500 y saldo de 15.500 en el ejemplo.'),
      'T2':('Sin evidencia entregada.','Abstención incorrecta: el documento contempla equipos sin área técnica.'),
      'T3':('«El sitio publica respuesta el mismo día cuando falla un flujo, pero no define un plazo de resolución garantizado.» PDF pp. 8–9, OA-09.6; también pp. 6–7.','Correcto: respuesta el mismo día no equivale a resolución garantizada.'),
      'T4':('Sin evidencia entregada.','Abstención incompleta: el documento distingue escenarios ilustrativos de resultados reales.'),
      'T5':('Sin fuente que documente un número de certificado.','Correcto: No sé, sin inventar certificación.')}
    rows=[['Caso / pregunta','Fragmento recuperado','Respuesta observada','Veredicto']]
    for case in results['cases']:
        actual=case['actual']['output']
        if case['case_id']=='T3':
            actual=actual.split('\nFuente:')[0]
        source, verdict=short[case['case_id']]
        rows.append([case['case_id']+' — '+case['query'],source,actual,verdict])
    y=table(c,rows,40,y,[260,210,370,W-920])
    y=para(c,'Para T1, T2 y T4 no se conserva un fragmento interno rechazado: no se inventa cuál se recuperó ni por qué fue descartado. Las respuestas completas, citas y extractos entregados están en blind-results-raw.json y blind-evaluation.json.',40,y,W-80,10)
    assert y>45, ('evaluation overflow',y)

    start('04 / Análisis de fallos y límites de la medición')
    rows=[['Hallazgo observado','Acción correctiva propuesta; no aplicada a la medición ciega'],['T1: consulta informativa enviada a revisión','Distinguir preguntar por una condición publicada de ordenar un pago o cambio. Añadir ejemplos de desarrollo al router y probar con preguntas nuevas.'],['T2 y T4: abstenciones sobre contenido disponible','Instrumentar candidatos recuperados, puntuaciones y decisión de suficiencia por separado. Revisar granularidad de chunks y cobertura semántica antes de atribuir el fallo al umbral.'],['Citas extensas en T3','Mantener página verificable y precisar el apartado realmente pertinente; no listar todos los títulos de un chunk como si cada uno respaldara la afirmación.'],['Preservación de puntuaciones y metadatos','Mantener el adaptador al endpoint oficial y comprobar el contrato de respuesta en cada actualización del proveedor.']]
    y=table(c,rows,40,H-110,[330,W-410])
    for text in [
      '<b>Interpretación:</b> 40% mide corrección contra la fuente en cinco casos; no es la puntuación del juez ni una estimación de precisión general. Dos abstenciones fueron incorrectas; la abstención por certificado no documentado sí fue correcta.',
      '<b>Coste y latencia:</b> duración total observada 32,338 segundos. No hay latencia individual ni facturación real devuelta por este arnés; esos valores son desconocidos, no cero.',
      '<b>Regresión:</b> el manager mantuvo 180 MXN / 40 minutos para Aurora, conservó citas de Outer Agent y pidió aclaración en dos consultas cruzadas. Dos banderas iniciales del arnés fallaron por esperar evidence=[] cuando el campo se omitía; se conservó esa distinción en la evidencia.',
      '<b>Paridad:</b> snapshots de retriever (5 nodos), agente (7) y manager (48) comparados con exports alojados; timeout 180 s y almacenamiento de ejecuciones desactivado. Los secretos no se incluyen en la entrega.'
    ]:y=para(c,text,40,y,W-80,13)
    assert y>45, ('analysis overflow',y)

    start('05 / Plan de gobernanza del conocimiento')
    rows=[['Elemento','Plan propuesto'],['Responsables','Sara mantiene la versión académica, índice y regresiones. El propietario ratifica políticas comerciales no publicadas. No supone aceptación formal de obligaciones.'],['Revisión','Cada 30 días y ante cambios, contradicciones, URLs caídas o información obsoleta. Primera revisión prevista: 25 diciembre 2026; no es una automatización programada.'],['Actualización','Comparar fuentes; registrar URL, fecha y cambio; preparar versión nueva; revisar títulos/tablas y hash; cargar en índice de validación; comprobar páginas y metadatos.'],['Promoción y reversión','Congelar parámetros; probar consulta con cita, desconocida, cruce de dominios e instrucciones maliciosas. Promover solo si valida; conservar referencia anterior y revertir ante atribución defectuosa.'],['Separación','No indexar preguntas reservadas, expectativas, informes de evaluación, conversaciones, claves ni audio. Outer Agent y Aurora mantienen fuentes y sesiones separadas.'],['Registro por versión','PDF/hash, URLs, fecha, cambios, índice, prueba de correspondencia, parámetros, hash de workflow, resultados reales y decisión de promoción o reversión.']]
    y=table(c,rows,40,H-110,[210,W-290])
    y=para(c,'<b>Fuente v1:</b> diez páginas; SHA-256 6c96c3df7a36e4534bdb413a217629538cf02be62231f18c2358c09453c2dee4. El hash local identifica el archivo, pero no prueba por sí solo el contenido del índice. La captura de LlamaCloud y la validación de páginas son evidencia complementaria.',40,y,W-80,11)
    y=para(c,'Plan detallado: docs/knowledge-governance.md. Las carencias de información se mantienen explícitas: no inferir moneda, impuestos, garantías de resolución, certificaciones ni resultados reales a partir de ejemplos. Sin evidencia pertinente, responder «No sé».',40,y,W-80,12)
    assert y>45, ('governance overflow',y)
    assert page==total
    c.save()
    print(out)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-image',type=Path,action='append',required=True)
    p.add_argument('--prompt-image',type=Path,required=True)
    a=p.parse_args()
    render(a.source_image,a.prompt_image)

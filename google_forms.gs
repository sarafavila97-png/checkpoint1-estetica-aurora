// Sara Adan — Checkpoint 1. Datos ficticios para una práctica académica.
// La clave se guarda en Propiedades del script, nunca en este archivo.
const WEBHOOK_URL = 'https://sarafavila.app.n8n.cloud/webhook/estetica-aurora-checkpoint1';

function crearFormulario() {
  const props = PropertiesService.getScriptProperties();
  let id = props.getProperty('FORM_ID');
  if (!id) {
    const form = FormApp.create('Estética Aurora — consultas de práctica', false);
    props.setProperty('FORM_ID', form.getId());
    form.setDescription('Negocio ficticio. Consulta servicios, precios y horarios de ejemplo. Recibirás una respuesta automática por correo. No ingreses datos sensibles; no se reservan citas.');
    form.setCollectEmail(true);
    form.addParagraphTextItem().setTitle('Consulta').setRequired(true)
      .setHelpText('Escribe de 1 a 800 caracteres.')
      .setValidation(FormApp.createParagraphTextValidation().requireTextLengthLessThanOrEqualTo(800).build());
    form.setConfirmationMessage('Consulta recibida. Revisa tu correo para ver la respuesta de la demostración.');
    id = form.getId();
  }
  console.log('Editar formulario: ' + FormApp.openById(id).getEditUrl());
}

function activarConexion() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('FORM_ID');
  if (!id || !props.getProperty('WEBHOOK_SECRET')) {
    throw new Error('Primero crea el formulario y configura WEBHOOK_SECRET en Propiedades del script.');
  }
  const existe = ScriptApp.getProjectTriggers().some(t => t.getHandlerFunction() === 'enviarConsulta');
  if (!existe) ScriptApp.newTrigger('enviarConsulta').forForm(id).onFormSubmit().create();
  const form = FormApp.openById(id);
  form.setPublished(true);
  console.log('Formulario: ' + form.getPublishedUrl());
}

function enviarConsulta(evento) {
  if (!evento || !evento.response) throw new Error('Esta función se ejecuta al enviar el formulario.');
  const respuesta = evento.response;
  const pregunta = respuesta.getItemResponses().find(r => r.getItem().getTitle() === 'Consulta');
  const consulta = String(pregunta ? pregunta.getResponse() : '').trim();
  const correo = respuesta.getRespondentEmail();
  if (!consulta || consulta.length > 800 || !correo) throw new Error('Consulta o correo no válidos.');
  const clave = PropertiesService.getScriptProperties().getProperty('WEBHOOK_SECRET');
  if (!clave) throw new Error('Falta WEBHOOK_SECRET.');
  const resultado = UrlFetchApp.fetch(WEBHOOK_URL, {
    method: 'post', contentType: 'application/json',
    headers: {'X-Aurora-Token': clave},
    payload: JSON.stringify({consulta, correo}),
    muteHttpExceptions: true
  });
  const estado = resultado.getResponseCode();
  if (estado < 200 || estado >= 300) throw new Error('n8n devolvió HTTP ' + estado + '. Revisa Executions; no se reintenta para evitar correos duplicados.');
  console.log('Consulta enviada correctamente a n8n. HTTP ' + estado);
}

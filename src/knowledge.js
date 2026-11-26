'use strict';

function sheetEvidence(steps) {
  if (!Array.isArray(steps) || steps.length !== 1 ||
      steps[0]?.action?.tool !== 'Consultar_informacion_estetica') {
    throw Error('SHEET_TOOL_CALL_REQUIRED');
  }
  let rows=steps[0].observation;
  if (typeof rows==='string') {
    if (!rows.trim()) throw Error('EMPTY_SHEET_OBSERVATION');
    try { rows=JSON.parse(rows); } catch { throw Error('INVALID_SHEET_OBSERVATION'); }
  }
  if (!Array.isArray(rows) || rows.length===0) throw Error('EMPTY_SHEET_OBSERVATION');
  rows=rows.map(row=>row?.json||row);
  if (rows.some(row=>!row || row.error || typeof row.clave!=='string' || !row.clave.trim() ||
      typeof row.informacion!=='string' || !row.informacion.trim())) {
    throw Error('INVALID_SHEET_ROWS');
  }
  const text=JSON.stringify(rows);
  if (text.length>12000) throw Error('SHEET_EVIDENCE_TOO_LARGE');
  return [{source_id:'Aurora/Base/current',source_kind:'aurora_sheet',text,section:'Base',
    page_start:null,page_end:null,score:null,source_version:'M1'}];
}

module.exports={sheetEvidence};

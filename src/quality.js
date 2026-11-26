'use strict';

// Caller supplies the manager-owned counter. Never read the counter from LLM output.
// This decision is not permission to send: channel validation and delivery gates
// must also pass, and an ESCALAR result must reach the human-review workflow.
function decideJudge(raw, correctionAttempt = 0) {
  const validAttempt = Number.isInteger(correctionAttempt) && correctionAttempt >= 0 && correctionAttempt <= 2;
  const attempt = validAttempt ? correctionAttempt : null;
  const decision = (route, score, reason, feedback = '') => ({
    route, score, attempt,
    next_attempt: route === 'CORREGIR' ? attempt + 1 : attempt,
    reason, feedback,
  });
  if (!validAttempt) return decision('ESCALAR', null, 'INVALID_ATTEMPT');
  if (!raw || typeof raw !== 'object' || Array.isArray(raw) ||
      Object.keys(raw).sort().join('|') !== 'estado_veredicto|exactitud_factual') {
    return decision('ESCALAR', null, 'INVALID_JUDGE_SCHEMA');
  }
  const score = raw.exactitud_factual;
  const verdict = raw.estado_veredicto;
  if (!Number.isInteger(score) || score < 1 || score > 5 ||
      !['APROBADO', 'CORREGIR', 'ESCALAR'].includes(verdict)) {
    return decision('ESCALAR', null, 'INVALID_JUDGE_VALUE');
  }
  if (verdict === 'ESCALAR') return decision('ESCALAR', score, 'JUDGE_ESCALATION');
  if (verdict === 'APROBADO') {
    return score >= 4 ? decision('APROBADO', score, 'SUPPORTED_ANSWER') :
      decision('ESCALAR', score, 'SCORE_VERDICT_CONFLICT');
  }
  if (score < 2 || score > 3) return decision('ESCALAR', score, 'SCORE_VERDICT_CONFLICT');
  if (attempt >= 2) return decision('ESCALAR', score, 'CORRECTION_LIMIT');
  const feedback = score === 2
    ? 'Elimina afirmaciones sustanciales sin respaldo. Reescribe usando solo la consulta, el contexto y las fuentes originales; si falta evidencia, indica No sé.'
    : 'Corrige omisiones o ambigüedades usando solo la consulta, el contexto y las fuentes originales. No agregues hechos ni cambies las restricciones del canal.';
  return decision('CORREGIR', score, 'REVISE_WITH_SAME_EVIDENCE', feedback);
}

module.exports = { decideJudge };

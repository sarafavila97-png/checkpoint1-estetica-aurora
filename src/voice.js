'use strict';

// Academic demo limits, not provider limits. Caller checks update_id in the
// durable receipt ledger before download and owns the Telegram webhook.
function voiceInput(update, allowedChatIds) {
  const fail = reason => ({ok:false,reason});
  const chatId=update?.message?.chat?.id;
  if (!Array.isArray(allowedChatIds) || !Number.isSafeInteger(chatId) ||
      !allowedChatIds.map(String).includes(String(chatId))) return fail('CHAT_NOT_ALLOWED');
  if (!Number.isSafeInteger(update.update_id) || update.update_id < 0) return fail('INVALID_UPDATE_ID');
  const v=update.message.voice;
  if (!v || typeof v.file_id !== 'string' || !v.file_id.trim()) return fail('MISSING_VOICE');
  if (typeof v.duration !== 'number' || !Number.isFinite(v.duration) || v.duration <= 0 || v.duration > 30 ||
      !Number.isSafeInteger(v.file_size) || v.file_size <= 0 || v.file_size > 5*1024*1024) return fail('AUDIO_LIMIT_OR_UNKNOWN_SIZE');
  return {ok:true,update_id:update.update_id,chat_id:String(chatId),file_id:v.file_id};
}

function transcriptText(result) {
  if (!result || result.error || typeof result.text !== 'string' || !result.text.trim()) {
    return {ok:false,reason:'EMPTY_OR_FAILED_TRANSCRIPTION'};
  }
  // Return only text; never forward a provider response or attached binary.
  return {ok:true,text:result.text.trim()};
}

function speechText(value) {
  const fail=reason=>({ok:false,reason});
  if (typeof value !== 'string' || !value.trim()) return fail('EMPTY_SPEECH');
  const text=value.trim(),characters=Array.from(text).length;
  if (characters>200) return fail('SPEECH_TOO_LONG');
  if (/[\r\n]/.test(text) || /(?:https?:\/\/|www\.)/i.test(text) ||
      /(?:^|\s)[a-z0-9-]+\.[a-z]{2,63}(?:\b|\/)/i.test(text) ||
      /[*_`#\[\]<>]/.test(text) || /^(?:[-+•‣▪]|\d+[.)])\s*/u.test(text) ||
      /\p{Extended_Pictographic}|\p{Regional_Indicator}|[0-9#*]\uFE0F?\u20E3/u.test(text)) {
    return fail('SPEECH_FORMAT_FORBIDDEN');
  }
  // Do not truncate: the caller may perform one bounded rewrite and revalidate.
  return {ok:true,text,characters};
}

module.exports={voiceInput,transcriptText,speechText};

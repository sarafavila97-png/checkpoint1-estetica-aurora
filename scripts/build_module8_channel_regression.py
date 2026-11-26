"""Prepare final Gmail two-message regression: four drafts, no sends; run once."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'work/implementation-private';D=P/'module6-drafts'
w=json.loads((P/'module4-drafts/inbox_batch_test.json').read_text())
raw=json.dumps(w,ensure_ascii=False).replace('Aurora M4 - Prueba lote dos correos','Aurora M8 - Regresion final dos correos').replace('wtvU9RXoJigPHsIG','HN9WViRuCuat7IGF').replace('m4-batch-v1-','m8-batch-v1-').replace('m4-two-message-batch','m8-final-two-message-batch').replace('M4 prueba sintetica','M8 prueba sintetica')
# Reuse established synthetic test contacts; new message IDs and real seed threads.
w=json.loads(raw);(D/'m8_channel_regression.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n')
print('Prepared final-channel batch; four draft creations, zero email sends. Do not blindly rerun.')

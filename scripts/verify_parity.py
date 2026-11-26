"""Compare a private n8n export to this public submission without printing secrets."""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def public_export(hosted):
    result = copy.deepcopy(hosted)
    for key in ('id', 'versionId', 'meta', 'nodeGroups', 'tags'):
        result.pop(key, None)
    for node in result['nodes']:
        node.pop('credentials', None)
        if node['name'] == 'Preparar consulta':
            code = node['parameters']['jsCode']
            code, count = re.subn(r"const correo_reportes = '[^'\n]+';", "const correo_reportes = 'REEMPLAZAR_CORREO_REPORTES';", code)
            assert count == 1, 'Expected exactly one reporting-address assignment'
            node['parameters']['jsCode'] = code
    return result

if __name__ == '__main__':
    public = json.loads((ROOT / 'checkpoint1_sara_adan.json').read_text())
    hosted = json.loads(Path(sys.argv[1]).read_text())
    assert public_export(hosted) == public, 'Public export differs beyond documented substitutions'
    nodes = {n['name']: n for n in public['nodes']}
    agent = nodes['Agente de consultas']
    assert 5 <= agent['parameters']['options']['maxIterations'] <= 10
    assert agent['parameters']['options']['returnIntermediateSteps'] is True
    assert agent['parameters']['options']['systemMessage'].strip() == (ROOT / 'system_message.txt').read_text().strip()
    for source, port in [('GPT-4', 'ai_languageModel'), ('Consultar_informacion_estetica', 'ai_tool')]:
        assert public['connections'][source][port][0][0]['node'] == 'Agente de consultas'
    assert not any('credentials' in n for n in public['nodes'])
    assert public['settings']['executionTimeout'] == 180
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', json.dumps(public))
    print('PASS: exact normalized hosted/public parity; 13 nodes; native model/tool ports; iteration cap; intermediate evidence; prompt parity; 180-second timeout; no email addresses or credential references.')

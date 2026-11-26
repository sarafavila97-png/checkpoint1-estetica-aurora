"""Compare public M2 snapshots with locally downloaded hosted exports."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT.parent / 'work' / 'implementation-private'
PAIRS = [
    ('manager-hosted-verified.json', 'aurora_manager.json'),
    ('knowledge-hosted-verified.json', 'workers/aurora_knowledge.json'),
    ('writer-hosted-restored.json', 'workers/response_writer.json'),
]

def public_snapshot(hosted):
    result = {key: copy.deepcopy(hosted[key]) for key in ['name', 'nodes', 'connections', 'settings']}
    result.update(active=False, pinData={})
    for node in result['nodes']:
        node.pop('credentials', None)
        if node['type'] == 'n8n-nodes-base.googleSheetsTool':
            node['parameters']['documentId']['value'] = 'REPLACE_AURORA_SHEET_ID'
    return result

def verify():
    manifest = json.loads((ROOT / 'evidence/module2/hosted-export-manifest.json').read_text())
    for private_name, public_name in PAIRS:
        hosted = json.loads((PRIVATE / private_name).read_text())
        public_path = ROOT / 'workflows' / public_name
        public = json.loads(public_path.read_text())
        assert public_snapshot(hosted) == public, public_name + ': hosted parity mismatch'
        record = next(row for row in manifest if row['file'] == public_name)
        assert hashlib.sha256(public_path.read_bytes()).hexdigest() == record['sha256']
        assert hosted['settings']['executionTimeout'] == 180
        assert hosted['settings']['saveDataErrorExecution'] == 'none'
        assert hosted['settings']['saveDataSuccessExecution'] == 'none'
        assert hosted['settings']['saveManualExecutions'] is False
        for node in public['nodes']:
            assert 'M2_CONTROLLED' not in json.dumps(node)
            if node['type'] == 'n8n-nodes-base.executeWorkflow':
                assert node['parameters']['workflowInputs']['value']['request'] == '={{ $json.request }}'
                assert node['parameters']['options']['waitForSubWorkflow'] is True
        print(f'PASS {public_name}: {len(public["nodes"])} nodes, exact sanitized hosted parity, 180s, no execution history')

if __name__ == '__main__':
    verify()

"""Build a public source package without reading production state or credentials."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
REPO = 'https://github.com/huy1907ddddddd/etsy-workflow-updates'
RUNTIME_DIRS = ('flow-worker', 'batch-worker', 'chatgpt-worker', 'kpi-worker', 'web-review', 'lark-review', 'telegram-review')
MODULES = (
    'production-engine.py', 'production-worker.cjs', 'production_batch.py',
    'production_batch_controls.py', 'production_batch_delete.py', 'production_design.py',
    'production_profiles.py', 'flow_worker_pool.py', 'flow_lark_orchestration.py',
    'chatgpt_image_orchestration.py', 'batch_reference.py', 'delivery_layout.py',
    'embroidery_direct.py', 'embroidery_layout.py', 'embroidery_mockup_layout.py',
    'embroidery_region_map.py', 'google_delivery.py', 'local_delivery.py',
    'kpi_sync_orchestration.py', 'pajama_set.py', 'mockup_prompt_sets.py',
    'thumbnail_copy.py', 'title_uniqueness.py', 'review_transport.py', 'review-transport.cjs',
    'workflow-error-stop.cjs', 'workflow-error-stop.test.cjs',
    'codex-title-description-worker.cjs', 'codex-title-description-worker.test.cjs',
    'codex-pilot-bridge.cjs', 'codex-keyword-worker.cjs', 'codex-listing-worker.cjs',
)
CONFIGS = (
    'apparel-listing-defaults.json', 'artwork-flow-prompts.json',
    'embroidery-front-back-mockups-v1.json', 'embroidery-front-back-mockups-v2.json',
    'embroidery-layout-standard.json', 'embroidery-size-standard.json',
    'listing-seo-standard.json',
    'mockup-wardrobe-standard.json', 'thumbnail-copy.json', 'title-uniqueness.json',
)
DOCS = (
    'direct-embroidery-prompt-to-mockup.md', 'embroidered-apparel-six-mockups.md',
    'mockup-prompt-presets.md', 'CHUAN_KICH_THUOC_THEU.md',
)
EXTENSIONS = {'.cjs', '.mjs', '.js', '.py', '.ps1', '.cmd', '.json', '.md', '.html', '.css', '.svg'}
SECRET_RULES = (
    re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    re.compile(r'\bAIza[A-Za-z0-9_-]{30,}\b'),
    re.compile(r'\b\d{7,12}:[A-Za-z0-9_-]{30,}\b'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    re.compile(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b'),
)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def selected(source):
    result = set()
    for name in RUNTIME_DIRS:
        for file in (source / 'scripts' / name).rglob('*'):
            rel = file.relative_to(source)
            if any(p in ('node_modules', '__pycache__', '.git') for p in rel.parts):
                continue
            if file.is_file() and file.suffix in EXTENSIONS and '.private.' not in file.name:
                result.add(rel.as_posix())
    for name in MODULES:
        result.add('scripts/' + name)
    for file in (source / 'scripts').glob('check-*.py'):
        result.add(file.relative_to(source).as_posix())
    for name in CONFIGS:
        result.add('config/' + name)
    for name in DOCS:
        result.add('docs/' + name)
    return sorted(result)

def build(source, version, register_version):
    if not re.fullmatch(r'\d{4}\.\d{2}\.\d{2}\.\d+', version):
        raise ValueError('Version must be YYYY.MM.DD.N')
    if not re.fullmatch(r'V\d+', register_version):
        raise ValueError('Register version must be V followed by digits')
    bindings = {}
    for name in ('listing-layout.json', 'kpi-layout.json', 'google-delivery.json'):
        config = source / 'config' / name
        if config.is_file():
            for key, value in json.loads(config.read_text(encoding='utf-8-sig')).items():
                if isinstance(value, str) and len(value) >= 6 and (key.endswith(('_id', '_token')) or key == 'url'):
                    bindings[value] = 'LOCAL_BINDING_' + key.upper()
    contents = []
    remapped = {}
    for rel in selected(source):
        parts = Path(rel).parts
        if not parts or parts[0] not in ('scripts', 'docs', 'config') or '..' in parts or '.private.' in rel or any(p in ('node_modules', '__pycache__', '.git') for p in parts):
            raise ValueError('Disallowed export path: ' + rel)
        file = source / rel
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(source):
            raise ValueError('Invalid source path: ' + rel)
        data = file.read_bytes()
        text = data.decode('utf-8-sig')
        if any(rule.search(text) for rule in SECRET_RULES):
            raise ValueError('Possible credential in ' + rel)
        # Personal account bindings are local, even when embedded in an old helper.
        emails = re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text)
        if any(not re.search(r'@(example\.(?:com|org|net|invalid)|test\.(?:invalid|local))$', e, re.I)
               and not (file.name.endswith('.test.cjs') and e == 'password@flow.google.com') for e in emails):
            raise ValueError('Review account/contact literal before public export: ' + rel)
        public_text = text
        for value, replacement in sorted(bindings.items(), key=lambda p: -len(p[0])):
            public_text = public_text.replace(value, replacement)
        public_text = re.sub(r'https?://[A-Za-z0-9.-]+\.larksuite\.com/(wiki|docx|sheets)/[A-Za-z0-9_-]{20,}',
                             r'https://local-workspace.invalid/\1/LOCAL_DESTINATION_REQUIRED', public_text)
        public_text = re.sub(r'https://docs\.google\.com/(document|spreadsheets)/d/[A-Za-z0-9_-]{20,}',
                             r'https://docs.google.com/\1/d/LOCAL_DESTINATION_REQUIRED', public_text)
        if public_text != text:
            remapped[rel] = True
            data = public_text.encode('utf-8')
        contents.append((rel, data))
    if not contents:
        raise ValueError('Empty source selection')
    temporary = ROOT / 'source.zip.tmp'
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for rel, data in contents:
            archive.writestr(rel, data)
    with ZipFile(temporary) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == [rel for rel, _ in contents]
        assert all(archive.read(rel) == data for rel, data in contents)
    package = temporary.read_bytes()
    rows = [{'path': rel, 'bytes': len(data), 'sha256': sha(data),
             'requires_local_binding_merge': rel in remapped} for rel, data in contents]
    metadata = {
        'distribution_version': version, 'workflow_register_version': register_version,
        'created_at': datetime.now(timezone.utc).isoformat(), 'repository': REPO,
        'package': 'source.zip', 'package_sha256': sha(package), 'file_count': len(rows),
        'scope': 'Selected source only; existing Workflow3 installation required',
        'local_binding_rule': 'Files marked requires_local_binding_merge contain LOCAL_BINDING_/LOCAL_DESTINATION_REQUIRED placeholders. Preserve or map the receiving machine destinations before activation.',
        'excluded': ['private configs', 'credentials', 'accounts/profiles', 'databases', 'production data/assets', 'installed dependencies', 'live n8n workflow database'],
    }
    temporary.replace(ROOT / 'source.zip')
    (ROOT / 'source-manifest.json').write_text(json.dumps({**metadata, 'files': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'LATEST.json').write_text(json.dumps({**metadata, 'manifest': 'source-manifest.json', 'instructions': 'AGENTS.md', 'update_guide': 'UPDATE.md'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'version': version, 'files': len(rows), 'package_bytes': len(package), 'sha256': sha(package)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--version', required=True)
    parser.add_argument('--register-version', required=True)
    args = parser.parse_args()
    build(args.source.resolve(), args.version, args.register_version)

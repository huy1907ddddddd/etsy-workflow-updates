import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('release_builder', Path(__file__).with_name('build_release.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.output = self.root / 'release'
        (self.source / 'scripts').mkdir(parents=True)
        (self.source / 'config').mkdir()
        self.output.mkdir()
        self.file = self.source / 'scripts' / 'runtime.cjs'
        self.file.write_text('module.exports = {};\n', encoding='utf-8')

    def build(self, paths=None):
        with patch.object(module, 'ROOT', self.output), patch.object(module, 'selected', return_value=paths or ['scripts/runtime.cjs']):
            module.build(self.source, '2026.11.07.1', 'V53')

    def test_manifest_and_package_match_original_bytes(self):
        before = self.file.read_bytes()
        self.build()
        latest = json.loads((self.output / 'LATEST.json').read_text())
        manifest = json.loads((self.output / 'source-manifest.json').read_text())
        self.assertEqual(latest['package_sha256'], module.sha((self.output / 'source.zip').read_bytes()))
        self.assertEqual(manifest['files'][0]['sha256'], module.sha(before))
        with ZipFile(self.output / 'source.zip') as archive:
            self.assertEqual(archive.read('scripts/runtime.cjs'), before)
        self.assertEqual(self.file.read_bytes(), before)

    def test_secret_fails_without_overwriting_previous_release(self):
        self.build()
        before = (self.output / 'source.zip').read_bytes()
        self.file.write_text('gh' + 'p_' + 'A' * 40, encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Possible credential'):
            self.build()
        self.assertEqual((self.output / 'source.zip').read_bytes(), before)

    def test_private_and_traversal_paths_are_rejected(self):
        for path in ('config/account.private.json', '../outside.cjs', 'scripts/node_modules/pkg/file.js'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Disallowed export path'):
                self.build([path])

    def test_local_document_identifiers_are_replaced_only_in_export(self):
        identifier = 'X' * 28
        url = 'https://company.larksuite.com/wiki/' + identifier
        (self.source / 'config' / 'listing-layout.json').write_text(json.dumps({'url': url, 'document_id': identifier}))
        original = "const target = '" + url + "'; const documentId = '" + identifier + "';"
        self.file.write_text(original, encoding='utf-8')
        self.build()
        manifest = json.loads((self.output / 'source-manifest.json').read_text())
        self.assertTrue(manifest['files'][0]['requires_local_binding_merge'])
        with ZipFile(self.output / 'source.zip') as archive:
            exported = archive.read('scripts/runtime.cjs').decode()
        self.assertNotIn(identifier, exported)
        self.assertNotIn('company.larksuite.com', exported)
        self.assertIn('LOCAL_BINDING_', exported)
        self.assertEqual(self.file.read_text(encoding='utf-8'), original)

    def test_personal_account_literal_blocks_public_export(self):
        self.file.write_text("const account = 'owner@personal-domain.invalid';", encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Review account/contact'):
            self.build()


if __name__ == '__main__':
    unittest.main()

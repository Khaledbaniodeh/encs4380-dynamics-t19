"""Local merge safety / idempotency tests; no GitHub interactions."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'integrate_module4.py'
spec = importlib.util.spec_from_file_location('module4_merge', SCRIPT)
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)

INDEX = '''<div class="roadmap"><article><p class="card-kicker">04 / Planned</p><h3>Guess the sensor</h3><p>Read an unfamiliar response curve and estimate the hidden sensor’s characteristics.</p></article></div>
Modules 1–3 available
Continue with Modules 2 and 3 · Module 4 coming next'''
MOD1 = '''<html><head><style>p{color:red}</style></head><body><header>Welcome</header><main><nav class="breadcrumb"><a href="./">All modules</a></nav><h1>Module 1</h1></main></body></html>'''
MOD2 = '''<html><nav class="module-nav" aria-label="Switch between modules"><a href="module-3.html">Module 3</a></nav></html>'''
MOD3 = '''<html><nav class="module-nav" aria-label="Switch between modules"><a href="module-3.html" aria-current="page">Module 3</a></nav></html>'''


class TestIntegration(unittest.TestCase):
    def test_index_card_and_idempotence(self):
        result = merge.add_index_card(INDEX)
        self.assertIn('href="module-4.html"',result)
        self.assertIn('Modules 1–4 available',result)
        self.assertEqual(merge.add_index_card(result),result)

    def test_navigation_links_and_idempotence(self):
        a = merge.add_module1_switcher(MOD1)
        self.assertIn('module4-switcher', a)
        self.assertIn('href="module-4.html"',a)
        self.assertEqual(merge.add_module1_switcher(a),a)
        for text, number in ((MOD2,2),(MOD3,3)):
            result = merge.add_header_link(text,number)
            self.assertIn('href="module-4.html"',result)
            self.assertEqual(merge.add_header_link(result,number),result)

    def test_build_changes_has_all_expected_files(self):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)
            for name,content in (
                ('index.html',INDEX),('module-1.html',MOD1),('module-2.html',MOD2),
                ('module-3.html',MOD3),('README.md','# Dynamics Lab\n')
            ):
                (repo/name).write_text(content,encoding='utf-8')
            changes=merge.build_changes(repo,Path(__file__).resolve().parents[1])
            self.assertEqual(len(changes),10)
            self.assertIn(repo/'module-4.html',changes)
            self.assertIn(repo/'README_MODULE4.md',changes)
            self.assertIn(repo/'index.html',changes)


if __name__=='__main__':
    unittest.main()

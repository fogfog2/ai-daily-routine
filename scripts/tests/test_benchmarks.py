import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

build = load('build-benchmarks')
refresh = load('refresh-benchmarks')

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'benchmarks.json').read_text())

    def test_published_snapshot_valid(self):
        build.validate(self.data)

    def test_two_efforts_same_model_are_distinct(self):
        build.validate(self.data)
        rows = [r for r in self.data['results'] if r['model'] == 'gpt-6-astra']
        self.assertEqual(len(rows), 5)

    def test_duplicate_configuration_rejected(self):
        self.data['results'].append(copy.deepcopy(self.data['results'][0]))
        with self.assertRaises(ValueError): build.validate(self.data)

    def test_missing_effort_rejected(self):
        self.data['results'].pop()
        with self.assertRaises(ValueError): build.validate(self.data)

    def test_elo_above_100_allowed(self):
        self.data['results'][0]['scores']['briefcase']['score'] = 1800
        build.validate(self.data)

    def test_invalid_percent_rejected(self):
        self.data['results'][0]['scores']['terminal']['score'] = 101
        with self.assertRaises(ValueError): build.validate(self.data)

    def test_zero_not_missing(self):
        row = next(r for r in self.data['results'] if r['model']=='gpt-6-luna' and r['effort']=='low')
        self.assertEqual(row['scores']['terminal']['score'], 0)
        self.assertIsNone(row['scores']['science']['score'])
        build.validate(self.data)

    def test_cost_without_score_rejected(self):
        self.data['results'][0]['scores']['science'] = {'score':None,'cost':1}
        with self.assertRaises(ValueError): build.validate(self.data)

    def test_nan_and_boolean_rejected(self):
        for value in [float('nan'), float('inf'), True]:
            with self.subTest(value=value):
                self.data['results'][0]['scores']['terminal']['score'] = value
                with self.assertRaises(ValueError): build.validate(self.data)

    def test_negative_cost_rejected(self):
        self.data['results'][0]['scores']['terminal']['cost'] = -1
        with self.assertRaises(ValueError): build.validate(self.data)

    def test_future_observation_rejected(self):
        self.data['results'][0]['observed'] = '2099-01-01'
        with self.assertRaises(ValueError): build.validate(self.data)

    def test_unknown_benchmark_rejected(self):
        self.data['results'][0]['scores']['other'] = {'score':1,'cost':None}
        with self.assertRaises(ValueError): build.validate(self.data)

class ParserTests(unittest.TestCase):
    def page(self, row):
        flight = '10:' + json.dumps({'models':[row]}) + '\n'
        # A Flight payload can be split between script tags.
        mid = len(flight)//2
        return ''.join('<script>self.__next_f.push(' + json.dumps([1, chunk]) + ')</script>' for chunk in [flight[:mid],flight[mid:]])

    def test_matches_exact_slug_across_split_chunks(self):
        row = {'slug':'gpt-6-astra-low','intelligenceIndex':42}
        self.assertEqual(refresh.parse_page(self.page(row),row['slug']),row)

    def test_missing_exact_model_fails(self):
        row = {'slug':'gpt-6-astra','intelligenceIndex':42}
        with self.assertRaises(ValueError): refresh.parse_page(self.page(row),'gpt-6-astra-high')

    def test_effort_mismatch_fails(self):
        with self.assertRaises(ValueError): refresh.configuration('gpt-6-astra','low',{'effort':{'slug':'max'}},'2026-10-06')

    def test_missing_result_remains_null_and_zero_preserved(self):
        raw = {'effort':{'slug':'low'},'name':'GPT-6 Luna (Low)','terminalBench40':0,'intelligenceIndex':20,'intelligenceIndexEvaluations':[]}
        row = refresh.configuration('gpt-6-luna','low',raw,'2026-10-06')
        self.assertEqual(row['scores']['terminal']['score'],0)
        self.assertIsNone(row['scores']['science']['score'])
        self.assertIsNone(row['scores']['terminal']['cost'])

if __name__ == '__main__': unittest.main()

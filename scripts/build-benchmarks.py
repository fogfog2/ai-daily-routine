#!/usr/bin/env python3
"""Validate the reviewed, versioned benchmark snapshot and copy it to the site."""
import datetime as dt
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'benchmarks.json'
TARGET = ROOT / 'site-pages/data/benchmarks.json'


def date(value):
    dt.date.fromisoformat(value)


def https(value):
    if not isinstance(value, str) or not value.startswith('https://'):
        raise ValueError(f'HTTPS source required: {value!r}')


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'finite numeric measurement required: {value!r}')


def unique(rows):
    identifiers = [row['id'] for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('duplicate identifier')
    return set(identifiers)


def validate(data):
    if data['schema_version'] != 2:
        raise ValueError('expected benchmark schema v2')
    date(data['as_of'])
    models = unique(data['models'])
    benchmarks = unique(data['benchmarks'])
    units = {row['id']: row['unit'] for row in data['benchmarks']}
    efforts = data['efforts']
    if efforts != ['low', 'medium', 'high', 'xhigh', 'max']:
        raise ValueError('expected ordered published effort labels')
    for benchmark in data['benchmarks']:
        https(benchmark['source']); https(benchmark['methodology'])
        if benchmark['unit'] not in ['%', 'Elo', '점'] or benchmark['direction'] != 'higher':
            raise ValueError('unknown metric scale/direction')
    seen = set()
    for row in data['results']:
        key = (row['model'], row['effort'])
        if key in seen:
            raise ValueError(f'duplicate model/effort: {key}')
        seen.add(key)
        if row['model'] not in models or row['effort'] not in efforts:
            raise ValueError(f'unknown model/effort: {key}')
        date(row['observed']); https(row['source'])
        if row['observed'] > data['as_of']:
            raise ValueError('observation after snapshot date')
        if not row['source_label'] or not row['fallback']:
            raise ValueError('source label and fallback conditions required')
        if set(row['scores']) != benchmarks:
            raise ValueError('all benchmarks need an explicit measurement or null')
        for ident, measurement in row['scores'].items():
            score, cost = measurement['score'], measurement['cost']
            if score is not None:
                number(score)
                if score < 0 or (units[ident] in ['%', '점'] and score > 100):
                    raise ValueError(f'score outside metric range: {key}/{ident}')
            if cost is not None:
                number(cost)
                if cost < 0 or score is None:
                    raise ValueError('cost must be nonnegative and accompany a score')
    expected = {(model, effort) for model in models for effort in efforts}
    if seen != expected:
        raise ValueError('missing model/effort configuration; represent unpublished results with null')
    for row in data['history']:
        date(row['date'])
    return data


def main():
    data = validate(json.loads(SOURCE.read_text(encoding='utf-8')))
    if not TARGET.parent.is_dir():
        raise FileNotFoundError(f'site data directory missing: {TARGET.parent}')
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    count = sum(m['score'] is not None for row in data['results'] for m in row['scores'].values())
    print(f'  benchmarks.json 갱신: {len(data["models"])}개 모델 · {len(data["benchmarks"])}개 평가 · {count}개 공개 점수')


if __name__ == '__main__':
    main()

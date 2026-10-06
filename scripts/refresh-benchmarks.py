#!/usr/bin/env python3
"""Refresh reviewed Artificial Analysis model/effort snapshots from public pages.

No credentials or unpublished endpoints are used. Source pages are parsed for
exact published values; missing measurements remain null. The refresh is atomic:
a missing model, effort mismatch, or failed validation leaves the snapshot intact.
Use --source-dir with saved public HTML pages for a reproducible offline refresh.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import importlib.util
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
EFFORTS = ['low', 'medium', 'high', 'xhigh', 'max']
FAMILIES = [
    ('gpt-6-astra', 'GPT-6 Astra', 'Codex', False),
    ('gpt-6-1-sol', 'GPT-6.1 Sol', 'Codex', False),
    ('gpt-6-sol', 'GPT-6 Sol', 'Codex', False),
    ('gpt-6-luna', 'GPT-6 Luna', 'Codex', False),
    ('claude-fable-5-1', 'Claude Fable 5.1', 'Claude', False),
    ('claude-opus-5-5', 'Claude Opus 5.5', 'Claude', False),
    ('claude-sonnet-5-5', 'Claude Sonnet 5.5', 'Claude', False),
    ('claude-opus-5', 'Claude Opus 5', 'Claude', True),
    ('claude-sonnet-5', 'Claude Sonnet 5', 'Claude', True),
]
# id, name, source JSON field, evaluation slug, unit, group, harness, description
DEFINITIONS = [
    ('terminal', 'Terminal-Bench 4.0 · AA', 'terminalBench40', 'terminalbench-4-0', '%', '코딩', 'mini-swe-agent', '66개 터미널 과제, 3회 반복의 pass@1 평균. 모델 API를 같은 하네스로 실행한 AA 평가이며 Claude Code·Codex 제품 자체의 점수가 아니다.'),
    ('science', 'Terminal-Bench-Science 0.1 · AA', 'terminalBenchScience', 'terminal-bench-science', '%', '과학·코딩', 'mini-swe-agent', '70개 과학 연구 터미널 과제, 3회 반복의 pass@1 평균. 일부 모델의 낮은 effort는 공개 결과가 없다.'),
    ('automation', 'AutomationBench-AA', 'automationBenchPartialScore', 'automationbench-aa', '%', '업무 자동화', 'AA REST API 평가', '657개 SaaS 업무. 금지 조건을 위반하면 0점, 그렇지 않으면 달성한 목표 비율로 채점한다. Zapier 원본의 엄격한 전체 성공률과 다른 지표다.'),
    ('briefcase', 'AA-Briefcase v1.1', None, 'aa-briefcase', 'Elo', '문서·업무', 'Stirrup', '91개 지식 업무의 과제 성공·분석·발표 품질을 결합한 Elo. 성공률 %와 비교하지 않는다.'),
    ('gdpval', 'GDPval-AA v2.1', 'gdpval', 'gdpval-aa', 'Elo', '문서·업무', 'Stirrup', '220개 실무 산출물을 판정 패널이 비교하는 Elo. 서로 다른 버전의 Elo는 합치지 않는다.'),
    ('pdf', 'GDP.pdf · All-pass', 'gdpPdfAllPass', 'gdp-pdf', '%', '문서·업무', 'AA API 평가', '복잡한 PDF에 근거한 전문 질문 100개, 5회 반복. All-pass 기준이며 평균 부분 점수와 다르다.'),
    ('context', 'AA-LCR v1.1', 'lcr', 'artificial-analysis-long-context-reasoning', '%', '긴 문맥', 'AA API 평가', '긴 입력을 읽고 추론하는 100문항, 3회 반복. 문맥 창의 최대 크기 자체를 측정하는 지표는 아니다.'),
    ('scicode', 'SciCode · AA', 'scicode', 'scicode', '%', '과학·코딩', 'AA 코드 실행 평가', '288개 과학 코딩 하위 문제, 3회 반복. AA에서 Under review로 표시하므로 잠정 결과로 읽는다.'),
    ('hle', 'Humanity’s Last Exam · AA', 'hle', 'humanitys-last-exam', '%', '추론', 'AA API 평가 · 도구 없음', '2,158개 전문 지식·추론 문제. 도구를 쓰는 공급사 HLE 수치와 조건이 다르다.'),
    ('index', 'AA Intelligence Index v4.3.2', 'intelligenceIndex', None, '점', '종합', 'AA 평가 10종 가중 집계', '독립 평가 10종의 가중 지수. 코딩 에이전트 해결률이 아니며 한국어 품질을 직접 평가하지 않는다. 비용은 해당 지수의 가중 평균 API 작업당 비용이다.'),
]
METHOD = 'https://artificialanalysis.ai/methodology/intelligence-benchmarking'


def parse_page(raw, slug):
    chunks = []
    for match in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>', raw):
        try:
            value = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if len(value) > 1 and isinstance(value[1], str):
            chunks.append(value[1])
    rows = []
    def walk(value):
        if isinstance(value, dict):
            if value.get('slug') == slug and 'intelligenceIndex' in value:
                rows.append(value)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    for line in ''.join(chunks).splitlines():
        try:
            walk(json.loads(line.split(':', 1)[1]))
        except (ValueError, IndexError):
            continue
    if not rows:
        raise ValueError(f'published model data missing: {slug}')
    return rows[0]


def configuration(model, effort, raw, observed):
    slug = model + ('-' + effort if effort != 'max' else '')
    if raw.get('effort', {}).get('slug') != effort:
        raise ValueError(f'effort mismatch: {slug}')
    evaluations = {row['slug']: row for row in raw.get('intelligenceIndexEvaluations', [])}
    scores = {}
    for ident, _, field, evaluation, unit, *_ in DEFINITIONS:
        entry = evaluations.get(evaluation, {})
        value = raw.get(field) if field else entry.get('score')
        # Never derive absent scores from nearby efforts, other versions or vendors.
        cost = (raw.get('intelligenceIndexCostPerTask') or {}).get('cost', {}).get('total') if ident == 'index' else entry.get('costPerTask')
        scores[ident] = {'score': round(value * (100 if unit == '%' else 1), 4) if value is not None else None,
                         'cost': round(cost, 6) if cost is not None and value is not None else None}
    return {'model': model, 'effort': effort, 'source_label': raw['name'],
            'source': 'https://artificialanalysis.ai/models/' + slug,
            'observed': observed, 'fallback': 'Default Fallback' if 'Fallback' in (raw.get('suffix') or '') else '없음',
            'scores': scores}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path)
    args = parser.parse_args()
    previous = json.loads((ROOT / 'benchmarks.json').read_text())
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    def get(pair):
        model, effort = pair
        slug = model + ('-' + effort if effort != 'max' else '')
        if args.source_dir:
            page = (args.source_dir / (slug + '.html')).read_text()
        else:
            request = urllib.request.Request('https://artificialanalysis.ai/models/' + slug,
                                             headers={'User-Agent': 'AI-Concepts-Benchmark-Watch/2.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                page = response.read().decode('utf-8')
        return configuration(model, effort, parse_page(page, slug), today)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(get, [(f[0], e) for f in FAMILIES for e in EFFORTS]))
    history = previous.get('history', [])
    entry = {'date': today, 'summary': 'Claude·Codex 9개 모델 계열 × 5개 effort의 AA 공개 결과를 확인. 벤치마크별 점수·API 작업당 비용·fallback 조건을 기록.'}
    if not history or history[-1] != entry:
        history.append(entry)
    # Retain the old product-harness snapshot with its original observation date.
    historical = previous.get('historical', [])
    if 'benchmark' in previous:
        historical.append({'benchmark': previous['benchmark'], 'results': previous['results'],
                           'note': '2026-09-30에 확인한 기존 기록. 이번 갱신에서는 리더보드의 해당 점수 행을 재확인하지 못해 최신 비교에서 제외했다.'})
    data = {'schema_version': 2, 'as_of': today, 'timezone': 'UTC',
            'note': 'effort 명칭이 같아도 공급사별 토큰 예산은 같지 않다. 아래는 AA의 동일 평가 구현에서 모델 API를 비교한 결과이며 실제 Codex·Claude Code의 도구·시스템 프롬프트·사용 한도에 따라 달라진다. API 작업당 비용은 구독 요금이나 사용 한도 소비량이 아니다. 미공개는 0점과 구분한다.',
            'efforts': EFFORTS,
            'models': [{'id': f[0], 'name': f[1], 'product': f[2], 'legacy': f[3]} for f in FAMILIES],
            'benchmarks': [{'id': d[0], 'name': d[1], 'unit': d[4], 'group': d[5], 'harness': d[6], 'description': d[7],
                            'source': 'https://artificialanalysis.ai/evaluations/' + d[3] if d[3] else 'https://artificialanalysis.ai/models',
                            'methodology': METHOD, 'direction': 'higher', 'status': 'under-review' if d[0] == 'scicode' else 'published'} for d in DEFINITIONS],
            'results': rows, 'historical': historical, 'history': history}
    spec = importlib.util.spec_from_file_location('build_benchmarks', ROOT / 'scripts/build-benchmarks.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.validate(data)
    target = ROOT / 'benchmarks.json'
    temporary = target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(target)
    count = sum(s['score'] is not None for r in rows for s in r['scores'].values())
    print(f'공개 원문 확인: {len(rows)} configurations · {count} published scores · {today} UTC')


if __name__ == '__main__':
    main()

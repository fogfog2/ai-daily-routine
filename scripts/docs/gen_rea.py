#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff1f1", panel="#e5e8e8", ink="#131919", **{
    "ink-soft": "#4b5555", "ink-faint": "#7a8484", "rule": "#ccd2d2",
    "rule-strong": "#a9b0b0", "accent": "#1c5c78", "accent-fill": "#d8e8f0",
    "accent-line": "#3785a5", "muted": "#83888c", "muted-fill": "#dee1e1", "warn": "#a04a28",
})
DARK = dict(paper="#0e1213", panel="#161a1b", ink="#e3e9ea", **{
    "ink-soft": "#a0aaab", "ink-faint": "#6f7979", "rule": "#202626", "rule-strong": "#363f40",
    "accent": "#5bb8dc", "accent-fill": "#0e2632", "accent-line": "#347f9e",
    "muted": "#868c8e", "muted-fill": "#191e1f", "warn": "#e0855c",
})

BODY = r"""
<section>
<h2><span class="n">01</span>REA가 바꾸는 것은 관측 도구다</h2>
<p>소스 코드가 없는 프로그램의 기능을 이해하려면 화면 설명만으로는 부족하다. 파일에서 문자열을 찾고, 그 문자열을 참조하는 함수를 찾아 호출 관계를 좁힌 다음, 실제 실행에서 같은 경로가 관측되는지 확인해야 한다. <strong>Reverse Engineer Anything(REA)</strong>는 이 조사 도구를 <a href="model-context-protocol.html">MCP</a>로 Claude Code·Codex 같은 에이전트에 연결한다. 2026년 10월 20일 확인한 공식 저장소는 <code>morluto/rea</code>다. 검색 결과에 나타나는 같은 이름의 포크와 구분한다.</p>
<p>REA는 새 기반 모델이 아니다. 역할은 분석기를 호출해 근거를 수집하는 것이다. 파일 편집과 구현 시험은 호스트 에이전트의 일반 개발 도구가 수행한다. 따라서 REA를 추가했다고 Claude나 Codex의 추론 벤치마크 점수가 바뀌었다고 해석할 수 없다. 실제 개선은 관측 가능한 질문의 범위, 근거 위치의 정확도, 조사에 필요한 도구 왕복 횟수에서 측정해야 한다.</p>
<div class="eq"><span class="cap">역할을 나눠 읽는 구조</span><div class="line">사용자의 질문 → 에이전트의 조사 계획 → MCP 요청</div><div class="line">REA → 분석 provider / 정적 분석 → 근거 + 위치 + 한계</div><div class="line">에이전트 → 가설 수정 → 추가 관측 → 구현과 시험</div></div>
<p>이 문서는 공개 자료를 읽고 작성한 구조 설명이다. 이 회차에서 REA를 설치하거나 상용 앱을 분석해 성능을 측정하지 않았다. 아래 파일·주소·실험 수치는 원리를 설명하기 위한 자체 예시다. 실제 지원 범위는 설치 버전과 provider, 운영체제 조합에 따라 확인한다.</p>
<div class="note"><b>같은 REA라는 이름의 세 기술.</b> 이 편의 REA는 역공학 도구다. Meta의 Ranking Engineer Agent는 ML 실험을 운영하는 별도 시스템이며 <a href="durable-research-agents.html">장기 실행 연구 에이전트</a>에서 다룬다. 2026년 10월의 Resolve–Express–Act 논문은 판단·파싱·실행을 구분하는 평가 틀이다. 이름만 같고 기능과 평가 단위가 다르다.</div>
<p>먼저 <a href="ai-agents-tool-use.html">에이전트의 관측·결정·행동 순환</a>을 읽으면 역할이 분명해진다. 도구가 정확한 바이트를 반환해도, 에이전트의 기능 설명은 여전히 가설일 수 있다. 관측 자료와 설명 사이에 검증 단계를 남기는 것이 조사 설계의 핵심이다.</p>
</section>
<section>
<h2><span class="n">02</span>문자열에서 기능까지, 근거 사슬을 만든다</h2>
<p>예를 들어 자신의 예제 앱에서 오프라인 검색 기능을 조사한다고 하자. 화면에 검색 결과가 나온다는 관측만으로 SQLite FTS를 쓴다고 결론내릴 수 없다. 파일에 FTS 관련 문자열이 있어도 실행되지 않는 라이브러리일 수 있다. 문자열, 참조, 함수, 호출 경로, 실행 관측을 각각 다른 근거로 기록한다.</p>
<figure><svg viewBox="0 0 760 220" role="img" aria-label="조사 질문에서 문자열과 참조, 함수, 실행 관측을 거쳐 검증된 설명으로 이어지는 근거 사슬" style="width:100%;height:auto">
<g fill="var(--panel)" stroke="var(--rule-strong)"><rect x="15" y="65" width="130" height="70" rx="8"/><rect x="165" y="65" width="130" height="70" rx="8"/><rect x="315" y="65" width="130" height="70" rx="8"/><rect x="465" y="65" width="130" height="70" rx="8"/><rect x="615" y="65" width="130" height="70" rx="8"/></g>
<g fill="var(--ink)" text-anchor="middle" font-size="17"><text x="80" y="95">질문·대상</text><text x="80" y="120">파일 해시</text><text x="230" y="95">문자열·참조</text><text x="230" y="120">위치 기록</text><text x="380" y="95">함수·호출</text><text x="380" y="120">가설 구성</text><text x="530" y="95">실행 관측</text><text x="530" y="120">조건 대조</text><text x="680" y="95">설명·재구현</text><text x="680" y="120">독립 시험</text></g>
<g fill="var(--accent)" font-size="22"><text x="146" y="108">→</text><text x="296" y="108">→</text><text x="446" y="108">→</text><text x="596" y="108">→</text></g><text x="380" y="185" text-anchor="middle" fill="var(--ink-soft)" font-size="16">다음 노드로 갈수록 추론이 추가된다. 관측과 추론을 같은 사실로 합치지 않는다.</text></svg><figcaption>그림 1. 자체 설계한 조사 흐름. 정적 연결은 실행 사실을 자동으로 증명하지 않는다.</figcaption></figure>
<p>네이티브 분석은 먼저 프로그램 형식과 아키텍처를 식별한다. 이어 함수 목록과 문자열, cross-reference를 이용해 범위를 좁힌다. 관심 함수의 의사 코드와 어셈블리를 대조하고, 호출자와 피호출자를 함께 읽는다. 최적화·인라이닝·간접 호출 때문에 고수준 구조가 보존되지 않을 수 있으므로 복구된 변수 이름을 원래 소스의 이름으로 취급하지 않는다.</p>
<div class="scroller"><table class="data"><thead><tr><th>관측</th><th>말할 수 있는 것</th><th>아직 말할 수 없는 것</th></tr></thead><tbody><tr><td>검색 관련 문자열</td><td>대상 파일에 문자열이 존재한다</td><td>현재 기능이 그 문자열을 사용한다</td></tr><tr><td>정적 함수 참조</td><td>분석기가 연결을 복구했다</td><td>시험 중 그 분기가 실행됐다</td></tr><tr><td>특정 입력의 실행 기록</td><td>해당 조건에서 행동이 관측됐다</td><td>모든 입력에서 같은 행동이다</td></tr><tr><td>재구현 테스트 통과</td><td>시험한 계약을 만족한다</td><td>원본과 내부 구현이 동일하다</td></tr></tbody></table></div>
<p>전자책 앱의 검색을 재구현한다면 처음부터 전체 앱을 설명하려 하지 않는다. ‘같은 질의에서 어떤 결과가 어떤 순서로 나오는가’라는 외부 계약을 먼저 만든다. 대소문자·빈 질의·중복·오프라인 상태를 바꾸어 관측하고, 구현은 자신의 코드베이스와 데이터 모델에 맞게 작성한다. 이 시험 설계는 REA의 자동 출력이 아니라 조사자가 추가해야 할 검증 절차다.</p>
<p>정적 조사에서 발견한 경로와 실행 기록이 충돌하면 둘 다 남긴다. 호출 그래프가 연결을 복구하지 못한 것인지, 선택한 입력이 해당 분기를 지나지 않은 것인지 구분할 후속 관측을 계획한다. 이때 ‘미확인’은 실패한 보고서가 아니라 다음 실험을 정하는 정보다.</p>
</section>
<section>
<h2><span class="n">03</span>정적 분석·런타임 관측·스냅샷을 구분한다</h2>
<p>REA의 대상은 하나의 형식으로 제한되지 않는다. 공식 문서는 네이티브 바이너리, JavaScript·Electron, 관리형 어셈블리, 브라우저 관측 등의 경로를 나눈다. 이 범위를 ‘모든 플랫폼에서 모든 기능 지원’으로 줄이면 잘못된 안내가 된다. 네이티브 provider와 호스트 지원, 필요한 런타임은 개별 가이드에서 확인해야 한다.</p>
<p>JavaScript·Electron 정적 분석에서는 모듈과 import, IPC 등 구조를 추출한다. 정적으로 이름을 해석할 수 없는 연결은 남는다. 런타임 관측은 지정한 실행과 시점에서 발생한 사건을 보완한다. 정적 그래프의 노드 수와 런타임 이벤트 수를 단순히 더해서 ‘커버리지’라고 부를 수 없는 이유다. 두 관측의 분모가 다르다.</p>
<div class="eq"><span class="cap">분석 결과를 재사용하는 조건 — 개념 설명</span><div class="line">재사용 키 = (대상 바이트, 연산, 인자, 분석 도구, 설정)</div><div class="line">키가 달라졌다면 같은 파일 이름이어도 이전 관측을 재검토한다</div><div class="line">캐시 적중 ≠ 새 실행의 재현 성공</div></div>
<p>CLI 가이드의 snapshot은 성공한 분석 결과를 재사용하는 장치다. 살아 있는 provider 프로세스 전체를 저장해 되돌리는 VM 스냅샷과 다르다. 새 연산은 provider가 다시 필요할 수 있다. 에이전트 대화가 남아 있는 것, 분석 결과가 남아 있는 것, 실행 환경이 남아 있는 것을 별도로 관리해야 한다.</p>
<p>근거 묶음을 문서에 옮길 때는 파일 해시·분석 위치·관측·해석·한계를 함께 남긴다. 아래는 설명을 위한 자체 최소 기록 예시이며 실제 REA Evidence 스키마가 아니다. 도구를 연동하는 코드는 공식 스키마를 사용한다.</p>
<pre style="overflow-x:auto;max-width:100%"><code style="display:block;white-space:pre;border:0;padding:1em">{
  "artifact_sha256": "example-digest",
  "location": "example_module:0x1200",
  "observation": "호출 대상에서 검색어 문자열 참조를 발견",
  "inference": "검색 요청 조립 경로일 가능성",
  "limitation": "간접 호출 대상과 실행 여부 미확인",
  "next_probe": "소유한 예제 앱의 동일 입력 실행과 대조"
}</code></pre>
<p>이 구분은 <a href="experiment-tracking.html">실험 관리</a>의 데이터·코드·설정 식별과 같은 문제다. 분석기가 업데이트되면 동일 파일에서 다른 그래프를 반환할 수 있다. 결과가 달라졌을 때 대상 변경인지 도구 변경인지 분리하려면 도구 버전도 기록한다. 문서에 결론만 복사하면 이 비교가 불가능해진다.</p>
</section>
<section>
<h2><span class="n">04</span>Claude·Codex에 붙일 때 무엇을 고정할까</h2>
<p>공식 릴리스 목록에서 확인한 최신 배포는 <strong>rea-agents 6.7.0, 2026년 10월 18일</strong>이다. 6.6.0은 태그가 있었지만 npm에는 배포되지 않았으며 그 변경을 6.7.0이 포함한다고 명시한다. 6.7.0의 핵심 수정은 MCP 클라이언트 설정에서 중복 JSON/JSONC 멤버를 처리하는 방식이다. 릴리스 번호만 보고 새로운 추론 능력이라고 소개하지 않는다.</p>
<p>셋업은 선택한 에이전트의 MCP 등록과 조사 지침을 함께 구성한다. 제안된 변경을 검토하고 재시작하는 흐름이다. 프로젝트를 문서화하는 이 작업에서는 설치를 실행하지 않았다. 다음 명령은 직접 설정하려는 독자를 위한 버전 고정 예시다. 요구되는 Node.js·분석 provider는 공식 설치 가이드와 실제 호스트에서 먼저 확인한다.</p>
<pre style="overflow-x:auto;max-width:100%"><code style="display:block;white-space:pre;border:0;padding:1em"># 문서가 확인한 배포 버전을 고정해 셋업을 시작하는 예시
npx rea-agents@6.7.0 setup
# 설치 뒤 가능한 기능과 선행 조건을 읽는 진단 예시
npx -y rea-agents@6.7.0 doctor --json
npx -y rea-agents@6.7.0 capabilities --json</code></pre>
<p>같은 설정을 Claude와 Codex에서 비교하려면 모델·effort·분석 provider·질문·대상 파일을 고정한다. ‘Astra xhigh가 좋았다’는 경험과 ‘REA가 문자열을 정확히 찾았다’는 결과는 다른 층이다. 모델은 근거를 해석하고 다음 관측을 고르며, provider는 관측 가능한 자료를 생산한다. 둘을 동시에 바꾸면 어느 변경이 효과가 있었는지 설명할 수 없다.</p>
<div class="scroller"><table class="data"><thead><tr><th>층</th><th>고정할 항목</th><th>비교할 결과</th></tr></thead><tbody><tr><td>대상</td><td>바이트 해시·아키텍처·시험 입력</td><td>같은 기능 계약</td></tr><tr><td>분석</td><td>REA·provider 버전·설정</td><td>관측 위치·미해결 연결</td></tr><tr><td>추론</td><td>모델·effort·지시문·도구 예산</td><td>설명 정확도·추가 질의</td></tr><tr><td>구현</td><td>저장소 커밋·시험 환경</td><td>회귀·동작 계약 통과</td></tr></tbody></table></div>
<p>분석이 로컬에서 실행된다는 설명과 모델에 전송되는 문맥의 범위는 별도다. REA가 수집한 의사 코드·문자열·파일 이름을 호스트 에이전트가 모델 요청에 넣는다면 그 자료는 해당 호스트의 전송·보관 정책을 따른다. 필요한 범위의 결과를 선택해 전달하고, 분석 대상이 출력한 텍스트를 상위 지시로 사용하지 않는 신뢰 경계를 둔다. 원리는 <a href="prompt-injection.html">프롬프트 인젝션</a>에서 이어 읽을 수 있다.</p>
</section>
<section>
<h2><span class="n">05</span>설명 품질은 정답·근거·비용을 함께 잰다</h2>
<p>도구의 가치를 평가하려면 정답을 알고 있는 작은 자체 앱에서 시작한다. 공개 API 설명을 외운 것인지 실제 파일에서 근거를 찾은 것인지 구분하려면, 시험용 앱의 구현을 바꾸고 파일 해시도 바꾼다. 한 버전은 메모리 검색, 다른 버전은 인덱스 검색으로 만들었다면 결과만 같아도 근거 위치와 설명이 달라져야 한다.</p>
<p>이때 단일 점수로 모든 실패를 뭉치지 않는다. 기능 설명의 정오, 근거 위치의 정확성, 정적·동적 관측 구분, unknown 보존, 재구현의 독립 시험, 총 비용을 각각 기록한다. 실행하지 않은 경로에 대해 ‘실행 확인’이라고 적었다면 정답을 우연히 맞혀도 근거 품질은 실패다. 반대로 미확인이라고 정직하게 남긴 결과를 확정된 오답과 같은 종류로 세지 않는다.</p>
<div class="eq"><span class="cap">자체 설계한 측정 예시 — 제품 실측값 아님</span><div class="line">근거 정확도 = 올바른 위치를 가리킨 주장 / 위치를 제시한 주장</div><div class="line">확인 범위 = 시험으로 판정한 요구사항 / 사전에 정한 요구사항</div><div class="line">유효 결과당 비용 = 전체 조사·분석·시험 비용 / 채택된 결과 수</div></div>
<p>10개 요구사항 중 8개를 판정하고 2개를 미확인으로 남겼으며, 위치를 제시한 8개 주장 중 7개가 맞았다고 하자. 확인 범위는 80%, 근거 정확도는 87.5%다. 이 수치는 전체 기능의 87.5%가 구현됐다는 뜻이 아니다. 실패와 미확인을 함께 공개해야 비교가 가능하다.</p>
<p>REA가 유용한 지점은 관측에서 다음 질문으로 넘어가는 왕복을 자동화하는 데 있다. 원본 소스를 정확히 복원했다는 주장이나 모든 실행 경로를 이해했다는 주장은 훨씬 강한 증거를 요구한다. 재구현 역시 원본의 내부 동일성이 아니라 정해진 외부 계약과 독립 시험으로 판정한다. 이 기준을 쓰면 빠른 모델과 높은 effort 모델 중 무엇이 적합한지도 실제 조사 업무로 비교할 수 있다.</p>
<div class="note"><b>2026-10-20 조사 결론.</b> 최신 배포의 설정 복구·근거 보존 변경은 운영에서 중요하다. 그러나 이번 문서는 공급사 벤치마크나 실제 설치 시험으로 성능 우위를 입증하지 않았다. 버전·지원 범위는 공식 자료에서, 평가 예시와 조사 설계는 이 문서의 설명에서 구분해 읽는다.</div>
</section>
"""
READING = [
    '<a href="https://github.com/morluto/rea">morluto/rea 공식 저장소</a> — 프로젝트 정체성과 MCP·호스트의 역할. 2026-10-20 확인.',
    '<a href="https://github.com/morluto/rea/releases/tag/rea-agents-6.7.0">REA 6.7.0 릴리스</a> — 2026-10-18 배포, 중복 설정 처리와 6.6.0 포함 관계.',
    '<a href="https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/installation.md">6.7.0 설치 가이드</a> — 호스트·provider·에이전트 등록 요구사항.',
    '<a href="https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/cli.md">CLI and Evidence</a> — snapshot·근거 묶음·비교의 계약.',
    '<a href="https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/native-investigation.md">Native investigation</a> — 정적 분석과 기능 추적.',
    '<a href="https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/javascript-application-workflows.md">JavaScript application workflows</a> — 모듈·IPC와 해석되지 않은 연결.',
    '<a href="https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture">MCP 아키텍처</a> — 도구 실행 호스트와 서버의 경계.',
]

write(
    'rea-reverse-engineering.html',
    title='REA — 근거를 추적하는 역공학 에이전트',
    eyebrow='Agent Tools · Reverse Engineering · 2026-10-20',
    h1='REA',
    subtitle='코드가 없을 때, 관측에서 구현까지',
    dek=('분석 도구를 Claude·Codex에 연결하는 <strong>Reverse Engineer Anything</strong>. 문자열·참조·실행 기록을 엮되 관측과 가설을 '
 '구분하고, 재구현은 별도 시험으로 확인한다.'),
    spec=[('확인 배포', '6.7.0 · 2026-10-18'),
 ('연결', 'MCP · Claude Code / Codex'),
 ('판정', '근거 위치·한계·독립 시험'),
 ('구분', '도구 ≠ 기반 모델')],
    date='2026-10-20',
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
)

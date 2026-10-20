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
<h2><span class="n">01</span>긴 답변과 장기 실행은 다른 문제다</h2>
<p>훈련이 몇 시간 걸리고 결과를 확인한 뒤 다시 실험해야 하는 작업은 대화 한 번으로 끝나지 않는다. 모델이 긴 문맥을 읽는 능력만으로는 프로세스 종료, 네트워크 단절, 중복 이벤트, 실험 예산을 처리할 수 없다. <strong>장기 실행 에이전트는 추론 순환을 영속 상태와 비동기 작업 위에 놓는 시스템</strong>이다. 기초 순환은 <a href="ai-agents-tool-use.html">AI Agents &amp; Tool Use</a>와 같지만 복구해야 할 시간이 길어진다.</p>
<p>2026년의 최근 흐름은 도구 호출 수를 늘리는 것에서, 완료된 작업을 식별하고 관측·실험·절차를 다음 실행에 전달하는 쪽으로 이동하고 있다. 다만 모든 기술이 같은 기능을 제공하지는 않는다. 관리형 워크플로는 실행 구조를, 연구 에이전트는 탐색과 근거 공유 정책을, 실행 추적은 관측 경로를 다룬다. 이 셋을 구분하면 제품 발표가 실제 설계에서 어느 문제를 푸는지 이해할 수 있다.</p>
<div class="scroller"><table class="data"><thead><tr><th>자료·확인 시점</th><th>핵심 초점</th><th>읽을 때의 경계</th></tr></thead><tbody>
<tr><td>Meta Ranking Engineer Agent · 2026-03-17</td><td>ML 실험의 대기·재개와 예산 내 반복</td><td>사내 광고 랭킹 시스템 사례</td></tr>
<tr><td>Claude dynamic workflows · 2026-10-09</td><td>프로그램이 여러 에이전트의 단계·결과를 연결</td><td>Managed Agents 베타 기능</td></tr>
<tr><td>AReaL-RSI · 2026-10-13 v1</td><td>연구 역할·조건부 기억·절차 개정</td><td>가중치를 갱신하지 않는 연구 프레임워크</td></tr>
<tr><td>OpenTelemetry export · 2026-10-14</td><td>API·세션 실행 경로 추적</td><td>추적 기록만으로 성공을 판정하지 않음</td></tr>
</tbody></table></div>
<p>Meta의 REA는 Ranking Engineer Agent의 약자다. <a href="rea-reverse-engineering.html">Reverse Engineer Anything</a>과 이름만 같다. 또 Resolve–Express–Act라는 10월 논문도 별도 연구다. 이름이 같다는 이유로 기능이나 수치를 섞으면, 코드 분석 도구에 ML 실험 생산성 수치를 붙이는 오류가 생긴다.</p>
<div class="eq"><span class="cap">이 문서에서 사용하는 개념 분해</span><div class="line">에이전트 시스템 = 의사결정 + 상태 저장 + 작업 실행 + 검증</div><div class="line">긴 문맥은 의사결정을 돕는다. 상태 저장과 복구의 대체물은 아니다.</div></div>
<p>이하의 상태 기계·예산식·평가 예시는 여러 제품에 공통으로 적용할 수 있도록 이 문서가 구성한 설계 설명이다. 특정 SDK가 그대로 제공하는 스키마나 보장으로 읽지 않는다. API 설정과 지원 범위는 해당 원문을 별도로 확인한다.</p>
</section>
<section>
<h2><span class="n">02</span>대기할 때는 상태를 남기고, 깨어날 때는 사실을 확인한다</h2>
<p>Meta의 공식 사례는 훈련 작업을 시작한 뒤 백그라운드 시스템에 대기를 맡기고, 완료되면 이어가는 hibernate-and-wake 구조를 설명한다. 과거 실험과 연구 가설을 활용하고 엔지니어가 승인한 계산 예산 안에서 검증·조합·집중 탐색을 수행한다. 이는 특정 사내 도메인 사례이며, 발표의 생산성 배수를 일반 코딩 에이전트의 성공률로 바꾸어 인용할 수 없다.</p>
<p>이를 자체 시스템에 적용한다고 가정하면, 가장 먼저 정의할 것은 ‘지금까지 무엇이 확정됐는가’다. 모델이 ‘훈련을 제출했다’고 말한 것과 작업 스케줄러가 반환한 job ID는 다르다. 결과를 저장했다는 메시지와 실제 결과 파일의 해시도 다르다. 영속 상태는 대화 요약만으로 구성하지 않고 외부 시스템의 식별자를 포함해야 한다.</p>
<figure><svg viewBox="0 0 760 255" role="img" aria-label="준비, 제출 확인, 대기, 결과 검증, 채택의 장기 실행 상태 전이" style="width:100%;height:auto"><g fill="var(--panel)" stroke="var(--rule-strong)"><rect x="20" y="45" width="125" height="65" rx="8"/><rect x="165" y="45" width="125" height="65" rx="8"/><rect x="310" y="45" width="125" height="65" rx="8"/><rect x="455" y="45" width="125" height="65" rx="8"/><rect x="600" y="45" width="140" height="65" rx="8"/><rect x="235" y="160" width="290" height="55" rx="8"/></g><g fill="var(--ink)" text-anchor="middle" font-size="17"><text x="82" y="84">준비</text><text x="227" y="84">제출 확인</text><text x="372" y="84">대기</text><text x="517" y="84">결과 검증</text><text x="670" y="84">채택 / 종료</text><text x="380" y="194">제출 불확실 → 외부 job 조회</text></g><g fill="var(--accent)" font-size="22"><text x="146" y="84">→</text><text x="291" y="84">→</text><text x="436" y="84">→</text><text x="581" y="84">→</text></g><path d="M227 111 L227 139 L300 139 L300 159 M455 186 L550 186 L550 113" fill="none" stroke="var(--accent-line)" stroke-width="2"/></svg><figcaption>그림 1. 자체 설계한 개념 상태 기계. 제출 결과를 모를 때 재제출부터 하면 중복 작업을 만들 수 있다.</figcaption></figure>
<p>네트워크가 제출 직후 끊겼다면 상태는 단순 실패가 아니라 ‘제출 여부 불확실’이다. 같은 요청을 반복하기 전에 작업 ID나 멱등 키로 외부 시스템을 조회한다. 외부 API가 멱등 제출을 제공하지 않으면 중복 검출과 정리 방법을 별도로 마련한다. 체크포인트가 있다고 자동으로 exactly-once 실행이 보장되는 것은 아니다.</p>
<pre style="overflow-x:auto;max-width:100%"><code style="display:block;white-space:pre;border:0;padding:1em"># 특정 제품 코드가 아닌 상태 기록 예시
run_id: experiment-17
artifact_commit: example-commit
request_key: experiment-17-train-1
external_job_id: job-42
status: waiting
last_event_id: event-8
remaining_budget: 7.5  # 자체 예시의 GPU-hour
next_action: query_job_then_verify_result</code></pre>
<p>재개할 때는 저장된 계획뿐 아니라 현재 권한, 남은 예산, 입력 파일 변경, 외부 작업의 실제 상태를 확인한다. 이전 실행이 허용된 권한과 지금의 정책이 다를 수 있기 때문이다. <a href="long-context.html">긴 문맥·컨텍스트 관리</a>는 필요한 정보를 모델에 보여주는 문제이고, 이 재확인은 외부 세계와 저장 상태의 일치 문제다.</p>
<p>이벤트 전달이 중복될 수 있다면 처리한 event ID를 저장하고 같은 결과의 재집계를 막는다. 일부 결과만 저장된 상태에서 종료될 수도 있으므로 산출물 저장, 검증 상태, 최종 채택을 단계별로 표시한다. ‘실행 완료’와 ‘결과 채택’이 분리되어야 실패한 실험도 반복 비용 없이 분석할 수 있다.</p>
</section>
<section>
<h2><span class="n">03</span>병렬화는 실행 구조와 공유 자원의 문제다</h2>
<p>Claude Managed Agents의 공식 문서는 subagent와 dynamic workflow를 구분한다. 전자는 주 에이전트가 보고를 받고 후속 메시지로 이어가는 방식이고, 후자는 작성된 프로그램이 백그라운드에서 여러 에이전트를 실행하고 결과를 합치는 방식이다. 워크플로 실행의 스레드는 실행 종료까지 보관되는 규칙을 따르므로, 대화형 후속 지시가 필요한 작업과 같은 것으로 취급하지 않는다.</p>
<p>컨텍스트가 분리됐다는 사실만으로 파일시스템과 자격 증명도 분리됐다고 추정하면 안 된다. 문맥 격리, 작업 디렉터리 격리, 계정 권한 격리는 각각 다른 설정이다. 두 작업자가 같은 파일을 바꾸거나 같은 실험 이름을 쓰면 독립적인 추론이 충돌하는 산출물을 만들 수 있다. 출력 경로와 변경 범위를 미리 정해야 한다.</p>
<div class="eq"><span class="cap">자체 예시의 병렬 처리 시간</span><div class="line">T<sub>순차</sub> = Σ t<sub>i</sub></div><div class="line">T<sub>병렬</sub> ≈ max(t<sub>i</sub>) + 조정 + 통합 + 재검증</div><div class="line">4개 작업이 각각 10분, 추가 비용이 8분이면 40 / 18 ≈ 2.22배</div></div>
<p>이 2.22배는 가정한 시간으로 계산한 예시이며 제품 성능 수치가 아니다. 에이전트를 네 개 만들었다고 항상 네 배 빨라지지 않는다. 공유 API의 속도 제한, 빌드 자원, 리더의 합성 시간, 충돌 수정 시간이 남는다. 작업이 앞 단계의 결과에 의존하면 독립적으로 실행할 부분부터 다시 나눠야 한다.</p>
<p>예를 들어 여러 문서를 검토할 때는 각 작업자가 문서 하나의 주장·출처·확인 불가 항목을 같은 형식으로 반환하게 할 수 있다. 합성 단계는 중복과 충돌을 찾아야 하며, 보고를 모두 이어 붙이는 것만으로 검증이 끝나지 않는다. 최종 산출물이 저장되는 경로는 한 작업자가 소유하거나 통합자가 원자적으로 갱신하는 방법을 택한다.</p>
<div class="scroller"><table class="data"><thead><tr><th>작업 특성</th><th>시작할 구조</th><th>확인할 비용</th></tr></thead><tbody><tr><td>단계가 고정된 반복 작업</td><td>일반 프로그램·워크플로</td><td>분기 유지·실패 복구</td></tr><tr><td>증거에 따라 조사 방향 변경</td><td>단일 에이전트 순환</td><td>도구 호출·문맥 증가</td></tr><tr><td>독립적인 다수 자료 검토</td><td>병렬 작업 + 통합 단계</td><td>결과 검증·중복 제거</td></tr><tr><td>같은 가설의 대안 탐색</td><td>독립 후보 + 제한된 근거 공유</td><td>탐색 다양성·평가 예산</td></tr></tbody></table></div>
<p>OpenAI의 장기 작업 문서도 목표와 중단 조건, 검토 시점을 정의하는 작업 운영을 다룬다. 제품의 Goal mode, 서브에이전트, 클라우드 실행은 이용 조건이 다른 기능이다. 제품 이름을 일반 내결함성 보장으로 바꾸지 않고 실제 작업에서 재개·중복·예산 종료를 시험한다.</p>
</section>
<section>
<h2><span class="n">04</span>AReaL-RSI — 가중치보다 연구 절차를 바꾼다</h2>
<p>10월 13일 공개된 AReaL-RSI v1은 기반 LLM의 가중치를 갱신하지 않는 지속적 연구 팀을 제안한다. 리더가 과제에 맞는 연구 방향을 정하고, 연구자 사이에는 출처·적용 조건·불확실성을 유지한 기억을 선택적으로 공유한다. 연구 캠페인 뒤 검토를 통해 연구 방향·지식·스킬을 개정하는 구조다. 학습된 모델 자체가 재귀적으로 더 강해졌다는 주장과 구분한다.</p>
<p>논문이 비교한 대상은 보고된 자원 배분 아래의 Codex-Goal과 연구 설정이다. 초록은 두 backbone 각각에서 Terminal Bench 2.2%p 개선과 KernelBench 평균 speedup의 32.2–36.8% 증가를 보고한다. 이 수치는 논문 실험 조건의 결과이며, Codex 제품 전체가 그만큼 느리다거나 모든 Claude 작업에 동일한 향상이 생긴다는 뜻이 아니다. 이 사이트의 공통 모델 벤치마크에 합산하지 않는다.</p>
<p>일반 설계로 옮길 때 중요한 것은 ‘무엇을 공유하는가’다. ‘타일 크기 128이 좋다’라는 결론만 전달하면 다른 dtype·shape·GPU에서 오히려 성능이 나빠질 수 있다. 다음 기록은 원리를 설명하기 위한 자체 예시로, 논문의 구현 스키마가 아니다.</p>
<pre style="overflow-x:auto;max-width:100%"><code style="display:block;white-space:pre;border:0;padding:1em">finding: 타일 크기 128이 현재 후보보다 빨랐다
source: benchmark-run-23
conditions: GPU-A / fp16 / shape-X / compiler-Y
validation: 해당 조건에서 반복 실행, 정확성 검사 통과
unknowns: 다른 shape와 GPU 미검증
reuse: 수신자가 자신의 조건에서 재측정한 뒤 채택</code></pre>
<p>모든 작업자가 가장 빠른 후보만 복사하면 서로 다른 아이디어를 탐색할 이유가 줄어든다. 조건을 붙인 공유는 결론의 적용 범위를 좁히며, 실패와 미해결 문제를 함께 전달하면 같은 실수를 반복하는 비용을 줄인다. 그러나 무엇을 공유할지 결정하는 조정 비용도 평가에 포함해야 한다. 공유 메시지 수를 줄였다고 전체 비용이 반드시 줄어드는 것은 아니다.</p>
<p>절차 개정도 산출물과 분리한다. ‘이 커널이 빨라졌다’는 코드 결과이고, ‘다음 실험 전에 어떤 검사를 수행하라’는 연구 절차다. 후자를 스킬이나 지침에 반영하려면 근거와 적용 조건, 이전 버전으로 되돌리는 방법을 남긴다. <a href="experiment-tracking.html">실험 관리</a>의 추적 단위가 모델·코드뿐 아니라 절차 버전까지 확장되는 셈이다.</p>
<div class="note"><b>자기 개선의 범위를 명시한다.</b> 프롬프트·기억·스킬·도구 프로그램을 바꾸는 개선과, <a href="rlvr.html">RLVR</a> 같은 파라미터 학습은 별도다. 어떤 것이 바뀌었는지 기록하지 않으면 모델 품질 향상과 시스템 구성 효과를 구분할 수 없다.</div>
</section>
<section>
<h2><span class="n">05</span>성공률·복구·비용을 같은 실행에서 잰다</h2>
<p>장기 실행은 최종 점수 하나로 평가하기 어렵다. 작업 자체의 성공 외에 외부 이벤트 전달, 대기 복구, 예산 종료, 중복 부작용을 함께 봐야 한다. 아래 항목은 이 문서가 제안하는 최소 평가 틀이다. 대기 시간이 긴 실험일수록 정상 실행과 실패 주입 실행을 나누어 기록하는 편이 원인을 찾기 쉽다.</p>
<div class="scroller"><table class="data"><thead><tr><th>평가 축</th><th>측정 예</th><th>자주 생기는 착시</th></tr></thead><tbody><tr><td>과제 품질</td><td>보류하지 않은 성공·실패·미완료 수</td><td>완료한 과제만 분모로 사용</td></tr><tr><td>복구</td><td>연결 단절 후 재개·중복 제출 수</td><td>재시도를 새 성공으로 집계</td></tr><tr><td>전체 비용</td><td>모든 에이전트·실험·실패·검증 비용</td><td>승리한 후보의 비용만 공개</td></tr><tr><td>시간</td><td>접수부터 검증 완료까지의 시간</td><td>대기·통합·검토 시간 제외</td></tr><tr><td>근거</td><td>최종 주장과 연결된 입력·실행·산출물</td><td>로그가 많으면 정확하다고 판단</td></tr></tbody></table></div>
<p>OpenTelemetry 같은 추적 도구는 요청과 세션 경로를 연결해 지연과 오류를 관측하는 데 도움을 준다. 추적 span이 정상 종료됐다고 과제가 옳게 풀렸다는 뜻은 아니다. 산출물의 정확성 검사와 작업 계약 검증을 별도로 둔다. 민감한 내용의 수집 범위도 실행 로그를 저장하기 전에 정한다.</p>
<div class="eq"><span class="cap">전체 자원 사용량으로 비교하는 자체 예시</span><div class="line">총비용 = 추론 + 실험 실행 + 도구 + 실패 재시도 + 최종 검증</div><div class="line">유효 결과당 비용 = 총비용 / 채택된 결과 수</div><div class="line">A: 24 단위 / 6건 = 4 · B: 36 단위 / 9건 = 4</div></div>
<p>위 예시에서 B는 결과 수가 많지만 채택 결과당 비용은 같다. 사용자의 목표가 마감 전 결과 수라면 B가 유리할 수 있고, 총예산이 24라면 A만 허용된다. 성공률·비용·시간을 하나의 ‘에이전트 성능’ 숫자로 압축하면 이 선택을 설명할 수 없다.</p>
<p>Claude·Codex의 모델과 effort를 비교할 때도 같은 원칙을 적용한다. 시스템 구조와 작업 집합을 고정한 뒤 모델·effort 하나를 바꾼다. 높은 effort가 계획 품질을 높여도 호출 지연이 늘 수 있고, 작은 모델을 더 많이 호출하면 통합 비용이 증가할 수 있다. 제품 기본값과 API 평가를 분리하고, 미공개 결과는 측정 전까지 비워 둔다.</p>
<p>최소 복구 점검은 제출 직후 단절, 완료 이벤트 중복, 부분 산출물 저장 뒤 종료, 예산 소진, 재개 전 권한 변경을 포함할 수 있다. 이 문서 회차에서는 이러한 시스템을 배포해 시험하지 않았다. 구조 원문과 계산 예시를 확인했으며, 실제 도입은 해당 환경에서 복구와 중단 조건을 검증하는 작업으로 이어져야 한다.</p>
</section>
"""

READING = [
    '<a href="https://engineering.fb.com/2026/03/17/ml-applications/ranking-engineer-agent-rea-autonomous-ai-system-accelerating-meta-ads-ranking-innovation/">Meta, Ranking Engineer Agent</a> — 2026-03-17. 사내 ML 실험의 대기·재개 사례.',
    '<a href="https://arxiv.org/abs/2610.18083">Zhou et al., AReaL-RSI</a> — arXiv:2610.18083v1, 2026-10-13. 가중치 갱신 없는 연구 역할·기억·절차 개정. 프리프린트.',
    '<a href="https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration">Claude Managed Agents: Multiagent orchestration</a> — subagent·dynamic workflow·공유 실행 자원. 2026-10-20 확인.',
    '<a href="https://platform.claude.com/docs/en/release-notes/overview">Claude Platform release notes</a> — dynamic workflows 10-09, OpenTelemetry 10-14 발표일.',
    '<a href="https://platform.claude.com/docs/en/manage-claude/opentelemetry">OpenTelemetry for the Claude API</a> — 실행 관측과 내보내기.',
    '<a href="https://learn.chatgpt.com/docs/long-running-work">OpenAI: Long-running work</a> — 목표·검토·장기 작업 운영. 2026-10-20 확인.',
]

write(
    'durable-research-agents.html',
    title='장기 실행 연구 에이전트 — 대기·복구·조건부 기억',
    eyebrow='Agent Systems · Durable Execution · 2026-10-20',
    h1='장기 실행 연구 에이전트',
    subtitle='기다리고, 복구하고, 근거를 다음 실험에 넘긴다',
    dek=('Meta REA·Claude 동적 워크플로·AReaL-RSI를 연결해 읽는다. <strong>영속 상태·조건부 기억·절차 개정</strong>을 모델 가중치 학습과 '
 '구분하고, 전체 비용과 복구 성공을 함께 평가한다.'),
    spec=[('실행', '제출 → 대기 → 검증 → 채택'),
 ('기억', '출처·조건·불확실성'),
 ('최근 연구', 'AReaL-RSI · 2026-10-13 v1'),
 ('비교 단위', '전체 실행·시간·비용')],
    date='2026-10-20',
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
)

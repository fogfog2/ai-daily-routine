#!/usr/bin/env python3
"""Weight-space programming: primary-source research note and worked example."""
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ec", panel="#e9e6df", ink="#25231f", **{
    "ink-soft":"#555149", "ink-faint":"#79746b", "rule":"#d4cec2", "rule-strong":"#aaa292",
    "accent":"#65502d", "accent-fill":"#e8ddc6", "accent-line":"#93743c",
    "muted":"#858071", "muted-fill":"#e2dfd6", "warn":"#9a432a"})
DARK = dict(paper="#151410", panel="#201e18", ink="#eee8dc", **{
    "ink-soft":"#b9b1a1", "ink-faint":"#918775", "rule":"#343027", "rule-strong":"#514a3c",
    "accent":"#d6b675", "accent-fill":"#352a17", "accent-line":"#ab8749",
    "muted":"#a0937d", "muted-fill":"#28241d", "warn":"#e59c7d"})

BODY = r'''
<section>
<h2><span class="n">01</span>프로그램의 출력이 신경망의 가중치가 된다</h2>
<p>보통 코딩 에이전트에게 모델 개선을 부탁하면 데이터 전처리, 손실 함수, 학습 루프를 만든다. 실제 숫자를 바꾸는 것은 역전파와 옵티마이저다. <strong>Weight-Space Programming은 자연어 목표를 받은 범용 LLM이 대상 신경망의 가중치를 분석하고 직접 편집하는 접근</strong>이다. 가중치는 모델의 부속 파일이 아니라 프로그램이 읽고 쓰는 산출물이 된다.</p>
<p>사용자가 지정한 원문은 MIT CSAIL 연구진의 <a href="https://rikiyat.github.io/blog/weight-space-programming/">Sparks of Weight-Space Programming</a>이다. 2026년 11월 2일 공개된 초기 연구 보고이며, 상용 API의 새 기능이나 확립된 학습 대체법으로 소개된 것이 아니다. 이 문서는 원문과 저자 로그·공개 체크포인트를 11월 6일 확인해 원리와 조건을 정리한다. 아래 수학 예제는 이해를 위한 자체 구성이다.</p>
<figure><svg viewBox="0 0 760 220" role="img" aria-label="자연어 목표와 대상 가중치를 읽은 LLM이 패치를 만들고 평가 결과를 다음 수정에 반영하는 구조" style="width:100%;height:auto"><g fill="var(--panel)" stroke="var(--rule-strong)"><rect x="15" y="35" width="155" height="80" rx="8"/><rect x="205" y="35" width="150" height="80" rx="8"/><rect x="390" y="35" width="155" height="80" rx="8"/><rect x="580" y="35" width="165" height="80" rx="8"/></g><g fill="var(--ink)" text-anchor="middle" font-size="16"><text x="92" y="67">목표 · 구조 · W</text><text x="92" y="93">읽을 수 있는 증거</text><text x="280" y="67">편집자 LLM</text><text x="280" y="93">진단 → 패치</text><text x="467" y="67">변경된 W′</text><text x="467" y="93">실행되는 대상 모델</text><text x="662" y="67">별도 평가</text><text x="662" y="93">성공 · 부작용 · 비용</text></g><g fill="var(--accent)" font-size="24"><text x="177" y="82">→</text><text x="362" y="82">→</text><text x="552" y="82">→</text></g><path d="M660 117 L660 175 L280 175 L280 117" fill="none" stroke="var(--accent-line)" stroke-width="2"/><text x="460" y="201" text-anchor="middle" fill="var(--ink-soft)" font-size="15">피드백을 허용하는 실험에서만 다음 수정으로 연결</text></svg><figcaption>그림 1. 편집자와 편집 대상은 별개 모델이다. 한 번에 쓰는 실험과 평가 피드백을 받는 실험을 구분한다.</figcaption></figure>
<p>수식으로는 대상 모델을 f<sub>W</sub>, 편집자를 E라고 두고 W′ = E(목표, 구조, W, 허용된 관측)로 나타낼 수 있다. 여기서 E의 출력은 전체 텐서일 수도, 일부 층에 적용하는 패치일 수도 있다. 텍스트로 모든 숫자를 나열해야 한다는 뜻은 아니다. 텐서 파일을 읽는 Python 코드를 작성해 특정 부분만 바꾸는 것도 이 구조에 들어간다.</p>
<div class="eq"><span class="cap">두 가지 갱신 경로</span><div class="line">경사 학습: W′ = W − η ∇<sub>W</sub>L</div><div class="line">직접 편집: W′ = W + ΔW<sub>진단·목표</sub></div><div class="line">차이는 ΔW를 만드는 절차다. 최종 산출물은 모두 가중치다.</div></div>
<p>‘경사 없이’는 대상 가중치의 편집 과정에 대한 말이다. 편집자 LLM과 기반 모델은 이미 학습돼 있다. 평가용 순전파를 허용하면 대상 모델 실행 비용도 든다. <a href="durable-research-agents.html">연구 에이전트</a>가 학습 스크립트의 하이퍼파라미터를 고치는 경우와, 가중치 자체를 고치는 경우를 먼저 나누어 읽으면 새로움이 선명해진다.</p>
</section>
<section>
<h2><span class="n">02</span>읽기·수정·작성은 서로 다른 능력이다</h2>
<p>가중치를 ‘이해했다’고 하려면 무엇을 맞혔는지 정해야 한다. 입력의 어느 위치를 보는지 추측하는 일, 특정 실패의 원인을 찾는 일, 새로운 정책을 만드는 일은 필요한 증거와 성공 기준이 다르다. <a href="interpretability.html">해석가능성</a>에서 상관관계와 인과 개입을 구분하듯, 그럴듯한 설명과 실제 동작 변화도 분리해야 한다.</p>
<div class="scroller"><table class="data"><thead><tr><th>작업</th><th>편집자가 받는 것</th><th>검증할 것</th></tr></thead><tbody>
<tr><td>읽기</td><td>가중치·아키텍처·입출력 의미</td><td>학습 과제나 행동의 식별 정확성</td></tr>
<tr><td>수정</td><td>기존 가중치·실패 사례·목표</td><td>실패 감소와 기존 동작의 보존</td></tr>
<tr><td>처음부터 작성</td><td>구조·환경 규칙·초기 텐서</td><td>생성된 정책의 실제 성과</td></tr>
</tbody></table></div>
<p>원문의 작은 네트워크 실험은 게임 식별·정책 수정·정책 작성을 다룬다. 규모를 키운 실험은 Python과 제한된 평가를 허용한다. 특히 아첨 모델 식별은 가중치만으로 실패했고 어텐션 관측을 추가한 뒤 성공했다. 이 차이는 ‘가중치만 보면 어떤 성향이든 알아낸다’는 결론을 막는다.</p>
<p>같은 함수를 구현하는 가중치 표현은 하나가 아니다. 예를 들어 2층 ReLU 네트워크에서 은닉 뉴런의 순서를 동시에 바꾸어도 함수는 그대로다. 순열 행렬 P에 대해 W₁′ = PW₁, W₂′ = W₂P<sup>T</sup>로 바꾸면 ReLU(Pz) = PReLU(z)이므로 W₂′ReLU(W₁′x) = W₂ReLU(W₁x)다. 따라서 특정 좌표가 늘 같은 의미를 가진다고 일반화하기 어렵다.</p>
<div class="note"><b>‘관측 없음’의 단위를 확인한다.</b> 네트워크 실행을 금지해도 구조·입력 채널·행동 목록을 알려줄 수 있다. 학습 데이터 없이 규칙을 읽는 것과, 아무 정보 없이 능력을 만드는 것은 다르다. 구조 설명과 도구 출력도 실험의 정보 예산이다.</div>
<p>실제 적용에서는 층 이름, 텐서 모양, 좌표계, 활성 함수, 정규화 위치를 함께 제공해야 한다. 어느 행렬이 입력을 읽고 어느 행렬이 잔차 스트림에 쓰는지 모르면 행과 열의 해석부터 뒤집힌다. 출력 설명만 맞혔다면 독립 사례에 예측을 적용하고, 수정 이유를 주장했다면 해당 부분만 바꾼 절제 실험으로 확인한다.</p>
</section>
<section>
<h2><span class="n">03</span>Qwen 사례 — 새 지식을 넣기보다 반복을 줄였다</h2>
<p>공개 체크포인트 카드에 따르면 Astra는 Qwen3.5-0.8B의 15·19층 MLP <code>down_proj</code>에서 각각 64개 출력 열을 수정했다. 총 131,072개, 약 0.016%의 파라미터다. 연습 문제의 50회 forward-pass 예산을 썼으므로 이 사례는 무피드백·무데이터 편집이 아니다. 역전파 학습을 하지 않은 가중치 수정이라는 의미다.</p>
<div class="scroller"><table class="data"><thead><tr><th>체크포인트</th><th>MATH-500</th><th>GSM8K</th><th>IFEval</th><th>MATH 토큰 한도 도달</th></tr></thead><tbody>
<tr><td>원문 기반 모델</td><td>7.9%</td><td>13.8%</td><td>21.0%</td><td>93.0%</td></tr>
<tr><td>원문 편집 모델 · 50회</td><td>48.1%</td><td>67.1%</td><td>62.3%</td><td>33.1%</td></tr>
</tbody></table></div>
<p>모델 카드의 프로토콜은 thinking 활성화·최대 32,768토큰과 동일한 샘플링 설정을 사용한다. 원문은 MATH-500을 문제당 4회 샘플링했다. 이는 500문제를 모두 한 번에 푼 단일 정답률이나 best-of-4 수치로 임의 변환하면 안 된다. 원문 저자 실험이며 이 문서에서 대형 모델 평가를 재실행하지 않았다.</p>
<p>이 현상은 답을 끝내지 못하던 반복 루프를 줄여 성능이 회복된 사례로 읽어야 한다. 원문의 추가 Gemma 실험에서는 개선을 입증하지 못했다. ‘가중치를 조금 건드리면 모든 작은 모델에 새 수학 능력이 생긴다’는 일반 법칙으로 확장할 근거는 없다.</p>
<p>체크포인트 카드에는 akhaliq의 별도 재실행도 기록돼 있다. 편집 모델의 전체 MATH-500은 51.0%였지만 기반 모델 점검은 25문제였다. 따라서 두 값을 완전히 같은 규모의 독립 A/B 비교로 제시하지 않는다. 재실행은 멀티모달 체크포인트를 사용했고 원문은 텍스트 전용 export를 사용했다는 차이도 카드에 명시돼 있다.</p>
<div class="eq"><span class="cap">수치의 분모를 따로 읽는다</span><div class="line">변경 비율 ≈ 131,072 / 800,000,000 × 100 = 0.016384%</div><div class="line">MATH-500 차이 = 48.1 − 7.9 = 40.2%p</div><div class="line">변경 비율은 학습 비용·시간·메모리 절감률이 아니다.</div></div>
<p>공개 로그의 모델은 <code>gpt-6-astra</code>이고 실험마다 effort가 다르다. 로그 README는 실험 1·2·4에 high, 3·5·6·7에 xhigh, 8에 max를 기록한다. Codex 자체 도구를 끄고, Python이 허용된 실험은 외부 샌드박스가 실행 결과를 다음 메시지로 돌려줬다. ‘Codex 도구 호출이 없다’는 기록을 ‘실험 전체에 Python이 없다’로 해석하면 안 된다.</p>
<p>이 자료는 Astra·Sol·Luna와 Claude의 effort별 우열을 평가한 벤치마크가 아니다. 같은 모델의 effort를 바꾼 통제 비교도 아니다. 결과를 재현할 때는 편집자 모델·effort뿐 아니라 대상 체크포인트 revision, 프롬프트, 허용 관측, 연습 문제와 평가 문제의 분리까지 기록해야 한다.</p>
</section>
<section>
<h2><span class="n">04</span>작은 행렬로 이해하는 직접 편집과 부작용</h2>
<p>다음은 원문의 패치를 재현하는 코드가 아니라 방향 제거의 의미를 설명하는 자체 예제다. 어떤 층의 출력이 y = Wx이고 단위 벡터 u 방향의 출력을 줄이고 싶다고 하자. 투영을 빼면 W′ = (I − αuu<sup>T</sup>)W가 된다. α = 1이면 출력의 u 성분을 제거하고, α = 0이면 원본을 유지한다.</p>
<div class="eq"><span class="cap">단위 벡터 u에 대한 출력 방향 제거</span><div class="line">W′ = W − αu(u<sup>T</sup>W)</div><div class="line">u<sup>T</sup>W′x = (1 − α)u<sup>T</sup>Wx</div><div class="line">u에 수직인 v는 v<sup>T</sup>W′x = v<sup>T</sup>Wx</div></div>
<p>W = [[2, 1], [1, 3]], u = [1, 0], x = [1, 2]라면 원래 출력은 [4, 7]이다. α를 0.5로 두면 [2, 7], 1로 두면 [0, 7]이 된다. 아래 코드는 표준 Python만 사용하며 이 문서를 작성하면서 실행해 확인했다.</p>
<pre style="max-width:100%;overflow-x:auto"><code>W = [[2.0, 1.0], [1.0, 3.0]]
u = [1.0, 0.0]  # 단위 벡터
x = [1.0, 2.0]

def edit(W, u, alpha):
    # u^T W의 열별 값
    dots = [sum(u[i] * W[i][j] for i in range(2))
            for j in range(2)]
    return [[W[i][j] - alpha * u[i] * dots[j]
             for j in range(2)] for i in range(2)]

def forward(W, x):
    return [sum(a * b for a, b in zip(row, x)) for row in W]

for alpha in [0.0, 0.5, 1.0]:
    print(alpha, forward(edit(W, u, alpha), x))
# 0.0 [4.0, 7.0]
# 0.5 [2.0, 7.0]
# 1.0 [0.0, 7.0]</code></pre>
<p>여기서 보존되는 것은 이 선형층 출력의 수직 성분이다. 이후에 비선형 함수·정규화·다른 층을 통과하면 최종 모델의 행동까지 보존된다는 보장은 없다. 제거한 방향이 반복뿐 아니라 유용한 계산에도 쓰였다면 다른 과제에 손실이 생길 수 있다. ‘한 방향 = 한 행동’은 검증할 가설이지 구조적 보장이 아니다.</p>
<figure><svg viewBox="0 0 660 230" role="img" aria-label="원본 출력 4 7에서 첫 방향 성분을 제거하면 0 7이 되지만 모델 전체의 행동 보존은 보장되지 않는 예" style="width:100%;height:auto"><path d="M70 190 L70 25 M70 190 L310 190" stroke="var(--rule-strong)" fill="none" stroke-width="2"/><path d="M70 190 L250 55 M70 55 L250 55" stroke="var(--muted)" fill="none" stroke-width="2" stroke-dasharray="5 4"/><path d="M70 190 L70 55" stroke="var(--accent-line)" fill="none" stroke-width="5"/><circle cx="250" cy="55" r="6" fill="var(--muted)"/><circle cx="70" cy="55" r="6" fill="var(--accent)"/><g fill="var(--ink)" font-size="16"><text x="180" y="38">원본 (4, 7)</text><text x="84" y="82">편집 (0, 7)</text><text x="170" y="215">제거한 방향 u</text><text x="355" y="85">한 층에서 성분을 지운다</text><text x="355" y="120">↓</text><text x="355" y="155">전체 과제의 변화는 별도 평가</text></g></svg><figcaption>그림 2. 자체 선형 예제. 좌표에서 보이는 국소 보존 성질과 전체 신경망의 성능 보존은 별개다.</figcaption></figure>
<p><a href="lora.html">LoRA</a>도 작은 ΔW를 만들지만 A·B를 데이터와 경사로 학습한다. 위 투영 예제의 ΔW는 랭크 1 이하이지만 계산 이유가 다르다. 변화량의 모양이 저랭크라는 사실만으로 같은 학습법이 되지는 않는다. <a href="https://arxiv.org/abs/2202.05262">ROME</a>는 사실 연관을 표적 편집하는 별도 방법으로, 범용 LLM이 자연어 목표를 해석해 편집안을 구성하는 접근과 구분한다.</p>
</section>
<section>
<h2><span class="n">05</span>어디에 쓰고, 어떻게 검증할 것인가</h2>
<p>처음 적용할 대상은 원인과 목표가 좁은 실패다. 특정 입력에서 반복하는 소형 모델, 단순 환경의 정책, 구조를 이해할 수 있는 작은 네트워크가 출발점이 될 수 있다. 정확한 기계 동작이나 사업 지식을 새로 추가해야 하는 문제라면 가중치 편집만으로 해결된다고 가정하지 않고 데이터 기반 적응·검색·도구 연동과 비교한다.</p>
<div class="scroller"><table class="data"><thead><tr><th>접근</th><th>변경 대상</th><th>핵심 차이</th></tr></thead><tbody>
<tr><td>프롬프트·에이전트 개선</td><td>입력·도구·절차</td><td>대상 모델의 가중치는 고정</td></tr>
<tr><td>파인튜닝·LoRA</td><td>전체 가중치·저랭크 변화량</td><td>데이터와 목적 함수로 학습</td></tr>
<tr><td>HyperNetworks</td><td>다른 모델을 생성하는 신경망</td><td>가중치 생성기 자체를 학습</td></tr>
<tr><td>Tracr</td><td>제한된 언어의 프로그램</td><td>명시적인 컴파일 규칙으로 Transformer 구성</td></tr>
<tr><td>Weight-Space Programming</td><td>가중치·텐서 패치</td><td>범용 LLM의 진단·추론으로 편집안 구성</td></tr>
</tbody></table></div>
<p>재현은 공개 <a href="https://github.com/RikiyaT/lm_understand-logs">실험 로그</a>에서 프롬프트와 실행 조건을 읽는 것부터 시작한다. 저장소에는 보고된 실행과 코드·출력·최종 네트워크가 있으며 초기 프롬프트 버전의 시험 실행은 빠져 있다고 명시돼 있다. 공개된 성공 로그만으로 전체 시도의 성공 확률을 추정하지 않는다. 변경된 Qwen 모델과 데모는 더 읽을거리에 연결했다.</p>
<p>자체 실험에서는 원본을 복사하고 수정 대상 텐서·shape·dtype·해시를 남긴다. 패치가 끝나면 허용한 텐서만 바뀌었는지, NaN·Inf가 없는지, 로딩과 최소 추론이 되는지 확인한다. 이어서 편집에 쓰지 않은 보류 집합에서 목표 실패를 측정하고 다른 과제의 회귀를 검사한다. 문제에 답할 때까지의 토큰 수·정답률·최대 길이 도달률을 함께 기록하면 반복 억제와 새로운 문제 해결 능력을 구분하는 데 도움이 된다.</p>
<div class="eq"><span class="cap">실제 비교에 들어가는 총비용</span><div class="line">편집 비용 = 편집자 추론 + 대상 모델 실행 + 검증 + 실패 후보</div><div class="line">작은 패치 ≠ 작은 탐색 비용 ≠ 작은 배포 메모리</div></div>
<p>변경 파일이 작더라도 배포 시 전체 모델을 올려야 할 수 있다. GPU 없이 편집 코드를 작성하더라도 대상 모델 평가에는 GPU를 사용할 수 있다. forward-pass 한 번이 여러 문제의 배치라면 횟수만으로 비용을 비교할 수 없다. <a href="experiment-tracking.html">실험 관리</a>에 모델 호출·토큰·배치 크기·대상 추론 시간을 함께 남기고 동일 예산의 학습 기준선과 비교한다.</p>
<p>가중치를 볼 수 없는 API 전용 모델은 이 방식의 직접 편집 대상이 될 수 없다. 반대로 편집자 역할은 API 모델이 맡고, 대상은 로컬 오픈 가중치 모델로 둘 수 있다. 이 경우 편집자가 실제로 읽은 텐서와 통계의 범위가 한계가 된다. 수십억 개 숫자를 모두 프롬프트로 읽는 방식보다 층별 분석과 국소 가설 검증이 현실적인 출발점이다.</p>
<div class="note"><b>확인한 범위.</b> 이 페이지는 저자 보고·공개 로그·체크포인트 카드와 관련 논문을 읽어 작성했다. 선형 예제와 비율 계산은 실행 검증했다. 원문의 게임 실험이나 Qwen/Gemma 전체 벤치마크는 재실행하지 않았으며, 일반 모델의 재학습을 대체할 정도의 범용성은 아직 입증된 결과로 취급하지 않는다.</div>
</section>
'''

READING = [
    '<a href="https://rikiyat.github.io/blog/weight-space-programming/">Takehi et al., Sparks of Weight-Space Programming</a> — 2026-11-02. 사용자 지정 원문·초기 실험 보고.',
    '<a href="https://github.com/RikiyaT/lm_understand-logs">저자 공개 로그·하네스·편집 코드</a> — 실험별 프롬프트, 모델 effort, 허용 도구, 최종 산출물.',
    '<a href="https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming">편집 Qwen 체크포인트와 재실행 기록</a> — 원문 결과·별도 재실행·설정 차이를 구분한다.',
    '<a href="https://huggingface.co/spaces/akhaliq/weight-space-programming-demo">akhaliq의 비교 데모</a> — 외부 데모. 여기서 실행 결과를 직접 검증하지 않았다.',
    '<a href="https://arxiv.org/abs/2106.09685">Hu et al., LoRA</a> — 저랭크 변화량을 학습하는 비교 대상.',
    '<a href="https://arxiv.org/abs/2202.05262">Meng et al., ROME</a> — 사실 연관의 위치 분석과 표적 가중치 편집.',
    '<a href="https://arxiv.org/abs/1609.09106">Ha et al., HyperNetworks</a> — 다른 신경망의 가중치를 생성하는 학습된 모델.',
    '<a href="https://arxiv.org/abs/2301.05062">Lindner et al., Tracr</a> — 프로그램을 Transformer로 컴파일하는 비교 대상.',
]

if __name__ == '__main__':
    write('weight-space-programming.html', title='Weight-Space Programming — LLM이 가중치를 읽고 고친다',
          eyebrow='Model Adaptation · Weight Editing · 2026-11-06', h1='Weight-Space Programming',
          subtitle='LLM이 신경망의 숫자를 직접 읽고, 고치고, 작성한다',
          dek='학습 루프를 만드는 에이전트에서 <strong>가중치 자체를 편집하는 에이전트</strong>로. Qwen의 반복 억제 사례와 실패 조건을 읽고, 작은 행렬 예제로 직접 편집의 원리와 한계를 살펴본다.',
          spec=[('핵심', '자연어 목표 → 텐서 패치'), ('구분', '읽기 · 수정 · 처음부터 작성'), ('원문', 'MIT CSAIL · 2026-11-02'), ('확인', '2026-11-06 · 초기 연구')],
          body=BODY, reading=READING, light=LIGHT, dark=DARK, date='2026-11-06')

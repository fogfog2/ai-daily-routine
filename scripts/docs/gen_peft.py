#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ee", panel="#e6e8e3", ink="#161913", **{
    "ink-soft": "#505548", "ink-faint": "#7e8475", "rule": "#d1d4cb",
    "rule-strong": "#adb1a5", "accent": "#3f6320", "accent-fill": "#e0ead4",
    "accent-line": "#628c3a", "muted": "#83878d", "muted-fill": "#dee0e3", "warn": "#a04d26",
})
DARK = dict(paper="#101210", panel="#181b16", ink="#e7eae2", **{
    "ink-soft": "#a5aa9c", "ink-faint": "#7a7f71", "rule": "#22261e", "rule-strong": "#383f30",
    "accent": "#8fc75e", "accent-fill": "#1a2612", "accent-line": "#5f8c3c",
    "muted": "#878d93", "muted-fill": "#1a1d20", "warn": "#e0895c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>어디에 무엇을 끼워 넣을 것인가</h2>
    <p>
      전체 파인튜닝이 비싼 이유는 <a href="lora.html">LoRA 문서</a>에서 다뤘다 —
      7B 모델에 112GB가 든다. 해결 방향은 하나다.
      <strong>대부분을 얼리고 작은 부분만 학습한다.</strong>
    </p>
    <p>
      그런데 "작은 부분"을 어디에 둘지는 여러 선택지가 있고,
      그 선택이 <em>추론 지연·메모리·성능</em>을 각각 다르게 바꾼다.
      PEFT 계열을 가르는 축은 결국 <strong>삽입 위치와 결합 방식</strong>이다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방식</th><th>어디에</th><th>어떻게 결합</th><th>추론 지연</th></tr>
        </thead>
        <tbody>
          <tr><td>Adapter</td><td>층 사이</td><td class="hi">직렬 (경로가 길어짐)</td><td>증가</td></tr>
          <tr><td>Prefix / Prompt</td><td>입력 앞</td><td>가상 토큰 추가</td><td>증가 (문맥 소모)</td></tr>
          <tr><td>LoRA</td><td>선형 층 옆</td><td class="hi">병렬 (더하기)</td><td class="hi">없음 (병합 시)</td></tr>
          <tr><td>IA³</td><td>활성값에</td><td class="hi">곱하기 (스케일)</td><td class="hi">거의 없음</td></tr>
          <tr><td>BitFit</td><td>bias 항</td><td>기존 파라미터만</td><td class="hi">없음</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>Adapter — 원조, 그리고 직렬의 대가</h2>
    <p>
      PEFT의 출발점은 2019년 Houlsby 등의 <strong>Adapter</strong>다.
      트랜스포머 블록 안에 작은 병목 모듈을 <em>끼워 넣는다</em>.
    </p>
    <div class="eq">
      <span class="cap">Adapter — 내렸다가 올리는 병목 구조</span>
      <div class="line">h ← h + W<sub>up</sub> · f( W<sub>down</sub> · h )</div>
      <div class="line">W<sub>down</sub> ∈ ℝ<sup>d×r</sup>,&nbsp; W<sub>up</sub> ∈ ℝ<sup>r×d</sup>,&nbsp; r ≪ d</div>
      <div class="line">// W_up 을 0 에 가깝게 초기화 → 처음엔 항등 함수</div>
    </div>
    <p>
      아이디어는 LoRA와 닮았다. 차원을 줄였다 늘리고,
      <a href="residual-connections.html">잔차</a>로 더하고,
      초기에는 아무 영향이 없게 시작한다 — 블록 끝을 0 으로 두는 그 관행 그대로다. 성능도 전체 파인튜닝에 근접했다.
    </p>
    <p>
      결정적 차이는 <strong>직렬</strong>이라는 점이다.
      기존 계산이 끝난 뒤 어댑터를 통과해야 다음으로 간다.
      순전파 경로에 층이 추가되므로 <em>원본 가중치에 합쳐 없앨 수가 없다</em>.
      배치 크기가 작은 온라인 추론에서 이 지연이 무시하기 어려운 수준이 된다는 보고가 있었다.
    </p>
    <p>
      LoRA 논문이 자신의 기여를 설명할 때 이 지점을 정면으로 겨냥한다 —
      <strong>병렬로 붙이면 더해서 없앨 수 있다.</strong>
      같은 저랭크 아이디어인데 결합 방식 하나가 배포 특성을 갈랐다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>Prefix·Prompt — 가중치 대신 입력을 바꾼다</h2>
    <p>
      전혀 다른 접근도 있다. 모델은 전혀 건드리지 않고
      <strong>입력 앞에 학습되는 벡터를 붙이는</strong> 것이다.
    </p>
    <p>
      <strong>Prompt Tuning</strong>은 임베딩 층에만 가상 토큰 <code>k</code>개를 붙인다.
      사람이 프롬프트를 손으로 쓰는 대신, <em>연속 공간에서 최적의 프롬프트를 경사하강으로 찾는</em> 셈이다.
      실제 단어에 대응할 필요가 없으므로 표현력이 훨씬 넓다.
    </p>
    <p>
      <strong>Prefix Tuning</strong>은 한 걸음 더 간다.
      임베딩만이 아니라 <em>모든 층의 어텐션 K·V에</em> 학습되는 접두사를 붙인다.
      매 층에서 개입하므로 더 강력하지만 파라미터도 더 든다.
    </p>
    <div class="note">
      <b>규모에 따라 평가가 갈린다.</b> Prompt Tuning은 모델이 작을 때는
      전체 파인튜닝에 한참 못 미치다가, <strong>10B를 넘어서면 격차가 거의 사라진다</strong>.
      큰 모델일수록 "무엇을 하라"는 신호만 잘 주면 되고,
      가중치를 고칠 필요가 줄어든다는 해석이다.
    </div>
    <p>
      실무적 약점은 분명하다. <strong>문맥 길이를 먹는다.</strong>
      접두사가 20~100 토큰을 차지하면 그만큼 실제 입력이 줄고,
      어텐션 비용도 늘어난다. 학습 안정성도 LoRA보다 까다롭다는 평이 많다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>IA³ — 더하지 않고 곱한다</h2>
    <p>
      <strong>IA³</strong>는 접근이 다르다. 새 행렬을 더하는 대신
      기존 활성값에 <strong>학습되는 벡터를 곱한다</strong>.
      키·값·FFN 중간 활성에 각각 스케일 벡터를 하나씩 둔다.
    </p>
    <div class="eq">
      <span class="cap">IA³ — 벡터 세 개면 끝난다</span>
      <div class="line">어텐션:&nbsp; softmax( Q (<strong>l<sub>k</sub></strong> ⊙ K)ᵀ / √d ) (<strong>l<sub>v</sub></strong> ⊙ V)</div>
      <div class="line">FFN:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; W<sub>2</sub> ( <strong>l<sub>ff</sub></strong> ⊙ f(W<sub>1</sub>x) )</div>
      <div class="line">// 학습 파라미터는 벡터 3개 — 행렬이 아니다</div>
      <div class="line">// 1 로 초기화하면 시작 시점에 항등</div>
    </div>
    <p>
      파라미터 수가 LoRA보다도 한 자릿수 적다.
      "무엇을 강조하고 무엇을 죽일지"만 조절하는 방식인데,
      few-shot 상황에서 놀랄 만큼 잘 작동한다는 결과가 보고됐다.
      곱셈이라 <strong>원본 가중치에 흡수시킬 수도 있어</strong> 추론 지연도 거의 없다.
    </p>
    <p>
      가장 극단적으로 단순한 것은 <strong>BitFit</strong>이다.
      새 파라미터를 아예 만들지 않고 <em>기존의 bias 항만</em> 학습한다.
      전체의 약 0.1% 미만이다. 큰 과제에서는 밀리지만,
      "이 정도로도 상당 부분 된다"는 사실 자체가 시사적이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 224" role="img" aria-label="PEFT 방식별 삽입 위치 비교 도식. Adapter는 층 사이에 직렬로 들어가 경로가 길어지고, Prefix는 입력 앞에 가상 토큰을 붙여 문맥을 소모하며, LoRA는 선형 층 옆에 병렬로 붙어 병합 가능하고, IA³는 활성값에 스케일 벡터를 곱한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="pf-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
              <marker id="pf-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">Adapter — 직렬</text>
            <rect x="24" y="30" width="46" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="47" y="46" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">층</text>
            <path d="M74 42 L88 42" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#pf-a)"/>
            <rect x="92" y="30" width="46" height="24" fill="var(--warn)" opacity="0.22" stroke="var(--warn)" stroke-width="1.4"/>
            <text x="115" y="46" text-anchor="middle" font-size="8" fill="var(--ink)">어댑터</text>
            <path d="M142 42 L156 42" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#pf-a)"/>
            <rect x="160" y="30" width="46" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="183" y="46" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">층</text>
            <text x="24" y="76" font-size="8.5" fill="var(--warn)">경로가 길어져 병합 불가 → 지연 증가</text>

            <line x1="24" y1="90" x2="330" y2="90" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="112" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">Prefix — 입력 앞</text>
            <rect x="24" y="124" width="60" height="24" fill="var(--warn)" opacity="0.22" stroke="var(--warn)" stroke-width="1.4"/>
            <text x="54" y="140" text-anchor="middle" font-size="8" fill="var(--ink)">가상 토큰</text>
            <rect x="88" y="124" width="118" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="147" y="140" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">실제 입력</text>
            <text x="24" y="170" font-size="8.5" fill="var(--warn)">문맥 길이를 먹는다</text>
            <text x="24" y="184" font-size="8.5" fill="var(--ink-faint)">가중치는 전혀 안 건드린다</text>

            <line x1="346" y1="26" x2="346" y2="212" stroke="var(--rule)" stroke-width="1"/>

            <text x="370" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">LoRA — 병렬 (더하기)</text>
            <rect x="370" y="30" width="70" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2" stroke-dasharray="4 3"/>
            <text x="405" y="47" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">W₀ ❄</text>
            <rect x="370" y="64" width="70" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="405" y="78" text-anchor="middle" font-size="8" fill="var(--accent)">B A</text>
            <circle cx="470" cy="52" r="11" fill="none" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="470" y="57" text-anchor="middle" font-size="11" fill="var(--accent)">+</text>
            <path d="M444 44 L458 48" stroke="var(--rule-strong)" stroke-width="1.2" marker-end="url(#pf-a)"/>
            <path d="M444 72 L460 60" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#pf-b)"/>
            <text x="370" y="104" font-size="8.5" fill="var(--accent)">W₀ + BA 로 합쳐진다 → 지연 0</text>

            <line x1="370" y1="118" x2="674" y2="118" stroke="var(--rule)" stroke-width="1"/>

            <text x="370" y="140" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">IA³ — 곱하기 (스케일)</text>
            <rect x="370" y="152" width="70" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="405" y="168" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">활성값</text>
            <circle cx="468" cy="164" r="11" fill="none" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="468" y="169" text-anchor="middle" font-size="11" fill="var(--accent)">⊙</text>
            <path d="M444 164 L456 164" stroke="var(--rule-strong)" stroke-width="1.2" marker-end="url(#pf-a)"/>
            <rect x="490" y="152" width="60" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="520" y="168" text-anchor="middle" font-size="8" fill="var(--accent)">벡터 l</text>
            <text x="370" y="196" font-size="8.5" fill="var(--accent)">행렬이 아니라 벡터 3개 — 가장 가볍다</text>
            <text x="370" y="210" font-size="8.5" fill="var(--ink-faint)">1 로 초기화하면 시작 시 항등</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        같은 목표(작은 부분만 학습)에 도달하는 네 가지 경로다.
        갈리는 지점은 성능이 아니라 <strong>결합 방식</strong> —
        더하기와 곱하기는 원본에 흡수되고, 직렬 삽입과 접두사는 그렇지 않다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>그래서 무엇을 쓰는가</h2>
    <p>
      실무의 기본값은 <strong>LoRA</strong>다. 이유는 성능이 가장 높아서가 아니라
      <em>제약이 가장 적어서</em>다 — 병합하면 지연이 0이고, 안 하면 어댑터를 갈아끼울 수 있고,
      하이퍼파라미터가 <code>r</code>과 붙일 위치 정도로 단순하다.
    </p>
    <p>
      다만 선택이 갈리는 경우들이 있다.
    </p>
    <ul>
      <li><strong>메모리가 극단적으로 부족하면</strong> — QLoRA. 베이스를 4비트로 얼리고 LoRA를 얹는다.</li>
      <li><strong>예시가 극소수라면</strong> — IA³. few-shot에서 강하다는 결과가 있고, 학습 파라미터가 가장 적다.</li>
      <li><strong>과제가 수백 개라면</strong> — Prompt Tuning. 과제당 저장 비용이 벡터 몇 개 수준이고, 배치 안에서 서로 다른 접두사를 섞기 쉽다.</li>
      <li><strong>도메인 자체가 크게 다르면</strong> — PEFT로는 한계가 있다. 사전학습 분포에서 멀리 떨어진 데이터(새 언어, 특수 표기 체계)는 전체 파인튜닝이나 계속 사전학습이 필요할 수 있다.</li>
    </ul>
    <div class="note">
      <b>PEFT가 항상 전체 파인튜닝과 같지는 않다.</b> 요약·분류처럼 사전학습 능력을
      <em>끌어내는</em> 과제에서는 거의 차이가 없지만,
      새 지식을 <em>주입해야</em> 하는 과제에서는 격차가 남는다는 보고가 있다.
      "0.1%만 학습해도 100%와 같다"는 표현은 <strong>과제 종류에 따라 조건부로</strong> 읽어야 한다.
    </div>
    <p>
      정리하면 PEFT 계열의 공통 전제는 하나다 —
      <em>파인튜닝이 만드는 변화는 좁은 부분공간에 있다.</em>
      그 전제 위에서 각 방법은 <strong>그 좁은 공간을 어디에 어떻게 마련할지</strong>만 다르게 답한다.
      그리고 배포 관점에서는 성능 차이보다 <strong>원본에 흡수되는가</strong>가 더 중요한 구분선이 됐다.
    </p>
  </section>
"""

READING = [
    "Houlsby et al., <em>Parameter-Efficient Transfer Learning for NLP</em> (arXiv:1902.00751) — 원조 Adapter.",
    "Li &amp; Liang, <em>Prefix-Tuning: Optimizing Continuous Prompts for Generation</em> (arXiv:2101.00190) — 모든 층의 K·V에 접두사.",
    "Lester et al., <em>The Power of Scale for Parameter-Efficient Prompt Tuning</em> (arXiv:2104.08691) — 규모가 커지면 격차가 사라진다.",
    "Liu et al., <em>Few-Shot Parameter-Efficient Fine-Tuning is Better and Cheaper than In-Context Learning</em> (arXiv:2205.05638) — IA³.",
    "Zaken et al., <em>BitFit: Simple Parameter-efficient Fine-tuning for Transformer-based Masked Language-models</em> (arXiv:2106.10199) — bias만 학습.",
    "Hu et al., <em>LoRA: Low-Rank Adaptation of Large Language Models</em> (arXiv:2106.09685) — 병렬 결합의 근거.",
]

write(
    "peft-adapters.html",
    title="PEFT — Adapter·Prefix·IA³",
    eyebrow="Adaptation · Parameter-Efficient Methods · 2019–2026",
    h1="PEFT — Adapter·Prefix·IA³",
    subtitle="LoRA 말고도 있는 길 — 어디에 무엇을 끼워 넣을 것인가",
    dek=(
        "대부분을 얼리고 작은 부분만 학습한다는 목표는 같다. "
        "갈리는 것은 <strong>어디에 끼워 넣고 어떻게 결합하는가</strong>다. "
        "직렬로 넣으면 경로가 길어져 추론이 느려지고, 접두사로 넣으면 문맥을 먹는다. "
        "더하기와 곱하기만이 원본 가중치에 흡수돼 지연 없이 배포된다."
    ),
    spec=[
        ("공통 전제", "변화는 좁은 부분공간"),
        ("Adapter", "직렬 · 병합 불가"),
        ("Prefix", "문맥 소모"),
        ("LoRA", "병렬 · 병합 가능"),
        ("IA³", "스케일 벡터 3개"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

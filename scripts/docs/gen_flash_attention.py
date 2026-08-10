#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eef0f1", panel="#e3e6e8", ink="#12181c", **{
    "ink-soft": "#4a545b", "ink-faint": "#7a848b", "rule": "#cdd2d5",
    "rule-strong": "#a9b0b5", "accent": "#1a5f8a", "accent-fill": "#d9e8f2",
    "accent-line": "#2c7fb0", "muted": "#82888e", "muted-fill": "#dde1e4", "warn": "#a03e28",
})
DARK = dict(paper="#0e1215", panel="#161b1f", ink="#e3eaee", **{
    "ink-soft": "#a0abb2", "ink-faint": "#6f797f", "rule": "#212729", "rule-strong": "#374045",
    "accent": "#5cb6e8", "accent-fill": "#102834", "accent-line": "#3a86b5",
    "muted": "#868d94", "muted-fill": "#1a1f23", "warn": "#e0805f",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>느린 이유가 곱셈이 아니었다</h2>
    <p>
      어텐션이 느린 이유를 물으면 대부분 <code>O(n²)</code> 연산량을 든다.
      시퀀스가 두 배가 되면 곱셈이 네 배가 되니까. 맞는 말이지만, 실제 GPU에서
      시간을 잡아먹는 것은 <strong>곱셈이 아니라 메모리 왕복</strong>이었다.
    </p>
    <p>
      현대 GPU의 연산 능력은 메모리 대역폭보다 훨씬 빠르게 발전해 왔다.
      A100 기준으로 숫자를 보면 격차가 분명하다.
    </p>
    <div class="eq">
      <span class="cap">A100 40GB — 계산은 넘치고 통로가 좁다</span>
      <div class="line">연산 성능 (bf16 텐서코어)   312 TFLOP/s</div>
      <div class="line">HBM 대역폭                  1.5 TB/s</div>
      <div class="line">SRAM 대역폭                 약 19 TB/s   (용량은 SM당 192KB뿐)</div>
      <div class="line">──────────────────────────────────────────────</div>
      <div class="line">비율: 연산이 대역폭보다 <strong>200배 이상</strong> 빠르다</div>
    </div>
    <p>
      즉 데이터를 한 번 읽어오는 동안 GPU는 수백 번의 곱셈을 할 수 있다.
      이런 장비에서는 <strong>얼마나 계산하는가</strong>보다 <strong>얼마나 읽고 쓰는가</strong>가 시간을 정한다.
      이런 연산을 <em>memory-bound</em>라고 부르고, 표준 어텐션이 정확히 여기 해당한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>N×N 행렬을 실제로 만들어 쓰는 대가</h2>
    <p>
      교과서적인 어텐션 구현은 네 단계를 순서대로 밟는다.
      각 단계마다 결과를 HBM에 쓰고 다음 단계에서 다시 읽는다.
    </p>
    <div class="eq">
      <span class="cap">표준 구현 — 매 줄이 HBM 왕복이다</span>
      <div class="line">S = QKᵀ           HBM에 <strong>N×N</strong> 쓰기</div>
      <div class="line">P = softmax(S)    N×N 읽기 → N×N 쓰기</div>
      <div class="line">(드롭아웃)         N×N 읽기 → N×N 쓰기</div>
      <div class="line">O = PV            N×N 읽기</div>
    </div>
    <p>
      문제는 저 <code>N×N</code>이다. <code>N = 8192</code>, fp16, 헤드 32개라면
      중간 행렬 하나가 <strong>4GB</strong>다. 이걸 쓰고 읽기를 여러 번 반복한다.
    </p>
    <p>
      그런데 우리가 원하는 최종 출력 <code>O</code>는 <code>N×d</code> 크기다.
      <code>d = 128</code>이면 그 행렬은 <code>N×N</code>보다 64배 작다.
      <strong>필요하지도 않은 거대한 중간물을 메모리에 왕복시키느라</strong> 시간을 쓰고 있는 셈이다.
    </p>
    <div class="note">
      <b>메모리 사용량도 여기서 온다.</b> 어텐션이 <code>O(N²)</code> 메모리를 쓴다는 말은
      수학적 필연이 아니라 <em>이 구현 방식</em>의 결과다.
      FlashAttention은 같은 수식을 <code>O(N)</code> 메모리로 계산한다 —
      근사가 아니라 정확히 같은 값을 낸다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>softmax를 쪼갤 수 있는가</h2>
    <p>
      해법은 뻔해 보인다. 행렬을 타일로 쪼개 SRAM에 올리고 거기서 다 끝내면 된다.
      곱셈은 쉽게 쪼개진다. 문제는 <strong>softmax</strong>다.
    </p>
    <p>
      softmax는 분모에 <em>행 전체의 합</em>이 들어간다. 한 행을 다 보기 전에는
      정규화를 할 수 없다. 게다가 수치 안정성을 위해 최댓값을 빼는데,
      그 최댓값도 행 전체를 봐야 안다. 부분만 보고 어떻게 계산할 것인가.
    </p>
    <p>
      답은 <strong>온라인 softmax</strong>다. 지금까지 본 최댓값과 부분합을 들고 있다가,
      새 블록에서 더 큰 값이 나오면 <em>이전 결과를 보정</em>한다.
    </p>
    <div class="eq">
      <span class="cap">블록을 하나 더 볼 때마다 갱신되는 상태</span>
      <div class="line">m<sub>new</sub> = max(m<sub>old</sub>, m<sub>블록</sub>)</div>
      <div class="line">ℓ<sub>new</sub> = e<sup>(m<sub>old</sub>−m<sub>new</sub>)</sup>·ℓ<sub>old</sub> + e<sup>(m<sub>블록</sub>−m<sub>new</sub>)</sup>·ℓ<sub>블록</sub></div>
      <div class="line">O<sub>new</sub> = e<sup>(m<sub>old</sub>−m<sub>new</sub>)</sup>·O<sub>old</sub> + e<sup>(m<sub>블록</sub>−m<sub>new</sub>)</sup>·P<sub>블록</sub>V<sub>블록</sub></div>
      <div class="line">// 마지막에 O를 ℓ 로 나누면 끝. 근사가 아니라 <strong>정확히 같은 값</strong>.</div>
    </div>
    <p>
      핵심은 지수항 <code>e<sup>(m<sub>old</sub>−m<sub>new</sub>)</sup></code>다.
      더 큰 최댓값을 만났을 때 이전까지 누적한 값의 스케일을 <strong>소급 정정</strong>하는 계수다.
      이 하나 덕분에 행 전체를 보지 않고도 정확한 softmax를 조립할 수 있다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 250" role="img" aria-label="표준 어텐션과 FlashAttention의 메모리 이동 비교. 표준은 N×N 중간 행렬을 HBM에 여러 번 쓰고 읽지만, FlashAttention은 Q·K·V 블록만 SRAM으로 가져와 그 안에서 계산을 끝내고 출력만 HBM에 쓴다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="fa-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="fa-wr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--warn)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.4" fill="var(--warn)">표준 — N×N 을 HBM 에 왕복</text>

            <rect x="26" y="34" width="120" height="150" fill="none" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="86" y="50" text-anchor="middle" font-size="9.5" fill="var(--ink-faint)">HBM (느림)</text>
            <rect x="40" y="60" width="92" height="24" fill="var(--warn)" opacity="0.18" stroke="var(--warn)" stroke-width="1.1"/>
            <text x="86" y="76" text-anchor="middle" font-size="9" fill="var(--ink)">S = QKᵀ  (N×N)</text>
            <rect x="40" y="92" width="92" height="24" fill="var(--warn)" opacity="0.18" stroke="var(--warn)" stroke-width="1.1"/>
            <text x="86" y="108" text-anchor="middle" font-size="9" fill="var(--ink)">P = softmax (N×N)</text>
            <rect x="40" y="124" width="92" height="24" fill="var(--warn)" opacity="0.18" stroke="var(--warn)" stroke-width="1.1"/>
            <text x="86" y="140" text-anchor="middle" font-size="9" fill="var(--ink)">드롭아웃 (N×N)</text>
            <rect x="40" y="156" width="92" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="86" y="170" text-anchor="middle" font-size="9" fill="var(--ink-soft)">O (N×d)</text>

            <path d="M154 72 L176 72" stroke="var(--warn)" stroke-width="1.3" marker-end="url(#fa-wr)"/>
            <path d="M176 104 L154 104" stroke="var(--warn)" stroke-width="1.3" marker-end="url(#fa-wr)"/>
            <path d="M154 136 L176 136" stroke="var(--warn)" stroke-width="1.3" marker-end="url(#fa-wr)"/>
            <text x="164" y="200" text-anchor="middle" font-size="9" fill="var(--warn)">왕복 8회</text>

            <line x1="228" y1="24" x2="228" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="256" y="20" font-size="10.5" letter-spacing="1.4" fill="var(--accent)">FlashAttention — SRAM 안에서 끝낸다</text>

            <rect x="256" y="34" width="112" height="150" fill="none" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="312" y="50" text-anchor="middle" font-size="9.5" fill="var(--ink-faint)">HBM</text>
            <rect x="270" y="60" width="84" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="312" y="74" text-anchor="middle" font-size="9" fill="var(--ink-soft)">Q, K, V</text>
            <rect x="270" y="156" width="84" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="312" y="170" text-anchor="middle" font-size="9" fill="var(--accent)">O (N×d)</text>
            <text x="312" y="196" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">N×N 은 어디에도 없다</text>

            <path d="M376 70 L406 70" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#fa-ar)"/>
            <text x="391" y="62" text-anchor="middle" font-size="8" fill="var(--ink-faint)">블록</text>
            <path d="M406 166 L376 166" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#fa-ar)"/>

            <rect x="414" y="34" width="176" height="150" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="502" y="50" text-anchor="middle" font-size="9.5" fill="var(--accent)">SRAM — 19 TB/s, 192KB</text>

            <rect x="428" y="60" width="44" height="30" fill="var(--paper)" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="450" y="79" text-anchor="middle" font-size="9" fill="var(--ink)">Qᵢ</text>
            <rect x="480" y="60" width="44" height="30" fill="var(--paper)" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="502" y="79" text-anchor="middle" font-size="9" fill="var(--ink)">Kⱼ</text>
            <rect x="532" y="60" width="44" height="30" fill="var(--paper)" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="554" y="79" text-anchor="middle" font-size="9" fill="var(--ink)">Vⱼ</text>

            <rect x="428" y="102" width="148" height="26" fill="none" stroke="var(--accent-line)" stroke-width="1.1" stroke-dasharray="3 2"/>
            <text x="502" y="119" text-anchor="middle" font-size="9" fill="var(--ink-soft)">블록 곱 → 온라인 softmax</text>

            <rect x="428" y="138" width="148" height="30" fill="var(--paper)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="502" y="151" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">누적 상태  m (최댓값) · ℓ (합) · O</text>
            <text x="502" y="163" text-anchor="middle" font-size="8.5" fill="var(--accent)">새 블록마다 소급 보정</text>

            <text x="256" y="218" font-size="9.5" fill="var(--accent)">메모리 O(N²) → O(N).  결과는 근사가 아니라 정확히 동일하다.</text>
            <text x="256" y="234" font-size="9" fill="var(--ink-faint)">역전파에서는 P를 저장하지 않고 필요할 때 다시 계산한다 (recomputation).</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        바뀐 것은 수식이 아니라 <strong>계산을 어디서 하는가</strong>다.
        Q·K·V를 블록 단위로 SRAM에 올려 그 안에서 곱셈과 softmax를 모두 끝내고,
        <code>N×N</code> 중간물은 <strong>한 번도 HBM에 쓰지 않는다</strong>.
        FLOPs는 오히려 늘지만(역전파 재계산 때문에) 전체 시간은 크게 줄어든다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>연산을 더 하고 시간을 아낀다</h2>
    <p>
      역전파에는 순전파의 <code>P</code> 행렬이 필요하다. 그런데 저장하지 않았다.
      FlashAttention의 선택은 <strong>다시 계산하는 것</strong>이다.
      저장해 둔 <code>m</code>과 <code>ℓ</code>만 있으면 블록별 <code>P</code>를 SRAM 안에서 재구성할 수 있다.
    </p>
    <p>
      이것이 이 기법의 성격을 압축해 보여준다.
      <strong>FLOPs는 늘어나는데 실행 시간은 줄어든다.</strong>
      memory-bound 상황에서는 계산이 사실상 공짜이므로,
      메모리 왕복을 없앨 수 있다면 곱셈을 더 하는 쪽이 이득이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>버전</th><th>발표</th><th>핵심 변화</th><th>보고된 성능</th></tr>
        </thead>
        <tbody>
          <tr><td>FlashAttention</td><td>2022</td><td>타일링 · 온라인 softmax · 재계산</td><td>GPT-2 학습 3배 · 메모리 O(N)</td></tr>
          <tr><td>FlashAttention-2</td><td>2023</td><td>작업 분할 개선 · 비행렬곱 연산 축소</td><td class="hi">A100에서 약 2배 추가</td></tr>
          <tr><td>FlashAttention-3</td><td>2024</td><td>Hopper 특화 — 비동기 · FP8</td><td class="hi">H100 FP16 1.5~2배</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      2편의 개선은 병렬화 구조에 관한 것이다. 1편은 작업을 블록에 나누는 방식이
      GPU의 워프 구조와 잘 맞지 않아 점유율이 낮았다. 이를 재배치하고,
      텐서코어가 처리하지 못하는 비행렬곱 연산(지수 계산 등)의 비중을 줄였다.
    </p>
    <p>
      3편은 Hopper 아키텍처를 겨냥한다. 데이터 이동과 계산을 겹쳐 수행하고(비동기),
      FP8 경로를 도입했다. 세대별 하드웨어에 맞춰 다시 쓰였다는 사실 자체가
      이 기법의 본질을 말해준다 — <strong>알고리즘이 아니라 하드웨어에 맞춘 구현</strong>이다.
    </p>
    <div class="note">
      <b>어떤 근사도 하지 않는다.</b> Linformer, Performer 같은 효율적 어텐션은
      수식을 바꿔 복잡도를 낮추고 품질을 조금 내준다.
      FlashAttention은 <em>정확히 같은 함수</em>를 계산한다.
      출력이 비트 단위로 동일하지는 않지만(연산 순서가 달라 부동소수점 오차가 다르다),
      수학적으로는 같은 값이다. 그래서 기존 모델에 그대로 끼워 넣을 수 있고,
      실제로 PyTorch의 <code>scaled_dot_product_attention</code> 기본 경로가 됐다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>남긴 것 — 긴 문맥이 열렸다</h2>
    <p>
      FlashAttention이 바꾼 것은 속도만이 아니다.
      메모리가 <code>O(N²)</code>에서 <code>O(N)</code>이 되면서
      <strong>다룰 수 있는 문맥 길이의 상한이 사라졌다</strong>.
      32K, 128K 문맥이 실용화된 배경에는 이 커널이 있다.
    </p>
    <p>
      더 넓게 보면 이 연구가 남긴 교훈은 하나의 태도다.
      알고리즘을 분석할 때 FLOPs만 세는 것으로는 부족하고,
      <strong>메모리 계층 사이의 이동을 함께 세야 한다</strong>는 것.
      IO 인식(IO-aware) 설계라는 이름이 여기서 나왔다.
    </p>
    <p>
      같은 관점이 다른 곳으로도 번졌다. PagedAttention은 KV 캐시의 단편화를
      OS의 페이징으로 풀었고, 여러 커널 융합 기법이 "중간 결과를 HBM에 쓰지 않는다"는
      같은 원칙을 따른다. 병목이 계산이 아니라 데이터 이동이라는 진단이
      추론 최적화 전반의 출발점이 된 셈이다.
    </p>
  </section>
"""

READING = [
    "Dao et al., <em>FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness</em> (arXiv:2205.14135) — 원 논문. IO 복잡도 분석과 타일링·재계산.",
    "Dao, <em>FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning</em> (arXiv:2307.08691) — 작업 분할과 점유율 개선.",
    "Shah et al., <em>FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision</em> (arXiv:2407.08608) — Hopper 비동기 실행과 FP8.",
    "Milakov &amp; Gimelshein, <em>Online normalizer calculation for softmax</em> (arXiv:1805.02867) — 온라인 softmax의 출처.",
    "Rabe &amp; Staats, <em>Self-attention Does Not Need O(n²) Memory</em> (arXiv:2112.05682) — 같은 시기 독립적으로 나온 메모리 절감 결과.",
]

write(
    "flash-attention.html",
    title="FlashAttention — 어텐션을 메모리 계층에 맞춰 다시 쓰다",
    eyebrow="Inference · IO-Aware Kernel · 2022–2026",
    h1="FlashAttention",
    subtitle="어텐션을 메모리 계층에 맞춰 다시 쓰다 — 병목은 곱셈이 아니었다",
    dek=(
        "A100에서 연산은 대역폭보다 200배 빠르다. "
        "이런 장비에서 어텐션이 느린 이유는 <code>O(N²)</code> 곱셈이 아니라 "
        "<strong>N×N 중간 행렬을 HBM에 왕복시키는 것</strong>이었다. "
        "FlashAttention은 수식을 그대로 두고 계산 장소만 바꿔 "
        "메모리를 <code>O(N)</code>으로 줄인다 — 근사 없이."
    ),
    spec=[
        ("병목", "HBM 왕복 (memory-bound)"),
        ("수단", "타일링 + 온라인 softmax"),
        ("메모리", "O(N²) → O(N)"),
        ("정확도", "근사 아님 (수학적 동일)"),
        ("역전파", "저장 대신 재계산"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

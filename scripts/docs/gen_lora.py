#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ee", panel="#e7e5e2", ink="#1a1715", **{
    "ink-soft": "#57504a", "ink-faint": "#867d75", "rule": "#d4d1cc",
    "rule-strong": "#b2aca4", "accent": "#8a4b1f", "accent-fill": "#f3e3d5",
    "accent-line": "#b06a33", "muted": "#7e8590", "muted-fill": "#dee0e3", "warn": "#9c3520",
})
DARK = dict(paper="#131110", panel="#1c1917", ink="#ece8e4", **{
    "ink-soft": "#aca49c", "ink-faint": "#7a736c", "rule": "#282320", "rule-strong": "#3e3833",
    "accent": "#e09456", "accent-fill": "#2f2013", "accent-line": "#a86f38",
    "muted": "#8b939e", "muted-fill": "#1c2024", "warn": "#e07a5f",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>전부 다시 학습시키는 것의 진짜 비용</h2>
    <p>
      7B 모델을 내 데이터에 맞추고 싶다고 하자. 정석은 전체 파인튜닝이다.
      모든 가중치를 열어 놓고 역전파를 돌린다. 문제는 메모리다.
    </p>
    <p>
      흔한 오해는 "파라미터 7B × 2바이트 = 14GB면 되겠네"다.
      실제로는 그 <strong>몇 배</strong>가 든다. 옵티마이저가 파라미터마다 상태를 들고 있기 때문이다.
      Adam은 1차·2차 모멘텀 두 개를 fp32로 유지한다.
    </p>
    <div class="eq">
      <span class="cap">7B 전체 파인튜닝의 메모리 내역 (mixed precision + Adam)</span>
      <div class="line">가중치 (bf16)            7B × 2B  =  14 GB</div>
      <div class="line">그래디언트 (bf16)         7B × 2B  =  14 GB</div>
      <div class="line">Adam m, v (fp32)         7B × 8B  =  56 GB</div>
      <div class="line">fp32 마스터 사본          7B × 4B  =  28 GB</div>
      <div class="line">──────────────────────────────────────</div>
      <div class="line">합계                              ≈ 112 GB  (활성값 제외)</div>
    </div>
    <p>
      80GB짜리 A100 한 장에 들어가지 않는다. 가중치 자체는 14GB뿐인데
      <em>학습에 필요한 부속물</em>이 여덟 배를 차지한다.
      LoRA의 출발점은 여기다 — 가중치를 얼려버리면 저 아래 세 줄이 통째로 사라진다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>변화량은 낮은 랭크로 충분하다는 가설</h2>
    <p>
      파인튜닝이 하는 일은 가중치 <code>W</code>를 <code>W + ΔW</code>로 옮기는 것이다.
      LoRA의 주장은 이 <code>ΔW</code>가 <strong>본질적으로 낮은 랭크</strong>라는 것이다.
      full-rank 행렬 하나를 통째로 학습할 필요 없이, 얇은 두 행렬의 곱으로 표현할 수 있다.
    </p>
    <div class="eq">
      <span class="cap">저랭크 분해 — 학습되는 것은 A와 B뿐이다</span>
      <div class="line">h = W<sub>0</sub>x + ΔWx = W<sub>0</sub>x + <strong>BA</strong>x</div>
      <div class="line">W<sub>0</sub> ∈ ℝ<sup>d×k</sup> (얼림)&nbsp;&nbsp; B ∈ ℝ<sup>d×r</sup>&nbsp;&nbsp; A ∈ ℝ<sup>r×k</sup>&nbsp;&nbsp; r ≪ min(d,k)</div>
      <div class="line">파라미터 수: d·k &nbsp;→&nbsp; r·(d+k)</div>
      <div class="line">h = W<sub>0</sub>x + (α/r) · BAx&nbsp;&nbsp;&nbsp;// α 는 스케일 상수</div>
    </div>
    <p>
      숫자를 넣어 보면 감이 온다. <code>d = k = 4096</code>인 어텐션 투영 행렬은 16.7M 파라미터다.
      <code>r = 8</code>이면 <code>8 × (4096+4096) = 65,536</code>개 — <strong>0.39%</strong>다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="전체 파인튜닝과 LoRA의 비교 도식. 전체 파인튜닝은 d×k 크기의 가중치 행렬 전체를 학습하고, LoRA는 원본 행렬을 얼린 채 옆에 r×k와 d×r 크기의 얇은 두 행렬만 학습해 그 출력을 더한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="lora-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="lora-gr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="28" y="20" font-size="10.5" letter-spacing="1.4" fill="var(--muted)">전체 파인튜닝 — 전부 학습</text>
            <rect x="28" y="34" width="104" height="104" fill="var(--warn)" opacity="0.16" stroke="var(--warn)" stroke-width="1.5"/>
            <text x="80" y="80" text-anchor="middle" font-size="11" fill="var(--ink)">W</text>
            <text x="80" y="96" text-anchor="middle" font-size="9" fill="var(--warn)">4096×4096</text>
            <text x="80" y="156" text-anchor="middle" font-size="9.5" fill="var(--warn)">16.7M 학습</text>
            <text x="80" y="172" text-anchor="middle" font-size="9" fill="var(--ink-faint)">옵티마이저 상태도</text>
            <text x="80" y="186" text-anchor="middle" font-size="9" fill="var(--ink-faint)">그만큼 따라붙는다</text>

            <line x1="188" y1="24" x2="188" y2="206" stroke="var(--rule)" stroke-width="1"/>

            <text x="216" y="20" font-size="10.5" letter-spacing="1.4" fill="var(--accent)">LoRA — 옆에 샛길</text>

            <rect x="216" y="34" width="104" height="104" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.5" stroke-dasharray="4 3"/>
            <text x="268" y="80" text-anchor="middle" font-size="11" fill="var(--ink-soft)">W₀</text>
            <text x="268" y="96" text-anchor="middle" font-size="9" fill="var(--ink-faint)">얼림 ❄</text>

            <path d="M196 86 L212 86" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#lora-gr)"/>

            <rect x="356" y="34" width="104" height="22" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="408" y="49" text-anchor="middle" font-size="9.5" fill="var(--accent)">A  (r=8 × 4096)</text>
            <rect x="386" y="72" width="22" height="66" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="397" y="110" text-anchor="middle" font-size="9.5" fill="var(--accent)" transform="rotate(-90 397 110)">B (4096×8)</text>

            <path d="M340 86 L352 60" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#lora-ar)"/>
            <path d="M408 60 L408 68" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#lora-ar)"/>

            <circle cx="500" cy="86" r="14" fill="none" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="500" y="91" text-anchor="middle" font-size="13" fill="var(--accent)">+</text>
            <path d="M324 90 L484 88" stroke="var(--rule-strong)" stroke-width="1.3" marker-end="url(#lora-gr)"/>
            <path d="M412 138 L492 100" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#lora-ar)"/>
            <path d="M516 86 L556 86" stroke="var(--rule-strong)" stroke-width="1.3" marker-end="url(#lora-gr)"/>
            <text x="580" y="90" font-size="10.5" fill="var(--ink-soft)">h</text>

            <text x="216" y="156" font-size="9.5" fill="var(--accent)">65,536 학습 — 0.39%</text>
            <text x="216" y="172" font-size="9" fill="var(--ink-faint)">B는 0으로 초기화된다. 그래서 학습 시작 시점의</text>
            <text x="216" y="186" font-size="9" fill="var(--ink-faint)">출력은 원본과 정확히 같다 (BA = 0).</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        원본 경로는 그대로 두고 <strong>병렬 경로를 하나 추가</strong>한다.
        <code>A</code>는 정규분포로, <code>B</code>는 <strong>0으로</strong> 초기화하는 것이 핵심이다 —
        <code>BA = 0</code>이므로 학습 시작 순간 모델은 원본과 완전히 동일하게 동작한다.
        망가진 상태에서 출발하지 않는다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">03</span>왜 랭크 8로도 되는가</h2>
    <p>
      직관적으로 이상하다. 4096×4096 행렬의 변화를 랭크 8이 담아낼 수 있다니.
      근거는 두 갈래다.
    </p>
    <p>
      첫째, <strong>사전학습이 이미 대부분의 일을 해 놓았다.</strong>
      파인튜닝은 없던 능력을 만드는 게 아니라 이미 있는 표현을 특정 방향으로 기울이는 작업이다.
      "존댓말로 답한다", "JSON만 출력한다" 같은 조정은 모델이 가진 표현 공간 안에서의
      좁은 이동이지 공간 자체의 재구성이 아니다.
    </p>
    <p>
      둘째, 논문의 실측이다. 전체 파인튜닝으로 얻은 <code>ΔW</code>를 특이값 분해해 보면
      상위 몇 개 특이값이 대부분의 에너지를 차지한다. <strong>본질적 랭크(intrinsic rank)가 낮다</strong>는 관찰이다.
    </p>
    <div class="note">
      <b>랭크를 올린다고 좋아지지 않는다.</b> 논문의 실험에서 <code>r</code>을 1, 2, 4, 8, 64로 바꿔도
      성능 차이가 크지 않았다. <code>r=1</code>로도 상당 부분 되는 경우가 있다.
      이는 <em>"작아서 아쉽지만 감수한다"가 아니라 "그 이상은 필요 없다"</em>에 가깝다.
      실무에서 <code>r</code>을 키우는 것보다 <strong>어느 층에 붙이느냐</strong>가 훨씬 큰 차이를 만든다.
    </div>
    <p>
      원 논문은 어텐션의 <code>W<sub>q</sub></code>, <code>W<sub>v</sub></code>에만 붙였다.
      이후 실무에서는 FFN을 포함해 <strong>모든 선형 층</strong>에 붙이는 편이 낫다는 결과가 쌓였다.
      QLoRA 논문도 같은 결론이다 — 랭크를 키우기보다 붙이는 위치를 늘리는 쪽이 효율적이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>추론에서는 공짜다</h2>
    <p>
      Adapter 계열의 고질병은 <strong>추론 지연</strong>이었다.
      층 사이에 새 모듈을 끼워 넣으므로 순전파 경로가 길어진다.
      LoRA에는 이 문제가 없다. 학습이 끝나면 <strong>합쳐버릴 수 있기</strong> 때문이다.
    </p>
    <div class="eq">
      <span class="cap">병합 — 구조가 원본과 완전히 같아진다</span>
      <div class="line">W' = W<sub>0</sub> + (α/r) · BA</div>
      <div class="line">// 이후 h = W'x 로 계산. 추가 연산 0, 추가 지연 0.</div>
    </div>
    <p>
      덧셈 한 번으로 원본과 같은 모양의 행렬이 나온다.
      배포되는 모델은 LoRA를 썼는지 알 수 없는 형태가 된다.
    </p>
    <p>
      이 성질이 만드는 더 재미있는 결과는 <strong>어댑터를 갈아끼울 수 있다</strong>는 점이다.
      7B 베이스 하나를 GPU에 올려 두고, 고객사별로 학습한 수십 MB짜리 LoRA를
      요청에 따라 바꿔 붙인다. 베이스 14GB는 한 번만 올리면 된다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방식</th><th>학습 파라미터</th><th>추론 지연</th><th>어댑터 교체</th></tr>
        </thead>
        <tbody>
          <tr><td>전체 파인튜닝</td><td>100%</td><td class="hi">증가 없음</td><td>불가 (모델 전체 사본)</td></tr>
          <tr><td>Adapter (직렬)</td><td>~1%</td><td>증가</td><td>가능</td></tr>
          <tr><td>Prefix Tuning</td><td>~0.1%</td><td>증가 (문맥 소모)</td><td>가능</td></tr>
          <tr><td>LoRA</td><td class="hi">0.1~1%</td><td class="hi">증가 없음 (병합 시)</td><td class="hi">가능</td></tr>
        </tbody>
      </table>
    </div>
    <div class="note">
      <b>병합하면 교체할 수 없고, 교체하려면 병합할 수 없다.</b>
      둘은 동시에 얻을 수 없다. 여러 어댑터를 동시 서빙하려면 병합하지 않은 채
      배치 안에서 각 요청에 맞는 <code>BA</code>를 따로 적용해야 하고,
      이때는 약간의 지연이 다시 생긴다. S-LoRA 같은 연구가 이 지점을 다룬다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>QLoRA — 베이스까지 4비트로</h2>
    <p>
      LoRA는 옵티마이저 상태를 없앴지만 <strong>베이스 가중치 14GB는 여전히 GPU에 있어야 한다</strong>.
      얼려 두더라도 순전파에는 써야 하기 때문이다. QLoRA는 이 마지막 덩어리를 건드린다 —
      베이스를 <strong>4비트로 양자화</strong>해 얼리고, 그 위에 LoRA를 붙인다.
    </p>
    <p>
      역전파는 4비트 가중치를 통과해 흐르지만, 그래디언트가 갱신하는 것은
      bf16으로 유지되는 <code>A</code>, <code>B</code>뿐이다. 기여는 세 가지다.
    </p>
    <ul>
      <li><strong>NF4</strong> — 정규분포를 따르는 가중치에 맞춘 4비트 자료형. 균등 양자화보다 정보 손실이 적다.</li>
      <li><strong>이중 양자화</strong> — 양자화 상수 자체를 다시 양자화한다. 파라미터당 약 0.37비트를 더 줄인다.</li>
      <li><strong>페이지드 옵티마이저</strong> — 메모리 급증 시 옵티마이저 상태를 CPU로 잠시 내린다.</li>
    </ul>
    <p>
      결과적으로 65B 모델을 <strong>48GB 한 장</strong>에서 파인튜닝할 수 있게 됐다.
      논문은 이렇게 학습한 Guanaco가 16비트 전체 파인튜닝 수준의 품질에 도달함을 보였다.
    </p>
    <div class="note">
      <b>다만 학습이 느려진다.</b> 순전파마다 4비트를 bf16으로 역양자화하는 비용이 붙는다.
      QLoRA는 <em>속도가 아니라 진입 가능성</em>을 산 기법이다 —
      원래 못 돌리던 크기를 돌릴 수 있게 만드는 쪽이지, 돌아가던 걸 빠르게 하는 쪽이 아니다.
    </div>
    <p>
      정리하면 LoRA는 하나의 관찰을 공학으로 옮긴 것이다 —
      <em>파인튜닝이 만드는 변화는 생각보다 좁은 부분공간에 있다.</em>
      그 관찰이 맞았기 때문에, 0.4%만 학습해도 되고, 병합하면 공짜가 되고,
      수십 MB짜리 파일로 모델의 성격을 바꿔 끼울 수 있게 됐다.
    </p>
  </section>
"""

READING = [
    "Hu et al., <em>LoRA: Low-Rank Adaptation of Large Language Models</em> (arXiv:2106.09685) — 원 논문. 본질적 랭크 관찰과 랭크별 실험이 여기 있다.",
    "Dettmers et al., <em>QLoRA: Efficient Finetuning of Quantized LLMs</em> (arXiv:2305.14314) — NF4·이중 양자화·페이지드 옵티마이저, 그리고 붙이는 위치에 대한 결론.",
    "Aghajanyan et al., <em>Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning</em> (arXiv:2012.13255) — 저랭크 가설의 이론적 배경.",
    "Sheng et al., <em>S-LoRA: Serving Thousands of Concurrent LoRA Adapters</em> (arXiv:2311.03285) — 병합하지 않고 다중 어댑터를 서빙하는 문제.",
    "Houlsby et al., <em>Parameter-Efficient Transfer Learning for NLP</em> (arXiv:1902.00751) — 직렬 Adapter. LoRA가 피해간 추론 지연 문제의 출처.",
]

write(
    "lora.html",
    title="LoRA — 얼린 가중치 옆에 샛길을 내다",
    eyebrow="Adaptation · Parameter-Efficient Fine-Tuning · 2021–2026",
    h1="LoRA",
    subtitle="얼린 가중치 옆에 샛길을 내다 — 0.4%만 학습하는 법",
    dek=(
        "7B 모델의 전체 파인튜닝에는 112GB가 든다. 가중치는 14GB뿐인데 "
        "옵티마이저 상태가 여덟 배를 차지한다. "
        "LoRA는 원본을 얼리고 <strong>변화량만 저랭크로</strong> 학습해 이 덩어리를 통째로 없앤다. "
        "그리고 학습이 끝나면 원본에 더해버릴 수 있어 <strong>추론 비용은 0</strong>이다."
    ),
    spec=[
        ("핵심", "ΔW = BA"),
        ("학습 비율", "0.1 ~ 1%"),
        ("초기화", "A 정규분포 · B 0"),
        ("추론 지연", "없음 (병합 시)"),
        ("확장", "QLoRA — 65B / 48GB"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

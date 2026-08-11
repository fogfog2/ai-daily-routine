#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0f1", panel="#e7e5e8", ink="#1a151a", **{
    "ink-soft": "#564e57", "ink-faint": "#857d87", "rule": "#d5d0d7",
    "rule-strong": "#b1aab3", "accent": "#6d2f7a", "accent-fill": "#eedcf2",
    "accent-line": "#93559f", "muted": "#84868d", "muted-fill": "#dfe0e3", "warn": "#a0522a",
})
DARK = dict(paper="#121016", panel="#1a171d", ink="#eae5eb", **{
    "ink-soft": "#aca2ad", "ink-faint": "#7d737f", "rule": "#262029", "rule-strong": "#3d3541",
    "accent": "#cf8ee0", "accent-fill": "#2c1533", "accent-line": "#96609f",
    "muted": "#87898f", "muted-fill": "#1b1c20", "warn": "#e0865c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>말로는 위치를 지정할 수 없다</h2>
    <p>
      <a href="diffusion-models.html">확산 모델</a>은 텍스트로 조건을 건다.
      "고양이"라고 쓰면 고양이가 나온다. 그런데 <em>어디에, 어떤 자세로</em>는 말로 표현하기 어렵다.
    </p>
    <p>
      "왼쪽 위에 앉아 있고 오른쪽을 보는 고양이"라고 써도 잘 안 된다.
      <strong>텍스트는 공간 정보를 담기에 부적합한 매체</strong>다.
      게다가 <a href="diffusion-models.html">CFG</a> 로 프롬프트 충실도를 올려도
      *무엇*이 나오는지가 강해질 뿐 *어디에*는 여전히 통제되지 않는다.
    </p>
    <p>
      필요한 것은 <strong>공간적 조건</strong>이다 —
      스케치, 자세 골격, <a href="depth-estimation.html">깊이 맵</a>, 경계선, 분할 마스크 같은 것들.
      이미지로 조건을 주면 위치·구도·형태를 정확히 지정할 수 있다.
    </p>
    <div class="note">
      <b>왜 그냥 파인튜닝하지 않는가.</b> 조건 종류마다 모델을 새로 학습하면
      <em>대규모 사전학습으로 얻은 생성 능력</em>을 잃기 쉽다.
      데이터가 수만 장 규모인데 원본은 수십억 장으로 학습된 것이라,
      전체를 미세조정하면 <strong>과적합하거나 망가진다</strong>.
      <a href="lora.html">LoRA</a> 가 풀었던 것과 같은 종류의 문제다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>얼려 두고 사본을 붙인다</h2>
    <p>
      ControlNet 의 구조는 <a href="lora.html">LoRA</a> 와 같은 철학을 다른 방식으로 구현한 것이다.
      <strong>원본은 얼리고, 옆에 학습 가능한 경로를 붙인다.</strong>
    </p>
    <div class="eq">
      <span class="cap">구조 — 인코더를 복제해 붙인다</span>
      <div class="line">원본 U-Net&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>전부 얼림 ❄</strong></div>
      <div class="line">&nbsp;&nbsp;+</div>
      <div class="line">인코더 사본&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 학습됨 — 조건 이미지를 받는다</div>
      <div class="line">&nbsp;&nbsp;+</div>
      <div class="line"><strong>zero convolution</strong>&nbsp; 사본의 출력을 원본에 더한다</div>
    </div>
    <p>
      인코더를 <em>복제</em>하는 이유가 있다.
      새 구조를 처음부터 학습하는 대신 <strong>이미 좋은 특징 추출기</strong>를 가져다 쓰는 것이다.
      사전학습된 가중치로 시작하니 적은 데이터로도 수렴한다.
    </p>
    <p>
      결정적인 장치는 <strong>zero convolution</strong> 이다.
      1×1 합성곱인데 <em>가중치와 편향을 전부 0으로 초기화</em>한다.
    </p>
    <div class="eq">
      <span class="cap">0 으로 시작하는 이유</span>
      <div class="line">학습 시작 시점:&nbsp; zero conv 출력 = 0</div>
      <div class="line">→ 원본에 더해지는 값이 0</div>
      <div class="line">→ <strong>원본과 완전히 동일하게 동작</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 무작위 노이즈가 섞여 원본을 망가뜨리는 일이 없다</div>
      <div class="line">// 학습이 진행되며 조건의 영향이 <em>점진적으로</em> 커진다</div>
    </div>
    <p>
      <a href="lora.html">LoRA</a> 가 <code>B</code>를 0으로 초기화해
      <em>시작 순간 원본과 같게</em> 만든 것과 정확히 같은 발상이다.
      <strong>망가진 상태에서 출발하지 않는다</strong>는 것이 두 기법의 공통 원칙이다.
    </p>
    <div class="note">
      <b>0 인데 학습이 되나.</b> 흔한 의문인데, 된다.
      zero conv 의 그래디언트는 <em>입력에 비례</em>하는데 입력이 0이 아니기 때문이다.
      가중치가 0이어도 <code>∂L/∂W = x · ∂L/∂y</code> 는 0이 아니므로
      첫 스텝에서 가중치가 0에서 벗어나고, 그 뒤로는 정상적으로 학습된다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>조건의 종류가 곧 통제의 종류</h2>
    <p>
      같은 구조에 <strong>무엇을 조건으로 주느냐</strong>가 통제하는 대상을 정한다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 232" role="img" aria-label="ControlNet의 구조와 조건 종류. 원본 확산 모델은 얼린 채 인코더 사본을 붙이고, zero convolution으로 출력을 더해 학습 시작 시점에는 원본과 동일하게 동작한다. 조건 이미지의 종류에 따라 통제하는 대상이 달라진다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="cn2-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="cn2-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">원본은 얼리고 옆에 붙인다</text>

            <rect x="24" y="34" width="90" height="96" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3" stroke-dasharray="4 3"/>
            <text x="69" y="54" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">원본 U-Net</text>
            <text x="69" y="68" text-anchor="middle" font-size="8" fill="var(--ink-faint)">얼림 ❄</text>
            <g fill="var(--muted)" opacity="0.35">
              <rect x="34" y="78" width="70" height="12"/>
              <rect x="34" y="94" width="70" height="12"/>
              <rect x="34" y="110" width="70" height="12"/>
            </g>

            <rect x="164" y="34" width="90" height="96" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="209" y="54" text-anchor="middle" font-size="8.5" fill="var(--accent)">인코더 사본</text>
            <text x="209" y="68" text-anchor="middle" font-size="8" fill="var(--accent)">학습됨</text>
            <g fill="var(--accent)" opacity="0.4">
              <rect x="174" y="78" width="70" height="12"/>
              <rect x="174" y="94" width="70" height="12"/>
              <rect x="174" y="110" width="70" height="12"/>
            </g>

            <rect x="164" y="146" width="90" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="209" y="162" text-anchor="middle" font-size="8" fill="var(--ink-soft)">조건 이미지</text>
            <path d="M209 144 L209 134" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#cn2-a)"/>

            <g>
              <circle cx="139" cy="84" r="9" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1.2"/>
              <text x="139" y="88" text-anchor="middle" font-size="9" fill="var(--accent)">0</text>
              <circle cx="139" cy="116" r="9" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1.2"/>
              <text x="139" y="120" text-anchor="middle" font-size="9" fill="var(--accent)">0</text>
            </g>
            <path d="M160 84 L150 84" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#cn2-a)"/>
            <path d="M160 116 L150 116" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#cn2-a)"/>
            <path d="M128 84 L110 84" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#cn2-a)"/>
            <path d="M128 116 L110 116" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#cn2-a)"/>

            <text x="272" y="70" font-size="8" fill="var(--accent)">zero convolution</text>
            <text x="272" y="84" font-size="8" fill="var(--ink-faint)">가중치·편향을 0 으로 초기화</text>
            <text x="272" y="100" font-size="8" fill="var(--accent)">→ 시작 시점에 원본과 동일</text>
            <text x="272" y="114" font-size="8" fill="var(--ink-faint)">→ 학습되며 조건의 영향이 커진다</text>
            <text x="272" y="134" font-size="8" fill="var(--warn)">망가진 상태에서 출발하지 않는다</text>

            <line x1="24" y1="184" x2="674" y2="184" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="204" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">조건이 통제 대상을 정한다</text>
            <text x="24" y="222" font-size="8" fill="var(--ink-soft)">경계선 → 형태 · 자세 골격 → 인물 포즈 · <tspan fill="var(--accent)">깊이 맵 → 공간 배치</tspan> · 분할 마스크 → 영역 · 스케치 → 구도</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        구조는 하나인데 <strong>조건만 바꾸면 다른 통제</strong>가 된다.
        조건 종류마다 별도의 ControlNet 을 학습하지만,
        <em>원본 확산 모델은 공유</em>하므로 여러 개를 갈아 끼울 수 있다 —
        <a href="lora.html">LoRA 어댑터</a>를 교체하는 것과 같은 구조다.
      </figcaption>
    </figure>

    <p>
      <a href="depth-estimation.html">깊이 맵</a>을 조건으로 쓰는 경우가 특히 유용하다.
      <em>공간 배치는 유지하면서 내용만 바꿀 수 있기</em> 때문이다 —
      같은 구도의 방을 다른 스타일로 바꾸거나, 물체 배치를 지키며 재질을 바꾸는 식이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>얼마나 따를 것인가</h2>
    <p>
      조건을 준다고 무조건 따르는 것이 좋지는 않다.
      <strong>조건 충실도와 생성 자유도가 맞바꿈</strong>이다.
    </p>
    <p>
      조건을 강하게 걸면 스케치를 정확히 따르지만 <em>어색하고 경직된</em> 결과가 나온다.
      약하게 걸면 자연스럽지만 <em>의도한 구도를 벗어난다</em>.
      그래서 조절 손잡이가 여럿 있다.
    </p>
    <div class="eq">
      <span class="cap">조절할 수 있는 것들</span>
      <div class="line"><strong>조건 강도</strong>&nbsp;&nbsp;&nbsp; zero conv 출력에 곱하는 계수</div>
      <div class="line"><strong>적용 구간</strong>&nbsp;&nbsp;&nbsp; 확산 단계 중 <em>일부에만</em> 조건을 건다</div>
      <div class="line"><strong>층별 가중</strong>&nbsp;&nbsp;&nbsp; 어느 해상도 층에 강하게 걸지</div>
    </div>
    <p>
      <strong>적용 구간</strong>이 흥미롭다. 확산은 <em>초반에 큰 구조, 후반에 세부</em>를 정한다.
      그래서 조건을 초반 단계에만 걸면 <em>구도는 따르되 세부는 자유롭게</em> 두는 효과가 난다.
      반대로 후반에만 걸면 큰 배치는 모델이 정하고 마무리만 맞춘다.
    </p>
    <div class="note">
      <b>여러 조건을 동시에 걸 수도 있다.</b> 자세 골격과 깊이 맵을 함께 주면
      "이 자세로, 이 공간 배치에" 라는 요구가 된다.
      다만 조건들이 <em>서로 모순되면</em> 결과가 무너진다 —
      깊이 맵은 앉아 있는데 골격은 서 있으면 모델이 절충하다 이상해진다.
      조건을 늘릴수록 <strong>일관성을 사람이 보장해야</strong> 한다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>같은 문제, 여러 답</h2>
    <p>
      공간 통제를 푸는 방법이 ControlNet 만 있는 것은 아니다.
      비용과 유연성이 다른 선택지들이 있다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방식</th><th>추가 비용</th><th>성격</th></tr>
        </thead>
        <tbody>
          <tr><td><strong>ControlNet</strong></td><td class="hi">인코더 사본만큼 (큼)</td><td>정밀한 공간 통제</td></tr>
          <tr><td>T2I-Adapter</td><td class="hi">훨씬 가벼움</td><td>통제력은 약간 낮다</td></tr>
          <tr><td>IP-Adapter</td><td>중간</td><td class="hi">이미지를 '스타일'로 참조</td></tr>
          <tr><td>Inpainting</td><td>없음 (마스크만)</td><td>영역을 지정해 다시 그림</td></tr>
          <tr><td>img2img</td><td>없음</td><td class="hi">노이즈를 덜 넣어 원본을 남김</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 <strong>img2img</strong> 가 가장 값싸다. 순수 노이즈에서 시작하는 대신
      <em>원본 이미지에 노이즈를 일부만 넣고</em> 거기서 역과정을 시작한다.
      노이즈를 적게 넣으면 원본이 많이 남고, 많이 넣으면 자유로워진다.
      추가 학습이 전혀 없다는 것이 장점이다.
    </p>
    <p>
      <strong>T2I-Adapter</strong> 는 ControlNet 의 경량판이다.
      인코더 전체를 복제하는 대신 작은 특징 추출기만 붙인다.
      <a href="peft-adapters.html">PEFT</a> 에서 본 것과 같은 저울이다 —
      <em>어디에 얼마나 큰 것을 붙일지</em>가 통제력과 비용을 정한다.
    </p>
    <div class="note">
      <b>온디바이스에서는 대부분 쓰기 어렵다.</b> ControlNet 은 <em>추론 비용을 늘린다</em> —
      인코더 사본을 매 단계 통과해야 한다.
      확산 모델 자체가 이미 <a href="super-resolution.html">여러 단계</a>를 도는데
      거기에 더해지는 것이라, 모바일에서는 부담이 크다.
      <a href="knowledge-distillation.html">증류</a>로 단계를 줄인 모델과 조합하는 연구가 이 지점을 다룬다.
    </div>
    <p>
      정리하면 ControlNet 은 <em>"말로 못 하는 것을 그림으로 말하게"</em> 하는 장치다.
      그리고 그 구현 원칙은 <a href="lora.html">LoRA</a> 와 같다 —
      <strong>이미 잘하는 것을 건드리지 말고, 옆에 붙여서, 0에서 시작한다.</strong>
      큰 모델을 다루는 방법론이 생성과 언어에서 같은 모양으로 수렴한 사례다.
    </p>
  </section>
"""

READING = [
    "Zhang et al., <em>Adding Conditional Control to Text-to-Image Diffusion Models</em> (arXiv:2302.05543) — ControlNet 원 논문. zero convolution.",
    "Mou et al., <em>T2I-Adapter: Learning Adapters to Dig out More Controllable Ability for Text-to-Image Diffusion Models</em> (arXiv:2302.08453) — 경량 대안.",
    "Ye et al., <em>IP-Adapter: Text Compatible Image Prompt Adapter for Text-to-Image Diffusion Models</em> (arXiv:2308.06721) — 이미지 프롬프트.",
    "Meng et al., <em>SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations</em> (arXiv:2108.01073) — img2img 의 이론적 근거.",
    "Ho &amp; Salimans, <em>Classifier-Free Diffusion Guidance</em> (arXiv:2207.12598) — 텍스트 조건 강도 조절의 출발점.",
]

write(
    "controlnet.html",
    title="ControlNet — 말로 못 하는 것을 그림으로",
    eyebrow="Generative · Conditional Control · 2023–2026",
    h1="ControlNet",
    subtitle="말로 못 하는 것을 그림으로 — 공간을 지정하는 법",
    dek=(
        "\"왼쪽 위에 앉아 오른쪽을 보는 고양이\"라고 써도 잘 안 된다. "
        "<strong>텍스트는 공간 정보를 담기에 부적합한 매체</strong>이기 때문이다. "
        "필요한 것은 스케치·자세·깊이 맵 같은 <em>이미지 조건</em>이고, "
        "그것을 원본을 망가뜨리지 않고 붙이는 방법이 ControlNet 이다."
    ),
    spec=[
        ("푸는 문제", "공간·구도 통제"),
        ("구조", "원본 얼림 + 인코더 사본"),
        ("핵심 장치", "zero convolution"),
        ("설계 원칙", "0에서 시작 (LoRA 와 동일)"),
        ("대가", "추론 비용 증가"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

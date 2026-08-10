#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0eff3", panel="#e6e4ea", ink="#17141c", **{
    "ink-soft": "#524d5e", "ink-faint": "#827c8f", "rule": "#d2cfd9",
    "rule-strong": "#aea9bb", "accent": "#5b3a9e", "accent-fill": "#e6dcf5",
    "accent-line": "#7d5cc0", "muted": "#83868f", "muted-fill": "#dfe0e5", "warn": "#a03a5c",
})
DARK = dict(paper="#111017", panel="#1a181f", ink="#e9e5ef", **{
    "ink-soft": "#a9a3b5", "ink-faint": "#77718280", "rule": "#262230", "rule-strong": "#3c3648",
    "accent": "#b492f0", "accent-fill": "#241b38", "accent-line": "#8467c4",
    "muted": "#8a8d96", "muted-fill": "#1d1f25", "warn": "#e07a9c",
})
DARK["ink-faint"] = "#8b8496"

BODY = r"""
  <section>
    <h2><span class="n">01</span>어려운 문제를 쉬운 문제 수백 개로</h2>
    <p>
      "노이즈에서 고양이 사진을 만들어라"는 너무 어려운 요구다.
      GAN은 이것을 한 번에 하려다 학습 불안정에 시달렸다.
    </p>
    <p>
      확산 모델의 발상은 문제를 <strong>쪼개는 것</strong>이다.
      깨끗한 이미지에 노이즈를 조금씩 더해 완전한 잡음으로 만드는 과정을 생각해 보자.
      이 <em>순방향 과정</em>은 학습할 것이 없다. 정해진 규칙대로 노이즈를 더하면 된다.
    </p>
    <p>
      그렇다면 그 반대는? 노이즈가 조금 섞인 이미지에서 <strong>그 조금을 걷어내는 일</strong>은
      훨씬 쉬운 문제다. 이것을 수백 번 반복하면 잡음에서 이미지가 나온다.
      확산 모델이 배우는 것은 이 <em>한 걸음</em>뿐이다.
    </p>
    <div class="note">
      <b>이 분해가 안정성의 근원이다.</b> GAN은 생성자와 판별자가 서로를 쫓는 최소최대 게임이라
      균형이 깨지기 쉽다. 확산 모델의 학습은 그냥 <em>회귀</em>다 —
      "이 이미지에 섞인 노이즈가 무엇이었는지 맞혀라". 목표가 고정돼 있으니 무너지지 않는다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>순방향 — 한 번에 아무 시점으로나 건너뛴다</h2>
    <p>
      각 단계에서 이미지를 조금 줄이고 그만큼 노이즈를 더한다.
      <code>β<sub>t</sub></code>는 미리 정해 둔 작은 수들의 수열이다.
    </p>
    <div class="eq">
      <span class="cap">순방향 확산 — 학습되는 파라미터가 없다</span>
      <div class="line">q(x<sub>t</sub> | x<sub>t−1</sub>) = 𝒩( √(1−β<sub>t</sub>)·x<sub>t−1</sub>,&nbsp; β<sub>t</sub>I )</div>
      <div class="line">α<sub>t</sub> = 1 − β<sub>t</sub>,&nbsp;&nbsp; ᾱ<sub>t</sub> = Π<sub>s≤t</sub> α<sub>s</sub></div>
      <div class="line"><strong>x<sub>t</sub> = √ᾱ<sub>t</sub>·x<sub>0</sub> + √(1−ᾱ<sub>t</sub>)·ε</strong>&nbsp;&nbsp;&nbsp;(ε ~ 𝒩(0, I))</div>
    </div>
    <p>
      마지막 줄이 실용적으로 중요하다. 가우시안을 여러 번 더한 것은 다시 가우시안이므로,
      <strong><code>t</code>단계까지 한 번에 건너뛸 수 있다</strong>.
      학습할 때 1000단계를 순서대로 밟을 필요 없이 <code>t</code>를 무작위로 뽑아
      곧바로 <code>x<sub>t</sub></code>를 만들면 된다.
    </p>
    <p>
      <code>t</code>가 커질수록 <code>ᾱ<sub>t</sub></code>는 0에 가까워지고,
      <code>x<sub>T</sub></code>는 원본의 흔적이 사라진 순수한 표준정규분포가 된다.
      샘플링의 출발점이 <em>아무 노이즈나 뽑아도 되는</em> 이유다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>학습 목표는 놀랄 만큼 단순하다</h2>
    <p>
      역과정을 배우려면 원래 변분 하한(ELBO)을 최적화해야 하고, 그 식은 복잡하다.
      DDPM 논문의 기여 중 하나는 이것을 정리했더니 <strong>세 줄짜리 손실</strong>이 남았다는 것이다.
    </p>
    <div class="eq">
      <span class="cap">DDPM 학습 — 섞인 노이즈를 맞히는 회귀</span>
      <div class="line">x<sub>0</sub> ~ 데이터,&nbsp;&nbsp; t ~ Uniform(1..T),&nbsp;&nbsp; ε ~ 𝒩(0, I)</div>
      <div class="line">x<sub>t</sub> = √ᾱ<sub>t</sub>·x<sub>0</sub> + √(1−ᾱ<sub>t</sub>)·ε</div>
      <div class="line"><strong>L = ‖ ε − ε<sub>θ</sub>(x<sub>t</sub>, t) ‖²</strong></div>
    </div>
    <p>
      신경망 <code>ε<sub>θ</sub></code>가 하는 일은 <em>"이 이미지에 섞인 노이즈를 그려내라"</em>다.
      이미지를 예측하는 것도, 확률분포를 예측하는 것도 아니다. 그냥 노이즈다.
      단계 번호 <code>t</code>를 함께 넣어주어 "지금 얼마나 흐린 상태인지"를 알려준다.
    </p>
    <p>
      노이즈를 맞히는 것과 이미지를 복원하는 것은 사실 같은 일이다.
      위 식을 <code>x<sub>0</sub></code>에 대해 풀면 바로 나온다.
      다만 <strong>노이즈를 목표로 두는 편이 학습이 잘 된다</strong>는 것이 실험적 발견이었다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 220" role="img" aria-label="확산 모델의 순방향과 역방향 과정 도식. 위쪽 순방향은 깨끗한 이미지에 노이즈를 점점 더해 완전한 잡음으로 만들며 학습이 필요 없고, 아래쪽 역방향은 신경망이 매 단계 섞인 노이즈를 예측해 걷어내며 잡음에서 이미지를 만든다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="df-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
              <marker id="df-r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--muted)">순방향 q — 정해진 규칙, 학습 없음</text>

            <g>
              <rect x="26" y="32" width="56" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
              <circle cx="54" cy="52" r="11" fill="var(--accent)" opacity="0.75"/>
              <rect x="38" y="64" width="32" height="6" fill="var(--accent)" opacity="0.55"/>
              <text x="54" y="90" text-anchor="middle" font-size="9" fill="var(--ink-faint)">x₀</text>

              <rect x="166" y="32" width="56" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
              <circle cx="194" cy="52" r="11" fill="var(--accent)" opacity="0.45"/>
              <rect x="178" y="64" width="32" height="6" fill="var(--accent)" opacity="0.3"/>
              <circle cx="176" cy="42" r="1.7" fill="var(--ink-faint)"/><circle cx="210" cy="60" r="1.7" fill="var(--ink-faint)"/>
              <circle cx="186" cy="70" r="1.7" fill="var(--ink-faint)"/><circle cx="206" cy="40" r="1.7" fill="var(--ink-faint)"/>
              <text x="194" y="90" text-anchor="middle" font-size="9" fill="var(--ink-faint)">x_t</text>

              <rect x="306" y="32" width="56" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
              <circle cx="318" cy="44" r="1.7" fill="var(--ink-faint)"/><circle cx="342" cy="40" r="1.7" fill="var(--ink-faint)"/>
              <circle cx="330" cy="58" r="1.7" fill="var(--ink-faint)"/><circle cx="350" cy="66" r="1.7" fill="var(--ink-faint)"/>
              <circle cx="314" cy="66" r="1.7" fill="var(--ink-faint)"/><circle cx="352" cy="48" r="1.7" fill="var(--ink-faint)"/>
              <circle cx="334" cy="36" r="1.7" fill="var(--ink-faint)"/><circle cx="322" cy="70" r="1.7" fill="var(--ink-faint)"/>
              <text x="334" y="90" text-anchor="middle" font-size="9" fill="var(--ink-faint)">x_T ~ 𝒩(0,I)</text>

              <path d="M90 54 L158 54" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#df-f)"/>
              <text x="124" y="48" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">+노이즈</text>
              <path d="M230 54 L298 54" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#df-f)"/>
              <text x="264" y="48" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">+노이즈</text>
            </g>

            <text x="410" y="46" font-size="9.5" fill="var(--ink-soft)">x_t = √ᾱ_t·x₀ + √(1−ᾱ_t)·ε</text>
            <text x="410" y="62" font-size="9" fill="var(--ink-faint)">어느 t로든 한 번에 건너뛸 수 있다</text>

            <line x1="26" y1="108" x2="674" y2="108" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="130" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">역방향 p — 신경망이 배우는 유일한 부분</text>

            <g>
              <rect x="306" y="142" width="56" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
              <circle cx="318" cy="154" r="1.7" fill="var(--ink-faint)"/><circle cx="342" cy="150" r="1.7" fill="var(--ink-faint)"/>
              <circle cx="330" cy="168" r="1.7" fill="var(--ink-faint)"/><circle cx="350" cy="176" r="1.7" fill="var(--ink-faint)"/>
              <circle cx="314" cy="176" r="1.7" fill="var(--ink-faint)"/><circle cx="352" cy="158" r="1.7" fill="var(--ink-faint)"/>

              <rect x="166" y="142" width="56" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
              <circle cx="194" cy="162" r="11" fill="var(--accent)" opacity="0.45"/>
              <rect x="178" y="174" width="32" height="6" fill="var(--accent)" opacity="0.3"/>

              <rect x="26" y="142" width="56" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
              <circle cx="54" cy="162" r="11" fill="var(--accent)" opacity="0.8"/>
              <rect x="38" y="174" width="32" height="6" fill="var(--accent)" opacity="0.6"/>

              <path d="M298 164 L230 164" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#df-r)"/>
              <path d="M158 164 L90 164" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#df-r)"/>
            </g>

            <rect x="238" y="196" width="184" height="18" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="330" y="209" text-anchor="middle" font-size="9" fill="var(--accent)">ε_θ(x_t, t) — 섞인 노이즈를 예측</text>

            <text x="440" y="158" font-size="9.5" fill="var(--ink-soft)">L = ‖ ε − ε_θ(x_t, t) ‖²</text>
            <text x="440" y="174" font-size="9" fill="var(--ink-faint)">배우는 것은 '한 걸음'뿐이고,</text>
            <text x="440" y="188" font-size="9" fill="var(--ink-faint)">그것을 수백 번 반복해 생성한다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        위아래가 대칭처럼 보이지만 성격은 전혀 다르다.
        <strong>순방향은 공짜</strong>이고(정해진 수식), <strong>역방향만 학습</strong>한다.
        게다가 학습되는 것은 전 과정이 아니라 <em>임의의 한 단계</em>다 —
        그래서 목표가 고정돼 있고, 그래서 무너지지 않는다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>느림을 푸는 두 갈래 — DDIM과 잠재공간</h2>
    <p>
      대가는 명확하다. <strong>생성에 1000번의 순전파가 필요하다</strong>.
      GAN이 한 번에 끝내는 일을 1000번 한다. 초기 확산 모델이 느렸던 이유다.
      두 가지 해법이 나왔고, 둘 다 지금 표준이 됐다.
    </p>
    <p>
      <strong>첫째, 단계를 건너뛴다(DDIM).</strong> DDPM의 역과정은 매 단계 노이즈를 새로 주입하는
      확률적 과정이다. DDIM은 이를 <em>결정론적</em> 과정으로 다시 쓴다.
      그러면 중간 단계를 띄엄띄엄 밟아도 되고, 20~50 단계로 비슷한 품질이 나온다.
    </p>
    <div class="note">
      <b>DDIM의 부수 효과가 오히려 더 유용하다.</b> 결정론적이므로 같은 초기 노이즈는
      항상 같은 이미지를 낸다. 즉 <em>노이즈가 이미지의 좌표</em>가 된다.
      두 노이즈 사이를 보간하면 두 이미지 사이가 자연스럽게 이어지고,
      이미지를 노이즈로 되돌린 뒤(inversion) 조건만 바꿔 편집할 수도 있다.
    </div>
    <p>
      <strong>둘째, 작은 공간에서 확산시킨다(Latent Diffusion).</strong>
      512×512 픽셀에서 직접 확산하면 매 단계 78만 차원을 다뤄야 한다.
      Stable Diffusion의 선택은 오토인코더로 이미지를 <code>64×64×4</code> 잠재 표현으로 먼저 압축하고,
      <strong>그 안에서 확산을 돌리는 것</strong>이다. 차원이 48배 줄어든다.
    </p>
    <p>
      이 분업이 핵심이다. 오토인코더는 <em>지각적으로 덜 중요한 고주파 성분</em>을 걷어내고,
      확산 모델은 <em>의미 있는 구조</em>를 만드는 데 집중한다.
      소비자용 GPU에서 이미지 생성이 가능해진 결정적 이유다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>조건을 거는 법 — CFG</h2>
    <p>
      "고양이"라고 썼는데 고양이가 나오게 하려면 텍스트 조건을 걸어야 한다.
      구조적으로는 U-Net에 크로스 어텐션을 넣어 CLIP 텍스트 임베딩을 참조시킨다.
      그런데 그것만으로는 <strong>프롬프트를 잘 안 따른다</strong>.
    </p>
    <p>
      <strong>Classifier-Free Guidance</strong>가 이 문제를 푼다.
      학습 때 조건을 일정 확률(보통 10%)로 비워 조건부·무조건부 모델을 하나로 학습해 두고,
      생성할 때 두 예측의 <em>차이를 증폭</em>한다.
    </p>
    <div class="eq">
      <span class="cap">CFG — 조건이 만든 차이를 밀어붙인다</span>
      <div class="line">ε̂ = ε<sub>θ</sub>(x<sub>t</sub>, ∅) + w · ( ε<sub>θ</sub>(x<sub>t</sub>, c) − ε<sub>θ</sub>(x<sub>t</sub>, ∅) )</div>
      <div class="line">// w = 1 이면 평범한 조건부 생성, w &gt; 1 이면 조건을 과장한다</div>
      <div class="line">// 실무에서 w ≈ 7 전후를 쓴다</div>
    </div>
    <p>
      <code>w</code>를 키우면 프롬프트 충실도는 올라가지만 다양성은 줄고,
      너무 키우면 과포화된 부자연스러운 이미지가 나온다.
      이미지 생성 UI의 "guidance scale" 슬라이더가 바로 이 값이다.
    </p>
    <p>
      대가도 있다. 매 단계 순전파를 <strong>두 번</strong>(조건부·무조건부) 해야 한다.
      확산 모델의 실제 생성 비용은 단계 수 × 2가 되는 셈이다.
    </p>
    <p>
      정리하면 확산 모델의 성공은 하나의 재구성에서 나왔다 —
      <em>생성이라는 어려운 문제를, 노이즈 제거라는 쉬운 문제의 반복으로 바꾼 것.</em>
      그 대가가 느린 생성이었고, DDIM과 잠재공간이 그것을 갚았다.
    </p>
  </section>
"""

READING = [
    "Ho et al., <em>Denoising Diffusion Probabilistic Models</em> (arXiv:2006.11239) — DDPM. 단순화된 손실이 여기서 유도된다.",
    "Song et al., <em>Denoising Diffusion Implicit Models</em> (arXiv:2010.02502) — DDIM. 결정론적 역과정과 단계 건너뛰기.",
    "Rombach et al., <em>High-Resolution Image Synthesis with Latent Diffusion Models</em> (arXiv:2112.10752) — Stable Diffusion의 근간.",
    "Ho &amp; Salimans, <em>Classifier-Free Diffusion Guidance</em> (arXiv:2207.12598) — guidance scale의 출처.",
    "Sohl-Dickstein et al., <em>Deep Unsupervised Learning using Nonequilibrium Thermodynamics</em> (arXiv:1503.03585) — 확산 모델의 원형.",
    "Peebles &amp; Xie, <em>Scalable Diffusion Models with Transformers</em> (arXiv:2212.09748) — U-Net을 트랜스포머로 교체한 DiT.",
]

write(
    "diffusion-models.html",
    title="Diffusion Models — 잡음 속에서 그림을 꺼내다",
    eyebrow="Training · Generative Modeling · 2015–2026",
    h1="Diffusion Models",
    subtitle="잡음 속에서 그림을 꺼내다 — 어려운 문제를 쉬운 문제 수백 개로",
    dek=(
        "노이즈에서 이미지를 한 번에 만드는 것은 어렵다. GAN은 그러다 학습이 무너졌다. "
        "확산 모델은 문제를 쪼갠다 — <strong>노이즈를 조금 걷어내는 일</strong>만 배우고 "
        "그것을 수백 번 반복한다. 학습 목표는 결국 세 줄짜리 회귀가 된다. "
        "대가는 느린 생성이고, DDIM과 잠재공간이 그 값을 치렀다."
    ),
    spec=[
        ("배우는 것", "섞인 노이즈 ε"),
        ("손실", "‖ε − ε_θ(x_t, t)‖²"),
        ("안정성", "회귀 · 적대 학습 아님"),
        ("약점", "다단계 생성 (느림)"),
        ("조건", "CFG · w ≈ 7"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

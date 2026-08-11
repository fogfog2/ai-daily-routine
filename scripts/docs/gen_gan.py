#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ed", panel="#e7e5e1", ink="#1a1614", **{
    "ink-soft": "#564f47", "ink-faint": "#857d73", "rule": "#d4d0ca",
    "rule-strong": "#b0aba2", "accent": "#9a3324", "accent-fill": "#f6ddd6",
    "accent-line": "#c05a45", "muted": "#7f858f", "muted-fill": "#dee0e4", "warn": "#8a5a12",
})
DARK = dict(paper="#131110", panel="#1c1917", ink="#ece7e3", **{
    "ink-soft": "#ada49c", "ink-faint": "#7d746c", "rule": "#282320", "rule-strong": "#3f3833",
    "accent": "#ef8a72", "accent-fill": "#331812", "accent-line": "#b05a44",
    "muted": "#8b9099", "muted-fill": "#1c1f23", "warn": "#d9a441",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>손실 함수를 신경망에게 맡기다</h2>
    <p>
      이미지를 생성하는 모델을 학습시킨다고 하자. 손실 함수를 무엇으로 둘까.
      만든 이미지와 실제 이미지의 픽셀 차이(MSE)를 쓰면 <strong>흐릿한 결과</strong>가 나온다.
      가능한 답들의 평균이 최적해가 되기 때문이다.
    </p>
    <p>
      근본 문제는 <em>"그럴듯함"을 수식으로 적을 수 없다</em>는 것이다.
      사람은 가짜 얼굴을 한눈에 알아보지만, 그 판단을 픽셀 연산으로 옮길 방법이 없다.
    </p>
    <p>
      GAN의 발상은 여기서 도약한다 — <strong>손실 함수 자체를 신경망으로 학습시키자.</strong>
      진짜와 가짜를 구별하는 <strong>판별자</strong>를 따로 두고,
      <strong>생성자</strong>는 그 판별자를 속이도록 학습한다.
      판별자가 좋아질수록 생성자에게 주는 신호도 정교해진다.
    </p>
    <div class="eq">
      <span class="cap">최소최대 게임 — 두 목표가 정확히 반대다</span>
      <div class="line">min<sub>G</sub> max<sub>D</sub>&nbsp; V(D, G) =</div>
      <div class="line">&nbsp;&nbsp;&nbsp;E<sub>x~p<sub>data</sub></sub>[ log D(x) ] + E<sub>z~p<sub>z</sub></sub>[ log(1 − D(G(z))) ]</div>
      <div class="line">// D 는 진짜에 1, 가짜에 0 을 주려 하고</div>
      <div class="line">// G 는 D(G(z)) 가 1 이 되게 하려 한다</div>
    </div>
    <p>
      이론적으로 이 게임의 최적점에서 생성 분포는 데이터 분포와 일치하고,
      판별자는 모든 입력에 0.5를 내놓는다 — 구별이 불가능해진 상태다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>학습이 무너지는 세 가지 방식</h2>
    <p>
      아름다운 이론과 달리 GAN 학습은 악명 높게 불안정했다.
      원인은 <strong>고정된 목표를 최적화하는 것이 아니라 움직이는 상대와 균형을 찾는 문제</strong>라는 데 있다.
      전형적인 실패가 셋이다.
    </p>
    <p>
      <strong>그래디언트 소실.</strong> 판별자가 너무 잘하면
      <code>D(G(z)) ≈ 0</code>이 되고 <code>log(1 − D(G(z)))</code>의 기울기가 거의 0이 된다.
      생성자는 배울 신호를 잃는다. 원 논문도 이를 알고 있어서
      실제 구현에서는 <code>−log D(G(z))</code>를 최대화하는 <em>비포화 형태</em>를 쓴다.
    </p>
    <p>
      <strong>모드 붕괴.</strong> 생성자가 판별자를 잘 속이는 <em>한 가지 이미지</em>를 찾으면
      그것만 반복해 만든다. 손실은 낮지만 다양성이 사라진다.
      숫자 10종을 생성해야 하는데 8만 계속 그리는 식이다.
    </p>
    <p>
      <strong>진동.</strong> 두 네트워크가 서로를 쫓아 빙빙 돈다.
      수렴하지 않고 계속 움직이며, 손실 값만 봐서는 <em>학습이 잘 되는지 알 수 없다</em>.
      GAN에는 "손실이 내려가면 좋은 것"이라는 상식이 통하지 않는다.
    </p>
    <div class="note">
      <b>평가 지표가 따로 필요했던 이유다.</b> 손실이 품질을 말해주지 않으므로
      <strong>FID</strong> 같은 별도 지표가 표준이 됐다.
      사전학습된 Inception 특징 공간에서 실제 이미지 분포와 생성 이미지 분포의
      평균·공분산 거리를 재는 방식이다. 낮을수록 좋다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>거리를 바꾸다 — WGAN</h2>
    <p>
      원래 GAN 목적함수는 두 분포 사이의 <strong>Jensen-Shannon 발산</strong>을 최소화하는 것과 같다.
      문제는 두 분포가 <em>겹치지 않을 때</em> JS 발산이 상수가 되어 기울기가 사라진다는 점이다.
      고차원 이미지 공간에서 데이터는 얇은 다양체 위에 놓이므로, 겹치지 않는 상황이 오히려 정상이다.
    </p>
    <p>
      WGAN은 거리 척도를 <strong>Wasserstein 거리</strong>로 바꾼다.
      "한 분포를 다른 분포로 옮기는 데 드는 최소 비용"이라 겹치지 않아도 <em>얼마나 먼지</em>를 말해준다.
    </p>
    <div class="eq">
      <span class="cap">WGAN — 판별자가 아니라 비평자(critic)</span>
      <div class="line">max<sub>‖f‖<sub>L</sub>≤1</sub>&nbsp; E<sub>x~p<sub>data</sub></sub>[ f(x) ] − E<sub>z</sub>[ f(G(z)) ]</div>
      <div class="line">// 출력에 시그모이드가 없다 — 확률이 아니라 점수를 낸다</div>
      <div class="line">// 제약: f 가 1-Lipschitz 여야 한다</div>
    </div>
    <p>
      Lipschitz 제약을 어떻게 걸 것인가가 관건이었다.
      원 논문은 가중치를 일정 범위로 자르는 방식(weight clipping)을 썼는데 조악했고,
      <strong>WGAN-GP</strong>가 <em>그래디언트 노름이 1에서 벗어나면 벌점</em>을 주는 방식으로 개선했다.
      이후 스펙트럴 정규화가 더 간결한 대안으로 자리 잡았다.
    </p>
    <p>
      실용적 이득이 컸다. 비평자 손실이 <strong>생성 품질과 상관관계를 갖게 되어</strong>
      학습 진행 상황을 눈으로 볼 수 있게 됐고, 모드 붕괴도 줄었다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="GAN과 확산 모델의 학습 구조 비교. GAN은 생성자와 판별자가 서로 반대 방향으로 밀며 균형을 찾는 최소최대 게임이라 불안정하고, 확산 모델은 고정된 목표를 향한 회귀라 안정적이지만 생성에 수백 번의 단계가 필요하다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="gan-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="gan-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">GAN — 서로를 쫓는 게임</text>

            <rect x="26" y="34" width="58" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="55" y="50" text-anchor="middle" font-size="9" fill="var(--ink-soft)">z ~ 𝒩</text>
            <path d="M88 46 L110 46" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#gan-a)"/>

            <rect x="114" y="32" width="68" height="28" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="148" y="50" text-anchor="middle" font-size="9.5" fill="var(--accent)">생성자 G</text>

            <path d="M186 46 L210 46" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#gan-a)"/>
            <rect x="214" y="34" width="54" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="241" y="50" text-anchor="middle" font-size="9" fill="var(--ink-soft)">가짜</text>

            <rect x="214" y="96" width="54" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="241" y="112" text-anchor="middle" font-size="9" fill="var(--ink-soft)">진짜</text>

            <path d="M272 46 L296 62" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#gan-m)"/>
            <path d="M272 108 L296 92" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#gan-m)"/>

            <rect x="300" y="62" width="68" height="30" fill="var(--warn)" opacity="0.2" stroke="var(--warn)" stroke-width="1.5"/>
            <text x="334" y="81" text-anchor="middle" font-size="9.5" fill="var(--ink)">판별자 D</text>

            <path d="M334 96 L334 122 L148 122 L148 66" stroke="var(--accent-line)" stroke-width="1.3" fill="none" stroke-dasharray="4 3" marker-end="url(#gan-a)"/>
            <text x="240" y="136" text-anchor="middle" font-size="8.5" fill="var(--accent)">G 는 D 를 속이도록 갱신</text>

            <text x="26" y="164" font-size="9" fill="var(--warn)">✗ 목표가 움직인다 → 진동 · 모드 붕괴</text>
            <text x="26" y="180" font-size="9" fill="var(--warn)">✗ 손실이 품질을 말해주지 않는다 (FID 필요)</text>
            <text x="26" y="200" font-size="9" fill="var(--accent)">✓ 생성은 단 한 번의 순전파 — 빠르다</text>

            <line x1="404" y1="26" x2="404" y2="216" stroke="var(--rule)" stroke-width="1"/>

            <text x="430" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--ink-soft)">확산 — 고정된 목표를 향한 회귀</text>

            <rect x="430" y="34" width="58" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="459" y="50" text-anchor="middle" font-size="9" fill="var(--ink-soft)">x_t</text>
            <path d="M492 46 L514 46" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#gan-m)"/>
            <rect x="518" y="32" width="68" height="28" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <text x="552" y="50" text-anchor="middle" font-size="9.5" fill="var(--ink-soft)">ε_θ</text>
            <path d="M590 46 L612 46" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#gan-m)"/>
            <rect x="616" y="34" width="52" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="642" y="50" text-anchor="middle" font-size="9" fill="var(--ink-soft)">ε̂</text>

            <rect x="518" y="76" width="150" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="593" y="91" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">L = ‖ε − ε̂‖²  ← 정답 고정</text>

            <text x="430" y="130" font-size="9" fill="var(--accent)">✓ 목표가 고정 → 안정적, 모드 붕괴 없음</text>
            <text x="430" y="146" font-size="9" fill="var(--accent)">✓ 다양성이 좋다 (분포 전체를 덮는다)</text>
            <text x="430" y="166" font-size="9" fill="var(--warn)">✗ 생성에 수십~수백 단계</text>

            <text x="430" y="196" font-size="9" fill="var(--ink-faint)">그래서 최근에는 확산 모델을 GAN 방식으로</text>
            <text x="430" y="210" font-size="9" fill="var(--ink-faint)">증류해 1~4단계로 줄이는 연구가 활발하다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        두 계열의 성격이 정반대다. GAN은 <strong>한 번에 만들지만 불안정</strong>하고,
        확산은 <strong>안정적이지만 여러 번 거친다</strong>.
        지금은 확산 모델의 품질을 GAN의 속도로 뽑아내려는 방향으로 수렴하고 있다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>StyleGAN — GAN이 도달한 정점</h2>
    <p>
      구조 개선의 계보에서 두 이정표가 있다.
      <strong>DCGAN</strong>은 합성곱 기반 안정화 레시피를 정리해
      GAN을 실제로 학습 가능한 것으로 만들었고,
      <strong>StyleGAN</strong>은 생성 품질과 제어 가능성을 크게 끌어올렸다.
    </p>
    <p>
      StyleGAN의 핵심 아이디어는 <strong>노이즈를 입력으로 넣지 않는 것</strong>이다.
      대신 잠재 벡터를 매핑 네트워크로 변환해 <code>W</code> 공간을 만들고,
      그것으로 <em>각 해상도 층의 정규화 파라미터를 조절</em>한다(AdaIN).
    </p>
    <ul>
      <li><strong>계층적 제어.</strong> 낮은 해상도 층은 자세·얼굴형 같은 굵은 속성을, 높은 해상도 층은 머리카락·피부결 같은 세부를 담당한다. 층별로 다른 스타일을 주입하면 속성을 섞을 수 있다.</li>
      <li><strong>풀린 잠재공간.</strong> <code>W</code> 공간이 원래 <code>Z</code>보다 속성별로 잘 분리돼, 나이·표정 같은 방향을 찾아 편집할 수 있다.</li>
      <li><strong>확률적 세부.</strong> 층마다 별도 노이즈를 더해 머리카락 배치 같은 무작위 요소를 담당하게 한다.</li>
    </ul>
    <p>
      한동안 "실존하지 않는 사람 얼굴"의 대명사가 됐던 결과물들이 여기서 나왔다.
      GAN이 도달한 시각적 정점이었다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>왜 밀렸고, 왜 아직 쓰이는가</h2>
    <p>
      2021년 <em>"Diffusion Models Beat GANs on Image Synthesis"</em>라는 제목의 논문이 나왔고,
      제목 그대로의 일이 벌어졌다. 확산 모델이 자리를 가져간 이유는 품질만이 아니다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>기준</th><th>GAN</th><th>확산 모델</th></tr>
        </thead>
        <tbody>
          <tr><td>생성 속도</td><td class="hi">1회 순전파</td><td>수십~수백 단계</td></tr>
          <tr><td>학습 안정성</td><td>불안정 (균형 문제)</td><td class="hi">안정 (회귀)</td></tr>
          <tr><td>분포 커버리지</td><td>모드 붕괴 위험</td><td class="hi">다양성 우수</td></tr>
          <tr><td>학습 확장성</td><td>규모를 키우기 어려움</td><td class="hi">잘 확장됨</td></tr>
          <tr><td>조건 제어</td><td>구조에 의존</td><td class="hi">CFG 로 일반적</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>확장성</strong>이 결정적이었다. GAN은 모델과 데이터를 키울수록
      균형 잡기가 더 어려워졌지만, 확산 모델은 그냥 회귀라 규모를 키우면 좋아졌다.
      대규모 텍스트-이미지 모델 시대에는 이 성질이 전부였다.
    </p>
    <div class="note">
      <b>그래도 GAN은 사라지지 않았다.</b> <em>한 번의 순전파</em>라는 성질은 여전히 유일하다.
      <a href="super-resolution.html">초해상도</a>, 실시간 이미지 변환, 음성 보코더처럼 <strong>지연이 중요한 곳</strong>에서는
      GAN 계열이 계속 쓰인다.
      더 흥미로운 것은 <strong>판별자가 확산 모델 안으로 흡수됐다는 점</strong>이다 —
      확산 모델을 1~4단계로 증류할 때 적대적 손실을 쓰는 방식이 표준이 됐다.
      "손실 함수를 학습시킨다"는 GAN의 원래 발상은 살아남아, 다른 모델의 부품이 됐다.
    </div>
  </section>
"""

READING = [
    "Goodfellow et al., <em>Generative Adversarial Networks</em> (arXiv:1406.2661) — 원 논문. 최소최대 게임과 이론적 최적점.",
    "Radford et al., <em>Unsupervised Representation Learning with Deep Convolutional GANs</em> (arXiv:1511.06434) — DCGAN. 안정화 레시피.",
    "Arjovsky et al., <em>Wasserstein GAN</em> (arXiv:1701.07875) — 거리 척도 교체의 근거.",
    "Gulrajani et al., <em>Improved Training of Wasserstein GANs</em> (arXiv:1704.00028) — WGAN-GP.",
    "Karras et al., <em>A Style-Based Generator Architecture for GANs</em> (arXiv:1812.04948) — StyleGAN.",
    "Dhariwal &amp; Nichol, <em>Diffusion Models Beat GANs on Image Synthesis</em> (arXiv:2105.05233) — 자리가 넘어간 시점.",
]

write(
    "gan.html",
    title="GAN — 두 신경망을 맞붙이다",
    eyebrow="Training · Adversarial Generation · 2014–2026",
    h1="GAN",
    subtitle="두 신경망을 맞붙이다 — 손실 함수를 학습시킨다는 발상",
    dek=(
        "\"그럴듯함\"은 수식으로 적을 수 없다. MSE를 쓰면 평균이 최적해가 되어 흐릿해진다. "
        "GAN은 <strong>손실 함수 자체를 신경망으로 학습</strong>시킨다 — 판별자가 곧 손실이다. "
        "강력했지만 고정된 목표가 없어 불안정했고, 그 때문에 확산 모델에 자리를 내줬다. "
        "다만 발상 자체는 확산 모델 증류의 부품으로 살아남았다."
    ),
    spec=[
        ("구조", "생성자 vs 판별자"),
        ("목표", "최소최대 게임"),
        ("실패 모드", "모드 붕괴 · 진동"),
        ("평가", "FID (손실 아님)"),
        ("강점", "1회 순전파 생성"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

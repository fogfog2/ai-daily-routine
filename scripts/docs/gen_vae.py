#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ef", panel="#e6e8e4", ink="#161a15", **{
    "ink-soft": "#4f574c", "ink-faint": "#7e8779", "rule": "#d1d5cd",
    "rule-strong": "#adb2a7", "accent": "#4a6b1f", "accent-fill": "#e3ecd6",
    "accent-line": "#6d9438", "muted": "#83888e", "muted-fill": "#dee1e3", "warn": "#a2502a",
})
DARK = dict(paper="#101210", panel="#191c17", ink="#e7eae4", **{
    "ink-soft": "#a5aca0", "ink-faint": "#7a8175", "rule": "#232720", "rule-strong": "#3a4033",
    "accent": "#9ed35e", "accent-fill": "#1c2612", "accent-line": "#6e9440",
    "muted": "#888e94", "muted-fill": "#1b1e21", "warn": "#e08a5c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>병목을 두면 무엇이 남는가</h2>
    <p>
      오토인코더의 구조는 허무할 만큼 단순하다. 입력을 좁은 층으로 밀어 넣고,
      다시 원래대로 복원하게 시킨다. 목표는 <strong>자기 자신</strong>이다.
    </p>
    <div class="eq">
      <span class="cap">오토인코더 — 라벨이 필요 없다</span>
      <div class="line">z = f<sub>enc</sub>(x)&nbsp;&nbsp;&nbsp;// x ∈ ℝ^784  →  z ∈ ℝ^32</div>
      <div class="line">x̂ = f<sub>dec</sub>(z)</div>
      <div class="line">L = ‖ x − x̂ ‖²</div>
    </div>
    <p>
      의미 없어 보이는 과제다. 입력을 그대로 내보내면 되지 않나.
      막는 것이 <strong>병목</strong>이다. 784차원을 32차원으로 통과시켜야 하므로
      전부 담을 수 없고, <em>무엇을 버릴지 골라야 한다</em>.
    </p>
    <p>
      복원 오차를 줄이려면 <strong>가장 중요한 변화 요인부터</strong> 남겨야 한다.
      숫자 이미지라면 어떤 숫자인지, 기울기, 획 두께 같은 것들이다.
      개별 픽셀의 미세한 잡음은 버려진다. 이렇게 <em>압축을 시켰더니 의미가 생기는</em> 것이
      표현 학습의 원형이다.
    </p>
    <div class="note">
      <b>선형 오토인코더는 PCA와 같은 부분공간을 찾는다.</b>
      활성함수 없이 선형 층만 쓰면 주성분 분석이 찾는 것과 같은 공간에 도달한다.
      비선형 층이 하는 일은 이 아이디어를 <em>휘어진 다양체</em>로 확장하는 것이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>왜 오토인코더로는 생성할 수 없나</h2>
    <p>
      디코더가 있으니 <code>z</code>를 아무거나 넣으면 새 이미지가 나올 것 같다.
      실제로 해보면 <strong>의미 없는 얼룩</strong>이 나온다. 이유는 잠재공간의 모양에 있다.
    </p>
    <p>
      평범한 오토인코더는 <code>z</code>의 분포에 아무 제약이 없다.
      학습된 잠재공간은 데이터가 놓인 지점들이 <em>여기저기 흩어진 섬</em>처럼 존재하고,
      섬과 섬 사이는 학습된 적 없는 빈 공간이다. 거기서 뽑은 <code>z</code>는 디코더에게 미지의 입력이다.
    </p>
    <p>
      VAE의 요구는 여기서 나온다 — <strong>잠재공간이 매끄럽고 채워져 있게 만들자.</strong>
      방법은 두 가지를 동시에 강제하는 것이다.
    </p>
    <ul>
      <li>인코더가 점 하나가 아니라 <strong>분포</strong>를 내놓게 한다. 같은 입력이라도 매번 조금씩 다른 <code>z</code>가 샘플링되므로, 디코더는 <em>주변 영역까지</em> 복원할 줄 알아야 한다.</li>
      <li>그 분포들이 전체적으로 <strong>표준정규분포에 가깝도록</strong> 벌점을 준다. 섬들이 한데 모여 빈틈이 메워진다.</li>
    </ul>
  </section>

  <section>
    <h2><span class="n">03</span>ELBO — 두 항의 줄다리기</h2>
    <p>
      VAE의 손실은 변분 추론에서 유도되지만, 최종 형태는 두 항의 합이라 읽기 쉽다.
    </p>
    <div class="eq">
      <span class="cap">ELBO — 최대화 대상 (부호를 뒤집어 손실로 쓴다)</span>
      <div class="line">ℒ = E<sub>q(z|x)</sub>[ log p(x|z) ] &nbsp;−&nbsp; KL( q(z|x) ‖ p(z) )</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ 복원 항 ─────────┘&nbsp;&nbsp;&nbsp;└ 정규화 항 ──────┘</div>
      <div class="line">p(z) = 𝒩(0, I)&nbsp;&nbsp;&nbsp;q(z|x) = 𝒩( μ(x), σ²(x) )</div>
    </div>
    <p>
      두 항이 서로를 당긴다. <strong>복원 항</strong>은 <code>z</code>에 정보를 최대한 담으라고 하고,
      <strong>KL 항</strong>은 <code>z</code>를 표준정규분포에 붙여 두라고 한다.
      KL이 이기면 <code>z</code>가 입력을 무시하게 되고(뒤에서 다룬다),
      복원이 이기면 평범한 오토인코더로 돌아간다.
    </p>
    <p>
      가우시안 가정 덕분에 KL 항은 <strong>닫힌 형태</strong>로 계산된다. 샘플링이 필요 없다.
    </p>
    <div class="eq">
      <span class="cap">KL 항 — 차원별로 더하면 끝</span>
      <div class="line">KL = −½ Σ<sub>j</sub> ( 1 + log σ<sub>j</sub>² − μ<sub>j</sub>² − σ<sub>j</sub>² )</div>
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>재매개화 — 샘플링을 미분 가능하게</h2>
    <p>
      한 가지 문제가 남는다. <code>z</code>를 <em>샘플링</em>해야 하는데,
      샘플링은 미분할 수 없는 연산이다. 인코더로 그래디언트를 보낼 수가 없다.
    </p>
    <p>
      <strong>재매개화 기법</strong>이 이것을 푼다. 무작위성을 <em>바깥에서 주입</em>하는 형태로 식을 다시 쓴다.
    </p>
    <div class="eq">
      <span class="cap">재매개화 — 무작위성을 계산 경로 밖으로 밀어낸다</span>
      <div class="line">이전:&nbsp; z ~ 𝒩( μ(x), σ²(x) )&nbsp;&nbsp;&nbsp;← μ, σ 로 미분 불가</div>
      <div class="line">이후:&nbsp; ε ~ 𝒩(0, I),&nbsp;&nbsp; <strong>z = μ(x) + σ(x) ⊙ ε</strong></div>
      <div class="line">// 이제 z 는 μ, σ 의 미분 가능한 함수. ε 는 그냥 입력된 상수.</div>
    </div>
    <p>
      같은 분포에서 뽑지만 계산 그래프의 모양이 다르다.
      확률적인 부분이 <code>ε</code>로 분리돼 <strong>그래디언트가 지나는 경로에서 빠졌다</strong>.
      이 한 줄이 VAE를 실제로 학습 가능하게 만든 장치다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 216" role="img" aria-label="오토인코더와 VAE의 잠재공간 비교. 오토인코더는 데이터 지점들이 섬처럼 흩어져 사이 공간이 비어 있어 새 샘플을 뽑을 수 없고, VAE는 KL 항이 분포를 표준정규분포로 모아 공간이 매끄럽게 채워지므로 임의의 점에서 샘플링과 보간이 가능하다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="vae-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--muted)">AE — 섬처럼 흩어진 잠재공간</text>
            <rect x="26" y="32" width="160" height="130" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g fill="var(--warn)" opacity="0.75">
              <circle cx="52" cy="56" r="4"/><circle cx="60" cy="66" r="4"/><circle cx="46" cy="70" r="4"/>
              <circle cx="146" cy="52" r="4"/><circle cx="156" cy="62" r="4"/>
              <circle cx="60" cy="136" r="4"/><circle cx="72" cy="144" r="4"/>
              <circle cx="150" cy="132" r="4"/><circle cx="140" cy="142" r="4"/>
              <circle cx="106" cy="96" r="4"/>
            </g>
            <text x="106" y="112" text-anchor="middle" font-size="9" fill="var(--warn)">?</text>
            <circle cx="106" cy="120" r="14" fill="none" stroke="var(--warn)" stroke-width="1.2" stroke-dasharray="3 2"/>
            <text x="26" y="180" font-size="9" fill="var(--warn)">빈 곳에서 뽑으면 얼룩이 나온다</text>
            <text x="26" y="194" font-size="9" fill="var(--ink-faint)">z 분포에 아무 제약이 없기 때문</text>

            <line x1="222" y1="24" x2="222" y2="208" stroke="var(--rule)" stroke-width="1"/>

            <text x="250" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">VAE — 채워진 잠재공간</text>
            <rect x="250" y="32" width="160" height="130" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <circle cx="330" cy="97" r="56" fill="none" stroke="var(--accent-line)" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>
            <circle cx="330" cy="97" r="34" fill="none" stroke="var(--accent-line)" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>
            <g fill="var(--accent)" opacity="0.8">
              <circle cx="310" cy="80" r="3.6"/><circle cx="344" cy="86" r="3.6"/><circle cx="326" cy="108" r="3.6"/>
              <circle cx="352" cy="112" r="3.6"/><circle cx="300" cy="106" r="3.6"/><circle cx="332" cy="70" r="3.6"/>
              <circle cx="316" cy="126" r="3.6"/><circle cx="356" cy="94" r="3.6"/><circle cx="292" cy="88" r="3.6"/>
              <circle cx="340" cy="130" r="3.6"/><circle cx="368" cy="76" r="3.6"/><circle cx="288" cy="122" r="3.6"/>
            </g>
            <text x="250" y="180" font-size="9" fill="var(--accent)">아무 데서나 뽑아도 그럴듯하다</text>
            <text x="250" y="194" font-size="9" fill="var(--ink-faint)">KL 항이 𝒩(0,I) 쪽으로 모았기 때문</text>

            <line x1="446" y1="24" x2="446" y2="208" stroke="var(--rule)" stroke-width="1"/>

            <text x="472" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--ink-soft)">재매개화</text>

            <rect x="472" y="34" width="60" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="502" y="50" text-anchor="middle" font-size="9" fill="var(--ink-soft)">x</text>
            <path d="M502 60 L502 72" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#vae-a)"/>

            <rect x="472" y="76" width="60" height="22" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="502" y="91" text-anchor="middle" font-size="9" fill="var(--accent)">μ, σ</text>

            <rect x="580" y="76" width="60" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1" stroke-dasharray="3 2"/>
            <text x="610" y="91" text-anchor="middle" font-size="9" fill="var(--ink-faint)">ε ~ 𝒩(0,I)</text>

            <path d="M502 100 L502 114" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#vae-a)"/>
            <path d="M600 100 L536 116" stroke="var(--rule-strong)" stroke-width="1.2" stroke-dasharray="3 2"/>

            <rect x="462" y="118" width="140" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="532" y="134" text-anchor="middle" font-size="9" fill="var(--accent)">z = μ + σ ⊙ ε</text>

            <path d="M502 144 L502 156" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#vae-a)"/>
            <rect x="472" y="160" width="60" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="502" y="175" text-anchor="middle" font-size="9" fill="var(--ink-soft)">x̂</text>

            <text x="472" y="200" font-size="8.5" fill="var(--ink-faint)">ε 가 경로 밖에 있어 그래디언트가 흐른다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        VAE가 산 것은 <strong>구조화된 잠재공간</strong>이다.
        두 점 사이를 보간하면 중간 이미지가 자연스럽게 이어지고, 임의의 점에서 샘플링이 된다.
        판 값은 <em>흐릿함</em>이다 — 분포를 강제하느라 세부를 평균 내기 때문이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>흐릿함, 붕괴, 그리고 확산 모델의 발판</h2>
    <p>
      VAE의 고질적 약점은 <strong>흐릿한 출력</strong>이다. 원인은 두 겹이다.
      복원 손실로 MSE를 쓰면 가능한 답들의 <em>평균</em>이 최적해가 되고, 평균은 흐리다.
      게다가 KL 항이 잠재 표현을 뭉개는 방향으로 압박한다.
    </p>
    <p>
      더 성가신 실패 모드는 <strong>사후 붕괴</strong>다.
      디코더가 충분히 강력하면(예: 자기회귀 디코더) <code>z</code> 없이도 그럴듯한 출력을 낼 수 있다.
      그러면 모델은 KL을 0으로 만드는 쉬운 길을 택한다 — <em><code>z</code>를 아예 쓰지 않는 것</em>이다.
      잠재변수가 무의미해진다. KL 항에 가중치를 서서히 올리는 <strong>KL 어닐링</strong> 같은 처방이 여기서 나왔다.
    </p>
    <div class="note">
      <b>β-VAE는 이 줄다리기를 손잡이로 만들었다.</b> KL 항에 계수 <code>β</code>를 붙여
      <code>β &gt; 1</code>이면 정규화를 강하게 건다. 그러면 각 잠재 차원이 서로 독립적인
      변화 요인(각도, 크기, 색)에 대응하는 <strong>풀림</strong> 현상이 나타난다.
      복원 품질을 내주고 해석 가능성을 사는 거래다.
    </div>
    <p>
      그러나 VAE의 가장 중요한 유산은 생성 품질이 아니라 <strong>잠재공간이라는 도구</strong> 자체다.
      Stable Diffusion을 보면 분명하다 — 확산 과정을 픽셀이 아니라
      <em>VAE가 만든 <code>64×64×4</code> 잠재공간 안에서</em> 돌린다.
      VAE는 지각적으로 덜 중요한 고주파를 걷어내는 압축기 역할을 맡고,
      의미 있는 구조를 만드는 일은 확산 모델이 한다.
    </p>
    <p>
      역할 분담을 이렇게 읽으면 계보가 선명해진다.
      VAE는 <em>좋은 생성기</em>로서는 GAN과 확산 모델에 밀렸지만,
      <em>좋은 압축기</em>로서는 현재 이미지 생성 파이프라인의 바닥에 그대로 깔려 있다.
      VQ-VAE 계열이 이산 코드북으로 같은 일을 하며 자기회귀 이미지·오디오 생성의 기반이 된 것도 같은 맥락이다.
    </p>
  </section>
"""

READING = [
    "Kingma &amp; Welling, <em>Auto-Encoding Variational Bayes</em> (arXiv:1312.6114) — VAE 원 논문. ELBO 유도와 재매개화.",
    "Rezende et al., <em>Stochastic Backpropagation and Approximate Inference in Deep Generative Models</em> (arXiv:1401.4082) — 같은 시기 독립적으로 나온 결과.",
    "Higgins et al., <em>β-VAE: Learning Basic Visual Concepts with a Constrained Variational Framework</em> (ICLR 2017) — 풀림과 β 손잡이.",
    "van den Oord et al., <em>Neural Discrete Representation Learning</em> (arXiv:1711.00937) — VQ-VAE. 이산 코드북 잠재공간.",
    "Bowman et al., <em>Generating Sentences from a Continuous Space</em> (arXiv:1511.06349) — 사후 붕괴와 KL 어닐링.",
    "Rombach et al., <em>High-Resolution Image Synthesis with Latent Diffusion Models</em> (arXiv:2112.10752) — VAE 잠재공간 위에서 도는 확산.",
]

write(
    "autoencoders-vae.html",
    title="Autoencoders & VAE — 압축이 만들어낸 잠재공간",
    eyebrow="Architecture · Representation Learning · 2013–2026",
    h1="Autoencoders &amp; VAE",
    subtitle="압축이 만들어낸 잠재공간 — 재구성만 시켰더니 의미가 생겼다",
    dek=(
        "입력을 좁은 층에 통과시켜 원래대로 복원하게 시킨다. 라벨은 필요 없다. "
        "병목 때문에 <strong>무엇을 버릴지 골라야</strong> 하고, 그 선택이 곧 의미가 된다. "
        "다만 그 공간은 구멍이 숭숭 뚫려 있어 생성에는 못 쓴다. "
        "VAE는 분포를 강제해 공간을 메우고, 흐릿함을 대가로 치른다."
    ),
    spec=[
        ("과제", "자기 자신 복원"),
        ("손실", "복원 + KL"),
        ("핵심 장치", "재매개화"),
        ("약점", "흐릿함 · 사후 붕괴"),
        ("현재 용도", "확산 모델의 압축기"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

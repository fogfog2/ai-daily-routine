#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff0f1", panel="#e4e7e8", ink="#12181b", **{
    "ink-soft": "#4a5459", "ink-faint": "#79838a", "rule": "#ccd2d5",
    "rule-strong": "#a9b0b4", "accent": "#26527e", "accent-fill": "#dae4f2",
    "accent-line": "#4477aa", "muted": "#83888c", "muted-fill": "#dee1e3", "warn": "#a04a26",
})
DARK = dict(paper="#0e1114", panel="#161a1e", ink="#e3e8ec", **{
    "ink-soft": "#a0a9af", "ink-faint": "#6f787e", "rule": "#202629", "rule-strong": "#363e44",
    "accent": "#79aae0", "accent-fill": "#101f33", "accent-line": "#4a77aa",
    "muted": "#868c90", "muted-fill": "#191d20", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>노이즈는 어디서 오는가</h2>
    <p>
      어두운 곳에서 찍은 사진이 지저분한 것은 카메라가 나빠서가 아니다.
      <strong>빛 자체가 이산적</strong>이기 때문이다.
    </p>
    <p>
      센서에 도달하는 광자의 개수는 매번 조금씩 다르다.
      평균이 100개라면 실제로는 95개, 108개가 들어온다 — <strong>포아송 분포</strong>를 따른다.
      이 흔들림의 표준편차는 평균의 제곱근이므로,
      <em>빛이 적을수록 신호 대비 흔들림이 커진다.</em>
    </p>
    <div class="eq">
      <span class="cap">빛이 적으면 왜 더 지저분한가</span>
      <div class="line">광자 평균 10,000개 → 표준편차 100 → 흔들림 <strong>1%</strong></div>
      <div class="line">광자 평균&nbsp;&nbsp;&nbsp; 100개 → 표준편차&nbsp; 10 → 흔들림 <strong>10%</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 노이즈가 는 것이 아니라 신호가 준 것이다</div>
    </div>
    <p>
      여기에 센서 자체의 열잡음과 회로 잡음이 더해진다. 이쪽은 밝기와 무관해
      대략 가우시안으로 본다. 그래서 실제 노이즈는 <strong>포아송 + 가우시안</strong>의 혼합이고,
      <em>밝기에 따라 세기가 달라진다</em>.
    </p>
    <div class="note">
      <b>이 사실이 실무에서 중요한 이유.</b> 연구에서 흔히 쓰는
      <em>"가우시안 노이즈 σ=25를 더한 데이터"</em>는 실제 사진과 성질이 다르다.
      균일한 세기의 가우시안만 학습한 모델은 <strong>실사진에서 잘 작동하지 않는다</strong> —
      <a href="super-resolution.html">초해상</a>에서 bicubic 축소로만 학습한 모델이
      실사진에서 실패하는 것과 같은 구조의 문제다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>지우는 것과 남기는 것</h2>
    <p>
      복원의 근본 난점은 <strong>노이즈와 세부가 둘 다 고주파</strong>라는 것이다.
      단순히 부드럽게 만들면 노이즈와 함께 <em>질감·머리카락·글자</em>가 사라진다.
    </p>
    <p>
      고전적 방법들은 이 문제를 <em>"무엇이 진짜 신호인가"</em>에 대한 가정으로 풀었다.
    </p>
    <ul>
      <li><strong>가우시안 블러</strong> — 이웃은 비슷하다고 가정. 경계까지 뭉갠다</li>
      <li><strong>양방향 필터</strong> — 위치가 가깝고 <em>밝기도 비슷한</em> 픽셀만 평균. 경계를 지킨다</li>
      <li><strong>Non-Local Means</strong> — 이웃이 아니라 <strong>비슷한 패치</strong>를 찾아 평균</li>
    </ul>
    <p>
      세 번째의 발상이 특히 좋다. 벽돌 무늬는 이미지 곳곳에 반복되므로,
      <em>멀리 있어도 비슷한 패치들</em>을 모아 평균 내면 노이즈는 상쇄되고 무늬는 남는다.
      노이즈는 무작위라 평균에서 사라지고, 무늬는 공통이라 살아남는다.
    </p>
    <div class="eq">
      <span class="cap">자기 유사성 — 노이즈만 골라 상쇄시키는 원리</span>
      <div class="line">비슷한 패치 N개를 평균하면</div>
      <div class="line">&nbsp;&nbsp;신호는 그대로 (공통 성분)</div>
      <div class="line">&nbsp;&nbsp;노이즈는 <strong>1/√N</strong> 로 줄어든다 (무작위 성분)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// BM3D 는 이 아이디어를 변환 영역에서 정교화해</div>
      <div class="line">// 오랫동안 학습 기반 방법의 기준선이었다</div>
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>잔차를 배우는 편이 낫다</h2>
    <p>
      학습 기반으로 넘어오면서 발견된 실무적 요령이 하나 있다.
      <strong>깨끗한 이미지를 예측하는 것보다 노이즈를 예측하는 편이 낫다.</strong>
    </p>
    <div class="eq">
      <span class="cap">잔차 학습</span>
      <div class="line">직접:&nbsp; 모델(y) → x&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 이미지 전체를 만들어내야 한다</div>
      <div class="line">잔차:&nbsp; 모델(y) → <strong>n</strong>,&nbsp; x = y − n&nbsp;// 노이즈만 찾으면 된다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// y = 노이즈 이미지, x = 깨끗한 이미지, n = 노이즈</div>
    </div>
    <p>
      노이즈는 이미지보다 <em>구조가 단순</em>하다. 대략 무작위이고 통계적 성질이 일정하다.
      반면 깨끗한 이미지는 복잡한 구조를 전부 재현해야 한다.
      <strong>쉬운 쪽을 배우게 하고 나머지는 뺄셈으로 얻는</strong> 것이 요령이다.
    </p>
    <div class="note">
      <b>같은 발상을 이미 본 적이 있다.</b>
      <a href="cnn-basics.html">잔차 연결</a>이 "항등을 배우지 말고 변화량만 배우게" 한 것,
      그리고 <a href="diffusion-models.html">확산 모델</a>이
      <em>이미지가 아니라 섞인 노이즈를 예측하게</em> 한 것이 모두 같은 계열이다.
      확산 모델의 학습 목표가 사실상 <strong>denoising</strong> 그 자체라는 점은
      우연이 아니라 설계의 출발점이었다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>깨끗한 정답이 없을 때</h2>
    <p>
      학습에는 <em>(노이즈 이미지, 깨끗한 이미지)</em> 쌍이 필요하다.
      그런데 실제 촬영에서 깨끗한 원본을 얻기가 어렵다.
      같은 장면을 오래 노출해 찍어도 미세한 움직임과 조명 변화가 있다.
    </p>
    <p>
      여기서 놀라운 결과가 나왔다. <strong>깨끗한 정답이 없어도 학습이 된다.</strong>
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 224" role="img" aria-label="깨끗한 정답 없이 학습하는 방법들. Noise2Noise는 같은 장면의 다른 노이즈 이미지 두 장을 쌍으로 쓰고, Noise2Void는 한 장에서 픽셀을 가리고 주변으로 복원하게 한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="dn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">기존 — 깨끗한 정답이 필요</text>
            <rect x="24" y="30" width="56" height="42" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g fill="var(--ink-faint)"><circle cx="36" cy="42" r="1.6"/><circle cx="58" cy="50" r="1.6"/><circle cx="48" cy="62" r="1.6"/><circle cx="68" cy="38" r="1.6"/></g>
            <text x="52" y="86" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">노이즈</text>
            <path d="M88 50 L110 50" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#dn-a)"/>
            <rect x="116" y="30" width="56" height="42" fill="var(--accent)" opacity="0.2" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="144" y="86" text-anchor="middle" font-size="7.5" fill="var(--accent)">깨끗한 원본</text>
            <text x="24" y="106" font-size="8" fill="var(--warn)">✗ 실제 촬영에서 얻기 어렵다</text>

            <line x1="200" y1="26" x2="200" y2="118" stroke="var(--rule)" stroke-width="1"/>

            <text x="224" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">Noise2Noise — 노이즈끼리</text>
            <rect x="224" y="30" width="56" height="42" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g fill="var(--ink-faint)"><circle cx="236" cy="42" r="1.6"/><circle cx="258" cy="50" r="1.6"/><circle cx="248" cy="62" r="1.6"/></g>
            <path d="M288 50 L310 50" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dn-a)"/>
            <rect x="316" y="30" width="56" height="42" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g fill="var(--ink-faint)"><circle cx="330" cy="56" r="1.6"/><circle cx="352" cy="40" r="1.6"/><circle cx="342" cy="64" r="1.6"/></g>
            <text x="298" y="86" text-anchor="middle" font-size="7.5" fill="var(--accent)">같은 장면 · 다른 노이즈</text>
            <text x="224" y="106" font-size="8" fill="var(--accent)">✓ 노이즈 평균이 0 이면 성립한다</text>

            <line x1="400" y1="26" x2="400" y2="118" stroke="var(--rule)" stroke-width="1"/>

            <text x="424" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">Noise2Void — 한 장으로</text>
            <rect x="424" y="30" width="70" height="42" fill="var(--muted-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <g stroke="var(--rule)" stroke-width="0.5" fill="none">
              <line x1="446" y1="30" x2="446" y2="72"/><line x1="470" y1="30" x2="470" y2="72"/>
              <line x1="424" y1="44" x2="494" y2="44"/><line x1="424" y1="58" x2="494" y2="58"/>
            </g>
            <rect x="446" y="44" width="24" height="14" fill="var(--warn)" opacity="0.5"/>
            <text x="512" y="45" font-size="8" fill="var(--warn)">가린다</text>
            <text x="512" y="59" font-size="8" fill="var(--ink-faint)">→ 주변으로 복원</text>
            <text x="424" y="86" font-size="7.5" fill="var(--ink-faint)">가린 자리를 이웃만 보고 맞힌다</text>
            <text x="424" y="106" font-size="8" fill="var(--accent)">✓ 쌍이 아예 필요 없다</text>

            <line x1="24" y1="132" x2="674" y2="132" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="152" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">왜 성립하는가</text>
            <text x="24" y="174" font-size="8.5" fill="var(--ink-soft)">MSE 를 최소화하면 <tspan fill="var(--accent)">답들의 평균</tspan>이 나온다 — 여기서는 그것이 이롭다.</text>
            <text x="24" y="190" font-size="8" fill="var(--ink-faint)">목표에 실린 노이즈가 평균 0 이면, 평균을 취하는 과정에서 노이즈만 사라지고 신호가 남는다.</text>
            <text x="24" y="210" font-size="8" fill="var(--warn)">초해상에서는 이 성질이 해로웠지만(흐려짐), denoising 에서는 정확히 원하는 것이다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        같은 수학적 성질이 과제에 따라 <strong>독이 되기도 약이 되기도</strong> 한다.
        <a href="super-resolution.html">초해상</a>에서 MSE 의 평균 성질은 흐림을 낳았지만,
        denoising 에서는 <em>노이즈를 상쇄시키는 바로 그 원리</em>가 된다.
        손실 함수를 고를 때 <em>무엇을 평균 내는가</em>를 봐야 하는 이유다.
      </figcaption>
    </figure>

    <p>
      <strong>Noise2Void</strong> 는 한 걸음 더 간다. 쌍조차 필요 없다.
      픽셀을 가리고 <em>주변만 보고 그 값을 맞히게</em> 한다.
      가린 픽셀의 노이즈는 주변에서 알 수 없으므로 예측할 수 없고,
      신호만 예측 가능하다. 그래서 <strong>모델은 신호만 배운다</strong>.
      <a href="self-supervised-learning.html">마스크 재구성</a>과 정확히 같은 구조다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>어디서 지울 것인가</h2>
    <p>
      실무 배치에서 중요한 판단이 하나 더 있다. <strong>파이프라인의 어느 지점</strong>에서 노이즈를 다룰 것인가.
    </p>
    <p>
      카메라는 센서의 RAW 데이터를 여러 단계(디모자이킹·화이트밸런스·톤매핑·압축)를 거쳐
      최종 이미지로 만든다. 노이즈 제거를 <em>어디에 넣느냐</em>가 결과를 바꾼다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>위치</th><th>장점</th><th>단점</th></tr>
        </thead>
        <tbody>
          <tr><td>RAW 단계</td><td class="hi">노이즈 모델이 단순·예측 가능</td><td>센서마다 다시 맞춰야 함</td></tr>
          <tr><td>RGB 단계</td><td>범용 · 센서 무관</td><td class="hi">이미 처리로 노이즈가 뒤엉킴</td></tr>
          <tr><td>여러 장 합성</td><td class="hi">가장 효과적 (√N 감소)</td><td>정렬 필요 · 움직이면 잔상</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>여러 장을 합치는 것</strong>이 원리적으로 가장 강력하다.
      앞에서 본 <code>1/√N</code> 이 그대로 적용된다 —
      실제로 스마트폰의 야간 촬영은 대부분 이 방식이다.
      다만 손떨림과 피사체 움직임을 정렬해야 하고, 정렬이 틀리면 잔상이 생긴다.
    </p>
    <div class="note">
      <b>지어내는 것과 지우는 것의 경계.</b> 최근 모델은 노이즈를 지우면서
      <em>있을 법한 세부를 채워 넣기도</em> 한다. 감상용으로는 좋지만,
      <a href="super-resolution.html">초해상</a>에서 지적한 위험이 그대로 적용된다 —
      <strong>증거로 쓰이는 이미지</strong>에서는 지어낸 세부가 문제가 된다.
      "노이즈 제거"라는 이름이 순수한 복원처럼 들리지만,
      강한 모델일수록 생성에 가까워진다는 점을 알고 써야 한다.
    </div>
    <p>
      정리하면 denoising 은 <em>무작위인 것과 그렇지 않은 것을 가르는</em> 과제다.
      고전 방법은 자기 유사성이라는 가정으로 그것을 했고,
      학습 방법은 데이터에서 <strong>"무엇이 예측 가능한가"</strong>를 배워서 한다.
      Noise2Void 가 보여준 것처럼, <em>예측 불가능한 것이 곧 노이즈</em>라는 정의가
      이 분야의 밑바닥에 깔려 있다.
    </p>
  </section>
"""

READING = [
    "Buades et al., <em>A Non-Local Algorithm for Image Denoising</em> (CVPR 2005) — 자기 유사성 기반 복원.",
    "Dabov et al., <em>Image Denoising by Sparse 3-D Transform-Domain Collaborative Filtering</em> (IEEE TIP 2007) — BM3D. 오랜 기준선.",
    "Zhang et al., <em>Beyond a Gaussian Denoiser: Residual Learning of Deep CNN for Image Denoising</em> (arXiv:1608.03981) — DnCNN. 잔차 학습.",
    "Lehtinen et al., <em>Noise2Noise: Learning Image Restoration without Clean Data</em> (arXiv:1803.04189) — 깨끗한 정답 없이 학습.",
    "Krull et al., <em>Noise2Void — Learning Denoising from Single Noisy Images</em> (arXiv:1811.10980) — 쌍조차 없이.",
    "Abdelhamed et al., <em>A High-Quality Denoising Dataset for Smartphone Cameras</em> (CVPR 2018) — SIDD. 실사진 노이즈의 성질.",
]

write(
    "denoising.html",
    title="노이즈 제거 — 무작위인 것을 가려내기",
    eyebrow="Vision · Image Restoration · 2005–2026",
    h1="노이즈 제거",
    subtitle="무작위인 것을 가려내기 — 노이즈와 세부는 둘 다 고주파다",
    dek=(
        "어두운 곳의 사진이 지저분한 것은 <strong>빛이 이산적</strong>이기 때문이다. "
        "광자 수가 포아송을 따라 흔들리고, 빛이 적을수록 그 비율이 커진다. "
        "문제는 노이즈와 세부가 <em>둘 다 고주파</em>라는 것 — "
        "부드럽게 만들면 질감과 글자가 함께 사라진다."
    ),
    spec=[
        ("원인", "포아송 + 가우시안"),
        ("난점", "노이즈·세부 모두 고주파"),
        ("고전 원리", "자기 유사성 · 1/√N"),
        ("학습 요령", "잔차(노이즈)를 예측"),
        ("정답 없이", "Noise2Noise · Noise2Void"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

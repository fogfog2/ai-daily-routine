#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0f1", panel="#e7e5e8", ink="#191519", **{
    "ink-soft": "#554d56", "ink-faint": "#847c86", "rule": "#d5d0d6",
    "rule-strong": "#b1aab2", "accent": "#7a3560", "accent-fill": "#f0dceb",
    "accent-line": "#a3588a", "muted": "#84868d", "muted-fill": "#dfe0e3", "warn": "#a0522a",
})
DARK = dict(paper="#121016", panel="#1a171c", ink="#eae5eb", **{
    "ink-soft": "#aba2ac", "ink-faint": "#7c737e", "rule": "#262028", "rule-strong": "#3c3540",
    "accent": "#dc8ec0", "accent-fill": "#2e1526", "accent-line": "#a35f88",
    "muted": "#87898f", "muted-fill": "#1b1c20", "warn": "#e0865c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>같은 점수, 다른 체감</h2>
    <p>
      <a href="super-resolution.html">초해상</a> 문서에서 PSNR 이 높은데 눈에는 나쁜 결과가 나온다고 했다.
      그 말을 정확히 하려면 <strong>PSNR 이 무엇을 재고 있는지</strong>를 봐야 한다.
    </p>
    <p>
      PSNR 은 MSE 를 로그로 바꾼 것이다. 픽셀별 차이를 제곱해 평균 낸 값이므로,
      <em>어디서 얼마나 틀렸는지</em>만 보고 <em>어떻게 틀렸는지</em>는 보지 않는다.
      다음 두 경우를 비교해 보자.
    </p>
    <div class="eq">
      <span class="cap">MSE 가 같은 두 열화 — 체감은 전혀 다르다</span>
      <div class="line">① 가우시안 노이즈로 MSE 100&nbsp;&nbsp;→ PSNR <strong>28.13 dB</strong></div>
      <div class="line">② 전체 밝기를 +10 이동해 MSE 100 → PSNR <strong>28.13 dB</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// ① 은 지저분해 보이고, ② 는 거의 알아채지 못한다</div>
      <div class="line">// 수치는 소수점까지 같다</div>
    </div>
    <p>
      사람의 시각은 <strong>절대 밝기보다 국소 대비와 구조</strong>에 민감하다.
      전체가 조금 밝아진 것은 잘 못 느끼고, 있어야 할 무늬가 깨진 것은 바로 알아챈다.
      픽셀별 제곱오차는 이 차이를 담지 못한다.
    </p>
    <div class="note">
      <b>그래서 지표가 여럿 필요하다.</b> 어느 하나가 "정답"인 것이 아니라,
      <em>각 지표가 무엇을 보는지</em>를 알고 목적에 맞게 고르는 문제다.
      논문에서 여러 지표를 함께 싣는 이유이기도 하다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>SSIM — 구조를 따로 본다</h2>
    <p>
      <strong>SSIM</strong> 은 앞의 관찰을 그대로 식에 옮겼다.
      두 이미지를 통째로 비교하지 않고, <em>작은 창을 밀어가며</em> 세 가지를 따로 재서 곱한다.
    </p>
    <div class="eq">
      <span class="cap">SSIM — 휘도 · 대비 · 구조의 곱</span>
      <div class="line">SSIM = l(x,y)<sup>α</sup> · c(x,y)<sup>β</sup> · s(x,y)<sup>γ</sup></div>
      <div class="line">&nbsp;</div>
      <div class="line">l 휘도&nbsp; 평균끼리 비교&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (2μ<sub>x</sub>μ<sub>y</sub>+C₁)/(μ<sub>x</sub>²+μ<sub>y</sub>²+C₁)</div>
      <div class="line">c 대비&nbsp; 표준편차끼리 비교&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (2σ<sub>x</sub>σ<sub>y</sub>+C₂)/(σ<sub>x</sub>²+σ<sub>y</sub>²+C₂)</div>
      <div class="line">s 구조&nbsp; <strong>정규화 후 상관</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (σ<sub>xy</sub>+C₃)/(σ<sub>x</sub>σ<sub>y</sub>+C₃)</div>
    </div>
    <p>
      세 번째 항이 핵심이다. 평균과 분산을 빼고 나눈 <em>정규화된 신호끼리</em> 상관을 재므로,
      밝기나 대비가 통째로 달라져도 <strong>무늬가 같으면 높은 점수</strong>가 나온다.
      앞의 ② 같은 경우를 PSNR 과 달리 관대하게 본다.
    </p>
    <p>
      값은 −1에서 1 사이이고 보통 0~1로 읽는다. 1이면 완전히 같다.
      실무에서는 여러 배율에서 계산해 합치는 <strong>MS-SSIM</strong> 을 쓰는 경우가 많다 —
      사람이 보는 거리에 따라 중요한 주파수가 다르기 때문이다.
    </p>
    <div class="note">
      <b>SSIM 도 만능이 아니다.</b> 구조를 보긴 하지만
      <em>"그럴듯하게 지어낸 다른 무늬"</em>는 여전히 벌한다.
      <a href="gan.html">GAN</a> 기반 초해상이 만든 사실적인 질감은
      원본과 위상이 다르므로 SSIM 도 낮게 준다.
      결국 <strong>원본과 픽셀 단위로 대응</strong>을 요구하는 계열이라는 한계를 공유한다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>LPIPS — 사람 판단을 학습한 지표</h2>
    <p>
      다음 발상은 급진적이다. <em>좋은 거리 함수를 사람이 설계하지 말고 학습하자.</em>
    </p>
    <p>
      <strong>LPIPS</strong> 는 두 이미지를 사전학습된 분류망에 통과시켜
      <em>중간 층 특징</em>의 거리를 잰다.
      <a href="super-resolution.html">초해상</a>의 지각 손실과 같은 재료인데,
      여기서는 학습이 아니라 <strong>평가</strong>에 쓴다.
    </p>
    <div class="eq">
      <span class="cap">LPIPS — 층별 특징 거리를 가중합</span>
      <div class="line">d(x, x₀) = Σ<sub>l</sub> (1/H<sub>l</sub>W<sub>l</sub>) Σ<sub>h,w</sub> ‖ w<sub>l</sub> ⊙ ( φ̂<sub>l</sub>(x) − φ̂<sub>l</sub>(x₀) ) ‖²</div>
      <div class="line">&nbsp;</div>
      <div class="line">φ̂ = 채널 정규화된 특징,&nbsp; w<sub>l</sub> = <strong>사람 판단으로 학습한 가중치</strong></div>
      <div class="line">// 낮을수록 유사하다 (PSNR·SSIM 과 방향이 반대다)</div>
    </div>
    <p>
      가중치 <code>w</code> 를 사람의 2지선다 판단 데이터로 학습한 것이 핵심이다.
      "어느 쪽이 원본에 더 가까워 보이는가"를 수만 번 물어 얻은 답에 맞춘다.
      그래서 <strong>지표 자체가 사람 선호의 근사</strong>가 된다.
    </p>
    <p>
      원 논문의 관찰이 흥미롭다 — <em>어떤 망을 쓰든, 심지어 무작위 초기화가 아닌
      어떤 과제로 학습했든</em> 깊은 특징 공간의 거리는 픽셀 거리보다 사람 판단에 훨씬 가까웠다.
      "지각적 유사도"가 특정 구조의 산물이 아니라 <em>깊은 표현 일반의 성질</em>이라는 시사다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="화질 지표의 세 계열 비교. 픽셀 기반 PSNR은 어떻게 틀렸는지를 구분하지 못하고, 구조 기반 SSIM은 밝기 변화에 관대하지만 지어낸 질감은 벌하며, 학습 기반 LPIPS는 사람 판단에 가깝지만 참조 이미지가 필요하다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">세 계열이 보는 것</text>

            <rect x="24" y="30" width="200" height="86" fill="var(--warn)" opacity="0.12" stroke="var(--warn)" stroke-width="1.2"/>
            <text x="36" y="50" font-size="9" fill="var(--ink)">① 픽셀 — PSNR</text>
            <text x="36" y="68" font-size="8" fill="var(--ink-soft)">위치별 차이의 제곱 평균</text>
            <text x="36" y="84" font-size="8" fill="var(--warn)">✗ 노이즈와 밝기 이동을 구분 못 함</text>
            <text x="36" y="100" font-size="8" fill="var(--accent)">✓ 계산이 값싸고 명확하다</text>

            <rect x="240" y="30" width="200" height="86" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="252" y="50" font-size="9" fill="var(--ink)">② 구조 — SSIM</text>
            <text x="252" y="68" font-size="8" fill="var(--ink-soft)">휘도·대비를 빼고 무늬를 비교</text>
            <text x="252" y="84" font-size="8" fill="var(--accent)">✓ 밝기 변화에 관대하다</text>
            <text x="252" y="100" font-size="8" fill="var(--warn)">✗ 지어낸 질감은 여전히 벌한다</text>

            <rect x="456" y="30" width="218" height="86" fill="var(--accent)" opacity="0.14" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="468" y="50" font-size="9" fill="var(--ink)">③ 학습 — LPIPS</text>
            <text x="468" y="68" font-size="8" fill="var(--ink-soft)">사람 판단에 맞춘 특징 거리</text>
            <text x="468" y="84" font-size="8" fill="var(--accent)">✓ 사람 평가와 상관이 가장 높다</text>
            <text x="468" y="100" font-size="8" fill="var(--warn)">✗ 무겁고, 망에 따라 값이 달라진다</text>

            <line x1="24" y1="132" x2="674" y2="132" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="152" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">참조가 있는가 — 다른 축</text>

            <rect x="24" y="164" width="300" height="56" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="36" y="182" font-size="8.5" fill="var(--ink)">Full-Reference — 원본과 비교</text>
            <text x="36" y="198" font-size="8" fill="var(--ink-faint)">PSNR · SSIM · LPIPS</text>
            <text x="36" y="212" font-size="8" fill="var(--warn)">실사진 복원에는 원본이 없다</text>

            <rect x="340" y="164" width="334" height="56" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="352" y="182" font-size="8.5" fill="var(--accent)">No-Reference — 결과만 보고 판정</text>
            <text x="352" y="198" font-size="8" fill="var(--ink-faint)">NIQE · BRISQUE · MUSIQ · CLIP-IQA</text>
            <text x="352" y="212" font-size="8" fill="var(--ink-soft)">현장 배포에서 실제로 필요한 쪽이다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        지표를 고르는 축이 둘이다 — <strong>무엇을 보는가</strong>(픽셀·구조·학습된 지각)와
        <strong>원본이 있는가</strong>다.
        연구는 원본이 있는 상황을 전제하지만,
        <em>실제 배포에서는 원본이 없다.</em> 이 간극이 다음 절의 주제다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>원본이 없을 때</h2>
    <p>
      벤치마크는 고해상 원본을 갖고 있으므로 비교가 가능하다.
      그런데 <strong>실제 사용자의 흐린 사진</strong>에는 원본이 없다.
      "이 결과가 좋은가"를 판정할 기준이 없는 것이다.
    </p>
    <p>
      <strong>무참조 지표</strong>가 이 자리를 맡는다.
      원본 없이 이미지 하나만 보고 품질을 점수화한다.
    </p>
    <ul>
      <li><strong>통계 기반</strong> — 자연 이미지가 따르는 통계적 규칙성에서 얼마나 벗어났는지를 잰다. 학습 없이 동작하지만 왜곡 종류에 따라 편차가 크다.</li>
      <li><strong>학습 기반</strong> — 사람이 매긴 품질 점수 데이터로 회귀 모델을 학습한다. 최근에는 <a href="vision-transformer.html">트랜스포머</a>나 <a href="clip.html">CLIP</a> 특징을 쓰는 방식이 강하다.</li>
    </ul>
    <div class="note">
      <b>무참조 지표는 속기 쉽다.</b> "선명해 보이면 좋은 점수"를 주는 경향이 있어,
      <em>과하게 선명화된 결과</em>가 원본보다 높은 점수를 받는 일이 생긴다.
      복원 모델을 이 지표로 최적화하면 <a href="evaluation-benchmarks.html">굿하트 법칙</a> 그대로 —
      지표는 오르고 실제 품질은 떨어지는 결과가 나온다.
      그래서 무참조 지표는 <strong>최적화 목표가 아니라 모니터링용</strong>으로 쓰는 것이 안전하다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실무에서 무엇을 볼 것인가</h2>
    <p>
      정리하면 지표 선택은 <strong>무엇을 만들고 있는지</strong>에 달려 있다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>목적</th><th>주로 보는 것</th><th>이유</th></tr>
        </thead>
        <tbody>
          <tr><td>정확한 복원 (의료·계측)</td><td class="hi">PSNR · SSIM</td><td>지어내면 안 된다. 충실도가 전부</td></tr>
          <tr><td>감상용 화질 개선</td><td class="hi">LPIPS · 사람 평가</td><td>보기 좋으면 된다</td></tr>
          <tr><td>실사진 서비스</td><td class="hi">무참조 + 표본 육안</td><td>원본이 없다</td></tr>
          <tr><td>압축·전송</td><td>MS-SSIM · VMAF</td><td>비트레이트 대비 체감 품질</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      가장 중요한 조언은 단순하다. <strong>여러 지표를 함께 보고, 반드시 눈으로 확인한다.</strong>
      단일 숫자로 순위를 매기는 순간 그 숫자를 올리는 방향으로 모델이 기운다.
    </p>
    <p>
      그리고 <a href="super-resolution.html">초해상</a>에서 본
      <em>왜곡-지각 트레이드오프</em>를 기억해야 한다.
      PSNR 과 LPIPS 를 동시에 최적화할 수 없다는 것은 이론적으로 알려진 사실이다.
      두 지표가 반대로 움직이는 것은 <strong>모델이 잘못된 것이 아니라
      트레이드오프 곡선 위를 이동한 것</strong>일 수 있다.
    </p>
    <div class="note">
      <b>사람 평가도 만능이 아니다.</b> MOS 는 참가자·화면·조명·제시 순서에 따라 흔들린다.
      쌍 비교(둘 중 어느 쪽이 나은가)가 절대 점수보다 안정적이고,
      <a href="evaluation-benchmarks.html">평가 문서</a>에서 본 위치 편향 같은 것도 그대로 나타난다.
      결국 <em>측정 자체가 설계 대상</em>이라는 점은 이미지에서도 같다.
    </div>
  </section>
"""

READING = [
    "Wang et al., <em>Image Quality Assessment: From Error Visibility to Structural Similarity</em> (IEEE TIP 2004) — SSIM 원 논문.",
    "Wang et al., <em>Multiscale Structural Similarity for Image Quality Assessment</em> (Asilomar 2003) — MS-SSIM.",
    "Zhang et al., <em>The Unreasonable Effectiveness of Deep Features as a Perceptual Metric</em> (arXiv:1801.03924) — LPIPS.",
    "Blau &amp; Michaeli, <em>The Perception-Distortion Tradeoff</em> (arXiv:1711.06077) — 충실도와 지각을 동시에 못 올리는 이유.",
    "Mittal et al., <em>Making a Completely Blind Image Quality Analyzer</em> (IEEE SPL 2013) — NIQE. 무참조 통계 기반.",
    "Ke et al., <em>MUSIQ: Multi-scale Image Quality Transformer</em> (arXiv:2108.05997) — 학습 기반 무참조 지표.",
]

write(
    "image-quality-metrics.html",
    title="화질 평가 지표 — 무엇을 재고 있는가",
    eyebrow="Vision · Evaluation · 2004–2026",
    h1="화질 평가 지표",
    subtitle="무엇을 재고 있는가 — PSNR 이 사람 눈과 어긋나는 지점",
    dek=(
        "가우시안 노이즈를 넣은 이미지와 전체 밝기를 +10 옮긴 이미지의 "
        "<strong>PSNR 이 소수점까지 같을 수 있다</strong>. 체감은 전혀 다른데도. "
        "픽셀별 제곱오차는 <em>어떻게 틀렸는지</em>를 보지 않기 때문이다. "
        "그래서 구조를 따로 재고(SSIM), 결국 사람 판단을 학습하기에 이른다(LPIPS)."
    ),
    spec=[
        ("PSNR", "MSE 의 로그 — 충실도"),
        ("SSIM", "휘도·대비·구조 분리"),
        ("LPIPS", "사람 판단 학습 · 낮을수록 유사"),
        ("무참조", "원본 없이 판정"),
        ("원칙", "여러 지표 + 육안 확인"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

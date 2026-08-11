#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ef", panel="#e6e8e3", ink="#161a14", **{
    "ink-soft": "#4f5749", "ink-faint": "#7e8677", "rule": "#d1d5cd",
    "rule-strong": "#adb2a6", "accent": "#6b5a12", "accent-fill": "#eee8c8",
    "accent-line": "#96832c", "muted": "#83888c", "muted-fill": "#dee1df", "warn": "#a04a28",
})
DARK = dict(paper="#101210", panel="#191b16", ink="#e7eae2", **{
    "ink-soft": "#a5ac9c", "ink-faint": "#7a8171", "rule": "#22261e", "rule-strong": "#38402e",
    "accent": "#d4c05c", "accent-fill": "#282411", "accent-line": "#9a8a34",
    "muted": "#868d8a", "muted-fill": "#191f1c", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>센서가 보는 것은 사진이 아니다</h2>
    <p>
      카메라 센서가 내놓는 <strong>RAW</strong> 데이터는 우리가 아는 사진이 아니다.
      그것을 사진으로 만드는 과정이 <strong>ISP</strong>(Image Signal Processing)다.
    </p>
    <p>
      RAW 가 부족한 것부터 보자. 센서의 화소 하나는 <em>색을 하나만</em> 잰다.
      빨강·초록·파랑 필터를 격자로 배치하는데, 이것이 <strong>베이어 패턴</strong>이다.
    </p>
    <div class="eq">
      <span class="cap">화소당 색이 하나뿐이다</span>
      <div class="line">필터 배치&nbsp; R 25% · G 50% · B 25%&nbsp;&nbsp;// 초록이 두 배 — 사람 눈이 민감해서</div>
      <div class="line">&nbsp;</div>
      <div class="line">화소마다 3채널 중 <strong>1채널만 측정</strong>, 나머지 2채널은 없다</div>
      <div class="line">→ 최종 이미지의 <strong>약 66%가 추정값</strong>이다</div>
    </div>
    <p>
      비어 있는 채널을 이웃에서 추정하는 것이 <strong>디모자이킹</strong>이다.
      이름은 낯설지만, 결과물 픽셀의 3분의 2를 만들어내는 <em>가장 중요한 단계</em>다.
      경계에서 잘못 추정하면 <em>지퍼 무늬</em>나 색 번짐이 생긴다.
    </p>
    <div class="note">
      <b>비트 심도도 줄어든다.</b> RAW 는 보통 12~14비트(4,096~16,384단계)인데
      최종 출력은 8비트(256단계)다. 이 압축을 <strong>톤매핑</strong>이 담당하는데,
      <em>어느 밝기 구간을 살리고 어디를 버릴지</em>가 여기서 결정된다.
      역광 사진에서 하늘이 날아가거나 그림자가 뭉개지는 것은 대부분 이 단계의 선택이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>손으로 쌓아 올린 파이프라인</h2>
    <p>
      전통적 ISP 는 여러 블록을 <strong>순서대로</strong> 통과시킨다.
      각 블록은 하나의 문제를 담당하고, 대개 손으로 설계된 알고리즘이다.
    </p>
    <div class="eq">
      <span class="cap">전형적인 ISP 순서</span>
      <div class="line">RAW</div>
      <div class="line">&nbsp;↓ 블랙레벨·불량화소 보정</div>
      <div class="line">&nbsp;↓ <strong>노이즈 제거</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;← RAW 단계가 유리하다</div>
      <div class="line">&nbsp;↓ 화이트밸런스&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 조명 색을 상쇄</div>
      <div class="line">&nbsp;↓ <strong>디모자이킹</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 빈 채널을 채운다</div>
      <div class="line">&nbsp;↓ 색보정 행렬&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 센서 색공간 → 표준 색공간</div>
      <div class="line">&nbsp;↓ <strong>톤매핑·감마</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 12비트 → 8비트</div>
      <div class="line">&nbsp;↓ 샤프닝 · 압축</div>
      <div class="line">RGB / JPEG</div>
    </div>
    <p>
      순서가 중요하다. <a href="denoising.html">노이즈 제거</a>를 디모자이킹 <em>앞</em>에 두는 이유가 있다 —
      RAW 단계의 노이즈는 <strong>모델이 단순</strong>하다.
      포아송+가우시안 혼합이고 화소끼리 독립에 가깝다.
    </p>
    <p>
      디모자이킹을 지나면 이웃 화소를 섞으므로 <em>노이즈가 공간적으로 상관</em>을 갖게 되고,
      톤매핑을 지나면 밝기에 따라 비선형으로 증폭된다.
      <strong>뒤로 갈수록 노이즈의 성질이 복잡해진다</strong> — 그래서 앞에서 처리한다.
    </p>
    <div class="note">
      <b>블록이 서로를 방해한다.</b> 각 블록이 <em>자기 지표만</em> 최적화하기 때문이다.
      노이즈 제거를 강하게 걸면 디모자이킹이 쓸 세부가 사라지고,
      샤프닝을 강하게 걸면 앞서 지운 노이즈가 되살아난다.
      그래서 전통 ISP 튜닝은 <strong>블록 간 상호작용을 손으로 맞추는</strong> 일이 되고,
      기기마다 수개월이 걸리기도 한다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>통째로 학습시키면 어떨까</h2>
    <p>
      블록을 하나씩 신경망으로 바꾸는 대신,
      <strong>RAW 를 넣으면 RGB 가 나오는 하나의 망</strong>을 학습시키자는 접근이 나왔다.
    </p>
    <p>
      장점이 분명하다. 블록 간 상호작용을 손으로 맞출 필요가 없다 —
      <em>최종 화질을 목표로</em> 전체가 함께 최적화된다.
      <a href="detection-lineage.html">검출기</a>가 영역 제안·앵커·할당을 하나씩 학습으로 흡수한 것과 같은 흐름이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="전통 ISP와 학습 기반 ISP의 비교. 전통 방식은 블록마다 손으로 튜닝하고 각 블록이 자기 지표만 최적화하지만, 학습 기반은 RAW에서 RGB까지를 하나의 목표로 함께 최적화한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="isp-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="isp-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">전통 ISP — 블록마다 따로 튜닝</text>

            <rect x="24" y="30" width="46" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="47" y="46" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">RAW</text>
            <path d="M74 42 L88 42" stroke="var(--muted)" stroke-width="1.1" marker-end="url(#isp-m)"/>
            <rect x="92" y="30" width="52" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="118" y="46" text-anchor="middle" font-size="7" fill="var(--ink-soft)">노이즈</text>
            <path d="M148 42 L162 42" stroke="var(--muted)" stroke-width="1.1" marker-end="url(#isp-m)"/>
            <rect x="166" y="30" width="58" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="195" y="46" text-anchor="middle" font-size="7" fill="var(--ink-soft)">디모자이킹</text>
            <path d="M228 42 L242 42" stroke="var(--muted)" stroke-width="1.1" marker-end="url(#isp-m)"/>
            <rect x="246" y="30" width="52" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="272" y="46" text-anchor="middle" font-size="7" fill="var(--ink-soft)">톤매핑</text>
            <path d="M302 42 L316 42" stroke="var(--muted)" stroke-width="1.1" marker-end="url(#isp-m)"/>
            <rect x="320" y="30" width="46" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="343" y="46" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">RGB</text>

            <g font-size="7" fill="var(--warn)">
              <text x="118" y="68" text-anchor="middle">지표 A</text>
              <text x="195" y="68" text-anchor="middle">지표 B</text>
              <text x="272" y="68" text-anchor="middle">지표 C</text>
            </g>
            <text x="390" y="46" font-size="8" fill="var(--warn)">블록마다 다른 목표</text>
            <text x="390" y="60" font-size="8" fill="var(--ink-faint)">→ 서로를 방해할 수 있다</text>
            <text x="24" y="86" font-size="8" fill="var(--ink-faint)">해석 가능하고 디버깅이 쉽다 · 기기마다 수개월 튜닝</text>

            <line x1="24" y1="102" x2="674" y2="102" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="122" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">학습 기반 — 하나의 목표로 함께</text>

            <rect x="24" y="134" width="46" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="47" y="151" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">RAW</text>
            <path d="M74 147 L94 147" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#isp-a)"/>
            <rect x="98" y="130" width="200" height="34" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="198" y="145" text-anchor="middle" font-size="8.5" fill="var(--accent)">하나의 신경망</text>
            <text x="198" y="157" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">최종 화질을 목표로 전체 최적화</text>
            <path d="M302 147 L322 147" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#isp-a)"/>
            <rect x="326" y="134" width="46" height="26" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="349" y="151" text-anchor="middle" font-size="7.5" fill="var(--accent)">RGB</text>

            <text x="396" y="145" font-size="8" fill="var(--accent)">블록 간 상호작용을 손으로 안 맞춰도 된다</text>
            <text x="396" y="159" font-size="8" fill="var(--warn)">대신 중간을 들여다볼 수 없다</text>

            <line x1="24" y1="180" x2="674" y2="180" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="200" font-size="8.5" fill="var(--ink-soft)">현실적 절충 — <tspan fill="var(--accent)">블록을 남기되 각각을 학습으로</tspan> 대체하거나, 일부 구간만 통합한다</text>
            <text x="24" y="216" font-size="8" fill="var(--ink-faint)">전면 교체는 검증·디버깅 부담이 커서, 단계적으로 넘어가는 경우가 많다</text>
            <text x="24" y="230" font-size="8" fill="var(--warn)">그리고 온디바이스에서는 <tspan fill="var(--warn)">전력·지연 예산</tspan>이 통합 여부를 실질적으로 결정한다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        학습 기반이 이론적으로 우월해 보이지만 <strong>해석 가능성을 잃는다</strong>.
        전통 ISP 는 색이 이상하면 어느 블록인지 짚을 수 있지만,
        통합 망은 <em>어디가 문제인지 알 수 없다</em>.
        그래서 실무에서는 블록 구조를 남기고 개별 블록만 학습으로 바꾸는 절충이 흔하다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>학습 데이터를 어떻게 만드나</h2>
    <p>
      학습 기반 ISP 의 실질적 난관은 <strong>정답 데이터</strong>다.
      RAW 입력에 대응하는 <em>이상적인 RGB</em>가 있어야 하는데, 그것이 무엇인지가 불분명하다.
    </p>
    <ul>
      <li><strong>기존 ISP 출력을 정답으로</strong> — 학습은 쉽지만 기존 ISP 를 넘어설 수 없다</li>
      <li><strong>전문가 보정 결과를 정답으로</strong> — 품질은 높지만 비싸고 주관적이다</li>
      <li><strong>여러 장 합성 결과를 정답으로</strong> — 장노출·다중 노출로 만든 깨끗한 이미지를 목표로 삼는다</li>
    </ul>
    <p>
      세 번째가 야간 촬영 연구에서 자주 쓰인다.
      짧은 노출 RAW 를 입력으로, <em>같은 장면의 긴 노출 결과</em>를 정답으로 두면
      "어두운 곳에서 밝고 깨끗하게"라는 목표가 데이터로 정의된다.
    </p>
    <div class="note">
      <b>목표가 미학적이라는 문제가 남는다.</b>
      <a href="image-quality-metrics.html">화질 평가</a>에서 봤듯 PSNR 이 사람 눈과 어긋나고,
      ISP 는 특히 <em>"어떤 색감이 좋은가"</em> 같은 취향이 개입한다.
      제조사마다 색이 다른 것은 기술 격차가 아니라 <strong>선택</strong>인 경우가 많다.
      그래서 학습 목표를 정하는 일 자체가 제품 결정이 된다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>ISP 와 인식 모델 사이</h2>
    <p>
      마지막으로 이 문서를 검출·인식과 이어 두자.
      <strong>ISP 는 사람이 보기 좋으라고 만들어졌다.</strong> 그런데 그 출력을 모델이 받는다.
    </p>
    <p>
      둘의 목표가 어긋날 수 있다.
      톤매핑이 어두운 영역을 눌러 보기 좋게 만들면 <em>그 영역의 물체 정보가 사라지고</em>,
      샤프닝이 경계를 강조하면 <a href="denoising.html">노이즈</a>도 함께 강조돼
      검출기가 헛것을 본다.
    </p>
    <div class="eq">
      <span class="cap">그래서 나오는 선택지</span>
      <div class="line">① <strong>RAW 를 모델에 직접</strong> 넣는다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;정보 손실이 없다 · 데이터·전처리를 새로 맞춰야 한다</div>
      <div class="line">&nbsp;</div>
      <div class="line">② <strong>인식 성능을 목표로 ISP 를 학습</strong>시킨다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;검출 손실을 ISP 까지 역전파 — 사람 눈에는 이상해 보일 수 있다</div>
      <div class="line">&nbsp;</div>
      <div class="line">③ <strong>두 경로를 분리</strong>한다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;표시용 ISP 와 인식용 ISP 를 따로 — 비용이 두 배</div>
    </div>
    <p>
      ②가 개념적으로 흥미롭다. ISP 를 <em>인식 파이프라인의 일부</em>로 보고
      최종 과제 손실로 함께 학습하는 것이다.
      결과 이미지가 사람 눈에 부자연스러워도 <strong>검출 성능이 오르면 성공</strong>이라는 관점인데,
      표시용으로는 쓸 수 없으므로 ③과 묶이는 경우가 많다.
    </p>
    <div class="note">
      <b>온디바이스에서는 예산이 결정한다.</b> ISP 는 이미 전용 하드웨어로 처리되고 있어
      <em>사실상 공짜</em>다. 이것을 신경망으로 바꾸면
      <a href="mobile-runtime.html">NPU 예산</a>을 인식 모델과 나눠 써야 한다.
      화질이 조금 나아져도 <strong>검출 모델을 작게 만들어야 한다면</strong> 손해일 수 있다.
      <a href="efficient-backbone.html">경량화</a>와 같은 저울 위에 놓인 문제다.
    </div>
    <p>
      정리하면 ISP 는 <em>"센서 값을 무엇으로 만들 것인가"</em>를 정하는 단계이고,
      그 답이 <strong>사람 눈이냐 모델이냐</strong>에 따라 최적해가 달라진다.
      두 목표가 같다고 가정하는 것이 흔한 실수이고,
      실제로는 어긋나는 지점이 계속 나온다.
    </p>
  </section>
"""

READING = [
    "Chen et al., <em>Learning to See in the Dark</em> (arXiv:1805.01934) — 짧은 노출 RAW → 긴 노출 RGB, 학습 기반 ISP 의 대표 사례.",
    "Schwartz et al., <em>DeepISP: Towards Learning an End-to-End Image Processing Pipeline</em> (arXiv:1801.06724) — 파이프라인 전체를 학습으로.",
    "Ignatov et al., <em>Replacing Mobile Camera ISP with a Single Deep Learning Model</em> (arXiv:2002.05509) — 모바일 ISP 대체 시도와 한계.",
    "Brooks et al., <em>Unprocessing Images for Learned Raw Denoising</em> (arXiv:1811.11127) — RGB 를 RAW 로 되돌려 학습 데이터를 만드는 방법.",
    "Buckler et al., <em>Reconfiguring the Imaging Pipeline for Computer Vision</em> (arXiv:1705.04352) — 인식용 ISP 는 무엇이 달라야 하는가.",
]

write(
    "isp-pipeline.html",
    title="ISP — 센서 값을 사진으로 만드는 일",
    eyebrow="Vision · Imaging Pipeline · 2018–2026",
    h1="ISP",
    subtitle="센서 값을 사진으로 만드는 일 — 사람 눈과 모델의 목표는 다르다",
    dek=(
        "센서 화소는 <strong>색을 하나만</strong> 잰다. "
        "최종 이미지의 약 66%는 이웃에서 추정한 값이고, "
        "12비트가 8비트로 눌리는 과정에서 무엇을 살릴지가 결정된다. "
        "이 모든 것을 하는 ISP 는 <em>사람이 보기 좋으라고</em> 만들어졌는데, "
        "그 출력을 인식 모델이 받는다."
    ),
    spec=[
        ("RAW 의 결손", "화소당 1채널 · 66% 추정"),
        ("비트", "12~14 → 8"),
        ("순서 원칙", "노이즈는 RAW 단계에서"),
        ("학습 기반", "해석 가능성을 내준다"),
        ("어긋남", "사람 눈 ↔ 인식 성능"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

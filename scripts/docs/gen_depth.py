#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff1f1", panel="#e4e8e8", ink="#131a1a", **{
    "ink-soft": "#4a5757", "ink-faint": "#798686", "rule": "#ccd3d3",
    "rule-strong": "#a9b1b1", "accent": "#155e63", "accent-fill": "#d6eaec",
    "accent-line": "#2f8890", "muted": "#83888c", "muted-fill": "#dee1e1", "warn": "#a34a28",
})
DARK = dict(paper="#0e1213", panel="#161b1c", ink="#e3eaea", **{
    "ink-soft": "#a0abab", "ink-faint": "#6f7a7a", "rule": "#202726", "rule-strong": "#364040",
    "accent": "#4cc2ca", "accent-fill": "#0d2a2c", "accent-line": "#2d8890",
    "muted": "#868d8d", "muted-fill": "#191f1f", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>사진은 3차원을 2차원으로 눌러 놓은 것</h2>
    <p>
      카메라는 <strong>깊이를 버린다</strong>. 3차원 공간의 점이 2차원 평면에 찍히면서
      "카메라에서 얼마나 멀리 있는가"라는 정보가 사라진다.
    </p>
    <p>
      한 장의 사진만 보면 <em>같은 픽셀을 만들어내는 3D 배치가 무수히 많다</em>.
      작은 물체가 가까이 있는 것과 큰 물체가 멀리 있는 것을 구분할 수 없다.
      <a href="super-resolution.html">초해상</a>과 같은 <strong>불량조건 역문제</strong>다 —
      답이 하나로 정해지지 않는다.
    </p>
    <p>
      그래서 깊이를 얻는 길은 <em>정보를 더 넣거나, 가정을 넣거나</em> 둘 중 하나다.
    </p>
    <div class="eq">
      <span class="cap">깊이를 얻는 세 갈래</span>
      <div class="line"><strong>스테레오</strong>&nbsp;&nbsp; 카메라 두 대 — 시차로 삼각측량</div>
      <div class="line"><strong>능동 센서</strong> ToF·구조광 — 빛을 쏴서 직접 잰다</div>
      <div class="line"><strong>단안 추정</strong> 한 장에서 <em>학습된 사전지식</em>으로 추측</div>
    </div>
    <p>
      앞의 둘은 물리적으로 측정하고, 마지막은 <strong>추론한다</strong>.
      이 차이가 정확도·비용·실패 방식을 전부 가른다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>스테레오 — 시차가 곧 거리다</h2>
    <p>
      두 눈이 깊이를 느끼는 원리와 같다. 좌우 카메라에서 같은 점이
      <em>서로 다른 위치</em>에 찍히고, 그 차이(시차)가 거리에 반비례한다.
    </p>
    <div class="eq">
      <span class="cap">삼각측량 — 관계는 단순하다</span>
      <div class="line">Z = f · B / d</div>
      <div class="line">&nbsp;</div>
      <div class="line">Z = 거리,&nbsp; f = 초점거리(px),&nbsp; B = 베이스라인(m),&nbsp; d = 시차(px)</div>
      <div class="line">// 가까울수록 시차가 크다 — 반비례 관계</div>
    </div>
    <p>
      이 <strong>반비례</strong>가 스테레오의 성격을 전부 결정한다.
      실제 값을 넣어 보면 분명해진다.
    </p>
    <div class="eq">
      <span class="cap">f=700px · B=12cm — 시차 1px 오차의 대가</span>
      <div class="line">시차(px)&nbsp;&nbsp;&nbsp; 거리(m)&nbsp;&nbsp;&nbsp; 1px 오차 시 거리 오차</div>
      <div class="line">&nbsp;&nbsp; 64&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1.31&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0.02 m</div>
      <div class="line">&nbsp;&nbsp; 16&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 5.25&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0.35 m</div>
      <div class="line">&nbsp;&nbsp;&nbsp; 4&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 21.00&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>7.00 m</strong></div>
      <div class="line">&nbsp;&nbsp;&nbsp; 2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 42.00&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>42.00 m</strong></div>
    </div>
    <p>
      같은 1픽셀 오차가 가까이서는 <strong>2cm</strong>, 멀리서는 <strong>42m</strong>다.
      <em>거리 오차가 거리의 제곱에 비례</em>하기 때문이다.
      스테레오가 근거리에 강하고 원거리에 약한 구조적 이유가 여기 있다.
    </p>
    <div class="note">
      <b>베이스라인을 늘리면 멀리 볼 수 있다.</b> <code>Z = fB/d</code> 에서 <code>B</code>가 커지면
      같은 거리에서 시차가 커지므로 정밀도가 오른다.
      그래서 자율주행 스테레오는 카메라를 멀리 떼어 놓는다.
      대신 <em>겹치는 시야가 줄고</em> 가까운 물체가 한쪽에만 보이는 문제가 생긴다 —
      공짜가 아니다.
    </div>
    <p>
      실제 어려움은 공식이 아니라 <strong>대응점 찾기</strong>에 있다.
      좌우 이미지에서 같은 점을 짝지어야 하는데,
      <a href="local-features.html">지역 특징 매칭</a>에서 본 문제가 그대로 나온다 —
      질감 없는 벽면, 반복 무늬, 한쪽에만 보이는 영역(가림)에서 실패한다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>단안 추정 — 스케일을 알 수 없다</h2>
    <p>
      카메라 한 대로 깊이를 추정하는 것은 <em>원리적으로 불가능</em>한 일을
      <strong>학습된 사전지식</strong>으로 푸는 것이다.
    </p>
    <p>
      모델이 쓰는 단서는 사람이 쓰는 것과 비슷하다 —
      물체의 통상적 크기, 원근에 따른 수렴, 가림 관계, 텍스처 밀도, 그림자.
      "사람 키는 대략 170cm"라는 <em>세계에 대한 지식</em>이 깊이 추정에 들어간다.
    </p>
    <p>
      그런데 결정적 한계가 있다. <strong>절대 스케일을 알 수 없다.</strong>
    </p>
    <div class="eq">
      <span class="cap">스케일 모호성 — 같은 이미지를 만드는 배치가 여럿</span>
      <div class="line">실물 크기 1m 물체가 2m 앞에 있는 것</div>
      <div class="line">실물 크기 2m 물체가 4m 앞에 있는 것</div>
      <div class="line">실물 크기 10m 물체가 20m 앞에 있는 것</div>
      <div class="line">&nbsp;</div>
      <div class="line">→ <strong>픽셀로는 완전히 같다</strong></div>
    </div>
    <p>
      그래서 단안 모델의 출력은 대개 <em>상대 깊이</em>다 —
      "A가 B보다 가깝다"는 알지만 "A가 3.2m"는 모른다.
      미터 단위 값이 필요하면 <strong>다른 정보로 스케일을 고정</strong>해야 한다 —
      카메라 높이, 알려진 물체 크기, IMU, 또는 학습 데이터의 카메라 설정.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="깊이 추정 세 방식의 비교. 스테레오는 시차로 삼각측량해 절대 거리를 얻지만 원거리에서 오차가 제곱으로 커지고, 능동 센서는 정확하지만 범위와 전력에 제약이 있으며, 단안 추정은 어디서나 쓰이지만 절대 스케일을 알 수 없다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">스테레오 — 시차로 잰다</text>

            <circle cx="50" cy="46" r="7" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <circle cx="50" cy="78" r="7" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <line x1="50" y1="53" x2="50" y2="71" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="20" y="66" font-size="7.5" fill="var(--ink-faint)">B</text>

            <circle cx="180" cy="62" r="6" fill="var(--accent)" opacity="0.6"/>
            <line x1="57" y1="46" x2="176" y2="60" stroke="var(--accent-line)" stroke-width="1"/>
            <line x1="57" y1="78" x2="176" y2="64" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="196" y="66" font-size="8" fill="var(--ink-soft)">Z = f·B / d</text>

            <text x="24" y="104" font-size="8" fill="var(--accent)">✓ 절대 거리를 얻는다</text>
            <text x="24" y="118" font-size="8" fill="var(--warn)">✗ 오차가 거리의 제곱에 비례</text>
            <text x="24" y="132" font-size="8" fill="var(--warn)">✗ 질감 없는 면에서 대응 실패</text>

            <line x1="256" y1="26" x2="256" y2="150" stroke="var(--rule)" stroke-width="1"/>

            <text x="280" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">능동 센서 — 빛을 쏜다</text>
            <rect x="280" y="40" width="26" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <g stroke="var(--accent-line)" stroke-width="1.1">
              <line x1="308" y1="46" x2="380" y2="40"/>
              <line x1="308" y1="54" x2="380" y2="60"/>
            </g>
            <rect x="384" y="34" width="10" height="32" fill="var(--accent)" opacity="0.5"/>
            <text x="404" y="54" font-size="8" fill="var(--ink-soft)">왕복 시간 → 거리</text>

            <text x="280" y="88" font-size="8" fill="var(--accent)">✓ 질감과 무관하게 정확</text>
            <text x="280" y="102" font-size="8" fill="var(--warn)">✗ 범위·전력·햇빛에 제약</text>
            <text x="280" y="116" font-size="8" fill="var(--warn)">✗ 해상도가 낮고 비싸다</text>
            <text x="280" y="132" font-size="8" fill="var(--ink-faint)">유리·거울·검은 표면에 약함</text>

            <line x1="24" y1="164" x2="674" y2="164" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="184" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">단안 추정 — 학습된 사전지식으로</text>

            <rect x="24" y="196" width="60" height="30" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="54" y="215" text-anchor="middle" font-size="8" fill="var(--ink-soft)">사진 1장</text>
            <text x="94" y="215" font-size="9" fill="var(--accent-line)">→</text>
            <rect x="112" y="196" width="70" height="30" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="147" y="215" text-anchor="middle" font-size="8" fill="var(--accent)">상대 깊이</text>

            <text x="200" y="208" font-size="8" fill="var(--accent)">✓ 카메라 한 대 · 어디서나</text>
            <text x="200" y="222" font-size="8" fill="var(--warn)">✗ 절대 스케일을 모른다 — 미터 값이 필요하면 따로 고정해야</text>

            <text x="480" y="192" font-size="8" fill="var(--ink-faint)">실무에서는 섞어 쓴다:</text>
            <text x="480" y="206" font-size="8" fill="var(--ink-faint)">스테레오/센서로 스케일을 잡고</text>
            <text x="480" y="220" font-size="8" fill="var(--ink-faint)">단안으로 조밀하게 채운다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        세 방식은 <strong>실패하는 방식이 다르다</strong>.
        스테레오는 질감 없는 곳에서, 능동 센서는 햇빛·유리에서,
        단안은 <em>본 적 없는 장면</em>에서 무너진다.
        그래서 하나를 고르기보다 <em>서로의 약점을 덮도록</em> 조합하는 것이 실무의 답이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>정답 없이 배우기</h2>
    <p>
      단안 모델을 학습시키려면 <em>깊이 정답</em>이 필요한데, 이것을 모으기가 어렵다.
      LiDAR 로 재면 정확하지만 비싸고 희소하며, 실내 센서는 범위가 짧다.
    </p>
    <p>
      돌파구는 <strong>자기지도</strong>였다. 정답 대신 <em>기하학적 제약</em>을 손실로 쓴다.
    </p>
    <div class="eq">
      <span class="cap">뷰 합성을 손실로 — 정답 깊이가 필요 없다</span>
      <div class="line">1) 프레임 A 의 깊이를 예측한다</div>
      <div class="line">2) 예측 깊이 + 카메라 이동으로 <strong>프레임 B 를 재구성</strong>한다</div>
      <div class="line">3) 재구성한 B 와 실제 B 의 차이를 손실로 쓴다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 깊이가 맞아야 재구성이 맞는다 → 깊이가 간접적으로 학습된다</div>
    </div>
    <p>
      영상만 있으면 학습이 된다는 뜻이다.
      스테레오 쌍을 쓰면 카메라 이동이 알려져 있어 <em>절대 스케일까지</em> 배울 수 있고,
      단안 영상만 쓰면 카메라 이동도 함께 추정해야 해 스케일이 다시 모호해진다.
    </p>
    <div class="note">
      <b>움직이는 물체가 이 가정을 깬다.</b> 뷰 합성은 <em>장면이 정지해 있고 카메라만 움직인다</em>고 가정한다.
      카메라와 같은 속도로 움직이는 차는 <strong>무한히 멀다고 학습</strong>된다 —
      상대 위치가 안 변하니 시차가 0인 것처럼 보이기 때문이다.
      자동 마스킹으로 그런 픽셀을 손실에서 빼는 처방이 표준이 됐다.
    </div>
    <p>
      최근에는 <strong>대규모 혼합 학습</strong>이 판을 바꿨다.
      서로 다른 데이터셋은 스케일과 단위가 제각각인데,
      <em>스케일·이동에 불변인 손실</em>을 쓰면 함께 학습할 수 있다.
      수백만 장을 섞어 학습한 모델이 <strong>처음 보는 장면에도 일반화</strong>하는 수준에 이르렀다 —
      <a href="self-supervised-learning.html">DINOv2</a> 같은 시각 기반 모델을 백본으로 쓰는 것도 같은 흐름이다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>무엇을 재고 어디에 쓰나</h2>
    <p>
      평가 지표부터 짚자. 상대 깊이 모델을 절대 지표로 재면 안 된다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>지표</th><th>보는 것</th><th>주의</th></tr>
        </thead>
        <tbody>
          <tr><td>AbsRel</td><td>상대 오차의 평균</td><td class="hi">스케일 정렬 후인지 확인</td></tr>
          <tr><td>RMSE</td><td>절대 오차</td><td>먼 곳이 지배한다</td></tr>
          <tr><td>δ&lt;1.25</td><td class="hi">비율이 1.25 안에 든 픽셀 비율</td><td>직관적이라 자주 쓰인다</td></tr>
          <tr><td>경계 정확도</td><td>물체 경계에서의 깊이 불연속</td><td class="hi">평균 지표가 못 보는 것</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 실무에서 중요하다. 평균 오차가 작아도
      <em>물체 경계가 뭉개지면</em> 쓸모가 떨어진다.
      배경 제거나 로봇 파지처럼 경계가 곧 결과인 응용에서는
      <a href="image-quality-metrics.html">평균 지표가 체감과 어긋나는</a> 상황이 그대로 반복된다.
    </p>
    <p>
      쓰임을 보면 요구가 갈린다.
    </p>
    <ul>
      <li><strong>사진 효과(보케)</strong> — 상대 깊이면 충분하고 경계가 중요하다</li>
      <li><strong>AR 오클루전</strong> — 실시간성이 우선. 정확도는 적당해도 된다</li>
      <li><strong>로봇 파지·측정</strong> — <em>절대 스케일이 필수</em>. 능동 센서를 쓴다</li>
      <li><strong>자율주행</strong> — 원거리 정밀도가 관건. 스테레오+LiDAR 조합</li>
    </ul>
    <div class="note">
      <b>온디바이스에서는 또 다른 저울이 있다.</b>
      깊이 추정은 <a href="segmentation.html">분할</a>처럼 <em>입력과 같은 크기의 출력</em>을 내므로
      연산량이 크다. <a href="mobile-runtime.html">NPU 예산</a>을 검출·인식 모델과 나눠 써야 하고,
      해상도를 낮추면 <em>경계가 먼저 뭉개진다</em>.
      <a href="efficient-backbone.html">경량화</a>와 같은 선택지 위에 놓인다.
    </div>
    <p>
      정리하면 깊이 추정은 <em>"카메라가 버린 정보를 되찾는"</em> 일이다.
      물리적으로 다시 재거나(스테레오·센서), 학습된 지식으로 추측하거나(단안).
      전자는 정확하지만 조건이 붙고, 후자는 어디서나 되지만 <strong>스케일을 모른다</strong>.
      실무의 답은 대개 둘을 섞는 것이고, <em>어느 쪽 실패를 감당할 수 있는지</em>가 선택을 정한다.
    </p>
  </section>
"""

READING = [
    "Eigen et al., <em>Depth Map Prediction from a Single Image using a Multi-Scale Deep Network</em> (arXiv:1406.2283) — 단안 깊이 추정의 출발점.",
    "Godard et al., <em>Digging Into Self-Supervised Monocular Depth Estimation</em> (arXiv:1806.01260) — Monodepth2. 자동 마스킹과 자기지도 손실.",
    "Ranftl et al., <em>Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer</em> (arXiv:1907.01341) — MiDaS. 스케일 불변 손실로 데이터셋 혼합.",
    "Yang et al., <em>Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data</em> (arXiv:2401.10891) — 대규모 학습으로 일반화.",
    "Chang &amp; Chen, <em>Pyramid Stereo Matching Network</em> (arXiv:1803.08669) — 학습 기반 스테레오 매칭.",
    "Zhou et al., <em>Unsupervised Learning of Depth and Ego-Motion from Video</em> (arXiv:1704.07813) — 뷰 합성을 손실로 쓰는 원형.",
]

write(
    "depth-estimation.html",
    title="깊이 추정 — 카메라가 버린 정보를 되찾기",
    eyebrow="Vision · 3D Perception · 2014–2026",
    h1="깊이 추정",
    subtitle="카메라가 버린 정보를 되찾기 — 다시 재거나, 추측하거나",
    dek=(
        "사진은 3차원을 2차원으로 눌러 <strong>깊이를 버린다</strong>. "
        "같은 픽셀을 만드는 3D 배치가 무수히 많아 한 장으로는 원리적으로 풀 수 없다. "
        "그래서 정보를 더 넣거나(스테레오·센서) 가정을 넣는다(학습). "
        "전자는 정확하지만 조건이 붙고, 후자는 어디서나 되지만 <em>절대 스케일을 모른다</em>."
    ),
    spec=[
        ("문제 성격", "불량조건 역문제"),
        ("스테레오", "Z = f·B / d"),
        ("오차 특성", "거리의 제곱에 비례"),
        ("단안 한계", "절대 스케일 모호"),
        ("학습 방법", "뷰 합성 자기지도"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

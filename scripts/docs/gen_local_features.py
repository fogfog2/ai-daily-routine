#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ee", panel="#e7e6e1", ink="#181712", **{
    "ink-soft": "#545046", "ink-faint": "#837e72", "rule": "#d3d1ca",
    "rule-strong": "#afaca2", "accent": "#7a4a1c", "accent-fill": "#f0e2d0",
    "accent-line": "#a67338", "muted": "#82868c", "muted-fill": "#dee0e2", "warn": "#8a5a12",
})
DARK = dict(paper="#12110e", panel="#1a1915", ink="#eae8e2", **{
    "ink-soft": "#aaa69a", "ink-faint": "#7c776c", "rule": "#25231d", "rule-strong": "#3b382f",
    "accent": "#dda06a", "accent-fill": "#2e2114", "accent-line": "#a8763e",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#d9a441",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>전체를 하나의 벡터로 만들면 잃는 것</h2>
    <p>
      <a href="metric-learning.html">메트릭 러닝</a>은 이미지 한 장을 벡터 하나로 만든다.
      "이 두 사진이 같은 물건인가"에는 잘 답하지만, 답하지 못하는 것이 있다 —
      <strong>어느 부분이 어느 부분에 대응하는가.</strong>
    </p>
    <p>
      대응 관계가 필요한 일들이 있다.
    </p>
    <ul>
      <li><strong>파노라마 합성</strong> — 두 사진을 이어 붙이려면 겹치는 지점을 정확히 알아야 한다</li>
      <li><strong><a href="depth-estimation.html">3D 복원</a>·SLAM</strong> — 여러 뷰의 같은 점을 찾아야 카메라 위치를 푼다</li>
      <li><strong>정밀 검증</strong> — 비슷한 두 제품 중 어느 부위가 다른지 짚어야 한다</li>
    </ul>
    <p>
      전역 벡터는 <em>"닮았다"</em>까지만 말한다.
      <strong>지역 특징</strong>은 이미지에서 <em>점들</em>을 뽑고 각 점에 서술자를 붙여,
      점 대 점 대응을 만든다. 뷰가 크게 달라도 <em>같은 물리적 지점</em>을 짚을 수 있다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>세 단계 — 검출·서술·매칭</h2>
    <p>
      고전적 파이프라인은 세 단계로 나뉘고, 딥러닝 이후에도 이 골격은 유지된다.
    </p>
    <div class="eq">
      <span class="cap">지역 특징 파이프라인</span>
      <div class="line">① <strong>검출</strong>&nbsp; 어디를 볼 것인가 — 반복 가능한 점을 고른다</div>
      <div class="line">② <strong>서술</strong>&nbsp; 그 주변을 벡터로 — 뷰가 변해도 비슷해야 한다</div>
      <div class="line">③ <strong>매칭</strong>&nbsp; 두 집합의 서술자를 짝짓는다</div>
    </div>
    <p>
      ①에서 <strong>반복 가능성</strong>이 핵심 요구다.
      같은 장면을 다른 각도·조명에서 찍었을 때 <em>같은 지점이 다시 뽑혀야</em> 한다.
      그래서 평평한 면이나 단순한 모서리는 나쁜 후보다 —
      평평한 곳은 어디나 비슷하고, 직선 모서리는 <em>선을 따라 미끄러진다</em>.
      두 방향 모두 변화가 큰 <strong>코너</strong>가 좋은 후보인 이유다.
    </p>
    <p>
      ②의 요구는 더 까다롭다. <em>같은 지점이면 비슷하고 다른 지점이면 달라야</em> 한다.
      <a href="metric-learning.html">메트릭 러닝</a>의 요구와 정확히 같은 형태인데,
      대상이 이미지 전체가 아니라 <strong>작은 패치</strong>라는 점만 다르다.
    </p>
    <div class="note">
      <b>SIFT 가 오래 표준이었던 이유.</b> 스케일 공간에서 극값을 찾아 크기 변화에 대응하고,
      주변 그래디언트의 주 방향으로 패치를 회전시켜 <em>회전에 불변</em>하게 만들고,
      그래디언트 방향 히스토그램으로 서술했다.
      학습 없이도 이 정도 불변성을 확보한 설계라, 딥러닝 이후에도 한동안 기준선으로 남았다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>매칭이 실제로 어려운 이유</h2>
    <p>
      서술자가 좋아도 매칭은 쉽지 않다.
      가장 가까운 것끼리 짝지으면 <strong>틀린 짝이 대량으로</strong> 생긴다.
    </p>
    <p>
      이유는 장면에 <em>반복되는 무늬</em>가 많기 때문이다.
      건물의 창문들, 타일 바닥, 나뭇잎 — 서술자만 보면 구분이 안 된다.
      한 점에 대해 비슷한 후보가 여럿이면, 최근접 하나를 고르는 것은 도박에 가깝다.
    </p>
    <div class="eq">
      <span class="cap">비율 검사 — 애매하면 버린다</span>
      <div class="line">d₁ = 가장 가까운 서술자까지의 거리</div>
      <div class="line">d₂ = 두 번째로 가까운 것까지의 거리</div>
      <div class="line">&nbsp;</div>
      <div class="line">d₁ / d₂ &lt; 0.8 이면 채택, 아니면 <strong>버린다</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 1등과 2등이 비슷하면 = 구별 못 하는 것 = 믿을 수 없다</div>
    </div>
    <p>
      절대 거리가 아니라 <strong>1등과 2등의 격차</strong>를 본다는 것이 요령이다.
      가까워도 2등이 바짝 붙어 있으면 버린다.
      <em>모호한 것을 조용히 버리는 것</em>이 틀린 짝을 남기는 것보다 낫다는 판단이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 234" role="img" aria-label="지역 특징 매칭의 어려움과 해법. 최근접만 보면 반복되는 무늬에서 틀린 짝이 생기지만, 1등과 2등의 거리 비율을 보면 모호한 것을 걸러낼 수 있고, 기하 검증으로 일관된 대응만 남긴다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">반복 무늬 — 최근접만 보면 틀린다</text>

            <rect x="24" y="30" width="130" height="86" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g stroke="var(--rule-strong)" stroke-width="0.8" fill="none">
              <rect x="38" y="44" width="22" height="22"/><rect x="70" y="44" width="22" height="22"/><rect x="102" y="44" width="22" height="22"/>
              <rect x="38" y="76" width="22" height="22"/><rect x="70" y="76" width="22" height="22"/><rect x="102" y="76" width="22" height="22"/>
            </g>
            <circle cx="81" cy="55" r="4" fill="var(--accent)"/>
            <text x="24" y="132" font-size="8" fill="var(--ink-faint)">창문이 다 비슷하게 생겼다</text>

            <rect x="186" y="30" width="130" height="86" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g stroke="var(--rule-strong)" stroke-width="0.8" fill="none">
              <rect x="200" y="44" width="22" height="22"/><rect x="232" y="44" width="22" height="22"/><rect x="264" y="44" width="22" height="22"/>
              <rect x="200" y="76" width="22" height="22"/><rect x="232" y="76" width="22" height="22"/><rect x="264" y="76" width="22" height="22"/>
            </g>
            <circle cx="243" cy="55" r="4" fill="var(--accent)"/>
            <circle cx="211" cy="55" r="4" fill="var(--warn)" opacity="0.7"/>
            <circle cx="275" cy="55" r="4" fill="var(--warn)" opacity="0.7"/>

            <path d="M85 55 L239 55" stroke="var(--accent-line)" stroke-width="1.3"/>
            <path d="M85 58 L207 57" stroke="var(--warn)" stroke-width="1" stroke-dasharray="3 2"/>
            <text x="186" y="132" font-size="8" fill="var(--warn)">후보가 여럿 — 1등을 믿을 수 없다</text>

            <line x1="348" y1="26" x2="348" y2="126" stroke="var(--rule)" stroke-width="1"/>

            <text x="372" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">비율 검사</text>
            <text x="372" y="42" font-size="8.5" fill="var(--ink-soft)">d₁/d₂ &lt; 0.8 이면 채택</text>
            <rect x="372" y="52" width="140" height="14" fill="var(--accent)" opacity="0.5"/>
            <text x="520" y="63" font-size="8" fill="var(--accent)">d₁ 확실히 가까움 ✓</text>
            <rect x="372" y="72" width="140" height="14" fill="var(--warn)" opacity="0.3"/>
            <rect x="372" y="90" width="132" height="14" fill="var(--warn)" opacity="0.3"/>
            <text x="520" y="90" font-size="8" fill="var(--warn)">1·2등이 비슷 → 버린다</text>

            <line x1="24" y1="146" x2="674" y2="146" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="166" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">기하 검증 — 남은 것도 다 믿지 않는다</text>
            <text x="24" y="188" font-size="8.5" fill="var(--ink-soft)">"올바른 대응들은 <tspan fill="var(--accent)">하나의 기하 변환</tspan>을 공유한다"</text>
            <text x="24" y="204" font-size="8" fill="var(--ink-faint)">RANSAC — 무작위로 몇 개 골라 변환을 세우고, 그 변환에 동의하는 짝이 몇인지 센다</text>
            <text x="24" y="218" font-size="8" fill="var(--ink-faint)">가장 많은 동의를 얻은 변환을 채택하고, 동의하지 않는 짝은 버린다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        매칭은 <strong>두 겹으로 거른다</strong>.
        서술자 수준에서 모호한 것을 버리고(비율 검사),
        남은 것도 <em>전체가 일관된 기하를 이루는지</em> 확인한다(RANSAC).
        개별 판단은 틀릴 수 있지만 <strong>다수가 같은 변환에 동의하기는 어렵다</strong>는 원리다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>학습으로 넘어가기</h2>
    <p>
      세 단계를 각각 학습으로 바꾸려는 시도가 이어졌는데, 순서가 흥미롭다.
    </p>
    <p>
      <strong>서술이 먼저였다.</strong> 패치를 벡터로 만드는 일은 지도학습이 자연스럽다 —
      같은 지점의 패치 쌍을 양성으로 두면 <a href="metric-learning.html">메트릭 러닝</a> 그대로다.
      학습된 서술자가 SIFT 를 넘어서는 데는 오래 걸리지 않았다.
    </p>
    <p>
      <strong>검출이 어려웠다.</strong> "좋은 점"의 정답 라벨이 없기 때문이다.
      사람이 "여기가 반복 가능한 지점"이라고 찍어 줄 수가 없다.
      SuperPoint 는 이것을 <em>자기지도</em>로 풀었다 —
      합성 도형으로 코너 검출기를 먼저 학습시킨 뒤,
      실제 이미지에 <strong>여러 변환을 가해 일관되게 검출되는 점</strong>을 정답으로 삼았다.
      "반복 가능성"이라는 요구를 학습 신호로 직접 옮긴 것이다.
    </p>
    <p>
      <strong>매칭은 가장 늦게, 그리고 가장 크게 바뀌었다.</strong>
      SuperGlue 는 매칭을 <em>점 대 점 독립 판단</em>이 아니라
      <strong>집합 대 집합 할당 문제</strong>로 본다.
      <a href="transformer.html">어텐션</a>으로 두 이미지의 점들이 서로를 참조하게 하고,
      최적 수송으로 전체 할당을 한 번에 푼다.
    </p>
    <div class="note">
      <b>이것이 큰 전환인 이유.</b> 개별 최근접 판단은 주변 맥락을 모른다.
      반면 어텐션 기반 매칭은 <em>"이 점의 이웃들이 저쪽 어디에 대응하는지"</em>를 함께 본다.
      반복 무늬에서 특히 강해지는데, 창문 하나는 구분이 안 되지만
      <strong>창문들의 배치는 구분되기</strong> 때문이다.
      <a href="nms.html">NMS</a>가 그랬듯, 후처리로 하던 일이 학습으로 흡수된 사례다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>점을 거치지 않는 길, 그리고 선택</h2>
    <p>
      최근에는 <strong>검출 없는(detector-free)</strong> 접근도 자리 잡았다.
      점을 먼저 뽑지 않고, 두 이미지의 <em>조밀한 특징 맵끼리</em> 직접 대응을 만든다.
      거친 단계에서 대략 맞추고 세밀한 단계에서 정밀화하는 구성이다.
    </p>
    <p>
      질감이 없는 면 — 흰 벽, 매끈한 제품 표면 — 에서 특히 유리하다.
      뽑을 코너가 없어 기존 방식이 실패하던 곳이다.
      대신 연산량이 크고, 모든 픽셀 쌍을 보므로 고해상에서 부담이 된다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>상황</th><th>맞는 접근</th><th>이유</th></tr>
        </thead>
        <tbody>
          <tr><td>질감 풍부 · 실시간</td><td class="hi">고전 또는 학습 지역 특징</td><td>값싸고 충분하다</td></tr>
          <tr><td>뷰 차이가 큼</td><td class="hi">학습 매칭 (어텐션)</td><td>맥락을 함께 본다</td></tr>
          <tr><td>질감 없는 면</td><td class="hi">detector-free</td><td>뽑을 점이 없다</td></tr>
          <tr><td><a href="efficient-backbone.html">온디바이스</a></td><td>경량 고전 방식</td><td>연산·메모리 제약</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막으로 이 문서를 <a href="metric-learning.html">메트릭 러닝</a>과 이어 두자.
      두 접근은 경쟁이 아니라 <strong>층위가 다르다</strong>.
    </p>
    <p>
      실무 구성은 대개 <em>둘을 겹쳐 쓴다</em> —
      전역 임베딩과 <a href="vector-search.html">벡터 검색</a>으로 수백만 개 중 후보 수십 개를 빠르게 추리고,
      그 후보에 대해서만 지역 특징 매칭으로 정밀 검증한다.
      전자는 <strong>빠르지만 대략적</strong>이고 후자는 <strong>정확하지만 비싸다</strong>.
      순서를 바꾸면 감당할 수 없다.
    </p>
  </section>
"""

READING = [
    "Lowe, <em>Distinctive Image Features from Scale-Invariant Keypoints</em> (IJCV 2004) — SIFT. 비율 검사도 여기서 나온다.",
    "Fischler &amp; Bolles, <em>Random Sample Consensus</em> (CACM 1981) — RANSAC. 기하 검증의 표준.",
    "DeTone et al., <em>SuperPoint: Self-Supervised Interest Point Detection and Description</em> (arXiv:1712.07629) — 반복 가능성을 학습 신호로.",
    "Sarlin et al., <em>SuperGlue: Learning Feature Matching with Graph Neural Networks</em> (arXiv:1911.11763) — 매칭을 할당 문제로.",
    "Sun et al., <em>LoFTR: Detector-Free Local Feature Matching with Transformers</em> (arXiv:2104.00680) — 점을 거치지 않는 매칭.",
    "Lindenberger et al., <em>LightGlue: Local Feature Matching at Light Speed</em> (arXiv:2306.13643) — 적응적 계산으로 가볍게.",
]

write(
    "local-features.html",
    title="지역 특징과 매칭 — 같은 지점을 다시 찾기",
    eyebrow="Vision · Correspondence · 2004–2026",
    h1="지역 특징과 매칭",
    subtitle="같은 지점을 다시 찾기 — 전역 벡터가 답하지 못하는 것",
    dek=(
        "전역 임베딩은 <em>\"닮았다\"</em>까지만 말한다. "
        "어느 부분이 어느 부분에 대응하는지는 답하지 못한다. "
        "지역 특징은 점을 뽑고 서술해 <strong>점 대 점 대응</strong>을 만든다 — "
        "뷰가 크게 달라도 같은 물리적 지점을 짚기 위해서다."
    ),
    spec=[
        ("세 단계", "검출 · 서술 · 매칭"),
        ("검출 요구", "반복 가능성"),
        ("매칭의 적", "반복되는 무늬"),
        ("고전 처방", "비율 검사 + RANSAC"),
        ("현재", "어텐션 기반 할당"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

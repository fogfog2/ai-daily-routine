#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f2", panel="#e5e6ea", ink="#15161c", **{
    "ink-soft": "#4e505a", "ink-faint": "#7d7f8a", "rule": "#d0d1d7",
    "rule-strong": "#acadb5", "accent": "#4a3a9e", "accent-fill": "#e0dcf5",
    "accent-line": "#6d5cc0", "muted": "#84868e", "muted-fill": "#dfe0e4", "warn": "#a04628",
})
DARK = dict(paper="#101116", panel="#18191f", ink="#e6e7ee", **{
    "ink-soft": "#a2a4b0", "ink-faint": "#757884", "rule": "#212228", "rule-strong": "#383a46",
    "accent": "#a294ee", "accent-fill": "#1c1836", "accent-line": "#6f61bb",
    "muted": "#868892", "muted-fill": "#1a1b21", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>분류로는 풀리지 않는 문제</h2>
    <p>
      분류기는 <strong>정해진 클래스 목록</strong>을 전제한다. 개·고양이·자동차를 배웠다면 그 셋 중 하나로 답한다.
      그런데 실무에서 자주 만나는 요구는 다른 모양이다.
    </p>
    <ul>
      <li>이 상품 사진이 <strong>카탈로그의 어느 품목</strong>인가 — 품목은 매일 늘어난다</li>
      <li>이 얼굴이 <strong>등록된 사람</strong>인가 — 등록은 나중에 이루어진다</li>
      <li>같은 물건을 <strong>다른 각도에서</strong> 찍었는데 같다고 볼 것인가</li>
    </ul>
    <p>
      클래스가 학습 시점에 정해지지 않는다. 새 품목이 추가될 때마다 모델을 다시 학습시킬 수는 없다.
      (<a href="few-shot-learning.html">예시가 몇 장뿐인 경우</a>는 또 다른 갈래다.)
      그래서 목표를 바꾼다 — <strong>"무엇인지 맞히기" 대신 "같은지 다른지 재기"</strong>다.
    </p>
    <div class="eq">
      <span class="cap">요구를 그대로 적으면 이렇게 된다</span>
      <div class="line">같은 품목, 같은 뷰&nbsp;&nbsp;&nbsp;&nbsp;→ 유사도 <strong>높게</strong></div>
      <div class="line">같은 품목, <strong>다른 뷰</strong>&nbsp;&nbsp;→ 유사도 <strong>높게</strong>&nbsp;&nbsp;← 어려운 쪽</div>
      <div class="line">다른 품목, 비슷한 외형 → 유사도 <strong>낮게</strong>&nbsp;&nbsp;← 더 어려운 쪽</div>
      <div class="line">다른 품목, 다른 외형&nbsp;&nbsp;→ 유사도 낮게</div>
    </div>
    <p>
      가운데 두 줄이 이 분야의 전부다. <em>겉모습이 달라도 같다고, 겉모습이 비슷해도 다르다고</em>
      판정해야 한다. 픽셀 거리로는 정확히 반대 결과가 나온다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>쌍과 삼중항 — 거리를 직접 가르치기</h2>
    <p>
      가장 직접적인 방법은 <strong>거리 자체를 손실에 넣는 것</strong>이다.
      대조 손실은 쌍을 보고, 같은 쌍은 당기고 다른 쌍은 밀어낸다.
    </p>
    <div class="eq">
      <span class="cap">대조 손실 — 다른 쌍은 마진까지만 밀어낸다</span>
      <div class="line">L = y · d² + (1−y) · max(0, m − d)²</div>
      <div class="line">// y=1 같은 쌍, y=0 다른 쌍, d = ‖f(a) − f(b)‖</div>
      <div class="line">// 이미 m 이상 떨어진 다른 쌍은 더 밀지 않는다 — 무한히 밀 이유가 없다</div>
    </div>
    <p>
      <strong>삼중항 손실</strong>은 한 걸음 더 간다. 절대 거리가 아니라 <em>상대 순서</em>를 요구한다.
      기준(anchor)에 대해 같은 것(positive)이 다른 것(negative)보다 마진만큼 가까우면 된다.
    </p>
    <div class="eq">
      <span class="cap">삼중항 손실 — 순서만 맞으면 된다</span>
      <div class="line">L = max( 0,&nbsp; d(a, p) − d(a, n) + m )</div>
      <div class="line">&nbsp;</div>
      <div class="line">d(a,p) + m ≤ d(a,n) 이면 손실 0 → 학습 신호 없음</div>
    </div>
    <p>
      절대 거리를 강요하지 않는 것이 장점이다.
      어떤 품목은 원래 편차가 크고 어떤 품목은 작은데, 상대 순서만 요구하면 그 차이를 억지로 맞추지 않는다.
    </p>
    <div class="note">
      <b>문제는 삼중항의 개수다.</b> N개 표본이면 삼중항은 <code>O(N³)</code>이고,
      그 대부분은 <strong>이미 조건을 만족해 손실이 0</strong>이다. 학습이 진행될수록 심해진다.
      그래서 <em>어려운 표본을 골라내는 일</em>(hard negative mining)이 본체가 된다 —
      너무 쉬우면 신호가 없고, 너무 어려우면(라벨 노이즈인 경우) 학습이 무너진다.
      배치 안에서 고르는 방식(batch-hard)이 실용적 타협으로 자리 잡았다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>마진을 각도로 옮기다 — ArcFace 계열</h2>
    <p>
      쌍·삼중항 방식의 부담은 <strong>표본을 어떻게 고르느냐</strong>에 성능이 크게 좌우된다는 것이다.
      다른 접근이 나왔다 — <em>분류 손실을 쓰되, 마진을 넣어 클래스를 밀어내는 것</em>이다.
    </p>
    <p>
      출발점은 관찰 하나다. softmax 분류기의 마지막 층에서 편향을 없애고 가중치와 특징을 정규화하면,
      로짓이 <strong>코사인 유사도</strong>가 된다. 즉 분류가 <em>각도 문제</em>가 된다.
    </p>
    <div class="eq">
      <span class="cap">마진을 어디에 넣는가 — 세 방식</span>
      <div class="line">Softmax&nbsp;&nbsp;&nbsp; s · cos(θ)</div>
      <div class="line">SphereFace s · cos(<strong>m</strong>·θ)&nbsp;&nbsp;&nbsp;// 각도를 곱한다</div>
      <div class="line">CosFace&nbsp;&nbsp;&nbsp; s · (cos θ − <strong>m</strong>)&nbsp;// 코사인에서 뺀다</div>
      <div class="line">ArcFace&nbsp;&nbsp;&nbsp; s · cos(θ + <strong>m</strong>)&nbsp;// 각도에 더한다</div>
    </div>
    <p>
      셋 다 <em>"정답 클래스의 점수를 일부러 깎아"</em> 모델이 더 확실히 맞히도록 강요한다.
      결과적으로 같은 클래스는 뭉치고 다른 클래스는 벌어진다.
    </p>
    <div class="eq">
      <span class="cap">m = 0.5 일 때 실제 값</span>
      <div class="line">&nbsp;θ°&nbsp;&nbsp;&nbsp;&nbsp; cos θ&nbsp;&nbsp; CosFace&nbsp;&nbsp; ArcFace</div>
      <div class="line">&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp; 1.000&nbsp;&nbsp;&nbsp; 0.500&nbsp;&nbsp;&nbsp; 0.878</div>
      <div class="line">&nbsp;30&nbsp;&nbsp;&nbsp;&nbsp; 0.866&nbsp;&nbsp;&nbsp; 0.366&nbsp;&nbsp;&nbsp; 0.520</div>
      <div class="line">&nbsp;60&nbsp;&nbsp;&nbsp;&nbsp; 0.500&nbsp;&nbsp;&nbsp; 0.000&nbsp;&nbsp;&nbsp; 0.024</div>
      <div class="line">&nbsp;90&nbsp;&nbsp;&nbsp;&nbsp; 0.000&nbsp;&nbsp; −0.500&nbsp;&nbsp; −0.479</div>
    </div>
    <p>
      CosFace 는 각도와 무관하게 일정한 값을 빼지만, ArcFace 는 <strong>각도 공간에서 일정한 마진</strong>을 준다.
      논문은 이 점을 강조한다 — 각도 마진이 <em>측지 거리에 정확히 대응</em>하므로 기하학적으로 더 자연스럽다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="임베딩 공간에서 마진 손실이 하는 일. 일반 softmax는 클래스 경계만 나누어 같은 클래스가 넓게 퍼지지만, 각도 마진을 주면 같은 클래스가 뭉치고 클래스 사이에 빈 구간이 생겨 새로운 항목도 판정할 수 있다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">Softmax — 경계만 나눈다</text>

            <circle cx="120" cy="120" r="72" fill="none" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 3">
              <line x1="120" y1="120" x2="120" y2="48"/>
              <line x1="120" y1="120" x2="182" y2="156"/>
              <line x1="120" y1="120" x2="58" y2="156"/>
            </g>
            <g fill="var(--warn)" opacity="0.7">
              <circle cx="112" cy="70" r="4"/><circle cx="134" cy="76" r="4"/><circle cx="122" cy="60" r="4"/>
              <circle cx="146" cy="92" r="4"/><circle cx="100" cy="84" r="4"/>
            </g>
            <g fill="var(--accent)" opacity="0.7">
              <circle cx="158" cy="146" r="4"/><circle cx="170" cy="128" r="4"/><circle cx="150" cy="164" r="4"/>
              <circle cx="176" cy="150" r="4"/><circle cx="140" cy="140" r="4"/>
            </g>
            <g fill="var(--ink-soft)" opacity="0.6">
              <circle cx="82" cy="146" r="4"/><circle cx="70" cy="128" r="4"/><circle cx="90" cy="164" r="4"/>
              <circle cx="64" cy="152" r="4"/><circle cx="98" cy="138" r="4"/>
            </g>
            <text x="26" y="212" font-size="8.5" fill="var(--warn)">클래스마다 넓게 퍼져 경계에 붙어 있다</text>
            <text x="26" y="226" font-size="8.5" fill="var(--ink-faint)">→ 새 항목이 어디 속하는지 애매하다</text>

            <line x1="246" y1="26" x2="246" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="272" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">각도 마진 — 뭉치고 벌린다</text>

            <circle cx="368" cy="120" r="72" fill="none" stroke="var(--accent-line)" stroke-width="1.2"/>
            <g stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 3">
              <line x1="368" y1="120" x2="368" y2="48"/>
              <line x1="368" y1="120" x2="430" y2="156"/>
              <line x1="368" y1="120" x2="306" y2="156"/>
            </g>
            <g fill="var(--warn)" opacity="0.85">
              <circle cx="366" cy="62" r="4"/><circle cx="374" cy="64" r="4"/><circle cx="370" cy="56" r="4"/>
              <circle cx="360" cy="68" r="4"/><circle cx="378" cy="70" r="4"/>
            </g>
            <g fill="var(--accent)" opacity="0.85">
              <circle cx="416" cy="148" r="4"/><circle cx="422" cy="142" r="4"/><circle cx="410" cy="154" r="4"/>
              <circle cx="426" cy="152" r="4"/><circle cx="418" cy="158" r="4"/>
            </g>
            <g fill="var(--ink-soft)" opacity="0.75">
              <circle cx="320" cy="148" r="4"/><circle cx="314" cy="142" r="4"/><circle cx="326" cy="154" r="4"/>
              <circle cx="310" cy="152" r="4"/><circle cx="318" cy="158" r="4"/>
            </g>
            <path d="M 368 62 A 58 58 0 0 1 400 78" fill="none" stroke="var(--accent)" stroke-width="1.6"/>
            <text x="404" y="76" font-size="8" fill="var(--accent)">마진</text>

            <text x="272" y="212" font-size="8.5" fill="var(--accent)">클래스 안은 조밀, 사이에는 빈 구간</text>
            <text x="272" y="226" font-size="8.5" fill="var(--ink-faint)">→ 학습에 없던 항목도 임계값으로 판정 가능</text>

            <line x1="470" y1="26" x2="470" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="496" y="46" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">왜 이것이 중요한가</text>
            <text x="496" y="70" font-size="8.5" fill="var(--ink-faint)">학습에 없던 품목·사람도</text>
            <text x="496" y="84" font-size="8.5" fill="var(--ink-faint)">임베딩만 뽑아 비교하면 된다.</text>
            <text x="496" y="106" font-size="8.5" fill="var(--accent)">모델 재학습 없이 항목 추가</text>
            <text x="496" y="120" font-size="8.5" fill="var(--accent)">= open-set 대응</text>
            <text x="496" y="146" font-size="8.5" fill="var(--ink-faint)">클래스 사이가 벌어져 있어야</text>
            <text x="496" y="160" font-size="8.5" fill="var(--ink-faint)">임계값 하나로 자를 수 있다.</text>
            <text x="496" y="186" font-size="8.5" fill="var(--warn)">뭉치지 않으면 같은 품목의</text>
            <text x="496" y="200" font-size="8.5" fill="var(--warn)">다른 뷰가 떨어져 나간다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        마진 손실의 목적은 정확도가 아니라 <strong>임베딩 공간의 모양</strong>이다.
        분류 정확도만 보면 왼쪽으로도 충분하지만,
        <em>학습에 없던 항목을 유사도로 판정</em>하려면 오른쪽이어야 한다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>다른 뷰를 같다고 하려면</h2>
    <p>
      관심사의 어려운 쪽 — <strong>같은 물체를 다른 각도에서 찍었을 때</strong> — 을 짚자.
      마진 손실만으로는 부족하다. 학습 데이터에 그 변화가 들어 있어야 한다.
    </p>
    <p>
      가장 큰 지렛대는 <strong>증강</strong>이다.
      <a href="self-supervised-learning.html">자기지도 학습</a>에서 봤듯,
      "같은 것"의 정의는 증강이 정한다. 회전·자르기·색 변형을 같은 것으로 묶으면
      모델은 그 변화에 <em>불변</em>한 표현을 배운다.
    </p>
    <div class="note">
      <b>여기에 함정이 있다.</b> 색 변형을 강하게 걸면 <em>색이 다른 같은 모델의 제품</em>을 구분하지 못하게 된다.
      회전을 넣으면 위아래가 중요한 품목에서 문제가 생긴다.
      <strong>무엇을 불변으로 둘지가 곧 과제 정의</strong>이고, 증강 설계가 그것을 결정한다.
      "일단 다 넣는다"는 접근이 실패하는 이유다.
    </div>
    <p>
      데이터 자체로 푸는 방법도 있다. 같은 물체를 <em>여러 각도에서 찍은 쌍</em>을 학습에 넣으면
      증강이 흉내 낼 수 없는 실제 뷰 변화를 배운다. <a href="person-reid.html">재식별(Re-ID)</a> 분야가 이 구성을 쓴다 —
      같은 사람을 다른 카메라·다른 시간에 찍은 것이 양성 쌍이다.
    </p>
    <p>
      구조 쪽 장치도 있다. 전역 평균 풀링 하나로 벡터를 만들면 <em>부분적으로 가려진 경우</em>에 약하다.
      이미지를 가로로 나눠 부분별 특징을 뽑아 합치거나, 어텐션으로 중요한 영역에 가중치를 주는 방식이 쓰인다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>임계값 — 실무에서 가장 어려운 부분</h2>
    <p>
      모델이 유사도를 잘 내놓아도 <a href="similarity-threshold.html"><strong>어디서 자를 것인가</strong></a>가 남는다.
      그리고 이것이 대개 가장 손이 많이 가는 부분이다.
    </p>
    <p>
      같은 품목 쌍의 점수 분포와 다른 품목 쌍의 분포는 <em>완전히 갈라지지 않는다</em>. 반드시 겹친다.
      겹치는 구간을 어떻게 처리하느냐가 시스템의 성격을 정한다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>임계값</th><th>결과</th><th>맞는 곳</th></tr>
        </thead>
        <tbody>
          <tr><td>높게</td><td class="hi">오탐 적음 · 놓침 많음</td><td>결제·출입 — 틀리면 안 되는 곳</td></tr>
          <tr><td>낮게</td><td>놓침 적음 · 오탐 많음</td><td>검색 후보 추리기 — 사람이 최종 판단</td></tr>
          <tr><td>두 단계</td><td class="hi">애매한 구간만 따로</td><td>자동 처리 + 사람 검토 병행</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      평가 지표도 정확도로는 부족하다. 임계값에 따라 달라지므로
      <strong>ROC-AUC</strong> 나 특정 오탐률에서의 재현율(예: FMR 1e-4 에서의 TAR)을 본다.
      실무에서는 <em>"오탐을 1만 건에 1건으로 유지할 때 몇 %를 잡는가"</em> 같은 형태가 유용하다.
    </p>
    <div class="note">
      <b>임계값은 데이터가 바뀌면 다시 잡아야 한다.</b>
      카메라가 바뀌거나 조명 조건이 달라지면 점수 분포가 통째로 이동한다.
      모델을 그대로 두고 임계값만 다시 잡는 것이 <em>정기적인 운영 작업</em>이 되는 이유다.
      점수를 그대로 쓰지 않고 <strong>보정</strong>해 확률처럼 다루는 방식도 쓰인다.
    </div>
    <p>
      마지막으로 규모 문제를 짚어 둔다.
      카탈로그가 100만 개면 매번 전수 비교할 수 없다.
      임베딩을 뽑는 것과 <em>그 임베딩으로 빠르게 찾는 것</em>은 다른 문제이고,
      후자는 <a href="vector-search.html">근사 최근접 탐색(ANN)</a>의 영역이다.
      부분끼리의 대응이 필요하면 <a href="local-features.html">지역 특징</a>이 맡는다.
      <a href="rag.html">RAG</a>가 텍스트에서 같은 구조를 쓰는 것처럼,
      <strong>임베딩 + 벡터 검색</strong>은 도메인을 가리지 않는 조합이다.
    </p>
  </section>
"""

READING = [
    "Schroff et al., <em>FaceNet: A Unified Embedding for Face Recognition and Clustering</em> (arXiv:1503.03832) — 삼중항 손실과 임베딩 학습.",
    "Deng et al., <em>ArcFace: Additive Angular Margin Loss for Deep Face Recognition</em> (arXiv:1801.07698) — 각도 마진과 기하학적 근거.",
    "Wang et al., <em>CosFace: Large Margin Cosine Loss for Deep Face Recognition</em> (arXiv:1801.09414) — 코사인 마진.",
    "Hermans et al., <em>In Defense of the Triplet Loss for Person Re-Identification</em> (arXiv:1703.07737) — batch-hard 표본 선택.",
    "Hadsell et al., <em>Dimensionality Reduction by Learning an Invariant Mapping</em> (CVPR 2006) — 대조 손실의 원형.",
    "Musgrave et al., <em>A Metric Learning Reality Check</em> (arXiv:2003.08505) — 공정 비교 시 방법 간 격차가 보고보다 작다는 지적.",
]

write(
    "metric-learning.html",
    title="메트릭 러닝 — 같은 것은 가깝게, 다른 것은 멀게",
    eyebrow="Vision · Representation Learning · 2006–2026",
    h1="메트릭 러닝",
    subtitle="같은 것은 가깝게, 다른 것은 멀게 — 클래스가 정해지지 않은 세계",
    dek=(
        "분류기는 정해진 클래스 목록을 전제한다. "
        "그런데 품목은 매일 늘고, 얼굴은 나중에 등록된다. "
        "그래서 목표를 바꾼다 — <strong>무엇인지 맞히는 대신 같은지 다른지 재기</strong>. "
        "어려운 것은 두 줄이다. <em>겉모습이 달라도 같다고, 비슷해도 다르다고</em> 해야 한다."
    ),
    spec=[
        ("바꾸는 것", "분류 → 거리"),
        ("고전", "대조 · 삼중항 손실"),
        ("현재", "각도 마진 (ArcFace)"),
        ("어려운 쪽", "표본 선택 · 증강 설계"),
        ("실무 난제", "임계값 정하기"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

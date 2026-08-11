#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff0f2", panel="#e4e6ea", ink="#13161c", **{
    "ink-soft": "#4b525d", "ink-faint": "#7a818c", "rule": "#ced2d8",
    "rule-strong": "#aaafb7", "accent": "#1d5090", "accent-fill": "#d9e5f4",
    "accent-line": "#3d78b8", "muted": "#84878e", "muted-fill": "#dfe0e4", "warn": "#a04a28",
})
DARK = dict(paper="#0f1114", panel="#171a1f", ink="#e4e7ec", **{
    "ink-soft": "#a1a7b0", "ink-faint": "#747a84", "rule": "#212429", "rule-strong": "#373d45",
    "accent": "#6ba3e8", "accent-fill": "#0f2338", "accent-line": "#3d78b8",
    "muted": "#868992", "muted-fill": "#191c21", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>임베딩을 뽑은 다음</h2>
    <p>
      <a href="metric-learning.html">메트릭 러닝</a>으로 좋은 임베딩을 얻었다.
      같은 품목은 가깝고 다른 품목은 멀다. 그런데 <strong>실제로 찾으려면</strong> 문제가 하나 남는다.
    </p>
    <p>
      카탈로그가 100만 개면 쿼리 하나당 100만 번 비교해야 한다.
      512차원 벡터라면 계산량이 이렇게 된다.
    </p>
    <div class="eq">
      <span class="cap">전수 비교 — 512차원 기준</span>
      <div class="line">N&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 쿼리당 연산&nbsp;&nbsp;&nbsp;&nbsp; fp32 저장</div>
      <div class="line">&nbsp;&nbsp;&nbsp; 10,000&nbsp;&nbsp;&nbsp;&nbsp; 0.01 GFLOP&nbsp;&nbsp;&nbsp; 0.02 GB</div>
      <div class="line">&nbsp;1,000,000&nbsp;&nbsp;&nbsp;&nbsp; 1.02 GFLOP&nbsp;&nbsp;&nbsp; 2.05 GB</div>
      <div class="line">100,000,000&nbsp;&nbsp; 102.40 GFLOP&nbsp; 204.80 GB</div>
    </div>
    <p>
      1억 개면 <strong>쿼리 한 번에 102 GFLOP</strong> 이고 저장에만 205GB 다.
      초당 수백 건을 처리해야 하는 서비스에서는 성립하지 않는다.
    </p>
    <p>
      그래서 <strong>근사</strong>로 간다. 정확한 최근접을 포기하고
      <em>대체로 맞는 답을 훨씬 빠르게</em> 얻는 것이다.
      이것이 ANN(Approximate Nearest Neighbor)이고,
      <strong>임베딩을 만드는 일과 그것으로 찾는 일은 별개의 문제</strong>라는 것이 이 문서의 요지다.
    </p>
    <div class="note">
      <b>근사가 허용되는 이유.</b> 임베딩 자체가 이미 근사다.
      모델이 매긴 유사도에 오차가 있는데, 그 위에서 <em>정확한</em> 최근접을 찾는 것은
      의미가 크지 않다. 검색 품질을 조금 내주고 속도를 수백 배 얻는 거래가 성립한다.
      다만 <em>얼마나 내줬는지</em>는 반드시 측정해야 한다 — 그것이 재현율(recall)이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>세 가지 전략</h2>
    <p>
      ANN 기법은 많지만 <strong>무엇을 아끼는가</strong>로 나누면 셋이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>전략</th><th>아끼는 것</th><th>대표</th><th>대가</th></tr>
        </thead>
        <tbody>
          <tr><td>후보를 줄인다</td><td class="hi">비교 횟수</td><td>IVF (클러스터링)</td><td>경계 근처를 놓친다</td></tr>
          <tr><td>벡터를 줄인다</td><td class="hi">메모리 · 거리 계산</td><td>PQ (양자화)</td><td>거리가 부정확해진다</td></tr>
          <tr><td>길을 만든다</td><td class="hi">탐색 경로</td><td>HNSW (그래프)</td><td>메모리를 더 쓴다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>IVF</strong> 는 먼저 벡터들을 군집으로 나눠 둔다.
      쿼리가 오면 <em>가까운 군집 몇 개만</em> 열어 그 안에서만 비교한다.
      1,000개 군집 중 10개만 보면 비교 횟수가 100분의 1이 된다.
    </p>
    <p>
      <strong>PQ</strong> 는 벡터 자체를 압축한다.
      512차원을 여러 부공간으로 쪼개고 각 부공간을 코드북 인덱스로 바꾼다.
    </p>
    <div class="eq">
      <span class="cap">PQ 압축률 — 512차원 fp32 기준</span>
      <div class="line">원본&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 512 × 4 = <strong>2,048 bytes</strong></div>
      <div class="line">PQ 64개 부공간 × 8비트&nbsp;&nbsp; 64 bytes&nbsp;&nbsp;→ <strong>32배</strong> 압축</div>
      <div class="line">PQ 32개 부공간 × 8비트&nbsp;&nbsp; 32 bytes&nbsp;&nbsp;→ <strong>64배</strong> 압축</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 205GB 가 6.4GB 로 — 메모리에 올릴 수 있게 된다</div>
    </div>
    <p>
      압축만 이득이 아니다. 거리 계산도 빨라진다 —
      부공간별 거리를 <em>미리 표로 만들어 두면</em> 덧셈만으로 근사 거리를 얻는다.
      <a href="ondevice-quantization.html">양자화</a>가 곱셈을 정수로 바꾼 것처럼,
      PQ 는 거리 계산을 <strong>테이블 조회로</strong> 바꾼다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>HNSW — 멀리 뛰고 가까이 걷는다</h2>
    <p>
      현재 가장 널리 쓰이는 것은 <strong>그래프 기반</strong>이다.
      벡터들을 노드로 두고 가까운 것끼리 연결한 뒤, <em>그래프를 따라 걸어서</em> 답을 찾는다.
    </p>
    <p>
      단순한 그래프에는 문제가 있다. 시작점이 멀면 <em>한 걸음씩 오래 걸어야</em> 한다.
      HNSW 의 해법은 <strong>여러 층을 두는 것</strong>이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 234" role="img" aria-label="HNSW의 계층 구조. 위층은 노드가 적고 연결이 길어 멀리 이동하고, 아래로 내려갈수록 노드가 촘촘해져 정밀하게 접근한다. 위에서 대략 위치를 잡고 아래에서 정확히 찾는 구조다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ann-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">위에서 멀리 뛰고, 아래에서 가까이 걷는다</text>

            <text x="24" y="46" font-size="8" fill="var(--ink-faint)">층 2</text>
            <rect x="60" y="30" width="400" height="30" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
            <g fill="var(--accent)" opacity="0.8">
              <circle cx="90" cy="45" r="4"/><circle cx="250" cy="45" r="4"/><circle cx="410" cy="45" r="4"/>
            </g>
            <line x1="90" y1="45" x2="250" y2="45" stroke="var(--accent-line)" stroke-width="1.1"/>
            <line x1="250" y1="45" x2="410" y2="45" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="478" y="48" font-size="8" fill="var(--ink-faint)">노드 적음 · 연결 길다</text>

            <text x="24" y="106" font-size="8" fill="var(--ink-faint)">층 1</text>
            <rect x="60" y="90" width="400" height="30" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
            <g fill="var(--accent)" opacity="0.65">
              <circle cx="90" cy="105" r="3.5"/><circle cx="170" cy="105" r="3.5"/><circle cx="250" cy="105" r="3.5"/>
              <circle cx="330" cy="105" r="3.5"/><circle cx="410" cy="105" r="3.5"/>
            </g>
            <g stroke="var(--accent-line)" stroke-width="1">
              <line x1="90" y1="105" x2="170" y2="105"/><line x1="170" y1="105" x2="250" y2="105"/>
              <line x1="250" y1="105" x2="330" y2="105"/><line x1="330" y1="105" x2="410" y2="105"/>
            </g>

            <text x="24" y="166" font-size="8" fill="var(--ink-faint)">층 0</text>
            <rect x="60" y="150" width="400" height="30" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <g fill="var(--accent)" opacity="0.5">
              <circle cx="80" cy="165" r="3"/><circle cx="120" cy="165" r="3"/><circle cx="160" cy="165" r="3"/>
              <circle cx="200" cy="165" r="3"/><circle cx="240" cy="165" r="3"/><circle cx="280" cy="165" r="3"/>
              <circle cx="320" cy="165" r="3"/><circle cx="360" cy="165" r="3"/><circle cx="400" cy="165" r="3"/>
              <circle cx="440" cy="165" r="3"/>
            </g>
            <g stroke="var(--accent-line)" stroke-width="0.8" opacity="0.6">
              <line x1="80" y1="165" x2="120" y2="165"/><line x1="120" y1="165" x2="160" y2="165"/>
              <line x1="160" y1="165" x2="200" y2="165"/><line x1="200" y1="165" x2="240" y2="165"/>
              <line x1="240" y1="165" x2="280" y2="165"/><line x1="280" y1="165" x2="320" y2="165"/>
              <line x1="320" y1="165" x2="360" y2="165"/><line x1="360" y1="165" x2="400" y2="165"/>
            </g>
            <text x="478" y="168" font-size="8" fill="var(--ink-faint)">전체 노드 · 연결 짧다</text>

            <path d="M90 55 L246 42" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#ann-a)"/>
            <path d="M250 55 L250 88" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#ann-a)"/>
            <path d="M254 105 L326 105" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#ann-a)"/>
            <path d="M330 118 L330 148" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#ann-a)"/>
            <circle cx="320" cy="165" r="6" fill="none" stroke="var(--warn)" stroke-width="2"/>

            <line x1="24" y1="196" x2="674" y2="196" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="216" font-size="8.5" fill="var(--ink-soft)">몇 걸음으로 도달한다 — 전수 비교 대신 <tspan fill="var(--accent)">경로 탐색</tspan>으로 바꾼 것이다</text>
            <text x="24" y="230" font-size="8" fill="var(--warn)">대가: 그래프(연결 정보)를 저장해야 해 메모리를 원본보다 더 쓰기도 한다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>계층이 건너뛰기를 만든다.</strong>
        위층은 노드가 성기고 연결이 길어 <em>한 걸음에 멀리</em> 간다.
        아래로 내려갈수록 촘촘해져 정밀하게 접근한다.
        고속도로로 도시 근처까지 간 뒤 골목길로 들어가는 것과 같은 구조다.
      </figcaption>
    </figure>

    <p>
      HNSW 는 재현율이 높고 빠르지만 <strong>메모리를 많이 쓴다</strong>.
      벡터뿐 아니라 <em>연결 정보</em>를 저장해야 하기 때문이다.
      그래서 실무에서는 <strong>IVF-PQ 와 HNSW 를 조합</strong>하는 구성이 흔하다 —
      그래프로 후보를 좁히고 압축된 벡터로 거리를 재는 식이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>무엇을 재고 무엇을 조절하나</h2>
    <p>
      ANN 의 성능은 단일 숫자로 말할 수 없다.
      <strong>재현율과 속도가 맞바꿈</strong>이기 때문이다.
    </p>
    <div class="eq">
      <span class="cap">함께 봐야 하는 것들</span>
      <div class="line"><strong>recall@k</strong>&nbsp;&nbsp; 정확한 상위 k 개 중 몇 개를 찾았나</div>
      <div class="line"><strong>QPS</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 초당 처리 쿼리 수</div>
      <div class="line"><strong>메모리</strong>&nbsp;&nbsp;&nbsp;&nbsp; 인덱스 전체 크기</div>
      <div class="line"><strong>구축 시간</strong>&nbsp; 인덱스를 만드는 데 걸리는 시간</div>
      <div class="line">&nbsp;</div>
      <div class="line">// "recall 0.95 에서 QPS 몇" 형태로 보고해야 비교가 된다</div>
    </div>
    <p>
      조절 손잡이는 대개 <em>얼마나 넓게 탐색할지</em>다.
      IVF 는 열어 볼 군집 수, HNSW 는 탐색 폭을 키우면
      재현율이 오르고 속도가 떨어진다. <strong>같은 인덱스에서 실행 시점에</strong> 바꿀 수 있어
      운영 중 조정이 가능하다.
    </p>
    <div class="note">
      <b>재현율 손실이 어디서 오는지 알아야 한다.</b>
      IVF 는 <em>군집 경계 근처</em>에서 놓친다 — 진짜 최근접이 옆 군집에 있는데 열지 않은 경우다.
      PQ 는 <em>거리 자체가 부정확</em>해 순위가 뒤바뀐다.
      그래서 PQ 로 후보를 추린 뒤 <strong>원본 벡터로 재순위화</strong>하는 구성이 자주 쓰인다 —
      정확도가 필요한 상위 몇 개만 정확히 계산하는 것이다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>검색은 파이프라인의 한 단계다</h2>
    <p>
      마지막으로 이 문서를 앞선 것들과 이어 두자.
      실무의 검색은 대개 <strong>여러 단계로 좁혀 간다</strong>.
    </p>
    <div class="eq">
      <span class="cap">전형적인 3단계</span>
      <div class="line">① <strong>ANN 으로 후보 추리기</strong>&nbsp;&nbsp; 100만 → 100개&nbsp;&nbsp;&nbsp;빠르고 대략적</div>
      <div class="line">② <strong>정확한 거리로 재순위</strong>&nbsp; 100 → 10개&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;원본 벡터 사용</div>
      <div class="line">③ <strong>정밀 검증</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 10 → 1개&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="local-features.html">지역 특징</a> 매칭 등</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 뒤로 갈수록 정확하고 비싸다 — 순서를 바꾸면 감당할 수 없다</div>
    </div>
    <p>
      ③에서 <a href="local-features.html">지역 특징 매칭</a>을 쓰면
      <em>어느 부분이 대응하는지</em>까지 확인할 수 있다.
      전역 임베딩으로는 못 하는 일이고, 후보가 10개로 줄었으니 비용을 감당할 수 있다.
    </p>
    <p>
      그리고 최종 판정에는 <a href="similarity-threshold.html">임계값</a>이 필요하다.
      여기서 앞 문서의 <strong>규모 효과</strong>가 그대로 적용된다 —
      후보를 100만 개에서 뽑는다면 오수락 확률이 그만큼 커지므로
      임계값을 더 엄격하게 잡아야 한다.
    </p>
    <div class="note">
      <b>운영에서 자주 부딪히는 것들.</b>
      <em>인덱스 갱신</em>이 대표적이다 — 항목을 추가·삭제하려면 그래프나 군집을 손봐야 하는데,
      기법에 따라 비용이 크게 다르다. 대량 추가가 잦으면 <em>주기적 재구축</em>을 전제로 설계한다.
      <em>필터 결합</em>도 까다롭다 — "이 카테고리 안에서만 검색"처럼 조건이 붙으면
      ANN 구조가 그대로 작동하지 않아, 사전 필터링과 사후 필터링 중 무엇이 나은지 상황마다 다르다.
    </div>
    <p>
      정리하면 ANN 은 <em>"좋은 임베딩을 실제로 쓸 수 있게"</em> 만드는 단계다.
      <a href="metric-learning.html">메트릭 러닝</a>이 <strong>무엇이 가까운지</strong>를 정했다면,
      ANN 은 <strong>그것을 어떻게 빨리 찾을지</strong>를 답한다.
      둘 중 하나만으로는 시스템이 되지 않는다.
    </p>
  </section>
"""

READING = [
    "Jégou et al., <em>Product Quantization for Nearest Neighbor Search</em> (IEEE TPAMI 2011) — PQ 의 원 논문.",
    "Malkov &amp; Yashunin, <em>Efficient and robust approximate nearest neighbor search using HNSW graphs</em> (arXiv:1603.09320) — HNSW.",
    "Johnson et al., <em>Billion-scale similarity search with GPUs</em> (arXiv:1702.08734) — FAISS. IVF-PQ 의 실용적 구현.",
    "Aumüller et al., <em>ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms</em> (arXiv:1807.05614) — 재현율-속도 곡선으로 비교하는 방법.",
    "Guo et al., <em>Accelerating Large-Scale Inference with Anisotropic Vector Quantization</em> (arXiv:1908.10396) — ScaNN. 검색 목적에 맞춘 양자화.",
]

write(
    "vector-search.html",
    title="벡터 검색 — 임베딩을 실제로 쓸 수 있게",
    eyebrow="Vision · Retrieval Systems · 2011–2026",
    h1="벡터 검색",
    subtitle="임베딩을 실제로 쓸 수 있게 — 근사로 수백 배를 얻는다",
    dek=(
        "좋은 임베딩을 얻었어도 100만 개와 비교하려면 "
        "쿼리 하나에 <strong>1 GFLOP</strong>, 1억 개면 <strong>102 GFLOP</strong> 이다. "
        "그래서 정확한 최근접을 포기하고 근사로 간다. "
        "임베딩을 <em>만드는 일</em>과 그것으로 <em>찾는 일</em>은 별개의 문제다."
    ),
    spec=[
        ("문제", "전수 비교가 불가능"),
        ("세 전략", "후보 축소 · 압축 · 그래프"),
        ("PQ", "512차원 → 64바이트 (32배)"),
        ("측정", "recall@k 와 QPS 를 함께"),
        ("위치", "검색 파이프라인의 1단계"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

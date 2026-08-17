#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0ee", panel="#e6e6e2", ink="#171814", **{
    "ink-soft": "#525449", "ink-faint": "#818376", "rule": "#d2d3cb",
    "rule-strong": "#aeafa4", "accent": "#5c5410", "accent-fill": "#ebe8cc",
    "accent-line": "#8a7f2c", "muted": "#82868c", "muted-fill": "#dee0e2", "warn": "#9c4426",
})
DARK = dict(paper="#111210", panel="#191a16", ink="#e8e9e2", **{
    "ink-soft": "#a7a99b", "ink-faint": "#7c7e70", "rule": "#24261e", "rule-strong": "#3b3d2f",
    "accent": "#ccc05c", "accent-fill": "#272410", "accent-line": "#928734",
    "muted": "#878d93", "muted-fill": "#1b1d20", "warn": "#dd8355",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>스케일링 법칙이 말하지 않는 것</h2>
    <p>
      스케일링 법칙은 파라미터와 데이터를 키우면 손실이 내려간다고 말한다.
      그런데 그 식에서 데이터는 <strong>토큰 개수</strong>라는 하나의 숫자로만 등장한다.
      1조 토큰이면 1조 토큰이지, 그것이 어떤 토큰인지는 식에 들어 있지 않다.
    </p>
    <p>
      실제로는 그 내용이 결과를 크게 가른다.
      같은 규모라도 <em>중복이 걸러지고 품질이 선별된</em> 1조 토큰과
      <em>웹에서 긁어낸 그대로의</em> 1조 토큰은 전혀 다른 모델을 만든다.
    </p>
    <p>
      Chinchilla 이후 학습 데이터가 병목이 되면서 이 문제가 전면에 나왔다.
      "토큰을 더 구할 수 없다면, 가진 토큰에서 더 뽑아내야 한다."
      데이터 큐레이션이 연구 주제가 된 배경이다.
    </p>
    <div class="note">
      <b>비용 구조가 이 판단을 지배한다.</b> 사전학습 한 번에 수백만 달러가 든다면,
      데이터 정제에 며칠을 더 쓰는 것은 반올림 오차다.
      <em>정제로 얻는 이득이 파라미터를 늘려 얻는 이득보다 싼 구간</em>이 넓다는 것이
      이 분야의 실용적 전제다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>중복 제거 — 가장 확실한 이득</h2>
    <p>
      웹 크롤에는 같은 문서가 여러 번 들어 있다. 미러 사이트, 인용, 상용구, 템플릿 페이지.
      중복이 학습에 미치는 영향은 세 갈래로 나쁘다.
    </p>
    <ul>
      <li><strong>암기를 유도한다.</strong> 같은 문자열을 여러 번 보면 모델이 그것을 그대로 외운다. 학습 데이터가 출력으로 새어 나오는 문제와 직결된다.</li>
      <li><strong>평가를 오염시킨다.</strong> 벤치마크 문제가 학습 데이터에 섞여 있으면 점수가 부풀려진다.</li>
      <li><strong>연산을 낭비한다.</strong> 같은 것을 반복 학습하는 데 GPU 시간을 쓴다.</li>
    </ul>
    <p>
      중복 제거는 두 층위로 한다. <strong>정확 중복</strong>은 해시로 걸러내면 되지만,
      실제로 문제가 되는 것은 <strong>근사 중복</strong>이다 —
      광고 한 줄만 다른 같은 기사 같은 것들. 문서 쌍을 전부 비교하면 <code>O(N²)</code>이라 불가능하다.
    </p>
    <div class="eq">
      <span class="cap">MinHash + LSH — 비슷한 것끼리만 비교한다</span>
      <div class="line">1) 문서를 n-gram 집합으로 본다</div>
      <div class="line">2) 여러 해시 함수의 최솟값을 모아 서명(signature)을 만든다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;→ 서명이 같을 확률 ≈ Jaccard 유사도</div>
      <div class="line">3) 서명을 밴드로 쪼개 버킷에 넣는다 (LSH)</div>
      <div class="line">4) <strong>같은 버킷에 든 쌍만</strong> 실제로 비교</div>
    </div>
    <p>
      이 절차로 <code>O(N²)</code>이 사실상 선형에 가까워진다.
      실측 효과도 분명하다 — 중복을 제거하면 <strong>같은 성능에 도달하는 학습 스텝이 줄고</strong>,
      학습 데이터 유출 빈도가 크게 떨어진다는 결과가 반복 보고됐다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>품질 필터링 — 무엇을 남길 것인가</h2>
    <p>
      중복을 걷어낸 다음은 품질이다. 여기서부터는 <strong>판단이 개입</strong>하고, 그래서 논쟁적이다.
      실무에서 쓰이는 층위는 대략 셋이다.
    </p>
    <p>
      <strong>규칙 기반.</strong> 값싸고 확실한 것부터 걸러낸다.
      문서 길이, 문장부호 비율, 단어 평균 길이, 반복 문장 비율,
      금칙어 목록, 언어 판별. C4와 Gopher 계열이 정리한 휴리스틱 목록이 사실상 표준이 됐다.
    </p>
    <p>
      <strong>분류기 기반.</strong> "좋은 문서"의 예시(위키백과, 교과서, 잘 정리된 참조 문헌)를 양성으로,
      무작위 웹 문서를 음성으로 두고 분류기를 학습해 점수를 매긴다.
      GPT-3가 이 방식을 썼다.
    </p>
    <p>
      <strong>모델 기반 평가.</strong> LLM에게 문서의 교육적 가치를 점수로 매기게 하고,
      그 라벨로 작은 분류기를 학습시켜 전체 코퍼스에 적용한다.
      FineWeb-Edu가 이 접근으로 만들어졌고, 같은 토큰 수에서 벤치마크 성능이 크게 올랐다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 220" role="img" aria-label="데이터 큐레이션 파이프라인 도식. 원시 웹 크롤에서 언어 판별, 규칙 기반 필터, 중복 제거, 품질 분류기, 벤치마크 오염 제거를 차례로 거치며 데이터가 줄어들고, 각 단계에서 대략적인 잔존 비율을 표시한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="dq-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--ink-soft)">큐레이션 파이프라인 — 걸러낼수록 줄어든다</text>

            <rect x="26" y="34" width="120" height="52" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="86" y="56" text-anchor="middle" font-size="9.5" fill="var(--ink-soft)">원시 웹 크롤</text>
            <text x="86" y="72" text-anchor="middle" font-size="9" fill="var(--ink-faint)">100%</text>

            <path d="M150 60 L172 60" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#dq-a)"/>

            <rect x="176" y="38" width="104" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="228" y="56" text-anchor="middle" font-size="9" fill="var(--ink-soft)">언어 판별</text>
            <text x="228" y="70" text-anchor="middle" font-size="9" fill="var(--ink-faint)">+ 규칙 필터</text>

            <path d="M284 60 L306 60" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#dq-a)"/>

            <rect x="310" y="38" width="104" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="362" y="56" text-anchor="middle" font-size="9" fill="var(--accent)">중복 제거</text>
            <text x="362" y="70" text-anchor="middle" font-size="8.5" fill="var(--accent)">MinHash + LSH</text>

            <path d="M418 60 L440 60" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#dq-a)"/>

            <rect x="444" y="38" width="104" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="496" y="56" text-anchor="middle" font-size="9" fill="var(--ink-soft)">품질 분류기</text>
            <text x="496" y="70" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">교육적 가치 점수</text>

            <path d="M552 60 L574 60" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#dq-a)"/>

            <rect x="578" y="38" width="96" height="44" fill="var(--warn)" opacity="0.18" stroke="var(--warn)" stroke-width="1.3"/>
            <text x="626" y="56" text-anchor="middle" font-size="9" fill="var(--ink)">오염 제거</text>
            <text x="626" y="70" text-anchor="middle" font-size="8.5" fill="var(--warn)">벤치마크 배제</text>

            <g>
              <rect x="26" y="106" width="648" height="16" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <rect x="26" y="106" width="420" height="16" fill="var(--rule-strong)" opacity="0.5"/>
              <rect x="26" y="106" width="228" height="16" fill="var(--accent)" opacity="0.5"/>
              <rect x="26" y="106" width="96" height="16" fill="var(--accent)" opacity="0.85"/>
            </g>
            <text x="30" y="138" font-size="8.5" fill="var(--accent)">최종 학습셋</text>
            <text x="258" y="138" font-size="8.5" fill="var(--ink-faint)">중복 제거 후</text>
            <text x="450" y="138" font-size="8.5" fill="var(--ink-faint)">규칙 필터 후</text>
            <text x="600" y="138" font-size="8.5" fill="var(--ink-faint)">원시</text>

            <rect x="26" y="156" width="648" height="1" fill="var(--rule)"/>

            <text x="26" y="178" font-size="9.5" fill="var(--ink-soft)">단계마다 <tspan fill="var(--warn)">과잉 제거의 위험</tspan>이 따른다.</text>
            <text x="26" y="194" font-size="9" fill="var(--ink-faint)">규칙 필터는 방언·비표준 표기·소수 언어를 함께 지우고,</text>
            <text x="26" y="208" font-size="9" fill="var(--ink-faint)">위키백과를 기준으로 삼은 분류기는 그 문체만 좋다고 배운다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        각 단계는 데이터를 줄이지만 <em>남은 데이터의 밀도를 올린다</em>.
        다만 필터는 중립적이지 않다 — 무엇을 "저품질"로 정의하느냐가
        <strong>어떤 언어와 어떤 집단의 글이 남는지</strong>를 결정한다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>과잉 제거라는 반대편 위험</h2>
    <p>
      필터를 세게 걸수록 좋아진다면 이야기가 간단하겠지만, 그렇지 않다.
      <strong>필터는 특정 종류의 글을 체계적으로 지운다.</strong>
    </p>
    <ul>
      <li><strong>방언과 비표준 표기.</strong> "품질 낮은 문서"를 거르는 규칙이 방언 표기, 구어체, 소수 집단의 글쓰기 방식을 함께 걸러낸다는 분석이 여러 차례 나왔다.</li>
      <li><strong>소수 언어.</strong> 언어 판별기의 정확도가 언어마다 다르다. 자료가 적은 언어일수록 오탐으로 버려지기 쉬워, 격차가 더 벌어진다.</li>
      <li><strong>기준 문체로의 수렴.</strong> 위키백과를 양성 예시로 쓰면 분류기는 "위키백과처럼 쓴 글"을 좋아하게 된다. 다양성이 줄어든다.</li>
      <li><strong>안전 필터의 부작용.</strong> 유해 내용을 거른다며 특정 정체성 관련 어휘가 포함된 문서를 통째로 지우면, 그 주제에 대한 모델의 지식만 얇아진다.</li>
    </ul>
    <p>
      그래서 큐레이션은 <em>"더 세게 거를수록 좋다"</em>가 아니라
      <strong>어느 지점에서 멈출 것인가의 문제</strong>다.
      그리고 그 지점을 정하는 것은 결국 값 판단이지 순수한 공학이 아니다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>커리큘럼 — 순서와 배합</h2>
    <p>
      무엇을 남길지 다음에 오는 물음은 <strong>어떤 비율로, 어떤 순서로 먹일 것인가</strong>다.
    </p>
    <p>
      <strong>도메인 배합</strong>은 실질적 영향이 크다.
      웹·코드·논문·책·수학을 어떤 비율로 섞느냐에 따라 능력 분포가 달라진다.
      코드 비중을 늘리면 코딩 능력만 오르는 것이 아니라
      <em>일반 추론 성능도 함께 오른다</em>는 관찰이 반복 보고돼,
      코드가 사실상 추론 학습 데이터로 취급되기 시작했다.
      DoReMi처럼 배합 비율 자체를 최적화하는 방법도 나왔다.
    </p>
    <p>
      <strong>순서</strong>는 좀 더 미묘하다. 고전적 커리큘럼 학습(쉬운 것부터)은
      대형 언어모델 사전학습에서 일관된 이득을 보이지 않았다.
      대신 <strong>학습 후반부에 고품질 데이터를 배치하는</strong> 방식은 널리 쓰인다 —
      학습률이 낮아지는 구간에서 본 데이터가 최종 가중치에 더 크게 남기 때문이다.
      "마지막에 무엇을 보여줬는가"가 모델의 성격에 영향을 준다.
    </p>
    <p>
      다만 <strong>사후 학습으로 가면 난이도 순서가 다시 결정적이 된다.</strong>
      <a href="rlvr.html">RLVR</a>처럼 그룹 안의 상대 순위로 학습하는 방식에서는
      모델이 이미 다 푸는 문항과 하나도 못 푸는 문항이 <em>똑같이 아무 신호도 만들지 못한다</em>.
      사전학습에서 흐릿하던 커리큘럼의 효과가 여기서는 비용에 직접 걸린다.
    </p>
    <div class="note">
      <b>중복 학습은 무조건 나쁜 것이 아니다.</b> 데이터가 정말 부족하면
      같은 데이터를 여러 번 도는 선택이 있다.
      연구 결과는 <em>대략 4회 정도까지는</em> 새 데이터를 쓰는 것과 큰 차이가 없고,
      그 이상 반복하면 이득이 급격히 떨어진다는 쪽으로 모인다.
      "중복 제거"와 "의도적 반복"은 다른 층위의 이야기다.
    </div>
    <p>
      정리하면, 데이터 큐레이션은 스케일링 법칙의 <code>D</code>를 늘리는 대신
      <strong>같은 <code>D</code>에서 얻는 것을 늘리는 작업</strong>이다.
      그리고 그 과정의 모든 선택 — 무엇을 저품질로 볼지, 어떤 언어를 남길지,
      어떤 비율로 섞을지 — 은 <em>모델이 무엇을 잘하고 무엇을 모를지</em>를 미리 정한다.
      데이터는 중립적인 원재료가 아니다.
    </p>
  </section>
"""

READING = [
    "Lee et al., <em>Deduplicating Training Data Makes Language Models Better</em> (arXiv:2107.06499) — 중복 제거의 효과와 MinHash 파이프라인.",
    "Penedo et al., <em>The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale</em> (arXiv:2406.17557) — 필터 단계별 효과의 체계적 실측.",
    "Raffel et al., <em>Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer</em> (arXiv:1910.10683) — C4 휴리스틱 필터의 출처.",
    "Xie et al., <em>DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining</em> (arXiv:2305.10429) — 도메인 배합 최적화.",
    "Muennighoff et al., <em>Scaling Data-Constrained Language Models</em> (arXiv:2305.16264) — 데이터가 부족할 때 반복 학습의 손익.",
    "Dodge et al., <em>Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus</em> (arXiv:2104.08758) — 필터가 어떤 글을 지우는지에 대한 분석.",
]

write(
    "curriculum-data-quality.html",
    title="데이터 품질과 커리큘럼 — 무엇을 먹이느냐가 정한다",
    eyebrow="Training · Data Curation · 2021–2026",
    h1="데이터 품질과 커리큘럼",
    subtitle="무엇을 먹이느냐가 정한다 — 스케일링 법칙이 말하지 않는 것",
    dek=(
        "스케일링 법칙에서 데이터는 <strong>토큰 개수</strong>라는 숫자 하나로만 등장한다. "
        "그런데 같은 1조 토큰이라도 정제된 것과 긁어낸 그대로는 전혀 다른 모델을 만든다. "
        "중복 제거는 확실한 이득이지만, 품질 필터부터는 판단이 개입한다 — "
        "무엇을 저품질로 정의하느냐가 <em>어떤 언어와 누구의 글이 남는지</em>를 정한다."
    ),
    spec=[
        ("가장 확실한 것", "중복 제거"),
        ("근사 중복", "MinHash + LSH"),
        ("품질 판정", "규칙 → 분류기 → LLM"),
        ("반대 위험", "과잉 제거 · 다양성 손실"),
        ("반복 학습", "약 4회까지 무해"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

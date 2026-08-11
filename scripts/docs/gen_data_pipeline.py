#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0ee", panel="#e6e6e2", ink="#171814", **{
    "ink-soft": "#525349", "ink-faint": "#818277", "rule": "#d2d3cc",
    "rule-strong": "#aeafa6", "accent": "#4a5a1a", "accent-fill": "#e6ead0",
    "accent-line": "#748535", "muted": "#84868c", "muted-fill": "#dfe0e2", "warn": "#a04628",
})
DARK = dict(paper="#111210", panel="#191a16", ink="#e8e9e2", **{
    "ink-soft": "#a7a89c", "ink-faint": "#7a7c70", "rule": "#23241e", "rule-strong": "#3a3b30",
    "accent": "#a8bd62", "accent-fill": "#22270f", "accent-line": "#75853a",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>모델보다 데이터에서 막힌다</h2>
    <p>
      <a href="segmentation.html">분할 문서</a>에서 <em>"실무적 최대 장벽은 모델이 아니라 라벨"</em>이라 했다.
      마스크 하나에 수십 분이 걸린다는 이야기였다.
      그런데 이 문제는 분할만의 것이 아니다.
    </p>
    <p>
      실제 프로젝트에서 시간이 어디로 가는지 보면 대체로 이런 모양이다 —
      모델 구조를 고르는 데는 하루, <strong>데이터를 모으고 라벨링하고 정제하는 데는 몇 달</strong>이다.
      그리고 성능을 가르는 것도 대개 후자다.
    </p>
    <p>
      <a href="curriculum-data-quality.html">데이터 품질</a> 문서가
      사전학습 코퍼스를 다뤘다면, 이 문서는 <strong>내 과제의 데이터를 만드는 일</strong>을 다룬다.
      규모가 작고 라벨이 필요하다는 점에서 성격이 다르다.
    </p>
    <div class="eq">
      <span class="cap">데이터 파이프라인의 단계</span>
      <div class="line">수집 → 선별 → 라벨링 → 검수 → 분할 → 버전 관리</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↑</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 모델이 틀린 것을 보고 다시 수집</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 일방향이 아니라 <strong>순환</strong>이다 — 이것이 핵심이다</div>
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>무엇을 라벨링할 것인가</h2>
    <p>
      예산이 10,000장어치라면 <strong>어떤 10,000장을 고를 것인가</strong>가 성능을 크게 가른다.
      무작위로 뽑는 것은 대개 나쁜 선택이다.
    </p>
    <p>
      이유는 데이터가 <em>불균형</em>하기 때문이다.
      쉬운 사례는 넘치고 어려운 사례는 드물다.
      무작위로 뽑으면 <strong>이미 잘하는 것을 또 배우는</strong> 데이터가 대부분이 된다.
    </p>
    <div class="eq">
      <span class="cap">능동 학습 — 모델이 모르는 것을 고른다</span>
      <div class="line">1) 라벨 있는 소량으로 모델을 학습한다</div>
      <div class="line">2) 라벨 없는 풀에 <strong>추론</strong>을 돌린다</div>
      <div class="line">3) <em>확신이 낮은 것</em>을 골라 라벨링한다</div>
      <div class="line">4) 다시 학습 — 반복</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 같은 예산으로 더 나은 모델을 얻는다</div>
    </div>
    <p>
      "확신이 낮다"를 재는 방법이 여럿이다 —
      최고 확률이 낮거나, 1등과 2등이 비슷하거나(<a href="local-features.html">비율 검사</a>와 같은 발상),
      여러 모델의 예측이 엇갈리거나, 예측 엔트로피가 높은 경우다.
    </p>
    <div class="note">
      <b>불확실성만 보면 함정에 빠진다.</b> 모델이 확신 없어 하는 것 중에는
      <em>애초에 라벨링이 불가능한 것</em>이 섞여 있다 — 흐릿하거나, 잘렸거나, 잘못 찍힌 사진.
      그런 것만 골라 라벨링하면 예산을 낭비한다.
      그래서 <strong>불확실성과 대표성을 함께</strong> 보는 방식이 쓰인다 —
      비슷한 것이 풀에 많은, 즉 <em>영향력이 큰</em> 사례를 우선한다.
    </div>
    <p>
      또 하나 중요한 원칙은 <strong>실패 사례에서 출발하는 것</strong>이다.
      배포된 모델이 틀린 입력을 모아 라벨링하면,
      <em>실제 분포에서 부족한 곳</em>을 정확히 겨냥할 수 있다.
      능동 학습보다 단순하지만 실무에서 더 자주 효과를 낸다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>라벨은 정답이 아니다</h2>
    <p>
      라벨을 <em>객관적 사실</em>로 보면 곤란해진다.
      사람이 붙인 것이므로 <strong>불일치가 반드시 생긴다</strong>.
    </p>
    <p>
      같은 이미지를 여러 명에게 주면 답이 갈린다.
      경계가 애매한 물체, 가려진 물체, 기준이 모호한 클래스에서 특히 그렇다.
      <em>"이 흐릿한 것도 사람으로 볼 것인가"</em> 같은 질문에 정답이 없다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 234" role="img" aria-label="라벨 불일치와 그 처리. 같은 이미지에 대해 라벨러마다 다른 답을 내며, 다수결로 합치거나 불일치가 큰 항목을 가이드라인 개선에 활용한다. 데이터 파이프라인은 일방향이 아니라 순환 구조다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="dp-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">같은 이미지, 다른 답</text>

            <rect x="24" y="30" width="70" height="52" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <ellipse cx="46" cy="56" rx="12" ry="18" fill="var(--ink-soft)" opacity="0.4"/>
            <ellipse cx="76" cy="58" rx="9" ry="14" fill="var(--ink-soft)" opacity="0.18"/>
            <text x="59" y="96" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">뒤쪽이 흐릿하다</text>

            <path d="M100 56 L124 56" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dp-a)"/>

            <g font-size="8">
              <rect x="130" y="30" width="86" height="16" fill="var(--accent)" opacity="0.3" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="136" y="42" fill="var(--ink)">A: 사람 2명</text>
              <rect x="130" y="50" width="86" height="16" fill="var(--warn)" opacity="0.25" stroke="var(--warn)" stroke-width="1"/>
              <text x="136" y="62" fill="var(--ink)">B: 사람 1명</text>
              <rect x="130" y="70" width="86" height="16" fill="var(--accent)" opacity="0.3" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="136" y="82" fill="var(--ink)">C: 사람 2명</text>
            </g>

            <path d="M222 58 L246 58" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dp-a)"/>
            <rect x="252" y="44" width="80" height="28" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="292" y="62" text-anchor="middle" font-size="8" fill="var(--accent)">다수결 → 2명</text>

            <text x="348" y="42" font-size="8" fill="var(--ink-soft)">그런데 <tspan fill="var(--warn)">불일치 자체가 정보</tspan>다</text>
            <text x="348" y="58" font-size="8" fill="var(--ink-faint)">여기서 갈렸다는 것은</text>
            <text x="348" y="72" font-size="8" fill="var(--ink-faint)">가이드라인이 이 경우를 안 다뤘다는 뜻</text>
            <text x="348" y="90" font-size="8" fill="var(--accent)">→ 가이드라인을 고치고 다시 라벨링</text>

            <line x1="24" y1="112" x2="674" y2="112" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="132" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">파이프라인은 순환이다</text>

            <g>
              <rect x="40" y="150" width="72" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <text x="76" y="167" text-anchor="middle" font-size="8" fill="var(--ink-soft)">수집·선별</text>
              <path d="M116 163 L136 163" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dp-a)"/>
              <rect x="140" y="150" width="72" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <text x="176" y="167" text-anchor="middle" font-size="8" fill="var(--ink-soft)">라벨링</text>
              <path d="M216 163 L236 163" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dp-a)"/>
              <rect x="240" y="150" width="72" height="26" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
              <text x="276" y="167" text-anchor="middle" font-size="8" fill="var(--accent)">검수</text>
              <path d="M316 163 L336 163" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dp-a)"/>
              <rect x="340" y="150" width="72" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <text x="376" y="167" text-anchor="middle" font-size="8" fill="var(--ink-soft)">학습</text>
              <path d="M416 163 L436 163" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#dp-a)"/>
              <rect x="440" y="150" width="72" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <text x="476" y="167" text-anchor="middle" font-size="8" fill="var(--ink-soft)">배포·관찰</text>
            </g>

            <path d="M476 180 L476 200 L76 200 L76 180" stroke="var(--accent-line)" stroke-width="1.4" fill="none" marker-end="url(#dp-a)"/>
            <text x="276" y="216" text-anchor="middle" font-size="8.5" fill="var(--accent)">틀린 사례를 모아 다시 수집한다 — 여기가 가장 효율이 높다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>불일치를 없애려 하지 말고 활용한다.</strong>
        라벨러들이 갈린 항목은 <em>가이드라인이 그 경우를 정의하지 않았다</em>는 신호다.
        여러 명에게 겹쳐 라벨링시키고 일치율(예: Cohen's kappa)을 재면,
        <strong>데이터 품질과 가이드라인 품질을 동시에</strong> 볼 수 있다.
      </figcaption>
    </figure>

    <p>
      그래서 실무에서는 <strong>가이드라인 문서</strong>가 핵심 산출물이 된다.
      경계 사례를 그림과 함께 명시하고, 불일치가 나올 때마다 갱신한다.
      <em>"애매하면 이렇게 한다"</em>는 규칙이 쌓일수록 데이터가 일관되진다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>나누는 방법이 결과를 속인다</h2>
    <p>
      데이터를 학습·검증·테스트로 나눌 때 <strong>무작위 분할이 함정</strong>이 되는 경우가 많다.
    </p>
    <p>
      이미지가 서로 독립이 아니기 때문이다.
      같은 촬영 세션의 연속 프레임, 같은 제품의 여러 각도,
      같은 사람의 여러 사진 — 이런 것들이 학습과 테스트에 <em>나뉘어 들어가면</em>
      테스트 점수가 부풀려진다.
    </p>
    <div class="eq">
      <span class="cap">무엇을 기준으로 나눌 것인가</span>
      <div class="line">✗ 무작위&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 같은 촬영본이 양쪽에 들어간다</div>
      <div class="line">✓ <strong>그룹 단위</strong>&nbsp; 촬영 세션·제품·인물 단위로 통째로 나눈다</div>
      <div class="line">✓ <strong>시간 단위</strong>&nbsp; 과거로 학습, 미래로 테스트</div>
      <div class="line">✓ <strong>환경 단위</strong>&nbsp; 다른 매장·다른 카메라로 테스트</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 배포 상황과 같은 <em>격차</em>를 테스트에 넣어야 한다</div>
    </div>
    <p>
      <a href="person-reid.html">Re-ID</a> 에서 본 <strong>도메인 격차</strong>가 여기서도 나온다.
      새 매장에 배포할 것이라면 테스트도 <em>학습에 없던 매장</em>으로 해야
      실제 성능을 예측할 수 있다.
    </p>
    <div class="note">
      <b>테스트셋은 건드리지 않는다.</b> 하이퍼파라미터를 테스트셋으로 고르면
      <a href="evaluation-benchmarks.html">평가 문서</a>에서 본 오염이 그대로 일어난다 —
      점수는 오르는데 실제 성능은 아니다.
      검증셋으로 고르고 테스트셋은 <em>마지막에 한 번만</em> 쓰는 것이 원칙이지만,
      실무에서 가장 자주 어겨지는 규칙이기도 하다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>재현 가능하게 만들기</h2>
    <p>
      데이터는 <strong>계속 변한다</strong>. 라벨을 고치고, 새 데이터를 넣고, 잘못된 것을 뺀다.
      그런데 <em>어느 시점의 데이터로 학습했는지</em>를 모르면 결과를 재현할 수 없다.
    </p>
    <p>
      코드는 git 으로 버전이 관리되는데 데이터는 그렇지 않은 경우가 많다.
      <a href="experiment-tracking.html">실험 관리</a>가 이 문제를 정면으로 다룬다.
      "지난달 모델이 더 좋았는데 왜 그런지 모르겠다"는 상황이 여기서 나온다.
    </p>
    <div class="eq">
      <span class="cap">실험 하나를 재현하려면 필요한 것</span>
      <div class="line">· 코드 커밋 해시</div>
      <div class="line">· <strong>데이터셋 버전</strong> ← 자주 빠진다</div>
      <div class="line">· 하이퍼파라미터 전체</div>
      <div class="line">· 난수 시드</div>
      <div class="line">· 환경 (라이브러리 버전 · 하드웨어)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 하나라도 없으면 "왜 달라졌는지" 를 좁힐 수 없다</div>
    </div>
    <p>
      완전한 재현은 어렵다 —
      <a href="distributed-training.html">분산 학습</a>의 비결정적 축약,
      GPU 커널의 부동소수점 순서 때문에 같은 시드로도 미세하게 달라진다.
      그래도 <strong>어느 요소가 바뀌었는지 특정할 수 있는 수준</strong>은 확보해야 한다.
    </p>
    <div class="note">
      <b>데이터 문제를 모델 문제로 오인하기 쉽다.</b>
      성능이 떨어졌을 때 대개 모델부터 의심하는데,
      실제로는 <em>데이터 수집 경로가 바뀌었거나, 라벨 기준이 달라졌거나,
      전처리가 어긋난</em> 경우가 많다.
      <a href="mobile-runtime.html">배포 단계</a>에서 전처리 불일치가 흔한 원인이었던 것과 같은 구조다.
      <strong>데이터를 먼저 의심하는 습관</strong>이 시간을 아낀다.
    </div>
    <p>
      정리하면 데이터 파이프라인은 <em>"한 번 만들고 끝"</em>이 아니라
      배포 결과가 다시 수집으로 돌아오는 <strong>순환</strong>이다.
      그리고 그 순환을 돌리려면 <em>무엇이 언제 바뀌었는지</em>를 알아야 한다.
      모델 코드보다 이쪽이 프로젝트 수명을 좌우하는 경우가 많다.
    </p>
  </section>
"""

READING = [
    "Settles, <em>Active Learning Literature Survey</em> (2009) — 무엇을 라벨링할지 고르는 방법들의 정리.",
    "Northcutt et al., <em>Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks</em> (arXiv:2103.14749) — 유명 벤치마크의 라벨 오류 실태.",
    "Sculley et al., <em>Hidden Technical Debt in Machine Learning Systems</em> (NeurIPS 2015) — 데이터 의존성이 만드는 부채.",
    "Sambasivan et al., <em>Everyone wants to do the model work, not the data work</em> (CHI 2021) — 데이터 작업이 저평가되는 구조.",
    "Gebru et al., <em>Datasheets for Datasets</em> (arXiv:1803.09010) — 데이터셋을 문서화하는 방법.",
    "Kaufman et al., <em>Leakage in Data Mining</em> (ACM TKDD 2012) — 분할이 잘못돼 점수가 부풀려지는 경로.",
]

write(
    "data-pipeline.html",
    title="데이터 파이프라인 — 모델보다 오래 걸리는 일",
    eyebrow="Infrastructure · Data Operations",
    h1="데이터 파이프라인",
    subtitle="모델보다 오래 걸리는 일 — 수집·라벨링·검수의 순환",
    dek=(
        "모델 구조를 고르는 데는 하루, <strong>데이터를 모으고 라벨링하고 정제하는 데는 몇 달</strong>이다. "
        "그리고 성능을 가르는 것도 대개 후자다. "
        "게다가 이것은 일방향 작업이 아니라 "
        "<em>배포 결과가 다시 수집으로 돌아오는 순환</em>이다."
    ),
    spec=[
        ("구조", "순환 (일방향 아님)"),
        ("무엇을 라벨링", "불확실 + 대표성"),
        ("가장 효율적", "실패 사례에서 출발"),
        ("라벨 불일치", "없애지 말고 활용"),
        ("분할", "무작위 아닌 그룹 단위"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

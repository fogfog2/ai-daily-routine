#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f1", panel="#e6e6e9", ink="#16171a", **{
    "ink-soft": "#4f5157", "ink-faint": "#7e8086", "rule": "#d1d1d5",
    "rule-strong": "#adadb2", "accent": "#33566b", "accent-fill": "#dde7ee",
    "accent-line": "#527e97", "muted": "#84868b", "muted-fill": "#dfe0e3", "warn": "#a04628",
})
DARK = dict(paper="#101114", panel="#18191c", ink="#e6e7ea", **{
    "ink-soft": "#a2a4a9", "ink-faint": "#757880", "rule": "#212226", "rule-strong": "#383a40",
    "accent": "#7fb0cc", "accent-fill": "#132430", "accent-line": "#4d7f9b",
    "muted": "#86888e", "muted-fill": "#1a1b1e", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>왜 좋아졌는지 모르는 상태</h2>
    <p>
      <a href="data-pipeline.html">데이터 파이프라인</a>에서 <em>"어느 시점의 데이터로 학습했는지 모르면
      결과를 재현할 수 없다"</em>고 했다. 이 문제는 데이터에만 있는 것이 아니다.
    </p>
    <p>
      실험을 수십 번 돌리다 보면 흔히 이런 상태가 된다 —
      <strong>지난주 모델이 더 좋았는데 무엇을 바꿔서 그랬는지 모른다.</strong>
      학습률도 만졌고, 증강도 바꿨고, 데이터도 조금 늘렸는데
      그중 무엇이 효과였는지 특정할 수 없다.
    </p>
    <p>
      원인은 대개 <em>한 번에 여러 개를 바꾼 것</em>이다.
      그리고 무엇을 바꿨는지 기록이 없다.
    </p>
    <div class="eq">
      <span class="cap">실험 하나를 재현하려면 필요한 것</span>
      <div class="line">· 코드 커밋 해시</div>
      <div class="line">· 데이터셋 버전 &amp; 분할 방식</div>
      <div class="line">· 하이퍼파라미터 <strong>전부</strong> (기본값 포함)</div>
      <div class="line">· 난수 시드</div>
      <div class="line">· 환경 — 라이브러리 버전 · GPU 종류 · 드라이버</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 하나라도 빠지면 "왜 달라졌는지" 를 좁힐 수 없다</div>
    </div>
    <div class="note">
      <b>기본값이 특히 위험하다.</b> 명시적으로 넘긴 인자만 기록하면
      <em>라이브러리 기본값이 바뀌었을 때</em> 알아채지 못한다.
      설정을 <strong>해석된 최종 형태로</strong> 저장해야 한다 —
      "무엇을 지정했는가"가 아니라 "실제로 무슨 값으로 돌았는가"다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>완전한 재현은 불가능하다</h2>
    <p>
      기록을 다 남겨도 <strong>비트 단위로 같은 결과</strong>는 얻기 어렵다.
      이유가 여럿이고, 대부분 고칠 수 없다.
    </p>
    <ul>
      <li><strong>병렬 축약의 순서</strong> — GPU 가 여러 스레드의 결과를 더하는 순서가 실행마다 다르다. 부동소수점 덧셈은 <em>결합법칙이 성립하지 않으므로</em> 결과가 미세하게 달라진다</li>
      <li><strong>비결정적 커널</strong> — 일부 연산(atomicAdd 기반)은 원래 순서가 보장되지 않는다</li>
      <li><strong>라이브러리 자동 튜닝</strong> — 상황에 따라 다른 알고리즘을 고른다</li>
      <li><strong><a href="distributed-training.html">분산 학습</a></strong> — 통신 순서와 타이밍이 매번 다르다</li>
    </ul>
    <div class="eq">
      <span class="cap">부동소수점은 결합법칙을 어긴다</span>
      <div class="line">(a + b) + c&nbsp;&nbsp;≠&nbsp;&nbsp;a + (b + c)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 크기가 아주 다른 수를 더할 때 반올림 위치가 달라진다</div>
      <div class="line">// 수백만 번 누적되면 눈에 보이는 차이가 된다</div>
    </div>
    <p>
      결정적 모드를 켤 수는 있다. 다만 <em>느려지고</em>, 일부 연산은 대체 구현이 없어
      아예 못 쓰기도 한다. 그래서 실무의 목표는 비트 일치가 아니라
      <strong>"어느 요소가 바뀌었는지 특정할 수 있는 수준"</strong>이다.
    </p>
    <div class="note">
      <b>그래서 시드를 여러 개 돌려야 한다.</b> 같은 설정으로 시드만 바꿔 돌리면
      결과가 얼마나 흔들리는지 알 수 있다. 그 <em>변동 폭보다 작은 차이</em>는
      개선이 아니라 노이즈다.
      논문에서 0.3% 향상을 주장하는데 시드 간 편차가 0.8%라면 그 주장은 근거가 약하다.
      <a href="evaluation-benchmarks.html">평가 문서</a>에서 본 것과 같은 문제다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>한 번에 하나만 바꾼다</h2>
    <p>
      기록 다음으로 중요한 것은 <strong>실험 설계</strong>다.
      원칙은 단순하다 — <em>한 번에 하나씩 바꾼다.</em>
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="실험 설계 비교. 여러 요소를 동시에 바꾸면 어느 것이 효과였는지 알 수 없고, 하나씩 바꾸면 기여를 분리할 수 있다. 상호작용이 의심되면 조합을 따로 확인한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">한꺼번에 바꾸면</text>

            <rect x="24" y="30" width="120" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="84" y="46" text-anchor="middle" font-size="8" fill="var(--ink-soft)">기준 · 72.1%</text>

            <rect x="24" y="62" width="120" height="24" fill="var(--warn)" opacity="0.2" stroke="var(--warn)" stroke-width="1.2"/>
            <text x="84" y="78" text-anchor="middle" font-size="8" fill="var(--ink)">전부 바꿈 · 74.8%</text>

            <text x="160" y="52" font-size="8" fill="var(--ink-faint)">학습률 ↓ · 증강 추가 · 데이터 +2천장</text>
            <text x="160" y="70" font-size="8" fill="var(--warn)">+2.7% 는 어디서 왔나 — 알 수 없다</text>
            <text x="160" y="86" font-size="8" fill="var(--warn)">셋 중 하나가 해로웠을 수도 있다</text>

            <line x1="24" y1="104" x2="674" y2="104" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="124" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">하나씩 바꾸면 (ablation)</text>

            <g font-size="8">
              <rect x="24" y="136" width="120" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <text x="84" y="150" text-anchor="middle" fill="var(--ink-soft)">기준 · 72.1%</text>

              <rect x="24" y="162" width="120" height="20" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="84" y="176" text-anchor="middle" fill="var(--ink)">+ 학습률 ↓ · 73.9%</text>
              <text x="156" y="176" fill="var(--accent)">+1.8 ← 효과 있음</text>

              <rect x="24" y="188" width="120" height="20" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="84" y="202" text-anchor="middle" fill="var(--ink)">+ 증강 · 74.9%</text>
              <text x="156" y="202" fill="var(--accent)">+1.0 ← 효과 있음</text>

              <rect x="304" y="188" width="120" height="20" fill="var(--warn)" opacity="0.2" stroke="var(--warn)" stroke-width="1"/>
              <text x="364" y="202" text-anchor="middle" fill="var(--ink)">+ 데이터 · 74.8%</text>
              <text x="436" y="202" fill="var(--warn)">−0.1 ← 효과 없음</text>
            </g>

            <text x="304" y="140" font-size="8" fill="var(--ink-soft)">각 요소의 기여를 분리할 수 있다</text>
            <text x="304" y="156" font-size="8" fill="var(--ink-faint)">→ 데이터 추가는 이번엔 소용없었다</text>
            <text x="304" y="172" font-size="8" fill="var(--ink-faint)">→ 다음엔 다른 데이터를 시도한다</text>

            <text x="480" y="140" font-size="8" fill="var(--warn)">주의: 상호작용</text>
            <text x="480" y="156" font-size="8" fill="var(--ink-faint)">따로는 무해한데 함께면</text>
            <text x="480" y="168" font-size="8" fill="var(--ink-faint)">해로운 조합이 있다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>ablation</strong> — 요소를 하나씩 더하거나 빼며 기여를 분리한다.
        좋은 논문이 반드시 싣는 표이고, 실무에서도 같은 이유로 필요하다.
        다만 <em>순서에 따라 결과가 달라질 수 있다</em> —
        A 를 넣은 뒤의 B 효과와 그 반대가 다르면 <strong>상호작용</strong>이 있다는 뜻이다.
      </figcaption>
    </figure>

    <p>
      실험 개수가 많아지면 <strong>탐색 방식</strong>도 문제가 된다.
      격자 탐색은 조합이 지수적으로 늘고, 중요하지 않은 축에 시간을 낭비한다.
      무작위 탐색이 같은 예산에서 더 나은 결과를 낸다는 것이 알려져 있다 —
      <em>중요한 축에 더 많은 서로 다른 값을 시도하게</em> 되기 때문이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>무엇을 기록할 것인가</h2>
    <p>
      기록이 많을수록 좋은 것은 아니다. <strong>나중에 볼 것</strong>만 남기는 편이 낫다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>종류</th><th>예</th><th>왜</th></tr>
        </thead>
        <tbody>
          <tr><td>설정</td><td class="hi">해석된 최종 하이퍼파라미터 전체</td><td>재현의 전제</td></tr>
          <tr><td>지표 곡선</td><td>손실 · 검증 정확도 · 학습률</td><td class="hi">발산·과적합 시점을 본다</td></tr>
          <tr><td>시스템</td><td>GPU 사용률 · 메모리 · 시간</td><td>병목이 데이터 로딩인지 확인</td></tr>
          <tr><td class="hi">예측 표본</td><td class="hi">틀린 사례 이미지</td><td class="hi">숫자로 안 보이는 것을 본다</td></tr>
          <tr><td>산출물</td><td>체크포인트 · 환경 정보</td><td>나중에 되돌리기</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      네 번째 줄이 자주 빠진다. 검증 정확도만 보면
      <em>어떤 종류를 틀리는지</em> 알 수 없다.
      틀린 사례 몇십 장을 매번 남겨 두면
      <a href="data-pipeline.html">다음에 무엇을 라벨링할지</a>가 함께 보인다.
    </p>
    <div class="note">
      <b>GPU 사용률이 낮으면 모델 문제가 아니다.</b>
      학습이 느릴 때 배치를 줄이거나 모델을 작게 만들기 전에,
      <em>GPU 가 놀고 있는지</em> 확인해야 한다.
      데이터 로딩이 병목이면 워커 수·전처리·저장 형식을 손보는 편이 훨씬 효과적이다.
      <a href="mobile-runtime.html">배포 단계</a>에서 위임 로그를 먼저 보는 것과 같은 순서다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실험에서 배포까지</h2>
    <p>
      마지막으로 실험 관리가 <strong>배포와 이어지는 지점</strong>을 짚자.
    </p>
    <p>
      좋은 모델을 찾았다면 그것이 <em>어떤 조건에서 나온 것인지</em> 알아야 배포할 수 있다.
      체크포인트 파일 하나만 남아 있으면 —
      어떤 전처리를 쓰는지, 입력 크기가 얼마인지, 클래스 순서가 무엇인지 모른다.
    </p>
    <div class="eq">
      <span class="cap">체크포인트와 함께 저장해야 하는 것</span>
      <div class="line">· 전처리 설정 (크기 · 정규화 상수 · 색 순서)</div>
      <div class="line">· 클래스 목록과 <strong>순서</strong></div>
      <div class="line">· 학습 시점의 지표 (배포 후 비교 기준)</div>
      <div class="line">· <a href="similarity-threshold.html">임계값</a> — 있다면</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 이것들이 없으면 모델은 있어도 쓸 수가 없다</div>
    </div>
    <p>
      <a href="mobile-runtime.html">모바일 런타임</a>에서 <em>전처리 불일치가 가장 흔한 원인</em>이라고 했다.
      그 불일치는 대개 <strong>여기서 시작된다</strong> —
      학습 설정이 모델과 함께 저장되지 않아, 배포하는 쪽이 추측으로 맞추는 것이다.
    </p>
    <div class="note">
      <b>배포 후에도 실험은 끝나지 않는다.</b>
      운영 중 지표를 계속 재고, 학습 때 값과 비교해야 한다.
      <a href="similarity-threshold.html">점수 분포가 움직이는</a> 것처럼
      입력 분포도 서서히 변하기 때문이다.
      <a href="data-pipeline.html">데이터 파이프라인</a>이 순환이었듯,
      실험도 <em>배포 결과가 다음 실험의 입력이 되는</em> 순환으로 보는 편이 맞다.
    </div>
    <p>
      정리하면 실험 관리는 <em>기억을 시스템에 맡기는 일</em>이다.
      며칠 뒤의 나는 무엇을 바꿨는지 기억하지 못하고,
      <strong>재현할 수 없는 개선은 개선이 아니다</strong> — 우연과 구분되지 않기 때문이다.
      화려한 도구가 필요한 것은 아니고, 설정과 결과를 짝지어 남기는 습관이 대부분을 해결한다.
    </p>
  </section>
"""

READING = [
    "Bergstra &amp; Bengio, <em>Random Search for Hyper-Parameter Optimization</em> (JMLR 2012) — 격자보다 무작위가 나은 이유.",
    "Sculley et al., <em>Hidden Technical Debt in Machine Learning Systems</em> (NeurIPS 2015) — 설정과 재현성이 만드는 부채.",
    "Pineau et al., <em>Improving Reproducibility in Machine Learning Research</em> (arXiv:2003.12206) — NeurIPS 재현성 체크리스트의 배경.",
    "Henderson et al., <em>Deep Reinforcement Learning that Matters</em> (arXiv:1709.06560) — 시드 간 편차가 개선 주장을 삼키는 사례.",
    "Dodge et al., <em>Show Your Work: Improved Reporting of Experimental Results</em> (arXiv:1909.03004) — 탐색 예산을 함께 보고해야 하는 이유.",
]

write(
    "experiment-tracking.html",
    title="실험 관리 — 재현할 수 없는 개선은 개선이 아니다",
    eyebrow="Infrastructure · Reproducibility",
    h1="실험 관리",
    subtitle="재현할 수 없는 개선은 개선이 아니다 — 기억을 시스템에 맡기기",
    dek=(
        "실험을 수십 번 돌리면 흔히 이런 상태가 된다 — "
        "<strong>지난주 모델이 더 좋았는데 무엇을 바꿔서 그랬는지 모른다.</strong> "
        "게다가 비트 단위 재현은 원리적으로 어렵다. "
        "그래서 목표는 완전한 재현이 아니라 <em>어느 요소가 바뀌었는지 특정할 수 있는 수준</em>이다."
    ),
    spec=[
        ("문제", "무엇이 효과였는지 모름"),
        ("완전 재현", "부동소수점 때문에 어렵다"),
        ("현실적 목표", "변화 요소를 특정"),
        ("설계 원칙", "한 번에 하나씩"),
        ("자주 빠지는 것", "틀린 사례 · 기본값"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

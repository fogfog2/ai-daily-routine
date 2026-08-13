#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ee", panel="#e7e6e2", ink="#181613", **{
    "ink-soft": "#544f47", "ink-faint": "#837e74", "rule": "#d3d1cb",
    "rule-strong": "#afaca4", "accent": "#8a3b2e", "accent-fill": "#f3ddd6",
    "accent-line": "#b06050", "muted": "#82868c", "muted-fill": "#dee0e2", "warn": "#8a5a12",
})
DARK = dict(paper="#121110", panel="#1a1816", ink="#eae8e4", **{
    "ink-soft": "#aaa59d", "ink-faint": "#7c776f", "rule": "#25231f", "rule-strong": "#3b3830",
    "accent": "#e0897a", "accent-fill": "#301a15", "accent-line": "#a85f50",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#d9a441",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>분포는 반드시 겹친다</h2>
    <p>
      <a href="metric-learning.html">메트릭 러닝</a>으로 임베딩을 잘 학습했다고 하자.
      같은 품목 쌍의 유사도는 높고 다른 품목 쌍은 낮다.
      그런데 실제 분포를 그려 보면 <strong>두 분포가 겹친다</strong>. 언제나 겹친다.
    </p>
    <p>
      겹치지 않는다면 임계값을 아무 데나 두어도 완벽하게 갈린다.
      현실에서는 그런 일이 없다 — 조명이 나쁜 같은 품목 사진과
      비슷하게 생긴 다른 품목 사진의 점수가 뒤섞인다.
    </p>
    <p>
      그래서 <strong>임계값은 오류의 종류를 고르는 일</strong>이 된다.
      없앨 수는 없고, 어느 쪽 오류를 더 받아들일지 정하는 것뿐이다.
    </p>
    <div class="eq">
      <span class="cap">두 종류의 오류 — 서로 반대로 움직인다</span>
      <div class="line"><strong>FMR</strong>&nbsp; 오수락&nbsp; 다른 것을 같다고 판정</div>
      <div class="line"><strong>FNMR</strong> 오거부&nbsp; 같은 것을 다르다고 판정</div>
      <div class="line">&nbsp;</div>
      <div class="line">임계값을 올리면&nbsp; FMR ↓&nbsp; FNMR ↑</div>
      <div class="line">임계값을 내리면&nbsp; FMR ↑&nbsp; FNMR ↓</div>
    </div>
    <div class="note">
      <b>이름은 분야마다 다르지만 같은 것이다.</b>
      생체인식에서는 FMR/FNMR, 검색에서는 정밀도/재현율,
      통계에서는 1종/2종 오류라 부른다.
      <a href="evaluation-benchmarks.html">평가 문서</a>에서 본 것처럼,
      <em>무엇을 재고 있는지</em>만 정확히 알면 이름은 부차적이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>숫자로 보면 선택이 무거워진다</h2>
    <p>
      실제 분포를 가정해 계산해 보자.
      같은 쌍 5,000개와 다른 쌍 500,000개의 유사도를 재고
      임계값을 바꿔 가며 오류율을 본다.
    </p>
    <div class="eq">
      <span class="cap">임계값별 오류율</span>
      <div class="line">임계값&nbsp;&nbsp;&nbsp;&nbsp; FMR(오수락)&nbsp;&nbsp; FNMR(오거부)</div>
      <div class="line">&nbsp;0.55&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 20.274%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1.12%</div>
      <div class="line">&nbsp;0.65&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 4.743%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 8.98%</div>
      <div class="line">&nbsp;0.75&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0.608%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 37.96%</div>
      <div class="line">&nbsp;0.85&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0.037%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 75.14%</div>
    </div>
    <p>
      0.55에서 0.85로 올리면 오수락이 <strong>548배</strong> 줄지만
      오거부가 <strong>67배</strong> 는다. 공짜가 없다.
    </p>
    <p>
      두 오류율이 같아지는 지점을 <strong>EER</strong>(등오류율)이라 하고,
      위 분포에서는 임계값 약 <code>0.63</code> 근처다.
      모델 비교에는 편리한 단일 숫자지만,
      <em>실무에서 EER 을 그대로 쓰는 경우는 드물다</em> —
      두 오류의 비용이 같은 상황이 거의 없기 때문이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="같은 쌍과 다른 쌍의 유사도 분포가 겹치는 모습과 임계값 선택. 임계값을 올리면 오수락이 줄고 오거부가 늘며, 두 분포가 겹치는 구간에서는 어떤 임계값을 골라도 오류가 남는다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">두 분포는 반드시 겹친다</text>

            <line x1="50" y1="150" x2="500" y2="150" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="50" y="168" font-size="8" fill="var(--ink-faint)">0.0</text>
            <text x="484" y="168" font-size="8" fill="var(--ink-faint)">1.0</text>
            <text x="275" y="184" text-anchor="middle" font-size="8" fill="var(--ink-faint)">유사도 →</text>

            <path d="M60 150 C 130 148, 170 60, 230 60 C 290 60, 330 148, 400 150 Z" fill="var(--muted)" opacity="0.28"/>
            <text x="196" y="52" font-size="8" fill="var(--ink-soft)">다른 쌍 (많다)</text>

            <path d="M250 150 C 320 148, 360 74, 410 74 C 460 74, 480 148, 500 150 Z" fill="var(--accent)" opacity="0.35"/>
            <text x="412" y="66" font-size="8" fill="var(--accent)">같은 쌍</text>

            <path d="M250 150 C 290 149, 320 108, 350 104 C 380 112, 390 140, 400 150 Z" fill="var(--warn)" opacity="0.32"/>
            <text x="300" y="132" font-size="7.5" fill="var(--warn)">겹침</text>

            <line x1="352" y1="46" x2="352" y2="158" stroke="var(--ink)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <text x="358" y="44" font-size="8" fill="var(--ink)">임계값</text>

            <path d="M352 168 L300 168" stroke="var(--warn)" stroke-width="1.2"/>
            <text x="240" y="172" font-size="7.5" fill="var(--warn)">← 내리면 오수락 ↑</text>
            <path d="M352 168 L404 168" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="410" y="172" font-size="7.5" fill="var(--accent)">올리면 오거부 ↑ →</text>

            <line x1="530" y1="26" x2="530" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="552" y="46" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">겹치는 구간에서는</text>
            <text x="552" y="66" font-size="8.5" fill="var(--warn)">어떤 임계값을 골라도</text>
            <text x="552" y="80" font-size="8.5" fill="var(--warn)">오류가 남는다</text>

            <text x="552" y="106" font-size="8.5" fill="var(--ink-soft)">모델을 개선한다는 것은</text>
            <text x="552" y="120" font-size="8" fill="var(--ink-faint)">이 겹침을 줄이는 것이지</text>
            <text x="552" y="132" font-size="8" fill="var(--ink-faint)">임계값을 잘 고르는 게 아니다</text>

            <text x="552" y="158" font-size="8.5" fill="var(--accent)">임계값은 그 다음 문제 —</text>
            <text x="552" y="172" font-size="8" fill="var(--ink-faint)">남은 오류를 어느 쪽으로</text>
            <text x="552" y="184" font-size="8" fill="var(--ink-faint)">보낼지 정하는 일이다</text>

            <line x1="24" y1="200" x2="500" y2="200" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="220" font-size="8.5" fill="var(--ink-soft)">EER — 두 오류율이 같아지는 지점. <tspan fill="var(--ink-faint)">모델 비교엔 편하지만 실무 기준으로는 잘 안 쓴다</tspan></text>
            <text x="24" y="234" font-size="8" fill="var(--ink-faint)">두 오류의 비용이 같은 상황이 거의 없기 때문이다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>모델 개선과 임계값 선택은 다른 일이다.</strong>
        좋은 모델은 두 분포의 <em>겹침을 줄인다</em>.
        임계값은 그러고도 남은 겹침에서 <em>어느 쪽 오류를 감수할지</em> 고르는 손잡이일 뿐이다.
        임계값 조정으로 해결되지 않는 문제를 임계값으로 풀려 하면 끝이 없다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">03</span>규모가 커지면 같은 임계값이 무너진다</h2>
    <p>
      여기가 실무에서 가장 자주 놓치는 지점이다.
      <strong>임계값은 후보 개수에 의존한다.</strong>
    </p>
    <p>
      1:1 검증(이 둘이 같은가)과 1:N 검색(이 중에 있는가)은 다르다.
      검색에서는 <em>모든 후보와 비교</em>하므로, 오수락 기회가 후보 수만큼 생긴다.
    </p>
    <div class="eq">
      <span class="cap">FMR 0.608% (임계값 0.75) 일 때 — 검색 한 번당 기대 오수락</span>
      <div class="line">후보&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 100 개&nbsp;&nbsp;→&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0.6 건</div>
      <div class="line">후보&nbsp;&nbsp; 10,000 개&nbsp;&nbsp;→&nbsp;&nbsp;&nbsp;&nbsp; 60.8 건</div>
      <div class="line">후보 1,000,000 개&nbsp;&nbsp;→&nbsp;&nbsp; <strong>6,082 건</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 모델도 임계값도 그대로인데 결과가 쓸모없어진다</div>
    </div>
    <p>
      후보 100개에서 잘 돌던 시스템을 100만 개로 확장하면,
      <em>검색할 때마다 6천 건의 오수락</em>이 상위에 섞인다.
      1등만 본다 해도 그중 하나일 확률이 높아진다.
    </p>
    <div class="note">
      <b>그래서 규모가 커지면 임계값을 다시 잡아야 한다.</b>
      필요한 FMR 이 <code>1/N</code> 수준으로 내려가야 하므로,
      <em>훨씬 엄격한 임계값</em>이 필요하고 그만큼 오거부가 는다.
      대규모 검색에서 <strong>모델 성능 요구가 급격히 높아지는</strong> 이유다 —
      단순히 데이터가 많아서가 아니라 오류 예산이 <code>N</code>으로 나뉘기 때문이다.
    </div>
    <p>
      그래서 실무 지표도 이 형태를 쓴다.
      <em>"FMR 이 1e-4 일 때의 TAR"</em> 처럼 <strong>오수락률을 고정하고 재현율을 보는</strong> 방식이다.
      단일 정확도 숫자는 임계값에 따라 달라져 비교에 쓸 수 없다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>어디에 둘 것인가 — 비용이 정한다</h2>
    <p>
      임계값은 통계가 아니라 <strong>비용이 정한다</strong>.
      두 오류가 각각 얼마짜리인지 따져야 한다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>상황</th><th>더 나쁜 오류</th><th>임계값</th></tr>
        </thead>
        <tbody>
          <tr><td>결제·출입 인증</td><td class="hi">오수락 (타인 통과)</td><td>높게</td></tr>
          <tr><td>사진 자동 분류</td><td>오거부 (분류 누락)</td><td class="hi">낮게</td></tr>
          <tr><td>검색 후보 추리기</td><td>오거부 (후보 누락)</td><td class="hi">낮게 — 사람이 최종 판단</td></tr>
          <tr><td>중복 제거</td><td class="hi">오수락 (다른 것을 병합)</td><td>높게 — 되돌리기 어렵다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄의 기준이 일반적으로 유용하다.
      <strong>되돌릴 수 있는 오류인가</strong>를 먼저 묻는 것이다.
      사람이 나중에 걸러낼 수 있으면 느슨하게 두고,
      한번 잘못되면 복구가 어려우면 엄격하게 둔다.
      <a href="ai-agents-tool-use.html">에이전트 설계</a>에서 본 판단 기준과 같다.
    </p>
    <p>
      <strong>두 단계 구성</strong>도 흔하다. 임계값을 하나가 아니라 둘 두는 것이다.
    </p>
    <div class="eq">
      <span class="cap">애매한 구간을 따로 뺀다</span>
      <div class="line">점수 ≥ 0.85&nbsp;&nbsp;→ 자동 승인</div>
      <div class="line">0.60 ~ 0.85&nbsp;&nbsp;→ <strong>사람 검토</strong></div>
      <div class="line">점수 &lt; 0.60&nbsp;&nbsp;→ 자동 거부</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 겹치는 구간만 사람에게 넘긴다 — 전수 검토보다 훨씬 싸다</div>
    </div>
    <p>
      겹침이 전체의 몇 %뿐이라면 검토 부담이 그만큼만 생긴다.
      <em>자동화율과 정확도를 함께</em> 관리할 수 있어 실무에서 널리 쓰인다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>임계값은 고정값이 아니다</h2>
    <p>
      한 번 정하면 끝이 아니라는 점이 마지막 주제다.
      <strong>점수 분포는 계속 움직인다.</strong>
    </p>
    <ul>
      <li><strong>카메라·조명이 바뀌면</strong> 같은 쌍의 점수가 통째로 내려간다</li>
      <li><strong>등록 데이터가 늘면</strong> 다른 쌍의 최댓값이 올라간다 (앞 절의 규모 효과)</li>
      <li><strong>모델을 바꾸면</strong> 점수의 스케일 자체가 달라진다 — 이전 임계값은 무의미하다</li>
      <li><strong>계절·시간대</strong>에 따라서도 분포가 흔들린다</li>
    </ul>
    <div class="note">
      <b>모델 교체 시 임계값을 그대로 쓰는 것이 흔한 사고다.</b>
      새 모델이 더 좋아도 점수 분포가 다르면 같은 임계값에서 전혀 다른 오류율이 나온다.
      <em>모델과 임계값은 한 쌍</em>으로 관리해야 하고,
      배포 전에 반드시 새로 잡아야 한다.
    </div>
    <p>
      그래서 운영에서는 <strong>점수 분포 자체를 모니터링</strong>한다.
      평균·분위수가 평소와 다르게 움직이면 조건이 바뀐 신호다.
      정확도 지표는 라벨이 있어야 계산되지만,
      <em>점수 분포는 라벨 없이도 볼 수 있어</em> 조기 경보로 쓸모가 있다.
    </p>
    <div class="note">
      <b>임계값을 아예 한 번에 정하지 않는 길도 있다.</b>
      <a href="object-tracking.html">다중 객체 추적</a>의 ByteTrack 은
      검출 점수를 높음·낮음 두 구간으로 나눠
      <em>높은 쪽으로 먼저 연결하고, 남은 것만 낮은 쪽에서 다시 찾는다.</em>
      겹치는 구간을 버리는 대신 <strong>다음 단계의 맥락으로 넘겨</strong> 판단을 미루는 방식이라,
      한 임계값으로 잘라야 할 때보다 잃는 것이 적다.
    </div>
    <p>
      점수를 그대로 쓰지 않고 <strong>보정</strong>하는 방법도 있다.
      코사인 유사도 0.8이 "80% 확률로 같다"는 뜻은 아니다.
      검증 데이터로 점수를 확률에 대응시켜 두면
      <em>임계값을 확률 기준으로</em> 정할 수 있어 해석과 이관이 쉬워진다.
    </p>
    <p>
      정리하면 임계값 설정은 <em>모델 문제가 아니라 제품 문제</em>다.
      좋은 모델은 두 분포의 겹침을 줄이지만, 겹침을 0으로 만들지는 못한다.
      남은 겹침을 <strong>어느 쪽 오류로 보낼지</strong>는
      비용과 되돌릴 수 있는지가 정하고, 그것은 공학이 아니라 운영의 판단이다.
    </p>
  </section>
"""

READING = [
    "Jain et al., <em>An Introduction to Biometric Recognition</em> (IEEE TCSVT 2004) — FMR/FNMR 과 운영점 설정의 고전적 정리.",
    "Grother et al., <em>Face Recognition Vendor Test (FRVT) Part 2: Identification</em> (NIST IR 8271) — 1:N 검색에서 갤러리 크기가 미치는 영향의 실측.",
    "Fawcett, <em>An introduction to ROC analysis</em> (Pattern Recognition Letters 2006) — ROC·AUC 의 의미와 오용.",
    "Guo et al., <em>On Calibration of Modern Neural Networks</em> (arXiv:1706.04599) — 점수를 확률로 보정하는 문제.",
    "Saito &amp; Rehmsmeier, <em>The Precision-Recall Plot Is More Informative than the ROC Plot</em> (PLOS ONE 2015) — 불균형 데이터에서 지표 선택.",
]

write(
    "similarity-threshold.html",
    title="유사도 임계값 — 어디서 자를 것인가",
    eyebrow="Vision · Evaluation · Operations",
    h1="유사도 임계값",
    subtitle="어디서 자를 것인가 — 겹치는 구간에서는 오류를 고를 뿐이다",
    dek=(
        "같은 품목 쌍과 다른 품목 쌍의 점수 분포는 <strong>반드시 겹친다</strong>. "
        "그래서 임계값 설정은 오류를 없애는 일이 아니라 "
        "<em>어느 쪽 오류를 감수할지 고르는</em> 일이다. "
        "게다가 후보가 100개에서 100만 개로 늘면, 같은 임계값에서 "
        "검색당 오수락이 0.6건에서 <strong>6,000건</strong>이 된다."
    ),
    spec=[
        ("전제", "두 분포는 겹친다"),
        ("두 오류", "FMR ↔ FNMR"),
        ("규모 의존", "오류 예산이 N 으로 나뉜다"),
        ("정하는 것", "통계가 아니라 비용"),
        ("주의", "모델 바꾸면 다시 잡는다"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

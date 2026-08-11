#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ef", panel="#e7e6e3", ink="#1a1615", **{
    "ink-soft": "#555049", "ink-faint": "#847e77", "rule": "#d4d1cd",
    "rule-strong": "#b0aca6", "accent": "#8c3520", "accent-fill": "#f4dcd4",
    "accent-line": "#b05f48", "muted": "#82868c", "muted-fill": "#dee0e2", "warn": "#8a5a12",
})
DARK = dict(paper="#121110", panel="#1a1817", ink="#eae8e5", **{
    "ink-soft": "#aaa59f", "ink-faint": "#7c7770", "rule": "#252320", "rule-strong": "#3b3833",
    "accent": "#e08872", "accent-fill": "#301813", "accent-line": "#a85c48",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#d9a441",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>보이지 않는 변화로 답이 뒤집힌다</h2>
    <p>
      95% 정확도의 분류기가 있다. 여기에 <strong>사람 눈에 안 보이는 노이즈</strong>를 더하면
      정확도가 <em>0%에 가깝게</em> 떨어진다. 이것이 적대적 예제다.
    </p>
    <p>
      "안 보이는"의 크기를 숫자로 보면 감이 온다.
      벤치마크에서 흔히 쓰는 값은 <code>ε = 8/255</code> 다.
    </p>
    <div class="eq">
      <span class="cap">섭동의 크기 — 픽셀당 최대 변화</span>
      <div class="line">ε = 8/255 ≈ 0.031&nbsp;&nbsp;&nbsp;// 0~1 범위에서 약 3%</div>
      <div class="line">&nbsp;</div>
      <div class="line">픽셀값 0~255 기준으로 <strong>최대 ±8</strong></div>
      <div class="line">// JPEG 압축 아티팩트보다도 작은 경우가 많다</div>
    </div>
    <p>
      중요한 것은 이것이 <em>무작위 노이즈가 아니라는</em> 점이다.
      무작위로 ±8 을 흔들면 정확도는 거의 안 떨어진다.
      적대적 예제는 <strong>손실이 가장 크게 오르는 방향</strong>으로 계산된 것이다.
    </p>
    <div class="note">
      <b>모델의 그래디언트를 모델에게 쓰는 것이다.</b>
      학습에서는 손실을 <em>줄이는</em> 방향으로 가중치를 갱신한다.
      공격은 같은 그래디언트를 <em>입력</em>에 대해 계산하고,
      손실을 <strong>키우는</strong> 방향으로 입력을 민다.
      학습을 가능하게 한 바로 그 도구가 공격 도구가 된다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>왜 이런 일이 생기나</h2>
    <p>
      초기 설명은 <em>"신경망이 너무 복잡해서 이상한 구멍이 생긴다"</em>였다.
      그런데 후속 연구는 반대에 가까운 답을 내놨다 —
      <strong>모델이 지나치게 선형적이기 때문</strong>이다.
    </p>
    <p>
      고차원 입력에서는 각 차원을 아주 조금씩만 밀어도
      <em>선형 결합의 합</em>이 크게 움직인다.
      784차원 입력에서 각 픽셀을 0.03 씩 밀면 내적은 20 이상 변할 수 있다.
    </p>
    <div class="eq">
      <span class="cap">차원이 높으면 작은 변화가 쌓인다</span>
      <div class="line">wᵀ(x + η) = wᵀx + wᵀη</div>
      <div class="line">&nbsp;</div>
      <div class="line">η = ε · sign(w) 로 두면&nbsp; wᵀη = ε · Σ|w<sub>i</sub>|</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 차원 n 이 크면 ε 가 작아도 합이 커진다</div>
    </div>
    <p>
      더 흥미로운 설명은 <strong>"적대적 특징도 진짜 특징"</strong>이라는 관점이다.
      데이터에는 <em>사람은 못 보지만 실제로 예측에 유용한</em> 패턴이 있고,
      모델은 그것도 학습한다. 그 패턴은 <strong>깨지기 쉬워서</strong>
      작은 섭동으로 뒤집힌다.
    </p>
    <div class="note">
      <b>이 관점이 왜 중요한가.</b> 적대적 취약성이 <em>버그가 아니라
      데이터의 성질</em>이라는 뜻이 된다.
      모델이 잘못 배운 것이 아니라, <strong>일반화에 실제로 도움이 되는 것</strong>을 배웠는데
      그것이 사람의 지각과 어긋날 뿐이다.
      그래서 강건성을 얻으려면 <em>정확도를 내줘야</em> 하는 구조적 이유가 생긴다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>공격과 방어의 비대칭</h2>
    <p>
      이 분야의 역사는 <strong>방어가 제안되고 곧 뚫리는</strong> 반복이었다.
      그리고 뚫린 이유가 대체로 같았다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 232" role="img" aria-label="그래디언트 마스킹으로 인한 거짓 방어. 그래디언트를 못 쓰게 만들면 그래디언트 기반 공격은 실패하지만 모델 자체는 여전히 취약하며, 그래디언트를 우회하는 공격으로 뚫린다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ad-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="ad-w" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--warn)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">거짓 방어 — 그래디언트 마스킹</text>

            <rect x="24" y="32" width="90" height="28" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="69" y="50" text-anchor="middle" font-size="8" fill="var(--ink-soft)">방어 추가</text>
            <text x="24" y="76" font-size="7.5" fill="var(--ink-faint)">양자화·무작위화·비미분 전처리</text>

            <path d="M122 46 L146 46" stroke="var(--warn)" stroke-width="1.2" marker-end="url(#ad-w)"/>

            <rect x="150" y="32" width="120" height="28" fill="var(--warn)" opacity="0.2" stroke="var(--warn)" stroke-width="1.2"/>
            <text x="210" y="50" text-anchor="middle" font-size="8" fill="var(--ink)">그래디언트가 쓸모없어짐</text>

            <path d="M278 46 L302 46" stroke="var(--warn)" stroke-width="1.2" marker-end="url(#ad-w)"/>
            <rect x="306" y="32" width="110" height="28" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="361" y="50" text-anchor="middle" font-size="8" fill="var(--ink-soft)">공격 실패 → "방어됨"</text>

            <path d="M424 46 L448 46" stroke="var(--warn)" stroke-width="1.4" marker-end="url(#ad-w)"/>
            <rect x="452" y="32" width="120" height="28" fill="var(--warn)" opacity="0.28" stroke="var(--warn)" stroke-width="1.4"/>
            <text x="512" y="50" text-anchor="middle" font-size="8" fill="var(--ink)">우회 공격에 뚫림</text>

            <text x="24" y="98" font-size="8" fill="var(--warn)">모델은 여전히 취약한데 <tspan fill="var(--warn)">공격 도구만 막은 것</tspan>이다</text>
            <text x="24" y="112" font-size="8" fill="var(--ink-faint)">근사 그래디언트·전이 공격·질의 기반 공격으로 우회된다</text>

            <line x1="24" y1="128" x2="674" y2="128" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="148" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">제대로 평가하려면</text>

            <g font-size="8.5">
              <text x="24" y="170" fill="var(--ink-soft)">· <tspan fill="var(--accent)">적응적 공격</tspan> — 그 방어를 <em>알고</em> 설계된 공격으로 시험한다</text>
              <text x="24" y="188" fill="var(--ink-soft)">· 여러 공격을 <tspan fill="var(--accent)">모두</tspan> 돌리고 <em>가장 나쁜 결과</em>를 보고한다</text>
              <text x="24" y="206" fill="var(--ink-soft)">· 반복 횟수·초기값을 충분히 — 약한 공격은 방어를 과대평가한다</text>
              <text x="24" y="224" fill="var(--warn)">· 그래디언트가 이상하면(무작위 시작이 크게 다르면) 마스킹을 의심한다</text>
            </g>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>그래디언트 마스킹</strong>이 거짓 방어의 전형이다.
        전처리를 비미분으로 만들거나 무작위성을 넣으면
        <em>그래디언트 기반 공격은 실패</em>하지만 모델 자체는 그대로 취약하다.
        수십 개의 방어가 이 방식으로 무너졌고,
        그래서 <em>적응적 공격으로 시험하지 않은 방어는 신뢰하지 않는다</em>는 것이 원칙이 됐다.
      </figcaption>
    </figure>

    <p>
      비대칭이 근본적이다. 방어는 <em>모든 공격</em>을 막아야 하고,
      공격은 <em>하나만</em> 통하면 된다.
      <a href="prompt-injection.html">프롬프트 인젝션</a>에서 본 것과 같은 구조다 —
      필터를 우회하는 표현이 무한하다는 점에서.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>실제로 통하는 방어와 그 대가</h2>
    <p>
      검증을 견딘 방어는 사실상 하나다 — <strong>적대적 학습</strong>.
      학습 중에 적대적 예제를 만들어 <em>그것으로 학습</em>시킨다.
    </p>
    <div class="eq">
      <span class="cap">최소최대 문제 — 안쪽은 공격, 바깥쪽은 학습</span>
      <div class="line">min<sub>θ</sub>&nbsp; E<sub>(x,y)</sub> [ <strong>max</strong><sub>‖δ‖≤ε</sub> L( f<sub>θ</sub>(x+δ), y ) ]</div>
      <div class="line">&nbsp;</div>
      <div class="line">안쪽 max: 가장 나쁜 섭동을 찾는다 (공격)</div>
      <div class="line">바깥쪽 min: 그 상황에서도 맞히도록 학습</div>
    </div>
    <p>
      대가가 크다. 매 스텝마다 공격을 <em>수십 번 반복</em>해 만들어야 하므로
      <strong>학습 비용이 몇 배에서 십수 배</strong>가 된다.
      그리고 더 근본적인 대가가 있다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th></th><th>깨끗한 정확도</th><th>강건 정확도</th></tr>
        </thead>
        <tbody>
          <tr><td>표준 학습</td><td class="hi">높다</td><td class="hi">거의 0</td></tr>
          <tr><td>적대적 학습</td><td>눈에 띄게 떨어진다</td><td class="hi">상당히 회복</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>깨끗한 정확도를 내주고 강건성을 산다.</strong>
      이것이 단순한 튜닝 문제가 아니라 <em>트레이드오프</em>라는 것이
      이론적·실증적으로 논의돼 왔다.
      앞 절의 <em>"적대적 특징도 유용한 특징"</em> 관점에서 보면 자연스럽다 —
      유용한 것을 버리라고 강제하니 성능이 떨어지는 것이다.
    </p>
    <div class="note">
      <b>ε 을 정하는 것이 곧 위협 모델을 정하는 것이다.</b>
      L∞ 8/255 로 학습한 모델은 <em>그 반경 안에서만</em> 강건하다.
      다른 노름(L2)이나 <strong>회전·밝기·번짐</strong> 같은 변환에는 여전히 약할 수 있다.
      "강건하다"는 말은 <em>무엇에 대해</em>를 빼면 의미가 없다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실무에서 무엇이 문제인가</h2>
    <p>
      마지막으로 <strong>이 위협이 실제로 얼마나 문제인지</strong>를 짚자.
      과장하기도 과소평가하기도 쉬운 주제다.
    </p>
    <p>
      L∞ 섭동은 <em>공격자가 입력 픽셀을 직접 조작할 수 있을 때</em>의 이야기다.
      카메라로 촬영하는 시스템에서는 그 전제가 성립하지 않는 경우가 많다.
    </p>
    <p>
      대신 <strong>물리적 공격</strong>이 실질적 위협이다.
      인쇄한 무늬를 붙이거나(패치), 표지판에 스티커를 붙이거나,
      옷에 특정 무늬를 넣어 <em>검출을 회피</em>하는 형태다.
      이쪽은 픽셀 조작 없이 <strong>실제 세계에서</strong> 작동한다.
    </p>
    <div class="eq">
      <span class="cap">위협 모델을 먼저 정한다</span>
      <div class="line">· 공격자가 <strong>입력에 접근</strong>할 수 있나 (API vs 카메라)</div>
      <div class="line">· 모델 내부를 <strong>아는가</strong> (화이트박스 vs 블랙박스)</div>
      <div class="line">· <strong>질의</strong>를 몇 번 던질 수 있나</div>
      <div class="line">· 성공하면 <strong>무엇을 얻는가</strong> — 이득이 없으면 공격도 없다</div>
    </div>
    <p>
      그리고 실무에서 더 흔한 문제는 <em>악의적 공격이 아니라</em>
      <strong>자연적 분포 이동</strong>이다.
      비·역광·다른 카메라·계절 변화에서 성능이 떨어지는 것 —
      <a href="person-reid.html">Re-ID 의 도메인 격차</a>에서 본 문제다.
    </p>
    <div class="note">
      <b>둘은 연결돼 있다.</b> 적대적 학습이
      <em>자연적 손상에 대한 강건성도 함께 올린다</em>는 보고가 있고,
      반대로 <a href="curriculum-data-quality.html">데이터 증강</a>을 다양하게 하면
      적대적 강건성이 조금 오르기도 한다.
      완전히 같지는 않지만 <strong>"학습 분포를 벗어난 입력을 어떻게 다룰 것인가"</strong>라는
      같은 물음의 두 얼굴이다.
    </div>
    <p>
      정리하면 적대적 예제는 <em>모델이 사람과 다른 것을 본다</em>는 사실을
      가장 극적으로 드러내는 현상이다.
      완전한 방어는 없고, 적대적 학습은 정확도를 대가로 요구하며,
      <strong>무엇에 대해 강건해야 하는지를 먼저 정하는 것</strong>이 실무의 출발점이다.
      <a href="evaluation-benchmarks.html">평가</a>가 그랬듯, 여기서도
      <em>측정 대상을 정의하는 일이 절반</em>이다.
    </p>
  </section>
"""

READING = [
    "Szegedy et al., <em>Intriguing properties of neural networks</em> (arXiv:1312.6199) — 적대적 예제의 발견.",
    "Goodfellow et al., <em>Explaining and Harnessing Adversarial Examples</em> (arXiv:1412.6572) — 선형성 가설과 FGSM.",
    "Madry et al., <em>Towards Deep Learning Models Resistant to Adversarial Attacks</em> (arXiv:1706.06083) — 최소최대 정식화와 PGD 적대적 학습.",
    "Athalye et al., <em>Obfuscated Gradients Give a False Sense of Security</em> (arXiv:1802.00420) — 그래디언트 마스킹으로 무너진 방어들.",
    "Ilyas et al., <em>Adversarial Examples Are Not Bugs, They Are Features</em> (arXiv:1905.02175) — 취약성이 데이터의 성질이라는 관점.",
    "Tsipras et al., <em>Robustness May Be at Odds with Accuracy</em> (arXiv:1805.12152) — 정확도와 강건성의 트레이드오프.",
]

write(
    "adversarial-robustness.html",
    title="적대적 예제 — 보이지 않는 변화로 답이 뒤집힌다",
    eyebrow="Evaluation · Robustness · 2013–2026",
    h1="적대적 예제와 강건성",
    subtitle="보이지 않는 변화로 답이 뒤집힌다 — 버그인가 데이터의 성질인가",
    dek=(
        "픽셀당 최대 <code>±8</code> — JPEG 아티팩트보다 작은 변화로 "
        "95% 정확도가 거의 0이 된다. "
        "무작위 노이즈로는 안 되고, <strong>손실이 가장 크게 오르는 방향</strong>으로 계산해야 한다. "
        "학습을 가능하게 한 그래디언트가 그대로 공격 도구가 되는 셈이다."
    ),
    spec=[
        ("표준 섭동", "L∞ ε = 8/255"),
        ("원인 가설", "고차원 선형성"),
        ("다른 관점", "적대적 특징도 유용한 특징"),
        ("유일한 방어", "적대적 학습"),
        ("대가", "깨끗한 정확도 하락"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

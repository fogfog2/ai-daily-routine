#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0ee", panel="#e6e6e2", ink="#181713", **{
    "ink-soft": "#535046", "ink-faint": "#827e74", "rule": "#d2d1cb",
    "rule-strong": "#aeaca4", "accent": "#8a5510", "accent-fill": "#f2e7cd",
    "accent-line": "#b08030", "muted": "#83868c", "muted-fill": "#dee0e2", "warn": "#9c3f22",
})
DARK = dict(paper="#121110", panel="#1a1916", ink="#e9e8e2", **{
    "ink-soft": "#a8a69a", "ink-faint": "#7b786e", "rule": "#24231e", "rule-strong": "#3a3830",
    "accent": "#dfab5c", "accent-fill": "#2d2413", "accent-line": "#a87f38",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>가중치는 보면 되지만 활성값은 그렇지 않다</h2>
    <p>
      <a href="ondevice-quantization.html">온디바이스 양자화</a>에서 봤듯,
      정수로 곱하려면 <strong>활성값에도 스케일이 필요하다</strong>.
      그런데 활성값의 범위를 어떻게 알 것인가.
    </p>
    <p>
      가중치는 쉽다. 학습이 끝나면 값이 고정이므로 <em>그냥 보면 된다</em>.
      최댓값을 읽어 스케일을 계산하면 끝이다.
    </p>
    <p>
      활성값은 <strong>입력에 따라 달라진다</strong>. 밝은 사진과 어두운 사진,
      복잡한 장면과 단순한 장면에서 중간 층의 값 범위가 다르다.
      그런데 배포된 모델은 <em>어떤 입력이 올지 모른 채</em> 스케일을 미리 정해 두어야 한다.
    </p>
    <div class="eq">
      <span class="cap">캘리브레이션이 하는 일</span>
      <div class="line">1) 대표 입력 몇백 장을 모델에 흘려보낸다</div>
      <div class="line">2) 각 층의 활성값 <strong>분포를 관찰</strong>한다</div>
      <div class="line">3) 그 분포에서 스케일을 정한다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 학습이 아니다 — 순전파만 하고 통계만 모은다</div>
      <div class="line">// 그래서 라벨이 필요 없고, 수백 장이면 충분하다</div>
    </div>
    <p>
      학습을 다시 돌리지 않아도 된다는 점이 <strong>PTQ</strong>(학습 후 양자화)를 값싸게 만든다.
      라벨 없는 이미지 몇백 장과 순전파 몇 분이면 된다.
      <a href="qat.html">QAT</a> 로 가기 전에 이것부터 시도하는 이유다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>범위를 어디서 자를 것인가</h2>
    <p>
      분포를 봤다고 스케일이 저절로 정해지지는 않는다.
      <strong>최댓값을 쓸 것인가, 잘라낼 것인가.</strong>
    </p>
    <p>
      실제 분포로 계산해 보면 선택의 무게가 드러난다.
      활성값 10,000개 중 대부분이 <code>|x| &lt; 4</code> 인데 아웃라이어가 둘 섞인 경우다.
    </p>
    <div class="eq">
      <span class="cap">캘리브레이션 방식별 결과</span>
      <div class="line">방식&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;범위&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;스케일&nbsp;&nbsp;&nbsp;잘리는 값</div>
      <div class="line">min-max&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 52.00&nbsp;&nbsp; 0.4094&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0개</div>
      <div class="line">99.99% 분위수&nbsp;&nbsp; 47.00&nbsp;&nbsp; 0.3701&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1개</div>
      <div class="line"><strong>99.9% 분위수&nbsp;&nbsp;&nbsp; 3.21&nbsp;&nbsp; 0.0253&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 10개</strong></div>
      <div class="line">99% 분위수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2.55&nbsp;&nbsp; 0.0201&nbsp;&nbsp;&nbsp;&nbsp; 100개</div>
    </div>
    <p>
      세 번째 줄이 결정적이다. 99.99% 에서 99.9% 로 한 칸 내렸을 뿐인데
      <strong>스케일이 약 16배 작아진다</strong>. 해상도가 16배 좋아진다는 뜻이다.
      대가는 10,000개 중 <em>10개가 잘리는</em> 것뿐이다.
    </p>
    <div class="note">
      <b>왜 이렇게 급격한가.</b> 아웃라이어는 <em>분포의 꼬리에 몇 개만</em> 있다.
      그 몇 개를 포기하는 순간 범위가 본체 크기로 줄어든다.
      반대로 말하면, <strong>최댓값을 그대로 쓰는 것은 몇 개를 위해 나머지 전부를 희생하는 것</strong>이다.
      min-max 가 안전해 보이지만 실제로는 가장 나쁜 선택인 경우가 많다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>무엇을 최소화할 것인가</h2>
    <p>
      분위수를 손으로 고르는 대신, <strong>오차를 정의하고 최소화</strong>하는 방식도 쓰인다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="캘리브레이션 방식의 트레이드오프. 범위를 넓게 잡으면 아무것도 잘리지 않지만 해상도가 나빠지고, 좁게 잡으면 해상도는 좋아지지만 잘리는 값이 생긴다. 두 오차의 합이 최소가 되는 지점을 찾는 것이 목표다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">두 종류의 오차가 반대로 움직인다</text>

            <line x1="60" y1="40" x2="60" y2="150" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <line x1="60" y1="150" x2="360" y2="150" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="30" y="46" font-size="8" fill="var(--ink-faint)">오차</text>
            <text x="60" y="168" font-size="8" fill="var(--ink-faint)">좁게</text>
            <text x="320" y="168" font-size="8" fill="var(--ink-faint)">넓게 (min-max)</text>
            <text x="176" y="182" text-anchor="middle" font-size="8" fill="var(--ink-faint)">범위를 어디까지 잡는가 →</text>

            <path d="M70 60 C 110 100, 160 138, 350 146" fill="none" stroke="var(--warn)" stroke-width="2"/>
            <text x="200" y="132" font-size="8" fill="var(--warn)">클리핑 오차 — 자른 값이 틀린다</text>

            <path d="M70 146 C 160 140, 240 100, 350 58" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <text x="240" y="76" font-size="8" fill="var(--accent)">반올림 오차 — 해상도가 나빠진다</text>

            <path d="M70 52 C 130 78, 180 82, 350 52" fill="none" stroke="var(--ink-soft)" stroke-width="2" stroke-dasharray="4 3"/>
            <circle cx="186" cy="80" r="4" fill="var(--ink)"/>
            <text x="196" y="72" font-size="8" fill="var(--ink)">합이 최소인 지점</text>

            <line x1="400" y1="30" x2="400" y2="200" stroke="var(--rule)" stroke-width="1"/>

            <text x="424" y="46" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">찾는 방법</text>

            <text x="424" y="70" font-size="8.5" fill="var(--ink-soft)">① 분위수 — 99.9% 등을 시험</text>
            <text x="424" y="84" font-size="8" fill="var(--ink-faint)">값싸고 대개 충분하다</text>

            <text x="424" y="106" font-size="8.5" fill="var(--ink-soft)">② MSE 최소화</text>
            <text x="424" y="120" font-size="8" fill="var(--ink-faint)">여러 범위를 시험해 양자화 전후</text>
            <text x="424" y="132" font-size="8" fill="var(--ink-faint)">텐서의 제곱오차가 작은 것을 고른다</text>

            <text x="424" y="154" font-size="8.5" fill="var(--ink-soft)">③ KL 발산 최소화</text>
            <text x="424" y="168" font-size="8" fill="var(--ink-faint)">양자화 전후 <em>분포</em>가 닮게 한다</text>
            <text x="424" y="180" font-size="8" fill="var(--ink-faint)">TensorRT 가 쓰는 방식</text>

            <text x="424" y="200" font-size="8" fill="var(--warn)">셋 다 대리 지표다 — 최종 정확도는 따로 확인</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        범위를 넓히면 <strong>클리핑 오차</strong>가 줄고 <strong>반올림 오차</strong>가 는다. 좁히면 반대다.
        둘의 합이 최소인 지점을 찾는 것이 캘리브레이션의 목표인데,
        <em>어느 오차가 최종 정확도에 더 해로운지는 층마다 다르다</em> — 그래서 실측이 필요하다.
      </figcaption>
    </figure>

    <p>
      <strong>KL 발산</strong> 방식이 흥미롭다. 값의 오차가 아니라
      <em>분포의 모양</em>이 보존되는지를 본다.
      개별 값이 조금 틀려도 전체 분포가 닮았으면 이후 층이 비슷하게 반응한다는 관점이다.
    </p>
    <div class="note">
      <b>어느 것도 최종 정확도를 직접 보지 않는다.</b>
      세 방식 모두 <em>텐서 하나의 오차</em>를 줄일 뿐이다.
      그런데 층별 오차가 최종 출력에 미치는 영향은 층마다 다르다 —
      초반 층의 작은 오차가 뒤에서 증폭되기도 하고, 그 반대이기도 하다.
      <a href="evaluation-benchmarks.html">대리 지표를 최적화하는</a> 전형적 상황이라,
      마지막에는 <strong>실제 정확도로 검증</strong>해야 한다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>어떤 데이터를 쓸 것인가</h2>
    <p>
      방식만큼 중요한 것이 <strong>무엇을 흘려보내는가</strong>다.
      캘리브레이션 데이터가 실제 입력 분포와 다르면 범위가 어긋난다.
    </p>
    <p>
      전형적인 실패를 보자.
    </p>
    <ul>
      <li><strong>밝은 사진만 썼다</strong> — 야간 촬영에서 활성값 분포가 달라져 범위를 벗어난다</li>
      <li><strong>한 클래스만 썼다</strong> — 다른 물체에서 반응하는 채널이 관찰되지 않는다</li>
      <li><strong>전처리가 다르다</strong> — 학습과 다른 정규화를 쓰면 입력부터 어긋난다</li>
      <li><strong>너무 적다</strong> — 몇 장으로는 꼬리 분포를 못 본다</li>
    </ul>
    <div class="eq">
      <span class="cap">실무 지침</span>
      <div class="line">· 학습·검증 데이터에서 <strong>무작위로</strong> 뽑는다 (수백 장)</div>
      <div class="line">· 실제 배포 환경의 다양성을 반영한다 (조명·기기·시간대)</div>
      <div class="line">· <strong>전처리를 배포와 동일하게</strong> 맞춘다 ← 가장 자주 틀리는 곳</div>
      <div class="line">· 라벨은 필요 없다 — 순전파만 하므로</div>
    </div>
    <p>
      세 번째가 특히 자주 문제가 된다.
      <a href="mobile-runtime.html">모바일 런타임</a>에서도 지적했듯,
      학습 파이프라인과 앱의 전처리가 미묘하게 다른 경우가 흔하다.
      캘리브레이션을 학습 쪽 전처리로 하고 배포는 앱 전처리로 하면,
      <strong>관찰한 분포와 실제 분포가 다르다</strong>.
    </p>
    <div class="note">
      <b>데이터가 아예 없을 때도 방법이 있다.</b>
      프라이버시나 보안 때문에 실제 데이터를 못 쓰는 경우,
      <em>배치정규화 층에 저장된 통계</em>로 합성 입력을 만들어 캘리브레이션하는 방식이 있다.
      BN 은 학습 중 본 활성값의 평균·분산을 갖고 있으므로,
      그 통계를 재현하는 입력을 역으로 생성하는 것이다.
      실제 데이터만은 못하지만 min-max 를 그냥 쓰는 것보다 낫다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>층마다 다르게, 그리고 검증</h2>
    <p>
      마지막으로 캘리브레이션이 <strong>층마다 다른 답</strong>을 요구한다는 점을 짚자.
    </p>
    <p>
      활성함수 종류에 따라 분포 모양이 다르다.
      ReLU 뒤는 전부 양수라 <em>비대칭</em>이 유리하고, 값이 0에 몰려 있다.
      반면 어텐션이나 정규화 뒤의 값은 <a href="normalization.html">0을 중심으로</a> 퍼져 <em>대칭</em>이 자연스럽다.
    </p>
    <p>
      층별 민감도도 다르다. 실무에서는 <strong>어느 층이 문제인지 찾는 것</strong>이 작업의 대부분이다.
    </p>
    <div class="eq">
      <span class="cap">민감도 분석 — 한 층씩 되돌려 본다</span>
      <div class="line">1) 전체를 INT8 로 양자화한 뒤 정확도를 잰다</div>
      <div class="line">2) <strong>층 하나만</strong> fp 로 되돌리고 다시 잰다</div>
      <div class="line">3) 크게 회복되면 → 그 층이 병목</div>
      <div class="line">4) 병목 층만 fp 로 남기거나 캘리브레이션을 따로 조정</div>
    </div>
    <p>
      이렇게 찾은 층은 대개 <strong>첫 층과 마지막 층</strong>이거나
      <a href="efficient-backbone.html">depthwise 층</a>이다.
      첫 층은 입력 분포를 그대로 받아 범위가 넓고,
      마지막 층은 출력이 곧 결과라 오차가 그대로 드러난다.
      그래서 <em>이 둘은 fp 로 남기는 것</em>이 관행에 가깝다.
    </p>
    <div class="note">
      <b>검증은 최종 정확도로 한다.</b> 층별 오차가 작아도 최종 성능이 떨어질 수 있고, 그 반대도 있다.
      <a href="image-quality-metrics.html">화질 지표</a>에서 본 것과 같은 구조다 —
      <em>중간 지표와 최종 목표는 다르다</em>.
      검출이라면 mAP 를, 분류라면 top-1 을, 실제 과제 데이터로 재야 한다.
    </div>
    <p>
      정리하면 캘리브레이션은 <em>"보지 못한 입력의 범위를 몇백 장으로 추정하는"</em> 일이다.
      추정이므로 틀릴 수 있고, 틀리는 방향이 두 가지(넓게/좁게)이며,
      어느 쪽이 덜 해로운지는 <strong>모델과 데이터에 따라 다르다</strong>.
      값싼 대신 손이 가는 단계이고, 그래서 <a href="qat.html">QAT</a> 로 넘어가기 전에
      여기서 충분히 시도해 보는 것이 순서다.
    </p>
  </section>
"""

READING = [
    "Krishnamoorthi, <em>Quantizing deep convolutional networks for efficient inference: A whitepaper</em> (arXiv:1806.08342) — 캘리브레이션 방식별 비교.",
    "Migacz, <em>8-bit Inference with TensorRT</em> (GTC 2017) — KL 발산 기반 범위 선택.",
    "Nagel et al., <em>A White Paper on Neural Network Quantization</em> (arXiv:2106.08295) — MSE 기반 범위 선택과 층별 민감도.",
    "Nagel et al., <em>Data-Free Quantization Through Weight Equalization and Bias Correction</em> (arXiv:1906.04721) — 데이터 없이 BN 통계로 캘리브레이션.",
    "Banner et al., <em>Post training 4-bit quantization of convolutional networks for rapid-deployment</em> (arXiv:1810.05723) — 클리핑 범위의 해석적 최적화.",
]

write(
    "calibration.html",
    title="캘리브레이션 — 보지 못한 입력의 범위를 정하기",
    eyebrow="Vision · On-Device Quantization · 2017–2026",
    h1="캘리브레이션",
    subtitle="보지 못한 입력의 범위를 정하기 — 몇백 장으로 추정한다",
    dek=(
        "가중치는 학습이 끝나면 고정이라 <em>그냥 보면</em> 된다. "
        "활성값은 입력마다 달라지는데, 배포된 모델은 "
        "<strong>어떤 입력이 올지 모른 채</strong> 스케일을 미리 정해야 한다. "
        "대표 데이터 몇백 장을 흘려보내 분포를 관찰하는 것이 캘리브레이션이고, "
        "여기서 <em>최댓값을 쓸 것인가 잘라낼 것인가</em>가 갈린다."
    ),
    spec=[
        ("필요한 것", "라벨 없는 수백 장"),
        ("하는 일", "순전파 + 통계 수집"),
        ("핵심 선택", "범위를 어디서 자를까"),
        ("두 오차", "클리핑 ↔ 반올림"),
        ("가장 잦은 실수", "전처리 불일치"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

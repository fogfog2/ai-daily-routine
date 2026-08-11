#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff1f0", panel="#e4e8e6", ink="#131a17", **{
    "ink-soft": "#4a5652", "ink-faint": "#798581", "rule": "#ccd3d0",
    "rule-strong": "#a9b1ad", "accent": "#0f6152", "accent-fill": "#d6ebe4",
    "accent-line": "#2c8a74", "muted": "#83888c", "muted-fill": "#dee1df", "warn": "#a34a28",
})
DARK = dict(paper="#0e1211", panel="#161b19", ink="#e3eae7", **{
    "ink-soft": "#a0aba6", "ink-faint": "#6f7a76", "rule": "#202726", "rule-strong": "#36403c",
    "accent": "#4cc4a2", "accent-fill": "#0d2a23", "accent-line": "#2d8a72",
    "muted": "#868d8a", "muted-fill": "#191f1d", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>같은 이름, 다른 문제</h2>
    <p>
      <a href="quantization.html">양자화 문서</a>는 LLM 을 다뤘다 —
      GPTQ·AWQ 로 <strong>가중치를 4비트</strong>까지 내려 70B 모델을 GPU 한 장에 올리는 이야기다.
      온디바이스 vision 은 같은 단어를 쓰지만 <em>다른 문제</em>를 푼다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th></th><th>LLM 양자화</th><th>온디바이스 vision</th></tr>
        </thead>
        <tbody>
          <tr><td>주 대상</td><td class="hi">가중치만 (W4A16)</td><td class="hi">가중치 + <strong>활성값</strong> (W8A8)</td></tr>
          <tr><td>병목</td><td>메모리 용량·대역폭</td><td>연산 처리량 · 전력</td></tr>
          <tr><td>목표</td><td>모델을 올릴 수 있게</td><td class="hi">NPU 정수 유닛을 쓰게</td></tr>
          <tr><td>실행</td><td>역양자화 후 fp16 곱셈</td><td class="hi">정수로 곱셈까지</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 핵심 차이다. LLM 은 4비트로 저장했다가 <em>계산 직전에 되돌려</em> fp16 으로 곱한다.
      메모리를 아끼는 것이 목적이기 때문이다.
    </p>
    <p>
      온디바이스는 다르다. <strong>곱셈 자체를 정수로</strong> 해야 한다.
      NPU 의 정수 유닛이 fp 유닛보다 훨씬 빠르고 전력을 적게 쓰기 때문이다.
      그러려면 활성값도 정수여야 하고, <em>거기서부터 어려워진다</em>.
    </p>
    <div class="note">
      <b>왜 활성값이 어려운가.</b> 가중치는 학습이 끝나면 <strong>고정</strong>이다. 값을 보고 범위를 정하면 된다.
      활성값은 <em>입력마다 달라진다</em>. 어떤 사진이 들어올지 모르는 채로 범위를 미리 정해야 한다.
      이 하나 때문에 캘리브레이션·아웃라이어·QAT 같은 것들이 전부 따라온다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>정수로 곱셈이 성립하는 이유</h2>
    <p>
      먼저 왜 정수로 계산할 수 있는지 보자. 양자화는 실수를 <em>스케일과 정수</em>로 나눠 적는 것이다.
    </p>
    <div class="eq">
      <span class="cap">대칭 · 비대칭</span>
      <div class="line">대칭&nbsp;&nbsp;&nbsp; x ≈ s · q&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;s = max|x| / 127,&nbsp; q ∈ [−127, 127]</div>
      <div class="line">비대칭&nbsp; x ≈ s · (q − z)&nbsp;&nbsp;&nbsp; s = (max−min) / 255,&nbsp; q ∈ [0, 255]</div>
      <div class="line">&nbsp;</div>
      <div class="line">// z = 영점(zero-point). 실수 0 이 어느 정수에 대응하는가</div>
    </div>
    <p>
      이제 곱셈을 전개하면 <strong>정수 연산만 남는다</strong>.
    </p>
    <div class="eq">
      <span class="cap">스케일이 밖으로 빠진다</span>
      <div class="line">x · w = s<sub>x</sub>(q<sub>x</sub> − z<sub>x</sub>) · s<sub>w</sub>(q<sub>w</sub> − z<sub>w</sub>)</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = <strong>s<sub>x</sub> · s<sub>w</sub></strong> · (q<sub>x</sub> − z<sub>x</sub>)(q<sub>w</sub> − z<sub>w</sub>)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 괄호 안은 전부 정수 → INT8 곱셈, INT32 누산</div>
      <div class="line">// 스케일은 <em>마지막에 한 번</em>만 곱한다</div>
    </div>
    <p>
      누산을 INT32 로 받는 것이 중요하다.
      INT8 끼리 곱하면 최대 <code>127×127 ≈ 16,129</code> 이고 이것을 수백 번 더하므로 INT8 에 담기지 않는다.
      곱셈은 8비트, 누산은 32비트 — 이것이 NPU 정수 파이프라인의 기본 형태다.
    </p>
    <p>
      <strong>대칭이냐 비대칭이냐</strong>는 실무에서 갈린다.
      가중치는 대체로 0을 중심으로 분포하므로 <em>대칭</em>이 자연스럽고 영점 계산이 빠진다.
      활성값은 ReLU 뒤라면 <strong>전부 양수</strong>라 대칭을 쓰면 음수 구간 절반을 버리게 된다 —
      그래서 활성값에는 비대칭을 쓰는 경우가 많다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>어디까지 묶어서 스케일을 정할 것인가</h2>
    <p>
      스케일 <code>s</code> 를 <strong>얼마나 잘게 나눠</strong> 정할지가 정확도를 크게 가른다.
      텐서 전체에 하나(per-tensor)를 쓸 수도, 출력 채널마다 하나(per-channel)를 쓸 수도 있다.
    </p>
    <p>
      <a href="efficient-backbone.html">경량 백본</a> 문서에서
      <em>"depthwise 층은 채널 단위 양자화가 아니면 정확도가 크게 떨어진다"</em>고 했다.
      왜 그런지 숫자로 보자.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="per-tensor와 per-channel 양자화의 차이. 채널마다 가중치 범위가 크게 다를 때 텐서 전체에 하나의 스케일을 쓰면 범위가 좁은 채널은 몇 단계밖에 쓰지 못해 뭉개지지만, 채널마다 스케일을 따로 두면 모든 채널이 전체 범위를 쓴다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">depthwise 층 — 채널마다 가중치 범위가 다르다</text>

            <g>
              <line x1="130" y1="34" x2="130" y2="150" stroke="var(--rule-strong)" stroke-width="1"/>
              <text x="24" y="48" font-size="8" fill="var(--ink-faint)">채널 0</text>
              <rect x="126" y="40" width="8" height="12" fill="var(--accent)" opacity="0.7"/>
              <text x="24" y="76" font-size="8" fill="var(--ink-faint)">채널 1</text>
              <rect x="110" y="68" width="40" height="12" fill="var(--accent)" opacity="0.7"/>
              <text x="24" y="104" font-size="8" fill="var(--ink-faint)">채널 2</text>
              <rect x="128" y="96" width="4" height="12" fill="var(--accent)" opacity="0.7"/>
              <text x="24" y="132" font-size="8" fill="var(--ink-faint)">채널 3</text>
              <rect x="50" y="124" width="160" height="12" fill="var(--accent)" opacity="0.7"/>
              <text x="76" y="164" font-size="8" fill="var(--ink-faint)">−3.2</text>
              <text x="196" y="164" font-size="8" fill="var(--ink-faint)">+3.2</text>
            </g>

            <line x1="252" y1="26" x2="252" y2="228" stroke="var(--rule)" stroke-width="1"/>

            <text x="276" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">per-tensor — 스케일 하나</text>
            <text x="276" y="38" font-size="8" fill="var(--ink-faint)">s = 3.2 / 127 로 전 채널 공통</text>

            <g font-size="8">
              <text x="276" y="60" fill="var(--ink-soft)">채널 0</text>
              <rect x="330" y="52" width="6" height="10" fill="var(--warn)" opacity="0.6"/>
              <text x="352" y="60" fill="var(--warn)">4.0 단계</text>
              <text x="276" y="80" fill="var(--ink-soft)">채널 1</text>
              <rect x="330" y="72" width="48" height="10" fill="var(--accent)" opacity="0.5"/>
              <text x="392" y="80" fill="var(--ink-faint)">63.5 단계</text>
              <text x="276" y="100" fill="var(--ink-soft)">채널 2</text>
              <rect x="330" y="92" width="3" height="10" fill="var(--warn)" opacity="0.8"/>
              <text x="352" y="100" fill="var(--warn)">1.6 단계 ← 뭉개진다</text>
              <text x="276" y="120" fill="var(--ink-soft)">채널 3</text>
              <rect x="330" y="112" width="190" height="10" fill="var(--accent)" opacity="0.5"/>
              <text x="534" y="120" fill="var(--ink-faint)">254 단계</text>
            </g>

            <line x1="276" y1="136" x2="674" y2="136" stroke="var(--rule)" stroke-width="1"/>

            <text x="276" y="156" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">per-channel — 채널마다 스케일</text>
            <g font-size="8">
              <text x="276" y="178" fill="var(--ink-soft)">채널 0</text>
              <rect x="330" y="170" width="190" height="10" fill="var(--accent)" opacity="0.6"/>
              <text x="534" y="178" fill="var(--accent)">254 단계</text>
              <text x="276" y="196" fill="var(--ink-soft)">채널 2</text>
              <rect x="330" y="188" width="190" height="10" fill="var(--accent)" opacity="0.6"/>
              <text x="534" y="196" fill="var(--accent)">254 단계</text>
            </g>
            <text x="276" y="220" font-size="8.5" fill="var(--accent)">범위가 좁은 채널도 전체 해상도를 쓴다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>가장 큰 채널이 나머지를 망친다.</strong>
        per-tensor 는 텐서 전체의 최댓값으로 스케일을 정하므로,
        범위가 좁은 채널은 254단계 중 <em>한두 단계</em>만 쓰게 된다.
        일반 합성곱은 채널 간 편차가 작아 견디지만,
        <strong>depthwise 는 채널이 서로 독립이라 편차가 크다</strong> — 그래서 특히 취약하다.
      </figcaption>
    </figure>

    <p>
      실측 보고도 이와 맞는다. per-tensor W4A8 에서
      <strong>MobileNetV2 는 약 2.5%, EfficientNet-lite 는 약 4.2%</strong> 정확도가 떨어진다는 결과가 있다.
      per-channel 로 바꾸면 손실이 크게 줄어든다.
    </p>
    <div class="note">
      <b>다만 활성값은 per-channel 로 하기 어렵다.</b>
      가중치는 고정이라 채널별 스케일을 미리 계산해 저장하면 되지만,
      활성값 스케일을 채널마다 두면 <em>런타임에 채널별 처리</em>가 필요해 정수 파이프라인이 복잡해진다.
      그래서 통상 <strong>가중치는 per-channel, 활성값은 per-tensor</strong> 로 간다.
      런타임 지원 여부도 확인해야 한다 — <a href="mobile-runtime.html">지원 연산자 문제</a>가 여기서도 나온다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>아웃라이어 하나가 전체를 망친다</h2>
    <p>
      앞 절의 문제를 일반화하면 이렇게 된다 — <strong>스케일은 최댓값이 정하는데,
      최댓값은 극소수 값이 정한다.</strong>
    </p>
    <p>
      활성값에서 이 문제가 더 심하다. 대부분의 값이 <code>[-2, 2]</code> 안에 있는데
      한 위치에서 <code>50</code> 이 나오면, 스케일이 50 기준으로 잡혀
      <em>나머지 전부가 몇 단계 안에 뭉친다</em>.
    </p>
    <div class="eq">
      <span class="cap">아웃라이어의 대가</span>
      <div class="line">활성값 대부분 [−2, 2],&nbsp; 아웃라이어 하나 50</div>
      <div class="line">&nbsp;</div>
      <div class="line">s = 50 / 127 ≈ 0.394</div>
      <div class="line">→ [−2, 2] 구간이 쓰는 단계 = 4 / 0.394 ≈ <strong>10 단계</strong></div>
      <div class="line">→ 254 단계 중 10 개만 실제로 쓰인다</div>
    </div>
    <p>
      처방은 몇 갈래다.
    </p>
    <ul>
      <li><strong>클리핑</strong> — 최댓값 대신 분위수(예: 99.99%)로 자른다. 아웃라이어는 포화시키고 나머지 해상도를 지킨다</li>
      <li><strong>범위 균등화</strong> — 수학적으로 동등한 변환으로 층 사이에 범위를 나눠 옮긴다. 값을 바꾸지 않고 분포만 고른다</li>
      <li><strong>혼합 정밀도</strong> — 문제가 되는 층만 fp16 으로 남긴다. <a href="mobile-runtime.html">그래프가 쪼개지는 대가</a>가 따른다</li>
    </ul>
    <div class="note">
      <b>클리핑은 손실을 맞바꾸는 것이다.</b> 자르면 아웃라이어 값이 틀리고, 안 자르면 나머지가 뭉개진다.
      어느 쪽 오차가 최종 정확도에 덜 해로운지는 <em>실측으로만</em> 알 수 있다.
      그래서 캘리브레이션 단계에서 여러 분위수를 시험해 고르는 것이 실무 절차가 됐다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실무 순서와 확인할 것들</h2>
    <p>
      온디바이스 양자화는 대개 이 순서로 진행한다.
    </p>
    <div class="eq">
      <span class="cap">권장 순서 — 값싼 것부터</span>
      <div class="line">① <strong>PTQ + per-channel 가중치</strong> 로 먼저 시도</div>
      <div class="line">&nbsp;&nbsp;&nbsp; 대개 여기서 대부분 해결된다</div>
      <div class="line">② 정확도가 부족하면 <strong>캘리브레이션 데이터·클리핑</strong> 조정</div>
      <div class="line">③ 그래도 부족하면 <strong>QAT</strong> — 학습을 다시 돌려야 한다</div>
      <div class="line">④ 특정 층만 문제면 <strong>혼합 정밀도</strong> (그래프 분할 대가)</div>
    </div>
    <p>
      ③으로 바로 가지 않는 것이 중요하다. QAT 는 학습 파이프라인을 다시 세워야 하므로 비싸다.
      <strong>PTQ 로 되는지 먼저 확인</strong>하고, 안 될 때만 올라간다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>확인할 것</th><th>왜</th></tr>
        </thead>
        <tbody>
          <tr><td class="hi">층별 오차 비교</td><td>어느 층에서 갈라지는지 찾아야 원인을 좁힌다</td></tr>
          <tr><td>정수 경로로 실제 실행됐는가</td><td class="hi">양자화했는데 fp 로 떨어지면 이득이 없다</td></tr>
          <tr><td>캘리브레이션 데이터 대표성</td><td>학습 분포와 다르면 범위가 어긋난다</td></tr>
          <tr><td>BN 융합 여부</td><td>합성곱과 배치정규화를 합친 뒤 양자화해야 한다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      두 번째 줄이 자주 놓치는 지점이다. 변환은 성공했는데
      런타임이 그 연산을 정수로 처리하지 못해 <em>내부적으로 되돌려 fp 로 계산</em>하는 경우가 있다.
      모델 크기는 줄었는데 속도는 그대로인 상황이 여기서 나온다 —
      <a href="mobile-runtime.html">위임 로그</a>를 확인해야 한다.
    </p>
    <div class="note">
      <b>양자화는 마지막에 한다.</b> <a href="efficient-backbone.html">경량 백본</a>으로 구조를 정하고,
      <a href="knowledge-distillation.html">증류</a>로 품질을 올린 뒤,
      마지막에 양자화하는 순서가 표준이다.
      사후 적용이 가능하고 효과가 가장 확실하기 때문이다.
      다만 <em>구조와 양자화가 충돌</em>할 수 있다는 것이 이 문서의 요지다 —
      depthwise 를 많이 쓰는 구조라면 per-channel 을 지원하는 런타임인지
      <strong>구조를 고르는 단계에서</strong> 확인하는 편이 낫다.
    </div>
  </section>
"""

READING = [
    "Jacob et al., <em>Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference</em> (arXiv:1712.05877) — 정수 전용 추론의 기본 형식.",
    "Krishnamoorthi, <em>Quantizing deep convolutional networks for efficient inference: A whitepaper</em> (arXiv:1806.08342) — per-tensor/per-channel 비교와 MobileNet 실측.",
    "Nagel et al., <em>A White Paper on Neural Network Quantization</em> (arXiv:2106.08295) — PTQ·QAT 전반의 정리.",
    "Nagel et al., <em>Data-Free Quantization Through Weight Equalization and Bias Correction</em> (arXiv:1906.04721) — 범위 균등화.",
    "Sheng et al., <em>A Quantization-Friendly Separable Convolution for MobileNets</em> (arXiv:1803.08607) — depthwise 가 양자화에 취약한 원인 분석.",
    "van Baalen et al., <em>FP8 versus INT8 for efficient deep learning inference</em> (arXiv:2303.17951) — 온디바이스에서 두 형식의 비교.",
]

write(
    "ondevice-quantization.html",
    title="온디바이스 양자화 — INT8 로 실제 굴리기",
    eyebrow="Vision · On-Device · 2017–2026",
    h1="온디바이스 양자화",
    subtitle="INT8 로 실제 굴리기 — 가중치만이 아니라 활성값까지",
    dek=(
        "LLM 양자화는 가중치를 4비트로 줄여 <em>모델을 올리는</em> 것이 목적이다. "
        "온디바이스는 다르다 — <strong>곱셈 자체를 정수로</strong> 해야 NPU 를 쓸 수 있고, "
        "그러려면 활성값도 정수여야 한다. "
        "가중치는 고정이지만 활성값은 입력마다 달라진다. 어려움은 전부 여기서 나온다."
    ),
    spec=[
        ("LLM 과 차이", "활성값까지 양자화"),
        ("목표", "NPU 정수 유닛"),
        ("곱셈·누산", "INT8 × INT8 → INT32"),
        ("핵심 선택", "per-channel 가중치"),
        ("최대 적", "아웃라이어"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

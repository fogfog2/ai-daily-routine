#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f2f1ee", panel="#e8e7e2", ink="#191b18", **{
    "ink-soft": "#4f5450", "ink-faint": "#7d827d", "rule": "#d6d5cf",
    "rule-strong": "#adaca4", "accent": "#2f6152", "accent-fill": "#dcebe4",
    "accent-line": "#4c8a75", "muted": "#86877f", "muted-fill": "#e2e1db", "warn": "#a1502a",
})
DARK = dict(paper="#0f1211", panel="#171b19", ink="#e6eae7", **{
    "ink-soft": "#a1a9a4", "ink-faint": "#737a76", "rule": "#212724", "rule-strong": "#363d39",
    "accent": "#8fc9b2", "accent-fill": "#16211c", "accent-line": "#5f957f",
    "muted": "#858986", "muted-fill": "#191d1b", "warn": "#dd9068",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>깊게 쌓았더니 학습 오차가 올라갔다</h2>
    <p>
      2015년 이전에도 층을 더 쌓으면 좋아진다는 것은 알려져 있었다.
      <a href="cnn-basics.html">CNN</a> 은 층마다 더 넓은 수용장과 더 추상적인 특징을 얻고,
      <a href="scaling-laws.html">규모의 법칙</a>이 말하는 방향도 그쪽이다.
      그런데 실제로 20층을 넘겨 쌓아 보면 이상한 일이 벌어졌다.
      <strong>더 깊은 망이 더 얕은 망보다 학습 오차가 높았다.</strong>
    </p>
    <p>
      이 말이 왜 이상한지를 짚어야 한다. 시험 오차가 높다면 과적합이다 —
      모델이 커서 훈련 데이터를 외웠다는 뜻이고, 정규화로 다루면 되는 익숙한 문제다.
      그런데 여기서 오른 것은 <em>학습</em> 오차다. 외우지도 못했다는 뜻이다.
      게다가 깊은 망은 얕은 망을 포함한다 —
      <strong>추가된 층이 전부 항등 사상이면 얕은 망과 정확히 같은 함수</strong>가 된다.
      해가 구성적으로 존재하는데 최적화가 그 해를 못 찾는다.
      이것을 <em>퇴화</em>(degradation) 문제라 부른다.
    </p>
    <p>
      말로만 두면 믿기 어려운 주장이라 직접 재현해 봤다.
      은닉 폭 32의 ReLU 다층 퍼셉트론에 He 초기화를 주고,
      고정된 3층 tanh 교사 함수를 전배치 SGD 로 1,200 스텝 학습시켰다.
      블록은 두 층씩 묶었고, <em>파라미터 수는 잔차 유무와 무관하게 같다.</em>
      학습률은 설정마다 {0.3, 0.1, 0.03} 중 가장 좋은 것을 골랐다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>깊이</th><th>평범한 망</th><th>잔차 망</th><th>잔차 + 블록 끝 0 초기화</th></tr>
        </thead>
        <tbody>
          <tr><td>6층</td><td>0.00063</td><td>0.01038</td><td>0.00119</td></tr>
          <tr><td>18층</td><td class="hi">0.00006</td><td>발산</td><td>0.00423</td></tr>
          <tr><td>50층</td><td class="hi">0.00259</td><td>발산</td><td>0.00463</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      평범한 망은 6층에서 18층으로 갈 때 오차가 <strong>10배 줄었다가</strong>,
      18층에서 50층으로 갈 때 <strong>43배 늘었다.</strong>
      깊이가 늘면서 표현력만 커졌다면 나올 수 없는 모양이다.
      상수를 예측할 때의 오차(타깃 분산)가 0.17083 이므로
      50층 망도 학습에 실패한 것은 아니다 — 다만 <em>더 얕은 자기 자신보다 못하다.</em>
    </p>
    <div class="note">
      <b>이 표의 한계를 먼저 밝힌다.</b> 장난감 회귀 문제이고, 정규화 층이 없고,
      전배치 SGD 1,200 스텝이다. 절대 수치는 원논문의 CIFAR·ImageNet 결과와 비교할 성질이 아니다.
      여기서 읽을 것은 <strong>부호와 방향</strong>뿐이다 —
      어느 지점부터 깊이가 학습 오차를 <em>악화</em>시킨다는 것.
      가운데 열(잔차만 넣은 망)이 18층부터 발산하는 것도 눈여겨 둘 것이다.
      04 절에서 그 이야기를 한다.
    </div>
    <p>
      원인 후보는 셋이었다. 기울기 소실·폭발,
      <a href="normalization.html">정규화</a>의 부재, 그리고 최적화 자체의 어려움.
      앞의 둘은 그 무렵 이미 상당히 다뤄져 있었다 —
      He 초기화와 배치 정규화가 나온 뒤였고, 그것들을 다 쓰고도 퇴화는 남았다.
      남은 답은 셋째였다. <strong>깊어질수록 항등에 가까운 사상을 배우기가 어려워진다.</strong>
    </p>
    <p>
      직관적으로도 그렇다. 층 하나가 항등을 흉내내려면
      가중치 행렬이 정확히 단위 행렬이 되어야 하는데,
      ReLU 와 <a href="normalization.html">정규화</a>를 지난 뒤 그 값을 맞추는 일은
      랜덤 초기화 지점에서 보면 좁은 표적이다.
      층이 50개면 그 좁은 표적을 50번 연속으로 맞혀야 한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>기본값을 항등으로 바꾼다</h2>
    <p>
      He 등이 2015년에 낸 답은 구조를 하나 바꾸는 것이었다.
      층 묶음이 원하는 사상 <span class="mono">H(x)</span> 를 직접 배우게 하는 대신,
      <strong>입력을 출력에 그대로 더해 두고 차이만 배우게 한다.</strong>
    </p>
    <div class="eq">
      <span class="cap">평범한 블록과 잔차 블록</span>
      <div class="line">평범한 블록 &nbsp; y = H(x)</div>
      <div class="line">잔차 블록 &nbsp;&nbsp;&nbsp; y = F(x) + x &nbsp;&nbsp; 여기서 F(x) = H(x) − x</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 배우는 대상이 사상 자체에서 <b>사상과 항등의 차이</b>로 바뀐다</div>
    </div>
    <p>
      표현할 수 있는 함수의 집합은 달라지지 않는다. 둘은 같은 것을 표현할 수 있다.
      달라지는 것은 <strong>어디가 원점인가</strong>다.
      평범한 블록에서 항등을 내려면 가중치를 단위 행렬로 맞춰야 하지만,
      잔차 블록에서 항등은 <span class="mono">F = 0</span> 이다.
      가중치를 0 쪽으로 밀기만 하면 되고, 그것은
      <a href="backprop-optimizers.html">가중치 감쇠</a>가 이미 매 스텝 하고 있는 일이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 200" role="img" aria-label="왼쪽은 평범한 블록으로 입력이 두 개의 가중치 층과 활성함수를 차례로 지나 출력이 되고, 오른쪽은 잔차 블록으로 같은 두 층을 지난 결과에 입력을 그대로 더한 뒤 활성함수를 통과한다. 오른쪽에는 가중치를 지나지 않고 출력으로 바로 이어지는 지름길 경로가 그려져 있다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="16" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">같은 파라미터 · 다른 원점</text>

            <rect x="24" y="30" width="320" height="150" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <text x="40" y="48" font-size="9" fill="var(--ink-soft)">평범한 블록 — 원점은 0 사상</text>
            <circle cx="56" cy="112" r="4" fill="var(--ink-faint)"/>
            <text x="46" y="132" font-size="8.5" fill="var(--ink-faint)">x</text>
            <line x1="60" y1="112" x2="106" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <rect x="106" y="98" width="52" height="28" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="116" y="116" font-size="9" fill="var(--ink)">W₁ relu</text>
            <line x1="158" y1="112" x2="204" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <rect x="204" y="98" width="52" height="28" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="218" y="116" font-size="9" fill="var(--ink)">W₂</text>
            <line x1="256" y1="112" x2="302" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <circle cx="306" cy="112" r="4" fill="var(--ink-faint)"/>
            <text x="288" y="132" font-size="8.5" fill="var(--ink-faint)">relu → y</text>
            <text x="40" y="166" font-size="8.5" fill="var(--warn)">항등을 내려면 W 를 단위 행렬로 맞춰야 한다</text>

            <rect x="356" y="30" width="320" height="150" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <text x="372" y="48" font-size="9" fill="var(--accent)">잔차 블록 — 원점은 항등 사상</text>
            <circle cx="388" cy="112" r="4" fill="var(--accent-line)"/>
            <text x="378" y="132" font-size="8.5" fill="var(--ink-faint)">x</text>
            <line x1="392" y1="112" x2="438" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <rect x="438" y="98" width="52" height="28" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="448" y="116" font-size="9" fill="var(--ink)">W₁ relu</text>
            <line x1="490" y1="112" x2="536" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <rect x="536" y="98" width="52" height="28" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="550" y="116" font-size="9" fill="var(--ink)">W₂</text>
            <line x1="588" y1="112" x2="624" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <circle cx="630" cy="112" r="8" fill="none" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="626" y="116" font-size="10" fill="var(--accent)">+</text>
            <line x1="638" y1="112" x2="660" y2="112" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <text x="608" y="132" font-size="8.5" fill="var(--ink-faint)">relu → y</text>
            <path d="M388 108 L388 70 L630 70 L630 104" fill="none" stroke="var(--accent-line)" stroke-width="2" stroke-dasharray="5 3"/>
            <text x="470" y="64" font-size="8.5" fill="var(--accent)">지름길 — 가중치가 없다</text>
            <text x="372" y="166" font-size="8.5" fill="var(--accent)">항등을 내려면 W₂ 를 0 으로 밀면 된다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        표현할 수 있는 함수는 양쪽이 같다. 바뀐 것은 <em>아무것도 배우지 않았을 때의 기본 동작</em>이다.
        왼쪽의 기본값은 신호를 지우는 것이고, 오른쪽의 기본값은 신호를 그대로 통과시키는 것이다.
      </figcaption>
    </figure>

    <p>
      지름길에 가중치가 없다는 점이 중요하다.
      Highway Network(2015)가 반년 앞서 같은 발상을 냈지만 그쪽은 지름길에
      <em>게이트</em>를 달았다 — <a href="rnn-lstm.html">LSTM</a> 의 게이트를 깊이 축으로 옮긴 구조다.
      게이트는 학습해야 하는 값이고, 학습 초기에 그 값이 0 쪽으로 닫히면
      지름길이 닫힌다. ResNet 은 게이트를 없애고 <strong>항상 열린 항등 경로</strong>로 바꿨다.
      배울 것이 하나 줄었고, 그만큼 초기에 실패할 여지가 줄었다.
    </p>
    <p>
      더하기의 대상이 되려면 차원이 맞아야 한다.
      채널 수나 해상도가 바뀌는 지점에서는 지름길에 1&times;1 합성곱을 하나 끼워
      <em>투영 지름길</em>로 만든다. ResNet-50 기준으로 그런 지점은 네 곳뿐이고,
      나머지 블록은 전부 가중치 없는 순수 항등이다.
      <a href="efficient-backbone.html">경량 백본</a>들이 이 규칙을 그대로 물려받았다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>기울기는 곱이 아니라 합으로 흐른다</h2>
    <p>
      최적화가 쉬워진 이유를 역전파 쪽에서 보면 더 선명하다.
      <a href="backprop-optimizers.html">역전파</a>는 층별 야코비안을 곱해 내려간다.
      평범한 망에서 <span class="mono">l</span> 층까지 내려온 기울기는 이렇게 생겼다.
    </p>
    <div class="eq">
      <span class="cap">평범한 망 — 곱</span>
      <div class="line">∂L/∂a<sub>l</sub> = ∂L/∂a<sub>L</sub> · ∏<sub>k=l..L−1</sub> (∂a<sub>k+1</sub>/∂a<sub>k</sub>)</div>
      <div class="line">&nbsp;</div>
      <span class="cap">잔차 망 — 각 항이 1 을 품는다</span>
      <div class="line">a<sub>k+1</sub> = a<sub>k</sub> + F(a<sub>k</sub>) &nbsp;⟹&nbsp; ∂a<sub>k+1</sub>/∂a<sub>k</sub> = <b>I</b> + ∂F/∂a<sub>k</sub></div>
      <div class="line">∂L/∂a<sub>l</sub> = ∂L/∂a<sub>L</sub> · ∏<sub>k</sub> (<b>I</b> + ∂F/∂a<sub>k</sub>)</div>
    </div>
    <p>
      곱을 전개하면 항등만 타고 온 항 하나가 반드시 남는다.
      <span class="mono">∂F/∂a</span> 가 전부 0 이어도 기울기는 1 배로 도착한다.
      평범한 망에서 층별 게인이 조금만 1 아래여도 무슨 일이 벌어지는지는 곱해 보면 안다.
    </p>
    <div class="eq">
      <span class="cap">층별 게인 g 로 L 층을 통과한 뒤의 배율</span>
      <div class="line">g = 0.90 · L = 20 &nbsp;&nbsp; 곱 <b>1.2158e−01</b> &nbsp;&nbsp;&nbsp; (1+g) 형 &nbsp;3.7590e+05</div>
      <div class="line">g = 0.90 · L = 56 &nbsp;&nbsp; 곱 <b>2.7389e−03</b> &nbsp;&nbsp;&nbsp; (1+g) 형 &nbsp;4.0757e+15</div>
      <div class="line">g = 0.95 · L = 56 &nbsp;&nbsp; 곱 <b>5.6562e−02</b> &nbsp;&nbsp;&nbsp; (1+g) 형 &nbsp;1.7456e+16</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 0.9 를 56번 곱하면 0.0027 이다. 5% 의 손실이 층마다 복리로 붙는다</div>
    </div>
    <p>
      여기까지는 식이다. 실제로 재면 어떤가 —
      01 절과 같은 망에서 <strong>입력층 가중치 기울기의 노름</strong>을
      깊이별로 재고 20개 시드의 기하평균을 취했다. 학습 전, 초기화 직후의 값이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 210" role="img" aria-label="깊이에 따른 입력층 기울기 노름을 로그 축으로 그린 두 패널. 왼쪽 넓은 축에서는 잔차만 넣은 망이 6층 2.9에서 130층 5.1의 21제곱까지 치솟는 반면 평범한 망과 0 초기화 잔차 망은 바닥 근처에 붙어 있다. 오른쪽 확대 패널에서는 평범한 망이 0.49에서 0.0015로 328배 감쇠하는 반면 0 초기화 잔차 망은 0.86에서 0.91 사이에 평탄하게 머문다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="16" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">입력층 기울기 노름 · 6 → 130층 · 20 seed 기하평균</text>

            <rect x="24" y="30" width="310" height="140" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <text x="34" y="44" font-size="8.5" fill="var(--ink-soft)">로그 축 1e−4 … 1e22</text>
            <line x1="40" y1="152" x2="320" y2="152" stroke="var(--rule)" stroke-width="1"/>
            <line x1="40" y1="135.4" x2="320" y2="135.4" stroke="var(--rule)" stroke-width="1" stroke-dasharray="2 4"/>
            <text x="300" y="133" font-size="7.5" fill="var(--ink-faint)">1</text>
            <polyline points="54,133.4 102,130.6 150,126.0 198,115.6 246,92.3 294,45.2" fill="none" stroke="var(--warn)" stroke-width="2"/>
            <polyline points="54,136.7 102,136.5 150,137.9 198,140.4 246,142.7 294,147.1" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <polyline points="54,135.6 102,135.2 150,135.1 198,135.4 246,135.6 294,135.6" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <text x="222" y="40" font-size="8.5" fill="var(--warn)">잔차만 · 5.06e21</text>
            <text x="34" y="166" font-size="8" fill="var(--ink-faint)">6층</text>
            <text x="278" y="166" font-size="8" fill="var(--ink-faint)">130층</text>

            <rect x="366" y="30" width="310" height="140" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <text x="376" y="44" font-size="8.5" fill="var(--ink-soft)">확대 — 로그 축 1e−3.2 … 1e1.2</text>
            <line x1="382" y1="152" x2="662" y2="152" stroke="var(--rule)" stroke-width="1"/>
            <line x1="382" y1="73.5" x2="662" y2="73.5" stroke="var(--rule)" stroke-width="1" stroke-dasharray="2 4"/>
            <text x="642" y="71" font-size="7.5" fill="var(--ink-faint)">1</text>
            <polyline points="402,75.0 440,72.5 478,71.9 516,73.8 554,74.7 592,74.5" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <polyline points="402,81.0 440,79.8 478,88.6 516,102.9 554,116.8 592,142.7" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <circle cx="592" cy="74.5" r="2.6" fill="var(--accent-line)"/>
            <circle cx="592" cy="142.7" r="2.6" fill="var(--ink-faint)"/>
            <text x="600" y="70" font-size="8" fill="var(--accent)">0.91</text>
            <text x="600" y="146" font-size="8" fill="var(--ink-faint)">0.0015</text>
            <text x="376" y="166" font-size="8" fill="var(--ink-faint)">6층</text>
            <text x="620" y="166" font-size="8" fill="var(--ink-faint)">130층</text>

            <line x1="24" y1="180" x2="676" y2="180" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="196" font-size="8.5" fill="var(--ink-soft)">━ 잔차만(정규화 없음) · ┄ 평범한 망 · ━ 잔차 + 블록 끝 0 초기화</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 2</span>
        평범한 망은 6층에서 130층으로 가며 입력층 기울기가 <strong>328배</strong> 줄었다
        (0.4933 → 0.0015). 잔차를 넣고 블록 끝 가중치를 0 으로 초기화한 망은
        같은 구간에서 0.86 ~ 1.15 사이에 머문다 — <em>깊이와 거의 무관하다.</em>
        그런데 잔차만 넣은 망은 반대쪽으로 터진다. 04 절이 그 이야기다.
      </figcaption>
    </figure>

    <p>
      오른쪽 패널의 평탄한 선이 잔차 연결이 실제로 사는 방식이다.
      130층짜리 망의 첫 층이 6층짜리 망의 첫 층과 <strong>같은 크기의 신호</strong>를 받는다.
      <a href="gradient-checkpointing.html">체크포인팅</a>이나
      <a href="mixed-precision.html">혼합 정밀도</a>가 깊은 망에서 성립하는 것도
      이 성질에 얹혀 있다 — fp16 의 표현 하한 근처로 기울기가 내려가지 않는다.
    </p>
    <p>
      같은 구조를 다른 각도에서 본 것이 Veit 등(2016)의 <em>앙상블 해석</em>이다.
      블록마다 지름길과 잔차 가지 둘 중 하나를 고를 수 있으므로,
      블록이 <span class="mono">n</span> 개면 입력에서 출력까지 경로가
      <span class="mono">2ⁿ</span> 개 있다.
    </p>
    <div class="eq">
      <span class="cap">잔차 망의 경로 수</span>
      <div class="line">블록 18개 (ResNet-38 급) &nbsp;&nbsp; 262,144 경로</div>
      <div class="line">블록 34개 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 17,179,869,184 경로</div>
      <div class="line">블록 54개 (ResNet-110 급) &nbsp; 18,014,398,509,481,984 경로</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 길이의 분포는 이항분포다 — 대부분의 경로가 <b>중간 길이</b>이고, 전체 깊이를 다 지나는 경로는 하나뿐이다</div>
    </div>
    <p>
      Veit 등의 관찰은 여기서 한 걸음 더 갔다.
      학습된 잔차 망에서 블록을 하나 <em>지워도</em> 성능이 크게 떨어지지 않는다.
      경로가 서로 강하게 의존하지 않기 때문이다.
      평범한 망에서 층 하나를 지우면 그 뒤가 전부 무너지는 것과 대조된다.
      이 성질은 <a href="pruning-sparsity.html">가지치기</a>가 잔차 구조에서
      비교적 잘 먹히는 이유이기도 하다.
    </p>
    <div class="note">
      <b>"잔차 연결이 기울기 소실을 해결한다"는 설명은 절반만 맞다.</b>
      Fig. 2 의 왼쪽 패널이 그 절반을 보여준다 — 잔차만 넣으면 소실이 아니라
      <em>폭주</em>가 온다. 130층에서 5.06e21 이다.
      곱의 각 항이 1 을 품는다는 것은 <strong>1 아래로 줄지 않는다</strong>는 뜻이지
      1 근처에 머문다는 뜻이 아니다. 항이 (1 + 무언가)라면 그 무언가만큼 매 층 커진다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>잔차만 넣으면 이번엔 폭주한다</h2>
    <p>
      순전파 쪽에서 보면 원인이 단순하다.
      각 블록의 출력을 이전 신호에 <em>더하기만</em> 하므로 신호는 누적된다.
      블록 출력들이 서로 독립이고 분산이 각각 1 이라면,
      <span class="mono">L</span> 개를 지난 뒤의 분산은 <span class="mono">1 + L</span> 이다.
    </p>
    <div class="eq">
      <span class="cap">잔차 스트림의 크기 누적 (블록 출력 분산 1, 독립 가정)</span>
      <div class="line">블록 &nbsp;&nbsp;0개 &nbsp; Var = &nbsp;1 &nbsp;&nbsp; 표준편차 1.000</div>
      <div class="line">블록 &nbsp;24개 &nbsp; Var = 25 &nbsp;&nbsp; 표준편차 <b>5.000</b></div>
      <div class="line">블록 &nbsp;48개 &nbsp; Var = 49 &nbsp;&nbsp; 표준편차 <b>7.000</b></div>
      <div class="line">블록 &nbsp;96개 &nbsp; Var = 97 &nbsp;&nbsp; 표준편차 <b>9.849</b></div>
      <div class="line">&nbsp;</div>
      <div class="line">// √L 로 자란다 — 폭발적이지는 않지만 무시할 수도 없다</div>
    </div>
    <p>
      순전파가 √L 로 자라는 동안 역전파는 훨씬 빠르게 자란다.
      기울기 쪽 곱 <span class="mono">∏(I + ∂F)</span> 은 층마다 배율이 곱해지므로 지수적이다.
      Fig. 2 에서 잰 5.06e21 이 그 결과다.
      그래서 <strong>잔차 연결은 혼자 쓰이는 법이 없다.</strong>
      크기를 되돌리는 장치와 반드시 짝을 이룬다. 처방은 크게 셋이다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>처방</th><th>무엇을 하는가</th><th>대가</th></tr>
        </thead>
        <tbody>
          <tr><td class="hi">정규화를 끼운다</td><td>블록마다 <a href="normalization.html">BN·LN</a> 으로 크기를 되돌린다</td><td>배치 의존·추론 시 통계 관리</td></tr>
          <tr><td class="hi">블록 끝을 0 으로</td><td>블록의 마지막 가중치를 0 초기화 (Fixup·ReZero)</td><td>초기 몇 스텝이 느리다</td></tr>
          <tr><td class="hi">가지에 게이트</td><td>학습되는 스칼라 α 를 곱해 α·F(x) + x</td><td>파라미터가 늘고 α 가 죽을 수 있다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      실무에서 압도적으로 많이 쓰인 것은 첫째다.
      원본 ResNet 은 <span class="mono">conv → BN → relu</span> 를 두 번 거친 뒤 더하고,
      더한 결과에 다시 ReLU 를 건다. 이 배치를 <em>사후 활성화</em>(post-activation)라 부른다.
    </p>
    <p>
      He 등이 이듬해에 낸 후속 논문이 이 배치를 다시 손봤다.
      더한 결과에 ReLU 를 걸면 <strong>항등 경로가 순수하지 않다</strong> —
      지름길로 온 신호도 매 블록 ReLU 를 한 번씩 통과하므로 음수 성분이 잘려 나간다.
      그래서 정규화와 활성화를 잔차 가지 <em>안쪽</em>으로 옮기고
      더한 결과는 그대로 두는 <em>사전 활성화</em>(pre-activation)로 바꿨다.
    </p>
    <div class="eq">
      <span class="cap">두 배치</span>
      <div class="line">사후 활성화 &nbsp; y = <b>relu</b>( BN(W₂ · relu(BN(W₁x))) + x )</div>
      <div class="line">사전 활성화 &nbsp; y = W₂ · relu(BN(W₁ · relu(BN(x)))) + x</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 아래쪽은 더한 결과에 아무것도 걸지 않는다 — 항등 경로가 입력에서 출력까지 한 번도 끊기지 않는다</div>
    </div>
    <p>
      같은 논쟁이 <a href="transformer.html">Transformer</a> 에서 그대로 반복됐다.
      원본 Transformer 는 <span class="mono">LayerNorm(x + Sublayer(x))</span> 의
      <em>Post-LN</em> 이었고, 지금 쓰이는 거의 모든 구현은
      <span class="mono">x + Sublayer(LayerNorm(x))</span> 의 <em>Pre-LN</em> 이다.
      Xiong 등(2020)이 짚은 것은 Post-LN 에서 출력층 근처 기울기가 커져
      <strong>워밍업 없이는 학습이 불안정하다</strong>는 점이었고,
      Pre-LN 은 워밍업 없이도 돈다.
      ResNet 의 사전 활성화와 정확히 같은 처방이 다섯 해 뒤 같은 이유로 다시 채택된 것이다.
    </p>
    <p>
      둘째 처방 — 블록 끝 0 초기화 — 는 Fig. 2 에서 이미 봤다.
      블록의 마지막 가중치가 0 이면 초기 상태의 망은 <strong>정확히 항등 함수</strong>이고,
      깊이에 무관하게 기울기 크기가 1 근처에 선다.
      죽은 초기화처럼 보이지만 그렇지 않다 —
      블록 안의 첫 가중치는 여전히 랜덤이므로 마지막 가중치에 대한 기울기는 0 이 아니고,
      첫 스텝부터 값이 붙는다.
      Fixup(2019)은 이 원리로 <em>정규화 층 없이</em> 만 층 규모를 학습시켰고,
      ReZero(2020)는 가지마다 0 으로 초기화된 스칼라 하나를 곱해 같은 효과를 냈다.
      확산 모델과 <a href="lora.html">LoRA</a> 계열이 새로 붙이는 가지를
      0 에서 출발시키는 관행도 뿌리가 같다 —
      <strong>붙이기 전과 정확히 같은 함수에서 시작한다.</strong>
    </p>
    <div class="note">
      <b>01 절 표의 가운데 열을 다시 보라.</b> 잔차를 넣었는데 18층부터 발산했다.
      정규화도 0 초기화도 없이 잔차만 넣은 설정이었다.
      <em>잔차 연결은 그 자체로 깊이를 주지 않는다.</em>
      깊이를 주는 것은 <strong>항등 경로와 크기 제어의 조합</strong>이고,
      어느 한쪽만으로는 방향만 바뀔 뿐 여전히 학습되지 않는다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>병목에서 잔차 스트림까지</h2>
    <p>
      깊이를 얻고 나면 다음 문제는 비용이다.
      256채널에서 3&times;3 합성곱을 두 번 쌓으면 가중치가 이만큼 든다.
    </p>
    <div class="eq">
      <span class="cap">블록 하나의 합성곱 가중치 (편향·BN 제외)</span>
      <div class="line">기본 블록 &nbsp; 3&times;3 (256→256) &times; 2 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>1,179,648</b></div>
      <div class="line">병목 블록 &nbsp; 1&times;1 (256→64) &nbsp;&nbsp; 16,384</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3&times;3 (64→64) &nbsp;&nbsp;&nbsp; 36,864</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1&times;1 (64→256) &nbsp;&nbsp; 16,384 &nbsp;&nbsp;&nbsp;&nbsp; 합 <b>69,632</b></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 같은 입출력 폭에서 <b>16.94배</b> 차이다</div>
    </div>
    <p>
      1&times;1 로 채널을 4분의 1 로 줄이고, 비싼 3&times;3 은 좁은 폭에서만 하고,
      다시 1&times;1 로 되돌린다. 이 <em>병목</em> 구조 덕분에
      50층·101층·152층이 현실적인 비용 안에 들어왔다.
      구성을 명시하고 직접 세어 보면 ResNet-50 은 이렇게 나온다.
    </p>
    <div class="eq">
      <span class="cap">ResNet-50 파라미터 — 7&times;7 스템, 폭 64·128·256·512, 확장 4, 블록 3·4·6·3</span>
      <div class="line">합성곱 가중치 &nbsp; 23,454,912</div>
      <div class="line">BN 파라미터 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 53,120</div>
      <div class="line">분류기 (2048→1000) &nbsp; 2,049,000</div>
      <div class="line">합계 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>25,557,032</b> &nbsp; (25.56M)</div>
    </div>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 190" role="img" aria-label="기본 블록과 병목 블록의 폭 비교. 기본 블록은 256채널에서 3x3 합성곱을 두 번 수행해 가중치가 1,179,648개다. 병목 블록은 1x1로 64채널까지 좁힌 뒤 3x3을 수행하고 다시 1x1로 256채널로 넓혀 가중치가 69,632개로 16.94배 적다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="16" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">같은 입출력 폭 256 — 안쪽을 좁힌다</text>

            <rect x="24" y="28" width="310" height="130" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <text x="36" y="46" font-size="9" fill="var(--ink-soft)">기본 블록</text>
            <rect x="60" y="62" width="44" height="64" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <rect x="130" y="62" width="44" height="64" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <rect x="200" y="62" width="44" height="64" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.4"/>
            <rect x="270" y="62" width="44" height="64" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="136" y="98" font-size="8.5" fill="var(--ink)">3&times;3</text>
            <text x="206" y="98" font-size="8.5" fill="var(--ink)">3&times;3</text>
            <text x="66" y="140" font-size="8" fill="var(--ink-faint)">256</text>
            <text x="276" y="140" font-size="8" fill="var(--ink-faint)">256</text>
            <text x="36" y="154" font-size="9" fill="var(--warn)">1,179,648 파라미터</text>

            <rect x="366" y="28" width="310" height="130" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <text x="378" y="46" font-size="9" fill="var(--accent)">병목 블록</text>
            <rect x="396" y="62" width="34" height="64" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <rect x="452" y="78" width="34" height="32" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <rect x="508" y="78" width="34" height="32" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <rect x="564" y="62" width="34" height="64" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="452" y="72" font-size="8" fill="var(--accent)">1&times;1</text>
            <text x="510" y="72" font-size="8" fill="var(--accent)">3&times;3</text>
            <text x="566" y="56" font-size="8" fill="var(--accent)">1&times;1</text>
            <text x="398" y="140" font-size="8" fill="var(--ink-faint)">256</text>
            <text x="458" y="140" font-size="8" fill="var(--ink-faint)">64</text>
            <text x="568" y="140" font-size="8" fill="var(--ink-faint)">256</text>
            <text x="378" y="154" font-size="9" fill="var(--accent)">69,632 파라미터 — 16.94배 적다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 3</span>
        병목이 아끼는 것은 <em>3&times;3 이 보는 채널 수</em>다.
        비용이 채널 수의 제곱으로 들기 때문에 폭을 4분의 1 로 줄이면 그 층만 16분의 1 이 된다.
        <a href="efficient-backbone.html">경량 백본</a>의 depthwise separable 도
        같은 질문에 다른 각도로 답한 것이다.
      </figcaption>
    </figure>

    <p>
      이 구조가 십 년을 견딘 이유는 성능보다 <em>이식성</em>에 있다.
      잔차 블록은 안에 무엇이 들었는지 묻지 않는다.
      합성곱을 <a href="transformer.html">어텐션</a>으로 갈아 끼워도,
      <a href="mamba-ssm.html">상태공간 모델</a>로 갈아 끼워도,
      <a href="mixture-of-experts.html">MoE</a> 라우터를 끼워도 바깥 계약은 같다 —
      <strong>들어온 것을 그대로 통과시키고 옆에서 무언가를 더한다.</strong>
    </p>
    <p>
      그래서 요즘은 잔차 연결을 <em>잔차 스트림</em>이라 부르는 관점이 널리 쓰인다.
      입력에서 출력까지 끊기지 않고 흐르는 하나의 통로가 있고,
      각 블록은 그 통로에서 읽어서 무언가를 <em>써 넣는다</em>는 그림이다.
      <a href="interpretability.html">해석가능성</a> 연구가 특정 층의 기여를
      빼거나 더해 볼 수 있는 것도 이 덧셈 구조 덕분이다 —
      곱으로 얽힌 망에서는 층 하나의 기여를 분리해 말할 수가 없다.
      <a href="vision-transformer.html">ViT</a> 가 <a href="cnn-basics.html">CNN</a> 의
      귀납 편향을 버리면서도 잔차 스트림만은 그대로 가져간 것도 같은 맥락이다.
    </p>
    <div class="note">
      <b>더하기와 잇기는 다르다.</b>
      <a href="segmentation.html">분할</a>과 <a href="diffusion-models.html">확산 모델</a>이 쓰는
      U-Net 의 스킵은 인코더의 특징 맵을 디코더에 <em>채널 방향으로 잇는다</em>(concat).
      해상도를 잃었다 되찾는 경로에서 잃어버린 고주파를 되돌려주는 것이 목적이고,
      채널 수가 늘어나므로 뒤에 이를 합칠 층이 필요하다.
      잔차의 덧셈은 폭을 유지한 채 <em>같은 자리에 값을 더하는</em> 것이라 목적이 다르다.
      <a href="super-resolution.html">초해상</a>과 <a href="denoising.html">노이즈 제거</a>처럼
      입력과 출력이 거의 같은 과제에서 전역 잔차(출력 = 입력 + 예측한 차이)를 쓰는 것은
      또 다른 변형이다 — 이때 망이 배우는 것은 이미지가 아니라 <strong>이미지의 보정량</strong>이다.
    </div>
    <p>
      한계도 분명하다. 잔차 연결은 <em>최적화</em>를 쉽게 만들 뿐
      <em>표현</em>을 늘리지 않는다.
      <a href="graph-neural-networks.html">GNN</a> 이 깊어질 때 겪는 과평활 문제처럼,
      층을 지날수록 표현이 뭉개지는 성질은 잔차를 넣어도 늦춰질 뿐 사라지지 않는다.
      깊이가 공짜가 된 것도 아니다 — 130층의 기울기가 6층과 같은 크기로 도착한다는 것은
      <strong>학습이 시작될 수 있다</strong>는 뜻이지 더 좋은 해에 도달한다는 보장이 아니다.
      01 절 표의 오른쪽 열에서 0 초기화 잔차 망도 50층에서 6층보다 오차가 높았다.
      다만 그 악화가 3.9배였고 평범한 망은 43배였다.
    </p>
    <p>
      정리하면 잔차 연결이 바꾼 것은 <strong>기본값</strong> 하나다.
      아무것도 배우지 않은 층이 신호를 지우는 대신 통과시키게 만들었고,
      그 결과 <em>층을 더 쌓는 일이 손해가 아니게</em> 됐다.
      <a href="nas.html">구조 탐색</a>이 훑는 공간도, <a href="knowledge-distillation.html">증류</a>가
      전제하는 교사의 깊이도, <a href="vision-transformer.html">ViT</a> 이후의 모든 블록도
      이 한 줄의 덧셈 위에 서 있다.
    </p>
  </section>
"""

READING = [
    "He et al., <em>Deep Residual Learning for Image Recognition</em> (arXiv:1512.03385) — 퇴화 문제의 제기와 잔차 블록·병목 구조.",
    "He et al., <em>Identity Mappings in Deep Residual Networks</em> (arXiv:1603.05027) — 항등 경로를 순수하게 두는 사전 활성화 배치.",
    "Srivastava et al., <em>Highway Networks</em> (arXiv:1505.00387) — 반년 앞선 게이트 달린 지름길. 게이트를 없앤 것이 ResNet 의 선택이었다.",
    "Veit et al., <em>Residual Networks Behave Like Ensembles of Relatively Shallow Networks</em> (arXiv:1605.06431) — 2ⁿ 경로와 블록 제거 실험.",
    "Zhang et al., <em>Fixup Initialization: Residual Learning Without Normalization</em> (arXiv:1901.09321) — 0 초기화만으로 정규화 없이 만 층을 학습시킨다.",
    "Bachlechner et al., <em>ReZero is All You Need: Fast Convergence at Large Depth</em> (arXiv:2003.04887) — 가지마다 0 으로 시작하는 스칼라 하나.",
    "Xiong et al., <em>On Layer Normalization in the Transformer Architecture</em> (arXiv:2002.04745) — Post-LN 과 Pre-LN, 그리고 워밍업이 필요했던 이유.",
]

write(
    "residual-connections.html",
    title="잔차 연결 — 기본값을 항등으로 바꾸기",
    eyebrow="Architecture · Residual · 2015–2026",
    h1="잔차 연결",
    subtitle="깊이를 가능하게 만든 한 줄의 덧셈 — ResNet 에서 잔차 스트림까지",
    dek=(
        "층을 더 쌓았더니 <strong>학습</strong> 오차가 올라갔다. 과적합이 아니라 최적화의 실패였다. "
        "해법은 층이 사상을 직접 배우게 하는 대신 "
        "<strong>입력을 그대로 더해 두고 차이만 배우게</strong> 하는 것이었다. "
        "다만 그것만으로는 이번엔 기울기가 터진다 — "
        "직접 재 보면 130층에서 5.06e21 이다. 그 절반의 이야기까지 함께 적는다."
    ),
    spec=[
        ("고치려는 것", "깊이의 퇴화 (학습 오차 증가)"),
        ("바꾸는 것", "블록의 기본값 = 항등"),
        ("기울기", "곱 → (I + ∂F) 의 곱"),
        ("반드시 짝짓는 것", "정규화 또는 0 초기화"),
        ("지금", "모든 블록의 바깥 계약"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-19",
)

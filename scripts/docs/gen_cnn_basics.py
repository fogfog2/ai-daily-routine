#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1f0", panel="#e5e8e6", ink="#141a16", **{
    "ink-soft": "#4c5750", "ink-faint": "#7b857e", "rule": "#ccd3cf",
    "rule-strong": "#a9b1ac", "accent": "#1f6048", "accent-fill": "#d8eae2",
    "accent-line": "#3a8a68", "muted": "#83888c", "muted-fill": "#dee1df", "warn": "#a04a28",
})
DARK = dict(paper="#0e1211", panel="#161b18", ink="#e3eae6", **{
    "ink-soft": "#a0aba5", "ink-faint": "#6f7a75", "rule": "#202725", "rule-strong": "#36403b",
    "accent": "#55c396", "accent-fill": "#0d2a20", "accent-line": "#328a68",
    "muted": "#868d8a", "muted-fill": "#191f1c", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>완전연결로 이미지를 다루면</h2>
    <p>
      224×224 컬러 이미지를 완전연결 층에 넣는다고 하자.
      입력이 <code>224 × 224 × 3 = 150,528</code> 차원이고,
      은닉 유닛 1,000개를 두면 파라미터가 <strong>1억 5천만 개</strong>다. 층 하나에.
    </p>
    <p>
      개수만 문제가 아니다. 더 근본적인 것은 <strong>구조를 버린다</strong>는 점이다.
      완전연결 층은 입력을 일렬로 편다. 그 순간
      <em>어느 픽셀이 어느 픽셀 옆에 있었는지</em>가 사라진다.
    </p>
    <p>
      그런데 이미지에는 분명한 규칙성이 있다.
    </p>
    <ul>
      <li><strong>가까운 픽셀이 관련 있다.</strong> 한 픽셀은 옆 픽셀과 함께 의미를 이룬다</li>
      <li><strong>같은 무늬가 어디서든 나타난다.</strong> 왼쪽 위의 모서리와 오른쪽 아래의 모서리는 같은 모서리다</li>
    </ul>
    <p>
      합성곱은 이 두 가지를 <strong>구조에 새겨 넣은 것</strong>이다.
      데이터로 배우게 하는 대신 처음부터 그렇게 만든다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>두 개의 제약 — 지역성과 공유</h2>
    <p>
      합성곱 층이 완전연결과 다른 점은 <em>두 개의 제약</em>을 건 것뿐이다.
    </p>
    <div class="eq">
      <span class="cap">합성곱 = 제약이 걸린 완전연결</span>
      <div class="line">① <strong>지역 연결</strong> — 출력 하나가 입력의 k×k 창만 본다</div>
      <div class="line">② <strong>가중치 공유</strong> — 모든 위치가 <em>같은</em> 커널을 쓴다</div>
      <div class="line">&nbsp;</div>
      <div class="line">파라미터: C<sub>in</sub> · C<sub>out</sub> · k · k&nbsp;&nbsp;&nbsp;// 입력 크기와 <strong>무관</strong></div>
    </div>
    <p>
      마지막 줄이 결정적이다. 입력이 224×224든 1024×1024든
      <strong>파라미터 수가 같다</strong>. 위치마다 다른 가중치를 두지 않기 때문이다.
    </p>
    <p>
      가중치 공유는 부수 효과도 낳는다. 같은 커널이 모든 위치를 훑으므로
      <em>무늬가 어디 있든 같은 방식으로 반응</em>한다. 이것을
      <strong>평행이동 등변성</strong>(translation equivariance)이라 한다 —
      입력이 오른쪽으로 움직이면 출력도 오른쪽으로 움직인다.
    </p>
    <div class="note">
      <b>등변성과 불변성은 다르다.</b> 합성곱 자체는 <em>등변</em>이다 — 위치가 따라 움직인다.
      분류에 필요한 것은 <em>불변</em>이다 — 어디 있든 같은 답이 나와야 한다.
      그 전환을 맡는 것이 풀링과 마지막의 전역 평균이다.
      "합성곱이 위치에 불변하다"는 흔한 설명은 정확하지 않다.
    </div>
    <p>
      이 제약들이 <a href="vision-transformer.html">ViT 문서</a>가 말한
      <strong>귀납 편향</strong>의 정체다. 편향은 공짜가 아니다 —
      데이터가 적을 때는 시작점을 크게 올려주지만,
      데이터가 아주 많아지면 <em>그 가정이 오히려 천장이 된다</em>.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>수용 영역 — 얼마나 멀리 보는가</h2>
    <p>
      3×3 커널 하나는 3픽셀만 본다. 그런데 그 출력을 다시 3×3으로 보면
      원본 기준 5픽셀을 본 셈이 된다. 층을 쌓을수록 <strong>보는 범위가 넓어진다</strong>.
      이것이 <strong>수용 영역</strong>이다.
    </p>
    <div class="eq">
      <span class="cap">3×3 을 쌓을 때 (stride 1) — 선형으로 늘어난다</span>
      <div class="line">&nbsp;1층 →&nbsp;&nbsp; 3 px</div>
      <div class="line">&nbsp;2층 →&nbsp;&nbsp; 5 px</div>
      <div class="line">&nbsp;3층 →&nbsp;&nbsp; 7 px</div>
      <div class="line">&nbsp;5층 →&nbsp; 11 px</div>
      <div class="line">10층 →&nbsp; 21 px&nbsp;&nbsp;// 224 이미지에서 아직 한참 작다</div>
    </div>
    <p>
      층당 2픽셀씩만 는다. 이대로는 이미지 전체를 보려면 100층 넘게 필요하다.
      그래서 <strong>다운샘플링</strong>(stride 2 또는 풀링)을 섞는다.
      해상도를 절반으로 줄이면 <em>이후 층의 시야가 두 배</em>가 된다.
    </p>
    <div class="eq">
      <span class="cap">3×3, 3×3, 풀링을 한 블록으로 반복하면 — 지수적으로 는다</span>
      <div class="line">블록 1 → 수용영역&nbsp;&nbsp; 6 px,&nbsp; 누적 stride&nbsp; 2</div>
      <div class="line">블록 2 → 수용영역&nbsp; 16 px,&nbsp; 누적 stride&nbsp; 4</div>
      <div class="line">블록 3 → 수용영역&nbsp; 36 px,&nbsp; 누적 stride&nbsp; 8</div>
      <div class="line">블록 4 → 수용영역&nbsp; 76 px,&nbsp; 누적 stride 16</div>
    </div>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 232" role="img" aria-label="수용 영역이 층을 쌓으며 넓어지는 과정. stride 1로만 쌓으면 층당 2픽셀씩 선형으로 늘지만, 다운샘플링을 섞으면 이후 층의 시야가 배로 커져 지수적으로 넓어진다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="cn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">한 칸의 출력이 원본에서 보는 범위</text>

            <g>
              <text x="24" y="42" font-size="8.5" fill="var(--ink-faint)">입력</text>
              <g stroke="var(--rule)" stroke-width="0.7" fill="var(--muted-fill)">
                <rect x="60" y="32" width="14" height="14"/><rect x="76" y="32" width="14" height="14"/>
                <rect x="92" y="32" width="14" height="14"/><rect x="108" y="32" width="14" height="14"/>
                <rect x="124" y="32" width="14" height="14"/><rect x="140" y="32" width="14" height="14"/>
                <rect x="156" y="32" width="14" height="14"/>
              </g>
              <rect x="92" y="32" width="46" height="14" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.4"/>
            </g>

            <path d="M115 50 L115 66" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#cn-a)"/>

            <g>
              <text x="24" y="82" font-size="8.5" fill="var(--ink-faint)">1층</text>
              <g stroke="var(--rule)" stroke-width="0.7" fill="var(--muted-fill)">
                <rect x="76" y="72" width="14" height="14"/><rect x="92" y="72" width="14" height="14"/>
                <rect x="108" y="72" width="14" height="14"/><rect x="124" y="72" width="14" height="14"/>
                <rect x="140" y="72" width="14" height="14"/>
              </g>
              <rect x="92" y="72" width="46" height="14" fill="var(--accent)" opacity="0.55" stroke="var(--accent-line)" stroke-width="1.4"/>
              <text x="170" y="83" font-size="8" fill="var(--accent)">3 px</text>
            </g>

            <path d="M115 90 L115 106" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#cn-a)"/>

            <g>
              <text x="24" y="122" font-size="8.5" fill="var(--ink-faint)">2층</text>
              <g stroke="var(--rule)" stroke-width="0.7" fill="var(--muted-fill)">
                <rect x="92" y="112" width="14" height="14"/><rect x="108" y="112" width="14" height="14"/>
                <rect x="124" y="112" width="14" height="14"/>
              </g>
              <rect x="108" y="112" width="14" height="14" fill="var(--accent)" opacity="0.85" stroke="var(--accent-line)" stroke-width="1.4"/>
              <text x="170" y="123" font-size="8" fill="var(--accent)">5 px</text>
            </g>

            <text x="24" y="158" font-size="8.5" fill="var(--warn)">stride 1 만 쓰면 층당 +2 px — 너무 느리다</text>

            <line x1="240" y1="26" x2="240" y2="222" stroke="var(--rule)" stroke-width="1"/>

            <text x="264" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">다운샘플링을 섞으면</text>

            <g>
              <rect x="264" y="34" width="120" height="30" fill="var(--accent)" opacity="0.2" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="324" y="53" text-anchor="middle" font-size="8" fill="var(--ink)">블록 1 — 6 px</text>
              <rect x="264" y="70" width="120" height="30" fill="var(--accent)" opacity="0.3" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="324" y="89" text-anchor="middle" font-size="8" fill="var(--ink)">블록 2 — 16 px</text>
              <rect x="264" y="106" width="120" height="30" fill="var(--accent)" opacity="0.45" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="324" y="125" text-anchor="middle" font-size="8" fill="var(--ink)">블록 3 — 36 px</text>
              <rect x="264" y="142" width="120" height="30" fill="var(--accent)" opacity="0.6" stroke="var(--accent-line)" stroke-width="1.3"/>
              <text x="324" y="161" text-anchor="middle" font-size="8" fill="var(--ink)">블록 4 — 76 px</text>
            </g>
            <text x="264" y="192" font-size="8.5" fill="var(--accent)">해상도를 줄이면 이후 층의 시야가 배가 된다</text>
            <text x="264" y="206" font-size="8" fill="var(--ink-faint)">→ 적은 층으로 넓게 볼 수 있다</text>

            <line x1="410" y1="26" x2="410" y2="222" stroke="var(--rule)" stroke-width="1"/>

            <text x="434" y="46" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">대가</text>
            <text x="434" y="70" font-size="8.5" fill="var(--warn)">해상도를 잃는다</text>
            <text x="434" y="86" font-size="8" fill="var(--ink-faint)">작은 물체·정밀한 경계가 사라진다</text>
            <text x="434" y="110" font-size="8.5" fill="var(--ink-soft)">그래서 검출·분할은</text>
            <text x="434" y="126" font-size="8" fill="var(--ink-faint)">여러 단계의 특징을 함께 쓴다 (FPN)</text>
            <text x="434" y="150" font-size="8.5" fill="var(--accent)">또는 dilated 합성곱으로</text>
            <text x="434" y="166" font-size="8" fill="var(--ink-faint)">해상도를 지키며 시야만 넓힌다</text>
            <text x="434" y="196" font-size="8" fill="var(--ink-faint)">유효 수용 영역은 이론값보다 작고</text>
            <text x="434" y="210" font-size="8" fill="var(--ink-faint)">중심이 가우시안처럼 진하다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>해상도와 시야는 맞바꾸는 관계다.</strong>
        넓게 보려면 줄여야 하고, 줄이면 세부를 잃는다.
        검출과 분할이 어려운 이유가 여기 있다 — <em>둘 다 필요</em>하기 때문이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>깊이가 만든 문제와 잔차 연결</h2>
    <p>
      층을 쌓으면 수용 영역이 넓어지고 표현력도 는다. 그런데 실제로 깊게 쌓아 보면
      <strong>더 깊은 망이 더 나쁜 결과</strong>를 내는 일이 벌어졌다.
      과적합이 아니라 <em>학습 오차 자체</em>가 높았다.
    </p>
    <p>
      이상한 일이다. 추가된 층이 항등 함수만 배워도 얕은 망과 같아야 하는데,
      그것조차 못 배웠다. <strong>최적화가 어려운 것</strong>이 문제였다.
    </p>
    <p>
      <strong>잔차 연결</strong>의 답은 간단하다 — 항등 함수를 <em>배우게 하지 말고 그냥 준다</em>.
    </p>
    <div class="eq">
      <span class="cap">잔차 블록 — 변화량만 배운다</span>
      <div class="line">일반:&nbsp; y = F(x)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 목표 전체를 배워야 한다</div>
      <div class="line">잔차:&nbsp; y = F(x) + <strong>x</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 목표와의 <em>차이</em>만 배우면 된다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// F 가 0 이면 항등 — 아무것도 안 하는 것이 기본값이 된다</div>
    </div>
    <p>
      역전파 관점에서도 이득이 명확하다. 덧셈은 그래디언트를 <strong>그대로 통과</strong>시키므로,
      깊은 층에서도 신호가 앞까지 도달한다.
      <a href="rnn-lstm.html">LSTM 의 셀 상태</a>가 시간축에서 하던 일을 깊이축에서 하는 셈이다.
    </p>
    <div class="note">
      <b>이 아이디어는 비전을 넘어갔다.</b> <a href="transformer.html">트랜스포머</a>의 모든 블록에
      잔차 연결이 들어 있고, U-Net 의 스킵 연결도 같은 계열이다.
      "깊게 쌓으려면 지름길을 둔다"는 것이 <em>구조 설계의 기본 문법</em>이 됐다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>합성곱은 끝났는가</h2>
    <p>
      <a href="vision-transformer.html">ViT</a> 가 나온 뒤 "합성곱의 시대가 끝났다"는 말이 돌았다.
      실제로는 그렇게 단순하지 않다.
    </p>
    <p>
      ViT 는 <strong>대규모 데이터</strong>에서 CNN 을 앞섰다.
      그런데 데이터가 충분치 않으면 여전히 CNN 의 편향이 유리하다.
      그리고 흥미롭게도, ViT 계열이 성공한 뒤 나온 연구들은
      <em>합성곱에 트랜스포머의 설계 요소를 이식</em>하면 비슷한 성능이 난다는 것을 보였다 —
      큰 커널, 적은 정규화, 다른 활성함수 같은 것들이다.
    </p>
    <p>
      즉 차이의 상당 부분은 <strong>어텐션 자체가 아니라 학습 레시피와 설계 관행</strong>에 있었다.
      <a href="yolov5.html">YOLOv5</a> 문서에서 본 것과 같은 결론이다 —
      구조보다 <em>잘 조율된 학습</em>이 성능을 가르는 경우가 많다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>상황</th><th>유리한 쪽</th><th>이유</th></tr>
        </thead>
        <tbody>
          <tr><td>데이터가 적다</td><td class="hi">CNN</td><td>편향이 시작점을 올린다</td></tr>
          <tr><td>데이터가 아주 많다</td><td class="hi">ViT</td><td>편향이 천장이 된다</td></tr>
          <tr><td>고해상 입력</td><td>CNN 또는 계층형 ViT</td><td>어텐션은 O(N²)</td></tr>
          <tr><td><a href="efficient-backbone.html">온디바이스</a></td><td class="hi">CNN 계열</td><td>연산자 지원·최적화가 성숙</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 실무에서 자주 결정적이다. 모바일 가속기와 런타임은
      합성곱에 오래 최적화돼 왔고, 지원 연산자 목록도 그쪽이 넓다.
      <em>이론적 우열과 배포 가능성은 다른 문제</em>다.
    </p>
    <p>
      정리하면 합성곱은 <strong>"가까운 것이 관련 있고, 같은 무늬는 어디서든 같다"</strong>는
      두 가정을 구조로 옮긴 것이다.
      그 가정이 맞는 데이터에서는 여전히 강력하고, 최근 구조들도 대부분
      초반 층이나 다운샘플링에 합성곱을 남겨 둔다.
    </p>
  </section>
"""

READING = [
    "LeCun et al., <em>Gradient-Based Learning Applied to Document Recognition</em> (Proc. IEEE 1998) — LeNet. 합성곱 구조의 원형.",
    "Krizhevsky et al., <em>ImageNet Classification with Deep Convolutional Neural Networks</em> (NeurIPS 2012) — AlexNet.",
    "Simonyan &amp; Zisserman, <em>Very Deep Convolutional Networks for Large-Scale Image Recognition</em> (arXiv:1409.1556) — VGG. 3×3 을 쌓는 설계.",
    "He et al., <em>Deep Residual Learning for Image Recognition</em> (arXiv:1512.03385) — ResNet. 깊이의 최적화 문제와 잔차 연결.",
    "Luo et al., <em>Understanding the Effective Receptive Field in Deep CNNs</em> (arXiv:1701.04128) — 유효 수용 영역은 이론값보다 작다.",
    "Liu et al., <em>A ConvNet for the 2020s</em> (arXiv:2201.03545) — 설계 관행을 옮기면 CNN 도 ViT 급이 된다는 결과.",
]

write(
    "cnn-basics.html",
    title="CNN 기초 — 합성곱·풀링·수용 영역",
    eyebrow="Vision · Fundamentals · 1998–2026",
    h1="CNN 기초",
    subtitle="합성곱·풀링·수용 영역 — 이미지의 규칙성을 구조에 새기다",
    dek=(
        "224×224 이미지를 완전연결에 넣으면 층 하나에 파라미터가 1억 5천만 개다. "
        "게다가 입력을 일렬로 펴는 순간 <em>어느 픽셀이 어디 있었는지</em>가 사라진다. "
        "합성곱은 <strong>가까운 것이 관련 있고, 같은 무늬는 어디서든 같다</strong>는 "
        "두 가정을 구조에 새겨 넣은 것이다. 그 가정이 곧 귀납 편향이다."
    ),
    spec=[
        ("두 제약", "지역 연결 · 가중치 공유"),
        ("파라미터", "입력 크기와 무관"),
        ("성질", "등변성 (불변성 아님)"),
        ("수용 영역", "stride 1 이면 층당 +2px"),
        ("깊이 문제", "잔차 연결로 해소"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

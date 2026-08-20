#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1efea", panel="#e7e3da", ink="#181310", **{
    "ink-soft": "#544c43", "ink-faint": "#847a6d", "rule": "#d4cec2",
    "rule-strong": "#b2a897", "accent": "#8a5320", "accent-fill": "#f0e3ce",
    "accent-line": "#b5793a", "muted": "#8a8074", "muted-fill": "#e2ded4", "warn": "#a33b28",
})
DARK = dict(paper="#100e0b", panel="#18140f", ink="#ece5db", **{
    "ink-soft": "#a99f8f", "ink-faint": "#71685c", "rule": "#221d16", "rule-strong": "#3a3126",
    "accent": "#e0a256", "accent-fill": "#26190a", "accent-line": "#a9772f",
    "muted": "#8b8173", "muted-fill": "#1a1610", "warn": "#e08a5c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>흐림은 곱셈이 아니라 겹침이다</h2>
    <p>
      흔들린 사진에서 가로등 하나가 여러 개로 번져 보인다.
      이것은 밝기가 <em>흐려진</em> 것이 아니라, <strong>한 점의 빛이 여러 자리로 퍼져 겹친</strong> 것이다.
      노출 시간 동안 카메라가 움직이면, 장면의 각 점이 센서 위에서 궤적을 그리며
      그 궤적을 따라 밝기가 흩뿌려진다.
    </p>
    <p>
      이 퍼짐을 하나의 도장(kernel)으로 볼 수 있다. 점 하나가 어떤 모양으로 번지는지 —
      이것이 <strong>점 확산 함수(PSF)</strong>다. 흐린 이미지는 선명한 원본의 모든 점에
      같은 도장을 찍어 더한 것, 즉 <strong>합성곱(convolution)</strong>이다.
    </p>
    <div class="eq">
      <span class="cap">흐림의 형성 모델</span>
      <div class="line"><strong>b = k ∗ x + n</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">b = 흐린 이미지 &nbsp; x = 선명한 원본 &nbsp; k = 흐림 커널(PSF) &nbsp; n = 노이즈</div>
      <div class="line">∗ = 합성곱 — 원본의 각 점에 커널을 찍어 전부 더한다</div>
    </div>
    <p>
      커널의 모양이 흐림의 종류를 말해 준다.
    </p>
    <ul>
      <li><strong>움직임 흐림</strong> — 커널이 <em>선분</em>이다. 방향과 길이가 카메라·피사체의 궤적을 담는다</li>
      <li><strong>초점 흐림</strong> — 커널이 <em>원반</em>이다. 렌즈 조리개 모양이 그대로 번짐이 된다</li>
      <li><strong>공간에 따라 변함</strong> — 회전 흔들림이나 서로 다른 거리의 물체는 <em>자리마다 커널이 다르다</em></li>
    </ul>
    <div class="note">
      <b>왜 이 관점이 중요한가.</b> 흐림을 "곱해진 흐릿함"이 아니라 <strong>겹쳐진 원본</strong>으로 보면,
      복원은 곧 <em>겹침을 되돌리는 것</em>(deconvolution)이 된다.
      그리고 <a href="optical-flow.html">광류</a>가 프레임 사이의 움직임을 재는 것과 같은 궤적이
      한 장 안에서는 움직임 흐림의 커널이 된다 — 움직임을 재는 문제와 흐림을 푸는 문제는 뿌리가 같다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>거꾸로 나누면 왜 터지는가</h2>
    <p>
      합성곱은 주파수 영역에서 곱셈이 된다. 그러니 흐림을 되돌리는 가장 단순한 생각은
      <em>그 곱셈을 나눗셈으로 되돌리는</em> 것이다.
    </p>
    <div class="eq">
      <span class="cap">순진한 역필터 — 그리고 그것이 터지는 이유</span>
      <div class="line">주파수 영역:&nbsp; B = K · X + N</div>
      <div class="line">나눠서 복원:&nbsp; X̂ = B / K = X + <strong>N / K</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// K 가 작은 주파수에서 N/K 가 폭발한다</div>
      <div class="line">// K=0.02, 노이즈 1% → N/K = <strong>50%</strong> 오차</div>
    </div>
    <p>
      문제는 커널이 <strong>어떤 주파수를 아예 0으로 지운다</strong>는 것이다.
      길이 <code>L</code> 픽셀의 직선 움직임 흐림은 상자(box) 모양이라,
      그 스펙트럼이 <code>1/L, 2/L, …</code> 주파수에서 정확히 0이 된다.
      <em>거기 담겼던 정보는 사라졌다.</em> 0으로 나누는 것은 없는 정보를 지어내라는 요구다 —
      결과는 온 화면을 뒤덮는 물결무늬(ringing)로 폭발한다.
    </p>
    <p>
      그래서 실무의 첫 도구는 <strong>위너 필터(Wiener filter)</strong>다.
      나눗셈에 신호 대 잡음비(SNR)를 넣어, <em>믿을 만한 주파수는 되돌리고 위험한 주파수는 눌러</em>준다.
    </p>
    <div class="eq">
      <span class="cap">위너 필터 — SNR 이 스스로 브레이크를 건다</span>
      <div class="line">X̂ = <strong>K̄ / ( |K|² + 1/SNR )</strong> · B</div>
      <div class="line">&nbsp;</div>
      <div class="line">SNR 큼 (믿을 만함) → 1/K 에 가까움&nbsp;&nbsp;// 되돌린다</div>
      <div class="line">|K|² ≪ 1/SNR (위험) → 0 에 가까움&nbsp;&nbsp;&nbsp;&nbsp;// 손대지 않는다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// K=0.02 에서: SNR=10⁶ → 이득 49.9 (≈ 역필터 50)</div>
      <div class="line">//&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; SNR=100&nbsp; → 이득 1.9 (억제)</div>
    </div>
    <p>
      <strong>리처드슨–루시(Richardson–Lucy)</strong>는 다른 각도로 같은 문제를 다룬다.
      밝기는 음수가 될 수 없고 노이즈가 포아송이라는 <a href="denoising.html">촬영의 물리</a>를 반복 갱신에 넣어,
      물리적으로 말이 되는 해로 수렴시킨다. 두 방법 모두 핵심은 같다 —
      <em>순진한 나눗셈을 그대로 두지 않고, 무언가로 제동을 건다.</em>
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>정답이 하나가 아니다</h2>
    <p>
      제동을 걸어도 근본 난점은 남는다. <strong>같은 흐린 이미지를 만드는 선명한 원본이 무수히 많다.</strong>
      이것이 복원을 <em>부정치(ill-posed)</em> 문제로 만든다 —
      <a href="super-resolution.html">초해상</a>이 한 픽셀에서 여러 픽셀을 지어내야 하는 것과 같은 성질이다.
    </p>
    <p>
      갈래를 좁히는 것은 <strong>사전지식(prior)</strong>, 즉 <em>"자연스러운 이미지란 어떤 것인가"</em>에 대한 가정이다.
      가장 강력한 단서는 <strong>기울기의 분포</strong>에 있다.
    </p>
    <div class="eq">
      <span class="cap">자연 이미지의 기울기는 희소하다</span>
      <div class="line">대부분의 픽셀: 이웃과 거의 같다 → 기울기 ≈ 0 (평평한 면)</div>
      <div class="line">드문 픽셀:&nbsp;&nbsp;&nbsp; 경계에서 크게 튄다&nbsp; → 무거운 꼬리 (edge)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 흐림은 경계를 완만하게 펴서 이 꼬리를 뭉갠다</div>
      <div class="line">// → 희소한 기울기를 선호하는 사전지식이 선명함을 되살린다</div>
    </div>
    <p>
      흐림은 날카로운 경계를 완만한 경사로 바꾼다. 그래서 <em>기울기가 뾰족하게 몰려 있는</em> 해를 선호하도록
      벌점을 주면(전변동 TV, L1 기울기), 복원이 경계를 다시 날카롭게 세운다.
      이것이 <a href="denoising.html">노이즈 제거</a>·초해상·디블러가 공유하는 한 가지 틀이다 —
      <strong>데이터 충실도 + 사전지식</strong>, 즉 <em>"흐리게 만들면 원본과 맞아야 하고, 동시에 자연스러워야 한다"</em>.
    </p>
    <div class="note">
      <b>순진한 최적화가 오히려 흐린 답을 고른다.</b>
      선명한 원본 <code>x</code> 와 커널 <code>k</code> 를 <em>동시에</em> 가장 그럴듯하게 찾으면(MAP<sub>x,k</sub>),
      뜻밖에도 <strong>"커널은 점(무흐림), 원본은 흐린 그대로"</strong> 라는 답이 이길 때가 많다 —
      흐린 이미지 자체가 기울기가 작아 사전지식 점수가 높기 때문이다.
      Levin 등(2009)이 짚은 이 함정 때문에, 좋은 블라인드 방법은 <em>원본을 적분해 없애고 커널만</em> 추정하거나,
      경계를 억지로 세우는 별도 장치를 둔다. <strong>목적함수를 잘못 세우면 아무것도 안 하는 것이 최적이 된다.</strong>
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>커널을 모를 때 — 닭이 먼저냐 달걀이 먼저냐</h2>
    <p>
      지금까지는 커널 <code>k</code> 를 안다고 가정했다(비블라인드). 현실의 흔들린 사진은
      커널조차 모른다 — <strong>블라인드 디컨볼루션</strong>이다.
      선명한 원본을 알면 커널을 알 수 있고, 커널을 알면 원본을 풀 수 있다. 그런데 <em>둘 다 모른다.</em>
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 250" role="img" aria-label="흐림의 형성과 블라인드 복원. 위: 선명한 점(원본)에 선분 모양 커널을 합성곱하면 번진 궤적이 된다. 가운데: 비블라인드는 커널을 알고 원본만 푼다. 아래: 블라인드는 커널과 원본을 번갈아 추정하며, 거친 해상도에서 시작해 점점 세밀하게 좁혀 간다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="db-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">형성 — 원본 ∗ 커널 = 흐림</text>
            <rect x="24" y="28" width="52" height="46" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <circle cx="50" cy="51" r="2.4" fill="var(--ink)"/>
            <text x="50" y="88" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">선명한 점</text>
            <text x="90" y="54" font-size="13" fill="var(--muted)">∗</text>
            <rect x="108" y="28" width="52" height="46" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <line x1="120" y1="62" x2="148" y2="40" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round"/>
            <text x="134" y="88" text-anchor="middle" font-size="7.5" fill="var(--accent)">커널(궤적)</text>
            <text x="174" y="54" font-size="13" fill="var(--muted)">=</text>
            <rect x="192" y="28" width="52" height="46" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <g stroke="var(--ink-soft)" stroke-width="2.2" stroke-linecap="round" opacity="0.5">
              <line x1="204" y1="62" x2="232" y2="40"/></g>
            <g stroke="var(--ink-faint)" stroke-width="1.4" stroke-linecap="round" opacity="0.35">
              <line x1="208" y1="60" x2="228" y2="44"/></g>
            <text x="218" y="88" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">번진 점</text>

            <line x1="290" y1="24" x2="290" y2="96" stroke="var(--rule)" stroke-width="1"/>

            <text x="312" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">비블라인드 — 커널을 안다</text>
            <rect x="312" y="34" width="90" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <text x="357" y="47" text-anchor="middle" font-size="8" fill="var(--ink-soft)">흐림 b + 커널 k</text>
            <path d="M357 56 L357 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#db-a)"/>
            <rect x="312" y="72" width="90" height="20" fill="var(--accent)" opacity="0.2" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="357" y="85" text-anchor="middle" font-size="8" fill="var(--accent)">원본 x 를 푼다</text>

            <text x="430" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">블라인드 — 둘 다 모른다</text>
            <rect x="430" y="34" width="70" height="20" fill="var(--muted-fill)" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="465" y="47" text-anchor="middle" font-size="8" fill="var(--ink-soft)">흐림 b 만</text>
            <path d="M512 44 L540 44" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#db-a)"/>
            <rect x="548" y="30" width="60" height="12" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="0.9"/>
            <text x="578" y="39" text-anchor="middle" font-size="7" fill="var(--accent)">커널 추정</text>
            <rect x="548" y="48" width="60" height="12" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="0.9"/>
            <text x="578" y="57" text-anchor="middle" font-size="7" fill="var(--accent)">원본 추정</text>
            <path d="M612 36 C 632 40, 632 52, 612 56" stroke="var(--muted)" stroke-width="1" fill="none" marker-end="url(#db-a)"/>
            <text x="640" y="49" font-size="7" fill="var(--muted)">번갈아</text>

            <line x1="24" y1="120" x2="676" y2="120" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="140" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">거친 곳에서 세밀한 곳으로 (coarse-to-fine)</text>
            <g>
              <rect x="40" y="158" width="30" height="30" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="55" y="177" text-anchor="middle" font-size="9" fill="var(--accent)">큰 흐림</text>
              <path d="M78 173 L108 173" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#db-a)"/>
              <rect x="116" y="152" width="42" height="42" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="137" y="176" text-anchor="middle" font-size="9" fill="var(--accent)">중간</text>
              <path d="M166 173 L196 173" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#db-a)"/>
              <rect x="204" y="146" width="54" height="54" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="231" y="176" text-anchor="middle" font-size="9" fill="var(--accent)">원해상도</text>
            </g>
            <text x="290" y="168" font-size="8.5" fill="var(--ink-soft)">작게 줄이면 큰 흐림도 몇 픽셀로 보인다.</text>
            <text x="290" y="184" font-size="8.5" fill="var(--ink-soft)">거기서 커널의 대략을 잡고, 해상도를 올리며 다듬는다 —</text>
            <text x="290" y="200" font-size="8" fill="var(--warn)">처음부터 원해상도에서 풀면 엉뚱한 국소해에 빠진다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        블라인드 디컨볼루션은 <strong>번갈아 추정</strong>한다 — 커널을 고정하고 원본을 풀고,
        원본을 고정하고 커널을 푼다. 여기에 <strong>거친 해상도부터</strong> 시작하는 것이 핵심이다.
        작게 줄이면 큰 흔들림도 작은 커널이 되어 잡기 쉽고, 그 대략을 올려 가며 다듬는다.
        <a href="segmentation.html">여러 비전 과제</a>에서 쓰는 피라미드식 접근과 같은 발상이다.
      </figcaption>
    </figure>

    <p>
      번갈아 푸는 방식은 시작점에 민감하고, 앞서 본 <em>MAP 함정</em>에 빠지기 쉽다.
      그래서 고전 블라인드 디블러는 강한 경계를 골라 커널을 추정하고,
      코스-투-파인으로 국소해를 피하는 등 <strong>세공(細工)</strong>이 많이 필요했다.
      이 복잡함이 다음 절의 전환을 불렀다 — <em>커널을 아예 추정하지 않는다.</em>
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>커널을 건너뛰기 — 데이터로 배우기</h2>
    <p>
      학습 기반 방법은 질문을 바꾼다. 커널을 추정하고 그것으로 원본을 푸는 대신,
      <strong>흐린 이미지에서 선명한 이미지로 곧장 가는 함수</strong>를 데이터로 배운다.
      커널은 신경망 안에 암묵적으로 녹는다.
    </p>
    <p>
      그러려면 <em>(흐린, 선명한)</em> 쌍이 대량으로 필요하다. 손으로 흔들어 찍을 수는 없으니,
      가장 널리 쓰인 방법이 <strong>고속 촬영 프레임을 평균</strong>내는 것이다 —
      노출 시간 동안 빛이 쌓이는 과정을 그대로 흉내 낸다.
    </p>
    <div class="eq">
      <span class="cap">움직임 흐림을 합성하는 법 (GoPro 식 데이터)</span>
      <div class="line">240fps 로 찍은 연속 프레임 x₁ … x_M 을</div>
      <div class="line">평균: &nbsp; b = (x₁ + x₂ + … + x_M) / M</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 노출 중 빛이 적분되는 물리를 그대로 흉내 낸다</div>
      <div class="line">// 가운데 프레임 x_(M/2) 가 "선명한 정답"</div>
    </div>
    <p>
      그 위에서 신경망은 몇 가지 요령으로 커진 문제를 감당한다.
      큰 흐림을 한 번에 못 푸니 <strong>여러 해상도로 나눠</strong> 거친 곳부터 풀고(멀티스케일),
      선명한 원본을 통째로 그리는 대신 <a href="residual-connections.html">흐림 이미지에 더할 보정만</a> 배운다 —
      <a href="denoising.html">노이즈 제거</a>에서 노이즈만 예측한 것과 같은 잔차 학습이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>접근</th><th>핵심</th><th>대가</th></tr>
        </thead>
        <tbody>
          <tr><td>위너 · 리처드슨–루시</td><td>커널을 알 때 빠르고 해석 가능</td><td class="hi">커널을 모르면 못 쓴다</td></tr>
          <tr><td>고전 블라인드</td><td>사전지식으로 커널까지 추정</td><td class="hi">세공 많음 · 국소해에 취약</td></tr>
          <tr><td>직접 회귀 (멀티스케일)</td><td class="hi">커널 없이 흐림→선명 학습</td><td>학습 분포 밖 흐림에 약함</td></tr>
          <tr><td>적대적 · 확산 사전지식</td><td class="hi">사실적인 세부를 되살림</td><td>없던 세부를 <em>지어낼</em> 수 있음</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 이 분야의 경계선이다. <a href="gan.html">적대적 학습</a>이나
      <a href="diffusion-models.html">확산 사전지식</a>을 쓰면 결과가 눈에 띄게 사실적이지만,
      모델은 <em>있을 법한</em> 세부를 <strong>지어내는</strong> 쪽으로 움직인다.
      번호판이나 얼굴처럼 <strong>증거로 쓰이는 이미지</strong>에서는 이 지어냄이 곧 위험이다.
    </p>
    <div class="note">
      <b>정리 — 디블러는 "무엇을 잃었는가"를 추론하는 문제다.</b>
      흐림은 정보를 <em>완만하게 섞고 일부 주파수는 아예 지운다.</em>
      지워진 것은 되돌릴 수 없으니, 복원은 언제나 <strong>남은 증거 + 자연스러움에 대한 가정</strong>으로
      빈자리를 메우는 일이다. 고전 방법은 그 가정을 수식(TV·희소 기울기)으로 적었고,
      학습 방법은 데이터에서 익힌다. 어느 쪽이든 결과는 <a href="image-quality-metrics.html">화질 지표</a>로
      재되, 지표가 높다고 <em>사실</em>인 것은 아니라는 점 — 강한 디블러일수록 생성에 가깝다는 사실을 알고 써야 한다.
    </div>
  </section>
"""

READING = [
    "Fergus et al., <em>Removing Camera Shake from a Single Photograph</em> (SIGGRAPH 2006) — 자연 이미지 기울기 사전지식으로 흔들림 커널을 추정.",
    "Levin et al., <em>Understanding and Evaluating Blind Deconvolution Algorithms</em> (CVPR 2009) — MAP<sub>x,k</sub> 가 무흐림 해를 고르는 함정과 그 해법.",
    "Krishnan &amp; Fergus, <em>Fast Image Deconvolution using Hyper-Laplacian Priors</em> (NeurIPS 2009) — 희소 기울기 사전지식의 빠른 비블라인드 복원.",
    "Nah et al., <em>Deep Multi-scale CNN for Dynamic Scene Deblurring</em> (arXiv:1612.02177) — GoPro 데이터셋과 멀티스케일 직접 회귀.",
    "Kupyn et al., <em>DeblurGAN: Blind Motion Deblurring Using Conditional Adversarial Networks</em> (arXiv:1711.07064) — 적대적 손실로 사실적 복원.",
    "Rim et al., <em>Real-World Blur Dataset for Learning and Benchmarking Deblurring Algorithms</em> (ECCV 2020) — RealBlur. 합성 흐림과 실제 흐림의 간극.",
]

write(
    "deblurring.html",
    title="디블러링 — 겹친 빛을 되돌리기",
    eyebrow="Vision · Image Restoration · 2006–2026",
    h1="디블러링",
    subtitle="겹친 빛을 되돌리기 — 흐림은 곱셈이 아니라 합성곱이다",
    dek=(
        "흔들린 사진에서 가로등이 여러 개로 번지는 것은 밝기가 <em>흐려진</em> 게 아니라 "
        "한 점의 빛이 궤적을 따라 <strong>겹친</strong> 것이다. 그래서 복원은 겹침을 되돌리는 "
        "디컨볼루션이 된다 — 그런데 그냥 나누면 노이즈가 폭발하고, 지워진 주파수는 되살아나지 않는다. "
        "무엇을 잃었는지 <em>추론</em>해야 하는 문제다."
    ),
    spec=[
        ("모델", "b = k ∗ x + n"),
        ("난점", "부정치 · 일부 주파수는 소실"),
        ("고전 원리", "위너 · 사전지식(TV·희소 기울기)"),
        ("블라인드", "커널·원본 번갈아 추정"),
        ("학습", "커널 없이 흐림→선명 회귀"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-20",
)

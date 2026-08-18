#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1f4", panel="#e5e7ee", ink="#15171f", **{
    "ink-soft": "#4d5262", "ink-faint": "#7b8090", "rule": "#d2d5de",
    "rule-strong": "#a9adba", "accent": "#3b4a7c", "accent-fill": "#dde2f0",
    "accent-line": "#5a6ca8", "muted": "#85868c", "muted-fill": "#e0e1e4", "warn": "#a34423",
})
DARK = dict(paper="#101117", panel="#171922", ink="#e7e9f0", **{
    "ink-soft": "#a3a8b8", "ink-faint": "#757a8a", "rule": "#22242e", "rule-strong": "#373a47",
    "accent": "#9aaee0", "accent-fill": "#1a1f33", "accent-line": "#6d7fb8",
    "muted": "#86888f", "muted-fill": "#1a1b20", "warn": "#e08a68",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>좌표를 맞추는 일과 상자를 맞추는 일은 다르다</h2>
    <p>
      검출기의 손실은 크게 둘이다. <em>이것이 무엇인가</em>(분류)와
      <em>어디에 있는가</em>(박스 회귀). 오래도록 뒤쪽은
      네 좌표에 <strong>L1 또는 smooth L1</strong> 을 걸어 풀었다.
      상자를 <code>(x₁, y₁, x₂, y₂)</code> 네 개의 숫자로 보고 각각을 정답에 가깝게 미는 방식이다.
    </p>
    <p>
      그런데 <strong>평가는 IoU 로 한다.</strong>
      <a href="detection-lineage.html">검출 계보</a>가 쓰는 AP 는
      IoU 가 임계를 넘는 예측만 정답으로 인정하고,
      <a href="nms.html">NMS</a> 도 IoU 로 중복을 지운다.
      <em>가르칠 때 쓰는 자와 채점할 때 쓰는 자가 다르다</em>는 뜻이다.
    </p>
    <p>
      이 어긋남은 말이 아니라 숫자로 드러난다.
      정사각형 정답 상자를 놓고 <strong>네 좌표를 전부 2px 씩 밀어</strong> 보자.
      L1 오차는 세 경우 모두 8px 로 같다.
    </p>
    <div class="eq">
      <span class="cap">같은 L1 오차 8px — 상자 크기만 다르다</span>
      <div class="line">변 <strong>10</strong>px 상자 &nbsp; IoU = <strong>0.4706</strong></div>
      <div class="line">변 <strong>40</strong>px 상자 &nbsp; IoU = <strong>0.8223</strong></div>
      <div class="line">변 <strong>160</strong>px 상자 &nbsp; IoU = <strong>0.9515</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 손실은 셋을 똑같이 취급하지만 채점은 0.47 과 0.95 로 갈린다</div>
    </div>
    <p>
      작은 물체에서 같은 픽셀 오차가 훨씬 비싸다. 그런데 L1 은 그것을 모른다.
      <strong>L1 은 척도에 의존하고 IoU 는 척도에 불변</strong>이라는,
      두 함수의 성질 차이가 그대로 남는 것이다.
    </p>
    <p>
      두 번째 어긋남은 <strong>네 좌표를 독립으로 본다</strong>는 점이다.
      UnitBox 가 2016년에 짚은 지점이 이것이다 —
      네 경계는 서로 상관된 값인데 ℓ₂ 손실은 각각을 따로 회귀한다.
      같은 크기의 오차라도 <em>방향의 조합</em>에 따라 결과가 달라진다.
    </p>
    <div class="eq">
      <span class="cap">10×10 정답 상자 · 오차의 조합에 따른 IoU</span>
      <div class="line">모두 +2 평행이동&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; L1 = 8px&nbsp;&nbsp; IoU = 0.4706</div>
      <div class="line">x₁ +2, x₂ −2 (가로 수축)&nbsp; L1 = 4px&nbsp;&nbsp; IoU = 0.6000</div>
      <div class="line">x₁ −2, x₂ +2 (가로 팽창)&nbsp; L1 = 4px&nbsp;&nbsp; IoU = <strong>0.7143</strong>&nbsp; ← L1 이 같은데 IoU 는 다르다</div>
    </div>
    <p>
      아래 두 줄은 L1 이 정확히 같다. 그런데 IoU 는 0.60 과 0.71 로 갈린다.
      같은 폭만큼 틀려도 <em>안으로 줄이는 것보다 밖으로 늘리는 쪽이 덜 손해</em>이기 때문이다.
      좌표를 하나씩 보는 손실은 이 구분을 표현할 수 없다.
    </p>
    <div class="note">
      <b>완화책은 있었다.</b> Faster R-CNN 계열은 좌표를 앵커 크기로 나누고
      폭·높이를 로그 공간에서 회귀해 척도 의존을 상당히 줄였다.
      <a href="yolov5.html">YOLOv5</a> 의 앵커 디코딩도 같은 계열의 처방이다.
      그래도 <strong>손실 함수와 평가 지표가 서로 다른 함수</strong>라는 사실 자체는 남는다.
      그렇다면 지표를 직접 최적화하면 되지 않는가 — 다음 절의 질문이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>IoU 를 그대로 손실로 쓰면 평지가 생긴다</h2>
    <p>
      가장 곧은 해법은 <strong>L<sub>IoU</sub> = 1 − IoU</strong> 다.
      UnitBox(2016)가 처음 제안했고, 이름 그대로 네 경계를 <em>하나의 단위</em>로 회귀한다.
    </p>
    <div class="eq">
      <span class="cap">IoU 손실이 공짜로 얻는 것</span>
      <div class="line">· <strong>척도 불변</strong> — 큰 물체와 작은 물체를 같은 잣대로 벌한다</div>
      <div class="line">· <strong>네 좌표 동시 최적화</strong> — 조합의 방향까지 값에 반영된다</div>
      <div class="line">· <strong>손실 = 지표</strong> — 낮추는 값이 곧 채점되는 값이다</div>
    </div>
    <p>
      그런데 여기에 <strong>구조적 결함</strong>이 하나 있다.
      두 상자가 겹치지 않으면 교집합이 0 이라 IoU 도 0 이고,
      <em>얼마나 떨어져 있든 값이 똑같이 0</em> 이다.
      손실은 1 로 고정되고 그래디언트는 사라진다.
    </p>
    <div class="eq">
      <span class="cap">10×10 정답 상자에서 예측을 0.5px 씩 당겨 보면</span>
      <div class="line">dx 12.0 → 11.5&nbsp;&nbsp; ΔIoU = <strong>+0.0000</strong>&nbsp;&nbsp;&nbsp; ΔGIoU = +0.0202</div>
      <div class="line">dx 11.0 → 10.5&nbsp;&nbsp; ΔIoU = <strong>+0.0000</strong>&nbsp;&nbsp;&nbsp; ΔGIoU = +0.0221</div>
      <div class="line">dx 10.0 →&nbsp; 9.5&nbsp;&nbsp; ΔIoU = <strong>+0.0000</strong>&nbsp;&nbsp;&nbsp; ΔGIoU = +0.0244</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 가까워지고 있는데 IoU 는 아무 말도 하지 않는다</div>
    </div>
    <p>
      이것이 사소한 구석이 아닌 이유는 <strong>학습 초기</strong>에 있다.
      앵커든 <a href="detr-lineage.html">DETR</a> 의 쿼리든, 처음에는 대부분이 정답과 전혀 겹치지 않는다.
      작은 물체일수록 그 상태가 오래 간다.
      배워야 할 대부분의 표본에서 신호가 0 이면 학습이 시작되지 않는다.
    </p>
    <p>
      그래서 실무는 오랫동안 <strong>L1 + IoU 계열의 합</strong>으로 갔다.
      L1 이 초기의 먼 거리를 좁히고, IoU 항이 마지막 정렬을 맡는 분업이다.
      다만 이건 우회일 뿐 <em>겹침이 0 인 구간을 IoU 자체가 설명하게 만드는</em> 해법은 아니다.
      그 해법이 GIoU 다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>GIoU — 최소 포위 상자로 거리를 만든다</h2>
    <p>
      발상은 한 줄이다. 두 상자를 <strong>모두 감싸는 가장 작은 상자 C</strong> 를 그리고,
      그 안에서 <em>아무것도 아닌 빈 영역</em>이 차지하는 비율만큼 벌을 준다.
    </p>
    <div class="eq">
      <span class="cap">GIoU (Rezatofighi et al., CVPR 2019)</span>
      <div class="line">C = A 와 B 를 모두 포함하는 최소 축정렬 상자</div>
      <div class="line">&nbsp;</div>
      <div class="line"><strong>GIoU = IoU − |C ∖ (A ∪ B)| / |C|</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">범위 &nbsp;−1 &lt; GIoU ≤ 1&nbsp;&nbsp;&nbsp; 손실 &nbsp;0 ≤ 1 − GIoU &lt; 2</div>
    </div>
    <p>
      멀어질수록 C 가 커지고 빈 영역의 비율이 1 에 가까워진다.
      겹치지 않는 구간에서도 <strong>값이 계속 움직인다</strong>는 것이 핵심이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 210" role="img" aria-label="겹치지 않는 세 배치에서 IoU는 모두 0으로 같지만 GIoU는 거리에 따라 마이너스 0.09, 마이너스 0.33, 마이너스 0.60으로 달라진다. 점선은 두 상자를 모두 감싸는 최소 포위 상자 C이며, C 안의 빈 영역이 커질수록 벌점이 커진다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="16" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">겹치지 않는 세 배치 — IoU 는 셋 다 0.000</text>

            <rect x="24" y="26" width="208" height="120" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <rect x="38" y="72" width="32" height="32" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="2"/>
            <rect x="76" y="72" width="32" height="32" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <rect x="38" y="72" width="70" height="32" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="2 3"/>
            <text x="38" y="66" font-size="8" fill="var(--ink-faint)">C</text>
            <text x="38" y="124" font-size="8.5" fill="var(--ink-soft)">간격 2 (dx=12)</text>
            <text x="38" y="138" font-size="9" fill="var(--accent)">GIoU = −0.0909</text>

            <rect x="246" y="26" width="208" height="120" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <rect x="260" y="72" width="32" height="32" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="2"/>
            <rect x="324" y="72" width="32" height="32" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <rect x="260" y="72" width="96" height="32" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="2 3"/>
            <text x="260" y="66" font-size="8" fill="var(--ink-faint)">C</text>
            <text x="260" y="124" font-size="8.5" fill="var(--ink-soft)">간격 10 (dx=20)</text>
            <text x="260" y="138" font-size="9" fill="var(--accent)">GIoU = −0.3333</text>

            <rect x="468" y="26" width="208" height="120" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <rect x="482" y="72" width="32" height="32" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="2"/>
            <rect x="610" y="72" width="32" height="32" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <rect x="482" y="72" width="160" height="32" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="2 3"/>
            <text x="482" y="66" font-size="8" fill="var(--ink-faint)">C</text>
            <text x="482" y="124" font-size="8.5" fill="var(--ink-soft)">간격 30 (dx=40)</text>
            <text x="482" y="138" font-size="9" fill="var(--accent)">GIoU = −0.6000</text>

            <line x1="24" y1="164" x2="676" y2="164" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="184" font-size="8.5" fill="var(--ink-soft)">채워진 상자 = 정답 · 점선 상자 = 예측 · 얇은 점선 = 최소 포위 상자 C</text>
            <text x="24" y="200" font-size="8.5" fill="var(--warn)">멀어질수록 −1 에 점근한다 — dx 1000 에서 −0.9802, dx 100000 에서 −0.9998</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        IoU 가 평지인 구간에 기울기를 만드는 방법은 <em>바깥</em>을 재는 것이다.
        다만 벌점의 분모가 C 이므로 값이 −1 을 넘지 못한다.
        아주 멀리 있는 상자끼리는 다시 기울기가 완만해진다.
      </figcaption>
    </figure>

    <p>
      GIoU 는 <a href="detr-lineage.html">DETR</a> 이 채택하면서 사실상 표준이 됐다.
      DETR 의 박스 손실은 L1 과 GIoU 를 <strong>5 : 2</strong> 로 섞는다.
      정규화 좌표에서 두 항의 크기를 재 보면 역할 분담이 보인다.
    </p>
    <div class="eq">
      <span class="cap">정규화 cxcywh · 0.2 크기 상자를 cx 방향으로 이동</span>
      <div class="line">이동 0.01&nbsp;&nbsp; 5·L1 = 0.050&nbsp;&nbsp; 2·(1−GIoU) = <strong>0.190</strong>&nbsp;&nbsp; 합 0.240</div>
      <div class="line">이동 0.10&nbsp;&nbsp; 5·L1 = 0.500&nbsp;&nbsp; 2·(1−GIoU) = <strong>1.333</strong>&nbsp;&nbsp; 합 1.833</div>
      <div class="line">이동 0.30&nbsp;&nbsp; 5·L1 = <strong>1.500</strong>&nbsp;&nbsp; 2·(1−GIoU) = 2.400&nbsp;&nbsp; 합 3.900</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 가까울수록 GIoU 항이 지배하고, 멀어질수록 L1 항의 비중이 커진다</div>
    </div>
    <p>
      가중치가 5 대 2 인데도 <em>작은 오차 영역에서는 GIoU 항이 네 배 가까이 크다.</em>
      L1 은 거리에 비례해 선형으로만 자라는 반면
      GIoU 손실은 조금만 어긋나도 빠르게 커지기 때문이다.
      두 항을 함께 두는 이유가 여기서 드러난다 — <strong>정밀한 정렬은 GIoU 가, 먼 거리의 견인은 L1 이</strong> 맡는다.
    </p>
    <p>
      그런데 GIoU 에는 <strong>값이 죽는 자리</strong>가 있다.
      한 상자가 다른 상자를 완전히 포함하면 C 가 큰 상자와 같아지고,
      C 안의 빈 영역이 정확히 합집합 바깥과 일치해 벌점 항이 0 이 된다.
      즉 <strong>포함 관계에서는 GIoU 가 IoU 와 완전히 같아진다.</strong>
    </p>
    <div class="eq">
      <span class="cap">10×10 정답 상자 안에 들어간 예측들</span>
      <div class="line">예측 (2, 2, 8, 8)&nbsp;&nbsp;&nbsp;&nbsp; IoU = 0.3600&nbsp;&nbsp; GIoU = <strong>0.3600</strong>&nbsp;&nbsp; 중심 거리 0.000</div>
      <div class="line">예측 (0, 0, 6, 6)&nbsp;&nbsp;&nbsp;&nbsp; IoU = 0.3600&nbsp;&nbsp; GIoU = <strong>0.3600</strong>&nbsp;&nbsp; 중심 거리 2.828</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 하나는 중심이 맞고 하나는 구석에 몰렸는데 두 값이 구분하지 못한다</div>
    </div>
    <p>
      6×6 상자를 정답 한가운데 놓든 왼쪽 위 구석에 붙이든 IoU 도 GIoU 도 0.36 이다.
      그러나 <em>다음 걸음으로 어디를 고쳐야 하는지</em>는 두 경우가 전혀 다르다.
      손실이 그 차이를 담지 못하면 모델은 그 방향을 배울 수 없다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>DIoU·CIoU — 중심과 모양을 따로 잰다</h2>
    <p>
      DIoU 는 벌점을 <strong>면적이 아니라 중심점 거리</strong>로 바꾼다.
      두 중심 사이의 거리를 최소 포위 상자의 대각선으로 정규화한 값이다.
    </p>
    <div class="eq">
      <span class="cap">DIoU · CIoU (Zheng et al., AAAI 2020)</span>
      <div class="line"><strong>DIoU = IoU − ρ²(b, b<sup>gt</sup>) / c²</strong></div>
      <div class="line">&nbsp;&nbsp;&nbsp;ρ = 두 중심 사이의 거리 &nbsp;·&nbsp; c = 최소 포위 상자의 대각선 길이</div>
      <div class="line">&nbsp;</div>
      <div class="line"><strong>CIoU = DIoU − α·v</strong></div>
      <div class="line">&nbsp;&nbsp;&nbsp;v = (4/π²) · ( arctan(w<sup>gt</sup>/h<sup>gt</sup>) − arctan(w/h) )²</div>
      <div class="line">&nbsp;&nbsp;&nbsp;α = v / ( (1 − IoU) + v )</div>
    </div>
    <p>
      앞 절의 예에 DIoU 를 대면 곧바로 갈라진다.
      중심이 맞은 쪽은 0.3600, 구석에 몰린 쪽은 <strong>0.3200</strong> 이다.
      벌점이 겹침의 <em>바깥</em>이 아니라 <em>어긋난 방향</em>을 재기 때문에
      포함 관계에서도 값이 죽지 않는다.
    </p>
    <p>
      더 흥미로운 것은 GIoU 와 DIoU 가 <strong>서로 반대로 순위를 매기는</strong> 배치가 있다는 점이다.
      같은 10×10 상자를 <em>가로로만</em> 밀어 IoU 를 1/3 로 맞춘 경우와,
      <em>대각선으로</em> 밀어 같은 IoU 를 만든 경우를 비교하면 그렇다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="IoU가 똑같이 0.3333인 두 배치 비교. 가로로만 민 경우는 GIoU 0.3333 DIoU 0.2564이고 중심 거리가 5.0, 대각선으로 민 경우는 GIoU 0.2307 DIoU 0.2820이고 중심 거리가 4.142다. GIoU는 가로 이동을, DIoU는 대각선 이동을 더 좋게 평가해 두 지표의 순위가 뒤집힌다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="16" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">IoU 는 둘 다 0.3333 — 그런데 순위가 뒤집힌다</text>

            <rect x="24" y="26" width="320" height="150" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <rect x="60" y="56" width="60" height="60" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="2"/>
            <rect x="90" y="56" width="60" height="60" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <rect x="60" y="56" width="90" height="60" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="2 3"/>
            <circle cx="90" cy="86" r="2.5" fill="var(--accent-line)"/>
            <circle cx="120" cy="86" r="2.5" fill="var(--ink-faint)"/>
            <line x1="90" y1="86" x2="120" y2="86" stroke="var(--warn)" stroke-width="1.4"/>
            <text x="60" y="140" font-size="9" fill="var(--ink-soft)">가로로만 이동 · 중심 거리 5.000</text>
            <text x="60" y="156" font-size="9" fill="var(--accent)">GIoU 0.3333 (높다) · DIoU 0.2564 (낮다)</text>
            <text x="176" y="86" font-size="8" fill="var(--warn)">ρ</text>

            <rect x="356" y="26" width="320" height="150" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <rect x="392" y="46" width="60" height="60" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="2"/>
            <rect x="410" y="64" width="60" height="60" fill="none" stroke="var(--ink-faint)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <rect x="392" y="46" width="78" height="78" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="2 3"/>
            <circle cx="422" cy="76" r="2.5" fill="var(--accent-line)"/>
            <circle cx="440" cy="94" r="2.5" fill="var(--ink-faint)"/>
            <line x1="422" y1="76" x2="440" y2="94" stroke="var(--warn)" stroke-width="1.4"/>
            <text x="392" y="140" font-size="9" fill="var(--ink-soft)">대각선으로 이동 · 중심 거리 4.142</text>
            <text x="392" y="156" font-size="9" fill="var(--accent)">GIoU 0.2307 (낮다) · DIoU 0.2820 (높다)</text>
            <text x="446" y="86" font-size="8" fill="var(--warn)">ρ</text>

            <line x1="24" y1="192" x2="676" y2="192" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="212" font-size="8.5" fill="var(--ink-soft)">GIoU 는 포위 상자의 빈 영역을 본다 — 대각선 이동은 C 를 양쪽으로 키우므로 더 나쁘게 친다.</text>
            <text x="24" y="226" font-size="8.5" fill="var(--ink-soft)">DIoU 는 중심 거리를 본다 — 대각선 이동은 중심이 더 가까우므로 더 좋게 친다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 2</span>
        같은 IoU 에서 두 손실이 정반대의 방향을 가리킨다.
        어느 쪽이 옳다기보다 <strong>무엇을 어긋남으로 정의했는가</strong>가 다를 뿐이다.
        손실 함수의 선택은 곧 <em>어떤 오차를 더 미워할지</em>의 선택이다.
      </figcaption>
    </figure>

    <p>
      CIoU 는 여기에 <strong>종횡비 항 v</strong> 를 더한다.
      겹침과 중심이 같아도 상자의 <em>모양</em>이 틀릴 수 있기 때문이다.
      정답이 10×10 인데 예측이 중심을 맞춘 채 20×5 라면 DIoU 는 IoU 와 같은 값만 내놓는다 —
      중심 거리가 0 이라 벌점 항이 사라진다.
    </p>
    <div class="eq">
      <span class="cap">10×10 정답 · 중심을 맞춘 채 모양만 바꾼 예측</span>
      <div class="line">예측 10×10&nbsp;&nbsp;&nbsp;&nbsp; IoU 1.0000&nbsp;&nbsp; v 0.0000&nbsp;&nbsp; α 0.0000&nbsp;&nbsp; CIoU 1.0000</div>
      <div class="line">예측 12.5×8&nbsp;&nbsp;&nbsp; IoU 0.6667&nbsp;&nbsp; v 0.0189&nbsp;&nbsp; α 0.0537&nbsp;&nbsp; CIoU 0.6657</div>
      <div class="line">예측 20×5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; IoU 0.3333&nbsp;&nbsp; v 0.1184&nbsp;&nbsp; α 0.1508&nbsp;&nbsp; CIoU <strong>0.3155</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// DIoU 는 세 줄 모두 IoU 와 같은 값이다 — 중심이 맞아 벌점이 0 이다</div>
    </div>
    <p>
      α 는 <strong>순서를 정하는 스위치</strong>다. v 를 0.05 로 고정하고 IoU 만 바꿔 보면
      IoU 0.9 에서 α = 0.3333, IoU 0.3 에서 α = 0.0667,
      전혀 겹치지 않을 때 α = 0.0476 까지 내려간다.
      <em>겹침이 나쁠수록 종횡비 벌점을 눌러 둔다</em>는 설계다.
      먼저 상자를 데려다 놓고, 자리를 잡은 뒤에 모양을 다듬는다.
    </p>
    <div class="note">
      <b>같은 발상이 후처리에도 들어갔다.</b> DIoU 논문은 손실과 함께
      <a href="nms.html">DIoU-NMS</a> 를 내놨다. 많이 겹쳐도 <em>중심이 멀면</em>
      서로 다른 물체일 가능성이 높다는 판단이다.
      가림이 심한 장면 — <a href="person-reid.html">재식별</a>이나
      <a href="object-tracking.html">다중 객체 추적</a>이 다루는 조건 — 에서 특히 그렇다.
      학습 손실과 추론 규칙이 <strong>같은 기하를 공유</strong>하게 된 셈이다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>v 가 못 하는 일, 그리고 그다음</h2>
    <p>
      CIoU 의 종횡비 항은 널리 쓰였지만 곧 약점이 지적됐다.
      직접 편미분해 보면 그 정체가 드러난다.
      정답 10×10, 예측 20×5 에서 수치 미분한 값이다.
    </p>
    <div class="eq">
      <span class="cap">v 의 편미분 — w = 20, h = 5, v = 0.118365</span>
      <div class="line">∂v/∂w = <strong>+0.005154</strong></div>
      <div class="line">∂v/∂h = <strong>−0.020614</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">w·(∂v/∂w) + h·(∂v/∂h) = 20(0.005154) + 5(−0.020614) = <strong>0</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 항등식이다 — v 는 w 와 h 의 <strong>비율</strong>만 보고 크기는 보지 않는다</div>
    </div>
    <p>
      두 결론이 따라 나온다.
      첫째, <strong>두 편미분의 부호가 반대</strong>다.
      v 항만 놓고 보면 폭을 줄이면서 높이를 늘리는 방향으로만 민다.
      둘째이자 더 중요한 것은, 위 항등식이 말하듯
      <strong>v 는 크기를 함께 키우거나 줄이는 방향에 완전히 무감각</strong>하다는 점이다.
      실제로 예측이 정사각형이기만 하면 2×2 든 20×20 이든 v = 0 이다.
    </p>
    <p>
      즉 <em>모양은 맞는데 크기가 틀린</em> 상황에서 v 는 아무 신호도 주지 않는다.
      크기를 고치는 일은 전부 IoU·DIoU 항의 몫으로 남는다.
      이 지점을 정면으로 고친 것이 EIoU 다 —
      비율 대신 <strong>변의 길이를 직접</strong> 재고,
      겹침·중심점·변 길이 <em>세 요소</em>를 각각의 항으로 분리한다.
      더불어 겹침이 작은 앵커가 손실을 지배하는 불균형을 Focal 가중으로 눌렀다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>손실</th><th>추가로 재는 것</th><th>해결한 문제</th><th>남은 문제</th></tr>
        </thead>
        <tbody>
          <tr><td>IoU (2016)</td><td>겹침</td><td>척도 불변 · 네 좌표 동시</td><td class="hi">겹치지 않으면 기울기 0</td></tr>
          <tr><td>GIoU (2019)</td><td>최소 포위 상자의 빈 영역</td><td>비겹침 구간의 기울기</td><td class="hi">포함 관계에서 IoU 로 퇴화</td></tr>
          <tr><td>DIoU (2020)</td><td>중심점 거리</td><td>포함 관계 · 수렴 속도</td><td>모양을 보지 않음</td></tr>
          <tr><td>CIoU (2020)</td><td>+ 종횡비 v</td><td>모양 어긋남</td><td class="hi">v 가 크기에 무감각</td></tr>
          <tr><td>EIoU (2021)</td><td>변 길이를 직접</td><td>v 의 무감각 · 표본 불균형</td><td>항이 늘어 조율할 것이 는다</td></tr>
          <tr><td>SIoU (2022)</td><td>+ 어긋난 <strong>각도</strong></td><td>이동 경로가 축을 따라 꺾이는 것</td><td>이득이 조건에 민감</td></tr>
          <tr><td>α-IoU (2021)</td><td>거듭제곱 재가중</td><td>정밀도 수준을 α 로 조절</td><td>α 를 데이터마다 정해야</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      SIoU 는 다른 각도에서 들어왔다. 앞의 손실들이 <em>얼마나 멀리</em> 는 재지만
      <em>어느 방향으로</em> 는 재지 않는다는 지적이다.
      각도 항을 넣어 예측이 축을 따라 먼저 정렬한 뒤 다가가게 만들었다.
      α-IoU 는 아예 기하를 건드리지 않고,
      기존 손실의 각 항을 <strong>거듭제곱</strong>으로 재가중해
      하나의 α 로 정밀도 수준을 조절할 수 있게 했다.
    </p>
    <div class="note">
      <b>사실 확인에서 걸러낸 것.</b> 흔히 <em>"GIoU 는 상자를 먼저 키우려 들고 DIoU 는 그러지 않는다"</em>
      고 정리되지만, 직접 계산해 보니 그렇게 깔끔하지 않다.
      정답 (0,0,10,10) 에 예측 (40,0,50,10) 을 놓고 1px 예산을 쓸 때
      GIoU 는 왼쪽 이동에 +0.0082, 폭 확장에 <strong>+0.0200</strong> 을 준다 — 확장을 선호한다.
      그런데 <strong>DIoU 도 같은 방향</strong>이다 (이동 +0.0072, 확장 +0.0153).
      DIoU 의 이점은 이 한 걸음에서 확장 선호가 사라지는 데 있는 것이 아니라,
      겹치기 시작한 뒤에도 중심 거리 항이 <em>계속 당긴다</em>는 데 있다.
      GIoU 의 벌점은 그 시점에 0 으로 죽는다.
    </div>
    <p>
      그래서 실무에서 무엇을 고를 것인가. 정직하게 말하면
      <strong>이 계열의 최종 AP 차이는 기하의 명료함에 비해 작고 조건에 민감하다.</strong>
      백본·라벨 할당·증강이 바뀌면 순위가 뒤집혔다는 보고가 흔하다.
      <a href="yolox.html">YOLOX</a> 가 보여준 것처럼
      검출 성능을 실제로 가르는 축은 손실의 세부보다
      <a href="yolov5.html">라벨 할당</a> 쪽인 경우가 많다.
    </p>
    <p>
      최근 흐름은 손실을 하나 더 고르는 대신 <strong>좌표의 표현 자체를 바꾸는</strong> 쪽이다.
      YOLOv8 계열의 박스 손실은 CIoU 를 유지하면서
      <em>분포 초점 손실</em>(DFL)을 함께 쓴다.
      좌표를 하나의 값으로 회귀하지 않고 기본 16개 구간의 <strong>확률 분포</strong>로 예측한 뒤
      기댓값을 취하는 방식이다.
      경계가 모호한 물체 — 가려졌거나 그림자에 잠긴 — 에서
      <em>모호함 자체를 표현할 수 있다</em>는 것이 이점이다.
      <a href="calibration.html">캘리브레이션</a>이 분류 점수에서 다루는 문제를
      좌표에서 다시 만나는 셈이다.
    </p>
    <p>
      정리하면 IoU 손실의 역사는 <strong>지표와 손실 사이의 간격을 좁혀 온 기록</strong>이다.
      L1 은 지표와 무관한 함수였고, IoU 손실은 지표 그 자체였지만 미분이 죽었고,
      GIoU 이후의 변형들은 <em>죽은 구간을 기하로 메우는</em> 작업이었다.
      <a href="nms.html">NMS</a> 가 후처리를 학습으로 흡수해 온 이야기와 같은 방향이다 —
      <a href="detection-lineage.html">검출 계보</a> 전체를 관통하는
      <strong>"손으로 정하던 것을 하나씩 학습으로"</strong> 의 또 다른 장면이다.
    </p>
  </section>
"""

READING = [
    "Yu et al., <em>UnitBox: An Advanced Object Detection Network</em> (arXiv:1608.01471) — 네 경계를 하나의 단위로 회귀한 최초의 IoU 손실.",
    "Rezatofighi et al., <em>Generalized Intersection over Union: A Metric and A Loss for Bounding Box Regression</em> (arXiv:1902.09630) — 최소 포위 상자로 평지를 없앤다.",
    "Zheng et al., <em>Distance-IoU Loss: Faster and Better Learning for Bounding Box Regression</em> (arXiv:1911.08287) — DIoU·CIoU 와 DIoU-NMS.",
    "Zhang et al., <em>Focal and Efficient IOU Loss for Accurate Bounding Box Regression</em> (arXiv:2101.08158) — 종횡비 대신 변 길이를 직접 재고 표본 불균형을 다룬다.",
    "Gevorgyan, <em>SIoU Loss: More Powerful Learning for Bounding Box Regression</em> (arXiv:2205.12740) — 어긋난 방향(각도)을 손실에 넣는다.",
    "He et al., <em>Alpha-IoU: A Family of Power Intersection over Union Losses for Bounding Box Regression</em> (arXiv:2110.13675) — 거듭제곱 하나로 정밀도 수준을 조절한다.",
]

write(
    "iou-losses.html",
    title="IoU 계열 손실 — 상자를 겹침으로 배우기",
    eyebrow="Vision · Box Regression · 2016–2026",
    h1="IoU 계열 손실",
    subtitle="상자를 좌표가 아니라 겹침으로 배우기 — L1 에서 GIoU·DIoU·CIoU 까지",
    dek=(
        "검출기는 IoU 로 채점되는데 오래도록 L1 으로 학습됐다. "
        "가르치는 자와 채점하는 자가 다르다는 뜻이다. "
        "IoU 를 그대로 손실로 쓰면 되지 않을까 — 그러면 "
        "<strong>겹치지 않는 구간에서 기울기가 통째로 사라진다.</strong> "
        "그 평지를 기하로 메워 온 십 년의 기록이다."
    ),
    spec=[
        ("고치려는 것", "손실 ≠ 평가 지표"),
        ("IoU 손실의 결함", "비겹침 구간 기울기 0"),
        ("GIoU", "포위 상자의 빈 영역"),
        ("DIoU · CIoU", "중심 거리 · 종횡비"),
        ("현재", "CIoU + 분포 회귀(DFL)"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-18",
)

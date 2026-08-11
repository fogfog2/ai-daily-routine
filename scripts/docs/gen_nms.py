#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ee", panel="#e7e6e2", ink="#181713", **{
    "ink-soft": "#54504a", "ink-faint": "#837e76", "rule": "#d3d1cc",
    "rule-strong": "#afaca5", "accent": "#8a5a14", "accent-fill": "#f2e6cd",
    "accent-line": "#b0802e", "muted": "#82868c", "muted-fill": "#dee0e2", "warn": "#9c3f22",
})
DARK = dict(paper="#121110", panel="#1a1916", ink="#eae8e3", **{
    "ink-soft": "#aaa69c", "ink-faint": "#7c776d", "rule": "#25231e", "rule-strong": "#3b3830",
    "accent": "#e0ad5c", "accent-fill": "#2e2412", "accent-line": "#a87f36",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>하나의 물체에 상자가 여럿 나온다</h2>
    <p>
      검출기는 이미지 전체에 후보를 뿌린다. <a href="yolov5.html">YOLOv5</a>는
      640 입력에서 <strong>25,200개</strong>를 내놓는다. 실제 물체는 몇 개뿐인데도 그렇다.
    </p>
    <p>
      문제는 개수가 아니라 <strong>같은 물체에 여러 후보가 걸린다</strong>는 것이다.
      물체 중심 근처의 격자 칸들이 저마다 "여기 사람이 있다"고 답하고,
      <a href="yolov5.html">이웃 칸까지 양성으로 삼는 라벨 할당</a> 때문에 이 현상은 오히려 의도된 것이다.
      학습에서는 양성 표본이 많아야 잘 배우기 때문이다.
    </p>
    <p>
      그런데 <em>출력</em>은 물체 하나에 상자 하나여야 한다.
      학습에 좋은 것과 출력에 필요한 것이 어긋나므로,
      <strong>추론 단계에서 정리하는 절차</strong>가 따로 필요해진다. 그것이 NMS 다.
    </p>
    <div class="note">
      <b>이 어긋남이 이 문서의 전부다.</b> NMS 는 모델이 배운 것이 아니라
      <em>사람이 만든 후처리 규칙</em>이다. 검출기 계보가 앵커·라벨 할당을 하나씩
      학습으로 흡수해 온 과정에서, NMS 는 <strong>가장 오래 남은 수작업</strong>이었다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>절차 — 점수순으로 훑으며 겹치면 지운다</h2>
    <p>
      알고리즘 자체는 몇 줄이다. 점수가 높은 것을 남기고, 그것과 많이 겹치는 것을 버린다.
    </p>
    <div class="eq">
      <span class="cap">Greedy NMS</span>
      <div class="line">1) 점수 내림차순 정렬</div>
      <div class="line">2) 가장 높은 것 <strong>M</strong> 을 결과에 넣고 목록에서 뺀다</div>
      <div class="line">3) 남은 각 상자 b 에 대해</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;IoU(M, b) &gt; N<sub>t</sub> 이면 <strong>b 를 버린다</strong></div>
      <div class="line">4) 목록이 빌 때까지 2~3 반복</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 클래스별로 따로 수행한다 — 사람과 자전거가 겹치는 것은 정상이다</div>
    </div>
    <p>
      겹침의 척도는 <strong>IoU</strong>(교집합 ÷ 합집합)다. 0에서 1 사이 값이고,
      크기가 다른 상자에도 공정하게 작동한다.
    </p>
    <div class="eq">
      <span class="cap">IoU 감각 잡기 — 10×10 상자 기준</span>
      <div class="line">완전히 같음&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; IoU = 1.000</div>
      <div class="line">가로로 절반 어긋남&nbsp;&nbsp; IoU = <strong>0.333</strong>&nbsp;&nbsp;← 절반 겹쳐도 1/3 이다</div>
      <div class="line">가장자리만 닿음&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; IoU = 0.053</div>
    </div>
    <p>
      두 번째 줄이 직관과 어긋나는 지점이다. <em>"절반 겹쳤으니 0.5"</em>가 아니다.
      합집합이 커지므로 값이 빠르게 떨어진다.
      그래서 흔히 쓰는 임계값 <code>0.45~0.5</code>는 생각보다 <strong>많이 겹쳐야</strong> 지운다는 뜻이다.
    </p>
    <p>
      비용도 짚어 두자. 정렬이 <code>O(N log N)</code>, 비교가 최악 <code>O(N²)</code>다.
      다만 실제로는 점수 임계값으로 미리 걸러 <em>수백 개</em>만 남기므로 감당 가능하다.
      25,200개를 그대로 돌리면 최악 3억 회 비교가 되어 현실적이지 않다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>가려진 물체를 지워버린다</h2>
    <p>
      NMS 의 고질적 실패는 <strong>진짜 물체 둘이 실제로 겹쳐 있을 때</strong> 나온다.
      군중 속 사람, 주차장의 차량처럼 <em>가림</em>이 있는 장면이다.
    </p>
    <p>
      앞사람과 뒷사람의 상자가 IoU 0.6으로 겹쳤다고 하자.
      임계값이 0.5라면 NMS 는 뒷사람을 <strong>중복이라고 판단해 지운다</strong>.
      모델은 정확히 찾아냈는데 후처리가 버리는 것이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="NMS의 동작과 실패. 같은 물체에 걸린 중복 상자는 잘 제거하지만, 실제로 겹쳐 있는 두 사람의 경우 뒷사람 상자를 중복으로 오인해 지워버린다. Soft-NMS는 지우는 대신 점수를 깎아 이 문제를 완화한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="nm-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">잘 되는 경우 — 같은 물체의 중복</text>

            <rect x="24" y="32" width="170" height="104" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <ellipse cx="104" cy="86" rx="26" ry="36" fill="var(--ink-soft)" opacity="0.25"/>
            <rect x="72" y="46" width="66" height="80" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <text x="140" y="54" font-size="8" fill="var(--accent)">.92</text>
            <rect x="66" y="52" width="66" height="80" fill="none" stroke="var(--rule-strong)" stroke-width="1.2" stroke-dasharray="3 2"/>
            <text x="36" y="140" font-size="7.5" fill="var(--ink-faint)">.71</text>
            <rect x="78" y="42" width="66" height="80" fill="none" stroke="var(--rule-strong)" stroke-width="1.2" stroke-dasharray="3 2"/>
            <text x="150" y="140" font-size="7.5" fill="var(--ink-faint)">.65</text>

            <path d="M202 84 L228 84" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#nm-a)"/>
            <text x="215" y="76" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">NMS</text>

            <rect x="236" y="32" width="120" height="104" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <ellipse cx="296" cy="86" rx="26" ry="36" fill="var(--ink-soft)" opacity="0.25"/>
            <rect x="264" y="46" width="66" height="80" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <text x="24" y="156" font-size="8.5" fill="var(--accent)">✓ 중복 둘을 지우고 하나만 남긴다</text>

            <line x1="24" y1="172" x2="674" y2="172" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="192" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">실패하는 경우 — 진짜 둘이 겹침</text>

            <rect x="24" y="200" width="150" height="34" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <ellipse cx="72" cy="217" rx="20" ry="14" fill="var(--ink-soft)" opacity="0.3"/>
            <ellipse cx="112" cy="217" rx="20" ry="14" fill="var(--ink-soft)" opacity="0.45"/>
            <rect x="50" y="204" width="46" height="26" fill="none" stroke="var(--accent-line)" stroke-width="1.8"/>
            <rect x="90" y="204" width="46" height="26" fill="none" stroke="var(--warn)" stroke-width="1.8" stroke-dasharray="3 2"/>
            <text x="182" y="212" font-size="8" fill="var(--ink-faint)">IoU 0.6 &gt; 임계 0.5</text>
            <text x="182" y="226" font-size="8" fill="var(--warn)">→ 뒷사람을 지운다 ✗</text>

            <line x1="378" y1="180" x2="378" y2="234" stroke="var(--rule)" stroke-width="1"/>

            <text x="400" y="192" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">Soft-NMS — 지우지 않고 깎는다</text>
            <text x="400" y="212" font-size="8.5" fill="var(--ink-soft)">s ← s · exp( −IoU² / σ )</text>
            <text x="400" y="228" font-size="8.5" fill="var(--ink-faint)">점수가 낮아진 채 살아남아, 최종 임계값이 판단한다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        같은 문제를 두 방향에서 볼 수 있다.
        임계값을 올리면 가려진 물체를 살리지만 중복이 남고,
        내리면 중복은 지우지만 가려진 물체를 잃는다.
        <strong>하나의 숫자로 두 요구를 동시에 만족시킬 수 없다.</strong>
      </figcaption>
    </figure>

    <p>
      <strong>Soft-NMS</strong> 는 이 딜레마를 우회한다 — <em>지우는 대신 점수를 깎는다.</em>
      많이 겹칠수록 많이 깎되 0으로 만들지는 않는다.
      가려진 물체는 점수가 낮아진 채 살아남고, 최종 점수 임계값이 판단하게 둔다.
      학습을 다시 할 필요 없이 추론 코드만 바꾸면 되므로 채택이 쉬웠다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>변형들 — 무엇을 기준으로 지울 것인가</h2>
    <p>
      NMS 계열의 변형은 대부분 <strong>"무엇을 겹침으로 볼 것인가"</strong>를 손본 것이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방식</th><th>바꾼 지점</th><th>노리는 것</th></tr>
        </thead>
        <tbody>
          <tr><td>Greedy NMS</td><td>IoU &gt; 임계 → 삭제</td><td>기본</td></tr>
          <tr><td>Soft-NMS</td><td class="hi">삭제 대신 점수 감쇠</td><td>가림 상황</td></tr>
          <tr><td>DIoU-NMS</td><td class="hi">중심점 거리를 함께 본다</td><td>겹쳐도 중심이 멀면 남긴다</td></tr>
          <tr><td>Cluster/Matrix NMS</td><td>병렬 계산으로 재구성</td><td>속도</td></tr>
          <tr><td>Weighted NMS</td><td>주변 상자를 가중 평균</td><td>좌표 정밀도</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>DIoU-NMS</strong> 의 발상이 특히 명료하다. 두 상자가 많이 겹치더라도
      <em>중심이 멀리 떨어져 있다면</em> 서로 다른 물체일 가능성이 높다.
      IoU 만 보면 놓치는 신호를 중심 거리로 보완한다.
    </p>
    <div class="note">
      <b>NMS 는 미분 가능하지 않다.</b> 정렬과 삭제는 이산 연산이라
      역전파가 지나갈 수 없다. 그래서 <strong>학습과 추론이 어긋난다</strong> —
      모델은 NMS 가 있다는 것을 모른 채 학습되고, 추론에서만 그 규칙이 적용된다.
      이 어긋남이 성능 상한을 만든다는 지적이 오래 있었고,
      다음 절의 흐름으로 이어진다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>없애는 방향 — 중복 억제를 학습으로</h2>
    <p>
      가장 큰 전환은 <a href="detr-lineage.html">DETR</a>이었다.
      <strong>헝가리안 매칭</strong>으로 예측과 정답을 일대일로 짝지어 학습하면,
      모델이 <em>스스로 중복을 내지 않는 법</em>을 배운다. NMS 가 필요 없어진다.
    </p>
    <p>
      일대일 매칭이 핵심이다. 정답 하나에 예측 하나만 배정되므로,
      같은 물체에 두 예측이 높은 점수를 주면 둘 다 벌을 받는다.
      <em>중복 억제가 손실 함수 안으로 들어온 것</em>이다.
    </p>
    <p>
      다만 대가가 있었다. 일대일 매칭은 <strong>양성 표본이 극도로 적어</strong> 수렴이 느리다.
      DETR 이 500 에폭을 요구했던 이유가 여기 있고,
      이후 연구들이 이 지점을 개선하는 데 몇 년을 썼다.
    </p>
    <p>
      YOLO 계열도 이 방향으로 왔다. 최근 세대는 학습 시
      <strong>일대다 분기와 일대일 분기를 함께</strong> 두고,
      추론에서는 일대일 분기만 써서 NMS 를 생략한다.
      학습의 이점(양성 많음)과 추론의 이점(NMS 없음)을 둘 다 취하는 구성이다.
    </p>
    <div class="note">
      <b>NMS 제거가 왜 중요한가.</b> 정확도보다 <strong>배포</strong> 쪽 이유가 크다.
      NMS 는 데이터 의존적 반복문이라 <em>연산 그래프에 넣기 어렵다</em>.
      <a href="yolo-lineage.html">모바일·엣지 런타임</a>에서 지원 연산자가 제한적일 때
      NMS 가 걸림돌이 되고, 지연도 입력 장면에 따라 들쭉날쭉해진다.
      NMS-free 모델은 <em>지연이 예측 가능</em>하다는 점에서 실무적으로 유리하다.
    </div>
    <p>
      정리하면 NMS 의 역사는 <em>검출기 전체의 축소판</em>이다.
      영역 제안 → 앵커 → 라벨 할당이 차례로 학습에 흡수됐고,
      NMS 가 마지막으로 남은 수작업이었다.
      <a href="detection-lineage.html">검출 계보</a>에서 본
      <strong>"손으로 정하던 것을 하나씩 학습으로"</strong>라는 흐름의 마지막 장이다.
    </p>
  </section>
"""

READING = [
    "Bodla et al., <em>Soft-NMS — Improving Object Detection With One Line of Code</em> (arXiv:1704.04503) — 삭제 대신 감쇠.",
    "Zheng et al., <em>Distance-IoU Loss: Faster and Better Learning for Bounding Box Regression</em> (arXiv:1911.08287) — DIoU-NMS.",
    "Carion et al., <em>End-to-End Object Detection with Transformers</em> (arXiv:2005.12872) — 헝가리안 매칭으로 NMS 제거.",
    "Wang et al., <em>YOLOv10: Real-Time End-to-End Object Detection</em> (arXiv:2405.14458) — 이중 라벨 할당으로 NMS-free.",
    "Shao et al., <em>CrowdHuman: A Benchmark for Detecting Human in a Crowd</em> (arXiv:1805.00123) — 가림 상황의 난이도를 드러낸 데이터셋.",
    "Hosang et al., <em>Learning Non-Maximum Suppression</em> (arXiv:1705.02950) — NMS 자체를 학습하려는 시도.",
]

write(
    "nms.html",
    title="NMS — 중복 상자를 걷어내는 마지막 수작업",
    eyebrow="Vision · Post-processing · 2005–2026",
    h1="NMS",
    subtitle="중복 상자를 걷어내는 마지막 수작업 — 그리고 그것을 없애는 흐름",
    dek=(
        "검출기는 물체 하나에 상자 여럿을 낸다. 학습에서는 그것이 <em>의도된 것</em>이다 — "
        "양성 표본이 많아야 잘 배운다. 그런데 출력은 하나여야 한다. "
        "이 어긋남을 메우는 후처리가 NMS 이고, "
        "검출기 계보에서 <strong>가장 오래 남은 수작업</strong>이었다."
    ),
    spec=[
        ("하는 일", "겹치는 상자 제거"),
        ("척도", "IoU (절반 겹침 = 0.333)"),
        ("흔한 임계값", "0.45 ~ 0.5"),
        ("실패", "가려진 물체를 지움"),
        ("현재 방향", "학습으로 흡수 (NMS-free)"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

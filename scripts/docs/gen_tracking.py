#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1eef0", panel="#e8e2e5", ink="#1a1316", **{
    "ink-soft": "#544850", "ink-faint": "#827079", "rule": "#d3c9ce",
    "rule-strong": "#b3a5ac", "accent": "#8f2d4a", "accent-fill": "#f5dbe2",
    "accent-line": "#b8536f", "muted": "#8a858c", "muted-fill": "#e1dbde", "warn": "#8a5510",
})
DARK = dict(paper="#110d0f", panel="#1a1418", ink="#eae2e6", **{
    "ink-soft": "#aba0a6", "ink-faint": "#7a6e75", "rule": "#261e22", "rule-strong": "#3e3238",
    "accent": "#e8829b", "accent-fill": "#2c0f18", "accent-line": "#a8455f",
    "muted": "#8d868b", "muted-fill": "#1d171b", "warn": "#dba25a",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>상자에는 번호가 없다</h2>
    <p>
      <a href="detection-lineage.html">검출기</a>는 매 프레임을 <strong>처음 보는 것처럼</strong> 처리한다.
      100번째 프레임에서 사람 세 명을 찾아냈다고 해서
      그 상자들이 99번째 프레임의 어느 상자와 같은 사람인지는 아무도 말해 주지 않는다.
      검출의 출력은 <em>상자와 점수</em>일 뿐 <em>정체성</em>이 아니다.
    </p>
    <p>
      추적(multi-object tracking)은 여기서 시작한다.
      <strong>시간 축에서 같은 대상에게 같은 번호를 유지하는 일</strong>이다.
      요구가 하나 늘었을 뿐인데 문제의 성격이 바뀐다 —
      검출은 프레임마다 독립이라 한 번 틀려도 그 프레임만 틀리지만,
      정체성은 <em>한 번 틀리면 그 뒤가 전부 틀린다</em>.
    </p>
    <div class="eq">
      <span class="cap">정체성은 곱해진다 — 프레임당 연결 정확도 p 가 T 프레임 뒤에 남기는 것</span>
      <div class="line">P(정체성 유지) = p<sup>T</sup></div>
      <div class="line">&nbsp;</div>
      <div class="line">p = 0.99&nbsp;&nbsp; T = 30 (1초)&nbsp;&nbsp;&nbsp;→ 0.740</div>
      <div class="line">p = 0.99&nbsp;&nbsp; T = 300 (10초)&nbsp;→ <strong>0.049</strong></div>
      <div class="line">p = 0.999&nbsp; T = 300 (10초)&nbsp;→ 0.741</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 30fps 기준. 프레임당 99%는 10초를 못 버틴다</div>
    </div>
    <p>
      숫자가 말하는 바는 분명하다. <strong>프레임당 99%는 좋은 성적이 아니다.</strong>
      10초짜리 궤적을 온전히 유지하려면 프레임당 실수가 <em>1000번에 한 번</em> 수준이어야 한다.
      검출에서라면 99%가 훌륭한 값이지만, 곱해지는 양에서는 그렇지 않다.
    </p>
    <div class="note">
      <b>그래서 추적은 검출의 후처리처럼 보이지만 요구 수준이 다르다.</b>
      <a href="nms.html">NMS</a>가 <em>한 프레임 안의 중복</em>을 정리하는 일이라면,
      추적은 <em>프레임 사이의 대응</em>을 정한다.
      <a href="optical-flow.html">Optical flow</a> 가 픽셀 단위로 같은 질문에 답하고,
      <a href="local-features.html">지역 특징 매칭</a>이 공간에서 같은 질문에 답한다.
      셋 다 <em>"같은 것이 어디로 갔는가"</em>이고, 추적은 그것을 <strong>물체 단위</strong>로 묻는다.
    </div>
    <p>
      쓰이는 곳은 대개 <em>세는 일과 재는 일</em>이다.
      매장에 몇 명이 들어왔는지, 차가 교차로를 지나는 데 몇 초 걸렸는지,
      같은 사람이 얼마나 머물렀는지 — 전부 <strong>정체성이 유지되어야만</strong> 답할 수 있는 질문이고,
      검출만으로는 하나도 답할 수 없다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>예측하고 짝짓는다</h2>
    <p>
      가장 오래 살아남은 골격은 <strong>tracking-by-detection</strong> 이다.
      검출기를 그대로 두고, 그 출력을 프레임 사이에서 잇는 얇은 층을 얹는다.
      두 걸음으로 나뉜다.
    </p>
    <ul>
      <li><strong>예측</strong> — 기존 트랙이 이번 프레임에 어디 있을지 미리 찍는다</li>
      <li><strong>연결</strong> — 예측 위치와 새 검출 상자를 짝지어 번호를 물려준다</li>
    </ul>
    <p>
      예측에 흔히 쓰는 것이 <strong>칼만 필터</strong>다.
      상자의 중심·크기·속도를 상태로 두고 <em>등속으로 움직인다</em>고 가정해 다음 위치를 낸다.
      검출이 들어오면 그것으로 상태를 보정한다.
      가정이 거칠지만 30fps 에서 <em>한 프레임 사이의 움직임</em>은 실제로 거의 직선이라 잘 맞는다.
    </p>
    <p>
      연결은 <strong>비용 행렬</strong>을 만들어 푼다.
      트랙 i 와 검출 j 가 얼마나 안 어울리는지를 칸마다 채우고,
      총합이 최소가 되도록 일대일로 짝짓는다 — <strong>헝가리안 알고리즘</strong>이다.
      비용으로 가장 단순한 것은 <a href="nms.html">IoU</a> 거리, 즉 <code>1 − IoU</code> 다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 250" role="img" aria-label="tracking-by-detection 의 한 프레임. 기존 트랙을 칼만 필터로 예측하고, 새 검출 상자와의 비용 행렬을 만들어 헝가리안 알고리즘으로 일대일 매칭한 뒤, 짝지어진 트랙은 갱신하고 짝이 없는 검출은 새 트랙으로, 짝이 없는 트랙은 유예 기간 뒤 종료한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="tk-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">한 프레임에서 일어나는 일</text>

            <rect x="24" y="30" width="78" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="63" y="48" text-anchor="middle" font-size="8" fill="var(--ink-soft)">기존 트랙</text>
            <text x="63" y="62" text-anchor="middle" font-size="7" fill="var(--ink-faint)">#1 #2 #3</text>

            <path d="M108 52 L130 52" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#tk-a)"/>

            <rect x="134" y="30" width="92" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="180" y="48" text-anchor="middle" font-size="8" fill="var(--accent)">칼만 예측</text>
            <text x="180" y="62" text-anchor="middle" font-size="7" fill="var(--ink-soft)">등속 가정</text>

            <rect x="24" y="96" width="78" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="63" y="114" text-anchor="middle" font-size="8" fill="var(--ink-soft)">새 검출</text>
            <text x="63" y="128" text-anchor="middle" font-size="7" fill="var(--ink-faint)">상자 + 점수</text>

            <path d="M108 118 L130 118" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#tk-a)"/>

            <rect x="134" y="86" width="92" height="64" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="180" y="102" text-anchor="middle" font-size="8" fill="var(--ink-soft)">비용 행렬</text>
            <g stroke="var(--rule)" stroke-width="0.9">
              <rect x="152" y="110" width="18" height="12" fill="var(--accent-fill)"/>
              <rect x="170" y="110" width="18" height="12" fill="none"/>
              <rect x="188" y="110" width="18" height="12" fill="none"/>
              <rect x="152" y="122" width="18" height="12" fill="none"/>
              <rect x="170" y="122" width="18" height="12" fill="var(--accent-fill)"/>
              <rect x="188" y="122" width="18" height="12" fill="none"/>
              <rect x="152" y="134" width="18" height="12" fill="none"/>
              <rect x="170" y="134" width="18" height="12" fill="none"/>
              <rect x="188" y="134" width="18" height="12" fill="var(--accent-fill)"/>
            </g>
            <text x="180" y="160" text-anchor="middle" font-size="7" fill="var(--ink-faint)">1 − IoU (+ 외형 거리)</text>

            <path d="M232 118 L254 118" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#tk-a)"/>

            <rect x="258" y="96" width="92" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="304" y="114" text-anchor="middle" font-size="8" fill="var(--accent)">헝가리안</text>
            <text x="304" y="128" text-anchor="middle" font-size="7" fill="var(--ink-soft)">총합 최소 일대일</text>

            <path d="M356 118 L378 118" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#tk-a)"/>

            <rect x="382" y="62" width="140" height="34" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="452" y="76" text-anchor="middle" font-size="8" fill="var(--ink-soft)">짝지어짐 → 번호 유지</text>
            <text x="452" y="89" text-anchor="middle" font-size="7" fill="var(--ink-faint)">칼만 상태 갱신</text>

            <rect x="382" y="102" width="140" height="34" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="452" y="116" text-anchor="middle" font-size="8" fill="var(--ink-soft)">남은 검출 → 새 트랙</text>
            <text x="452" y="129" text-anchor="middle" font-size="7" fill="var(--ink-faint)">몇 프레임 뒤 확정</text>

            <rect x="382" y="142" width="140" height="34" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="452" y="156" text-anchor="middle" font-size="8" fill="var(--warn)">남은 트랙 → 유예</text>
            <text x="452" y="169" text-anchor="middle" font-size="7" fill="var(--ink-faint)">N 프레임 안 오면 종료</text>

            <path d="M452 58 C 452 34, 180 22, 180 26" stroke="var(--accent-line)" stroke-width="1.2" fill="none" stroke-dasharray="3 3" marker-end="url(#tk-a)"/>
            <text x="316" y="34" text-anchor="middle" font-size="7" fill="var(--accent)">다음 프레임으로</text>

            <line x1="24" y1="196" x2="674" y2="196" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="214" font-size="8" fill="var(--ink-soft)">비용 행렬은 작다 — 트랙 100 × 검출 100 이면 10,000칸,</text>
            <text x="24" y="228" font-size="8" fill="var(--ink-soft)">헝가리안은 O(n³) 이라 약 10⁶ 연산이다.</text>
            <text x="24" y="242" font-size="8" fill="var(--accent)">비용은 전부 검출기에 있다. 추적 층 자체는 거의 공짜다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        예측 → 비용 행렬 → 일대일 매칭 → 갱신. 이 고리가 매 프레임 돈다.
        <strong>짝이 남는 쪽</strong>이 실무의 절반이다 —
        짝 없는 검출은 <em>새 트랙</em>이 되고, 짝 없는 트랙은 <em>바로 죽이지 않고 몇 프레임 기다린다</em>.
        이 유예 길이가 짧으면 잠깐 가려진 사람이 새 번호를 받고, 길면 남의 번호를 물려받는다.
      </figcaption>
    </figure>

    <p>
      이 골격을 최소 형태로 보여준 것이 <strong>SORT</strong>(2016)다.
      칼만 필터와 헝가리안, IoU 비용이 전부인데
      논문은 <em>단일 머신에서 260Hz</em> 로 돈다고 보고했다.
      추적 층이 얼마나 가벼운지를 보여주는 숫자다 —
      실제 비용은 앞단 검출기가 다 쓴다.
    </p>
    <div class="note">
      <b>그래서 추적기 성능은 검출기 성능에 매여 있다.</b>
      검출이 놓친 프레임에서는 짝지을 상자 자체가 없고,
      검출이 흔들리면 비용 행렬도 흔들린다.
      <em>추적기를 바꾸기 전에 검출기를 보는 것</em>이 대개 맞는 순서다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>위치만으로는 부족하다 — 외형을 넣는다</h2>
    <p>
      IoU 비용은 <em>겹치면 같은 것</em>이라는 가정 위에 있다.
      사람이 서로 지나쳐 상자가 포개지는 순간 이 가정이 무너진다.
      두 트랙의 예측 상자가 둘 다 두 검출과 겹치면
      헝가리안은 <strong>총합이 작은 쪽</strong>을 고를 뿐, 누가 누구인지는 모른다.
    </p>
    <p>
      <strong>DeepSORT</strong>(2017)가 넣은 것이 <em>외형</em>이다.
      상자를 잘라 임베딩 모델에 넣어 벡터를 뽑고,
      트랙마다 최근 벡터를 모아 둔 다음, 비용에 <strong>코사인 거리</strong>를 더한다.
      논문은 이것으로 SORT 대비 <strong>ID 스위치를 45% 줄였다</strong>고 보고한다.
    </p>
    <div class="eq">
      <span class="cap">두 종류의 거리를 섞는다</span>
      <div class="line">cost(i, j) = λ · d<sub>운동</sub>(i, j) + (1 − λ) · d<sub>외형</sub>(i, j)</div>
      <div class="line">&nbsp;</div>
      <div class="line">d<sub>운동</sub>&nbsp;&nbsp;예측 상자와의 IoU 거리 — <strong>짧은 가림에 강함</strong></div>
      <div class="line">d<sub>외형</sub>&nbsp;&nbsp;임베딩 코사인 거리 — <strong>긴 공백을 건넘</strong></div>
    </div>
    <p>
      여기서 추적은 조용히 <a href="person-reid.html">재식별(Re-ID)</a> 문제가 된다.
      <em>다른 카메라의 같은 사람</em>을 찾는 문제와
      <em>다른 프레임의 같은 사람</em>을 찾는 문제는 형식이 같다.
      학습에 없던 대상을 다뤄야 하므로 분류가 아니라 <strong>거리</strong>를 배워야 하고,
      그래서 <a href="metric-learning.html">메트릭 러닝</a>이 그대로 들어온다.
      추적기 안의 외형 모델은 사실상 작은 Re-ID 모델이다.
    </p>
    <p>
      트랙의 외형을 어떻게 대표할지도 선택이다.
      최근 벡터 하나만 쓰면 가려진 순간의 나쁜 벡터에 끌려가고,
      전부 평균 내면 옷을 갈아입듯 서서히 변하는 외형을 못 따라간다.
      실무에서는 <em>지수이동평균으로 천천히 갱신하되 저품질 프레임은 건너뛰는</em> 절충이 흔하다.
    </p>
    <div class="note">
      <b>외형이 만능은 아니다.</b> 같은 유니폼을 입은 선수들,
      같은 색 옷의 군중, 뒷모습만 보이는 구간에서는 임베딩이 거의 구분을 못 한다.
      <a href="similarity-threshold.html">유사도 임계값</a>에서 본 문제가 그대로 나온다 —
      <em>거리 분포가 겹치면 임계값을 어디에 놓아도 한쪽이 틀린다.</em>
      그래서 외형은 위치를 <strong>대체</strong>하는 것이 아니라 <strong>보강</strong>하는 자리에 둔다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>버린 상자를 다시 줍다</h2>
    <p>
      추적기는 보통 검출 점수에 임계값을 걸고 시작한다.
      0.5 아래는 오검출로 보고 버린 뒤, 남은 상자만 연결에 쓴다.
      <strong>ByteTrack</strong>(2021)의 관찰은 이 습관을 정면으로 겨눈다 —
      <em>가려진 물체는 점수가 낮아진다.</em>
      즉 <strong>버려진 낮은 점수 상자 안에 가장 어려운 대상이 들어 있다.</strong>
    </p>
    <p>
      처방은 놀랄 만큼 단순하다. 연결을 <strong>두 번</strong> 한다.
    </p>
    <ul>
      <li><strong>1차</strong> — 높은 점수 상자만으로 평소처럼 매칭한다</li>
      <li><strong>2차</strong> — 짝을 못 찾은 트랙을 <em>낮은 점수 상자</em>와 IoU 로만 매칭한다</li>
    </ul>
    <p>
      2차에서 외형을 쓰지 않는 것이 요점이다.
      낮은 점수 상자는 대개 가려지거나 흐릿해서 <em>임베딩이 믿을 만하지 않다</em>.
      대신 <strong>이미 예측 위치가 있는 트랙</strong>만 상대하므로
      "이 자리에 뭔가 있다"는 약한 증거로 충분하다.
      점수가 낮다는 것은 <em>없다</em>가 아니라 <em>애매하다</em>는 뜻이고,
      맥락이 있으면 애매함은 해소된다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>MOT17 test</th><th>MOTA</th><th>IDF1</th><th>HOTA</th><th>속도</th></tr>
        </thead>
        <tbody>
          <tr><td>ByteTrack (논문 보고)</td><td class="hi">80.3</td><td class="hi">77.3</td><td class="hi">63.1</td><td>30 FPS (V100 1장)</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      이 결과가 인상적인 이유는 <em>새 모듈이 없다</em>는 데 있다.
      학습되는 부품을 하나도 추가하지 않고, 이미 검출기가 계산해 놓고 버리던 것을 주워 썼다.
      <a href="nms.html">NMS</a>·<a href="similarity-threshold.html">임계값</a>에서 반복해 나오는 구조다 —
      <strong>임계값은 결정을 단순하게 만드는 대신 정보를 버리고,
      버려진 정보에는 대개 가장 어려운 사례가 몰려 있다.</strong>
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 210" role="img" aria-label="검출 점수 분포와 두 단계 연결. 높은 점수 구간은 1차 매칭에 쓰이고, 종래에 버려지던 낮은 점수 구간은 2차 매칭에서 기존 트랙과만 IoU로 연결된다. 가려진 대상은 점수가 낮은 쪽으로 밀려나므로 이 구간에 어려운 사례가 몰린다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">검출 점수 축 — 무엇을 버리고 있었나</text>

            <line x1="24" y1="120" x2="560" y2="120" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="24" y="136" font-size="7.5" fill="var(--ink-faint)">0.0</text>
            <text x="268" y="136" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">0.5</text>
            <text x="552" y="136" font-size="7.5" fill="var(--ink-faint)">1.0</text>

            <rect x="24" y="86" width="244" height="34" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
            <rect x="268" y="60" width="284" height="60" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>

            <text x="146" y="106" text-anchor="middle" font-size="8" fill="var(--ink-soft)">낮은 점수</text>
            <text x="410" y="94" text-anchor="middle" font-size="8" fill="var(--accent)">높은 점수</text>

            <line x1="268" y1="46" x2="268" y2="128" stroke="var(--warn)" stroke-width="1.4" stroke-dasharray="4 3"/>
            <text x="268" y="40" text-anchor="middle" font-size="8" fill="var(--warn)">종래 임계값</text>

            <text x="146" y="158" text-anchor="middle" font-size="7.5" fill="var(--warn)">가려진 사람 · 흐린 상자</text>
            <text x="146" y="171" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">+ 진짜 오검출</text>
            <text x="146" y="188" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">→ 통째로 버려졌다</text>

            <text x="410" y="158" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">1차 매칭에 사용</text>
            <text x="410" y="171" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">IoU + 외형</text>

            <line x1="580" y1="30" x2="580" y2="190" stroke="var(--rule)" stroke-width="1"/>

            <text x="596" y="52" font-size="8" fill="var(--accent)">ByteTrack</text>
            <text x="596" y="70" font-size="7.5" fill="var(--ink-soft)">1차 — 높은 점수</text>
            <text x="596" y="83" font-size="7.5" fill="var(--ink-faint)">평소대로</text>
            <text x="596" y="103" font-size="7.5" fill="var(--ink-soft)">2차 — 남은 트랙만</text>
            <text x="596" y="116" font-size="7.5" fill="var(--ink-faint)">낮은 점수와 IoU</text>
            <text x="596" y="136" font-size="7.5" fill="var(--ink-faint)">외형은 안 씀</text>
            <text x="596" y="149" font-size="7.5" fill="var(--ink-faint)">(믿을 수 없어서)</text>
            <text x="596" y="176" font-size="7.5" fill="var(--accent)">새 학습 부품 0개</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 2</span>
        낮은 점수 구간에는 <strong>오검출과 가려진 진짜 대상이 섞여</strong> 있다.
        그것만 따로 보면 가릴 수 없지만, <em>기존 트랙의 예측 위치라는 맥락</em>을 곁들이면 갈라진다.
        2차 매칭이 <strong>새 트랙을 만들지 않는</strong> 것이 안전장치다 —
        짝을 못 찾은 낮은 점수 상자는 그냥 버려지므로 오검출이 트랙으로 승격되지 않는다.
      </figcaption>
    </figure>

    <p>
      뒤이은 개선들도 대부분 <em>새 모델이 아니라 가정을 손보는</em> 쪽이었다.
      <strong>OC-SORT</strong>(2022)는 칼만 필터의 등속 가정이
      <em>가려진 구간에서 오차를 누적</em>한다는 점을 지적한다 —
      관측이 없는 동안 예측만 반복하면 상태가 조용히 어긋나고,
      대상이 다시 나타났을 때는 이미 엉뚱한 곳을 보고 있다.
      그래서 트랙이 복구되면 <em>공백 구간의 상태를 관측 기준으로 다시 계산</em>한다.
      <strong>BoT-SORT</strong>(2022)는 <em>카메라가 움직이면 모든 상자가 함께 움직인다</em>는 점을 보정한다 —
      배경 정합으로 전역 움직임을 먼저 빼고 나서 물체의 움직임을 본다.
    </p>
    <div class="note">
      <b>세 방법의 공통점.</b> 전부 <em>학습하지 않는 부분</em>을 고쳤다.
      점수 임계값, 등속 가정, 정지 카메라 가정 —
      코드에 손으로 박혀 있던 전제들이다.
      <a href="detection-lineage.html">검출기 계보</a>가 앵커·라벨 할당·NMS 를 차례로 학습에 넘긴 것과 같은 지점에
      추적이 지금 서 있다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>무엇으로 재는가, 그리고 어디로 가는가</h2>
    <p>
      추적을 평가하려면 <em>검출이 맞았는가</em>와 <em>번호가 유지됐는가</em>를 함께 봐야 하는데,
      오래 쓰인 <strong>MOTA</strong> 는 이 둘을 한 분수에 밀어 넣는다.
    </p>
    <div class="eq">
      <span class="cap">MOTA 와 그 무감각 — GT 100,000 상자, FN 10,000, FP 8,000 을 고정하고 IDSW 만 바꾸면</span>
      <div class="line">MOTA = 1 − (FN + FP + IDSW) / GT</div>
      <div class="line">&nbsp;</div>
      <div class="line">IDSW =&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;→ MOTA 0.8200</div>
      <div class="line">IDSW =&nbsp;&nbsp;500&nbsp;&nbsp;→ MOTA 0.8150</div>
      <div class="line">IDSW = 1,000&nbsp;&nbsp;→ MOTA 0.8100</div>
      <div class="line">IDSW = 2,000&nbsp;&nbsp;→ MOTA 0.8000</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 정체성 실패가 <strong>4배</strong>로 늘어도 점수는 2점 빠진다</div>
    </div>
    <p>
      정체성이 곱해지는 양이라는 것을 01절에서 봤는데,
      MOTA 는 그것을 <em>더하는 양</em>으로 취급한다.
      그래서 MOTA 만 보고 고르면 <strong>검출만 잘하는 추적기</strong>가 이긴다.
      반대편 지표인 <strong>IDF1</strong> 은 정체성 쪽으로 치우쳐 검출 품질을 덜 본다.
    </p>
    <p>
      <strong>HOTA</strong>(2021)는 둘을 분리해 재고 <em>기하평균</em>으로 합친다.
    </p>
    <div class="eq">
      <span class="cap">HOTA = √(DetA × AssA) — 기하평균이 불균형을 벌한다</span>
      <div class="line">DetA 0.75 · AssA 0.75&nbsp;&nbsp;산술평균 0.750&nbsp;&nbsp;HOTA <strong>0.750</strong></div>
      <div class="line">DetA 0.90 · AssA 0.60&nbsp;&nbsp;산술평균 0.750&nbsp;&nbsp;HOTA <strong>0.735</strong></div>
      <div class="line">DetA 0.80 · AssA 0.40&nbsp;&nbsp;산술평균 0.600&nbsp;&nbsp;HOTA <strong>0.566</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 산술평균이 같아도 한쪽이 무너지면 HOTA 는 내려간다</div>
      <div class="line">// DetA·AssA 를 따로 볼 수 있는 것이 실무에서 더 유용하다</div>
    </div>
    <p>
      실무적으로 값진 것은 총점보다 <strong>분해</strong>다.
      DetA 가 낮으면 검출기를 손볼 일이고, AssA 가 낮으면 연결 로직이나 외형 모델을 볼 일이다.
      <a href="evaluation-benchmarks.html">평가 지표를 고르는 일</a>이
      곧 <em>무엇을 개선하게 될지를 고르는 일</em>이라는 원칙이 여기서도 그대로 성립한다.
    </p>
    <p>
      그리고 예상대로, <strong>연결 자체를 학습으로 흡수하려는</strong> 흐름이 있다.
      <strong>MOTR</strong>(2022)은 <a href="detr-lineage.html">DETR</a> 의 쿼리를 시간 축으로 늘린다 —
      한 번 잡힌 대상은 <em>트랙 쿼리</em>가 되어 다음 프레임으로 넘어가고,
      그 쿼리가 계속 같은 대상을 물고 간다.
      비용 행렬도, 칼만 필터도, 임계값도 없다.
      춤추는 사람처럼 <em>움직임이 불규칙하고 외형이 서로 비슷한</em> DanceTrack 에서
      MOTR 은 ByteTrack 을 HOTA 기준 6.5% 앞섰다고 보고됐다.
      운동 가정이 무너지는 곳에서 손으로 짠 규칙이 먼저 무너진다는 뜻이다.
    </p>
    <p>
      다른 갈래는 <strong>기억을 모델 안에 두는</strong> 것이다.
      <strong>SAM 2</strong>(2024)는 <a href="segmentation.html">분할</a> 모델에 스트리밍 메모리를 붙여
      한 번 지정된 대상을 영상 내내 따라간다.
      가려짐을 따로 판정하는 출력을 두어, 사라진 동안에는 마스크를 내지 않다가
      다시 나타나면 메모리로 이어 붙인다.
      <em>추적을 별도 단계로 두지 않고 표현 자체에 시간을 넣는</em> 접근이다.
    </p>
    <div class="pair">
      <div class="fast">
        <span class="kicker">tracking-by-detection</span>
        <p>
          부품이 분리돼 있어 검출기만 갈아 끼울 수 있다.
          왜 틀렸는지 단계별로 볼 수 있고, 추적 층은 거의 공짜다.
          대신 가정들이 손으로 박혀 있어 장면이 바뀌면 다시 맞춰야 한다.
        </p>
      </div>
      <div class="slow">
        <span class="kicker">끝단 학습 · 메모리</span>
        <p>
          운동 가정이 통하지 않는 장면에서 강하다.
          대신 프레임 단위가 아니라 <em>구간 단위</em> 라벨이 필요해 학습이 비싸고,
          틀렸을 때 어디를 고칠지 가리키기 어렵다.
        </p>
      </div>
    </div>
    <p>
      현장의 선택은 대체로 갈라져 있다.
      <a href="mobile-runtime.html">기기 위에서 도는 파이프라인</a>은 여전히 tracking-by-detection 이다 —
      검출기 하나에 예산을 다 쓰고, 추적은 CPU 에서 도는 몇 줄이다.
      끝단 학습 추적기는 그 위에 자기 몫의 연산을 더 요구한다.
      <a href="nms.html">NMS 가 그랬듯</a> 이쪽도 언젠가 흡수될 가능성이 높지만,
      <strong>흡수의 조건은 정확도가 아니라 배포 비용</strong>이라는 점도 그때와 같다.
    </p>
    <p>
      정리하면 추적은 <em>"정체성을 시간에 걸쳐 유지하는 일"</em>이고,
      그 난이도는 <strong>실수가 곱해진다</strong>는 한 가지 성질에서 거의 다 나온다.
      위치로 시작해 외형을 더하고, 버리던 상자를 줍고, 가정을 하나씩 손보는 과정은
      전부 그 곱셈의 밑을 1에 가깝게 미는 일이었다.
    </p>
  </section>
"""

READING = [
    "Bewley et al., <em>Simple Online and Realtime Tracking</em> (arXiv:1602.00763) — 칼만 필터 + 헝가리안의 최소 골격, 260Hz.",
    "Wojke et al., <em>Simple Online and Realtime Tracking with a Deep Association Metric</em> (arXiv:1703.07402) — 외형 임베딩을 더해 ID 스위치 45% 감소.",
    "Zhang et al., <em>ByteTrack: Multi-Object Tracking by Associating Every Detection Box</em> (arXiv:2110.06864) — 낮은 점수 상자를 2차 연결에 쓴다.",
    "Cao et al., <em>Observation-Centric SORT: Rethinking SORT for Robust Multi-Object Tracking</em> (arXiv:2203.14360) — 가림 구간의 칼만 오차 누적과 재갱신.",
    "Aharon et al., <em>BoT-SORT: Robust Associations Multi-Pedestrian Tracking</em> (arXiv:2206.14651) — 카메라 움직임 보상.",
    "Luiten et al., <em>HOTA: A Higher Order Metric for Evaluating Multi-Object Tracking</em> (IJCV 2021, arXiv:2009.07736) — DetA·AssA 분해와 기하평균.",
    "Zeng et al., <em>MOTR: End-to-End Multiple-Object Tracking with Transformer</em> (arXiv:2105.03247) — 트랙 쿼리로 연결을 학습에 흡수.",
    "Ravi et al., <em>SAM 2: Segment Anything in Images and Videos</em> (arXiv:2408.00714) — 스트리밍 메모리와 가림 판정.",
]

write(
    "object-tracking.html",
    title="다중 객체 추적 — 정체성은 곱해진다",
    eyebrow="Vision · Tracking · 2016–2026",
    h1="다중 객체 추적",
    subtitle="정체성은 곱해진다 — 같은 것에 같은 번호를 유지하는 일",
    dek=(
        "검출기는 매 프레임을 처음 보는 것처럼 처리한다. "
        "상자에는 번호가 없고, 번호를 붙이는 순간 문제의 성격이 바뀐다 — "
        "<strong>검출 오류는 그 프레임에서 끝나지만 정체성 오류는 그 뒤를 전부 오염시킨다.</strong> "
        "프레임당 99%가 왜 좋은 성적이 아닌지에서 출발해, "
        "위치·외형·버려진 상자·평가 지표를 차례로 본다."
    ),
    spec=[
        ("문제", "시간 축의 정체성 유지"),
        ("기본 골격", "예측 + 일대일 매칭"),
        ("난점", "오류가 곱해진다"),
        ("전환점", "낮은 점수 상자 회수"),
        ("평가", "HOTA = √(DetA×AssA)"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-13",
)

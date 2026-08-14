#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f3efe8", panel="#eae4d9", ink="#1a1512", **{
    "ink-soft": "#584e43", "ink-faint": "#8b8174", "rule": "#ddd4c6",
    "rule-strong": "#b5aa97", "accent": "#8b4420", "accent-fill": "#f4dfd0",
    "accent-line": "#c26933", "muted": "#8a8a91", "muted-fill": "#e3ded5", "warn": "#2c5f80",
})
DARK = dict(paper="#131110", panel="#1d1a17", ink="#ede8df", **{
    "ink-soft": "#aca194", "ink-faint": "#7f7668", "rule": "#282320", "rule-strong": "#41372e",
    "accent": "#e2a26c", "accent-fill": "#2b1c12", "accent-line": "#ba7740",
    "muted": "#8c8c94", "muted-fill": "#1e1b19", "warn": "#84c0e2",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>같은 이름을 쓰는 두 문제</h2>
    <p>
      <a href="isp-pipeline.html">ISP</a> 문서에서 12비트가 8비트로 눌린다고만 적고 지나간 단계가 있다.
      <strong>톤 매핑</strong>이다. 그 앞에 놓인 <strong>HDR</strong>(High Dynamic Range)까지가 이 문서의 주제인데,
      먼저 용어를 갈라야 한다. HDR 이라는 말이 <em>방향이 반대인 두 문제</em>를 함께 가리키기 때문이다.
    </p>
    <div class="pair">
      <div class="fast">
        <span class="kicker">포착 — 넓힌다</span>
        <p>
          센서가 담을 수 있는 것보다 넓은 밝기를 <strong>기록</strong>하는 문제.
          여러 장을 합치거나 한 장에서 추정한다.
          결과물은 실수형 <em>휘도 맵</em>이지 사진이 아니다.
        </p>
      </div>
      <div class="slow">
        <span class="kicker">표시 — 좁힌다</span>
        <p>
          기록한 것을 좁은 화면에 <strong>보여주는</strong> 문제. 이것이 톤 매핑이다.
          정보를 반드시 <em>버려야</em> 하고, 무엇을 버릴지가 사진의 인상을 정한다.
        </p>
      </div>
    </div>
    <p>
      흔히 싫어하는 그 <em>과장된 HDR 느낌</em>은 앞이 아니라 뒤에서 생긴다.
      범위의 단위부터 맞추자. 다이내믹 레인지는 최대 휘도와 최소 휘도의 <strong>비</strong>이고,
      그것을 <code>log₂</code> 로 재면 사진의 <em>스톱</em>(stop)이 된다 — 1 스톱은 밝기 2배다.
    </p>
    <div class="eq">
      <span class="cap">스톱 = log₂(최대 휘도 ÷ 최소 휘도)</span>
      <div class="line">창밖이 보이는 실내&nbsp;&nbsp;10⁶ : 1&nbsp;&nbsp;→&nbsp;&nbsp;<strong>19.9 스톱</strong></div>
      <div class="line">12비트 센서&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;&nbsp;<strong>약 12 스톱</strong></div>
      <div class="line">보통의 SDR 화면&nbsp;&nbsp;&nbsp;&nbsp;1,000 : 1&nbsp;&nbsp;→&nbsp;&nbsp;<strong>10.0 스톱</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">센서가 장면의 <em>양 끝</em>을 자르고, 화면이 남은 것을 다시 누른다 — 손실이 두 번</div>
    </div>
    <div class="note">
      <b>비트 심도와 다이내믹 레인지는 다른 것이다.</b> 12비트는 4,096<em>단계</em>라는 뜻이지
      12스톱이라는 뜻이 아니다. 단계는 <strong>얼마나 곱게 나누는가</strong>이고
      다이내믹 레인지는 <strong>위아래로 얼마나 넓은가</strong>다.
      선형 부호화에서는 둘이 맞물리지만 로그·감마로 부호화하면 같은 비트로 훨씬 넓게 담는다 — 5절의 PQ·HLG 가 그 장치다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>여러 장으로 넓히기 — 그리고 유령</h2>
    <p>
      가장 직접적인 방법은 <strong>노출을 바꿔 여러 장 찍는 것</strong>이다.
      어둡게 찍은 장은 하이라이트가 살아 있고 밝게 찍은 장은 그림자가 살아 있다.
      −3EV / 0 / +3EV 세 장이면 센서 범위에 <strong>6 스톱</strong>이 붙는다 — 12 스톱 센서가 18 스톱이 된다.
    </p>
    <p>
      1997년 Debevec 과 Malik 이 이 합성을 정식화했다.
      화소값은 <em>휘도 × 노출 시간</em>을 카메라 응답 함수에 통과시킨 값이므로,
      노출을 알면 역산할 수 있다는 발상이다.
    </p>
    <div class="eq">
      <span class="cap">노출을 되돌려 절대 휘도를 복원한다</span>
      <div class="line">관측&nbsp;&nbsp;Z<sub>ij</sub> = f( E<sub>i</sub> · Δt<sub>j</sub> )&nbsp;&nbsp;&nbsp;&nbsp;// f = 응답 함수, E = 휘도, Δt = 노출</div>
      <div class="line">복원&nbsp;&nbsp;ln E<sub>i</sub> = Σ<sub>j</sub> w(Z<sub>ij</sub>) [ g(Z<sub>ij</sub>) − ln Δt<sub>j</sub> ] ÷ Σ<sub>j</sub> w(Z<sub>ij</sub>)</div>
      <div class="line">&nbsp;</div>
      <div class="line">w 는 <strong>중간 밝기에 크고 양 끝에 작다</strong> — 0 과 255 에는 정보가 없기 때문</div>
    </div>
    <p>
      여기에 조용한 전제가 하나 있다. <strong>여러 장이 정확히 같은 장면이어야 한다</strong>는 것.
      손이 흔들리고 사람이 걸으면 전제가 깨지고, 깨진 자리에 <strong>고스팅</strong>이 남는다.
      정렬로 잡을 수는 있지만 — <a href="optical-flow.html">Optical Flow</a> 가 하는 일이 그것이다 —
      <em>노출이 다른</em> 두 장의 대응을 찾는 일은 훨씬 어렵다. 밝기 항상성 가정이 아예 성립하지 않는다.
    </p>
    <p>
      그래서 2007년 Mertens 등의 <strong>노출 융합</strong>은 휘도 맵 복원을 건너뛴다.
      응답 함수도 노출 시간도 없이, LDR 여러 장을 화소별 가중 합으로 바로 섞는다.
    </p>
    <div class="eq">
      <span class="cap">"잘 노출된 화소"를 식으로 쓰면</span>
      <div class="line">w = 대비 × 채도 × 노출적정도&nbsp;&nbsp;&nbsp;&nbsp;// 하나라도 0 이면 그 화소는 버려진다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;대비 = 라플라시안 크기&nbsp;&nbsp;&nbsp;&nbsp;채도 = RGB 표준편차</div>
      <div class="line">&nbsp;</div>
      <div class="line">노출적정도&nbsp;&nbsp;w(i) = exp( −(i − 0.5)² / 2σ² ),&nbsp;&nbsp;σ = 0.2</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;i=0.50 → <strong>1.000</strong>&nbsp;&nbsp;i=0.25 → 0.458&nbsp;&nbsp;i=0.10 → 0.135&nbsp;&nbsp;i=0/1 → <strong>0.044</strong></div>
    </div>
    <p>
      어느 쪽을 쓸지는 결과물의 용도가 정한다. 휘도 맵이 필요한 곳 — 조명 추정, 렌더링, 계측 —
      에서는 Debevec 계열이어야 하고, 화면에 띄울 사진 한 장이 목적이면 노출 융합이 짧고 안정적이다.
      결과가 이미 LDR 이라 <em>톤 매핑도 따로 필요 없다</em>.
      "HDR 로 찍었다"는 말이 어느 쪽인지 자주 흐려지는 이유이기도 하다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>톤 매핑 — 무엇을 버릴지 고르는 일</h2>
    <p>
      이제 좁히는 쪽이다. 18 스톱을 10 스톱 화면에 올려야 한다.
      가장 단순한 방법은 넘치는 것을 자르는 것인데, 하늘이 하얗게 날아가는 그 현상이다.
      2002년 Reinhard 등이 사진 암실의 관행 — 존 시스템, 닷징과 버닝 — 을 두 단계 식으로 옮겼다.
    </p>
    <div class="eq">
      <span class="cap">① 키 값으로 전체를 옮기고 ② 압축 곡선을 통과시킨다</span>
      <div class="line">L̄<sub>w</sub> = exp( (1/N) Σ ln(δ + L<sub>w</sub>) )&nbsp;&nbsp;&nbsp;&nbsp;// <strong>로그</strong>평균 — 산술평균이 아니다</div>
      <div class="line">L = (a / L̄<sub>w</sub>) · L<sub>w</sub>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// a = 0.18 (중간 회색)</div>
      <div class="line">&nbsp;</div>
      <div class="line">단순형&nbsp;&nbsp;&nbsp;&nbsp;L<sub>d</sub> = L / (1 + L)</div>
      <div class="line">흰점 포함&nbsp;L<sub>d</sub> = L (1 + L / L<sub>white</sub>²) / (1 + L)&nbsp;&nbsp;&nbsp;&nbsp;// L = L<sub>white</sub> 에서 정확히 1</div>
    </div>
    <p>
      두 곳에 계산이 숨어 있다. 평균이 <strong>로그</strong>평균인 이유 —
      휘도 <span class="mono">[0.02, 0.05, 0.3, 1.2, 8, 60, 400]</span> 의 산술평균은 <strong>67.08</strong> 인데
      로그평균은 <strong>1.83</strong> 이다. 태양 하나가 산술평균을 통째로 끌고 가버린다.
      그리고 단순형은 <strong>어떤 L 에도 1 에 닿지 않는다</strong> — L=1000 에서도 0.9990 이다.
      절대 날아가지 않는 대신 <em>순백이 나오지 않고</em>, <span class="mono">L_white</span> 항이 그 값을 되돌려준다.
    </p>
    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="톤 매핑 곡선 비교 그래프. 가로축은 로그2 휘도로 마이너스 6에서 플러스 8까지, 세로축은 표시값 0에서 1이다. 선형 클리핑은 휘도 1에서 곧바로 1에 도달해 그 위 8스톱을 전부 잃는다. Reinhard 단순형은 완만하게 올라가되 1에 닿지 않는다. 흰점을 8로 둔 Reinhard는 휘도 8에서 1에 도달한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="20" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">같은 장면, 다른 곡선 — 무엇을 버리는가</text>

            <g stroke="var(--rule)" stroke-width="0.7">
              <line x1="70" y1="44" x2="620" y2="44"/>
              <line x1="70" y1="120" x2="620" y2="120"/>
            </g>
            <line x1="70" y1="196" x2="620" y2="196" stroke="var(--rule-strong)" stroke-width="1"/>
            <line x1="70" y1="196" x2="70" y2="40" stroke="var(--rule-strong)" stroke-width="1"/>

            <path d="M70 194 L83 193 L96 192 L109 191 L122 190 L135 188 L149 186 L162 184 L175 181 L188 177 L201 172 L214 166 L227 158 L240 148 L253 136 L266 120 L280 100 L293 75 L306 44 L620 44" fill="none" stroke="var(--warn)" stroke-width="1.6" stroke-dasharray="4 3"/>
            <path d="M70 194 L86 193 L102 192 L119 191 L135 189 L151 187 L167 184 L183 180 L199 176 L216 170 L232 164 L248 156 L264 147 L280 137 L296 126 L313 115 L329 105 L345 95 L361 86 L377 77 L394 71 L410 65 L426 60 L442 57 L458 54 L474 51 L491 50 L507 48 L523 47 L539 46 L555 46 L571 45 L588 45 L604 45 L620 45" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <path d="M70 194 L86 193 L102 192 L119 191 L135 189 L151 187 L167 184 L183 180 L199 176 L216 170 L232 163 L248 155 L264 146 L280 136 L296 125 L313 114 L329 103 L345 92 L361 81 L377 71 L394 61 L410 52 L426 44 L442 44 L458 44 L474 44 L491 44 L507 44 L523 44 L539 44 L555 44 L571 44 L588 44 L604 44 L620 44" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="6 3"/>

            <g font-size="7.5" fill="var(--ink-faint)">
              <text x="70" y="210" text-anchor="middle">−6</text>
              <text x="149" y="210" text-anchor="middle">−4</text>
              <text x="227" y="210" text-anchor="middle">−2</text>
              <text x="306" y="210" text-anchor="middle">0</text>
              <text x="384" y="210" text-anchor="middle">+2</text>
              <text x="463" y="210" text-anchor="middle">+4</text>
              <text x="541" y="210" text-anchor="middle">+6</text>
              <text x="620" y="210" text-anchor="middle">+8</text>
              <text x="345" y="228" text-anchor="middle">log₂ L &nbsp;(스톱)</text>
              <text x="58" y="47" text-anchor="end">1.0</text>
              <text x="58" y="123" text-anchor="end">0.5</text>
              <text x="58" y="199" text-anchor="end">0</text>
            </g>

            <g font-size="8">
              <text x="316" y="36" fill="var(--warn)">선형 클리핑 — 여기서 위쪽 8 스톱이 전부 사라진다</text>
              <text x="466" y="88" fill="var(--accent)">Reinhard, L_white = 8</text>
              <text x="452" y="140" fill="var(--accent-line)">Reinhard 단순형 — 1 에 닿지 않는다</text>
            </g>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        가로축이 <em>로그</em> 휘도라는 점이 중요하다. 클리핑 곡선이 오른쪽 절반을 천장에 붙여 놓은
        만큼이 <strong>버려진 정보</strong>다. Reinhard 곡선은 그 구간을 살리는 대신 중간 대비를 내준다.
        위 예시 휘도는 입력이 <strong>14.3 스톱</strong>인데 단순형을 지나면 출력이 <strong>9.0 스톱</strong>이 된다.
      </figcaption>
    </figure>
    <p>
      여기까지가 <strong>전역</strong> 연산자다. 화소 하나를 볼 때 그 값만 보므로 빠르고 예측 가능한 대신,
      전체를 눌렀으니 <em>국소 대비가 함께 죽는다</em> — 창밖도 방 안도 다 보이는데 밋밋한 그 결과다.
      같은 해 Durand 와 Dorsey 가 내놓은 <strong>지역</strong> 연산자는 이미지를 두 층으로 갈라
      압축을 한쪽에만 건다.
    </p>
    <div class="eq">
      <span class="cap">base / detail 분해 — 세부는 남기고 밝기만 누른다</span>
      <div class="line">log L&nbsp;&nbsp;=&nbsp;&nbsp;base&nbsp;&nbsp;+&nbsp;&nbsp;detail</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;base&nbsp;&nbsp;&nbsp;= <strong>양방향 필터</strong>(log L)&nbsp;&nbsp;&nbsp;&nbsp;// 경계를 넘지 않는 저역 통과</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;detail = log L − base</div>
      <div class="line">&nbsp;</div>
      <div class="line">출력&nbsp;&nbsp;=&nbsp;&nbsp;exp( <strong>γ · base</strong> + detail ),&nbsp;&nbsp;γ &lt; 1</div>
    </div>
    <p>
      <a href="denoising.html">노이즈 제거</a>의 양방향 필터가 여기 다시 나온다.
      가우시안 필터를 쓰면 평균이 경계를 넘어 새어 나가고 그 결과가 <strong>헤일로</strong>다 —
      밝은 하늘과 어두운 건물의 경계에 생기는 밝은 띠. 양방향 필터는 <em>값이 비슷한 이웃만</em> 평균한다.
    </p>
    <div class="note">
      <b>지역 연산자의 대가는 물리적 순서가 깨진다는 것이다.</b>
      전역 연산자는 단조 함수라 <em>원래 밝던 곳이 여전히 밝다</em>는 성질이 보장되는데,
      지역 연산자는 그 보장을 버린다 — 어두운 방 안의 흰 종이가 창밖 하늘보다 밝게 나올 수 있다.
      보기에는 자연스럽지만 <strong>계측이나 인식의 입력으로는 위험한 변형</strong>이고,
      <a href="isp-pipeline.html">ISP</a> 에서 본 "사람 눈이냐 모델이냐"의 분기가 여기서 다시 나온다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>모바일이 택한 우회로 — 브라케팅을 하지 않는다</h2>
    <p>
      휴대폰은 앞의 전제가 특히 잘 깨지는 환경이다. 삼각대가 없고, 손이 흔들리고,
      찍히는 대상이 대개 <em>움직이는 사람</em>이다. 2016년 Google 의 <strong>HDR+</strong> 는
      브라케팅과 고스팅의 충돌을 <em>피하는</em> 쪽을 골랐다.
      노출을 바꾸지 않고 <strong>똑같이 짧은 노출로 여러 장</strong>을, 그것도 일부러 어둡게 찍는다.
    </p>
    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 200" role="img" aria-label="브라케팅과 짧은 노출 버스트를 비교한 도식. 브라케팅은 노출이 다른 세 장을 찍어 범위를 넓히지만 노출이 길어 블러와 고스팅이 생긴다. 짧은 노출 버스트는 동일한 짧은 노출로 여덟 장을 찍어 하이라이트를 지키고, 그림자의 노이즈는 프레임 평균으로 갚는다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="20" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">같은 목표, 반대 전략</text>

            <text x="26" y="48" font-size="8.5" fill="var(--ink)">브라케팅</text>
            <g>
              <rect x="120" y="38" width="34" height="16" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="166" y="34" width="70" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="248" y="30" width="140" height="32" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            </g>
            <g font-size="7" fill="var(--ink-faint)">
              <text x="137" y="49" text-anchor="middle">−3EV</text>
              <text x="201" y="49" text-anchor="middle">0EV</text>
              <text x="318" y="49" text-anchor="middle">+3EV &nbsp;(노출이 길다)</text>
            </g>
            <text x="404" y="45" font-size="8" fill="var(--warn)">✗ 긴 노출 = 블러</text>
            <text x="404" y="58" font-size="8" fill="var(--warn)">✗ 프레임 간 노출차 = 정렬 난이도 ↑ → 고스팅</text>

            <line x1="26" y1="80" x2="674" y2="80" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="108" font-size="8.5" fill="var(--ink)">짧은 노출 버스트</text>
            <g>
              <rect x="120" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="156" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="192" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="228" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="264" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="300" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="336" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
              <rect x="372" y="98" width="30" height="16" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1"/>
            </g>
            <text x="414" y="110" font-size="8" fill="var(--accent)">전부 같은 노출 · 전부 언더노출</text>
            <text x="120" y="130" font-size="7.5" fill="var(--ink-faint)">→ 하이라이트가 애초에 포화하지 않는다 · 셔터가 짧아 블러도 적다</text>

            <rect x="120" y="144" width="440" height="34" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="132" y="159" font-size="8" fill="var(--accent)">대가는 그림자 노이즈 — N 장 평균으로 갚는다 (표준편차 1/√N)</text>
            <text x="132" y="173" font-size="8" fill="var(--ink-soft)">2장 0.50스톱 · 4장 1.00스톱 · 8장 1.50스톱 · 16장 2.00스톱</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 2</span>
        고스팅을 <em>고치는</em> 대신 <strong>생기지 않게 촬영한다</strong>.
        노출을 안 바꾸니 프레임 간 정렬이 쉬워지고, 짧은 노출이라 움직임 블러도 작다.
        잃은 것은 그림자의 SNR 이고, 그것을 프레임 수로 사 온다.
      </figcaption>
    </figure>
    <p>
      계산이 맞아떨어진다. <a href="denoising.html">노이즈 제거</a>에서 본 <span class="mono">1/√N</span> 이 그대로 적용돼,
      독립인 노이즈를 N 장 평균하면 표준편차가 <span class="mono">1/√N</span> 로 준다.
      스톱으로 환산하면 <strong>16 장이 정확히 2 스톱</strong>이다.
      하이라이트를 지키려고 2 스톱 언더노출로 찍고, 그 2 스톱을 16 장 평균으로 되사 오는 구조다.
    </p>
    <p>
      합성은 RAW 단계에서 한다. <a href="isp-pipeline.html">ISP</a> 에서 노이즈 제거를 디모자이킹 앞에 두는 이유를 봤는데,
      프레임 병합도 같은 논리로 노이즈 모델이 단순한 RAW 에서 해야 한다.
      기준 프레임 하나를 고르고 나머지를 쌍으로 정렬해 합치되,
      정렬이 어긋난 영역은 <strong>합치지 않고 기준 프레임을 그대로 쓴다</strong>. 유령보다 노이즈가 낫다는 판단이다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방식</th><th>얻는 것</th><th>내주는 것</th><th>정렬 난이도</th></tr>
        </thead>
        <tbody>
          <tr><td>노출 브라케팅</td><td class="hi">범위 +4~6 스톱</td><td>고스팅 · 긴 노출의 블러</td><td class="hi">높음 (노출이 다름)</td></tr>
          <tr><td>노출 융합</td><td>휘도 맵·톤매핑 불필요</td><td>물리적 휘도를 잃음</td><td>높음 (같은 이유)</td></tr>
          <tr><td>짧은 노출 버스트</td><td class="hi">고스팅이 근본적으로 적음</td><td>그림자 SNR (√N 으로 갚음)</td><td>낮음</td></tr>
          <tr><td>단일 장 복원</td><td>촬영 제약 없음</td><td class="hi">포화 영역은 지어낸 값</td><td>없음</td></tr>
        </tbody>
      </table>
    </div>
    <div class="note">
      <b>나중에 다시 브라케팅이 들어왔다.</b> Pixel 은 이후 버스트에 <em>노출이 다른 장을 섞는</em> 방식을
      추가했다. 짧은 노출만으로는 아주 어두운 장면에서 그림자 SNR 을 채우지 못했기 때문이다.
      되돌아간 것이 아니라 <strong>정렬이 좋아지자 브라케팅의 비용이 감당 가능해진 것</strong>이다.
      "고스팅 때문에 브라케팅을 피한다"는 명제의 유효기간이 정렬 성능에 달려 있었던 셈이다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>학습으로 흡수된 것, 그리고 남은 것</h2>
    <p>
      <em>정렬 → 병합 → 압축</em>이라는 손으로 짠 단계들이 각자 실패 모드를 갖는 배치는,
      <a href="detection-lineage.html">검출기</a>가 그랬듯 대개 하나의 망으로 흡수된다.
      실제로 그랬다. 특히 Wu 등(2018)은 <strong>전경이 크게 움직이는 경우</strong>를 정면으로 다뤘다 —
      광학 흐름으로 미리 정렬하는 대신 정렬되지 않은 입력을 그대로 넣고 <em>이미지 변환 문제</em>로 풀어,
      정렬 실패가 곧 고스팅이 되던 연결을 끊었다.
    </p>
    <p>
      더 나아간 것이 <strong>한 장에서 HDR 을 복원</strong>하는 시도다.
      Eilertsen 등(2017)은 포화한 영역의 값을 신경망으로 <em>예측</em>했다. 여기서 성격이 달라진다.
    </p>
    <div class="note">
      <b>포화한 화소에는 정보가 없다.</b> 255 로 잘린 하늘이 원래 얼마나 밝았는지는
      그 이미지 안에 남아 있지 않다. 단일 장 복원이 내놓는 값은 복원이 아니라
      <strong>그럴듯한 추정</strong>이다. <a href="super-resolution.html">초해상</a>에서 지적한 것과 같은 문제이고
      결론도 같다 — 감상용으로는 유용하지만 <em>증거나 계측</em>으로 쓰면 안 된다.
      지표가 좋아져도 이 성질은 바뀌지 않는다.
    </div>
    <p>
      평가도 그대로 옮겨오지 않는다. <a href="image-quality-metrics.html">화질 평가</a>의 PSNR·SSIM 은
      0~1 로 정규화된 LDR 을 전제로 설계됐다. 휘도가 수천 배로 벌어진 HDR 에 그대로 쓰면
      <strong>밝은 영역의 오차만 지표를 지배한다</strong>. 그래서 μ-law 로 압축한 뒤 PSNR 을 재거나
      사람의 대비 감도를 모형화한 HDR 전용 지표를 쓴다.
      끝으로 표시 쪽 — 앞의 톤 매핑이 전부 <em>화면이 좁다</em>는 전제 위에 있었는데 그 전제가 흔들리고 있다.
    </p>
    <div class="eq">
      <span class="cap">HDR 표시 표준 — ITU-R BT.2100</span>
      <div class="line"><strong>PQ</strong> (SMPTE ST 2084)&nbsp;&nbsp;최대 <strong>10,000 cd/m²</strong> · <em>절대</em> 휘도</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;0.005 ~ 10,000 cd/m² = log₂(2×10⁶) ≈ <strong>20.9 스톱</strong></div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;SDR 기준 백색 100 cd/m² 보다 log₂(100) = <strong>6.6 스톱</strong> 위까지</div>
      <div class="line">&nbsp;</div>
      <div class="line"><strong>HLG</strong> (ARIB STD-B67)&nbsp;&nbsp;<em>상대</em> 휘도 · SDR 화면에서도 그럭저럭 보인다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;방송처럼 <em>수신기를 고를 수 없는</em> 환경을 위한 설계</div>
    </div>
    <p>
      PQ 의 20.9 스톱은 1절에서 잰 장면의 약 20 스톱과 거의 같다 —
      원리적으로는 <strong>톤 매핑 없이 보여줄 수 있는 지점</strong>에 표준이 닿았다는 뜻이다.
      실제 패널은 아직 1,000~2,000 cd/m² 대라 압축은 계속 필요하지만 눌러야 할 폭이 줄었다.
      다만 PQ 가 절대 휘도라는 점이 문제를 남긴다 —
      <strong>같은 콘텐츠를 최대 밝기가 다른 화면에 어떻게 걸 것인가</strong>.
      결국 화면마다 다시 톤 매핑을 해야 하고, 그 단계는 표준화되지 않아 기기마다 결과가 다르다.
      압축을 촬영 쪽에서 표시 쪽으로 옮겼을 뿐 <em>무엇을 버릴지 고르는 일</em>은 사라지지 않았다.
    </p>
    <div class="note">
      <b>온디바이스에서는 프레임 수가 화질이다.</b> HDR 합성은
      <a href="mobile-runtime.html">모바일 런타임</a> 예산을 크게 먹는 축에 든다 —
      8~16장을 정렬하고 병합하는 일이 <em>셔터를 누른 뒤 1초 안에</em> 끝나야 하기 때문이다.
      그래서 실무의 선택은 대개 "더 좋은 모델"이 아니라
      <strong>몇 장을 쓸 것인가, 정렬을 어디까지 할 것인가</strong>가 된다.
      <a href="efficient-backbone.html">경량화</a>와 같은 저울인데,
      여기서는 화질이 프레임 수와 직접 교환된다는 점이 다르다.
    </div>
  </section>
"""

READING = [
    "Debevec &amp; Malik, <em>Recovering High Dynamic Range Radiance Maps from Photographs</em> (SIGGRAPH 1997) — 노출이 다른 사진들에서 카메라 응답과 절대 휘도를 복원한 원전.",
    "Reinhard et al., <em>Photographic Tone Reproduction for Digital Images</em> (SIGGRAPH 2002) — 키 값 스케일링과 L/(1+L) 계열 전역 연산자.",
    "Durand &amp; Dorsey, <em>Fast Bilateral Filtering for the Display of High-Dynamic-Range Images</em> (SIGGRAPH 2002) — base/detail 분해로 세부를 살리는 지역 연산자.",
    "Mertens et al., <em>Exposure Fusion</em> (Pacific Graphics 2007) — 휘도 맵을 만들지 않고 LDR 을 직접 섞는 우회로.",
    "Hasinoff et al., <em>Burst Photography for High Dynamic Range and Low-Light Imaging on Mobile Cameras</em> (SIGGRAPH Asia 2016) — HDR+ 원전. 짧은 노출 버스트 전략.",
    "Wu et al., <em>Deep High Dynamic Range Imaging with Large Foreground Motions</em> (arXiv:1711.08937) — 정렬을 전제하지 않고 이미지 변환으로 푸는 학습 기반 합성.",
    "Eilertsen et al., <em>HDR Image Reconstruction from a Single Exposure using Deep CNNs</em> (arXiv:1710.07480) — 포화 영역을 예측해 한 장에서 복원.",
    "Delbracio et al., <em>Mobile Computational Photography: A Tour</em> (arXiv:2102.09000) — 모바일 파이프라인 전반의 개관.",
]

write(
    "hdr-tone-mapping.html",
    title="HDR 과 톤 매핑 — 담을 수 없는 밝기를 다루는 법",
    eyebrow="Vision · Imaging · 1997–2026",
    h1="HDR 과 톤 매핑",
    subtitle="넓히는 문제와 좁히는 문제는 방향이 반대다",
    dek=(
        "장면은 약 <strong>20 스톱</strong>인데 센서는 12, 화면은 10이다. "
        "부족한 범위를 여러 장으로 넓히는 일과 넓힌 것을 다시 화면에 눌러 담는 일은 "
        "<em>이름만 같고 방향이 반대인 두 문제</em>다. "
        "휴대폰이 브라케팅을 포기하고 짧은 노출 버스트를 고른 이유도 여기 있다."
    ),
    spec=[
        ("장면 ↔ 화면", "약 20 ↔ 10 스톱"),
        ("브라케팅", "−3/0/+3 → +6 스톱"),
        ("버스트 평균", "16장 = 2 스톱"),
        ("Reinhard", "1 에 닿지 않는다"),
        ("PQ 표준", "10,000 cd/m² · 20.9 스톱"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-14",
)

#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f2f1ea", panel="#e9e7dc", ink="#191811", **{
    "ink-soft": "#54523f", "ink-faint": "#83816d", "rule": "#d6d3c4",
    "rule-strong": "#b3b09f", "accent": "#6e5a20", "accent-fill": "#eee6cc",
    "accent-line": "#96803c", "muted": "#8a8878", "muted-fill": "#e2e0d4", "warn": "#a04628",
})
DARK = dict(paper="#12120d", panel="#1a1a14", ink="#eae8dd", **{
    "ink-soft": "#a8a695", "ink-faint": "#7b7a68", "rule": "#232219", "rule-strong": "#3c3a2c",
    "accent": "#d8b96a", "accent-fill": "#2a2413", "accent-line": "#96803c",
    "muted": "#8c8a7a", "muted-fill": "#1c1c15", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>먼저 이름부터 — DINO 는 둘이다</h2>
    <p>
      이 아카이브 안에서만도 <strong>DINO</strong> 라는 이름이 서로 다른 두 가지를 가리킨다.
      섞으면 문서를 잘못 읽게 되므로 먼저 갈라 둔다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>이름</th><th>정체</th><th>어디서 나오나</th></tr>
        </thead>
        <tbody>
          <tr>
            <td class="hi">DINO (이 문서)</td>
            <td class="hi">라벨 없이 시각 표현을 배우는 <strong>자기지도 학습법</strong><br><em>self-<b>DI</b>stillation with <b>NO</b> labels</em></td>
            <td><a href="self-supervised-learning.html">자기지도 학습</a> · <a href="rf-detr.html">RF-DETR</a> 백본</td>
          </tr>
          <tr>
            <td>DINO (검출기)</td>
            <td><a href="detr-lineage.html">DETR</a> 계열 검출기. 잡음 학습과 쿼리 초기화로 수렴을 고친 모델<br><em>DETR with Improved DeNoising Anchor Boxes</em> (arXiv:2203.03605)</td>
            <td><a href="detr-lineage.html">DETR 계보</a></td>
          </tr>
          <tr>
            <td>Grounding DINO</td>
            <td>위쪽 <em>검출기</em> DINO 에 텍스트를 붙여 오픈보캐블러리로 확장한 것</td>
            <td><a href="vision-language-models.html">Vision-Language 모델</a></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p>
      약자가 우연히 겹쳤을 뿐 계보가 다르다.
      다만 <strong>DINOv2·DINOv3</strong> 는 언제나 이 문서의 자기지도 계열을 뜻한다 —
      버전 번호가 붙으면 검출기가 아니다.
    </p>
    <p>
      본론으로 간다. <a href="self-supervised-learning.html">자기지도 학습</a> 문서에서
      "자기증류(BYOL·DINO)"를 한 갈래로 소개하고 지나갔다. 이 문서는 그 갈래를 펼친다 —
      <em>라벨이 하나도 없는데 어떻게 학습 신호가 생기는가</em>, 그리고
      그렇게 배운 특징이 왜 <a href="rf-detr.html">검출기</a>·<a href="depth-estimation.html">깊이 추정</a>의
      <strong>고정 백본</strong>으로 쓰이게 됐는가.
    </p>
    <div class="note">
      <b>출발점의 이상함을 먼저 느껴 두면 좋다.</b>
      DINO 는 <a href="knowledge-distillation.html">지식 증류</a>의 형태를 그대로 쓴다 —
      교사가 내놓은 분포를 학생이 따라가게 한다.
      그런데 <em>교사가 따로 없다</em>. 교사는 학생 자신의 과거 평균이다.
      자기가 자기를 가르치는데 왜 아무것도 배우지 않는 상태(붕괴)로 무너지지 않는가 —
      그 질문이 이 방법의 전부다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>교사는 학생의 과거다 — 그리고 왜 무너지지 않는가</h2>
    <p>
      구조는 단순하다. 같은 아키텍처(<a href="vision-transformer.html">ViT</a>)를 두 벌 두고
      하나를 학생, 하나를 교사라 부른다.
      학생만 역전파로 갱신하고, 교사는 <strong>학생 가중치의 지수이동평균(EMA)</strong>으로 따라간다.
    </p>
    <div class="eq">
      <span class="cap">교사 갱신 — 그래디언트가 흐르지 않는다</span>
      <div class="line">θ<sub>t</sub> ← λ · θ<sub>t</sub> + (1 − λ) · θ<sub>s</sub></div>
      <div class="line">&nbsp;</div>
      <div class="line">λ : 0.996 → 1.0 (코사인 스케줄)&nbsp;&nbsp;// 학습이 진행될수록 교사가 천천히 움직인다</div>
      <div class="line">손실은 <strong>학생 쪽으로만</strong> 흐른다 — 교사는 stop-gradient</div>
    </div>
    <p>
      손실은 교사 분포와 학생 분포의 교차 엔트로피다. 여기까지는 증류와 같다.
      문제는 <strong>정답이 없다는 것</strong>이다.
      두 네트워크가 "모든 입력에 대해 같은 상수를 뱉자"고 합의하면 손실은 0 이 된다.
      이것이 <em>붕괴(collapse)</em>다. 아무것도 배우지 않은 상태가 최적해가 되는 함정이다.
    </p>
    <p>
      DINO 의 답은 장치 두 개를 <strong>반대 방향으로</strong> 거는 것이다.
      교사 출력에 <em>센터링</em>과 <em>샤프닝</em>을 동시에 건다.
    </p>
    <div class="eq">
      <span class="cap">교사 출력에 걸리는 두 힘</span>
      <div class="line">센터링&nbsp;&nbsp; g ← g − c&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// c 는 배치 평균의 이동평균</div>
      <div class="line">샤프닝&nbsp;&nbsp; p = softmax(g / τ<sub>t</sub>),&nbsp;&nbsp; τ<sub>t</sub> = 0.04 → 0.07</div>
      <div class="line">&nbsp;</div>
      <div class="line">학생 쪽은 더 부드럽게 &nbsp; τ<sub>s</sub> = 0.1</div>
    </div>
    <p>
      온도를 이렇게 낮추면 분포가 얼마나 뾰족해지는지는 계산해 보면 바로 보인다.
      로짓이 <code>[2.0, 1.6, 1.2, …]</code> 처럼 0.4씩 벌어진 8차원 벡터를 넣어 본 값이다.
    </p>
    <div class="eq">
      <span class="cap">온도에 따른 교사 분포 (로짓 간격 0.4, 8차원 · 직접 계산)</span>
      <div class="line">&nbsp;τ&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 최댓값&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2위&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 엔트로피</div>
      <div class="line">1.00&nbsp;&nbsp;&nbsp; 34.369%&nbsp;&nbsp; 23.038%&nbsp;&nbsp; 1.7453</div>
      <div class="line">0.10&nbsp;&nbsp;&nbsp; 98.168%&nbsp;&nbsp;&nbsp; 1.798%&nbsp;&nbsp; 0.0931&nbsp;&nbsp;← 학생</div>
      <div class="line">0.07&nbsp;&nbsp;&nbsp; 99.670%&nbsp;&nbsp;&nbsp; 0.329%&nbsp;&nbsp; 0.0222&nbsp;&nbsp;← 교사 (후반)</div>
      <div class="line">0.04&nbsp;&nbsp;&nbsp; 99.996%&nbsp;&nbsp;&nbsp; 0.005%&nbsp;&nbsp; 0.0005&nbsp;&nbsp;← 교사 (초반)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 균등분포의 엔트로피 = ln 8 = 2.0794</div>
    </div>
    <p>
      τ<sub>t</sub>=0.04 에서 교사는 사실상 <strong>원-핫</strong>이다.
      샤프닝만 걸면 곧장 붕괴한다 — 한 차원이 계속 이기면 그 차원이 영원히 이긴다.
      센터링이 막는 것이 바로 이 지점이다. 어떤 차원이 자주 이길수록 <code>c</code> 가 커져
      그 차원의 로짓을 <em>깎아</em> 버린다.
    </p>
    <div class="eq">
      <span class="cap">센터링을 키우면 승자가 바뀐다 (τ<sub>t</sub> = 0.04 · 직접 계산)</span>
      <div class="line">c&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 0번 차원&nbsp;&nbsp;&nbsp; argmax&nbsp;&nbsp; 엔트로피</div>
      <div class="line">0.0&nbsp;&nbsp;&nbsp; 99.995%&nbsp;&nbsp;&nbsp;&nbsp; dim0&nbsp;&nbsp;&nbsp; 0.0005</div>
      <div class="line">0.2&nbsp;&nbsp;&nbsp; 99.331%&nbsp;&nbsp;&nbsp;&nbsp; dim0&nbsp;&nbsp;&nbsp; 0.0402</div>
      <div class="line">0.4&nbsp;&nbsp;&nbsp; 49.999%&nbsp;&nbsp;&nbsp;&nbsp; dim0&nbsp;&nbsp;&nbsp; 0.6934&nbsp;&nbsp;← 로짓 간격과 같아진 지점</div>
      <div class="line">0.6&nbsp;&nbsp;&nbsp;&nbsp; 0.669%&nbsp;&nbsp;&nbsp;&nbsp; dim1&nbsp;&nbsp;&nbsp; 0.0407&nbsp;&nbsp;← 승자 교체</div>
      <div class="line">0.8&nbsp;&nbsp;&nbsp;&nbsp; 0.005%&nbsp;&nbsp;&nbsp;&nbsp; dim1&nbsp;&nbsp;&nbsp; 0.0010</div>
    </div>
    <p>
      전환이 <em>칼같이</em> 일어난다. 센터링 값이 로짓 간격(0.4)에 이르는 순간 50:50 이 되고,
      그 앞뒤로는 다시 뾰족해진다. 두 힘의 성격이 여기서 드러난다 —
      <strong>샤프닝은 분포를 뾰족하게, 센터링은 승자를 계속 갈아치우게</strong> 만든다.
      뾰족하되 한 곳에 고이지 않는 상태가 유지되는 이유다.
    </p>
    <div class="note">
      <b>둘 중 하나만 빼면 무너진다.</b> 논문은 이것을 실험으로 보인다 —
      센터링만 있으면 출력이 균등분포로 뭉개지고, 샤프닝만 있으면 한 차원으로 붕괴한다.
      <a href="normalization.html">정규화</a>가 층 사이의 분포를 붙잡는 것과 비슷하게,
      여기서는 <em>출력 분포의 모양 자체</em>를 두 힘의 균형으로 붙잡는다.
      <a href="knowledge-distillation.html">지식 증류</a>에서 온도가 "부드러운 정답"을 만드는 손잡이였다면,
      여기서는 온도가 <strong>붕괴를 막는 장치의 한쪽</strong>이 된다.
    </div>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 260" role="img" aria-label="DINO 의 학습 구조. 한 이미지에서 큰 크롭 둘과 작은 크롭 여덟을 잘라, 교사에는 큰 크롭만 학생에는 전부를 넣는다. 교사 출력에는 센터링과 샤프닝이 걸리고 교사 가중치는 학생의 지수이동평균으로 갱신된다. 손실은 학생 쪽으로만 흐른다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="20" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">한 장의 이미지에서 크롭 10 개</text>

            <rect x="24" y="34" width="86" height="86" fill="none" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <rect x="34" y="44" width="52" height="52" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <rect x="52" y="62" width="48" height="48" fill="none" stroke="var(--accent-line)" stroke-width="1.2"/>
            <g fill="none" stroke="var(--muted)" stroke-width="0.9" stroke-dasharray="2 2">
              <rect x="30" y="40" width="20" height="20"/>
              <rect x="60" y="38" width="20" height="20"/>
              <rect x="84" y="56" width="20" height="20"/>
              <rect x="38" y="82" width="20" height="20"/>
              <rect x="70" y="92" width="20" height="20"/>
            </g>
            <text x="24" y="136" font-size="8.5" fill="var(--accent)">global 2 × 224²</text>
            <text x="24" y="149" font-size="8.5" fill="var(--muted)">local 8 × 96²</text>

            <g stroke="var(--rule-strong)" stroke-width="1"><line x1="118" y1="60" x2="176" y2="60"/></g>
            <g stroke="var(--rule-strong)" stroke-width="1"><line x1="118" y1="150" x2="176" y2="150"/></g>
            <text x="126" y="54" font-size="8" fill="var(--ink-faint)">global 만</text>
            <text x="126" y="144" font-size="8" fill="var(--ink-faint)">전부</text>

            <rect x="180" y="36" width="104" height="48" rx="3" fill="var(--panel)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="196" y="58" font-size="10" fill="var(--accent)">교사 ViT</text>
            <text x="196" y="72" font-size="8" fill="var(--ink-faint)">stop-gradient</text>

            <rect x="180" y="126" width="104" height="48" rx="3" fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="196" y="148" font-size="10" fill="var(--ink)">학생 ViT</text>
            <text x="196" y="162" font-size="8" fill="var(--ink-faint)">역전파 대상</text>

            <g stroke="var(--accent-line)" stroke-width="1"><line x1="290" y1="60" x2="344" y2="60"/></g>
            <g stroke="var(--rule-strong)" stroke-width="1"><line x1="290" y1="150" x2="344" y2="150"/></g>

            <rect x="348" y="34" width="118" height="52" rx="3" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="360" y="52" font-size="8.5" fill="var(--accent)">− 센터링 c</text>
            <text x="360" y="66" font-size="8.5" fill="var(--accent)">softmax(· / 0.04)</text>
            <text x="360" y="79" font-size="8" fill="var(--ink-faint)">뾰족하되 고이지 않게</text>

            <rect x="348" y="128" width="118" height="44" rx="3" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="360" y="146" font-size="8.5" fill="var(--ink-soft)">softmax(· / 0.1)</text>
            <text x="360" y="160" font-size="8" fill="var(--ink-faint)">더 부드럽게</text>

            <g stroke="var(--rule-strong)" stroke-width="1"><line x1="472" y1="60" x2="512" y2="60"/></g>
            <g stroke="var(--rule-strong)" stroke-width="1"><line x1="472" y1="150" x2="512" y2="150"/></g>

            <text x="518" y="98" font-size="10" fill="var(--ink)">교차 엔트로피</text>
            <text x="518" y="112" font-size="8.5" fill="var(--ink-faint)">− Σ p&#8348; log p&#8347;</text>
            <g stroke="var(--rule-strong)" stroke-width="1"><line x1="512" y1="60" x2="512" y2="150"/></g>

            <path d="M 560 104 L 600 104 L 600 208 L 232 208 L 232 180" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="3 3"/>
            <text x="332" y="222" font-size="8.5" fill="var(--ink-faint)">그래디언트는 학생에게만</text>

            <path d="M 232 126 L 232 106 L 176 106 L 176 96 L 232 96 L 232 84" fill="none" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="24" y="192" font-size="8.5" fill="var(--accent)">교사 ← EMA(학생)</text>
            <text x="24" y="205" font-size="8" fill="var(--ink-faint)">λ : 0.996 → 1.0</text>
            <text x="24" y="228" font-size="8" fill="var(--warn)">교사는 학생의 과거 평균이다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        교사와 학생은 <strong>같은 구조</strong>이고, 교사는 학생의 이동평균일 뿐이다.
        서로 다른 것은 <em>보는 것</em>(교사는 큰 크롭만)과
        <em>출력에 걸리는 처리</em>(센터링 + 더 낮은 온도)뿐이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">03</span>멀티크롭 — "부분을 보고 전체를 맞혀라"</h2>
    <p>
      학습 신호가 어디서 나오는지가 아직 남았다. 답은 <strong>크롭을 비대칭으로 주는 것</strong>이다.
      한 장에서 큰 크롭 2 개(224×224)와 작은 크롭 8 개(96×96)를 자른 뒤,
      <em>교사에는 큰 크롭만, 학생에는 전부</em> 넣는다.
    </p>
    <p>
      그러면 학생은 <strong>물체의 일부만 보고 전체를 본 교사의 답을 맞혀야</strong> 한다.
      이것이 과제 정의다. 라벨은 없지만 요구는 분명하다 —
      <em>부분과 전체가 같은 표현으로 모이게 하라.</em>
    </p>
    <div class="note">
      <b>이 요구가 왜 특별한가.</b>
      <a href="metric-learning.html">메트릭 러닝</a>과 <a href="clip.html">CLIP</a> 은
      "같은 것"을 <strong>바깥에서</strong> 정해 준다 — 라벨이나 캡션이 짝을 알려 준다.
      멀티크롭은 그 짝을 <em>이미지 자르기만으로</em> 만든다.
      그래서 데이터 확보의 상한이 사라진다. 캡션 없는 사진이면 무엇이든 학습 재료가 된다.
    </div>
    <p>
      비용이 걱정될 수 있지만 작은 크롭은 생각보다 싸다.
      <a href="vision-transformer.html">ViT</a> 는 패치 개수의 제곱으로 어텐션 비용이 들기 때문이다.
    </p>
    <div class="eq">
      <span class="cap">크롭 하나의 비용 (패치 16 기준 · 직접 계산)</span>
      <div class="line">224 → 토큰 (224/16)² = <strong>196</strong>&nbsp;&nbsp;&nbsp; 어텐션 196² = 38,416</div>
      <div class="line">&nbsp;96 → 토큰 (96/16)²&nbsp; = <strong>&nbsp;36</strong>&nbsp;&nbsp;&nbsp; 어텐션 &nbsp;36² = &nbsp;1,296</div>
      <div class="line">&nbsp;</div>
      <div class="line">어텐션 비용 비 = 38,416 / 1,296 ≈ <strong>29.6배</strong></div>
      <div class="line">픽셀 합계&nbsp;&nbsp; 2·224² = 100,352&nbsp;&nbsp; 8·96² = 73,728&nbsp;&nbsp;→ 총 1.735배</div>
    </div>
    <p>
      작은 크롭 8 개를 다 합쳐도 어텐션 비용은 큰 크롭 <em>한 개의 4분의 1 남짓</em>이다.
      "뷰를 많이 만들면 비싸다"는 직관이 여기서는 어긋난다 —
      <strong>해상도를 낮추면 제곱으로 싸지기 때문</strong>이다.
      멀티크롭이 널리 퍼진 실용적인 이유가 이것이다.
    </p>
    <p>
      증강의 역할은 <a href="self-supervised-learning.html">자기지도 학습</a>에서 본 것과 같다.
      무엇을 <em>같다고</em> 묶느냐가 곧 과제 정의다.
      색 변형·블러·솔라리제이션을 같은 것으로 묶으면 그 변화에 불변한 표현이 나오고,
      그 선택이 다운스트림 성능을 가른다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>창발 — 아무도 시키지 않은 분할이 나타났다</h2>
    <p>
      논문 제목이 "Emerging Properties" 인 이유가 여기 있다.
      DINO 로 학습한 ViT 의 <strong>어텐션 맵을 그려 보니 물체의 경계가 그대로 드러났다</strong>.
      <a href="segmentation.html">분할</a> 라벨을 한 장도 준 적이 없는데도 그렇다.
    </p>
    <p>
      지도학습 ViT 나 합성곱망에서는 이만큼 뚜렷하게 나오지 않았다.
      "라벨을 맞히는" 과제는 <em>클래스를 가르는 데 필요한 만큼만</em> 보면 되지만,
      "부분과 전체를 일치시키는" 과제는 <strong>물체가 어디까지인지 알아야</strong> 풀리기 때문이라는 해석이 붙었다.
    </p>
    <p>
      정량 지표에서도 특이한 점이 나왔다. 특징을 그대로 두고
      <strong>k-NN 분류기</strong>만 붙여도 — 파인튜닝도, 선형 분류기 학습도 없이 —
      ImageNet 성능이 나온다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>모델</th><th>k-NN top-1</th><th>선형 프로브 top-1</th><th>메모</th></tr>
        </thead>
        <tbody>
          <tr><td>ViT-S/16</td><td>74.5%</td><td>77.0%</td><td>기준선</td></tr>
          <tr><td>ViT-S/8</td><td class="hi">78.3%</td><td>—</td><td>패치만 작게 했는데 k-NN 최고</td></tr>
          <tr><td>ViT-B/8</td><td>77.4%</td><td class="hi">80.1%</td><td>선형 프로브 최고</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      표를 세로로 읽으면 이상한 줄이 하나 보인다.
      <strong>k-NN 에서는 ViT-S/8(78.3%)이 더 큰 ViT-B/8(77.4%)을 앞선다.</strong>
      모델을 키우는 것보다 <em>패치를 잘게 자르는 것</em>이 더 크게 작용한 것이다.
      선형 프로브에서는 순서가 뒤집혀 ViT-B/8 이 80.1% 로 앞선다.
    </p>
    <div class="note">
      <b>두 지표가 다른 것을 잰다.</b>
      선형 프로브는 특징 위에 <em>새 층을 학습</em>하므로 표현이 조금 엉켜 있어도 펴 준다.
      k-NN 은 아무것도 학습하지 않고 <strong>거리만</strong> 쓴다 —
      <a href="metric-learning.html">메트릭 러닝</a>이 손실로 강제하던 성질,
      즉 "같은 것은 이미 가까이 있어야 한다"를 그대로 요구한다.
      k-NN 점수가 높다는 것은 그 성질이 <em>부수 효과로 생겼다</em>는 뜻이고,
      그래서 <a href="vector-search.html">벡터 검색</a>에 바로 얹을 수 있다는 실용적 함의가 따라온다.
      <a href="similarity-threshold.html">임계값</a>을 잡을 수 있는 점수 분포가 공짜로 나오는 셈이다.
    </div>
    <p>
      다만 창발한 어텐션 맵이 곧 분할기는 아니다.
      경계가 보인다는 것과 픽셀 단위로 정확하다는 것은 다른 이야기이고,
      실제 분할에는 여전히 디코더와 라벨이 붙는다.
      이 특징이 <a href="few-shot-learning.html">Few-Shot 인식</a>이나
      <a href="depth-estimation.html">깊이 추정</a>의 <em>출발점</em>으로 유용하다는 쪽이 정확한 서술이다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>DINOv2·v3 — 방법에서 기반 모델로</h2>
    <p>
      DINO 가 <em>방법</em>이었다면 DINOv2 부터는 <strong>내려받아 쓰는 물건</strong>이 됐다.
      바뀐 것은 손실이 아니라 <em>데이터와 규모</em> 쪽이다.
    </p>
    <p>
      DINOv2 는 웹에서 긁은 대규모 이미지 풀에서 자기지도 검색으로
      큐레이션된 씨앗 데이터셋과 비슷한 것들을 골라내고 중복을 제거해
      <strong>LVD-142M</strong>(1억 4,200만 장)을 만들었다.
      사람이 라벨을 붙이지는 않지만 <em>무엇을 학습에 넣을지는 자동으로 고른다</em> —
      <a href="curriculum-data-quality.html">데이터 품질</a>이 규모만큼 중요하다는 쪽에 선 설계다.
    </p>
    <div class="eq">
      <span class="cap">보고된 ImageNet-1k 선형 프로브</span>
      <div class="line">DINO&nbsp;&nbsp;&nbsp; ViT-B/8&nbsp;&nbsp;&nbsp; 80.1%</div>
      <div class="line">DINOv2&nbsp; ViT-g/14&nbsp;&nbsp; <strong>86.5%</strong>&nbsp;&nbsp; 직전 자기지도 대비 +4.2%p</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 약지도 학습된 OpenCLIP-G/14 와 대등한 수준으로 보고됐다</div>
    </div>
    <p>
      마지막 줄이 이 계열의 분기점이다.
      <a href="clip.html">CLIP</a> 계열은 <strong>캡션</strong>이라는 사람 언어를 감독 신호로 쓴다.
      DINOv2 는 그것 없이 대등한 수준에 올라섰다 —
      캡션이 없는 도메인(의료 영상·위성·산업 검사)에서 이 차이가 결정적이다.
    </p>
    <div class="note">
      <b>대신 잃은 것이 있다.</b> CLIP 은 텍스트와 같은 공간에 있으므로
      "고양이"라고 쓰면 바로 찾을 수 있다. DINOv2 에는 그 통로가 없다.
      <a href="vision-language-models.html">Vision-Language 모델</a>이
      DINOv2 계열 백본 위에 언어 쪽을 따로 붙이는 구성을 자주 쓰는 이유다.
      <em>특징을 잘 뽑는 것과 말로 지시받는 것은 별개의 능력</em>이다.
    </div>
    <p>
      규모를 키우자 예상 못 한 결함도 드러났다.
      <strong>레지스터</strong> 논문은 큰 ViT 의 특징 맵에 <em>노름이 비정상적으로 큰 토큰</em>이
      배경처럼 정보가 적은 자리에 나타난다고 보고했다.
      모델이 그 자리를 <strong>전역 계산용 메모장으로 전용</strong>한 것이다.
      분류에는 티가 안 나지만 <em>패치 단위로 특징을 쓰는 과제</em>에서는 그대로 잡음이 된다.
    </p>
    <p>
      처방은 허무할 만큼 간단했다 —
      입력 토큰 열에 <strong>내용이 없는 토큰 몇 개를 그냥 더해 준다</strong>.
      메모장이 따로 생기니 배경 패치를 빼앗지 않는다.
      DINOv2 에 레지스터를 붙인 가중치가 별도로 배포돼 있다.
    </p>
    <p>
      DINOv3(2025)는 같은 방향을 더 밀었다 —
      라벨 없는 이미지 17억 장으로 70억 파라미터 ViT 를 학습했다.
      여기서 새로 등장한 것이 <strong>Gram 앵커링</strong>이다.
      오래 학습하면 전역 성능은 유지되는데 <em>패치 단위 특징이 서서히 뭉개지는</em> 현상이 있었고,
      약 100만 반복 지점부터 <em>과거의 안정된 자기 자신</em>과 특징 간 Gram 행렬을 맞추게 해 이를 되돌렸다.
      분할·깊이처럼 조밀한 예측을 쓰는 과제에서 개선이 보고됐다.
    </p>
    <p>
      70억 파라미터를 그대로 쓰기는 어려우므로,
      <a href="knowledge-distillation.html">증류</a>로 작은 변형들을 함께 낸다.
      큰 모델을 <em>교사로 쓰는</em> 이 구도는 DINO 가 안에서 하던 자기증류와 형태가 같다 —
      다만 이번에는 <strong>교사가 진짜로 따로 있다</strong>.
    </p>
    <div class="note">
      <b>그래서 실무에서 이것을 어떻게 쓰는가.</b>
      대개 <strong>백본을 얼려 두고 머리만 학습</strong>한다.
      <a href="rf-detr.html">RF-DETR</a> 이 DINOv2 백본에 deformable 디코더를 올린 구성이 그 예이고,
      <a href="depth-estimation.html">깊이 추정</a>·<a href="segmentation.html">분할</a> 쪽도 같은 패턴을 쓴다.
      라벨이 적을 때 특히 유리하다 — 특징은 이미 배워 놓았고, 배울 것은 <em>과제별 머리</em>뿐이기 때문이다.
      다만 대형 ViT 백본은 무겁다.
      <a href="mobile-runtime.html">온디바이스 배포</a>에서는 증류된 작은 변형을 쓰거나
      <a href="efficient-backbone.html">경량 백본</a>으로 갈아타는 판단이 따로 필요하다.
    </div>
    <p>
      정리하면 이 계열이 바꾼 것은 하나다.
      <strong>"시각 특징을 학습하는 일"과 "과제를 푸는 일"이 분리됐다.</strong>
      <a href="scaling-laws.html">규모의 법칙</a>이 언어에서 밀어붙인 것을,
      시각에서는 라벨이라는 병목을 치우는 방식으로 밀어붙인 셈이다.
    </p>
  </section>
"""

READING = [
    "Caron et al., <em>Emerging Properties in Self-Supervised Vision Transformers</em> (arXiv:2104.14294) — DINO 원 논문. 센터링·샤프닝과 창발한 어텐션 맵.",
    "Oquab et al., <em>DINOv2: Learning Robust Visual Features without Supervision</em> (arXiv:2304.07193) — LVD-142M 큐레이션과 ViT-g/14 86.5%.",
    "Meta AI, <em>DINOv3</em> (arXiv:2508.10104) — 17억 장 · 70억 파라미터. Gram 앵커링으로 조밀 특징 열화를 되돌린다.",
    "Darcet et al., <em>Vision Transformers Need Registers</em> (arXiv:2309.16588, ICLR 2024) — 배경 패치가 전역 계산에 전용되는 문제와 레지스터 토큰.",
    "Grill et al., <em>Bootstrap Your Own Latent (BYOL)</em> (arXiv:2006.07733) — 음성 표본 없이 EMA 교사만으로 학습하는 계열의 출발점.",
    "Zhou et al., <em>iBOT: Image BERT Pre-Training with Online Tokenizer</em> (arXiv:2111.07832) — 패치 단위 목표를 더한 갈래. DINOv2 가 결합해 쓴다.",
]

write(
    "dino-self-distillation.html",
    title="DINO 와 자기증류 — 라벨 없이 배운 시각 특징",
    eyebrow="Vision · Self-Supervised Learning · 2021–2026",
    h1="DINO 와 자기증류",
    subtitle="라벨 없이 배운 특징이 어떻게 기반 모델이 됐나",
    dek=(
        "교사가 학생 자신의 과거 평균인데도 학습이 무너지지 않는다. "
        "센터링과 샤프닝이라는 <strong>반대 방향의 두 힘</strong>이 그것을 붙잡는다. "
        "그렇게 배운 특징에서는 아무도 시키지 않은 <em>물체 경계</em>가 어텐션 맵에 떠오르고, "
        "지금은 검출기와 깊이 추정이 그 위에 머리만 얹는다."
    ),
    spec=[
        ("무엇인가", "라벨 없는 자기증류"),
        ("붕괴 방지", "센터링 + 샤프닝"),
        ("과제 정의", "멀티크롭 — 부분↔전체"),
        ("창발", "어텐션에 물체 경계"),
        ("현재", "DINOv2·v3 — 고정 백본"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-12",
)

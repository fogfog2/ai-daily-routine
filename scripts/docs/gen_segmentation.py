#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f2", panel="#e6e5ea", ink="#17151c", **{
    "ink-soft": "#524e5b", "ink-faint": "#817d8b", "rule": "#d2d0d8",
    "rule-strong": "#aeabb6", "accent": "#5a3d8c", "accent-fill": "#e6dcf3",
    "accent-line": "#7d5fb0", "muted": "#84868e", "muted-fill": "#dfe0e4", "warn": "#a04a28",
})
DARK = dict(paper="#111017", panel="#191820", ink="#e7e5ee", **{
    "ink-soft": "#a5a2b0", "ink-faint": "#787484", "rule": "#222029", "rule-strong": "#383547",
    "accent": "#ab8ee8", "accent-fill": "#1e1836", "accent-line": "#7259b5",
    "muted": "#868892", "muted-fill": "#1a1a21", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>상자로는 부족한 순간</h2>
    <p>
      <a href="detection-lineage.html">검출</a>은 물체를 사각형으로 감싼다.
      빠르고 충분한 경우가 많지만, 상자가 답이 되지 않는 상황이 있다.
    </p>
    <ul>
      <li><strong>모양이 상자와 다르다.</strong> 도로·하늘·잔디 같은 것은 애초에 사각형이 아니다</li>
      <li><strong>면적이 필요하다.</strong> 결함 검사에서 "긁힘이 몇 mm²인가"는 상자로 못 잰다</li>
      <li><strong>경계가 곧 결과다.</strong> 배경 제거·합성에서는 픽셀 단위 경계가 산출물이다</li>
      <li><strong>상자가 겹친다.</strong> 겹쳐 놓인 물체는 상자만으로 어느 픽셀이 누구 것인지 알 수 없다</li>
    </ul>
    <p>
      <strong>분할</strong>은 이것을 픽셀 단위로 답한다.
      그런데 "픽셀마다 라벨을 붙인다"는 말은 생각보다 여러 뜻을 담고 있어,
      먼저 <em>무엇을 요구하는지</em>를 갈라야 한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>세 가지 분할</h2>
    <p>
      같은 "분할"이라도 요구가 다르다. 이 구분을 놓치면 데이터셋도 지표도 어긋난다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="시맨틱·인스턴스·판옵틱 분할의 차이. 시맨틱은 같은 종류를 한 덩어리로 묶어 개체를 구분하지 못하고, 인스턴스는 개체를 구분하지만 배경을 다루지 않으며, 판옵틱은 둘을 합쳐 모든 픽셀에 라벨과 개체 번호를 함께 준다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">같은 장면, 다른 요구</text>

            <g>
              <text x="30" y="40" font-size="8.5" fill="var(--ink-faint)">원본</text>
              <rect x="30" y="48" width="140" height="90" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <rect x="30" y="110" width="140" height="28" fill="var(--ink-soft)" opacity="0.18"/>
              <ellipse cx="70" cy="96" rx="16" ry="24" fill="var(--ink-soft)" opacity="0.4"/>
              <ellipse cx="104" cy="96" rx="16" ry="24" fill="var(--ink-soft)" opacity="0.4"/>
              <text x="100" y="156" text-anchor="middle" font-size="8" fill="var(--ink-faint)">사람 둘 + 도로</text>
            </g>

            <g>
              <text x="200" y="40" font-size="8.5" fill="var(--accent)">시맨틱</text>
              <rect x="200" y="48" width="140" height="90" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <rect x="200" y="110" width="140" height="28" fill="var(--accent)" opacity="0.25"/>
              <ellipse cx="240" cy="96" rx="16" ry="24" fill="var(--accent)" opacity="0.7"/>
              <ellipse cx="274" cy="96" rx="16" ry="24" fill="var(--accent)" opacity="0.7"/>
              <text x="200" y="156" font-size="8" fill="var(--ink-soft)">같은 색 = 같은 종류</text>
              <text x="200" y="169" font-size="8" fill="var(--warn)">✗ 둘을 구분 못 한다</text>
              <text x="200" y="182" font-size="8" fill="var(--accent)">✓ 도로 같은 배경도 다룬다</text>
            </g>

            <g>
              <text x="370" y="40" font-size="8.5" fill="var(--accent)">인스턴스</text>
              <rect x="370" y="48" width="140" height="90" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <ellipse cx="410" cy="96" rx="16" ry="24" fill="var(--accent)" opacity="0.75"/>
              <ellipse cx="444" cy="96" rx="16" ry="24" fill="var(--warn)" opacity="0.6"/>
              <text x="370" y="156" font-size="8" fill="var(--accent)">✓ 개체를 구분한다</text>
              <text x="370" y="169" font-size="8" fill="var(--warn)">✗ 도로·하늘은 대상 아님</text>
              <text x="370" y="182" font-size="8" fill="var(--ink-faint)">셀 수 있는 것만 (things)</text>
            </g>

            <g>
              <text x="540" y="40" font-size="8.5" fill="var(--accent)">판옵틱</text>
              <rect x="540" y="48" width="134" height="90" fill="var(--muted-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
              <rect x="540" y="110" width="134" height="28" fill="var(--accent)" opacity="0.25"/>
              <ellipse cx="578" cy="96" rx="16" ry="24" fill="var(--accent)" opacity="0.75"/>
              <ellipse cx="612" cy="96" rx="16" ry="24" fill="var(--warn)" opacity="0.6"/>
              <text x="540" y="156" font-size="8" fill="var(--accent)">✓ 둘 다 — 모든 픽셀에</text>
              <text x="540" y="169" font-size="8" fill="var(--ink-soft)">라벨 + 개체 번호</text>
              <text x="540" y="182" font-size="8" fill="var(--ink-faint)">겹침 없이 정확히 하나씩</text>
            </g>

            <line x1="24" y1="196" x2="674" y2="196" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="216" font-size="8.5" fill="var(--ink-soft)">things = 셀 수 있는 것(사람·차) · stuff = 셀 수 없는 것(도로·하늘) — <tspan fill="var(--accent)">이 구분이 과제를 가른다</tspan></text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>things</strong>와 <strong>stuff</strong>의 구분이 핵심이다.
        셀 수 있는 것은 개체를 나눠야 하고, 셀 수 없는 것은 나눌 개체가 없다.
        판옵틱은 이 둘을 하나의 출력으로 합쳐,
        <em>모든 픽셀이 정확히 하나의 라벨과 하나의 개체에 속하게</em> 한다.
      </figcaption>
    </figure>

    <p>
      지표도 갈린다. 시맨틱은 클래스별 <strong>mIoU</strong>(교집합/합집합의 평균)를 쓰고,
      인스턴스는 검출처럼 마스크 IoU 기반 <strong>AP</strong>를 쓴다.
      판옵틱은 둘을 합친 <strong>PQ</strong>를 쓰는데, 분할 품질과 인식 품질의 곱으로 정의된다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>해상도를 잃고 되찾기</h2>
    <p>
      분할의 구조적 난점은 <a href="cnn-basics.html">CNN 기초</a>에서 본 것 그대로다.
      <strong>넓게 보려면 해상도를 줄여야 하는데, 픽셀 단위 출력은 해상도가 필요하다.</strong>
    </p>
    <p>
      분류망을 그대로 쓰면 마지막에 <code>1/32</code> 해상도가 남는다.
      512×512 입력이 16×16이 되는 것이다. 여기서 픽셀 라벨을 만들려면 되살려야 한다.
    </p>
    <div class="eq">
      <span class="cap">해상도를 되찾는 세 방식</span>
      <div class="line">① <strong>인코더-디코더</strong>&nbsp;&nbsp;줄인 만큼 다시 키운다 (U-Net)</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;스킵 연결로 초반 층의 세부를 가져온다</div>
      <div class="line">&nbsp;</div>
      <div class="line">② <strong>dilated 합성곱</strong>&nbsp;커널에 구멍을 내 시야만 넓힌다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;해상도를 안 줄이고 수용 영역을 키운다 (DeepLab)</div>
      <div class="line">&nbsp;</div>
      <div class="line">③ <strong>다중 스케일 융합</strong>&nbsp;여러 해상도를 끝까지 함께 유지</div>
    </div>
    <p>
      <strong>U-Net</strong> 의 스킵 연결이 특히 중요하다.
      디코더가 위치 정보를 복원할 때, 인코더 초반의 고해상 특징을 그대로 이어 붙인다.
      깊은 층은 <em>무엇인지</em>를 알고 얕은 층은 <em>어디인지</em>를 아는데, 둘 다 필요하기 때문이다.
    </p>
    <div class="note">
      <b>U-Net 이 의료 영상에서 나온 것은 우연이 아니다.</b>
      데이터가 수백 장뿐인 상황을 전제로 설계됐다 —
      강한 증강, 대칭 구조, 적은 파라미터.
      지금은 <a href="diffusion-models.html">확산 모델</a>의 기본 백본으로 더 유명해졌는데,
      노이즈 제거도 <em>입력과 같은 크기의 출력</em>을 요구하는 과제라 구조가 그대로 맞았다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>개체를 나누는 두 갈래</h2>
    <p>
      인스턴스 분할은 <em>"어느 픽셀이 어느 개체인가"</em>를 답해야 한다.
      접근이 크게 둘로 갈렸다.
    </p>
    <p>
      <strong>검출 먼저(top-down).</strong> Mask R-CNN 이 대표다.
      상자를 찾은 뒤 각 상자 안에서 마스크를 예측한다.
      검출기 위에 마스크 분기를 하나 더 얹는 구조라 자연스럽고 성능도 좋다.
    </p>
    <p>
      결정적 세부는 <strong>RoIAlign</strong> 이었다.
      기존 RoIPool 은 관심 영역을 격자에 맞추느라 <em>반올림</em>을 했는데,
      분류에는 무해하던 이 오차가 <strong>픽셀 단위 마스크에서는 치명적</strong>이었다.
      쌍선형 보간으로 반올림을 없앤 것만으로 마스크 정확도가 크게 올랐다.
    </p>
    <p>
      <strong>상향식(bottom-up).</strong> 픽셀마다 임베딩을 뽑고 <em>같은 개체끼리 뭉치게</em> 학습한 뒤
      군집화로 개체를 나눈다. <a href="metric-learning.html">메트릭 러닝</a>의 발상을 픽셀에 적용한 것이다.
      상자에 의존하지 않아 겹침이나 특이한 모양에 유연하지만, 군집 단계가 불안정하기 쉽다.
    </p>
    <div class="note">
      <b>최근에는 세 과제가 하나로 합쳐지는 중이다.</b>
      마스크를 <em>질의(query)로 예측</em>하는 방식 — <a href="detr-lineage.html">DETR</a> 계열의 발상 —
      이 시맨틱·인스턴스·판옵틱을 <strong>같은 구조로</strong> 처리할 수 있음을 보였다.
      과제별로 다른 헤드를 붙이던 관행이 사라지는 흐름이다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>라벨 비용과 프롬프트 분할</h2>
    <p>
      분할의 실무적 최대 장벽은 모델이 아니라 <a href="data-pipeline.html"><strong>라벨</strong></a>이다.
      상자 하나는 클릭 두 번이면 되지만, 마스크 하나는 경계를 따라 그려야 한다.
      이미지 한 장에 수십 분이 걸리는 경우도 흔하다.
    </p>
    <p>
      그래서 우회로가 많이 연구됐다 —
      상자 라벨만으로 마스크를 학습하거나(weakly-supervised),
      점 몇 개만 찍거나, 합성 데이터를 쓰는 방식이다.
    </p>
    <p>
      <strong>SAM</strong>(Segment Anything)은 다른 각도에서 문제를 바꿨다.
      <em>무엇을 분할할지는 사용자가 지정하고, 모델은 경계만 잘 찾는</em> 구조다.
      점·상자·대략적 마스크를 프롬프트로 받아 그 영역의 마스크를 낸다.
    </p>
    <div class="eq">
      <span class="cap">SAM 이 바꾼 것 — 과제 정의 자체</span>
      <div class="line">기존:&nbsp; 이미지 → <strong>정해진 클래스</strong>의 마스크</div>
      <div class="line">SAM:&nbsp;&nbsp; 이미지 + <strong>프롬프트</strong> → 그 영역의 마스크</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 클래스 목록이 필요 없다 — 무엇이든 가리키면 잘라낸다</div>
      <div class="line">// 대신 '그것이 무엇인지'는 답하지 않는다</div>
    </div>
    <p>
      마지막 줄이 중요하다. SAM 은 <strong>분류하지 않는다</strong>.
      경계를 찾는 능력과 이름을 붙이는 능력을 분리한 것이고,
      그래서 <a href="clip.html">CLIP</a> 이나 <a href="vision-language-models.html">VLM</a> 과 조합해 쓰는 구성이 흔하다.
    </p>
    <div class="note">
      <b>실무에서는 라벨링 도구로 먼저 자리 잡았다.</b>
      사람이 점을 찍으면 SAM 이 마스크를 만들고, 사람은 확인만 한다.
      <em>모델을 대체하는 것이 아니라 라벨 비용을 낮추는</em> 쪽이
      가장 확실한 효용이었다 — 앞서 말한 최대 장벽이 그것이었기 때문이다.
    </div>
    <p>
      정리하면 분할은 <em>"어디까지가 그것인가"</em>를 묻는 과제다.
      검출이 위치를 대략 답한다면 분할은 경계를 정확히 답하고,
      그 정확도만큼 라벨 비용과 연산 비용을 치른다.
      <strong>상자로 충분한지 먼저 묻는 것</strong>이 실무의 첫 판단이 되는 이유다.
    </p>
  </section>
"""

READING = [
    "Long et al., <em>Fully Convolutional Networks for Semantic Segmentation</em> (arXiv:1411.4038) — 분류망을 분할로 바꾼 출발점.",
    "Ronneberger et al., <em>U-Net: Convolutional Networks for Biomedical Image Segmentation</em> (arXiv:1505.04597) — 스킵 연결 인코더-디코더.",
    "Chen et al., <em>Rethinking Atrous Convolution for Semantic Image Segmentation</em> (arXiv:1706.05587) — DeepLab. dilated 합성곱.",
    "He et al., <em>Mask R-CNN</em> (arXiv:1703.06870) — RoIAlign 과 마스크 분기.",
    "Kirillov et al., <em>Panoptic Segmentation</em> (arXiv:1801.00868) — things/stuff 통합과 PQ 지표.",
    "Kirillov et al., <em>Segment Anything</em> (arXiv:2304.02643) — 프롬프트 기반 분할.",
]

write(
    "segmentation.html",
    title="분할 — 어디까지가 그것인가",
    eyebrow="Vision · Dense Prediction · 2014–2026",
    h1="분할",
    subtitle="어디까지가 그것인가 — 시맨틱·인스턴스·판옵틱",
    dek=(
        "검출은 물체를 사각형으로 감싼다. 그런데 도로와 하늘은 사각형이 아니고, "
        "결함의 면적은 상자로 잴 수 없다. "
        "분할은 <strong>픽셀 단위로</strong> 답하지만, 그 말은 여러 뜻을 담고 있다 — "
        "종류만 가를 것인가, 개체를 나눌 것인가, 배경까지 포함할 것인가."
    ),
    spec=[
        ("시맨틱", "종류만 · 개체 구분 없음"),
        ("인스턴스", "개체 구분 · 배경 제외"),
        ("판옵틱", "둘 다 · 모든 픽셀"),
        ("구조적 난점", "해상도 vs 시야"),
        ("최대 장벽", "라벨 비용"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

#!/usr/bin/env python3
"""U-Net and encoder-decoder architecture note. Source: original papers below."""
from build import write

LIGHT = dict(paper="#f2f3ed", panel="#e7eee6", ink="#17231f", **{
    "ink-soft":"#465b50", "ink-faint":"#6b8073", "rule":"#cfdcd1",
    "rule-strong":"#a9c5ad", "accent":"#24725c", "accent-fill":"#dbede0",
    "accent-line":"#449f77", "muted":"#758c7a", "muted-fill":"#e0e9df", "warn":"#ae613c"
})
DARK = dict(paper="#101914", panel="#18251c", ink="#e5f1e8", **{
    "ink-soft":"#a3bca9", "ink-faint":"#758f7d", "rule":"#283b2e",
    "rule-strong":"#3d5945", "accent":"#91ddb0", "accent-fill":"#183e2b",
    "accent-line":"#5dbb83", "muted":"#809788", "muted-fill":"#1d2c21", "warn":"#e0a070"
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>분류에는 좋았던 축소가, 위치에는 손실이었다</h2>
    <p>이미지 분류는 한 장을 하나의 이름으로 바꾼다. 고양이가 오른쪽 위에 있든 왼쪽 아래에 있든 답은 같다. 그래서 <a href="cnn-basics.html">CNN</a>은 풀링과 스트라이드로 해상도를 낮추면서 넓은 영역을 바라본다. 깊은 층의 한 지점은 원본의 큰 구역을 대표한다. 이 과정에서 위치의 작은 차이는 점점 사라진다.</p>
    <p>하지만 <a href="segmentation.html">분할</a>의 출력은 이미지와 나란히 놓이는 픽셀 지도다. 각각의 픽셀이 어느 물체에 속하는지 결정해야 하므로 <strong>무엇인지 아는 것</strong>과 <strong>정확히 어디인지 아는 것</strong>이 동시에 필요하다. 저해상도에서만 예측한 뒤 크게 늘리면 넓은 문맥은 남지만 가는 경계가 흐려진다. 반대로 고해상도 특징만 쓰면 경계는 보이지만 물체 전체가 무엇인지 놓치기 쉽다.</p>
    <div class="note"><b>핵심 질문.</b> 모델이 전체 장면을 이해하기 위해 버렸던 위치 정보를, 마지막 픽셀 예측에 어떻게 다시 가져올 것인가? U-Net의 답은 축소하기 전의 특징을 대응되는 확대 단계로 직접 보내는 것이다.</div>
    <p>2015년 Ronneberger·Fischer·Brox의 U-Net은 생의학 영상 분할을 위해 이 문제를 정면으로 다뤘다. 논문은 적은 수의 주석 이미지에서 학습하기 위해 강한 데이터 증강도 함께 사용했다. 오늘날 여러 분야에서 쓰는 U-Net형 설계는 원본의 특정 층 수나 필터 수보다, <em>다중 해상도 인코더·디코더와 가로 연결</em>이라는 구성 원리를 가리킨다.</p>
  </section>

  <section>
    <h2><span class="n">02</span>왼쪽은 압축하고, 오른쪽은 복원한다</h2>
    <p>인코더는 입력을 여러 해상도로 낮춘다. 원본 크기가 H×W라면 한 단계마다 대략 H/2×W/2가 되며, 채널 수를 늘려 더 추상적인 특징을 담는다. 병목에서는 공간 해상도가 가장 낮지만 수용 영역이 넓다. 디코더는 다시 해상도를 키우며 각 위치의 출력을 만든다. 그림을 따라가면 U자 모양이 된다.</p>
    <figure>
      <svg viewBox="0 0 740 300" role="img" aria-label="인코더가 네 단계로 해상도를 줄이고 디코더가 늘리며, 같은 높이의 특징이 가로로 연결되는 U-Net 구조">
        <defs><marker id="unet-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10" fill="none" stroke="currentColor" stroke-width="1.5"/></marker></defs>
        <g fill="none" stroke="var(--accent-line)" stroke-width="2" marker-end="url(#unet-arr)">
          <path d="M110 68H188 M265 68V125H290 M360 163H405 M480 163V105H515 M587 68H650"/>
          <path d="M110 78H510" stroke-dasharray="5 5"/>
          <path d="M265 78H510" stroke-dasharray="5 5"/>
        </g>
        <g fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="2">
          <rect x="20" y="36" width="90" height="72" rx="8"/><rect x="188" y="36" width="78" height="72" rx="8"/>
          <rect x="290" y="125" width="70" height="76" rx="8"/><rect x="405" y="125" width="75" height="76" rx="8"/>
          <rect x="510" y="36" width="78" height="72" rx="8"/><rect x="650" y="36" width="70" height="72" rx="8"/>
        </g>
        <g fill="var(--ink)" font-family="sans-serif" font-size="14" text-anchor="middle">
          <text x="65" y="63">입력 특징</text><text x="65" y="84">H × W</text>
          <text x="227" y="63">압축</text><text x="227" y="84">H/2</text>
          <text x="325" y="157">병목</text><text x="325" y="181">H/4</text>
          <text x="442" y="157">확대</text><text x="442" y="181">H/2</text>
          <text x="549" y="63">결합</text><text x="549" y="84">H × W</text>
          <text x="685" y="63">픽셀별</text><text x="685" y="84">예측</text>
        </g>
        <text x="370" y="59" fill="var(--accent)" font-size="12" text-anchor="middle">같은 해상도의 특징을 전달</text>
        <text x="370" y="251" fill="var(--ink-soft)" font-size="12" text-anchor="middle">도식은 원리를 단순화했다. 원본 U-Net에는 더 많은 단계와 특징 채널이 있다.</text>
      </svg>
      <figcaption><span class="tag">STRUCTURE</span> 축소 경로의 특징이 확대 경로로 건너간다. 가로 연결은 서로 다른 해상도를 무작정 합치는 선이 아니라, 대응되는 해상도 사이의 정보 경로다.</figcaption>
    </figure>
    <p>원본 U-Net은 패딩 없는 합성곱을 썼다. 합성곱을 지날 때마다 특징 지도의 가로·세로가 줄어들어, 가로 연결 전에 인코더 특징을 잘라 디코더 특징과 맞췄다. 현대 구현은 같은 크기를 유지하는 패딩을 많이 사용하지만, <strong>대응 해상도를 정확히 맞춰 결합한다</strong>는 조건은 그대로다. 입력 크기가 2의 거듭제곱 배수가 아니라면 업샘플링 후 크기를 명시적으로 맞춰야 한다.</p>
  </section>

  <section>
    <h2><span class="n">03</span>가로 연결은 잔차 덧셈과 다르다</h2>
    <p>인코더의 i번째 해상도 특징을 Eᵢ, 그 아래 단계에서 올라온 디코더 특징을 Dᵢ₊₁이라 하자. 업샘플링 U 뒤에 두 특징을 채널 방향으로 잇고, 합성곱 블록 Fᵢ가 다음 디코더 특징을 만든다.</p>
    <div class="eq"><span class="cap">U-NET형 결합의 추상식</span>Dᵢ = Fᵢ( concat( Eᵢ, U(Dᵢ₊₁) ) )</div>
    <p>여기서 concat은 같은 위치의 값을 더하는 것이 아니라 채널 축에 나란히 붙이는 연산이다. H×W×C₁과 H×W×C₂를 붙이면 H×W×(C₁+C₂)가 된다. 디코더는 얕은 층이 보존한 경계와 깊은 층이 얻은 의미를 모두 입력받고, 다음 합성곱에서 무엇을 쓸지 학습한다. 실제 구현에서는 한쪽 특징을 더해 결합하거나 attention gate를 두는 변형도 있으므로 concat 자체를 모든 U-Net형 모델의 불변 조건으로 생각하면 안 된다.</p>
    <p><a href="residual-connections.html">잔차 연결</a>의 x+F(x)는 차원이 맞는 특징을 더해 항등 경로를 만든다. 그것의 주된 목적은 깊은 모델의 최적화를 돕는 것이다. U-Net의 가로 연결은 축소 경로의 <em>공간 세부</em>를 확대 경로로 가져오는 것이다. 둘 다 흔히 skip connection이라 불리지만, 전달하는 정보와 결합 방식이 다르다.</p>
    <div class="note"><b>왜 병목만으로 부족한가?</b> 다운샘플링은 많은 입력 위치를 하나로 모은다. 나중에 보간을 아무리 정교하게 해도 병목에 없는 세밀한 경계 정보를 단독으로 되살릴 수 없다. 가로 연결은 그 정보가 사라지기 전에 우회로를 만든다.</div>
    <p>그 대가도 있다. 학습 중에는 인코더의 고해상도 특징을 디코더가 사용할 때까지 보관해야 한다. 해상도가 큰 초반 특징은 메모리를 많이 차지하고, concat은 채널 폭을 늘린다. <a href="gradient-checkpointing.html">활성값 재계산</a>, 좁은 채널, 타일 단위 추론은 이 비용을 다루는 선택지지만 정확도·속도와 교환 관계가 있다.</p>
  </section>

  <section>
    <h2><span class="n">04</span>같은 골격, 다른 과제</h2>
    <p>원본의 목표는 픽셀별 의미 분할이었다. 디코더의 마지막 특징에 1×1 합성곱을 적용하면 위치마다 클래스 점수를 낼 수 있다. 하지만 복원된 고해상도 특징을 출력으로 쓰는 과제라면 같은 골격을 다른 방식으로 연결할 수 있다. <a href="denoising.html">노이즈 제거</a>와 <a href="deblurring.html">디블러링</a>은 깨끗한 픽셀 값을 예측하고, <a href="diffusion-models.html">확산 모델</a>의 많은 구현은 시간과 조건을 입력받아 노이즈 또는 다른 매개변수를 예측한다. 이때의 U-Net은 픽셀 분할기와 출력의 뜻이 다르다.</p>
    <p>다중 해상도 구조가 모두 같은 것은 아니다. <a href="detection-lineage.html">객체 검출</a>의 FPN도 깊은 특징을 위로 올려 얕은 특징과 결합한다. 그러나 FPN은 여러 해상도의 출력 특징 각각을 검출 헤드에 내어주는 것이 전형적이고, U-Net은 한 고해상도 예측 지도를 복원하는 흐름에서 출발했다. 둘 다 상향 경로와 횡단 연결을 쓰지만, 출력 위치와 목적이 다르다.</p>
    <div class="scroller"><table class="data"><thead><tr><th>구조</th><th>주로 보존하려는 것</th><th>전형적 출력</th></tr></thead><tbody><tr><td>U-Net</td><td>문맥 + 픽셀 위치</td><td>고해상도 픽셀 지도</td></tr><tr><td>FPN</td><td>여러 크기의 의미 특징</td><td>다중 해상도 특징 지도</td></tr><tr><td>잔차 블록</td><td>항등 경로와 기울기</td><td>같은 해상도의 특징</td></tr></tbody></table></div>
    <p>SegNet은 인코더의 풀링 인덱스를 디코더로 전달해 업샘플링 위치를 정하는 다른 해법이다. 저장하는 정보와 비용의 형태가 다르다. 결국 인코더·디코더라는 큰 이름보다 <strong>무슨 정보를 어디로 보내고 어떤 해상도에서 예측하는지</strong>를 보는 편이 구조를 더 정확히 이해하게 한다.</p>
  </section>

  <section>
    <h2><span class="n">05</span>어디에 두어야 하고, 어디서 실패하는가</h2>
    <p>U-Net은 출력이 공간적으로 정렬되어야 하고 넓은 문맥도 필요한 과제의 기본 출발점이다. 의료영상의 작은 경계, 위성영상의 영역, 사진 복원처럼 한 픽셀씩 위치가 중요한 작업이 그렇다. 같은 이유로 인코더가 너무 많이 줄이면 작은 대상은 병목에서 사라질 수 있다. 가로 연결이 있더라도 얕은 특징 자체가 약하거나 라벨이 거칠면 경계 품질을 보장하지 않는다.</p>
    <p>또 한 가지 실패는 학습과 추론의 경계 조건이다. 원본 U-Net 논문은 겹치는 타일과 거울 패딩을 사용해 큰 이미지의 가장자리도 예측했다. 타일별로 독립 처리하면 이음새가 보일 수 있고, 작은 입력에서는 병목이 충분한 문맥을 보지 못한다. 패딩 방식, 타일 중첩, 출력 잘라내기 규칙까지 함께 정해야 한다.</p>
    <p>모델을 읽을 때는 다음 네 질문으로 요약된다. <strong>몇 번 축소하는가?</strong> <strong>어느 해상도의 특징을 건너뛰는가?</strong> <strong>합치는 방법은 무엇인가?</strong> <strong>어느 해상도에서 손실을 계산하는가?</strong> 답이 같지 않다면 이름이 U-Net이라도 비용과 결과는 달라질 수 있다. 이 문서를 <a href="cnn-basics.html">CNN 기초</a> 다음, <a href="segmentation.html">분할</a>과 <a href="diffusion-models.html">확산 모델</a> 전에 읽으면 구조가 어떤 문제를 해결하는지 연결된다.</p>
  </section>
"""

READING = [
    '<a href="https://arxiv.org/abs/1505.04597">Ronneberger et al., <em>U-Net: Convolutional Networks for Biomedical Image Segmentation</em> (2015)</a> — 축소·확대 경로와 가로 연결의 원형.',
    '<a href="https://arxiv.org/abs/1511.00561">Badrinarayanan et al., <em>SegNet: A Deep Convolutional Encoder-Decoder Architecture for Image Segmentation</em> (2015)</a> — 풀링 인덱스로 위치를 복원하는 대안.',
    '<a href="https://arxiv.org/abs/1612.03144">Lin et al., <em>Feature Pyramid Networks for Object Detection</em> (2017)</a> — 다중 해상도를 검출 출력에 연결한 구조.',
    '<a href="https://arxiv.org/abs/1512.03385">He et al., <em>Deep Residual Learning for Image Recognition</em> (2015)</a> — 덧셈 잔차 경로와 U-Net 연결의 차이를 볼 기준.',
    '<a href="https://arxiv.org/abs/2006.11239">Ho et al., <em>Denoising Diffusion Probabilistic Models</em> (2020)</a> — U-Net형 예측기를 생성 모델에 사용한 사례.'
]

write(
    "u-net-encoder-decoder.html",
    title="U-Net과 인코더·디코더 — 작게 보고 다시 크게 그리다",
    eyebrow="Architecture · Vision · Encoder / Decoder",
    h1="U-Net과 인코더·디코더",
    subtitle="넓은 문맥과 정확한 위치를 동시에 쓰는 구조",
    dek="축소는 장면을 이해하게 하지만 픽셀의 위치를 흐린다. U-Net은 축소하기 전의 특징을 대응되는 확대 단계로 보내 두 정보를 다시 결합한다. 가로 연결이 무엇을 보존하고 얼마를 치르는지, 잔차 연결과 FPN은 왜 다른지 살핀다.",
    spec=[("과제", "픽셀마다 정확히 예측"),("핵심", "다중 해상도 + 가로 연결"),("결합", "원본은 채널 방향 이어붙이기"),("출력", "분할 · 복원 · 생성"),("비용", "고해상도 특징의 저장")],
    body=BODY,reading=READING,light=LIGHT,dark=DARK,date="2026-09-30"
)

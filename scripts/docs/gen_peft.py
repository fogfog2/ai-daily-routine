#!/usr/bin/env python3
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ee", panel="#e6e8e3", ink="#161913", **{
    "ink-soft": "#505548", "ink-faint": "#7e8475", "rule": "#d1d4cb",
    "rule-strong": "#adb1a5", "accent": "#3f6320", "accent-fill": "#e0ead4",
    "accent-line": "#628c3a", "muted": "#83878d", "muted-fill": "#dee0e3", "warn": "#a04d26",
})
DARK = dict(paper="#101210", panel="#181b16", ink="#e7eae2", **{
    "ink-soft": "#a5aa9c", "ink-faint": "#7a7f71", "rule": "#22261e", "rule-strong": "#383f30",
    "accent": "#8fc75e", "accent-fill": "#1a2612", "accent-line": "#5f8c3c",
    "muted": "#878d93", "muted-fill": "#1a1d20", "warn": "#e0895c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>PEFT의 핵심은 “얼마나 적게 학습하느냐”보다 “어디를 바꾸느냐”다</h2>
    <p>
      전체 파인튜닝은 모든 가중치를 갱신하지만, PEFT(parameter-efficient fine-tuning)는
      <strong>사전학습 백본을 대부분 얼리고 작은 보정 경로만 학습</strong>한다.
      <a href="lora.html">LoRA</a>가 가장 널리 알려졌지만, Adapter·Prefix·IA³처럼
      서로 다른 위치에 작은 자유도를 주는 방법도 같은 문제를 푼다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead><tr><th>방식</th><th>보정 위치</th><th>추론 경로</th><th>병합 가능성</th><th>CNN 적합성</th></tr></thead>
        <tbody>
          <tr><td>Serial Adapter</td><td>블록 뒤</td><td>새 연산 추가</td><td>대체로 어려움</td><td class="hi">가능</td></tr>
          <tr><td>Residual / Conv Adapter</td><td>특징맵 옆</td><td>병렬 분기</td><td>구조에 따라 다름</td><td class="hi">높음</td></tr>
          <tr><td>LoRA</td><td>가중치 업데이트</td><td>병렬 저랭크</td><td class="hi">가능</td><td class="hi">Conv2d에도 가능</td></tr>
          <tr><td>IA³ / Channel scale</td><td>활성 채널</td><td>곱셈</td><td>일부 흡수 가능</td><td class="hi">높음</td></tr>
          <tr><td>BN affine only</td><td>γ·β / 통계</td><td>기존 경로</td><td class="hi">추가 연산 없음</td><td class="hi">매우 높음</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      Transformer에서는 토큰 차원 <code>d</code>가 중심이지만 CNN에서는 특징이
      <code>B × C × H × W</code>다. 따라서 CNN adapter의 설계 포인트는
      <strong>채널을 얼마나 줄일지</strong>뿐 아니라 <strong>공간적 locality를 보존할지</strong>,
      그리고 <strong>새 분기가 실제 런타임에서 fusion 가능한지</strong>까지 포함한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>Transformer 쪽 Adapter·Prefix·LoRA·IA³</h2>
    <p>
      Houlsby Adapter는 블록 내부에 작은 bottleneck MLP를 직렬로 삽입한다.
      차원을 <code>d → r → d</code>로 줄였다가 복원하고 잔차로 더한다.
      작지만 순전파 경로가 길어져 원본 가중치만으로 되돌리기 어렵다는 것이 배포상의 약점이다.
    </p>
    <div class="eq">
      <span class="cap">Bottleneck adapter</span>
      <div class="line">h' = h + W<sub>up</sub> σ(W<sub>down</sub> h)</div>
      <div class="line">r ≪ d</div>
    </div>
    <p>
      Prefix/Prompt tuning은 가중치 대신 입력 또는 각 층의 K·V에 학습 가능한 벡터를 붙인다.
      IA³는 활성값에 채널별 스케일을 곱한다. 반면 LoRA는
      <code>ΔW = BA</code>를 병렬로 학습한 뒤 <code>W ← W + ΔW</code>로 합칠 수 있어,
      같은 PEFT라도 <strong>배포 시 추가 연산을 없앨 수 있다는 점</strong>이 강점이다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>CNN Residual Adapter — 1×1 Conv로 도메인별 샛길을 만든다</h2>
    <p>
      CNN에서 adapter를 체계적으로 쓴 초기 흐름은 Rebuffi 등의
      <strong>residual adapter</strong>다. 하나의 공유 CNN 백본은 그대로 두고,
      각 도메인마다 작은 <code>1×1 Conv</code> 계열 보정 모듈을 저장한다.
      2017년 NeurIPS와 2018년 CVPR 연구는 series·parallel adapter를 비교했고,
      <strong>얕은 층과 깊은 층 모두에 작은 적응이 필요할 수 있다</strong>고 보고했다.
    </p>
    <div class="eq">
      <span class="cap">CNN parallel residual adapter — conceptual form</span>
      <div class="line">y = F(x; W<sub>0</sub>) + A(x; θ)</div>
      <div class="line">A(x; θ) = Conv<sub>1×1</sub>(x)   또는   Conv<sub>up</sub>(σ(Conv<sub>down</sub>(x)))</div>
      <div class="line">W<sub>0</sub>: frozen backbone, θ: task/domain-specific parameters</div>
    </div>
    <p>
      <code>1×1 Conv</code>는 공간 크기 <code>H×W</code>를 건드리지 않고 채널만 섞는다.
      그래서 사전학습된 공간 필터는 보존하면서 도메인별 채널 조합만 바꾸기 좋다.
      여러 카메라·제품군·조명 도메인에 같은 백본을 쓰고
      <strong>adapter만 갈아끼우는 구조</strong>가 특히 잘 맞는다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 720 260" role="img" aria-label="CNN에서 frozen convolution backbone 옆에 residual adapter를 병렬로 두는 구조와 Conv2d LoRA를 가중치에 병합하는 구조를 비교한다.">
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
            </marker>
            <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
            </marker>
          </defs>
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="24" font-size="11" fill="var(--accent)">Residual / Conv Adapter</text>
            <rect x="26" y="46" width="120" height="44" rx="3" fill="var(--muted-fill)" stroke="var(--rule-strong)"/>
            <text x="86" y="72" text-anchor="middle" font-size="10" fill="var(--ink-soft)">Frozen Conv block</text>
            <path d="M150 68 L206 68" stroke="var(--muted)" stroke-width="1.4" marker-end="url(#arr)"/>
            <circle cx="226" cy="68" r="14" fill="none" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="226" y="73" text-anchor="middle" font-size="14" fill="var(--accent)">+</text>
            <path d="M86 92 L86 126 L202 126 L214 83" fill="none" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#arr2)"/>
            <rect x="98" y="108" width="92" height="36" rx="3" fill="var(--accent-fill)" stroke="var(--accent-line)"/>
            <text x="144" y="131" text-anchor="middle" font-size="9" fill="var(--accent)">1×1 / DW Adapter</text>
            <text x="26" y="174" font-size="9.5" fill="var(--ink-faint)">장점: task별 작은 모듈 교체</text>
            <text x="26" y="191" font-size="9.5" fill="var(--warn)">주의: 분기가 남으면 latency 증가</text>

            <line x1="350" y1="30" x2="350" y2="220" stroke="var(--rule)" />

            <text x="384" y="24" font-size="11" fill="var(--accent)">Conv2d LoRA</text>
            <rect x="384" y="46" width="122" height="44" rx="3" fill="var(--muted-fill)" stroke="var(--rule-strong)"/>
            <text x="445" y="72" text-anchor="middle" font-size="10" fill="var(--ink-soft)">W₀ frozen</text>
            <rect x="384" y="112" width="122" height="36" rx="3" fill="var(--accent-fill)" stroke="var(--accent-line)"/>
            <text x="445" y="135" text-anchor="middle" font-size="9.5" fill="var(--accent)">ΔW = B A</text>
            <path d="M510 68 L554 68" stroke="var(--muted)" stroke-width="1.4" marker-end="url(#arr)"/>
            <path d="M510 130 L552 82" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#arr2)"/>
            <circle cx="574" cy="68" r="14" fill="none" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="574" y="73" text-anchor="middle" font-size="14" fill="var(--accent)">+</text>
            <path d="M590 68 L650 68" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#arr2)"/>
            <text x="552" y="112" font-size="9.5" fill="var(--accent)">merge</text>
            <text x="384" y="174" font-size="9.5" fill="var(--ink-faint)">배포: W = W₀ + ΔW</text>
            <text x="384" y="191" font-size="9.5" fill="var(--accent)">추가 operator 없이 가능</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        CNN adapter는 특징맵을 보정하는 별도 분기로 남길 수도 있고,
        Conv2d 저랭크 업데이트처럼 최종 가중치에 합칠 수도 있다.
        <strong>학습 파라미터 수가 같아도 배포 지연은 전혀 다를 수 있다.</strong>
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>Conv-Adapter — locality를 보존하는 CNN 전용 PET</h2>
    <p>
      Chen 등의 <strong>Conv-Adapter</strong>는 CNN의 중간 특징맵을 직접 보정하도록 설계됐다.
      공개된 CVPR Workshops 2024 버전은 bottleneck 안에
      <strong>depth-wise separable convolution과 비선형성</strong>을 사용하고,
      CNN에서 공간적 locality를 유지하는 것이 중요하다고 분석한다.
    </p>
    <p>
      ResNet-50 BiT-M 기준 실험에서는 전체 파인튜닝 파라미터의 평균 약
      <strong>3.5%</strong>만 학습하면서 23개 교차 도메인 분류 과제에서
      full fine-tuning과 비슷하거나 더 나은 결과를 보고했다.
      분류뿐 아니라 검출·분할에도 확장해, 전체 파인튜닝 대비 학습 파라미터를 크게 줄이면서
      비슷한 성능을 유지하는 결과를 제시했다.
    </p>
    <div class="note">
      <b>CNN에서는 “MLP adapter를 그대로 옮기기”보다 공간 구조를 보존하는 쪽이 중요하다.</b>
      ViT/LLM adapter는 토큰 벡터를 다루지만 ConvNet의 중간 표현은 특징맵이다.
      작은 depthwise convolution이나 1×1 convolution을 쓰면
      채널 보정과 국소 공간 정보를 함께 다룰 수 있다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>Conv2d에 LoRA를 붙이는 법 — 커널을 저랭크 업데이트로 본다</h2>
    <p>
      LoRA는 선형층 전용 개념이 아니다. Conv2d 커널
      <code>W ∈ R<sup>Cout × Cin × k × k</sup></code>를
      <code>Cout × (Cin·k²)</code> 행렬로 보면 같은 저랭크 업데이트를 정의할 수 있다.
    </p>
    <div class="eq">
      <span class="cap">Conv2d low-rank update</span>
      <div class="line">W' = W<sub>0</sub> + ΔW</div>
      <div class="line">ΔW = B A,  rank(ΔW) ≤ r</div>
      <div class="line">A ∈ R<sup>r × (Cin·k²)</sup>,  B ∈ R<sup>Cout × r</sup></div>
    </div>
    <p>
      학습 중에는 저랭크 분기로 계산하고, 배포 전에 <code>ΔW</code>를 커널에 합치면
      런타임 그래프는 원래 Conv2d 하나로 돌아갈 수 있다.
      <strong>온디바이스에서는 이 mergeability가 매우 큰 장점</strong>이다.
    </p>
    <p>
      다만 depthwise convolution은 <code>groups=Cin</code>이라 일반 Conv처럼
      입력·출력 채널을 자유롭게 저랭크 결합하기 어렵다.
      MobileNet·RepViT처럼 depthwise/pointwise가 분리된 구조에서는
      <strong>1×1 pointwise Conv에 LoRA를 우선 적용</strong>하고,
      depthwise 쪽은 채널 스케일·작은 spatial adapter로 두는 편이 구현과 런타임 측면에서 단순하다.
    </p>
  </section>

  <section>
    <h2><span class="n">06</span>BN·채널 스케일만 학습하는 초경량 적응</h2>
    <p>
      CNN은 BatchNorm이라는 별도 적응 손잡이가 있다.
      백본 convolution은 모두 얼린 채 <strong>BN의 affine 파라미터 γ·β만 학습</strong>하거나,
      새 도메인의 running mean/variance만 다시 추정해도 도메인 이동을 어느 정도 흡수할 수 있다.
      이는 Transformer의 IA³나 FiLM식 channel modulation과 비슷한 관점이다.
    </p>
    <div class="eq">
      <span class="cap">Channel-wise modulation</span>
      <div class="line">y<sub>c</sub> = γ<sub>c</sub> · x<sub>c</sub> + β<sub>c</sub></div>
      <div class="line">학습량 O(C), 추가 spatial convolution 없음</div>
    </div>
    <p>
      비용은 매우 작지만 표현력도 제한된다.
      색감·밝기·센서 통계처럼 <em>feature distribution이 이동한 문제</em>에는 잘 맞고,
      객체 형태나 텍스처 규칙 자체가 크게 달라지는 경우에는 Conv Adapter나
      일부 block fine-tuning이 더 필요할 수 있다.
    </p>
  </section>

  <section>
    <h2><span class="n">07</span>온디바이스 배포와 양자화에서 무엇이 달라지는가</h2>
    <p>
      학습 파라미터가 3%라고 해서 추론 비용도 3%인 것은 아니다.
      Adapter가 별도 branch로 남으면 작은 Conv 하나라도
      <strong>메모리 왕복·kernel launch·그래프 분할</strong> 때문에 지연이 늘 수 있다.
      반대로 Conv-LoRA처럼 커널에 병합되면 추론 그래프를 원본과 동일하게 유지할 수 있다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead><tr><th>방법</th><th>학습 메모리</th><th>추론 추가 연산</th><th>온디바이스 권장 상황</th></tr></thead>
        <tbody>
          <tr><td>Conv-LoRA</td><td class="hi">낮음</td><td class="hi">병합 후 0</td><td>고정 task·NPU 그래프 유지</td></tr>
          <tr><td>Parallel Conv Adapter</td><td class="hi">낮음</td><td>분기 유지</td><td>여러 task adapter 교체가 중요</td></tr>
          <tr><td>BN / Channel scale</td><td class="hi">매우 낮음</td><td class="hi">거의 0</td><td>센서·조명 domain shift</td></tr>
          <tr><td>Partial fine-tuning</td><td>중간</td><td class="hi">0</td><td>domain gap이 크고 정확도가 우선</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      INT8 PTQ/QAT까지 한다면 adapter를 <strong>병합한 뒤 다시 calibration</strong>하는 편이 안전하다.
      합쳐진 <code>W'</code>의 채널별 범위가 원본 <code>W₀</code>와 달라질 수 있기 때문이다.
      특히 per-channel weight quantization을 쓰는 CNN에서는 저랭크 보정이 특정 출력 채널의
      dynamic range를 크게 바꾸지 않는지 확인해야 한다.
      자세한 양자화 흐름은 <a href="ondevice-quantization.html">온디바이스 양자화</a>와
      <a href="calibration.html">캘리브레이션</a> 문서로 이어진다.
    </p>
  </section>

  <section>
    <h2><span class="n">08</span>실무 선택 기준</h2>
    <ul>
      <li><strong>한 모델을 여러 제품·카메라 도메인에 공용으로 쓰려면</strong> — frozen CNN + domain-specific residual/Conv Adapter가 관리하기 쉽다.</li>
      <li><strong>NPU/DSP 그래프를 절대 바꾸고 싶지 않다면</strong> — Conv2d LoRA처럼 최종 커널에 병합 가능한 방법이 가장 안전하다.</li>
      <li><strong>조명·센서 통계 차이가 주원인이면</strong> — BN affine/statistics 또는 channel scale부터 시도한다.</li>
      <li><strong>MobileNet·RepViT 계열이면</strong> — depthwise보다 pointwise 1×1 Conv를 먼저 적응 대상으로 본다.</li>
      <li><strong>도메인 차이가 매우 크거나 새 저수준 특징이 필요하면</strong> — adapter만 고집하지 말고 early block 일부 또는 전체 fine-tuning과 비교한다.</li>
    </ul>
    <div class="note">
      <b>핵심 구분선은 “trainable parameter 비율”이 아니라 “배포할 때 남는 연산”이다.</b>
      서버 학습에서는 1~3% adapter가 충분히 작아 보이지만,
      모바일/NPU에서는 unsupported branch 하나가 전체 그래프를 CPU로 쪼갤 수 있다.
      따라서 정확도 표와 함께 <strong>merge 가능 여부·operator support·양자화 후 range</strong>를 같이 봐야 한다.
    </div>
  </section>
"""

READING = [
    "Rebuffi, Bilen &amp; Vedaldi, <em>Learning Multiple Visual Domains with Residual Adapters</em>, NeurIPS 2017 — CNN residual adapter와 Visual Decathlon.",
    "Rebuffi, Bilen &amp; Vedaldi, <em>Efficient Parametrization of Multi-Domain Deep Neural Networks</em>, CVPR 2018 — series/parallel adapter와 저랭크 adapter 압축.",
    "Guo et al., <em>SpotTune: Transfer Learning Through Adaptive Fine-Tuning</em>, CVPR 2019 — 입력별로 frozen/fine-tuned residual block을 선택.",
    "Chen et al., <em>Conv-Adapter: Exploring Parameter Efficient Transfer Learning for ConvNets</em>, CVPR Workshops 2024 (arXiv:2208.07463) — locality를 보존하는 ConvNet PET.",
    "Houlsby et al., <em>Parameter-Efficient Transfer Learning for NLP</em> (arXiv:1902.00751) — bottleneck Adapter.",
    "Hu et al., <em>LoRA: Low-Rank Adaptation of Large Language Models</em> (arXiv:2106.09685) — 저랭크 업데이트와 병합.",
    "Liu et al., <em>Few-Shot Parameter-Efficient Fine-Tuning is Better and Cheaper than In-Context Learning</em> (arXiv:2205.05638) — IA³.",
]

write(
    "peft-adapters.html",
    title="PEFT — Adapter·Prefix·IA³ + CNN Adapter",
    eyebrow="Adaptation · Parameter-Efficient Methods · CNN / Transformer · 2017–2026",
    h1="PEFT — Adapter와 CNN 적응",
    subtitle="Transformer의 LoRA에서 CNN의 Residual·Conv Adapter까지",
    dek=(
        "대부분을 얼리고 작은 부분만 학습한다는 목표는 같다. "
        "CNN에서는 여기에 <strong>공간 locality·1×1/depthwise convolution·BN·런타임 fusion</strong>이 더해진다. "
        "같은 3%의 학습 파라미터라도 병합 가능 여부에 따라 온디바이스 지연은 완전히 달라진다."
    ),
    spec=[
        ("CNN 원형", "Residual Adapter · 2017"),
        ("현대 ConvNet", "Conv-Adapter · locality"),
        ("병합형", "Conv2d LoRA"),
        ("초경량", "BN / channel scale"),
        ("배포 기준", "operator · INT8 range"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-09-03",
)

#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1f0", panel="#e5e8e6", ink="#13191a", **{
    "ink-soft": "#4b5658", "ink-faint": "#7a8586", "rule": "#ccd3d2",
    "rule-strong": "#a9b1b0", "accent": "#1d5f7a", "accent-fill": "#d8e8f0",
    "accent-line": "#3a86a5", "muted": "#83888c", "muted-fill": "#dee1e1", "warn": "#a04a28",
})
DARK = dict(paper="#0e1213", panel="#161b1c", ink="#e3eaea", **{
    "ink-soft": "#a0abac", "ink-faint": "#6f7a7b", "rule": "#202627", "rule-strong": "#364041",
    "accent": "#5cbadd", "accent-fill": "#0d2733", "accent-line": "#35809e",
    "muted": "#868c8e", "muted-fill": "#191e1f", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>정답이 하나가 아닌 문제</h2>
    <p>
      저해상 이미지를 크게 만드는 일은 <strong>정보를 되살리는 것이 아니라 지어내는 것</strong>이다.
      이 사실을 먼저 받아들여야 이 분야의 모든 설계 선택이 이해된다.
    </p>
    <p>
      4배 확대를 생각해 보자. 저해상 픽셀 하나가 고해상 픽셀 <code>4×4 = 16</code>개에 대응한다.
      우리가 아는 것은 그 16개의 <em>평균에 가까운 값</em> 하나뿐이고, 나머지는 알 수 없다.
    </p>
    <div class="eq">
      <span class="cap">배율이 올라갈수록 지어내야 할 양이 제곱으로 는다</span>
      <div class="line">배율 2 → 저해상 픽셀 1개당 미지수 <strong>4</strong>개</div>
      <div class="line">배율 3 → 미지수 <strong>9</strong>개</div>
      <div class="line">배율 4 → 미지수 <strong>16</strong>개</div>
      <div class="line">배율 8 → 미지수 <strong>64</strong>개</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 같은 저해상 입력을 만들어내는 고해상 이미지가 무수히 많다</div>
    </div>
    <p>
      수학에서는 이런 것을 <strong>불량조건 역문제</strong>라고 부른다.
      답이 여럿이므로 "무엇을 정답으로 볼 것인가"를 정해야 하고,
      그 선택이 곧 손실 함수가 된다. 그리고 다음 절에서 보듯,
      가장 자연스러워 보이는 선택이 가장 나쁜 결과를 낳는다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>MSE 를 쓰면 흐려진다 — 이유는 평균이다</h2>
    <p>
      복원 문제이니 픽셀 차이를 줄이는 것이 자연스러워 보인다.
      실제로 초기 연구들은 MSE 를 썼고, <a href="image-quality-metrics.html"><strong>PSNR</strong></a> 이라는 지표도 여기서 나온다.
    </p>
    <div class="eq">
      <span class="cap">PSNR — MSE 를 로그 스케일로 바꾼 것일 뿐이다</span>
      <div class="line">PSNR = 10 · log<sub>10</sub>( 255² / MSE )&nbsp;&nbsp;[dB]</div>
      <div class="line">&nbsp;</div>
      <div class="line">MSE 100.00 → 28.13 dB</div>
      <div class="line">MSE&nbsp; 25.00 → 34.15 dB</div>
      <div class="line">MSE&nbsp;&nbsp; 6.25 → 40.17 dB</div>
      <div class="line">// PSNR 을 올린다는 것은 MSE 를 줄인다는 것과 정확히 같은 말이다</div>
    </div>
    <p>
      문제는 <strong>MSE 를 최소화하는 답이 무엇인가</strong>에 있다.
      가능한 고해상 이미지가 여럿일 때, 제곱오차의 기댓값을 최소화하는 것은
      <em>그 답들의 평균</em>이다. 이것은 통계의 기본 성질이다.
    </p>
    <p>
      벽돌 벽을 4배 확대한다고 하자. 벽돌 무늬의 위상이 조금씩 다른 답이 여럿 가능한데,
      그것들을 평균 내면 <strong>무늬가 상쇄돼 밋밋한 회색면</strong>이 된다.
      MSE 기준으로는 이것이 최적해다. 어느 하나를 골라 틀리는 것보다,
      가운데를 취해 조금씩 틀리는 쪽이 제곱오차가 작기 때문이다.
    </p>
    <div class="note">
      <b>그래서 PSNR 이 높은데 눈에는 나쁜 결과가 나온다.</b>
      SRGAN 논문이 정확히 이 점을 지적한다 — MSE 를 최소화한 결과는
      <em>PSNR 은 높지만 고주파 세부가 없다</em>.
      이 관찰이 초해상 연구의 방향을 바꿨다.
      <a href="autoencoders-vae.html">VAE</a>의 출력이 흐린 것도,
      <a href="gan.html">GAN</a> 문서에서 MSE 를 쓰면 평균이 최적해가 된다고 한 것도 같은 이유다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>목표를 바꾼다 — 지각 손실과 적대 손실</h2>
    <p>
      해법은 <strong>"픽셀이 같아야 한다"는 요구를 버리는 것</strong>이다.
      대신 <em>"보기에 같아야 한다"</em>로 목표를 바꾼다.
    </p>
    <p>
      <strong>지각 손실</strong>은 픽셀이 아니라 <em>사전학습된 분류망의 특징 공간</em>에서 거리를 잰다.
      VGG 같은 망의 중간 층 활성값을 비교하는 것이다.
      벽돌 무늬의 위상이 달라도 "벽돌 질감"이라는 특징이 같으면 손실이 작다.
      평균을 낼 이유가 사라진다.
    </p>
    <div class="eq">
      <span class="cap">SRGAN 의 지각 손실 — 두 항의 합</span>
      <div class="line">L = L<sub>content</sub> + λ · L<sub>adversarial</sub></div>
      <div class="line">&nbsp;</div>
      <div class="line">L<sub>content</sub> = ‖ φ(I<sup>HR</sup>) − φ(G(I<sup>LR</sup>)) ‖²&nbsp;&nbsp;// φ = VGG 특징</div>
      <div class="line">L<sub>adversarial</sub> = −log D( G(I<sup>LR</sup>) )&nbsp;&nbsp;&nbsp;&nbsp;// 판별자를 속인다</div>
    </div>
    <p>
      <strong>적대 손실</strong>이 나머지를 맡는다.
      판별자는 "이것이 진짜 고해상 이미지인가"를 판정하고,
      생성자는 그것을 속이도록 학습한다.
      <a href="gan.html">GAN 문서</a>에서 본 <em>"손실 함수 자체를 학습시킨다"</em>는 발상이
      여기서 그대로 쓰인다 — 사람이 "그럴듯함"을 수식으로 적을 수 없으니 판별자에게 맡긴다.
    </p>
    <p>
      SRGAN 논문은 이 조합으로 <strong>4배 확대에서 사실적인 결과</strong>를 처음 얻었다고 보고했다.
      그리고 중요한 것은 평가 방식이었다 — <strong>MOS</strong>(사람이 매긴 주관 점수)에서
      원본에 가장 가까운 점수를 받았지만, <em>PSNR 은 오히려 낮았다</em>.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="초해상에서 손실 함수 선택이 결과를 가르는 도식. 하나의 저해상 입력에 대응하는 고해상 답이 여럿일 때, MSE는 그 답들의 평균을 택해 흐려지고, 지각 손실과 적대 손실은 그중 하나를 택해 선명하지만 원본과 다를 수 있다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="sr-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="sr-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--warn)"/>
              </marker>
            </defs>

            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">하나의 저해상 입력 → 가능한 고해상 답이 여럿</text>

            <rect x="26" y="86" width="52" height="52" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <g stroke="var(--rule-strong)" stroke-width="0.6" opacity="0.5">
              <line x1="52" y1="86" x2="52" y2="138"/><line x1="26" y1="112" x2="78" y2="112"/>
            </g>
            <text x="52" y="154" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">저해상</text>

            <path d="M84 100 L118 62" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <path d="M84 112 L118 112" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <path d="M84 124 L118 162" stroke="var(--rule-strong)" stroke-width="1.1"/>

            <g>
              <rect x="122" y="40" width="44" height="44" fill="var(--accent)" opacity="0.2" stroke="var(--accent-line)" stroke-width="1"/>
              <g stroke="var(--accent)" stroke-width="2" opacity="0.8">
                <line x1="128" y1="50" x2="160" y2="50"/><line x1="128" y1="62" x2="160" y2="62"/><line x1="128" y1="74" x2="160" y2="74"/>
              </g>
              <rect x="122" y="90" width="44" height="44" fill="var(--accent)" opacity="0.2" stroke="var(--accent-line)" stroke-width="1"/>
              <g stroke="var(--accent)" stroke-width="2" opacity="0.8">
                <line x1="128" y1="96" x2="160" y2="96"/><line x1="128" y1="108" x2="160" y2="108"/><line x1="128" y1="120" x2="160" y2="120"/>
              </g>
              <rect x="122" y="140" width="44" height="44" fill="var(--accent)" opacity="0.2" stroke="var(--accent-line)" stroke-width="1"/>
              <g stroke="var(--accent)" stroke-width="2" opacity="0.8">
                <line x1="128" y1="152" x2="160" y2="152"/><line x1="128" y1="164" x2="160" y2="164"/><line x1="128" y1="176" x2="160" y2="176"/>
              </g>
            </g>
            <text x="144" y="200" text-anchor="middle" font-size="8" fill="var(--ink-faint)">위상이 다른 답들</text>

            <line x1="212" y1="26" x2="212" y2="226" stroke="var(--rule)" stroke-width="1"/>

            <text x="238" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">MSE — 평균을 택한다</text>
            <path d="M184 112 L232 112" stroke="var(--warn)" stroke-width="1.4" marker-end="url(#sr-m)"/>

            <rect x="238" y="60" width="60" height="60" fill="var(--muted-fill)" stroke="var(--warn)" stroke-width="1.4"/>
            <rect x="244" y="66" width="48" height="48" fill="var(--warn)" opacity="0.14"/>
            <text x="268" y="136" text-anchor="middle" font-size="8.5" fill="var(--warn)">밋밋함</text>

            <text x="238" y="160" font-size="8.5" fill="var(--accent)">✓ PSNR 높음</text>
            <text x="238" y="174" font-size="8.5" fill="var(--warn)">✗ 고주파 세부 없음</text>
            <text x="238" y="194" font-size="8" fill="var(--ink-faint)">무늬가 상쇄돼 회색면이 된다.</text>
            <text x="238" y="207" font-size="8" fill="var(--ink-faint)">제곱오차 기준으로는 이게 최적해다.</text>

            <line x1="392" y1="26" x2="392" y2="226" stroke="var(--rule)" stroke-width="1"/>

            <text x="418" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">지각 + 적대 — 하나를 택한다</text>
            <path d="M184 124 L412 150" stroke="var(--accent-line)" stroke-width="1.4" fill="none" marker-end="url(#sr-a)"/>

            <rect x="418" y="60" width="60" height="60" fill="var(--muted-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <g stroke="var(--accent)" stroke-width="2.4" opacity="0.85">
              <line x1="426" y1="72" x2="470" y2="72"/><line x1="426" y1="88" x2="470" y2="88"/>
              <line x1="426" y1="104" x2="470" y2="104"/>
            </g>
            <text x="448" y="136" text-anchor="middle" font-size="8.5" fill="var(--accent)">선명함</text>

            <text x="418" y="160" font-size="8.5" fill="var(--warn)">✗ PSNR 낮음</text>
            <text x="418" y="174" font-size="8.5" fill="var(--accent)">✓ MOS(사람 평가) 높음</text>
            <text x="418" y="194" font-size="8" fill="var(--ink-faint)">지어낸 세부라 원본과 다를 수 있다.</text>
            <text x="418" y="207" font-size="8" fill="var(--ink-faint)">"그럴듯함"과 "정확함"은 다른 목표다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        이 그림이 초해상의 근본 긴장을 담고 있다.
        <strong>정확함과 그럴듯함은 같은 방향이 아니다.</strong>
        지표를 올릴수록 눈에는 나빠지는 구간이 있고, 그 반대도 있다.
        <em>왜곡-지각 트레이드오프</em>라고 부르며, 이론적으로도 둘을 동시에 최적화할 수 없음이 알려져 있다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>어디서 확대할 것인가 — sub-pixel 합성곱</h2>
    <p>
      구조 설계에서 의외로 중요한 선택이 하나 있다.
      <strong>언제 해상도를 키우는가</strong>다.
    </p>
    <p>
      초기 SRCNN 은 <em>먼저 bicubic 으로 확대한 뒤</em> 3층 합성곱으로 다듬었다.
      단순하지만 낭비가 크다 — 모든 연산이 <strong>확대된 큰 해상도</strong>에서 일어난다.
      4배 확대라면 연산량이 16배가 된다.
    </p>
    <p>
      <strong>ESPCN</strong> 이 이 순서를 뒤집었다.
      저해상 상태로 특징을 뽑고 <em>마지막에만</em> 확대한다.
      확대는 학습되는 층이 하는데, 방식이 재치 있다.
    </p>
    <div class="eq">
      <span class="cap">sub-pixel 합성곱 — 채널을 공간으로 편다</span>
      <div class="line">저해상 특징맵&nbsp; H × W × (C · r²)</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;↓ 픽셀 셔플 (재배열만 한다 — 곱셈 없음)</div>
      <div class="line">고해상 출력&nbsp;&nbsp;&nbsp; rH × rW × C</div>
      <div class="line">&nbsp;</div>
      <div class="line">r=2 → 채널 C·4,&nbsp;&nbsp; r=3 → C·9,&nbsp;&nbsp; r=4 → C·16</div>
    </div>
    <p>
      마지막 합성곱이 채널을 <code>r²</code>배로 만들고, 그 채널들을 공간 격자로 <em>재배열</em>한다.
      재배열은 메모리 이동일 뿐 연산이 아니므로 사실상 공짜다.
      무거운 특징 추출은 전부 작은 해상도에서 끝난다.
    </p>
    <div class="note">
      <b>이 선택이 온디바이스에서 결정적이다.</b> 연산량이 <code>r²</code>배 차이 나므로
      모바일에서는 사실상 유일한 선택지가 된다.
      <a href="quantization.html">양자화</a>나 <a href="pruning-sparsity.html">가지치기</a>가
      모델을 작게 만드는 것과 달리, 이것은 <em>같은 모델을 어디서 계산할지</em>를 바꾼 것이다.
      전치 합성곱(deconvolution)도 확대에 쓰이지만 격자 무늬 아티팩트가 생기기 쉬워
      sub-pixel 방식이 표준이 됐다.
    </div>
    <p>
      나머지 구조는 익숙한 것들의 조합이다 —
      <strong>잔차 블록</strong>을 깊게 쌓고(EDSR 은 배치 정규화를 <em>제거해</em> 성능을 올렸다),
      채널·공간 어텐션을 더하고(RCAN), 최근에는
      <a href="vision-transformer.html">트랜스포머</a> 블록을 쓴다(SwinIR).
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>실제 저해상은 bicubic 이 아니다</h2>
    <p>
      학계 벤치마크의 오랜 관행은 고해상 이미지를 <strong>bicubic 축소</strong>해서
      저해상 입력을 만드는 것이었다. 데이터를 무한히 만들 수 있어 편리하다.
    </p>
    <p>
      그런데 실제 사진의 열화는 그렇지 않다.
      센서 노이즈, 렌즈 흐림, 손떨림, JPEG 압축 아티팩트가 <em>뒤섞여</em> 있다.
      bicubic 으로만 학습한 모델은 실사진에서 <strong>노이즈까지 선명하게 확대</strong>해 버린다.
    </p>
    <p>
      <strong>Real-ESRGAN</strong> 계열은 열화를 <em>여러 단계로 무작위 조합</em>해 학습 데이터를 만든다 —
      (<a href="denoising.html">노이즈 제거</a>에서 다루는 실제 노이즈 모델과 같은 문제의식이다.)
      흐림 → 축소 → 노이즈 → JPEG 을 순서와 강도를 바꿔가며 반복 적용한다.
      실제 열화 과정을 모사하는 것이 아니라, <em>충분히 넓게 덮어</em> 강건하게 만드는 접근이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>세대</th><th>대표</th><th>핵심</th><th>대가</th></tr>
        </thead>
        <tbody>
          <tr><td>MSE 기반</td><td>SRCNN · EDSR</td><td>픽셀 오차 최소화</td><td class="hi">흐림</td></tr>
          <tr><td>적대 기반</td><td>SRGAN · ESRGAN</td><td class="hi">지각 + 적대 손실</td><td>없던 세부를 지어냄</td></tr>
          <tr><td>실사진 대응</td><td>Real-ESRGAN</td><td class="hi">복합 열화 모델링</td><td>학습 설계가 복잡</td></tr>
          <tr><td>확산 기반</td><td>StableSR · OSEDiff</td><td class="hi">생성 사전지식 활용</td><td>느리고 무겁다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      최근 흐름은 <a href="diffusion-models.html">확산 모델</a>을 쓰는 쪽이다.
      대규모로 학습된 생성 모델이 <em>"자연스러운 이미지란 무엇인가"</em>를 이미 알고 있으므로,
      그 사전지식을 복원에 빌려 쓴다. 품질은 좋지만 값이 비싸다 —
      SDXL 급 백본은 모바일에서 이미지 한 장에 수 초, 메모리 수백 MB를 쓴다는 보고가 있다.
    </p>
    <div class="note">
      <b>그래서 증류가 들어온다.</b> 2026년 NTIRE 의 모바일 초해상 챌린지에서
      상위 접근은 <em>한 단계 확산 교사를 작은 학생으로 증류</em>하고
      U-Net 을 가지치기한 뒤 경량 디코더를 붙이는 구성이었다.
      <a href="knowledge-distillation.html">지식 증류</a>와
      <a href="pruning-sparsity.html">가지치기</a>가 여기서 만난다.
      영상 쪽에서도 한 단계 확산으로 스트리밍 초해상을 노리는 연구가 나와 있다.
    </div>
    <p>
      마지막으로 실무에서 가장 중요한 점을 짚어 둔다.
      <strong>초해상은 지어내는 기술이므로 용도를 가린다.</strong>
      감상용 이미지라면 그럴듯한 세부가 이득이지만,
      번호판이나 얼굴처럼 <em>지어낸 세부가 판단 근거가 되는</em> 곳에서는 위험하다.
      모델이 만든 것은 "원래 있었을 법한 것"이지 "원래 있던 것"이 아니다.
      <a href="hallucination.html">환각</a> 문서에서 본 것과 같은 성질이 이미지에서 나타나는 셈이다.
    </p>
  </section>
"""

READING = [
    "Dong et al., <em>Image Super-Resolution Using Deep Convolutional Networks</em> (arXiv:1501.00092) — SRCNN. 딥러닝 초해상의 출발점.",
    "Ledig et al., <em>Photo-Realistic Single Image Super-Resolution Using a Generative Adversarial Network</em> (arXiv:1609.04802) — SRGAN. 지각 손실과 MOS·PSNR 괴리.",
    "Shi et al., <em>Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network</em> (arXiv:1609.05158) — ESPCN. 픽셀 셔플.",
    "Lim et al., <em>Enhanced Deep Residual Networks for Single Image Super-Resolution</em> (arXiv:1707.02921) — EDSR. 배치 정규화 제거의 근거.",
    "Wang et al., <em>Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data</em> (arXiv:2107.10833) — 복합 열화 모델링.",
    "Blau &amp; Michaeli, <em>The Perception-Distortion Tradeoff</em> (arXiv:1711.06077) — 왜곡과 지각을 동시에 최적화할 수 없음의 이론.",
    "Liang et al., <em>SwinIR: Image Restoration Using Swin Transformer</em> (arXiv:2108.10257) — 트랜스포머 기반 복원.",
]

write(
    "super-resolution.html",
    title="Super-Resolution — 없는 픽셀을 지어내는 일",
    eyebrow="Vision · Image Restoration · 2015–2026",
    h1="Super-Resolution",
    subtitle="없는 픽셀을 지어내는 일 — 정확함과 그럴듯함은 같은 방향이 아니다",
    dek=(
        "4배 확대에서 저해상 픽셀 하나는 고해상 픽셀 16개에 대응한다. "
        "같은 입력을 만드는 답이 무수히 많다는 뜻이다. "
        "픽셀 오차를 줄이면 <strong>그 답들의 평균</strong>이 최적해가 되어 흐려진다 — "
        "PSNR 은 높은데 눈에는 나쁜 결과가 여기서 나온다. "
        "그래서 목표를 \"픽셀이 같게\"에서 \"보기에 같게\"로 바꿔야 했다."
    ),
    spec=[
        ("문제 성격", "불량조건 역문제"),
        ("MSE 의 함정", "여러 답의 평균"),
        ("SRGAN", "지각 + 적대 손실"),
        ("확대 위치", "마지막 (sub-pixel)"),
        ("실사진 대응", "복합 열화 모델링"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

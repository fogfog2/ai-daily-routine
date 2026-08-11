#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff1f0", panel="#e4e8e6", ink="#131a18", **{
    "ink-soft": "#4a5754", "ink-faint": "#798683", "rule": "#ccd3d1",
    "rule-strong": "#a9b1af", "accent": "#1a5c56", "accent-fill": "#d6eae7",
    "accent-line": "#31877f", "muted": "#83888c", "muted-fill": "#dee1df", "warn": "#a34a28",
})
DARK = dict(paper="#0e1211", panel="#161b1a", ink="#e3eae8", **{
    "ink-soft": "#a0abaa", "ink-faint": "#6f7a78", "rule": "#202726", "rule-strong": "#36403e",
    "accent": "#4cc4b8", "accent-fill": "#0d2a27", "accent-line": "#2d8880",
    "muted": "#868d8b", "muted-fill": "#191f1e", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>시간 축이 빠져 있었다</h2>
    <p>
      지금까지 다룬 <a href="detection-lineage.html">검출</a>·<a href="segmentation.html">분할</a>·
      <a href="depth-estimation.html">깊이</a>는 전부 <strong>한 장의 이미지</strong>를 다룬다.
      동영상은 그 이미지들이 <em>이어져 있다</em>는 점이 다르다.
    </p>
    <p>
      프레임을 따로따로 처리하면 두 가지를 잃는다.
    </p>
    <ul>
      <li><strong>일관성</strong> — 같은 물체의 상자가 프레임마다 떨리고, 분할 경계가 흔들린다</li>
      <li><strong>움직임 정보</strong> — 정지 사진으로는 알 수 없는 것들. 걷는지 넘어지는지, 다가오는지 멀어지는지</li>
    </ul>
    <p>
      <strong>Optical flow</strong>는 이 시간 축을 다루는 가장 기본적인 도구다.
      두 프레임 사이에서 <em>각 픽셀이 어디로 이동했는지</em>를 답한다.
    </p>
    <div class="eq">
      <span class="cap">출력은 픽셀마다의 이동 벡터</span>
      <div class="line">flow(x, y) = (u, v)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 프레임 1의 (x,y) 픽셀이 프레임 2의 (x+u, y+v) 로 갔다</div>
      <div class="line">// 이미지 크기만큼의 <strong>조밀한</strong> 벡터장이 나온다</div>
    </div>
    <p>
      <a href="local-features.html">지역 특징 매칭</a>과 목적이 닮았지만 다르다.
      지역 특징은 <em>뽑을 만한 점 몇백 개</em>만 대응시키고,
      optical flow 는 <strong>모든 픽셀</strong>에 답한다.
      대신 프레임 간 변화가 작다고 가정한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>밝기가 변하지 않는다는 가정</h2>
    <p>
      고전적 방법의 출발점은 하나의 가정이다 —
      <strong>같은 점은 움직여도 밝기가 같다.</strong>
    </p>
    <div class="eq">
      <span class="cap">밝기 항상성과 그 결과</span>
      <div class="line">I(x, y, t) = I(x+u, y+v, t+1)</div>
      <div class="line">&nbsp;&nbsp;↓ 1차 테일러 전개</div>
      <div class="line"><strong>I<sub>x</sub>·u + I<sub>y</sub>·v + I<sub>t</sub> = 0</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 미지수는 2개(u, v), 식은 <strong>1개</strong> — 풀 수 없다</div>
    </div>
    <p>
      마지막 줄이 이 분야의 근본 문제다. <strong>조리개 문제</strong>라 부른다.
      픽셀 하나만 봐서는 움직임을 결정할 수 없다.
    </p>
    <p>
      직관적으로도 그렇다. 긴 직선이 지나가는 것을 <em>작은 구멍으로</em> 보면,
      선이 위로 가는지 대각선으로 가는지 구분할 수 없다 —
      <em>선을 따라가는 성분은 보이지 않기</em> 때문이다.
    </p>
    <div class="note">
      <b>그래서 가정을 하나 더 넣는다.</b> 고전 방법들은 <em>이웃 픽셀이 비슷하게 움직인다</em>고 가정한다.
      작은 창 안에서 같은 flow 를 공유한다고 보거나(Lucas-Kanade),
      전체적으로 매끄럽도록 벌점을 준다(Horn-Schunck).
      <strong>부족한 제약을 가정으로 메우는</strong> 것은
      <a href="super-resolution.html">초해상</a>·<a href="depth-estimation.html">깊이</a>와 같은 구조다.
    </div>
    <p>
      이 가정들이 깨지는 곳이 곧 실패 지점이다 —
      <em>조명이 바뀌면</em> 밝기 항상성이 깨지고,
      <em>물체 경계에서는</em> 이웃이 다르게 움직인다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>큰 움직임과 반복적 정제</h2>
    <p>
      테일러 전개는 <em>움직임이 작다</em>는 전제 위에 있다.
      빠르게 움직이는 물체는 몇십 픽셀을 건너뛰므로 이 근사가 무너진다.
    </p>
    <p>
      고전적 처방은 <strong>피라미드</strong>다.
      이미지를 축소하면 움직임도 함께 작아지므로,
      낮은 해상도에서 대략 잡고 올라가며 정밀화한다.
      <a href="cnn-basics.html">CNN 이 해상도를 줄여 시야를 넓히던 것</a>과 같은 발상이다.
    </p>
    <p>
      학습 기반으로 넘어와서도 이 골격은 유지됐고,
      <strong>RAFT</strong> 가 구조를 다시 정리했다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 234" role="img" aria-label="RAFT 구조. 두 프레임의 특징으로 모든 픽셀 쌍의 유사도를 담은 상관 볼륨을 만들고, 그것을 반복해서 조회하며 flow를 점진적으로 갱신한다. 조리개 문제 때문에 픽셀 하나만으로는 움직임을 결정할 수 없다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="of-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">조리개 문제 — 구멍으로 보면 알 수 없다</text>

            <rect x="24" y="30" width="80" height="60" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <line x1="34" y1="86" x2="94" y2="34" stroke="var(--ink-soft)" stroke-width="5" opacity="0.4"/>
            <circle cx="64" cy="60" r="18" fill="none" stroke="var(--warn)" stroke-width="1.6"/>
            <text x="64" y="106" text-anchor="middle" font-size="7.5" fill="var(--warn)">이 안만 보면</text>

            <path d="M112 60 L134 60" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#of-a)"/>

            <g>
              <circle cx="176" cy="60" r="18" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <line x1="162" y1="74" x2="190" y2="46" stroke="var(--ink-soft)" stroke-width="5" opacity="0.4"/>
              <path d="M176 60 L192 44" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#of-a)"/>
              <path d="M176 60 L190 60" stroke="var(--accent-line)" stroke-width="1.4" stroke-dasharray="2 2" marker-end="url(#of-a)"/>
              <path d="M176 60 L176 44" stroke="var(--accent-line)" stroke-width="1.4" stroke-dasharray="2 2" marker-end="url(#of-a)"/>
            </g>
            <text x="210" y="52" font-size="8" fill="var(--warn)">셋 다 같은 모습이다</text>
            <text x="210" y="66" font-size="8" fill="var(--ink-faint)">선을 따라가는 성분은 안 보인다</text>
            <text x="210" y="84" font-size="8" fill="var(--ink-soft)">→ 이웃을 함께 봐야 결정된다</text>

            <line x1="24" y1="118" x2="674" y2="118" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="138" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">RAFT — 상관 볼륨을 반복 조회</text>

            <rect x="24" y="150" width="56" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="52" y="167" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">프레임 1</text>
            <rect x="24" y="182" width="56" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="52" y="199" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">프레임 2</text>

            <path d="M86 178 L108 178" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#of-a)"/>

            <rect x="112" y="152" width="96" height="52" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="160" y="172" text-anchor="middle" font-size="8" fill="var(--accent)">상관 볼륨</text>
            <text x="160" y="186" text-anchor="middle" font-size="7" fill="var(--ink-soft)">모든 픽셀 쌍의 유사도</text>
            <text x="160" y="198" text-anchor="middle" font-size="7" fill="var(--ink-faint)">한 번만 만든다</text>

            <path d="M214 178 L236 178" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#of-a)"/>

            <rect x="240" y="152" width="96" height="52" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="288" y="172" text-anchor="middle" font-size="8" fill="var(--ink-soft)">GRU 갱신</text>
            <text x="288" y="186" text-anchor="middle" font-size="7" fill="var(--ink-faint)">현재 flow 로 조회 →</text>
            <text x="288" y="198" text-anchor="middle" font-size="7" fill="var(--ink-faint)">보정량 예측 → 더함</text>

            <path d="M288 148 C 288 130, 160 130, 160 148" stroke="var(--accent-line)" stroke-width="1.3" fill="none" marker-end="url(#of-a)"/>
            <text x="224" y="136" text-anchor="middle" font-size="7" fill="var(--accent)">반복 (수십 회)</text>

            <path d="M342 178 L364 178" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#of-a)"/>
            <rect x="368" y="164" width="60" height="28" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="398" y="182" text-anchor="middle" font-size="8" fill="var(--accent)">flow</text>

            <text x="446" y="162" font-size="8" fill="var(--ink-soft)">피라미드로 단계를 올라가는 대신</text>
            <text x="446" y="176" font-size="8" fill="var(--accent)">같은 해상도에서 반복 정제</text>
            <text x="446" y="194" font-size="8" fill="var(--ink-faint)">→ 큰 움직임과 작은 세부를</text>
            <text x="446" y="206" font-size="8" fill="var(--ink-faint)">&nbsp;&nbsp;&nbsp;한 구조로 다룬다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>상관 볼륨</strong>이 핵심이다 — 모든 픽셀 쌍의 유사도를 한 번 계산해 두고,
        <em>매 반복마다 현재 추정 위치를 조회</em>한다.
        피라미드를 오르내리며 단계마다 다른 것을 배우는 대신,
        <strong>하나의 갱신 규칙을 반복 적용</strong>하는 구조로 바꿨다.
      </figcaption>
    </figure>

    <p>
      반복 구조라 <em>정확도와 속도를 실행 시점에 조절</em>할 수 있다는 부수 효과도 있다.
      반복을 줄이면 빠르고 덜 정확하다.
      <a href="chain-of-thought.html">추론 시간 스케일링</a>과 같은 성격의 손잡이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>정답을 어디서 구하나</h2>
    <p>
      학습에는 <em>픽셀마다의 정확한 이동 벡터</em>가 필요한데,
      이것은 실사진에서 <strong>측정할 수가 없다</strong>.
      사람이 손으로 찍을 수도 없다.
    </p>
    <p>
      그래서 이 분야는 <strong>합성 데이터에 크게 의존</strong>한다.
      3D 렌더링으로 장면을 만들면 이동 벡터를 정확히 알 수 있다.
      의자를 무작위로 날리는 비현실적 데이터셋이 표준으로 쓰이기도 했다 —
      <em>사실적이지 않아도 움직임의 다양성이 있으면</em> 학습에 도움이 됐기 때문이다.
    </p>
    <div class="note">
      <b>합성-실제 격차가 이 분야의 상수다.</b>
      <a href="super-resolution.html">bicubic 축소로만 학습한 초해상</a>이
      실사진에서 실패하던 것과 같은 문제다.
      합성 데이터에는 <em>모션 블러·롤링 셔터·노이즈·압축 아티팩트</em>가 없다.
      그래서 합성으로 사전학습하고 소량의 실제 데이터로 미세조정하는 순서가 관행이 됐다.
    </div>
    <p>
      자기지도 접근도 있다. <a href="depth-estimation.html">깊이 추정</a>에서 본 것과 같은 발상으로,
      예측한 flow 로 <em>다음 프레임을 재구성</em>해 그 오차를 손실로 쓴다.
      정답이 필요 없지만 <strong>가려지는 영역</strong>에서 문제가 생긴다 —
      한 프레임에만 보이는 부분은 재구성할 수 없기 때문이다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>flow 를 쓸 것인가, 안 쓸 것인가</h2>
    <p>
      Optical flow 는 오랫동안 <strong>동영상 처리의 기본 부품</strong>이었다.
      프레임 정렬이 필요한 거의 모든 곳에 쓰인다.
    </p>
    <ul>
      <li><strong>동영상 초해상·denoise</strong> — 여러 프레임을 정렬해 합치면 <a href="denoising.html">1/√N 효과</a>를 얻는다</li>
      <li><strong>프레임 보간</strong> — 중간 프레임을 만들어 부드럽게</li>
      <li><strong>추적</strong> — 검출 결과를 프레임 간에 잇는다</li>
      <li><strong>손떨림 보정</strong> — 전역 움직임을 추정해 상쇄</li>
      <li><strong>행동 인식</strong> — 움직임 패턴 자체가 단서</li>
    </ul>
    <p>
      그런데 최근에는 <strong>flow 를 명시적으로 쓰지 않는</strong> 흐름도 뚜렷하다.
      동영상을 통째로 <a href="vision-transformer.html">트랜스포머</a>에 넣고
      <em>시간 축 어텐션으로 알아서 대응을 찾게</em> 하는 방식이다.
    </p>
    <div class="eq">
      <span class="cap">두 접근의 성격</span>
      <div class="line"><strong>명시적 flow</strong>&nbsp; 대응을 먼저 구하고 그것으로 정렬</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;해석 가능 · 오류가 눈에 보임 · 별도 모델 필요</div>
      <div class="line">&nbsp;</div>
      <div class="line"><strong>암묵적 처리</strong>&nbsp; 어텐션이 대응을 내부에서 처리</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;끝단 학습 · 데이터가 많이 필요 · 비싸다</div>
    </div>
    <p>
      <a href="nms.html">NMS</a>·<a href="detection-lineage.html">앵커</a>가 학습에 흡수된 것과 같은 흐름이다.
      다만 flow 는 <em>그 자체가 산출물인 경우</em>가 있어(로봇·측정)
      완전히 대체되지는 않는다.
    </p>
    <div class="note">
      <b>온디바이스에서는 여전히 비싸다.</b> 조밀한 flow 는
      <a href="segmentation.html">분할</a>처럼 <em>입력 크기의 출력</em>을 내는 데다,
      RAFT 계열은 상관 볼륨이 크고 반복까지 한다.
      그래서 모바일에서는 <em>희소 추적</em>으로 대체하거나,
      반복 횟수를 줄이거나, 해상도를 낮춰 쓰는 절충이 흔하다 —
      <a href="mobile-runtime.html">예산 안에서 무엇을 포기할지</a>의 문제로 돌아온다.
    </div>
    <p>
      정리하면 optical flow 는 <em>"시간 축의 대응 문제"</em>다.
      <a href="local-features.html">지역 특징</a>이 <strong>공간적 대응</strong>을 조밀하지 않게 푼다면,
      flow 는 <strong>시간적 대응</strong>을 조밀하게 푼다.
      둘 다 <em>"같은 것이 어디로 갔는가"</em>를 묻는다는 점에서 같은 계보에 있다.
    </p>
  </section>
"""

READING = [
    "Horn &amp; Schunck, <em>Determining Optical Flow</em> (Artificial Intelligence 1981) — 매끄러움 제약을 넣은 변분 접근.",
    "Lucas &amp; Kanade, <em>An Iterative Image Registration Technique</em> (IJCAI 1981) — 지역 창 가정.",
    "Dosovitskiy et al., <em>FlowNet: Learning Optical Flow with Convolutional Networks</em> (arXiv:1504.06852) — 학습 기반의 출발점과 합성 데이터.",
    "Sun et al., <em>PWC-Net: CNNs for Optical Flow Using Pyramid, Warping, and Cost Volume</em> (arXiv:1709.02371) — 피라미드·워핑·비용 볼륨의 정리.",
    "Teed &amp; Deng, <em>RAFT: Recurrent All-Pairs Field Transforms for Optical Flow</em> (arXiv:2003.12039) — 상관 볼륨과 반복 갱신.",
    "Butler et al., <em>A Naturalistic Open Source Movie for Optical Flow Evaluation</em> (ECCV 2012) — Sintel. 합성 벤치마크의 표준.",
]

write(
    "optical-flow.html",
    title="Optical Flow — 시간 축의 대응 문제",
    eyebrow="Vision · Motion · 1981–2026",
    h1="Optical Flow",
    subtitle="시간 축의 대응 문제 — 각 픽셀이 어디로 갔는가",
    dek=(
        "검출·분할·깊이는 전부 <em>한 장</em>을 다룬다. "
        "동영상은 프레임이 이어져 있다는 점이 다르고, 따로 처리하면 "
        "<strong>일관성과 움직임 정보</strong>를 잃는다. "
        "Optical flow 는 픽셀마다 이동 벡터를 답하는데, "
        "미지수 2개에 식이 1개라 <em>가정 없이는 풀리지 않는다</em>."
    ),
    spec=[
        ("출력", "픽셀마다 이동 벡터 (u,v)"),
        ("근본 난점", "조리개 문제"),
        ("고전 처방", "이웃이 비슷하게 움직인다"),
        ("RAFT", "상관 볼륨 + 반복 갱신"),
        ("정답 문제", "합성 데이터 의존"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

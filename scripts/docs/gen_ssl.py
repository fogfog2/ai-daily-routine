#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eef0f1", panel="#e4e7e8", ink="#12181a", **{
    "ink-soft": "#4a5558", "ink-faint": "#79848a", "rule": "#ccd2d4",
    "rule-strong": "#a9b0b3", "accent": "#0d6478", "accent-fill": "#d6e9ee",
    "accent-line": "#2b8ba3", "muted": "#83888c", "muted-fill": "#dee1e3", "warn": "#a04a26",
})
DARK = dict(paper="#0e1214", panel="#161b1d", ink="#e3eaec", **{
    "ink-soft": "#a0abaf", "ink-faint": "#6f7a7e", "rule": "#202728", "rule-strong": "#364042",
    "accent": "#4cc3dd", "accent-fill": "#0e2a31", "accent-line": "#2d8699",
    "muted": "#868d90", "muted-fill": "#191f20", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>라벨은 비싸고 데이터는 널려 있다</h2>
    <p>
      ImageNet은 사람이 손으로 붙인 라벨 120만 장으로 만들어졌다.
      그 규모를 100배로 늘리려면 비용도 100배가 된다. 어느 시점에서는 불가능해진다.
    </p>
    <p>
      반면 <strong>라벨 없는 데이터</strong>는 사실상 무한하다.
      인터넷의 이미지, 텍스트, 오디오는 계속 쌓인다.
      자기지도 학습의 물음은 여기서 나온다 — <em>데이터 자신에게서 정답을 만들어낼 수는 없나.</em>
    </p>
    <p>
      답은 <strong>데이터 일부를 가리고 그것을 맞히게 하는 것</strong>이다.
      가린 부분이 정답이므로 사람이 개입할 필요가 없다.
      이미 익숙한 예가 있다 — GPT의 다음 토큰 예측, BERT의 빈칸 채우기가 모두 자기지도다.
    </p>
    <div class="note">
      <b>언어에서는 쉽게 풀렸고 이미지에서는 오래 걸렸다.</b>
      텍스트는 이산적이라 "다음 단어를 맞혀라"가 자연스러운 분류 문제가 된다.
      이미지는 연속값이라 픽셀을 그대로 예측하면 <em>의미 없는 저수준 세부</em>에
      모델이 매달린다. 이미지용 자기지도가 다른 길을 찾아야 했던 이유다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>대조 학습 — 같은 것은 가깝게, 다른 것은 멀게</h2>
    <p>
      이미지 자기지도의 첫 돌파구는 <strong>대조 학습</strong>이었다.
      라벨이 있을 때 같은 일을 하는 것이 <a href="metric-learning.html">메트릭 러닝</a>이다.
      픽셀을 예측하는 대신 <em>표현 공간에서의 관계</em>를 학습한다.
    </p>
    <p>
      한 장의 이미지에 서로 다른 증강을 두 번 적용해 두 개의 뷰를 만든다.
      자르기, 색 변형, 흐리기 같은 것들이다. 이 둘은 <strong>같은 것</strong>(양성 쌍)이고,
      배치 안의 다른 이미지들은 <strong>다른 것</strong>(음성)이다.
    </p>
    <div class="eq">
      <span class="cap">InfoNCE — 분모에 음성들이 들어간다</span>
      <div class="line">L = − log&nbsp; exp( sim(z<sub>i</sub>, z<sub>j</sub>) / τ )&nbsp;/&nbsp;Σ<sub>k≠i</sub> exp( sim(z<sub>i</sub>, z<sub>k</sub>) / τ )</div>
      <div class="line">sim(a,b) = aᵀb / (‖a‖‖b‖)&nbsp;&nbsp;&nbsp;// 코사인 유사도</div>
      <div class="line">τ = 온도. 작을수록 어려운 음성에 민감해진다.</div>
    </div>
    <p>
      형태를 보면 <strong>분류 손실과 같다</strong>. "이 표현과 짝인 것은 배치 안의 어느 것인가"를
      맞히는 <code>N</code>지선다 문제다. 정답 라벨은 데이터 구성에서 자동으로 나온다.
    </p>
    <p>
      SimCLR가 밝힌 실무적 조건이 두 가지 있다.
      <strong>증강 조합이 결정적</strong>이라는 것(특히 자르기 + 색 왜곡),
      그리고 <strong>음성이 많아야 한다</strong>는 것이다. 배치 크기를 4096까지 키워야 성능이 났다.
      MoCo는 이 문제를 다르게 풀었다 — 이전 배치의 표현을 큐에 쌓아 두고 음성으로 재사용한다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>음성 없이도 되나 — 붕괴를 막는 비대칭</h2>
    <p>
      대조 학습에는 성가신 요구가 있다. <strong>음성 표본</strong>이 많이 필요하다.
      그런데 음성이라고 뽑은 것 중에 사실 같은 클래스인 이미지가 섞여 있으면
      "멀어져라"라는 잘못된 신호를 준다.
    </p>
    <p>
      그렇다면 양성 쌍만 쓰면 안 될까. 문제는 <strong>붕괴</strong>다.
      "같은 것은 가깝게"만 시키면 모델은 가장 쉬운 답을 찾는다 —
      <em>모든 입력에 같은 상수 벡터를 내놓는 것</em>이다. 손실은 0이 되고 표현은 무의미해진다.
      음성은 이 붕괴를 막는 척력 역할을 하고 있었다.
    </p>
    <p>
      BYOL과 SimSiam은 음성 없이 붕괴를 피하는 방법을 보였다.
      열쇠는 <strong>두 갈래를 비대칭으로 만드는 것</strong>이다.
    </p>
    <ul>
      <li><strong>예측기(predictor)</strong>를 한쪽에만 붙인다. 두 갈래가 대칭이 아니게 된다.</li>
      <li><strong>정지 그래디언트.</strong> 타깃 쪽으로는 그래디언트를 흘리지 않는다. 목표를 쫓아가되 목표가 함께 움직이지는 않게 한다.</li>
      <li>BYOL은 여기에 <strong>이동평균 타깃</strong>을 더한다. 타깃 네트워크는 온라인 네트워크의 지수이동평균으로 천천히 따라간다.</li>
    </ul>
    <div class="note">
      <b>SimSiam의 실험이 원인을 좁혔다.</b> 이동평균을 빼도 붕괴하지 않았다.
      즉 필수 요소는 <strong>정지 그래디언트</strong>였다.
      "쫓아갈 목표가 잠시 고정돼 있는 것"이 붕괴를 막는 핵심이라는 해석이다.
    </div>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="자기지도 학습의 세 갈래 비교. 대조 학습은 양성 쌍을 당기고 음성들을 밀어내며, BYOL 계열은 음성 없이 예측기와 정지 그래디언트라는 비대칭으로 붕괴를 막고, 마스크 재구성은 가려진 부분을 복원하게 한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ss-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="ss-x" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="24" y="20" font-size="10" letter-spacing="1.2" fill="var(--accent)">대조 — 밀고 당긴다</text>

            <circle cx="76" cy="72" r="9" fill="var(--accent)" opacity="0.8"/>
            <circle cx="104" cy="62" r="9" fill="var(--accent)" opacity="0.8"/>
            <path d="M88 70 L94 65" stroke="var(--accent-line)" stroke-width="2"/>
            <text x="90" y="48" text-anchor="middle" font-size="8" fill="var(--accent)">당김</text>

            <circle cx="44" cy="122" r="8" fill="var(--muted)" opacity="0.5"/>
            <circle cx="130" cy="126" r="8" fill="var(--muted)" opacity="0.5"/>
            <circle cx="88" cy="146" r="8" fill="var(--muted)" opacity="0.5"/>
            <path d="M74 84 L52 112" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#ss-x)"/>
            <path d="M108 74 L124 116" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#ss-x)"/>
            <path d="M92 82 L90 136" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#ss-x)"/>

            <text x="24" y="178" font-size="8.5" fill="var(--ink-faint)">음성이 많아야 한다</text>
            <text x="24" y="192" font-size="8.5" fill="var(--ink-faint)">(배치 4096 · 큐)</text>
            <text x="24" y="212" font-size="8.5" fill="var(--warn)">가짜 음성 문제</text>

            <line x1="176" y1="26" x2="176" y2="226" stroke="var(--rule)" stroke-width="1"/>

            <text x="200" y="20" font-size="10" letter-spacing="1.2" fill="var(--accent)">BYOL — 음성 없이</text>

            <rect x="200" y="40" width="52" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <text x="226" y="54" text-anchor="middle" font-size="8" fill="var(--ink-soft)">뷰 1</text>
            <rect x="336" y="40" width="52" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <text x="362" y="54" text-anchor="middle" font-size="8" fill="var(--ink-soft)">뷰 2</text>

            <rect x="200" y="72" width="52" height="22" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="226" y="87" text-anchor="middle" font-size="8" fill="var(--accent)">인코더</text>
            <rect x="336" y="72" width="52" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2" stroke-dasharray="3 2"/>
            <text x="362" y="87" text-anchor="middle" font-size="8" fill="var(--ink-faint)">타깃</text>

            <rect x="200" y="106" width="52" height="22" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="226" y="121" text-anchor="middle" font-size="8" fill="var(--accent)">예측기</text>

            <path d="M226 60 L226 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#ss-a)"/>
            <path d="M226 94 L226 104" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#ss-a)"/>
            <path d="M362 60 L362 70" stroke="var(--rule-strong)" stroke-width="1.2" marker-end="url(#ss-x)"/>
            <path d="M330 106 L258 116" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ss-a)"/>
            <text x="294" y="103" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">맞춘다</text>

            <line x1="344" y1="100" x2="380" y2="100" stroke="var(--warn)" stroke-width="1.6"/>
            <line x1="352" y1="94" x2="372" y2="106" stroke="var(--warn)" stroke-width="1.6"/>
            <text x="362" y="122" text-anchor="middle" font-size="7.5" fill="var(--warn)">정지 그래디언트</text>

            <text x="200" y="178" font-size="8.5" fill="var(--accent)">예측기 + 정지 그래디언트</text>
            <text x="200" y="192" font-size="8.5" fill="var(--ink-faint)">= 비대칭이 붕괴를 막는다</text>
            <text x="200" y="212" font-size="8.5" fill="var(--ink-faint)">음성 표본 불필요</text>

            <line x1="410" y1="26" x2="410" y2="226" stroke="var(--rule)" stroke-width="1"/>

            <text x="434" y="20" font-size="10" letter-spacing="1.2" fill="var(--accent)">MAE — 가리고 복원</text>

            <g>
              <rect x="434" y="40" width="88" height="88" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <g fill="var(--warn)" opacity="0.35">
                <rect x="434" y="40" width="22" height="22"/><rect x="478" y="40" width="22" height="22"/>
                <rect x="456" y="62" width="22" height="22"/><rect x="500" y="62" width="22" height="22"/>
                <rect x="434" y="84" width="22" height="22"/><rect x="478" y="84" width="22" height="22"/>
                <rect x="456" y="106" width="22" height="22"/><rect x="500" y="106" width="22" height="22"/>
                <rect x="500" y="40" width="22" height="22"/><rect x="434" y="106" width="22" height="22"/>
                <rect x="478" y="62" width="22" height="22"/><rect x="456" y="84" width="22" height="22"/>
              </g>
              <g stroke="var(--rule)" stroke-width="0.6" fill="none">
                <line x1="456" y1="40" x2="456" y2="128"/><line x1="478" y1="40" x2="478" y2="128"/><line x1="500" y1="40" x2="500" y2="128"/>
                <line x1="434" y1="62" x2="522" y2="62"/><line x1="434" y1="84" x2="522" y2="84"/><line x1="434" y1="106" x2="522" y2="106"/>
              </g>
            </g>
            <text x="478" y="146" text-anchor="middle" font-size="8.5" fill="var(--warn)">75% 가림</text>

            <path d="M534 84 L560 84" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ss-a)"/>
            <rect x="566" y="60" width="52" height="48" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="592" y="80" text-anchor="middle" font-size="8" fill="var(--accent)">복원</text>
            <text x="592" y="94" text-anchor="middle" font-size="8" fill="var(--accent)">픽셀</text>

            <text x="434" y="178" font-size="8.5" fill="var(--accent)">인코더는 보이는 25%만 본다</text>
            <text x="434" y="192" font-size="8.5" fill="var(--ink-faint)">→ 학습이 훨씬 빠르다</text>
            <text x="434" y="212" font-size="8.5" fill="var(--ink-faint)">증강 설계에 덜 의존한다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        세 갈래가 같은 목표를 다르게 이룬다.
        대조는 <em>밀고 당기며</em>, BYOL은 <em>비대칭</em>으로, MAE는 <em>가린 것을 복원</em>하며 표현을 만든다.
        공통점은 라벨이 데이터 구성 자체에서 나온다는 것이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>마스크 재구성 — 언어의 방식이 이미지로</h2>
    <p>
      ViT가 자리 잡으면서 이미지에도 BERT식 접근이 가능해졌다.
      이미지를 패치로 나누면 <em>토큰처럼</em> 다룰 수 있기 때문이다.
    </p>
    <p>
      <strong>MAE</strong>의 설계는 두 가지가 특이하다.
    </p>
    <ul>
      <li><strong>가림 비율이 극단적이다 — 75%.</strong> BERT의 15%와 대조된다. 이미지는 공간적 중복이 커서 조금만 가리면 이웃 픽셀에서 쉽게 유추된다. 어려운 과제로 만들려면 대부분을 지워야 한다.</li>
      <li><strong>인코더는 보이는 패치만 처리한다.</strong> 가려진 자리는 디코더 단계에서야 채워 넣는다. 인코더 입력이 1/4이므로 학습이 크게 빨라진다.</li>
    </ul>
    <p>
      대조 학습과 비교했을 때 실무적 장점이 분명하다.
      <strong>증강 설계에 덜 민감하고, 큰 배치가 필요 없다.</strong>
      대조 학습의 성능이 증강 조합에 크게 좌우되던 것과 대비된다.
    </p>
    <p>
      <a href="dino-self-distillation.html">DINO 계열</a>은 또 다른 갈래다. 자기증류 방식으로 학습하는데,
      학습된 ViT의 어텐션 맵이 <strong>물체 경계를 라벨 없이 잡아낸다</strong>는 관찰이 유명하다.
      DINOv2는 이 방향을 대규모로 밀어붙여, 파인튜닝 없이도 여러 다운스트림 과제에서
      쓸 수 있는 범용 시각 특징을 만들었다 — RF-DETR 같은 검출기가 그 백본을 쓴다.
      교사가 학생 자신의 이동평균인데도 왜 붕괴하지 않는지는
      <a href="dino-self-distillation.html">별도 문서</a>에서 계산과 함께 다룬다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>무엇을 배웠는가</h2>
    <p>
      자기지도 학습이 남긴 교훈은 <strong>과제 설계가 곧 능력을 정한다</strong>는 것이다.
      같은 데이터, 같은 구조라도 무엇을 맞히게 하느냐에 따라 전혀 다른 표현이 나온다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>계열</th><th>학습 신호</th><th>필요한 것</th><th>결과 표현의 성격</th></tr>
        </thead>
        <tbody>
          <tr><td>대조 (SimCLR·MoCo)</td><td>양성 당김 · 음성 밀어냄</td><td class="hi">큰 배치 · 증강 설계</td><td>선형 분류에 강함</td></tr>
          <tr><td>자기증류 (BYOL·DINO)</td><td>비대칭 예측</td><td>정지 그래디언트</td><td>의미 분할까지 잡음</td></tr>
          <tr><td>마스크 재구성 (MAE)</td><td>가린 부분 복원</td><td class="hi">적은 제약</td><td>파인튜닝에 강함</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 열의 차이가 실무적으로 중요하다.
      대조 학습 표현은 <em>선형 분류기만 얹어도</em> 잘 되지만 파인튜닝 여지가 적고,
      MAE 표현은 선형 평가에서는 약하지만 <em>전체를 파인튜닝하면</em> 더 높이 간다.
      "좋은 표현"이 하나가 아니라 <strong>쓰임에 따라 다르다</strong>는 뜻이다.
    </p>
    <p>
      더 큰 그림에서 보면, 자기지도는 현대 대형 모델의 전제 조건이었다.
      LLM의 사전학습이 자기지도이고, CLIP은 이미지-텍스트 쌍이라는
      <em>인터넷에 이미 존재하던 약한 라벨</em>을 이용했으며,
      <a href="dino-self-distillation.html">DINOv2</a> 같은 시각 기반 모델도 같은 계보다.
      <strong>라벨링 비용에서 풀려난 것이 규모를 키울 수 있게 한 조건</strong>이었다.
    </p>
  </section>
"""

READING = [
    "Chen et al., <em>A Simple Framework for Contrastive Learning of Visual Representations</em> (arXiv:2002.05709) — SimCLR. 증강 조합과 배치 크기의 영향.",
    "He et al., <em>Momentum Contrast for Unsupervised Visual Representation Learning</em> (arXiv:1911.05722) — MoCo. 큐로 음성을 재사용.",
    "Grill et al., <em>Bootstrap Your Own Latent</em> (arXiv:2006.07733) — BYOL. 음성 없는 학습.",
    "Chen &amp; He, <em>Exploring Simple Siamese Representation Learning</em> (arXiv:2011.10566) — SimSiam. 정지 그래디언트가 핵심임을 분리.",
    "He et al., <em>Masked Autoencoders Are Scalable Vision Learners</em> (arXiv:2111.06377) — MAE. 75% 가림과 비대칭 인코더·디코더.",
    "Oquab et al., <em>DINOv2: Learning Robust Visual Features without Supervision</em> (arXiv:2304.07193) — 범용 시각 특징.",
]

write(
    "self-supervised-learning.html",
    title="Self-Supervised Learning — 라벨 없이 배우는 법",
    eyebrow="Training · Representation Learning · 2018–2026",
    h1="Self-Supervised Learning",
    subtitle="라벨 없이 배우는 법 — 데이터 자신이 정답이 된다",
    dek=(
        "라벨은 비싸고 데이터는 널려 있다. "
        "자기지도는 <strong>데이터 일부를 가리고 그것을 맞히게</strong> 해 정답을 스스로 만든다. "
        "언어에서는 다음 토큰 예측으로 곧장 풀렸지만, "
        "이미지는 픽셀을 그대로 예측하면 저수준 세부에 매달려 다른 길이 필요했다."
    ),
    spec=[
        ("대조 학습", "InfoNCE · 큰 배치"),
        ("붕괴 방지", "정지 그래디언트"),
        ("MAE 가림 비율", "75%"),
        ("BERT 가림 비율", "15%"),
        ("의의", "규모 확장의 전제"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

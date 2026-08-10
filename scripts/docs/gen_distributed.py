#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff1f0", panel="#e5e8e6", ink="#131a17", **{
    "ink-soft": "#4b5652", "ink-faint": "#7a8582", "rule": "#ccd3d0",
    "rule-strong": "#a9b1ae", "accent": "#146046", "accent-fill": "#d6ebe2",
    "accent-line": "#2f8a68", "muted": "#83888c", "muted-fill": "#dee1e2", "warn": "#a0492a",
})
DARK = dict(paper="#0e1211", panel="#161b19", ink="#e3eae7", **{
    "ink-soft": "#a0aba7", "ink-faint": "#6f7a77", "rule": "#202726", "rule-strong": "#364040",
    "accent": "#4ec99a", "accent-fill": "#0e2a20", "accent-line": "#2f8a68",
    "muted": "#868d90", "muted-fill": "#191f1e", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>한 장에 무엇이 들어가야 하는가</h2>
    <p>
      학습에 필요한 메모리는 가중치만이 아니다.
      <a href="lora.html">LoRA 문서</a>에서 봤듯 7B 모델에 112GB가 든다.
      70B라면 <strong>1TB를 넘는다</strong>. 어떤 단일 GPU에도 들어가지 않는다.
    </p>
    <div class="eq">
      <span class="cap">파라미터 하나당 학습 메모리 (mixed precision + Adam)</span>
      <div class="line">bf16 가중치        2 바이트</div>
      <div class="line">bf16 그래디언트     2 바이트</div>
      <div class="line">fp32 마스터 사본    4 바이트</div>
      <div class="line">fp32 Adam m, v     8 바이트</div>
      <div class="line">─────────────────────────</div>
      <div class="line">합계              <strong>16 바이트 / 파라미터</strong>&nbsp;&nbsp;(활성값 별도)</div>
    </div>
    <p>
      그래서 쪼개야 한다. 문제는 <em>무엇을 쪼갤 것인가</em>다.
      선택지는 셋이고, 각각 <strong>통신 비용과 제약</strong>이 다르다 —
      데이터를 쪼개거나, 각 층의 행렬을 쪼개거나, 층 자체를 나눠 맡는다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>데이터 병렬 — 가장 쉽고 가장 낭비가 크다</h2>
    <p>
      <strong>데이터 병렬(DP)</strong>은 모든 GPU가 <em>모델 전체의 사본</em>을 갖고
      서로 다른 데이터 조각을 처리한다. 역전파가 끝나면 그래디언트를 평균 내어 맞춘다.
    </p>
    <div class="eq">
      <span class="cap">데이터 병렬의 한 스텝</span>
      <div class="line">각 GPU: 자기 미니배치로 순전파 · 역전파 → 그래디언트 g<sub>i</sub></div>
      <div class="line">전체:&nbsp;&nbsp;&nbsp; <strong>all-reduce</strong>( g<sub>1</sub>, …, g<sub>N</sub> ) → 평균 g</div>
      <div class="line">각 GPU: 같은 g 로 각자 옵티마이저 스텝 (결과가 동일)</div>
      <div class="line">// 통신량 = 파라미터 크기 · 스텝마다 1회</div>
    </div>
    <p>
      구현이 단순하고 확장이 잘 된다. 그런데 <strong>모델이 한 장에 들어가야</strong> 쓸 수 있고,
      더 나쁜 것은 <em>모든 GPU가 똑같은 옵티마이저 상태를 중복 보관</em>한다는 점이다.
      GPU 64장이면 같은 56GB짜리 Adam 상태가 64벌 있다.
    </p>
    <p>
      <strong>ZeRO</strong>가 이 낭비를 겨냥한다. 중복을 단계적으로 없앤다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>단계</th><th>분할 대상</th><th>메모리 (N=64 기준)</th><th>추가 통신</th></tr>
        </thead>
        <tbody>
          <tr><td>DP</td><td>없음</td><td>16 B/param</td><td>기준</td></tr>
          <tr><td>ZeRO-1</td><td>옵티마이저 상태</td><td>4 + 12/N</td><td>없음</td></tr>
          <tr><td>ZeRO-2</td><td>+ 그래디언트</td><td>2 + 14/N</td><td>없음</td></tr>
          <tr><td>ZeRO-3</td><td class="hi">+ 파라미터</td><td class="hi">16/N</td><td>약 1.5배</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      ZeRO-3에서는 각 GPU가 파라미터의 일부만 들고 있다가
      <em>필요한 층을 계산할 때만</em> 다른 GPU에서 모아 온다(all-gather).
      쓰고 나면 즉시 버린다. 메모리를 통신으로 산 것이다.
      PyTorch의 FSDP가 같은 원리를 구현한 것이다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>텐서 병렬 — 행렬 하나를 쪼갠다</h2>
    <p>
      <strong>텐서 병렬(TP)</strong>은 층 안의 행렬 연산 자체를 여러 GPU에 나눈다.
      한 GPU에 들어가지 않는 거대한 층을 다룰 수 있게 해준다.
    </p>
    <p>
      핵심은 <em>어느 방향으로 쪼개느냐</em>다. FFN의 두 행렬을 예로 보면 설계가 분명해진다.
    </p>
    <div class="eq">
      <span class="cap">FFN 을 쪼개는 표준 방식 (Megatron-LM)</span>
      <div class="line">Y = GeLU(X · A) · B</div>
      <div class="line">&nbsp;</div>
      <div class="line">A 는 <strong>열</strong>로 분할:&nbsp; A = [A₁ | A₂]</div>
      <div class="line">&nbsp;&nbsp;→ GeLU(X·A₁), GeLU(X·A₂) 를 <em>독립적으로</em> 계산 가능</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(GeLU 는 원소별 연산이라 통신이 필요 없다)</div>
      <div class="line">&nbsp;</div>
      <div class="line">B 는 <strong>행</strong>으로 분할:&nbsp; B = [B₁ ; B₂]</div>
      <div class="line">&nbsp;&nbsp;→ 각자 부분합을 만든 뒤 <strong>all-reduce</strong> 한 번으로 합산</div>
    </div>
    <p>
      열 분할 다음에 행 분할을 놓는 것이 요령이다.
      이렇게 짜면 <strong>FFN 블록 전체에서 통신이 단 한 번</strong>으로 끝난다.
      어텐션은 더 자연스럽다 — 헤드가 이미 독립적이므로 헤드 단위로 나누면 된다.
    </p>
    <div class="note">
      <b>TP는 노드 안에서만 쓴다.</b> 통신이 <em>층마다</em> 일어나고 양도 많다.
      NVLink로 묶인 같은 서버 안 8장 정도가 한계이고,
      느린 네트워크로 연결된 노드 사이에 TP를 걸면 통신이 계산을 압도한다.
      실무의 기본 배치는 <strong>노드 안 TP, 노드 간 DP/PP</strong>다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>파이프라인 병렬 — 층을 나눠 맡고, 거품과 싸운다</h2>
    <p>
      <strong>파이프라인 병렬(PP)</strong>은 층을 구간으로 나눠 GPU마다 맡긴다.
      GPU 0이 1~10층, GPU 1이 11~20층 하는 식이다.
      통신량이 가장 적다 — 구간 경계의 활성값만 넘기면 된다.
    </p>
    <p>
      대신 고유한 문제가 생긴다. <strong>파이프라인 거품</strong>이다.
      순진하게 구현하면 GPU 0이 일하는 동안 나머지는 놀고,
      GPU 1이 일할 때 GPU 0은 다음 배치를 기다린다.
    </p>
    <p>
      해법은 배치를 <strong>마이크로배치</strong>로 잘게 쪼개 흘려보내는 것이다.
      GPU 0이 첫 조각을 넘기면 곧바로 두 번째 조각을 시작한다.
      공장의 조립 라인과 같다.
    </p>
    <div class="eq">
      <span class="cap">거품 비율 — 마이크로배치를 늘릴수록 줄어든다</span>
      <div class="line">거품 ≈ (p − 1) / (m + p − 1)</div>
      <div class="line">p = 파이프라인 단계 수,&nbsp; m = 마이크로배치 수</div>
      <div class="line">&nbsp;</div>
      <div class="line">p=4, m=4&nbsp;&nbsp;→ 43% 낭비</div>
      <div class="line">p=4, m=32 →&nbsp; 8.6% 낭비</div>
    </div>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="파이프라인 병렬의 거품 도식. 마이크로배치가 적으면 각 GPU가 대기하는 빈 시간이 크게 생기고, 마이크로배치를 늘리면 작업이 촘촘히 채워져 대기 시간 비율이 줄어든다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">마이크로배치 4개 — 거품 43%</text>

            <g font-size="8" fill="var(--ink-faint)">
              <text x="26" y="42">GPU0</text><text x="26" y="60">GPU1</text>
              <text x="26" y="78">GPU2</text><text x="26" y="96">GPU3</text>
            </g>

            <g>
              <rect x="62" y="33" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="90" y="33" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="118" y="33" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="146" y="33" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="174" y="33" width="112" height="12" fill="var(--warn)" opacity="0.18"/>

              <rect x="62" y="51" width="26" height="12" fill="var(--warn)" opacity="0.18"/>
              <rect x="90" y="51" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="118" y="51" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="146" y="51" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="174" y="51" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="202" y="51" width="84" height="12" fill="var(--warn)" opacity="0.18"/>

              <rect x="62" y="69" width="54" height="12" fill="var(--warn)" opacity="0.18"/>
              <rect x="118" y="69" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="146" y="69" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="174" y="69" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="202" y="69" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="230" y="69" width="56" height="12" fill="var(--warn)" opacity="0.18"/>

              <rect x="62" y="87" width="82" height="12" fill="var(--warn)" opacity="0.18"/>
              <rect x="146" y="87" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="174" y="87" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="202" y="87" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="230" y="87" width="26" height="12" fill="var(--accent)" opacity="0.7"/>
              <rect x="258" y="87" width="28" height="12" fill="var(--warn)" opacity="0.18"/>
            </g>
            <text x="62" y="116" font-size="8" fill="var(--warn)">연한 칸이 노는 시간</text>

            <line x1="26" y1="130" x2="674" y2="130" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="152" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">마이크로배치 12개 — 거품 20%</text>

            <g font-size="8" fill="var(--ink-faint)">
              <text x="26" y="176">GPU0</text><text x="26" y="192">GPU1</text>
              <text x="26" y="208">GPU2</text><text x="26" y="224">GPU3</text>
            </g>

            <g>
              <rect x="62" y="167" width="204" height="11" fill="var(--accent)" opacity="0.7"/>
              <rect x="266" y="167" width="51" height="11" fill="var(--warn)" opacity="0.18"/>

              <rect x="62" y="183" width="17" height="11" fill="var(--warn)" opacity="0.18"/>
              <rect x="79" y="183" width="204" height="11" fill="var(--accent)" opacity="0.7"/>
              <rect x="283" y="183" width="34" height="11" fill="var(--warn)" opacity="0.18"/>

              <rect x="62" y="199" width="34" height="11" fill="var(--warn)" opacity="0.18"/>
              <rect x="96" y="199" width="204" height="11" fill="var(--accent)" opacity="0.7"/>
              <rect x="300" y="199" width="17" height="11" fill="var(--warn)" opacity="0.18"/>

              <rect x="62" y="215" width="51" height="11" fill="var(--warn)" opacity="0.18"/>
              <rect x="113" y="215" width="204" height="11" fill="var(--accent)" opacity="0.7"/>
            </g>

            <line x1="350" y1="26" x2="350" y2="222" stroke="var(--rule)" stroke-width="1"/>

            <text x="376" y="46" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">세 방식의 성격</text>

            <text x="376" y="72" font-size="9" fill="var(--accent)">DP — 데이터를 쪼갠다</text>
            <text x="376" y="86" font-size="8.5" fill="var(--ink-faint)">통신: 스텝당 1회 (파라미터 크기)</text>
            <text x="376" y="100" font-size="8.5" fill="var(--warn)">제약: 모델이 한 장에 들어가야 (ZeRO 로 해소)</text>

            <text x="376" y="126" font-size="9" fill="var(--accent)">TP — 행렬을 쪼갠다</text>
            <text x="376" y="140" font-size="8.5" fill="var(--ink-faint)">통신: 층마다 · 양이 많다</text>
            <text x="376" y="154" font-size="8.5" fill="var(--warn)">제약: 노드 안 (NVLink) 에서만</text>

            <text x="376" y="180" font-size="9" fill="var(--accent)">PP — 층을 나눠 맡는다</text>
            <text x="376" y="194" font-size="8.5" fill="var(--ink-faint)">통신: 경계 활성값만 · 가장 적다</text>
            <text x="376" y="208" font-size="8.5" fill="var(--warn)">제약: 거품 · 마이크로배치로 완화</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        세 방식은 <strong>경쟁 관계가 아니라 서로 다른 축</strong>이다.
        통신 특성이 다르므로, 실제 대형 학습은 셋을 겹쳐 쓴다 —
        보통 <em>노드 안은 TP, 노드 사이는 PP, 그 위에 DP</em>를 얹는 3D 병렬 구성이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>3D 병렬, 그리고 통신이 정하는 설계</h2>
    <p>
      실제 대형 모델 학습은 세 방식을 <strong>동시에</strong> 쓴다.
      GPU 1,024장으로 학습한다면 예컨대 이렇게 나눈다 —
      TP 8 (노드 안) × PP 8 (노드 사이) × DP 16.
      <code>8 × 8 × 16 = 1,024</code>다.
    </p>
    <p>
      배치를 정하는 원칙은 <strong>통신 대역폭의 계층</strong>이다.
      노드 안 NVLink는 빠르고, 노드 사이 InfiniBand는 그보다 느리다.
      통신이 잦은 TP를 빠른 링크에, 통신이 적은 PP/DP를 느린 링크에 배치한다.
    </p>
    <p>
      MoE 모델이 들어오면 축이 하나 더 붙는다 —
      <strong>전문가 병렬</strong>이다. 전문가들을 서로 다른 GPU에 두고,
      토큰을 담당 GPU로 보냈다 받는 all-to-all 통신이 층마다 두 번 일어난다.
      MoE의 이론적 FLOPs 절감이 그대로 속도로 이어지지 않는 이유가 여기 있다.
    </p>
    <div class="note">
      <b>메모리가 부족할 때의 순서.</b> 실무에서는 대개 이 순서로 손을 댄다 —
      ① <a href="gradient-checkpointing.html">그래디언트 체크포인팅</a>으로 활성값을 줄이고,
      ② ZeRO 단계를 올리고, ③ TP를 노드 안에서 켜고,
      ④ 그래도 안 되면 PP를 도입한다.
      뒤로 갈수록 구현 복잡도와 통신 비용이 커지기 때문이다.
    </div>
    <p>
      정리하면 분산 학습의 설계는 <em>연산을 어떻게 나눌 것인가</em>의 문제가 아니라
      <strong>통신을 어디에 놓을 것인가</strong>의 문제다.
      어떤 방식을 택하든 계산량의 총합은 같고, 갈리는 것은
      데이터가 얼마나 자주, 얼마나 멀리 오가느냐다.
      추론에서 병목이 메모리 대역폭이었듯, 학습에서는 네트워크가 그 자리를 차지한다.
    </p>
  </section>
"""

READING = [
    "Rajbhandari et al., <em>ZeRO: Memory Optimizations Toward Training Trillion Parameter Models</em> (arXiv:1910.02054) — 중복 제거의 3단계.",
    "Shoeybi et al., <em>Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism</em> (arXiv:1909.08053) — 열·행 분할 설계.",
    "Huang et al., <em>GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism</em> (arXiv:1811.06965) — 마이크로배치와 거품.",
    "Narayanan et al., <em>Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM</em> (arXiv:2104.04473) — 3D 병렬의 실측과 배치 원칙.",
    "Zhao et al., <em>PyTorch FSDP: Experiences on Scaling Fully Sharded Data Parallel</em> (arXiv:2304.11277) — ZeRO-3 계열의 실제 구현.",
]

write(
    "distributed-training.html",
    title="분산 학습 — DP·TP·PP",
    eyebrow="Infrastructure · Parallelism · 2019–2026",
    h1="분산 학습 — DP·TP·PP",
    subtitle="한 장에 담기지 않을 때 — 통신을 어디에 놓을 것인가",
    dek=(
        "학습에는 파라미터당 <strong>16바이트</strong>가 든다. 70B면 1TB를 넘는다. "
        "쪼개는 방법은 셋이다 — 데이터를 쪼개거나, 행렬을 쪼개거나, 층을 나눠 맡거나. "
        "계산량의 총합은 어느 쪽이든 같다. "
        "갈리는 것은 <strong>데이터가 얼마나 자주, 얼마나 멀리 오가느냐</strong>다."
    ),
    spec=[
        ("학습 메모리", "16 B / 파라미터"),
        ("DP", "통신 1회 · 중복 큼"),
        ("ZeRO-3", "16/N · 통신 1.5배"),
        ("TP", "층마다 통신 · 노드 안"),
        ("PP", "통신 최소 · 거품 발생"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

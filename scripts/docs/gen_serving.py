#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0ee", panel="#e6e6e2", ink="#171814", **{
    "ink-soft": "#515349", "ink-faint": "#808277", "rule": "#d2d3cc",
    "rule-strong": "#aeafa6", "accent": "#8a5310", "accent-fill": "#f2e4cb",
    "accent-line": "#b07a2c", "muted": "#83878d", "muted-fill": "#dee0e2", "warn": "#9c3a22",
})
DARK = dict(paper="#121210", panel="#1a1a16", ink="#e9e9e2", **{
    "ink-soft": "#a8a99b", "ink-faint": "#7d7e71", "rule": "#25251e", "rule-strong": "#3c3c30",
    "accent": "#e0a955", "accent-fill": "#302311", "accent-line": "#a87c34",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e07a5f",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>성격이 전혀 다른 두 단계</h2>
    <p>
      LLM 추론은 한 덩어리로 보이지만 <strong>두 개의 다른 작업</strong>으로 나뉜다.
      둘의 병목이 정반대라 서빙 설계 전체가 이 구분 위에 놓인다.
    </p>
    <div class="eq">
      <span class="cap">프리필과 디코드 — 같은 모델, 다른 성격</span>
      <div class="line"><strong>프리필</strong> (prefill) — 프롬프트 전체를 한 번에 처리</div>
      <div class="line">&nbsp;&nbsp;· 모든 토큰을 병렬로 계산 → 큰 행렬곱</div>
      <div class="line">&nbsp;&nbsp;· <strong>연산 병목</strong> (compute-bound) · GPU 를 꽉 채워 쓴다</div>
      <div class="line">&nbsp;</div>
      <div class="line"><strong>디코드</strong> (decode) — 토큰을 하나씩 생성</div>
      <div class="line">&nbsp;&nbsp;· 매번 가중치 전체와 KV 캐시를 읽어야 함</div>
      <div class="line">&nbsp;&nbsp;· <strong>메모리 대역폭 병목</strong> · GPU 연산 유닛이 논다</div>
    </div>
    <p>
      디코드가 문제다. 토큰 하나를 만들려고 <em>모델 가중치 전체</em>를 HBM에서 읽어 온다.
      7B 모델이 bf16이면 14GB를, 토큰 하나마다 읽는다.
      읽어 온 가중치로 하는 계산은 <strong>행렬-벡터 곱</strong> 하나뿐이다.
    </p>
    <p>
      결과적으로 GPU의 연산 능력은 대부분 놀고 있다.
      배치 크기 1로 서빙하면 GPU 사용률이 <em>한 자릿수 퍼센트</em>에 머무는 일이 흔하다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>배칭 — 읽어 온 가중치를 여러 번 쓴다</h2>
    <p>
      해법은 <strong>배칭</strong>이다. 여러 요청을 묶어 동시에 처리하면
      <em>한 번 읽어 온 가중치를 여러 요청에 재사용</em>할 수 있다.
      행렬-벡터 곱이 행렬-행렬 곱이 되고, 그제야 텐서 코어가 제대로 돈다.
    </p>
    <p>
      가중치 읽기 비용은 배치 크기와 무관하게 일정하므로,
      배치를 키울수록 <strong>토큰당 비용이 반비례해 내려간다</strong>.
      LLM 서빙에서 처리량을 올리는 가장 강력한 손잡이다.
    </p>
    <p>
      그런데 소박하게 구현하면 문제가 생긴다. <strong>정적 배칭</strong>은
      배치 안의 모든 요청이 끝날 때까지 기다린다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 232" role="img" aria-label="정적 배칭과 연속 배칭의 비교. 정적 배칭은 배치 안에서 먼저 끝난 요청의 자리가 가장 긴 요청이 끝날 때까지 비어 있지만, 연속 배칭은 끝난 자리에 대기 중인 새 요청을 즉시 채워 넣는다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">정적 배칭 — 다 끝날 때까지 기다린다</text>

            <g font-size="8" fill="var(--ink-faint)">
              <text x="26" y="40">요청A</text><text x="26" y="58">요청B</text>
              <text x="26" y="76">요청C</text><text x="26" y="94">요청D</text>
            </g>

            <g>
              <rect x="62" y="31" width="200" height="12" fill="var(--accent)" opacity="0.65"/>
              <rect x="62" y="49" width="70" height="12" fill="var(--accent)" opacity="0.65"/>
              <rect x="132" y="49" width="130" height="12" fill="var(--warn)" opacity="0.2"/>
              <rect x="62" y="67" width="110" height="12" fill="var(--accent)" opacity="0.65"/>
              <rect x="172" y="67" width="90" height="12" fill="var(--warn)" opacity="0.2"/>
              <rect x="62" y="85" width="46" height="12" fill="var(--accent)" opacity="0.65"/>
              <rect x="108" y="85" width="154" height="12" fill="var(--warn)" opacity="0.2"/>
            </g>
            <line x1="262" y1="26" x2="262" y2="102" stroke="var(--warn)" stroke-width="1.3" stroke-dasharray="3 2"/>
            <text x="268" y="70" font-size="8" fill="var(--warn)">여기서야</text>
            <text x="268" y="82" font-size="8" fill="var(--warn)">새 배치 시작</text>

            <text x="26" y="118" font-size="8.5" fill="var(--warn)">연한 칸 = 낭비되는 GPU 자리. 출력 길이가 제각각이라 손실이 크다.</text>

            <line x1="26" y1="132" x2="674" y2="132" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="154" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">연속 배칭 — 끝난 자리에 바로 채운다</text>

            <g font-size="8" fill="var(--ink-faint)">
              <text x="26" y="176">슬롯1</text><text x="26" y="194">슬롯2</text>
              <text x="26" y="212">슬롯3</text><text x="26" y="230">슬롯4</text>
            </g>

            <g>
              <rect x="62" y="167" width="200" height="12" fill="var(--accent)" opacity="0.65"/>
              <text x="162" y="176" text-anchor="middle" font-size="7" fill="var(--paper)">A</text>

              <rect x="62" y="185" width="70" height="12" fill="var(--accent)" opacity="0.65"/>
              <text x="97" y="194" text-anchor="middle" font-size="7" fill="var(--paper)">B</text>
              <rect x="132" y="185" width="88" height="12" fill="var(--accent-line)" opacity="0.75"/>
              <text x="176" y="194" text-anchor="middle" font-size="7" fill="var(--paper)">E</text>
              <rect x="220" y="185" width="42" height="12" fill="var(--accent)" opacity="0.5"/>
              <text x="241" y="194" text-anchor="middle" font-size="7" fill="var(--paper)">G</text>

              <rect x="62" y="203" width="110" height="12" fill="var(--accent)" opacity="0.65"/>
              <text x="117" y="212" text-anchor="middle" font-size="7" fill="var(--paper)">C</text>
              <rect x="172" y="203" width="90" height="12" fill="var(--accent-line)" opacity="0.75"/>
              <text x="217" y="212" text-anchor="middle" font-size="7" fill="var(--paper)">F</text>

              <rect x="62" y="221" width="46" height="12" fill="var(--accent)" opacity="0.65"/>
              <text x="85" y="230" text-anchor="middle" font-size="7" fill="var(--paper)">D</text>
              <rect x="108" y="221" width="154" height="12" fill="var(--accent-line)" opacity="0.75"/>
              <text x="185" y="230" text-anchor="middle" font-size="7" fill="var(--paper)">H</text>
            </g>

            <line x1="330" y1="146" x2="330" y2="226" stroke="var(--rule)" stroke-width="1"/>

            <text x="356" y="166" font-size="9" fill="var(--accent)">스케줄링 단위가 <tspan fill="var(--accent)">요청이 아니라 스텝</tspan>이다.</text>
            <text x="356" y="182" font-size="8.5" fill="var(--ink-faint)">매 토큰 생성 스텝마다 배치 구성을 다시 짠다.</text>
            <text x="356" y="198" font-size="8.5" fill="var(--ink-faint)">끝난 요청은 즉시 빠지고 대기열의 새 요청이 들어온다.</text>
            <text x="356" y="220" font-size="8.5" fill="var(--accent)">처리량이 수 배까지 오른다고 보고된다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        LLM 요청은 <strong>출력 길이를 미리 알 수 없다</strong>.
        어떤 답은 열 토큰, 어떤 답은 이천 토큰이다.
        정적 배칭이 크게 손해 보는 이유가 이것이고,
        <em>스텝 단위로 배치를 재구성하는</em> 연속 배칭이 표준이 된 이유이기도 하다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">03</span>메모리가 배치 크기를 정한다</h2>
    <p>
      배치를 키우고 싶어도 상한이 있다. <strong>KV 캐시</strong>다.
      요청마다 지금까지의 키·값을 들고 있어야 하고, 이것이 토큰마다 자란다.
    </p>
    <div class="eq">
      <span class="cap">KV 캐시 크기 — 요청 하나당</span>
      <div class="line">2 × 층 수 × KV 헤드 수 × 헤드 차원 × 시퀀스 길이 × 정밀도</div>
      <div class="line">// 2 는 키와 값</div>
      <div class="line">&nbsp;</div>
      <div class="line">가중치는 <strong>공유</strong>되지만 KV 캐시는 <strong>요청마다 별도</strong>다.</div>
      <div class="line">그래서 동시 요청 수의 실질적 상한을 KV 캐시가 정한다.</div>
    </div>
    <p>
      여기서 <a href="kv-cache-paged-attention.html">PagedAttention</a>이 등장한다.
      기존 방식은 요청마다 <em>최대 길이만큼</em> 연속된 메모리를 미리 잡아 두어
      실제 사용량과의 차이가 통째로 낭비됐다.
      OS의 페이징을 빌려 캐시를 작은 블록으로 쪼개 관리하면
      이 단편화가 거의 사라지고, 그만큼 배치를 키울 수 있다.
    </p>
    <p>
      모델 구조 쪽에서 줄이는 방법도 있다.
      <strong>GQA</strong>(grouped-query attention)는 여러 쿼리 헤드가
      KV 헤드를 공유하게 해 캐시 크기를 직접 줄인다.
      최근 모델 대부분이 채택한 이유가 서빙 비용이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>지연과 처리량은 맞바꾸는 관계다</h2>
    <p>
      서빙 성능은 하나의 숫자로 말할 수 없다.
      최소한 세 가지를 구분해야 하고, 서로 충돌한다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>지표</th><th>뜻</th><th>체감</th><th>배치를 키우면</th></tr>
        </thead>
        <tbody>
          <tr><td>TTFT</td><td>첫 토큰까지의 시간</td><td>반응이 시작되는 속도</td><td class="hi">나빠진다</td></tr>
          <tr><td>TPOT</td><td>토큰당 생성 시간</td><td>읽는 속도를 따라오는가</td><td>나빠진다</td></tr>
          <tr><td>처리량</td><td>초당 총 토큰 수</td><td>운영 비용</td><td class="hi">좋아진다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      대화형 서비스는 TTFT가 중요하다. 사용자가 기다리는 시간이기 때문이다.
      반면 배치 작업(문서 대량 요약 등)은 TTFT가 몇 초여도 상관없고
      <strong>처리량만 높으면 된다</strong>. 같은 하드웨어라도 목표에 따라 설정이 달라진다.
    </p>
    <div class="note">
      <b>프리필이 디코드를 방해한다.</b> 긴 프롬프트의 프리필이 들어오면
      그 스텝이 오래 걸려, 같은 배치에서 토큰을 받고 있던 다른 요청들이 <em>잠시 멈춘다</em>.
      사용자에게는 출력이 뚝뚝 끊기는 것으로 보인다.
      그래서 <strong>청크 프리필</strong>(긴 프리필을 잘게 쪼개 디코드 사이에 끼워 넣기)이나
      <strong>프리필·디코드 분리</strong>(서로 다른 GPU 그룹에 할당)가 쓰인다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>더 짜내는 방법들</h2>
    <p>
      배칭 위에 얹는 기법들이 여럿 있다. 각각 다른 자원을 절약한다.
    </p>
    <ul>
      <li><strong>접두사 캐싱.</strong> 같은 시스템 프롬프트를 쓰는 요청들이 앞부분 KV 캐시를 공유한다. 긴 공통 프롬프트를 쓰는 서비스에서 프리필 비용이 크게 준다. 문맥이 <a href="long-context.html">10만 토큰대로 길어지면</a> 프리필이 연산의 7할을 차지하므로, 재사용 여부가 비용을 통째로 가른다.</li>
      <li><strong><a href="speculative-decoding.html">추측 디코딩</a>.</strong> 작은 모델이 초안을 여러 토큰 쓰고 큰 모델이 한 번에 검증한다. 디코드가 메모리 병목이라는 성질을 이용해 <em>남는 연산 능력으로 지연을 산다</em>.</li>
      <li><strong><a href="quantization.html">양자화</a>.</strong> 가중치를 4비트로 줄이면 읽어야 할 바이트가 줄어 디코드가 직접 빨라진다. KV 캐시도 양자화 대상이다.</li>
      <li><strong>연산자 융합·최적 커널.</strong> <a href="flash-attention.html">FlashAttention</a> 계열을 포함해, 중간 결과를 HBM에 쓰지 않는 커널들.</li>
    </ul>
    <p>
      공통점이 보인다. <strong>거의 모든 기법이 메모리 이동을 줄이는 쪽을 향한다.</strong>
      디코드가 대역폭 병목이라는 진단이 서빙 최적화 전체의 출발점인 셈이다.
    </p>
    <p>
      마지막으로 <a href="mixture-of-experts.html">MoE</a>가 여기서 어떻게 읽히는지 짚어 두자.
      MoE는 토큰당 활성 파라미터를 줄이므로 <em>읽어야 할 가중치가 준다</em> —
      디코드에 유리하다. 다만 전문가 전체를 GPU에 상주시켜야 하므로
      <strong>메모리는 그대로</strong>이고, 요청이 몰릴 때만 이득이 커진다.
      "MoE가 아끼는 것은 연산이지 메모리가 아니다"라는 말이
      서빙 관점에서는 <em>"처리량은 늘지만 장비 요구사항은 그대로"</em>로 번역된다.
    </p>
  </section>
"""

READING = [
    "Kwon et al., <em>Efficient Memory Management for Large Language Model Serving with PagedAttention</em> (arXiv:2309.06180) — vLLM. 페이징과 연속 배칭.",
    "Yu et al., <em>Orca: A Distributed Serving System for Transformer-Based Generative Models</em> (OSDI 2022) — 반복 단위 스케줄링(연속 배칭)의 원형.",
    "Agrawal et al., <em>Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve</em> (arXiv:2403.02310) — 청크 프리필.",
    "Ainslie et al., <em>GQA: Training Generalized Multi-Query Transformer Models</em> (arXiv:2305.13245) — KV 캐시를 줄이는 구조적 선택.",
    "Zhong et al., <em>DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving</em> (arXiv:2401.09670) — 프리필·디코드 분리.",
    "Pope et al., <em>Efficiently Scaling Transformer Inference</em> (arXiv:2211.05102) — 배치·병렬 구성에 따른 지연·처리량 분석.",
]

write(
    "llm-serving.html",
    title="LLM 서빙 — 배칭과 스케줄링",
    eyebrow="Application · Inference Serving · 2022–2026",
    h1="LLM 서빙 — 배칭과 스케줄링",
    subtitle="한 장비에 여러 요청을 태우다 — 지연과 처리량의 맞바꿈",
    dek=(
        "토큰 하나를 만들려고 모델 가중치 <strong>전체</strong>를 읽는다. "
        "그 가중치로 하는 계산은 행렬-벡터 곱 하나뿐이라 GPU 연산 유닛이 논다. "
        "배칭은 <em>읽어 온 가중치를 여러 요청에 재사용</em>해 이 낭비를 메운다. "
        "다만 출력 길이를 미리 알 수 없어, 스텝 단위로 배치를 다시 짜야 한다."
    ),
    spec=[
        ("프리필", "연산 병목"),
        ("디코드", "메모리 대역폭 병목"),
        ("표준 기법", "연속 배칭"),
        ("배치 상한", "KV 캐시 메모리"),
        ("충돌 지표", "TTFT ↔ 처리량"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

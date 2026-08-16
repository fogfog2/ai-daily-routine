#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1f3", panel="#e5e8ec", ink="#131820", **{
    "ink-soft": "#4a5462", "ink-faint": "#79838f", "rule": "#ccd2d9",
    "rule-strong": "#a8b0ba", "accent": "#1d5a7a", "accent-fill": "#d7e7ef",
    "accent-line": "#3287ad", "muted": "#838890", "muted-fill": "#dee1e5", "warn": "#a3492e",
})
DARK = dict(paper="#0e1114", panel="#161a1f", ink="#e2e8ee", **{
    "ink-soft": "#a0a9b4", "ink-faint": "#6f7883", "rule": "#1f2429", "rule-strong": "#353d45",
    "accent": "#57b6dd", "accent-fill": "#0c2632", "accent-line": "#2c7ea1",
    "muted": "#868c93", "muted-fill": "#181d21", "warn": "#e08760",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>문맥이 길어지면 무엇이 비싸지는가</h2>
    <p>
      <a href="flash-attention.html">FlashAttention</a> 편은 마지막에
      <em>"긴 문맥이 열렸다"</em>고 적고 끝난다.
      <a href="embeddings.html">임베딩과 위치 인코딩</a> 편은 위치 보간과 YaRN 을 한 문단으로 지나간다.
      둘 다 맞는 말인데, 그 사이에 빠진 것이 있다 —
      <strong>무엇이 얼마나 비싸지는지</strong>가 정리돼 있지 않다.
    </p>
    <p>
      문맥 길이 N 이 커질 때 비용은 <em>한 덩어리로</em> 커지지 않는다.
      성질이 다른 두 가지가 <strong>서로 다른 속도로</strong> 커진다.
    </p>
    <div class="eq">
      <span class="cap">두 가지가 따로 큰다</span>
      <div class="line"><strong>KV 캐시</strong>&nbsp; O(N) &nbsp;— 토큰 하나마다 K,V 한 쌍을 쌓아 둔다</div>
      <div class="line"><strong>어텐션 연산</strong>&nbsp; O(N²) &nbsp;— 모든 토큰이 모든 토큰을 본다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 나머지(FFN·투영)는 O(N) 이다 — 토큰 수에 비례할 뿐</div>
    </div>
    <p>
      선형인 쪽이 먼저 아프고, 제곱인 쪽이 나중에 아프다.
      순서가 이렇게 되는 이유는 상수가 다르기 때문이다. 숫자로 보는 편이 빠르다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>KV 캐시 (fp16)</th><th>토큰당</th><th>32K</th><th>128K</th><th>1M</th></tr>
        </thead>
        <tbody>
          <tr><td>70B급 · MHA (KV 헤드 64)</td><td>2,560 KB</td><td>80 GB</td><td class="hi">320 GB</td><td>2,441 GB</td></tr>
          <tr><td>70B급 · GQA (KV 헤드 8)</td><td class="hi">320 KB</td><td>10 GB</td><td class="hi">40 GB</td><td>305 GB</td></tr>
          <tr><td>8B급 · GQA (KV 헤드 8)</td><td>128 KB</td><td>4 GB</td><td>16 GB</td><td>122 GB</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      계산식은 단순하다. <span class="mono">2 &times; 층수 &times; KV헤드수 &times; 헤드차원 &times; 2바이트</span>가
      토큰 하나의 값이고, 여기에 토큰 수를 곱한다.
      80층·KV헤드 8·헤드차원 128 이면 토큰당 320 KB 이고,
      128K 문맥은 <strong>40 GB</strong> — 70B 모델 가중치(fp16 140 GB)의 3할에 해당한다.
      <a href="mixed-precision.html">정밀도</a>를 낮추거나 <a href="quantization.html">양자화</a>해도
      이 비율 자체는 변하지 않는다. 둘 다 같이 줄기 때문이다.
    </p>
    <div class="note">
      <b>MHA 열을 보라.</b> 같은 128K 에서 320 GB 다. H100 한 장이 80 GB 이므로
      <em>사용자 한 명의 문맥</em>이 네 장을 먹는다. GQA 가 선택이 아니라 전제가 된 이유가 여기 있다 —
      <a href="kv-cache-paged-attention.html">KV 캐시</a> 편에서 다룬 그 이야기가
      긴 문맥에서는 훨씬 절박해진다.
    </div>
    <p>
      제곱인 쪽은 늦게 오지만 오면 압도한다.
      70B 급(80층·d 8192)에서 프리필 시 어텐션이 전체 연산에서 차지하는 비중을 계산하면 이렇다.
    </p>
    <div class="eq">
      <span class="cap">프리필 연산에서 어텐션이 차지하는 비중</span>
      <div class="line">&nbsp;&nbsp;4K 토큰&nbsp;&nbsp;&nbsp;&nbsp;어텐션&nbsp;&nbsp;&nbsp;&nbsp;7.1%</div>
      <div class="line">&nbsp;32K 토큰&nbsp;&nbsp;&nbsp;&nbsp;어텐션&nbsp;&nbsp;&nbsp;38.0%</div>
      <div class="line">128K 토큰&nbsp;&nbsp;&nbsp;&nbsp;어텐션&nbsp;&nbsp;&nbsp;<strong>71.1%</strong></div>
      <div class="line">&nbsp;&nbsp;1M 토큰&nbsp;&nbsp;&nbsp;&nbsp;어텐션&nbsp;&nbsp;&nbsp;<strong>94.9%</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 어텐션 4·L·N²·d 와 선형부 2·P·N 이 같아지는 지점은 N ≈ 53,000</div>
    </div>
    <p>
      <strong>5만 토큰 언저리에서 성격이 바뀐다.</strong>
      그 아래에서 모델은 "파라미터를 읽어 오는 기계"이고,
      그 위에서는 "토큰 쌍을 세는 기계"다.
      최적화의 표적이 통째로 달라진다는 뜻이다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>위치를 늘리는 문제 — 메모리와 무관하다</h2>
    <p>
      메모리와 연산을 다 감당해도 <strong>품질이 먼저 무너지는</strong> 경우가 있다.
      4K 로 학습한 모델에 32K 를 넣으면, 모델이 <em>한 번도 본 적 없는 회전각</em>이 등장한다.
      <a href="embeddings.html">RoPE</a> 가 위치를 각도로 표현하기 때문이다.
    </p>
    <p>
      처방은 세 갈래인데, 셋 다 <em>같은 질문</em>에 다르게 답한다 —
      <strong>본 적 없는 곳을 어떻게 다룰 것인가.</strong>
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 250" role="img" aria-label="위치 인코딩 확장의 세 갈래. 외삽은 학습 범위 밖의 각도를 그대로 쓰다가 무너지고, 위치 보간은 긴 위치를 학습 범위 안으로 압축해 넣으며, NTK-aware와 YaRN은 주파수 차원마다 압축 정도를 달리해 세밀한 구분을 보존한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="lc-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="20" font-size="9.5" letter-spacing="1.2" fill="var(--ink-faint)">학습 범위 0–4K &nbsp;|&nbsp; 목표 0–32K</text>

            <text x="24" y="52" font-size="10" fill="var(--warn)">외삽</text>
            <rect x="24" y="60" width="120" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <rect x="144" y="60" width="360" height="20" fill="none" stroke="var(--warn)" stroke-width="1.1" stroke-dasharray="3 3"/>
            <text x="84" y="74" text-anchor="middle" font-size="8" fill="var(--accent)">본 적 있음</text>
            <text x="324" y="74" text-anchor="middle" font-size="8" fill="var(--warn)">본 적 없는 각도 — 여기서 무너진다</text>

            <text x="24" y="114" font-size="10" fill="var(--accent)">위치 보간</text>
            <rect x="24" y="122" width="480" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.1"/>
            <line x1="504" y1="132" x2="150" y2="132" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#lc-a)"/>
            <text x="330" y="158" text-anchor="middle" font-size="8" fill="var(--ink-soft)">32K 위치를 4K 범위 안으로 눌러 넣는다 — 새 각도가 없다</text>
            <text x="530" y="136" font-size="8" fill="var(--ink-faint)">대신 해상도를 잃는다</text>

            <text x="24" y="192" font-size="10" fill="var(--accent)">NTK-aware · YaRN</text>
            <rect x="24" y="200" width="160" height="14" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <rect x="184" y="200" width="160" height="14" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
            <rect x="344" y="200" width="160" height="14" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="104" y="232" text-anchor="middle" font-size="8" fill="var(--ink-faint)">고주파 — 거의 안 건드림</text>
            <text x="264" y="232" text-anchor="middle" font-size="8" fill="var(--ink-soft)">중간</text>
            <text x="424" y="232" text-anchor="middle" font-size="8" fill="var(--accent)">저주파 — 크게 늘림</text>
          </g>
        </svg>
      </div>
      <figcaption>
        차원마다 회전 주기가 다르다는 사실을 이용한다. 옆 글자를 구분하는 고주파 차원은 그대로 두고,
        문서 전체 범위를 담당하는 저주파 차원만 늘리면 <strong>세밀한 구분을 지키면서</strong> 범위를 넓힐 수 있다.
      </figcaption>
    </figure>

    <p>
      여기서 중요한 것은 <strong>이 확장이 공짜가 아니라는 점</strong>이다.
      위치 보간은 인접한 두 토큰의 각도 차이를 8분의 1로 줄인다 — 가까운 위치를 구분하기 어려워진다.
      짧은 문맥 성능이 떨어지는 보고가 흔한 이유다.
      YaRN 이 차원별로 다르게 스케일링하는 것은 이 대가를 <em>가장 덜 아픈 쪽에 몰아주려는</em> 시도다.
    </p>
    <div class="note">
      <b>학습 없이 되는 것과 안 되는 것.</b> 확장 기법은 대개 <em>소량의 추가 학습</em>을 전제한다.
      "설정 파일에서 <span class="mono">rope_scaling</span> 만 바꾸면 1M 문맥"이라는 말은 절반만 맞다 —
      토큰을 받아들이기는 하지만, 그 범위에서 <a href="evaluation-benchmarks.html">실제로 쓸 수 있는지</a>는
      별개로 재야 한다. 04 절이 그 이야기다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>제곱을 깎는 세 방향</h2>
    <p>
      O(N²) 을 줄이는 시도는 오래됐고, 지금 살아남은 것들은 <strong>세 부류</strong>로 정리된다.
      공통점은 <em>"모든 토큰이 모든 토큰을 볼 필요는 없다"</em>는 가정이고,
      갈리는 지점은 <em>무엇을 버릴 것인가</em>다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방향</th><th>무엇을 하는가</th><th>대가</th></tr>
        </thead>
        <tbody>
          <tr><td class="hi">창을 자른다</td><td>최근 w 개만 본다 (sliding window)</td><td>창 밖 정보가 사라진다</td></tr>
          <tr><td class="hi">캐시를 줄인다</td><td>GQA · MQA · MLA — K,V 를 공유하거나 압축</td><td>표현력을 조금 내준다</td></tr>
          <tr><td class="hi">구조를 바꾼다</td><td><a href="mamba-ssm.html">SSM</a> · 선형 어텐션 — 상태를 고정 크기로</td><td>정확한 회상이 약해진다</td></tr>
        </tbody>
      </table>
    </div>

    <p>
      첫째 방향에서 재미있는 발견이 하나 나왔다.
      최근 w 개만 남기고 <em>앞쪽을 버리면</em> 성능이 급격히 무너지는데,
      원인이 <strong>정보 손실이 아니었다.</strong>
    </p>
    <div class="eq">
      <span class="cap">어텐션 싱크 — softmax 는 반드시 1이 된다</span>
      <div class="line">softmax 출력의 합 = 1 &nbsp;— 어디에도 줄 곳이 없어도 <strong>어딘가엔 줘야 한다</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">모델은 <em>맨 앞 몇 토큰</em>을 그 배출구로 쓰도록 학습된다</div>
      <div class="line">그 토큰을 버리면 → 배출구가 사라지고 → 분포 전체가 뒤틀린다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 처방: 앞 <strong>4개</strong>만 남긴다. 의미가 없어도 자리는 필요하다</div>
    </div>
    <p>
      StreamingLLM 은 이 관찰 하나로 Llama-2·MPT·Falcon·Pythia 를
      <strong>400만 토큰</strong>까지 안정적으로 돌렸고,
      매번 다시 계산하는 방식 대비 최대 <strong>22.2배</strong> 빨랐다.
      추가 학습은 없다.
    </p>
    <div class="note">
      <b>다만 이것은 "긴 문맥"이 아니라 "끝나지 않는 스트림"이다.</b>
      창 밖 내용은 여전히 못 본다. 대화가 끊기지 않고 이어지는 것과
      100만 토큰 문서에서 3장의 내용을 찾아 오는 것은 다른 능력이다.
      논문도 이 점을 분명히 한다.
    </div>
    <p>
      둘째 방향은 캐시 자체를 줄인다. 01 절의 표에서 GQA 가 KV 헤드를 64 → 8 로 줄여
      8분의 1을 만든 것이 그것이고, DeepSeek-V2 의 <strong>MLA</strong> 는 한 걸음 더 간다 —
      K,V 를 저차원 잠재 벡터로 <em>압축해서</em> 저장하고 쓸 때 복원한다.
      논문은 KV 캐시 <strong>93.3% 감소</strong>와 최대 생성 처리량 <strong>5.76배</strong>를 보고한다.
      <a href="autoencoders-vae.html">인코더로 눌러 두고 필요할 때 편다</a>는 발상 그대로다.
    </p>
    <p>
      셋째 방향은 어텐션을 아예 버린다.
      <a href="mamba-ssm.html">상태 공간 모델</a>은 과거를 <em>고정 크기 상태</em>에 요약하므로
      N 이 아무리 커져도 메모리가 늘지 않는다. 대신 <strong>정확한 회상</strong>이 약하다 —
      "고정 크기에 요약한다"는 말은 곧 "무엇인가는 버린다"는 말이다.
      그래서 실전 모델은 <em>몇 층만 어텐션</em>으로 남기는 혼합형이 흔하다.
    </p>
    <div class="eq">
      <span class="cap">창을 자르면 얼마나 아끼나 — 1M 문맥, 창 4K</span>
      <div class="line">KV 캐시&nbsp;&nbsp;&nbsp;&nbsp;4,096 / 1,000,000 = <strong>0.41%</strong></div>
      <div class="line">어텐션 연산&nbsp;&nbsp;대략 <strong>0.8%</strong> 수준 (N·w 대 N²/2)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 절감이 이렇게 크니 <em>무엇을 잃는가</em>가 유일한 쟁점이 된다</div>
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>열린 문맥과 쓸 수 있는 문맥은 다르다</h2>
    <p>
      여기까지가 <em>넣을 수 있게 만드는</em> 이야기다.
      그런데 넣은 것을 모델이 <strong>실제로 쓰는지</strong>는 따로 재야 한다.
      이 구분을 흐리는 것이 긴 문맥 논의에서 가장 흔한 오해다.
    </p>
    <p>
      가장 널리 쓰인 검사는 <strong>NIAH</strong>(needle in a haystack) 다.
      긴 무관한 글 속에 문장 하나를 심어 두고 찾아오게 한다.
      쉽고 그림이 예쁘게 나와서 모델 발표마다 등장했는데, <em>너무 쉽다</em>는 것이 문제였다.
    </p>
    <p>
      RULER 는 같은 모델들을 <strong>더 어려운 과제</strong>로 다시 쟀다 —
      바늘을 여러 개 심고, 유사한 미끼를 섞고, 세는 과제와 추적 과제를 넣었다. 결과는 분명했다.
    </p>
    <div class="note">
      <b>NIAH 는 거의 만점인데 RULER 에서는 대부분 무너졌다.</b>
      32K 를 표방한 모델 중 그 길이에서 기준을 넘긴 것은 넷뿐이었고
      (GPT-4 · Command-R · Yi-34B · Mixtral),
      <strong>거의 모든 모델이 표방한 길이에 닿기 전에</strong> 기준 아래로 떨어졌다.
      "지원 문맥"은 스펙시트의 숫자이고, "유효 문맥"은 그보다 짧다.
    </div>
    <p>
      한 걸음 더 들어가면 <em>어디에 두느냐</em>도 성능을 가른다.
      Lost in the Middle 은 문서 20개 중 정답 위치만 바꿔 가며 측정했다.
    </p>
    <div class="eq">
      <span class="cap">정답 문서의 위치만 바꿨을 때 (문서 20개, 다중문서 QA)</span>
      <div class="line">1번째 (맨 앞)&nbsp;&nbsp;&nbsp;&nbsp;정확도 약 <strong>75%</strong></div>
      <div class="line">10번째 (한가운데)&nbsp;정확도 약 <strong>55%</strong></div>
      <div class="line">20번째 (맨 뒤)&nbsp;&nbsp;&nbsp;&nbsp;정확도 약 <strong>72%</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// U 자 곡선 — 내용이 아니라 <em>위치</em>만으로 20%p 가 갈린다</div>
      <div class="line">// 가운데에 두면 문서를 아예 안 준 것보다 못한 경우까지 보고됐다</div>
    </div>
    <p>
      마지막 줄이 특히 중요하다.
      정답을 손에 쥐여 줬는데 <strong>안 준 것만 못한</strong> 상황이 나온다는 뜻이다.
      맥락을 더 넣는 것이 언제나 이득이라는 직관은 이 지점에서 깨진다.
    </p>
    <p>
      <a href="hallucination.html">환각</a> 편에서 "근거를 줘도 무시하는" 사례를 다뤘는데,
      그 일부는 모델의 성향이 아니라 <em>근거를 둔 자리</em>의 문제일 수 있다.
      <a href="evaluation-benchmarks.html">벤치마크가 실제 사용 조건과 어긋나는</a> 전형적인 예이기도 하다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>그래서 길게 넣을 것인가, 찾아 올 것인가</h2>
    <p>
      실무의 질문은 대개 이 형태로 온다 —
      <strong>문서를 통째로 넣을 것인가, <a href="rag.html">검색해서 필요한 부분만</a> 넣을 것인가.</strong>
      앞 절들을 거치고 나면 답이 취향 문제가 아니라는 것이 보인다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th></th><th>긴 문맥에 통째로</th><th>검색해서 부분만</th></tr>
        </thead>
        <tbody>
          <tr><td>비용</td><td>요청마다 N² 를 다시 낸다</td><td class="hi">색인은 한 번, 조회는 싸다</td></tr>
          <tr><td>지연</td><td>프리필이 길다</td><td class="hi">짧다</td></tr>
          <tr><td>정확도</td><td class="hi">문서 전체를 걸친 추론에 강하다</td><td>검색이 놓치면 끝이다</td></tr>
          <tr><td>갱신</td><td>매번 다시 넣는다</td><td class="hi">색인만 갱신</td></tr>
          <tr><td>취약점</td><td class="hi">가운데를 흘린다 (04절)</td><td>청크 경계에서 맥락이 끊긴다</td></tr>
        </tbody>
      </table>
    </div>

    <p>
      갈림의 기준은 <em>질문의 성격</em>이다.
      "이 계약서 3조가 뭐라고 돼 있나"는 <a href="vector-search.html">검색</a>이 이긴다 —
      답이 한 곳에 있고, 그 한 곳만 찾으면 된다.
      "이 계약서가 앞선 계약서와 어디가 다른가"는 긴 문맥이 이긴다 —
      답이 어느 한 청크에도 들어 있지 않다.
    </p>
    <p>
      비용 쪽도 한 번 더 짚을 만하다.
      100만 토큰을 매 요청마다 넣는다면 어텐션이 연산의 95%를 차지하고,
      그 계산은 <em>같은 문서인데도 매번 다시</em> 일어난다.
      <a href="llm-serving.html">프리픽스 캐싱</a>이 이 낭비를 겨냥한 기능이고,
      긴 문맥이 실용화된 배경에는 <a href="kv-cache-paged-attention.html">캐시를 재사용하는 서빙 구조</a>가 함께 있다.
    </p>
    <div class="note">
      <b>둘을 섞는 쪽이 실제로는 흔하다.</b> 검색으로 후보를 넉넉히 추린 다음
      (한 청크가 아니라 수만 토큰 규모로) 긴 문맥에 밀어 넣는 방식이다.
      검색의 취약점(놓침)은 넉넉히 뽑아서 덮고,
      긴 문맥의 취약점(가운데 흘림·비용)은 범위를 좁혀서 덮는다.
      <strong>순서가 중요하다</strong> — 04 절을 생각하면 가장 중요한 근거는 앞이나 뒤에 두는 편이 낫다.
    </div>
    <p>
      정리하면 문맥 길이는 <em>하나의 숫자가 아니다.</em>
      <strong>넣을 수 있는 길이</strong>(메모리·위치 인코딩),
      <strong>감당할 수 있는 길이</strong>(N² 비용),
      <strong>실제로 쓰는 길이</strong>(RULER·위치 편향) 셋이 각각 다르고,
      대체로 <em>이 순서대로 짧아진다.</em>
      스펙시트에 적힌 것은 첫 번째뿐이다.
    </p>
  </section>
"""

READING = [
    "Chen et al., <em>Extending Context Window of Large Language Models via Position Interpolation</em> (arXiv:2306.15595) — 외삽 대신 내삽.",
    "Peng et al., <em>YaRN: Efficient Context Window Extension of Large Language Models</em> (arXiv:2309.00071) — 차원별로 다르게 스케일링한다.",
    "Xiao et al., <em>Efficient Streaming Language Models with Attention Sinks</em> (arXiv:2309.17453, ICLR 2024) — 앞 4개 토큰을 남기는 것만으로 400만 토큰까지.",
    "Ainslie et al., <em>GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints</em> (arXiv:2305.13245) — KV 헤드를 줄이는 표준 처방.",
    "DeepSeek-AI, <em>DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model</em> (arXiv:2405.04434) — MLA 로 KV 캐시 93.3% 감소.",
    "Liu et al., <em>Lost in the Middle: How Language Models Use Long Contexts</em> (arXiv:2307.03172) — 위치만으로 갈리는 U 자 곡선.",
    "Hsieh et al., <em>RULER: What's the Real Context Size of Your Long-Context Language Models?</em> (arXiv:2404.06654, COLM 2024) — 표방 길이와 유효 길이의 간격.",
]

write(
    "long-context.html",
    title="긴 문맥 — 넣을 수 있는 길이와 쓸 수 있는 길이",
    eyebrow="LLM · Inference · 2023–2026",
    h1="긴 문맥",
    subtitle="넣을 수 있는 길이와 실제로 쓰는 길이는 다르다",
    dek=(
        "문맥이 길어질 때 비싸지는 것은 <strong>두 가지이고 속도가 다르다</strong> — "
        "KV 캐시는 선형, 어텐션은 제곱. 5만 토큰 언저리에서 병목이 뒤바뀐다. "
        "그리고 메모리와 위치 인코딩을 다 해결해도 남는 문제가 있다 — "
        "<em>넣은 것을 모델이 실제로 쓰는가.</em>"
    ),
    spec=[
        ("두 비용", "KV 캐시 O(N) · 어텐션 O(N²)"),
        ("성격이 바뀌는 지점", "70B급에서 약 53K 토큰"),
        ("위치 확장", "PI · NTK-aware · YaRN"),
        ("창을 자를 때", "어텐션 싱크 4개는 남긴다"),
        ("유효 문맥", "표방 길이보다 짧다 (RULER)"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-16",
)

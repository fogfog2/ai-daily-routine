#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0ef", panel="#e6e6e3", ink="#171814", **{
    "ink-soft": "#515349", "ink-faint": "#808277", "rule": "#d2d3cd",
    "rule-strong": "#aeafa7", "accent": "#5c4a92", "accent-fill": "#e2ddf2",
    "accent-line": "#7c6bb5", "muted": "#84868c", "muted-fill": "#dfe0e2", "warn": "#a04628",
})
DARK = dict(paper="#111210", panel="#191a17", ink="#e8e9e3", **{
    "ink-soft": "#a6a89e", "ink-faint": "#797b72", "rule": "#232420", "rule-strong": "#393b34",
    "accent": "#a596e8", "accent-fill": "#1d1936", "accent-line": "#6f61b5",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>모델이 좋아도 안 돌아간다</h2>
    <p>
      <a href="efficient-backbone.html">경량 백본</a>으로 작게 만들고
      <a href="quantization.html">양자화</a>로 더 줄였다. 벤치마크도 좋다.
      그런데 실제 기기에 올리면 <strong>안 돌거나, 느리거나, 결과가 다르다</strong>.
    </p>
    <p>
      원인은 대개 모델이 아니라 <em>그 사이의 층</em>에 있다.
      학습 프레임워크가 만든 모델은 곧바로 기기에서 실행되지 않는다.
      변환하고, 최적화하고, 특정 런타임이 해석해야 한다.
      그 과정에서 <strong>깨질 수 있는 지점</strong>이 여럿이다.
    </p>
    <div class="eq">
      <span class="cap">학습에서 기기까지 — 사이의 단계들</span>
      <div class="line">학습 프레임워크 (PyTorch 등)</div>
      <div class="line">&nbsp;&nbsp;↓ <strong>내보내기</strong>&nbsp;&nbsp;&nbsp;&nbsp;동적 제어 흐름이 사라지거나 굳는다</div>
      <div class="line">중간 표현 (ONNX 등)</div>
      <div class="line">&nbsp;&nbsp;↓ <strong>변환</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;지원 안 되는 연산자에서 멈춘다</div>
      <div class="line">런타임 형식 (TFLite · CoreML · NCNN …)</div>
      <div class="line">&nbsp;&nbsp;↓ <strong>실행</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;가속기가 못 맡으면 CPU 로 떨어진다</div>
      <div class="line">기기 (CPU · GPU · NPU)</div>
    </div>
    <p>
      각 화살표마다 실패하거나 성능이 새어 나갈 구멍이 있다.
      온디바이스 배포에서 시간을 가장 많이 잡아먹는 것이 이 부분이다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>연산자 지원이 모델을 정한다</h2>
    <p>
      가장 자주 부딪히는 벽은 <strong>지원 연산자 목록</strong>이다.
      런타임은 정해진 연산자 집합만 실행할 수 있다.
      모델이 그 밖의 연산을 쓰면 변환이 실패하거나, 되더라도 느린 경로로 떨어진다.
    </p>
    <p>
      문제가 되는 것들이 대체로 정해져 있다.
    </p>
    <ul>
      <li><strong>동적 크기</strong> — 입력에 따라 출력 크기가 변하는 연산. <a href="nms.html">NMS</a> 가 대표다</li>
      <li><strong>제어 흐름</strong> — 조건 분기, 반복. 내보내기 시점에 굳어버리기 쉽다</li>
      <li><strong>최신 활성함수·정규화</strong> — 논문에는 있지만 런타임에는 아직 없다</li>
      <li><strong>희소·비정형 연산</strong> — <a href="pruning-sparsity.html">가지치기</a> 결과가 그대로 안 올라가는 이유</li>
    </ul>
    <div class="note">
      <b>그래서 모델 선택이 런타임에 종속된다.</b>
      "정확도가 가장 높은 모델"이 아니라 <em>"목표 런타임에서 온전히 도는 모델 중 가장 좋은 것"</em>을 고르게 된다.
      <a href="yolo-lineage.html">검출기</a>에서 NMS-free 모델이 배포 관점에서 선호되는 이유가 정확히 이것이다 —
      후처리가 그래프 안에 들어가면 변환할 것이 하나 줄어든다.
    </div>
    <p>
      실무 순서는 그래서 거꾸로다.
      모델을 고르고 배포를 고민하는 것이 아니라,
      <strong>목표 기기와 런타임을 먼저 정하고 그 제약 안에서 모델을 고른다.</strong>
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>가속기가 안 맡으면 소용없다</h2>
    <p>
      요즘 기기에는 CPU 말고도 GPU 와 NPU 가 있다.
      NPU 는 신경망 연산에 특화돼 있어 훨씬 빠르고 전력도 적게 쓴다.
      문제는 <strong>모든 연산을 맡지는 못한다</strong>는 것이다.
    </p>
    <p>
      런타임은 그래프를 훑어 <em>가속기가 처리할 수 있는 구간</em>을 찾아 넘긴다.
      나머지는 CPU 가 맡는다. 여기서 성능이 새어 나간다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="가속기 위임 구조. 모델 전체가 NPU에서 돌면 빠르지만, 중간에 지원되지 않는 연산이 하나 있으면 그래프가 쪼개져 CPU와 NPU 사이를 오가느라 전송 비용이 발생하고 오히려 느려질 수 있다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="mr-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="mr-w" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--warn)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">전부 위임 — 빠르다</text>
            <g>
              <rect x="24" y="30" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
              <rect x="88" y="30" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
              <rect x="152" y="30" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
              <rect x="216" y="30" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
            </g>
            <text x="290" y="47" font-size="8.5" fill="var(--accent)">NPU 한 번에 처리</text>
            <text x="24" y="72" font-size="8" fill="var(--ink-faint)">전송 1회 · 위임 1개</text>

            <line x1="24" y1="86" x2="674" y2="86" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="106" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">중간에 미지원 연산 하나 — 그래프가 쪼개진다</text>
            <g>
              <rect x="24" y="118" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
              <text x="54" y="135" text-anchor="middle" font-size="7.5" fill="var(--ink)">NPU</text>
              <rect x="88" y="118" width="60" height="26" fill="var(--warn)" opacity="0.3" stroke="var(--warn)" stroke-width="1.3"/>
              <text x="118" y="135" text-anchor="middle" font-size="7.5" fill="var(--ink)">CPU</text>
              <rect x="152" y="118" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
              <text x="182" y="135" text-anchor="middle" font-size="7.5" fill="var(--ink)">NPU</text>
              <rect x="216" y="118" width="60" height="26" fill="var(--accent)" opacity="0.4" stroke="var(--accent-line)" stroke-width="1.1"/>
              <text x="246" y="135" text-anchor="middle" font-size="7.5" fill="var(--ink)">NPU</text>
            </g>
            <path d="M84 152 L88 152" stroke="var(--warn)" stroke-width="1.4" marker-end="url(#mr-w)"/>
            <path d="M148 152 L152 152" stroke="var(--warn)" stroke-width="1.4" marker-end="url(#mr-w)"/>
            <text x="290" y="127" font-size="8.5" fill="var(--warn)">전송 3회 · 위임 3개</text>
            <text x="290" y="141" font-size="8" fill="var(--ink-faint)">메모리 복사와 동기화 비용이 붙는다</text>
            <text x="24" y="168" font-size="8" fill="var(--warn)">연산자 하나 때문에 전체가 느려질 수 있다</text>

            <line x1="24" y1="182" x2="674" y2="182" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="202" font-size="8.5" fill="var(--ink-soft)">확인할 것: <tspan fill="var(--accent)">몇 개 구간으로 쪼개졌는가</tspan> · 어느 연산이 위임에서 빠졌는가</text>
            <text x="24" y="216" font-size="8" fill="var(--ink-faint)">런타임이 위임 로그를 내주므로, 느릴 때 가장 먼저 볼 곳이다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>연산자 하나가 전체 속도를 결정할 수 있다.</strong>
        중간에 미지원 연산이 끼면 그래프가 쪼개지고,
        구간마다 <em>메모리 복사와 동기화</em>가 붙는다.
        모델을 더 줄이는 것보다 <em>그 연산 하나를 지원되는 것으로 바꾸는 편</em>이
        효과가 큰 경우가 많다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>수치가 달라진다</h2>
    <p>
      배포에서 당황스러운 문제 중 하나는 <strong>같은 입력에 다른 출력</strong>이다.
      학습 환경에서 검증한 결과가 기기에서 재현되지 않는다.
    </p>
    <p>
      원인이 여럿이다.
    </p>
    <ul>
      <li><strong>정밀도 차이</strong> — <a href="mixed-precision.html">fp32 대신 fp16</a> 이나 int8 로 도는데, 가속기마다 반올림 방식이 다르다</li>
      <li><strong>연산 순서</strong> — 병렬 축약의 순서가 달라 부동소수점 결과가 미세하게 달라진다</li>
      <li><strong>융합 최적화</strong> — 여러 연산을 하나로 합치면서 중간 정밀도가 바뀐다</li>
      <li><strong>전처리 불일치</strong> ← <em>가장 흔하다</em></li>
    </ul>
    <div class="note">
      <b>전처리가 범인인 경우가 놀랄 만큼 많다.</b>
      학습에서는 라이브러리로 리사이즈·정규화를 하는데,
      앱에서는 다른 라이브러리나 하드웨어 경로를 쓴다.
      보간 방식이 다르거나(bilinear 의 align_corners 같은 세부),
      색 채널 순서가 다르거나(RGB vs BGR), 정규화 상수가 다르면
      <strong>모델은 완벽한데 입력이 다른</strong> 상황이 된다.
      디버깅할 때 모델보다 <em>입력 텐서를 먼저 비교</em>하는 것이 빠르다.
    </div>
    <p>
      그래서 배포 검증은 <strong>층별 출력 비교</strong>로 한다.
      같은 입력을 넣고 중간 텐서를 뽑아, 어느 지점에서 갈라지는지 찾는다.
      최종 출력만 보면 원인을 좁힐 수 없다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>지연만 보면 안 된다</h2>
    <p>
      마지막으로 실제 사용자 경험을 정하는 것들을 짚자.
      <em>추론 한 번의 지연</em>은 여러 지표 중 하나일 뿐이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>지표</th><th>왜 중요한가</th></tr>
        </thead>
        <tbody>
          <tr><td>지연 (latency)</td><td>반응 속도. 흔히 유일하게 측정되는 것</td></tr>
          <tr><td class="hi">전력·발열</td><td class="hi">계속 돌리면 기기가 뜨거워지고 성능이 떨어진다</td></tr>
          <tr><td>메모리 peak</td><td>다른 앱과 경쟁. 초과하면 앱이 종료된다</td></tr>
          <tr><td>모델 크기</td><td>앱 용량. 다운로드 이탈률에 직결</td></tr>
          <tr><td>초기화 시간</td><td>첫 실행까지의 대기. 사용자가 가장 먼저 겪는다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>발열이 특히 자주 간과된다.</strong>
      벤치마크는 몇 번 돌려 평균을 내지만, 실제로는 연속 사용이 흔하다.
      기기가 뜨거워지면 <em>스로틀링</em>이 걸려 클럭이 낮아지고,
      처음 측정한 지연이 지켜지지 않는다.
      <em>1분 연속 실행 후의 지연</em>을 함께 재야 하는 이유다.
    </p>
    <div class="note">
      <b>기기 파편화도 현실적 제약이다.</b>
      같은 코드가 최신 폰에서는 NPU 로, 3년 된 폰에서는 CPU 로 떨어진다.
      성능 차이가 <em>수 배</em>가 되므로,
      실무에서는 기기 등급을 나눠 <strong>다른 크기의 모델을 배포</strong>하거나
      기능 자체를 켜고 끄는 구성을 쓴다.
    </div>
    <p>
      정리하면 온디바이스 배포는 <em>모델 최적화 문제가 아니라 시스템 문제</em>다.
      <a href="efficient-backbone.html">경량 백본</a>·<a href="quantization.html">양자화</a>·<a href="knowledge-distillation.html">증류</a>가
      모델 쪽을 담당한다면, 이 문서의 내용은 <strong>그것을 실제로 굴리는 쪽</strong>이다.
      그리고 대개 후자에서 더 많은 시간이 든다.
    </p>
  </section>
"""

READING = [
    "TensorFlow Lite 문서 — 연산자 지원 목록과 위임(delegate) 구조. 변환 실패 시 가장 먼저 볼 곳.",
    "ONNX 명세 — opset 버전별 연산자 정의. 프레임워크 간 이식의 기준.",
    "Core ML Tools 문서 — Apple 기기용 변환과 계산 유닛 지정.",
    "Ignatov et al., <em>AI Benchmark: All About Deep Learning on Smartphones</em> (arXiv:1910.06663) — 기기별 실측과 파편화의 실태.",
    "Ma et al., <em>ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design</em> (arXiv:1807.11164) — FLOPs 가 아니라 실측을 봐야 하는 근거.",
]

write(
    "mobile-runtime.html",
    title="모바일 추론 런타임 — 모델과 기기 사이",
    eyebrow="Vision · On-Device Deployment · 2017–2026",
    h1="모바일 추론 런타임",
    subtitle="모델과 기기 사이 — 여기서 대부분의 시간이 든다",
    dek=(
        "작게 만들고 양자화까지 했는데 기기에서 <strong>안 돌거나, 느리거나, 결과가 다르다</strong>. "
        "원인은 대개 모델이 아니라 <em>그 사이의 층</em>에 있다 — "
        "내보내기, 변환, 연산자 지원, 가속기 위임. "
        "연산자 하나가 전체 속도를 결정하기도 한다."
    ),
    spec=[
        ("첫 번째 벽", "지원 연산자 목록"),
        ("성능 누수", "그래프 분할 · 전송 비용"),
        ("결과 불일치", "전처리가 가장 흔한 원인"),
        ("간과되는 지표", "발열 · 메모리 peak"),
        ("실무 순서", "런타임 먼저, 모델 나중"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

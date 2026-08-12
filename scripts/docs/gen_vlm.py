#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f2", panel="#e5e6ea", ink="#15161c", **{
    "ink-soft": "#4e505a", "ink-faint": "#7d7f89", "rule": "#d0d1d7",
    "rule-strong": "#acadb5", "accent": "#2a4a8c", "accent-fill": "#dce2f3",
    "accent-line": "#4f6fb5", "muted": "#84868e", "muted-fill": "#dfe0e4", "warn": "#a04628",
})
DARK = dict(paper="#101116", panel="#18191f", ink="#e6e7ee", **{
    "ink-soft": "#a2a4b0", "ink-faint": "#757884", "rule": "#212228", "rule-strong": "#383a46",
    "accent": "#8aa4ee", "accent-fill": "#161c36", "accent-line": "#5a72b5",
    "muted": "#868892", "muted-fill": "#1a1b21", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>CLIP 이 못 하는 것</h2>
    <p>
      <a href="clip.html">CLIP</a> 은 이미지와 텍스트를 같은 공간에 놓았다.
      덕분에 <a href="few-shot-learning.html">zero-shot 분류</a>가 되고,
      이미지로 텍스트를 검색할 수 있게 됐다.
    </p>
    <p>
      그런데 CLIP 이 하는 일은 <strong>둘을 비교하는 것</strong>뿐이다.
      "이 이미지가 이 문장과 얼마나 맞는가"에는 답하지만,
      <em>"이 이미지에 무엇이 보이는지 설명해라"</em>에는 답하지 못한다.
    </p>
    <div class="eq">
      <span class="cap">할 수 있는 것과 없는 것</span>
      <div class="line">CLIP&nbsp;&nbsp;&nbsp;&nbsp; 이미지 ↔ 텍스트 <strong>유사도</strong></div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 후보 목록이 있어야 고를 수 있다</div>
      <div class="line">&nbsp;</div>
      <div class="line">VLM&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 이미지 → <strong>텍스트 생성</strong></div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 설명·질문 답변·추론이 열린다</div>
    </div>
    <p>
      차이는 <strong>판별이냐 생성이냐</strong>다.
      후보 중에서 고르는 것과 없던 문장을 만들어내는 것은 다른 능력이고,
      후자를 하려면 <a href="transformer.html">언어 모델</a>이 필요하다.
    </p>
    <p>
      그래서 자연스러운 물음이 나온다 —
      <em>이미 잘하는 시각 인코더와 이미 잘하는 언어 모델을 어떻게 이을 것인가.</em>
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>이미지를 토큰으로 만든다</h2>
    <p>
      언어 모델은 <strong>토큰만 받는다</strong>. 이미지를 넣으려면
      <em>토큰처럼 생긴 것</em>으로 바꿔야 한다.
    </p>
    <p>
      <a href="vision-transformer.html">ViT</a> 가 이미 이미지를 패치 단위 벡터로 만든다.
      남은 일은 그 벡터를 <strong>언어 모델의 임베딩 공간에 맞추는 것</strong>이다.
      이 역할을 하는 부분을 <em>커넥터</em> 또는 <em>프로젝터</em>라 부른다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="Vision-Language 모델의 기본 구조. 시각 인코더가 이미지를 벡터로 만들고 커넥터가 그것을 언어 모델의 토큰 공간으로 옮기면, 언어 모델은 텍스트 토큰과 함께 처리한다. 커넥터 방식에 따라 토큰 수와 비용이 달라진다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="vl-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">기본 구조 — 셋을 잇는다</text>

            <rect x="24" y="32" width="56" height="46" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <g stroke="var(--rule)" stroke-width="0.6" fill="none">
              <line x1="42" y1="32" x2="42" y2="78"/><line x1="60" y1="32" x2="60" y2="78"/>
              <line x1="24" y1="47" x2="80" y2="47"/><line x1="24" y1="62" x2="80" y2="62"/>
            </g>
            <text x="52" y="92" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">이미지</text>

            <path d="M86 55 L106 55" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#vl-a)"/>

            <rect x="110" y="34" width="70" height="42" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3" stroke-dasharray="4 3"/>
            <text x="145" y="52" text-anchor="middle" font-size="8" fill="var(--ink-soft)">시각 인코더</text>
            <text x="145" y="66" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">대개 얼림 ❄</text>

            <path d="M186 55 L206 55" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#vl-a)"/>

            <rect x="210" y="34" width="70" height="42" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.7"/>
            <text x="245" y="52" text-anchor="middle" font-size="8" fill="var(--accent)">커넥터</text>
            <text x="245" y="66" text-anchor="middle" font-size="7.5" fill="var(--accent)">학습됨</text>

            <path d="M286 55 L306 55" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#vl-a)"/>

            <g>
              <rect x="310" y="44" width="16" height="22" fill="var(--accent)" opacity="0.45" stroke="var(--accent-line)" stroke-width="0.9"/>
              <rect x="329" y="44" width="16" height="22" fill="var(--accent)" opacity="0.45" stroke="var(--accent-line)" stroke-width="0.9"/>
              <rect x="348" y="44" width="16" height="22" fill="var(--accent)" opacity="0.45" stroke="var(--accent-line)" stroke-width="0.9"/>
              <rect x="370" y="44" width="16" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="0.9"/>
              <rect x="389" y="44" width="16" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="0.9"/>
            </g>
            <text x="336" y="82" text-anchor="middle" font-size="7" fill="var(--accent)">이미지 토큰</text>
            <text x="397" y="82" text-anchor="middle" font-size="7" fill="var(--ink-faint)">텍스트</text>

            <path d="M411 55 L431 55" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#vl-a)"/>
            <rect x="435" y="34" width="76" height="42" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3" stroke-dasharray="4 3"/>
            <text x="473" y="52" text-anchor="middle" font-size="8" fill="var(--ink-soft)">언어 모델</text>
            <text x="473" y="66" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">얼리거나 일부만</text>

            <path d="M517 55 L537 55" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#vl-a)"/>
            <text x="545" y="58" font-size="8" fill="var(--accent)">텍스트 출력</text>

            <line x1="24" y1="104" x2="674" y2="104" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="124" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">커넥터를 어떻게 만드느냐가 비용을 정한다</text>

            <rect x="24" y="138" width="200" height="30" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="34" y="150" font-size="8" fill="var(--ink)">① 선형 투영 — 패치 그대로</text>
            <text x="34" y="163" font-size="7.5" fill="var(--warn)">토큰 수가 많다 (수백 개)</text>

            <rect x="236" y="138" width="200" height="30" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="246" y="150" font-size="8" fill="var(--accent)">② 질의 기반 압축</text>
            <text x="246" y="163" font-size="7.5" fill="var(--ink-soft)">학습된 질의 N개로 요약 (32~64)</text>

            <rect x="448" y="138" width="200" height="30" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="458" y="150" font-size="8" fill="var(--ink)">③ 교차 어텐션 삽입</text>
            <text x="458" y="163" font-size="7.5" fill="var(--ink-faint)">LM 층 사이에 끼워 넣는다</text>

            <text x="24" y="192" font-size="8.5" fill="var(--warn)">이미지 토큰 수가 곧 비용이다 — 어텐션은 O(N²)</text>
            <text x="24" y="208" font-size="8" fill="var(--ink-faint)">고해상 입력이나 여러 장을 넣으면 문맥이 금세 찬다. 압축이 필요한 이유다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        구조의 핵심은 <strong>무엇을 얼리고 무엇을 학습하는가</strong>다.
        시각 인코더와 언어 모델은 이미 잘하므로 대개 얼리고,
        <em>커넥터만 학습</em>한다. <a href="lora.html">LoRA</a>·<a href="controlnet.html">ControlNet</a> 과
        같은 원칙이 여기서도 반복된다.
      </figcaption>
    </figure>

    <p>
      <strong>이미지 토큰 수</strong>가 실무에서 결정적이다.
      224×224 를 14×14 패치로 나누면 256개, 고해상이면 수천 개가 된다.
      <a href="transformer.html">어텐션이 <code>O(N²)</code></a> 이므로 비용이 빠르게 늘고,
      문맥 창도 잡아먹는다. 그래서 <em>압축하는 커넥터</em>가 나왔다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>학습은 두 단계로</h2>
    <p>
      커넥터를 학습시키는 방식은 대체로 두 단계다.
    </p>
    <div class="eq">
      <span class="cap">정렬 → 지시 학습</span>
      <div class="line"><strong>1단계 · 정렬</strong></div>
      <div class="line">&nbsp;&nbsp;이미지-캡션 쌍으로 <em>커넥터만</em> 학습</div>
      <div class="line">&nbsp;&nbsp;목표: 시각 특징을 LM 이 알아듣는 형태로 옮기기</div>
      <div class="line">&nbsp;</div>
      <div class="line"><strong>2단계 · 지시 학습</strong></div>
      <div class="line">&nbsp;&nbsp;(이미지, 질문, 답변) 로 커넥터 + LM 일부를 학습</div>
      <div class="line">&nbsp;&nbsp;목표: 요청을 알아듣고 형식에 맞게 답하기</div>
    </div>
    <p>
      2단계는 <a href="instruction-tuning.html">instruction tuning</a> 그대로다.
      언어 모델에서 <em>"능력을 만드는 게 아니라 접근하는 문을 내는"</em> 단계였던 것이
      여기서도 같은 역할을 한다.
    </p>
    <div class="note">
      <b>학습 데이터를 모델이 만든다.</b> (이미지, 질문, 답변) 삼중항을 사람이 만들려면 비싸다.
      그래서 <em>강한 언어 모델에게 이미지 설명을 주고 질문·답변을 생성시키는</em> 방식이 표준이 됐다.
      값싸지만 <a href="instruction-tuning.html">모방의 함정</a>이 그대로 따라온다 —
      생성 모델이 이미지를 직접 보지 않았으므로,
      <strong>설명에 없던 것은 지어낼 수 있다</strong>.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>세는 것과 읽는 것에서 약하다</h2>
    <p>
      VLM 은 인상적인 결과를 내지만 <strong>실패 양상이 뚜렷하다</strong>.
      그리고 그 실패가 <em>구조에서 예측 가능한</em> 것들이다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>약한 곳</th><th>왜</th></tr>
        </thead>
        <tbody>
          <tr><td class="hi">개수 세기</td><td>전역 특징에 개수 정보가 잘 남지 않는다</td></tr>
          <tr><td class="hi">정밀한 위치·공간 관계</td><td>패치를 뭉개면 "왼쪽/오른쪽"이 흐려진다</td></tr>
          <tr><td>작은 글자 읽기</td><td class="hi">해상도가 낮으면 애초에 안 보인다</td></tr>
          <tr><td>없는 것을 있다고 함</td><td><a href="hallucination.html">환각</a> — 텍스트 사전지식이 이미지를 이긴다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 특히 중요하다. VLM 의 환각은
      <em>"이미지에 없는데 있다고 답하는"</em> 형태로 나타난다.
      "이 사진에 개가 있나요?" 라고 물으면 없어도 있다고 하는 경향이 보고됐다 —
      <strong>언어 모델의 사전지식이 시각 증거를 압도</strong>하기 때문이다.
    </p>
    <div class="note">
      <b>해상도가 많은 문제의 원인이다.</b> 시각 인코더가 224나 336 해상도로 학습됐으면
      그보다 큰 이미지는 축소돼 들어간다. 작은 글자·세부가 사라진다.
      그래서 <em>이미지를 타일로 쪼개 각각 인코딩</em>하는 방식이 널리 쓰이는데,
      토큰 수가 배로 늘어 <a href="llm-serving.html">비용</a>이 오른다.
      해상도와 비용의 맞바꿈이 VLM 설계의 중심 축이다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>검출·분할로 넘어가기</h2>
    <p>
      VLM 의 흥미로운 확장은 <strong>출력을 텍스트가 아닌 것으로</strong> 만드는 방향이다.
    </p>
    <p>
      좌표를 텍스트로 뱉게 하면(예: <code>&lt;box&gt;12,34,56,78&lt;/box&gt;</code>)
      검출을 언어 문제로 바꿀 수 있다. 클래스 목록이 필요 없어져
      <em>"빨간 우산을 든 사람"</em> 같은 자유로운 지시로 찾을 수 있다.
    </p>
    <p>
      이것이 <strong>오픈보캐블러리 검출·분할</strong>이다.
      <a href="detection-lineage.html">기존 검출기</a>는 학습 시점에 클래스가 고정되는데,
      VLM 기반은 <em>말로 지정</em>하므로 그 제약이 사라진다.
    </p>
    <div class="eq">
      <span class="cap">무엇이 달라지나</span>
      <div class="line">기존:&nbsp; 이미지 → <strong>정해진 80개 클래스</strong> 중 검출</div>
      <div class="line">VLM:&nbsp;&nbsp; 이미지 + <strong>텍스트 지시</strong> → 해당하는 것 검출</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 새 클래스에 재학습이 필요 없다</div>
      <div class="line">// 대신 느리고, 좌표 정밀도가 전용 검출기보다 낮다</div>
    </div>
    <p>
      <a href="segmentation.html">SAM</a> 과 조합하는 구성도 흔하다 —
      VLM 이 <em>무엇을 어디서</em> 찾을지 정하고, SAM 이 <em>정확한 경계</em>를 만든다.
      각자 잘하는 것을 맡기는 방식이다.
    </p>
    <div class="note">
      <b>실무 선택은 여전히 갈린다.</b> 클래스가 고정돼 있고 속도가 중요하면
      <a href="rf-detr.html">전용 검출기</a>가 낫다 — 훨씬 빠르고 정확하다.
      VLM 기반은 <em>클래스가 자주 바뀌거나 미리 정할 수 없을 때</em> 값어치가 있다.
      <a href="mobile-runtime.html">온디바이스</a>에서는 크기 때문에 대체로 쓰기 어렵고,
      그래서 <em>VLM 으로 라벨을 만들어 작은 전용 모델을 학습시키는</em>
      <a href="knowledge-distillation.html">증류</a> 구성이 실용적 절충으로 쓰인다.
    </div>
    <p>
      정리하면 VLM 은 <a href="clip.html">CLIP</a> 이 만든 공통 공간 위에
      <strong>생성 능력을 얹은 것</strong>이다.
      비교만 하던 것이 설명하고 답하게 되면서 쓸 수 있는 곳이 크게 늘었지만,
      <em>세밀한 시각 판단은 여전히 전용 모델이 낫다</em>는 것이 현재 위치다.
    </p>
    <p>
      시각 인코더 쪽을 캡션 없이 학습한 <a href="dino-self-distillation.html">DINOv2 계열</a>로 두고
      언어 쪽만 따로 붙이는 구성도 흔하다.
      <em>특징을 잘 뽑는 것</em>과 <em>말로 지시받는 것</em>은 별개의 능력이라
      어느 쪽을 어디서 가져올지가 설계 선택으로 남는다.
      (이름이 비슷한 Grounding DINO 는 자기지도 DINO 가 아니라
      <a href="detr-lineage.html">DETR 계열 검출기</a> 쪽 DINO 에서 온 것이다 —
      <a href="dino-self-distillation.html">구분은 여기</a>에 정리해 두었다.)
    </p>
  </section>
"""

READING = [
    "Liu et al., <em>Visual Instruction Tuning</em> (arXiv:2304.08485) — LLaVA. 선형 커넥터와 2단계 학습.",
    "Li et al., <em>BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models</em> (arXiv:2301.12597) — 질의 기반 압축 커넥터.",
    "Alayrac et al., <em>Flamingo: a Visual Language Model for Few-Shot Learning</em> (arXiv:2204.14198) — 교차 어텐션 삽입 방식.",
    "Li et al., <em>Evaluating Object Hallucination in Large Vision-Language Models</em> (arXiv:2305.10355) — 없는 물체를 있다고 하는 문제.",
    "Liu et al., <em>Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection</em> (arXiv:2303.05499) — 텍스트로 지정하는 검출.",
    "Tong et al., <em>Eyes Wide Shut? Exploring the Visual Shortcomings of Multimodal LLMs</em> (arXiv:2401.06209) — 시각 인코더의 한계가 VLM 을 제약하는 방식.",
]

write(
    "vision-language-models.html",
    title="Vision-Language 모델 — 비교에서 생성으로",
    eyebrow="Application · Multimodal · 2022–2026",
    h1="Vision-Language 모델",
    subtitle="비교에서 생성으로 — CLIP 이 못 하던 것",
    dek=(
        "CLIP 은 이미지와 텍스트의 <strong>유사도</strong>만 잰다. "
        "후보 목록이 있어야 고를 수 있고, \"무엇이 보이는지 설명해라\"에는 답하지 못한다. "
        "VLM 은 시각 인코더와 언어 모델을 이어 <em>텍스트를 생성</em>하게 만든다. "
        "관건은 이미지를 <strong>토큰으로 어떻게 옮기느냐</strong>다."
    ),
    spec=[
        ("CLIP 과 차이", "판별 → 생성"),
        ("구조", "인코더 + 커넥터 + LM"),
        ("학습되는 것", "주로 커넥터"),
        ("비용 축", "이미지 토큰 수 · 해상도"),
        ("약한 곳", "개수 · 위치 · 환각"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

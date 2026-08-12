#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1f0", panel="#e5e8e5", ink="#151a15", **{
    "ink-soft": "#4e574d", "ink-faint": "#7d867b", "rule": "#cfd5cd",
    "rule-strong": "#acb2a9", "accent": "#2d6340", "accent-fill": "#daebe0",
    "accent-line": "#4a8c62", "muted": "#83888c", "muted-fill": "#dee1de", "warn": "#a04a28",
})
DARK = dict(paper="#0f1210", panel="#171b17", ink="#e4eae4", **{
    "ink-soft": "#a1aba0", "ink-faint": "#707a70", "rule": "#202720", "rule-strong": "#364036",
    "accent": "#5fc788", "accent-fill": "#0e2a1a", "accent-line": "#348a58",
    "muted": "#868d86", "muted-fill": "#191f19", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>예시가 다섯 장뿐일 때</h2>
    <p>
      새 제품이 출시됐다. 사진이 다섯 장 있다.
      이것을 분류기에 넣어 학습시키면 <strong>거의 확실히 과적합</strong>한다.
      다섯 장을 외워 버리고 여섯 번째 사진은 못 맞힌다.
    </p>
    <p>
      그런데 사람은 다섯 장이면 충분히 배운다. 심지어 한 장으로도 된다.
      차이가 어디서 오는가 — <strong>사람은 이미 아는 것이 많기 때문</strong>이다.
      새 제품을 배울 때 "물체란 무엇인가", "각도가 바뀌면 어떻게 보이는가"를
      처음부터 배우지 않는다.
    </p>
    <p>
      Few-shot 학습의 전제가 정확히 이것이다.
      <em>사전 지식을 갖춘 상태에서 시작</em>하고, 새 클래스에 대해서는
      <strong>최소한만 조정</strong>한다.
    </p>
    <div class="eq">
      <span class="cap">용어 정리 — N-way K-shot</span>
      <div class="line">support set&nbsp; 클래스당 K 장의 예시 (K = 1, 5 등)</div>
      <div class="line">query set&nbsp;&nbsp;&nbsp; 분류해야 할 새 이미지</div>
      <div class="line">&nbsp;</div>
      <div class="line">5-way 1-shot&nbsp; 5개 클래스, 각 1장 → 새 이미지를 분류</div>
      <div class="line">&nbsp;</div>
      <div class="line">zero-shot&nbsp;&nbsp;&nbsp;&nbsp; 예시가 <strong>0장</strong> — 이름·설명만 주어진다</div>
    </div>
    <div class="note">
      <b>"few-shot" 이 두 가지를 뜻한다.</b> 비전에서는 위처럼
      <em>support set 으로 새 클래스를 분류하는</em> 과제 설정을 말한다.
      LLM 에서는 <a href="in-context-learning.html">프롬프트에 예시를 넣는 것</a>을 말한다.
      둘 다 "예시 몇 개로 새 과제를" 라는 점은 같지만
      <strong>학습이 일어나는 방식이 전혀 다르다</strong> — 헷갈리기 쉬운 지점이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>비교로 푸는 방법</h2>
    <p>
      가장 자연스러운 접근은 <strong>분류를 비교로 바꾸는 것</strong>이다.
      <a href="metric-learning.html">메트릭 러닝</a>이 이미 이 일을 하고 있었다.
    </p>
    <p>
      support set 의 각 클래스를 <em>임베딩의 평균</em>으로 대표하고,
      query 를 가장 가까운 대표에 배정한다. 이것이 <strong>프로토타입 방식</strong>이다.
    </p>
    <div class="eq">
      <span class="cap">Prototypical Network — 학습할 것이 없다</span>
      <div class="line">c<sub>k</sub> = (1/K) Σ f(x<sub>i</sub>)&nbsp;&nbsp;&nbsp;// 클래스 k 의 프로토타입 = 평균</div>
      <div class="line">&nbsp;</div>
      <div class="line">p(y=k | x) = softmax( −d( f(x), c<sub>k</sub> ) )</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 새 클래스가 와도 <strong>평균만 계산</strong>하면 끝 — 가중치 갱신 없음</div>
    </div>
    <p>
      단순한데 강력하다. 그리고 실무적으로 중요한 성질이 있다 —
      <strong>새 클래스 추가에 재학습이 필요 없다</strong>.
      <a href="metric-learning.html">메트릭 러닝</a>이 말한
      <em>"클래스가 정해지지 않은 세계"</em>를 그대로 다룬다.
    </p>
    <div class="note">
      <b>거리 함수 선택이 생각보다 중요하다.</b>
      원 논문은 <em>유클리드 거리</em>가 코사인보다 잘 작동한다고 보고했다.
      제곱 유클리드 거리로 softmax 를 취하면 <strong>선형 분류기와 동등</strong>해지는
      성질이 있어, 학습이 안정된다는 해석이 붙는다.
      "무엇을 가깝다고 볼 것인가"의 정의가 결과를 가르는 것은 이 계열의 공통점이다.
    </div>
    <p>
      학습 방식도 특이하다. 일반 분류처럼 학습하지 않고
      <strong>few-shot 상황을 흉내 내며</strong> 학습한다 —
      매 배치마다 클래스 몇 개를 뽑아 support/query 로 나누고,
      그 상황에서 잘하도록 임베딩을 조정한다.
      <em>"적은 예시로 구분하는 연습"</em>을 반복하는 셈이다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>Zero-shot — 예시가 아예 없을 때</h2>
    <p>
      예시가 0장이면 비교할 대상이 없다.
      그런데도 분류가 가능한 이유는 <strong>다른 양식(modality)의 정보</strong>를 쓰기 때문이다.
    </p>
    <p>
      <a href="clip.html">CLIP</a> 이 이것을 실용적 수준으로 끌어올렸다.
      이미지와 텍스트를 같은 공간에 놓았으므로,
      <em>클래스 이름을 텍스트로 넣어 그 임베딩을 프로토타입처럼 쓴다</em>.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 232" role="img" aria-label="few-shot과 zero-shot의 비교. few-shot은 예시 이미지들의 평균을 클래스 대표로 삼고, zero-shot은 클래스 이름의 텍스트 임베딩을 대표로 삼는다. 구조는 같고 대표를 무엇으로 만드는지만 다르다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="fs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">Few-shot — 예시들의 평균이 대표</text>

            <g>
              <rect x="24" y="30" width="26" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="54" y="30" width="26" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="84" y="30" width="26" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <text x="67" y="70" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">support 3장</text>
            </g>
            <path d="M118 43 L142 43" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#fs-a)"/>
            <text x="130" y="36" text-anchor="middle" font-size="7" fill="var(--ink-faint)">f</text>
            <g fill="var(--accent)" opacity="0.6">
              <circle cx="156" cy="36" r="3.5"/><circle cx="166" cy="46" r="3.5"/><circle cx="152" cy="50" r="3.5"/>
            </g>
            <circle cx="158" cy="44" r="8" fill="none" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="176" y="47" font-size="7.5" fill="var(--accent)">평균 = 프로토타입</text>

            <line x1="300" y1="26" x2="300" y2="90" stroke="var(--rule)" stroke-width="1"/>

            <text x="324" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">Zero-shot — 텍스트가 대표</text>
            <rect x="324" y="30" width="150" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="399" y="46" text-anchor="middle" font-size="7.5" fill="var(--ink-soft)">"a photo of a cat"</text>
            <path d="M482 42 L506 42" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#fs-a)"/>
            <circle cx="522" cy="42" r="8" fill="none" stroke="var(--accent-line)" stroke-width="1.6"/>
            <circle cx="522" cy="42" r="3.5" fill="var(--accent)" opacity="0.6"/>
            <text x="540" y="45" font-size="7.5" fill="var(--accent)">텍스트 임베딩</text>
            <text x="324" y="70" font-size="7.5" fill="var(--ink-faint)">예시 이미지가 0장 — 이름만 있으면 된다</text>

            <line x1="24" y1="102" x2="674" y2="102" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="122" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">이후는 같다 — 가장 가까운 대표로 분류</text>

            <circle cx="200" cy="168" r="6" fill="var(--warn)" opacity="0.7"/>
            <text x="200" y="192" text-anchor="middle" font-size="7.5" fill="var(--warn)">query</text>

            <circle cx="110" cy="146" r="8" fill="none" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="110" y="132" text-anchor="middle" font-size="7" fill="var(--ink-faint)">고양이</text>
            <circle cx="300" cy="146" r="8" fill="none" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="300" y="132" text-anchor="middle" font-size="7" fill="var(--ink-faint)">개</text>
            <circle cx="230" cy="200" r="8" fill="none" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="230" y="218" text-anchor="middle" font-size="7" fill="var(--ink-faint)">자동차</text>

            <line x1="194" y1="164" x2="118" y2="150" stroke="var(--accent-line)" stroke-width="1.8"/>
            <text x="140" y="172" font-size="7" fill="var(--accent)">가장 가까움</text>
            <line x1="206" y1="166" x2="292" y2="148" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="3 2"/>
            <line x1="204" y1="174" x2="224" y2="194" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="3 2"/>

            <text x="360" y="146" font-size="8.5" fill="var(--ink-soft)">구조는 동일하다 —</text>
            <text x="360" y="162" font-size="8" fill="var(--ink-faint)">대표를 <em>이미지 평균</em>으로 만드느냐</text>
            <text x="360" y="176" font-size="8" fill="var(--ink-faint)"><em>텍스트</em>로 만드느냐만 다르다</text>
            <text x="360" y="198" font-size="8" fill="var(--accent)">그래서 둘을 섞을 수도 있다 —</text>
            <text x="360" y="212" font-size="8" fill="var(--ink-faint)">텍스트 대표에 예시 몇 장을 더해 보정</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        few-shot 과 zero-shot 은 <strong>같은 구조의 두 변형</strong>이다.
        클래스 대표를 무엇으로 만드느냐만 다르고, 이후 절차는 동일하다.
        그래서 <em>텍스트 대표에 예시 몇 장을 섞는</em> 중간 형태도 자연스럽게 나온다.
      </figcaption>
    </figure>

    <p>
      zero-shot 의 성능은 <strong>프롬프트 문구에 크게 좌우된다</strong>.
      단순히 <code>"cat"</code> 보다 <code>"a photo of a cat"</code> 이 낫고,
      여러 문구의 임베딩을 평균하면 더 나아진다.
      <a href="in-context-learning.html">ICL</a> 에서 본
      <em>형식이 내용보다 중요할 때가 있다</em>는 관찰이 여기서도 반복된다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>가벼운 적응 — 프롬프트만 학습</h2>
    <p>
      zero-shot 은 편하지만 <em>내 도메인에 최적은 아니다</em>.
      의료 영상이나 특수 부품처럼 일반 웹 이미지와 다른 데이터에서는 성능이 떨어진다.
    </p>
    <p>
      그렇다고 전체를 파인튜닝하면 <a href="clip.html">CLIP</a> 이 가진
      <strong>범용성을 잃는다</strong> — 좁은 데이터에 과적합해 다른 클래스를 못 맞히게 된다.
    </p>
    <p>
      절충안은 <strong>프롬프트만 학습</strong>하는 것이다.
      모델은 얼리고, 텍스트 쪽 입력 벡터만 조정한다.
    </p>
    <div class="eq">
      <span class="cap">프롬프트 학습 — 문구를 사람이 쓰지 않는다</span>
      <div class="line">기존:&nbsp;&nbsp;&nbsp; "a photo of a [CLASS]"&nbsp;&nbsp;&nbsp;// 사람이 손으로</div>
      <div class="line">학습형: [v₁][v₂]…[v<sub>n</sub>][CLASS]&nbsp;&nbsp;&nbsp;// v 는 학습되는 벡터</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 실제 단어에 대응할 필요가 없다 — 연속 공간에서 최적을 찾는다</div>
      <div class="line">// 학습 파라미터가 아주 적어 예시 몇 장으로도 된다</div>
    </div>
    <p>
      <a href="peft-adapters.html">PEFT</a> 에서 본 Prompt Tuning 과 같은 발상이다.
      대형 모델을 다루는 원칙 — <em>얼리고, 작은 것만 학습하고, 원본을 망가뜨리지 않는다</em> —
      이 비전에서도 그대로 쓰인다.
    </p>
    <div class="note">
      <b>여기서도 과적합이 문제다.</b> 학습에 쓴 클래스에서는 좋아지는데
      <em>보지 않은 클래스에서 오히려 나빠지는</em> 현상이 보고됐다.
      학습된 프롬프트가 그 클래스들에 특화돼 범용성을 잃는 것이다.
      이미지 조건을 프롬프트에 넣어 <strong>일반화를 지키려는</strong> 후속 연구들이 이 지점을 다룬다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>평가가 특히 까다롭다</h2>
    <p>
      few-shot 연구는 <strong>평가 설계에서 논쟁이 많았던</strong> 분야다.
      결과가 좋아 보이는데 실제로는 그렇지 않은 경우가 반복됐기 때문이다.
    </p>
    <ul>
      <li><strong>클래스 분할이 결과를 바꾼다</strong> — 어떤 클래스를 "새 클래스"로 두느냐에 따라 난이도가 크게 다르다</li>
      <li><strong>편차가 크다</strong> — support set 을 어떻게 뽑느냐에 따라 흔들려, 수백 번 반복해 평균과 신뢰구간을 봐야 한다</li>
      <li><strong>기준선이 강하다</strong> — 잘 학습된 임베딩 위에 <em>단순 선형 분류기</em>를 얹는 것이 정교한 방법과 비슷하다는 결과가 반복 보고됐다</li>
    </ul>
    <div class="note">
      <b>세 번째가 이 분야의 중요한 교훈이다.</b>
      복잡한 메타러닝 알고리즘의 이득이라 여겨졌던 것 중 상당 부분이
      <em>사실은 좋은 사전학습 표현의 이득</em>이었다.
      <a href="metric-learning.html">메트릭 러닝</a>에서 본
      <em>"공정 비교 시 방법 간 격차가 보고보다 작다"</em>는 지적과 같은 계열이다.
      <a href="evaluation-benchmarks.html">평가 문서</a>의 주제가 여기서도 반복된다.
    </div>
    <p>
      실무 관점에서 정리하면 이렇다.
      <strong>먼저 좋은 사전학습 모델을 구하는 것</strong>이 알고리즘 선택보다 중요하다.
      <a href="dino-self-distillation.html">DINOv2</a> 나 <a href="clip.html">CLIP</a> 같은
      범용 특징 위에서는 단순한 방법으로도 충분한 경우가 많다.
      둘의 성격은 다르다 — 캡션으로 배운 쪽은 말로 지시할 수 있고,
      <a href="dino-self-distillation.html">라벨 없이 배운 쪽</a>은 캡션이 없는 도메인에서 강하다.
    </p>
    <p>
      그리고 <em>정말 few-shot 이 필요한지</em>를 먼저 물어야 한다.
      라벨을 몇백 장 더 모을 수 있다면 <a href="data-pipeline.html">그쪽이 훨씬 확실하다</a>.
      few-shot 은 <strong>더 모을 수 없을 때</strong>의 답이지,
      라벨링을 아끼는 손쉬운 방법이 아니다.
    </p>
  </section>
"""

READING = [
    "Snell et al., <em>Prototypical Networks for Few-shot Learning</em> (arXiv:1703.05175) — 평균을 프로토타입으로.",
    "Finn et al., <em>Model-Agnostic Meta-Learning</em> (arXiv:1703.03400) — 빠르게 적응하도록 초기값을 학습.",
    "Radford et al., <em>Learning Transferable Visual Models From Natural Language Supervision</em> (arXiv:2103.00020) — CLIP. zero-shot 분류.",
    "Zhou et al., <em>Learning to Prompt for Vision-Language Models</em> (arXiv:2109.01134) — CoOp. 프롬프트 학습.",
    "Tian et al., <em>Rethinking Few-Shot Image Classification: a Good Embedding Is All You Need?</em> (arXiv:2003.11539) — 단순 기준선이 강하다는 결과.",
    "Chen et al., <em>A Closer Look at Few-shot Classification</em> (arXiv:1904.04232) — 평가 설계의 문제를 지적.",
]

write(
    "few-shot-learning.html",
    title="Few-Shot / Zero-Shot — 예시가 거의 없을 때",
    eyebrow="Vision · Low-Data Regime · 2017–2026",
    h1="Few-Shot / Zero-Shot",
    subtitle="예시가 거의 없을 때 — 사전 지식을 갖춘 채로 시작한다",
    dek=(
        "새 제품 사진이 다섯 장뿐이면 분류기는 <strong>그 다섯 장을 외워 버린다</strong>. "
        "사람이 다섯 장으로 배울 수 있는 것은 이미 아는 것이 많기 때문이다. "
        "그래서 분류를 <em>비교</em>로 바꾸고, 새 클래스에는 최소한만 조정한다. "
        "예시가 0장이면 이름을 대신 쓴다."
    ),
    spec=[
        ("설정", "N-way K-shot"),
        ("핵심 전환", "분류 → 비교"),
        ("프로토타입", "예시들의 평균"),
        ("zero-shot", "텍스트가 대표 역할"),
        ("교훈", "좋은 표현이 알고리즘보다 중요"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

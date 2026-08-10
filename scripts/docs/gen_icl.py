#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ef", panel="#e6e8e5", ink="#161a16", **{
    "ink-soft": "#4f574f", "ink-faint": "#7e867d", "rule": "#d1d5d0",
    "rule-strong": "#adb2ab", "accent": "#2a6350", "accent-fill": "#dbebe4",
    "accent-line": "#458c73", "muted": "#83888c", "muted-fill": "#dee1e2", "warn": "#a04b28",
})
DARK = dict(paper="#101210", panel="#181b18", ink="#e6eae5", **{
    "ink-soft": "#a5aca3", "ink-faint": "#7a8178", "rule": "#222722", "rule-strong": "#384038",
    "accent": "#5fc9a4", "accent-fill": "#0f2a22", "accent-line": "#358c70",
    "muted": "#868d90", "muted-fill": "#191f1c", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>가중치가 변하지 않는데 배운다</h2>
    <p>
      프롬프트에 예시 몇 개를 넣으면 모델이 새 과제를 수행한다.
      학습률도, 그래디언트도, 파라미터 갱신도 없다.
      <strong>가중치는 단 하나도 변하지 않는다.</strong>
    </p>
    <div class="eq">
      <span class="cap">few-shot 프롬프트 — 이것이 전부다</span>
      <div class="line">사과 → apple</div>
      <div class="line">바다 → sea</div>
      <div class="line">하늘 → sky</div>
      <div class="line">구름 → <span style="opacity:.6">▮</span></div>
      <div class="line">// 모델은 "cloud" 를 내놓는다. 번역을 배운 적이 없어도.</div>
    </div>
    <p>
      GPT-3 논문이 이 현상을 전면에 내세웠고, 이름도 붙였다 —
      <strong>in-context learning</strong>. 문맥 안에서 일어나는 학습이라는 뜻이다.
    </p>
    <p>
      다만 "학습"이라는 말이 오해를 부른다.
      영구적으로 무언가를 획득하는 것이 아니라,
      <em>그 요청을 처리하는 동안만 유지되는 일시적 적응</em>이다.
      대화가 끝나면 사라진다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>예시는 무엇을 알려주는가 — 놀라운 실험</h2>
    <p>
      상식적으로는 모델이 예시에서 <em>입력과 출력의 대응 관계</em>를 배운다고 생각하게 된다.
      그런데 이를 정면으로 검증한 실험이 예상 밖의 결과를 내놓았다.
    </p>
    <p>
      Min 등은 예시의 <strong>라벨을 무작위로 바꿔</strong> 넣어 봤다.
      "사과 → sea", "바다 → sky" 같은 식으로 대응을 망가뜨린 것이다.
      상식대로라면 성능이 무너져야 한다.
    </p>
    <p>
      <strong>성능이 거의 떨어지지 않았다.</strong>
      반면 다른 것을 망가뜨리면 성능이 크게 떨어졌다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>망가뜨린 요소</th><th>성능 영향</th><th>의미</th></tr>
        </thead>
        <tbody>
          <tr><td>입력-라벨 대응 (무작위 라벨)</td><td class="hi">거의 없음</td><td>정답을 배우는 게 아니다</td></tr>
          <tr><td>라벨 공간 (없는 라벨 사용)</td><td>큼</td><td>"어떤 답들이 가능한가"가 중요</td></tr>
          <tr><td>입력 분포 (엉뚱한 문장)</td><td>큼</td><td>"어떤 입력을 다루는가"가 중요</td></tr>
          <tr><td>형식 (구조 파괴)</td><td class="hi">매우 큼</td><td>형식이 가장 중요하다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      해석은 이렇다. 예시는 모델에게 <em>새로운 지식을 가르치는 것이 아니라</em>
      <strong>이미 가진 능력 중 무엇을 쓸지 지정하는 것</strong>에 가깝다.
      "지금은 번역 과제이고, 출력은 영단어 하나이며, 형식은 이렇다"는 신호다.
    </p>
    <div class="note">
      <b>다만 이 결론은 조건부다.</b> 후속 연구들은 <em>충분히 큰 모델</em>에서는
      무작위 라벨이 성능을 떨어뜨리고, 심지어 <strong>뒤집힌 라벨을 따라가는</strong>
      능력까지 나타난다고 보고했다. 즉 모델이 커질수록
      <em>과제 지정</em>에서 <em>실제 대응 학습</em> 쪽으로 성질이 옮겨간다.
      "예시의 정답은 중요하지 않다"는 명제는 규모에 따라 달라진다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>어떻게 가능한가 — 두 가지 설명</h2>
    <p>
      메커니즘에 대한 설명은 크게 두 갈래다.
    </p>
    <p>
      <strong>첫째, 암묵적 경사하강 가설.</strong>
      어텐션 연산이 수학적으로 경사하강 한 스텝과 유사한 형태를 띤다는 관찰이다.
      단순화된 선형 회귀 과제에서, 트랜스포머가 문맥 안의 예시들로
      <em>내부적으로 최소제곱 해에 가까운 것을 계산</em>한다는 결과가 나왔다.
      이 관점에서 순전파는 "가중치를 바꾸지 않는 학습 루프"가 된다.
    </p>
    <p>
      <strong>둘째, 귀납 헤드.</strong>
      해석가능성 연구에서 발견된 구체적 회로다.
      두 개의 어텐션 헤드가 협력해 <em>"앞서 A 다음에 B가 나왔으니, 지금 A가 나왔다면 다음은 B"</em>
      라는 패턴 복사를 수행한다.
    </p>
    <div class="eq">
      <span class="cap">귀납 헤드 — 두 헤드의 협력</span>
      <div class="line">① 이전 토큰 헤드: 각 위치에 "내 앞 토큰이 무엇이었는지"를 기록</div>
      <div class="line">② 귀납 헤드: 현재 토큰과 같은 것을 과거에서 찾아,</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;<strong>그 다음에 왔던 토큰</strong>을 복사해 온다</div>
      <div class="line">// [A][B] … [A] → [B] 를 예측</div>
    </div>
    <p>
      흥미로운 것은 <strong>형성 시점</strong>이다.
      학습 곡선에서 귀납 헤드가 갑자기 생기는 구간이 있고,
      바로 그 지점에서 in-context learning 능력이 <em>계단처럼 뛴다</em>.
      두 현상의 시점이 일치한다는 것이 이 회로가 원인이라는 강한 정황이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 224" role="img" aria-label="파인튜닝과 in-context learning의 비교, 그리고 귀납 헤드의 동작 도식. 파인튜닝은 가중치를 영구히 바꾸지만 in-context learning은 문맥 안에서만 일시적으로 작동하며, 귀납 헤드는 과거에 같은 토큰이 나온 자리를 찾아 그 다음 토큰을 복사한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ic-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">파인튜닝 — 가중치가 변한다</text>
            <rect x="26" y="30" width="120" height="30" fill="var(--warn)" opacity="0.18" stroke="var(--warn)" stroke-width="1.2"/>
            <text x="86" y="49" text-anchor="middle" font-size="8.5" fill="var(--ink)">W → W'  (영구)</text>
            <text x="26" y="76" font-size="8" fill="var(--ink-faint)">그래디언트 · 학습률 · 시간 필요</text>
            <text x="26" y="90" font-size="8" fill="var(--ink-faint)">과제마다 별도 모델</text>

            <text x="26" y="120" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">ICL — 문맥 안에서만</text>
            <rect x="26" y="132" width="120" height="30" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="86" y="151" text-anchor="middle" font-size="8.5" fill="var(--accent)">W 그대로 (일시적)</text>
            <text x="26" y="178" font-size="8" fill="var(--ink-faint)">즉시 · 무료 · 요청마다 다른 과제</text>
            <text x="26" y="192" font-size="8" fill="var(--warn)">매 요청마다 예시 토큰 비용</text>
            <text x="26" y="206" font-size="8" fill="var(--warn)">문맥 길이가 상한</text>

            <line x1="186" y1="26" x2="186" y2="212" stroke="var(--rule)" stroke-width="1"/>

            <text x="212" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">귀납 헤드 — [A][B] … [A] → [B]</text>

            <g>
              <rect x="212" y="34" width="40" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
              <text x="232" y="50" text-anchor="middle" font-size="9" fill="var(--accent)">사과</text>
              <rect x="256" y="34" width="46" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
              <text x="279" y="50" text-anchor="middle" font-size="9" fill="var(--accent)">apple</text>

              <rect x="310" y="34" width="40" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <text x="330" y="50" text-anchor="middle" font-size="9" fill="var(--ink-faint)">바다</text>
              <rect x="354" y="34" width="40" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <text x="374" y="50" text-anchor="middle" font-size="9" fill="var(--ink-faint)">sea</text>

              <rect x="402" y="34" width="40" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.8"/>
              <text x="422" y="50" text-anchor="middle" font-size="9" fill="var(--accent)">사과</text>

              <rect x="450" y="34" width="46" height="24" fill="none" stroke="var(--accent-line)" stroke-width="1.4" stroke-dasharray="3 2"/>
              <text x="473" y="50" text-anchor="middle" font-size="9" fill="var(--accent)">?</text>
            </g>

            <path d="M416 62 C 400 88, 250 88, 232 62" stroke="var(--accent-line)" stroke-width="1.4" fill="none" marker-end="url(#ic-a)"/>
            <text x="324" y="96" text-anchor="middle" font-size="8" fill="var(--accent)">① 과거에서 같은 토큰을 찾는다</text>

            <path d="M285 62 C 300 116, 460 116, 473 62" stroke="var(--accent-line)" stroke-width="1.4" fill="none" marker-end="url(#ic-a)"/>
            <text x="380" y="126" text-anchor="middle" font-size="8" fill="var(--accent)">② 그 다음에 왔던 토큰을 복사한다</text>

            <line x1="212" y1="142" x2="674" y2="142" stroke="var(--rule)" stroke-width="1"/>

            <text x="212" y="164" font-size="9" fill="var(--ink-soft)">학습 중 귀납 헤드가 형성되는 시점과</text>
            <text x="212" y="178" font-size="9" fill="var(--ink-soft)">ICL 능력이 <tspan fill="var(--accent)">계단처럼 뛰는 시점</tspan>이 일치한다.</text>
            <text x="212" y="198" font-size="8.5" fill="var(--ink-faint)">회로가 원인이라는 강한 정황이지만,</text>
            <text x="212" y="211" font-size="8.5" fill="var(--ink-faint)">복잡한 과제까지 이 회로로 설명되는지는 미해결이다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        귀납 헤드는 <strong>패턴 복사</strong>라는 매우 단순한 기능이다.
        그런데 few-shot 프롬프트의 구조가 정확히 이 형태다 —
        입력-출력 쌍을 나열하고 새 입력을 주는 것.
        <em>단순한 회로가 범용적으로 보이는 능력의 밑바닥에 있다</em>는 것이 이 발견의 함의다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>실무에서 — 무엇이 성능을 좌우하나</h2>
    <p>
      ICL은 민감하다. 같은 예시라도 배치에 따라 결과가 크게 달라진다.
      알려진 요인들이 있다.
    </p>
    <ul>
      <li><strong>순서.</strong> 예시 순서만 바꿔도 정확도가 크게 흔들린다. 마지막 예시의 영향이 특히 크다는 관찰이 반복된다.</li>
      <li><strong>라벨 편향.</strong> 예시에 특정 라벨이 많으면 모델이 그쪽으로 기운다. 예시 분포를 균형 있게 맞추는 것이 중요하다.</li>
      <li><strong>유사도.</strong> 무작위 예시보다 <em>지금 질문과 비슷한</em> 예시를 뽑아 넣는 편이 낫다. 검색으로 예시를 고르는 방식이 흔히 쓰인다.</li>
      <li><strong>형식 일관성.</strong> 구분자와 배열을 일정하게 유지하는 것이 내용보다 중요할 때가 많다.</li>
    </ul>
    <p>
      비용 구조도 짚어야 한다. 파인튜닝은 <em>한 번 비싸고 이후 공짜</em>지만,
      ICL은 <strong>매 요청마다 예시 토큰 값을 낸다</strong>.
      호출이 많아지면 누적 비용이 파인튜닝을 넘어선다.
      게다가 문맥 길이가 상한이라 예시를 무한정 넣을 수도 없다.
    </p>
    <div class="note">
      <b>문맥이 길어지면서 판이 바뀌고 있다.</b> 100만 토큰 문맥에서는
      예시를 수백~수천 개 넣는 <em>many-shot</em>이 가능해졌고,
      이 영역에서는 앞서 말한 "정답이 중요하지 않다"는 성질이 사라진다 —
      예시가 많아질수록 <strong>실제로 대응 관계를 학습</strong>하는 쪽으로 옮겨가고,
      파인튜닝에 근접하는 성능을 보인다는 보고가 나왔다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>왜 중요한가</h2>
    <p>
      ICL이 가져온 실질적 변화는 <strong>배포 방식</strong>이다.
      과제마다 모델을 따로 학습시켜 배포하던 구조가,
      <em>하나의 모델에 서로 다른 프롬프트를 보내는</em> 구조로 바뀌었다.
      새 과제에 드는 비용이 학습 파이프라인에서 프롬프트 작성으로 내려왔다.
    </p>
    <p>
      더 넓게 보면, ICL은 <strong>사전학습이 무엇을 만들어냈는지</strong>에 대한 단서다.
      다음 토큰 예측만 시켰는데 "예시를 보고 규칙을 파악하는" 능력이 나왔다.
      이것이 명시적으로 학습된 것이 아니라 <em>부산물로 창발했다</em>는 점이
      이 현상을 흥미롭게 만든다.
    </p>
    <p>
      한 가지 관점은 이렇다. 인터넷 텍스트에는
      <em>같은 패턴이 반복되는 문서</em>가 무수히 많다 — 목록, 표, 사전, 번역 대조.
      그런 문서에서 다음 토큰을 잘 맞히려면 <strong>앞에서 본 패턴을 이어가는 능력</strong>이 필요하다.
      그 능력이 곧 in-context learning이다.
      우리가 새 능력이라 부르는 것이, 모델 입장에서는
      <em>사전학습 때 하던 일을 계속하고 있는 것</em>일 수 있다.
    </p>
    <p>
      이 관점은 <a href="chain-of-thought.html">사고 사슬</a>과도 이어진다.
      거기서도 모델은 새 능력을 얻는 것이 아니라,
      <em>문맥에 놓인 것을 이어가는</em> 같은 일을 다른 형태로 하고 있다.
    </p>
  </section>
"""

READING = [
    "Brown et al., <em>Language Models are Few-Shot Learners</em> (arXiv:2005.14165) — GPT-3. ICL 현상을 전면에 내세운 논문.",
    "Min et al., <em>Rethinking the Role of Demonstrations</em> (arXiv:2202.12837) — 무작위 라벨 실험.",
    "Olsson et al., <em>In-context Learning and Induction Heads</em> (Anthropic, 2022) — 귀납 헤드와 능력 도약의 시점 일치.",
    "von Oswald et al., <em>Transformers Learn In-Context by Gradient Descent</em> (arXiv:2212.07677) — 암묵적 경사하강 관점.",
    "Wei et al., <em>Larger language models do in-context learning differently</em> (arXiv:2303.03846) — 규모에 따라 결론이 뒤집히는 지점.",
    "Agarwal et al., <em>Many-Shot In-Context Learning</em> (arXiv:2404.11018) — 긴 문맥에서 예시 수를 늘렸을 때의 변화.",
]

write(
    "in-context-learning.html",
    title="In-Context Learning — 가중치를 건드리지 않는 학습",
    eyebrow="Application · Emergent Behavior · 2020–2026",
    h1="In-Context Learning",
    subtitle="가중치를 건드리지 않는 학습 — 배우는 게 아니라 고르는 것",
    dek=(
        "예시 몇 개를 프롬프트에 넣으면 모델이 새 과제를 한다. "
        "그래디언트도, 파라미터 갱신도 없다. "
        "예시의 <strong>라벨을 무작위로 망가뜨려도</strong> 성능이 거의 떨어지지 않는다는 실험이 있다 — "
        "예시는 정답을 가르치는 게 아니라 <em>무엇을 할지 지정하는 신호</em>에 가깝다. "
        "다만 모델이 커지고 예시가 많아지면 이 결론이 뒤집힌다."
    ),
    spec=[
        ("가중치 변화", "없음"),
        ("지속", "그 요청 동안만"),
        ("가장 중요한 것", "형식 · 라벨 공간"),
        ("추정 회로", "귀납 헤드"),
        ("비용", "매 요청마다 토큰"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

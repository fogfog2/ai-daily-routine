#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f1", panel="#e6e6e9", ink="#16171b", **{
    "ink-soft": "#4f5158", "ink-faint": "#7e8088", "rule": "#d1d1d6",
    "rule-strong": "#adadb4", "accent": "#2e4f8a", "accent-fill": "#dde3f2",
    "accent-line": "#5170b0", "muted": "#84868c", "muted-fill": "#dfe0e3", "warn": "#a3452a",
})
DARK = dict(paper="#101115", panel="#18191e", ink="#e6e7ec", **{
    "ink-soft": "#a2a4ac", "ink-faint": "#757881", "rule": "#212227", "rule-strong": "#383a44",
    "accent": "#8aa8e8", "accent-fill": "#161d33", "accent-line": "#5470b0",
    "muted": "#86888f", "muted-fill": "#1a1b1f", "warn": "#e0855e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>점수가 오르는 것과 능력이 오르는 것</h2>
    <p>
      모델을 평가하려면 숫자가 필요하다. 그런데 숫자가 생기는 순간
      <strong>그 숫자를 올리는 것 자체가 목표</strong>가 된다.
      경제학의 굿하트 법칙이 말하는 바 그대로다 —
      <em>측정값이 목표가 되면 좋은 측정값이기를 그친다.</em>
    </p>
    <p>
      LLM 평가는 이 문제를 특히 심하게 겪는다. 이유가 셋이다.
    </p>
    <ul>
      <li><strong>학습 데이터가 인터넷 전체다.</strong> 벤치마크 문제가 그 안에 들어 있을 가능성이 상시 존재한다.</li>
      <li><strong>출력이 자유 형식이다.</strong> 정답이 하나로 정해지지 않는 과제가 많아 채점 자체가 어렵다.</li>
      <li><strong>능력의 범위가 넓다.</strong> 하나의 점수로 요약하려는 시도 자체가 무리다.</li>
    </ul>
    <p>
      그래서 벤치마크를 읽을 때 던져야 할 질문은
      "몇 점인가"가 아니라 <strong>"이 점수가 무엇을 재고 있는가"</strong>다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>오염 — 답을 이미 본 시험</h2>
    <p>
      가장 흔하고 가장 다루기 어려운 문제가 <strong>데이터 오염</strong>이다.
      벤치마크 문제와 정답이 학습 데이터에 섞여 들어가면,
      모델은 푸는 것이 아니라 <em>기억을 인출</em>한다. 점수는 오르지만 능력은 그대로다.
    </p>
    <p>
      벤치마크가 공개돼 있으므로 오염은 사실상 시간 문제다.
      GitHub 저장소, 논문, 블로그 해설, 토론 게시판에 문제와 답이 퍼진다.
      다음 모델의 크롤링에 그것이 들어간다.
    </p>
    <div class="eq">
      <span class="cap">오염을 의심하게 하는 신호들</span>
      <div class="line">· 학습 컷오프 <strong>이전</strong> 문제에서만 유난히 강하다</div>
      <div class="line">· 같은 난이도의 <strong>새로 만든</strong> 문제에서 성능이 급락한다</div>
      <div class="line">· 문제를 바꿔 쓰거나 숫자만 바꾸면 성능이 떨어진다</div>
      <div class="line">· 보기 순서를 섞으면 정확도가 크게 흔들린다</div>
      <div class="line">· 문제의 <strong>앞부분만 주면 뒷부분을 이어서 생성</strong>한다 ← 결정적</div>
    </div>
    <p>
      마지막 신호가 가장 직접적이다. 모델에게 벤치마크 문제의 일부만 주고
      나머지를 이어 쓰게 했을 때 원문을 그대로 복원한다면, 그 문제를 본 것이다.
    </p>
    <div class="note">
      <b>완전한 제거는 불가능에 가깝다.</b> 학습 데이터에서 벤치마크와 겹치는 문서를
      걸러내는 작업(decontamination)이 표준 절차가 됐지만,
      바꿔 쓴 형태나 번역본, 부분 인용까지 잡아내기는 어렵다.
      그래서 최근에는 <em>비공개 테스트셋</em>이나 <strong>학습 컷오프 이후에 만들어진 문제</strong>로
      평가하는 방식이 신뢰를 얻는다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>포화 — 다 맞히면 구분이 안 된다</h2>
    <p>
      두 번째 문제는 <strong>포화</strong>다. 벤치마크가 어려웠다가
      모델이 좋아지면서 점수가 상한에 붙는다. 90%대에 몰리면
      <em>모델 간 차이를 더 이상 구분하지 못한다</em>.
    </p>
    <p>
      게다가 상한 근처에서는 <strong>남은 오답이 대부분 벤치마크 자체의 오류</strong>인 경우가 많다.
      라벨이 틀렸거나, 문제가 모호하거나, 답이 여러 개인 문항들이다.
      그 구간의 점수 차이는 능력 차이가 아니라 노이즈에 가깝다.
    </p>
    <p>
      대응은 <em>계속 더 어려운 것을 만드는 것</em>이었다.
      그런데 이 순환에도 한계가 있다 —
      난이도를 올리다 보면 <strong>사람도 풀기 어려운 전문 문제</strong>가 되고,
      그것이 실제 사용 상황을 대표하는지는 별개의 문제가 된다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="벤치마크 포화 곡선과 평가 방식의 층위. 새 벤치마크가 나오면 몇 년 안에 점수가 상한에 붙어 구분력을 잃는 순환이 반복되며, 그에 따라 평가 방식도 정답 대조에서 심판 모델과 사람 비교로 옮겨간다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">포화의 순환</text>

            <line x1="52" y1="34" x2="52" y2="140" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <line x1="52" y1="140" x2="300" y2="140" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="34" y="42" font-size="8" fill="var(--ink-faint)">100</text>
            <text x="38" y="144" font-size="8" fill="var(--ink-faint)">0</text>
            <text x="176" y="158" text-anchor="middle" font-size="8" fill="var(--ink-faint)">시간 →</text>

            <line x1="52" y1="44" x2="300" y2="44" stroke="var(--warn)" stroke-width="1" stroke-dasharray="3 3"/>
            <text x="256" y="40" font-size="7.5" fill="var(--warn)">상한 · 구분력 상실</text>

            <path d="M58 128 C 90 120, 110 70, 150 52 C 175 44, 200 44, 296 44" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <circle cx="58" cy="128" r="3" fill="var(--accent)"/>
            <text x="58" y="120" font-size="7.5" fill="var(--ink-faint)">출시</text>
            <circle cx="180" cy="45" r="3" fill="var(--warn)"/>
            <text x="184" y="60" font-size="7.5" fill="var(--warn)">포화</text>

            <text x="52" y="180" font-size="8.5" fill="var(--ink-faint)">상한 근처의 남은 오답은 대부분</text>
            <text x="52" y="193" font-size="8.5" fill="var(--warn)">벤치마크 자체의 라벨 오류·모호한 문항</text>
            <text x="52" y="212" font-size="8.5" fill="var(--ink-faint)">→ 그 구간의 점수 차는 능력 차가 아니다</text>

            <line x1="340" y1="26" x2="340" y2="216" stroke="var(--rule)" stroke-width="1"/>

            <text x="366" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">평가 방식의 층위</text>

            <rect x="366" y="30" width="290" height="40" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="376" y="46" font-size="8.5" fill="var(--accent)">① 정답 대조 — 객관식·수학·코드 실행</text>
            <text x="376" y="60" font-size="8" fill="var(--ink-faint)">싸고 재현 가능 · 좁은 능력만 잰다 · 오염에 취약</text>

            <rect x="366" y="78" width="290" height="40" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="376" y="94" font-size="8.5" fill="var(--ink-soft)">② 심판 모델 — LLM 이 채점</text>
            <text x="376" y="108" font-size="8" fill="var(--ink-faint)">자유 형식 가능 · 길이·문체·자기 선호 편향</text>

            <rect x="366" y="126" width="290" height="40" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="376" y="142" font-size="8.5" fill="var(--ink-soft)">③ 사람 비교 — 블라인드 대결·Elo</text>
            <text x="376" y="156" font-size="8" fill="var(--ink-faint)">실제 선호 반영 · 느리고 비쌈 · 취향 편향</text>

            <text x="366" y="186" font-size="8.5" fill="var(--accent)">아래로 갈수록 현실에 가깝고 비싸진다.</text>
            <text x="366" y="202" font-size="8.5" fill="var(--ink-faint)">어느 하나로 충분하지 않아 대개 함께 쓴다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        벤치마크의 수명은 유한하다. 출시 → 경쟁 → 포화 → 새 벤치마크의 순환이 반복된다.
        그래서 <strong>절대 점수보다 어떤 조건에서 측정됐는지</strong>가 중요하고,
        오래된 벤치마크의 높은 점수는 그 자체로는 별 정보가 되지 못한다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>심판 모델 — 편리하고 편향된다</h2>
    <p>
      자유 형식 출력을 채점하려면 사람이 읽어야 한다. 느리고 비싸다.
      그래서 <strong>LLM을 심판으로 쓰는 방식</strong>이 널리 퍼졌다.
      두 답을 주고 어느 쪽이 나은지 고르게 하거나, 기준을 주고 점수를 매기게 한다.
    </p>
    <p>
      사람 판정과의 일치율이 높게 보고되지만, <strong>알려진 편향</strong>이 여럿이다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>편향</th><th>내용</th><th>완화</th></tr>
        </thead>
        <tbody>
          <tr><td>위치 편향</td><td>먼저 제시된 답을 선호</td><td class="hi">순서를 바꿔 두 번 평가</td></tr>
          <tr><td>길이 편향</td><td>긴 답을 더 좋게 평가</td><td>길이 통제 지표 사용</td></tr>
          <tr><td>자기 선호</td><td class="hi">자기가 생성한 답을 선호</td><td>다른 계열 모델로 채점</td></tr>
          <tr><td>문체 편향</td><td>목록·소제목이 있으면 우대</td><td>기준을 명시적으로 제시</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>자기 선호</strong>가 특히 성가시다.
      같은 회사 모델로 채점하면 결과가 그쪽에 유리하게 나올 수 있으므로,
      벤치마크 발표에서 <em>누가 심판이었는지</em>를 확인해야 한다.
    </p>
    <div class="note">
      <b>길이 편향은 평가와 학습 양쪽에 걸쳐 있다.</b>
      <a href="dpo-alignment.html">선호 학습</a>에서 답변이 길어지는 현상과 같은 뿌리다.
      사람도 모델도 긴 답을 좋게 평가하는 경향이 있고,
      그것으로 학습하면 모델이 길어지고, 그 모델이 다시 평가에서 유리해진다.
      <em>순환이 강화된다</em>는 점이 문제의 핵심이다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>그래서 무엇을 봐야 하는가</h2>
    <p>
      공개 벤치마크의 한계가 분명해지면서 평가의 무게중심이 옮겨가고 있다.
    </p>
    <ul>
      <li><strong>비공개·동적 평가.</strong> 문제를 공개하지 않거나 주기적으로 교체한다. 오염을 구조적으로 막는다.</li>
      <li><strong>실행 기반 검증.</strong> 코드는 테스트를 돌려 통과 여부로 채점한다. 심판이 필요 없고 조작하기 어렵다.</li>
      <li><strong>실제 과제 벤치마크.</strong> 인위적 문제 대신 실제 이슈를 해결하게 하는 식으로, 사용 상황에 가까운 과제를 쓴다.</li>
      <li><strong>블라인드 대결.</strong> 사용자가 두 답을 비교해 투표하고 Elo로 순위를 매긴다. 실제 선호를 반영하지만 취향 편향이 섞인다.</li>
    </ul>
    <p>
      그럼에도 가장 중요한 조언은 단순하다 —
      <strong>자기 과제로 직접 평가하라.</strong>
      공개 벤치마크는 모델을 <em>후보로 좁히는 데</em> 쓰고,
      최종 판단은 실제 데이터와 실제 요구사항으로 만든 자체 평가셋으로 해야 한다.
      수십 개의 대표 사례만 있어도 공개 순위표보다 훨씬 많은 것을 알려준다.
    </p>
    <p>
      마지막으로 짚을 것은 <strong>무엇이 측정되지 않는가</strong>다.
      대부분의 벤치마크는 정확도를 재고, 비용·지연·일관성·거절 행동·
      긴 대화에서의 안정성 같은 것은 잘 재지 않는다.
      실제 서비스에서 문제가 되는 것은 오히려 이쪽인 경우가 많다.
      <em>순위표에 없는 축을 스스로 정의하는 것</em>이 평가 설계의 실질이다.
    </p>
  </section>
"""

READING = [
    "Zheng et al., <em>Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena</em> (arXiv:2306.05685) — 심판 모델의 신뢰도와 편향.",
    "Sainz et al., <em>NLP Evaluation in trouble: On the Need to Measure LLM Data Contamination</em> (arXiv:2310.18018) — 오염 탐지 방법론.",
    "Zhou et al., <em>Don't Make Your LLM an Evaluation Benchmark Cheater</em> (arXiv:2311.01964) — 오염이 점수에 미치는 정량적 영향.",
    "Jimenez et al., <em>SWE-bench: Can Language Models Resolve Real-World GitHub Issues?</em> (arXiv:2310.06770) — 실행 기반·실제 과제 평가.",
    "Dubois et al., <em>Length-Controlled AlpacaEval</em> (arXiv:2404.04475) — 길이 편향을 통제한 승률.",
    "Liang et al., <em>Holistic Evaluation of Language Models</em> (arXiv:2211.09110) — 정확도 외의 축을 함께 재는 시도.",
]

write(
    "evaluation-benchmarks.html",
    title="평가와 벤치마크 — 무엇을 재고 있는가",
    eyebrow="Evaluation · Measurement · 2021–2026",
    h1="평가와 벤치마크",
    subtitle="무엇을 재고 있는가 — 점수가 오르는 것과 능력이 오르는 것",
    dek=(
        "숫자가 생기는 순간 그 숫자를 올리는 것이 목표가 된다. "
        "학습 데이터가 인터넷 전체라 <strong>벤치마크 문제가 이미 그 안에</strong> 있을 수 있고, "
        "어려웠던 시험은 몇 년이면 포화해 구분력을 잃는다. "
        "그래서 물어야 할 것은 \"몇 점인가\"가 아니라 <em>\"이 점수가 무엇을 재고 있는가\"</em>다."
    ),
    spec=[
        ("근본 문제", "굿하트 법칙"),
        ("오염", "사실상 시간 문제"),
        ("결정적 신호", "문제 뒷부분 복원"),
        ("심판 모델", "위치·길이·자기 선호 편향"),
        ("가장 나은 방법", "자기 과제로 직접"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

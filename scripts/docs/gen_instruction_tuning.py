#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff0f0", panel="#e5e7e6", ink="#14181a", **{
    "ink-soft": "#4d5557", "ink-faint": "#7c8486", "rule": "#cfd2d2",
    "rule-strong": "#abafaf", "accent": "#1f5f6b", "accent-fill": "#d9eaed",
    "accent-line": "#3c8794", "muted": "#83888c", "muted-fill": "#dee1e2", "warn": "#a04b28",
})
DARK = dict(paper="#0f1213", panel="#171a1b", ink="#e4e9ea", **{
    "ink-soft": "#a1a9ab", "ink-faint": "#757d7f", "rule": "#212627", "rule-strong": "#373f41",
    "accent": "#5ec2d3", "accent-fill": "#10282d", "accent-line": "#357f8c",
    "muted": "#868c90", "muted-fill": "#191d1e", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>사전학습 모델은 부탁을 알아듣지 못한다</h2>
    <p>
      사전학습이 끝난 모델에게 <em>"프랑스의 수도는?"</em>이라고 물으면
      답 대신 이런 것이 나올 수 있다 — <em>"독일의 수도는? 이탈리아의 수도는?"</em>
    </p>
    <p>
      틀린 동작이 아니다. 모델은 <strong>배운 대로</strong> 하고 있다.
      학습 목표는 "다음 토큰을 맞히기"였고, 인터넷에서 저 문장 뒤에 자주 오는 것은
      답이 아니라 <em>비슷한 질문의 목록</em>이다. 퀴즈 문제지 같은 문서가 그렇게 생겼다.
    </p>
    <p>
      즉 사전학습 모델은 능력이 없는 게 아니라 <strong>무엇을 해달라는 요청인지 모른다</strong>.
      지식과 추론 능력은 가중치 안에 이미 들어 있는데,
      <em>"이건 질문이고 너는 답해야 한다"</em>는 형식을 모를 뿐이다.
    </p>
    <div class="note">
      <b>GPT-3 시절의 프롬프트 기교가 여기서 나왔다.</b>
      few-shot 예시를 잔뜩 넣어야 했던 이유는 모델을 <em>"질문-답변이 이어지는 문서"</em>의
      한가운데로 밀어 넣기 위해서였다. Instruction tuning은 이 일을
      <strong>프롬프트가 아니라 가중치에</strong> 새기는 단계다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>과제를 지시문으로 바꿔 쓰다</h2>
    <p>
      방법 자체는 단순하다. 기존의 수많은 NLP 데이터셋을
      <strong>자연어 지시문 형식으로 다시 쓰고</strong>, 그것으로 지도학습을 이어간다.
    </p>
    <div class="eq">
      <span class="cap">같은 데이터를 지시문으로 변환</span>
      <div class="line">원본 (감성 분류 데이터셋)</div>
      <div class="line">&nbsp;&nbsp;text: "이 영화 최고였다"&nbsp;&nbsp;label: 1</div>
      <div class="line">&nbsp;</div>
      <div class="line">변환 후</div>
      <div class="line">&nbsp;&nbsp;<strong>지시:</strong> 다음 리뷰의 감정이 긍정인지 부정인지 답하시오.</div>
      <div class="line">&nbsp;&nbsp;<strong>입력:</strong> 이 영화 최고였다</div>
      <div class="line">&nbsp;&nbsp;<strong>출력:</strong> 긍정</div>
    </div>
    <p>
      손실 함수는 사전학습과 <strong>완전히 같다</strong> — 다음 토큰 예측이다.
      바뀐 것은 데이터의 <em>형식</em>뿐이다.
      다만 보통 <strong>출력 부분에만 손실을 건다</strong>(지시문과 입력은 조건으로만 쓴다).
    </p>
    <p>
      결정적 발견은 <strong>일반화</strong>였다.
      FLAN 논문은 60여 개 과제로 학습한 모델이
      <em>학습에 없던 과제</em>에서도 지시를 따른다는 것을 보였다.
      개별 과제를 배운 게 아니라 <strong>"지시를 따른다"는 메타 능력</strong>을 배운 것이다.
    </p>
    <p>
      과제 종류가 많을수록 이 일반화가 좋아진다는 것도 확인됐다.
      데이터 양보다 <strong>과제 다양성</strong>이 더 중요하다는 결과가 반복 보고됐다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>양이 아니라 질 — LIMA의 반례</h2>
    <p>
      초기 흐름은 과제와 데이터를 계속 늘리는 쪽이었다.
      그런데 <strong>LIMA</strong>가 흥미로운 반례를 내놓았다 —
      <em>엄선한 1,000개</em>의 예시만으로 파인튜닝했는데 품질이 매우 좋았다.
    </p>
    <p>
      저자들의 해석이 "표면 정렬 가설"이다.
      <strong>지식과 능력은 사전학습에서 거의 다 획득되고,
      정렬은 그중 어떤 형식으로 답할지를 고르는 얇은 층에 불과하다</strong>는 것이다.
      그렇다면 필요한 것은 많은 데이터가 아니라 <em>일관되고 좋은 소수의 예시</em>다.
    </p>
    <div class="note">
      <b>다만 이 가설은 논쟁적이다.</b> 소수 데이터로도 <em>말투와 형식</em>은 확실히 잡히지만,
      복잡한 추론이나 다단계 도구 사용 같은 능력까지 그렇게 얻어지는지는 별개다.
      실무의 절충안은 <strong>다양성은 넓게, 품질은 높게, 총량은 과하지 않게</strong> 쪽으로 모였다.
    </div>
    <p>
      데이터를 만드는 방법도 갈라진다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방식</th><th>만드는 법</th><th>장단</th></tr>
        </thead>
        <tbody>
          <tr><td>사람 작성</td><td>라벨러가 직접 지시·답변 작성</td><td>품질 높음 · 비쌈</td></tr>
          <tr><td>기존 데이터 변환</td><td>NLP 데이터셋을 지시문화 (FLAN)</td><td class="hi">싸고 다양 · 문체가 딱딱</td></tr>
          <tr><td>모델 생성 (self-instruct)</td><td>LLM에게 지시·답변을 만들게 함</td><td class="hi">확장 쉬움 · 오류 전파</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      세 번째 방식은 값싸지만 위험이 있다. 생성 모델의 편향과 실수가 그대로 데이터에 들어가고,
      그것으로 학습한 모델이 다시 데이터를 만들면 오류가 누적된다.
      또 강한 모델의 출력을 베끼면 <em>말투는 닮지만 사실성은 따라오지 않는다</em>는 분석도 있다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>정렬 파이프라인에서의 위치</h2>
    <p>
      Instruction tuning은 단독으로 쓰이기보다 <strong>정렬의 첫 단계</strong>로 놓인다.
      전체 흐름에서의 자리를 보면 역할이 분명해진다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 216" role="img" aria-label="정렬 파이프라인 도식. 사전학습된 기반 모델이 instruction tuning을 거쳐 지시를 따르는 모델이 되고, 이어 선호 학습을 거쳐 사람이 선호하는 방식으로 답하는 모델이 된다. 각 단계에서 필요한 데이터 종류와 얻는 능력이 다르다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="it-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <rect x="26" y="40" width="150" height="56" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="101" y="62" text-anchor="middle" font-size="10" fill="var(--ink-soft)">기반 모델</text>
            <text x="101" y="78" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">다음 토큰 예측</text>

            <path d="M180 68 L212 68" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#it-a)"/>
            <text x="196" y="60" text-anchor="middle" font-size="8" fill="var(--ink-faint)">SFT</text>

            <rect x="216" y="40" width="150" height="56" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.8"/>
            <text x="291" y="62" text-anchor="middle" font-size="10" fill="var(--accent)">지시를 따르는 모델</text>
            <text x="291" y="78" text-anchor="middle" font-size="8.5" fill="var(--accent)">Instruction Tuning</text>

            <path d="M370 68 L402 68" stroke="var(--accent-line)" stroke-width="1.5" marker-end="url(#it-a)"/>
            <text x="386" y="60" text-anchor="middle" font-size="8" fill="var(--ink-faint)">선호</text>

            <rect x="406" y="40" width="150" height="56" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="481" y="62" text-anchor="middle" font-size="10" fill="var(--ink-soft)">정렬된 모델</text>
            <text x="481" y="78" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">RLHF · DPO</text>

            <line x1="26" y1="118" x2="674" y2="118" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="140" font-size="9" letter-spacing="1.1" fill="var(--ink-faint)">데이터</text>
            <text x="101" y="158" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">웹 텍스트</text>
            <text x="101" y="172" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">수조 토큰</text>

            <text x="291" y="158" text-anchor="middle" font-size="8.5" fill="var(--accent)">(지시, 답변) 쌍</text>
            <text x="291" y="172" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">수천 ~ 수십만</text>

            <text x="481" y="158" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">(선택, 기각) 쌍</text>
            <text x="481" y="172" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">비교 판단</text>

            <text x="26" y="196" font-size="9" letter-spacing="1.1" fill="var(--ink-faint)">얻는 것</text>
            <text x="101" y="212" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">지식 · 언어 능력</text>
            <text x="291" y="212" text-anchor="middle" font-size="8.5" fill="var(--accent)">형식 · 요청 이해</text>
            <text x="481" y="212" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">뉘앙스 · 무해성</text>

            <rect x="580" y="132" width="94" height="70" fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="3 2"/>
            <text x="627" y="152" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">SFT 는</text>
            <text x="627" y="166" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">"무엇을 할지"</text>
            <text x="627" y="184" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">선호 학습은</text>
            <text x="627" y="198" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">"어떻게 할지"</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        두 단계의 역할이 다르다.
        SFT는 <strong>모범 답안을 따라 하게</strong> 해서 형식을 잡고,
        선호 학습은 <strong>둘 중 나은 쪽을 고르게</strong> 해서 뉘앙스를 잡는다.
        SFT만으로는 "이 답이 저 답보다 왜 나은지"를 가르칠 수 없다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>부작용 — 흉내와 망각</h2>
    <p>
      Instruction tuning에는 두 가지 알려진 부작용이 있다.
    </p>
    <p>
      <strong>모방의 함정.</strong> SFT는 <em>답변을 그대로 따라 하게</em> 하는 학습이다.
      모범 답안에 모델이 실제로 모르는 사실이 들어 있으면,
      모델은 <strong>"모르는 것도 자신 있게 말하는 법"</strong>을 배운다.
      환각을 오히려 강화할 수 있다는 지적이 여기서 나온다.
      RLHF 논문들이 "모른다고 답하는 것"을 선호 데이터로 가르치려는 이유이기도 하다.
    </p>
    <p>
      <strong>정렬 세금(alignment tax).</strong> 정렬 단계를 거치면
      일부 벤치마크 성능이 <em>떨어지는</em> 현상이 관찰된다.
      좁은 형식에 맞추느라 사전학습에서 얻은 다양성 일부를 잃는 것이다.
      사전학습 데이터를 일정 비율 섞어 학습하는 식으로 완화한다.
    </p>
    <p>
      마지막으로, 형식 자체가 남기는 흔적도 있다.
      학습 데이터의 답변이 대체로 길고 목록을 좋아하면 모델도 그렇게 답한다.
      "불릿 포인트로 장황하게 답하는 챗봇" 같은 인상은
      구조적 필연이 아니라 <em>학습 데이터의 문체가 그대로 옮겨온 결과</em>다.
    </p>
    <p>
      한 문장으로 줄이면, instruction tuning은 <em>능력을 만드는 단계가 아니라
      이미 있는 능력에 접근하는 문을 내는 단계</em>다.
      그래서 값싸고, 그래서 데이터의 성격이 그대로 모델의 성격이 된다.
    </p>
  </section>
"""

READING = [
    "Wei et al., <em>Finetuned Language Models Are Zero-Shot Learners</em> (arXiv:2109.01652) — FLAN. 과제 다양성과 미학습 과제 일반화.",
    "Ouyang et al., <em>Training language models to follow instructions with human feedback</em> (arXiv:2203.02155) — InstructGPT. SFT + RLHF 파이프라인.",
    "Zhou et al., <em>LIMA: Less Is More for Alignment</em> (arXiv:2305.11206) — 1,000 예시와 표면 정렬 가설.",
    "Wang et al., <em>Self-Instruct: Aligning Language Models with Self-Generated Instructions</em> (arXiv:2212.10560) — 모델로 지시 데이터 생성.",
    "Chung et al., <em>Scaling Instruction-Finetuned Language Models</em> (arXiv:2210.11416) — 과제 수·모델 크기에 따른 확장.",
    "Gudibande et al., <em>The False Promise of Imitating Proprietary LLMs</em> (arXiv:2305.15717) — 흉내가 문체만 옮기는 문제.",
]

write(
    "instruction-tuning.html",
    title="Instruction Tuning — 지시를 따르게 만들기",
    eyebrow="Alignment · Supervised Fine-Tuning · 2021–2026",
    h1="Instruction Tuning",
    subtitle="지시를 따르게 만들기 — 능력이 아니라 문을 내는 단계",
    dek=(
        "사전학습 모델에게 \"프랑스의 수도는?\"이라 물으면 "
        "답 대신 <em>비슷한 질문 목록</em>이 나올 수 있다. 틀린 게 아니라 배운 대로 하는 것이다. "
        "지식은 이미 가중치에 있고, 없는 것은 <strong>\"이건 요청이고 답해야 한다\"는 형식</strong>이다. "
        "Instruction tuning은 그 형식을 프롬프트가 아니라 가중치에 새긴다."
    ),
    spec=[
        ("손실", "사전학습과 동일"),
        ("바뀌는 것", "데이터 형식뿐"),
        ("중요한 것", "양보다 과제 다양성"),
        ("LIMA", "엄선 1,000개"),
        ("부작용", "모방의 함정 · 정렬 세금"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)

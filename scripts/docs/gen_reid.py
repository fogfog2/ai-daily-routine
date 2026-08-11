#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ef", panel="#e6e8e4", ink="#161a15", **{
    "ink-soft": "#4f574d", "ink-faint": "#7e867b", "rule": "#d1d5cf",
    "rink-strong": "#adb2aa", "rule-strong": "#adb2aa", "accent": "#39632a",
    "accent-fill": "#dfebd8", "accent-line": "#5c8c46",
    "muted": "#83888c", "muted-fill": "#dee1e1", "warn": "#a04b28",
})
DARK = dict(paper="#101210", panel="#181b17", ink="#e6eae4", **{
    "ink-soft": "#a5aca1", "ink-faint": "#7a8176", "rule": "#222720", "rule-strong": "#38402f",
    "accent": "#83c964", "accent-fill": "#152615", "accent-line": "#5a8c42",
    "muted": "#868d90", "muted-fill": "#191f1c", "warn": "#e0855c",
})
LIGHT.pop("rink-strong", None)

BODY = r"""
  <section>
    <h2><span class="n">01</span>얼굴이 보이지 않을 때</h2>
    <p>
      매장 A 카메라에 찍힌 사람이 30분 뒤 매장 B 카메라에 나타났다. 같은 사람인가.
      이것이 <strong>재식별</strong>(Re-Identification)이 푸는 문제다.
    </p>
    <p>
      얼굴 인식과 다른 점이 있다. <strong>얼굴이 안 보이는 경우가 대부분</strong>이다.
      감시 카메라는 위에서 비스듬히 찍고, 사람은 등을 돌리고 있고, 해상도는 낮다.
      쓸 수 있는 단서는 옷차림·체형·자세·소지품 같은 <em>전신의 외형</em>뿐이다.
    </p>
    <p>
      그리고 이 단서들은 하나같이 불안정하다.
    </p>
    <ul>
      <li><strong>뷰가 바뀐다.</strong> 앞모습과 뒷모습은 픽셀 수준에서 완전히 다르다</li>
      <li><strong>조명이 바뀐다.</strong> 실내 형광등과 실외 햇빛에서 같은 옷의 색이 달라진다</li>
      <li><strong>가려진다.</strong> 다른 사람이나 기둥에 몸 절반이 가린다</li>
      <li><strong>자세가 바뀐다.</strong> 서 있을 때와 앉아 있을 때의 실루엣이 다르다</li>
    </ul>
    <p>
      즉 <a href="metric-learning.html">메트릭 러닝</a>이 말한 어려운 쪽 —
      <em>겉모습이 달라도 같다고 해야 하는</em> 상황이 기본값인 과제다.
      Re-ID 가 메트릭 러닝의 실전 시험대로 자주 쓰이는 이유다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>닫힌 집합이 아니다</h2>
    <p>
      과제 구성을 정확히 보아야 방법이 이해된다.
      Re-ID 는 <strong>검색 문제</strong>로 정식화된다.
    </p>
    <div class="eq">
      <span class="cap">Re-ID 의 평가 구성</span>
      <div class="line">query&nbsp;&nbsp;&nbsp;&nbsp; 찾고 싶은 사람의 이미지 1장</div>
      <div class="line">gallery&nbsp;&nbsp; 후보 이미지 수천~수만 장 (다른 카메라·다른 시간)</div>
      <div class="line">&nbsp;</div>
      <div class="line">→ gallery 를 유사도 순으로 정렬</div>
      <div class="line">→ 상위에 같은 사람이 있는가</div>
    </div>
    <p>
      결정적인 제약은 <strong>학습에 없던 사람을 찾아야 한다</strong>는 것이다.
      학습 데이터의 인물 ID 와 테스트의 인물 ID 는 <em>겹치지 않는다</em>.
      분류기로 풀 수 없는 구조이고, 그래서 임베딩을 학습해 거리로 판정한다.
    </p>
    <div class="eq">
      <span class="cap">평가 지표 — 두 가지를 함께 본다</span>
      <div class="line">Rank-1&nbsp;&nbsp; 1등이 정답인 비율&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 자동 판정에 중요</div>
      <div class="line">mAP&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 정답들의 순위 전반&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 검색 품질에 중요</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 같은 사람의 이미지가 gallery 에 여러 장 있으므로</div>
      <div class="line">// 하나만 맞히는 것과 여럿을 위로 올리는 것은 다르다</div>
    </div>
    <p>
      Rank-1 만 높고 mAP 가 낮으면 <em>운 좋게 한 장만 잘 맞히는</em> 모델이다.
      실무에서 후보를 추려 사람이 확인하는 구성이라면 mAP 가 더 중요하다.
      최종 판정에는 <a href="similarity-threshold.html">임계값</a>이 따로 필요하다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>전역 벡터 하나로는 부족하다</h2>
    <p>
      가장 단순한 구성은 백본에 전역 평균 풀링을 붙여 벡터 하나를 뽑는 것이다.
      잘 작동하지만 <strong>가림에 약하다</strong>. 몸 절반이 가려지면 평균이 통째로 오염된다.
    </p>
    <p>
      해법은 <strong>부분으로 나누는 것</strong>이다. 사람은 대체로 세로로 서 있으므로
      특징 맵을 <em>가로 줄무늬</em>로 잘라 부분마다 벡터를 뽑고 이어 붙인다.
      머리·상의·하의·신발이 대략 분리되는 셈이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="재식별에서 전역 특징과 부분 특징의 차이. 전역 평균 풀링은 가림이 있으면 벡터 전체가 오염되지만, 가로 줄무늬로 나눠 부분별 특징을 뽑으면 가려진 부분만 영향을 받고 나머지는 살아남는다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="rd-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">전역 풀링 — 가림이 전체를 오염시킨다</text>

            <rect x="30" y="34" width="52" height="128" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <ellipse cx="56" cy="52" rx="11" ry="13" fill="var(--ink-soft)" opacity="0.35"/>
            <rect x="42" y="68" width="28" height="42" fill="var(--ink-soft)" opacity="0.3"/>
            <rect x="44" y="112" width="24" height="40" fill="var(--ink-soft)" opacity="0.22"/>
            <rect x="30" y="110" width="52" height="52" fill="var(--warn)" opacity="0.3"/>
            <text x="56" y="176" text-anchor="middle" font-size="8" fill="var(--warn)">하반신 가림</text>

            <path d="M90 98 L116 98" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#rd-a)"/>
            <text x="103" y="90" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">GAP</text>

            <rect x="122" y="88" width="80" height="20" fill="var(--warn)" opacity="0.28" stroke="var(--warn)" stroke-width="1.3"/>
            <text x="162" y="102" text-anchor="middle" font-size="8" fill="var(--ink)">벡터 1개</text>
            <text x="122" y="126" font-size="8" fill="var(--warn)">평균에 가림이 섞여</text>
            <text x="122" y="139" font-size="8" fill="var(--warn)">전체가 흐트러진다</text>

            <line x1="232" y1="26" x2="232" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="256" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">부분 특징 — 살아남는 부분이 있다</text>

            <rect x="262" y="34" width="52" height="128" fill="var(--muted-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <ellipse cx="288" cy="52" rx="11" ry="13" fill="var(--ink-soft)" opacity="0.35"/>
            <rect x="274" y="68" width="28" height="42" fill="var(--ink-soft)" opacity="0.3"/>
            <rect x="276" y="112" width="24" height="40" fill="var(--ink-soft)" opacity="0.22"/>
            <rect x="262" y="110" width="52" height="52" fill="var(--warn)" opacity="0.3"/>
            <g stroke="var(--accent-line)" stroke-width="1.1" stroke-dasharray="3 2">
              <line x1="262" y1="66" x2="314" y2="66"/>
              <line x1="262" y1="98" x2="314" y2="98"/>
              <line x1="262" y1="130" x2="314" y2="130"/>
            </g>

            <path d="M322 98 L346 98" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#rd-a)"/>

            <g>
              <rect x="352" y="40" width="66" height="18" fill="var(--accent)" opacity="0.5" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="426" y="53" font-size="7.5" fill="var(--accent)">머리 ✓</text>
              <rect x="352" y="70" width="66" height="18" fill="var(--accent)" opacity="0.5" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="426" y="83" font-size="7.5" fill="var(--accent)">상의 ✓</text>
              <rect x="352" y="100" width="66" height="18" fill="var(--warn)" opacity="0.3" stroke="var(--warn)" stroke-width="1"/>
              <text x="426" y="113" font-size="7.5" fill="var(--warn)">하의 ✗</text>
              <rect x="352" y="130" width="66" height="18" fill="var(--warn)" opacity="0.3" stroke="var(--warn)" stroke-width="1"/>
              <text x="426" y="143" font-size="7.5" fill="var(--warn)">신발 ✗</text>
            </g>

            <text x="256" y="176" font-size="8.5" fill="var(--accent)">가려진 부분만 버리고 나머지로 판정한다</text>
            <text x="256" y="190" font-size="8" fill="var(--ink-faint)">부분별 벡터를 이어 붙이거나 가중 평균한다</text>

            <line x1="24" y1="206" x2="674" y2="206" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="226" font-size="8.5" fill="var(--ink-soft)">전제: 사람은 세로로 서 있고 신체 순서가 일정하다 — <tspan fill="var(--warn)">앉거나 누우면 이 가정이 깨진다</tspan></text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>PCB</strong> 계열이 이 구조를 정착시켰다.
        단순한 가로 분할인데도 큰 폭의 성능 향상을 냈다 —
        <em>사람이 세로로 서 있다</em>는 강한 사전지식을 구조에 넣은 것이다.
        자세 추정으로 관절 위치를 받아 정렬하는 방식이 더 정확하지만, 그만큼 무겁고 의존이 늘어난다.
      </figcaption>
    </figure>

    <p>
      손실은 대개 <strong>둘을 함께</strong> 쓴다 —
      ID 분류 손실(학습 데이터의 인물을 분류)과 삼중항 손실(거리를 직접 조정)이다.
      전자는 학습을 안정시키고 후자는 임베딩 공간의 모양을 잡는다.
      여기에 라벨 스무딩과 BNNeck 같은 장치를 더한
      <em>강한 기준선</em>이 정립돼, 화려한 구조보다 잘 조율된 기본이 낫다는 결과가 반복 보고됐다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>재순위화 — 이웃을 보고 다시 정렬한다</h2>
    <p>
      Re-ID 에는 다른 검색 과제에 없는 후처리가 하나 있다. <strong>재순위화</strong>다.
    </p>
    <p>
      발상은 이렇다. query 와 어떤 후보가 진짜 같은 사람이라면,
      <em>둘의 이웃 목록도 서로 닮아야 한다.</em>
      단순히 "가깝다"가 아니라 <strong>"서로를 이웃으로 여기는가"</strong>를 본다.
    </p>
    <div class="eq">
      <span class="cap">k-reciprocal 재순위화</span>
      <div class="line">1) query 의 상위 k 이웃 집합 R(q, k) 을 구한다</div>
      <div class="line">2) 각 후보 g 에 대해 R(g, k) 도 구한다</div>
      <div class="line">3) <strong>q ∈ R(g,k) 이고 g ∈ R(q,k)</strong> 이면 상호 이웃 — 신뢰도 높음</div>
      <div class="line">4) 두 집합의 겹침(Jaccard)으로 거리를 다시 계산해 정렬</div>
    </div>
    <p>
      효과가 크다. mAP 가 눈에 띄게 오르는 경우가 흔해 벤치마크에서 사실상 표준이 됐다.
      다만 <strong>gallery 전체를 알아야</strong> 계산할 수 있으므로
      실시간 스트리밍에는 그대로 쓰기 어렵다 — 배치 검색에 맞는 기법이다.
    </p>
    <div class="note">
      <b>이것이 벤치마크와 실무의 괴리를 만든다.</b> 논문의 mAP 에는 재순위화가 포함된 경우가 많은데,
      실제 시스템은 후보가 실시간으로 들어오므로 그 이득을 그대로 가져오지 못한다.
      수치를 볼 때 <em>재순위화 적용 여부</em>를 확인해야 하는 이유다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실무에서 무너지는 지점</h2>
    <p>
      Re-ID 는 벤치마크 성능과 현장 성능의 격차가 특히 큰 분야다. 이유가 분명하다.
    </p>
    <p>
      <strong>도메인 격차.</strong> 학습한 데이터셋의 카메라·조명·인구 구성과
      실제 설치 환경이 다르다. 벤치마크에서 90%를 내던 모델이 새 현장에서 크게 떨어지는 일이 흔하다.
      데이터셋을 바꿔 평가하는 <em>cross-domain</em> 설정에서 성능이 급락한다는 보고가 이를 뒷받침한다.
    </p>
    <p>
      <strong>옷이 단서라는 것.</strong> 대부분의 모델은 사실상 옷을 보고 판정한다.
      같은 사람이 옷을 갈아입으면 실패하고, <em>다른 사람이 비슷한 옷을 입으면</em> 오인한다.
      단체복을 입는 환경에서 특히 취약하다.
      옷 변화에 강건한 설정(clothes-changing Re-ID)이 별도 연구 주제가 된 이유다.
    </p>
    <p>
      <strong>시간·공간 제약을 안 쓴다.</strong> 순수 외형 모델은
      <em>1분 전 A 카메라에 있던 사람이 지금 500m 떨어진 B 카메라에 있을 수 없다</em>는
      상식을 모른다. 실무 시스템은 카메라 배치와 이동 시간을 제약으로 넣어 후보를 크게 줄인다.
      모델을 개선하는 것보다 이 제약이 더 큰 이득을 주는 경우가 많다.
    </p>
    <div class="note">
      <b>용도를 가려야 하는 기술이다.</b> Re-ID 는 본질적으로
      <em>특정 개인을 카메라 사이에서 추적하는</em> 능력이라 감시 목적과 분리하기 어렵다.
      데이터셋 수집 과정의 동의 문제로 <strong>공개 데이터셋이 철회된 사례</strong>도 있다.
      정확도를 올리는 일과 그것을 어디에 쓸지는 별개의 판단이고,
      후자를 공학이 대신 답해 주지 않는다.
    </div>
    <p>
      정리하면 Re-ID 는 <a href="metric-learning.html">메트릭 러닝</a>의 원리를
      가장 가혹한 조건에서 시험하는 과제다 —
      뷰·조명·가림이 전부 변하는데 같다고 해야 하고, 학습에 없던 사람을 다뤄야 한다.
      그래서 여기서 통하는 기법은 다른 매칭 문제에도 대체로 통한다.
    </p>
  </section>
"""

READING = [
    "Zheng et al., <em>Scalable Person Re-identification: A Benchmark</em> (ICCV 2015) — Market-1501. 평가 구성과 지표의 표준.",
    "Sun et al., <em>Beyond Part Models: Person Retrieval with Refined Part Pooling</em> (arXiv:1711.09349) — PCB. 가로 분할 부분 특징.",
    "Hermans et al., <em>In Defense of the Triplet Loss for Person Re-Identification</em> (arXiv:1703.07737) — batch-hard 삼중항.",
    "Zhong et al., <em>Re-ranking Person Re-identification with k-reciprocal Encoding</em> (arXiv:1701.08398) — 상호 이웃 재순위화.",
    "Luo et al., <em>Bag of Tricks and A Strong Baseline for Deep Person Re-identification</em> (arXiv:1903.07071) — 잘 조율된 기본이 강하다는 결과.",
    "Ye et al., <em>Deep Learning for Person Re-identification: A Survey and Outlook</em> (arXiv:2001.04193) — 도메인 격차와 열린 문제 정리.",
]

write(
    "person-reid.html",
    title="재식별 (Re-ID) — 다른 카메라의 같은 사람",
    eyebrow="Vision · Retrieval · 2015–2026",
    h1="재식별 (Re-ID)",
    subtitle="다른 카메라의 같은 사람 — 뷰도 조명도 다 바뀌는데",
    dek=(
        "얼굴이 보이지 않는다. 쓸 수 있는 것은 옷차림·체형·자세뿐인데 "
        "그마저 카메라가 바뀌면 함께 달라진다. "
        "게다가 <strong>학습에 없던 사람</strong>을 찾아야 한다 — 분류로는 풀리지 않는 구조다. "
        "메트릭 러닝의 어려운 쪽을 기본값으로 삼는 과제다."
    ),
    spec=[
        ("구성", "query → gallery 검색"),
        ("제약", "학습에 없던 인물"),
        ("지표", "Rank-1 · mAP"),
        ("구조", "부분 특징 (가로 분할)"),
        ("실무 난점", "도메인 격차 · 옷 의존"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

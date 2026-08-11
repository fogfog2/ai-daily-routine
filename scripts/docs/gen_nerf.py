#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f2", panel="#e5e5ea", ink="#16151c", **{
    "ink-soft": "#4f4d5a", "ink-faint": "#7e7c8a", "rule": "#d0cfd7",
    "rule-strong": "#acaab5", "accent": "#4a3a8c", "accent-fill": "#e0dcf2",
    "accent-line": "#6d5cb5", "muted": "#84868e", "muted-fill": "#dfe0e4", "warn": "#a04a28",
})
DARK = dict(paper="#101016", panel="#18181f", ink="#e6e5ee", **{
    "ink-soft": "#a3a1b0", "ink-faint": "#757383", "rule": "#212028", "rule-strong": "#383546",
    "accent": "#9d8ce8", "accent-fill": "#1b1836", "accent-line": "#6a5cb5",
    "muted": "#868892", "muted-fill": "#1a1a21", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>사진 몇 장에서 공간을 복원하기</h2>
    <p>
      <a href="depth-estimation.html">깊이 추정</a>은 <em>한 시점에서의 거리</em>를 답한다.
      그런데 여기서 한 걸음 더 나가면 다른 요구가 나온다 —
      <strong>찍지 않은 각도에서 본 모습</strong>을 만들어내는 것이다.
    </p>
    <p>
      물체를 여러 각도에서 찍은 사진 수십 장이 있다.
      이것으로 <em>중간 각도의 사진</em>을 만들 수 있을까.
      이 문제를 <strong>새 시점 합성</strong>(novel view synthesis)이라 한다.
    </p>
    <p>
      고전적 방법은 <a href="local-features.html">지역 특징 매칭</a>으로 3D 점을 복원하고
      메시를 만드는 것이었다. 잘 되지만 <em>반투명·반사·머리카락</em> 같은 것에 약하다.
      메시는 표면을 전제하는데 세상에는 표면으로 표현하기 어려운 것이 많다.
    </p>
    <div class="note">
      <b>표현 방식이 무엇을 담을 수 있는지 정한다.</b>
      메시는 <em>경계가 뚜렷한 불투명 표면</em>에 최적화돼 있다.
      연기·유리·잔디처럼 <strong>부피를 가진 것</strong>은 표면으로 근사하면 무너진다.
      그래서 다른 표현이 필요했고, 그 답이 <em>공간 자체를 함수로 보는</em> 것이었다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>NeRF — 장면을 신경망에 담는다</h2>
    <p>
      NeRF 의 발상은 급진적이다. 3D 모델을 만드는 대신,
      <strong>공간의 모든 점에 대해 색과 밀도를 답하는 함수</strong>를 학습한다.
    </p>
    <div class="eq">
      <span class="cap">NeRF — 5차원 입력, 4차원 출력</span>
      <div class="line">F<sub>θ</sub>( x, y, z, θ, φ ) → ( r, g, b, σ )</div>
      <div class="line">&nbsp;</div>
      <div class="line">입력: 공간의 위치 (x,y,z) + <strong>보는 방향</strong> (θ,φ)</div>
      <div class="line">출력: 그 지점의 색과 <strong>밀도</strong> σ</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 신경망 하나가 장면 하나를 통째로 담는다</div>
    </div>
    <p>
      <strong>보는 방향</strong>이 입력에 들어간 것이 결정적이다.
      같은 지점이라도 각도에 따라 다른 색을 낼 수 있으므로
      <em>반사와 광택</em>이 자연스럽게 표현된다. 메시가 어려워하던 부분이다.
    </p>
    <p>
      이미지를 만드는 방법은 <strong>볼륨 렌더링</strong>이다.
      픽셀마다 광선을 쏘고, 그 위의 점들을 표본으로 뽑아 색을 누적한다.
    </p>
    <div class="eq">
      <span class="cap">광선을 따라 색을 쌓는다</span>
      <div class="line">C(r) = Σ T<sub>i</sub> · (1 − exp(−σ<sub>i</sub>δ<sub>i</sub>)) · c<sub>i</sub></div>
      <div class="line">&nbsp;</div>
      <div class="line">T<sub>i</sub> = exp( −Σ<sub>j&lt;i</sub> σ<sub>j</sub>δ<sub>j</sub> )&nbsp;&nbsp;// 여기까지 살아남은 빛의 비율</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 앞이 불투명하면 뒤는 안 보인다 — T 가 그것을 표현한다</div>
    </div>
    <p>
      이 렌더링 과정 전체가 <strong>미분 가능</strong>하다는 것이 핵심이다.
      만들어낸 이미지와 실제 사진의 차이를 손실로 두면,
      그래디언트가 렌더링을 거슬러 올라가 <em>신경망 가중치까지</em> 도달한다.
    </p>
    <div class="note">
      <b>위치를 그대로 넣으면 흐릿해진다.</b> 신경망은 저주파 함수를 선호해서
      좌표를 직접 넣으면 세부가 뭉개진다. NeRF 는 <strong>위치 인코딩</strong>으로 이것을 푼다 —
      좌표를 여러 주파수의 사인·코사인으로 펼쳐 넣는다.
      <a href="embeddings.html">트랜스포머의 정현파 위치 인코딩</a>과 같은 도구가
      전혀 다른 목적으로 쓰인 사례다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>느린 것이 문제였다</h2>
    <p>
      NeRF 는 품질로 놀라움을 줬지만 <strong>실용성에서 막혔다</strong>.
    </p>
    <ul>
      <li><strong>학습이 며칠</strong> — 장면 하나에 GPU 로 1~2일</li>
      <li><strong>렌더링이 초 단위</strong> — 픽셀마다 광선을 쏘고 그 위에서 신경망을 수백 번 호출한다</li>
      <li><strong>장면마다 새로 학습</strong> — 학습된 가중치가 곧 그 장면이라 재사용이 안 된다</li>
    </ul>
    <p>
      두 번째가 특히 심하다. 1080p 한 장이면 200만 픽셀,
      광선마다 표본 100개면 <strong>2억 번의 신경망 호출</strong>이다.
      실시간은 고사하고 한 장에 수십 초가 걸린다.
    </p>
    <p>
      가속 연구가 쏟아졌고, 방향은 대체로 하나였다 —
      <strong>신경망이 하던 일을 자료구조로 옮기는 것</strong>이다.
      해시 격자에 특징을 저장해 두면 신경망을 아주 작게 만들 수 있고,
      학습 시간이 며칠에서 <em>분 단위</em>로 줄어든다.
    </p>
    <div class="note">
      <b>같은 교환이 반복된다.</b> <a href="gradient-checkpointing.html">체크포인팅</a>이
      메모리를 연산으로 바꿨듯, 여기서는 <em>연산을 메모리로</em> 바꾼다.
      격자에 미리 저장해 두면 매번 계산할 필요가 없다.
      무엇이 병목인지에 따라 어느 쪽으로 밀지가 정해진다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>3D Gaussian Splatting — 방향을 바꾸다</h2>
    <p>
      2023년 <strong>3D Gaussian Splatting</strong>(3DGS)이 판을 바꿨다.
      접근이 근본적으로 다르다 — <em>신경망을 거의 쓰지 않는다.</em>
    </p>
    <p>
      장면을 <strong>수백만 개의 3D 가우시안</strong>으로 표현한다.
      각 가우시안은 위치·크기·방향(공분산)·색·불투명도를 갖는 <em>명시적인 덩어리</em>다.
      공간을 함수로 질의하는 대신 <strong>덩어리들을 화면에 투영해 쌓는다</strong>.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="NeRF와 3D Gaussian Splatting의 비교. NeRF는 광선을 쏘고 그 위의 점마다 신경망을 호출해 느리지만, 3DGS는 명시적인 가우시안 덩어리들을 화면에 투영해 정렬 후 합성하므로 훨씬 빠르다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="nf-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="nf-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--warn)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">NeRF — 광선마다 신경망을 수백 번</text>

            <circle cx="40" cy="70" r="8" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="40" y="92" text-anchor="middle" font-size="7" fill="var(--ink-faint)">카메라</text>
            <path d="M50 70 L230 52" stroke="var(--warn)" stroke-width="1.2" marker-end="url(#nf-m)"/>
            <g fill="var(--warn)" opacity="0.7">
              <circle cx="80" cy="66" r="2.5"/><circle cx="105" cy="63" r="2.5"/><circle cx="130" cy="61" r="2.5"/>
              <circle cx="155" cy="59" r="2.5"/><circle cx="180" cy="57" r="2.5"/><circle cx="205" cy="54" r="2.5"/>
            </g>
            <text x="140" y="86" font-size="7.5" fill="var(--warn)">표본마다 F(x,d) 호출</text>

            <text x="24" y="114" font-size="8" fill="var(--ink-faint)">1080p · 표본 100개 → <tspan fill="var(--warn)">2억 번 호출</tspan></text>
            <text x="24" y="128" font-size="8" fill="var(--warn)">한 장에 수십 초 · 학습 1~2일</text>

            <line x1="270" y1="26" x2="270" y2="146" stroke="var(--rule)" stroke-width="1"/>

            <text x="294" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">3DGS — 덩어리를 투영해 쌓는다</text>

            <g>
              <ellipse cx="340" cy="52" rx="14" ry="8" fill="var(--accent)" opacity="0.45" transform="rotate(-20 340 52)"/>
              <ellipse cx="376" cy="66" rx="10" ry="14" fill="var(--accent)" opacity="0.45" transform="rotate(30 376 66)"/>
              <ellipse cx="410" cy="48" rx="16" ry="7" fill="var(--accent)" opacity="0.45"/>
              <ellipse cx="352" cy="86" rx="9" ry="9" fill="var(--accent)" opacity="0.45"/>
              <ellipse cx="398" cy="82" rx="13" ry="9" fill="var(--accent)" opacity="0.45" transform="rotate(-40 398 82)"/>
            </g>
            <text x="378" y="112" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">각각 위치·공분산·색·불투명도</text>

            <path d="M440 66 L466 66" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#nf-a)"/>
            <text x="453" y="58" text-anchor="middle" font-size="7" fill="var(--ink-faint)">투영</text>

            <rect x="472" y="42" width="60" height="48" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="502" y="70" text-anchor="middle" font-size="8" fill="var(--accent)">화면</text>

            <text x="546" y="56" font-size="8" fill="var(--accent)">깊이순 정렬 후</text>
            <text x="546" y="70" font-size="8" fill="var(--accent)">알파 합성</text>
            <text x="546" y="88" font-size="8" fill="var(--ink-faint)">래스터화라 GPU 에 맞다</text>

            <text x="294" y="128" font-size="8.5" fill="var(--accent)">1080p 에서 <tspan fill="var(--accent)">100 fps 이상</tspan> · 학습도 훨씬 빠르다</text>

            <line x1="24" y1="160" x2="674" y2="160" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="180" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">무엇이 달라졌나</text>
            <text x="24" y="200" font-size="8.5" fill="var(--ink-soft)">암묵적(함수) → <tspan fill="var(--accent)">명시적(덩어리)</tspan> · 광선 행진 → <tspan fill="var(--accent)">래스터화</tspan></text>
            <text x="24" y="216" font-size="8" fill="var(--ink-faint)">빈 공간에서 낭비하지 않고, 정렬·블렌딩은 그래픽 하드웨어가 원래 잘하는 일이다</text>
            <text x="24" y="230" font-size="8" fill="var(--warn)">대신 저장 용량이 크다 — 장면 하나에 수백 MB 가 되기도</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>암묵적 표현에서 명시적 표현으로</strong> 돌아온 셈이다.
        원 논문은 1080p 에서 <em>100 fps 이상</em>의 실시간 렌더링을 보고했다.
        핵심은 셋 — 3D 가우시안 표현, 밀도를 조절하며 최적화, 그리고
        <em>가시성을 고려한 빠른 렌더링</em>이다.
      </figcaption>
    </figure>

    <p>
      <strong>밀도 조절</strong>이 학습의 요령이다.
      복원이 부족한 곳에서는 가우시안을 <em>쪼개거나 복제</em>하고,
      불투명도가 낮아 기여하지 않는 것은 제거한다.
      필요한 곳에만 표현력을 배분하는 방식이다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>이후 — 하나가 아니라 여러 갈래로</h2>
    <p>
      3DGS 이후 흐름은 <em>단일 후계자가 나타나는</em> 모양이 아니다.
      문제마다 특화된 변형이 갈라져 나왔다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방향</th><th>무엇을 고치나</th></tr>
        </thead>
        <tbody>
          <tr><td class="hi">앨리어싱 제거</td><td>축소·확대 시 깜빡임. 다중 스케일·필터링으로 (Mip-Splatting 등)</td></tr>
          <tr><td class="hi">가속·경량화</td><td>희소 처리·인코딩 압축·정렬 최적화. 온디바이스를 겨냥한 것도 나왔다</td></tr>
          <tr><td>하드웨어 활용</td><td class="hi">블렌딩을 텐서 코어에 맞게 재구성하는 시도</td></tr>
          <tr><td>표면 품질</td><td>가우시안이 표면에 붙도록 정규화 — 메시 추출을 위해</td></tr>
          <tr><td>동적 장면</td><td class="hi">시간 축 추가 — 움직이는 장면을 담는다</td></tr>
          <tr><td>의미 부여</td><td>가우시안에 언어 특징을 붙여 <a href="vision-language-models.html">말로 질의</a></td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 흥미롭다. 각 가우시안에 <a href="clip.html">CLIP</a> 특징을 붙이면
      <em>"빨간 의자"를 3D 공간에서 찾을 수 있다</em>.
      다만 <strong>보는 각도에 따라 의미가 달라지는</strong> 문제가 있어
      그것을 다루는 후속 연구가 이어지고 있다.
    </p>
    <div class="note">
      <b>NeRF 가 사라진 것은 아니다.</b> 3DGS 가 속도에서 앞서지만,
      <em>암묵적 표현이 유리한 곳</em>이 남아 있다 —
      메모리가 작고, 매끄러운 표면 복원에 강하며, 정규화를 넣기 쉽다.
      그리고 NeRF 계열에서도 온디바이스 가속기 연구가 이어지고 있다.
      <a href="mamba-ssm.html">Mamba 와 트랜스포머</a>처럼
      <strong>하나가 다른 하나를 완전히 대체하지 않는</strong> 구도다.
    </div>
    <p>
      실무 관점에서 남는 제약도 있다.
      <strong>여전히 장면마다 학습</strong>해야 하고(수십~수백 장의 사진과 정확한 카메라 자세가 필요),
      <em>일반화된 모델</em>은 아니다.
      사진 몇 장으로 즉시 3D 를 만드는 <em>피드포워드</em> 방식이 연구되고 있지만
      아직 품질 격차가 있다.
    </p>
    <p>
      정리하면 이 분야는 <em>"공간을 어떻게 표현할 것인가"</em>의 질문이고,
      답이 <strong>메시 → 신경망 함수 → 명시적 덩어리</strong>로 옮겨왔다.
      각 전환마다 <em>무엇을 잘 담을 수 있는지</em>와 <em>얼마나 빠른지</em>가 함께 바뀌었고,
      지금은 하나로 수렴하기보다 용도별로 갈라지는 국면이다.
    </p>
  </section>
"""

READING = [
    "Mildenhall et al., <em>NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis</em> (arXiv:2003.08934) — 원 논문. 위치 인코딩과 볼륨 렌더링.",
    "Kerbl et al., <em>3D Gaussian Splatting for Real-Time Radiance Field Rendering</em> (SIGGRAPH 2023) — 1080p 100fps 이상. 세 핵심 구성요소.",
    "Müller et al., <em>Instant Neural Graphics Primitives with a Multiresolution Hash Encoding</em> (arXiv:2201.05989) — 해시 격자로 학습을 분 단위로.",
    "Barron et al., <em>Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields</em> (arXiv:2111.12077) — 앨리어싱과 무한 장면 처리.",
    "Yu et al., <em>Mip-Splatting: Alias-free 3D Gaussian Splatting</em> (CVPR 2024) — 3DGS 의 앨리어싱 문제.",
    "Chen &amp; Wang, <em>A Survey on 3D Gaussian Splatting</em> (arXiv:2401.03890) — 3DGS 이후 갈래들의 정리.",
]

write(
    "nerf-3d.html",
    title="NeRF & 3D 표현 — 공간을 무엇으로 담을 것인가",
    eyebrow="Vision · 3D Representation · 2020–2026",
    h1="NeRF &amp; 3D 표현",
    subtitle="공간을 무엇으로 담을 것인가 — 함수에서 덩어리로",
    dek=(
        "메시는 <em>경계가 뚜렷한 불투명 표면</em>을 전제한다. "
        "연기·유리·머리카락은 그 전제를 벗어난다. "
        "NeRF 는 장면을 <strong>공간의 색과 밀도를 답하는 함수</strong>로 바꿔 이 문제를 풀었지만 느렸고, "
        "3D Gaussian Splatting 은 <strong>명시적 덩어리</strong>로 돌아와 실시간을 얻었다."
    ),
    spec=[
        ("푸는 문제", "새 시점 합성"),
        ("NeRF", "5D → 색·밀도 함수"),
        ("느린 이유", "광선당 신경망 수백 회"),
        ("3DGS", "1080p 100fps 이상"),
        ("현재", "단일 후계자 없이 분화"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)

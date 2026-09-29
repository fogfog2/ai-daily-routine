#!/usr/bin/env python3
"""RTMDet family: source-grounded architecture and deployment note."""
from build import write
LIGHT = dict(paper="#f2f3ed", panel="#e7eee6", ink="#17231f", **{
    "ink-soft":"#465b50", "ink-faint":"#6b8073", "rule":"#cfdcd1",
    "rule-strong":"#a9c5ad", "accent":"#24725c", "accent-fill":"#dbede0",
    "accent-line":"#449f77", "muted":"#758c7a", "muted-fill":"#e0e9df", "warn":"#ae613c"
})
DARK = dict(paper="#101914", panel="#18251c", ink="#e5f1e8", **{
    "ink-soft":"#a3bca9", "ink-faint":"#758f7d", "rule":"#283b2e",
    "rule-strong":"#3d5945", "accent":"#91ddb0", "accent-fill":"#183e2b",
    "accent-line":"#5dbb83", "muted":"#809788", "muted-fill":"#1d2c21", "warn":"#e0a070"
})

BODY = r"""
  <style>.sheet table th,.sheet table td{padding:12px 10px;border-bottom:1px solid var(--rule)}.sheet table th{color:var(--accent);font-weight:600}.sheet table tbody tr:hover{background:var(--accent-fill)}</style>
  <section>
    <h2><span class="n">01</span>한 검출기에서 세 가지 출력으로</h2>
    <p>RTMDet는 OpenMMLab이 2022년에 발표한 실시간 인식 모델 계열이다. <a href="yolox.html">YOLOX</a>와 함께 읽으면 앵커 없는 1단계 검출의 공통 기반과 설계 차이를 볼 수 있다. 특징을 뽑는 백본, 여러 해상도를 섞는 넥, 분류와 위치를 예측하는 헤드를 함께 조정하고, 같은 골격을 다른 출력 과제로 확장한다.</p>
    <figure>
      <svg viewBox="0 0 760 290" role="img" aria-label="이미지가 CSPNeXt 백본과 CSPNeXt 기반 넥을 지나 RTMDet 상자 검출, RTMDet-Ins 인스턴스 마스크, RTMDet-R 회전 상자로 갈라지는 계열 구조">
        <g fill="var(--panel)" stroke="var(--rule-strong)" stroke-width="1.5">
          <rect x="12" y="110" width="95" height="64" rx="10"/><rect x="142" y="100" width="140" height="84" rx="10"/><rect x="317" y="100" width="145" height="84" rx="10"/>
          <rect x="525" y="15" width="220" height="70" rx="10"/><rect x="525" y="108" width="220" height="70" rx="10"/><rect x="525" y="201" width="220" height="70" rx="10"/>
        </g>
        <g fill="none" stroke="var(--accent)" stroke-width="2"><path d="M107 142H142M282 142H317M462 142H493V50H525M493 142H525M493 142V236H525"/></g>
        <g fill="var(--ink)" text-anchor="middle" font-size="16" font-family="system-ui,sans-serif">
          <text x="60" y="148">입력 이미지</text><text x="212" y="133">CSPNeXt</text><text x="212" y="157" font-size="12">다중 해상도 특징</text><text x="390" y="133">CSPNeXt 넥</text><text x="390" y="157" font-size="12">상향 · 하향 결합</text>
          <text x="635" y="43">RTMDet</text><text x="635" y="65" font-size="12">범주 + 수평 상자</text><text x="635" y="136">RTMDet-Ins</text><text x="635" y="158" font-size="12">물체별 픽셀 마스크</text><text x="635" y="229">RTMDet-R</text><text x="635" y="251" font-size="12">방향을 포함한 회전 상자</text>
        </g>
      </svg>
      <figcaption><span class="cap">FAMILY MAP</span> 크기와 과제는 서로 다른 선택 축이다. tiny·s·m·l·x는 모델 용량을, Ins·R은 출력의 종류를 나타낸다. 모든 과제에서 모든 크기를 제공한다는 뜻은 아니다.</figcaption>
    </figure>
    <p><a href="segmentation.html">인스턴스 분할</a>이 필요한지, 수평 상자로 충분한지부터 정해야 한다. 항공 영상의 비스듬한 선박처럼 방향이 중요한 대상에는 회전 상자가 더 맞을 수 있다. 이 선택은 주석 형식과 평가 지표도 바꾼다.</p>
  </section>
  <section>
    <h2><span class="n">02</span>백본과 넥의 균형이 속도를 만든다</h2>
    <p>논문은 CSP 계열 블록에 <strong>5×5 depthwise 합성곱</strong>을 넣어 주변 문맥을 넓힌다. 채널별 공간 연산은 <a href="efficient-backbone.html">경량 백본</a>에서 본 원리와 연결된다. 하지만 연산량이 작아도 층을 늘리면 순차 실행이 길어진다. RTMDet는 블록의 깊이를 줄이고 폭을 조정하며, 백본뿐 아니라 넥에도 충분한 용량을 배분한다.</p>
    <p>각 해상도에서 예측하는 헤드는 합성곱 가중치를 공유하되 Batch Normalization은 해상도마다 둔다. 분포가 다른 특징에 통계까지 강제로 공유하지 않는 선택이다. 분류와 상자 회귀의 역할, 해상도 사이의 가중치 공유는 서로 다른 설계 축이므로 혼동하지 말아야 한다.</p>
    <div class="note"><b>FLOPs만 보고 빠르다고 판단하지 않는다.</b> 깊이, 채널 폭, 메모리 이동, 런타임의 연산자 구현을 함께 본다. 실제 장치의 병목은 <a href="mobile-runtime.html">모바일 런타임</a> 문서와 이어 읽을 수 있다.</div>
  </section>
  <section>
    <h2><span class="n">03</span>양성 예측을 고르는 기준도 학습의 일부다</h2>
    <p>밀집 검출기는 많은 후보를 낸다. 어떤 후보가 어느 정답 상자를 학습할지 정하는 라벨 할당이 필요하다. RTMDet의 dynamic soft label assignment는 SimOTA를 바탕으로, 매칭 비용에 상자 품질을 반영하는 부드러운 분류 목표를 사용한다.</p>
    <div class="eq"><span class="cap">매칭 비용 — 논문 기본 가중치</span><div class="line">C = C<sub>cls</sub> + 3C<sub>reg</sub> + C<sub>center</sub></div><div class="line">C<sub>cls</sub> = CE(P, Y<sub>soft</sub>) · (Y<sub>soft</sub> − P)²</div><div class="line">Y<sub>soft</sub> = IoU(예측 상자, 정답 상자)</div></div>
    <p>높은 분류 확률만으로 좋은 후보라고 취급하지 않고 위치 품질도 함께 고려한다. 위 식은 <em>매칭에 사용하는 비용</em>이며 전체 학습 손실과 동일한 식은 아니다. <a href="iou-losses.html">IoU 계열 손실</a>을 함께 보면 상자 품질을 측정하는 값이 어디에 쓰이는지 구분할 수 있다.</p>
    <p>학습에서는 캐시를 활용한 Mosaic·MixUp과 두 단계의 증강 구성이 사용된다. 강한 증강으로 다양성을 확보한 뒤 후반에는 구성을 바꿔 예측을 다듬는다. 사용자 데이터로 옮길 때는 체크포인트, 학습 설정, 후처리 설정을 한 세트로 보관해야 재현할 수 있다.</p>
  </section>
  <section>
    <h2><span class="n">04</span>tiny부터 x까지, 같은 조건으로 읽기</h2>
    <p>아래는 <a href="https://github.com/open-mmlab/mmdetection/blob/main/configs/rtmdet/README.md">MMDetection 공식 모델 목록</a>의 기본 검출 모델이다. 2026-09-30 원문 확인 기준이며, 2022년 계열의 공개 체크포인트 결과다. 최신 검출기 전체의 순위를 뜻하지 않는다.</p>
    <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;text-align:left;font-size:.86em"><caption style="text-align:left;padding:12px 0">COCO box AP · 입력 640 · TensorRT FP16, RTX 3090</caption><thead><tr><th>크기</th><th>AP</th><th>파라미터 M</th><th>지연 ms</th></tr></thead><tbody>
      <tr><td>tiny</td><td>41.1</td><td>4.8</td><td>0.98</td></tr><tr><td>s</td><td>44.6</td><td>8.89</td><td>1.22</td></tr><tr><td>m</td><td>49.4</td><td>24.71</td><td>1.62</td></tr><tr><td>l</td><td>51.5</td><td>52.3</td><td>2.44</td></tr><tr><td>x</td><td>52.8</td><td>94.86</td><td>3.10</td></tr>
    </tbody></table></div>
    <p>공식 측정은 TensorRT 8.4.3·cuDNN 8.2.0·FP16·batch 1이며 <strong>NMS를 제외</strong>한다. 영상 디코딩, 전처리, 데이터 전송, 후처리까지 포함한 서비스 지연과 구분해야 한다. 기본 RTMDet는 <a href="nms.html">NMS</a>를 사용하므로 앵커가 없다는 이유로 중복 제거도 없다고 해석하면 안 된다.</p>
    <p>tiny나 s에서 시작해 대상 장치의 지연과 사용자 데이터 정확도를 함께 측정한다. 작은 물체를 놓친다면 크기만 키우기 전에 입력 해상도와 데이터 분포를 확인한다. P6·다른 백본 구성은 조건이 달라 이 표에 섞지 않았다.</p>
  </section>
  <section>
    <h2><span class="n">05</span>Ins와 R이 더하는 것</h2>
    <p><strong>RTMDet-Ins</strong>는 마스크 특징과 물체별 동적 커널을 예측하는 경로를 더한다. 상자는 물체를 둘러싸고 마스크는 그 물체의 픽셀을 가른다. 공식 목록에는 tiny·s·m·l·x가 있으며 box AP와 mask AP를 각각 기록한다. 검출 모델의 지연과 마스크 후처리를 포함한 지연을 직접 비교하지 않는다.</p>
    <p><strong>RTMDet-R</strong>은 각도 예측과 회전 상자 디코딩을 추가한다. <a href="https://github.com/open-mmlab/mmrotate/tree/1.x/configs/rotated_rtmdet">MMRotate 공식 구성</a>에는 tiny·s·m·l이 제공된다. 각도 범위와 상자 표현, 회전 IoU, 학습 증강을 맞춰야 한다. DOTA의 mAP50과 COCO의 여러 IoU 임계값을 평균한 AP는 서로 다른 지표다.</p>
    <p>도입 순서는 출력 과제 선택 → 대응하는 공식 설정·체크포인트 선택 → 사용자 데이터 평가 → 실제 런타임 변환 → 전처리부터 후처리까지 재측정이다. ONNX나 TensorRT로 변환할 때도 상자·마스크·회전 연산의 지원을 각각 확인한다. RTMDet는 이러한 선택을 하나의 계열 안에서 비교할 수 있는 출발점이다.</p>
  </section>
"""
READING = [
    '<a href="https://arxiv.org/abs/2212.07784">Lyu et al., <em>RTMDet: An Empirical Study of Designing Real-Time Object Detectors</em> (2022)</a> — 구조·할당·과제 확장의 원 논문.',
    '<a href="https://github.com/open-mmlab/mmdetection/blob/main/configs/rtmdet/README.md">MMDetection RTMDet 모델 목록</a> — 검출·Ins 체크포인트와 측정 조건.',
    '<a href="https://github.com/open-mmlab/mmrotate/tree/1.x/configs/rotated_rtmdet">MMRotate RTMDet-R</a> — 회전 검출 설정과 DOTA 결과.',
    '<a href="https://github.com/open-mmlab/mmyolo/tree/main/configs/rtmdet">MMYOLO RTMDet</a> — 별도 학습 구현과 설정.',
    '<a href="https://arxiv.org/abs/2107.08430">Ge et al., <em>YOLOX</em> (2021)</a> — 앵커프리 헤드와 SimOTA의 배경.',
]
write('rtmdet-family.html', title='RTMDet 계열 — 검출에서 마스크와 회전 상자까지',
      eyebrow='Vision · Real-Time Detection · OpenMMLab', h1='RTMDet 계열',
      subtitle='검출 · 인스턴스 분할 · 회전 상자를 잇는 실시간 구조',
      dek='백본만 바꾸면 검출기가 좋아질까? RTMDet는 넥과 헤드, 라벨 할당과 학습 전략을 함께 조정한다. tiny부터 x까지의 크기 선택과 Ins·R의 과제 확장을 같은 지도 위에서 살핀다.',
      spec=[('출발','OpenMMLab · 2022'),('크기','tiny · s · m · l · x'),('출력','상자 · 마스크 · 회전 상자'),('핵심','CSPNeXt · soft assignment'),('확인','2026-09-30 · 공식 자료')],
      body=BODY, reading=READING, light=LIGHT, dark=DARK, date='2026-09-30')

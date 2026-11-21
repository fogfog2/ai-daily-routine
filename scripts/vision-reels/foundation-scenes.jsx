import React from 'react';
import {
  mint,
  amber,
  blue,
  dim,
  line,
  panel,
  range,
  clamp,
  mix,
  Text,
  Tile,
  Arrow,
  Point,
  Caption,
  SignalBox,
} from './research-drawing';

const letters = 'ABCDEF';
const overlaps = [0.8, 0.65, 0.5, 0.3, 0.15, 0.1];
const costs = [4.2, 1.6, 4.4, 3.9, 6.2, 7.6];
function Candidates({ dynamic = false, count = false, reveal = 1 }) {
  return (
    <g>
      <Caption>{count ? '후보별 IoU · 큰 값부터' : '후보별 비용 · 낮을수록 먼저 선택'}</Caption>
      {overlaps.map((v, i) => {
        const chosen = i === 1 || (dynamic && i === 3),
          x = 54 + 94 * i;
        const val = count ? v : costs[i],
          height = (count ? v * 190 : val * 21) * clamp(reveal * 1.15 - i * 0.025);
        return (
          <g key={i}>
            <rect
              x={x}
              y={357 - height}
              width="55"
              height={height}
              fill={count ? blue : chosen ? mint : line}
              rx="4"
            />
            <Text x={x + 27} y={345 - height} anchor="middle" size={20}>
              {val.toFixed(count ? 2 : 1)}
            </Text>
            <Text x={x + 27} y={388} anchor="middle" color={chosen && !count ? mint : dim}>
              {letters[i]}
            </Text>
          </g>
        );
      })}
      <Caption foot>
        {count
          ? '0.80 + 0.65 + 0.50 + 0.30 + 0.15 + 0.10 = 2.50'
          : dynamic
            ? 'k = 2   ·   B와 D에 양성 신호'
            : 'k = 1   ·   B에 양성 신호'}
      </Caption>
    </g>
  );
}
function CandidateGrid({ p }) {
  const pts = [
    [1, 2],
    [2, 2],
    [3, 2],
    [1, 3],
    [2, 3],
    [3, 3],
  ];
  return (
    <g>
      <Caption>검출 격자 위의 후보 위치</Caption>
      {range(40).map((i) => (
        <rect
          key={i}
          x={115 + (i % 8) * 54}
          y={140 + Math.floor(i / 8) * 48}
          width="53"
          height="47"
          fill={panel}
          stroke={line}
        />
      ))}
      <rect
        x="167"
        y="190"
        width="190"
        height="143"
        fill={mint}
        fillOpacity=".12"
        stroke={mint}
        strokeWidth="3"
      />
      {pts.slice(0, 1 + Math.floor(5 * p)).map(([x, y], i) => (
        <g key={i}>
          <Point x={140 + x * 54} y={160 + y * 48} />
          <Text x={151 + x * 54} y={151 + y * 48} size={15}>
            {letters[i]}
          </Text>
        </g>
      ))}
      <Caption foot>민트 테두리는 정답 · 점은 후보의 중심입니다.</Caption>
    </g>
  );
}

const nmsShift = (iou) => (180 * (1 - iou)) / (1 + iou);
function Suppression({ iou = 0.8, soft = false, geometry = false }) {
  const dx = nmsShift(iou),
    changed = soft ? 0.9 * Math.exp((-iou * iou) / 0.5) : iou > 0.5 ? 0 : 0.9;
  return (
    <g>
      <Caption>
        {geometry
          ? '같은 크기인 두 상자의 수평 겹침'
          : soft
            ? '가우시안 Soft-NMS · σ = 0.50'
            : '하드 NMS · IoU 기준 0.50'}
      </Caption>
      <rect
        x="83"
        y="178"
        width="180"
        height="131"
        fill={blue}
        fillOpacity=".11"
        stroke={blue}
        strokeWidth="4"
      />
      <rect
        x={83 + dx}
        y="178"
        width="180"
        height="131"
        fill={amber}
        fillOpacity=".12"
        stroke={amber}
        strokeWidth="4"
        strokeDasharray={!geometry && !soft && iou > 0.5 ? '8 6' : undefined}
      />
      <Text x={83} y={352} color={blue} size={23}>
        1순위 0.95
      </Text>
      <Text x={391} y={202} color={amber} size={23}>
        후보 점수
      </Text>
      <Text x={391} y={256} size={38}>
        {geometry ? '0.90' : changed.toFixed(2)}
      </Text>
      <Text x={391} y={311} size={21} color={dim}>
        {'IoU = ' + iou.toFixed(2)}
      </Text>
      <Caption foot>
        {geometry
          ? '겹치는 폭이 커지면 IoU가 커집니다.'
          : soft
            ? '다음 선택 전 점수를 다시 정렬합니다.'
            : '기준을 넘은 두 번째 후보는 제거됩니다.'}
      </Caption>
    </g>
  );
}
function Ranking({ p }) {
  const vals = [0.9, 0.5],
    after = 0.9 * Math.exp((-0.8 * 0.8) / 0.5);
  const a = mix(vals[0], after, p);
  return (
    <g>
      <Caption>1순위 상자를 확정한 뒤 남은 두 후보</Caption>
      {[
        [a, '가까운 후보', amber],
        [vals[1], '먼 후보', blue],
      ].map(([v, name, c], i) => (
        <g key={name}>
          <Text x={45} y={200 + i * 95} color={c}>
            {name}
          </Text>
          <rect x="211" y={176 + i * 95} width={v * 340} height="32" fill={c} rx="5" />
          <Text x={579} y={204 + i * 95} anchor="end">
            {v.toFixed(2)}
          </Text>
        </g>
      ))}
      <Caption foot>
        {a > 0.5 ? '다음 후보  ·  가까운 상자' : '다음 후보  ·  멀리 있던 상자'}
      </Caption>
    </g>
  );
}
function PatchGrid({ small = false, p = 1, pairs = false }) {
  const n = small ? 14 : 7,
    N = n * n + 1,
    x = 37,
    y = 149,
    s = 239;
  return (
    <g>
      <Caption>
        {pairs ? '패치 수에서 질의 × 키 점수로' : '224 × 224 이미지 · 정사각형 패치로 분할'}
      </Caption>
      <rect x={x} y={y} width={s} height={s} fill="#4f7583" />
      <circle cx={x + 171} cy={y + 55} r="24" fill={amber} />
      <path d={`M${x} ${y + 169}l63 -78 46 34 38 -44 92 101v57H${x}z`} fill="#76a49a" />
      {range(n + 1).map((i) => (
        <g key={i} stroke="#19333b" strokeWidth="1.6">
          <path d={`M${x + (s * i) / n} ${y}v${s * p}`} />
          <path d={`M${x} ${y + (s * i) / n}h${s * p}`} />
        </g>
      ))}
      <Text x={313} y={198} color={blue}>
        패치 {small ? 16 : 32} × {small ? 16 : 32}
      </Text>
      <Text x={313} y={255} color={mint}>
        {n} × {n} = {n * n}개
      </Text>
      <Text x={313} y={316} size={22}>
        분류 토큰 포함 {N}개
      </Text>
      <Caption foot>
        {pairs
          ? `한 헤드의 점수  ·  ${N} × ${N} = ${(N * N).toLocaleString('en-US')}`
          : '작은 패치일수록 물체 경계를 더 잘게 나눕니다.'}
      </Caption>
    </g>
  );
}
function Project({ p }) {
  const cells = ['#77b7a3', '#3f747c', '#acc8a9', '#467c83'];
  return (
    <g>
      <Caption>패치 한 장을 시퀀스의 특징 벡터로</Caption>
      {cells.map((c, i) => (
        <rect
          key={i}
          x={mix(42 + (i % 2) * 37, 40 + i * 36, p)}
          y={mix(224 + Math.floor(i / 2) * 37, 248, p)}
          width="33"
          height="33"
          fill={c}
        />
      ))}
      <Arrow x={194} y={265} dx={51} dy={0} />
      <SignalBox x={254} y={236} w={165} label="선형 투영" />
      <Arrow x={424} y={265} dx={42} dy={0} />
      <SignalBox x={478} y={236} w={151} label="패치 토큰" color={mint} />
      <Caption foot>위치 임베딩을 더해 이미지 속 위치를 전달합니다.</Caption>
    </g>
  );
}
function UnitVectors({ p }) {
  const o = [202, 330],
    ang = 0.98 - 0.4 * p;
  const end = (a) => [148 * Math.cos(a), -148 * Math.sin(a)];
  return (
    <g>
      <Caption>길이가 1인 특징 벡터 · 2차원 설명 예시</Caption>
      <path d="M50 330h345M202 377V133" stroke={line} strokeWidth="2" />
      <path d="M350 330a148 148 0 0 0-148-148" stroke={line} strokeDasharray="5 6" fill="none" />
      {[0.23, ang].map((a, i) => (
        <Arrow key={i} x={o[0]} y={o[1]} dx={end(a)[0]} dy={end(a)[1]} c={i ? mint : amber} />
      ))}
      <Text x={421} y={219} color={amber}>
        사진 벡터
      </Text>
      <Text x={421} y={264} color={mint}>
        문장 벡터
      </Text>
      <Caption foot>각도가 작아지면 코사인 유사도가 커집니다.</Caption>
    </g>
  );
}
function Contrastive({ p }) {
  const row = Math.min(2, Math.floor(p * 3));
  return (
    <g>
      <Caption>한 배치의 사진 3장 × 설명문 3개</Caption>
      {range(3).map((i) => (
        <React.Fragment key={i}>
          <Text x={272 + i * 74} y={157} size={18} anchor="middle">
            문장 {i + 1}
          </Text>
          <Text x={215} y={211 + i * 63} anchor="end" size={20} color={i === row ? amber : dim}>
            사진 {i + 1}
          </Text>
        </React.Fragment>
      ))}
      {range(9).map((i) => {
        const r = Math.floor(i / 3),
          c = i % 3;
        return (
          <rect
            key={i}
            x={239 + c * 74}
            y={172 + r * 63}
            width="67"
            height="56"
            rx="5"
            fill={r === c ? '#408779' : panel}
            stroke={r === row ? amber : line}
            strokeWidth="2"
          />
        );
      })}
      <Caption foot>대각선은 데이터에서 함께 수집한 이미지·문장 쌍입니다.</Caption>
    </g>
  );
}
function Scale({ scale }) {
  const prob = 1 / (1 + Math.exp(-scale * 0.2));
  return (
    <g>
      <Caption>코사인 0.80 / 0.60 · 후보 두 개</Caption>
      <Text x={57} y={176} color={amber}>
        스케일 × {Number(scale.toFixed(1))}
      </Text>
      {[prob, 1 - prob].map((v, i) => (
        <g key={i}>
          <Text x={58} y={245 + i * 76}>
            문장 {i + 1}
          </Text>
          <rect
            x="164"
            y={217 + i * 76}
            width={366 * v}
            height="34"
            fill={i ? blue : mint}
            rx="5"
          />
          <Text x={602} y={244 + i * 76} anchor="end">
            {Math.round(v * 100)}%
          </Text>
        </g>
      ))}
      <Caption foot>두 후보의 확률 합은 100%입니다.</Caption>
    </g>
  );
}
const housePath = 'M125 295l88 -73 88 73m-153 -18v87h131v-87M183 364v-52h32v52m22 -65h21v25h-21z';
function Edges({ p }) {
  return (
    <g>
      <Caption>집의 지붕과 창문 위치를 지정하는 윤곽 조건</Caption>
      <Tile x={58} y={149} w={324} h={246} />
      <path
        d={housePath}
        fill="none"
        stroke={mint}
        strokeWidth="5"
        strokeLinejoin="round"
        pathLength="1"
        strokeDasharray={`${p} 1`}
      />
      <Text x={422} y={231} color={amber}>
        텍스트 조건
      </Text>
      <Text x={422} y={280} size={22}>
        “작은 집”
      </Text>
      <Caption foot>문장의 의미와 선의 위치가 서로 다른 단서를 줍니다.</Caption>
    </g>
  );
}
function Residual({ weight, branch = false, p = 1, expanded = false }) {
  const add = 0.6 * weight;
  const barWidth = expanded ? 560 : 216;
  const barHeight = expanded ? 30 : 14;
  return (
    <g>
      <Caption>
        {branch ? '사전 학습 블록과 학습 가능한 조건 분기' : '조건 분기가 기본 특징에 더하는 값'}
      </Caption>
      <SignalBox x={34} y={158} w={206} label="기본 특징 0.40" />
      <SignalBox x={34} y={309} w={206} label="조건 특징 0.60" color={amber} />
      <Arrow x={248} y={189} dx={122} dy={49} c={blue} />
      <Arrow x={248} y={337} dx={122} dy={-74} c={amber} />
      <Point x={mix(249, 369, p)} y={mix(189, 238, p)} c={blue} />
      <Point x={mix(249, 369, p)} y={mix(337, 263, p)} c={amber} />
      <g transform={expanded ? 'translate(45 383)' : 'translate(384 294)'}>
        <rect width={barWidth} height={barHeight} rx="4" fill={panel} stroke={line} />
        <rect width={barWidth * 0.4} height={barHeight} fill={blue} />
        <rect x={barWidth * 0.4} width={barWidth * add} height={barHeight} fill={amber} />
      </g>
      <Text x={260} y={368} color={amber} size={20}>
        w = {weight.toFixed(2)}
      </Text>
      <SignalBox x={382} y={221} w={220} label={'출력 ' + (0.4 + add).toFixed(2)} color={mint} />
      <Caption foot>
        기본 0.40 + 조건 경로 {add.toFixed(2)} = {(0.4 + add).toFixed(2)}
      </Caption>
    </g>
  );
}

export const foundationResults = {
  simResult: {
    caption: 'YOLOX 표 2 · COCO val · 누적 실험',
    heads: ['라벨 할당', 'AP ↑', '추론 시간'],
    rows: [
      ['다중 양성', '45.0', '11.1 ms'],
      ['+ SimOTA', '47.3', '11.1 ms'],
    ],
    foot: '학습 시 양성 할당 규칙을 바꾼 비교입니다.',
  },
  nmsResult: {
    caption: 'Soft-NMS 표 1 · COCO test-dev',
    heads: ['후처리', 'R-FCN AP ↑'],
    rows: [
      ['하드 NMS', '31.1'],
      ['가우시안 Soft-NMS', '32.4'],
    ],
    foot: '동일 검출기에서 후처리 알고리즘을 비교했습니다.',
  },
};
export const foundationScenes = {
  simPool: ({ total }) => <CandidateGrid p={total} />,
  simCount: ({ total }) => <Candidates count reveal={clamp(0.2 + total * 1.4)} />,
  simCost: ({ idx, total }) => <Candidates dynamic={idx > 0} reveal={clamp(0.4 + total * 2)} />,
  nmsBoxes: ({ total }) => <Suppression geometry iou={0.14 + 0.66 * total} />,
  nmsDecay: ({ idx, total }) => (
    <Suppression soft={idx > 0} iou={0.45 + 0.35 * clamp(total * 1.5)} />
  ),
  nmsRank: ({ total }) => <Ranking p={clamp(total * 1.6)} />,
  vitPatch: ({ idx, phase }) => <PatchGrid small={idx > 0} p={clamp(0.2 + phase * 1.8)} />,
  vitProject: ({ total }) => <Project p={clamp(total * 1.8)} />,
  vitPairs: ({ idx, total }) => <PatchGrid small={idx > 0} pairs p={clamp(0.26 + total * 2)} />,
  vitArithmetic: ({ total }) => <PatchGrid small={total > 0.45} pairs />,
  clipVectors: ({ total }) => <UnitVectors p={total} />,
  clipBatch: ({ total }) => <Contrastive p={total} />,
  clipScale: ({ total }) => <Scale scale={2 + 8 * total} />,
  clipProbability: ({ total }) => <Scale scale={2 + 8 * clamp(total * 1.4)} />,
  ctrlEdge: ({ total }) => <Edges p={clamp(0.08 + total * 1.4)} />,
  ctrlBranch: ({ total }) => <Residual branch weight={0} p={(total * 3) % 1} />,
  ctrlWeight: ({ total }) => <Residual weight={0.5 * total} p={(total * 3) % 1} />,
  ctrlOutput: ({ total }) => <Residual weight={0.5 * clamp(total * 1.7)} p={(total * 2) % 1} />,
};
export const foundationComparisons = {
  'yolox-simota': (second) => <Candidates dynamic={second} />,
  'soft-nms': (second) => <Suppression soft={second} />,
  'vit-patch-tokens': (second) => <PatchGrid small={second} />,
  'clip-zero-shot': (second) => <Scale scale={second ? 10 : 2} />,
  'controlnet-zero-conv': (second) => <Residual expanded weight={second ? 0.5 : 0} />,
};

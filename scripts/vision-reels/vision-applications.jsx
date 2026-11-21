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

function Alignment({ p }) {
  const theta = mix(0.18, 0.76, p);
  return (
    <g>
      <Caption>안개 → 맑음 · 특징 공간에서의 두 변화 벡터</Caption>
      <path d="M73 350h324M131 379V142" stroke={line} strokeWidth="2" />
      <Arrow x={131} y={350} dx={174} dy={-161} c={blue} />
      <Arrow x={131} y={350} dx={211 * Math.cos(theta)} dy={-211 * Math.sin(theta)} c={amber} />
      <Text x={369} y={208} color={blue} size={22}>
        텍스트 변화 방향
      </Text>
      <Text x={369} y={278} color={amber} size={22}>
        복원 영상의 변화
      </Text>
      <Caption foot>두 방향의 코사인 유사도를 학습 신호로 사용합니다.</Caption>
    </g>
  );
}
function Matrix({ x, y, rows, cols, c, p = 1, step = 13 }) {
  return (
    <g>
      {range(rows * cols).map((i) => (
        <rect
          key={i}
          x={x + (i % cols) * step}
          y={y + Math.floor(i / cols) * step}
          width={step - 2}
          height={step - 2}
          rx="1"
          fill={i < rows * cols * p ? c : line}
        />
      ))}
    </g>
  );
}
function LowRank({ p }) {
  return (
    <g>
      <Caption>8 × 8 갱신 행렬을 랭크 2로 표현하는 예시</Caption>
      <Matrix x={49} y={202} rows={8} cols={2} c={blue} />
      <Text x={93} y={265}>
        ×
      </Text>
      <Matrix x={136} y={242} rows={2} cols={8} c={amber} />
      <Arrow x={263} y={257} dx={66} dy={0} />
      <Matrix x={364} y={203} rows={8} cols={8} c={mint} p={p} />
      <Text x={490} y={260} color={mint}>
        ΔW
      </Text>
      <Text x={48} y={365} size={22} color={dim}>
        8 × 2
      </Text>
      <Text x={139} y={365} size={22} color={dim}>
        2 × 8
      </Text>
      <Text x={362} y={365} size={22} color={dim}>
        8 × 8
      </Text>
      <Caption foot>예시의 학습 계수 · 8×2 + 2×8 = 32개</Caption>
    </g>
  );
}
function Adapters({ select = false, p = 1 }) {
  return (
    <g>
      <Caption>기본 블록은 고정 · 작은 경로가 변화량을 더함</Caption>
      {range(4).map((i) => {
        const x = 36 + 152 * i,
          on = !select || i % 2 === 1;
        return (
          <g key={i}>
            <Tile x={x} y={262} w={120} h={60} />
            <Text x={x + 60} y={299} anchor="middle" size={21}>
              층 {i + 1}
            </Text>
            <path
              d={`M${x + 12} 261v-49h98v49`}
              fill="none"
              stroke={on ? mint : line}
              strokeWidth="3"
              strokeDasharray={on ? undefined : '6 6'}
            />
            <Tile x={x + 11} y={173} w={101} h={46} border={on ? mint : line} />
            <Text x={x + 61} y={204} anchor="middle" size={18} color={on ? mint : dim}>
              {on ? 'LoRA' : '닫힘'}
            </Text>
            {i < 3 && <Arrow x={x + 121} y={292} dx={28} dy={0} c={blue} />}
          </g>
        );
      })}
      <Point x={mix(48, 601, p)} y={343} c={blue} />
      <Caption foot>
        {select
          ? '예시 선택  ·  2번, 4번 층에 저랭크 갱신'
          : '예시 기준  ·  네 층 모두에 저랭크 갱신'}
      </Caption>
    </g>
  );
}

const scramble = [2, 0, 3, 1];
function Jigsaw({ p }) {
  return (
    <g>
      <Caption>조각의 위치를 복원하는 작은 시각 과제</Caption>
      {range(4).map((i) => {
        const from = scramble[i],
          x = mix(225 + (from % 2) * 100, 225 + (i % 2) * 100, p),
          y = mix(153 + Math.floor(from / 2) * 100, 153 + Math.floor(i / 2) * 100, p);
        const angle = [0, 90, 270, 180][i];
        return (
          <g key={i} transform={`translate(${x} ${y})`}>
            <rect width="96" height="96" fill="#365b63" stroke={line} strokeWidth="2" />
            <path
              d="M95 23a72 72 0 0 0-72 72h72z"
              transform={`rotate(${angle} 48 48)`}
              fill={mint}
            />
            <Text x={8} y={22} size={15} color={amber}>
              {i + 1}
            </Text>
          </g>
        );
      })}
      <Caption foot>작은 퍼즐로 국소 모양과 전체 배치에 대한 감각을 봅니다.</Caption>
    </g>
  );
}
function Budget({ limit = 4, p = 1 }) {
  return (
    <g>
      <Caption>비용 모형 예시 · D와 E의 단위 비용을 1로 고정</Caption>
      {range(25).map((i) => {
        const d = (i % 5) + 1,
          e = Math.floor(i / 5) + 1;
        return (
          <rect
            key={i}
            x={190 + (d - 1) * 45}
            y={339 - (e - 1) * 41}
            width="40"
            height="36"
            rx="4"
            stroke={line}
            fill={d + e <= limit && i <= 25 * p ? mint : panel}
          />
        );
      })}
      {range(5).map((i) => (
        <React.Fragment key={i}>
          <Text x={211 + 45 * i} y={404} anchor="middle" size={18}>
            {i + 1}
          </Text>
          <Text x={170} y={363 - i * 41} anchor="end" size={18}>
            {i + 1}
          </Text>
        </React.Fragment>
      ))}
      <Text x={77} y={157} size={20} color={blue}>
        반복 E
      </Text>
      <Text x={443} y={400} size={20} color={blue}>
        표본 D
      </Text>
      <Caption foot>민트색은 D + E ≤ {limit}를 만족하는 조합입니다.</Caption>
    </g>
  );
}
function Pairs({ p }) {
  const rank = [0, 2, 1];
  return (
    <g>
      <Caption>예측 순위와 실제 성능 순위의 세 쌍 비교</Caption>
      <Text x={145} y={151} size={21} color={dim}>
        가벼운 평가
      </Text>
      <Text x={402} y={151} size={21} color={dim}>
        충분한 학습
      </Text>
      {range(3).map((i) => {
        const y = 209 + i * 65,
          to = 209 + rank[i] * 65,
          col = [mint, amber, blue][i];
        return (
          <g key={i}>
            <Text x={143} y={y} color={col}>
              {i + 1} · {'ABC'[i]}
            </Text>
            <path
              d={`M217 ${y - 7}L${mix(217, 409, p)} ${mix(y - 7, to - 7, p)}`}
              stroke={col}
              strokeWidth="3"
            />
            <Text x={428} y={to} color={col}>
              {rank[i] + 1} · {'ABC'[i]}
            </Text>
          </g>
        );
      })}
      <Caption foot>예시에서는 B와 C의 상대 순서가 뒤집혔습니다.</Caption>
    </g>
  );
}

function QuantSteps({ bits, p }) {
  const n = 2 ** bits,
    val = 0.18 + 0.64 * p,
    quant = Math.round(val * (n - 1)) / (n - 1);
  const X = (v) => 68 + 518 * v;
  return (
    <g>
      <Caption>범위 [0, 1] 위의 균일 양자화 격자</Caption>
      <Text x={64} y={168} color={blue}>
        {bits}비트 · {n}개 코드
      </Text>
      <path d="M68 265h518" stroke={line} strokeWidth="3" />
      {range(n).map((i) => (
        <path key={i} d={`M${X(i / (n - 1))} 248v34`} stroke={dim} strokeWidth="2" />
      ))}
      <Point x={X(val)} y={219} c={amber} />
      <Arrow x={X(val)} y={229} dx={X(quant) - X(val)} dy={31} c={amber} />
      <Point x={X(quant)} y={265} c={mint} />
      <Text x={66} y={347} color={amber} size={22}>
        원래 값 {val.toFixed(3)}
      </Text>
      <Text x={341} y={347} color={mint} size={22}>
        양자화 {quant.toFixed(3)}
      </Text>
      <Caption foot>가장 가까운 코드로 이동한 거리가 반올림 오차입니다.</Caption>
    </g>
  );
}
function Allocation({ guided }) {
  const ns = guided ? [3, 5] : [4, 4];
  return (
    <g>
      <Caption>같은 크기의 두 층 · 평균 4비트 예시</Caption>
      {ns.map((n, i) => (
        <g key={i}>
          <Text x={49} y={219 + i * 98} color={i ? amber : blue}>
            층 {i + 1}
          </Text>
          {range(5).map((j) => (
            <rect
              key={j}
              x={166 + 64 * j}
              y={184 + i * 98}
              width="55"
              height="46"
              rx="5"
              fill={j < n ? (i ? amber : blue) : panel}
              stroke={line}
            />
          ))}
          <Text x={528} y={219 + i * 98}>
            {n} bit
          </Text>
        </g>
      ))}
      <Caption foot>
        {guided
          ? '민감도가 큰 층에 한 비트를 더 배정합니다.'
          : '같은 평균 예산을 두 층에 균등 배정합니다.'}
      </Caption>
    </g>
  );
}
function RangePlot({ p }) {
  const bound = mix(0.54, 0.9, p),
    vals = [0.16, 0.29, 0.44, 0.49, 0.62, 0.71, 0.84];
  return (
    <g>
      <Caption>범위를 바꾸면 같은 코드 수의 간격도 바뀝니다.</Caption>
      <rect x={62} y={203} width={530 * bound} height="95" fill="#34585b" />
      {range(8).map((i) => (
        <path key={i} d={`M${62 + (530 * bound * i) / 7} 195v112`} stroke={mint} strokeWidth="2" />
      ))}
      {vals.map((v, i) => (
        <circle
          key={i}
          cx={62 + 530 * v}
          cy={253 + Math.sin(i) * 11}
          r="7"
          fill={v > bound ? amber : blue}
        />
      ))}
      <Text x={60} y={363} size={22} color={amber}>
        범위 밖 표본 {vals.filter((v) => v > bound).length}개
      </Text>
      <Caption foot>범위가 넓어질수록 인접한 두 코드 사이의 간격이 커집니다.</Caption>
    </g>
  );
}

const expertColors = [blue, mint, amber];
function owner(c, r) {
  if ((c === 4 && r === 4) || (c === 5 && r === 3) || (c === 6 && r === 2)) return 2;
  return c === 1 || r === 1 ? 1 : 0;
}
function RoutedSurface({ routed, p = 1 }) {
  const n = 10,
    h = 6,
    step = 34,
    x = 146,
    y = 168;
  return (
    <g>
      <Caption>{routed ? '패치별로 점수가 가장 높은 전문가' : '공유된 하나의 적응 경로'}</Caption>
      {range(n * h).map((i) => {
        const c = i % n,
          r = Math.floor(i / n),
          k = owner(c, r);
        return (
          <rect
            key={i}
            x={x + c * step}
            y={y + r * step}
            width={step - 1}
            height={step - 1}
            rx="3"
            fill={routed && i <= p * n * h ? expertColors[k] : '#688692'}
            opacity={k === 0 ? 0.74 : 0.94}
          />
        );
      })}
      <path d="M299 320l70 -70" stroke="#192e36" strokeWidth="5" />
      <text x={x} y={402} fill={dim} fontSize="19">
        합성 표면 · 사선은 작은 흠집
      </text>
      <Caption foot>
        {routed
          ? '색은 설명용 경로이며 결함의 정답 마스크와 다릅니다.'
          : '같은 색의 패치들이 하나의 처리 경로를 사용합니다.'}
      </Caption>
    </g>
  );
}
function RoutingScores({ p }) {
  const points = [
    [0.71, 0.22, 0.07],
    [0.19, 0.67, 0.14],
    [0.11, 0.28, 0.61],
  ];
  const ix = Math.min(2, Math.floor(p * 3)),
    vals = points[ix];
  return (
    <g>
      <Caption>한 패치에 대한 세 라우팅 점수 · 축소 예시</Caption>
      {vals.map((v, i) => (
        <g key={i}>
          <Text x={48} y={202 + i * 71} color={expertColors[i]}>
            전문가 {i + 1}
          </Text>
          <rect
            x={195}
            y={176 + i * 71}
            width={v * 411}
            height="33"
            rx="4"
            fill={expertColors[i]}
          />
          <Text x={590} y={202 + i * 71} anchor="end">
            {v.toFixed(2)}
          </Text>
        </g>
      ))}
      <Caption foot>논문 구성은 전문가 4개 중 상위 2개의 출력을 섞습니다.</Caption>
    </g>
  );
}
function Directions({ p }) {
  const start = [-0.8, -0.5, -0.35],
    end = [-Math.PI / 2, Math.PI / 6, (5 * Math.PI) / 6];
  return (
    <g>
      <Caption>출력 전문가 방향 분리 · 세 벡터의 직관</Caption>
      <circle cx="330" cy="274" r="110" fill="none" stroke={line} strokeDasharray="5 7" />
      {end.map((a, i) => (
        <Arrow
          key={i}
          x={330}
          y={274}
          dx={104 * Math.cos(mix(start[i], a, p))}
          dy={104 * Math.sin(mix(start[i], a, p))}
          c={expertColors[i]}
        />
      ))}
      <Caption foot>세 방향이 고르게 벌어진 예시의 끼인각은 120°입니다.</Caption>
    </g>
  );
}
function Disparity({ base = 0.1, p = 1, expanded = false }) {
  const d = (200 * base) / 2,
    xL = 378,
    xR = xL - 5 * d;
  return (
    <g>
      <Caption>정렬한 좌우 영상 · 화면의 변위는 5배 확대</Caption>
      {['왼쪽', '오른쪽'].map((label, i) => (
        <g key={label}>
          <Tile x={54} y={154 + i * 96} w={550} h={74} />
          <Text x={73} y={199 + i * 96} size={20} color={dim}>
            {label}
          </Text>
        </g>
      ))}
      <path d={`M${xL} 191v103`} stroke={line} strokeDasharray="5 7" />
      {expanded && (
        <g>
          <rect x={xR} y={253} width={xL - xR} height={68} fill="#44796f" />
          <rect x={xR} y={330} width={xL - xR} height={25} fill={blue} opacity=".45" />
          {range(2).map((i) => (
            <path
              key={i}
              d={`M${i ? xR : xL} ${i ? 266 : 170}l17 21-17 21-17-21z`}
              fill={i ? mint : amber}
            />
          ))}
        </g>
      )}
      <Point x={xL} y={191} c={amber} />
      <Point x={mix(xL, xR, p)} y={287} c={mint} />
      <Arrow x={xL} y={347} dx={(xR - xL) * p} dy={0} c={blue} />
      <Text x={62} y={394} size={22} color={amber}>
        B = {base.toFixed(2)} m
      </Text>
      <Text x={360} y={394} size={22} color={mint}>
        시차 {Number(d.toFixed(1))} px
      </Text>
      <Caption foot>초점거리 200 px · 깊이 2 m · 동일한 표면점</Caption>
    </g>
  );
}
function DataMix({ p }) {
  const types = ['의자', '선반', '식물'];
  const colors = [blue, amber, mint];
  return (
    <g>
      <Caption>떠 있는 물체의 종류를 제한하는 학습 실험</Caption>
      {range(12).map((i) => {
        const k = i <= Math.floor(12 * p) ? 0 : i % 3,
          x = 70 + (i % 6) * 87,
          y = 193 + Math.floor(i / 6) * 79;
        const shape = [
          'M2 1h25v22H2z M1 25h31 M6 25v13 M27 25v13',
          'M1 0h31v37H1z M1 13h31M1 26h31',
          'M16 38V13 M16 22q-18 1-13-15 11 0 13 15m0-7q0-16 16-14 1 14-16 14',
        ][k];
        return (
          <path
            key={i}
            d={shape}
            transform={`translate(${x} ${y})`}
            fill="none"
            stroke={colors[k]}
            strokeWidth="3"
          />
        );
      })}
      <Text x={60} y={373} size={21} color={dim}>
        {types.join(' · ')} 등 여러 물체 → 의자만
      </Text>
      <Caption foot>같은 학습 변경을 실내 자료와 도로 자료에서 평가합니다.</Caption>
    </g>
  );
}

export const applicationResults = {
  hazeResult: {
    caption: 'BiLaLoRA 표 1 · 적응 방식 비교',
    heads: ['측정 항목', '전체 미세 조정', 'BiLaLoRA'],
    rows: [
      ['학습 시간 (h)', '4.215', '0.940'],
      ['MUSIQ ↑', '64.43', '64.40'],
    ],
    foot: '품질과 학습 시간을 서로 다른 단위로 비교합니다.',
  },
  nasResult: {
    caption: '표 1 · NAS-Bench-201 · 켄달 순위 상관',
    heads: ['평가 후보 집합', '논문 표기값 ↑'],
    rows: [
      ['전체 후보', '93.31'],
      ['상위 20%', '81.33'],
      ['상위 5%', '64.00'],
    ],
    foot: '상위 집단은 충분히 학습한 성능을 기준으로 정합니다.',
  },
  bitsResult: {
    caption: '표 4 · 4비트 EDSR · ×4 · Urban100',
    heads: ['구성', 'PSNR ↑', 'SSIM ↑'],
    rows: [
      ['세 요소 제외', '23.54 dB', '0.677'],
      ['전체 구성', '25.61 dB', '0.762'],
    ],
    foot: '비트 배정 두 종류와 동적 범위 정규화를 포함합니다.',
  },
  moeResult: {
    caption: 'MoECLIP 표 2 · MVTec-AD · AUROC ↑',
    heads: ['구성', '픽셀 단위', '이미지 단위'],
    rows: [
      ['전체 모델', '92.5', '93.9'],
      ['FOFS·ETF 제외', '91.6', '91.7'],
    ],
    foot: '두 지표는 결함의 위치와 이미지 전체를 각각 평가합니다.',
  },
  stereoResult: {
    caption: '표 1 · 오류율(%) ↓ · 학습 물체를 바꾼 비교',
    heads: ['학습 물체', '실내 · 2 px', '도로 · 3 px'],
    rows: [
      ['여러 종류', '6.60', '5.11'],
      ['의자만', '5.29', '7.02'],
    ],
    foot: '실내 Middlebury 2014(H) · 도로 KITTI-15',
  },
};
export const applicationScenes = {
  hazeImage: ({ total }) => <Alignment p={total} />,
  hazeLowRank: ({ total }) => <LowRank p={clamp(0.13 + total * 1.7)} />,
  hazePlace: ({ idx, total }) => <Adapters select={idx > 0} p={total} />,
  nasJigsaw: ({ total }) => <Jigsaw p={clamp(total * 1.35)} />,
  nasBudget: ({ idx, phase }) => <Budget limit={idx ? 7 : 4} p={clamp(0.22 + phase * 1.8)} />,
  nasRanking: ({ total }) => <Pairs p={clamp(0.1 + total * 1.6)} />,
  bitsRound: ({ total }) => <QuantSteps bits={total < 0.46 ? 3 : 4} p={total} />,
  bitsMove: ({ total }) => <Allocation guided={total > 0.42} />,
  bitsRange: ({ total }) => <RangePlot p={total} />,
  moePatch: ({ total }) => <RoutedSurface routed={total > 0.18} p={total} />,
  moeRoute: ({ total }) => <RoutingScores p={total} />,
  moeSeparate: ({ total }) => <Directions p={clamp(total * 1.5)} />,
  stereoPair: ({ total }) => <Disparity p={clamp(0.1 + total * 1.3)} />,
  stereoBase: ({ total }) => <Disparity base={mix(0.1, 0.3, clamp((total - 0.2) * 2))} />,
  stereoObjects: ({ total }) => <DataMix p={total} />,
};
export const applicationComparisons = {
  'bilalora-dehazing': (second) => <Adapters select={second} />,
  'budget-vision-nas': (second) => <Budget limit={second ? 7 : 4} />,
  'gradient-bit-allocation': (second) => <Allocation guided={second} />,
  'moeclip-patches': (second) => <RoutedSurface routed={second} />,
  'stereo-training-data': (second) => <Disparity expanded base={second ? 0.3 : 0.1} />,
};

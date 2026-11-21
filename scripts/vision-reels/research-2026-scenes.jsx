import React from 'react';
import {
  Caption,
  SignalBox,
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
} from './research-drawing';

const spectra = [
  [0.2, 0.8, 0.7, 0.3, 0.4, 0.6],
  [0.7, 0.3, 0.2, 0.8, 0.8, 0.2],
];
const wavelengths = ['#8e93df', '#86b7de', '#77d6c1', '#a4d997', '#e8be82', '#df968a'];

function Bands({ spectral, progress = 1 }) {
  return (
    <g>
      <Caption>
        {spectral ? '파장별 관측 · 여섯 막대의 높이' : '단순 RGB 센서 · 이웃 두 대역의 합'}
      </Caption>
      {spectra.map((s, row) => {
        const values = spectral ? s : [s[0] + s[1], s[2] + s[3], s[4] + s[5]];
        const base = 248 + row * 137;
        const slot = 482 / values.length;
        return (
          <g key={row}>
            <Text x={31} y={base - 31} color={row ? amber : blue}>
              표면 {row ? 'B' : 'A'}
            </Text>
            <path d={`M115 ${base}h500`} stroke={line} strokeWidth="2" />
            {values.map((v, i) => {
              const h = v * 84 * clamp(progress * 1.2 - i * 0.03);
              const x = 125 + i * slot;
              return (
                <g key={i}>
                  <rect
                    x={x}
                    y={base - h}
                    width={slot - 12}
                    height={h}
                    fill={wavelengths[spectral ? i : i * 2]}
                    rx="4"
                  />
                  <Text x={x + (slot - 12) / 2} y={base - h - 7} anchor="middle" size={20}>
                    {Number(v.toFixed(1))}
                  </Text>
                </g>
              );
            })}
          </g>
        );
      })}
      <Caption foot>
        {spectral ? '각 쌍의 합이 같아도 안쪽 분포는 다릅니다.' : 'A와 B 모두  [ 1, 1, 1 ]'}
      </Caption>
    </g>
  );
}

function SensorGrid({ coarse, x, progress }) {
  const n = coarse ? 4 : 12,
    size = 216 / n;
  return (
    <g>
      <Text x={x + 108} y={153} anchor="middle" size={21} color={coarse ? amber : blue}>
        {coarse ? '저해상도 다중분광' : '고해상도 RGB'}
      </Text>
      {range(n * n).map((i) => {
        const col = i % n,
          row = Math.floor(i / n);
        const surface = col / n + 0.33 * (row / n) > 0.62;
        return (
          <rect
            key={i}
            x={x + col * size}
            y={177 + row * size}
            width={size - 1}
            height={size - 1}
            fill={surface ? '#ab7866' : '#458e91'}
            stroke={coarse ? '#29454d' : 'none'}
          />
        );
      })}
      <rect
        x={x + Math.min(n - 1, Math.floor(progress * n)) * size}
        y={177}
        width={size}
        height={216}
        fill="none"
        stroke={coarse ? amber : blue}
        strokeWidth="3"
      />
    </g>
  );
}

function SensorSample({ progress }) {
  return (
    <g>
      <Caption>같은 경계를 다른 간격으로 표본화합니다.</Caption>
      <SensorGrid x={51} progress={progress} />
      <SensorGrid x={384} coarse progress={progress} />
      <Caption foot>분광 표본 한 칸이 여러 RGB 위치에 걸칩니다.</Caption>
    </g>
  );
}

function Fusion({ total }) {
  return (
    <g>
      <Caption>고해상도 공간 정보와 분광 단서의 결합</Caption>
      <SignalBox x={33} y={155} label="RGB 특징" />
      <SignalBox x={33} y={308} label="분광 특징" color={amber} />
      <Arrow x={223} y={184} dx={123} dy={60} c={blue} />
      <Arrow x={223} y={339} dx={123} dy={-77} c={amber} />
      {[false, true].map((ms, i) => {
        const t = (total * 2.5) % 1;
        return (
          <Point
            key={i}
            x={mix(224, 345, t)}
            y={mix(ms ? 339 : 184, ms ? 262 : 244, t)}
            c={ms ? amber : blue}
          />
        );
      })}
      <SignalBox x={355} y={226} w={254} label="색 보정 모델" color={mint} />
      <Caption foot>학습 신호는 최종 출력의 색 오차에서 옵니다.</Caption>
    </g>
  );
}

// Time runs left to right. A drifts to the neighbouring stripe after the occluder.
const timeX = (t) => 64 + 527 * t;
function trackY(t, teacher) {
  const truth = 271 - 52 * Math.sin(t * 4);
  const drift = clamp((t - 0.48) / 0.24);
  return teacher === 'A' ? truth + drift * 70 : truth + 10 * Math.max(0, 1 - t / 0.43);
}
function trace(fn, until = 1) {
  return range(91)
    .map((i) => {
      const t = (until * i) / 90;
      return (i ? 'L' : 'M') + timeX(t).toFixed(1) + ' ' + fn(t).toFixed(1);
    })
    .join(' ');
}
function Traces({ progress = 1, select = false, emphasize = false }) {
  const teacher = (t) => (select && t >= 0.55 ? 'B' : 'A');
  return (
    <g>
      <Caption>가로축은 시간 · 세로축은 영상 안의 위치</Caption>
      <Tile x={35} y={140} w={594} h={260} />
      <rect x={timeX(0.38)} y="143" width={timeX(0.55) - timeX(0.38)} height="254" fill="#364953" />
      <Text x={timeX(0.465)} y={178} anchor="middle" size={19}>
        가림
      </Text>
      {['A', 'B'].map((s, i) => (
        <path
          key={s}
          d={trace((t) => trackY(t, s), progress)}
          fill="none"
          stroke={i ? blue : amber}
          strokeWidth="4"
          strokeDasharray={emphasize ? '7 7' : undefined}
          opacity={emphasize ? 0.65 : 1}
        />
      ))}
      {emphasize && (
        <path
          d={trace((t) => trackY(t, teacher(t)), progress)}
          fill="none"
          stroke={mint}
          strokeWidth="7"
        />
      )}
      <Point
        x={timeX(progress)}
        y={trackY(progress, teacher(progress))}
        c={emphasize ? mint : amber}
      />
      <Text x={53} y={381} color={amber} size={20}>
        A
      </Text>
      <Text x={88} y={381} color={blue} size={20}>
        B
      </Text>
      <Text x={590} y={380} anchor="end" size={18} color={dim}>
        시간 →
      </Text>
      <Caption foot>
        {emphasize
          ? select
            ? '선택 궤적  ·  A → B'
            : '선택 궤적  ·  교사 A 고정'
          : '두 교사가 가림 뒤 서로 다른 후보를 냅니다.'}
      </Caption>
    </g>
  );
}
function Score({ total }) {
  const a = (t) => 0.78 - 0.5 * clamp((t - 0.38) / 0.35);
  const b = (t) => 0.52 + 0.32 * clamp((t - 0.38) / 0.35);
  const y = (v) => 378 - 191 * v;
  return (
    <g>
      <Caption>같은 시점의 두 후보에 매긴 신뢰도 · 예시</Caption>
      <Tile x={34} y={146} w={594} h={255} />
      {[a, b].map((fn, i) => (
        <g key={i}>
          <path
            d={trace((t) => y(fn(t)), total)}
            fill="none"
            stroke={i ? blue : amber}
            strokeWidth="5"
          />
          <Point x={timeX(total)} y={y(fn(total))} c={i ? blue : amber} />
        </g>
      ))}
      <Text x={55} y={180} size={20} color={amber}>
        교사 A
      </Text>
      <Text x={153} y={180} size={20} color={blue}>
        교사 B
      </Text>
      <Text x={590} y={380} anchor="end" size={18} color={dim}>
        시간 →
      </Text>
      <Caption foot>
        {a(total) >= b(total)
          ? '현재 프레임에서 A의 점수가 높습니다.'
          : '현재 프레임에서 B의 점수가 높습니다.'}
      </Caption>
    </g>
  );
}

const nodeX = [101, 327, 559];
const channelY = (n) => 151 + n * 43;
const retained = [true, false, true, true, false, true];

function ClassSet({ total }) {
  const labels = ['사과', '배', '의자', '컵', '버스', '시계'];
  const marks = [
    'M14 12C8 6 1 11 3 19s6 10 11 7c6 3 11-2 12-9 0-7-7-9-12-5z M14 11q0-5 6-7',
    'M14 5q5-3 6 4l1 6c2 4 7 7 6 12-2 7-21 7-23 0-1-5 5-10 7-14l1-6z',
    'M5 6h18v15H5z M4 21h22 M7 22v9 M23 22v9',
    'M4 8h17v12q0 7-8 7t-9-7z M21 9h4q7 5-3 10',
    'M3 6h24v17H3z M6 10h18v6H6z M7 23v4 M23 23v4',
    'M10 4h10 M10 27h10 M15 7a9 9 0 1 0 .1 0 M15 11v6l4 2',
  ];
  return (
    <g>
      <Caption>선별기가 구별해야 하는 두 종류를 고릅니다.</Caption>
      {labels.map((label, i) => {
        const x = 57 + (i % 3) * 188,
          y = 152 + Math.floor(i / 3) * 106;
        const fade = i > 1 ? mix(1, 0.33, clamp(total * 2)) : 1;
        const c = i > 1 ? dim : mint;
        return (
          <g key={label} opacity={fade}>
            <Tile x={x} y={y} w={164} h={84} border={c} />
            <path
              d={marks[i]}
              transform={`translate(${x + 18} ${y + 17}) scale(1.6)`}
              stroke={c}
              strokeWidth="1.8"
              fill="none"
              strokeLinejoin="round"
            />
            <Text x={x + 86} y={y + 51} color={c}>
              {label}
            </Text>
          </g>
        );
      })}
      <Caption foot>목표 클래스의 표본으로 분류 손실을 평가합니다.</Caption>
    </g>
  );
}
function MlpMask({ pruning = 0 }) {
  const layers = ['입력', '중간 채널', '출력'];
  return (
    <g>
      <Caption>MLP · 연결된 두 선형층</Caption>
      {layers.map((l, i) => (
        <Text key={l} x={nodeX[i]} y={128} size={18} color={dim} anchor="middle">
          {l}
        </Text>
      ))}
      {range(6).map((ch) => {
        const y = channelY(ch),
          removed = !retained[ch];
        const color = removed && pruning > 0.5 ? amber : mint;
        return (
          <g key={ch}>
            {range(3).map((i) => (
              <g
                key={i}
                opacity={removed ? mix(0.7, 0.04, pruning) : 0.65}
                stroke={removed ? amber : mint}
                strokeWidth="2"
              >
                <path d={`M101 ${205 + i * 65}L327 ${y}L559 ${205 + i * 65}`} fill="none" />
              </g>
            ))}
            <circle cx="327" cy={y} r="13" fill={panel} stroke={color} strokeWidth="3" />
            {removed && pruning > 0 && (
              <path
                d={`M320 ${y - 7}l14 14m0 -14l-14 14`}
                opacity={pruning}
                stroke={amber}
                strokeWidth="3"
              />
            )}
          </g>
        );
      })}
      {[101, 559].map((x) =>
        range(3).map((i) => (
          <circle
            key={x + '-' + i}
            cx={x}
            cy={205 + i * 65}
            r="9"
            stroke={blue}
            strokeWidth="2"
            fill={panel}
          />
        )),
      )}
      <Caption foot>
        {pruning > 0.5
          ? '마스크  [ 1, 0, 1, 1, 0, 1 ]   ·   4개 유지'
          : '마스크  [ 1, 1, 1, 1, 1, 1 ]   ·   6개 유지'}
      </Caption>
    </g>
  );
}
function Energy({ total }) {
  const values = [1, 0.85, 0.7, 0.49, 0.32, 0.22, 0.13, 0.09];
  const energy = values.map((v) => v * v).reduce((a, b) => a + b);
  const keep = Math.min(values.length, 1 + Math.floor(total * 8));
  const fraction = values.slice(0, keep).reduce((a, b) => a + b * b, 0) / energy;
  return (
    <g>
      <Caption>특잇값을 큰 순서로 쌓는 예시</Caption>
      {values.map((v, i) => (
        <g key={i}>
          <rect
            x={65 + 68 * i}
            y={346 - 165 * v}
            width="49"
            height={165 * v}
            rx="4"
            fill={i < keep ? blue : panel}
            stroke={i < keep ? blue : line}
          />
          <Text x={89 + 68 * i} y={376} size={18} color={dim} anchor="middle">
            {i + 1}
          </Text>
        </g>
      ))}
      <Text x={57} y={164} color={mint}>
        보존 에너지 {Math.round(fraction * 100)}%
      </Text>
      <Caption foot>제곱합의 비율을 보면 남길 차원을 정할 수 있습니다.</Caption>
    </g>
  );
}

function Layers({ progress }) {
  const weights = [0.6, 0.2, 0.2];
  const labels = ['앞층', '뒤층', '남은 투과율'];
  const colors = [amber, blue, dim];
  return (
    <g>
      <Caption>앞에서 뒤로 합성한 픽셀 하나</Caption>
      {weights.map((v, i) => {
        const w = 430 * v,
          offset = i === 0 ? 0 : i === 1 ? 258 : 344;
        return (
          <g key={i}>
            <rect
              x={98 + offset}
              y="190"
              width={w * clamp(progress * 3 - i)}
              height="70"
              fill={colors[i]}
            />
            <rect x={98 + offset} y="190" width={w} height="70" fill="none" stroke={line} />
            <rect x={52 + i * 197} y="308" width="13" height="13" fill={colors[i]} />
            <Text x={74 + i * 197} y={324} color={colors[i]} size={20}>
              {labels[i]}
            </Text>
            <Text x={74 + i * 197} y={365} size={30}>
              {v.toFixed(2)}
            </Text>
          </g>
        );
      })}
      <Caption foot>뒤층의 가중치 = (1 − 0.60) × 0.50 = 0.20</Caption>
    </g>
  );
}
const clusters = [
  [112, 213],
  [215, 183],
  [308, 244],
  [422, 188],
  [535, 232],
  [204, 320],
  [410, 324],
];
function LoadScene({ filtered = false, progress = 0.3 }) {
  const cx = mix(136, 480, progress);
  return (
    <g>
      <Caption>카메라 시점과 장면 묶음 · 위에서 본 예시</Caption>
      <Tile x={32} y={136} w={596} h={273} />
      <path d={`M${cx} 385l-91 -232h182z`} fill="#4c7c79" opacity=".22" />
      {clusters.map(([x, y], i) => {
        const active = !filtered || Math.abs(x - cx) < 112;
        const c = active ? mint : line;
        return (
          <g key={i} opacity={active ? 1 : 0.45}>
            {range(7).map((j) => {
              const dx = 22 * Math.cos(j * 2),
                dy = 16 * Math.sin(j * 2);
              return (
                <ellipse
                  key={j}
                  cx={x + dx}
                  cy={y + dy}
                  rx={16 + (j % 3) * 2}
                  ry={6 + (j % 4)}
                  transform={`rotate(${i * 19 + j * 11} ${x + dx} ${y + dy})`}
                  fill={active ? '#3e8a81' : panel}
                  stroke={c}
                  strokeWidth="1.4"
                />
              );
            })}
          </g>
        );
      })}
      <path d={`M${cx} 365l-17 22h34z`} fill={amber} />
      <Text x={58} y={389} size={18} color={amber}>
        카메라
      </Text>
      <Caption foot>
        {filtered ? '강조된 묶음만 GPU에 읽어 옵니다.' : '모든 묶음이 GPU 메모리에 있습니다.'}
      </Caption>
    </g>
  );
}
function PixelGroup({ total }) {
  const x = mix(220, 405, total),
    y = 241;
  const alpha = Math.exp(-0.5 * (((x - 225) / 46) ** 2 + ((y - 237) / 38) ** 2));
  const keep = alpha >= 1 / 255;
  return (
    <g>
      <Caption>2 × 2 픽셀 그룹 · 대표 위치에서 먼저 검사</Caption>
      {range(4).map((i) => {
        const px = 225 + (i % 2) * 67,
          py = 237 + Math.floor(i / 2) * 67;
        return (
          <g key={i}>
            <rect
              x={px - 33}
              y={py - 33}
              width="66"
              height="66"
              fill={panel}
              stroke={i === 0 ? amber : line}
              strokeWidth="3"
            />
            <circle cx={px} cy={py} r="4" fill={i === 0 ? amber : dim} />
          </g>
        );
      })}
      {[1, 0.68, 0.34].map((r, i) => (
        <ellipse
          key={i}
          cx={x}
          cy={y}
          rx={82 * r}
          ry={60 * r}
          fill={mint}
          fillOpacity=".12"
          stroke={mint}
          strokeOpacity=".65"
        />
      ))}
      <Text x={48} y={171} color={amber} size={20}>
        대표 픽셀 α = {alpha.toFixed(3)}
      </Text>
      <Text x={464} y={277} size={22} color={keep ? mint : amber}>
        {keep ? '그룹 계산' : '그룹 생략'}
      </Text>
      <Caption foot>α &lt; 1/255이면 이 그룹에서 해당 가우시안을 건너뜁니다.</Caption>
    </g>
  );
}

const gridW = 12,
  gridH = 7;
function covered(c, r) {
  return c < 7 + (r < 2 ? 1 : 0) - (r > 4 ? 1 : 0);
}
function qualityColor(c, r) {
  if ((c === 5 || c === 6) && r >= 2 && r <= 4) return '#e5a36c';
  if (c >= 9 && r < 3) return '#dead73';
  return ['#51968b', '#69ab96', '#76b5a0'][(c * 3 + r * 2 + Math.floor(c / 3)) % 3];
}
function QualityMap({ full = false, progress = 1 }) {
  const cell = 34,
    x = 116,
    y = 143;
  return (
    <g>
      <Caption>
        {full ? '전체 품질 예측 · 사선은 비대응 영역' : '부분 품질 지도 · 참조 특징과 대응한 곳'}
      </Caption>
      <defs>
        <pattern id="inferred-hatch" width="10" height="10" patternUnits="userSpaceOnUse">
          <path d="M-1 1l2-2M0 10l10-10M9 11l2-2" stroke="#182d35" strokeWidth="2.5" />
        </pattern>
      </defs>
      {range(gridW * gridH).map((i) => {
        const c = i % gridW,
          r = Math.floor(i / gridW),
          seen = covered(c, r);
        const painted = (seen || full) && c + 0.3 * r <= progress * (gridW + 2);
        const left = x + c * cell,
          top = y + r * cell;
        return (
          <g key={i}>
            <rect
              x={left}
              y={top}
              width={cell - 1}
              height={cell - 1}
              fill={painted ? qualityColor(c, r) : panel}
              stroke={line}
            />
            {painted && !seen && (
              <rect
                x={left}
                y={top}
                width={cell - 1}
                height={cell - 1}
                fill="url(#inferred-hatch)"
              />
            )}
          </g>
        );
      })}
      <Text x={119} y={411} size={18} color={mint}>
        높은 유사도
      </Text>
      <Text x={253} y={411} size={18} color={amber}>
        낮은 유사도
      </Text>
      <Text x={389} y={411} size={18} color={dim}>
        {full ? '사선 = 추정' : '빈 칸 = 비대응'}
      </Text>
      <Caption foot>
        {full ? '문맥에서 추정한 값까지 포함합니다.' : '대응이 없는 위치의 점수는 비어 있습니다.'}
      </Caption>
    </g>
  );
}
function Warp({ total }) {
  const positions = [
    [0, 0],
    [1, 1],
    [3, 0],
    [4, 2],
    [1, 3],
    [3, 3],
  ];
  const start = 76,
    end = 405,
    top = 195,
    unit = 31;
  const t = clamp((total - 0.1) * 1.8);
  return (
    <g>
      <Caption>시점 이동에 따른 특징의 위치 변화</Caption>
      {[start, end].map((x, i) => (
        <g key={i}>
          <Tile x={x - 12} y={top - 20} w={202} h={183} />
          <Text x={x + 80} y={top - 37} anchor="middle" color={i ? mint : blue}>
            {i ? '합성 시점' : '참조 시점'}
          </Text>
          {range(6).map((c) => (
            <path key={c} d={`M${x + c * unit} ${top - 10}v158`} stroke={line} strokeWidth="1" />
          ))}
        </g>
      ))}
      {positions.map(([c, r], i) => {
        const sx = start + c * unit + 5,
          ex = end + c * unit + unit,
          py = top + r * unit + 10;
        return (
          <g key={i}>
            <circle cx={sx} cy={py} r="7" fill={blue} />
            <path d={`M${sx} ${py}h${ex - sx}`} stroke={blue} strokeDasharray="4 7" opacity=".45" />
            <Point x={mix(sx, ex, t)} y={py} c={mint} />
          </g>
        );
      })}
      <Caption foot>새로 드러난 표면에는 옮겨 올 대응 특징이 없습니다.</Caption>
    </g>
  );
}

export const newResults = {
  spectralResult: {
    caption: '표 3 · 모바일 센서 조건 · LPIENet',
    heads: ['오차 지표 ↓', 'RGB', 'RGB + MS'],
    rows: [
      ['평균 ΔE₀₀', '3.29', '1.66'],
      ['평균 재현 오차', '4.71', '3.11'],
    ],
    foot: '센서 감도로 렌더링한 분광 자료에서 평가했습니다.',
  },
  trackResult: {
    caption: '표 2 · 동일한 교사 다섯 개 · 위치 정확도 ↑',
    heads: ['평가 자료', '무작위 선택', '검증기 선택'],
    rows: [
      ['DAVIS', '77.7', '81.1'],
      ['RoboTAP', '78.0', '83.1'],
    ],
    foot: '가시점 기준 · 임계 거리 1, 2, 4, 8, 16 px에서 평균',
  },
  nuwaResult: {
    caption: '표 3 · Orin NX · 아홉 모델 평균',
    heads: ['가지치기 목표', '지연 시간 ↓', '파라미터'],
    rows: [
      ['DeiT-Base', '45.45 ms', '86.57 M'],
      ['40%', '29.70 ms', '51.75 M'],
      ['60%', '22.01 ms', '34.48 M'],
    ],
    foot: '같은 기기에서 측정한 추론 지연 시간입니다.',
  },
  seeleResult: {
    caption: '표 4 · Mip-NeRF 360 · AGX Orin',
    heads: ['3DGS 구성', 'FPS ↑', 'PSNR ↑'],
    rows: [
      ['코드 최적화', '21.75', '27.46'],
      ['전처리 추가', '46.15', '27.70'],
      ['전체 SEELE', '59.67', '27.72'],
    ],
    foot: 'FPS는 초당 프레임 수, PSNR의 단위는 dB입니다.',
  },
  iqaResult: {
    caption: '표 2 · Mip-NeRF 360 · DINOv2-SIM 기준',
    heads: ['모델 구성', '순위 상관 ↑'],
    rows: [
      ['부분 지도 입력 제외', '0.464'],
      ['전체 모델', '0.622'],
    ],
    foot: 'SRCC는 두 평가가 매긴 순위의 상관계수입니다.',
  },
};
export function NewScene({ scene, idx, phase, total }) {
  switch (scene) {
    case 'spectralBands':
      return <Bands spectral={idx === 0} progress={clamp(0.23 + phase * 2)} />;
    case 'spectralSample':
      return <SensorSample progress={total} />;
    case 'spectralFuse':
      return <Fusion total={total} />;
    case 'trackCandidates':
      return <Traces progress={clamp(0.1 + total * 0.9)} />;
    case 'trackScore':
      return <Score total={clamp(0.07 + total * 0.93)} />;
    case 'trackSelect':
      return <Traces progress={clamp(0.12 + total * 1.4)} select emphasize />;
    case 'nuwaTask':
      return <ClassSet total={total} />;
    case 'nuwaMask':
      return <MlpMask pruning={clamp(total * 2)} />;
    case 'nuwaBudget':
      return <Energy total={total} />;
    case 'seeleLayers':
      return <Layers progress={clamp(0.04 + total * 1.4)} />;
    case 'seeleLoad':
      return <LoadScene filtered={idx > 0} progress={total} />;
    case 'seeleGroup':
      return <PixelGroup total={total} />;
    case 'iqaWarp':
      return <Warp total={total} />;
    case 'iqaPartial':
      return <QualityMap progress={clamp(0.08 + total * 1.6)} />;
    case 'iqaComplete':
      return <QualityMap full={idx > 0} progress={idx > 0 ? clamp(0.56 + phase) : 1} />;
    default:
      throw Error('Unknown research scene ' + scene);
  }
}
export function NewComparison({ id, second }) {
  switch (id) {
    case 'spectral-mobile-color':
      return <Bands spectral={second} />;
    case 'verifier-point-tracking':
      return <Traces select={second} emphasize />;
    case 'nuwa-vit':
      return <MlpMask pruning={second ? 1 : 0} />;
    case 'seele-3dgs':
      return <LoadScene filtered={second} />;
    case 'pr-iqa':
      return <QualityMap full={second} />;
    default:
      throw Error('Unknown research comparison ' + id);
  }
}

import React from 'react';

const mint = '#83e0c2',
  amber = '#ffc67a',
  blue = '#93c8ff',
  ink = '#f2f2e6',
  dim = '#aec2c3',
  line = '#435f68',
  panel = '#20363e';
const range = (n) => Array.from({ length: n }, (_, i) => i);
const clamp = (x) => Math.max(0, Math.min(1, x));
const mix = (a, b, t) => a + (b - a) * t;
function Text({ x, y, children, size = 23, color = ink, anchor = 'start' }) {
  return (
    <text
      x={x}
      y={y}
      fontFamily="Noto Sans CJK KR, sans-serif"
      fontWeight="550"
      fontSize={size}
      fill={color}
      textAnchor={anchor}
    >
      {children}
    </text>
  );
}
function Tile({ x, y, w, h, color = panel, border = line, r = 9 }) {
  return (
    <rect x={x} y={y} width={w} height={h} fill={color} stroke={border} strokeWidth="2" rx={r} />
  );
}
function Arrow({ x, y, dx, dy, c = mint, dash = false }) {
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  return (
    <g stroke={c} strokeWidth="3" fill="none">
      <path d={`M${x} ${y}l${dx} ${dy}`} strokeDasharray={dash ? '6 6' : undefined} />
      <path transform={`translate(${x + dx} ${y + dy}) rotate(${angle})`} d="M-9 -5L0 0L-9 5" />
    </g>
  );
}
function Point({ x, y, c = amber }) {
  return (
    <g>
      <circle cx={x} cy={y} r="9" stroke={c} strokeWidth="2" fill="none" />
      <circle cx={x} cy={y} r="4" fill={c} />
    </g>
  );
}
function SourceMatrix({ sparse = false, progress = 1, row = 3 }) {
  const step = 33,
    left = 185,
    top = 133;
  return (
    <g>
      <Text x={24} y={104} size={22} color={dim}>
        첫 프레임의 위치 i × 다음 프레임의 위치 j
      </Text>
      {range(64).map((i) => {
        const a = Math.floor(i / 8),
          b = i % 8;
        const k = Math.floor(a / 2),
          l = Math.floor(b / 2);
        const inTile = l === k || l === Math.min(3, k + 1);
        const computed = (!sparse || inTile) && i <= progress * 64;
        const on = a === row && b === 4;
        return (
          <rect
            key={i}
            x={left + b * step}
            y={top + a * step}
            width="30"
            height="30"
            rx="3"
            fill={
              computed
                ? on
                  ? amber
                  : ['#326765', '#49867d', '#619388'][(a + 3 * b) % 3]
                : '#253940'
            }
            stroke={a === row && computed ? mint : line}
          />
        );
      })}
      <Text x={145} y={top + row * step + 22} color={mint} anchor="end">
        i = {row}
      </Text>
      <Text x={left + step * 4 + 12} y={top - 9} size={19} color={amber} anchor="middle">
        j = 4
      </Text>
      <Text x={27} y={450} color={mint}>
        {sparse ? '조회에 걸친 블록만 계산' : '8 × 8 = 64개 상관값'}
      </Text>
    </g>
  );
}
function Lookup({ progress }) {
  const x = 1.25 + 2.8 * progress,
    y = 1.55 + 0.7 * Math.sin(progress * Math.PI),
    left = 56,
    top = 151,
    st = 50,
    ix = Math.floor(x),
    iy = Math.floor(y);
  return (
    <g>
      <Text x={26} y={110} color={dim}>
        현재 추정한 도착 위치
      </Text>
      {range(35).map((i) => {
        const a = i % 7,
          b = Math.floor(i / 7);
        const weight = Math.max(0, 1 - Math.abs(a - x)) * Math.max(0, 1 - Math.abs(b - y));
        return (
          <g key={i}>
            <circle
              cx={left + a * st}
              cy={top + b * st}
              r={5 + weight * 17}
              fill={weight ? mint : line}
            />
          </g>
        );
      })}
      <rect
        x={left + ix * st}
        y={top + iy * st}
        width={st}
        height={st}
        stroke={blue}
        fill="none"
        strokeDasharray="5 4"
      />
      <Point x={left + x * st} y={top + y * st} />
      <Text x={418} y={204} size={21} color={amber}>
        ● 실수 좌표
      </Text>
      <Text x={418} y={250} size={21} color={mint}>
        ● 보간 이웃
      </Text>
      <Text x={27} y={442} color={mint}>
        도착점이 움직이면 필요한 셀도 바뀝니다.
      </Text>
    </g>
  );
}
// A local pixel trajectory over one exposure. Rotation and translation here are illustrative.
function trajectory(t, translation) {
  return [
    185 + 89 * Math.sin(t * 0.91) + translation * 117 * t,
    331 - 135 * (1 - Math.cos(t * 1.25)) - translation * 61 * t,
  ];
}
function BlurPath({ translation = 0, progress = 1, residual = false }) {
  const pts = range(25).map((i) => trajectory((i / 24) * progress, translation));
  const last = pts.at(-1),
    rotation = trajectory(progress, 0);
  return (
    <g>
      <Text x={28} y={109} size={21} color={dim}>
        노출 구간 · 센서 평면의 한 점
      </Text>
      <Tile x={30} y={135} w={596} h={258} />
      {range(10).map((i) => (
        <path key={i} d={`M${48 + i * 62} 140v248`} stroke={line} opacity=".45" />
      ))}
      {range(4).map((i) => (
        <path key={i} d={`M35 ${167 + i * 62}h588`} stroke={line} opacity=".45" />
      ))}
      {pts
        .filter((_, i) => i % 3 === 0)
        .map(([x, y], i) => (
          <g key={i} opacity={0.16 + i * 0.065}>
            <rect
              x={x - 17}
              y={y - 20}
              width="34"
              height="40"
              rx="4"
              fill="#c99d70"
              stroke="#ffe4b7"
            />
            <path d={`M${x - 16} ${y - 9}h32`} stroke="#fbe6c7" />
          </g>
        ))}
      <polyline
        points={pts.map((x) => x.join(',')).join(' ')}
        fill="none"
        stroke={amber}
        strokeWidth="4"
      />
      <Point x={last[0]} y={last[1]} />
      {residual && (
        <>
          <Arrow x={185} y={331} dx={rotation[0] - 185} dy={rotation[1] - 331} c={blue} />
          <Arrow
            x={rotation[0]}
            y={rotation[1]}
            dx={last[0] - rotation[0]}
            dy={last[1] - rotation[1]}
            c={mint}
          />
        </>
      )}
      <Text x={30} y={448} color={translation > 0.01 ? mint : blue}>
        {residual
          ? '파랑 · 회전     초록 · 남은 이동'
          : translation > 0.01
            ? '회전 + 병진 성분'
            : '회전 성분'}
      </Text>
    </g>
  );
}
function NoisePatch({ x, y, frame, w = 144 }) {
  const n = 10,
    st = w / n,
    cut = 4 + Math.round(frame % 3);
  return (
    <g>
      {range(n * n).map((i) => {
        const a = i % n,
          b = Math.floor(i / n),
          signal = a >= cut && a < cut + 3 && b > 2 && b < 8 ? 115 : 45;
        const noise = Math.sin(173 * i + frame * 79) * 23;
        const f = Math.round(signal + noise);
        return (
          <rect
            key={i}
            x={x + a * st}
            y={y + b * st}
            width={st - 0.6}
            height={st - 0.6}
            fill={`rgb(${f},${f + 8},${f + 4})`}
          />
        );
      })}
    </g>
  );
}
function RawFrames({ previous = false, frame = 4 }) {
  return (
    <g>
      <Text x={24} y={108} color={dim} size={22}>
        같은 현재 프레임 · 입력 구성 비교
      </Text>
      {previous && (
        <>
          <NoisePatch x={37} y={165} frame={frame - 1} />
          <Text x={109} y={346} anchor="middle">
            이전 RAW
          </Text>
        </>
      )}
      {!previous && (
        <rect
          x="37"
          y="165"
          width="144"
          height="144"
          rx="4"
          stroke={line}
          strokeDasharray="5 7"
          fill="none"
        />
      )}
      <NoisePatch x={227} y={165} frame={frame} />
      <Text x={299} y={346} anchor="middle">
        현재 RAW
      </Text>
      <Arrow x={379} y={240} dx={64} dy={0} />
      <Tile x={455} y={201} w={170} h={78} border={mint} />
      <Text x={540} y={248} anchor="middle">
        특징 결합
      </Text>
      <Text x={28} y={448} color={mint}>
        {previous ? '이전 + 현재 → 현재 프레임 복원' : '현재 → 현재 프레임 복원'}
      </Text>
    </g>
  );
}
function Pack({ progress }) {
  const colors = ['#c97e71', '#6bb995', '#7bc4a6', '#7da6d8'];
  return (
    <g>
      <Text x={27} y={109} size={22} color={dim}>
        공간의 네 위치 → 채널 네 개
      </Text>
      {range(4).map((i) => {
        const x0 = 62 + (i % 2) * 66,
          y0 = 190 + Math.floor(i / 2) * 66;
        const p = clamp(progress * 1.55 - i * 0.12),
          x = mix(x0, 342 + 46 * i, p),
          y = mix(y0, 191 + 22 * i, p);
        return (
          <g key={i}>
            <rect x={x0} y={y0} width="58" height="58" rx="5" fill="none" stroke={line} />
            <rect x={x} y={y} width="59" height="59" rx="6" fill={colors[i]} />
            <Text x={x + 29} y={y + 39} size={20} color="#14232a" anchor="middle">
              {['R', 'G₁', 'G₂', 'B'][i]}
            </Text>
          </g>
        );
      })}
      <Text x={28} y={443} color={mint}>
        2 × 2 × 1 → 1 × 1 × 4
      </Text>
    </g>
  );
}
function Attention({ diffuse = 0, progress = 1 }) {
  const dist = [0.1, 0.7, 0.1, 0.1].map((q, i) => mix(q, [0.2, 0.4, 0.2, 0.2][i], diffuse));
  return (
    <g>
      <Text x={26} y={110} color={dim} size={21}>
        프롬프트 토큰 하나가 보는 위치 네 개
      </Text>
      {dist.map((v, i) => {
        const x = 62 + i * 149,
          height = v * 225 * progress;
        return (
          <g key={i}>
            <rect
              x={x}
              y={321 - height}
              width="87"
              height={height}
              fill={i === 1 ? mint : blue}
              rx="5"
            />
            <Text x={x + 44} y={303 - height} anchor="middle">
              {v.toFixed(2)}
            </Text>
            <Text x={x + 44} y={363} size={21} color={dim} anchor="middle">
              위치 {i + 1}
            </Text>
          </g>
        );
      })}
      <path d="M36 323H625" stroke={line} strokeWidth="3" />
      <Text x={28} y={445} color={mint}>
        가중합에 쓰는 확률의 합 = 1
      </Text>
    </g>
  );
}
function CrossBranches({ progress, step }) {
  const p = (progress * 2) % 1;
  return (
    <g>
      <Text x={26} y={110} color={dim}>
        두 방향의 교차 어텐션
      </Text>
      <Tile x={35} y={170} w={204} h={128} border={amber} />
      <Text x={137} y={242} anchor="middle">
        프롬프트 토큰
      </Text>
      <Tile x={424} y={170} w={197} h={128} border={mint} />
      <Text x={521} y={242} anchor="middle">
        영상 특징
      </Text>
      <Arrow x={242} y={197} dx={173} dy={0} c={amber} />
      <Arrow x={420} y={270} dx={-174} dy={0} c={mint} />
      <circle cx={mix(243, 412, p)} cy={197} r="8" fill={amber} />
      <circle cx={mix(416, 248, p)} cy={270} r="8" fill={mint} />
      {step >= 2 && <path d="M42 317v27h576v-27" fill="none" stroke={blue} strokeWidth="3" />}
      <Text x={27} y={442} color={step >= 2 ? blue : amber}>
        {step >= 2 ? '함께 재구성 · 결합된 두 출력' : '한 경로의 표현이 다른 경로의 입력에 영향'}
      </Text>
    </g>
  );
}
function GainBars({ colorGain = 0, progress = 1 }) {
  const input = [0.2, 0.4, 0.6],
    gain = [3, 2, 1.5].map((v) => mix(2, v, colorGain)),
    colors = ['#ee938c', '#83e0b4', '#8ebbf3'];
  return (
    <g>
      <Text x={27} y={107} size={21} color={dim}>
        선형 채널 값 · 설명용 픽셀 하나
      </Text>
      {input.map((v, i) => {
        const y = 157 + i * 74;
        const out = v * mix(1, gain[i], progress);
        return (
          <g key={i}>
            <Text x={28} y={y + 24}>
              {'RGB'[i]}
            </Text>
            <rect x="82" y={y} width={out * 330} height="30" rx="4" fill={colors[i]} />
            <path
              d={`M${82 + v * 330} ${y - 5}v40`}
              stroke={ink}
              strokeWidth="2"
              strokeDasharray="3 3"
            />
            <Text x={560} y={y + 25} anchor="middle">
              {out.toFixed(2)}
            </Text>
          </g>
        );
      })}
      <Text x={28} y={421} size={23} color={dim}>
        점선 · 원래 값
      </Text>
      <Text x={295} y={421} size={24} color={mint}>
        {colorGain > 0.5 ? '게인 (3, 2, 1.5)' : '게인 (2, 2, 2)'}
      </Text>
    </g>
  );
}
function ColorGrid({ progress, idx }) {
  return (
    <g>
      <Text x={25} y={109} size={22} color={dim}>
        위치별 보정과 RGB 색 좌표의 전역 매핑
      </Text>
      {range(36).map((i) => {
        const a = i % 6,
          b = Math.floor(i / 6);
        return (
          <rect
            key={i}
            x={36 + a * 32}
            y={158 + b * 27}
            width="30"
            height="25"
            fill={`rgb(${55 + a * 20},${73 + b * 14},${89 + b * 10})`}
          />
        );
      })}
      {range(4).map((j) => (
        <g key={j} transform={`translate(${386 + j * 13} ${181 - j * 12})`}>
          <rect width="149" height="135" rx="3" stroke={blue} fill="#24383e" fillOpacity=".6" />
          {range(3).map((i) => (
            <path key={i} d={`M${36 + i * 37} 0v135 M0 ${33 + i * 34}h149`} stroke={line} />
          ))}
        </g>
      ))}
      <Point x={42 + progress * 173} y={230 + 42 * Math.sin(progress * 6)} />
      <Point x={436 + progress * 88} y={214 - progress * 31} c={mint} />
      <Text x={40} y={365} size={22}>
        국소 · bilateral grid
      </Text>
      <Text x={368} y={365} size={22}>
        전역 · 3D LUT
      </Text>
      <Text x={28} y={445} color={mint}>
        {idx < 2 ? '위치 · 가이드 값 → 주변 계수 보간' : '저해상도 예측 → 고해상도 조회'}
      </Text>
    </g>
  );
}
const results = {
  corrResult: {
    caption: '표 1 · 고해상도 전체 추론',
    heads: ['모델', '실행 시간 감소'],
    rows: [
      ['RAFT', '63%'],
      ['DPFlow', '9%'],
    ],
    foot: '모델별 처리 해상도와 병목이 다릅니다.',
  },
  gyroResult: {
    caption: '표 3 · 흐림 커널 구성 비교',
    heads: ['커널 정보', 'PSNR ↑'],
    rows: [
      ['회전만', '34.30 dB'],
      ['회전 + 추정 병진', '34.65 dB'],
      ['회전 + 정답 병진', '34.78 dB'],
    ],
    foot: '정답 병진은 실험에서 제공한 조건입니다.',
  },
  rawResult: {
    caption: '표 5 · Galaxy S25 Plus · 다중 프레임',
    heads: ['모델', '지연', '전류'],
    rows: [
      ['AQ', '17.94 ms', '366 mA'],
      ['BRQ', '12.91 ms', '244 mA'],
    ],
    foot: '고정 전압 5 V · 실온 25 °C',
  },
  carResult: {
    caption: '표 1 · COCO 마스크 평가 · SAM-B',
    heads: ['모델 / 정밀도', 'mAP ↑'],
    rows: [
      ['PTQ4SAM / W4A4', '24.7'],
      ['CAR-SAM / W4A4', '39.3'],
      ['부동소수점 기준', '55.8'],
    ],
    foot: '같은 W4A4에서 14.6 mAP 포인트 차이',
  },
  gainResult: {
    caption: 'FastGaMer · 저자 보고값',
    heads: ['평가 항목', '결과'],
    rows: [
      ['4K 실행 · V100', '6.2 ms'],
      ['PQ-PSNR 개선', '+1.4 dB'],
    ],
    foot: '속도와 복원 품질은 별도 지표입니다.',
  },
};
function Evidence({ scene, idx, phase }) {
  const d = results[scene],
    xs = d.heads.length === 3 ? [43, 301, 489] : [43, 400],
    active = Math.min(idx, d.rows.length - 1);
  return (
    <g>
      <Text x={27} y={106} color={dim} size={22}>
        {d.caption}
      </Text>
      {d.heads.map((h, i) => (
        <Text key={h} x={xs[i]} y={169} size={21} color={blue}>
          {h}
        </Text>
      ))}
      {d.rows.map((row, i) => {
        const y = 189 + i * 63;
        return (
          <g key={i}>
            <Tile
              x={25}
              y={y}
              w={608}
              h={51}
              border={i === active ? mint : line}
              color={i === active ? '#2b4b4a' : panel}
            />
            {row.map((v, j) => (
              <Text key={j} x={xs[j]} y={y + 34} size={23} color={j === 0 ? ink : mint}>
                {v}
              </Text>
            ))}
            {i === active && <rect x={28} y={y + 47} width={phase * 600} height="2" fill={mint} />}
          </g>
        );
      })}
      <Text x={27} y={447} color={amber} size={21}>
        {d.foot}
      </Text>
    </g>
  );
}
export function ResearchScene({ scene, idx, phase, total }) {
  if (results[scene]) return <Evidence {...{ scene, idx, phase }} />;
  switch (scene) {
    case 'corrPairs':
      return (
        <SourceMatrix
          progress={clamp(0.12 + total * 1.3)}
          row={Math.min(7, Math.floor(total * 8))}
        />
      );
    case 'corrLookup':
      return <Lookup progress={total} />;
    case 'corrBlocks':
      return <SourceMatrix sparse progress={clamp(0.16 + total * 1.8)} />;
    case 'gyroExposure':
      return <BlurPath progress={clamp(0.03 + total * 0.97)} />;
    case 'gyroResidual':
      return <BlurPath translation={clamp(total * 1.8)} residual progress={clamp(0.35 + total)} />;
    case 'gyroKernel':
      return <BlurPath translation={clamp(total * 2)} progress={0.45 + 0.55 * phase} />;
    case 'rawSensor':
      return <RawFrames frame={Math.floor(total * 16)} />;
    case 'rawPack':
      return <Pack progress={clamp(total * 1.4)} />;
    case 'rawTemporal':
      return <RawFrames previous={total > 0.2} frame={Math.floor(total * 14)} />;
    case 'carPrompt':
      return <CrossBranches progress={total} step={0} />;
    case 'carAttention':
      return <Attention diffuse={clamp((total - 0.33) * 2)} progress={clamp(0.35 + total * 3)} />;
    case 'carJoint':
      return <CrossBranches progress={total} step={idx} />;
    case 'gainPixel':
      return <GainBars progress={clamp(total * 1.5)} />;
    case 'gainColor':
      return <GainBars colorGain={clamp(total * 2)} progress={1} />;
    case 'gainGrid':
      return <ColorGrid progress={total} idx={idx} />;
    default:
      throw Error('Unknown research scene ' + scene);
  }
}
export function ResearchCompare({ id, second }) {
  switch (id) {
    case 'flow-correlation':
      return <SourceMatrix sparse={second} />;
    case 'gyrodvd':
      return <BlurPath translation={second ? 1 : 0} />;
    case 'mobile-raw-denoising':
      return <RawFrames previous={second} />;
    case 'car-sam':
      return <Attention diffuse={second ? 1 : 0} />;
    case 'fastgamer':
      return <GainBars colorGain={second ? 1 : 0} />;
    default:
      throw Error('Unknown research comparison ' + id);
  }
}

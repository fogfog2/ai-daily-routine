import React from 'react';
import lumen from './art/lumen.jpg';

const ink = '#f2f2e6',
  quiet = '#aec2c3',
  mint = '#83e0c2',
  amber = '#ffc67a',
  blue = '#93c8ff',
  line = '#46616a';
const unit = (x) => Math.max(0, Math.min(1, x));
const lerp = (a, b, t) => a + (b - a) * t;
function Label({ x, y, children, color = ink, size = 23, center = false }) {
  return (
    <text
      x={x}
      y={y}
      fill={color}
      fontSize={size}
      fontFamily="Noto Sans CJK KR, sans-serif"
      textAnchor={center ? 'middle' : 'start'}
    >
      {children}
    </text>
  );
}
function Mark({ x, y, color = mint }) {
  return (
    <g stroke={color} fill="none">
      <circle cx={x} cy={y} r="8" strokeWidth="3" />
      <path d={`M${x - 14} ${y}h9m10 0h9 M${x} ${y - 14}v9m0 10v9`} strokeWidth="2" />
    </g>
  );
}
function House({ x, slant = 0 }) {
  return (
    <g transform={`translate(${x} 146) skewY(${slant})`}>
      <rect x="-10" y="-50" width="248" height="238" rx="10" fill="#48616b" />
      <path d="M0 25L72 -27L219 13V172H0Z" fill="#d4b591" />
      <path d="M-6 25L70 -32L225 11" fill="none" stroke="#775748" strokeWidth="10" />
      {Array.from({ length: 7 }, (_, i) => (
        <path key={i} d={`M2 ${40 + i * 20}h215`} stroke="#ac8b6e" strokeWidth="2" />
      ))}
      {[12, 72, 132].map((left) => (
        <g key={left}>
          <rect
            x={left}
            y="43"
            width="39"
            height="56"
            fill="#2a424b"
            stroke="#f3dbb5"
            strokeWidth="5"
          />
          <path d={`M${left + 19} 43v56 M${left} 68h39`} stroke="#d7c7ae" strokeWidth="3" />
        </g>
      ))}
      <rect x="142" y="112" width="34" height="60" fill="#635447" />
      <circle cx="169" cy="145" r="2" fill={amber} />
    </g>
  );
}
function Windows({ scene, idx, phase, total }) {
  const resolving = scene === 'descriptors' ? 1 : unit((total - 0.56) / 0.32);
  const x1 = 111,
    y1 = 189,
    x2 = lerp(530, 470, resolving),
    y2 = 189 - (x2 - 398) * 0.07;
  return (
    <g>
      <House x={39} />
      <House x={398} slant={-4} />
      <path
        d={`M${x1} ${y1} Q318 102 ${x2} ${y2}`}
        pathLength="1"
        strokeDasharray="1"
        strokeDashoffset={1 - unit(total * 8 + 0.12)}
        fill="none"
        stroke={resolving > 0.85 ? mint : amber}
        strokeWidth="4"
      />
      <Mark x={x1} y={y1} />
      <Mark x={x2} y={y2} color={resolving > 0.85 ? mint : amber} />
      {(total > 0.52 || scene === 'descriptors') &&
        [
          [70, -25],
          [142, 112],
        ].map(([x, y], i) => (
          <path
            key={i}
            d={`M${39 + x} ${146 + y} Q324 ${145 + y + 14} ${398 + x} ${146 + y - x * 0.07}`}
            fill="none"
            stroke={blue}
            opacity=".8"
            strokeDasharray="6 5"
            strokeWidth="2"
          />
        ))}
      <Label x={52} y={364} color={quiet}>
        시점 A
      </Label>
      <Label x={406} y={364} color={quiet}>
        시점 B
      </Label>
      {scene === 'windows' ? (
        <Label x={28} y={440} color={resolving > 0.85 ? mint : amber}>
          {resolving > 0.85 ? '문과 지붕의 위치까지 비교' : '같은 모양이 반복되는 창문'}
        </Label>
      ) : (
        <g>
          {['특징점', '기술자', '매처', 'F 추정'].map((v, i) => (
            <g key={v}>
              <rect
                x={28 + i * 157}
                y="398"
                width="136"
                height="53"
                rx="9"
                stroke={i === Math.min(idx, 3) ? mint : line}
                fill="#24393e"
              />
              <Label x={96 + i * 157} y={432} center size={22}>
                {v}
              </Label>
            </g>
          ))}
          <circle cx={lerp(32, 626, (idx + phase) / 5)} cy="462" r="5" fill={mint} />
        </g>
      )}
    </g>
  );
}
const residuals = [1, 3, 6, 9];
export function Epipolar({ threshold, reveal = 1 }) {
  const count = residuals.filter((v) => v <= threshold).length;
  return (
    <g>
      <Label x={25} y={104} size={21} color={quiet}>
        정답 대응점에서 측정한 오차 · 설명용 네 대응
      </Label>
      {residuals.map((v, i) => {
        const x = 83 + i * 158,
          y = 277,
          pass = v <= threshold;
        return (
          <g key={v} opacity={0.12 + 0.88 * unit(reveal * 4 - i)}>
            <rect
              x={x - 58}
              y={y - threshold * 10}
              width="116"
              height={threshold * 20}
              fill="#28524e"
            />
            <line x1={x - 60} y1={y} x2={x + 60} y2={y} stroke={mint} strokeWidth="3" />
            <line
              x1={x}
              x2={x}
              y1={y}
              y2={y - v * 10}
              stroke={pass ? mint : amber}
              strokeWidth="2"
              strokeDasharray="4 3"
            />
            <Mark x={x} y={y - v * 10} color={pass ? mint : amber} />
            <Label x={x} y={382} center>
              {v} px
            </Label>
          </g>
        );
      })}
      <Label x={26} y={450} size={26} color={blue}>
        허용 {threshold.toFixed(threshold % 1 ? 1 : 0)} px
      </Label>
      <Label x={310} y={450} size={28} color={mint}>
        {count} / 4 · PCK {25 * count}%
      </Label>
    </g>
  );
}
function Pose({ total }) {
  const a = lerp(-0.62, -0.26, total),
    cx = 155,
    cy = 301;
  return (
    <g>
      <Label x={25} y={119} color={quiet}>
        카메라 방향의 각도 오차
      </Label>
      <path
        d={`M${cx + 64 * Math.cos(-0.83)} ${cy + 64 * Math.sin(-0.83)} A64 64 0 0 1 ${cx + 64 * Math.cos(a)} ${cy + 64 * Math.sin(a)}`}
        stroke={amber}
        strokeWidth="5"
        fill="none"
      />
      {[
        [-0.83, mint, '정답'],
        [a, amber, '추정'],
      ].map(([t, c, label]) => (
        <g key={label}>
          <path
            d={`M${cx} ${cy}l${204 * Math.cos(t)} ${204 * Math.sin(t)}`}
            stroke={c}
            strokeWidth="4"
          />
          <Label x={cx + 215 * Math.cos(t)} y={cy + 215 * Math.sin(t)} size={22} color={c}>
            {label}
          </Label>
        </g>
      ))}
      <Mark x={cx} y={cy} />
      <Label x={24} y={440} color={blue}>
        픽셀 단위의 오차
      </Label>
      <Label x={349} y={440} color={amber}>
        방향 오차 · 도(°)
      </Label>
    </g>
  );
}
const observed = [42, 40, 43, 37, 40, 35, 39, 34, 36, 32, 36, 31];
const temporal = [42, 41.6, 41.2, 40.3, 39.6, 38.4, 37.9, 36.5, 35.6, 34.8, 33.9, 33];
function Curve({ values, toY, progress, color }) {
  const pos = unit(progress) * (values.length - 1),
    last = Math.floor(pos);
  const toX = (i) => 54 + (i * 548) / (values.length - 1);
  const v = lerp(values[last], values[Math.min(last + 1, values.length - 1)], pos - last);
  const points = values
    .slice(0, last + 1)
    .map((n, i) => [toX(i), toY(n)])
    .concat([[toX(pos), toY(v)]]);
  return (
    <g>
      <polyline
        points={points.map((pt) => pt.join(',')).join(' ')}
        fill="none"
        stroke={color}
        strokeWidth="4"
      />
      <circle cx={toX(pos)} cy={toY(v)} r="6" fill={color} />
    </g>
  );
}
export function Trace({ history = true, progress = 1 }) {
  const x = lerp(135, 122, progress);
  return (
    <g>
      <defs>
        <clipPath id="stream-view">
          <rect x="25" y="90" width="274" height="144" rx="12" />
        </clipPath>
      </defs>
      <g clipPath="url(#stream-view)">
        <image href={lumen} x={-12 - 13 * progress} y="46" width="350" height="231" />
        <Mark x={x} y={159} />
      </g>
      <Label x={327} y={141} color={quiet} size={21}>
        같은 주름의 추적점
      </Label>
      <Label x={327} y={191} color={mint}>
        프레임 {Math.floor(progress * 11) + 1} / 12
      </Label>
      <path d="M45 265V400H615" fill="none" stroke={line} strokeWidth="3" />
      <Curve values={observed} toY={(n) => 392 - (n - 30) * 9} color={amber} progress={progress} />
      {history && (
        <Curve values={temporal} toY={(n) => 392 - (n - 30) * 9} color={mint} progress={progress} />
      )}
      <Label x={26} y={448} size={22} color={amber}>
        ● 단일 프레임 예시
      </Label>
      {history && (
        <Label x={306} y={448} size={22} color={mint}>
          ● 상태 활용 예시
        </Label>
      )}
    </g>
  );
}
function StateFlow({ progress }) {
  const cycle = (progress * 4) % 1;
  return (
    <g>
      <Label x={25} y={107} color={quiet}>
        해상도별 상태를 다음 시점에 전달
      </Label>
      {['t − 1', 't', 't + 1'].map((t, i) => (
        <Label key={t} x={178 + i * 193} y={150} center color={blue}>
          {t}
        </Label>
      ))}
      {Array.from({ length: 4 }, (_, j) => {
        const y = 172 + j * 56;
        return (
          <g key={j}>
            <Label x={22} y={y + 25} size={19}>
              {['미세', '중간 1', '중간 2', '거친'][j]}
            </Label>
            {[0, 1, 2].map((i) => (
              <g key={i}>
                <rect
                  x={128 + i * 193}
                  y={y}
                  width="103"
                  height="36"
                  rx="6"
                  stroke={line}
                  fill="#244842"
                />
                {[0, 1, 2, 3].map((k) => (
                  <rect
                    key={k}
                    x={137 + i * 193 + k * 23}
                    y={y + 10}
                    width="14"
                    height="16"
                    fill={k === Math.floor(cycle * 4) ? amber : mint}
                    opacity={0.55 + j * 0.1}
                  />
                ))}
                {i < 2 && (
                  <g>
                    <path
                      d={`M${232 + i * 193} ${y + 18}h86m-9 -6l9 6l-9 6`}
                      fill="none"
                      stroke={line}
                      strokeWidth="3"
                    />
                    <circle cx={234 + i * 193 + cycle * 81} cy={y + 18} r="5" fill={mint} />
                  </g>
                )}
              </g>
            ))}
          </g>
        );
      })}
      <Label x={28} y={452} color={mint}>
        해상도 4개 × 블록별 은닉 상태 4개
      </Label>
    </g>
  );
}
function Scale({ idx, phase }) {
  const flat = idx < 3,
    scales = flat ? [2, 2, 2, 2] : [1.5, 2.5, 1.5, 2.5];
  return (
    <g>
      <Label x={25} y={125} color={quiet}>
        프레임마다 정답에 맞춘 보정 스케일
      </Label>
      {[1, 2, 3].map((v) => (
        <g key={v}>
          <path d={`M42 ${355 - (v - 1) * 88}h571`} stroke={line} strokeDasharray="5 6" />
          <Label x={19} y={361 - (v - 1) * 88} size={17}>
            {v}
          </Label>
        </g>
      ))}
      <Curve
        values={scales}
        toY={(v) => 355 - (v - 1) * 88}
        progress={0.2 + 0.8 * phase}
        color={flat ? mint : amber}
      />
      <Label x={25} y={422} color={blue}>
        평균 스케일 2.0
      </Label>
      <Label x={342} y={422} color={flat ? mint : amber}>
        표준편차 {flat ? '0.0' : '0.5'}
      </Label>
    </g>
  );
}
function Runtime({ idx, phase }) {
  if (idx === 0)
    return (
      <g>
        <Label x={25} y={118} color={quiet}>
          C3VD split 1 · 그림 4
        </Label>
        {Array.from({ length: 9 }, (_, i) => (
          <rect
            key={i}
            x={28 + i * 68}
            y={213}
            width="54"
            height="74"
            rx="9"
            fill={i < 8 && phase * 10 > i ? mint : line}
          />
        ))}
        <Label x={28} y={357} size={30} color={mint}>
          8 / 9 영상에서 더 작은 σ
        </Label>
        <Label x={28} y={423} size={21} color={quiet}>
          비교 모델 · FlashDepth
        </Label>
      </g>
    );
  const data = [
    ['100', '40.2', '24.9'],
    ['500', '40.0', '25.0'],
    ['1000', '40.3', '24.8'],
    ['3000', '40.7', '24.6'],
  ];
  return (
    <g>
      <Label x={24} y={110} size={21} color={quiet}>
        RTX A6000 · 518×518 · BF16 · torch.compile
      </Label>
      {['프레임 수', '지연 (ms)', '처리율 (FPS)'].map((v, i) => (
        <Label key={v} x={60 + 198 * i} y={173} size={22}>
          {v}
        </Label>
      ))}
      {data.map((row, i) => {
        const active = i === Math.min(3, Math.floor(((idx + phase) / 4) * 4));
        return (
          <g key={row[0]}>
            <rect
              x="27"
              y={193 + 48 * i}
              width="605"
              height="43"
              rx="6"
              fill={active ? '#28534c' : '#24373d'}
            />
            {row.map((v, j) => (
              <Label key={j} x={61 + 198 * j} y={223 + 48 * i} color={active ? mint : ink}>
                {v}
              </Label>
            ))}
          </g>
        );
      })}
      <Label x={28} y={452} size={22} color={amber}>
        표 9 · 초기 5프레임 제외
      </Label>
    </g>
  );
}
export function NextScene({ scene, idx, phase, total }) {
  switch (scene) {
    case 'windows':
    case 'descriptors':
      return <Windows {...{ scene, idx, phase, total }} />;
    case 'epipolar':
      return (
        <Epipolar
          reveal={idx === 0 ? phase : 1}
          threshold={idx < 4 ? 2 : idx === 4 ? lerp(2, 7, unit(phase * 2)) : 7}
        />
      );
    case 'posemetric':
      return <Pose total={total} />;
    case 'depthtrack':
      return <Trace history={false} progress={total} />;
    case 'streamstate':
      return <StateFlow progress={total} />;
    case 'scaletrack':
      return <Scale idx={idx} phase={phase} />;
    case 'streambench':
      return <Runtime idx={idx} phase={phase} />;
    default:
      throw Error('Unknown scene ' + scene);
  }
}

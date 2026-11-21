import React from 'react';
import { NextScene, Epipolar, Trace } from './next-scenes';
import lumen from './art/lumen.jpg';

export const C = {
  bg: '#101c21',
  panel: '#182a30',
  line: '#39515a',
  white: '#f2f2e6',
  muted: '#aec2c3',
  mint: '#83e0c2',
  gold: '#ffc67a',
  blue: '#93c8ff',
  pink: '#fa9a92',
};
export const fixed = 'DejaVu Sans Mono, monospace';
export const clamp = (v) => Math.min(1, Math.max(0, v));
const mix = (a, b, u) => a + (b - a) * u;
const smooth = (v) => {
  const n = clamp(v);
  return n * n * (3 - 2 * n);
};
const ramp = (v, a, b) => smooth((v - a) / (b - a));
const seq = (n) => Array.from({ length: n }, (_, i) => i);
export function Txt({
  x,
  y,
  children,
  size = 23,
  fill = C.white,
  mono = false,
  weight = 550,
  anchor = 'start',
  ...props
}) {
  return (
    <text
      x={x}
      y={y}
      fontSize={size}
      fontWeight={weight}
      fill={fill}
      fontFamily={mono ? fixed : 'Noto Sans CJK KR, sans-serif'}
      textAnchor={anchor}
      {...props}
    >
      {children}
    </text>
  );
}
function Box({ x, y, w, h, fill = C.panel, stroke = C.line, r = 12, ...rest }) {
  return (
    <rect
      x={x}
      y={y}
      width={w}
      height={h}
      rx={r}
      fill={fill}
      stroke={stroke}
      strokeWidth="2"
      {...rest}
    />
  );
}
function Wire({ x1, y1, x2, y2, color = C.mint, dash = false, width = 3 }) {
  return (
    <line
      {...{ x1, y1, x2, y2 }}
      stroke={color}
      strokeWidth={width}
      strokeDasharray={dash ? '6 7' : undefined}
      strokeLinecap="round"
    />
  );
}
function Dot({ x, y, color = C.mint, r = 7 }) {
  return (
    <g>
      <circle cx={x} cy={y} r={r + 6} fill="none" stroke={color} strokeWidth="2" />
      <circle cx={x} cy={y} r={r} fill={color} stroke={C.bg} strokeWidth="2" />
    </g>
  );
}
function Packet({ a, b, y, u, color = C.mint }) {
  return (
    <g>
      <Wire x1={a} x2={b} y1={y} y2={y} color={C.line} />
      <circle cx={mix(a, b, u)} cy={y} r="6" fill={color} />
    </g>
  );
}
function Tool({ x, y }) {
  return (
    <g transform={`translate(${x} ${y}) rotate(29)`}>
      <path
        d="M-12 235 L-9 27 Q-7 19 0 12 L8 26 L13 235Z"
        fill="#8ba1aa"
        stroke="#c9e1dc"
        strokeWidth="3"
      />
      <path
        d="M-7 30 L-15 2 L-10 -10 L0 12 L10 -13 L15 -7 L8 28"
        fill="#dee5dc"
        stroke="#52666c"
        strokeWidth="3"
      />
      <path d="M2 30 V225" stroke="#4a626c" strokeWidth="4" />
    </g>
  );
}
function Scope({ mode = 'camera', movement = 0, weight = 0.5, legend = true }) {
  const dx = 38 * movement,
    bx = 229 - dx,
    by = 249,
    predictedX = 421 - dx,
    actualX = predictedX + 51 * movement,
    actualY = 281 - 24 * movement;
  return (
    <g>
      <defs>
        <clipPath id="view">
          <rect x="18" y="83" width="604" height="326" rx="16" />
        </clipPath>
        <radialGradient id="hot">
          <stop stopColor={C.gold} stopOpacity=".94" />
          <stop offset="1" stopColor="#f16a3f" stopOpacity="0" />
        </radialGradient>
      </defs>
      <g clipPath="url(#view)">
        <image
          href={lumen}
          x={-15 - dx}
          y="47"
          width="710"
          height="455"
          preserveAspectRatio="none"
        />
        <Tool x={actualX} y={actualY} />
        {mode === 'residual' && (
          <g>
            <rect x="18" y="83" width="604" height="326" fill={C.bg} opacity=".65" />
            <ellipse cx={actualX} cy={actualY} rx="106" ry="77" fill="url(#hot)" />
          </g>
        )}
        {mode === 'confidence' && (
          <g>
            <rect
              x="18"
              y="83"
              width="604"
              height="326"
              fill={C.mint}
              opacity={0.22 + weight * 0.23}
            />
            <ellipse cx={actualX} cy={actualY} rx="69" ry="59" fill="#14252b" opacity=".88" />
          </g>
        )}
        <Wire x1="229" y1={by} x2={bx} y2={by} dash />
        <Dot x={bx} y={by} />
        <Wire x1={predictedX} y1="281" x2={actualX} y2={actualY} color={C.gold} dash width={4} />
        <rect
          x={predictedX - 10}
          y="271"
          width="20"
          height="20"
          fill="none"
          stroke="white"
          strokeWidth="2"
          strokeDasharray="4 3"
        />
        <Dot x={actualX} y={actualY} color={C.gold} />
      </g>
      {legend && (
        <>
          <Txt x={22} y={451} size={22} fill={C.mint}>
            ● 배경점
          </Txt>
          <Txt x={204} y={451} size={22} fill={C.gold}>
            ● 도구 끝
          </Txt>
          <Txt x={397} y={451} size={22}>
            □ 예상 위치
          </Txt>
        </>
      )}
    </g>
  );
}
function Weighting({ step, p }) {
  if (step < 3 || step === 7)
    return <Scope movement={1} mode={step < 2 ? 'residual' : 'confidence'} />;
  const confidence = step === 6 ? 0.12 + 0.64 * p : 0.9 - 0.78 * p;
  const huber = 1.5; // Huber(e=2, delta=1).
  const errorTerm = confidence * huber,
    penalty = -0.5 * Math.log(confidence);
  return (
    <g>
      <Scope movement={1} mode="confidence" weight={confidence} legend={false} />
      <rect x={28} y={319} width={599} height={84} rx={8} fill={C.bg} opacity=".93" />
      <Txt x={42} y={353} size={20} mono fill={C.mint}>
        C · Huber(e)
      </Txt>
      <Txt x={42} y={385} size={20} mono fill={C.gold}>
        −λ log C
      </Txt>
      <rect x={224} y={338} width={178 * errorTerm} height={13} rx={5} fill={C.mint} />
      <rect x={224} y={372} width={178 * penalty} height={13} rx={5} fill={C.gold} />
      <Txt x={609} y={352} anchor="end" mono size={20} fill={C.mint}>
        {errorTerm.toFixed(2)}
      </Txt>
      <Txt x={609} y={386} anchor="end" mono size={20} fill={C.gold}>
        {penalty.toFixed(2)}
      </Txt>
      <Txt x={28} y={454} size={21} mono fill={C.white}>
        C = {confidence.toFixed(2)} e = 2 δ = 1 λ = 0.5
      </Txt>
    </g>
  );
}
function DepthDiagram({ p, step }) {
  const points = [
    [86, 282],
    [248, 131],
    [438, 173],
    [561, 268],
  ];
  const stage = Math.min(points.length - 2, Math.max(0, step - 1));
  return (
    <g>
      <path
        d="M55 337 L136 194 L162 226 L82 365Z M484 312 L551 198 L596 232 L526 348Z"
        fill="#273f48"
        stroke={C.blue}
        strokeWidth="3"
      />
      {points.slice(1).map(([x, y], i) => (
        <Wire
          key={i}
          x1={points[i][0]}
          y1={points[i][1]}
          x2={x}
          y2={y}
          dash={i > stage}
          color={i <= stage ? C.mint : C.line}
        />
      ))}
      {points.map(([x, y], i) => (
        <Dot key={i} x={x} y={y} color={i <= stage + 1 ? C.mint : C.line} r={7} />
      ))}
      <circle
        cx={mix(points[stage][0], points[stage + 1][0], p)}
        cy={mix(points[stage][1], points[stage + 1][1], p)}
        r="9"
        fill={C.gold}
      />
      <Txt x={45} y={393} size={23}>
        프레임 t
      </Txt>
      <Txt x={440} y={393} size={23}>
        프레임 t+1
      </Txt>
      <Txt x={198} y={108} size={21} fill={C.mint}>
        3D 점
      </Txt>
      <Txt x={377} y={144} size={21} fill={C.blue}>
        R · X + t
      </Txt>
      <Txt x={29} y={455} size={24} mono fill={C.gold}>
        {
          ['ray = K⁻¹p', 'X = D · K⁻¹p', 'X′ = RX + t', 'p′ ∼ KX′', 'e = |D(p′) − Z′|'][
            Math.min(step, 4)
          ]
        }
      </Txt>
    </g>
  );
}
function Adapter({ step, p }) {
  return (
    <g>
      <Box x={24} y={108} w={161} h={62} />
      <Txt x={104} y={148} anchor="middle">
        공유 인코더
      </Txt>
      {[
        ['깊이 · 신뢰도', 111],
        ['카메라 자세', 205],
      ].map(([v, y], i) => (
        <g key={v}>
          <Wire x1={185} y1={139} x2={344} y2={y + 26} color={i ? C.gold : C.mint} />
          <circle cx={mix(185, 344, p)} cy={mix(139, y + 26, p)} r="6" fill={i ? C.gold : C.mint} />
          <Box x={345} y={y} w={220} h={54} />
          <Txt x={455} y={y + 35} anchor="middle" size={22}>
            {v}
          </Txt>
        </g>
      ))}
      <Txt x={28} y={302} fill={C.muted} size={21}>
        FFN 가중치 업데이트
      </Txt>
      {seq(4).map((i) =>
        seq(8).map((j) => (
          <rect
            key={i + '-' + j}
            x={33 + j * 20}
            y={329 + i * 20}
            width="15"
            height="15"
            rx="2"
            fill={
              j === Math.floor(8 * p) % 8 ? C.gold : i === Math.floor(4 * p) % 4 ? C.blue : C.line
            }
          />
        )),
      )}
      <Txt x={227} y={359} size={24} fill={C.gold}>
        u · 랭크별
      </Txt>
      <Txt x={227} y={403} size={24} fill={C.blue}>
        v · 출력 채널별
      </Txt>
      <Txt x={30} y={467} size={25} mono fill={C.mint}>
        {step >= 3 ? 'Wdeploy = W₀ + ΔW' : 'ΔW = s [B ⊙ (v1ᵀ + 1uᵀ)] A'}
      </Txt>
    </g>
  );
}
function Results({ sr = false, step, p }) {
  const rows = sr
    ? [
        ['직접 QAT', '29.9114', '0.853'],
        ['전체 절차', '30.0003', '0.856'],
      ]
    : [
        ['기본 LoRA', '0.099', '0.538'],
        ['+ 신뢰도 손실', '0.095', '0.376'],
        ['+ DVM-LoRA', '0.088', '0.335'],
      ];
  const active = sr ? Math.min(step, 1) : Math.min(2, Math.max(0, step - 1));
  return (
    <g>
      <Txt x={27} y={113} size={21} fill={C.muted}>
        {sr ? '논문 표 4  ·  INT8 복원' : '논문 표 3  ·  SCARED'}
      </Txt>
      <Txt x={352} y={166} size={21} mono>
        {sr ? 'PSNR ↑' : 'AbsRel ↓'}
      </Txt>
      <Txt x={500} y={166} size={21} mono>
        {sr ? 'SSIM ↑' : 'TAE ↓'}
      </Txt>
      {rows.map(([label, v, w], i) => {
        const y = 188 + i * 68;
        return (
          <g key={label}>
            <Box
              x={20}
              y={y}
              w={617}
              h={54}
              r={7}
              fill={i === active ? '#2b484a' : C.panel}
              stroke={i === active ? C.mint : C.line}
            />
            <rect
              x={22}
              y={y + 49}
              width={i === active ? Math.max(1, p * 610) : 0}
              height="3"
              fill={C.mint}
            />
            <Txt x={38} y={y + 36} size={23}>
              {label}
            </Txt>
            <Txt x={353} y={y + 37} size={24} mono>
              {v}
            </Txt>
            <Txt x={500} y={y + 37} size={24} mono fill={C.mint}>
              {w}
            </Txt>
          </g>
        );
      })}
      <Txt x={28} y={431} size={22} fill={C.gold}>
        {sr ? '전체 절차에 교사 지도 포함' : 'DVM-LoRA만 적용한 조건'}
      </Txt>
      <Txt x={28} y={467} size={22} fill={C.muted}>
        {sr ? '같은 검증 표의 비교' : '표 3에 측정값 없음'}
      </Txt>
    </g>
  );
}
function Warehouse({ grid = 0, boxes = 0, p = 0.5 }) {
  const lx = 117 + 8 * p;
  return (
    <g>
      <defs>
        <pattern id="belt" width="27" height="28" patternUnits="userSpaceOnUse">
          <path d="M0 0 L-10 28 M27 0 L17 28" stroke="#73868a" strokeWidth="2" />
        </pattern>
      </defs>
      <Box x={23} y={92} w={607} h={315} fill="#415252" />
      <path d="M24 276L630 240V389L24 405Z" fill="#435758" />
      <path d="M24 299L630 266V337L24 386Z" fill="#1f3339" />
      <path d="M24 299L630 266V337L24 386Z" fill="url(#belt)" />
      {[
        [lx, 194, 1],
        [345, 174, 0.67],
      ].map(([x, y, s], i) => (
        <g key={i} transform={`translate(${x} ${y}) scale(${s})`}>
          <path d="M0 26L98 4L164 33L68 61Z" fill="#d8b98c" />
          <path d="M0 26L68 61V146L0 108Z" fill="#a7825d" />
          <path d="M68 61L164 33V114L68 146Z" fill="#c99c6d" />
          <path d="M44 16L113 46V78L128 74V42L61 12Z" fill="#eed7a6" />
          <path d="M83 88L110 80V101L83 108Z" fill="#eee8d5" />
        </g>
      ))}
      {grid > 0 && (
        <g opacity={grid}>
          <svg x="168" y="90" width="304" height="304" viewBox="0 0 304 304">
            <rect width="304" height="304" stroke={C.mint} fill="none" strokeWidth="4" />
            {seq(18).map((i) => (
              <path
                key={i}
                d={`M${(i + 1) * 16} 0V304 M0 ${(i + 1) * 16}H304`}
                fill="none"
                stroke={C.mint}
                strokeWidth="1.2"
              />
            ))}
          </svg>
        </g>
      )}
      {[
        [lx - 3, 193, 171, 153],
        [342, 173, 118, 100],
        [lx + 8, 202, 136, 125],
        [319, 152, 155, 125],
      ]
        .slice(0, boxes)
        .map(([x, y, w, h], i) => (
          <g key={i}>
            <rect
              {...{ x, y, width: w, height: h }}
              fill="none"
              stroke={i < 2 ? C.mint : C.gold}
              strokeWidth={i < 2 ? 4 : 2}
              strokeDasharray={i < 2 ? undefined : '7 5'}
            />
            <rect x={x} y={y - 22} width="48" height="22" fill={i < 2 ? C.mint : C.gold} />
            <Txt x={x + 3} y={y - 5} size={15} fill={C.bg} mono>
              {['.94', '.88', '.71', '.49'][i]}
            </Txt>
          </g>
        ))}
    </g>
  );
}
function Timer({ step, p, full = false }) {
  return (
    <g>
      <Txt x={30} y={122} size={22} fill={C.muted}>
        배치 1 · NVIDIA T4 · TensorRT 10.4 · FP16
      </Txt>
      {['입력 준비', '엔진 실행', '최종 선택'].map((t, i) => (
        <g key={t}>
          <Box
            x={24 + i * 210}
            y={191}
            w={191}
            h={86}
            fill={full ? '#463c32' : i === 1 ? '#234d49' : C.panel}
            stroke={full ? C.gold : i === 1 ? C.mint : C.line}
          />
          <Txt x={119 + i * 210} y={245} anchor="middle" size={25}>
            {t}
          </Txt>
        </g>
      ))}
      <Packet a={233} b={418} y={316} u={p} />
      <Txt x={325} y={376} anchor="middle" size={39} mono fill={C.mint}>
        1.0 ms
      </Txt>
      <path
        d="M30 396v18h590v-18"
        fill="none"
        stroke={step >= 3 ? C.gold : C.line}
        strokeWidth="3"
      />
      <Txt x={320} y={457} size={21} anchor="middle" fill={C.gold}>
        입력부터 최종 선택까지 · 측정값 미공개
      </Txt>
    </g>
  );
}
function Frontier({ step, p }) {
  return (
    <g>
      <Txt x={28} y={108} size={21} mono fill={C.muted}>
        COCO AP ↑
      </Txt>
      <path d="M101 134V404H602" fill="none" stroke={C.muted} strokeWidth="2" />
      {[
        [1, 218, '1.0 ms'],
        [1.4, 484, '1.4 ms'],
      ].map(([v, x, label]) => (
        <Txt key={v} x={x} y={443} anchor="middle" size={21} mono>
          {label}
        </Txt>
      ))}
      <Wire
        x1={218}
        y1={318}
        x2={mix(218, 484, step === 0 ? 0 : p)}
        y2={mix(318, 176, step === 0 ? 0 : p)}
        dash
      />
      <Dot x={218} y={318} />
      <Txt x={134} y={284} size={23} fill={C.mint}>
        Atto · 30.5
      </Txt>
      {step >= 1 && (
        <>
          <Dot x={484} y={176} color={C.gold} />
          <Txt x={391} y={142} size={23} fill={C.gold}>
            Femto · 37.8
          </Txt>
        </>
      )}
      <Txt x={300} y={486} size={20} fill={C.muted}>
        엔진 지연 중앙값 →
      </Txt>
    </g>
  );
}
function Textile({ x, y, size, contrast = 1, p = 0, zoom = 1 }) {
  // A fixed repeated-weave signal. The toy coefficient controls amplitude only.
  const tile = (size / 7) * zoom,
    lo = Math.round(137 - 56 * contrast),
    hi = Math.round(137 + 56 * contrast);
  const id = 'weave' + Math.round(x) + '-' + Math.round(y);
  return (
    <g>
      <defs>
        <pattern
          id={id}
          width={tile}
          height={tile}
          patternUnits="userSpaceOnUse"
          patternTransform={`translate(${x} ${y})`}
        >
          <rect width={tile} height={tile} fill={`rgb(${lo},${lo + 10},${lo + 11})`} />
          <path
            d={`M0 0L${tile / 2} ${tile / 2}L${tile} 0 M0 ${tile / 2}L${tile / 2} ${tile}L${tile} ${tile / 2}`}
            fill="none"
            stroke={`rgb(${hi},${hi + 12},${hi + 10})`}
            strokeWidth={Math.max(1, tile * 0.2)}
          />
        </pattern>
      </defs>
      <rect
        {...{ x, y, width: size, height: size }}
        rx="6"
        fill={`url(#${id})`}
        stroke={C.line}
        strokeWidth="2"
      />
      {p > 0 && (
        <rect
          x={x + size * (0.16 + 0.22 * p)}
          y={y + size * 0.22}
          width={size * 0.3}
          height={size * 0.3}
          fill="none"
          stroke={C.gold}
          strokeWidth="3"
        />
      )}
    </g>
  );
}
function Round({ step, p, example }) {
  const merged = example === undefined ? step >= 3 : example;
  const value = merged ? 0.98 : 0.49,
    dest = merged ? 1 : 0;
  const shown = mix(value, dest, p);
  return (
    <g>
      <Txt x={26} y={110} size={22} fill={C.muted}>
        단일 계수 예시 · scale = 1 · zero point = 0
      </Txt>
      <Txt x={30} y={170} size={30} fill={C.gold} mono>
        {merged ? 'Q(0.49 + 0.49)' : 'Q(0.49) + Q(0.49)'}
      </Txt>
      <Wire x1={74} y1={264} x2={592} y2={264} color={C.muted} />
      {[0, 0.5, 1].map((n) => (
        <g key={n}>
          <Wire x1={80 + 500 * n} y1={253} x2={80 + 500 * n} y2={278} color={C.muted} />
          <Txt x={80 + 500 * n} y={313} size={22} anchor="middle" mono>
            {n}
          </Txt>
        </g>
      ))}
      <Wire x1={80 + 500 * value} y1={232} x2={80 + 500 * shown} y2={232} color={C.gold} />
      <Dot x={80 + 500 * shown} y={232} color={C.gold} />
      <Textile x={35} y={358} size={104} contrast={dest} />
      <Txt x={170} y={399} size={24}>
        계수 출력
      </Txt>
      <Txt x={170} y={443} size={30} mono fill={C.mint}>
        {merged ? 'Q(0.98) = 1' : '0 + 0 = 0'}
      </Txt>
    </g>
  );
}
function Kernels({ step, p }) {
  const folded = ramp(step + p, 2.75, 4);
  return (
    <g>
      <Txt x={28} y={123} size={22} fill={C.muted}>
        평가 모드의 선형 분기
      </Txt>
      {['3×3', '1×1', '항등'].map((name, i) => {
        const x = mix(31, 427, folded),
          y = mix(168 + i * 91, 229, folded);
        return (
          <g key={name} opacity={1 - folded * 0.7}>
            <Box {...{ x, y }} w={137} h={53} />
            <Txt x={x + 68} y={y + 35} size={23} anchor="middle">
              {name}
            </Txt>
            <Wire x1={x + 137} y1={y + 26} x2={410} y2={255} color={C.mint} />
          </g>
        );
      })}
      <Box x={412} y={216} w={194} h={77} fill="#264742" stroke={C.mint} />
      <Txt x={507} y={265} anchor="middle" size={23}>
        배포 Conv
      </Txt>
      <Txt x={30} y={447} size={27} mono fill={C.gold}>
        W = Σ Wᵢ b = Σ bᵢ
      </Txt>
    </g>
  );
}
function Train({ step, p }) {
  return (
    <g>
      <Txt x={24} y={115} size={22} fill={C.muted}>
        융합된 연산 그래프
      </Txt>
      {['실수 가중치', '가짜 양자화', '배포 Conv'].map((v, i) => (
        <g key={v}>
          <Box
            x={18 + i * 209}
            y={180}
            w={192}
            h={78}
            stroke={i === Math.min(step, 2) ? C.gold : C.line}
          />
          <Txt x={114 + i * 209} y={230} size={24} anchor="middle">
            {v}
          </Txt>
        </g>
      ))}
      <Packet a={38} b={605} y={290} u={p} />
      <Txt x={34} y={356} fill={C.mint} size={22}>
        정답 영상 + 교사 복원 신호
      </Txt>
      <path
        d="M420 356H564V265"
        fill="none"
        stroke={C.mint}
        strokeWidth="3"
        strokeDasharray="8 5"
      />
      <Txt x={30} y={438} fill={C.gold} size={25} mono>
        FP weights → fake Q → INT8
      </Txt>
    </g>
  );
}
function DetectorPath({ train = 1, progress = 0.55 }) {
  const pulse = (progress * 3) % 1;
  const moving = (x1, y1, x2, y2, color) => (
    <circle cx={mix(x1, x2, pulse)} cy={mix(y1, y2, pulse)} r="6" fill={color} />
  );
  return (
    <g>
      <Txt x={28} y={111} size={22} fill={train > 0.5 ? C.gold : C.mint}>
        {train > 0.5 ? '학습 · 같은 입력을 두 모델에 전달' : '추론 · 학생 검출기 실행'}
      </Txt>
      <Box x={27} y={213} w={116} h={94} />
      <path d="M38 286l91-9" stroke={C.line} strokeWidth="5" />
      <g transform={`translate(${55 + 10 * pulse} 231)`}>
        <path d="M0 10L23 3L43 11L20 19Z" fill="#e3ba8d" />
        <path d="M0 10L20 19V47L0 39Z" fill="#ac835c" />
        <path d="M20 19L43 11V39L20 47Z" fill="#cc996b" />
      </g>
      <g opacity={train}>
        <Wire x1={144} y1={247} x2={234} y2={182} color={C.gold} />
        {moving(144, 247, 234, 182, C.gold)}
        <Box x={235} y={148} w={200} h={67} stroke={C.gold} />
        <Txt x={335} y={190} anchor="middle" size={23}>
          DINOv3 · 고정
        </Txt>
        <Wire x1={435} y1={180} x2={493} y2={221} color={C.gold} />
        {moving(435, 180, 493, 221, C.gold)}
        <Box x={495} y={194} w={138} h={60} stroke={C.gold} />
        <Txt x={564} y={232} size={22} anchor="middle">
          특징 정렬
        </Txt>
        <Wire x1={401} y1={299} x2={495} y2={241} color={C.mint} dash />
        {moving(401, 299, 495, 241, C.mint)}
      </g>
      <Wire x1={143} y1={278} x2={237} y2={331} color={C.mint} />
      {moving(143, 278, 237, 331, C.mint)}
      <Box x={237} y={300} w={198} h={65} stroke={C.mint} />
      <Txt x={336} y={340} anchor="middle">
        학생 검출기
      </Txt>
      <Wire x1={435} y1={332} x2={483} y2={332} color={C.mint} />
      {moving(435, 332, 483, 332, C.mint)}
      <Box x={485} y={300} w={148} h={65} stroke={C.mint} />
      <Txt x={559} y={340} anchor="middle" size={21}>
        상자 · 클래스
      </Txt>
      <Txt x={28} y={445} fill={C.muted} size={22}>
        {train > 0.5 ? '검출 손실 + λ × 특징 정렬 손실' : '검출기에 학습된 가중치 사용'}
      </Txt>
    </g>
  );
}
function FeatureGrid({ idx, p }) {
  const vectors = idx >= 3;
  const theta = idx === 3 ? Math.PI / 3 : idx === 4 ? ((1 - p) * Math.PI) / 3 : 0;
  return (
    <g>
      <Txt x={27} y={117} size={22} fill={C.muted}>
        {vectors ? '같은 공간 위치 · 벡터 방향 비교' : '해상도와 채널 축 맞추기'}
      </Txt>
      {vectors ? (
        <g>
          <path d="M98 340H399 M142 368V155" fill="none" stroke={C.line} strokeWidth="2" />
          <Wire x1={142} y1={340} x2={335} y2={340} color={C.gold} width={5} />
          <Wire
            x1={142}
            y1={340}
            x2={142 + 161 * Math.cos(theta)}
            y2={340 - 161 * Math.sin(theta)}
            color={C.mint}
            width={5}
          />
          <Dot x={335} y={340} color={C.gold} />
          <Dot x={142 + 161 * Math.cos(theta)} y={340 - 161 * Math.sin(theta)} />
          <Txt x={410} y={237} fill={C.gold}>
            ● 교사
          </Txt>
          <Txt x={410} y={281} fill={C.mint}>
            ● 학생
          </Txt>
          <Txt x={34} y={441} size={28} mono fill={C.mint}>
            cos({Math.round((theta * 180) / Math.PI)}°) = {Math.cos(theta).toFixed(2)}
          </Txt>
        </g>
      ) : (
        <g>
          {[0, 1].map((side) => {
            const n = side === 0 && idx === 0 ? 6 : 4;
            const x = side ? 389 : 69;
            const size = 161 / n;
            return (
              <g key={side}>
                {seq(n * n).map((k) => {
                  const row = Math.floor(k / n),
                    col = k % n;
                  return (
                    <rect
                      key={k}
                      x={x + col * size}
                      y={159 + row * size}
                      width={size - 3}
                      height={size - 3}
                      rx="2"
                      fill={
                        row === 1 && col === 2
                          ? side
                            ? C.mint
                            : C.gold
                          : ['#234447', '#335453', '#385d62'][(row + col) % 3]
                      }
                    />
                  );
                })}
                <Txt x={x + 80} y={362} anchor="middle" size={22}>
                  {side ? '학생 F₅' : '교사 패치'}
                </Txt>
              </g>
            );
          })}
          <Packet a={246} b={369} y={238} u={p} />
          <Txt x={30} y={443} size={23} fill={C.mint}>
            {idx < 2 ? '교사 격자 → 학생 해상도로 보간' : '학생 특징 → 교사의 채널 차원으로 투영'}
          </Txt>
        </g>
      )}
    </g>
  );
}
function GradientBand({ idx, p }) {
  const low = 1.9,
    high = 2.1;
  const value = idx < 4 ? 2 + 0.13 * Math.sin(p * Math.PI * 2) : idx === 4 ? 1.5 : mix(2, 2.4, p);
  const x = (v) => 70 + (v - 1.3) * 420;
  const factor = value < low ? high / value : value > high ? low / value : 1;
  return (
    <g>
      <Txt x={26} y={122} size={22} fill={C.muted}>
        대상 모듈의 기울기 비율 · 에폭 평균
      </Txt>
      <rect x={x(low)} y={204} width={x(high) - x(low)} height={99} fill="#29564c" />
      <path d="M60 270H616" stroke={C.line} strokeWidth="4" />
      {[1.5, 1.9, 2.1, 2.5].map((v) => (
        <g key={v}>
          <Wire x1={x(v)} y1={252} x2={x(v)} y2={283} color={C.muted} />
          <Txt x={x(v)} y={335} anchor="middle" mono size={19}>
            {v}%
          </Txt>
        </g>
      ))}
      <Txt x={x(value)} y={186} anchor="middle" size={23} fill={C.gold}>
        {value.toFixed(2)}%
      </Txt>
      <path d={`M${x(value) - 9} 198h18l-9 15Z`} fill={C.gold} />
      <Dot x={x(value)} y={245} color={C.gold} />
      <Txt x={32} y={429} size={25} fill={C.mint}>
        {idx < 4 ? '목표 2.0% · 허용 폭 ±0.1%p' : `다음 λ = 현재 λ × ${factor.toFixed(2)}`}
      </Txt>
    </g>
  );
}
function DistillationResults({ idx, p }) {
  const rows = [
    ['기본', '52.1', '56.7'],
    ['+ DSI', '52.3', '56.4'],
    ['+ DSI + GAM', '52.6', '56.8'],
  ];
  const active = idx === 0 ? 0 : idx === 1 ? Math.min(2, Math.floor(p * 3)) : idx === 2 ? 1 : 2;
  return (
    <g>
      <Txt x={25} y={113} size={22} fill={C.muted}>
        RT-DETRv2-L · COCO 검증 · 표 2
      </Txt>
      <Txt x={375} y={171} mono size={23}>
        AP
      </Txt>
      <Txt x={508} y={171} mono size={23}>
        AP75
      </Txt>
      {rows.map(([label, a, b], i) => {
        const y = 191 + i * 67;
        return (
          <g key={label}>
            <Box
              x={24}
              y={y}
              w={607}
              h={53}
              stroke={active === i ? C.mint : C.line}
              fill={active === i ? '#2c4d4a' : C.panel}
            />
            <Txt x={44} y={y + 35} size={24}>
              {label}
            </Txt>
            <Txt x={375} y={y + 35} mono size={24}>
              {a}
            </Txt>
            <Txt x={508} y={y + 35} mono size={24} fill={idx >= 2 ? C.gold : C.white}>
              {b}
            </Txt>
          </g>
        );
      })}
      <Txt x={28} y={448} size={22} fill={C.muted}>
        AP75 · 상자 겹침 기준 IoU 0.75
      </Txt>
    </g>
  );
}

export function Diagram({ scene, idx = 0, phase = 0.6, scenePhase = 0.5 }) {
  const p = smooth(phase);
  switch (scene) {
    case 'teacherpath':
      return <DetectorPath train={idx < 3 ? 1 : 1 - ramp(phase, 0, 0.4)} progress={scenePhase} />;
    case 'patchalignment':
      return <FeatureGrid idx={idx} p={p} />;
    case 'gradientband':
      return <GradientBand idx={idx} p={p} />;
    case 'distillationresult':
      return <DistillationResults idx={idx} p={p} />;
    case 'motion':
      return <Scope movement={ramp(scenePhase, 0.12, 0.76)} />;
    case 'warp':
      return <DepthDiagram step={idx} p={p} />;
    case 'weight':
      return <Weighting step={idx} p={p} />;
    case 'adapter':
      return <Adapter step={idx} p={p} />;
    case 'ablation':
      return <Results step={idx} p={p} />;
    case 'patch':
      return (
        <>
          <Warehouse grid={idx > 0 ? 0.65 + 0.25 * p : 0} p={scenePhase} />
          <Txt x={28} y={456} size={25} mono fill={C.mint}>
            {idx < 1 ? '380 × 380 px' : '380 / 20 = 19     19² = 361'}
          </Txt>
        </>
      );
    case 'candidates':
      return (
        <>
          <Warehouse boxes={idx < 2 ? Math.max(1, Math.ceil(p * 4)) : 4} p={scenePhase} />
          <Txt x={28} y={455} size={23} fill={C.mint}>
            {idx === 3
              ? 'Femto · 상위 200 후보 → 디코더 2층'
              : 'Atto · 어댑터 → 순위 → 상위 300 후보'}
          </Txt>
        </>
      );
    case 'timer':
      return <Timer step={idx} p={p} />;
    case 'frontier':
      return <Frontier step={idx} p={p} />;
    case 'texture':
      return (
        <>
          <Textile x={32} y={182} size={162} p={0.25 + p * 0.65} />
          <Textile x={300} y={127} size={270} zoom={2.5} />
          <Wire x1={192} y1={211} x2={300} y2={141} color={C.gold} dash />
          <Wire x1={192} y1={299} x2={300} y2={381} color={C.gold} dash />
          <Txt x={34} y={452} size={23} fill={C.mint}>
            {idx === 3 ? 'PixelShuffle · 채널 → 공간' : '입력 무늬와 동일 위치의 확대'}
          </Txt>
        </>
      );
    case 'fusion':
      return <Kernels step={idx} p={p} />;
    case 'round':
      return <Round step={idx} p={p} />;
    case 'qat':
      return <Train step={idx} p={p} />;
    case 'results':
      return <Results sr step={idx} p={p} />;
    default:
      return <NextScene scene={scene} idx={idx} phase={phase} total={scenePhase} />;
  }
}
export function Demo({ id, second }) {
  let image;
  if (id === 'endoda3') image = <Scope mode={second ? 'confidence' : 'residual'} movement={1} />;
  else if (id === 'rf-detr-atto')
    image = (
      <>
        <Timer step={second ? 4 : 1} p={0.7} full={second} />
        {second && <path d="M31 388V415H619V388" fill="none" stroke={C.gold} strokeWidth="5" />}
      </>
    );
  else if (id === 'rt-detr-v4') image = <DetectorPath train={second ? 0 : 1} />;
  else if (id === 'loma') image = <Epipolar threshold={second ? 7 : 2} />;
  else if (id === 'endostreamdepth') image = <Trace history={second} />;
  else image = <Round step={0} p={1} example={second} />;
  return (
    <svg width="660" height="430" viewBox="0 65 660 430" style={{ background: C.panel }}>
      {image}
    </svg>
  );
}

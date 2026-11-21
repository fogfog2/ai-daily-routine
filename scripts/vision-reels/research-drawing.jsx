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
export { mint, amber, blue, ink, dim, line, panel, range, clamp, mix, Text, Tile, Arrow, Point };

const pad = 28;
function Caption({ children, foot = false }) {
  return (
    <Text x={pad} y={foot ? 450 : 106} color={foot ? mint : dim} size={22}>
      {children}
    </Text>
  );
}

function SignalBox({ x, y, w = 185, label, color = blue }) {
  return (
    <g>
      <Tile x={x} y={y} w={w} h={59} border={color} />
      <Text x={x + w / 2} y={y + 37} anchor="middle" color={color} size={22}>
        {label}
      </Text>
    </g>
  );
}
export { Caption, SignalBox };

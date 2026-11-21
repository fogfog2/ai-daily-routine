import React from 'react';
import { AbsoluteFill, Composition, registerRoot, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, Diagram, Demo, clamp, fixed } from './visuals';
import depth from './endoda3.json';
import atto from './rf-detr-atto.json';
import sr from './mobile-int8-sr.json';

import loma from './loma.json';
import stream from './endostreamdepth.json';
import rtv4 from './rt-detr-v4.json';
import correlation from './flow-correlation.json';
import gyro from './gyrodvd.json';
import raw from './mobile-raw-denoising.json';
import car from './car-sam.json';
import gain from './fastgamer.json';
import spectral from './spectral-mobile-color.json';
import tracking from './verifier-point-tracking.json';
import nuwa from './nuwa-vit.json';
import seele from './seele-3dgs.json';
import iqa from './pr-iqa.json';
import simota from './yolox-simota.json';
import softNms from './soft-nms.json';
import patchTokens from './vit-patch-tokens.json';
import clipZeroShot from './clip-zero-shot.json';
import controlNet from './controlnet-zero-conv.json';
import bilaLora from './bilalora-dehazing.json';
import budgetNas from './budget-vision-nas.json';
import gradientBits from './gradient-bit-allocation.json';
import moeClip from './moeclip-patches.json';
import stereoData from './stereo-training-data.json';
import { ResearchScene, ResearchCompare } from './cvpr-graphics';
const episodes = [
  depth,
  atto,
  sr,
  loma,
  stream,
  rtv4,
  correlation,
  gyro,
  raw,
  car,
  gain,
  spectral,
  tracking,
  nuwa,
  seele,
  iqa,
  simota,
  softNms,
  patchTokens,
  clipZeroShot,
  controlNet,
  bilaLora,
  budgetNas,
  gradientBits,
  moeClip,
  stereoData,
];
const labels = {
  'rt-detr-v4': 'RT-DETRv4',
  loma: 'LoMa',
  endostreamdepth: 'EndoStreamDepth',
  endoda3: 'EndoDA3',
  'rf-detr-atto': 'RF-DETR Atto',
  'mobile-int8-sr': 'Mobile INT8 SR',
};
const notes = {
  teacherpath: ['학습 전용 증류 경로', '같은 입력에서 학습과 추론의 경로를 따라갑니다.'],
  patchalignment: ['Lᴅꜱɪ = −mean(cos θ)', '같은 위치에서 학생과 교사의 특징 방향을 맞춥니다.'],
  gradientband: ['GAM · 에폭마다 λ 갱신', '전체 손실에서 얻은 모듈별 기울기 L1 노름을 사용합니다.'],
  distillationresult: [
    '52.1 → 52.3 → 52.6 AP',
    '동일한 학생 검출기에 학습 조건을 하나씩 추가한 결과입니다.',
  ],
  windows: ['반복 구조와 대응의 모호성', '비슷한 패치가 두 개일 때 주변 구조를 함께 봅니다.'],
  descriptors: ['DaD → 기술자 → 매처', '기술자를 학습한 뒤 고정하고 매처를 학습합니다.'],
  epipolar: ['PCK(τ) · 허용 오차 안의 비율', '추정한 F를 사람이 표시한 정답 대응에서 평가합니다.'],
  posemetric: ['카메라 상대 자세', '픽셀 오차와 회전·이동 방향의 각도 오차를 비교합니다.'],
  depthtrack: ['프레임별 깊이 추정', '합성 궤적에서 실제 접근 추세와 흔들림을 함께 봅니다.'],
  streamstate: ['현재 특징 + 이전 상태', '각 블록의 은닉 상태가 다음 시점으로 전달됩니다.'],
  scaletrack: ['σ = std(s₁, …, sₜ)', '프레임별 최적 깊이 스케일의 표준편차입니다.'],
  streambench: ['C3VD · 9개 영상 중 8개', '그림 4에서 FlashDepth보다 스케일 변동이 작았습니다.'],
  motion: ['카메라 운동 + 국소 운동', '배경점과 도구 끝의 실제 위치를 비교합니다.'],
  warp: ['기하학적 깊이 잔차', '재투영한 깊이와 새 시점의 깊이를 비교합니다.'],
  weight: ['C · Huber(e) − λ log C', '작은 신뢰도에도 비용이 생깁니다.'],
  adapter: ['DVM-LoRA', 'FFN에 추가되는 파라미터는 r + d_out개입니다.'],
  ablation: ['시간 정렬 오차  TAE ↓', '같은 손실에서 어댑터를 바꾼 차이를 읽습니다.'],
  patch: ['20 × 20 px / patch', 'Atto의 12개 백본 층은 모두 전역 어텐션을 씁니다.'],
  candidates: ['Atto · decoder depth 0', '어댑터 특징에서 후보를 점수순으로 고릅니다.'],
  timer: ['엔진 실행 구간', '최종 검출 선택은 타이머 밖에서 수행합니다.'],
  frontier: ['+0.4 ms   /   +7.3 AP', '두 모델의 입력과 백본 설정도 함께 달라집니다.'],
  texture: ['×3  ·  단일 영상 초해상도', '합성 무늬로 공간 재배치와 질감 차이를 봅니다.'],
  fusion: ['학습 그래프 → 배포 그래프', '고정된 정규화를 접고 선형 분기를 합칩니다.'],
  round: ['Q(a + b)  ≠  Q(a) + Q(b)', '반올림 순서만 바꿔 같은 두 계수를 비교합니다.'],
  qat: ['Deploy-before-QAT', '실제로 내보낼 그래프의 정수화 오차를 학습합니다.'],
  results: ['29.9114 → 30.0003 dB', '직접 QAT와 교사 지도를 포함한 전체 절차의 비교입니다.'],
};
function captionParts(text) {
  if (text.length <= 44) return [text];
  const words = text.split(' ');
  const cut = words
    .map((_, i) => {
      const part = words.slice(0, i + 1).join(' ');
      return [i + 1, Math.abs(part.length - text.length / 2) - (/[.,?]$/.test(part) ? 5 : 0)];
    })
    .slice(0, -1)
    .sort((a, b) => a[1] - b[1])[0][0];
  return [words.slice(0, cut).join(' '), words.slice(cut).join(' ')];
}
function Movie({ episode, cues }) {
  const frame = useCurrentFrame(),
    { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps,
    time = t * 1000;
  const index = cues.findIndex((c) => time < c.endMs),
    cue = cues[index < 0 ? cues.length - 1 : index];
  const scene = episode.scenes.find((s) => s.id === cue.scene),
    local = cues.filter((c) => c.scene === scene.id);
  const idx = local.indexOf(cue),
    phase = clamp((time - cue.startMs) / (cue.endMs - cue.startMs));
  const phaseAll = clamp(
    (time - local[0].startMs) / (local[local.length - 1].endMs - local[0].startMs),
  );
  const chunks = captionParts(cue.text);
  const spoken =
    chunks.length === 1 || phase < chunks[0].length / cue.text.length ? chunks[0] : chunks[1];
  const [headline, detail] = scene.note || notes[scene.id];
  const reported =
    scene.reported ??
    ['ablation', 'results', 'timer', 'frontier', 'streambench', 'distillationresult'].includes(
      scene.id,
    );
  const clock = (s) => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
  return (
    <AbsoluteFill
      style={{
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        background: C.bg,
        color: C.white,
        padding: '44px 32px 28px',
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '2px solid ' + C.line,
          paddingBottom: 17,
          color: C.mint,
          fontSize: 22,
          letterSpacing: 1.4,
        }}
      >
        <b>AI CONCEPTS</b>
        <span style={{ color: C.muted, fontFamily: fixed, fontSize: 20 }}>
          {episode.label || labels[episode.id]}
        </span>
      </div>
      <div
        style={{
          fontSize: 41,
          fontWeight: 750,
          letterSpacing: -1.3,
          marginTop: 31,
          lineHeight: 1.34,
          wordBreak: 'keep-all',
        }}
      >
        {episode.title}
      </div>
      <div style={{ fontSize: 26, color: C.muted, marginTop: 12, marginBottom: 29 }}>
        {scene.title}
      </div>
      <svg
        viewBox="0 0 660 505"
        width="656"
        height="502"
        style={{
          background: C.panel,
          border: '1px solid ' + C.line,
          borderRadius: 20,
          boxSizing: 'border-box',
        }}
      >
        <text x="25" y="47" fontSize="17" fontFamily={fixed} fill={C.muted}>
          {reported ? 'REPORTED MEASUREMENT' : 'SCHEMATIC'}
        </text>
        <text x="632" textAnchor="end" y="47" fontSize="18" fill={C.muted}>
          {reported ? '원문 보고값' : '설명용 예시'}
        </text>
        {episode.comparison ? (
          <ResearchScene scene={scene.id} idx={idx} phase={phase} total={phaseAll} />
        ) : (
          <Diagram scene={scene.id} idx={idx} phase={phase} scenePhase={phaseAll} />
        )}
      </svg>
      <div style={{ marginTop: 26, paddingLeft: 18, borderLeft: '4px solid ' + C.gold }}>
        <div style={{ fontSize: 32, fontWeight: 700, letterSpacing: -0.7, color: C.gold }}>
          {headline}
        </div>
        <div style={{ fontSize: 22, marginTop: 10, lineHeight: 1.5, color: C.muted }}>{detail}</div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 35,
          right: 35,
          top: 918,
          height: 235,
          display: 'flex',
          alignItems: 'center',
          borderTop: '2px solid ' + C.line,
          fontSize: 36,
          lineHeight: 1.5,
          wordBreak: 'keep-all',
          fontWeight: 600,
          letterSpacing: -0.6,
        }}
      >
        {spoken}
      </div>
      <div
        style={{
          position: 'absolute',
          left: 35,
          right: 35,
          bottom: 53,
          display: 'flex',
          justifyContent: 'space-between',
          gap: 12,
          alignItems: 'end',
          color: C.muted,
          fontSize: 17,
        }}
      >
        <span>{episode.source}</span>
        <span style={{ fontFamily: fixed, whiteSpace: 'nowrap' }}>
          {clock(t)} / {clock(durationInFrames / fps)}
        </span>
      </div>
      <div
        style={{
          position: 'absolute',
          height: 4,
          bottom: 32,
          left: 35,
          right: 35,
          background: C.line,
        }}
      >
        <div
          style={{
            height: '100%',
            width: (100 * frame) / (durationInFrames - 1) + '%',
            background: C.mint,
          }}
        />
      </div>
    </AbsoluteFill>
  );
}
function ResearchDemo({ id, second }) {
  return (
    <svg width="660" height="430" viewBox="0 65 660 430" style={{ background: C.panel }}>
      <ResearchCompare id={id} second={second} />
    </svg>
  );
}
function Root() {
  return (
    <>
      {episodes.flatMap((episode) => {
        const seconds = episode.scenes.reduce((sum, s) => sum + s.seconds, 0);
        const placeholder = episode.scenes.flatMap((s, i) => {
          const start = episode.scenes.slice(0, i).reduce((a, b) => a + b.seconds, 0);
          return s.cues.map((text, j) => ({
            text,
            scene: s.id,
            startMs: 1000 * (start + (s.seconds * j) / s.cues.length),
            endMs: 1000 * (start + (s.seconds * (j + 1)) / s.cues.length),
          }));
        });
        return [
          <Composition
            key={episode.id}
            id={episode.id}
            component={Movie}
            defaultProps={{ episode, cues: placeholder }}
            width={720}
            height={1280}
            fps={15}
            durationInFrames={seconds * 15}
          />,
          <Composition
            key={'demo-' + episode.id}
            id={'demo-' + episode.id}
            component={episode.comparison ? ResearchDemo : Demo}
            defaultProps={{ id: episode.id, second: false }}
            width={660}
            height={430}
            fps={15}
            durationInFrames={1}
          />,
        ];
      })}
    </>
  );
}
registerRoot(Root);

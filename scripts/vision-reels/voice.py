"""Build the Korean narration, cue sheet and WebVTT on the editorial scene clock."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from supertonic import TTS

HERE = Path(__file__).resolve().parent
TERMS = {
    "알티 디트르 버전 포": "RT-DETRv4",
    "알티 디트르 버전 투 라지": "RT-DETRv2-L",
    "감 모듈": "GAM 모듈",
    "에프 파이브": "F₅",
    "표 이에서": "표 2에서",
    "오십이 점 일": "52.1", "오십이 점 삼": "52.3", "오십이 점 육": "52.6",
    "오십육 점 칠": "56.7", "오십육 점 사": "56.4", "오십육 점 팔": "56.8",
    "영 점 칠오": "0.75",

    "엔도스트림뎁스": "EndoStreamDepth",
    "플래시뎁스": "FlashDepth",
    "씨쓰리브이디": "C3VD",
    "엔비디아 알티엑스 에이 육천": "NVIDIA RTX A6000",
    "다드 검출기": "DaD 검출기",
    "로마는": "LoMa는",
    "하드매치": "HardMatch",
    "맘바": "Mamba",
    "스케일 이는": "스케일 2는",
    "사십 점 이 밀리초": "40.2ms",
    "사십 점 칠 밀리초": "40.7ms",
    "오백십팔 제곱": "518×518",
    "영 점 공팔팔": "0.088",
    "영 점 오삼팔": "0.538",
    "영 점 삼칠육": "0.376",
    "영 점 삼삼오": "0.335",
    "영 점 사구": "0.49",
    "영 점 구팔": "0.98",
    "영 점 공구": "0.09",
    "영 점 팔오삼": "0.853",
    "영 점 팔오육": "0.856",
    "이십구 점 구일일사": "29.9114",
    "삼십 점 영영영삼": "30.0003",
    "삼십칠 점 팔": "37.8",
    "삼십 점 오": "30.5",
    "일 점 사": "1.4",
    "일 점 영": "1.0",
    "칠 점 삼": "7.3",
    "영 점 사": "0.4",
    "엔도 디에이 쓰리": "EndoDA3",
    "알에프 디트르": "RF-DETR",
    "디브이엠 로라": "DVM-LoRA",
    "기본 로라": "기본 LoRA",
    "같은 로라": "같은 LoRA",
    "텐서알티 십 점 사": "TensorRT 10.4",
    "에프피 십육": "FP16",
    "엔비디아 티포": "NVIDIA T4",
    "인트 팔": "INT8",
    "코코": "COCO",
    "스케어드": "SCARED",
    "표 삼": "표 3",
    "표 사": "표 4",
    "신뢰도 씨": "신뢰도 C",
    "모바일원": "MobileOne",
    "픽셀 셔플": "PixelShuffle",
    "아토": "Atto",
    "펨토": "Femto",
    "삼백팔십": "380",
    "삼백육십한 개": "361개",
    "이십 픽셀": "20픽셀",
    "삼백 후보": "300개 후보",
    "이백 개": "200개",
    "데시벨": "dB",
}


def caption(text):
    for spoken, written in TERMS.items():
        text = text.replace(spoken, written)
    return text


def stamp(ms):
    sec, ms = divmod(ms, 1000)
    return f"{sec // 3600:02}:{sec // 60 % 60:02}:{sec % 60:02}.{ms:03}"


def build(spec, engine, voice, out):
    rate = engine.sample_rate
    directory = out / spec["id"]
    directory.mkdir(parents=True, exist_ok=True)
    timeline, soundtrack = [], []
    scene_start = 0
    for scene in spec["scenes"]:
        parts, offsets = [], [0]
        for i, spoken in enumerate(scene["cues"]):
            digest = hashlib.sha256(spoken.encode("utf-8")).hexdigest()[:12]
            clip = directory / f"{scene['id']}-{i}-{digest}.wav"
            if not clip.exists():
                wave, _ = engine.synthesize(
                    text=spoken, voice_style=voice, lang="ko", speed=1.02, total_steps=8
                )
                wave = wave.ravel()
                active = np.flatnonzero(np.abs(wave) > 0.004)
                if active.size:
                    wave = wave[
                        max(0, active[0] - int(0.06 * rate)) : active[-1]
                        + int(0.10 * rate)
                    ]
                sf.write(clip, wave, rate)
            wave, _ = sf.read(clip)
            parts.extend([wave, np.zeros(int(0.30 * rate))])
            offsets.append(offsets[-1] + len(wave) + len(parts[-1]))
        total = scene["seconds"] * rate
        speed = offsets[-1] / total
        raw = directory / "scene.wav"
        timed = directory / "timed.wav"
        sf.write(raw, np.concatenate(parts), rate)
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(raw),
                "-af",
                f"atempo={speed:.8f}",
                str(timed),
            ],
            check=True,
        )
        wave, _ = sf.read(timed)
        soundtrack.append(np.pad(wave[:total], (0, max(0, total - len(wave)))))
        for i, spoken in enumerate(scene["cues"]):
            start = round(
                1000 * (scene_start + scene["seconds"] * offsets[i] / offsets[-1])
            )
            end = round(
                1000 * (scene_start + scene["seconds"] * offsets[i + 1] / offsets[-1])
            )
            timeline.append(
                dict(text=caption(spoken), startMs=start, endMs=end, scene=scene["id"])
            )
        print(spec["id"], scene["id"], "tempo", round(speed, 2), flush=True)
        scene_start += scene["seconds"]
    sf.write(directory / "audio.wav", np.concatenate(soundtrack), rate)
    (directory / "cues.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2) + "\n"
    )
    (directory / "ko.vtt").write_text(
        "WEBVTT\n\n"
        + "\n\n".join(
            f"{stamp(c['startMs'])} --> {stamp(c['endMs'])}\n{c['text']}"
            for c in timeline
        )
        + "\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("episodes", nargs="+")
    args = parser.parse_args()
    np.random.seed(270)
    engine = TTS(
        model_dir=args.model,
        auto_download=False,
        intra_op_num_threads=2,
        inter_op_num_threads=1,
    )
    voice = engine.get_voice_style("F2")
    for episode in args.episodes:
        build(
            json.loads((HERE / (episode + ".json")).read_text()),
            engine,
            voice,
            args.out,
        )

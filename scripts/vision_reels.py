"""Insert the optional video supplement in the three published vision articles."""

import json
import re
from html import escape
from pathlib import Path

STUDIO = Path(__file__).parent / "vision-reels"
EPISODES = {
    "depth-estimation": (
        "endoda3",
        "EndoDA3",
        "같은 프레임에서 두 지도를 비교하세요.",
        [
            (
                "깊이 잔차",
                "예상 위치와 도구 끝이 어긋난 영역에 큰 깊이 잔차가 나타납니다.",
            ),
            (
                "예측 신뢰도",
                "같은 위치에서 어둡게 표시한 낮은 신뢰도는 이 잔차의 학습 기여를 줄입니다.",
            ),
        ],
    ),
    "rf-detr": (
        "rf-detr-atto",
        "RF-DETR Atto",
        "타이머의 양 끝을 바꿔 보세요.",
        [
            (
                "엔진 실행",
                "T4의 엔진 실행 중앙값은 1.0ms입니다. TensorRT 10.4, FP16, 배치 1 조건입니다.",
            ),
            (
                "전체 처리",
                "입력 준비와 최종 검출 선택까지 포함합니다. 개발사는 전체 구간의 지연을 보고하지 않았습니다.",
            ),
        ],
    ),
    "super-resolution": (
        "mobile-int8-sr",
        "모바일 INT8 초해상도",
        "같은 두 계수의 반올림 순서를 바꿔 보세요.",
        [
            (
                "각각 반올림",
                "0.49를 각각 반올림하면 0 + 0 = 0입니다. 예시 무늬의 대비가 사라집니다.",
            ),
            (
                "합산 후 반올림",
                "0.49 + 0.49 = 0.98을 한 번 반올림하면 1입니다. 같은 무늬의 대비가 살아납니다.",
            ),
        ],
    ),
}
START = "<!-- vision-reel:start -->"
END = "<!-- vision-reel:end -->"


def insert(html, slug):
    html = re.sub(
        re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S
    )
    if slug not in EPISODES:
        return html
    episode, topic, prompt, options = EPISODES[slug]
    spec = json.loads((STUDIO / f"{episode}.json").read_text(encoding="utf-8"))
    seconds = sum(scene["seconds"] for scene in spec["scenes"])
    media = f"../media/vision/{episode}"
    choices, images = [], []
    for i, (label, explanation) in enumerate(options):
        key = "ab"[i]
        choices.append(
            f'<input class="vr-choice vr-{key}" type="radio" name="vr-layer" id="vr-{key}"'
            f'{" checked" if not i else ""}><label for="vr-{key}">{escape(label)}</label>'
        )
        images.append(
            f'<div class="vr-view vr-view-{key}"><img width="660" height="430" loading="lazy" '
            f'src="{media}/view-{key}.jpg" alt="{escape(label)} 설명용 도식">'
            f"<p>{escape(explanation)}</p></div>"
        )
    panel = f'''{START}
<link rel="stylesheet" href="../vision-reels.css">
<script src="../vision-reels.js" defer></script>
<details class="vision-reel" id="video-explainer">
  <summary><span>영상 기반 설명 보기</span><small>{topic} · {seconds // 60}분 {seconds % 60:02}초</small></summary>
  <div class="vr-content">
    <p class="vr-title">{escape(spec["title"])}</p>
    <div class="vr-layout">
      <video controls playsinline preload="none" data-poster="{media}/poster.jpg" width="720" height="1280"
             aria-label="{topic} 한국어 해설 영상" src="{media}/video.mp4">
        <track kind="captions" src="{media}/ko.vtt" srclang="ko" label="한국어">
        <a href="{media}/video.mp4">영상 파일 열기</a>
      </video>
      <fieldset class="vr-demo"><legend>{escape(prompt)}</legend>
        {"".join(choices)}
        {"".join(images)}
      </fieldset>
    </div>
    <div class="vr-links"><a href="{media}/script.txt">시간표와 전체 대본</a>
      <a href="{escape(spec["sourceUrl"], quote=True)}">{escape(spec["source"])}</a>
      <a href="{media}/video.mp4" download>MP4 다운로드</a></div>
  </div>
</details>
{END}
'''
    before, marker, after = html.partition("</header>")
    if not marker:
        raise ValueError(f"Missing article header in {slug}")
    return before + marker + "\n" + panel + after.lstrip("\n")

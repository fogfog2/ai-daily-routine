#!/usr/bin/env python3
"""팔레트 + 본문 -> 완성 HTML.

공용 CSS(_shell.css)는 01-kvcache.html 에서 추출한 것으로 전 편 동일하다.
편마다 다른 것은 팔레트 토큰과 본문뿐이다.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
SHELL = (HERE / "_shell.css").read_text(encoding="utf-8")

# 문서를 공개 사이트에 직접 수록하므로 목록은 내부 경로다.
ARCHIVE = "../index.html"

TOKENS = [
    "paper", "panel", "ink", "ink-soft", "ink-faint", "rule", "rule-strong",
    "accent", "accent-fill", "accent-line", "muted", "muted-fill", "warn",
]


def palette_css(light: dict, dark: dict) -> str:
    def block(d):
        return "\n".join(f"    --{k}: {d[k]};" for k in TOKENS)

    return (
        ":root {\n" + block(light) + "\n  }\n"
        "  @media (prefers-color-scheme: dark) {\n"
        "    :root:not([data-theme=\"light\"]) {\n" + block(dark) + "\n    }\n  }\n"
        "  :root[data-theme=\"dark\"] {\n" + block(dark) + "\n  }\n"
    )


def build(title, eyebrow, h1, subtitle, dek, spec, body, reading, light, dark, date="2026-08-09"):
    specs = "\n".join(
        f"    <div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in spec
    )
    reads = "\n".join(f"      <li>{r}</li>" for r in reading)
    return f"""<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  {palette_css(light, dark)}
{SHELL}</style>

<div class="sheet">

  <a class="backlink" href="{ARCHIVE}">&larr; AI Concepts Archive</a>

  <header class="masthead">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="subtitle">{subtitle}</p>
    <p class="dek">{dek}</p>
  </header>

  <dl class="spec">
{specs}
  </dl>

{body}

  <footer>
    <h2>더 읽을거리</h2>
    <ul>
{reads}
    </ul>
    <p class="colophon">AI Concepts Archive · 자동 생성 학습 노트 · {date}</p>
  </footer>

</div>
"""


OUT_DIR = HERE.parent.parent / "site-pages" / "docs"


def write(name, **kw):
    """완성본을 공개 사이트의 docs/ 로 바로 쓴다.

    이제 문서를 직접 수록하므로 아티팩트를 거치지 않는다.
    build-docs.py 가 뒤이어 상단 네비게이션을 주입한다.
    """
    out = OUT_DIR / name
    out.write_text(build(**kw), encoding="utf-8")
    print(f"  {name}: {out.stat().st_size:,} bytes")
    return out

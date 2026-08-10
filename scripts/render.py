#!/usr/bin/env python3
"""archive/*.md -> site/index.html

의존성 없는 최소 마크다운 렌더러. 루틴이 실제로 쓰는 문법만 지원한다:
제목(#/##/###), 굵게, 링크, 인용, 목록, 수평선.
"""
import html
import pathlib
import re
import sys


def inline(text: str) -> str:
    """인라인 마크업. 이스케이프를 먼저 하고 태그를 넣는다."""
    out = html.escape(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        out,
    )
    return out


def render(md: str) -> str:
    parts, buf = [], []

    def flush():
        if buf:
            parts.append("<ul>" + "".join(buf) + "</ul>")
            buf.clear()

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith("<!--"):
            continue
        if line.startswith("### "):
            flush()
            parts.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            flush()
            parts.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            flush()
            parts.append(f"<h2 class='day'>{inline(line[2:])}</h2>")
        elif line.startswith("> "):
            flush()
            parts.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.startswith("---"):
            flush()
            parts.append("<hr>")
        elif line.startswith(("- ", "* ")):
            buf.append(f"<li>{inline(line[2:])}</li>")
        else:
            flush()
            cls = " class='takeaway'" if line.startswith("**그래서:**") else ""
            parts.append(f"<p{cls}>{inline(line)}</p>")

    flush()
    return "\n".join(parts)


CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --bg:#fbfbfa; --fg:#1a1a19; --muted:#6b6b66; --line:#e2e2dd;
  --card:#fff; --accent:#7a5cff; --shadow:0 1px 2px rgba(0,0,0,.05);
}
@media (prefers-color-scheme:dark){
  :root{--bg:#151517;--fg:#ececea;--muted:#9a9a94;--line:#2c2c30;
        --card:#1d1d20;--accent:#a894ff;--shadow:none}
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif;
  line-height:1.65;font-size:16px}
.wrap{max-width:760px;margin:0 auto;padding:48px 20px 96px}
header{margin-bottom:40px;padding-bottom:24px;border-bottom:1px solid var(--line)}
h1{font-size:1.7rem;margin:0 0 6px;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:.9rem;margin:0}
.day{font-size:1.25rem;margin:0 0 4px;letter-spacing:-.01em}
section.entry{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:24px 26px;margin-bottom:22px;box-shadow:var(--shadow)}
h2{font-size:1.15rem;margin:26px 0 8px;letter-spacing:-.01em}
h3{font-size:1.02rem;margin:24px 0 6px;letter-spacing:-.01em}
h3:first-of-type{margin-top:8px}
p{margin:.5em 0}
ul{margin:.5em 0;padding-left:1.25em}
li{margin:.28em 0}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code{background:rgba(127,127,127,.14);padding:.12em .38em;
  border-radius:4px;font-size:.88em}
blockquote{margin:.6em 0;padding:.15em 0 .15em 14px;
  border-left:3px solid var(--line);color:var(--muted);font-size:.9rem}
hr{border:0;border-top:1px solid var(--line);margin:20px 0}
.takeaway{border-left:3px solid var(--accent);padding:8px 14px;margin:12px 0 0;
  background:rgba(122,92,255,.06);border-radius:0 6px 6px 0}
@media (prefers-color-scheme:dark){.takeaway{background:rgba(168,148,255,.09)}}
.empty{color:var(--muted);text-align:center;padding:56px 0}
footer{margin-top:40px;color:var(--muted);font-size:.82rem;text-align:center}
"""


def main() -> None:
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])

    files = sorted(src.glob("*.md"), reverse=True)  # 최신 날짜 우선
    if files:
        body = "\n".join(
            f"<section class='entry'>{render(f.read_text(encoding='utf-8'))}</section>"
            for f in files
        )
    else:
        body = "<p class='empty'>아직 리포트가 없습니다. <code>/ai-daily</code>를 실행하세요.</p>"

    latest = files[0].stem if files else "-"
    dst.write_text(
        "<!doctype html>\n"
        '<html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>AI Daily</title>"
        f"<style>{CSS}</style></head><body><div class='wrap'>"
        "<header><h1>AI Daily</h1>"
        f"<p class='sub'>매일 수집하는 AI 뉴스 · 총 {len(files)}일치 · 최신 {latest}</p>"
        "</header>"
        f"{body}"
        "<footer>ai-daily 루틴 자동 생성</footer>"
        "</div></body></html>",
        encoding="utf-8",
    )
    print(f"{len(files)}개 리포트 렌더링")


if __name__ == "__main__":
    main()

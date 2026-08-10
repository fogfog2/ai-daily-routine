#!/usr/bin/env python3
"""문서 페이지 후처리 — 내부 링크와 네비게이션을 붙인다.

site-pages/docs/<slug>.html 각각에:
  · 목록으로 돌아가는 링크 (없으면 추가)
  · 아티팩트 절대주소로 남아 있는 Archive 링크를 내부 경로로 치환
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from catalog import DOCS

DOCS_DIR = pathlib.Path(__file__).parent.parent / "site-pages" / "docs"

NAV_CSS = """
<style>
  /* 목록 페이지와 같은 톤. 문서 자체의 팔레트를 건드리지 않도록
     currentColor 대신 자체 변수를 쓰고, 라이트/다크 양쪽을 정의한다. */
  .site-nav {
    --nav-bg: #f4f4f2; --nav-fg: #4d5654; --nav-line: #d5d7d3; --nav-hi: #0f6f63;
    position: sticky; top: 0; z-index: 50;
    display: flex; align-items: center; gap: .55rem;
    padding: .5rem 1.1rem;
    font: 500 .74rem/1 ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
    letter-spacing: .06em;
    background: var(--nav-bg);
    color: var(--nav-fg);
    border-bottom: 1px solid var(--nav-line);
  }
  @media (prefers-color-scheme: dark) {
    .site-nav { --nav-bg: #101211; --nav-fg: #9fa9a6; --nav-line: #242927; --nav-hi: #3fc9b4; }
  }
  :root[data-theme="dark"] .site-nav { --nav-bg: #101211; --nav-fg: #9fa9a6; --nav-line: #242927; --nav-hi: #3fc9b4; }
  :root[data-theme="light"] .site-nav { --nav-bg: #f4f4f2; --nav-fg: #4d5654; --nav-line: #d5d7d3; --nav-hi: #0f6f63; }
  .site-nav a { color: var(--nav-fg); text-decoration: none; }
  .site-nav a:hover, .site-nav a:focus-visible { color: var(--nav-hi); outline: none; }
  .site-nav .sep { opacity: .45; }
  .site-nav .cur { opacity: .7; }
  @media print { .site-nav { display: none; } }
</style>
"""


def nav_html(title: str) -> str:
    safe = re.sub(r"<[^>]+>", "", title)
    return (
        f'{NAV_CSS}'
        f'<nav class="site-nav">'
        f'<a href="../index.html">← AI CONCEPTS</a>'
        f'<span class="sep">/</span>'
        f'<span class="cur">{safe}</span>'
        f'</nav>\n'
    )


def process(path: pathlib.Path, title: str) -> str:
    html = path.read_text(encoding="utf-8")
    original = html
    changed = []

    # 1) claude.ai Archive 절대주소 → 내부 목록
    new = re.sub(
        r'href="https://claude\.ai/code/artifact/1d524519[^"]*"',
        'href="../index.html"',
        html,
    )
    if new != html:
        changed.append("archive링크")
        html = new

    # 2) 상단 네비게이션 — 이미 있으면 통째로 교체한다(팔레트 갱신 반영)
    if 'class="site-nav"' in html:
        new = re.sub(
            r"<style>\s*/\* 목록 페이지와.*?</style>\s*<nav class=\"site-nav\">.*?</nav>\s*",
            "", html, flags=re.S)
        if new == html:  # 구버전 네비 형태
            new = re.sub(r"<style>[^<]*?\.site-nav\s*\{.*?</style>\s*<nav class=\"site-nav\">.*?</nav>\s*",
                         "", html, flags=re.S)
        html = new
        changed.append("네비 교체")
    else:
        changed.append("네비")

    m = re.search(r"(<title>.*?</title>\s*\n?)", html, re.S)
    if m:
        html = html[: m.end()] + nav_html(title) + html[m.end():]
    else:
        html = nav_html(title) + html

    # 매 실행마다 빈 줄이 한 줄씩 쌓여 49편 전체가 '수정됨'으로 잡히던 문제.
    # 자동 루틴이 매일 도는 이상 무의미한 커밋이 계속 생기므로 여기서 정규화한다.
    html = re.sub(r"\n{3,}", "\n\n", html)

    # 내용이 실제로 달라졌을 때만 쓴다 — 멱등성을 보장해야
    # git 이 '변경 없음'을 정확히 판단할 수 있다.
    if html == original:
        return "변경 없음"
    path.write_text(html, encoding="utf-8")
    return ", ".join(changed) or "변경 없음"


def main() -> None:
    if not DOCS_DIR.exists():
        print(f"docs 폴더가 없습니다: {DOCS_DIR}")
        return
    done, missing = 0, []
    for title, sub, uid, slug, stage, summ, date in DOCS:
        p = DOCS_DIR / f"{slug}.html"
        if not p.exists():
            missing.append(slug)
            continue
        note = process(p, title)
        done += 1
        print(f"  {slug:26} {note}")
    print(f"\n  처리 {done}편" + (f" · 누락 {len(missing)}편: {', '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()

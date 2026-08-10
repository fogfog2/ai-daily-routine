#!/usr/bin/env python3
"""AI Concepts Archive — 파이프라인 단계별 도입 페이지.

catalog.py 를 단일 출처로 삼는다. 게임 서버 /ai/ 페이지와 같은 분류를 쓴다.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from catalog import STAGES, DOCS, url, validate, by_stage

validate()
HERE = pathlib.Path(__file__).parent

ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" '
         'stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg>')

CSS = """
  :root {
    --paper: #eef1ef;
    --paper-raised: #e2e7e4;
    --ink: #12181c;
    --ink-soft: #4a5459;
    --ink-faint: #7c8a86;
    --line: #c9d2cd;
    --accent: #0f8b8d;
    --accent-soft: #d9efee;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #10161a;
      --paper-raised: #171f24;
      --ink: #e7ece9;
      --ink-soft: #9fadab;
      --ink-faint: #647672;
      --line: #2a3338;
      --accent: #35d6c4;
      --accent-soft: #16302e;
    }
  }
  :root[data-theme="dark"] {
    --paper: #10161a;
    --paper-raised: #171f24;
    --ink: #e7ece9;
    --ink-soft: #9fadab;
    --ink-faint: #647672;
    --line: #2a3338;
    --accent: #35d6c4;
    --accent-soft: #16302e;
  }
  :root[data-theme="light"] {
    --paper: #eef1ef;
    --paper-raised: #e2e7e4;
    --ink: #12181c;
    --ink-soft: #4a5459;
    --ink-faint: #7c8a86;
    --line: #c9d2cd;
    --accent: #0f8b8d;
    --accent-soft: #d9efee;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: "Pretendard Variable", Pretendard, "Apple SD Gothic Neo",
      "Noto Sans KR", "Malgun Gothic", ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
    line-height: 1.7;
    word-break: keep-all;
    -webkit-font-smoothing: antialiased;
  }

  a { color: var(--accent); }
  a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

  .wrap { max-width: 780px; margin: 0 auto; padding: 4rem 1.5rem 5rem; }

  /* ---------- 머리말 ---------- */
  header {
    display: flex; justify-content: space-between; align-items: flex-end;
    gap: 1.5rem; flex-wrap: wrap;
    border-bottom: 1px solid var(--line);
    padding-bottom: 1.6rem;
  }
  .eyebrow {
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--accent); margin: 0 0 0.7rem;
  }
  h1 {
    font-family: Charter, "Iowan Old Style", Georgia, "Times New Roman", serif;
    font-weight: 600; font-size: clamp(1.9rem, 5vw, 2.5rem);
    line-height: 1.1; letter-spacing: -0.01em; margin: 0; text-wrap: balance;
  }
  .meta {
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 0.78rem; color: var(--ink-faint); text-align: right; white-space: nowrap;
  }
  .meta strong { color: var(--ink-soft); font-weight: 600; }
  .dek { max-width: 54ch; color: var(--ink-soft); font-size: 1rem; margin: 1.3rem 0 0; }

  /* ---------- 목차 ---------- */
  nav.toc {
    display: flex; flex-wrap: wrap; gap: 0.5rem;
    margin: 1.8rem 0 3rem; padding-bottom: 1.8rem;
    border-bottom: 1px solid var(--line);
  }
  nav.toc a {
    display: inline-flex; align-items: baseline; gap: 0.4rem;
    font-size: 0.82rem; text-decoration: none;
    padding: 0.4rem 0.75rem; border-radius: 999px;
    border: 1px solid var(--line); color: var(--ink-soft);
    transition: border-color .15s, background .15s, color .15s;
  }
  nav.toc a:hover { border-color: var(--accent); background: var(--accent-soft); color: var(--accent); }
  nav.toc a b {
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 0.7rem; font-weight: 600; color: var(--accent);
  }
  nav.toc a span { color: var(--ink-faint); font-variant-numeric: tabular-nums; }

  /* ---------- 단계 ---------- */
  section.stage { margin-bottom: 3rem; scroll-margin-top: 1.5rem; }
  .stage-head { display: grid; grid-template-columns: auto 1fr; gap: 0 1rem; margin-bottom: 1.1rem; }
  .stage-no {
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 0.75rem; font-weight: 600; color: var(--accent);
    border: 1px solid var(--accent); border-radius: 4px;
    padding: 0.15rem 0.45rem; align-self: start; margin-top: 0.35rem;
  }
  .stage-head h2 {
    font-family: Charter, "Iowan Old Style", Georgia, serif;
    font-weight: 600; font-size: 1.3rem; margin: 0; letter-spacing: -0.01em;
  }
  .stage-head h2 em {
    font-style: normal; font-size: 0.85rem; font-weight: 500;
    color: var(--ink-faint); margin-left: 0.5rem;
  }
  .stage-head p {
    grid-column: 2; margin: 0.3rem 0 0;
    font-size: 0.9rem; color: var(--ink-soft); max-width: 58ch;
  }

  .list { display: flex; flex-direction: column; }

  .entry {
    display: grid; grid-template-columns: 1fr auto;
    gap: 0.3rem 1.2rem; align-items: center;
    padding: 1.1rem 0; border-top: 1px solid var(--line);
    text-decoration: none; color: inherit;
  }
  .entry:first-child { border-top: none; }
  .entry .body h3 {
    font-family: Charter, "Iowan Old Style", Georgia, serif;
    font-weight: 600; font-size: 1.1rem; margin: 0 0 0.2rem;
    color: var(--ink); letter-spacing: -0.005em;
  }
  .entry .body .kr {
    font-size: 0.88rem; font-weight: 600; color: var(--ink-faint);
    display: block; margin: -0.1rem 0 0.4rem;
  }
  .entry .body p { margin: 0; font-size: 0.9rem; color: var(--ink-soft); max-width: 52ch; }

  .entry .go {
    grid-column: 2; grid-row: 1;
    align-self: center; width: 2rem; height: 2rem; border-radius: 999px;
    border: 1px solid var(--line);
    display: flex; align-items: center; justify-content: center; flex: none;
    transition: border-color .15s ease, background .15s ease, transform .15s ease;
  }
  .entry .go svg { width: 0.95rem; height: 0.95rem; stroke: var(--ink-faint); transition: stroke .15s ease; }
  .entry:hover .go { border-color: var(--accent); background: var(--accent-soft); transform: translate(2px, -2px); }
  .entry:hover .go svg { stroke: var(--accent); }
  .entry:hover .body h3 { color: var(--accent); }

  footer {
    margin-top: 3.2rem; padding-top: 1.6rem;
    border-top: 1px solid var(--line);
    font-size: 0.85rem; color: var(--ink-faint);
  }

  @media (max-width: 540px) {
    .stage-head { grid-template-columns: 1fr; }
    .stage-head p { grid-column: 1; }
    .stage-no { margin-bottom: 0.5rem; }
  }
  @media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms !important; } }
"""

toc = "\n".join(
    f'    <a href="#{st["id"]}"><b>{st["no"]}</b> {st["name"]} <span>{len(items)}</span></a>'
    for st, items in by_stage()
)

sections = []
for st, items in by_stage():
    rows = "\n".join(
        f'      <a class="entry" href="{url(uid, slug)}" target="_blank" rel="noopener">\n'
        f'        <span class="body">\n'
        f'          <h3>{title}</h3>\n'
        f'          <span class="kr">{sub}</span>\n'
        f'          <p>{summary}</p>\n'
        f'        </span>\n'
        f'        <span class="go" aria-hidden="true">{ARROW}</span>\n'
        f'      </a>'
        for title, sub, uid, slug, _s, summary, _d in items
    )
    sections.append(
        f'  <section class="stage" id="{st["id"]}">\n'
        f'    <div class="stage-head">\n'
        f'      <span class="stage-no">{st["no"]}</span>\n'
        f'      <h2>{st["name"]} <em>{st["tagline"]}</em></h2>\n'
        f'      <p>{st["desc"]}</p>\n'
        f'    </div>\n'
        f'    <div class="list">\n{rows}\n    </div>\n'
        f'  </section>'
    )

html = f"""<title>AI Concepts Archive</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>{CSS}</style>

<div class="wrap">
  <header>
    <div>
      <p class="eyebrow">Automated Learning Log</p>
      <h1>AI Concepts Archive</h1>
    </div>
    <div class="meta"><strong>{len(DOCS)}</strong> entries · <strong>{len(STAGES)}</strong> stages</div>
  </header>

  <p class="dek">
    AI 개념을 하나씩 골라 정리한 글 모음입니다. 컴퓨터·AI 전공 수준을 기준으로 작성했습니다.
    <strong>모델이 만들어져 서비스되기까지의 순서</strong>로 묶었습니다 —
    위에서부터 읽으면 한 번의 흐름이 되고, 필요한 단계만 골라 봐도 됩니다.
  </p>

  <nav class="toc">
{toc}
  </nav>

{chr(10).join(sections)}

  <footer>
    자동으로 갱신됩니다. 실행될 때마다 새로운 AI 개념을 골라 글을 발행하고, 해당 단계에 한 줄을 추가합니다.
  </footer>
</div>
"""

out = HERE / "archive.html"
out.write_text(html, encoding="utf-8")
print(f"archive.html: {len(DOCS)}편 / {len(STAGES)}단계, {out.stat().st_size:,} bytes")

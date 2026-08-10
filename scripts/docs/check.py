#!/usr/bin/env python3
"""발행 전 점검. 태그 균형, 테마 3중 정의, SVG 접근성, 미정의 CSS 변수."""
import pathlib
import re
import sys

TOKENS = {
    "paper", "panel", "ink", "ink-soft", "ink-faint", "rule", "rule-strong",
    "accent", "accent-fill", "accent-line", "muted", "muted-fill", "warn",
    # build-docs.py 가 주입하는 상단 네비게이션 전용 토큰.
    # 문서 팔레트와 섞이지 않도록 별도 이름을 쓴다.
    "nav-bg", "nav-fg", "nav-line", "nav-hi",
}

VOID = {"meta", "br", "hr", "img", "input", "path", "rect", "line", "circle",
        "polygon", "use", "stop", "tspan", "marker"}

fail = 0
for name in sys.argv[1:]:
    p = pathlib.Path(name)
    h = p.read_text(encoding="utf-8")
    errs = []

    for t in ["section", "figure", "figcaption", "div", "table", "svg", "p",
              "h1", "h2", "ul", "li", "dl", "footer", "header", "g", "text"]:
        o = len(re.findall(r"<" + t + r"[\s>]", h))
        c = len(re.findall(r"</" + t + r">", h))
        if o != c:
            errs.append(f"{t} 태그 불균형 open={o} close={c}")

    # 테마 3중 정의
    if h.count("--accent:") < 3:
        errs.append(f"테마 정의 부족 (--accent {h.count('--accent:')}회, 3 필요)")
    if 'data-theme="dark"' not in h:
        errs.append("data-theme=dark 오버라이드 없음")

    # 사용된 var() 가 전부 정의됐는지
    used = set(re.findall(r"var\(--([a-z-]+)\)", h))
    missing = used - TOKENS
    if missing:
        errs.append(f"미정의 CSS 변수: {sorted(missing)}")

    # SVG 접근성
    for m in re.finditer(r"<svg\b[^>]*>", h):
        if 'role="img"' not in m.group(0) or "aria-label" not in m.group(0):
            errs.append("svg에 role/aria-label 누락")

    # 본문 내 미치환 플레이스홀더
    if re.search(r"\bTODO\b|\bLorem\b|\bXXX\b", h):
        errs.append("플레이스홀더 잔존")

    status = "OK " if not errs else "FAIL"
    if errs:
        fail = 1
    print(f"[{status}] {p.name}  ({len(h):,} bytes)")
    for e in errs:
        print(f"        - {e}")

sys.exit(fail)

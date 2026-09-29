"""今日の日付を漢字で「毛筆で書く」SVG アニメーションを作る。

字形は毛筆体 Yuji Boku (SIL OFL 1.1, scripts/OFL-YujiBoku.txt) の輪郭 (scripts/glyphs.json)。
それを KanjiVG (https://kanjivg.tagaini.net, CC BY-SA 3.0) の書き順データ (scripts/kanjivg/*.svg) を
太い線のマスクにして 1 画ずつ現すことで、筆の形のまま書き順どおりに書いていく。

使い方: python scripts/kanji_date.py [出力先] [YYYY-MM-DD]
日付を省くと日本時間の今日になる。
"""

import datetime
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
GLYPHS = json.loads((HERE / "glyphs.json").read_text(encoding="utf-8"))
DIGITS = "〇一二三四五六七八九"
WEEKDAYS = "月火水木金土日"

CELL = 109  # 1 文字の枠 (KanjiVG と glyphs.json の座標系)
WIDTH = 760  # 画像の幅。長い日付は字間を詰めて収める
PAD = 28
INK = "#16130f"
PAPER = "#f4eee0"
SHU = "#c23a2b"  # 落款の朱

BRUSH = 17  # マスクの線の太さ。筆の字形を覆える太さにする
SPEED = 190  # 筆の速さ (枠の座標で 1 秒あたり)
STROKE_MIN = 0.16  # どんなに短い画でもかける時間
STROKE_GAP = 0.09  # 画と画の間 (筆を運ぶ間)
CHAR_GAP = 0.3  # 字と字の間
HOLD = 5.0  # 落款を押してから消えるまで
FADE = 1.2


def to_kanji(n: int) -> str:
    """1〜99 を「三十一」のような漢数字にする。"""
    tens, ones = divmod(n, 10)
    s = ""
    if tens:
        s += ("" if tens == 1 else DIGITS[tens]) + "十"
    if ones:
        s += DIGITS[ones]
    return s


def strokes(char: str) -> list[str]:
    svg = (HERE / "kanjivg" / f"{ord(char):05x}.svg").read_text(encoding="utf-8")
    return re.findall(r'<path id="kvg:[0-9a-f]+-s\d+"[^>]*\sd="([^"]+)"', svg)


def approx_length(d: str) -> float:
    """KanjiVG のパス (M/C/S/L, 相対・絶対) の長さを、各区間の端点を結んだ折れ線で近似する。"""
    arity = {"m": 2, "l": 2, "c": 6, "s": 4, "q": 4, "t": 2, "h": 1, "v": 1}
    x = y = 0.0
    total = 0.0
    for cmd, args in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        nums = [float(v) for v in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        n = arity.get(cmd.lower(), 2)
        for i in range(0, len(nums) - n + 1, n):
            seg = nums[i : i + n]
            if cmd.lower() == "h":
                nx, ny = (x + seg[0], y) if cmd == "h" else (seg[0], y)
            elif cmd.lower() == "v":
                nx, ny = (x, y + seg[0]) if cmd == "v" else (x, seg[0])
            elif cmd.islower():
                nx, ny = x + seg[-2], y + seg[-1]
            else:
                nx, ny = seg[-2], seg[-1]
            if cmd.lower() != "m":
                total += math.hypot(nx - x, ny - y)
            x, y = nx, ny
    return total


def texts_for(date: datetime.date) -> tuple[str, str, str]:
    """(大きく書く日付, 小さく添える年と曜日, 落款の字)"""
    reiwa = date.year - 2018
    era = "令和" + ("元" if reiwa == 1 else to_kanji(reiwa)) + "年"
    wd = WEEKDAYS[date.weekday()]
    return to_kanji(date.month) + "月" + to_kanji(date.day) + "日", era + "　" + wd + "曜日", wd


def build(date: datetime.date) -> str:
    main_text, sub_text, seal_char = texts_for(date)
    sub_scale = 0.4
    seal_size = CELL * 0.5

    # 大きい行は中央、小さい行は右寄せにして、その右に落款を置く
    main_adv = min(CELL, (WIDTH - PAD * 2) / len(main_text))
    sub_adv = CELL * sub_scale * 0.92
    sub_y = PAD + CELL + 14
    height = sub_y + seal_size + PAD
    seal_x = WIDTH - PAD - seal_size - 6
    sub_x = seal_x - 14 - len(sub_text) * sub_adv
    layout = [
        (main_text, (WIDTH - len(main_text) * main_adv) / 2, PAD, main_adv, 1.0),
        (sub_text, sub_x, sub_y + (seal_size - CELL * sub_scale) / 2, sub_adv, sub_scale),
    ]

    defs, body, css = [], [], []
    anim = []  # (selector, 種類, 開始, 終了)。keyframes は 1 周の長さが決まってから書く
    t = 0.6
    n = 0
    for text, x0, y0, adv, scale in layout:
        for i, ch in enumerate(text):
            if ch == "　":
                continue
            mask = []
            for d in strokes(ch):
                dt = max(STROKE_MIN * scale ** 0.5, approx_length(d) * scale / SPEED)
                mask.append(f'<path id="s{n}" pathLength="1" d="{d}"/>')
                anim.append((f"#s{n}", "stroke", t, t + dt))
                n += 1
                t += dt + STROKE_GAP * scale ** 0.5
            # 書き終えたらマスクを全面に開き、筆の字形がマスクからはみ出した部分も出す
            mask.append(f'<rect id="r{n}" class="full" x="-10" y="-10" width="{CELL + 20}" height="{CELL + 20}"/>')
            anim.append((f"#r{n}", "fill", t - STROKE_GAP, t + 0.25))
            n += 1
            m = len(defs)
            defs.append(
                f'<mask id="m{m}" maskUnits="userSpaceOnUse" x="-10" y="-10" '
                f'width="{CELL + 20}" height="{CELL + 20}">{"".join(mask)}</mask>'
            )
            body.append(
                f'<g transform="translate({x0 + i * adv:.1f} {y0:.1f}) scale({scale})">'
                f'<path fill="{INK}" mask="url(#m{m})" d="{GLYPHS[ch]}"/></g>'
            )
            t += CHAR_GAP * scale ** 0.5
        t += 0.2

    # 落款: 朱の角印に曜日の字を白抜きで
    seal_at = t + 0.3
    s = seal_size / CELL
    body.append(
        f'<g transform="translate({seal_x:.1f} {sub_y:.1f}) rotate(-4 {seal_size / 2:.1f} {seal_size / 2:.1f})">'
        f'<g id="seal"><rect width="{seal_size:.1f}" height="{seal_size:.1f}" rx="5" fill="{SHU}"/>'
        f'<g transform="translate({seal_size * 0.12:.1f} {seal_size * 0.1:.1f}) scale({s * 0.76:.3f})">'
        f'<path fill="{PAPER}" d="{GLYPHS[seal_char]}"/></g></g></g>'
    )
    end = seal_at + 0.35
    cycle = end + HOLD + FADE
    pct = lambda v: f"{v / cycle * 100:.3f}%"

    css.append(
        f"mask path{{fill:none;stroke:#fff;stroke-width:{BRUSH};stroke-linecap:round;stroke-linejoin:round;"
        "stroke-dasharray:1 2;stroke-dashoffset:1;opacity:0}"
        ".full{fill:#fff;opacity:0}"
        f"mask *,#seal,#ink{{animation-duration:{cycle:.2f}s;animation-iteration-count:infinite}}"
        "#ink{animation-name:fade}"
        f"@keyframes fade{{0%,{pct(end + HOLD)}{{opacity:1}}{pct(end + HOLD + FADE)},100%{{opacity:0}}}}"
        "#seal{transform-box:fill-box;transform-origin:center;opacity:0;animation-name:seal}"
        f"@keyframes seal{{0%,{pct(seal_at)}{{opacity:0;transform:scale(1.6)}}"
        f"{pct(seal_at + 0.001)}{{opacity:.6;transform:scale(1.6);animation-timing-function:cubic-bezier(.5,0,.8,.3)}}"
        f"{pct(end)}{{opacity:1;transform:scale(.96)}}{pct(end + 0.12)},100%{{opacity:1;transform:scale(1)}}}}"
    )
    for i, (sel, kind, start, stop) in enumerate(anim):
        if kind == "stroke":
            # 入りでためて、送りで速く、収筆でゆるめる
            frames = (
                f"0%,{pct(start)}{{stroke-dashoffset:1;opacity:0;animation-timing-function:cubic-bezier(.55,0,.35,1)}}"
                f"{pct(start + 0.001)}{{opacity:1}}{pct(stop)},100%{{stroke-dashoffset:0;opacity:1}}"
            )
        else:
            frames = f"0%,{pct(start)}{{opacity:0}}{pct(stop)},100%{{opacity:1}}"
        css.append(f"@keyframes a{i}{{{frames}}}{sel}{{animation-name:a{i}}}")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" viewBox="0 0 {WIDTH} {height:.0f}">
<!-- Glyphs: Yuji Boku (C) The Yuji Project Authors, SIL OFL 1.1. Stroke order: KanjiVG (C) Ulrich Apel, CC BY-SA 3.0 - https://kanjivg.tagaini.net -->
<title>{main_text} {sub_text.replace("　", " ")}</title>
<style>{"".join(css)}</style>
<defs>{"".join(defs)}</defs>
<rect width="100%" height="100%" rx="12" fill="{PAPER}"/>
<g id="ink">
{chr(10).join(body)}
</g>
</svg>
"""


def main() -> None:
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "date-kanji.svg")
    if len(sys.argv) > 2:
        date = datetime.date.fromisoformat(sys.argv[2])
    else:
        date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date()
    out.write_text(build(date), encoding="utf-8")
    print(f"{out}: {date}")


if __name__ == "__main__":
    main()

"""プロフィール用のサイバーなバナー (assets/cyber.svg) を作る。

デジタルレインが降る電脳空間で、「忍」の輪郭をホログラムのようにトレースして照準がロックオンし、
グリッチしながら名乗りが現れ、ターミナルに接続ログが打ち込まれる。
「忍」の輪郭は毛筆体 Yuji Boku (SIL OFL 1.1) から取り出したもの (glyphs.json)。

使い方: python scripts/cyber_banner.py [出力先]
"""

import pathlib
import random
import sys

from kanji_date import CELL, GLYPHS

W, H = 760, 240
CYAN = "#38f3ff"
GREEN = "#3dff9a"
RED = "#ff2e63"
TEXT = "#d9fbff"
RAIN_CHARS = "0123456789ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
CYCLE = 11.0
HOLD_UNTIL = 9.6  # ここから消えはじめる

KANJI_CENTER = (122, 120)
KANJI_SCALE = 1.5
TITLE_X = 262

LOG = [
    ("> DIVE INTO THE NET", 2.3),
    ("> GHOST LINE ........ ESTABLISHED", 3.1),
    ("> QUANT.MODULE ...... ONLINE", 4.0),
]


def pct(v: float) -> str:
    return f"{v / CYCLE * 100:.3f}%"


def rain(rnd: random.Random) -> str:
    """縦に並んだ文字の列を、それぞれ違う速さで上から下へ流し続ける。"""
    cols = []
    step, line = 17, 15
    for i, x in enumerate(range(6, W, step)):
        n = rnd.randint(7, 15)
        dur = rnd.uniform(3.2, 7.5)
        chars = []
        for j in range(n):
            head = j == n - 1
            op = 1 if head else 0.15 + 0.6 * j / n
            fill = "#e8fff2" if head else GREEN
            chars.append(f'<tspan x="{x}" dy="{line}" fill="{fill}" fill-opacity="{op:.2f}">{rnd.choice(RAIN_CHARS)}</tspan>')
        cols.append(
            f'<text class="col" style="animation-duration:{dur:.1f}s;animation-delay:-{rnd.uniform(0, dur):.1f}s;'
            f'--h:{-(n * line)}px">{"".join(chars)}</text>'
        )
    return "\n".join(cols)


def reticle() -> str:
    cx, cy = KANJI_CENTER
    ticks = "".join(
        f'<line x1="0" y1="-96" x2="0" y2="{-88 if k % 3 else -84}" transform="rotate({k * 15})"/>' for k in range(24)
    )
    corners = "".join(
        f'<path d="M{sx * 70},{sy * 50} L{sx * 70},{sy * 70} L{sx * 50},{sy * 70}" transform="translate(0 0)"/>'
        for sx in (-1, 1)
        for sy in (-1, 1)
    )
    return f"""<g transform="translate({cx} {cy})" fill="none" stroke="{CYAN}">
<g id="lock"><g class="spin" stroke-width="1" opacity=".75">{ticks}</g>
<circle class="spin-r" r="80" stroke-width="1.5" stroke-dasharray="40 14 6 14" opacity=".8"/>
<circle class="spin" r="104" stroke-width=".8" stroke-dasharray="2 6" opacity=".5"/>
<g stroke-width="2" id="corners">{corners}</g></g>
</g>"""


def build() -> str:
    rnd = random.Random(1995)
    cx, cy = KANJI_CENTER
    kx, ky = cx - CELL * KANJI_SCALE / 2, cy - CELL * KANJI_SCALE / 2
    title_at = 1.9

    css = [
        f"svg{{font-family:'Consolas','SFMono-Regular','Menlo','Courier New',monospace}}",
        # デジタルレイン
        f".col{{font-size:13px;animation-name:rain;animation-timing-function:linear;animation-iteration-count:infinite}}"
        f"@keyframes rain{{from{{transform:translateY(var(--h))}}to{{transform:translateY({H}px)}}}}",
        # 走査線の帯
        f"#scan{{animation:scan 4.5s linear infinite}}@keyframes scan{{from{{transform:translateY(-40px)}}to{{transform:translateY({H + 40}px)}}}}",
        f"#all{{animation:all {CYCLE}s infinite}}"
        f"@keyframes all{{0%{{opacity:0}}1%{{opacity:1}}{pct(HOLD_UNTIL)}{{opacity:1}}{pct(HOLD_UNTIL + 0.05)}{{opacity:.2}}"
        f"{pct(HOLD_UNTIL + 0.1)}{{opacity:1}}{pct(HOLD_UNTIL + 0.7)},100%{{opacity:0}}}}",
        # 忍: 輪郭をトレースしてから、中を発光させる
        f"#trace{{stroke-dasharray:1 1;stroke-dashoffset:1;animation:trace {CYCLE}s infinite}}"
        f"@keyframes trace{{0%,{pct(0.3)}{{stroke-dashoffset:1;animation-timing-function:cubic-bezier(.4,0,.2,1)}}{pct(1.8)},100%{{stroke-dashoffset:0}}}}",
        f"#kfill{{opacity:0;animation:kfill {CYCLE}s infinite}}"
        f"@keyframes kfill{{0%,{pct(1.6)}{{opacity:0}}{pct(1.7)}{{opacity:.9}}{pct(1.75)}{{opacity:.2}}{pct(1.85)}{{opacity:.8}}{pct(2.3)},100%{{opacity:.55}}}}",
        # 照準: 回り続け、ロックオンで締まる
        ".spin,.spin-r{transform-box:view-box;transform-origin:0 0}"
        ".spin{animation:spin 14s linear infinite}.spin-r{animation:spin 9s linear infinite reverse}"
        "@keyframes spin{to{transform:rotate(360deg)}}",
        f"#lock{{animation:lock {CYCLE}s infinite}}"
        f"@keyframes lock{{0%,{pct(0.2)}{{transform:scale(1.35);opacity:0}}{pct(0.6)}{{opacity:1}}"
        f"{pct(1.8)}{{transform:scale(1.35);animation-timing-function:cubic-bezier(.7,0,.2,1)}}{pct(2.1)},100%{{transform:scale(1);opacity:1}}}}",
        f"#corners{{animation:corners {CYCLE}s infinite}}"
        f"@keyframes corners{{0%,{pct(2.1)}{{stroke:{CYAN}}}{pct(2.12)}{{stroke:{RED}}}{pct(2.5)}{{stroke:{RED}}}{pct(2.8)},100%{{stroke:{CYAN}}}}}",
        # 名乗り: ちらつきながら現れ、ときどきグリッチする
        f"#title{{opacity:0;animation:title {CYCLE}s infinite}}"
        f"@keyframes title{{0%,{pct(title_at)}{{opacity:0}}{pct(title_at + 0.05)}{{opacity:1}}{pct(title_at + 0.1)}{{opacity:0}}"
        f"{pct(title_at + 0.18)}{{opacity:1}}{pct(title_at + 0.22)}{{opacity:.3}}{pct(title_at + 0.3)},100%{{opacity:1}}}}",
    ]
    for cls, dx, dy, spots in (("gr", -3, 1, (title_at + 0.3, 5.2, 7.9)), ("gc", 3, -1, (title_at + 0.35, 5.25, 7.95))):
        frames = [f"0%{{transform:translate(0,0);opacity:0}}"]
        for s in spots:
            frames.append(
                f"{pct(s)}{{transform:translate(0,0);opacity:0}}{pct(s + 0.02)}{{transform:translate({dx}px,{dy}px);opacity:.9}}"
                f"{pct(s + 0.08)}{{transform:translate({-dx * 2}px,0);opacity:.9}}{pct(s + 0.14)}{{transform:translate({dx}px,{-dy}px);opacity:.8}}"
                f"{pct(s + 0.2)}{{transform:translate(0,0);opacity:0}}"
            )
        frames.append("100%{transform:translate(0,0);opacity:0}")
        css.append(f".{cls}{{animation:{cls} {CYCLE}s infinite}}@keyframes {cls}{{{''.join(frames)}}}")
    css.append(
        f"#sub{{opacity:0;animation:sub {CYCLE}s infinite}}"
        f"@keyframes sub{{0%,{pct(title_at + 0.4)}{{opacity:0}}{pct(title_at + 0.9)},100%{{opacity:1}}}}"
    )

    # ターミナル: 1 文字ずつ打ち込む (幅を段階的に開く)
    log_svg = []
    for i, (line, at) in enumerate(LOG):
        n = len(line)
        dur = n * 0.022
        y = 166 + i * 19
        css.append(
            f"#t{i}{{transform:scaleX(0);transform-box:fill-box;transform-origin:left;animation:t{i} {CYCLE}s infinite}}"
            f"@keyframes t{i}{{0%,{pct(at)}{{transform:scaleX(0);animation-timing-function:steps({n})}}{pct(at + dur)},100%{{transform:scaleX(1)}}}}"
        )
        log_svg.append(
            f'<clipPath id="c{i}"><rect id="t{i}" x="{TITLE_X}" y="{y - 12}" width="{n * 7.3:.0f}" height="16"/></clipPath>'
            f'<text x="{TITLE_X}" y="{y}" font-size="12" fill="{GREEN if i else CYAN}" clip-path="url(#c{i})" letter-spacing=".3">{line}</text>'
        )
    last_end = LOG[-1][1] + len(LOG[-1][0]) * 0.022
    css.append(
        f"#cursor{{opacity:0;animation:cursor {CYCLE}s infinite}}"
        f"@keyframes cursor{{0%,{pct(last_end)}{{opacity:0}}"
        + "".join(f"{pct(last_end + k * 0.5)}{{opacity:{k % 2}}}" for k in range(1, 10))
        + "100%{opacity:1}}"
    )
    cursor_x = TITLE_X + len(LOG[-1][0]) * 7.3 + 6

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<!-- 忍: Yuji Boku (C) The Yuji Project Authors, SIL OFL 1.1 -->
<title>TechNinja</title>
<style>{"".join(css)}</style>
<defs>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24,0 L0,0 0,24" fill="none" stroke="{CYAN}" stroke-width=".4" opacity=".18"/></pattern>
<pattern id="lines" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>
<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".12"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset=".4" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity=".8"/></linearGradient>
<mask id="rainmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#02070a"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<g mask="url(#rainmask)" opacity=".85">
{rain(rnd)}
</g>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<g id="all">
<rect x="{TITLE_X - 14}" y="40" width="{W - TITLE_X - 16}" height="{H - 62}" fill="#02070a" opacity=".72"/>
<path d="M{TITLE_X - 14},52 L{TITLE_X - 14},40 L{TITLE_X + 6},40 M{W - 30},{H - 34} L{W - 30},{H - 22} L{W - 50},{H - 22}" fill="none" stroke="{CYAN}" stroke-width="1.5"/>
{reticle()}
<g transform="translate({kx:.1f} {ky:.1f}) scale({KANJI_SCALE})" filter="url(#glow)">
<path id="kfill" d="{GLYPHS["忍"]}" fill="{CYAN}" fill-opacity=".35"/>
<path id="trace" pathLength="1" d="{GLYPHS["忍"]}" fill="none" stroke="{CYAN}" stroke-width="1.1" vector-effect="non-scaling-stroke"/>
</g>
<text x="{cx}" y="{H - 10}" font-size="9" fill="{CYAN}" text-anchor="middle" letter-spacing="2" opacity=".7">TARGET: 忍 // LOCKED</text>
<g font-size="46" font-weight="700" letter-spacing="3">
<text class="gr" x="{TITLE_X}" y="96" fill="{RED}">TechNinja</text>
<text class="gc" x="{TITLE_X}" y="96" fill="{CYAN}">TechNinja</text>
<text id="title" x="{TITLE_X}" y="96" fill="{TEXT}" filter="url(#glow)">TechNinja</text>
</g>
<text id="sub" x="{TITLE_X + 2}" y="126" font-size="13" letter-spacing="3.2" fill="#7fd8e6">QUANT DEVELOPER // NINJA // JAPAN</text>
{"".join(log_svg)}
<rect id="cursor" x="{cursor_x:.0f}" y="{166 + (len(LOG) - 1) * 19 - 11}" width="8" height="13" fill="{GREEN}"/>
<text x="{W - 24}" y="30" font-size="10" fill="{CYAN}" text-anchor="end" letter-spacing="1.5" opacity=".7">NODE.06 // NET.DIVE v2.6</text>
</g>
<rect id="scan" width="{W}" height="40" fill="url(#band)"/>
<rect width="{W}" height="{H}" fill="url(#lines)"/>
</g>
</svg>
"""


def main() -> None:
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "assets/cyber.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8", newline="\n")
    print(out)


if __name__ == "__main__":
    main()

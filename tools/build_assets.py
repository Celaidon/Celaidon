#!/usr/bin/env python3
"""Generates every pixel-art SVG used by the profile README.

Each image is drawn on a small logical grid (one grid cell = one "pixel") and written out as merged
horizontal runs, so the SVGs stay small and render crisp at any size. The 5x7 letters are drawn from
the bitmap font below instead of SVG <text>, because GitHub does not load web fonts inside images.
"""
import math
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
PREVIEW = Path(sys.argv[2]) if len(sys.argv) > 2 else None
OUT.mkdir(parents=True, exist_ok=True)
if PREVIEW:
    PREVIEW.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------- palette
PLUM = "#2b2346"
PLUM_D = "#1c1630"
PLUM_L = "#3a2f5e"
INK = "#2a2145"
CREAM = "#fff4e6"
PINK = "#ffb3d1"
PINK_D = "#f28cb5"
LAV = "#b8a7ff"
LAV_L = "#cbbfff"
MINT = "#a8f0d1"
PEACH = "#ffd7a8"
SKY = "#8fd3ff"
YELLOW = "#ffe29a"

# ----------------------------------------------------------------------------- 5x7 bitmap font
_F = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".###./#...#/#..../#..../#..../#...#/.###.",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".###./#...#/#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": ".###./..#../..#../..#../..#../..#../.###.",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    "N": "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
    "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../.###.",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": "####./....#/....#/.###./....#/....#/####.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": ".###./#..../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/....#/.###.",
    ".": "...../...../...../...../...../...../..#..",
    ",": "...../...../...../...../...../..#../.#...",
    ":": "...../..#../...../...../..#../...../.....",
    "-": "...../...../...../.###./...../...../.....",
    "+": "...../..#../..#../#####/..#../..#../.....",
    "/": "....#/....#/...#./..#../.#.../#..../#....",
    "&": ".##../#..#./#.#../.#.../#.#.#/#..#./.##.#",
    "'": "..#../..#../.#.../...../...../...../.....",
    "!": "..#../..#../..#../..#../..#../...../..#..",
    "?": ".###./#...#/....#/...#./..#../...../..#..",
    "@": ".###./#...#/#.###/#.#.#/#.###/#..../.####",
    "#": ".#.#./.#.#./#####/.#.#./#####/.#.#./.#.#.",
    "(": "...#./..#../.#.../.#.../.#.../..#../...#.",
    ")": ".#.../..#../...#./...#./...#./..#../.#...",
    "*": "...../..#../...../...../...../...../.....",  # centred dot, used as a separator
}
FONT = {k: v.split("/") for k, v in _F.items()}
for _k, _rows in FONT.items():
    assert len(_rows) == 7 and all(len(r) == 5 for r in _rows), _k


def text_width(s, scale=1):
    return sum((4 if ch == " " else 6) * scale for ch in s) - scale


# ----------------------------------------------------------------------------- pixel canvas
class Layer:
    def __init__(self, cls=None):
        self.cls = cls
        self.px = {}

    def dot(self, x, y, c):
        self.px[(int(x), int(y))] = c

    def rect(self, x, y, w, h, c):
        for j in range(h):
            for i in range(w):
                self.px[(x + i, y + j)] = c

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def sprite(self, rows, legend, x, y, scale=1):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in legend:
                    self.rect(x + i * scale, y + j * scale, scale, scale, legend[ch])

    def circle(self, cx, cy, r, c, ring=None):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                d = math.hypot(x - cx, y - cy)
                if d <= r:
                    self.dot(x, y, c)
        if ring:
            for y in range(int(cy - r - 2), int(cy + r + 3)):
                for x in range(int(cx - r - 2), int(cx + r + 3)):
                    d = math.hypot(x - cx, y - cy)
                    if r < d <= r + 1.2:
                        self.dot(x, y, ring)

    def text(self, s, x, y, c, scale=1, outline=None):
        def draw(ox, oy, col):
            cx = x + ox
            for ch in s:
                if ch == " ":
                    cx += 4 * scale
                    continue
                glyph = FONT.get(ch.upper())
                if glyph is None:
                    raise ValueError(f"no glyph for {ch!r} in {s!r}")
                for j, row in enumerate(glyph):
                    for i, bit in enumerate(row):
                        if bit == "#":
                            self.rect(cx + i * scale, y + oy + j * scale, scale, scale, col)
                cx += 6 * scale

        if outline:
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                draw(ox * max(1, scale // 2), oy * max(1, scale // 2), outline)
        draw(0, 0, c)


def runs(px):
    by_row = {}
    for (x, y), c in px.items():
        by_row.setdefault((c, y), []).append(x)
    paths = {}
    for (c, y), xs in sorted(by_row.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        xs.sort()
        start = prev = xs[0]
        for nx in xs[1:] + [None]:
            if nx is not None and nx == prev + 1:
                prev = nx
                continue
            w = prev - start + 1
            paths.setdefault(c, []).append(f"M{start} {y}h{w}v1h-{w}z")
            if nx is not None:
                start = prev = nx
    return {c: "".join(v) for c, v in paths.items()}


def write_svg(name, W, H, scale, title, desc, layers, css="", backdrop=None):
    width, height = round(W * scale), round(H * scale)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{width}" height="{height}" '
        f'shape-rendering="crispEdges" role="img" aria-labelledby="t d">',
        f"<title id=\"t\">{title}</title><desc id=\"d\">{desc}</desc>",
    ]
    if css:
        parts.append(f"<style>{css}</style>")
    if backdrop:
        parts.append(backdrop)
    for layer in layers:
        inner = "".join(f'<path fill="{c}" d="{d}"/>' for c, d in runs(layer.px).items())
        parts.append(f'<g class="{layer.cls}">{inner}</g>' if layer.cls else f"<g>{inner}</g>")
    parts.append("</svg>")
    svg = "".join(parts)
    (OUT / name).write_text(svg, encoding="utf-8")
    if PREVIEW:
        import cairosvg

        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(PREVIEW / (Path(name).stem + ".png")), scale=1)
    return len(svg)


def mix(a, b, t):
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# ----------------------------------------------------------------------------- sprites
BOAT_KEYS = {
    "o": "#3b2a55", "c": CREAM, "w": "#f0b98f", "W": "#d89870", "p": PINK, "P": PINK_D,
    "h": "#6b4a8e", "s": "#ffe0c9", "k": "#3b2a55", "r": "#ff9fb9",
}
SLEEPER = [
    "............................",
    "...hhhhh....................",
    "..hhhhhhh...................",
    ".hhhhhhhhh..................",
    ".hsssssssh..................",
    ".hskksskks..................",
    ".hsrssssrs..................",
    "..sssssss.pppppppppppppppp..",
    ".......pppppppppppppppppppp.",
    ".......pppPpppPpppPpppPpppp.",
    ".......pppppPpppPpppPppppPp.",
    "occccccccccccccccccccccccco.",
    ".owwwwwwwwwwwwwwwwwwwwwwwo..",
    "..oWWWWWWWWWWWWWWWWWWWWWo...",
    "...oooooooooooooooooooooo...",
]
# fix row widths (all rows must be 28 wide)
SLEEPER = [r.ljust(28, ".")[:28] for r in SLEEPER]

SAILBOAT = [
    ".......oPPP.....",
    ".......oc.......",
    ".......occ......",
    ".......occc.....",
    "......pocccc....",
    ".....ppoccccc...",
    "....pppocccccc..",
    "...ppppoccccccc.",
    "..pppppocccccccc",
    ".ppppppocccccccc",
    ".wwwwwwwwwwwwww.",
    "..wwwwwwwwwwww..",
    "...WWWWWWWWWW...",
    "bbb..bbbbb..bbbb",
    "..BBBB.....BBBB.",
]
SAIL_KEYS = {"o": "#3b2a55", "c": CREAM, "p": PINK, "P": PINK_D, "w": "#f0b98f", "W": "#d89870", "b": SKY, "B": "#6fb4e6"}

BUBBLE = [
    "................",
    "..oooooooooooo..",
    ".oppppppppppppo.",
    ".oppppppppppppo.",
    ".oppkkpkkpkkppo.",
    ".oppkkpkkpkkppo.",
    ".oppppppppppppo.",
    ".oppppppppppppo.",
    "..oppooooooooo..",
    "..opo...........",
    "..oo............",
]
BUBBLE = [r.ljust(16, ".")[:16] for r in BUBBLE]
BUBBLE_KEYS = {"o": "#3b2a55", "p": PINK, "k": "#3b2a55"}

TROPHY = [
    "................",
    "...oooooooooo...",
    "..oyyyyyyyyyyo..",
    ".oyoyyyyyyyyoyo.",
    ".oyoyyyyyyyyoyo.",
    ".oyoyyyyyyyyoyo.",
    "..ooyyyyyyyyoo..",
    "....oyyyyyyo....",
    ".....ooyyoo.....",
    "......oyyo......",
    "......oyyo......",
    ".....oYYYYo.....",
    "....oYYYYYYo....",
    "....oooooooo....",
]
TROPHY = [r.ljust(16, ".")[:16] for r in TROPHY]
TROPHY_KEYS = {"o": "#3b2a55", "y": YELLOW, "Y": "#f2c14e"}

GEM = [
    "..oooooooo..",
    ".oLLMMMMDDo.",
    "oLLMMMMMMDDo",
    "oLMMMMMMMMDo",
    "oMMMMMMMMMDo",
    ".oMMMMMMMDo.",
    "..oMMMMMDo..",
    "...oMMMDo...",
    "....oMDo....",
    ".....oo.....",
]

CLOUD = [
    "....oooo........",
    "..ooccccoo.ooo..",
    ".occccccccoccco.",
    "occccccccccccccc",
    ".oooooooooooooo.",
]


def sparkle(layer, x, y, c, big=False):
    layer.dot(x, y, c)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        layer.dot(x + dx, y + dy, c)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            layer.dot(x + dx, y + dy, c)


def frame(layer, x, y, w, h, fill, border, shadow=None):
    if shadow:
        layer.rect(x + 2, y + 2, w, h, shadow)
    layer.rect(x, y, w, h, border)
    layer.rect(x + 1, y + 1, w - 2, h - 2, fill)
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        layer.px.pop((cx, cy), None)  # notched corners
    if shadow:
        for cx, cy in ((x + 2, y + 2), (x + w + 1, y + h + 1), (x + 2, y + h + 1), (x + w + 1, y + 2)):
            layer.px.pop((cx, cy), None)


# ============================================================================= BANNER
def banner():
    W, H = 200, 56
    rnd = random.Random(7)
    bands = ["#231c3d", "#2a2247", "#322852", "#3b2e5e", "#45356b", "#523d79",
             "#624587", "#764f94", "#8d5aa0", "#a666a8", "#c277b0"]
    edges = [0, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 46]
    sky = Layer()
    for i, c in enumerate(bands):
        sky.rect(0, edges[i], W, edges[i + 1] - edges[i], c)
    for i in range(1, len(bands)):  # dithered seams between bands
        y = edges[i]
        for x in range(0, W, 2):
            sky.dot(x, y, bands[i - 1])
            sky.dot(x + 1, y - 1, bands[i])

    stars_a, stars_b, stars_c = Layer("tw1"), Layer("tw2"), Layer()
    for _ in range(46):
        x = rnd.randrange(0, W)
        y = rnd.randrange(1, 30)
        if 6 < x < 150 and 7 < y < 24:  # keep the title area calm
            continue
        c = rnd.choice([CREAM, PINK, LAV_L, CREAM])
        rnd.choice([stars_a, stars_b, stars_c, stars_c]).dot(x, y, c)
    sparks = Layer("tw2")
    for (x, y, c, big) in ((172, 8, CREAM, True), (120, 30, PINK, False), (196, 30, LAV_L, False), (160, 4, PINK, False), (70, 3, LAV_L, False)):
        sparkle(sparks, x, y, c, big)

    moon = Layer()
    moon.circle(190, 10, 6, CREAM)
    for x, y in ((187, 8), (188, 8), (192, 12), (191, 7), (188, 13)):
        moon.dot(x, y, "#ffdcc2")
    for y in range(0, 24):
        for x in range(172, 200):
            d = math.hypot(x - 190, y - 10)
            if 6.5 < d <= 9 and (x + y) % 2 == 0:
                moon.dot(x, y, "#d58fbd")

    clouds = Layer("drift")
    clouds.sprite(CLOUD, {"o": "#c9a6e0", "c": "#f4cfe6"}, 0, 1)
    clouds2 = Layer("drift2")
    clouds2.sprite(CLOUD, {"o": "#b79ad6", "c": "#e6d2f7"}, 0, 5)

    title = Layer()
    title.text("VANI MISHRA", 9, 8, CREAM, scale=2, outline=INK)
    sub1 = Layer()
    sub1.text("CS STUDENT @ VIT CHENNAI", 10, 27, PEACH, outline=INK)
    sub2 = Layer()
    sub2.text("FLUTTER + PYTHON + AI", 10, 37, MINT, outline=INK)

    boat = Layer("bob")
    boat.sprite(SLEEPER, BOAT_KEYS, 162, 31)

    z1, z2, z3 = Layer("z1"), Layer("z2"), Layer("z3")
    z4 = ["####", "..#.", ".#..", "####"]
    z5 = ["#####", "...#.", "..#..", ".#...", "#####"]
    z1.sprite(z4, {"#": CREAM}, 173, 28)
    z2.sprite(z5, {"#": PINK}, 177, 21)
    z3.sprite(z5, {"#": LAV_L}, 180, 14)

    sea = Layer()
    sea.rect(0, 46, W, 2, "#7a72d0")
    sea.rect(0, 48, W, 4, "#5f58b4")
    sea.rect(0, 52, W, 4, "#4a4496")
    crest1, crest2 = Layer("sway1"), Layer("sway2")
    for x in range(-16, W + 16):
        if (x % 12) < 4:
            crest1.dot(x, 47, "#d7d1ff")
        if ((x + 6) % 12) < 3:
            crest1.dot(x, 50, "#9d96ec")
        if ((x + 3) % 14) < 5:
            crest2.dot(x, 53, "#7a72d0")
        if ((x + 9) % 10) < 2:
            crest2.dot(x, 54, "#a39df0")

    css = (
        "@keyframes tw{0%,55%,100%{opacity:1}70%{opacity:.15}}"
        ".tw1{animation:tw 3.2s steps(1) infinite}.tw2{animation:tw 4.1s steps(1) infinite 1.1s}"
        "@keyframes bob{0%,49%{transform:translateY(0)}50%,100%{transform:translateY(1px)}}"
        ".bob{animation:bob 2.4s steps(1) infinite}"
        "@keyframes sway{0%,49%{transform:translateX(0)}50%,100%{transform:translateX(-4px)}}"
        ".sway1{animation:sway 1.8s steps(1) infinite}.sway2{animation:sway 2.4s steps(1) infinite .6s}"
        "@keyframes zz{0%,12%{opacity:0}13%,100%{opacity:1}}"
        "@keyframes zzb{0%,38%{opacity:0}39%,100%{opacity:1}}"
        "@keyframes zzc{0%,63%{opacity:0}64%,100%{opacity:1}}"
        "@keyframes zrst{0%{opacity:0}}"
        ".z1{animation:zz 4.8s steps(1) infinite}.z2{animation:zzb 4.8s steps(1) infinite}"
        ".z3{animation:zzc 4.8s steps(1) infinite}"
        "@keyframes drift{0%{transform:translateX(-24px)}100%{transform:translateX(210px)}}"
        ".drift{animation:drift 70s linear infinite}.drift2{animation:drift 95s linear infinite -40s}"
        + REDUCED
    )
    layers = [sky, stars_c, stars_a, stars_b, sparks, moon, clouds, clouds2, title, sub1, sub2, boat, z1, z2, z3, sea, crest1, crest2]
    return write_svg(
        "banner.svg", W, H, 4.5,
        "Vani Mishra: pixel-art banner",
        "A pixel-art dusk sky with a girl napping in a small boat on a calm sea, beside the name Vani Mishra, CS student at VIT Chennai, Flutter, Python and AI.",
        layers, css,
    )


# ============================================================================= DIVIDER + FOOTER
def wave():
    W, H = 225, 7
    base = Layer("sway")
    cols = [PINK, LAV, MINT]
    for x in range(-12, W + 12):
        y = 2 + round(1.6 * math.sin(2 * math.pi * x / 18))
        c = cols[(x // 6) % 3]
        base.dot(x, y, c)
        base.dot(x, y + 1, c)
    css = ("@keyframes sw{0%,49%{transform:translateX(0)}50%,100%{transform:translateX(-6px)}}"
           ".sway{animation:sw 1.6s steps(1) infinite}" + REDUCED)
    return write_svg("wave.svg", W, H, 4, "Pixel wave divider", "A decorative pixel wave in pink, lavender and mint.", [base], css)


def footer():
    W, H = 225, 18
    bg = Layer()
    frame(bg, 36, 1, 153, 16, PLUM, LAV)
    t = Layer()
    t.text("NAPPING IN A BOAT BETWEEN COMMITS", 40, 5, LAV_L)
    heart = ["..##.##..", ".#######.", ".#######.", "..#####..", "...###...", "....#...."]
    h1, h2 = Layer("pulse"), Layer("pulse")
    h1.sprite(heart, {"#": PINK}, 24, 6)
    h2.sprite(heart, {"#": PINK}, 192, 6)
    css = ("@keyframes pl{0%,69%{opacity:1}70%,100%{opacity:.35}}.pulse{animation:pl 2s steps(1) infinite}" + REDUCED)
    return write_svg("footer.svg", W, H, 4, "Footer", "Napping in a boat between commits, with two pixel hearts.", [bg, t, h1, h2], css)


# ============================================================================= ACHIEVEMENT
def achievement():
    W, H = 225, 60
    bg = Layer()
    frame(bg, 0, 0, 221, 56, PLUM, LAV, shadow=PLUM_D)
    bg.rect(4, 4, 213, 1, PLUM_L)
    icon_bg = Layer()
    icon_bg.rect(7, 9, 36, 38, PLUM_L)
    trophy = Layer("shine")
    trophy.sprite(TROPHY, TROPHY_KEYS, 9, 15, scale=2)
    trophy.rect(19, 21, 2, 4, CREAM)
    txt = Layer()
    txt.text("ACHIEVEMENT UNLOCKED", 50, 8, MINT)
    txt.text("1ST PRIZE", 50, 18, CREAM, scale=2)
    txt.text("BEST OPEN-SOURCE AI PROJECT", 50, 36, PINK)
    txt.text("HACKTOBERFEST 2026 HACK DAY", 50, 45, LAV_L)
    for line in ("ACHIEVEMENT UNLOCKED", "BEST OPEN-SOURCE AI PROJECT", "HACKTOBERFEST 2026 HACK DAY"):
        assert 50 + text_width(line) < 217, line
    sp1, sp2 = Layer("tw1"), Layer("tw2")
    sparkle(sp1, 198, 24, YELLOW, True)
    sparkle(sp2, 182, 30, PINK)
    sparkle(sp2, 211, 14, MINT)
    css = ("@keyframes tw{0%,55%,100%{opacity:1}70%{opacity:.15}}.tw1{animation:tw 2.6s steps(1) infinite}"
           ".tw2{animation:tw 3.4s steps(1) infinite .8s}"
           "@keyframes sh{0%,80%{opacity:1}90%{opacity:.4}}.shine{animation:sh 3s steps(1) infinite}" + REDUCED)
    return write_svg(
        "achievement.svg", W, H, 4,
        "Achievement unlocked: 1st prize, Best Open-Source AI Project",
        "A pixel trophy beside the text 1st prize, Best Open-Source AI Project, Hacktoberfest 2026 Hack Day.",
        [bg, icon_bg, trophy, txt, sp1, sp2], css,
    )


# ============================================================================= PROJECT CARDS
def icon_qr():
    L = Layer()
    L.rect(0, 0, 16, 16, CREAM)
    dark = "#3b2a55"
    for ox, oy in ((1, 1), (10, 1), (1, 10)):
        L.rect(ox, oy, 5, 5, dark)
        L.rect(ox + 1, oy + 1, 3, 3, CREAM)
        L.dot(ox + 2, oy + 2, dark)
    L.rect(11, 11, 3, 3, dark)
    L.dot(12, 12, CREAM)
    rnd = random.Random(3)
    for y in range(0, 16):
        for x in range(0, 16):
            in_finder = (x < 7 and y < 7) or (x > 8 and y < 7) or (x < 7 and y > 8)
            in_align = 10 <= x <= 14 and 10 <= y <= 14
            if not in_finder and not in_align and 1 <= x <= 14 and 1 <= y <= 14 and rnd.random() < 0.45:
                L.dot(x, y, dark)
    return L


def icon_tomato():
    L = Layer()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 9.2)
            if d <= 6.4:
                L.dot(x, y, "#ff8a9b")
            elif d <= 7.4:
                L.dot(x, y, "#3b2a55")
    for x, y in ((4, 7), (4, 8), (5, 6)):
        L.dot(x, y, "#ffc2cc")
    for x in range(5, 11):
        L.dot(x, 4, "#7fe0b0")
    for x in (4, 5, 10, 11):
        L.dot(x, 5, "#7fe0b0")
    L.dot(7, 3, "#5cc896")
    L.dot(8, 3, "#5cc896")
    L.dot(8, 2, "#3b2a55")
    L.dot(8, 1, "#3b2a55")
    return L


def card(name, title, lines, tags, icon_fn, accent, alt):
    W, H = 150, 48
    bg = Layer()
    frame(bg, 0, 0, 146, 44, PLUM, accent, shadow=PLUM_D)
    bg.rect(5, 6, 22, 22, PLUM_L)
    ic = icon_fn()
    icon = Layer()
    for (x, y), c in ic.px.items():
        icon.dot(x + 8, y + 9 - 2, c)
    t = Layer()
    t.text(title, 32, 6, CREAM)
    for i, line in enumerate(lines):
        t.text(line, 32, 16 + i * 9, LAV_L)
    t.text(tags, 32, 35, accent)
    for s in (title, *lines, tags):
        assert text_width(s) <= 114, (s, text_width(s))
    return write_svg(name, W, H, 3, title.title(), alt, [bg, icon, t], REDUCED)


def cards():
    sail = Layer()
    sail.sprite(SAILBOAT, SAIL_KEYS, 0, 0)
    bub = Layer()
    bub.sprite(BUBBLE, BUBBLE_KEYS, 0, 2)
    card("card-nap-in-a-boat.svg", "NAP IN A BOAT", ["BLEND TWO LLMS WITH", "A SLIDER. 1ST PRIZE"], "SLERP + GGUF", lambda: sail, PINK,
         "Project card: Nap in a Boat. Blend two language models with a slider. 1st prize. SLERP and GGUF.")
    card("card-wedroid.svg", "WEDROID", ["EVENT MANAGER APP", "QR SCAN + SHEETS"], "ANDROID CLUB VITC", icon_qr, MINT,
         "Project card: WeDroid Event Manager. QR scanner and live Google Sheets updates for Android Club VITC.")
    card("card-rag.svg", "LOCAL RAG CHATBOT", ["ASK QUESTIONS OVER", "YOUR .TXT FILES"], "OLLAMA + PYTHON", lambda: bub, LAV,
         "Project card: Local RAG Chatbot. Ask questions over your text files with a local Ollama model.")
    card("card-celadon.svg", "CELADON", ["STUDY LOG, TO-DO,", "JOURNAL, POMODORO"], "FLUTTER + FIREBASE", icon_tomato, PEACH,
         "Project card: Celadon. A Flutter and Firebase productivity app with a study log, to-do list, journal and Pomodoro timer.")


# ============================================================================= SKILLS INVENTORY
def skills():
    items = [
        ("PYTHON", "#8fd3ff"), ("DART", "#7fe0e0"), ("FLUTTER", "#6fb4ff"), ("JAVA", "#ffb38f"),
        ("C/C++", "#b8a7ff"), ("FIREBASE", "#ffd36b"), ("OPENCV", "#a8f0d1"), ("MEDIAPIPE", "#ff9fb9"),
        ("OLLAMA", "#f4e3cf"), ("RAG", "#d6a8ff"), ("GIT", "#ff9d7a"), ("FIGMA", "#e3a8ff"),
    ]
    SW, SH, GAP, M = 58, 32, 4, 6
    W = 6 * SW + 5 * GAP + 2 * M
    H = 2 * SH + GAP + 2 * M
    bg = Layer()
    g = Layer()
    t = Layer()
    for i, (label, col) in enumerate(items):
        r, c = divmod(i, 6)
        x = M + c * (SW + GAP)
        y = M + r * (SH + GAP)
        frame(bg, x, y, SW, SH, PLUM, "#4a3d7a")
        light, dark = mix(col, "#ffffff", 0.45), mix(col, "#000000", 0.28)
        keys = {"o": "#3b2a55", "L": light, "M": col, "D": dark}
        g.sprite(GEM, keys, x + (SW - 12) // 2, y + 5)
        g.dot(x + (SW - 12) // 2 + 3, y + 7, "#ffffff")
        w = text_width(label)
        assert w <= SW - 4, label
        t.text(label, x + (SW - w) // 2, y + 20, CREAM)
    glints = Layer("tw1")
    for i in (0, 5, 8):
        r, c = divmod(i, 6)
        sparkle(glints, M + c * (SW + GAP) + SW - 6, M + r * (SH + GAP) + 6, CREAM)
    css = ("@keyframes tw{0%,55%,100%{opacity:1}70%{opacity:.1}}.tw1{animation:tw 3s steps(1) infinite}" + REDUCED)
    return write_svg(
        "skills.svg", W, H, 900 / W, "Skills inventory",
        "An inventory grid of gems labelled Python, Dart, Flutter, Java, C and C++, Firebase, OpenCV, MediaPipe, Ollama, RAG, Git and Figma.",
        [bg, g, t, glints], css,
    )


if __name__ == "__main__":
    sizes = {
        "banner": banner(), "wave": wave(), "footer": footer(), "achievement": achievement(),
        "skills": skills(),
    }
    cards()
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:28s}{p.stat().st_size / 1024:7.1f} KB")

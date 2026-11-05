import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Palette constants matching the project aesthetic
DARK = (81, 66, 103, 255)       # #514267 Dark Purple
DARK_SHADOW = (58, 47, 75, 255) # Deeper Dark Purple
LAVENDER = (200, 182, 226, 255) # #C8B6E2 Lavender
LAV_LIGHT = (225, 215, 240, 255)# Light Lavender
WHITE = (255, 255, 255, 255)    # #FFFFFF White
SOFT_GREY = (243, 240, 247, 255)# #F3F0F7 Soft Grey
PINK = (255, 179, 209, 255)     # #FFB3D1 Pastel Pink
MINT = (168, 240, 209, 255)     # Soft Mint
SKY = (143, 211, 255, 255)      # Soft Sky Blue

def get_base():
    return Image.open("assets/projects/base_card_canvas.png").convert("RGBA")

def draw_sparkle(d, cx, cy, size, col):
    # Diamond 4-point sparkle
    pts = [
        (cx, cy - size),
        (cx + size * 0.28, cy - size * 0.28),
        (cx + size, cy),
        (cx + size * 0.28, cy + size * 0.28),
        (cx, cy + size),
        (cx - size * 0.28, cy + size * 0.28),
        (cx - size, cy),
        (cx - size * 0.28, cy - size * 0.28),
    ]
    d.polygon(pts, fill=col)

def draw_round_rect(d, xy, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=rad, fill=fill, outline=outline, width=width)

# =============================================================================
# 1. VIRTUAL CANVAS
# =============================================================================
def make_virtual_canvas():
    base = get_base()
    # Draw at 2x resolution (2400x1200) for supersampled anti-aliasing
    layer = Image.new("RGBA", (2400, 1200), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    
    # 2x scale coordinates (center is 1200, 600)
    CX, CY = 1200, 600
    
    # Canvas frame / floating UI window
    draw_round_rect(d, (CX - 500, CY - 240, CX + 500, CY + 240), rad=30, fill=(255, 255, 255, 160), outline=LAVENDER, width=8)
    # Window header bar
    d.line([(CX - 480, CY - 180), (CX + 480, CY - 180)], fill=LAVENDER, width=4)
    # Window dots
    for i, col in enumerate([PINK, LAVENDER, MINT]):
        d.ellipse([CX - 460 + i * 36, CY - 218, CX - 436 + i * 36, CY - 194], fill=col)
    
    # Gesture tracking crosshairs / landmarks
    pts = [
        (CX - 380, CY + 80), (CX - 280, CY - 40), (CX - 150, CY - 100),
        (CX, CY - 140), (CX + 160, CY - 80), (CX + 320, CY + 40), (CX + 420, CY + 100)
    ]
    # Draw connecting tracking dash-lines
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i+1]], fill=(200, 182, 226, 120), width=6)
    for p in pts:
        d.ellipse([p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12], fill=WHITE, outline=DARK, width=6)
    
    # Sweeping glowing brushstroke (rainbow of dreamy lavender / purple / pink)
    for t in range(0, 100):
        s = t / 100.0
        x = CX - 400 + s * 800
        y = CY + 80 * math.sin(s * math.pi * 2.2) - 20
        rad = int(24 + 18 * math.sin(s * math.pi))
        col = (
            int(81 * (1 - s) + 200 * s),
            int(66 * (1 - s) + 182 * s),
            int(103 * (1 - s) + 226 * s),
            230
        )
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col)
    
    # Glowing paintbrush / stylus or Hand with pointing index finger at CX, CY - 140
    # Pointing hand silhouette
    hand_pts = [
        (CX - 120, CY + 220),  # wrist left
        (CX - 90, CY + 60),    # palm left
        (CX - 60, CY - 40),    # index base
        (CX - 20, CY - 160),   # index tip
        (CX + 20, CY - 150),   # index tip right
        (CX + 20, CY - 30),    # index joint
        (CX + 60, CY - 10),    # middle knuckle
        (CX + 80, CY + 40),    # ring knuckle
        (CX + 90, CY + 100),   # pinky
        (CX + 40, CY + 220),   # wrist right
    ]
    # Hand shadow
    d.polygon([(p[0] + 10, p[1] + 10) for p in hand_pts], fill=(200, 182, 226, 140))
    # Hand body
    d.polygon(hand_pts, fill=WHITE, outline=DARK, width=12)
    # Fingertip glow ring
    d.ellipse([CX - 40, CY - 180, CX + 40, CY - 100], outline=PINK, width=10)
    d.ellipse([CX - 60, CY - 200, CX + 60, CY - 80], outline=(255, 179, 209, 100), width=6)
    
    # Sparkles around the fingertip
    draw_sparkle(d, CX - 100, CY - 180, 36, PINK)
    draw_sparkle(d, CX + 80, CY - 190, 44, WHITE)
    draw_sparkle(d, CX + 140, CY - 130, 28, LAVENDER)
    draw_sparkle(d, CX + 360, CY - 40, 40, PINK)
    draw_sparkle(d, CX - 320, CY + 40, 32, WHITE)

    layer_down = layer.resize((1200, 600), Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, layer_down)

# =============================================================================
# 2. FORENSYS
# =============================================================================
def make_forensys():
    base = get_base()
    layer = Image.new("RGBA", (2400, 1200), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    CX, CY = 1200, 600

    # Digital forensic shield badge in center
    shield_pts = [
        (CX, CY - 260),          # top center
        (CX + 280, CY - 200),    # top right
        (CX + 260, CY + 80),     # mid right
        (CX, CY + 260),          # bottom tip
        (CX - 260, CY + 80),     # mid left
        (CX - 280, CY - 200),    # top left
    ]
    # Shield shadow
    d.polygon([(p[0] + 12, p[1] + 12) for p in shield_pts], fill=(200, 182, 226, 140))
    # Shield fill
    d.polygon(shield_pts, fill=WHITE, outline=DARK, width=14)
    # Inner shield accent border
    inner_shield = [
        (CX, CY - 220),
        (CX + 230, CY - 170),
        (CX + 210, CY + 60),
        (CX, CY + 210),
        (CX - 210, CY + 60),
        (CX - 230, CY - 170),
    ]
    d.polygon(inner_shield, fill=LAV_LIGHT, outline=LAVENDER, width=8)

    # Stylized circuit / digital node lines inside shield
    nodes = [
        (CX - 120, CY - 80), (CX + 120, CY - 80),
        (CX, CY), (CX - 100, CY + 100), (CX + 100, CY + 100)
    ]
    for n1 in nodes:
        for n2 in nodes:
            if n1 != n2:
                d.line([n1, n2], fill=(200, 182, 226, 160), width=6)
    for n in nodes:
        d.ellipse([n[0]-14, n[1]-14, n[0]+14, n[1]+14], fill=WHITE, outline=DARK, width=6)

    # Foreground Magnifying Glass examining evidence
    MG_CX, MG_CY = CX + 120, CY - 20
    MG_R = 170
    # Handle
    d.line([(MG_CX + int(MG_R * 0.7), MG_CY + int(MG_R * 0.7)),
            (MG_CX + int(MG_R * 0.7) + 160, MG_CY + int(MG_R * 0.7) + 160)],
           fill=DARK, width=32)
    d.line([(MG_CX + int(MG_R * 0.7) + 40, MG_CY + int(MG_R * 0.7) + 40),
            (MG_CX + int(MG_R * 0.7) + 150, MG_CY + int(MG_R * 0.7) + 150)],
           fill=LAVENDER, width=16)

    # Glass rim
    d.ellipse([MG_CX - MG_R, MG_CY - MG_R, MG_CX + MG_R, MG_CY + MG_R], fill=(255, 255, 255, 220), outline=DARK, width=16)
    # Glass reflection
    d.arc([MG_CX - MG_R + 25, MG_CY - MG_R + 25, MG_CX + MG_R - 25, MG_CY + MG_R - 25],
          start=190, end=270, fill=WHITE, width=14)

    # Fingerprint ridges inside magnifying lens
    for rad in [40, 70, 100, 130]:
        d.arc([MG_CX - rad, MG_CY - rad + 10, MG_CX + rad, MG_CY + rad + 10],
              start=200, end=340, fill=DARK, width=8)
        d.arc([MG_CX - rad, MG_CY - rad + 35, MG_CX + rad, MG_CY + rad + 35],
              start=20, end=160, fill=DARK, width=8)

    # Sparkles / Evidence indicators
    draw_sparkle(d, CX - 380, CY - 100, 40, LAVENDER)
    draw_sparkle(d, CX - 320, CY + 140, 32, PINK)
    draw_sparkle(d, CX + 440, CY - 160, 44, WHITE)
    draw_sparkle(d, CX + 360, CY + 180, 36, PINK)

    layer_down = layer.resize((1200, 600), Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, layer_down)

# =============================================================================
# 3. DESKTOP PET (LEON)
# =============================================================================
def make_desktop_pet():
    base = get_base()
    # Retro pixel art canvas for desktop pet (Leon Kennedy)
    # Center pixel grid (scaled cleanly)
    layer = Image.new("RGBA", (2400, 1200), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    CX, CY = 1200, 600

    # Chibi Leon pixel pet in center
    PX = 14 # pixel size
    # Let's draw an adorable retro pixel Leon
    # Center X = 1100, Y = 580
    LX, LY = CX - 140, CY - 120

    # Hair (Leon's signature center-parted brown/blonde fringe)
    HAIR_COLOR = (120, 95, 135, 255) # stylized lavender-brown
    HAIR_LIGHT = (180, 155, 200, 255)
    FACE_COLOR = (255, 240, 245, 255)
    JACKET_DARK = DARK
    JACKET_SHIRT = (200, 182, 226, 255)
    
    # Draw pixel blocks for Leon
    def p(dx, dy, w, h, col):
        d.rectangle([LX + dx * PX, LY + dy * PX, LX + (dx + w) * PX, LY + (dy + h) * PX], fill=col)

    # Shadow
    d.ellipse([LX - 2 * PX, LY + 23 * PX, LX + 20 * PX, LY + 29 * PX], fill=(200, 182, 226, 120))

    # Hair back
    p(2, -2, 14, 8, HAIR_COLOR)
    p(0, 1, 18, 6, HAIR_COLOR)
    # Face base
    p(3, 4, 12, 10, FACE_COLOR)
    # Eyes (anime pixel eyes with white shine)
    p(4, 8, 3, 4, DARK)
    p(11, 8, 3, 4, DARK)
    p(5, 8, 1, 2, WHITE)
    p(12, 8, 1, 2, WHITE)
    # Blush
    p(3, 11, 2, 1, PINK)
    p(13, 11, 2, 1, PINK)
    # Cute little mouth
    p(8, 11, 2, 1, DARK)

    # Hair front fringe (Leon's parted bangs)
    p(1, 2, 5, 6, HAIR_COLOR)
    p(2, 3, 4, 6, HAIR_LIGHT)
    p(12, 2, 5, 7, HAIR_COLOR)
    p(13, 3, 3, 5, HAIR_LIGHT)
    p(6, 2, 2, 3, HAIR_COLOR)
    p(10, 2, 2, 3, HAIR_COLOR)

    # Tactical bomber jacket (RE4 style in Dark Purple / Lavender)
    p(2, 14, 14, 9, JACKET_DARK)
    p(6, 14, 6, 9, JACKET_SHIRT) # Inner tactical shirt
    p(8, 14, 2, 9, DARK)          # Holster strap
    # Arms
    p(0, 14, 3, 7, JACKET_DARK)
    p(15, 14, 3, 7, JACKET_DARK)
    p(0, 20, 3, 2, FACE_COLOR) # Little hands
    p(15, 20, 3, 2, FACE_COLOR)
    # Legs
    p(4, 23, 4, 4, JACKET_DARK)
    p(10, 23, 4, 4, JACKET_DARK)

    # Speech Bubble floating above him: CX + 200, CY - 180
    BX, BY = CX + 240, CY - 140
    BW, BH = 340, 220
    draw_round_rect(d, (BX - BW//2 + 10, BY - BH//2 + 10, BX + BW//2 + 10, BY + BH//2 + 10), rad=24, fill=(200, 182, 226, 120))
    draw_round_rect(d, (BX - BW//2, BY - BH//2, BX + BW//2, BY + BH//2), rad=24, fill=WHITE, outline=DARK, width=10)
    # Speech tail
    d.polygon([(BX - 60, BY + BH//2 - 2), (BX - 110, BY + BH//2 + 60), (BX - 20, BY + BH//2 - 2)], fill=WHITE)
    d.line([(BX - 60, BY + BH//2 - 2), (BX - 110, BY + BH//2 + 60), (BX - 20, BY + BH//2 - 2)], fill=DARK, width=10)
    # Inner pink heart inside speech bubble
    # Draw heart at BX, BY - 10
    HX, HY = BX, BY - 10
    d.ellipse([HX - 64, HY - 44, HX, HY + 20], fill=PINK)
    d.ellipse([HX, HY - 44, HX + 64, HY + 20], fill=PINK)
    d.polygon([(HX - 60, HY - 8), (HX + 60, HY - 8), (HX, HY + 56)], fill=PINK)

    # Cute Pixel Mouse Cursor petting Leon's head!
    CUR_X, CUR_Y = LX - 80, LY - 80
    # Draw pixel cursor hand pointing
    d.polygon([
        (CUR_X, CUR_Y), (CUR_X, CUR_Y + 110),
        (CUR_X + 32, CUR_Y + 84), (CUR_X + 68, CUR_Y + 130),
        (CUR_X + 92, CUR_Y + 116), (CUR_X + 56, CUR_Y + 70),
        (CUR_X + 88, CUR_Y + 70)
    ], fill=WHITE, outline=DARK, width=8)

    # Petting hearts & sparkles
    draw_sparkle(d, CX - 340, CY + 80, 36, PINK)
    draw_sparkle(d, CX + 460, CY + 80, 42, LAVENDER)
    draw_sparkle(d, LX + 120, LY - 80, 30, PINK)

    layer_down = layer.resize((1200, 600), Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, layer_down)

# =============================================================================
# 4. JARVIS
# =============================================================================
def make_jarvis():
    base = get_base()
    layer = Image.new("RGBA", (2400, 1200), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    CX, CY = 1200, 600

    # Futuristic AI Arc Reactor Core in center
    # Outer pulse ring
    d.ellipse([CX - 280, CY - 280, CX + 280, CY + 280], outline=(200, 182, 226, 120), width=6)
    d.ellipse([CX - 240, CY - 240, CX + 240, CY + 240], fill=(255, 255, 255, 140), outline=LAVENDER, width=10)
    
    # Outer segmented reactor ring (triangular notches)
    N = 12
    for i in range(N):
        ang = i * (2 * math.pi / N)
        r1, r2 = 200, 235
        x1, y1 = CX + r1 * math.cos(ang), CY + r1 * math.sin(ang)
        x2, y2 = CX + r2 * math.cos(ang), CY + r2 * math.sin(ang)
        d.line([(x1, y1), (x2, y2)], fill=DARK, width=12)

    # Middle ring
    d.ellipse([CX - 190, CY - 190, CX + 190, CY + 190], fill=WHITE, outline=DARK, width=12)
    # Inner energy ring
    d.ellipse([CX - 130, CY - 130, CX + 130, CY + 130], fill=LAV_LIGHT, outline=LAVENDER, width=12)
    # Core center
    d.ellipse([CX - 70, CY - 70, CX + 70, CY + 70], fill=WHITE, outline=DARK, width=10)
    # Glowing center spark
    draw_sparkle(d, CX, CY, 46, PINK)

    # Dynamic Audio Waveform flowing horizontally across the core
    # Draw audio waveform bars on left and right
    bar_heights = [24, 48, 80, 130, 90, 160, 220, 140, 180, 110, 60, 30]
    # Left waves
    for i, h in enumerate(bar_heights):
        bx = CX - 320 - (len(bar_heights) - 1 - i) * 36
        d.line([(bx, CY - h), (bx, CY + h)], fill=DARK if i % 2 == 0 else LAVENDER, width=14)
    # Right waves
    for i, h in enumerate(reversed(bar_heights)):
        bx = CX + 320 + i * 36
        d.line([(bx, CY - h), (bx, CY + h)], fill=DARK if i % 2 == 0 else LAVENDER, width=14)

    # Holographic orbital arcs / orbit satellites
    d.arc([CX - 480, CY - 180, CX + 480, CY + 180], start=-30, end=70, fill=LAVENDER, width=6)
    d.arc([CX - 480, CY - 180, CX + 480, CY + 180], start=150, end=250, fill=LAVENDER, width=6)
    # Satellite dots
    d.ellipse([CX + 450, CY - 60, CX + 474, CY - 36], fill=PINK)
    d.ellipse([CX - 460, CY + 40, CX - 436, CY + 64], fill=WHITE, outline=DARK, width=4)

    # Dreamy sparkles around the AI core
    draw_sparkle(d, CX - 380, CY - 180, 40, WHITE)
    draw_sparkle(d, CX + 380, CY - 190, 36, PINK)
    draw_sparkle(d, CX - 220, CY + 220, 32, LAVENDER)
    draw_sparkle(d, CX + 240, CY + 210, 42, WHITE)

    layer_down = layer.resize((1200, 600), Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, layer_down)

if __name__ == "__main__":
    print("Generating 4 project cards...")
    vc = make_virtual_canvas()
    vc.save("assets/projects/virtual-canvas.png")
    print("Saved virtual-canvas.png")

    fs = make_forensys()
    fs.save("assets/projects/forensys.png")
    print("Saved forensys.png")

    dp = make_desktop_pet()
    dp.save("assets/projects/desktop-pet.png")
    print("Saved desktop-pet.png")

    jv = make_jarvis()
    jv.save("assets/projects/jarvis.png")
    print("Saved jarvis.png")
    print("All 4 cards generated successfully!")

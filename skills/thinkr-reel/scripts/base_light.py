import cairo, math, subprocess, sys, json, os, random

W, H, FPS = 1080, 1920, 30
NIGHT = (0.980, 0.976, 0.969)   # Paper (background)
NIGHT2 = (0.953, 0.949, 0.937)  # Linen (panels)
GRAPH = (0.851, 0.847, 0.827)   # Stone (lines)
WHITE = (0.067, 0.071, 0.082)   # Ink (main text)
MUTED = (0.365, 0.376, 0.408)   # Slate
DIM = (0.55, 0.56, 0.59)
RED = (0.890, 0.106, 0.137)     # THINKR Red #E31B23
REDB = (0.710, 0.071, 0.106)    # Red Deep #B5121B
LIMEB = (0.561, 0.722, 0.0)     # Lime, data only
TEAL = REDB
AMBER = REDB

def hexa(c, a=1): return (*c, a)
def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x):
    x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, start, dur): return ease((t - start) / dur)

def bg(ctx):
    ctx.set_source_rgb(*NIGHT); ctx.paint()
    r = cairo.RadialGradient(W/2, 1000, 0, W/2, 1000, 800)
    r.add_color_stop_rgba(0, *NIGHT2, 1); r.add_color_stop_rgba(1, *NIGHT2, 0)
    ctx.set_source(r); ctx.paint()
    ctx.set_source_rgba(*GRAPH, 0.55)
    for x in range(30, W, 60):
        for y in range(30, H, 60):
            ctx.arc(x, y, 1.6, 0, 2*math.pi); ctx.fill()

FAMS = {"Bold": "FigtreeXB", "Medium": "FigtreeMed", "Black": "FigtreeBlk", "Mono": "JBMonoSB", "Serif": "InstrSerifIt"}
def font(ctx, size, weight="Bold"):
    ctx.select_font_face(FAMS.get(weight, weight), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def mark(ctx, x, y, size, ink=None, head=None, a=1):
    ink = ink or WHITE; head = head or RED; k = size/480
    def R(x0, y0, x1, y1, c):
        ctx.set_source_rgba(*c, a); ctx.rectangle(x + x0*k, y + y0*k, (x1-x0)*k, (y1-y0)*k); ctx.fill()
    for r in [(0,0,38,480),(0,0,480,38),(442,0,480,480),(96,442,480,480),
              (96,96,134,480),(96,96,384,134),(346,96,384,384),(192,346,384,384),(192,240,230,384)]:
        R(*r, ink)
    R(230,173,298,240, head)

def wordmark(ctx, cx, y, size, a=1, ink=None):
    ink = ink or WHITE
    font(ctx, size, "Black"); e1 = ctx.text_extents("THINK"); e2 = ctx.text_extents("R")
    x = cx - (e1.x_advance + e2.x_advance)/2
    ctx.set_source_rgba(*ink, a); ctx.move_to(x, y); ctx.show_text("THINK")
    ctx.set_source_rgba(*RED, a); ctx.move_to(x + e1.x_advance, y); ctx.show_text("R")

def wrap(ctx, text, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        test = (cur + " " + w).strip()
        if ctx.text_extents(test).x_advance > maxw and cur:
            lines.append(cur); cur = w
        else: cur = test
    lines.append(cur); return lines

def text_c(ctx, text, y, size, color, alpha=1, weight="Bold", maxw=920, lh=1.15, dy=0):
    font(ctx, size, weight)
    ctx.set_source_rgba(*color, alpha)
    lines = wrap(ctx, text, maxw)
    for i, ln in enumerate(lines):
        e = ctx.text_extents(ln)
        ctx.move_to(W/2 - e.x_advance/2, y + dy + i*size*lh); ctx.show_text(ln)
    return y + len(lines)*size*lh

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x+w-r, y+r, r, -math.pi/2, 0); ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi); ctx.arc(x+r, y+r, r, math.pi, 1.5*math.pi)
    ctx.close_path()

def chip(ctx, label, color, a):
    font(ctx, 32, "Mono"); e = ctx.text_extents(label)
    w = e.x_advance + 36; x = W/2 - w/2; y = 300
    ctx.set_source_rgba(*RED, a); ctx.rectangle(x, y + 18, 20, 20); ctx.fill()
    ctx.set_source_rgba(*MUTED, a); ctx.move_to(x + 36, y + 38); ctx.show_text(label)

def progress(ctx, idx, n, frac):
    gap, x0, x1, y = 10, 80, W-80, 210
    segw = (x1 - x0 - gap*(n-1)) / n
    for i in range(n):
        x = x0 + i*(segw+gap)
        ctx.set_source_rgba(*GRAPH, 1); ctx.rectangle(x, y, segw, 6); ctx.fill()
        f = 1 if i < idx else (frac if i == idx else 0)
        if f > 0:
            ctx.set_source_rgba(*LIMEB, 1); ctx.rectangle(x, y, segw*f, 6); ctx.fill()
    if idx < n-1:
        mark(ctx, 80, 112, 52); wordmark(ctx, 0, 0, 1, a=0)
        font(ctx, 44, "Black"); ctx.set_source_rgba(*WHITE, 1); ctx.move_to(150, 156); ctx.show_text("THINK")
        e = ctx.text_extents("THINK"); ctx.set_source_rgba(*RED, 1); ctx.move_to(150 + e.x_advance, 156); ctx.show_text("R")

# ---------- scenes ----------
def s_hook(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "THE SCIENCE", TEAL, a)
    text_c(ctx, "How does", 560, 92, WHITE, a, dy=30*(1-a))
    b = prog(t, .25, .5)
    font(ctx, 200); lbl = "BPC-157"; e = ctx.text_extents(lbl)
    s = 0.85 + 0.15*b
    ctx.save(); ctx.translate(W/2, 880); ctx.scale(s, s)
    ctx.set_source_rgba(*TEAL, b); ctx.move_to(-e.x_advance/2, 0); ctx.show_text(lbl); ctx.restore()
    c = prog(t, .6, .4)
    text_c(ctx, "actually work?", 1060, 92, WHITE, c, dy=30*(1-c))
    # bead chain wiggle
    n = 15
    for i in range(n):
        p = prog(t, .8 + i*0.08, .3)
        x = 150 + i*(780/(n-1)); y = 1300 + 26*math.sin(i*0.9 + t*3)
        if i < n-1:
            x2 = 150 + (i+1)*(780/(n-1)); y2 = 1300 + 26*math.sin((i+1)*0.9 + t*3)
            ctx.set_source_rgba(*TEAL, 0.35*p); ctx.set_line_width(5)
            ctx.move_to(x, y); ctx.line_to(x2, y2); ctx.stroke()
        ctx.set_source_rgba(*TEAL, p); ctx.arc(x, y, 17*p, 0, 2*math.pi); ctx.fill()

def s_molecule(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "THE MOLECULE", TEAL, a)
    text_c(ctx, "15 amino acids", 520, 96, WHITE, a, dy=30*(1-a))
    # zigzag chain of 15 numbered beads
    n = 15; pts = []
    for i in range(n):
        row = i // 5; col = i % 5
        if row == 1: col = 4 - col
        pts.append((220 + col*160, 760 + row*190))
    for i in range(n):
        p = prog(t, .2 + i*0.17, .35)
        if p <= 0: continue
        x, y = pts[i]
        if i > 0:
            px, py = pts[i-1]
            ctx.set_source_rgba(*TEAL, 0.45); ctx.set_line_width(6)
            ctx.move_to(px, py); ctx.line_to(px + (x-px)*p, py + (y-py)*p); ctx.stroke()
        ctx.set_source_rgba(*TEAL, 0.18*p); ctx.arc(x, y, 58*p, 0, 2*math.pi); ctx.fill()
        ctx.set_source_rgba(*TEAL, p); ctx.set_line_width(4); ctx.arc(x, y, 44*p, 0, 2*math.pi); ctx.stroke()
        font(ctx, 34); s = str(i+1); e = ctx.text_extents(s)
        ctx.set_source_rgba(*WHITE, p); ctx.move_to(x - e.x_advance/2, y + 12); ctx.show_text(s)
    c = prog(t, 2.6, .5)
    text_c(ctx, "Modeled on a protective protein found in gastric juice", 1420, 48, MUTED, c, weight="Medium", maxw=860, dy=20*(1-c))

def s_three(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "IN THE LAB", TEAL, a)
    text_c(ctx, "It does 3 things", 520, 96, WHITE, a, dy=30*(1-a))
    items = ["New blood vessels", "Growth hormone response", "Cell migration"]
    for i, it in enumerate(items):
        p = prog(t, .35 + i*0.4, .4)
        y = 820 + i*210; x = 150
        rrect(ctx, x + 40*(1-p), y, 780, 140, 28)
        ctx.set_source_rgba(1, 1, 1, 0.05*p); ctx.fill_preserve()
        ctx.set_source_rgba(*TEAL, 0.5*p); ctx.set_line_width(2); ctx.stroke()
        ctx.set_source_rgba(*TEAL, p); ctx.arc(x + 80 + 40*(1-p), y + 70, 40, 0, 2*math.pi); ctx.fill()
        font(ctx, 46); s = str(i+1); e = ctx.text_extents(s)
        ctx.set_source_rgba(0.03, 0.05, 0.08, p); ctx.move_to(x + 80 + 40*(1-p) - e.x_advance/2, y + 86); ctx.show_text(s)
        font(ctx, 46); ctx.set_source_rgba(*WHITE, p); ctx.move_to(x + 150 + 40*(1-p), y + 86); ctx.show_text(it)

def branch(ctx, x, y, ang, length, depth, grow, seed):
    if depth == 0 or grow <= 0: return
    seg = clamp(grow * 1.0)
    x2 = x + math.cos(ang)*length*seg; y2 = y + math.sin(ang)*length*seg
    ctx.set_line_width(2 + depth*2.6); ctx.set_source_rgba(*RED, 0.55 + depth*0.07)
    ctx.move_to(x, y); ctx.line_to(x2, y2); ctx.stroke()
    if grow > 1:
        rnd = random.Random(seed)
        for k, sgn in enumerate((-1, 1)):
            branch(ctx, x2, y2, ang + sgn*(0.42 + rnd.random()*0.3), length*0.74, depth-1, grow-1, seed*3+k)

def s_vessels(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "MECHANISM 01", TEAL, a)
    text_c(ctx, "Grows new blood vessels", 520, 92, WHITE, a, dy=30*(1-a), maxw=900)
    g = clamp((t - .3) / (d - 1.2)) * 6.2
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    branch(ctx, W/2, 1360, -math.pi/2, 200, 6, g, 7)
    branch(ctx, W/2-10, 1360, -math.pi/2 - 0.9, 150, 5, g - 0.6, 11)
    branch(ctx, W/2+10, 1360, -math.pi/2 + 0.9, 150, 5, g - 0.6, 13)
    c = prog(t, 1.4, .5)
    text_c(ctx, "via VEGFR2 + nitric oxide signaling", 1460, 48, MUTED, c, weight="Medium", dy=20*(1-c))
    text_c(ctx, "(Akt–eNOS pathway)", 1525, 40, DIM, c, weight="Medium")

def s_receptors(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "MECHANISM 02", TEAL, a)
    text_c(ctx, "Primes tendon cells", 520, 92, WHITE, a, dy=30*(1-a))
    cx, cy, R = W/2, 1040, 230
    p = prog(t, .2, .5)
    ctx.set_source_rgba(*TEAL, 0.10*p); ctx.arc(cx, cy, R*p, 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(*TEAL, 0.8*p); ctx.set_line_width(5); ctx.arc(cx, cy, R*p, 0, 2*math.pi); ctx.stroke()
    ctx.set_source_rgba(*TEAL, 0.35*p); ctx.arc(cx+20, cy-10, 80*p, 0, 2*math.pi); ctx.fill()
    nrec = int(4 + 12 * clamp((t - .6) / (d - 1.6)))
    for i in range(nrec):
        ang = i * (2*math.pi/16) + 0.2
        bx, by = cx + math.cos(ang)*R, cy + math.sin(ang)*R
        ox, oy = cx + math.cos(ang)*(R+42), cy + math.sin(ang)*(R+42)
        ctx.set_source_rgba(*AMBER, 1); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(bx, by); ctx.line_to(ox, oy); ctx.stroke()
        for s in (-0.5, 0.5):
            ctx.move_to(ox, oy); ctx.line_to(ox + math.cos(ang+s)*22, oy + math.sin(ang+s)*22); ctx.stroke()
    # GH molecules drifting in
    rnd = random.Random(3)
    for k in range(10):
        ang = rnd.random()*2*math.pi; ph = rnd.random()
        f = ((t*0.35 + ph) % 1)
        r = R + 130 - 90*f
        ctx.set_source_rgba(*WHITE, 0.8*(1-f)*p)
        ctx.arc(cx + math.cos(ang)*r, cy + math.sin(ang)*r, 10, 0, 2*math.pi); ctx.fill()
    c = prog(t, 1.0, .5)
    text_c(ctx, "More growth hormone receptors = a louder repair signal", 1460, 48, MUTED, c, weight="Medium", maxw=860, dy=20*(1-c))

def s_migration(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "MECHANISM 03", TEAL, a)
    text_c(ctx, "Moves repair cells in", 520, 86, WHITE, a, dy=30*(1-a))
    top, bot = 800, 1300
    gap = 220
    ctx.set_source_rgba(*TEAL, 0.10)
    rrect(ctx, 90, top, W/2 - gap/2 - 90, bot-top, 30); ctx.fill()
    rrect(ctx, W/2 + gap/2, top, W/2 - gap/2 - 90, bot-top, 30); ctx.fill()
    # fibers
    ctx.set_source_rgba(*TEAL, 0.25); ctx.set_line_width(3)
    for y in range(top+40, bot, 60):
        ctx.move_to(120, y); ctx.line_to(W/2 - gap/2 - 30, y); ctx.stroke()
        ctx.move_to(W/2 + gap/2 + 30, y); ctx.line_to(W - 120, y); ctx.stroke()
    fp = clamp((t - .3) / (d - 1.0))
    rnd = random.Random(5)
    for k in range(14):
        side = -1 if k % 2 == 0 else 1
        y = top + 60 + rnd.random()*(bot-top-120)
        sx = W/2 + side*(gap/2 + 120 + rnd.random()*250)
        tx = W/2 + side*rnd.random()*70
        f = ease(clamp(fp*1.3 - rnd.random()*0.3))
        x = sx + (tx - sx)*f
        ctx.set_source_rgba(*AMBER, 0.95); ctx.arc(x, y, 22, 0, 2*math.pi); ctx.fill()
        ctx.set_source_rgba(0.5, 0.3, 0.0, 0.9); ctx.arc(x+4, y-3, 8, 0, 2*math.pi); ctx.fill()
    c = prog(t, .8, .5)
    text_c(ctx, "via the FAK–paxillin pathway", 1420, 48, MUTED, c, weight="Medium", dy=20*(1-c))

def s_reality(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "REALITY CHECK", AMBER, a)
    text_c(ctx, "35 of 36 studies were in animals or cells", 500, 84, WHITE, a, dy=30*(1-a), maxw=900)
    n = 36; cols = 6; sp = 110; x0 = W/2 - (cols-1)*sp/2; y0 = 760
    for i in range(n):
        p = prog(t, .3 + i*0.055, .25)
        x = x0 + (i % cols)*sp; y = y0 + (i // cols)*sp
        last = i == n-1
        col = AMBER if last else DIM
        rad = (40 if last else 34)*p
        if last:
            pulse = 1 + 0.12*math.sin(t*6)*p
            ctx.set_source_rgba(*AMBER, 0.25*p); ctx.arc(x, y, rad*1.6*pulse, 0, 2*math.pi); ctx.fill()
        ctx.set_source_rgba(*col, p); ctx.arc(x, y, rad, 0, 2*math.pi); ctx.fill()
    c = prog(t, 2.5, .5)
    text_c(ctx, "Only 1 human study: 12 people, no control group", 1430, 46, AMBER, c, weight="Medium", maxw=900, dy=20*(1-c))

def s_cta(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "THE TAKEAWAY", TEAL, a)
    font(ctx, 150)
    b = prog(t, .15, .5)
    text_c(ctx, "Promising", 720, 150, WHITE, b, dy=40*(1-b))
    c = prog(t, .6, .5)
    text_c(ctx, "≠ proven", 900, 150, AMBER, c, dy=40*(1-c))
    e2 = prog(t, 1.6, .5)
    rrect(ctx, W/2 - 410, 1080, 820, 110, 55)
    ctx.set_source_rgba(*TEAL, e2); ctx.fill()
    font(ctx, 46); s = "Follow for science-first breakdowns"; e = ctx.text_extents(s)
    font(ctx, 40); s = "Follow for science-first breakdowns"; e = ctx.text_extents(s)
    ctx.set_source_rgba(0.03, 0.05, 0.08, e2); ctx.move_to(W/2 - e.x_advance/2, 1148); ctx.show_text(s)
    f = prog(t, 2.0, .5)
    text_c(ctx, "Educational only. Not medical advice.", 1300, 34, MUTED, f, weight="Medium")
    text_c(ctx, "Source: Vasireddi et al., HSS Journal 2025", 1350, 30, DIM, f, weight="Medium")

LIME = (0.808, 0.914, 0.361)
BRED = (0.820, 0.165, 0.067)

def s_brand(ctx, t, d):
    a = prog(t, 0, .4)
    ctx.select_font_face("TeX Gyre Heros", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(38); lbl = "FOLLOW FOR MORE"; e = ctx.text_extents(lbl)
    ctx.set_source_rgba(*LIME, a); ctx.move_to(W/2 - e.x_advance/2, 660 + 20*(1-a)); ctx.show_text(lbl)
    b = prog(t, .15, .5); s = 0.88 + 0.12*b
    ctx.set_font_size(160); lbl = "THINKR MD"; e = ctx.text_extents(lbl)
    ctx.save(); ctx.translate(W/2, 860); ctx.scale(s, s)
    ctx.set_source_rgba(*WHITE, b); ctx.move_to(-e.x_advance/2, 0); ctx.show_text(lbl); ctx.restore()
    c = prog(t, .45, .4)
    ctx.set_font_size(72); lbl = "@thinkrmd"; e = ctx.text_extents(lbl)
    ctx.set_source_rgba(*WHITE, 0.92*c); ctx.move_to(W/2 - e.x_advance/2, 990 + 20*(1-c)); ctx.show_text(lbl)
    p = prog(t, .8, .4)
    ctx.set_font_size(44); lbl = "Save \u00b7 Share \u00b7 Follow"; e = ctx.text_extents(lbl)
    pw = e.x_advance + 100
    rrect(ctx, W/2 - pw/2, 1080, pw, 104, 52); ctx.set_source_rgba(*BRED, p); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, p); ctx.move_to(W/2 - e.x_advance/2, 1148); ctx.show_text(lbl)

SCENES = [s_hook, s_molecule, s_three, s_vessels, s_receptors, s_migration, s_reality, s_cta, s_brand]

# ---------- THINKR brand overrides ----------
def s_hook(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "THE SCIENCE", None, a)
    text_c(ctx, "How does", 580, 92, WHITE, a, dy=30*(1-a))
    b = prog(t, .25, .5)
    font(ctx, 210, "Black"); lbl = "BPC-157"; e = ctx.text_extents(lbl)
    s_ = 0.85 + 0.15*b
    ctx.save(); ctx.translate(W/2, 880); ctx.scale(s_, s_)
    ctx.set_source_rgba(*REDB, b); ctx.move_to(-e.x_advance/2, 0); ctx.show_text(lbl); ctx.restore()
    c = prog(t, .6, .4)
    text_c(ctx, "actually work?", 1050, 92, WHITE, c, dy=30*(1-c))
    n = 15
    for i in range(n):
        p = prog(t, .8 + i*0.08, .3)
        x = 150 + i*(780/(n-1)); y = 1290 + 26*math.sin(i*0.9 + t*3)
        if i < n-1:
            x2 = 150 + (i+1)*(780/(n-1)); y2 = 1290 + 26*math.sin((i+1)*0.9 + t*3)
            ctx.set_source_rgba(*GRAPH, p); ctx.set_line_width(5)
            ctx.move_to(x, y); ctx.line_to(x2, y2); ctx.stroke()
        col = RED if i == n-1 else WHITE
        ctx.set_source_rgba(*col, p); ctx.rectangle(x-14*p, y-14*p, 28*p, 28*p); ctx.fill()

def s_molecule(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "THE MOLECULE", None, a)
    text_c(ctx, "15 amino acids", 520, 96, WHITE, a, dy=30*(1-a))
    n = 15; pts = []
    for i in range(n):
        row = i // 5; col = i % 5
        if row == 1: col = 4 - col
        pts.append((220 + col*160, 760 + row*190))
    for i in range(n):
        p = prog(t, .2 + i*0.17, .35)
        if p <= 0: continue
        x, y = pts[i]
        if i > 0:
            px, py = pts[i-1]
            ctx.set_source_rgba(*GRAPH, 1); ctx.set_line_width(6)
            ctx.move_to(px, py); ctx.line_to(px + (x-px)*p, py + (y-py)*p); ctx.stroke()
        last = i == n-1
        ctx.set_source_rgba(*(RED if last else NIGHT2), p); ctx.arc(x, y, 44*p, 0, 2*math.pi); ctx.fill()
        ctx.set_source_rgba(*(RED if last else WHITE), p); ctx.set_line_width(4); ctx.arc(x, y, 44*p, 0, 2*math.pi); ctx.stroke()
        font(ctx, 32, "Mono"); s_ = str(i+1); e = ctx.text_extents(s_)
        ctx.set_source_rgba(*WHITE, p); ctx.move_to(x - e.x_advance/2, y + 11); ctx.show_text(s_)
    c = prog(t, 2.6, .5)
    text_c(ctx, "Modeled on a protective protein found in gastric juice", 1420, 48, MUTED, c, weight="Medium", maxw=860, dy=20*(1-c))

def s_three(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "IN THE LAB", None, a)
    text_c(ctx, "It does 3 things", 520, 96, WHITE, a, dy=30*(1-a))
    items = ["New blood vessels", "Growth hormone response", "Cell migration"]
    for i, it in enumerate(items):
        p = prog(t, .35 + i*0.4, .4)
        y = 820 + i*210; x = 150 + 40*(1-p)
        ctx.set_source_rgba(*NIGHT2, p); ctx.rectangle(x, y, 780, 140); ctx.fill()
        ctx.set_source_rgba(*GRAPH, p); ctx.set_line_width(2); ctx.rectangle(x, y, 780, 140); ctx.stroke()
        ctx.set_source_rgba(*RED, p); ctx.rectangle(x, y, 10, 140); ctx.fill()
        font(ctx, 40, "Mono"); ctx.set_source_rgba(*REDB, p); ctx.move_to(x + 50, y + 84); ctx.show_text(f"0{i+1}")
        font(ctx, 46, "Bold"); ctx.set_source_rgba(*WHITE, p); ctx.move_to(x + 150, y + 86); ctx.show_text(it)

def s_receptors(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "MECHANISM 02", None, a)
    text_c(ctx, "Primes tendon cells", 520, 92, WHITE, a, dy=30*(1-a))
    cx, cy, R_ = W/2, 1040, 230
    p = prog(t, .2, .5)
    ctx.set_source_rgba(*NIGHT2, p); ctx.arc(cx, cy, R_*p, 0, 2*math.pi); ctx.fill()
    ctx.set_source_rgba(*WHITE, 0.85*p); ctx.set_line_width(5); ctx.arc(cx, cy, R_*p, 0, 2*math.pi); ctx.stroke()
    ctx.set_source_rgba(*GRAPH, p); ctx.arc(cx+20, cy-10, 80*p, 0, 2*math.pi); ctx.fill()
    nrec = int(4 + 12 * clamp((t - .6) / (d - 1.6)))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(nrec):
        ang = i * (2*math.pi/16) + 0.2
        bx, by = cx + math.cos(ang)*R_, cy + math.sin(ang)*R_
        ox, oy = cx + math.cos(ang)*(R_+42), cy + math.sin(ang)*(R_+42)
        ctx.set_source_rgba(*REDB, 1); ctx.set_line_width(5)
        ctx.move_to(bx, by); ctx.line_to(ox, oy); ctx.stroke()
        for s_ in (-0.5, 0.5):
            ctx.move_to(ox, oy); ctx.line_to(ox + math.cos(ang+s_)*22, oy + math.sin(ang+s_)*22); ctx.stroke()
    rnd = random.Random(3)
    for k in range(10):
        ang = rnd.random()*2*math.pi; ph = rnd.random()
        f = ((t*0.35 + ph) % 1); r = R_ + 130 - 90*f
        ctx.set_source_rgba(*WHITE, 0.8*(1-f)*p)
        ctx.arc(cx + math.cos(ang)*r, cy + math.sin(ang)*r, 10, 0, 2*math.pi); ctx.fill()
    c = prog(t, 1.0, .5)
    text_c(ctx, "More growth hormone receptors = a louder repair signal", 1460, 48, MUTED, c, weight="Medium", maxw=860, dy=20*(1-c))

def s_migration(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "MECHANISM 03", None, a)
    text_c(ctx, "Moves repair cells in", 520, 86, WHITE, a, dy=30*(1-a))
    top, bot, gap = 800, 1300, 220
    ctx.set_source_rgba(*NIGHT2, 1)
    ctx.rectangle(90, top, W/2 - gap/2 - 90, bot-top); ctx.fill()
    ctx.rectangle(W/2 + gap/2, top, W/2 - gap/2 - 90, bot-top); ctx.fill()
    ctx.set_source_rgba(*GRAPH, 1); ctx.set_line_width(3)
    for y in range(top+40, bot, 60):
        ctx.move_to(120, y); ctx.line_to(W/2 - gap/2 - 30, y); ctx.stroke()
        ctx.move_to(W/2 + gap/2 + 30, y); ctx.line_to(W - 120, y); ctx.stroke()
    fp = clamp((t - .3) / (d - 1.0))
    rnd = random.Random(5)
    for k in range(14):
        side = -1 if k % 2 == 0 else 1
        y = top + 60 + rnd.random()*(bot-top-120)
        sx = W/2 + side*(gap/2 + 120 + rnd.random()*250)
        tx = W/2 + side*rnd.random()*70
        f = ease(clamp(fp*1.3 - rnd.random()*0.3))
        x = sx + (tx - sx)*f
        ctx.set_source_rgba(*WHITE, 0.95); ctx.arc(x, y, 22, 0, 2*math.pi); ctx.fill()
        ctx.set_source_rgba(*RED, 1); ctx.rectangle(x-6, y-9, 12, 12); ctx.fill()
    c = prog(t, .8, .5)
    text_c(ctx, "via the FAK–paxillin pathway", 1420, 48, MUTED, c, weight="Medium", dy=20*(1-c))

def s_reality(ctx, t, d):
    a = prog(t, 0, .4)
    font(ctx, 32, "Mono"); lbl = "REALITY CHECK"; e = ctx.text_extents(lbl)
    x = W/2 - (e.x_advance + 36)/2
    ctx.set_source_rgba(*RED, a); ctx.rectangle(x, 318, 20, 20); ctx.fill()
    ctx.set_source_rgba(*REDB, a); ctx.move_to(x + 36, 338); ctx.show_text(lbl)
    text_c(ctx, "35 of 36 studies were in animals or cells", 500, 84, WHITE, a, dy=30*(1-a), maxw=900)
    n = 36; cols = 6; sp = 110; x0 = W/2 - (cols-1)*sp/2; y0 = 760
    for i in range(n):
        p = prog(t, .3 + i*0.055, .25)
        x = x0 + (i % cols)*sp; y = y0 + (i // cols)*sp
        last = i == n-1
        sz = (66 if last else 56)*p
        if last:
            pulse = 1 + 0.12*math.sin(t*6)*p
            ctx.set_source_rgba(*LIMEB, 0.22*p); ctx.rectangle(x - sz*0.8*pulse, y - sz*0.8*pulse, sz*1.6*pulse, sz*1.6*pulse); ctx.fill()
        ctx.set_source_rgba(*(LIMEB if last else GRAPH), p); ctx.rectangle(x - sz/2, y - sz/2, sz, sz); ctx.fill()
    c = prog(t, 2.5, .5)
    font(ctx, 34, "Mono"); ctx.set_source_rgba(*WHITE, c)
    for j, ln in enumerate(["1 HUMAN STUDY:", "12 PEOPLE, NO CONTROL GROUP"]):
        e = ctx.text_extents(ln); ctx.move_to(W/2 - e.x_advance/2, 1420 + j*50 + 20*(1-c)); ctx.show_text(ln)

def s_cta(ctx, t, d):
    a = prog(t, 0, .4)
    chip(ctx, "THE TAKEAWAY", None, a)
    b = prog(t, .15, .5)
    text_c(ctx, "Promising", 720, 150, WHITE, b, dy=40*(1-b))
    c = prog(t, .6, .5)
    text_c(ctx, "but not proven.", 890, 150, REDB, c, weight="Serif", dy=40*(1-c))
    e2 = prog(t, 1.6, .5)
    font(ctx, 40, "Bold"); s_ = "Follow for science-first breakdowns"; e = ctx.text_extents(s_)
    pw = e.x_advance + 90
    rrect(ctx, W/2 - pw/2, 1060, pw, 110, 55); ctx.set_source_rgba(*RED, e2); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, e2); ctx.move_to(W/2 - e.x_advance/2, 1128); ctx.show_text(s_)
    f = prog(t, 2.0, .5)
    text_c(ctx, "Educational only. Not medical advice.", 1290, 34, MUTED, f, weight="Medium")
    text_c(ctx, "Source: Vasireddi et al., HSS Journal 2025", 1340, 30, DIM, f, weight="Medium")

def s_brand(ctx, t, d):
    a = prog(t, 0, .5)
    s_ = 0.9 + 0.1*a
    ctx.save(); ctx.translate(W/2, 640); ctx.scale(s_, s_); mark(ctx, -110, -110, 220, a=a); ctx.restore()
    b = prog(t, .25, .5)
    wordmark(ctx, W/2, 960 + 20*(1-b), 170, a=b)
    c = prog(t, .5, .4)
    font(ctx, 44, "Mono"); lbl = "MD  ·  @thinkrmd"; e = ctx.text_extents(lbl)
    ctx.set_source_rgba(*MUTED, c); ctx.move_to(W/2 - e.x_advance/2, 1050 + 15*(1-c)); ctx.show_text(lbl)
    p = prog(t, .8, .4)
    font(ctx, 44, "Bold"); lbl = "Save · Share · Follow"; e = ctx.text_extents(lbl)
    pw = e.x_advance + 100
    rrect(ctx, W/2 - pw/2, 1130, pw, 104, 52); ctx.set_source_rgba(*RED, p); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, p); ctx.move_to(W/2 - e.x_advance/2, 1198); ctx.show_text(lbl)
    q = prog(t, 1.2, .5)
    text_c(ctx, "Get your edge back.", 1360, 64, WHITE, q, weight="Serif")

SCENES = [s_hook, s_molecule, s_three, s_vessels, s_receptors, s_migration, s_reality, s_cta, s_brand]

def render(idx, dur, out, still_t=None):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    def frame(t):
        bg(ctx)
        fade = clamp((dur - t) / 0.2) if idx < len(SCENES)-1 else 1
        ctx.push_group()
        SCENES[idx](ctx, t, dur)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(fade)
        progress(ctx, idx, len(SCENES), clamp(t/dur))
    if still_t is not None:
        frame(still_t); surf.write_to_png(out); return
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                          "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    nf = round(dur * FPS)
    for f in range(nf):
        frame(f / FPS); surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    else: sys.exit(f"scene {idx} failed")

if __name__ == "__main__":
    durs = json.load(open(sys.argv[1]))
    mode = sys.argv[2]
    if mode == "stills":
        for i, d in enumerate(durs):
            render(i, d, f"still_{i+1}.png", still_t=d*0.85)
    else:
        i = int(mode); render(i, durs[i], f"scene_{i+1}.mp4")

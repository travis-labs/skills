import cairo, math, sys, json, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_light as B
from base_light import *

IMG = {}
# per scene: (image index or None, scale, dy)
PLAN = {0:(1,0.8,300), 1:(2,1.0,0), 2:(3,1.0,-60), 3:(4,1.0,0), 4:(5,1.0,0), 5:(6,1.0,0), 6:(7,0.7,90), 7:(8,0.6,0), 8:(None,1,0)}

def photo_bg(ctx, idx, t, d):
    ctx.set_source_rgb(*NIGHT); ctx.paint()
    n, sc, dy = PLAN[idx]
    if n is None:
        B.bg(ctx); return
    if n not in IMG: IMG[n] = cairo.ImageSurface.create_from_png(f"bg_{n}.png")
    s = IMG[n]; z = 1 + 0.05 * clamp(t / d)
    k = (1080 / s.get_width()) * sc * z
    ctx.save(); ctx.translate(540, 960 + dy); ctx.scale(k, k); ctx.translate(-s.get_width()/2, -s.get_height()/2)
    p = cairo.SurfacePattern(s); p.set_extend(cairo.EXTEND_PAD); p.set_filter(cairo.FILTER_GOOD)
    ctx.set_source(p); ctx.paint(); ctx.restore()
    g = cairo.LinearGradient(0, 0, 0, 700)
    g.add_color_stop_rgba(0, *NIGHT, 0.75); g.add_color_stop_rgba(1, *NIGHT, 0)
    ctx.set_source(g); ctx.rectangle(0, 0, W, 700); ctx.fill()

def s_hook(ctx, t, d):
    a = prog(t, 0, .4); chip(ctx, "THE SCIENCE", None, a)
    text_c(ctx, "How does", 470, 88, WHITE, a, dy=30*(1-a))
    b = prog(t, .25, .5); font(ctx, 200, "Black"); lbl = "BPC-157"; e = ctx.text_extents(lbl)
    s_ = 0.85 + 0.15*b
    ctx.save(); ctx.translate(W/2, 680); ctx.scale(s_, s_)
    ctx.set_source_rgba(*REDB, b); ctx.move_to(-e.x_advance/2, 0); ctx.show_text(lbl); ctx.restore()
    c = prog(t, .6, .4); text_c(ctx, "actually work?", 810, 88, WHITE, c, dy=30*(1-c))

def headline_scene(label, head, sub, sub2=None, hsize=92):
    def f(ctx, t, d):
        a = prog(t, 0, .4); chip(ctx, label, None, a)
        text_c(ctx, head, 520, hsize, WHITE, a, dy=30*(1-a), maxw=900)
        c = prog(t, 1.0, .5)
        if sub: text_c(ctx, sub, 1440, 48, WHITE, c, weight="Medium", maxw=860, dy=20*(1-c))
        if sub2: text_c(ctx, sub2, 1505 if len(sub) < 40 else 1555, 40, MUTED, c, weight="Medium")
    return f

def s_three(ctx, t, d):
    a = prog(t, 0, .4); chip(ctx, "IN THE LAB", None, a)
    text_c(ctx, "It does 3 things", 520, 96, WHITE, a, dy=30*(1-a))
    items = ["New blood vessels", "Growth hormone response", "Cell migration"]
    for i, it in enumerate(items):
        p = prog(t, .35 + i*0.4, .4)
        y = 1170 + i*118; x = 150 + 40*(1-p)
        ctx.set_source_rgba(1, 1, 1, 0.92*p); ctx.rectangle(x, y, 780, 100); ctx.fill()
        ctx.set_source_rgba(*RED, p); ctx.rectangle(x, y, 10, 100); ctx.fill()
        font(ctx, 38, "Mono"); ctx.set_source_rgba(*REDB, p); ctx.move_to(x + 46, y + 64); ctx.show_text(f"0{i+1}")
        font(ctx, 44, "Bold"); ctx.set_source_rgba(*WHITE, p); ctx.move_to(x + 140, y + 66); ctx.show_text(it)

def s_reality(ctx, t, d):
    a = prog(t, 0, .4)
    font(ctx, 32, "Mono"); lbl = "REALITY CHECK"; e = ctx.text_extents(lbl); x = W/2 - (e.x_advance + 36)/2
    ctx.set_source_rgba(*RED, a); ctx.rectangle(x, 318, 20, 20); ctx.fill()
    ctx.set_source_rgba(*REDB, a); ctx.move_to(x + 36, 338); ctx.show_text(lbl)
    text_c(ctx, "35 of 36 studies were in animals or cells", 470, 80, WHITE, a, dy=30*(1-a), maxw=900)
    c = prog(t, 2.0, .5); font(ctx, 34, "Mono"); ctx.set_source_rgba(*WHITE, c)
    for j, ln in enumerate(["THE 1 HUMAN STUDY:", "12 PEOPLE, NO CONTROL GROUP"]):
        e = ctx.text_extents(ln); ctx.move_to(W/2 - e.x_advance/2, 1440 + j*50 + 20*(1-c)); ctx.show_text(ln)

def s_cta(ctx, t, d):
    a = prog(t, 0, .4); chip(ctx, "THE TAKEAWAY", None, a)
    b = prog(t, .15, .5); text_c(ctx, "Promising", 500, 140, WHITE, b, dy=40*(1-b))
    c = prog(t, .6, .5); text_c(ctx, "but not proven.", 650, 130, REDB, c, weight="Serif", dy=40*(1-c))
    e2 = prog(t, 1.6, .5)
    font(ctx, 40, "Bold"); s_ = "Follow for science-first breakdowns"; e = ctx.text_extents(s_); pw = e.x_advance + 90
    rrect(ctx, W/2 - pw/2, 1350, pw, 100, 50); ctx.set_source_rgba(*RED, e2); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, e2); ctx.move_to(W/2 - e.x_advance/2, 1413); ctx.show_text(s_)
    f = prog(t, 2.0, .5)
    text_c(ctx, "Educational only. Not medical advice.", 1500, 32, MUTED, f, weight="Medium")
    text_c(ctx, "Source: Vasireddi et al., HSS Journal 2025", 1545, 28, DIM, f, weight="Medium")

SCENES = [s_hook,
  headline_scene("THE MOLECULE", "15 amino acids", "Modeled on a protective protein found in gastric juice", hsize=96),
  s_three,
  headline_scene("MECHANISM 01", "Grows new blood vessels", "via VEGFR2 + nitric oxide signaling", "(Akt–eNOS pathway)"),
  headline_scene("MECHANISM 02", "Primes tendon cells", "More growth hormone receptors = a louder repair signal"),
  headline_scene("MECHANISM 03", "Moves repair cells in", "via the FAK–paxillin pathway", hsize=86),
  s_reality, s_cta, B.s_brand]

def render(idx, dur, out, still_t=None):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    def frame(t):
        photo_bg(ctx, idx, t, dur)
        fade = clamp((dur - t) / 0.2) if idx < len(SCENES)-1 else 1
        ctx.push_group(); SCENES[idx](ctx, t, dur); ctx.pop_group_to_source(); ctx.paint_with_alpha(fade)
        B.progress(ctx, idx, len(SCENES), clamp(t/dur))
        if fade < 1:
            ctx.set_source_rgba(*NIGHT, (1-fade)*0.6); ctx.paint()
    if still_t is not None:
        frame(still_t); surf.write_to_png(out); return
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgra","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),tmp], stdin=subprocess.PIPE)
    for f in range(round(dur*FPS)):
        frame(f/FPS); surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    else: sys.exit(f"scene {idx} failed")

if __name__ == "__main__":
    durs = json.load(open(sys.argv[1])); mode = sys.argv[2]
    if mode == "stills":
        for i, d in enumerate(durs): render(i, d, f"pst_{i+1}.png", still_t=d*0.8)
    else:
        i = int(mode); render(i, durs[i], f"pscene_{i+1}.mp4")

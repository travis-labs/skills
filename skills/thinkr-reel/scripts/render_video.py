import cairo, sys, json, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_photo as P
from base_light import *
import base_light as B

def render(idx, dur, out):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    n, sc, dy = P.PLAN[idx]
    reader = None
    if n is not None:
        reader = subprocess.Popen(["ffmpeg","-loglevel","error","-i",f"clip_{n}.mp4","-vf",f"fps={FPS},scale={W}:{H}:flags=lanczos",
                                   "-f","rawvideo","-pix_fmt","bgra","-"], stdout=subprocess.PIPE)
    last = None
    tmp = out.replace(".mp4", ".tmp.mp4")
    enc = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgra","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),tmp], stdin=subprocess.PIPE)
    for f in range(round(dur*FPS)):
        t = f / FPS
        ctx.set_source_rgb(*NIGHT); ctx.paint()
        if reader:
            buf = reader.stdout.read(W*H*4)
            if len(buf) == W*H*4: last = bytearray(buf)
            fs = cairo.ImageSurface.create_for_data(last, cairo.FORMAT_ARGB32, W, H, W*4)
            ctx.save(); ctx.translate(540, 960 + dy); ctx.scale(sc, sc); ctx.translate(-W/2, -H/2)
            p = cairo.SurfacePattern(fs); p.set_extend(cairo.EXTEND_PAD); p.set_filter(cairo.FILTER_GOOD)
            ctx.set_source(p); ctx.paint(); ctx.restore()
            g = cairo.LinearGradient(0, 0, 0, 700)
            g.add_color_stop_rgba(0, *NIGHT, 0.75); g.add_color_stop_rgba(1, *NIGHT, 0)
            ctx.set_source(g); ctx.rectangle(0, 0, W, 700); ctx.fill()
            g2 = cairo.LinearGradient(0, 1300, 0, 1620)
            g2.add_color_stop_rgba(0, *NIGHT, 0); g2.add_color_stop_rgba(0.45, *NIGHT, 0.8); g2.add_color_stop_rgba(1, *NIGHT, 0.8)
            ctx.set_source(g2); ctx.rectangle(0, 1300, W, 620); ctx.fill()
        else:
            B.bg(ctx)
        fade = clamp((dur - t) / 0.2) if idx < len(P.SCENES)-1 else 1
        ctx.push_group(); P.SCENES[idx](ctx, t, dur); ctx.pop_group_to_source(); ctx.paint_with_alpha(fade)
        B.progress(ctx, idx, len(P.SCENES), clamp(t/dur))
        if fade < 1: ctx.set_source_rgba(*NIGHT, (1-fade)*0.6); ctx.paint()
        surf.flush(); enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close()
    if reader: reader.stdout.close(); reader.wait()
    if enc.wait() == 0: os.replace(tmp, out)
    else: sys.exit(f"scene {idx} failed")

if __name__ == "__main__":
    durs = json.load(open(sys.argv[1])); i = int(sys.argv[2]); render(i, durs[i], f"vscene_{i+1}.mp4")

import sys, os, math, subprocess, wave
sys.path.insert(0, '/home/claude/shorts')
import drumlib as D
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W, H, FPS = 1920, 1080, 30
BOLD = D.BOLD

def seg(estilo, bpm, relleno, tema_n, nivel, bars, salida, fotograma=None, musica=False, tono=0, drums_gain=0.85, pd=None, sub='Toca junto con el video'):
    tema = D.TEMAS[tema_n]
    bar_dur = 4 * 60.0 / bpm
    ev, step = D.build_events(estilo, bpm, relleno, bars)
    total = bars * bar_dur
    wav = salida + '.wav'; D.audio(ev, total, wav)
    if musica:
        import cancion
        cancion.agregar_musica(wav, ev, bpm, bars, D.RELLENOS[relleno]['inicio'] if relleno != 'ninguno' else None, tono, drums_gain=drums_gain, pd=pd)
    usadas = [v for v in D.ORDER if any(e[1] == v for e in ev)]
    col = {v: tema['cols'][D.ORDER.index(v)] for v in D.ORDER}
    f_xs = ImageFont.truetype(BOLD, 30); f_sm = ImageFont.truetype(BOLD, 38)
    f_t = ImageFont.truetype(BOLD, 76); f_b = ImageFont.truetype(BOLD, 120)
    titulo = D.ESTILOS_TODOS[estilo]['nombre']
    bg = D.fondo(tema).resize((W, H))
    labels16 = ["1","e","y","e","2","e","y","e","3","e","y","e","4","e","y","e"]
    nrows = len(usadas); evs = sorted(ev)
    tx0, tx1 = 260, 1860; tc = (tx1 - tx0) / 16
    nfr = int(round(total * FPS))
    p = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),
        '-i','-','-c:v','libx264','-preset','veryfast','-crf','26','-pix_fmt','yuv420p','-r',str(FPS),'-g','30','-t',f'{total:.3f}',
        '-an',salida], stdin=subprocess.PIPE)
    rl = D.RELLENOS[relleno]
    bh = min(90, 280 / nrows)
    frames = [fotograma] if fotograma is not None else range(nfr)
    for k in frames:
        t = k / FPS; gs = int(t / step); b = gs // 16; fase = (t % step) / step
        fr = bg.copy(); d = ImageDraw.Draw(fr)
        d.text((60, 30), f"BATERÍA  ·  NIVEL {nivel}", font=f_sm, fill=tema['acc'])
        d.text((60, 85), titulo, font=f_t, fill=tema['txt'])
        bw = d.textlength(f"{bpm} BPM", font=f_b)
        d.text((W - 60 - bw, 40), f"{bpm} BPM", font=f_b, fill=tema['acc'])
        d.text((60, 175), sub, font=f_sm, fill=tema['mut'])
        par = (b // 2) * 2
        for k2 in range(2):
            bb = par + k2
            if bb >= bars: continue
            y0 = 300 + k2 * (bh * nrows + 150)
            y1 = y0 + bh * nrows
            d.rounded_rectangle([30, y0 - 70, W - 30, y1 + 16], radius=20, fill=tema['lane'])
            d.text((50, y0 - 56), f"Comp. {bb + 1}", font=f_xs, fill=tema['mut'])
            if relleno != 'ninguno' and bb % 4 == 3:
                d.rectangle([tx0 + tc * rl['inicio'], y0 - 6, tx1, y1], outline=tema['txt'], width=4)
            for s_ in range(17):
                x = tx0 + tc * s_
                d.line([x, y0 - 6, x, y1], fill=tema['mut'] if s_ % 4 == 0 else tema['bot'], width=4 if s_ % 4 == 0 else 2)
            for s_ in range(16):
                cx = tx0 + tc * s_ + tc / 2; big = s_ % 4 == 0
                fo = f_sm if big else f_xs
                lw = d.textlength(labels16[s_], font=fo)
                d.text((cx - lw / 2, y0 - 56 + (0 if big else 5)), labels16[s_], font=fo, fill=tema['txt'] if big else tema['mut'])
            for r, v in enumerate(usadas):
                y = y0 + r * bh + bh / 2
                d.text((50, y - 16), D.NOMBRE[v] if len(D.NOMBRE[v]) < 11 else 'Hi-hat ab.', font=f_xs, fill=col[v])
                d.line([tx0, y, tx1, y], fill=tema['bot'], width=3)
            for (te, v, g, i, b2, mano) in evs:
                if b2 != bb: continue
                y = y0 + usadas.index(v) * bh + bh / 2; cx = tx0 + tc * i + tc / 2
                rad = min(14 if v in ('hat', 'ride') else 20, bh * 0.4); ab = bb * 16 + i
                if ab == gs:
                    rad += int(14 * (1 - fase)); d.ellipse([cx-rad, y-rad, cx+rad, y+rad], fill=tema['txt'])
                    rad -= 5; d.ellipse([cx-rad, y-rad, cx+rad, y+rad], fill=col[v])
                elif ab < gs: d.ellipse([cx-rad, y-rad, cx+rad, y+rad], fill=col[v])
                else: d.ellipse([cx-rad, y-rad, cx+rad, y+rad], outline=col[v], width=3)
                if mano:
                    mw = d.textlength(mano, font=f_xs); d.text((cx - mw / 2, y + 14), mano, font=f_xs, fill=tema['txt'])
        d.text((60, 1035), D.WATERMARK, font=f_xs, fill=tema['mut'])
        if fotograma is not None:
            fr.save(salida + '.png'); p.stdin.close(); p.terminate(); return
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    return total, wav

if __name__ == '__main__':
    seg('rock_basico', 60, 'ninguno', 'noche', 1, 8, '/tmp/prueba_largo.mp4', fotograma=int(5.2*FPS))

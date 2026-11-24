"""Largo play along IA v2: agrega tablatura de ejemplo (solo visual) con cursor sincronizado a los tiempos detectados."""
import sys, os, json, subprocess, numpy as np, librosa
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import drumlib as D
W, H, FPS = 1920, 1080, 15
OUT = '/home/claude/shorts/largos_ia'
info = json.load(open(f'{OUT}/info.json')); inicio = info['inicio']; dur = [d for _, d in info['pistas']]; total = info['duracion']
T = D.TEMAS['noche']; F = lambda s: ImageFont.truetype(D.BOLD, s)
RB = dict(hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-------x-------")
RX = dict(hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-----x-x-------")
FILL = dict(hat="x-x-x-x-x-x-----", snare="----x-------xxxx", kick="x-------x-------")
PISTAS = [('Do mayor', 'Nivel base: bombo en 1 y 3, caja en 2 y 4, hi-hat en corcheas', [('Ritmo (repítelo en cada compás)', RB)]),
          ('Sol mayor', 'Sube un paso: agrega un bombo extra en el "y" del 3', [('Ritmo con bombo extra (repítelo)', RX)]),
          ('Re mayor', 'Libre: cierra cada 4 compases con un relleno corto', [('Compases 1 a 3', RB), ('Compás 4: relleno de caja', FILL)])]
LAN = [('hat', 'Hi-hat', T['cols'][2]), ('snare', 'Caja', T['cols'][7]), ('kick', 'Bombo', T['cols'][8])]
LAB = ["1", "e", "y", "a", "2", "e", "y", "a", "3", "e", "y", "a", "4", "e", "y", "a"]
GX0, GX1 = 330, 1830; CELL = (GX1-GX0)/16
def grad():
    a = np.linspace(0, 1, H)[:, None, None]; return Image.fromarray((np.repeat(np.array(T['top'])*(1-a)+np.array(T['bot'])*a, W, 1)).astype(np.uint8))
def centrado(d, y, txt, font, fill):
    w = d.textlength(txt, font=font); d.text(((W-w)/2, y), txt, font=font, fill=fill)
# fase del compas: en que tiempo (mod 4) cambia mas el acorde
fase, beats = [], []
for i in range(3):
    y, sr = librosa.load(f'/tmp/pa{i+1}_con_bateria.mp3', sr=22050); _, b = librosa.beat.beat_track(y=y, sr=sr)
    beats.append(librosa.frames_to_time(b, sr=sr))
    ys, _ = librosa.load(f'/tmp/pa{i+1}.mp3', sr=22050)
    ch = librosa.feature.chroma_cens(y=ys, sr=sr); sync = librosa.util.sync(ch, b, aggregate=np.median)
    d_ = np.linalg.norm(np.diff(sync, axis=1), axis=0)  # cambio entre tiempo k y k+1
    sc = [d_[(j-1)::4].sum() if j > 0 else d_[3::4].sum() for j in range(4)]
    fase.append(int(np.argmax([d_[k::4].sum() for k in range(4)])) + 1)
    print('pista', i+1, 'fase', fase[-1], np.round([d_[k::4].sum() for k in range(4)], 1))
def base(k):
    nom, tip, paneles = PISTAS[k]
    im = grad(); d = ImageDraw.Draw(im)
    centrado(d, 40, 'PLAY ALONG DE BATERÍA', F(70), T['txt'])
    centrado(d, 130, 'Toca tú encima  ·  Sin batería en la música', F(36), T['mut'])
    centrado(d, 195, f'Pieza {k+1} de 3  ·  {nom}  ·  100 BPM', F(48), T['acc'])
    n = len(paneles); ph = 190 if n == 2 else 240; y0 = 290
    pos = []
    for pi, (tit, pat) in enumerate(paneles):
        py = y0 + pi*(ph+55)
        d.text((GX0, py-6), tit, font=F(34), fill=T['txt'])
        ty = py + 78; rh = (ph-80)/3
        for s in range(16):
            cx = GX0 + CELL*s + CELL/2; w = d.textlength(LAB[s], font=F(30))
            d.text((cx-w/2, py+36), LAB[s], font=F(30), fill=T['txt'] if s % 4 == 0 else T['mut'])
        d.rounded_rectangle([GX0-6, ty-10, GX1+6, ty+rh*3+6], 14, fill=T['lane'])
        for r, (v, nombre, col) in enumerate(LAN):
            yy = ty + r*rh + rh/2
            d.text((60, yy-20), nombre, font=F(34), fill=col)
            d.line([GX0, yy, GX1, yy], fill=(51, 65, 85), width=2)
            for s in range(16):
                if pat[v][s] == 'x':
                    cx = GX0 + CELL*s + CELL/2; rad = 14 if v == 'hat' else 20
                    d.ellipse([cx-rad, yy-rad, cx+rad, yy+rad], fill=col)
        pos.append((ty-10, ty+rh*3+6))
    d.text((60, 1020), D.WATERMARK, font=F(30), fill=T['mut'])
    centrado(d, 910, tip, F(42), T['txt'])
    return im, pos
escenas = [base(k) for k in range(3)]
def tarjeta(i):
    im = grad(); d = ImageDraw.Draw(im)
    centrado(d, 40, 'PLAY ALONG DE BATERÍA', F(70), T['txt']); centrado(d, 130, 'Toca tú encima  ·  Sin batería en la música', F(36), T['mut'])
    centrado(d, 360, f'Pieza {i+1} de 3', F(110), T['acc']); centrado(d, 520, f'{PISTAS[i][0]}  ·  100 BPM', F(70), T['txt'])
    centrado(d, 650, 'Prepárate: empieza en unos segundos', F(44), T['mut']); d.text((60, 1020), D.WATERMARK, font=F(30), fill=T['mut']); return im
tarj = [tarjeta(i) for i in range(3)]
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', f'{OUT}/audio.wav',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{OUT}/largo_ia_03.mp4']
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for n in range(int(total*FPS)):
    t = n/FPS; k = None
    for i in range(3):
        if inicio[i] <= t < inicio[i]+dur[i]: k = i
    if k is None:
        nxt = next((i for i in range(3) if t < inicio[i]), 2); im = tarj[nxt].copy()
    else:
        im0, pos = escenas[k]; im = im0.copy(); d = ImageDraw.Draw(im); tl = t - inicio[k]
        b = beats[k]; j = int(np.searchsorted(b, tl, side='right') - 1)
        if j >= 0 and j+1 < len(b):
            f = (tl - b[j]) / (b[j+1]-b[j]); bib = (j - (fase[k]-1)) % 4; step = min(15, bib*4 + int(f*4)); barno = ((j - (fase[k]-1)) // 4)
            since = tl - b[j]; e = np.exp(-since/0.14)
            panel = 0 if len(pos) == 1 else (1 if barno % 4 == 3 else 0)
            for pi, (ya, yb) in enumerate(pos):
                if pi == panel:
                    x = GX0 + CELL*step; d.rounded_rectangle([x+3, ya, x+CELL-3, yb], 10, outline=T['txt'], width=3)
            r = int(30 + 18*e); col = tuple(int(c*(0.45+0.55*e)) for c in T['acc']); d.ellipse([1760-r, 215-r, 1760+r, 215+r], fill=col)
        pr_ = tl/dur[k]; d.rounded_rectangle([360, 975, 1560, 987], 6, fill=T['lane']); d.rounded_rectangle([360, 975, 360+int(1200*pr_), 987], 6, fill=T['acc'])
        m, s = int(tl//60), int(tl % 60); centrado(d, 995, f'{m}:{s:02d} / {int(dur[k]//60)}:{int(dur[k] % 60):02d}', F(28), T['mut'])
    pr.stdin.write(im.tobytes())
pr.stdin.close(); pr.wait(); print('ok')

import sys, os, math, wave, subprocess, json
sys.path.insert(0, '/home/claude/shorts')
import largo as L, drumlib as D
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

def job(a):
    est, bpm, rel, tema, niv, i, mus, tono, dg, pd, sub, bars = a
    f = f'/home/claude/shorts/tmp_largo/s{i}.mp4'
    tot, wav = L.seg(est, bpm, rel, tema, niv, bars, f, musica=mus, tono=tono, drums_gain=dg, pd=pd, sub=sub)
    return i, f, wav, tot

def concat_wavs(paths, out):
    w0 = wave.open(paths[0]); par = w0.getparams(); w0.close()
    o = wave.open(out, 'wb'); o.setparams(par)
    for p in paths:
        w = wave.open(p); o.writeframes(w.readframes(w.getnframes())); w.close()
    o.close()

def construir(nombre, estilo, bpms, relleno, tema, nivel, seg_seg=120, musica=True, tono=0, drums_gain=0.85, pd=None, sub='Toca junto con el video', bars=8):
    args = [(estilo, b, relleno, tema, nivel, i, musica, tono, drums_gain, pd, sub, bars) for i, b in enumerate(bpms)]
    with Pool(2) as p: res = sorted(p.map(job, args))
    lista, wavs, caps, t = [], [], [], 0.0
    for (i, f, wav, tot), b in zip(res, bpms):
        reps = max(1, round(seg_seg / tot))
        caps.append((t, b, reps * tot))
        for _ in range(reps): lista.append(f); wavs.append(wav)
        t += reps * tot
    open('/home/claude/shorts/tmp_largo/lista.txt', 'w').write(''.join(f"file '{f}'\n" for f in lista))
    concat_wavs(wavs, '/home/claude/shorts/tmp_largo/audio.wav')
    out = f'/home/claude/shorts/largos/{nombre}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', '/home/claude/shorts/tmp_largo/lista.txt',
        '-i', '/home/claude/shorts/tmp_largo/audio.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], check=True)
    return out, caps, t

def miniatura(nombre, titulo, sub, tema_n):
    tema = D.TEMAS[tema_n]
    im = D.fondo(tema).resize((1280, 720)); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(D.BOLD, 120); f2 = ImageFont.truetype(D.BOLD, 62)
    y = 90
    for ln in titulo.split('\n'):
        d.text((70, y), ln, font=f1, fill=tema['txt']); y += 135
    d.text((70, y + 25), sub, font=f2, fill=tema['acc'])
    d.text((70, 650), D.WATERMARK, font=ImageFont.truetype(D.BOLD, 34), fill=tema['mut'])
    im.save(f'/home/claude/shorts/largos/{nombre}.png')

if __name__ == '__main__':
    nombre = 'largo01_cancion_rock_basico_60_a_80bpm'
    out, caps, t = construir(nombre, 'rock_basico', [60, 65, 70, 75, 80], 'redoble_1', 'noche', 1)
    miniatura(nombre, 'TOCA BATERÍA\nCON ESTA CANCIÓN', '60 a 80 BPM  ·  Nivel 1', 'noche')
    json.dump(dict(archivo=out, duracion=t, capitulos=caps), open(f'/home/claude/shorts/largos/{nombre}.json', 'w'))
    print(out, t, caps)

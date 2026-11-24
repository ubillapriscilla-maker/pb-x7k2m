"""PDF gratis: 20 ritmos de batería con tablatura (gancho para el canal).
Uso: python3 pdf_tablaturas.py salida.pdf"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drumlib as D
from partitura import partitura
import tempfile

W, H = 1240, 1754           # A4 a 150 dpi
M = 90
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F = lambda s, b=True: ImageFont.truetype(B if b else R, s)
T = D.TEMAS['papel']
TXT, MUT, ACC, LANE = T['txt'], T['mut'], T['acc'], T['lane']
CANAL = 'youtube.com/@priscillaubillasoriano'
NIVEL = {1: 'Fácil', 2: 'Básico', 3: 'Intermedio', 4: 'Avanzado', 5: 'Experto'}
NOM = dict(D.NOMBRE)
LAB = ["1", "e", "y", "a", "2", "e", "y", "a", "3", "e", "y", "a", "4", "e", "y", "a"]
CONSEJO = {
    'rock_basico': 'La base de casi todo el rock y el pop. Cuenta en voz alta 1 y 2 y 3 y 4.',
    'rock_bombo_extra': 'El bombo extra va justo antes del 3. Tócalo suave al principio.',
    'ride_rock': 'Mismo ritmo de rock, pero en el ride: suena más abierto, ideal para coros.',
    'pop_4_al_piso': 'Bombo en los cuatro tiempos, parejo. Muy usado en pop y música bailable.',
    'disco': 'Hi-hat cerrado en el tiempo y abierto en el "y". Abre y cierra con el pie.',
    'hiphop_boom_bap': 'Relajado y un poco atrás del tiempo. No lo apures.',
    'reggae_one_drop': 'Caja y bombo juntos solo en el 3. El silencio en el 1 es parte del ritmo.',
    'medio_tiempo': 'La caja va solo en el 3: suena el doble de lento sin cambiar el pulso.',
    'rock_16avos': 'Hi-hat con una mano a 16avos: empieza muy lento y relaja la muñeca.',
    'funk_16avos': 'Hi-hat a 16avos y bombo sincopado. Pide mucha independencia: paciencia.',
    'punk': 'Rápido y parejo. Primero domínalo lento, la velocidad llega sola.',
    'metal_doble_bombo': 'Bombo en todos los 16avos: alterna los pies (o pedal doble) muy parejo.',
    'bombo_y_caja': 'Solo pies y caja, sin platillos. Ideal para tu primera semana.',
    'hat_negras': 'Hi-hat en los cuatro tiempos. Perfecto para coordinar manos y pie.',
    'rock_sincopado': 'El bombo cae en el "y": escucha cómo cambia la sensación del ritmo.',
    'funk_sincopado': 'Bombo fuera del tiempo y caja firme en 2 y 4. Mantén el hi-hat parejo.',
    'doble_bombo_corto': 'Dos golpes de bombo seguidos. Practícalos solos antes de juntarlos.',
    'metal_galope': 'El galope: un golpe largo y dos cortos en el bombo. Muy de heavy metal.',
    'funk_abierto': 'El hi-hat abierto da el color. Ciérralo justo en el tiempo siguiente.',
    'blast_beat': 'Caja y bombo alternados muy rápido. Solo para cuando ya tengas buen control.',
}


def fondo():
    im = Image.new('RGB', (W, H), T['top']); return im, ImageDraw.Draw(im)


def pie(d, n):
    d.line([M, H - 110, W - M, H - 110], fill=LANE, width=2)
    d.text((M, H - 90), f'Más ritmos y videos para tocar encima: {CANAL}', font=F(24, False), fill=MUT)
    d.text((W - M - 40, H - 90), str(n), font=F(24), fill=MUT)


def tab(d, x0, y0, w, hits):
    voces = [v for v in D.ORDER if v in hits and 'x' in hits[v]]
    lw = 210; gx0, gx1 = x0 + lw, x0 + w; cell = (gx1 - gx0) / 16; rh = 58
    for s in range(16):
        cx = gx0 + cell * s + cell / 2; tw = d.textlength(LAB[s], font=F(26))
        d.text((cx - tw / 2, y0), LAB[s], font=F(26), fill=TXT if s % 4 == 0 else MUT)
    ty = y0 + 46
    d.rounded_rectangle([gx0 - 6, ty - 6, gx1 + 6, ty + rh * len(voces) + 6], 12, fill=LANE)
    for b in range(1, 4):
        xb = gx0 + cell * 4 * b; d.line([xb, ty, xb, ty + rh * len(voces)], fill=(190, 178, 158), width=3)
    for r, v in enumerate(voces):
        yy = ty + r * rh + rh / 2; col = T['cols'][D.ORDER.index(v)]
        d.text((x0, yy - 16), NOM[v], font=F(28), fill=col)
        d.line([gx0, yy, gx1, yy], fill=(196, 186, 168), width=2)
        for s in range(16):
            if hits[v][s] == 'x':
                cx = gx0 + cell * s + cell / 2; rad = 15 if v in ('hat', 'ride', 'ohat') else 20
                d.ellipse([cx - rad, yy - rad, cx + rad, yy + rad], fill=col)
    return ty + rh * len(voces) + 10


def score(d, im, x0, y0, hits, alto=None, ancho=560, maxalto=150):
    from PIL import ImageChops
    f = tempfile.mktemp(suffix='.png'); partitura(hits, f)
    s = Image.open(f).convert('RGB'); k = min(ancho / s.width, maxalto / s.height)
    s = s.resize((int(s.width * k), int(s.height * k)), Image.LANCZOS)
    s = ImageChops.multiply(s, Image.new('RGB', s.size, T['top']))
    im.paste(s, (x0 + 210, y0))
    d.text((x0, y0 + s.height // 2 - 16), 'Partitura', font=F(28), fill=MUT)
    return y0 + s.height


def portada(n):
    im, d = fondo()
    d.text((M, 260), 'BATERÍA DESDE CERO', font=F(44), fill=ACC)
    d.text((M, 330), '20 ritmos con', font=F(96), fill=TXT)
    d.text((M, 440), 'tablatura', font=F(96), fill=TXT)
    d.text((M, 600), 'Del más fácil al más exigente, con el BPM para empezar', font=F(32, False), fill=MUT)
    d.text((M, 645), 'y un consejo para cada uno.', font=F(32, False), fill=MUT)
    y = 820
    for t in ['Cómo usar esta guía:', '1. Lee la página "Cómo leer la tablatura".',
              '2. Toca cada ritmo lento, con metrónomo, hasta que salga limpio.',
              '3. Sube 5 BPM y repite.',
              '4. Practícalo con los videos del canal, que tienen la misma tablatura.']:
        d.text((M, y), t, font=F(32, t.endswith(':')), fill=TXT); y += 58
    d.text((M, 1300), 'Priscilla Ubilla Drummer', font=F(40), fill=TXT)
    d.text((M, 1360), CANAL, font=F(32, False), fill=ACC)
    d.text((M, 1440), 'Guía gratuita. Puedes compartirla, pero no venderla.', font=F(24, False), fill=MUT)
    pie(d, n); return im


def como_leer(n):
    im, d = fondo()
    d.text((M, 140), 'Cómo leer la tablatura', font=F(60), fill=TXT)
    y = 260
    for t in ['Cada fila es una parte de la batería: hi-hat, caja, bombo, etc.',
              'Cada columna es un momento del compás. Se cuenta así:',
              '"1 e y e  2 e y e  3 e y e  4 e y e" (16 espacios en un compás).',
              'Un círculo significa: golpea esa parte en ese momento.',
              'Si hay dos círculos en la misma columna, se tocan juntos.']:
        d.text((M, y), t, font=F(29, False), fill=TXT); y += 48
    d.text((M, y + 20), 'Ejemplo: rock básico', font=F(36), fill=ACC)
    ys = score(d, im, M, y + 70, D.ESTILOS['rock_basico']['hits'], maxalto=140)
    yb = tab(d, M, ys + 20, W - 2 * M, D.ESTILOS['rock_basico']['hits'])
    y = yb + 40
    for t in ['Hi-hat en todos los "1, y, 2, y...": ocho golpes por compás (corcheas).',
              'Caja en el 2 y en el 4.', 'Bombo en el 1 y en el 3.',
              'Empieza a 60 BPM. Cuando te salga 4 veces seguidas sin error, sube a 65.']:
        d.text((M, y), '- ' + t, font=F(28, False), fill=TXT); y += 46
    d.text((M, y + 15), 'Cómo leer la partitura', font=F(36), fill=ACC); y += 75
    for t in ['La cruz arriba es el hi-hat (con una "o" encima: hi-hat abierto).',
              'La nota en el centro del pentagrama es la caja; la de abajo, el bombo.',
              'Plicas hacia arriba: manos. Plicas hacia abajo: pie.',
              'Negra = 1 tiempo. Corchea (una barra) = medio tiempo.',
              'Semicorchea (dos barras) = un cuarto de tiempo.', 'El símbolo en zigzag es un silencio: ahí no se toca.']:
        d.text((M, y), '- ' + t, font=F(27, False), fill=TXT); y += 44
    pie(d, n); return im


def paginas():
    est = sorted([k for k in D.ESTILOS if '__' not in k], key=lambda k: (D.ESTILOS[k]['nivel'], list(D.ESTILOS).index(k)))
    pags = [portada(1), como_leer(2)]
    for i in range(0, len(est), 2):
        im, d = fondo(); y = 90
        for k in est[i:i + 2]:
            st = D.ESTILOS[k]; num = est.index(k) + 1
            d.text((M, y), f'{num:02d}', font=F(64), fill=ACC)
            d.text((M + 110, y + 4), st['nombre'], font=F(46), fill=TXT)
            lo = max(60, st['bpm'][0])
            d.text((M + 110, y + 66), f"Nivel {NIVEL[st['nivel']].lower()}  ·  empieza a {lo} BPM", font=F(28, False), fill=MUT)
            ys = score(d, im, M, y + 115, st['hits'])
            yb = tab(d, M, ys + 10, W - 2 * M, st['hits'])
            d.text((M, yb + 15), CONSEJO.get(k, ''), font=F(28, False), fill=TXT)
            y = yb + 110
        pie(d, len(pags) + 1); pags.append(im)
    return pags


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'tablaturas.pdf'
    p = paginas()
    p[0].save(out, save_all=True, append_images=p[1:], resolution=150)
    print(out, len(p), 'paginas')

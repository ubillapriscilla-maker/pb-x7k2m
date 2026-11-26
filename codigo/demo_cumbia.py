"""Cumbia v2: cada instrumento según fuentes (ver plan/estudio_latinos.md)."""
import sys, wave, numpy as np
sys.path.insert(0, '/home/claude/pb-x7k2m/codigo')
import banda as B, bateria as BT
SR = 44100
bpm = 96; step = 60 / bpm / 4; N = 16
P = {'bombo': 36, 'aro': 37, 'hh': 42, 'guiro_c': 73, 'guiro_l': 74, 'conga_mute': 62, 'conga_ab': 63,
     'tumba': 64, 'timb_a': 65, 'timb_b': 66, 'crash': 49}
# progresión típica de dos o tres acordes: i y V7 (con iv), en La menor
PROG = [(57, 'm'), (57, 'm'), (52, '7'), (52, '7'), (57, 'm'), (50, 'm'), (52, '7'), (57, 'm')]
# melodía escrita a mano (escala menor armónica, frases de 2 compases pregunta-respuesta): (paso, nota, duración)
MEL = [[(0, 76, 2), (2, 76, 2), (4, 74, 2), (6, 72, 2), (8, 71, 2), (10, 72, 2), (12, 69, 4)],
       [(4, 69, 2), (6, 71, 2), (8, 72, 2), (10, 74, 2), (12, 76, 4)],
       [(0, 74, 2), (2, 74, 2), (4, 72, 2), (6, 71, 2), (8, 68, 2), (10, 69, 2), (12, 71, 4)],
       [(4, 64, 2), (6, 68, 2), (8, 71, 2), (10, 74, 2), (12, 76, 4)],
       [(0, 76, 2), (2, 76, 2), (4, 74, 2), (6, 72, 2), (8, 71, 2), (10, 72, 2), (12, 69, 2), (14, 72, 2)],
       [(0, 74, 4), (4, 77, 2), (6, 76, 2), (8, 74, 2), (10, 72, 2), (12, 74, 4)],
       [(0, 71, 2), (2, 72, 2), (4, 74, 2), (6, 72, 2), (8, 71, 2), (10, 68, 2), (12, 71, 4)],
       [(0, 69, 8)]]
rng = np.random.default_rng(9)

def g(s): return [i for i, c in enumerate(s.replace(' ', '')) if c != '-']

# ---------------- percusión y batería
capas = {
    'guiro_l': ('x--- x--- x--- x---', 85),   # güiro: raspado largo en el tiempo...
    'guiro_c': ('--xx --xx --xx --xx', 72),   # ...y dos cortos ("chaaa-chi-ki")
    'conga_mute': ('x--- ---- x--- ----', 80),  # conga: palma, abierto, palma, abierto
    'conga_ab': ('---- x--- ---- x---', 95),
    'tumba': ('---- --x- ---- --x-', 90),     # conga grave en el contratiempo (el "llamador")
    'bombo': ('x--- ---- x--- ----', 100),    # bombo en 1 y 3
    'aro': ('---- x--- ---- x---', 92),       # aro en 2 y 4
    'hh': ('--x- --x- --x- --x-', 60),        # hi-hat suave en el contratiempo
}
notas = []
for b in range(N):
    for voz, (pat, vel) in capas.items():
        for s in g(pat):
            t = (b * 16 + s) * step + rng.normal(0, 0.004)
            notas.append((max(0, t), P[voz], int(np.clip(vel + rng.normal(0, 6), 30, 127)), voz))
    if b % 4 == 3:  # remate de timbal al cerrar cada frase de 4 compases
        for s, v in ((12, 'timb_a'), (13, 'timb_a'), (14, 'timb_b'), (15, 'timb_b')):
            notas.append(((b * 16 + s) * step, P[v], 100, v))
    if b % 4 == 0 and b > 0:
        notas.append((b * 16 * step, P['crash'], 95, 'crash'))
notas.append((N * 16 * step, P['bombo'], 110, 'bombo')); notas.append((N * 16 * step, P['crash'], 110, 'crash'))
dr = BT.procesar(BT._fluid(notas, 8), 'funk')

# ---------------- banda
L = {k: [] for k in ('gtr', 'gtr_dist', 'bajo', 'teclas', 'pad', 'lead', 'extra')}
def nota(pista, kind, b, s, m, d, v):
    L[pista].append(((b * 16 + s) * step + rng.normal(0, 0.004), m, d * step, v, kind))
for b in range(N):
    raiz, tipo = PROG[b % 8]
    ac = B.notas_acorde(raiz, tipo)
    r = 33 + (raiz - 33) % 12  # tónica en el registro del bajo
    # bajo: "negra y dos corcheas" con tónica, quinta y octava (dos veces por compás), notas cortas (staccato)
    for s, iv, d in ((0, 0, 3), (4, 7, 1.6), (6, 12, 1.6), (8, 0, 3), (12, 7, 1.6), (14, 12, 1.6)):
        nota('bajo', 'bajo', b, s, r + iv, d, 0.95 if s in (0, 8) else 0.8)
    # piano "base": acordes cortos en el contratiempo (segunda corchea de cada tiempo), registro Do4-Fa5
    v = B.voicear(ac, None, 60, 77)
    for s in (2, 6, 10, 14):
        for m in v:
            nota('teclas', 'piano', b, s, m, 1.2, 0.8)
    # guitarra eléctrica limpia: también en el contratiempo, dos cuerdas agudas
    for s in (2, 6, 10, 14):
        for m in v[-2:]:
            nota('gtr', 'gtr', b, s, m + 12, 0.9, 0.7)
    # colchón: cuerdas sostenidas solo en la segunda vuelta (Fa#4-Fa#5)
    if b >= 8:
        for m in B.voicear(ac, None, 66, 78):
            nota('pad', 'cuerdas', b, 0, m, 15.5, 0.6)
    # figura: melodía en acordeón
    for s, m, d in MEL[b % 8]:
        nota('lead', 'acordeon', b, s, m, d * 0.92, 0.85)
B.PROGRAMA.update({'acordeon': 21})
mu = B._mezcla(L, 'cumbia', (N * 16 + 8) * step, np.zeros(int(((N * 16 + 8) * step + 3) * SR)), 9)
x = BT.mezclar(dr, mu, -16.5, -19.0)
o = wave.open('/tmp/lat/cumbia_v2.wav', 'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((x * 32767).astype(np.int16).tobytes()); o.close()
print(round(len(x) / SR, 1))

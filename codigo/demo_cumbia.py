"""Muestras de cumbia (patrones tomados de fuentes; ver plan/estudio_latinos.md)."""
import sys, wave, numpy as np
sys.path.insert(0, '/home/claude/pb-x7k2m/codigo')
import banda as B, bateria as BT
SR = 44100
P = {'bombo': 36, 'aro': 37, 'caja': 38, 'hh': 42, 'hh_ab': 46, 'hh_pie': 44, 'tom1': 48, 'tom_piso': 43,
     'guiro_c': 73, 'guiro_l': 74, 'maraca': 70, 'conga_ab': 63, 'conga_mute': 62, 'conga_baja': 64,
     'timb_a': 65, 'timb_b': 66, 'bongo_a': 60, 'bongo_b': 61, 'cencerro': 56, 'crash': 49}

def grid(s):
    return [i for i, c in enumerate(s.replace(' ', '')) if c != '-']

def batería(compases, bpm, kit, capas, semilla=3):
    step = 60 / bpm / 4; rng = np.random.default_rng(semilla); notas = []
    for b in range(compases):
        for voz, (pat, vel) in capas.items():
            for s in grid(pat):
                t = (b * 16 + s) * step + rng.normal(0, 0.003)
                v = vel * (1.0 if s % 4 == 0 else 0.85) + rng.normal(0, 5)
                notas.append((max(0, t), P[voz], int(np.clip(v, 30, 127)), voz))
    x = BT._fluid(notas, kit)
    return BT.procesar(x, 'funk')

def banda(compases, bpm, ton, prog, partes, semilla=4):
    """partes: lista de (pista, kind, función(compás, raíz, acorde) -> [(paso, midi, dur_pasos, vel)])"""
    step = 60 / bpm / 4; rng = np.random.default_rng(semilla)
    L = {k: [] for k in ('gtr', 'gtr_dist', 'bajo', 'teclas', 'pad', 'lead', 'extra')}
    for b in range(compases):
        rel, tipo = prog[b % len(prog)]
        raiz = ton + rel; ac = B.notas_acorde(raiz, tipo)
        for pista, kind, f in partes:
            for (s, m, d, v) in f(b, raiz, ac):
                L[pista].append(((b * 16 + s) * step + rng.normal(0, 0.004), m, d * step, v, kind))
    return B._mezcla(L, 'cumbia', compases * 16 * step, np.zeros(int((compases * 16 * step + 3) * SR)), semilla)

B.PROGRAMA.update({'acordeon': 21, 'gtr_chorus': 27, 'organo_cumbia': 16})
bajo_cumbia = lambda b, r, ac: [(0, 36 + (r - 36) % 12, 7, 0.95), (8, 36 + (r - 36) % 12 + 7, 6, 0.85), (14, 36 + (r - 36) % 12 + 7 - 12 + 12, 2, 0.7)]

def acordeon_off(b, r, ac):  # acordes cortos en los contratiempos
    v = B.voicear(ac, None, 60, 76)
    return [(s, m, 1.5, 0.75) for s in (2, 6, 10, 14) for m in v]

def melodia_acordeon(b, r, ac):
    frase = [(0, 4, 3), (4, 7, 2), (6, 9, 2), (8, 7, 4), (12, 4, 2), (14, 2, 2)] if b % 2 == 0 else [(0, 0, 4), (4, 2, 2), (6, 4, 2), (8, 2, 6), (14, -1, 2)]
    base = 72 + (r - 72) % 12 if b % 4 < 2 else 72 + (ac[0] - 72) % 12
    return [(s, base + iv if iv >= 0 else base - 1, d, 0.85) for (s, iv, d) in frase]

def guitarra_chicha(b, r, ac):  # guitarra limpia en arpegio de semicorcheas
    v = sorted(B.voicear(ac, None, 64, 79))
    seq = v + v[1:-1][::-1]
    return [(s, seq[(s // 2) % len(seq)], 1.8, 0.75) for s in range(0, 16, 2)]

out = []
bpm = 92; ton = 9  # La menor, tonalidad muy usada en cumbia
prog = [(0, 'm'), (0, 'm'), (7, 'M'), (7, 'M'), (5, 'M'), (5, 'M'), (7, 'M'), (0, 'm')]
N = 8
# 1) Cumbia colombiana en batería (adaptación de tambora, llamador y guacharaca)
d1 = batería(N, bpm, 8, {'hh': ('x-xx x-xx x-xx x-xx', 85), 'aro': ('--x- ---- --x- ----', 95),
                        'tom1': ('---- --x- ---- --x-', 95), 'bombo': ('x--- x--- x--- x---', 105),
                        'hh_pie': ('x--- x--- x--- x---', 70), 'guiro_l': ('x--- x--- x--- x---', 80),
                        'guiro_c': ('--xx --xx --xx --xx', 75), 'conga_ab': ('---- --x- ---- --x-', 85)})
m1 = banda(N, bpm, ton, prog, [('bajo', 'bajo', bajo_cumbia), ('teclas', 'acordeon', acordeon_off), ('lead', 'acordeon', melodia_acordeon)])
out.append(BT.mezclar(d1, m1))
# 2) Cumbia del sur (estilo chileno/argentino): bombo y aro en negras, hi-hat abierto en los contratiempos ("pum-chas")
d2 = batería(N, bpm, 8, {'bombo': ('x--- x--- x--- x---', 105), 'aro': ('x--- x--- x--- x---', 80),
                        'hh_ab': ('--x- --x- --x- --x-', 85), 'guiro_l': ('x--- x--- x--- x---', 80),
                        'guiro_c': ('--xx --xx --xx --xx', 75), 'timb_a': ('---- ---- ---- -x-x', 90)})
m2 = banda(N, bpm, ton, prog, [('bajo', 'bajo', bajo_cumbia), ('teclas', 'organo_cumbia', acordeon_off), ('lead', 'acordeon', melodia_acordeon)])
out.append(BT.mezclar(d2, m2))
# 3) Cumbia peruana (chicha): percusión de timbales, bongó y güiro, sin batería; guitarra eléctrica limpia arpegiada
d3 = batería(N, bpm, 8, {'timb_a': ('---- x--- ---- x---', 95), 'timb_b': ('---- ---- ---- --x-', 90),
                        'bongo_a': ('x-x- --x- x-x- --x-', 80), 'bongo_b': ('---x ---- ---x ----', 80),
                        'guiro_l': ('x--- x--- x--- x---', 80), 'guiro_c': ('--xx --xx --xx --xx', 75),
                        'conga_baja': ('x--- ---- x--- ----', 90)})
m3 = banda(N, bpm, ton, prog, [('bajo', 'bajo', bajo_cumbia), ('gtr', 'gtr_chorus', guitarra_chicha), ('lead', 'gtr_chorus', melodia_acordeon)])
out.append(BT.mezclar(d3, m3))
sil = np.zeros((int(1.0 * SR), 2))
allm = np.concatenate([out[0], sil, out[1], sil, out[2]])
o = wave.open('/tmp/lat/cumbias.wav', 'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((allm * 32767).astype(np.int16).tobytes()); o.close()
print([round(len(x) / SR, 1) for x in out])

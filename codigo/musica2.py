"""Motor de música para los videos largos (canciones para tocar batería encima).

Reglas de composición aplicadas:
- Armonía: progresiones diatónicas de pop/rock (I-V-vi-IV, vi-IV-I-V, I-vi-IV-V, IV-I-V-vi...) con colores
  (maj7, add9, m7, sus4 antes del V). La estrofa y el coro usan progresiones distintas.
- Conducción de voces: cada acorde se voicea en la inversión más cercana al anterior (los dedos se mueven poco).
- Melodía: frases de 4 compases (pregunta y respuesta). Notas del acorde en los tiempos fuertes, notas de paso
  por grado conjunto en los débiles, saltos de máximo una sexta seguidos de movimiento contrario, la primera frase
  termina abierta (semicadencia) y la segunda cierra en la tónica. El coro va más agudo y con notas más largas.
- Arreglo por secciones: intro, estrofa, coro, puente y final; cada sección suma o quita instrumentos.
- Bajo: tónica del acorde en el 1 y siguiendo al bombo, con nota de aproximación antes de cada cambio de acorde.
- Sonido: piano eléctrico (FM), pad con desafinación leve, arpegio brillante tipo campana, bajo filtrado,
  estéreo con paneo y reverb.
"""
import numpy as np

SR = 44100
MAYOR = [0, 2, 4, 5, 7, 9, 11]
# grados (1-7) -> (semitono de la raíz, tipo)
GRADOS = {1: (0, 'M'), 2: (2, 'm'), 3: (4, 'm'), 4: (5, 'M'), 5: (7, 'M'), 6: (9, 'm')}
PROGS_ESTROFA = [[1, 5, 6, 4], [6, 4, 1, 5], [1, 6, 4, 5], [1, 4, 6, 5], [4, 1, 5, 6], [1, 3, 4, 5]]
PROGS_CORO = [[4, 1, 5, 6], [1, 5, 6, 4], [6, 4, 1, 5], [4, 5, 3, 6], [1, 5, 4, 4]]
PROGS_PUENTE = [[2, 5, 1, 6], [4, 5, 6, 6], [2, 4, 5, 5]]
RITMOS = [  # células rítmicas de 1 compás: (paso de inicio, duración en semicorcheas)
    [(0, 4), (4, 2), (6, 2), (8, 6), (14, 2)],
    [(2, 2), (4, 4), (8, 2), (10, 2), (12, 4)],
    [(0, 6), (6, 2), (8, 4), (12, 4)],
    [(0, 2), (2, 2), (4, 4), (10, 2), (12, 4)],
    [(4, 2), (6, 2), (8, 2), (10, 6)],
]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def acorde(grado, tonica, color):
    r, tipo = GRADOS[grado]
    raiz = tonica + r
    tri = [0, 4, 7] if tipo == 'M' else [0, 3, 7]
    extra = []
    if color:
        if grado in (1, 4): extra = [11] if grado == 4 else [14]  # IVmaj7, Iadd9
        elif tipo == 'm': extra = [10]  # m7
    return raiz, [raiz + i for i in tri + extra]


def voicear(notas, previo, lo=52, hi=72):
    """Elige la inversión más cercana al voicing anterior (conducción de voces)."""
    pcs = sorted(set(n % 12 for n in notas))
    cands = []
    for base in range(lo, hi - 6):
        v = []
        for pc in pcs:
            n = base + ((pc - base) % 12)
            v.append(n)
        v = sorted(v)
        if v[-1] <= hi: cands.append(v)
    if not previo: return min(cands, key=lambda v: abs(np.mean(v) - 62))
    return min(cands, key=lambda v: sum(min(abs(a - b) for b in previo) for a in v))


# ---------- instrumentos ----------
def env(n, a, d_rate, s=0.0, rel=0.05):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * (s + (1 - s) * np.exp(-t * d_rate))
    r = int(rel * SR)
    if r and n > r: e[-r:] *= np.linspace(1, 0, r)
    return e


def epiano(f, dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 1.8 * np.exp(-t * 7) + 0.25
    mod = np.sin(2 * np.pi * f * t)
    car = np.sin(2 * np.pi * f * t + idx * mod)
    tine = np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t * 30) * 0.12
    return (car + tine) * env(n, 0.003, 2.2, 0.12, 0.08) * vel


def pad(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for c in (-7, 0, 6):
        fc = f * 2 ** (c / 1200)
        ph = (fc * t) % 1.0
        out += 2 * ph - 1
    # filtro pasa bajos de un polo
    a = np.exp(-2 * np.pi * 1400 / SR); y = np.zeros(n); acc = 0.0
    from scipy.signal import lfilter
    y = lfilter([1 - a], [1, -a], out)
    y = lfilter([1 - a], [1, -a], y)
    return y / 3 * env(n, 0.6, 0.0, 1.0, 0.6)


def campana(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 4) + 0.15 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 8)
    return s * env(n, 0.002, 5.0, 0.0, 0.05)


def lead(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.35)
    ph = np.cumsum(f * vib) / SR
    tri = 2 * np.abs(2 * (ph % 1) - 1) - 1
    s = 0.7 * tri + 0.3 * np.sin(2 * np.pi * ph * 2)
    return s * env(n, 0.012, 1.2, 0.55, 0.09)


def bajo(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = (f * t) % 1
    saw = 2 * ph - 1
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * 420 / SR)
    y = lfilter([1 - a], [1, -a], saw); y = lfilter([1 - a], [1, -a], y)
    y = 0.6 * y / (np.abs(y).max() + 1e-9) + 0.55 * np.sin(2 * np.pi * f * t)
    return y * env(n, 0.004, 3.0, 0.35, 0.04)


def reverb(x, mezcla=0.22):
    from scipy.signal import lfilter
    out = np.zeros_like(x)
    for dl, g in ((1557, .80), (1617, .79), (1491, .81), (1422, .78), (1277, .80), (1356, .79)):
        b = np.zeros(dl + 1); b[0] = 1
        a = np.zeros(dl + 1); a[0] = 1; a[dl] = -g
        out += lfilter([1], a, x) * 0.16
    for dl, g in ((225, .5), (556, .5), (441, .5)):
        b = np.zeros(dl + 1); b[0] = -g; b[dl] = 1
        a = np.zeros(dl + 1); a[0] = 1; a[dl] = -g
        out = lfilter(b, a, out)
    return x * (1 - mezcla) + out * mezcla


# ---------- composición ----------
def secciones(nbars):
    """Reparte los compases en intro / estrofa / coro / puente / final (bloques de 4 u 8)."""
    plan = [('intro', 4)]
    resto = nbars - 4 - 4
    ciclo = ['estrofa', 'coro', 'estrofa', 'coro', 'puente', 'coro']
    i = 0
    while resto >= 8:
        plan.append((ciclo[i % len(ciclo)], 8)); resto -= 8; i += 1
    if resto >= 4: plan.append(('coro' if i % 2 else 'estrofa', 4)); resto -= 4
    plan.append(('final', 4 + resto))
    return plan


def melodia(rng, prog_acordes, escala, tonica, registro, nbar, coro):
    """Devuelve lista de (compás, paso, duración, midi)."""
    notas = []
    cel = RITMOS[rng.integers(len(RITMOS))]
    cel2 = RITMOS[rng.integers(len(RITMOS))]
    previo = None
    for b in range(nbar):
        raiz, tonos = prog_acordes[b % len(prog_acordes)]
        frase_b = b % 4
        ritmo = cel if frase_b in (0, 1) else cel2
        if frase_b == 3:
            ritmo = [(0, 4), (4, 12)] if not coro else [(0, 2), (2, 2), (4, 12)]
        if coro: ritmo = [(s, min(16 - s, d * 2)) for (s, d) in ritmo if s % 4 == 0] or ritmo
        cierre = (b % 8 == 7)
        for j, (st, du) in enumerate(ritmo):
            fuerte = st % 8 == 0 or j == len(ritmo) - 1
            if fuerte or previo is None:
                pcs = [t % 12 for t in tonos]
                if frase_b == 3 and j == len(ritmo) - 1:
                    pcs = [tonica % 12] if cierre else [(tonica + 7) % 12, (tonica + 2) % 12]
                cands = [m for m in range(registro - 5, registro + 10) if m % 12 in pcs]
            else:
                cands = [m for m in range(registro - 5, registro + 10) if (m - tonica) % 12 in escala and abs(m - previo) <= 2 and m != previo]
                if not cands: cands = [m for m in range(registro - 5, registro + 10) if (m - tonica) % 12 in escala]
            if previo is None:
                m = min(cands, key=lambda x: abs(x - registro))
            else:
                pesos = np.array([1.0 / (1 + abs(x - previo)) ** 2 * (0.3 if abs(x - previo) > 9 else 1) for x in cands])
                m = cands[rng.choice(len(cands), p=pesos / pesos.sum())]
            notas.append((b, st, du, m)); previo = m
    return notas


def componer(bpm, nbars, kicks_loop, loop_bars, tonica=60, semilla=1, clic=False):
    """Devuelve audio estéreo (n, 2) de nbars compases. kicks_loop: tiempos (s) del bombo dentro del loop."""
    rng = np.random.default_rng(semilla)
    step = 60.0 / bpm / 4; bar = 16 * step
    n = int(nbars * bar * SR) + SR * 2
    L = {k: np.zeros(n) for k in ('ep', 'pad', 'arp', 'lead', 'bajo', 'clic')}

    def add(buf, s, t0):
        i0 = int(t0 * SR); e = min(n, i0 + len(s))
        if i0 < n: buf[i0:e] += s[:e - i0]

    pe = PROGS_ESTROFA[rng.integers(len(PROGS_ESTROFA))]
    pc = PROGS_CORO[rng.integers(len(PROGS_CORO))]
    while pc == pe: pc = PROGS_CORO[rng.integers(len(PROGS_CORO))]
    pp = PROGS_PUENTE[rng.integers(len(PROGS_PUENTE))]
    color = rng.random() < 0.7
    plan = secciones(nbars)
    escala = MAYOR
    voz_prev = None
    b0 = 0
    for nombre, nb in plan:
        prog = {'estrofa': pe, 'coro': pc, 'puente': pp, 'intro': pe, 'final': [4, 5, 1, 1]}[nombre]
        acs = []
        for g in prog:
            raiz, tonos = acorde(g, tonica, color)
            if nombre == 'puente' and g == 5: tonos = [raiz, raiz + 5, raiz + 7, raiz + 10]  # V7sus
            acs.append((raiz, tonos))
        mel = []
        if nombre in ('estrofa', 'coro', 'puente'):
            mel = melodia(rng, acs, escala, tonica, tonica + (17 if nombre == 'coro' else 12), nb, nombre == 'coro')
        for k in range(nb):
            b = b0 + k; t_b = b * bar
            raiz, tonos = acs[k % len(acs)]
            voz = voicear(tonos, voz_prev); voz_prev = voz
            # piano eléctrico: comping según sección
            if nombre in ('intro', 'final', 'puente'):
                golpes = [(0, 16, .9)]
            elif nombre == 'estrofa':
                golpes = [(0, 6, .85), (6, 4, .6), (10, 6, .7)]
            else:
                golpes = [(0, 4, .85), (4, 4, .55), (6, 2, .5), (8, 4, .75), (12, 2, .5), (14, 2, .55)]
            if nombre == 'final' and k == nb - 1: golpes = [(0, 16, 1.0)]
            for st, du, vel in golpes:
                for m in voz:
                    add(L['ep'], epiano(midi_hz(m), du * step + 0.3, vel) / len(voz), t_b + st * step)
            # pad en coro, puente y final
            if nombre in ('coro', 'puente', 'final', 'intro'):
                for m in voz:
                    add(L['pad'], pad(midi_hz(m), bar + 0.4) / len(voz) * (0.6 if nombre == 'intro' else 1), t_b)
            # arpegio brillante en el coro
            if nombre == 'coro':
                arp = sorted(voz) + [voz[0] + 12]
                for s in range(0, 16, 2):
                    m = arp[(s // 2) % len(arp)] + 12
                    add(L['arp'], campana(midi_hz(m), 4 * step) * (0.8 if s % 4 == 0 else 0.55), t_b + s * step)
            # bajo: raíz en el 1 + bombo + aproximación
            r = raiz - 24 if raiz - 24 >= 36 else raiz - 12
            sig = acs[(k + 1) % len(acs)][0] - 24
            if sig < 36: sig += 12
            lb = (b % loop_bars) * bar
            ks = sorted(set([0.0] + [round(x - lb, 6) for x in kicks_loop if lb <= x < lb + bar - 1e-6]))
            if nombre in ('intro',): ks = [0.0]
            for j, kt in enumerate(ks):
                fin = ks[j + 1] if j + 1 < len(ks) else bar
                add(L['bajo'], bajo(midi_hz(r), max(step * 1.5, fin - kt - 0.02)), t_b + kt)
            if nombre not in ('intro', 'final') and sig != r and k % 2 == 1:
                apr = sig - 1 if sig > r else sig + 2
                add(L['bajo'], bajo(midi_hz(apr), step * 1.6) * 0.8, t_b + 14 * step)
            if clic:
                t_c = np.arange(int(0.03 * SR)) / SR
                c = np.sin(2 * np.pi * 1600 * t_c) * np.exp(-t_c * 140)
                for q in range(4): add(L['clic'], c * (1.3 if q == 0 else 0.8), t_b + q * 4 * step)
        for (bb, st, du, m) in mel:
            add(L['lead'], lead(midi_hz(m), du * step * 0.95), (b0 + bb) * bar + st * step)
        b0 += nb
    # mezcla estéreo con paneo
    pan = {'ep': -0.25, 'pad': 0.0, 'arp': 0.45, 'lead': 0.1, 'bajo': 0.0, 'clic': 0.0}
    vol = {'ep': 0.30, 'pad': 0.10, 'arp': 0.10, 'lead': 0.07, 'bajo': 0.42, 'clic': 0.5}
    st = np.zeros((n, 2))
    wet = np.zeros(n)
    for k, buf in L.items():
        g = vol[k]; p = pan[k]
        st[:, 0] += buf * g * np.sqrt((1 - p) / 2) * 1.414
        st[:, 1] += buf * g * np.sqrt((1 + p) / 2) * 1.414
        if k in ('ep', 'pad', 'arp', 'lead'): wet += buf * g
    rv = reverb(wet, 1.0) * 0.35
    st[:, 0] += rv; st[:, 1] += np.roll(rv, 331)
    return st[:int(nbars * bar * SR)]

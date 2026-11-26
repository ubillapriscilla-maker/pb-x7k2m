"""Banda de acompañamiento por estilo para los videos de batería (guitarra, bajo y teclados).

Cada estilo usa los instrumentos y la forma de tocar propios del género (estudio del 26 nov 2026):
- Rock: guitarra distorsionada con power chords; en la estrofa corcheas apagadas con la palma, en el coro acordes
  abiertos que suenan largo. Bajo en corcheas sobre la tónica, amarrado al bombo, con nota de paso al cambio.
  Órgano suave de fondo en el coro. Progresiones I-bVII-IV, I-V-vi-IV, vi-IV-I-V.
- Pop: guitarra limpia rasgueada en semicorcheas, piano en los tiempos, bajo tónica-octava, gancho de sinte pluck.
- Punk: power chords distorsionados en corcheas todas hacia abajo, bajo en corcheas.
- Metal: chugs apagados en galope sobre la tónica (menor), acordes abiertos en los acentos.
- Funk: guitarra en semicorcheas con acorde de novena (el "acorde de James Brown") y rasguidos apagados entre medio,
  vamp de uno o dos acordes (dórico), bajo sincopado con octavas, clavinet y bronces en el coro.
- Disco: bajo en octavas (tónica en el tiempo, octava en el contratiempo), guitarra "chank" en las cuerdas agudas
  en semicorcheas, cuerdas sostenidas y piano en los contratiempos.
- Motown: piano en negras, guitarra en el 2 y el 4, bajo al estilo de James Jamerson: tónica-quinta-octava con
  síncopas ("uno y") y notas cromáticas de aproximación.
- Hip-hop boom bap: Rhodes con acordes menores con séptima/novena (progresiones de jazz y soul), sonido "lo-fi",
  bajo profundo que sigue al bombo.
- Bossa nova: guitarra de nylon con el pulgar en el 1 y el 3 (tónica y quinta) y los dedos en el patrón sincopado,
  acordes maj7, m7 y 7 (II-V-I), Rhodes suave.
- Ska: guitarra y órgano cortos en todos los contratiempos, bajo caminando en negras, bronces en el coro.
- Reggaetón: bajo sintetizado en el dembow (3-3-2), arpegio pluck, progresión i-VI-III-VII.
- Reggae: se mantiene el arreglo aprobado por Priscilla (musica2, estilo reggae).

La música va por debajo de la batería: el bajo y los acordes siguen al bombo y a los tiempos del ritmo.
"""
import numpy as np
from scipy.signal import lfilter, butter, sosfilt, resample_poly

SR = 44100
_RNG = np.random.default_rng(7)

# ----------------------------------------------------------------------------- utilidades


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _t(dur):
    return np.arange(int(max(dur, 0.01) * SR)) / SR


def _rel(x, rel=0.02):
    n = min(len(x), int(rel * SR))
    if n > 1:
        x[-n:] *= np.linspace(1, 0, n)
    return x


def _lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x)


def _hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


def _bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)


# ----------------------------------------------------------------------------- instrumentos


def ks(f, dur, brillo=0.5, decay=0.996, pos=0.18, rng=_RNG):
    """Cuerda pulsada (Karplus-Strong) calculada al doble de frecuencia de muestreo para afinar mejor."""
    sr2 = SR * 2
    N = max(2, int(round(sr2 / f - 0.5)))
    n = int(dur * sr2) + 1
    exc = rng.uniform(-1, 1, N)
    a = 1 - brillo  # excitación más suave = cuerda más opaca
    if a > 0:
        exc = lfilter([1 - a], [1, -a], exc)
    k = max(1, int(N * pos)); exc = exc - np.roll(exc, k)  # posición del ataque (cerca del puente = más brillo)
    x = np.zeros(n); x[:N] = exc
    den = np.zeros(N + 2); den[0] = 1; den[N] = -decay * 0.5; den[N + 1] = -decay * 0.5
    y = lfilter([1.0], den, x)
    y = resample_poly(y, 1, 2)
    m = np.abs(y[:N]).max() + 1e-9
    return _rel(y / m, 0.012)


def guitarra(notas, dur, vel=1.0, abajo=True, brillo=0.55, decay=0.996, apagada=False, rng=_RNG):
    """Rasgueo: las cuerdas suenan escalonadas (abajo = grave a agudo)."""
    orden = notas if abajo else notas[::-1]
    sep = 0.007 if not apagada else 0.004
    largo = dur + sep * len(notas) + 0.02
    out = np.zeros(int(largo * SR) + 10)
    for i, m in enumerate(orden):
        d = dur if not apagada else min(dur, 0.09)
        s = ks(hz(m), d, brillo * (0.8 if apagada else 1.0), 0.985 if apagada else decay, rng=rng)
        g = vel * (0.85 + 0.15 * rng.random()) * (1.0 if not apagada else 0.8)
        i0 = int(i * sep * SR)
        out[i0:i0 + len(s)] += s * g
    return out


def rasguido_muerto(dur=0.05, vel=0.6, rng=_RNG):
    """El "chick" de funk: cuerdas apagadas con la mano izquierda (sin nota)."""
    t = _t(dur)
    s = _bp(rng.normal(size=len(t)), 900, 4200) * np.exp(-t * 70)
    return s / (np.abs(s).max() + 1e-9) * vel * 0.5


def bajo_dedo(f, dur, vel=1.0, brillo=0.3, rng=_RNG):
    t = _t(dur)
    s = ks(f, dur, brillo, 0.9975, pos=0.3, rng=rng)[:len(t)]
    if len(s) < len(t):
        s = np.pad(s, (0, len(t) - len(s)))
    fund = np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6)
    y = _lp(0.6 * s + 0.7 * fund, 1500)
    return _rel(y * vel, 0.03)


def bajo_sinte(f, dur, vel=1.0):
    """Bajo sintetizado redondo (hip-hop, reggaetón): seno con un poco de saturación."""
    t = _t(dur)
    caida = 1 + 0.06 * np.exp(-t * 40)
    ph = 2 * np.pi * np.cumsum(f * caida) / SR
    y = np.tanh(1.6 * (np.sin(ph) + 0.25 * np.sin(2 * ph))) * np.minimum(1, t * 300)
    return _rel(y * vel * 0.45, 0.04)


def rhodes(f, dur, vel=1.0):
    t = _t(dur + 0.25)
    env = np.exp(-t * (1.1 + f / 700)) * np.minimum(1, t * 400)
    idx = 1.6 * vel * np.exp(-t * 3.5) + 0.25
    car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    tine = np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t * 28) * 0.18 * vel
    y = (car + tine) * env * vel
    n_off = int(dur * SR)
    if n_off < len(y):
        y[n_off:] *= np.exp(-np.arange(len(y) - n_off) / SR * 14)
    return y


def organo(f, dur, vel=1.0, registro='rock'):
    """Órgano tipo Hammond: registros por armónicos, leslie (vibrato) y clic de tecla."""
    t = _t(dur)
    pesos = {'rock': [(0.5, 0.3), (1, 1.0), (1.5, 0.5), (2, 0.6), (3, 0.3), (4, 0.25)],
             'jazz': [(0.5, 0.3), (1, 1.0), (1.5, 0.5)],
             'reggae': [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.3), (8, 0.1)]}[registro]
    vib = 0.0025 * np.sin(2 * np.pi * 6.2 * t)
    y = sum(w * np.sin(2 * np.pi * f * h * (t + vib)) for h, w in pesos)
    y *= (1 + 0.12 * np.sin(2 * np.pi * 6.2 * t + 1)) * np.minimum(1, t * 250)
    nc = min(len(t), int(0.006 * SR))
    y[:nc] += np.random.default_rng(int(f)).normal(size=nc) * 0.3
    return _rel(y * vel * 0.35, 0.02)


def piano(f, dur, vel=1.0):
    t = _t(dur + 0.3)
    B = 0.0004
    y = np.zeros(len(t))
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > SR * 0.45:
            break
        y += (1 / k ** 1.1) * np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.8 + 0.5 * k + f / 900))
    y *= np.minimum(1, t * 600) * vel
    n_off = int(dur * SR)
    if n_off < len(y):
        y[n_off:] *= np.exp(-np.arange(len(y) - n_off) / SR * 10)
    return y * 0.6


def clavinet(f, dur, vel=1.0, rng=_RNG):
    s = ks(f, max(dur, 0.06), 0.95, 0.99, pos=0.08, rng=rng)
    return _hp(s, 300) * vel * 0.8


def cuerdas(f, dur, vel=1.0):
    t = _t(dur + 0.4)
    y = np.zeros(len(t))
    for det in (-0.006, 0.0, 0.007):
        ff = f * (1 + det)
        for k in range(1, 12):
            if ff * k > 7000:
                break
            y += np.sin(2 * np.pi * ff * k * t + det * 100 * k) / k
    env = np.minimum(1, t / 0.18)
    n_off = int(dur * SR)
    if n_off < len(y):
        env[n_off:] *= np.exp(-np.arange(len(y) - n_off) / SR * 5)
    return _lp(y * env * vel * 0.12, 3500)


def bronces(f, dur, vel=1.0):
    t = _t(dur)
    env = np.minimum(1, t / 0.015) * np.exp(-t * 2.0)
    br = np.minimum(1, t / 0.03) * np.exp(-t * 6) * 0.8 + 0.3
    y = np.zeros(len(t))
    for k in range(1, 16):
        if f * k > 9000:
            break
        y += np.sin(2 * np.pi * f * k * t) / k * np.exp(-k / (1.5 + 9 * br))
    return _rel(y * env * vel * 0.5, 0.03)


def pluck(f, dur, vel=1.0):
    t = _t(dur)
    y = np.zeros(len(t))
    br = np.exp(-t * 12)
    for k in range(1, 10):
        y += np.sin(2 * np.pi * f * k * t) / k * np.exp(-k / (1 + 8 * br))
    return _rel(y * np.exp(-t * 5) * np.minimum(1, t * 500) * vel * 0.5, 0.02)


def nylon(f, dur, vel=1.0, rng=_RNG):
    return _lp(ks(f, dur, 0.35, 0.995, pos=0.25, rng=rng), 3000) * vel


def reverb(x, mezcla=1.0):
    y = np.zeros_like(x)
    for d, g in ((1499, .72), (1637, .70), (1811, .68), (1993, .66)):
        a = np.zeros(d + 1); a[0] = 1; a[d] = -g
        y += lfilter([1], a, x)
    y = _lp(y, 5000) * 0.12
    return y * mezcla


# ----------------------------------------------------------------------------- armonía

TIPOS = {'M': [0, 4, 7], 'm': [0, 3, 7], '5': [0, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10],
         'maj7': [0, 4, 7, 11], '9': [0, 4, 10, 14], 'm9': [0, 3, 10, 14], '7#9': [0, 4, 10, 15],
         'add9': [0, 4, 7, 14], 'm7b5': [0, 3, 6, 10]}

ESTILO_DE = {
    'bombo_y_caja': 'rock', 'hat_negras': 'rock', 'medio_tiempo': 'rock', 'ride_rock': 'rock', 'rock_16avos': 'rock',
    'rock_basico': 'rock', 'rock_bombo_extra': 'rock', 'rock_sincopado': 'rock', 'pop_4_al_piso': 'pop',
    'punk': 'punk', 'blast_beat': 'metal', 'doble_bombo_corto': 'metal', 'metal_doble_bombo': 'metal',
    'metal_galope': 'metal', 'funk_16avos': 'funk', 'funk_abierto': 'funk', 'funk_sincopado': 'funk',
    'disco': 'disco', 'hiphop_boom_bap': 'hiphop', 'motown': 'motown', 'bossa_nova': 'bossa', 'ska': 'ska',
    'reggaeton': 'reggaeton', 'reggae_one_drop': 'reggae',
}

# progresiones: (semitonos desde la tónica, tipo); estrofa y coro distintos
PROGS = {
    'rock': ([[(0, 'M'), (10, 'M'), (5, 'M'), (0, 'M')], [(9, 'm'), (5, 'M'), (0, 'M'), (7, 'M')]],
             [[(0, 'M'), (7, 'M'), (9, 'm'), (5, 'M')], [(5, 'M'), (0, 'M'), (7, 'M'), (7, 'M')]]),
    'pop': ([[(0, 'add9'), (7, 'M'), (9, 'm7'), (5, 'maj7')], [(9, 'm7'), (5, 'maj7'), (0, 'add9'), (7, 'M')]],
            [[(5, 'maj7'), (7, 'M'), (9, 'm7'), (0, 'add9')], [(0, 'add9'), (7, 'M'), (5, 'maj7'), (5, 'maj7')]]),
    'punk': ([[(0, 'M'), (5, 'M'), (7, 'M'), (5, 'M')]], [[(0, 'M'), (7, 'M'), (9, 'm'), (5, 'M')]]),
    'metal': ([[(0, 'm'), (0, 'm'), (8, 'M'), (10, 'M')]], [[(0, 'm'), (8, 'M'), (3, 'M'), (10, 'M')]]),
    'funk': ([[(0, 'm7'), (0, 'm7'), (5, '9'), (5, '9')]], [[(5, '9'), (5, '9'), (0, 'm7'), (7, '7#9')]]),
    'disco': ([[(0, 'm7'), (5, '9'), (0, 'm7'), (5, '9')]], [[(3, 'maj7'), (5, '9'), (0, 'm7'), (0, 'm7')]]),
    'motown': ([[(0, 'M'), (9, 'm'), (5, 'M'), (7, 'M')]], [[(0, 'M'), (5, 'M'), (0, 'M'), (7, '7')]]),
    'hiphop': ([[(0, 'm9'), (5, 'm7'), (3, 'maj7'), (2, 'm7')]], [[(0, 'm9'), (8, 'maj7'), (5, 'm7'), (7, 'm7')]]),
    'bossa': ([[(0, 'maj7'), (9, '7'), (2, 'm7'), (7, '7')]], [[(2, 'm7'), (7, '7'), (0, 'maj7'), (5, 'maj7')]]),
    'ska': ([[(0, 'M'), (9, 'm'), (2, 'm'), (7, '7')]], [[(0, 'M'), (5, 'M'), (7, 'M'), (0, 'M')]]),
    'reggaeton': ([[(0, 'm'), (8, 'M'), (3, 'M'), (10, 'M')]], [[(0, 'm'), (8, 'M'), (3, 'M'), (10, 'M')]]),
}
MENOR = {'metal', 'funk', 'disco', 'hiphop', 'reggaeton'}
PENTA_MAY = [0, 2, 4, 7, 9]
PENTA_MEN = [0, 3, 5, 7, 10]


def notas_acorde(raiz, tipo):
    return [raiz + i for i in TIPOS[tipo]]


def voicear(pcs, previo, lo, hi):
    """Acorde en la inversión más cercana al anterior (los dedos se mueven poco), dentro de [lo, hi]."""
    p0 = pcs[0] % 12
    forma = sorted({(p - p0) % 12 for p in pcs})
    cands = []
    for inv in range(len(forma)):
        sh = forma[inv:] + [x + 12 for x in forma[:inv]]
        sh = [x - sh[0] for x in sh]
        pc_bajo = (p0 + forma[inv]) % 12
        for b in range(lo, hi + 1):
            if b % 12 == pc_bajo and b + sh[-1] <= hi:
                cands.append([b + x for x in sh])
    if not cands:
        r = lo + (p0 - lo) % 12
        return [r + x for x in forma]
    if previo is None:
        return cands[len(cands) // 2]
    c = float(np.mean(previo))
    return min(cands, key=lambda v: abs(float(np.mean(v)) - c))


def power(raiz_pc, lo=40):
    r = lo + (raiz_pc - lo) % 12
    return [r, r + 7, r + 12]


FORMAS_GTR = {  # formas reales de guitarra (intervalos desde la raíz); E = raíz en la 6a cuerda, A = en la 5a
    'M': ('E', [0, 7, 12, 16, 19, 24]), 'm': ('E', [0, 7, 12, 15, 19, 24]), '7': ('E', [0, 7, 10, 16, 19, 24]),
    'm7': ('E', [0, 7, 10, 15, 19, 24]), '5': ('E', [0, 7, 12]), 'maj7': ('A', [0, 7, 11, 16, 19]),
    '9': ('A', [0, 4, 10, 14, 19]), 'm9': ('A', [0, 3, 10, 14, 19]), '7#9': ('A', [0, 4, 10, 15]),
    'add9': ('A', [0, 4, 7, 14, 16]), 'm7b5': ('A', [0, 6, 10, 15])}


def acorde_guitarra(pcs, lo=48, tipo=None):
    """Acorde con una forma real de guitarra (cejilla tipo Mi o tipo La), como lo tocaría un guitarrista."""
    if tipo is None:
        rel = sorted({(p - pcs[0]) % 12 for p in pcs})
        tipo = next((t for t, iv in TIPOS.items() if sorted({i % 12 for i in iv}) == rel), 'M')
    cuerda, forma = FORMAS_GTR.get(tipo, FORMAS_GTR['M'])
    base = 40 if cuerda == 'E' else 45
    r = base + (pcs[0] - base) % 12
    return [r + x for x in forma]


# ----------------------------------------------------------------------------- secciones


def secciones(nbars):
    plan = [('intro', min(4, nbars))]
    resto = nbars - plan[0][1] - (4 if nbars >= 12 else 0)
    ciclo = ['estrofa', 'coro', 'estrofa', 'coro', 'puente', 'coro']
    i = 0
    while resto >= 8:
        plan.append((ciclo[i % len(ciclo)], 8)); resto -= 8; i += 1
    if resto >= 4:
        plan.append(('coro' if i % 2 else 'estrofa', 4)); resto -= 4
    if nbars >= 12:
        plan.append(('final', 4 + resto))
    elif resto > 0:
        plan.append(('coro', resto))
    return plan


def motivo(rng, menor):
    """Gancho de 2 compases: ritmo + grados de la pentatónica. Se repite en el coro (eso lo hace pegajoso)."""
    celdas = [[0, 3, 6, 10, 12], [0, 2, 4, 8, 14], [2, 4, 6, 10], [0, 6, 8, 10, 12, 14]]
    c1 = celdas[rng.integers(len(celdas))]; c2 = celdas[rng.integers(len(celdas))]
    esc = PENTA_MEN if menor else PENTA_MAY
    grados = list(rng.integers(0, 5, len(c1) + len(c2)))
    grados[-1] = 0  # termina en la tónica
    notas = []
    k = 0
    for b, cel in ((0, c1), (1, c2)):
        for j, st in enumerate(cel):
            sig = cel[j + 1] if j + 1 < len(cel) else 16
            notas.append((b, st, max(1, sig - st), esc[grados[k] % 5] + 12 * (grados[k] // 5)))
            k += 1
    return notas


# ----------------------------------------------------------------------------- componer


def componer(bpm, nbars, kicks_loop, loop_bars, tonica=62, semilla=1, clic=False, estilo='pop', plan=None):
    """Audio estéreo (n, 2) de nbars compases. estilo: nombre del ritmo de drumlib o familia (rock, funk...)."""
    fam = ESTILO_DE.get(str(estilo).split('__')[0], estilo)
    if fam == 'reggae':
        import musica2
        return musica2.componer(bpm, nbars, kicks_loop, loop_bars, tonica=tonica, semilla=semilla, clic=clic, estilo='reggae')
    if fam not in PROGS:
        fam = 'pop'
    rng = np.random.default_rng(semilla)
    step = 60.0 / bpm / 4; bar = 16 * step
    n = int(nbars * bar * SR) + SR * 3
    pistas = ['gtr', 'gtr_dist', 'bajo', 'teclas', 'pad', 'lead', 'extra', 'clic']
    L = {k: np.zeros(n) for k in pistas}
    menor = fam in MENOR
    # tónica cómoda para la guitarra (E, A, D, G) y el bajo
    ton = tonica % 12
    if fam in ('rock', 'punk', 'metal'):
        ton = 4 if fam == 'metal' else (9 if ton not in (4, 9, 2, 7) else ton)

    def add(k, s, t0, g=1.0):
        t0 += rng.normal(0, 0.003)  # humanizar: músicos reales no caen exacto en la grilla
        i0 = max(0, int(t0 * SR)); e = min(n, i0 + len(s))
        if i0 < n:
            L[k][i0:e] += s[:e - i0] * g

    # bombo por compás (pasos de semicorchea)
    pasos_loop = 16 * loop_bars
    kick_steps = {}
    for tk in kicks_loop:
        st = int(round(tk / step)) % pasos_loop
        kick_steps.setdefault(st // 16, set()).add(st % 16)

    plan = plan or secciones(nbars)
    prog_e = PROGS[fam][0][rng.integers(len(PROGS[fam][0]))]
    prog_c = PROGS[fam][1][rng.integers(len(PROGS[fam][1]))]
    por_acorde = 2 if bpm >= 150 else 1  # en tempos rápidos cada acorde dura 2 compases
    mot = motivo(rng, menor)
    previo = None
    b0 = 0
    for (sec, nb) in plan:
        prog = prog_c if sec in ('coro', 'final') else (prog_e if sec != 'puente' else prog_e[::-1])
        for k in range(nb):
            b = b0 + k
            tb = b * bar
            ci = (k // por_acorde) % len(prog)
            rel, tipo = prog[ci]
            sig_rel = prog[((k + 1) // por_acorde) % len(prog)][0]
            raiz = ton + rel
            pcs = notas_acorde(raiz, tipo)
            ks_b = sorted(kick_steps.get(b % loop_bars, {0}))
            ultimo = (sec == 'final' and k == nb - 1) or b == nbars - 1
            lleno = sec in ('coro', 'final', 'puente')
            if ultimo:  # golpe final: todos juntos en el 1 y que suene
                _final(add, fam, pcs, raiz, tb, bar, previo)
                continue
            previo = _compas(add, fam, sec, k, pcs, tipo, raiz, sig_rel + ton, tb, step, ks_b, lleno, rng, previo)
            # gancho en el coro: el mismo motivo cada 2 compases, ajustado al acorde
            if sec == 'coro' and k % 4 in (0, 1) and fam not in ('punk',):
                for (bb, st, du, gr) in mot:
                    if bb != k % 2:
                        continue
                    m = 72 + ton + gr
                    if fam in ('rock', 'metal'):
                        m -= 12
                    m = _a_acorde(m, pcs) if st in (0, 8) else m
                    _lead(add, fam, m, du * step * 0.92, tb + st * step)
            if clic:
                tc = _t(0.03); c = np.sin(2 * np.pi * 1600 * tc) * np.exp(-tc * 140)
                for q in range(4):
                    add('clic', c * (1.3 if q == 0 else 0.8), tb + q * 4 * step)
        b0 += nb
    return _mezcla(L, fam, nbars * bar)


def _a_acorde(m, pcs):
    return min((m + d for d in range(-2, 3)), key=lambda x: (min(abs((x - p) % 12) for p in pcs) != 0, abs(x - m)))


def _lead(add, fam, m, dur, t0):
    f = hz(m)
    if fam in ('rock', 'metal'):
        add('gtr_dist', ks(f, dur, 0.75, 0.998, pos=0.12), t0, 0.55)
    elif fam in ('funk', 'ska'):
        add('lead', bronces(f, dur, 0.9), t0, 0.55)
    elif fam == 'disco':
        add('lead', cuerdas(f, dur, 1.0) * 1.6, t0, 0.6)
    elif fam in ('hiphop', 'bossa'):
        add('lead', rhodes(f, dur, 0.7), t0, 0.35)
    elif fam == 'motown':
        add('lead', piano(f, dur, 0.9) + piano(f * 2, dur, 0.5), t0, 0.35)
    else:
        add('lead', pluck(f, dur, 1.0), t0, 0.45)


def _final(add, fam, pcs, raiz, tb, bar, previo):
    dur = bar * 0.9
    r_b = 28 + (raiz - 28) % 12
    add('bajo', bajo_dedo(hz(r_b), dur, 1.0), tb, 1.0)
    if fam in ('rock', 'punk', 'metal'):
        add('gtr_dist', guitarra(power(raiz), dur, 1.0, decay=0.9985), tb, 1.0)
    elif fam in ('hiphop', 'bossa'):
        for m in voicear(pcs, previo, 55, 74):
            add('teclas', rhodes(hz(m), dur, 0.8), tb, 0.6)
    else:
        add('gtr', guitarra(acorde_guitarra(pcs), dur, 0.9, decay=0.998), tb, 0.8)
        for m in voicear(pcs, previo, 55, 74):
            add('teclas', piano(hz(m), dur, 0.8), tb, 0.5)


def _compas(add, fam, sec, k, pcs, tipo, raiz, sig, tb, step, ks_b, lleno, rng, previo):
    """Toca un compás del estilo. Devuelve el voicing de teclado usado (para conducir las voces)."""
    T = lambda s: tb + s * step  # noqa: E731
    r_b = 28 + (raiz - 28) % 12          # tónica en el registro del bajo (E1 a D#2)
    s_b = 28 + (sig - 28) % 12
    intro = sec == 'intro'
    voz = voicear(pcs, previo, 55, 74)

    if fam in ('rock', 'punk', 'metal'):
        pw = power(raiz)
        if fam == 'metal':  # galope apagado sobre la tónica + acorde abierto en los acentos
            for s in range(16):
                if s % 4 in (0, 2, 3):
                    add('gtr_dist', guitarra(pw[:2], step * 0.9, 0.9, apagada=True), T(s), 0.8)
            if lleno:
                add('gtr_dist', guitarra(pw, step * 7, 1.0, decay=0.998), T(0), 0.6)
        elif fam == 'punk' or not lleno:  # corcheas todas hacia abajo (apagadas en la estrofa del rock)
            ap = fam == 'rock' and not lleno
            for s in range(0, 16, 2):
                add('gtr_dist', guitarra(pw, step * (1.6 if not ap else 0.9), 0.95, apagada=ap), T(s), 0.9)
        else:  # coro de rock: acordes abiertos que suenan largo (1 y el "y" del 2)
            add('gtr_dist', guitarra(pw, step * 6, 1.0, decay=0.998), T(0), 1.0)
            add('gtr_dist', guitarra(pw, step * 10, 0.9, abajo=False, decay=0.998), T(6), 0.85)
            for m in voz:
                add('pad', organo(hz(m), 16 * step, 0.6), T(0), 0.35)
        if not intro or fam != 'rock':
            for s in range(0, 16, 2):  # bajo en corcheas, nota de paso al final si cambia el acorde
                nota = r_b
                if s == 14 and sig != raiz:
                    nota = s_b - 2 if (s_b - r_b) % 12 < 7 else s_b + 1
                add('bajo', bajo_dedo(hz(nota), step * 1.8, 0.95 if s in ks_b else 0.8, brillo=0.45), T(s))
        return voz

    if fam == 'pop':
        g = acorde_guitarra(pcs, 50, tipo)
        patron = [(0, 1), (4, 1), (6, 0), (10, 0), (12, 1), (14, 0)]  # abajo / arriba
        for s, ab in patron:
            add('gtr', guitarra(g, step * 1.8, 0.75 if ab else 0.55, abajo=bool(ab), apagada=intro), T(s), 0.7)
        if not intro:
            for s in (0, 8) if not lleno else (0, 6, 8, 14):
                for m in voz:
                    add('teclas', piano(hz(m), step * 5, 0.7), T(s), 0.33)
            for s in sorted(set(ks_b) | {0, 8}):
                add('bajo', bajo_dedo(hz(r_b), step * 1.9, 0.9), T(s))
            for s in (6, 14):
                add('bajo', bajo_dedo(hz(r_b + 12), step * 0.9, 0.6), T(s))
        return voz

    if fam == 'funk':
        g = acorde_guitarra(pcs, 52, tipo)[-3:]
        acentos = {0, 3, 6, 10, 14} if k % 2 == 0 else {0, 4, 7, 10, 13}
        for s in range(16):
            if s in acentos:
                add('gtr', guitarra(g, step * 0.8, 0.9, abajo=s % 2 == 0, brillo=0.7), T(s), 0.6)
            else:
                add('gtr', rasguido_muerto(0.04, 0.5 + 0.2 * (s % 2 == 0)), T(s), 0.6)
        if not intro:
            linea = [(0, 0, 2), (3, 0, 1), (6, 12, 1), (7, 0, 1), (10, 10, 1), (12, 12, 1), (14, 7, 1)]
            for s, iv, d in linea:
                add('bajo', bajo_dedo(hz(r_b + iv), step * d * 0.9, 1.0 if iv == 0 else 0.75, brillo=0.55), T(s))
            for s in (2, 5, 8, 11, 13):
                for m in voz[-2:]:
                    add('teclas', clavinet(hz(m), step * 0.7, 0.6), T(s), 0.4)
            if lleno:
                for s in (6, 14):
                    for m in voz[-3:]:
                        add('extra', bronces(hz(m + 12), step * 1.2, 0.8), T(s), 0.25)
        return voz

    if fam == 'disco':
        g = acorde_guitarra(pcs, 55, tipo)[-3:]
        for s in range(16):  # chank en semicorcheas: abierto en los contratiempos, apagado el resto
            ab = s % 4 == 2
            add('gtr', guitarra(g, step * 0.8, 0.8 if ab else 0.45, abajo=s % 2 == 0, apagada=not ab, brillo=0.75), T(s), 0.5)
        if not intro:
            for s in range(0, 16, 2):  # octavas
                oct_ = 12 if s % 4 == 2 else 0
                add('bajo', bajo_dedo(hz(r_b + oct_), step * 1.4, 0.95, brillo=0.5), T(s))
            if k % 2 == 1:
                add('bajo', bajo_dedo(hz(r_b + 12), step * 0.6, 0.7, brillo=0.5), T(15))
            for s in (2, 6, 10, 14):
                for m in voz:
                    add('teclas', piano(hz(m), step * 1.2, 0.55), T(s), 0.3)
            if lleno:
                for m in voz:
                    add('pad', cuerdas(hz(m), step * 16, 0.9), T(0), 0.8)
        return voz

    if fam == 'motown':
        for s in (0, 4, 8, 12):
            for m in voz:
                add('teclas', piano(hz(m), step * 2.5, 0.8 if s in (0, 8) else 0.65), T(s), 0.33)
        if not intro:
            g = acorde_guitarra(pcs, 55, tipo)[-3:]
            for s in (4, 12):
                add('gtr', guitarra(g, step * 1.0, 0.8, brillo=0.7), T(s), 0.6)
            # Jamerson: tónica en el 1 y su "y", quinta, octava, sexta y aproximación cromática al acorde que viene
            linea = [(0, 0, 2), (2, 0, 1), (6, 7, 1), (8, 12, 2), (11, 9, 1), (12, 7, 2)]
            for s, iv, d in linea:
                add('bajo', bajo_dedo(hz(r_b + iv), step * d * 0.95, 0.95, brillo=0.4), T(s))
            apr = s_b - 1 if (s_b - r_b) % 12 != 0 else r_b + 4
            add('bajo', bajo_dedo(hz(apr), step * 1.6, 0.8, brillo=0.4), T(14))
        return voz

    if fam == 'hiphop':
        v = voicear(pcs, previo, 53, 72)
        for j, m in enumerate(v):  # acorde de Rhodes que suena todo el compás (un poco arpegiado, como sampleado)
            add('teclas', rhodes(hz(m), step * 15, 0.75), T(0) + j * 0.012, 0.42)
        if k % 2 == 1:
            add('teclas', rhodes(hz(v[-1] + 2 if (v[-1] + 2) % 12 in [(p % 12) for p in PENTA_MEN] else v[-1]), step * 3, 0.5), T(10), 0.3)
        if not intro:
            pasos = ks_b or [0]
            for j, s in enumerate(pasos):
                fin = pasos[j + 1] if j + 1 < len(pasos) else 16
                nota = r_b if j == 0 or fin - s > 2 else r_b + 7
                add('bajo', bajo_sinte(hz(nota), step * (fin - s) * 0.95, 0.9), T(s))
        return v

    if fam == 'bossa':
        g = voicear(pcs, previo, 52, 67)
        quinta = r_b + 7 if (r_b + 7) < 43 else r_b - 5
        for s, m in ((0, r_b + 12), (8, quinta + 12)):  # pulgar: tónica y quinta en el 1 y el 3
            add('gtr', nylon(hz(m), step * 7, 0.9), T(s), 0.75)
        dedos = [0, 6, 12] if k % 2 == 0 else [2, 8, 10]
        for s in dedos:
            add('gtr', sum_pad([nylon(hz(m), step * 2.5, 0.7) for m in g]), T(s), 0.45)
        if lleno:
            for m in voicear(pcs, previo, 57, 76):
                add('pad', rhodes(hz(m), step * 15, 0.4), T(0), 0.3)
        return g

    if fam == 'ska':
        g = acorde_guitarra(pcs, 55, tipo)[-3:]
        for s in (2, 6, 10, 14):  # todos los contratiempos, corto y hacia arriba
            add('gtr', guitarra(g, step * 0.9, 0.85, abajo=False, brillo=0.75), T(s), 0.6)
            if not intro:
                for m in voz:
                    add('teclas', organo(hz(m), step * 0.9, 0.8, 'reggae'), T(s), 0.45)
        if not intro:
            camino = [0, 4, 7, 9] if '3' not in tipo and tipo in ('M', '7') else [0, 3, 7, 10]
            for q, s in enumerate((0, 4, 8, 12)):
                nota = r_b + camino[q]
                if q == 3 and sig != raiz:
                    nota = s_b - 1
                add('bajo', bajo_dedo(hz(nota), step * 3.6, 0.9, brillo=0.4), T(s))
            if lleno:
                for s in (14,):
                    for m in voz[-2:]:
                        add('extra', bronces(hz(m + 12), step * 1.5, 0.8), T(s), 0.25)
        return voz

    if fam == 'reggaeton':
        for s in (0, 3, 6, 8, 11, 14):  # dembow 3-3-2
            add('bajo', bajo_sinte(hz(r_b), step * 2.6, 0.95), T(s))
        arp = sorted(voicear(pcs, previo, 60, 79))
        orden = arp + arp[1:-1][::-1]
        for s in range(0, 16, 2):
            add('lead', pluck(hz(orden[(s // 2) % len(orden)]), step * 1.8, 0.7), T(s), 0.3)
        if lleno:
            for m in voz:
                add('pad', cuerdas(hz(m), step * 16, 0.7), T(0), 0.6)
        return voz
    return voz


def sum_pad(lst):
    n = max(len(x) for x in lst)
    out = np.zeros(n)
    for j, x in enumerate(lst):
        i0 = int(j * 0.008 * SR)
        e = min(n, i0 + len(x)); out[i0:e] += x[:e - i0]
    return out


def _mezcla(L, fam, largo_s):
    # guitarra distorsionada: saturación + caja de amplificador (paso bajo) + quitar barro
    if np.abs(L['gtr_dist']).max() > 0:
        x = L['gtr_dist']
        x = np.tanh(x * (6.0 if fam in ('metal', 'punk') else 4.0))
        x = _lp(_hp(x, 110), 4200, 4) * 0.55
        L['gtr_dist'] = x
    L['bajo'] = _hp(L['bajo'], 38)
    if fam == 'hiphop':  # lo-fi: Rhodes más oscuro
        L['teclas'] = _lp(L['teclas'], 3200)
    vol = {'gtr': 0.90, 'gtr_dist': 0.50, 'bajo': 0.36, 'teclas': 0.80, 'pad': 0.60, 'lead': 1.20, 'extra': 1.60, 'clic': 0.5}
    pan = {'gtr': -0.35, 'gtr_dist': -0.25, 'bajo': 0.0, 'teclas': 0.30, 'pad': 0.0, 'lead': 0.12, 'extra': 0.4, 'clic': 0.0}
    n = len(L['bajo'])
    st = np.zeros((n, 2)); wet = np.zeros(n)
    for k, buf in L.items():
        if not buf.any():
            continue
        g = vol[k]; p = pan[k]
        if k == 'gtr_dist':  # doble toma abierta a los lados, como en las grabaciones de rock
            st[:, 0] += buf * g * 0.75
            st[:, 1] += np.roll(buf, int(0.012 * SR)) * g * 0.75
        else:
            st[:, 0] += buf * g * np.sqrt((1 - p) / 2) * 1.414
            st[:, 1] += buf * g * np.sqrt((1 + p) / 2) * 1.414
        if k in ('teclas', 'pad', 'lead', 'gtr', 'extra'):
            wet += buf * g
    rv = reverb(wet, 1.0)
    st[:, 0] += rv; st[:, 1] += np.roll(rv, 331)
    pico = np.abs(st).max() + 1e-9
    st = np.tanh(st / pico * 1.4) * 0.8  # pegamento: compresión suave de toda la banda
    return st[:int(largo_s * SR)]

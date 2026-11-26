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


def _m(f):
    return int(round(69 + 12 * np.log2(f / 440.0)))


def _n(kind, f, dur, vel):
    return [(0.0, _m(f), dur, vel, kind)]


def guitarra(notas, dur, vel=1.0, abajo=True, brillo=0.55, decay=0.996, apagada=False, rng=_RNG, kind='gtr'):
    """Rasgueo: las cuerdas suenan escalonadas (abajo = grave a agudo). apagada = palm mute / cuerdas apagadas."""
    orden = notas if abajo else notas[::-1]
    sep = 0.008 if not apagada else 0.004
    d = dur if not apagada else min(dur, 0.12)
    k = kind + ('_m' if apagada else '')
    return [(i * sep, m, d, vel * (0.85 + 0.15 * rng.random()) * (1.0 if abajo or i else 0.9), k) for i, m in enumerate(orden)]


def rasguido_muerto(notas, vel=0.6):
    """El "chick" de funk: cuerdas apagadas con la mano izquierda."""
    return [(i * 0.003, m, 0.03, vel * 0.55, 'gtr_m') for i, m in enumerate(notas)]


def bajo_dedo(f, dur, vel=1.0, brillo=0.3, rng=_RNG):
    return _n('bajo', f, dur, vel)


def bajo_sinte(f, dur, vel=1.0):
    return _n('bajo', f, dur, vel)


def rhodes(f, dur, vel=1.0):
    return _n('rhodes', f, dur, vel)


def organo(f, dur, vel=1.0, registro='rock'):
    return _n('organo', f, dur, vel)


def piano(f, dur, vel=1.0):
    return _n('piano', f, dur, vel)


def clavinet(f, dur, vel=1.0, rng=_RNG):
    return _n('clav', f, dur, vel)


def cuerdas(f, dur, vel=1.0):
    return _n('cuerdas', f, dur, vel)


def bronces(f, dur, vel=1.0):
    return _n('bronces', f, dur, vel)


def pluck(f, dur, vel=1.0):
    return _n('pluck', f, dur, vel)


def nylon(f, dur, vel=1.0, rng=_RNG):
    return _n('nylon', f, dur, vel)


def ks(f, dur, brillo=0.5, decay=0.996, pos=0.18, rng=_RNG):
    return _n('dist', f, dur, 1.0)


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
    L = {k: [] for k in pistas}
    clic_buf = np.zeros(n)
    menor = fam in MENOR
    # tónica cómoda para la guitarra (E, A, D, G) y el bajo
    ton = tonica % 12
    if fam in ('rock', 'punk', 'metal'):
        ton = 4 if fam == 'metal' else (9 if ton not in (4, 9, 2, 7) else ton)

    def add(k, s, t0, g=1.0):
        if isinstance(s, np.ndarray):  # clic de metrónomo (audio)
            i0 = int(t0 * SR); e = min(n, i0 + len(s)); clic_buf[i0:e] += s[:e - i0] * g
            return
        t0 += rng.normal(0, 0.004)  # humanizar: músicos reales no caen exacto en la grilla
        for (off, m, d, v, kind) in s:
            if k == 'gtr_dist' and kind.startswith('gtr'):
                kind = 'dist' + kind[3:]
            vel = v * (0.75 + 0.25 * min(1.0, g)) * (0.92 + 0.12 * rng.random())
            L[k].append((t0 + off, m, d, min(1.0, vel), kind))

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
            ultimo = sec == 'final' and k == nb - 1
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
    return _mezcla(L, fam, nbars * bar, clic_buf, semilla)


def _a_acorde(m, pcs):
    return min((m + d for d in range(-2, 3)), key=lambda x: (min(abs((x - p) % 12) for p in pcs) != 0, abs(x - m)))


def _lead(add, fam, m, dur, t0):
    f = hz(m)
    if fam in ('rock', 'metal'):
        add('lead', [(0.0, m, dur, 0.9, 'dist_lead')], t0, 0.9)
    elif fam in ('funk', 'ska'):
        add('lead', bronces(f, dur, 0.9), t0, 0.55)
    elif fam == 'disco':
        add('lead', cuerdas(f, dur, 1.0) + cuerdas(f * 2, dur, 0.8), t0, 0.8)
    elif fam in ('hiphop', 'bossa'):
        add('lead', rhodes(f, dur, 0.7), t0, 0.35)
    elif fam == 'motown':
        add('lead', piano(f, dur, 0.9) + piano(f * 2, dur, 0.7), t0, 0.8)
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
                add('gtr', rasguido_muerto(g, 0.5 + 0.2 * (s % 2 == 0)), T(s), 0.6)
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
    out = []
    for j, notas in enumerate(lst):
        out += [(off + j * 0.009, m, d, v, k) for (off, m, d, v, k) in notas]
    return out


import os, subprocess, tempfile, wave as _wave

SF2 = [p for p in ('/home/claude/mrbumpy409/generaluser-gs/GeneralUser-GS.sf2', os.path.expanduser('~/sf/GeneralUser-GS.sf2'),
                   '/usr/share/sounds/sf2/FluidR3_GM.sf2') if os.path.exists(p)]

# programa General MIDI por tipo de sonido (0 = piano). Algunos cambian según el estilo.
PROGRAMA = {'piano': 0, 'rhodes': 4, 'organo': 16, 'clav': 7, 'cuerdas': 48, 'bronces': 61, 'pluck': 5, 'nylon': 24,
            'gtr': 27, 'gtr_m': 28, 'dist': 29, 'dist_m': 29, 'dist_lead': 29, 'bajo': 33}
POR_ESTILO = {
    'rock': {'bajo': 34, 'organo': 18}, 'punk': {'bajo': 34, 'dist': 30, 'dist_m': 30},
    'metal': {'bajo': 34, 'dist': 30, 'dist_m': 30, 'dist_lead': 30}, 'funk': {'bajo': 33},
    'hiphop': {'bajo': 32}, 'bossa': {'bajo': 32, 'pluck': 11}, 'reggaeton': {'bajo': 38, 'pluck': 25},
    'ska': {'organo': 16}, 'pop': {'pluck': 5},
}


def _render(notas, programa, semilla):
    """Toca las notas con un instrumento grabado (SoundFont) usando FluidSynth. Devuelve audio estéreo."""
    import pretty_midi
    pm = pretty_midi.PrettyMIDI()
    ins = pretty_midi.Instrument(program=programa)
    for (t, m, d, v, _k) in notas:
        if t < 0:
            d += t; t = 0.0
        if d <= 0.01 or not 0 < m < 128:
            continue
        vel = int(np.clip(28 + 99 * v ** 0.8, 1, 127))
        ins.notes.append(pretty_midi.Note(velocity=vel, pitch=int(m), start=float(t), end=float(t + d)))
    if not ins.notes:
        return None
    pm.instruments.append(ins)
    with tempfile.TemporaryDirectory() as td:
        mid = os.path.join(td, 'a.mid'); wav = os.path.join(td, 'a.wav')
        pm.write(mid)
        subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.5', '-R', '0', '-C', '0', '-r', str(SR), '-F', wav, SF2[0], mid],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        w = _wave.open(wav); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2) / 32767.0; w.close()
    return x


def _peak(x, f0, db, q=1.0):
    """Ecualizador de campana (fórmula RBJ): db negativo quita, positivo agrega."""
    A = 10 ** (db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0)


def _ir(seg=1.8, semilla=3):
    """Respuesta de una sala (reverb por convolución): ruido que decae, más oscuro con el tiempo, distinto en cada lado."""
    r = np.random.default_rng(semilla)
    t = np.arange(int(seg * SR)) / SR
    out = []
    for c in range(2):
        x = r.normal(size=len(t)) * np.exp(-t * 3.6)
        x = 0.6 * _lp(x, 6500) + 0.4 * _lp(x, 1800)
        x[:int(0.018 * SR)] = 0  # pre-delay
        out.append(x / np.sqrt(np.sum(x ** 2)))
    return np.stack(out, 1)


def _comp(x, umbral=-18.0, ratio=3.0, ataque=0.01, relajo=0.15):
    """Compresor simple (nivela los golpes para que la banda suene pareja y "pegada")."""
    m = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    a = np.exp(-1 / (ataque * SR)); r = np.exp(-1 / (relajo * SR))
    env = lfilter([1 - r], [1, -r], m)  # aproximación rápida del seguidor de envolvente
    env = np.maximum(env, lfilter([1 - a], [1, -a], m) * 0.7)
    db = 20 * np.log10(env + 1e-9)
    red = np.minimum(0, (umbral - db) * (1 - 1 / ratio))
    g = 10 ** (red / 20)
    return x * (g[:, None] if x.ndim == 2 else g)


def _mezcla(L, fam, largo_s, clic_buf, semilla):
    from scipy.signal import fftconvolve
    progs = dict(PROGRAMA); progs.update(POR_ESTILO.get(fam, {}))
    n = int(largo_s * SR) + SR * 3
    vol = {'gtr': 0.80, 'gtr_dist': 0.70, 'bajo': 0.85, 'teclas': 0.70, 'pad': 0.45, 'lead': 0.65, 'extra': 0.55}
    pan = {'gtr': -0.45, 'gtr_dist': 0.0, 'bajo': 0.0, 'teclas': 0.35, 'pad': 0.0, 'lead': 0.15, 'extra': 0.45}
    envio = {'gtr': 0.18, 'gtr_dist': 0.10, 'bajo': 0.0, 'teclas': 0.22, 'pad': 0.35, 'lead': 0.28, 'extra': 0.25}
    st = np.zeros((n, 2)); wet = np.zeros((n, 2))

    def poner(dst, x, g=1.0):
        e = min(n, len(x)); dst[:e] += x[:e] * g

    for k, notas in L.items():
        if not notas or k == 'clic':
            continue
        porkind = {}
        for nt in notas:
            porkind.setdefault(nt[4], []).append(nt)
        pista = np.zeros((n, 2))
        for kind, ns in porkind.items():
            x = _render(ns, progs.get(kind, 0), semilla)
            if x is None:
                continue
            if k == 'gtr_dist' and kind.startswith('dist') and kind != 'dist_lead':
                # doble toma: la misma parte tocada dos veces (con otra humanización), una a cada lado
                r2 = np.random.default_rng(semilla + 99)
                ns2 = [(t + r2.normal(0, 0.006), m, d, min(1, v * (0.95 + 0.1 * r2.random())), kk) for (t, m, d, v, kk) in ns]
                x2 = _render(ns2, progs.get(kind, 0), semilla + 1)
                mono1 = x.mean(1); mono2 = x2.mean(1) if x2 is not None else mono1
                e = min(len(mono1), len(mono2))
                x = np.stack([mono1[:e], mono2[:e]], 1) * 1.2
            poner(pista, x)
        if not pista.any():
            continue
        if k == 'bajo':
            mono = _hp(pista.mean(1), 35)
            mono = _comp(mono, -22, 4, 0.005, 0.12)
            pista = np.stack([mono, mono], 1) * 1.4
        else:
            pista = np.stack([_hp(pista[:, 0], 120 if k != 'pad' else 90), _hp(pista[:, 1], 120 if k != 'pad' else 90)], 1)
            if k != 'gtr_dist':
                p = pan[k]
                mono = pista.mean(1)
                ancho = pista[:, 0] - pista[:, 1]
                pista = np.stack([mono * np.sqrt((1 - p) / 2) * 1.414 + 0.5 * ancho,
                                  mono * np.sqrt((1 + p) / 2) * 1.414 - 0.5 * ancho], 1)
        if k != 'bajo':  # quitar "barro" (250-400 Hz) y dar presencia, como en una mezcla de estudio
            pista = _peak(pista, 320, -4.0, 0.9)
            if k in ('gtr', 'gtr_dist', 'lead'):
                pista = _peak(pista, 3000, 2.5, 0.8)
        else:
            pista = _peak(pista, 800, 2.0, 1.0)  # que el bajo se escuche también en parlantes chicos (celular)
        if fam == 'hiphop' and k in ('teclas', 'lead'):  # lo-fi: Rhodes más oscuro
            pista = np.stack([_lp(pista[:, 0], 5500), _lp(pista[:, 1], 5500)], 1)
        g = vol[k] * (0.7 if (k == 'bajo' and fam in ('metal', 'reggaeton')) else 1.0)
        st += pista * g
        wet += pista * vol[k] * envio[k]
    ir = _ir(1.6 if fam not in ('punk', 'metal') else 1.0, semilla)
    rev = np.stack([fftconvolve(wet[:, c], ir[:, c])[:n] for c in range(2)], 1)
    st += rev * 0.9
    st[:, 0] += clic_buf * 0.5; st[:, 1] += clic_buf * 0.5
    st = _comp(st, -16, 2.0, 0.015, 0.25)  # pegamento de la banda
    pico = np.abs(st).max() + 1e-9
    st = np.tanh(st / pico * 1.2) / np.tanh(1.2) * 0.85
    return st[:int(largo_s * SR)]

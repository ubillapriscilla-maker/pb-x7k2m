"""Batería grabada (sets reales del SoundFont GeneralUser GS) elegida según el estilo.

- Rock, punk y metal: "Power Kit" (bombo y caja grandes, con cuerpo).
- Funk, motown, disco, ska, reggae, hip-hop: "Room Kit" (batería de sala, seca y cercana, como en los discos de soul/funk;
  en hip-hop con filtro lo-fi, como un sample de vinilo).
- Pop y rudimentos: "Standard" (sonido neutro y claro).
- Bossa nova: "Jazz Kit" (caja más fina, platillos suaves).
- Reggaetón: "808/909" (bombo y caja electrónicos, como en el género).

Los golpes vienen de drumlib.build_events (el mismo patrón que se ve en la tablatura), así que lo que suena coincide con lo
que muestra el video.
"""
import os, subprocess, tempfile, wave
import numpy as np

import banda as B

SR = 44100
NOTA = {'timb_a': 65, 'timb_b': 66, 'rim': 38, 'kick': 36, 'snare': 38, 'aro': 37, 'hat': 42, 'ohat': 46, 'crash': 49, 'ride': 51, 't1': 50, 't2': 47, 't3': 43}
KIT = {'rock': 16, 'punk': 16, 'metal': 16, 'funk': 8, 'motown': 8, 'disco': 8, 'ska': 8, 'reggae': 8, 'hiphop': 8,
       'pop': 1, 'bossa': 32, 'reggaeton': 25}


# Ajuste por voz y estilo: (semitonos más agudo, dB, corte de graves Hz, brillo dB).
# Reggae: aro claro, agudo y presente (pedido de Priscilla); caja afinada aguda y seca, como en los discos de Jamaica;
# rimshot = palo en el parche y el aro a la vez (caja + aro juntos, más fuerte).
AJUSTE = {'reggae': {'aro': (4, 5.0, 350, 5.0), 'snare': (4, 1.0, 180, 3.0), 'rim': (4, 4.0, 180, 4.0),
                     'timb_a': (2, 3.0, 300, 4.0)}}
# Efecto propio de la timbaleta (Priscilla, 26 nov 2026): reverb tipo placa, brillante y larga, como en los discos de reggae.
CON_PLACA = {'timb_a'}


def familia(estilo):
    e = str(estilo).split('__')[0]
    return B.ESTILO_DE.get(e, 'rud' if e.startswith('rud_') else 'pop')


def render(ev, total, estilo, semilla=5, loop=True, eco_s=None):
    """ev: eventos de drumlib.build_events (t, voz, ganancia, ...). Devuelve audio estéreo de 'total' segundos.
    loop=True: la cola del final (platillos que siguen sonando) se suma al inicio para que el loop no se corte."""
    fam = familia(estilo)
    kit = KIT.get(fam, 0)
    rng = np.random.default_rng(semilla)
    notas = []
    for (t, voz, g, *resto) in ev:
        if voz not in NOTA:
            continue
        paso = resto[0] if resto else 0
        acento = 1.0 if paso % 4 == 0 else (0.9 if paso % 2 == 0 else 0.8)
        v = g * (acento if voz in ('hat', 'ride') else 1.0)
        base = {'timb_a': 110, 'timb_b': 108, 'rim': 118, 'kick': 112, 'snare': 108, 'aro': 100, 'hat': 92, 'ohat': 96, 'crash': 108, 'ride': 92}.get(voz, 105)
        vel = int(np.clip(base * v + rng.normal(0, 5), 30, 127))
        notas.append((max(0.0, t + rng.normal(0, 0.003)), NOTA[voz], vel, voz))
    aj = AJUSTE.get(fam, {})
    x = _fluid([nt for nt in notas if nt[3] not in aj], kit)
    from scipy.signal import resample
    for voz, (semis, db, hp, brillo) in aj.items():
        sel = [nt for nt in notas if nt[3] == voz]
        if not sel:
            continue
        if voz == 'rim':  # rimshot: caja y aro al mismo tiempo
            sel = sel + [(t, 37, v, vz) for (t, m, v, vz) in sel]
        fac = 2 ** (semis / 12)
        xa = _fluid([(t * fac, m, min(127, v + 8), vz) for (t, m, v, vz) in sel], kit)
        xa = resample(xa, int(len(xa) / fac), axis=0)  # afinar más agudo (y más corto, más seco)
        xa = B._hp(xa, hp)
        xa = B._peak(xa, 2800, brillo, 0.9) * 10 ** (db / 20)
        if voz in CON_PLACA:
            xa = placa(xa, eco_s)
        m = max(len(x), len(xa)); y = np.zeros((m, 2)); y[:len(x)] += x; y[:len(xa)] += xa; x = y
    n = int(total * SR)
    out = np.zeros((n, 2))
    e = min(n, len(x)); out[:e] = x[:e]
    if loop and len(x) > n:
        cola = x[n:]; m = min(n, len(cola)); out[:m] += cola[:m]
    return procesar(out, fam, semilla)


def placa(x, eco_s=None):
    """Reverb de placa (brillante, ~2 s) y, si se pide, eco tipo dub (repeticiones que se van apagando)."""
    from scipy.signal import fftconvolve
    r = np.random.default_rng(21)
    t = np.arange(int(2.2 * SR)) / SR
    ir = []
    for c in range(2):
        z = r.normal(size=len(t)) * np.exp(-t * 3.0)
        z = B._hp(B._lp(z, 9000), 400)
        z[:int(0.012 * SR)] = 0
        ir.append(z / np.sqrt(np.sum(z ** 2)))
    n = len(x) + len(t)
    xx = np.zeros((n, 2)); xx[:len(x)] = x
    wet = np.stack([fftconvolve(xx[:, c], ir[c])[:n] for c in range(2)], 1)
    y = xx + 0.55 * wet
    if eco_s:
        d = int(eco_s * SR)
        eco = np.zeros((n + 4 * d, 2)); eco[:n] = y
        for k in range(1, 4):
            g = 0.45 ** k
            eco[k * d:k * d + n, k % 2] += _lpf(y[:, k % 2], 3500 - 700 * k) * g
        y = eco
    return y


def _lpf(x, fc):
    return B._lp(x, max(800, fc))


def _fluid(notas, kit):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI()
    ins = pretty_midi.Instrument(program=kit, is_drum=True)
    for (t, m, vel, _v) in notas:
        ins.notes.append(pretty_midi.Note(velocity=int(vel), pitch=m, start=t, end=t + 0.2))
    if not ins.notes:
        return np.zeros((SR, 2))
    pm.instruments.append(ins)
    with tempfile.TemporaryDirectory() as td:
        mid = os.path.join(td, 'd.mid'); wav = os.path.join(td, 'd.wav')
        pm.write(mid)
        subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.6', '-R', '0', '-C', '0', '-r', str(SR), '-F', wav, B.SF2[0], mid],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        w = wave.open(wav); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2) / 32767.0; w.close()
    return x


def procesar(x, fam, semilla=5):
    """Mezcla de batería: graves del bombo, golpe de la caja, compresión paralela y un poco de sala."""
    from scipy.signal import fftconvolve
    y = B._hp(x, 30)
    y = B._peak(y, 60, 3.0, 1.0)      # cuerpo del bombo
    y = B._peak(y, 400, -3.0, 1.0)    # quitar "caja de cartón"
    y = B._peak(y, 4500, 2.0, 0.8)    # ataque y brillo de platillos
    aplastada = B._comp(y, -30, 8, 0.002, 0.08)  # compresión paralela (golpe con más cuerpo, sin perder dinámica)
    y = y + 0.5 * aplastada / (np.abs(aplastada).max() + 1e-9) * np.abs(y).max()
    ir = B._ir(0.7 if fam not in ('pop', 'reggaeton') else 1.0, semilla + 7)
    sala = np.stack([fftconvolve(y[:, c], ir[:, c])[:len(y)] for c in range(2)], 1)
    y = y + sala * (0.12 if fam != 'hiphop' else 0.06)
    if fam == 'hiphop':  # sonido de sample de vinilo: más oscuro y un poco saturado
        y = np.stack([B._lp(y[:, 0], 7000), B._lp(y[:, 1], 7000)], 1)
        y = np.tanh(y / (np.abs(y).max() + 1e-9) * 1.6)
    return y / (np.abs(y).max() + 1e-9) * 0.9


def mezclar(dr, mu, bateria_db=-16.0, banda_db=-20.0):
    """Mezcla final de una clase: la batería adelante (es lo que se enseña) y la banda unos 4 dB por debajo."""
    def rms(x):
        return np.sqrt(np.mean(x ** 2)) + 1e-9
    n = min(len(dr), len(mu))
    d = dr[:n] if dr.ndim == 2 else np.stack([dr[:n], dr[:n]], 1)
    m = mu[:n]
    x = d * (10 ** (bateria_db / 20) / rms(d)) + m * (10 ** (banda_db / 20) / rms(m))
    x = B._comp(x, -14, 2.0, 0.01, 0.2)
    return np.tanh(x / (np.abs(x).max() + 1e-9) * 1.3) / np.tanh(1.3) * 0.9

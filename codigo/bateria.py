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
NOTA = {'kick': 36, 'snare': 38, 'aro': 37, 'hat': 42, 'ohat': 46, 'crash': 49, 'ride': 51, 't1': 50, 't2': 47, 't3': 43}
KIT = {'rock': 16, 'punk': 16, 'metal': 16, 'funk': 8, 'motown': 8, 'disco': 8, 'ska': 8, 'reggae': 8, 'hiphop': 8,
       'pop': 1, 'bossa': 32, 'reggaeton': 25}


def familia(estilo):
    e = str(estilo).split('__')[0]
    return B.ESTILO_DE.get(e, 'rud' if e.startswith('rud_') else 'pop')


def render(ev, total, estilo, semilla=5, loop=True):
    """ev: eventos de drumlib.build_events (t, voz, ganancia, ...). Devuelve audio estéreo de 'total' segundos.
    loop=True: la cola del final (platillos que siguen sonando) se suma al inicio para que el loop no se corte."""
    import pretty_midi
    fam = familia(estilo)
    kit = KIT.get(fam, 0)
    rng = np.random.default_rng(semilla)
    pm = pretty_midi.PrettyMIDI()
    ins = pretty_midi.Instrument(program=kit, is_drum=True)
    for (t, voz, g, *resto) in ev:
        if voz not in NOTA:
            continue
        paso = resto[0] if resto else 0
        acento = 1.0 if paso % 4 == 0 else (0.9 if paso % 2 == 0 else 0.8)
        v = g * (acento if voz in ('hat', 'ride') else 1.0)
        base = {'kick': 112, 'snare': 108, 'aro': 100, 'hat': 92, 'ohat': 96, 'crash': 108, 'ride': 92}.get(voz, 105)
        vel = int(np.clip(base * v + rng.normal(0, 5), 30, 127))
        t0 = max(0.0, t + rng.normal(0, 0.003))
        ins.notes.append(pretty_midi.Note(velocity=vel, pitch=NOTA[voz], start=t0, end=t0 + 0.2))
    pm.instruments.append(ins)
    with tempfile.TemporaryDirectory() as td:
        mid = os.path.join(td, 'd.mid'); wav = os.path.join(td, 'd.wav')
        pm.write(mid)
        subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.6', '-R', '0', '-C', '0', '-r', str(SR), '-F', wav, B.SF2[0], mid],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        w = wave.open(wav); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2) / 32767.0; w.close()
    n = int(total * SR)
    out = np.zeros((n, 2))
    e = min(n, len(x)); out[:e] = x[:e]
    if loop and len(x) > n:
        cola = x[n:]; m = min(n, len(cola)); out[:m] += cola[:m]
    return procesar(out, fam, semilla)


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

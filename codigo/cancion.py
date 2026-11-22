import wave
import numpy as np
SR = 44100
PROG = [("C", [261.63, 329.63, 392.00], 130.81), ("G", [196.00, 246.94, 293.66], 98.00),
        ("Am", [220.00, 261.63, 329.63], 110.00), ("F", [174.61, 220.00, 261.63], 87.31)]
PENTA = [523.25, 587.33, 659.25, 783.99, 880.00]

def _add(mix, s, t0):
    n = len(mix); idx = (int(t0 * SR) + np.arange(len(s))) % n
    np.add.at(mix, idx, s)

def _pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for f in freqs:
        out += (np.sin(2*np.pi*f*t) + 0.3*np.sin(2*np.pi*2*f*t) + 0.15*np.sin(2*np.pi*3*f*t))
    att = np.minimum(1, t / 0.08); rel = np.minimum(1, (dur - t) / 0.25)
    return out / len(freqs) * att * rel

def _bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*2*f*t)) * np.exp(-t * 5) * np.minimum(1, t / 0.005)

def _pluck(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*2*f*t) + 0.2*np.sin(2*np.pi*3*f*t)) * np.exp(-t * 6) * np.minimum(1, t / 0.004)

def agregar_musica(path, ev, bpm, bars, relleno_inicio=None, tono=0, semilla=7):
    """Suma acordes, bajo (sigue al bombo) y melodia simple sobre el audio de bateria. Loop continuo."""
    w = wave.open(path); n = w.getnframes(); drums = np.frombuffer(w.readframes(n), dtype=np.int16).astype(float) / 32767; w.close()
    k = 2 ** (tono / 12.0); step = 60.0 / bpm / 4; bar = 16 * step
    pad = np.zeros(n); bass = np.zeros(n); mel = np.zeros(n)
    rng = np.random.default_rng(semilla)
    motivos = [[int(x) for x in rng.integers(0, 5, 4)] for _ in range(4)]
    for b in range(bars):
        nombre, acorde, raiz = PROG[b % 4]
        _add(pad, _pad([f * k for f in acorde], bar + 0.2), b * bar)
        mot = motivos[(b // 4 * 2 + b % 4) % 4] if (b // 4) % 2 else motivos[b % 4]
        for j, st in enumerate((0, 4, 8, 12)):
            if relleno_inicio is not None and b % 4 == 3 and st >= relleno_inicio:
                continue
            if st == 0 and b % 2 == 1 and j == 0: pass
            _add(mel, _pluck(PENTA[mot[j]] * k, step * 3.5), (b * 16 + st) * step)
    for (t, voz, g, *_r) in ev:
        if voz == "kick":
            b = int(t // bar) % bars
            _add(bass, _bass(PROG[b % 4][2] * k, step * 3), t)
    music = pad * 0.16 + bass * 0.55 + mel * 0.14
    mix = drums * 0.85 + music
    mix = np.tanh(mix * 1.1); mix = mix / max(1e-9, np.abs(mix).max()) * 0.9
    with wave.open(path, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
        o.writeframes((mix * 32767).astype(np.int16).tobytes())

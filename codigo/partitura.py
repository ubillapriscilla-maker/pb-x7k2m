"""Convierte un ritmo de 16 pasos (hits de drumlib) en partitura de batería PNG con LilyPond.
Uso desde Python: png = partitura(hits, ruta_png)"""
import os, subprocess, tempfile, shutil

try:
    import lilypond
    LY = str(lilypond.executable())
except Exception:
    LY = shutil.which('lilypond') or 'lilypond'

MANOS = {'hat': 'hh', 'ohat': 'hho', 'ride': 'cymr', 'crash': 'cymc', 't1': 'tomh', 't2': 'tommh', 't3': 'tomfl', 'snare': 'sn'}
PIES = {'kick': 'bd'}
DUR = {1: '16', 2: '8', 3: '8.', 4: '4'}
RES = {1: 'r16', 2: 'r8', 3: 'r8.', 4: 'r4'}


def _voz(hits, mapa, compases=1):
    pasos = []
    for s in range(16):
        ns = [mapa[v] for v in mapa if v in hits and hits[v][s] == 'x']
        pasos.append(ns)
    out = []
    for b in range(4):
        pos = [i for i in range(4) if pasos[b * 4 + i]]
        if not pos:
            out.append('r4'); continue
        if pos[0] > 0: out.append(RES[pos[0]])
        for j, p in enumerate(pos):
            fin = pos[j + 1] if j + 1 < len(pos) else 4
            ns = pasos[b * 4 + p]
            nota = ns[0] if len(ns) == 1 else '<' + ' '.join(ns) + '>'
            out.append(nota + DUR[fin - p])
    return ' '.join(out * compases)


def ly_codigo(hits, compases=1):
    arriba = _voz(hits, MANOS, compases)
    abajo = _voz(hits, PIES, compases)
    return r'''\version "2.24.0"
\paper { indent = 0 ragged-right = ##t line-width = 150\mm top-margin = 2\mm bottom-margin = 2\mm left-margin = 2\mm
  oddFooterMarkup = ##f oddHeaderMarkup = ##f evenHeaderMarkup = ##f evenFooterMarkup = ##f }
\header { tagline = ##f }
\layout { #(layout-set-staff-size 26) }
\new DrumStaff \with { \override StaffSymbol.thickness = #1.2 }
\drummode { \numericTimeSignature \time 4/4 << { \voiceOne %s } \\ { \voiceTwo %s } >> \bar "|." }
''' % (arriba, abajo)


def partitura(hits, png, compases=1):
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, 'p.ly')
    open(src, 'w').write(ly_codigo(hits, compases))
    r = subprocess.run([LY, '-dbackend=eps', '-dno-gs-load-fonts', '-dinclude-eps-fonts', '--png', '-dresolution=300',
                        '-dcrop', '-o', os.path.join(tmp, 'p'), src], capture_output=True, text=True)
    cand = [f for f in os.listdir(tmp) if f.endswith('.png')]
    pick = [f for f in cand if 'cropped' in f] or cand
    if not pick:
        raise RuntimeError(r.stderr[-800:])
    shutil.copy(os.path.join(tmp, pick[0]), png)
    shutil.rmtree(tmp, ignore_errors=True)
    return png


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import drumlib as D
    for k in ['rock_basico', 'disco', 'funk_16avos', 'reggae_one_drop']:
        print(partitura(D.ESTILOS[k]['hits'], f'/tmp/part_{k}.png'))

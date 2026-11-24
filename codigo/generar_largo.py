"""Uso: python3 generar_largo.py N   -> crea largos/largoNN_*.mp4/.png y largos/info_NN.json (en /home/claude/shorts/largos)"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_largo as B, drumlib as D, largos_tabla as T
ADJ = {1: 'fácil', 2: 'básico', 3: 'intermedio', 4: 'avanzado', 5: 'experto'}
def mmss(x): return f"{int(x//60)}:{int(x%60):02d}"
def generar(n):
    d = T.largo_datos(n); est = d['estilo']; niv = d['nivel']
    bpms = [d['bpm0'] + 5 * i for i in range(5)]
    nombre = f"largo{n:02d}_{est}_{bpms[0]}_a_{bpms[-1]}bpm"
    out, caps, t = B.construir(nombre, est, bpms, d['relleno'], d['tema'], niv, tono=d['tono'])
    nm = D.ESTILOS[est]['nombre']; rl = D.RELLENOS[d['relleno']]['nombre'].lower()
    B.miniatura(nombre, 'TOCA BATERÍA\n' + nm.upper()[:16], f"{bpms[0]} a {bpms[-1]} BPM  ·  Nivel {niv}", d['tema'])
    cap = '\n'.join(f"{mmss(c[0])} {c[1]} BPM" for c in caps)
    titulo = f"Cómo tocar batería: ritmo {ADJ[niv]} de {nm.lower()} de {bpms[0]} a {bpms[-1]} BPM (práctica con canción)"
    desc = (f"Práctica de batería: ritmo {ADJ[niv]} de {nm.lower()}, con una canción hecha para estudiar.\n"
            f"Mira la tablatura de izquierda a derecha y toca junto con el video. Cada 4 compases hay un relleno: {rl}.\n"
            f"Empieza a {bpms[0]} BPM y sube de 5 en 5 hasta {bpms[-1]} BPM. Cuando te salga limpio, pasa a la siguiente velocidad.\n\n"
            f"Capítulos:\n{cap}\n\nEs parte de un curso de batería para principiantes. El sonido de la batería y la música son sintéticos, hechos para estudiar.\n\n"
            "#batería #comotocarbateria #aprenderbatería #ritmosdebatería #practicabatería")
    info = dict(n=n, archivo=os.path.basename(out), miniatura=nombre + '.png', titulo=titulo, descripcion=desc, duracion=round(t, 1),
                tags=["cómo tocar batería", "ritmos de batería para principiantes", "batería para principiantes", "práctica de batería", "aprender batería", nm.lower(), f"{bpms[0]} bpm"])
    json.dump(info, open(f'/home/claude/shorts/largos/info_{n:02d}.json', 'w'), ensure_ascii=False, indent=1)
    return info
if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(generar(int(a))['archivo'], flush=True)

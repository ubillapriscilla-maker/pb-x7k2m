"""Largos serie B (determinista): impares = play-along SIN bateria (toca tu encima); pares = cancion de dominio publico con ritmo de bateria.
Uso: python3 largos_b.py N [N ...] -> crea largos_b/lbNN_*.mp4/.png y largos_b/info_NN.json"""
import sys, os, json
sys.path.insert(0, '/home/claude/shorts')
import drumlib as D, build_largo as B
from canciones_pd import CANCIONES
OUT = '/home/claude/shorts/largos_b'
PA_ESTILOS = ['rock_basico', 'rock_bombo_extra', 'bombo_y_caja', 'hat_negras', 'rock_sincopado', 'pop_4_al_piso', 'ska', 'motown', 'ride_rock',
              'hiphop_boom_bap', 'reggae_one_drop', 'disco', 'reggaeton', 'rock_16avos', 'medio_tiempo', 'funk_16avos']
PD_ESTILOS = ['rock_basico', 'hat_negras', 'pop_4_al_piso', 'ska', 'motown', 'rock_bombo_extra', 'disco', 'hiphop_boom_bap']
PD_ORDEN = ['oda', 'estrellita', 'corderito']
TEMAS = ['noche', 'neon', 'papel', 'atardecer', 'bosque', 'retro']
TONOS = [0, 2, -2, 5, 3]


def datos(n):
    if n % 2 == 1:
        i = (n - 1) // 2
        est = PA_ESTILOS[i % len(PA_ESTILOS)]; ciclo = i // len(PA_ESTILOS)
        lo, hi = D.ESTILOS_TODOS[est]['bpm']
        b0 = max(60, lo) + 10 * ciclo
        return dict(n=n, tipo='pa', estilo=est, bpm0=b0, tema=TEMAS[n % 6], nivel=D.ESTILOS_TODOS[est]['nivel'], tono=TONOS[i % 5], cancion=None)
    i = n // 2 - 1
    can = PD_ORDEN[i % 3]; j = i // 3
    est = PD_ESTILOS[j % len(PD_ESTILOS)]; ciclo = j // len(PD_ESTILOS)
    lo, hi = D.ESTILOS_TODOS[est]['bpm']
    b0 = max(60, lo) + 10 * ciclo
    return dict(n=n, tipo='pd', estilo=est, bpm0=b0, tema=TEMAS[(n + 1) % 6], nivel=D.ESTILOS_TODOS[est]['nivel'], tono=0, cancion=can)


ADJ = {1: 'fácil', 2: 'básico', 3: 'intermedio', 4: 'avanzado', 5: 'experto'}
def mmss(x): return f"{int(x // 60)}:{int(x % 60):02d}"


def generar(n):
    os.makedirs(OUT, exist_ok=True)
    d = datos(n); est = d['estilo']; niv = d['nivel']; nm = D.ESTILOS_TODOS[est]['nombre']
    bpms = [d['bpm0'] + 5 * i for i in range(5)]
    if d['tipo'] == 'pa':
        nombre = f"lb{n:02d}_playalong_{est}_{bpms[0]}_a_{bpms[-1]}bpm"
        out, caps, t = B.construir(nombre, est, bpms, 'ninguno', d['tema'], niv, tono=d['tono'], drums_gain=0.0, sub='Sin batería: la tocas tú, con clic', bars=8)
        B.miniatura(nombre, 'TOCA TU BATERÍA\nSIN BATERÍA', f"{nm}  ·  {bpms[0]} a {bpms[-1]} BPM", d['tema'])
        titulo = f"Play along de batería sin batería: ritmo de {nm.lower()} de {bpms[0]} a {bpms[-1]} BPM | Toca encima"
        intro = (f"Play along para bateristas: una canción hecha para estudiar SIN la batería, para que la toques tú encima. Suena un clic suave en cada tiempo.\n"
                 f"Sigue en pantalla la tablatura del ritmo de {nm.lower()} (nivel {ADJ[niv]}) y tócalo junto con el video.\n")
        tags = ["play along batería", "play along para bateristas", "toca batería sin batería", "backing track batería", "práctica de batería",
                "aprender batería", nm.lower(), f"{bpms[0]} bpm"]
        tag_h = "#playalong #batería #bateria #backingtrack #practicabatería"
    else:
        c = CANCIONES[d['cancion']]
        nombre = f"lb{n:02d}_{d['cancion']}_{est}_{bpms[0]}_a_{bpms[-1]}bpm"
        pd = dict(acordes=c['acordes'], notas=c['notas'], compases=c['compases'])
        out, caps, t = B.construir(nombre, est, bpms, 'ninguno', d['tema'], niv, musica=True, tono=0, drums_gain=0.85, pd=pd,
                                   sub=f"Canción: {c['nombre']} (dominio público)", bars=c['compases'])
        B.miniatura(nombre, 'BATERÍA CON\n' + c['nombre'].upper()[:16], f"{nm}  ·  {bpms[0]} a {bpms[-1]} BPM", d['tema'])
        titulo = f"Batería con \"{c['nombre']}\": ritmo de {nm.lower()} de {bpms[0]} a {bpms[-1]} BPM | Con tablatura"
        intro = (f"Practica batería con una canción que cualquiera puede usar: \"{c['nombre']}\", {c['autor']}. La música y la batería son sintéticas, hechas para estudiar.\n"
                 f"Sigue en pantalla la tablatura del ritmo de {nm.lower()} (nivel {ADJ[niv]}) y tócalo junto con el video.\n")
        tags = [f"batería {c['nombre'].lower()}", "canciones de dominio público", "cómo tocar batería", "batería para principiantes",
                "práctica de batería", "aprender batería", nm.lower(), f"{bpms[0]} bpm"]
        tag_h = "#batería #bateria #canciones #comotocarbateria #practicabatería"
    cap = '\n'.join(f"{mmss(c0[0])} {c0[1]} BPM" for c0 in caps)
    desc = (intro + f"Empieza a {bpms[0]} BPM y sube de 5 en 5 hasta {bpms[-1]} BPM. Cuando te salga limpio, pasa a la siguiente velocidad.\n\n"
            f"Capítulos:\n{cap}\n\nEs parte de un curso de batería para principiantes.\n\n" + tag_h)
    assert len(titulo) <= 100, (len(titulo), titulo)
    info = dict(n=n, archivo=os.path.basename(out), miniatura=nombre + '.png', titulo=titulo, descripcion=desc, duracion=round(t, 1), tags=tags)
    json.dump(info, open(f'{OUT}/info_{n:02d}.json', 'w'), ensure_ascii=False, indent=1)
    return info


if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(generar(int(a))['archivo'], flush=True)

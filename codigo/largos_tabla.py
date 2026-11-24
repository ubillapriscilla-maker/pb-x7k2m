"""Tabla determinista de videos largos: n -> configuracion. Cualquier sesion puede regenerar el largo n."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drumlib as D

FIJOS = {  # los primeros 9, ya publicados o listos
 1: ('rock_basico', 60, 'redoble_1', 'noche', 1, 0),
 2: ('rock_bombo_extra', 60, 'redoble_1', 'neon', 1, 2),
 3: ('bombo_y_caja', 60, 'redoble_1', 'bosque', 1, 5),
 4: ('hat_negras', 60, 'redoble_1', 'atardecer', 1, 7),
 5: ('rock_sincopado', 60, 'redoble_1', 'retro', 1, -2),
 6: ('ride_rock', 60, 'redoble_1', 'noche', 2, 3),
 7: ('pop_4_al_piso', 65, 'redoble_1', 'neon', 2, 0),
 8: ('disco', 65, 'redoble_1', 'atardecer', 2, 4),
 9: ('hiphop_boom_bap', 60, 'redoble_1', 'bosque', 2, -3),
}
BLOQUES = [(2, 1), (1, 1), (3, 0), (2, 2), (4, 0), (3, 1), (5, 0), (1, 2), (4, 1), (5, 1), (3, 2), (5, 2)]
REL = {1: 'redoble_1', 2: 'redoble_1', 3: 'toms_bajada', 4: 'redoble_2', 5: 'paradiddle_toms'}
INICIO = {1: 60, 2: 60, 3: 65, 4: 70, 5: 75}
TEMAS = ['noche', 'neon', 'papel', 'atardecer', 'bosque', 'retro']
TONOS = [0, 2, 5, 7, -2, 3, 4, -3]

def cfg(n):
    if n in FIJOS: return FIJOS[n]
    # n=10: ultimo estilo de nivel 2 (reggae). Despues, bloques (nivel, pasada) en orden
    if n == 10: return ('reggae_one_drop', 60, 'redoble_1', 'papel', 2, 6 % 8 and TONOS[6])
    k = n - 11
    for niv, pasada in BLOQUES:
        est = [e for e, v in D.ESTILOS.items() if v['nivel'] == niv]
        if k < len(est):
            bpm = min(INICIO[niv] + 10 * pasada, 100)
            return (est[k], bpm, REL[niv], TEMAS[n % 6], niv, TONOS[n % 8])
        k -= len(est)
    k = n - 11  # ciclo de nuevo desde el principio con mas velocidad
    return cfg(10 + 1 + (k % 40)) if n < 200 else cfg(11)

def largo_datos(n):
    est, b0, rel, tema, niv, tono = cfg(n)
    return dict(n=n, estilo=est, bpm0=b0, relleno=rel, tema=tema, nivel=niv, tono=tono)

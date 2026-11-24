"""Serie B de Shorts: rudimentos, generos nuevos y redobles por tecnica. Determinista: plan_b(N) siempre da lo mismo.
Uso: python3 serie_b.py N1 N2 ...  -> renderiza los Shorts B con esos numeros en /home/claude/shorts/serie_b/"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drumlib as D

RUD = ["rud_simple", "rud_doble", "rud_paradiddle", "rud_simple_bombo", "rud_paradiddle_inv", "rud_doble_bombo", "rud_paradiddle_bombo"]
GEN = ["ska", "motown", "reggaeton", "bossa_nova"]
GEN_REL = ["ninguno", "redoble_1", "toms_bajada", "redoble_2"]
BASES = ["rock_basico", "pop_4_al_piso", "hat_negras", "ride_rock", "rock_16avos", "medio_tiempo", "disco", "hiphop_boom_bap"]
FILLS = ["redoble_tom1", "redoble_dos_toms", "redoble_caja_tom", "redoble_2", "paradiddle", "redoble_toms", "toms_bajada", "redoble_1"]
NIV_FILL = {"redoble_1": 2, "redoble_tom1": 2, "toms_bajada": 3, "redoble_2": 3, "redoble_dos_toms": 3, "redoble_caja_tom": 4, "paradiddle": 4, "redoble_toms": 4}
HOOK = {"rud": ("MANOS EN ORDEN", "Sigue las letras R y L"), "gen": ("UN RITMO NUEVO", "Mira y toca conmigo"),
        "tec": ("NUEVO REDOBLE", "Entra al final de cada 4 compases")}
# Identidad visual fija: fondo crema (tema 'papel'), igual que la serie A.
TEMA_FIJO = "papel"
TIPOS = ["rud", "gen", "tec"]


TEMPOS_GEN = {"ska": [110, 130, 100, 120, 140], "motown": [100, 120, 105, 125, 110],
              "reggaeton": [90, 70, 100, 80, 95], "bossa_nova": [80, 100, 120, 90, 110]}
GANCHOS_GEN = ["Este ritmo de {g} suena pro: tócalo a {b} BPM{r} #shorts",
               "¿Sabes tocar {g} en batería? Así va a {b} BPM{r} #shorts",
               "El ritmo de {g} que todo baterista debería saber ({b} BPM){r} #shorts",
               "Así se toca {g} en batería a {b} BPM{r} #shorts"]


def plan_b(total=200):
    usados = {(x["estilo"], x["bpm"], x["relleno"]) for x in D.plan(180)}
    out, k = [], {"rud": 0, "gen": 0, "tec": 0}
    for n in range(1, total + 1):
        tipo = TIPOS[(n - 1) % 3]; i = k[tipo]; k[tipo] += 1
        if tipo == "rud":
            est = RUD[i % len(RUD)]; a = i // len(RUD); st = D.ESTILOS_TODOS[est]
            bpm = 60 + 5 * a; rel = "ninguno"; niv = st["nivel"]
        elif tipo == "gen":
            est = GEN[i % len(GEN)]; a = i // len(GEN); st = D.ESTILOS_TODOS[est]
            bpm = st["bpm"][0] + 5 * (a // len(GEN_REL)); rel = GEN_REL[(a + i % len(GEN)) % len(GEN_REL)]; niv = st["nivel"]
            if n >= 5 and est in TEMPOS_GEN:  # tempos reales y variados (>= 20 BPM entre videos seguidos del mismo estilo)
                bpm = TEMPOS_GEN[est][a % len(TEMPOS_GEN[est])]
        else:
            rel = FILLS[i % len(FILLS)]; a = i // len(FILLS)
            est = BASES[(i + a) % len(BASES)]; bpm = 60 + 5 * a; niv = NIV_FILL[rel]
        while (est, bpm, rel) in usados:
            bpm += 5
        usados.add((est, bpm, rel))
        out.append(dict(n=n, tipo=tipo, nivel=niv, estilo=est, bpm=bpm, relleno=rel, tema=TEMA_FIJO, diseno="tablatura",
                        hook=HOOK[tipo]))
    return out


ADJ = {1: "fácil", 2: "básico", 3: "intermedio", 4: "avanzado", 5: "experto"}


def meta_b(c):
    st = D.ESTILOS_TODOS[c["estilo"]]; rl = D.RELLENOS[c["relleno"]]; bpm = c["bpm"]
    pie = ("#shorts #batería #bateria #comotocarbateria #aprenderbatería")
    cierre = ("Mira la tablatura de izquierda a derecha, deja el video en repetición y toca junto con él. Cuando te salga limpio, sube 5 BPM.\n"
              "Es parte de un curso de batería para principiantes. El sonido de la batería es sintético, hecho para estudiar.\n\n")
    if c["tipo"] == "rud":
        titulo = f"Rudimento de batería: {st['nombre']} a {bpm} BPM | Cómo tocar batería #shorts"
        desc = (f"Rudimento de batería a {bpm} BPM: {st['nombre']}. Las letras R y L indican qué mano toca cada golpe (R derecha, L izquierda).\n"
                "Los rudimentos son la base de los redobles y de la velocidad en la batería.\n" + cierre + pie + " #rudimentos #rudimentosdebateria")
        tags = ["rudimentos de batería", "rudimentos batería principiantes", "paradiddle", "cómo tocar batería", "ejercicios de batería",
                "manos batería", f"{bpm} bpm", "tablatura batería", "shorts"]
    elif c["tipo"] == "gen":
        titulo = f"Ritmo de {st['nombre'].lower()} en batería a {bpm} BPM | Cómo tocar batería #shorts"
        if c["n"] >= 5:
            r = "" if c["relleno"] == "ninguno" else " + " + rl["nombre"].lower()
            for k in range(len(GANCHOS_GEN)):
                titulo = GANCHOS_GEN[((c["n"] // 3) + k) % len(GANCHOS_GEN)].format(g=st["nombre"].lower(), b=bpm, r=r)
                if len(titulo) <= 100: break
        extra = f"Cada 4 compases hay un relleno: {rl['nombre'].lower()}.\n" if c["relleno"] != "ninguno" else "Ritmo constante para practicar el groove.\n"
        desc = f"Cómo tocar el ritmo de {st['nombre'].lower()} en batería a {bpm} BPM (nivel {ADJ[c['nivel']]}).\n" + extra + cierre + pie + " #ritmosdebatería"
        tags = [f"ritmo de {st['nombre'].lower()} batería", f"cómo tocar {st['nombre'].lower()} en batería", "cómo tocar batería", "ritmos de batería",
                "aprender batería", f"{bpm} bpm", "tablatura batería", "shorts"]
    else:
        titulo = f"Cómo tocar: {rl['nombre']} a {bpm} BPM | Redobles de batería #shorts"
        desc = (f"Cómo tocar un redoble en batería: {rl['nombre'].lower()}, sobre un ritmo de {st['nombre'].lower()} a {bpm} BPM (nivel {ADJ[c['nivel']]}).\n"
                "El redoble entra al final de cada 4 compases y después vuelve el ritmo con un crash.\n" + cierre + pie + " #redobles #redoblesdebateria")
        tags = ["redobles de batería", "cómo tocar un redoble", "redobles para principiantes", "cómo tocar batería", "fills de batería",
                rl["nombre"].lower(), f"{bpm} bpm", "tablatura batería", "shorts"]
    assert len(titulo) <= 100, (len(titulo), titulo)
    return dict(titulo=titulo, descripcion=desc, tags=tags)


def archivo_b(c):
    return f"b{c['n']:03d}_{c['tipo']}_{c['estilo']}_{c['bpm']}bpm.mp4"


def guardar_csv(ruta, total=200):
    pb = plan_b(total)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["n", "archivo", "titulo", "descripcion", "etiquetas"])
        for c in pb:
            m = meta_b(c); w.writerow([c["n"], archivo_b(c), m["titulo"], m["descripcion"], ",".join(m["tags"])])
    return pb


if __name__ == "__main__":
    os.makedirs("/home/claude/shorts/serie_b", exist_ok=True)
    pb = plan_b()
    for a in sys.argv[1:]:
        c = pb[int(a) - 1]
        out = "/home/claude/shorts/serie_b/" + archivo_b(c)
        D.render(c, out); print(out, flush=True)

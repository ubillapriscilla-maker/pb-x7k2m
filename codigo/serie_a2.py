"""Serie A v2: Shorts con VARIACIONES de bombo, caja y hi-hat dentro de cada estilo, segun nivel.
Cada variacion sale una vez; un mismo estilo no vuelve hasta varios Shorts despues y, cuando vuelve,
su BPM difiere al menos 20 del anterior.
Uso:
  python3 serie_a2.py plan          -> reescribe filas n>=5 de plan/titulos_shorts.csv (no toca n<=4)
  python3 serie_a2.py N1 N2 ...     -> renderiza esos n en $OUT_A2 (por defecto /home/claude/shorts/serie_a2)"""
import sys, os, csv, copy
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import drumlib as D

OUT = os.environ.get('OUT_A2', '/home/claude/shorts/serie_a2')
ULT = 4      # n <= 4 ya publicados o fijos
TOTAL = 180
SEP = 4      # un estilo no se repite dentro de los ultimos SEP Shorts


def _set(p, pasos, c='x'):
    p = list(p)
    for i in pasos: p[i] = c
    return ''.join(p)


def _quita(p, pasos):
    return _set(p, pasos, '-')


# (clave, etiqueta corta, voz, sube nivel, nivel minimo, funcion sobre hits)
MODS = [
    ('h4', 'hi-hat en negras', 'H', 0, 1, lambda h: {**h, 'hat': 'x---x---x---x---'}),
    ('hab', 'hi-hat abierto en el y del 4', 'H', 0, 2,
     lambda h: {**h, 'hat': _quita(h['hat'], [14]), 'ohat': _set(h.get('ohat', '-' * 16), [14])}),
    ('ride', 'en el ride', 'H', 0, 2, lambda h: {**{k: v for k, v in h.items() if k != 'hat'}, 'ride': h['hat']}),
    ('h16', 'hi-hat en semicorcheas', 'H', 1, 2, lambda h: {**h, 'hat': 'x' * 16}),
    ('ky2', 'bombo en el y del 2', 'K', 0, 1, lambda h: {**h, 'kick': _set(h['kick'], [6])}),
    ('ky3', 'bombo en el y del 3', 'K', 0, 1, lambda h: {**h, 'kick': _set(h['kick'], [10])}),
    ('ky4', 'bombo en el y del 4', 'K', 0, 1, lambda h: {**h, 'kick': _set(h['kick'], [14])}),
    ('ke3', 'bombo en la e del 3', 'K', 1, 2, lambda h: {**h, 'kick': _set(h['kick'], [9])}),
    ('ka4', 'bombo en el a del 4', 'K', 1, 3, lambda h: {**h, 'kick': _set(h['kick'], [15])}),
    ('sy4', 'caja extra en el y del 4', 'S', 0, 2, lambda h: {**h, 'snare': _set(h['snare'], [14])}),
    ('sa4', 'caja extra en el a del 4', 'S', 1, 3, lambda h: {**h, 'snare': _set(h['snare'], [15])}),
]
# Voces que NO se tocan en cada estilo (son su identidad)
FIJAS = {
    'bombo_y_caja': 'H', 'hat_negras': 'H', 'rock_16avos': 'H', 'funk_16avos': 'H', 'disco': 'HK',
    'pop_4_al_piso': 'K', 'reggae_one_drop': 'SK', 'blast_beat': 'HKS', 'metal_doble_bombo': 'K',
    'doble_bombo_corto': 'K', 'metal_galope': 'K', 'funk_abierto': 'H', 'ride_rock': 'H',
}


def variantes(est):
    base = D.ESTILOS[est]; fij = FIJAS.get(est, ''); h0 = base['hits']
    ok = [m for m in MODS if m[2] not in fij and (m[2] != 'H' or 'hat' in h0)]
    out, vistos = [], {repr(sorted(h0.items()))}
    for a in range(len(ok)):
        for b in [None] + list(range(a + 1, len(ok))):
            ms = [ok[a]] + ([ok[b]] if b is not None else [])
            if len({m[2] for m in ms}) < len(ms): continue          # una sola variacion por voz
            h = copy.deepcopy(h0)
            try:
                for m in ms: h = m[5](h)
            except KeyError:
                continue
            key = repr(sorted(h.items()))
            if key in vistos: continue
            vistos.add(key)
            niv = min(5, max([base['nivel']] + [m[4] for m in ms]) + sum(m[3] for m in ms))
            etiqueta = ' y '.join(m[1] for m in ms)
            out.append(dict(clave=f"{est}__{'_'.join(m[0] for m in ms)}", base=est, nivel=niv, hits=h,
                            nombre=f"{base['nombre']} + {' + '.join(m[1] for m in ms)}" if not etiqueta.startswith('en ') else f"{base['nombre']} {etiqueta}",
                            corto=etiqueta, bpm=base['bpm']))
    out.sort(key=lambda v: (v['nivel'], v['clave'].count('_')))
    return out


def registrar():
    todas = {}
    for est in list(D.ESTILOS):
        if '__' in est: continue
        for v in variantes(est):
            e = dict(nombre=v['nombre'], nivel=v['nivel'], bpm=v['bpm'], hits=v['hits'])
            D.ESTILOS[v['clave']] = e; D.ESTILOS_TODOS[v['clave']] = e; todas[v['clave']] = v
    return todas


VARS = registrar()

# Identidad visual fija: fondo crema (tema 'papel'), el que mejor rindio en las primeras pruebas (22 nov 2026).
TEMA_FIJO = "papel"


def plan_a2(total=TOTAL):
    porest = {}
    for v in VARS.values(): porest.setdefault(v['base'], []).append(v)
    for l in porest.values(): l.sort(key=lambda v: (v['nivel'], v['clave'].count('_'), v['clave']))
    usadas, ult, ult_bpm, nvis, out = set(), {}, {}, {}, []
    temas = list(D.TEMAS)
    for n in range(ULT + 1, total + 1):
        tope = min(5, 2 + (n - 1) // 40)      # el nivel maximo sube cada ~10 dias
        recientes = [c['base'] for c in out[-SEP:]]
        cands = []
        for t in range(tope, 6):
            for sep in (recientes, recientes[-1:]):
                for est, l in porest.items():
                    libres = [v for v in l if v['clave'] not in usadas and v['nivel'] <= t]
                    if libres and est not in sep: cands.append((ult.get(est, -99), nvis.get(est, 0), est, libres[0]))
                if cands: break
            if cands: break
        cands.sort(key=lambda t: (t[0], t[1], t[2]))
        _, _, est, v = cands[0]
        lo, hi = v['bpm']
        pasos = list(range(max(60, lo), hi + 1, 5)) or [lo]
        ant = ult_bpm.get(est)
        lejos = [b for b in pasos if ant is None or abs(b - ant) >= 20] or [max(pasos, key=lambda b: abs(b - ant))]
        bpm = lejos[0] if nvis.get(est, 0) % 2 == 0 else lejos[-1]
        rels = D.ORDEN_REL[v['nivel']]
        rel = rels[nvis.get(est, 0) % len(rels)]
        usadas.add(v['clave']); ult[est] = n; ult_bpm[est] = bpm; nvis[est] = nvis.get(est, 0) + 1
        out.append(dict(dia=n, nivel=v['nivel'], estilo=v['clave'], base=est, bpm=bpm, relleno=rel,
                        tema=TEMA_FIJO, diseno=D.DISENOS[0]))
    return out


CANAL = "https://www.youtube.com/@priscillaubillasoriano"
GUIA_PDF = "https://drive.google.com/file/d/1t8sIDXStLzZWBQjdaUPORjTc5MmYwaYb/view"
GANCHOS = [
    "Este ritmo de {e} suena pro y es {adj}: {v} a {b} BPM",
    "¿Te sale este ritmo de {e}? {v} a {b} BPM (nivel {adj})",
    "El cambio que hace sonar mejor tu {e}: {v} | nivel {adj}, {b} BPM",
    "Ritmo de {e} con {v} a {b} BPM: tócalo conmigo (nivel {adj})",
    "Prueba este ritmo de {e} a {b} BPM: {v} (nivel {adj})",
    "Así suena el {e} con {v} | Batería nivel {adj}, {b} BPM",
]


def meta_gancho(c):
    m = D.meta(c)
    v = VARS.get(c['estilo'])
    adj = {1: "fácil", 2: "básico", 3: "intermedio", 4: "avanzado", 5: "experto"}[c['nivel']]
    if not v:
        return m
    e = D.ESTILOS[v['base']]['nombre']
    e = e[0].lower() + e[1:] if not e.split()[0].isupper() else e
    var = v['corto'].replace('en el ride', 'ride')
    t = None
    for k in range(len(GANCHOS)):
        cand = GANCHOS[(c['dia'] + k) % len(GANCHOS)].format(e=e, v=var, b=c['bpm'], adj=adj)
        if len(cand) <= 91: t = cand + " #shorts"; break
        if len(cand) <= 100: t = cand; break
    if t is None:
        t = f"Ritmo de {e} a {c['bpm']} BPM (nivel {adj})"
    m['titulo'] = t
    m['descripcion'] = m['descripcion'].replace(
        "Es parte de un curso de batería para principiantes. Sigue la serie para ir subiendo de nivel.",
        "Es parte de un curso de batería para principiantes. Sigue la serie para ir subiendo de nivel.\n"
        "Practica más tiempo con los videos largos (play along y canciones para tocar encima): " + CANAL + "/videos\n"
        "Listas por nivel: " + CANAL + "/playlists")
    m['descripcion'] = 'Descarga GRATIS la guía en PDF con 20 ritmos y su tablatura: ' + GUIA_PDF + '\n\n' + m['descripcion']
    tags = m['tags'] if isinstance(m['tags'], list) else m['tags'].split(',')
    m['tags'] = [x for x in tags if '+' not in x] + [e.lower(), f"ritmo de {e.lower()}", var]
    return m


def archivo(c):
    return f"dia{c['dia']:03d}_{c['estilo'].replace('__', '_v_')}_{c['bpm']}bpm.mp4"


def fila(c):
    m = meta_gancho(c)
    t = m['titulo']
    for a, b in ((' | Cómo tocar batería #shorts', ' #shorts'), ('Ritmo de batería ', 'Ritmo ')):
        if len(t) > 100: t = t.replace(a, b)
    if len(t) > 100: t = t.replace(' #shorts', '')
    m['titulo'] = t if len(t) <= 100 else t[:100].rsplit(' ', 1)[0]
    tags = ','.join(m['tags']) if isinstance(m['tags'], list) else m['tags']
    return [c['dia'], archivo(c), m['titulo'], m['descripcion'], tags]


if __name__ == '__main__':
    pl = {c['dia']: c for c in plan_a2()}
    if sys.argv[1] == 'plan':
        p = os.path.join(AQUI, '..', 'plan', 'titulos_shorts.csv')
        rows = list(csv.reader(open(p, encoding='utf-8')))
        body = [r for r in rows[1:] if int(r[0]) <= ULT] + [fila(pl[n]) for n in sorted(pl)]
        with open(p, 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh, quoting=csv.QUOTE_ALL); w.writerow(rows[0]); w.writerows(body)
        print(len(body), 'filas')
    else:
        os.makedirs(OUT, exist_ok=True)
        from multiprocessing import Pool
        # el orden de publicación lo manda plan/titulos_shorts.csv (puede estar reordenado):
        # la fila n dice qué archivo va; se busca en el plan la entrada que genera ese archivo
        por_arch = {archivo(c): c for c in pl.values()}
        # specs congeladas por archivo (plan/specs_a.json): el patrón de cada video no cambia aunque se edite drumlib
        sp = os.path.join(AQUI, '..', 'plan', 'specs_a.json')
        if os.path.exists(sp):
            import json as _j
            for arch, c in _j.load(open(sp, encoding='utf-8')).items():
                base = D.ESTILOS_TODOS.get(c['base'], {})
                D.ESTILOS_TODOS[c['estilo']] = dict(base, nombre=c['nombre'], hits=c['hits'])
                por_arch[arch] = dict({k: v for k, v in c.items() if k not in ('nombre', 'hits', 'nivel_estilo')}, _archivo=arch)
        filas = {int(r['dia']): r['archivo'] for r in csv.DictReader(open(os.path.join(AQUI, '..', 'plan', 'titulos_shorts.csv'), encoding='utf-8'))}
        cs = [por_arch[filas[int(a)]] for a in sys.argv[1:] if int(a) in filas and filas[int(a)] in por_arch]

        def work(c):
            f = f"{OUT}/{c.get('_archivo') or archivo(c)}"
            if not os.path.exists(f): D.render({k: v for k, v in c.items() if k != '_archivo'}, f)
            return f
        with Pool(int(os.environ.get('NP', '4'))) as P:
            for f in P.imap_unordered(work, cs): print(f, flush=True)

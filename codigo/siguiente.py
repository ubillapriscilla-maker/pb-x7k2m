"""Decide qué video toca subir según lo que YA está publicado en el canal (no según la fecha).
Así, si un día no se publica algo (por ejemplo, porque se acabaron los créditos), al día siguiente
se sigue exactamente donde quedó, sin saltarse ni repetir nada.

Uso:
  python3 siguiente.py SERIE titulos.json [cantidad]
    SERIE: A (Shorts serie A), B (Shorts serie B), LA (largos A), LB (largos B)
    titulos.json: lista JSON con los títulos de las últimas subidas del canal (hasta 100)
    cantidad: cuántos pendientes listar (por defecto 1)
Imprime JSON: {"serie":..., "pendientes":[{n, archivo, titulo, descripcion, tags, miniatura?}], "ultimo_publicado": n}

REGLA: nunca cambies el título de una fila ya publicada en plan/, porque así se reconoce lo publicado.
"""
import sys, json, csv, io, urllib.request

BASE = 'https://raw.githubusercontent.com/ubillapriscilla-maker/pb-x7k2m/main/'
FUENTE = {
    'A': ('plan/titulos_shorts.csv', 'dia', 'v/'),
    'B': ('plan/titulos_shorts_b.csv', 'n', 'v/b/'),
    'LA': ('plan/largos.json', 'n', 'l/'),
    'LB': ('plan/largos_b.json', 'n', 'l/b/'),
}
VENTANA = 30   # cuántos números hacia atrás se revisan para rellenar huecos


def leer(ruta):
    try:
        return open(ruta, encoding='utf-8').read()
    except OSError:
        return urllib.request.urlopen(BASE + ruta, timeout=60).read().decode('utf-8')


def norm(t):
    return ' '.join(str(t).split()).casefold()


def filas(serie):
    ruta, clave, carpeta = FUENTE[serie]
    txt = leer(ruta)
    if ruta.endswith('.csv'):
        out = []
        for r in csv.DictReader(io.StringIO(txt)):
            out.append(dict(n=int(r[clave]), archivo=r['archivo'], titulo=r['titulo'], descripcion=r['descripcion'],
                            tags=[x for x in r['etiquetas'].split(',') if x.strip()], carpeta=carpeta,
                            titulo_en=r.get('titulo_en', '') or '', descripcion_en=r.get('descripcion_en', '') or ''))
    else:
        out = [dict(e, carpeta=carpeta) for e in json.loads(txt)]
    return sorted(out, key=lambda e: e['n'])


def pendientes(serie, titulos, cantidad=1):
    pub = {norm(t) for t in titulos}
    fs = filas(serie)
    hechos = [e['n'] for e in fs if norm(e['titulo']) in pub]
    ultimo = max(hechos) if hechos else 0
    desde = max(1, ultimo - VENTANA)
    cand = [e for e in fs if e['n'] >= desde and e['n'] not in hechos]
    return dict(serie=serie, ultimo_publicado=ultimo, pendientes=cand[:cantidad])


if __name__ == '__main__':
    serie = sys.argv[1].upper()
    titulos = json.load(open(sys.argv[2], encoding='utf-8'))
    cant = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    print(json.dumps(pendientes(serie, titulos, cant), ensure_ascii=False, indent=1))

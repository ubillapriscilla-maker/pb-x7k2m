import sys, os, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drumlib as D
from multiprocessing import Pool
OUT = '/home/claude/shorts/lote'
def work(c):
    f = f"{OUT}/dia{c['dia']:02d}_{c['estilo']}_{c['bpm']}bpm.mp4"
    D.render(c, f)
    return f
if __name__ == '__main__':
    pl = D.plan(180)
    for f in os.listdir(OUT):
        if f.endswith('.mp4'): os.remove(f"{OUT}/{f}")
    json.dump(pl, open(f"{OUT}/calendario_90_dias.json", 'w'), ensure_ascii=False, indent=1)
    with open(f"{OUT}/calendario_90_dias.csv", 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(pl[0])); w.writeheader(); w.writerows(pl)
    with open(f"{OUT}/titulos_y_descripciones.csv", 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['dia', 'archivo', 'titulo', 'descripcion', 'etiquetas'])
        for c in pl:
            m = D.meta(c)
            w.writerow([c['dia'], f"dia{c['dia']:02d}_{c['estilo']}_{c['bpm']}bpm.mp4", m['titulo'], m['descripcion'], ','.join(m['tags']) if isinstance(m['tags'], list) else m['tags']])
    with Pool(int(os.environ.get('NP', '4'))) as p:
        for i, f in enumerate(p.imap_unordered(work, pl), 1):
            print(i, f, flush=True)

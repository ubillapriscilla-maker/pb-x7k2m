"""Dibujo de la batería vista desde atrás (desde donde se toca), con lo que suena iluminado.

Piezas: crash (izquierda), ride (derecha), hi-hat con su pedal, caja, tom 1, tom 2, tom de piso, bombo con su pedal.
Cada golpe ilumina la pieza con el color de su fila en la tablatura y la hace "saltar" un poco.
El pedal del bombo baja cuando suena el bombo. El pedal del hi-hat queda abajo (hi-hat cerrado) y sube cuando el
hi-hat se toca abierto.
"""
import math
from PIL import ImageDraw, ImageFont

# geometría en un lienzo de 1080 de ancho; y0 = borde superior de la zona de la batería (alto ~540)
PIEZAS = {
    # voz: (cx, cy, rx, ry, alto_casco)
    "crash": (235, 95, 125, 26, 0),
    "ride": (850, 125, 140, 30, 0),
    "t1": (440, 210, 82, 34, 48),
    "t2": (640, 210, 82, 34, 48),
    "kick": (540, 345, 150, 150, 0),
    "t3": (835, 360, 118, 44, 120),
    "hat": (150, 255, 105, 20, 0),
    "snare": (330, 345, 108, 42, 46),
}
ETIQ = {"crash": "Crash", "ride": "Ride", "hat": "Hi-hat", "snare": "Caja", "t1": "Tom 1", "t2": "Tom 2", "t3": "Tom de piso",
        "kick": "Bombo"}


def mezcla(c1, c2, a):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))


def _tambor(d, cx, cy, rx, ry, alto, base_parche, casco, borde, glow, colv, k):
    s = 1 + 0.06 * glow
    rx2, ry2 = rx * s, ry * s
    if alto:
        d.rectangle([cx - rx2, cy, cx + rx2, cy + alto], fill=casco)
        d.ellipse([cx - rx2, cy + alto - ry2, cx + rx2, cy + alto + ry2], fill=casco)
        d.line([cx - rx2, cy, cx - rx2, cy + alto], fill=borde, width=3)
        d.line([cx + rx2, cy, cx + rx2, cy + alto], fill=borde, width=3)
    parche = mezcla(base_parche, colv, min(1, glow * 1.1))
    if glow > 0.05:
        g = 10 * glow
        d.ellipse([cx - rx2 - g, cy - ry2 - g, cx + rx2 + g, cy + ry2 + g], outline=colv, width=max(2, int(6 * glow)))
    d.ellipse([cx - rx2, cy - ry2, cx + rx2, cy + ry2], fill=parche, outline=borde, width=4)


def _platillo(d, cx, cy, rx, ry, base, colv, glow, borde, dy=0):
    vib = math.sin(glow * 25) * 3 * glow
    cy = cy + dy + vib
    c = mezcla(base, colv, min(1, glow * 1.1))
    if glow > 0.05:
        g = 10 * glow
        d.ellipse([cx - rx - g, cy - ry - g, cx + rx + g, cy + ry + g], outline=colv, width=max(2, int(6 * glow)))
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=c, outline=borde, width=3)
    d.ellipse([cx - rx * 0.22, cy - ry * 0.45, cx + rx * 0.22, cy + ry * 0.35], fill=mezcla(c, borde, 0.25))


def tripode(d, x, y_union, y_piso, abre, color, ancho=5):
    """Patas de atril: tres patas que salen de un punto y se abren hacia el piso."""
    d.line([x, y_union, x - abre, y_piso], fill=color, width=ancho)
    d.line([x, y_union, x + abre, y_piso], fill=color, width=ancho)
    d.line([x, y_union, x + abre * 0.25, y_piso + 8], fill=color, width=ancho)
    for dx in (-abre, abre, abre * 0.25):
        yy = y_piso + (8 if dx == abre * 0.25 else 0)
        d.ellipse([x + dx - 6, yy - 4, x + dx + 6, yy + 4], fill=color)


def dibujar(img, y0, tema, col, brillo, hat_abierto, bombo_abajo, fuente):
    """brillo: dict voz -> 0..1 (1 = recién golpeado). col: color de cada voz (el mismo de la tablatura)."""
    d = ImageDraw.Draw(img)
    borde = tema["txt"]; parche = mezcla(tema["top"], (255, 255, 255), 0.55)
    casco = mezcla(tema["lane"], tema["txt"], 0.35); bronce = (214, 175, 92); fierro = mezcla(tema["mut"], tema["txt"], 0.3)

    def P(v):
        cx, cy, rx, ry, al = PIEZAS[v]
        return cx, cy + y0, rx, ry, al

    def b(v):
        return brillo.get(v, 0.0)

    # soportes de platillos
    for v in ("crash", "ride"):
        cx, cy, rx, ry, _ = P(v)
        bx = cx + (10 if v == "crash" else -40)
        d.line([cx, cy, bx, y0 + 445], fill=fierro, width=6)
        tripode(d, bx, y0 + 445, y0 + 505, 34 if v == "crash" else 42, fierro)
    hx, hy, hrx, hry, _ = P("hat")
    d.line([hx, hy, hx, y0 + 455], fill=fierro, width=7)
    tripode(d, hx, y0 + 455, y0 + 505, 48, fierro)
    # platillos de atrás
    _platillo(d, *P("crash")[:4], bronce, col.get("crash", bronce), b("crash"), borde)
    _platillo(d, *P("ride")[:4], bronce, col.get("ride", bronce), b("ride"), borde)
    # bombo (parche trasero, el que golpea el mazo) y toms montados encima
    kx, ky, krx, kry, _ = P("kick")
    gk = b("kick")
    _tambor(d, kx, ky, krx, kry, 0, parche, casco, borde, gk * 0.7, col.get("kick", borde), None)
    d.ellipse([kx - krx * 0.18, ky - kry * 0.18, kx + krx * 0.18, ky + kry * 0.18], outline=mezcla(parche, borde, 0.3), width=3)
    for v in ("t1", "t2"):
        cx, cy, rx, ry, al = P(v)
        d.line([cx, cy + al, kx, ky - kry + 20], fill=fierro, width=6)
        _tambor(d, cx, cy, rx, ry, al, parche, casco, borde, b(v), col.get(v, borde), None)
    # tom de piso con patas
    cx, cy, rx, ry, al = P("t3")
    for dx in (-rx + 15, rx - 15):
        d.line([cx + dx, cy + al, cx + dx * 1.15, y0 + 520], fill=fierro, width=6)
    _tambor(d, cx, cy, rx, ry, al, parche, casco, borde, b("t3"), col.get("t3", borde), None)
    # caja con su soporte
    cx, cy, rx, ry, al = P("snare")
    d.line([cx, cy + al, cx, y0 + 460], fill=fierro, width=6)
    tripode(d, cx, y0 + 460, y0 + 510, 34, fierro)
    gs = max(b("snare"), b("aro"))
    cs = col.get("snare", borde) if b("snare") >= b("aro") else col.get("aro", borde)
    _tambor(d, cx, cy, rx, ry, al, parche, casco, borde, gs, cs, None)
    if b("aro") > 0.05:  # golpe de aro: se ilumina el borde
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col.get("aro", borde), width=int(4 + 8 * b("aro")))
    # hi-hat: dos platillos; abiertos se separan
    gh = max(b("hat"), b("ohat"))
    ch = col.get("ohat" if b("ohat") > b("hat") else "hat", bronce)
    sep = 20 if hat_abierto else 4
    _platillo(d, hx, hy + sep, hrx, hry, bronce, ch, gh * 0.6, borde)
    _platillo(d, hx, hy - (2 if not hat_abierto else 0), hrx, hry, bronce, ch, gh, borde, dy=-sep / 2)
    # pedales
    def pedal(x, abajo, colp, activo):
        y = y0 + 528
        base = mezcla(fierro, tema["top"], 0.2)
        d.rounded_rectangle([x - 38, y + 18, x + 38, y + 30], radius=5, fill=base, outline=borde)
        alto = 2 if abajo else 20
        c = mezcla(base, colp, activo)
        d.polygon([(x - 30, y + 20), (x + 30, y + 20), (x + 24, y - 14 - alto), (x - 24, y - 14 - alto)], fill=c, outline=borde, width=2)
    # varilla del hi-hat: baja por el atril hasta el pedal (cerrado = pedal abajo)
    d.line([hx + 3, y0 + 505, hx + 3, y0 + 512], fill=fierro, width=4)
    pedal(hx, not hat_abierto, col.get("hat", bronce), 0.8 if not hat_abierto else 0.0)
    pedal(kx, bombo_abajo, col.get("kick", borde), gk)
    # mazo del bombo
    ang = 0.15 if bombo_abajo else 0.55
    bx, by = kx, y0 + 500
    ex, ey = bx, by - 120 * math.cos(ang)
    d.line([bx, by, ex, ey], fill=fierro, width=6)
    d.ellipse([ex - 14, ey - 14, ex + 14, ey + 14], fill=mezcla(parche, col.get("kick", borde), gk), outline=borde, width=2)
    # nombres de las piezas (chicos)
    pos = {"crash": (235, 30), "ride": (850, 60), "hat": (60, 205), "snare": (195, 440), "t1": (395, 125), "t2": (595, 125),
           "t3": (770, 250), "kick": (560, 452)}
    for v, (x, y) in pos.items():
        on = b(v) > 0.3 or (v == "hat" and b("ohat") > 0.3) or (v == "snare" and b("aro") > 0.3)
        d.text((x, y + y0), ETIQ[v], font=fuente, fill=col.get(v, borde) if on else tema["mut"])
    d.text((hx + 44, y0 + 532), "Pedal hi-hat", font=fuente, fill=tema["mut"])
    d.text((kx + 44, y0 + 532), "Pedal bombo", font=fuente, fill=tema["mut"])

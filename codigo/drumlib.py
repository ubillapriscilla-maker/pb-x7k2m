#!/usr/bin/env python3
"""Biblioteca para generar Shorts de practica de bateria 100% con codigo.
Audio sintetizado (sin derechos de autor) + partitura animada. Dos disenos (grilla y notas cayendo) y 6 temas de color.
"""
import json, math, subprocess, wave
import numpy as np
import kit as KIT
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
WATERMARK = "@priscillaubillasoriano"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ORDER = ["crash", "ride", "hat", "ohat", "t1", "t2", "t3", "snare", "kick", "aro"]  # orden de colores del tema
ORDER_VIS = ["crash", "ride", "hat", "ohat", "t1", "t2", "t3", "aro", "snare", "kick"]  # orden de filas en pantalla
ETIQ2 = {"hat": ("Hi-hat", "cerrado"), "ohat": ("Hi-hat", "abierto"), "t3": ("Tom", "de piso")}


def etiqueta(d, x, y, v, font, fill, centro=False, simple=False):
    """Nombre del instrumento; hi-hat cerrado/abierto en dos líneas para que se entienda cuál es cuál.
    simple=True: si el ritmo no usa hi-hat abierto, el cerrado se nombra solo "Hi-hat" en una línea."""
    lineas = ETIQ2.get(v, (NOMBRE[v],))
    if simple and v == "hat":
        lineas = ("Hi-hat",)
    if len(lineas) > 1:
        font = ImageFont.truetype(font.path, int(font.size * 0.8))
    h = font.size + 1
    y0 = y - (len(lineas) - 1) * h / 2
    for k, t in enumerate(lineas):
        xx = x - d.textlength(t, font=font) / 2 if centro else x
        d.text((xx, y0 + k * h), t, font=font, fill=fill)


NOMBRE = {"crash": "Crash", "ride": "Ride", "hat": "Hi-hat", "ohat": "Hi-hat abierto", "t1": "Tom 1",
          "t2": "Tom 2", "t3": "Tom piso", "snare": "Caja", "kick": "Bombo", "aro": "Aro"}


def pat(**kw):
    return {k: v for k, v in kw.items()}


# ---------------------------------------------------------------- ritmos (16 pasos = 16avos de un compas 4/4)
ESTILOS = {
    "rock_basico": dict(nombre="Rock básico", nivel=1, bpm=(60, 110), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-------x-------")),
    "rock_bombo_extra": dict(nombre="Rock con bombo extra", nivel=1, bpm=(60, 110), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-----x-x-------")),
    "ride_rock": dict(nombre="Rock con ride", nivel=2, bpm=(70, 110), hits=pat(
        ride="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-------x-x-----")),
    "pop_4_al_piso": dict(nombre="Pop con bombo en negras", nivel=2, bpm=(90, 120), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x---x---x---x---")),
    "disco": dict(nombre="Disco", nivel=2, bpm=(100, 124), hits=pat(
        hat="x---x---x---x---", ohat="--x---x---x---x-", snare="----x-------x---", kick="x---x---x---x---")),
    "hiphop_boom_bap": dict(nombre="Hip-hop boom bap", nivel=2, bpm=(70, 95), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-------x-x-----")),
    # one drop escrito como en los métodos: bombo y aro juntos solo en el 3 (el 1 queda vacío)
    "reggae_one_drop": dict(nombre="Reggae one drop", nivel=2, bpm=(65, 90), hits=pat(
        hat="x-x-x-x-x-x-x-x-", aro="--------x-------", kick="--------x-------")),
    "medio_tiempo": dict(nombre="Rock a medio tiempo", nivel=3, bpm=(70, 110), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="--------x-------", kick="x-------------x-")),
    "rock_16avos": dict(nombre="Rock con hi-hat en semicorcheas", nivel=3, bpm=(60, 95), hits=pat(
        hat="xxxxxxxxxxxxxxxx", snare="----x-------x---", kick="x-------x-x-----")),
    "funk_16avos": dict(nombre="Funk en semicorcheas", nivel=3, bpm=(70, 100), hits=pat(
        hat="xxxxxxxxxxxxxxxx", snare="----x-------x---", kick="x--x----x-x-----")),
    "punk": dict(nombre="Punk rock rápido", nivel=3, bpm=(130, 175), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-------x-------")),
    "metal_doble_bombo": dict(nombre="Metal con doble bombo", nivel=4, bpm=(80, 125), hits=pat(
        ride="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="xxxxxxxxxxxxxxxx")),
    "bombo_y_caja": dict(nombre="Bombo y caja (sin hi-hat)", nivel=1, bpm=(60, 100), hits=pat(
        snare="----x-------x---", kick="x-------x-------")),
    "hat_negras": dict(nombre="Hi-hat en negras", nivel=1, bpm=(60, 100), hits=pat(
        hat="x---x---x---x---", snare="----x-------x---", kick="x-------x-------")),
    "rock_sincopado": dict(nombre="Rock con bombo sincopado", nivel=1, bpm=(60, 100), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x---x-x---x-----")),
    "funk_sincopado": dict(nombre="Funk sincopado", nivel=4, bpm=(75, 105), hits=pat(
        hat="xxxxxxxxxxxxxxxx", snare="----x-------x---", kick="x--x--x-x--x--x-")),
    "doble_bombo_corto": dict(nombre="Rock con dobles de bombo", nivel=4, bpm=(70, 110), hits=pat(
        ride="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-x---x-x-x-----")),
    "metal_galope": dict(nombre="Metal al galope", nivel=5, bpm=(85, 130), hits=pat(
        ride="x-x-x-x-x-x-x-x-", snare="----x-------x---", kick="x-xxx-xxx-xxx-xx")),
    "funk_abierto": dict(nombre="Funk con hi-hat abierto", nivel=5, bpm=(75, 100), hits=pat(
        hat="xxxxxxxxxxxxxx-x", ohat="--------------x-", snare="----x-------x---", kick="x--x--x-x--x-x--")),
    "blast_beat": dict(nombre="Blast beat", nivel=5, bpm=(90, 150), hits=pat(
        ride="x-x-x-x-x-x-x-x-", snare="-x-x-x-x-x-x-x-x", kick="x-x-x-x-x-x-x-x-")),
}

# ---------------------------------------------------------------- serie B: generos nuevos y rudimentos (manos en la caja)
GENEROS_B = {
    "ska": dict(nombre="Ska", nivel=2, bpm=(80, 120), hits=pat(
        # ska tradicional: bombo junto con la caja (o aro) en 2 y 4; hi-hat en los contratiempos
        hat="--x---x---x---x-", snare="----x-------x---", kick="----x-------x---")),
    "motown": dict(nombre="Motown", nivel=2, bpm=(80, 120), hits=pat(
        # bombo como en "I Can't Help Myself" (Four Tops), corregido por Priscilla: 1, y del 1, y del 2, y del 3 y 4
        hat="x-x-x-x-x-x-x-x-", snare="x---x---x---x---", kick="x-x---x---x-x---")),
    "reggaeton": dict(nombre="Reggaetón (dembow)", nivel=3, bpm=(80, 100), hits=pat(
        hat="x-x-x-x-x-x-x-x-", snare="---x--x----x--x-", kick="x---x---x---x---")),
    "bossa_nova": dict(nombre="Bossa nova", nivel=4, bpm=(70, 110), hits=pat(
        # 2 compases: clave de bossa en el aro (cross-stick). Comp.1: 1, y del 2, 4 | Comp.2: 2, y del 3
    hat="x-x-x-x-x-x-x-x-" * 2, aro="x-----x-----x-------x-----x-----", kick="x-----x-x-----x-" * 2)),
}
RUDIMENTOS_B = {
    "rud_simple": dict(nombre="Golpe simple (RLRL)", nivel=2, bpm=(60, 120), manos="RLRLRLRLRLRLRLRL", hits=pat(snare="xxxxxxxxxxxxxxxx")),
    "rud_doble": dict(nombre="Golpe doble (RRLL)", nivel=3, bpm=(60, 110), manos="RRLLRRLLRRLLRRLL", hits=pat(snare="xxxxxxxxxxxxxxxx")),
    "rud_paradiddle": dict(nombre="Paradiddle (RLRR LRLL)", nivel=3, bpm=(60, 110), manos="RLRRLRLLRLRRLRLL", hits=pat(snare="xxxxxxxxxxxxxxxx")),
    "rud_paradiddle_inv": dict(nombre="Paradiddle invertido (RLLR LRRL)", nivel=4, bpm=(60, 110), manos="RLLRLRRLRLLRLRRL", hits=pat(snare="xxxxxxxxxxxxxxxx")),
    "rud_simple_bombo": dict(nombre="Golpe simple con bombo", nivel=3, bpm=(60, 110), manos="RLRLRLRLRLRLRLRL", hits=pat(
        snare="xxxxxxxxxxxxxxxx", kick="x---x---x---x---")),
    "rud_paradiddle_bombo": dict(nombre="Paradiddle con bombo", nivel=4, bpm=(60, 105), manos="RLRRLRLLRLRRLRLL", hits=pat(
        snare="xxxxxxxxxxxxxxxx", kick="x-------x-------")),
    "rud_doble_bombo": dict(nombre="Golpe doble con bombo", nivel=4, bpm=(60, 100), manos="RRLLRRLLRRLLRRLL", hits=pat(
        snare="xxxxxxxxxxxxxxxx", kick="x---x---x---x---")),
}
ESTILOS_TODOS = {**ESTILOS, **GENEROS_B, **RUDIMENTOS_B}  # ESTILOS queda intacto: el plan de 180 y la tabla de largos no cambian

# ---------------------------------------------------------------- rellenos (pasos finales del compas)
RELLENOS = {
    "ninguno": dict(nombre="", inicio=16, hits=pat(), stick=""),
    "redoble_1": dict(nombre="Redoble de caja (1 tiempo)", inicio=12, hits=pat(snare="xxxx"), stick="RLRL"),
    "toms_bajada": dict(nombre="Bajada de toms", inicio=12, hits=pat(t1="xx--", t2="--x-", t3="---x"), stick=""),
    "redoble_2": dict(nombre="Redoble de caja (2 tiempos)", inicio=8, hits=pat(snare="xxxxxxxx"), stick="RLRLRLRL"),
    "paradiddle": dict(nombre="Paradiddle en la caja", inicio=8, hits=pat(snare="xxxxxxxx"), stick="RLRRLRLL"),
    "paradiddle_toms": dict(nombre="Paradiddle a los toms", inicio=8, hits=pat(snare="xxxx----", t1="----xx--", t2="------x-", t3="-------x"),
                            stick="RLRR"),
    "redoble_toms": dict(nombre="Redoble que baja por los toms", inicio=8, hits=pat(snare="xxxx----", t1="----xx--", t2="------x-", t3="-------x"),
                         stick="RLRL"),
    "redoble_tom1": dict(nombre="Redoble en el tom 1", inicio=12, hits=pat(t1="xxxx"), stick="RLRL", manos_todas=True),
    "redoble_dos_toms": dict(nombre="Redoble del tom 1 al tom 2", inicio=8, hits=pat(t1="xxxx----", t2="----xxxx"),
                             stick="RLRLRLRL", manos_todas=True),
    "redoble_caja_tom": dict(nombre="Redoble de la caja al tom piso", inicio=8, hits=pat(snare="xxxx----", t3="----xxxx"),
                             stick="RLRLRLRL", manos_todas=True),
}

# ---------------------------------------------------------------- temas visuales
TEMAS = {
    "noche": dict(top=(15, 23, 42), bot=(8, 12, 24), txt=(255, 255, 255), mut=(148, 163, 184), acc=(250, 204, 21), lane=(30, 41, 59),
                  cols=[(250, 204, 21), (253, 224, 71), (250, 204, 21), (251, 146, 60), (167, 139, 250), (96, 165, 250), (45, 212, 191), (56, 189, 248), (244, 114, 182)]),
    "neon": dict(top=(10, 6, 30), bot=(2, 2, 12), txt=(240, 255, 255), mut=(120, 140, 190), acc=(0, 255, 200), lane=(25, 20, 60),
                 cols=[(255, 0, 170), (0, 229, 255), (0, 255, 200), (255, 230, 0), (160, 100, 255), (80, 160, 255), (0, 255, 120), (255, 80, 80), (255, 140, 0)]),
    "papel": dict(top=(247, 242, 232), bot=(232, 224, 208), txt=(30, 30, 30), mut=(110, 100, 90), acc=(200, 60, 40), lane=(214, 204, 186),
                  cols=[(200, 60, 40), (180, 90, 30), (200, 140, 30), (160, 110, 20), (60, 110, 160), (50, 130, 120), (100, 90, 150), (30, 90, 160), (170, 40, 90)]),
    "atardecer": dict(top=(70, 20, 90), bot=(230, 100, 60), txt=(255, 255, 255), mut=(255, 220, 200), acc=(255, 220, 120), lane=(120, 40, 100),
                      cols=[(255, 235, 150), (255, 220, 120), (255, 245, 200), (255, 180, 100), (200, 160, 255), (160, 200, 255), (150, 255, 220), (255, 255, 255), (255, 140, 200)]),
    "bosque": dict(top=(20, 50, 38), bot=(8, 24, 18), txt=(240, 255, 240), mut=(150, 190, 160), acc=(190, 230, 120), lane=(34, 74, 56),
                   cols=[(230, 240, 130), (200, 235, 120), (170, 225, 120), (140, 215, 140), (120, 200, 180), (110, 190, 220), (240, 200, 110), (255, 160, 90), (240, 120, 120)]),
    "retro": dict(top=(34, 32, 30), bot=(18, 17, 16), txt=(250, 240, 220), mut=(170, 160, 140), acc=(255, 140, 40), lane=(60, 56, 50),
                  cols=[(255, 140, 40), (255, 170, 60), (255, 200, 90), (255, 120, 60), (60, 190, 170), (60, 170, 200), (120, 200, 140), (240, 220, 170), (255, 90, 70)]),
}

# Identidad del curso (pedido de Priscilla, 22 nov 2026): TODOS los videos en crema ('papel').
# Cualquier nombre de tema que pidan los generadores se resuelve a crema.
TEMA_CURSO = 'papel'
for _k in list(TEMAS):
    TEMAS[_k] = TEMAS[TEMA_CURSO]



# ---------------------------------------------------------------- audio
def _t(n):
    return np.arange(n) / SR


def s_kick(n):
    """Bombo: cuerpo grave con caída de tono, cola corta y golpe del mazo (click) al inicio."""
    t = _t(n); r = np.random.default_rng(3)
    f = 52 + 105 * np.exp(-t * 38)
    cuerpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.5)
    click = np.diff(r.standard_normal(n), prepend=0) * np.exp(-t * 420) * 0.18 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 260) * 0.12
    return np.tanh(1.7 * (cuerpo + click)) / np.tanh(1.7)


def s_snare(n):
    t = _t(n); r = np.random.default_rng(1)
    return r.standard_normal(n) * 0.7 * np.exp(-t * 22) + np.sin(2 * np.pi * 190 * t) * 0.5 * np.exp(-t * 28)


def _hp(x):
    return np.diff(x, prepend=0)


def s_hat(n):
    t = _t(n); return _hp(np.random.default_rng(2).standard_normal(n)) * 0.35 * np.exp(-t * 70)


def s_ohat(n):
    t = _t(n); return _hp(np.random.default_rng(3).standard_normal(n)) * 0.3 * np.exp(-t * 10)


def s_aro(n):
    """Aro (cross-stick): golpe seco y de madera, con resonancias cortas del aro y el casco."""
    t = _t(n); r = np.random.default_rng(6)
    tono = (np.sin(2 * np.pi * 480 * t) * np.exp(-t * 55) * 0.55 + np.sin(2 * np.pi * 1020 * t) * np.exp(-t * 85) * 0.45
            + np.sin(2 * np.pi * 1730 * t) * np.exp(-t * 130) * 0.3)
    ruido = np.diff(r.standard_normal(n), prepend=0) * np.exp(-t * 380) * 0.35
    return (tono + ruido) * 0.9


def s_tom(f0):
    def f(n):
        t = _t(n); fr = f0 * (1 + 0.5 * np.exp(-t * 18))
        return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7) * 0.9
    return f


def s_crash(n):
    t = _t(n); return _hp(np.random.default_rng(4).standard_normal(n)) * 0.35 * np.exp(-t * 2.2)


def s_ride(n):
    t = _t(n); r = _hp(np.random.default_rng(5).standard_normal(n)) * 0.12
    m = sum(np.sin(2 * np.pi * fq * t) for fq in (3480, 4350, 5620, 6780)) * 0.05
    return (r + m) * np.exp(-t * 5)


VOICES = {"kick": (s_kick, .35, .55), "snare": (s_snare, .3, .5), "hat": (s_hat, .1, .55), "ohat": (s_ohat, .4, .55),
          "t1": (s_tom(190), .45, .6), "t2": (s_tom(140), .45, .6), "t3": (s_tom(95), .5, .65),
          "crash": (s_crash, 1.6, .55), "ride": (s_ride, .9, .6), "aro": (s_aro, .12, .75)}


# ---------------------------------------------------------------- construccion del video (eventos)
def build_events(estilo, bpm, relleno, bars):
    st = ESTILOS_TODOS[estilo]; rl = RELLENOS[relleno]
    step = 60.0 / bpm / 4
    ev = []  # (tiempo, voz, ganancia, paso, compas, mano)
    for b in range(bars):
        es_relleno = relleno != "ninguno" and b % 4 == 3
        tras_relleno = relleno != "ninguno" and (b % 4 == 0)
        for voz, s in st["hits"].items():
            if len(s) == 32:  # patron de 2 compases
                s = s[(b % 2) * 16:(b % 2) * 16 + 16]
            for i, ch in enumerate(s):
                if ch == "-":
                    continue
                if es_relleno and i >= rl["inicio"] and voz != "crash":
                    continue
                g = 1.0 if i % 4 == 0 else (0.8 if i % 2 == 0 else 0.6) if voz in ("hat", "ride") else 1.0
                mano0 = st["manos"][i] if voz == "snare" and st.get("manos") else ""
                ev.append((((b * 16) + i) * step, voz, g, i, b, mano0))
        if es_relleno:
            for voz, s in rl["hits"].items():
                for j, ch in enumerate(s):
                    if ch != "-":
                        mano = rl["stick"][j] if (voz == "snare" or rl.get("manos_todas")) and j < len(rl["stick"]) else ""
                        if relleno in ("paradiddle_toms", "redoble_toms") and voz != "snare":
                            mano = ""
                        ev.append((((b * 16) + rl["inicio"] + j) * step, voz, 1.0, rl["inicio"] + j, b, mano))
        if tras_relleno:
            ev.append((b * 16 * step, "crash", 1.0, 0, b, ""))
    return ev, step


def audio(ev, total, path):
    n = int((total) * SR)
    mix = np.zeros(n)
    cache = {}
    for (t, voz, g, *_r) in ev:
        fn, dur, vol = VOICES[voz]
        if voz not in cache:
            cache[voz] = fn(int(dur * SR))
        s = cache[voz] * g * vol
        i0 = int(t * SR)
        idx = (i0 + np.arange(len(s))) % n  # circular: la cola del final se mezcla con el inicio, el loop queda continuo
        np.add.at(mix, idx, s)
    mix = np.tanh(mix * 1.2)
    mix = mix / max(1e-9, np.abs(mix).max()) * 0.9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


HOOK_T = 2.4
HOOKS = {1: ("TU PRIMER RITMO", "Fácil: toca conmigo"), 2: ("SUENA A CANCIÓN", "y es más fácil de lo que crees"),
         3: ("¿PUEDES TOCARLO?", "Un nivel más arriba"), 4: ("DESAFÍO DE BATERÍA", "Hazlo lento y sube el BPM"),
         5: ("NIVEL EXPERTO", "¿Lo logras limpio?")}


def _hook(d, fr, cfg, tema, titulo, bpm, t, f_big, f_sm, f_xs, compacto=False):
    """Portada animada de los primeros segundos: promesa clara. No toca audio ni duracion."""
    a, b = cfg.get("hook") or HOOKS[cfg["nivel"]]
    off = int(max(0, 1 - t / 0.25) ** 2 * 120)  # entra desde arriba en 0.25 s
    if compacto:  # solo la franja de arriba: la batería dibujada queda visible desde el primer segundo
        f_h = ImageFont.truetype(BOLD, 80 if len(a) < 16 else 68)
        d.rectangle([0, 0, W, 225], fill=tema["top"])
        d.text((40, 20 - off), a, font=f_h, fill=tema["acc"])
        d.text((40, 120 - off), b, font=f_sm, fill=tema["txt"])
        d.text((40, 175 - off), f"{titulo}  ·  {bpm} BPM", font=f_xs, fill=tema["mut"])
        return
    f_h = ImageFont.truetype(BOLD, 96 if len(a) < 16 else 84)
    d.rectangle([0, 0, W, 470], fill=tema["bg"] if "bg" in tema else tema["top"])
    d.text((60, 70 - off), a, font=f_h, fill=tema["acc"])
    d.text((60, 215 - off), b, font=f_sm, fill=tema["txt"])
    d.text((60, 290 - off), f"{titulo}  ·  {bpm} BPM", font=f_sm, fill=tema["mut"])
    d.text((60, 380 - off), "Quédate 20 segundos y tócalo", font=f_xs, fill=tema["txt"])



def leyenda_manos(d, x_der, y, tema, font):
    """Recuadro pequeño que explica R y L (pedido de Priscilla, 23 nov 2026)."""
    txt = "R = mano derecha    L = mano izquierda"
    w = d.textlength(txt, font=font); h = font.size
    x0 = x_der - w - 36
    d.rounded_rectangle([x0, y - 12, x_der, y + h + 14], radius=14, fill=tema["lane"], outline=tema["acc"], width=3)
    d.text((x0 + 18, y), txt, font=font, fill=tema["txt"])


def fondo(tema):
    a = np.array(tema["top"], float); b = np.array(tema["bot"], float)
    g = np.linspace(0, 1, H)[:, None] * (b - a) + a
    arr = np.repeat(g[:, None, :], W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def render(cfg, salida):
    """cfg: estilo, bpm, relleno, tema, diseno ('grilla'|'cayendo'), nivel, bars(opc)"""
    estilo, bpm, relleno = cfg["estilo"], cfg["bpm"], cfg["relleno"]
    tema = TEMAS[cfg["tema"]]
    bar_dur = 4 * 60.0 / bpm
    bars = cfg.get("bars") or max(4, int(math.ceil(22 / bar_dur / 4)) * 4)
    ev, step = build_events(estilo, bpm, relleno, bars)
    total = bars * bar_dur
    wav = salida + ".wav"
    if cfg.get("banda"):  # batería grabada + banda por estilo, compuestas juntas para este video (desde 26 nov 2026)
        import bateria, banda
        dr = bateria.render(ev, total, estilo, loop=True)
        kicks = [e[0] for e in ev if e[1] == "kick"]
        mitad = bars // 2
        mu = banda.componer(bpm, bars, kicks, bars, tonica=62, semilla=sum(map(ord, estilo)) + bpm, estilo=estilo,
                            plan=[("estrofa", mitad), ("coro", bars - mitad)])
        mix = bateria.mezclar(dr, mu)
        with wave.open(wav, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    else:
        audio(ev, total, wav)
    usadas = [v for v in ORDER_VIS if any(e[1] == v for e in ev)]
    col = {v: tema["cols"][ORDER.index("snare" if v == "aro" else v)] for v in ORDER}
    f_xs = ImageFont.truetype(BOLD, 34); f_sm = ImageFont.truetype(BOLD, 42); f_md = ImageFont.truetype(BOLD, 54)
    titulo = ESTILOS_TODOS[estilo]["nombre"]
    variacion = ""
    if " + " in titulo:
        titulo, variacion = titulo.split(" + ", 1); variacion = "+ " + variacion
    f_big = ImageFont.truetype(BOLD, 78 if len(titulo) < 18 else 62 if len(titulo) < 26 else 52)
    f_var = None
    if variacion:
        _d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        for _s in range(42, 25, -2):
            f_var = ImageFont.truetype(BOLD, _s)
            if _d.textlength(variacion, font=f_var) <= W - 120: break
    bg = fondo(tema)
    nfr = int(round(total * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", salida], stdin=subprocess.PIPE)
    gx0, gx1 = 200, 1030
    rl = RELLENOS[relleno]
    nrows = len(usadas)
    labels16 = ["1", "e", "y", "a", "2", "e", "y", "a", "3", "e", "y", "a", "4", "e", "y", "a"]
    cell = (gx1 - gx0) / 16
    gy0 = 600; rh = min(150, 760 / nrows)
    evs = sorted(ev)
    usa_manos = any(e[5] for e in ev)
    line_y = 1380; top_y = 560; horizonte = 4 * 60.0 / bpm
    lane_w = (gx1 - 60) / nrows
    con_kit = cfg.get("kit", True) and cfg["diseno"] == "tablatura"
    tiempos_voz = {}
    for e in sorted(ev):
        tiempos_voz.setdefault(e[1], []).append(e[0])
    hh = sorted((e[0], e[1]) for e in ev if e[1] in ("hat", "ohat"))
    hh_t = [x[0] for x in hh]; hh_v = [x[1] for x in hh]
    f_big_k = ImageFont.truetype(BOLD, 66 if len(titulo) < 22 else 54 if len(titulo) < 30 else 46)
    f_kit = ImageFont.truetype(BOLD, 24)
    f_lbl = ImageFont.truetype(BOLD, 28)
    # tablatura con aire: usa el espacio libre hasta antes de la zona que tapa YouTube (~y 1480)
    _n = max(1, nrows)
    _gapk = 124 if _n <= 3 else 104
    _extra = (44 if _n <= 2 else 30) if usa_manos else 0  # espacio en el recuadro para las letras R / L
    _sep = 78 if usa_manos else 34  # de la tablatura al texto (con leyenda de manos si hay)
    sin_ingles = False
    una_caja = False  # muchas filas: se muestra solo el compás que suena, con filas grandes
    _bhk = (1480 - 142 - _sep - 865 - _gapk - 20 - 2 * _extra) / (2 * _n)
    if _bhk < 40:
        una_caja = True
        _bhk = (1480 - 142 - _sep - 865 - 20 - _extra) / _n
    _bhk = max(30, min(68, _bhk))
    _esc = min(1.4, _bhk / 44)  # escala de puntos según el alto de fila
    rudi = str(cfg.get("estilo", "")).startswith("rud_")
    if not rudi:  # ritmos: diseño original (Priscilla, 25 nov 2026: el espaciado nuevo es solo para rudimentos)
        _gapk, _extra, una_caja, sin_ingles, _esc = 104, 0, False, False, 1.0
        _bhk = min(44, 216 / _n)
    fin_tab = (865 + _bhk * nrows + 20 + _extra) if una_caja else (865 + 2 * _bhk * nrows + _gapk + 20 + 2 * _extra)  # borde inferior de la tablatura (modo batería dibujada)
    y_txt = fin_tab + (78 if usa_manos else 34)
    for k in range(nfr):
        t = k / FPS
        gs = int(t / step); b = gs // 16; cur = gs % 16
        fase = (t % step) / step
        fr = bg.copy(); d = ImageDraw.Draw(fr)
        es_rel = relleno != "ninguno" and b % 4 == 3
        if con_kit:
            d.text((40, 28), f"BATERÍA · NIVEL {cfg['nivel']}  ·  {bpm} BPM  ·  Compás {b + 1} de {bars}", font=f_xs, fill=tema["acc"])
            d.text((40, 70), titulo, font=f_big_k, fill=tema["txt"])
            if variacion:
                d.text((40, 70 + f_big_k.size + 8), variacion, font=f_var, fill=tema["acc"])
            # batería dibujada: se ilumina lo que suena
            import bisect
            br = {}
            for v_, ts_ in tiempos_voz.items():
                j = bisect.bisect_right(ts_, t + 0.01) - 1
                if j >= 0:
                    br[v_] = max(0.0, 1 - (t - ts_[j]) / 0.22) if t >= ts_[j] - 0.01 else 0.0
            j = bisect.bisect_right(hh_t, t + 0.01) - 1
            abierto = j >= 0 and hh_v[j] == "ohat"
            KIT.dibujar(fr, 180, tema, col, br, abierto, br.get("kick", 0) > 0.45, f_kit)
            d = ImageDraw.Draw(fr)
            if relleno != "ninguno":
                proximo = (b % 4 == 3)
                txt = ("Relleno: " + rl["nombre"]) if proximo else ("Siguiente relleno: " + rl["nombre"])
                d.text((40, 742 if rudi else 752), txt, font=f_xs, fill=tema["acc"] if proximo else tema["mut"])
        else:
            d.text((60, 90), f"BATERÍA  ·  NIVEL {cfg['nivel']}", font=f_sm, fill=tema["acc"])
            d.text((60, 160), titulo, font=f_big, fill=tema["txt"])
            if variacion:
                d.text((60, 245), variacion, font=f_var, fill=tema["acc"])
            d.text((60, 300 if variacion else 280), f"{bpm} BPM   |   Compás {b + 1} de {bars}", font=f_sm, fill=tema["mut"])
            if relleno != "ninguno":
                proximo = (b % 4 == 3)
                txt = ("Relleno: " + rl["nombre"]) if proximo else ("Siguiente relleno: " + rl["nombre"])
                d.text((60, 375 if variacion else 360), txt, font=f_xs, fill=tema["acc"] if proximo else tema["mut"])
            else:
                d.text((60, 375 if variacion else 360), "Ritmo constante: repítelo sin parar", font=f_xs, fill=tema["mut"])
        if cfg["diseno"] == "grilla":
            for s in range(16):
                cx = gx0 + cell * s + cell / 2
                lw = d.textlength(labels16[s], font=f_xs)
                d.text((cx - lw / 2, gy0 - 70), labels16[s], font=f_xs, fill=tema["txt"] if s % 4 == 0 else tema["mut"])
            if es_rel:
                d.rounded_rectangle([gx0 + cell * rl["inicio"], gy0 - 10, gx1, gy0 + rh * nrows], radius=14, fill=tema["lane"])
            d.rounded_rectangle([gx0 + cell * cur + 2, gy0 - 14, gx0 + cell * (cur + 1) - 2, gy0 + rh * nrows + 4], radius=12,
                                outline=tema["txt"], width=3)
            for r, v in enumerate(usadas):
                y = gy0 + r * rh + rh / 2
                etiqueta(d, 24, y - 20, v, f_xs, col[v])
                d.line([gx0, y, gx1, y], fill=tema["lane"], width=3)
            for (te, v, g, i, bb, mano) in evs:
                if bb != b:
                    continue
                y = gy0 + usadas.index(v) * rh + rh / 2
                cx = gx0 + cell * i + cell / 2
                rad = 15 if v in ("hat", "ride") else 20
                if i == cur:
                    rad += int(12 * (1 - fase))
                d.ellipse([cx - rad, y - rad, cx + rad, y + rad], fill=col[v])
                if mano:
                    mw = d.textlength(mano, font=f_xs)
                    d.text((cx - mw / 2, y + 26), mano, font=f_xs, fill=tema["txt"])
        elif cfg["diseno"] == "tablatura":
            # dos compases completos, quietos, de izquierda a derecha; solo se marca la nota que suena
            tx0, tx1 = 230, 1030; tc = (tx1 - tx0) / 16
            if con_kit:
                tx0, tx1 = 215, 925; tc = (tx1 - tx0) / 16
            par = b if (con_kit and una_caja) else (b // 2) * 2
            ty = 560; bh = min(120, 360 / nrows); gap = 150
            if con_kit:
                ty = 865; bh = _bhk; gap = _gapk
            for k2 in range(1 if (con_kit and una_caja) else 2):
                bb = par + k2
                if bb >= bars:
                    continue
                ex = _extra if con_kit else 0
                y0 = ty + k2 * (bh * nrows + gap + ex)
                y1 = y0 + bh * nrows
                d.rounded_rectangle([30, y0 - 80, (945 if con_kit else W - 30), y1 + 20 + ex], radius=20, fill=tema["lane"])
                d.text((50, y0 - 66), f"Comp. {bb + 1}", font=f_xs, fill=tema["mut"])
                for s_ in range(17):
                    x = tx0 + tc * s_
                    d.line([x, y0 - 6, x, y1], fill=tema["mut"] if s_ % 4 == 0 else tema["bot"], width=4 if s_ % 4 == 0 else 2)
                for s_ in range(16):
                    cx = tx0 + tc * s_ + tc / 2
                    big = s_ % 4 == 0
                    lw = d.textlength(labels16[s_], font=f_sm if big else f_xs)
                    d.text((cx - lw / 2, y0 - 62 + (0 if big else 6)), labels16[s_], font=f_sm if big else f_xs,
                           fill=tema["txt"] if big else tema["mut"])
                for r, v in enumerate(usadas):
                    y = y0 + r * bh + bh / 2
                    if con_kit and ("ohat" in usadas or (rudi and bh < 40)):
                        etiqueta(d, 40, y - 14, v, f_lbl, col[v], simple="ohat" not in usadas)
                    else:
                        etiqueta(d, 50, y - 18, v, f_xs, col[v], simple=con_kit and "ohat" not in usadas)
                    d.line([tx0, y, tx1, y], fill=tema["bot"], width=3)
                for (te, v, g, i, b2, mano) in evs:
                    if b2 != bb:
                        continue
                    y = y0 + usadas.index(v) * bh + bh / 2
                    cx = tx0 + tc * i + tc / 2
                    rad = 11 if v in ("hat", "ride") else 15
                    if con_kit:
                        rad = 12 if (rudi and usa_manos) else int(round(rad * _esc))  # rudimentos: puntos chicos, con aire entre notas
                    rad0 = rad
                    ab = bb * 16 + i
                    if ab == gs:
                        rad += int((9 if (con_kit and rudi) else 14) * (1 - fase))
                        d.ellipse([cx - rad, y - rad, cx + rad, y + rad], fill=tema["txt"])
                        rad -= 5
                        d.ellipse([cx - rad, y - rad, cx + rad, y + rad], fill=col[v])
                    elif ab < gs:
                        d.ellipse([cx - rad, y - rad, cx + rad, y + rad], fill=col[v])
                    else:
                        d.ellipse([cx - rad, y - rad, cx + rad, y + rad], outline=col[v], width=3)
                    if mano:
                        mw = d.textlength(mano, font=f_xs)
                        d.text((cx - mw / 2, (y1 + 2) if (con_kit and rudi) else (y + 16)), mano, font=f_xs, fill=tema["txt"])
        else:
            d.rounded_rectangle([40, top_y - 10, W - 40, line_y + 60], radius=24, fill=tema["lane"])
            for r, v in enumerate(usadas):
                cx = 60 + lane_w * r + lane_w / 2
                d.line([cx, top_y, cx, line_y], fill=tema["bot"], width=3)
                etiqueta(d, cx, line_y + 80, v, f_xs, col[v], centro=True)
            d.line([60, line_y, W - 60, line_y], fill=tema["txt"], width=4)
            for rep in (-1, 0, 1):
                for (te, v, g, i, bb, mano) in evs:
                    tt = te + rep * total
                    dt = tt - t
                    if -0.15 < dt < horizonte:
                        cx = 60 + lane_w * usadas.index(v) + lane_w / 2
                        y = line_y - dt / horizonte * (line_y - top_y)
                        rad = min(lane_w * 0.38, 21)
                        if abs(dt) < 0.06:
                            rad += 7
                        d.ellipse([cx - rad, y - rad, cx + rad, y + rad], fill=col[v])
                        if mano and dt > -0.05:
                            mw = d.textlength(mano, font=f_xs)
                            d.text((cx - mw / 2, y - 19), mano, font=f_xs, fill=tema["bot"])
        if t < HOOK_T:
            _hook(d, fr, cfg, tema, titulo, bpm, t, f_big, f_sm, f_xs, compacto=con_kit)
        ya, yb = (1565, 1630) if con_kit else (1640, 1720)
        if con_kit:  # español grande + inglés chico debajo (la tablatura se entiende en cualquier idioma)
            if cfg.get("cta", True) and t >= total * 0.65:
                d.text((40, y_txt), "Sígueme: mañana otro ritmo", font=f_md, fill=tema["acc"])
                if not sin_ingles:
                    d.text((40, y_txt + 62), "Follow for a new groove tomorrow", font=f_xs, fill=tema["mut"])
                d.text((40, y_txt + (62 if sin_ingles else 102)), ("Como en: " + cfg["cancion"]) if cfg.get("cancion") else "Guárdalo para practicar en loop",
                       font=f_xs, fill=tema["acc"] if cfg.get("cancion") else tema["txt"])
            else:
                d.text((40, y_txt), "Toca junto con el video", font=f_md, fill=tema["txt"])
                if not sin_ingles:
                    d.text((40, y_txt + 62), "Play along with the video", font=f_xs, fill=tema["mut"])
                d.text((40, y_txt + (62 if sin_ingles else 102)), ("Como en: " + cfg["cancion"]) if cfg.get("cancion") else "Míralo en loop hasta que salga limpio",
                       font=f_xs, fill=tema["acc"] if cfg.get("cancion") else tema["mut"])
        elif cfg.get("cta", True) and t >= total * 0.65:
            d.text((40 if con_kit else 60, ya), "Sígueme: mañana otro ritmo", font=f_md, fill=tema["acc"])
            d.text((40 if con_kit else 60, yb), "Guárdalo para practicar en loop", font=f_sm, fill=tema["txt"])
        else:
            d.text((40 if con_kit else 60, ya), "Toca junto con el video", font=f_md, fill=tema["txt"])
            d.text((40 if con_kit else 60, yb), "Míralo en loop hasta que salga limpio", font=f_sm, fill=tema["mut"])
        if not con_kit:
            d.text((60, 1810), WATERMARK, font=f_xs, fill=tema["mut"])
        if usa_manos:
            leyenda_manos(d, 940 if con_kit else W - 40, fin_tab + 14 if con_kit else 1490, tema, f_xs)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    import os
    os.remove(wav)
    return dict(duracion=round(total, 1), compases=bars)


# ---------------------------------------------------------------- calendario de 90 dias
NIVEL_RELLENOS = {1: ["ninguno"], 2: ["ninguno", "redoble_1"], 3: ["redoble_1", "toms_bajada", "ninguno"],
                  4: ["redoble_2", "toms_bajada", "paradiddle", "redoble_1"], 5: ["paradiddle", "paradiddle_toms", "redoble_toms", "redoble_2"]}
DISENOS = ["tablatura"]


BPM_INICIO = {1: 60, 2: 60, 3: 65, 4: 70, 5: 75}
BPM_TOPE = {1: 100, 2: 110, 3: 120, 4: 130, 5: 140}
ORDEN_REL = {1: ["ninguno"], 2: ["ninguno", "redoble_1"], 3: ["ninguno", "redoble_1", "toms_bajada"],
             4: ["redoble_1", "toms_bajada", "redoble_2", "paradiddle"],
             5: ["paradiddle", "redoble_2", "paradiddle_toms", "redoble_toms"]}


def plan(dias=90):
    """5 etapas de 18 dias, de facil a dificil. Cada estilo parte lento (60-75 BPM) y sube de 5 en 5.
    Los rellenos entran de a poco dentro de cada etapa. Nunca repite estilo+BPM+relleno."""
    out, usados, veces = [], set(), {}
    nombres_tema = list(TEMAS)
    for d in range(dias):
        etapa = -(-dias // 5)
        nivel = min(5, 1 + d // etapa)
        dn = d % etapa
        disp = [k for k, v in ESTILOS.items() if v["nivel"] <= nivel]
        nuevos = [k for k in disp if ESTILOS[k]["nivel"] == nivel]
        repaso = [k for k in disp if ESTILOS[k]["nivel"] < nivel] or nuevos
        pool = repaso if d % 3 == 2 else nuevos
        est = pool[(d // 3 * 2 + d % 3) % len(pool)]
        lo, hi = ESTILOS[est]["bpm"]
        n = veces.get(est, 0)
        base = max(60, min(lo, BPM_INICIO[nivel])) if n == 0 else None
        if n == 0:
            bpm = base
        else:
            bpm = min(prev_bpm[est] + 5, BPM_TOPE[nivel])
        rels = ORDEN_REL[nivel]
        idx = min(len(rels) - 1, dn * len(rels) // etapa)
        if d % 3 == 2 and idx > 0:
            idx -= 1
        rel = rels[idx]
        while (est, bpm, rel) in usados:
            bpm += 5
        usados.add((est, bpm, rel)); veces[est] = n + 1; prev_bpm[est] = bpm
        out.append(dict(dia=d + 1, nivel=nivel, estilo=est, bpm=bpm, relleno=rel,
                        tema=nombres_tema[d % len(nombres_tema)], diseno=DISENOS[0]))
    return out


prev_bpm = {}


def meta(c):
    st = ESTILOS[c["estilo"]]; rl = RELLENOS[c["relleno"]]
    niv = {1: "Principiante", 2: "Básico", 3: "Intermedio", 4: "Avanzado", 5: "Experto"}[c["nivel"]]
    adj = {1: "fácil", 2: "básico", 3: "intermedio", 4: "avanzado", 5: "experto"}[c["nivel"]]
    titulo = f"Ritmo de batería {adj}: {st['nombre']} a {c['bpm']} BPM | Cómo tocar batería #shorts"
    desc = (f"Cómo tocar batería: ritmo {adj} de {st['nombre'].lower()} a {c['bpm']} BPM (nivel {niv.lower()}).\n"
            + (f"Incluye un relleno cada 4 compases: {rl['nombre'].lower()}.\n" if c["relleno"] != "ninguno" else "Ritmo constante, ideal para ganar control y tiempo.\n")
            + "Mira la tablatura de izquierda a derecha, deja el video en repetición y toca junto con él. "
              "Cuando te salga limpio, sube 5 BPM.\n"
              "Es parte de un curso de batería para principiantes. Sigue la serie para ir subiendo de nivel.\n"
              "El sonido de la batería es sintético, hecho para estudiar.\n\n"
              "#shorts #batería #bateria #comotocarbateria #aprenderbatería #ritmosdebatería")
    tags = ["cómo tocar batería", "como tocar bateria", "batería para principiantes", "ritmos de batería para principiantes",
            "batería fácil", "aprender batería", "clases de batería", "ritmo de batería", "práctica de batería",
            f"{c['bpm']} bpm", st["nombre"].lower(), "tablatura batería", "shorts"]
    return dict(titulo=titulo, descripcion=desc, tags=tags)


if __name__ == "__main__":
    import sys
    p = plan()
    print(len(p), "dias; combinaciones unicas:", len({(x['estilo'], x['bpm'], x['relleno']) for x in p}))

"""Canciones de dominio publico (autores fallecidos hace mas de un siglo o tradicionales), en do mayor, 4/4.
Cada nota: (compas, paso 0-15, duracion en pasos, frecuencia). Un paso = una semicorchea; una negra = 4 pasos."""
NOTA = {"G4": 392.00, "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99, "A5": 880.00}


def _compases(lista):
    out = []
    for b, comp in enumerate(lista):
        st = 0
        for n, dur in comp:
            if n != "-":
                out.append((b, st, dur, NOTA[n]))
            st += dur
    return out


Q, E, H, DQ, W = 4, 2, 8, 6, 16
CANCIONES = {
    "oda": dict(
        nombre="Himno a la alegría", autor="Beethoven (siglo XIX, dominio público)",
        compases=16,
        acordes=["C", "G", "C", "G", "C", "G", "C", "C", "G", "G", "G", "G", "C", "G", "C", "C"],
        notas=_compases([
            [("E5", Q), ("E5", Q), ("F5", Q), ("G5", Q)], [("G5", Q), ("F5", Q), ("E5", Q), ("D5", Q)],
            [("C5", Q), ("C5", Q), ("D5", Q), ("E5", Q)], [("E5", DQ), ("D5", E), ("D5", H)],
            [("E5", Q), ("E5", Q), ("F5", Q), ("G5", Q)], [("G5", Q), ("F5", Q), ("E5", Q), ("D5", Q)],
            [("C5", Q), ("C5", Q), ("D5", Q), ("E5", Q)], [("D5", DQ), ("C5", E), ("C5", H)],
            [("D5", Q), ("D5", Q), ("E5", Q), ("C5", Q)], [("D5", Q), ("E5", E), ("F5", E), ("E5", Q), ("C5", Q)],
            [("D5", Q), ("E5", E), ("F5", E), ("E5", Q), ("D5", Q)], [("C5", Q), ("D5", Q), ("G4", H)],
            [("E5", Q), ("E5", Q), ("F5", Q), ("G5", Q)], [("G5", Q), ("F5", Q), ("E5", Q), ("D5", Q)],
            [("C5", Q), ("C5", Q), ("D5", Q), ("E5", Q)], [("D5", DQ), ("C5", E), ("C5", H)]])),
    "estrellita": dict(
        nombre="Brilla, brilla, estrellita", autor="melodía tradicional (dominio público)",
        compases=12,
        acordes=["C", "F", "C", "G", "C", "C", "C", "G", "C", "F", "C", "G"],
        notas=_compases([
            [("C5", Q), ("C5", Q), ("G5", Q), ("G5", Q)], [("A5", Q), ("A5", Q), ("G5", H)],
            [("F5", Q), ("F5", Q), ("E5", Q), ("E5", Q)], [("D5", Q), ("D5", Q), ("C5", H)],
            [("G5", Q), ("G5", Q), ("F5", Q), ("F5", Q)], [("E5", Q), ("E5", Q), ("D5", H)],
            [("G5", Q), ("G5", Q), ("F5", Q), ("F5", Q)], [("E5", Q), ("E5", Q), ("D5", H)],
            [("C5", Q), ("C5", Q), ("G5", Q), ("G5", Q)], [("A5", Q), ("A5", Q), ("G5", H)],
            [("F5", Q), ("F5", Q), ("E5", Q), ("E5", Q)], [("D5", Q), ("D5", Q), ("C5", H)]])),
    "corderito": dict(
        nombre="Mary tenía un corderito", autor="canción infantil tradicional (dominio público)",
        compases=8,
        acordes=["C", "G", "C", "C", "C", "G", "G", "C"],
        notas=_compases([
            [("E5", Q), ("D5", Q), ("C5", Q), ("D5", Q)], [("E5", Q), ("E5", Q), ("E5", H)],
            [("D5", Q), ("D5", Q), ("D5", H)], [("E5", Q), ("G5", Q), ("G5", H)],
            [("E5", Q), ("D5", Q), ("C5", Q), ("D5", Q)], [("E5", Q), ("E5", Q), ("E5", Q), ("E5", Q)],
            [("D5", Q), ("D5", Q), ("E5", Q), ("D5", Q)], [("C5", W)]])),
}

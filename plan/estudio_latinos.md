# Estudio de ritmos latinos (para batería, percusión y banda)

Regla de Priscilla: nunca inventar patrones. Cada patrón lleva su fuente. Lo que no está verificado queda marcado "PENDIENTE".
Grilla de 16 semicorcheas por compás de 4/4: `1 e y a 2 e y a 3 e y a 4 e y a` (x = golpe, - = silencio).

## 1. Cumbia

### Origen y tambores tradicionales (Colombia / Panamá)
- Tambora: tambor grave de dos parches; se toca en el parche y en la madera. Su figura en la madera es negra + dos corcheas; en batería se pasa al hi-hat, al aro del tom de piso o a un woodblock (Modern Drummer, sep 2015).
- Llamador: tambor chico que marca los tiempos débiles / el contratiempo ("um-pa"); es el que "llama" al resto.
- Tambor alegre: improvisa encima de la base.
- Guacharaca (o güiro / güira) y maracas: el "chiqui-chiqui"; en batería lo imita el hi-hat.
- Fuentes: Carnegie Hall Musical Explorers (cumbia, lección 1); Movimiento Afrolatino; Reverb.com "Latin Beats: cumbia on a drum kit".

### Patrones de batería verificados
A. Cumbia base (foro Batacas, patrón escrito por bateristas):
```
HH mano   x-xx x-xx x-xx x-xx   (corchea + dos semicorcheas por tiempo)
Aro caja  --x- ---- --x- ----   ("y" del 1 y del 3)
Tom 1     ---- --x- ---- --x-   ("y" del 2 y del 4; en otra versión, bongó)
Bombo     x--- x--- x--- x---   (negras)
HH pie    x--- x--- x--- x---
```
B. Cumbia del sur (recomendación de un baterista chileno, mismo foro): bombo y aro de caja en negras; hi-hat "corchea y dos semis", o hi-hat abriendo en los contratiempos ("pum-chas").
C. Variante con cencerro (Batacas): bombo en negras, cáscara (corchea + 2 semis) mano derecha, cencerro en negras junto al bombo, "y" del 2 y del 4 en el tom grave.
D. Bombo "tumbao" (siguiendo al bajo) en algunos momentos (Batacas; Reverb.com).
- Bajo: tumbao de tónica y quinta con anticipaciones; güiro en los contratiempos junto a las congas (Melodigging, cumbia argentina).

### Cómo toca cada instrumento (fuentes por instrumento, 26 nov 2026)
- Güiro / güira: el gesto central es un raspado largo seguido de dos cortos en cada tiempo, "chaaa-chi-ki" (Veena Studio, guía de música latina). Grilla: largo en x--- x--- x--- x---, cortos en --xx --xx --xx --xx.
- Bajo: tónica y quinta (y octava), notas cortas (staccato); patrón "negra y dos corcheas" dos veces por compás con tónica, quinta y octava (De Bajo Eléctrico, 10 ritmos de cumbia, patrón 3). Grilla: T--- 5-8- T--- 5-8-.
- Teclado (tesis UNLP "El teclado en la cumbia"): la BASE (mano izquierda, casi siempre piano) marca el contratiempo, la segunda corchea de cada pulso, con tríadas o tétradas entre Do4 y Fa5 (en villera una octava más grave); es el único rol constante de toda la canción. El COLCHÓN (mano derecha) son sonidos sostenidos tipo cuerdas, órgano o coro entre Fa#4 y Fa#5, eventual. La FIGURA es la melodía o contramelodía (acordeón, trompeta, saxo, flauta de pan o sintes lead), de Sol3 a Do6. La marcación del contratiempo del piano junto con la guitarra eléctrica y la conga grave es esencial en el ritmo.
- Congas: en 4 tiempos, palma (golpe sordo), abierto, palma, abierto (Entrebongos, cumbia colombiana en congas); el llamador va siempre a contratiempo y es lo más importante, porque la cumbia "va cruzada" (Batacas).
- Armonía: dos o tres acordes, I-V o i-V7; tempo 85-105 BPM (Veena Studio).
- Batería moderna: bombo suave en 1 y 3, aro/caja en 2 y 4, hi-hat liviano (Melodigging).

### Variantes regionales
- Cumbia peruana / chicha: guitarra eléctrica protagonista (punteos y arpegios), órgano/teclado, timbales, bongó, güiro, congas; sin acordeón ni vientos de madera (Wikipedia; El Peruano, J. Cosamalón).
- Cumbia argentina: santafesina (acordeón y guitarra), villera (teclados/sintes, influencias de reggae y electrónica), sonidera, norteña (Wikipedia; Rolling Stone vía Wikipedia).
- Cumbia chilena: PENDIENTE confirmar con la grabación de Priscilla (drumcam aPbfaVYHGzo) antes de publicar.

### Muestra hecha (codigo/demo_cumbia.py, versión 2)
Versión 3 (26 nov, pedido de Priscilla): solo batería, bajo, guitarra y teclado — nada de percusión ni otros instrumentos, porque el curso es de batería. El hi-hat imita al güiro; la guitarra lleva la melodía; el piano la base en contratiempo.
Versión 2: una sola cumbia de 16 compases a 96 BPM en La menor (Lam-Lam-Mi7-Mi7-Lam-Rem-Mi7-Lam) con cada instrumento según lo de arriba y melodía escrita a mano en acordeón. La versión 1 (tres cumbias) sonaba mal: melodía al azar y partes sin el rol correcto.

Versión 1 (descartada):
1. Colombiana adaptada a batería (patrón A + guacharaca/güiro + llamador en conga), bajo tónica-quinta, acordeón.
2. Del sur (patrón B con hi-hat abierto en contratiempos + güiro + remate de timbal), órgano en contratiempos y acordeón.
3. Peruana/chicha (timbales, bongó, güiro, conga; guitarra eléctrica limpia arpegiada).

## 2. Salsa (en estudio)
- Clave de son 2-3 / 3-2: base de todo; cada parte se ordena según la clave (Wikipedia, Salsa musical structure). En salsa se usa casi siempre la clave de son.
- Conga (tumbao/marcha): slap en el 2 y tonos abiertos en el 4 y sus contratiempos (Rob Bridge, Latin Drum Set Basics; Wikipedia).
- Cáscara: patrón en la madera del timbal; en batería en el aro/costado o cencerro; el bombo hace el tumbao del bajo (anticipación) y el pie izquierdo puede tocar la clave (Drumsettips; Vic Firth lección 32).
- PENDIENTE: grilla exacta de la cáscara 2-3 y 3-2, campana de mambo y de bongó, montuno de piano.

## 3. Merengue (en estudio)
- Partes: paseo (intro), merengue y jaleo (Francis' Drumming Blog). Tambora: palo y mano, con el "quintillo" (cinquillo) que marca dónde empieza el ciclo; güira en semicorcheas (Leicester Drum School; soundwitches).
- En batería: tambora en tom/aro y cross-stick, güira con el hi-hat (Rhythm Notes).
- PENDIENTE: grilla exacta de tambora (merengue derecho y jaleo) y güira.

## 4. Songo (en estudio)
- Creado por Los Van Van (Juan Formell) a inicios de los 70; lo desarrolló el baterista José Luis Quintana "Changuito", único de estos estilos nacido en la batería (Wikipedia; Hudson Music; Rhythm Notes).
- PENDIENTE: grilla del songo de Changuito.

## 5. Por estudiar
Bachata, cha-cha-chá, bolero, mambo, son montuno, guaguancó, samba, baião, 6/8 afrocubano, tango, candombe, cueca y huayno (Método de Batería del Sur del Mundo, Manuel Páez), joropo, plena.

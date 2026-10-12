# Algoritmo de recomendación: "¿Qué juego ahora?" (paso 4)

Recomienda juegos **pendientes** de tu librería (incluida la familiar) según tus gustos
de siempre, lo que juegas últimamente y lo que ha jugado tu familia. Todo se calcula en
cada visita con datos reales de Steam; no se guarda nada del usuario.

El código está en `analysis.py` (sección "Qué jugar") y `app.py` (`pedir_generos_presupuesto`
y el bloque "Qué jugar" de `index`).

## Fórmula completa (resumen)

```
puntos = redondear( mezcla × primo × anti × fama × nota )

mezcla = 0,4 × afinidad_siempre + 0,6 × afinidad_racha
primo  = 1,25 si un familiar le echó ≥ 20 h; si no, 1
anti   = 0,8  si tiene algún género que sueles abandonar; si no, 1
fama   = 1,2 (< 1.000 reseñas) · 1 · 0,9 (> 100.000 reseñas)
nota   = 1,15 (≥ 90 % positivas) · 1 (70-89 %) · 0,9 (50-69 %) · 0,75 (< 50 %)
```

Con 0 de mezcla el juego queda fuera (los multiplicadores no lo rescatan). Después: orden
de más a menos puntos (empates al azar) y top 5 con variedad.
En la web los puntos se muestran sin explicar de dónde salen (es un misterio a propósito).

## Datos de partida

| Dato | De dónde sale |
|---|---|
| Tus juegos y horas | `GetOwnedGames` (+ `GetRecentlyPlayedGames` para préstamos jugados en 2 semanas) |
| Fecha de tu última partida de cada juego | `rtime_last_played` de `GetOwnedGames` |
| Minutos jugados en las últimas 2 semanas | `playtime_2weeks` de `GetOwnedGames` |
| Géneros y nº de reseñas de cada juego | Steam Store `appdetails` (una consulta por juego, con caché en memoria) |
| % de reseñas positivas | Steam Store `appreviews` (solo los 15 finalistas, con caché en memoria) |
| Etiquetas de la comunidad (Terror, Metroidvania...) | API oficial `IStoreBrowseService/GetItems` (por lotes de 50) + `IStoreService/GetTagList` (nombres en español) |
| Horas de cada familiar | `GetOwnedGames` de cada familiar |

## Paso a paso

### 1. Candidatos: tus pendientes
Juegos con **0 h** o con horas **desconocidas** (préstamos de la familia que no has jugado
en las últimas 2 semanas: quizá ya los probaste). Función `pendientes()`.

### 2. Géneros de los candidatos (con presupuesto)
Pedir los géneros de cientos de juegos sería lento y Steam cortaría (error 429), así que en
cada visita se usan **todos los que ya están en caché** y se piden **20 nuevos al azar**
(`PRESUPUESTO_GENEROS`). Cada visita cubre más librería ("analizados X de Y").
Un juego cuya consulta falla no se puntúa (se reintenta en otra visita).

### 3. Tus gustos de siempre
De tus **10 juegos con más horas**, el % de esas horas que tiene cada género
(`horas_por_genero`). Un juego suma sus horas a **todos** sus géneros (los % no suman 100).
Ej.: Acción 80 %, Aventura 60 %, Rol 30 %.

### 4. Tu racha actual
De tus **últimos 10 juegos jugados** (por fecha; los préstamos recientes cuentan como
"ahora mismo"), el % que tiene cada género. **Un voto por juego**, sin mirar horas, para que
un juego de 1.000 h no aplaste lo que juegas ahora (`ultimos_jugados`, `racha_actual`).
Ej.: 7 de Rol y 3 de Acción → Rol 70 %, Acción 30 %.

### 5. Afinidad de cada pendiente
Para cada lista de gustos (siempre y racha): **suma de tus % en los géneros que tiene el
juego** (`afinidad`). "Indie", "Free to Play" y "Acceso anticipado" no suman: no dicen cómo
se juega (`NO_DEFINEN_PERFIL`). Después se mezclan:

```
puntos = 0,4 × afinidad_siempre + 0,6 × afinidad_racha      (PESO_RACHA = 0.6)
```

Si tu perfil no trae fechas (no hay racha), solo cuenta la afinidad de siempre.
Un juego con **0 puntos** no se parece a nada de lo que juegas y no se recomienda.

### 5b. Territorio inexplorado → "¿Te atreves?"
Los géneros de Steam son muy amplios (Resident Evil 2 es solo "Acción"). Las **etiquetas** de
la comunidad son mucho más precisas (Zombis, Terror...). Con ellas (`territorio_inexplorado`):
- **Lo que conoces** (`experiencia`): las 10 etiquetas más votadas (`TOP_EXPERIENCIA`) de cada
  juego que has jugado de verdad (2 h o más). Las de la familia no cuentan.
- **Lo que define a un pendiente** (`etiquetas_nuevas`): sus 3 etiquetas más votadas
  (`TOP_DEFINEN`), quitando las neutras que no dicen de qué va (`ETIQUETAS_NEUTRAS`: Un jugador,
  Indie, 2D, Buena trama...).
- Si alguna de esas 3 **nunca** aparece en lo que conoces, es **territorio inexplorado**: se
  aparta del top 5 y va a la opción **"¿Te atreves?"** (aunque tenga 0 puntos: la gracia es probar).
  Allí salen los 3 con más puntos, cada uno con una etiqueta nueva distinta si se puede
  (`elegir_atrevidos`, `TOP_ATREVIDOS`).
- En la web: tarjeta "🧭 ¿Te atreves?" con 1 juego visible y botón "Otro" (`atreverse.js`). Muestra
  "Nunca has jugado a nada de: ..." (hasta 3 etiquetas nuevas) y una frase absurda de `BIOS_ATREVIDO`
  (`poner_retos`, hueco `{nueva}` = su etiqueta nueva más votada). Sin puntos (pueden ser 0) y sin
  👍 % (la nota solo se pide para los finalistas del top).
- Sin etiquetas de lo que conoces (p. ej. Steam falló), no se aparta nada.

Ej.: has jugado Hollow Knight (Metroidvania, Plataformas...). Resident Evil 2 (Zombis,
Supervivencia / Terror, Terror) → "¿Te atreves?". Dead Cells (Roguelike, Metroidvania...) → top normal.

### 6. El consejo del primo
Si un familiar le echó **20 h o más** al juego (`UMBRAL_PRIMO`), sus puntos se multiplican
por **1,25** (`PLUS_PRIMO`). Al multiplicar, un juego con 0 puntos sigue fuera: la base son
siempre tus gustos. Si varios familiares llegan al umbral, cuenta el que más horas tiene.
Se muestra el dato real: *"Primo le echó 87 h"* (`consejos_familia`).

### 6a. Anti-gustos
Géneros que sueles **probar y dejar**. Un juego **abandonado** es uno con menos de 2 h
(`UMBRAL_ABANDONO`) que **no has tocado en las últimas 2 semanas** (sin `playtime_2weeks`:
un juego recién empezado no está abandonado) (`abandonados`). Sus géneros se piden con un
presupuesto propio de **10 consultas nuevas por visita** (`PRESUPUESTO_ABANDONOS`).

Un género es anti-gusto si cumple las tres condiciones (`anti_gustos`):
- aparece en **al menos 3** de tus abandonados analizados (`MIN_ABANDONOS_ANTI`);
- y en **al menos el 25 %** de ellos (`PCT_ABANDONOS_ANTI`);
- y tu % en ese género, de siempre o de la racha, es **menor del 20 %** (`MAX_GUSTO_ANTI`).
  Así un género muy común que te gusta (p. ej. Acción) nunca es anti-gusto.

Indie, Free to Play y Acceso anticipado no cuentan. Un pendiente con algún anti-gusto:
puntos × **0,8** (`CASTIGO_ANTI`), una sola vez aunque tenga varios.
Ej.: 12 abandonados (5 de Estrategia, 7 de Acción, 3 de Deportes) y te gusta Acción →
anti-gustos: Estrategia y Deportes. "Acción + Estrategia" pasa de 58 a 46.

### 6b. Joya oculta / superventas
Según el **nº de reseñas en Steam** (llega en la misma consulta que los géneros, sin llamadas
extra; `multiplicador_fama`):

| Reseñas | Efecto |
|---|---|
| menos de 1.000 (`UMBRAL_JOYA`) | 💎 joya oculta: × 1,2 (`PLUS_JOYA`) |
| 1.000 – 100.000 | nada |
| más de 100.000 (`UMBRAL_SUPERVENTAS`) | superventas: × 0,9 (`CASTIGO_SUPERVENTAS`) |
| sin dato | nada (no se inventa) |

### 6c. Nota de las reseñas (% positivo)
Del endpoint `appreviews` de Steam (una consulta por juego, con caché; `get_valoracion`).
Para no consultar cientos de juegos, se hace en **dos pasadas** (`app.py`): se puntúa todo con
los pasos anteriores, se piden las notas **solo de los 15 mejores** (`FINALISTAS`) y se vuelve
a puntuar con ellas (`nota_fiable`, `multiplicador_valoracion`):

| % de reseñas positivas | Efecto |
|---|---|
| 90 % o más (`UMBRAL_ACLAMADO`) | 👑 aclamado: × 1,15 (`PLUS_ACLAMADO`) |
| 70 – 89 % | nada |
| 50 – 69 % (`UMBRAL_MIXTO`) | × 0,9 (`CASTIGO_MIXTO`) |
| menos del 50 % (`UMBRAL_MALO`) | × 0,75 (`CASTIGO_MALO`) |
| menos de 10 reseñas (`MIN_RESENAS_NOTA`) o sin dato | nada (el % no es fiable) |

La pegatina 💎 **joya oculta** exige además **80 % o más** de positivas cuando se sabe
(`JOYA_MIN_PCT`): un juego desconocido y malo no es una joya (el plus de pocas reseñas sí se aplica).

Los puntos llevan decimales durante todo el cálculo y se **redondean una sola vez al final**.
Python redondea los ",5" al par más cercano (`round(72.5)` = 72).

### 7. Orden y desempate
De más a menos puntos. A igualdad de puntos, orden **al azar** (se baraja antes de ordenar).

### 8. Variedad
Se eligen los **5 mejores** (`TOP_RECOMENDACIONES`), pero como mucho **2 con los mismos
géneros en común contigo** (`MAX_IGUALES`). Si no hay variedad suficiente, los huecos se
rellenan con los saltados, en su orden (`con_variedad`).

### 9. Bios de Steam Match (solo texto, NO afectan a los puntos)
Cada recomendación lleva una frase absurda sacada de plantillas con huecos rellenados con
datos reales (nombre, un género en común al azar, familiar y sus horas, dueño, % positivo)
(`bio`, `poner_bios`; plantillas `BIOS_*`). Si el juego tiene algo especial (consejo del
primo, préstamo, joya, aclamado), hay un 50 % de usar una frase de ese tipo
(`PROB_BIO_ESPECIAL`); si no, una general. En una visita no se repite ninguna frase.

## Ejemplo completo

Gustos de siempre: Acción 100 %. Racha actual: Rol 70 %, Acción 30 %.
Tu primo le echó 87 h a "Juego B".

| Pendiente | Géneros | Reseñas | % positivo | Siempre | Racha | Mezcla 40/60 | Primo | Fama | Nota | Puntos |
|---|---|---|---|---|---|---|---|---|---|---|
| Juego A | Acción + Rol | 20.000 | 80 % | 100 | 100 | 100 | — | — | — | **100** |
| Juego B | Acción | 300 | 95 % | 100 | 30 | 58 | ×1,25 | 💎 ×1,2 | 👑 ×1,15 | **100** |
| Juego F | Acción | 300 | 85 % | 100 | 30 | 58 | — | 💎 ×1,2 | — | **70** |
| Juego C | Acción | 5.000 | 75 % | 100 | 30 | 58 | — | — | — | **58** |
| Juego H | Acción | 300 | 40 % | 100 | 30 | 58 | — | ×1,2 (sin 💎) | ×0,75 | **52** |
| Juego G | Acción | 500.000 | 72 % | 100 | 30 | 58 | — | ×0,9 | — | **52** |
| Juego D | Rol | 8.000 | 88 % | 0 | 70 | 42 | — | — | — | **42** |
| Juego E | Estrategia | — | — | 0 | 0 | 0 | — | — | — | fuera |

Top 5 con variedad (máx. 2 con solo "Acción"): A y B (empatan a 100, orden al azar), F, D,
y se rellena con C.

## Constantes (todas en `analysis.py`)

| Constante | Valor | Qué controla |
|---|---|---|
| `TOP_GENEROS` | 10 | juegos con más horas que definen tus gustos de siempre |
| `ULTIMOS_JUGADOS` | 10 | juegos recientes que forman tu racha |
| `PESO_RACHA` | 0.6 | peso de la racha frente a lo de siempre (60/40) |
| `PRESUPUESTO_GENEROS` | 20 | consultas nuevas de géneros por visita |
| `UMBRAL_PRIMO` / `PLUS_PRIMO` | 20 h / ×1,25 | consejo de la familia |
| `UMBRAL_JOYA` / `PLUS_JOYA` | 1.000 reseñas / ×1,2 | joya oculta |
| `UMBRAL_SUPERVENTAS` / `CASTIGO_SUPERVENTAS` | 100.000 reseñas / ×0,9 | superventas |
| `UMBRAL_ABANDONO` | 120 min | menos de esto (y sin jugar en 2 semanas) = abandonado |
| `PRESUPUESTO_ABANDONOS` | 10 | consultas nuevas de géneros de abandonados por visita |
| `MIN_ABANDONOS_ANTI` / `PCT_ABANDONOS_ANTI` | 3 / 25 % | mínimo de abandonos para un anti-gusto |
| `MAX_GUSTO_ANTI` / `CASTIGO_ANTI` | 20 % / ×0,8 | gusto máximo para ser anti-gusto y su castigo |
| `TOP_EXPERIENCIA` / `TOP_DEFINEN` | 10 / 3 | etiquetas de "lo que conoces" / que definen un pendiente |
| `ETIQUETAS_NEUTRAS` | ~45 | etiquetas que no dicen de qué va un juego |
| `TOP_ATREVIDOS` | 3 | juegos en "¿Te atreves?" |
| `FINALISTAS` | 15 | juegos a los que se consulta la nota de las reseñas |
| `UMBRAL_ACLAMADO` / `PLUS_ACLAMADO` | 90 % / ×1,15 | aclamado |
| `UMBRAL_MIXTO` / `CASTIGO_MIXTO` | 70 % / ×0,9 | reseñas variadas |
| `UMBRAL_MALO` / `CASTIGO_MALO` | 50 % / ×0,75 | más negativas que positivas |
| `MIN_RESENAS_NOTA` | 10 | reseñas mínimas para que el % cuente |
| `JOYA_MIN_PCT` | 80 % | % mínimo para la pegatina 💎 |
| `MAX_IGUALES` | 2 | juegos con la misma mezcla de géneros en el top |
| `TOP_RECOMENDACIONES` | 5 | recomendaciones mostradas |

## Ruleta del caos (4.4)

No es una recomendación: un juego al azar de TODA la librería con una frase absurda por plantillas
(`ruleta` en `analysis.py`). No puntúa nada.

---

# Algoritmo de compra: "¿Qué comprar?" (paso 5)

Recomienda juegos de la **tienda** que no tenéis ni tú ni tu familia, en dos listas: **mainstream**
(populares y afines) y **bizarras** (mezclas raras de tus gustos, poco conocidas pero bien valoradas).
Código: `analysis.py` (sección "Qué comprar") y `buscar_tienda` en `steam_client.py`.

## Fórmula (resumen)

```
puntos = afinidad × nota de reseñas × plus de oferta
afinidad        = suma de tus % en las 3 etiquetas en común que más pesan (TOP_AFINIDAD)
nota de reseñas = multiplicador_valoracion (el mismo del paso 4)
plus de oferta  = 1 + 0,2 × descuento / 100   (el PRECIO no puntúa: lo gratis no gana nada)
```

## Paso a paso

1. **Tus etiquetas favoritas** (`tus_etiquetas`). De cada juego jugado 2 h o más se toman sus 5
   etiquetas más votadas que dicen algo de cómo se juega (sin `ETIQUETAS_NEUTRAS` ni avisos de
   contenido) y cada una suma las horas COMPLETAS del juego. Las **amplias** (Acción, Rol, Estrategia...)
   suman aparte a mitad de peso (`PESO_AMPLIAS`), sin quitar hueco a las específicas: probado con una
   librería real, a peso completo copaban el top y la búsqueda devolvía "cualquier juego popular".
   Resultado: `{etiqueta: % de tus horas}` (no suma 100).
2. **Búsquedas** (3 llamadas a `IStoreQueryService/Query`, caché de 3 h porque los precios cambian):
   - Mainstream: tus 5 favoritas, con ALGUNA de ellas, ordenadas por popularidad.
   - Bizarras (`mezclas_raras`): tu n.º 1 y tu n.º 2, cada una con una etiqueta al azar de tus
     puestos 6.º-10.º, con LAS DOS a la vez, ordenadas por valoración.
3. **Filtros** (`candidatos_compra`): fuera lo que ya tenéis tú o tu familia, los que no están a la
   venta (sin precio y no gratis) y los **adultos** (`ETIQUETAS_ADULTAS` entre sus 5 etiquetas más
   votadas; la violencia no excluye). Mainstream: ≥ 10.000 reseñas. Bizarras: entre 50 y 10.000
   reseñas y ≥ 80 % positivas.
4. **Puntos** (`puntuar_compra`): fórmula de arriba. Las etiquetas amplias dan afinidad a mitad de
   peso porque ya pesan la mitad en tus %. Con menos de 10 reseñas, la nota no cuenta.
5. **Elección** (`elegir_compra`): de más a menos puntos (empates al azar), fuera los que no
   comparten nada contigo, como mucho **1 gratis por lista** (abundan entre los populares), como mucho
   **1 juego por desarrolladora** en las dos listas juntas (evita dos entregas de la misma saga; idea del
   usuario: el parecido de nombres se descartó porque falla con subtítulos y confunde "Dead Cells" con
   "Dead Space"; el publisher, porque los grandes publican juegos sin relación) y
   variedad con `con_variedad` (máx. 2 con la misma mezcla de etiquetas en común). 6 + 6 (la rejilla queda completa).

## Constantes (todas en `analysis.py`)

| Constante | Valor | Qué controla |
|---|---|---|
| `TOP_ETIQUETAS_GUSTO` | 5 | etiquetas específicas de cada juego que cuentan |
| `PESO_AMPLIAS` | 0,5 | peso de las etiquetas amplias |
| `TOP_FAVORITAS` | 5 | favoritas usadas en la búsqueda mainstream |
| `RAREZAS` | 6.º-10.º | puestos que se mezclan en las bizarras |
| `MEZCLAS` | 2 | búsquedas de mezclas raras |
| `UMBRAL_MAINSTREAM` | 10.000 | reseñas: mainstream desde aquí, bizarras por debajo |
| `MIN_RESENAS_BIZARRA` | 50 | reseñas mínimas de una bizarra |
| `MIN_PCT_BIZARRA` | 80 % | positivas mínimas de una bizarra |
| `PLUS_OFERTA` | 0,2 | plus máximo por descuento (100 % = × 1,2) |
| `MAX_GRATIS` | 1 | gratis como mucho por lista |
| `TOP_MAINSTREAM` / `TOP_BIZARRAS` | 6 / 6 | recomendaciones mostradas |
| `TOP_AFINIDAD` | 3 | etiquetas en común que suman afinidad (si sumaran todas, ganarían siempre los juegos con muchas etiquetas, como los de gestión) |

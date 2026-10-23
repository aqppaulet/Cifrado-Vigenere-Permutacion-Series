# Acuerdo de entradas y descifrado: alfabeto inglés A-Z

Documento para entregar a la profesora y al equipo de descifrado. Describe la versión implementada en los dos programas.

## 1. Alfabeto y formato común

El alfabeto tiene exactamente 26 letras, en este orden:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

Texto claro y cifrado deben tener **al menos una letra**. Antes de entrar al algoritmo se preprocesan: minúsculas a mayúsculas, `ñ/Ñ` a `N`, y `áéíóúü/ÁÉÍÓÚÜ` a `AEIOUU`. Se aceptan las formas Unicode compuestas y con acentos combinados. La salida siempre cumple `[A-Z]+`. Por ejemplo, `NiñoÁgil` se convierte en `NINOAGIL`. El descifrado recupera el mensaje preprocesado; no restaura tildes, Ñ ni la capitalización original.

Se rechazan espacios, tabulaciones, saltos de línea, números, signos, emojis y letras distintas de las inglesas y las españolas indicadas. El preprocesamiento no elimina espacios ni signos. Para probar una frase, escribe las palabras juntas: por ejemplo, `HolaMundo` se procesa como `HOLAMUNDO`.

No se admiten textos vacíos. No se exige una longitud múltiplo del tamaño de clave. No hay una longitud máxima fija programada; los archivos y resultados completos deben caber en memoria.

## 2. Vigenère

- Clave: una o más letras; aplica el mismo preprocesamiento que el mensaje. `LIMÓN` y `limon` se usan como `LIMON`; `AÑO` se usa como `ANO`.
- Se rechazan claves vacías, espacios incluso en los extremos, números, símbolos y letras no admitidas.
- La clave puede ser más corta, igual o más larga que el mensaje.
- Numeración: `A=0, B=1, ..., Z=25`.
- En cada mensaje, la clave empieza en su primera letra y se repite cíclicamente.
- Cifrado: `C[i] = (P[i] + K[i % longitud_clave]) mod 26`.
- Descifrado: `P[i] = (C[i] - K[i % longitud_clave]) mod 26`.
- El cifrado tiene la misma cantidad de letras que el texto claro. No lleva relleno, Base64 ni separadores.

Vector de comprobación:

```text
Texto claro:    ATTACKATDAWN
Clave:          LEMON
Texto cifrado:  LXFOPVEFRNHR
```

## 3. Permutación de series (transposición por bloques)

La clave es numérica porque indica posiciones: debe contener todos los enteros del `1` al `N`, una sola vez cada uno, con mínimo dos posiciones. Se escriben con dígitos ASCII y se separan por espacios o comas. `3 1 4 2`, `3,1,4,2` y `3, 1, 4, 2` son equivalentes. Se permiten espacios exteriores en esta clave; no saltos de línea ni tabulaciones. Se rechazan valores repetidos, negativos, cero, decimales, posiciones omitidas y fuera de rango.

El bloque tiene `N` letras. La clave indica el **orden de lectura de las posiciones del texto claro**, numeradas desde 1:

```text
Clave:                  3 1 4 2
Posiciones originales:  1 2 3 4
Bloque original:        A B C D
Bloque cifrado:         C A D B
```

Para descifrar `CADB`, se coloca `C` en la posición 3, `A` en la 1, `D` en la 4 y `B` en la 2. Se usa la **misma clave en el mismo orden**, sin invertirla antes de introducirla en el programa.

Si el último bloque tiene menos de `N` letras, se filtra la clave conservando solo las posiciones existentes, en su orden original. No se agrega relleno y el tamaño del cifrado no cambia. Se admite una clave más larga que todo el mensaje.

```text
Texto claro:          ABCDEFGHIJK
Bloques:              ABCD | EFGH | IJK
Orden último bloque:  3 1 2       (se omite la posición 4)
Bloques cifrados:     CADB | GEHF | KIJ
Texto cifrado:        CADBGEHFKIJ
```

Vectores de comprobación:

| Texto claro | Clave | Texto cifrado |
| --- | --- | --- |
| `ABCD` | `3 1 4 2` | `CADB` |
| `ABCDEFGHIJ` | `3 1 4 2` | `CADBGEHFIJ` |
| `ABCDEFGHIJK` | `3 1 4 2` | `CADBGEHFKIJ` |
| `ABC` | `3 1 4 2` | `CAB` |

## 4. Archivos e intercambio

Los archivos son texto UTF-8 **sin BOM**, una secuencia de letras admitidas sin espacios ni saltos de línea, tampoco al final. Se aplica el mismo preprocesamiento que a la entrada por línea. Un PDF o un documento de Word no es una entrada válida. Los nombres de archivo sí pueden llevar espacios.

Los archivos generados contienen únicamente el mensaje cifrado o descifrado en A-Z; no se incluyen el nombre del algoritmo ni la clave. El equipo debe comunicar por separado **qué algoritmo utilizó y cuál fue la clave exacta**. Debe conservarse todo el mensaje. La copia de la ventana y el archivo incluyen el resultado completo, aunque la vista previa esté recortada.

## 5. Casos de aceptación y rechazo

| Entrada | Resultado esperado |
| --- | --- |
| `HOLAMUNDO` | Aceptada. |
| `HolaMundo` | Aceptada y normalizada a `HOLAMUNDO`. |
| `HOLA MUNDO` | Rechazada por espacio. |
| `AÑO`, `CAFÉ`, `pingüino` | Aceptadas; se procesan como `ANO`, `CAFE`, `PINGUINO`. |
| `ABC123`, `HOLA!` | Rechazadas. |
| Mensaje vacío o archivo vacío | Rechazado. |
| Archivo que termina con salto de línea | Rechazado. |
| Vigenère, clave `LEMON` | Aceptada. |
| Vigenère, clave `AÑO` | Aceptada y preprocesada a `ANO`. |
| Vigenère, clave ` LEMON ` | Rechazada. |
| Permutación, clave `3 1 4 2` | Aceptada. |
| Permutación, clave `1 1 2`, `2 3` o `1` | Rechazada. |

## 6. Límites del descifrado

Se valida el formato de las entradas. No se comprueba que la clave sea la correcta ni que el mensaje esté íntegro: una clave equivocada, una alteración o un recorte pueden producir otras letras sin aviso. Para las pruebas entre equipos, comparen la salida con los vectores de este documento antes de intercambiar mensajes nuevos.

# Cifrado y descifrado en Python

Dos implementaciones con menú en español. Requieren Python 3.9 o posterior y no necesitan instalar bibliotecas. Mantén los tres archivos `.py` juntos: `interfaz.py` contiene el menú compartido.

Ambos aceptan texto con mayúsculas, minúsculas, números, símbolos, espacios, tildes, `ñ`, emojis y otros caracteres Unicode. También aceptan texto vacío o formado solo por espacios. No se eliminan los espacios iniciales, finales o repetidos. Al descifrar se recupera exactamente el texto original. Vigenère clásico deja intactos los caracteres ajenos al alfabeto elegido; **Vigenère ampliado cifra todo el texto**, incluidos símbolos y espacios. Permutación cambia la posición de todos los caracteres.

## Uso con menú

Desde esta carpeta, ejecuta uno de estos comandos:

```bash
python3 vigenere.py
python3 permutacion_series.py
```

1. Elige **Cifrar** o **Descifrar**.
2. Para Vigenère, elige **3) Ampliado: todos los caracteres** (opción predeterminada al pulsar Enter), o uno de los dos modos clásicos.
3. Introduce la clave.
4. Escribe una línea, pega varias líneas o introduce el nombre de un archivo UTF-8 que esté en la carpeta del proyecto.
5. Revisa el resultado: se guarda automáticamente en la carpeta del proyecto, sin sobrescribir archivos ni preguntar por el nombre.

| Programa | Cifrado | Descifrado |
| --- | --- | --- |
| Vigenère (clásico o ampliado) | `cV1.txt`, `cV2.txt`, etc. | `dV1.txt`, `dV2.txt`, etc. |
| Permutación de series | `cP1.txt`, `cP2.txt`, etc. | `dP1.txt`, `dP2.txt`, etc. |

Con entrada por teclado (una o varias líneas) se muestra el resultado completo en pantalla. Con entrada desde un archivo se muestran las primeras **5 líneas** del resultado, tanto al cifrar como al descifrar, con hasta **200 caracteres por línea** para evitar vistas previas enormes. Si se recorta contenido, se indica que la vista previa está truncada. El archivo de salida siempre contiene el resultado completo. Esto también se aplica a los argumentos `--texto` y `--archivo`.

Para leer un archivo, introduce solo su nombre, sin rutas. Si escribes `mensaje`, se agrega `.txt` automáticamente. La carpeta del proyecto es la que contiene estos programas, incluso si los ejecutas desde otra carpeta. Las cuatro series (`cV`, `dV`, `cP`, `dP`) tienen numeración independiente y eligen el primer nombre libre de su secuencia. Tanto cifrar como descifrar generan un archivo nuevo.

En la entrada de varias líneas, una línea con solo `FIN` termina la captura; no forma parte del texto. Las líneas vacías sí se conservan. Si tu texto contiene una línea `FIN` o necesitas conservar exactamente el salto final, usa un archivo.

## 1. Vigenère

### Ampliado: todos los caracteres Unicode

Ejecuta `python3 vigenere.py`, elige cifrar o descifrar y selecciona el modo **3**. La clave puede contener letras, números, símbolos, emojis y espacios; debe tener al menos un carácter. Las mayúsculas y minúsculas son distintas, y los espacios de la clave se conservan, incluso al inicio o al final. Para descifrar necesitas el mismo modo y la clave exacta.

Esta variante convierte el texto y la clave a UTF-8 y aplica Vigenère sobre un alfabeto de 256 bytes: `cifrado[i] = (texto[i] + clave[i % longitud_clave]) % 256`. Para descifrar resta en vez de sumar. Así también se transforman los bytes de los números, símbolos, espacios y saltos de línea.

El cifrado binario se representa en **Base64** para poder mostrarlo y guardarlo como texto, en líneas de hasta 80 caracteres. Base64 es solo la representación del resultado tras cifrar. Los saltos de línea del texto original se recuperan al descifrar. Puedes pegar el cifrado en la opción de varias líneas o leerlo directamente de su archivo.

```bash
python3 vigenere.py --cifrar --ampliado -k "Mi clave #2026 🔑" -t "¡Hola! 123 @# 🙂"
python3 vigenere.py --descifrar --ampliado -k "Mi clave #2026 🔑" -a cV1.txt
```

El segundo comando supone que el primero creó `cV1.txt`; usa el nombre que muestre el programa. El descifrado se guardará como `dV1.txt` si está disponible. En línea de comandos debes indicar `--ampliado` tanto al cifrar como al descifrar. Sin `--ampliado` se usa el modo clásico, para conservar la compatibilidad con los ejemplos anteriores.

### Clásico: letras A-Z o alfabeto español

Cada letra se desplaza según la siguiente letra de la clave, que se repite. En el alfabeto de 26 letras, `A` desplaza 0 posiciones, `B` desplaza 1, etc.

```text
Texto:    ATTACKATDAWN
Clave:    LEMON
Cifrado:  LXFOPVEFRNHR
```

- La clave acepta letras mayúsculas o minúsculas, sin espacios internos ni tildes. Se ignoran espacios al inicio o final de la clave.
- Se conservan mayúsculas y minúsculas del texto.
- Los caracteres ajenos al alfabeto elegido, como tildes, números, emojis, signos y saltos de línea, quedan intactos y no consumen letras de la clave.
- En el modo de 26 letras, `ñ` queda intacta. En el modo español se cifra y puede aparecer en la clave; su posición es entre `N` y `O`.
- Para descifrar necesitas la misma clave **y el mismo alfabeto**.

```bash
python3 vigenere.py --cifrar --clave LEMON --texto "ATTACKATDAWN"
python3 vigenere.py --descifrar --clave LEMON --texto "LXFOPVEFRNHR"
python3 vigenere.py --cifrar --espanol --clave AÑO --texto "Hola, señor 👋"
```

## 2. Permutación de series

Aquí se implementa como **transposición por bloques**: la longitud de la clave determina el tamaño del bloque y sus números indican el orden de lectura de las posiciones originales, numeradas desde 1.

```text
Clave:             3 1 4 2
Bloque original:   A B C D
Bloque cifrado:    C A D B

Texto:             ABCDEFGHIJ
Cifrado:           CADBGEHFIJ
```

- Usa todos los números del `1` al tamaño del bloque, una sola vez cada uno; mínimo dos números.
- Acepta espacios o comas: `3 1 4 2` y `3,1,4,2` son equivalentes.
- Reordena todos los caracteres, incluidos espacios, tildes, emojis y saltos de línea.
- Si el último bloque está incompleto, omite las posiciones que no existen. Por ejemplo, para `IJ` la clave `3 1 4 2` se reduce a `1 2`, dando `IJ`; para `IJK` se reduce a `3 1 2`, dando `KIJ`.
- No agrega relleno: al descifrar recuperas el texto exacto, incluidos los espacios finales.

```bash
python3 permutacion_series.py --cifrar --clave "3 1 4 2" --texto "ABCDEFGHIJ"
python3 permutacion_series.py --descifrar --clave "3,1,4,2" --texto "CADBGEHFIJ"
```

## Archivos y ayuda

Ambos programas aceptan los mismos argumentos de entrada y guardan automáticamente el resultado:

```bash
python3 vigenere.py --cifrar -k LIMON -a mensaje.txt
python3 vigenere.py --descifrar -k LIMON -a cV1.txt

python3 permutacion_series.py --cifrar -k "3 1 4 2" -a mensaje.txt
python3 permutacion_series.py --descifrar -k "3 1 4 2" -a cP1.txt

python3 vigenere.py --help
python3 permutacion_series.py --help
```

Los ejemplos de archivos suponen que no había resultados antes de ejecutar esos cuatro comandos en orden. Para descifrar, usa el nombre que el programa haya mostrado al cifrar. Usa comillas para nombres con espacios. `--archivo` acepta solo nombres de archivos dentro del proyecto. Los resultados se numeran automáticamente según el programa y la operación (`cV`, `dV`, `cP` o `dP`); ya no se usa `--salida`. Los archivos conservan sus saltos de línea originales y deben tener codificación UTF-8.

También puedes importar las funciones en otro programa:

```python
import vigenere
import permutacion_series

texto = "¡Hola, señor!\nPython 123 🙂  "
cifrado = vigenere.cifrar(texto, "AÑO", espanol=True)
assert vigenere.descifrar(cifrado, "AÑO", espanol=True) == texto

cifrado = vigenere.cifrar(texto, " Mi clave #2026 🔑 ", ampliado=True)
assert vigenere.descifrar(cifrado, " Mi clave #2026 🔑 ", ampliado=True) == texto

cifrado = permutacion_series.cifrar(texto, "3 1 4 2")
assert permutacion_series.descifrar(cifrado, "3 1 4 2") == texto
```

Para comprobar los ejemplos, la validación de claves y la recuperación exacta de archivos:

```bash
python3 -m unittest -v
```

La suite incluye 44 pruebas, 500 textos Unicode aleatorios en cuatro modos, textos grandes, 12 procesos simultáneos y errores simulados de escritura. Las pruebas usan carpetas temporales y no modifican tus resultados. Consulta [INFORME_PRUEBAS.md](INFORME_PRUEBAS.md) para ver los fallos encontrados, sus correcciones y las limitaciones que siguen presentes.

Una clave incorrecta o un cifrado truncado no siempre se detectan: estos algoritmos no comprueban la integridad del mensaje. Recuperar texto legible no confirma que la clave y el archivo sean correctos.

Estos cifrados clásicos son para prácticas educativas; no protegen datos sensibles.

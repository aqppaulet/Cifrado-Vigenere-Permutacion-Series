# Informe de pruebas — 21 de octubre de 2026

Resultado: **44 pruebas pasan** en Python 3.13.5. Incluyen las 25 pruebas anteriores y 19 nuevas. El conjunto completo terminó en aproximadamente 2,6 segundos en este equipo. Las pruebas nuevas se encuentran en `tests/test_limites.py`.

## Fallos reproducidos y corregidos

| Caso | Comportamiento anterior | Corrección |
| --- | --- | --- |
| Leer una tubería con nombre como si fuera un archivo | Los dos programas quedaban esperando datos indefinidamente. Se reprodujo y detuvo el bloqueo mediante un tiempo límite. | Se comprueba que la entrada sea un archivo regular antes de leerla. Se rechazan tuberías, carpetas y dispositivos. |
| Escritura interrumpida o sin espacio disponible | Quedaba un archivo de salida parcial con un nombre de resultado normal. | Se intenta eliminar el archivo recién creado si falla la escritura o se interrumpe con Ctrl-C. Se conservan los archivos anteriores. Se probaron los fallos mediante simulación de falta de espacio e interrupción; no se llenó el disco. |
| Cifrado Base64 con bits de relleno alterados | Por ejemplo, `DvR=` se aceptaba igual que `DvQ=` pese a que el programa solo genera la segunda forma. | Se exige la representación Base64 canónica. Se siguen permitiendo espacios y saltos de línea al pegar el cifrado. |
| Archivo con una sola línea enorme | La vista previa imprimía la línea completa; una entrada de 20 000 caracteres generaba más de 20 000 caracteres en consola. | La vista previa de archivo muestra hasta cinco líneas, con un máximo de 200 caracteres por línea y un aviso si recorta. El archivo completo se conserva. La entrada por teclado sigue mostrando todo. |
| Archivo con otra codificación | Mostraba el mensaje técnico de decodificación de Python en inglés. | Ahora indica en español que el archivo debe guardarse con codificación UTF-8. |

También se sustituyó el ajuste de líneas del Base64 por cortes de longitud fija, manteniendo exactamente el formato generado. Para un texto de 1 000 000 de caracteres, una medición anterior tardó 0,525 s; después del cambio, tres mediciones tardaron 0,095, 0,094 y 0,094 s. Es una comparación orientativa de este equipo, no una garantía de rendimiento.

## Cobertura adicional

- **500 textos aleatorios reproducibles**, cada uno comprobado en Vigenère clásico, clásico español, ampliado y permutación: 2 000 recuperaciones exactas adicionales. Se mezclan letras, símbolos, controles, emojis, caracteres combinados y puntos de código Unicode válidos. Se usa una semilla fija para poder repetir los casos.
- Texto grande de **900 007 bytes en UTF-8**, recuperado exactamente en los cuatro modos. La medición adicional de un millón de caracteres también comprobó la recuperación exacta.
- **12 procesos simultáneos** creando cifrados: todos los resultados fueron distintos, completos y sin sobrescribir el archivo que ya existía.
- Archivos inexistentes, carpetas, enlaces circulares, entradas no UTF-8 y tuberías: mensajes de error sin un traceback de Python.
- Numeración con huecos y separación de las cuatro series `cV`, `dV`, `cP` y `dP`: los archivos existentes se mantienen intactos.
- Menús con opciones incorrectas, claves inválidas y nombres de archivo equivocados: permiten reintentar.
- Fin inesperado de la entrada durante la captura de texto: no se genera un cifrado incompleto.
- Claves de permutación duplicadas, fuera de rango, con 5 000 dígitos o con formato incorrecto: se rechazan.
- Claves de permutación más largas que el texto: el bloque incompleto se cifra y descifra correctamente.
- Texto y claves que empiezan por guion en la línea de comandos: funcionan con `--texto=-Hola` y `--clave=-#`.
- Permisos de escritura denegados: se simula el error y se comprueba que no se cree un resultado.

Los archivos de las pruebas se crean en carpetas temporales; los resultados reales del proyecto no se usan ni se sobrescriben.

## Limitaciones confirmadas que siguen presentes

1. **Una clave incorrecta puede dar texto válido sin avisar.** En el ampliado, cifrar `Hola` con `B` y descifrar con `C` produce `Gnk\x60`, que es texto UTF-8 válido. Las pruebas documentan este comportamiento; no lo presentan como una detección correcta de la clave. En los modos clásicos y en permutación tampoco hay una comprobación de clave correcta.
2. **Algunos recortes pasan desapercibidos.** Cifrar `Hola mundo` con `B` en modo ampliado y conservar solo los primeros cuatro caracteres Base64 permite recuperar `Hol` sin error. La validación del formato no detecta una pérdida que siga formando Base64 válido. Para detectar estos casos de forma fiable habría que agregar una comprobación de integridad y definir un formato de mensaje nuevo.
3. **Los archivos deben ser texto UTF-8.** Un PDF, una imagen o texto guardado en otra codificación no se admite como archivo de entrada de estos programas.
4. **Los archivos se procesan completos en memoria.** Las pruebas con textos grandes no garantizan que un archivo de varios gigabytes quepa en la memoria disponible. No se ha implementado procesamiento por fragmentos.
5. **`FIN` termina la captura de varias líneas.** Si el contenido incluye una línea con solo `FIN`, debe usarse un archivo o `--texto` para conservarla como parte del mensaje.
6. **La limpieza de un resultado parcial necesita que Python pueda ejecutarla.** Un corte de energía o una terminación forzada del proceso puede impedirla. Tampoco se simularon daños físicos del disco.

Estas pruebas comprueban comportamiento y manejo de errores; no certifican la seguridad criptográfica de los algoritmos.

## Repetir las pruebas

Desde la carpeta del proyecto:

```bash
python3 -m unittest discover -s tests -v
```

Solo las pruebas nuevas:

```bash
python3 -m unittest tests.test_limites -v
```

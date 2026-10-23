# Taller de cifrado A-Z: web para GitHub Pages

La versión web está en **`docs/`** y funciona en el navegador sin instalar Python ni Tkinter. Tiene interfaces separadas para **Vigenère** y **permutación de series**, entrada por **una línea o archivo**, preprocesamiento visible a A-Z y botones para copiar o descargar el resultado completo.

- [Abrir Vigenère](docs/index.html).
- [Abrir permutación](docs/permutacion.html).
- [Reglas para la profesora y el equipo de descifrado](docs/limites.html).
- [Cómo publicarla en GitHub Pages](PUBLICAR_WEB.md).

El preprocesamiento convierte `NiñoÁgil` en `NINOAGIL` y la clave `LIMÓN` en `LIMON`. El algoritmo recibe solo letras A-Z. El descifrado recupera el texto preprocesado; no restaura Ñ, tildes ni la capitalización original. Solo al cifrar se aceptan y eliminan espacios del mensaje: `Hola Mundo` se usa como `HOLAMUNDO`. El descifrado y las claves conservan sus reglas. En permutación, el pretratamiento también elimina los dígitos 0-9 solo al cifrar; Vigenère sigue rechazándolos. Los símbolos y saltos de línea siguen sin admitirse.

Abre `docs/index.html` directamente, o ejecuta desde esta carpeta:

```bash
python3 -m http.server 8000 --directory docs
```

Después abre `http://localhost:8000`. Para alojarla en GitHub Pages, publica la carpeta **`/docs`** desde la rama que contenga estos cambios. La configuración paso a paso está en [PUBLICAR_WEB.md](PUBLICAR_WEB.md). La rama de esta versión es **`web/github-pages`**; para servirla, activa GitHub Pages usando esa rama y **`/docs`**.

No hay compilación, bibliotecas externas ni envío de mensajes, claves o archivos a servidores. Las rutas relativas funcionan bajo la subruta de un repositorio de GitHub Pages. El diseño se adapta a escritorio y móvil; las páginas se desplazan de forma normal cuando el contenido supera la pantalla.

`python3 preparar_paquete.py` genera **`Cifrados_Web.zip`**, que contiene solo la web, y **`Cifrados_AZ.zip`**, con el proyecto completo. Para compartir la web sin GitHub, basta con extraer el ZIP web y abrir `index.html` en un navegador moderno.

Las comprobaciones web se ejecutan con `python3 tests/verificar_web.py` (requiere Firefox solo para probar). El informe está en [INFORME_PRUEBAS.md](INFORME_PRUEBAS.md).

## Versión de escritorio (opcional)

Dos aplicaciones gráficas independientes, en español, para cifrar y descifrar. Cada ventana muestra las reglas, la clave que necesita, el texto preprocesado y un ejemplo. Al abrirse se centra y ajusta al tamaño de la pantalla; en pantallas pequeñas dispone de desplazamiento vertical para mantener accesibles todos los controles. Permiten escribir **una línea** o elegir **un archivo de texto** desde cualquier carpeta.

Solo requieren **Python 3.9 o posterior con Tkinter**. No usan pip, navegador, servidor, conexión a Internet ni bibliotecas externas durante su ejecución.

## Abrir las ventanas

Descomprime el ZIP completo en una carpeta donde puedas guardar archivos. Conserva la carpeta `cifrados` junto a los lanzadores.

**Windows:** con Python instalado y los archivos `.pyw` asociados a Python, abre con doble clic `Vigenere.pyw` o `Permutacion.pyw`. También puedes usar `py Vigenere.pyw` o `py Permutacion.pyw` desde una terminal.

**Linux o macOS:** desde la carpeta del proyecto:

```bash
python3 vigenere.py
python3 permutacion_series.py
```

En Debian/Ubuntu, si aparece «Falta Tkinter», instálalo con `sudo apt-get install python3-tk`. En Windows, habilita Tcl/Tk al instalar Python. En macOS, usa una distribución de Python que incluya Tkinter. La interfaz necesita una sesión de escritorio gráfico.

## Cómo usar cualquiera de las dos ventanas

1. Elige **Cifrar** o **Descifrar**.
2. Escribe la clave siguiendo las instrucciones de esa ventana.
3. Selecciona **Una línea** y escribe el mensaje, o **Archivo .txt** y pulsa **Elegir archivo…**.
4. Pulsa **Cifrar y guardar** o **Descifrar y guardar**. También funciona `Ctrl+Enter`.
5. Revisa el campo **Preprocesado**, el resultado y su ruta de guardado. **Copiar resultado completo** permite pasarlo a otra persona.

Los errores indican qué corregir; los datos del formulario se conservan. **Limpiar** borra la clave y las entradas para empezar otro mensaje. Si cambias una entrada, el resultado anterior desaparece para evitar confundirlo con el de la nueva entrada.

## Reglas del mensaje y las claves

| Entrada | Regla |
| --- | --- |
| Texto claro y texto cifrado | Una o más letras. Antes del algoritmo se normalizan a `ABCDEFGHIJKLMNOPQRSTUVWXYZ`. |
| Preprocesamiento | Minúsculas a mayúsculas; `ñ/Ñ` a `N`; `áéíóúü` y sus mayúsculas a `AEIOUU`. También acepta estas letras con acentos Unicode combinados. |
| Espacios en los mensajes | Solo al cifrar se aceptan y eliminan. Al descifrar se rechazan. |
| Dígitos 0-9 en permutación | Solo al cifrar se eliminan del mensaje durante el pretratamiento, antes de formar bloques. No se eliminan de la clave. Vigenère y el descifrado siguen rechazándolos en el mensaje. |
| Caracteres rechazados en los mensajes | Saltos de línea, tabulaciones, números, símbolos, emojis y letras fuera de A-Z/a-z y las letras españolas indicadas. |
| Mensaje vacío | Se rechaza. |
| Clave de Vigenère | Una o más letras; aplica el mismo preprocesamiento que el mensaje. Ejemplo: `LIMÓN` se usa como `LIMON`. Sin espacios, números ni símbolos. |
| Clave de permutación | Una permutación de los números `1` a `N`, sin repetir ni omitir posiciones, con `N >= 2`. Separa con espacios o comas. Ejemplo: `3 1 4 2`. |
| Archivo de entrada | Texto UTF-8 sin BOM, con una sola secuencia de letras, **sin salto de línea final**. |

Los números y separadores de la clave de permutación representan posiciones; el mensaje de ese algoritmo sigue usando solo letras. Se permiten espacios alrededor de esa clave numérica; no se permiten en la clave de Vigenère ni en el texto cifrado al descifrar. Al cifrar, los espacios del mensaje se eliminan. El preprocesamiento sustituye las tildes y Ñ indicadas automáticamente, sin eliminar otros caracteres inválidos. Por ejemplo, `NiñoÁgil` se convierte en `NINOAGIL`. Al descifrar se recupera ese texto preprocesado; las tildes, la Ñ y la capitalización original no se restauran.

No hay un límite fijo de longitud del mensaje. La clave de Vigenère puede ser más larga o más corta que el mensaje. La clave de permutación puede definir un bloque mayor que el mensaje. Ambos algoritmos cargan el contenido completo en memoria.

Para crear un archivo de ejemplo sin salto final:

```bash
python3 -c "from pathlib import Path; Path('mensaje.txt').write_text('ATTACKATDAWN', encoding='utf-8')"
```

## Ejemplos para comprobar la implementación

| Algoritmo | Texto claro | Clave | Texto cifrado |
| --- | --- | --- | --- |
| Vigenère | `ATTACKATDAWN` | `LEMON` | `LXFOPVEFRNHR` |
| Permutación | `ABCDEFGHIJ` | `3 1 4 2` | `CADBGEHFIJ` |
| Permutación, último bloque de 3 letras | `ABCDEFGHIJK` | `3 1 4 2` | `CADBGEHFKIJ` |

Vigenère usa `A=0`, ..., `Z=25`, suma para cifrar y resta para descifrar, módulo 26. La clave se repite desde el principio para cada mensaje.

Permutación divide el texto en bloques de `N` letras y lee sus posiciones según la clave, numeradas desde 1. Por ejemplo, `ABCD` con `3 1 4 2` produce `CADB`. Si el último bloque está incompleto, se omiten las posiciones que no existen y **no se agrega relleno**. Para descifrar se colocan las letras en esas posiciones originales. Debe conservarse la misma clave en el mismo orden.

El documento [LIMITACIONES_DESCIFRADO.md](LIMITACIONES_DESCIFRADO.md) contiene el acuerdo completo para compartir con la profesora y el equipo de descifrado.

## Archivos de salida

Se guardan automáticamente en la carpeta del programa. Cada operación usa el primer número libre y conserva los archivos existentes.

| Aplicación | Cifrar | Descifrar |
| --- | --- | --- |
| Vigenère | `cV1.txt`, `cV2.txt`, ... | `dV1.txt`, `dV2.txt`, ... |
| Permutación | `cP1.txt`, `cP2.txt`, ... | `dP1.txt`, `dP2.txt`, ... |

Los resultados contienen solo letras A-Z, sin cabeceras, relleno ni salto final. Las ventanas muestran hasta 2000 letras para que la vista previa siga siendo manejable; el archivo y el botón de copia incluyen el resultado completo. Si no se puede guardar, se muestra un aviso y el resultado sigue disponible para copiar.

## Compartir

Ejecuta `python3 preparar_paquete.py` para crear `Cifrados_AZ.zip`. Envía ese ZIP y pide que lo **extraigan antes de abrir** los programas. Incluye las aplicaciones, los lanzadores de Windows, ejemplos, instrucciones, limitaciones y pruebas. No incluye resultados personales, el historial Git, cachés ni un intérprete de Python. **No es un ejecutable autónomo: el destinatario necesita Python con Tkinter.**

## Consola opcional y pruebas

Los mismos algoritmos también aceptan argumentos para automatizar comprobaciones:

```bash
python3 vigenere.py --cifrar -k LEMON -t ATTACKATDAWN
python3 vigenere.py --descifrar -k LEMON -t LXFOPVEFRNHR
python3 permutacion_series.py --cifrar -k "3 1 4 2" -t ABCDEFGHIJ
python3 permutacion_series.py --descifrar -k "3 1 4 2" -t CADBGEHFIJ
python3 vigenere.py --help
python3 -m unittest discover -s tests -v
```

En consola, `--archivo` acepta nombres de archivos dentro del proyecto; en la ventana, el selector permite cualquier carpeta. Las pruebas usan carpetas temporales. Las de las ventanas necesitan Tkinter y un escritorio; si faltan, se omiten e indican el motivo. Consulta [INFORME_PRUEBAS.md](INFORME_PRUEBAS.md) para ver la verificación realizada.

## Organización del código

- `cifrados/vigenere.py` y `cifrados/permutacion.py`: algoritmos comentados.
- `cifrados/validacion.py`: alfabeto y validación común.
- `cifrados/interfaz_vigenere.py` y `cifrados/interfaz_permutacion.py`: instrucciones y configuración de cada interfaz.
- `cifrados/ventana.py`: formulario gráfico reutilizable.
- `cifrados/archivos.py`: lectura UTF-8 y guardado sin sobrescribir.
- `cifrados/interfaz.py`: inicio gráfico y argumentos opcionales.

Los algoritmos reciben únicamente A-Z después del preprocesamiento de entrada. Los cifrados antiguos del modo español o ampliado no forman parte del formato actual. Una clave equivocada o un mensaje recortado pueden dar un resultado de letras sin producir error: no hay comprobación de integridad.

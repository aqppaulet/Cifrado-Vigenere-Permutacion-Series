# Informe de pruebas — 23 de octubre de 2026

**49 pruebas pasan, sin omisiones**, en Python 3.13.5. Incluyen catorce pruebas de las ventanas con widgets reales de Tkinter en una pantalla virtual Xvfb. La ejecución completa terminó en aproximadamente 4,2 segundos en este equipo.

## Aplicación web

**24 pruebas web pasan en Firefox real**, además de las 49 pruebas Python indicadas arriba. Se usa un perfil temporal y un servidor limitado a localhost; la aplicación se sirve bajo una subruta de proyecto para comprobar las rutas de GitHub Pages.

- Solo el cifrado de permutación elimina dígitos 0-9 durante el pretratamiento desde línea o archivo, antes de formar bloques. Se comprueba que Vigenère y el descifrado sigan rechazando números y que una entrada sin letras se rechace.
- Ambos cifrados eliminan espacios iniciales, finales, internos y repetidos desde línea o archivo. El descifrado sigue rechazando espacios; las claves y el rechazo de tabulaciones/saltos no cambian.
- Vectores conocidos y **200 mensajes aleatorios comparados con Python**: cifrado, descifrado y preprocesamiento idénticos, incluidas Ñ, tildes y diéresis en ambas capitalizaciones.
- Validación de mensajes y claves; rechazo de espacios al descifrar y en la clave de Vigenère, saltos, símbolos, Unicode no admitido, BOM y UTF-8 defectuoso.
- Ambas interfaces: entrada por línea y archivo, preprocesado visible, cifrado, descifrado, limpieza, carga de ejemplo e invalidación del resultado al cambiar la clave.
- Descarga: nombre de archivo por algoritmo/operación y contenido completo sin salto final.
- Disposición sin desbordamiento horizontal y controles visibles con anchos de **360, 390, 768 y 1366 píxeles**. Se comprueba además que las acciones principales de ambas páginas sean visibles sin desplazar en portátiles de **1366×768**.
- Navegación, documento de limitaciones y recursos servidos desde una subruta.

Para repetir: `python3 tests/verificar_web.py`. Solo las pruebas necesitan Python y Firefox; el sitio publicado funciona sin ellos, en un navegador moderno.

La verificación descrita comprueba la web local, no un despliegue remoto. La rama preparada para publicación es `web/github-pages`, con la carpeta `/docs` como origen de GitHub Pages.

## Comprobaciones Python y escritorio realizadas

- Vigenère: vector `ATTACKATDAWN` + `LEMON` = `LXFOPVEFRNHR`, vuelta de Z a A, clave de una letra y clave mayor que el mensaje.
- Permutación: vectores de referencia, bloques completos e incompletos y todas las permutaciones de tamaños 2 a 5 con diferentes restos.
- **500 mensajes aleatorios reproducibles por algoritmo** (semilla `20261023`): 1000 recuperaciones del texto normalizado en mayúsculas.
- Mensaje de **un millón de letras** procesado y recuperado por ambos algoritmos.
- Rechazo de mensajes y claves inválidas: vacío, solo espacios, espacios al descifrar o en claves de Vigenère, saltos de línea, números, símbolos, caracteres Unicode que se expanden al convertir a mayúsculas, BOM y tipos incorrectos.
- Formato de la clave numérica: separadores equivalentes, duplicados, rangos incorrectos, dígitos no ASCII y posiciones excesivamente largas.
- Preprocesamiento de Ñ, vocales acentuadas y diéresis en ambas capitalizaciones, incluyendo acentos Unicode combinados; resultados idénticos desde línea y archivo. La clave de Vigenère aplica las mismas reglas.
- CLI: cifrado y descifrado desde texto y archivos, normalización a mayúsculas, errores sin traceback y eliminación de los modos español/ampliado.
- Ventanas: inicio de las dos aplicaciones, botones de cifrado y descifrado, etiquetas, selector de archivos fuera del proyecto y cancelación del selector.
- Ventanas: mensajes de error, corrección de las entradas, limpieza, alternancia de línea/archivo y eliminación del resultado anterior cuando cambia el formulario.
- Ventanas: campo de texto preprocesado, centrado y tamaño inicial dentro de pantallas de 1366×768, 1024×600 y 800×600, con desplazamiento para acceder al final si el formulario no cabe.
- Ventanas: vista previa limitada a 2000 letras, copia completa al portapapeles y archivo completo sin salto de línea final.
- Fallo de guardado gráfico: avisa y permite copiar el resultado calculado.
- Archivos inexistentes, carpetas, tuberías, enlaces circulares y contenido no UTF-8: se rechazan sin bloquear.
- Guardado de **12 procesos simultáneos** sin sobrescribir archivos existentes; numeración con huecos y series independientes.
- Errores simulados de permisos, falta de espacio e interrupción: no quedan resultados parciales, y se mantienen los archivos anteriores.

Las pruebas trabajan con carpetas temporales y no usan resultados personales del proyecto.

## Repetir

Con Python, Tkinter y una sesión gráfica:

```bash
python3 -m unittest discover -s tests -v
```

En Linux con Tkinter y Xvfb instalados, para probar sin mostrar ventanas:

```bash
xvfb-run -a python3 -m unittest discover -s tests -v
```

Si falta Tkinter o no hay escritorio, las catorce pruebas gráficas se omiten explícitamente. El resto sigue comprobando algoritmos, archivos, argumentos e inicio de las interfaces.

En esta verificación, Tkinter y Xvfb se descargaron y extrajeron en `/tmp` para ejecutar todas las pruebas. No se instalaron paquetes del sistema, porque sudo requería una contraseña de administrador. El ZIP compartible no incluye estas herramientas temporales.

## Límites confirmados

- El descifrado devuelve el texto preprocesado A-Z; no recupera Ñ, tildes, diéresis ni capitalización original.
- Una clave equivocada o un mensaje recortado puede producir letras válidas sin aviso. No hay comprobación de integridad.
- Los mensajes completos se mantienen en memoria. La prueba de un millón de letras no garantiza capacidad para archivos de varios gigabytes.
- Los archivos de entrada deben contener únicamente letras, sin BOM ni salto final. La aplicación preprocesa letras españolas y elimina espacios comunes solo al cifrar; el descifrado y las claves conservan sus validaciones.
- No se ha comprobado la ejecución visual en Windows o macOS. Los lanzadores `.pyw` y las interfaces usan la biblioteca estándar de Python.
- Un corte de energía o una terminación forzada puede impedir la limpieza de una escritura parcial.

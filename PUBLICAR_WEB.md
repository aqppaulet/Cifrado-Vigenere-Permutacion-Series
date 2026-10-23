# Publicar el taller de cifrado en GitHub Pages

La aplicación web está en `docs/`. Es HTML, CSS y JavaScript estático: no necesita Python, Node, npm, servidor propio, claves de API ni una etapa de compilación. Los mensajes, claves y archivos se procesan en el navegador del usuario.

## Probar antes de publicar

Abre `docs/index.html` en el navegador. También puedes servir la carpeta desde el proyecto:

```bash
python3 -m http.server 8000 --directory docs
```

Abre `http://localhost:8000`. Para terminar el servidor, pulsa `Ctrl+C`.

- `index.html`: Vigenère, con clave de letras.
- `permutacion.html`: transposición por bloques, con clave de posiciones.
- `limites.html`: reglas, ejemplos y acuerdo para el equipo de descifrado.

Ambas interfaces permiten una línea o un archivo UTF-8, muestran el texto preprocesado y permiten copiar o descargar el resultado completo. La descarga ocurre cuando se pulsa el botón; el navegador decide la carpeta de destino. Los contadores de nombres se reinician al abrir de nuevo la página.

## Activar GitHub Pages

1. Sube los cambios de `docs/` al repositorio `aqppaulet/Cifrado-Vigenere-Permutacion-Series`.
2. En GitHub, abre **Settings → Pages** del repositorio.
3. En **Build and deployment → Source**, elige **Deploy from a branch**.
4. Selecciona la rama que contenga la web y la carpeta **`/docs`**. La rama preparada para esta versión es **`web/github-pages`** y la carpeta es **`/docs`**. No hace falta integrar los cambios en `main`.
5. Pulsa **Save** y espera a que GitHub termine el despliegue. Pages mostrará el enlace publicado; los errores aparecerán en Actions.

GitHub admite la carpeta `/docs` de una rama como origen de publicación. Consulta la [documentación oficial de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

La dirección esperada, una vez activado el servicio para este repositorio, es:

```text
https://aqppaulet.github.io/Cifrado-Vigenere-Permutacion-Series/
```

Subir la rama publica el código en GitHub. La web queda accesible cuando se activa Pages con el origen `web/github-pages` y `/docs`. Usa el enlace que confirme GitHub tras desplegar.

## Compartir sin GitHub

Ejecuta `python3 preparar_paquete.py` y comparte `Cifrados_Web.zip`. El destinatario puede extraerlo y abrir `index.html` en un navegador moderno, sin instalar Python ni Tkinter. El botón de copia puede requerir HTTPS o localhost; si el navegador lo restringe al abrir un archivo, la aplicación selecciona el resultado para copiarlo manualmente.

## Preprocesamiento y límites

Se aplican las mismas reglas que en Python: minúsculas a mayúsculas, Ñ a N, y áéíóúü a AEIOUU, incluidas sus versiones mayúsculas y formas con acentos combinados. Los algoritmos reciben solo A-Z. El descifrado no restaura la escritura original.

Se rechazan espacios, saltos de línea, números, símbolos, mensajes vacíos y archivos con BOM. La clave de Vigenère usa el mismo preprocesamiento; la clave de permutación sigue siendo numérica. Los archivos se leen completos en memoria.

Todos los recursos están dentro de `docs/`, con rutas relativas para funcionar bajo la subruta del repositorio. No se usan fuentes externas, analítica ni llamadas a servidores desde la aplicación. El acuerdo completo también está disponible en la propia web.

## Verificación

```bash
python3 tests/verificar_web.py
```

Requiere Firefox únicamente para las pruebas. El programa crea un perfil temporal y un servidor en localhost, comprueba los algoritmos contra resultados de Python y prueba ambos formularios, lectura de archivos, descargas y tamaños de móvil y escritorio. Cierra el navegador y el servidor al terminar. Los usuarios de la web no necesitan estas herramientas.

"""Interfaz de consola compartida por los dos programas; sin dependencias externas."""

import argparse
from pathlib import Path
import stat
from typing import Callable


CARPETA_PROYECTO = Path(__file__).resolve().parent
LINEAS_VISTA_PREVIA = 5
CARACTERES_POR_LINEA_PREVIA = 200


def _ruta_archivo(nombre: str) -> Path:
    nombre = nombre.strip()
    if not nombre or nombre in (".", "..") or any(caracter in nombre for caracter in ("/", "\\", "\0")):
        raise ValueError("Escribe solo el nombre del archivo, por ejemplo mensaje.txt, sin carpetas ni rutas.")
    if not Path(nombre).suffix:
        nombre += ".txt"
    ruta = CARPETA_PROYECTO / nombre
    try:
        padre_real = ruta.resolve().parent
    except RuntimeError as error:
        raise ValueError("El archivo contiene un enlace circular y no se puede abrir.") from error
    if padre_real != CARPETA_PROYECTO:
        raise ValueError("El archivo debe estar dentro de la carpeta del proyecto.")
    return ruta


def _leer_archivo(nombre: str) -> str:
    ruta = _ruta_archivo(nombre)
    if not stat.S_ISREG(ruta.stat().st_mode):
        raise ValueError("Elige un archivo de texto; no se admiten carpetas, tuberías ni dispositivos.")
    # newline="" conserva también los saltos CRLF de los archivos originales.
    try:
        with ruta.open("r", encoding="utf-8", newline="") as archivo:
            return archivo.read()
    except UnicodeDecodeError as error:
        raise ValueError("El archivo no está codificado en UTF-8. Guárdalo como texto UTF-8 e inténtalo de nuevo.") from error


def _guardar_resultado(texto: str, prefijo: str) -> Path:
    numero = 1
    while True:
        nombre = f"{prefijo}{numero}.txt"
        ruta = CARPETA_PROYECTO / nombre
        try:
            # La creación exclusiva evita sobrescribir incluso con dos programas abiertos.
            archivo = ruta.open("x", encoding="utf-8", newline="")
        except FileExistsError:
            numero += 1
            continue
        try:
            with archivo:
                archivo.write(texto)
        except BaseException:
            # Un error o una interrupción no deben dejar un resultado incompleto.
            try:
                ruta.unlink()
            except OSError:
                pass
            raise
        print(f"Resultado guardado en: {ruta}")
        return ruta


def _elegir(mensaje: str, opciones: tuple[str, ...]) -> str:
    while True:
        respuesta = input(mensaje).strip()
        if respuesta in opciones:
            return respuesta
        print(f"Elige una de estas opciones: {', '.join(opciones)}.")


def _mostrar_resultado(texto: str, desde_archivo: bool, cifrado: bool) -> None:
    tipo = "cifrado" if cifrado else "descifrado"
    if desde_archivo:
        lineas = texto.splitlines(keepends=True)
        truncada = len(lineas) > LINEAS_VISTA_PREVIA
        fragmentos = []
        for linea in lineas[:LINEAS_VISTA_PREVIA]:
            contenido = linea.rstrip("\r\n")
            if len(contenido) > CARACTERES_POR_LINEA_PREVIA:
                fragmentos.append(contenido[:CARACTERES_POR_LINEA_PREVIA] + "…\n")
                truncada = True
            else:
                fragmentos.append(linea)
        muestra = "".join(fragmentos)
        print(f"\n--- Texto {tipo}: vista previa (primeras {LINEAS_VISTA_PREVIA} líneas) ---")
    else:
        muestra = texto
        print(f"\n--- Texto {tipo} ---")
    if not texto:
        print("(Texto vacío)")
    else:
        print(muestra, end="" if muestra.endswith(("\n", "\r")) else "\n")
    print("--- Fin del resultado ---")
    if desde_archivo and truncada:
        print("Vista previa truncada; el resultado completo se guarda en el archivo.")


def _pedir_texto() -> tuple[str, bool]:
    """Devuelve el texto y si la entrada procede de un archivo."""
    print("\nEntrada: 1) Una línea  2) Varias líneas  3) Archivo UTF-8")
    print("El texto admite mayúsculas, minúsculas, números, símbolos, tildes, emojis y espacios.")
    print("Los espacios al inicio y al final también se conservan.")
    opcion = _elegir("Opción: ", ("1", "2", "3"))
    if opcion == "1":
        return input("Texto: "), False
    if opcion == "3":
        print(f"Carpeta del proyecto: {CARPETA_PROYECTO}")
        while True:
            try:
                return _leer_archivo(input("Nombre del archivo de entrada (ejemplo: mensaje.txt): ")), True
            except (ValueError, OSError) as error:
                print(f"No se pudo leer: {error}")
    print("Escribe o pega tu texto. Termina con una línea que contenga solo FIN.")
    lineas = []
    while True:
        linea = input()
        if linea == "FIN":
            return "\n".join(lineas), False
        lineas.append(linea)


def ejecutar(
    *,
    nombre: str,
    prefijo_cifrado: str,
    prefijo_descifrado: str,
    descripcion: str,
    ayuda_clave: str,
    cifrar: Callable,
    descifrar: Callable,
    validar_clave: Callable,
    admite_espanol: bool = False,
) -> None:
    parser = argparse.ArgumentParser(
        description=f"{nombre}: {descripcion}",
        epilog=(f"Cifrados: {prefijo_cifrado}1.txt, {prefijo_cifrado}2.txt, etc. "
                f"Descifrados: {prefijo_descifrado}1.txt, {prefijo_descifrado}2.txt, etc. "
                "Se guardan en el proyecto, con numeración independiente y sin sobrescribir."),
    )
    operaciones = parser.add_mutually_exclusive_group()
    operaciones.add_argument("--cifrar", action="store_true", help="Cifrar el texto.")
    operaciones.add_argument("--descifrar", action="store_true", help="Descifrar el texto.")
    parser.add_argument(
        "-k", "--clave",
        help=ayuda_clave + (" Con --ampliado: cualquier texto no vacío, incluidos símbolos y espacios." if admite_espanol else ""),
    )
    entradas = parser.add_mutually_exclusive_group()
    entradas.add_argument(
        "-t", "--texto",
        help="Texto entre comillas: admite mayúsculas, minúsculas, símbolos, espacios y texto vacío.",
    )
    entradas.add_argument("-a", "--archivo", help="Nombre de un archivo UTF-8 dentro del proyecto.")
    if admite_espanol:
        modos = parser.add_mutually_exclusive_group()
        modos.add_argument("--espanol", action="store_true", help="Usar 27 letras, incluyendo Ñ después de N.")
        modos.add_argument("--ampliado", action="store_true", help="Cifrar todo el texto UTF-8, incluidos símbolos y espacios; salida Base64.")
    args = parser.parse_args()
    opciones = {"espanol": args.espanol, "ampliado": args.ampliado} if admite_espanol else {}
    modo_argumentos = args.cifrar or args.descifrar

    if modo_argumentos:
        if args.clave is None or (args.texto is None and args.archivo is None):
            parser.error("Indica --clave y una entrada: --texto o --archivo.")
        try:
            texto = args.texto if args.texto is not None else _leer_archivo(args.archivo)
            funcion = cifrar if args.cifrar else descifrar
            resultado = funcion(texto, args.clave, **opciones)
            _mostrar_resultado(resultado, desde_archivo=args.archivo is not None, cifrado=args.cifrar)
            _guardar_resultado(resultado, prefijo_cifrado if args.cifrar else prefijo_descifrado)
        except (ValueError, OSError) as error:
            parser.exit(1, f"Error: {error}\n")
        except (KeyboardInterrupt, EOFError):
            parser.exit(1, "\nGuardado cancelado.\n")
        return

    if args.clave is not None or args.texto is not None or args.archivo is not None:
        parser.error("Para usar argumentos, indica --cifrar o --descifrar; sin argumentos se abre el menú.")

    try:
        print(f"\n=== {nombre} ===\n{descripcion}")
        print(f"Carpeta para leer y guardar archivos: {CARPETA_PROYECTO}")
        while True:
            print("\n1) Cifrar\n2) Descifrar\n0) Salir")
            operacion = _elegir("Opción: ", ("1", "2", "0"))
            if operacion == "0":
                return
            if admite_espanol:
                print("\nModo: 1) Clásico A-Z  2) Clásico español con Ñ  3) Ampliado: todos los caracteres")
                predeterminado = "2" if args.espanol else "3"
                eleccion = input(f"Opción [{predeterminado}]: ").strip() or predeterminado
                while eleccion not in ("1", "2", "3"):
                    eleccion = _elegir("Elige 1, 2 o 3: ", ("1", "2", "3"))
                opciones = {"espanol": eleccion == "2", "ampliado": eleccion == "3"}
            if opciones.get("ampliado"):
                print("Clave ampliada: cualquier texto no vacío; se distinguen mayúsculas, símbolos y espacios.")
                print("El cifrado se muestra en Base64. Para descifrarlo, usa este mismo modo y la clave exacta.")
            else:
                print(ayuda_clave)
            while True:
                clave = input("Clave: ")
                try:
                    validar_clave(clave, **opciones)
                    break
                except ValueError as error:
                    print(f"Clave inválida: {error}")
            try:
                texto, desde_archivo = _pedir_texto()
                funcion = cifrar if operacion == "1" else descifrar
                resultado = funcion(texto, clave, **opciones)
            except (ValueError, OSError) as error:
                print(f"Error: {error}")
                continue
            _mostrar_resultado(resultado, desde_archivo=desde_archivo, cifrado=operacion == "1")
            print("Para descifrar, conserva la misma clave y, en Vigenère, el mismo modo y alfabeto.")
            try:
                _guardar_resultado(resultado, prefijo_cifrado if operacion == "1" else prefijo_descifrado)
            except OSError as error:
                print(f"No se pudo guardar el resultado: {error}")
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")

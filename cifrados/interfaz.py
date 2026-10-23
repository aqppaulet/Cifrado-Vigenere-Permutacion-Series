"""Inicio de las ventanas gráficas y argumentos de consola opcionales."""

import argparse
from pathlib import Path
from typing import Callable

from .archivos import guardar_resultado, leer_archivo, ruta_archivo
from .validacion import REGLAS_TEXTO


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARACTERES_VISTA_PREVIA = 200


def _ruta_archivo(nombre: str) -> Path:
    return ruta_archivo(nombre, CARPETA_PROYECTO)


def _leer_archivo(nombre: str) -> str:
    return leer_archivo(nombre, CARPETA_PROYECTO)


def _guardar_resultado(texto: str, prefijo: str) -> Path:
    return guardar_resultado(texto, prefijo, CARPETA_PROYECTO)


def _mostrar_resultado(texto: str, desde_archivo: bool, cifrado: bool) -> None:
    tipo = "cifrado" if cifrado else "descifrado"
    truncada = desde_archivo and len(texto) > CARACTERES_VISTA_PREVIA
    muestra = texto[:CARACTERES_VISTA_PREVIA] if truncada else texto
    detalle = " (vista previa de hasta 200 letras)" if desde_archivo else ""
    print(f"\n--- Texto {tipo}{detalle} ---")
    print(muestra)
    print("--- Fin del resultado ---")
    if truncada:
        print("Vista previa truncada; el resultado completo se guarda en el archivo.")


def ejecutar(
    *,
    nombre: str,
    prefijo_cifrado: str,
    prefijo_descifrado: str,
    descripcion: str,
    ayuda_clave: str,
    ejemplo: str,
    cifrar: Callable,
    descifrar: Callable,
    validar_clave: Callable,
) -> None:
    """Abre la ventana sin argumentos; con argumentos procesa una entrada."""
    parser = argparse.ArgumentParser(
        description=f"{nombre}: {descripcion} {REGLAS_TEXTO}",
        epilog=(f"{ejemplo} Cifrados: {prefijo_cifrado}1.txt, {prefijo_cifrado}2.txt, etc. "
                f"Descifrados: {prefijo_descifrado}1.txt, {prefijo_descifrado}2.txt, etc. "
                "Se guardan en el proyecto, sin sobrescribir. Para descifrar, usa la misma clave."),
    )
    operaciones = parser.add_mutually_exclusive_group()
    operaciones.add_argument("--cifrar", action="store_true", help="Cifrar el texto claro.")
    operaciones.add_argument("--descifrar", action="store_true", help="Recuperar el texto claro en mayúsculas.")
    parser.add_argument("-k", "--clave", help=ayuda_clave)
    entradas = parser.add_mutually_exclusive_group()
    entradas.add_argument("-t", "--texto", help="Normaliza letras, ñ y acentos; solo al cifrar elimina espacios. Sin signos.")
    entradas.add_argument(
        "-a", "--archivo",
        help="Archivo UTF-8 del proyecto: sin BOM ni salto final; al cifrar elimina espacios.",
    )
    args = parser.parse_args()

    if args.cifrar or args.descifrar:
        if args.clave is None or (args.texto is None and args.archivo is None):
            parser.error("Indica --clave y una entrada: --texto o --archivo.")
        try:
            validar_clave(args.clave)
            texto = args.texto if args.texto is not None else _leer_archivo(args.archivo)
            funcion = cifrar if args.cifrar else descifrar
            resultado = funcion(texto, args.clave)
            _mostrar_resultado(resultado, desde_archivo=args.archivo is not None, cifrado=args.cifrar)
            _guardar_resultado(resultado, prefijo_cifrado if args.cifrar else prefijo_descifrado)
        except (ValueError, OSError) as error:
            parser.exit(1, f"Error: {error}\n")
        except (KeyboardInterrupt, EOFError):
            parser.exit(1, "\nOperación cancelada.\n")
        return

    if args.clave is not None or args.texto is not None or args.archivo is not None:
        parser.error("Para usar argumentos, indica --cifrar o --descifrar; sin argumentos se abre la ventana gráfica.")

    # Importación diferida: la ayuda, los algoritmos y la CLI funcionan sin Tk.
    from .ventana import abrir_ventana
    abrir_ventana(
        nombre=nombre, descripcion=descripcion, ayuda_clave=ayuda_clave,
        ejemplo=ejemplo, prefijo_cifrado=prefijo_cifrado,
        prefijo_descifrado=prefijo_descifrado, cifrar=cifrar, descifrar=descifrar,
        validar_clave=validar_clave,
    )

"""Operaciones de lectura y escritura de archivos del proyecto."""

import stat
from pathlib import Path


def ruta_archivo(nombre: str, carpeta: Path) -> Path:
    """Resuelve un nombre simple y garantiza que permanezca en ``carpeta``."""
    nombre = nombre.strip()
    if not nombre or nombre in (".", "..") or any(
        caracter in nombre for caracter in ("/", "\\", "\0")
    ):
        raise ValueError("Escribe solo el nombre del archivo, por ejemplo mensaje.txt, sin carpetas ni rutas.")
    if not Path(nombre).suffix:
        nombre += ".txt"
    ruta = carpeta / nombre
    try:
        padre_real = ruta.resolve().parent
    except RuntimeError as error:
        raise ValueError("El archivo contiene un enlace circular y no se puede abrir.") from error
    if padre_real != carpeta:
        raise ValueError("El archivo debe estar dentro de la carpeta del proyecto.")
    return ruta


def leer_archivo(nombre: str, carpeta: Path) -> str:
    """Lee un archivo regular como texto UTF-8 sin normalizar saltos de línea."""
    ruta = ruta_archivo(nombre, carpeta)
    if not stat.S_ISREG(ruta.stat().st_mode):
        raise ValueError("Elige un archivo de texto; no se admiten carpetas, tuberías ni dispositivos.")
    try:
        with ruta.open("r", encoding="utf-8", newline="") as archivo:
            return archivo.read()
    except UnicodeDecodeError as error:
        raise ValueError("El archivo no está codificado en UTF-8. Guárdalo como texto UTF-8 e inténtalo de nuevo.") from error


def guardar_resultado(texto: str, prefijo: str, carpeta: Path) -> Path:
    """Guarda el resultado en el primer nombre libre sin sobrescribir archivos."""
    numero = 1
    while True:
        ruta = carpeta / f"{prefijo}{numero}.txt"
        try:
            archivo = ruta.open("x", encoding="utf-8", newline="")
        except FileExistsError:
            numero += 1
            continue
        try:
            with archivo:
                archivo.write(texto)
        except BaseException:
            try:
                ruta.unlink()
            except OSError:
                pass
            raise
        print(f"Resultado guardado en: {ruta}")
        return ruta
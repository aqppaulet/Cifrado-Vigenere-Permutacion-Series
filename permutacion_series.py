"""Transposición por bloques con una permutación de posiciones como clave."""

import re

from interfaz import ejecutar


def validar_clave(clave: str) -> list[int]:
    """Acepta posiciones separadas por espacios o comas, numeradas desde 1."""
    clave = clave.strip()
    if not re.fullmatch(r"[0-9]+(?:[\s,]+[0-9]+)*", clave):
        raise ValueError("Usa posiciones separadas por espacios o comas, por ejemplo: 3 1 4 2.")
    posiciones = [int(numero) for numero in re.split(r"[\s,]+", clave)]
    if len(posiciones) < 2 or sorted(posiciones) != list(range(1, len(posiciones) + 1)):
        raise ValueError("La clave debe incluir una vez cada número del 1 al tamaño del bloque (mínimo 2).")
    return posiciones


def _transformar(texto: str, clave: str, inversa: bool) -> str:
    posiciones = validar_clave(clave)
    tamano = len(posiciones)
    resultado = []
    for inicio in range(0, len(texto), tamano):
        bloque = texto[inicio:inicio + tamano]
        # En el bloque final se omiten las posiciones inexistentes: no hay relleno.
        orden = [posicion - 1 for posicion in posiciones if posicion <= len(bloque)]
        if inversa:
            original = [""] * len(bloque)
            for caracter, posicion in zip(bloque, orden):
                original[posicion] = caracter
            resultado.extend(original)
        else:
            resultado.extend(bloque[posicion] for posicion in orden)
    return "".join(resultado)


def cifrar(texto: str, clave: str) -> str:
    """Reordena todos los caracteres, incluidos espacios y saltos de línea."""
    return _transformar(texto, clave, inversa=False)


def descifrar(texto: str, clave: str) -> str:
    """Reconstruye el orden original sin eliminar ningún carácter."""
    return _transformar(texto, clave, inversa=True)


if __name__ == "__main__":
    ejecutar(
        nombre="Permutación de series",
        prefijo_cifrado="cP",
        prefijo_descifrado="dP",
        descripcion="Reordena posiciones en bloques según una clave .",
        ayuda_clave="Posiciones del 1 al N, sin repetir, por ejemplo:con ESPACIOS como 3 1 4 2, tambien 3,1,4,2 ",
        cifrar=cifrar,
        descifrar=descifrar,
        validar_clave=validar_clave,
    )

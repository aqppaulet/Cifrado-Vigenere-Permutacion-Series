"""Transposición por bloques mediante una permutación de posiciones."""

import re


def validar_clave(clave: str) -> list[int]:
    """Valida posiciones separadas por espacios o comas, numeradas desde 1."""
    clave = clave.strip()
    formato_correcto = re.fullmatch(r"[0-9]+(?:[\s,]+[0-9]+)*", clave)
    if formato_correcto is None:
        raise ValueError("Usa posiciones separadas por espacios o comas, por ejemplo: 3 1 4 2.")

    numeros = re.split(r"[\s,]+", clave)
    posiciones = []
    for numero in numeros:
        posiciones.append(int(numero))

    posiciones_ordenadas = sorted(posiciones)
    posiciones_esperadas = list(range(1, len(posiciones) + 1))
    tiene_tamano_valido = len(posiciones) >= 2
    es_una_permutacion = posiciones_ordenadas == posiciones_esperadas

    if not tiene_tamano_valido or not es_una_permutacion:
        raise ValueError(
            "La clave debe incluir una vez cada número del 1 al tamaño del bloque (mínimo 2)."
        )

    return posiciones


def _transformar(texto: str, clave: str, inversa: bool) -> str:
    """Procesa el texto en bloques y aplica la permutación solicitada."""
    posiciones = validar_clave(clave)
    tamano_bloque = len(posiciones)
    resultado = []

    for inicio in range(0, len(texto), tamano_bloque):
        fin = inicio + tamano_bloque
        bloque = texto[inicio:fin]
        orden_bloque = []

        for posicion in posiciones:
            indice = posicion - 1
            if indice < len(bloque):
                orden_bloque.append(indice)

        if inversa:
            original = [""] * len(bloque)
            indice = 0

            for posicion in orden_bloque:
                original[posicion] = bloque[indice]
                indice += 1

            for caracter in original:
                resultado.append(caracter)
        else:
            for posicion in orden_bloque:
                resultado.append(bloque[posicion])

    return "".join(resultado)


def cifrar(texto: str, clave: str) -> str:
    """Reordena todos los caracteres en bloques."""
    return _transformar(texto, clave, inversa=False)


def descifrar(texto: str, clave: str) -> str:
    """Reconstruye el orden original de los caracteres."""
    return _transformar(texto, clave, inversa=True)
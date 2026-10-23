"""Transposición por bloques mediante una permutación de posiciones."""

import re

from .validacion import normalizar_letras


def preparar_texto(texto: str, descifrar: bool = False) -> str:
    """Solo al cifrar, elimina los dígitos 0-9 antes de preparar las letras."""
    if not descifrar and isinstance(texto, str):
        texto = re.sub(r"[0-9]", "", texto)
    return normalizar_letras(texto, eliminar_espacios=not descifrar)


def validar_clave(clave: str) -> list[int]:
    """Valida posiciones separadas por espacios o comas, numeradas desde 1."""
    if not isinstance(clave, str):
        raise ValueError("La clave debe escribirse con posiciones, por ejemplo: 3 1 4 2.")
    clave = clave.strip(" ")
    # Primero comprobamos que solo se hayan usado números y separadores válidos.
    formato_correcto = re.fullmatch(r"[0-9]+(?:(?: +| *, *)[0-9]+)*", clave)
    if formato_correcto is None:
        raise ValueError("Usa posiciones separadas por espacios o comas, por ejemplo: 3 1 4 2.")

    numeros = re.split(r"[ ,]+", clave)
    posiciones = []
    for numero in numeros:
        # La clave usa posiciones desde 1, como se suele explicar en papel.
        try:
            posiciones.append(int(numero))
        except ValueError as error:
            raise ValueError("Una posición de la clave es demasiado larga.") from error

    # Para ser una permutación válida deben aparecer exactamente 1, 2, ..., N.
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
    texto = preparar_texto(texto, descifrar=inversa)
    tamano_bloque = len(posiciones)
    resultado = []

    for inicio in range(0, len(texto), tamano_bloque):
        # Cada bloque tiene el tamaño de la clave, excepto el último.
        fin = inicio + tamano_bloque
        bloque = texto[inicio:fin]
        orden_bloque = []

        for posicion in posiciones:
            # Python usa índices desde 0; la clave usa posiciones desde 1.
            indice = posicion - 1
            if indice < len(bloque):
                orden_bloque.append(indice)

        if inversa:
            # En el descifrado, cada carácter cifrado vuelve a su posición
            # original dentro del bloque.
            original = [""] * len(bloque)
            indice = 0

            for posicion in orden_bloque:
                original[posicion] = bloque[indice]
                indice += 1

            for caracter in original:
                resultado.append(caracter)
        else:
            # En el cifrado, leemos el bloque siguiendo el orden de la clave.
            for posicion in orden_bloque:
                resultado.append(bloque[posicion])

    return "".join(resultado)


def cifrar(texto: str, clave: str) -> str:
    """Reordena letras A-Z por bloques, sin añadir relleno."""
    return _transformar(texto, clave, inversa=False)


def descifrar(texto: str, clave: str) -> str:
    """Reconstruye el orden de las letras y devuelve el texto en mayúsculas."""
    return _transformar(texto, clave, inversa=True)

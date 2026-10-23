"""Vigenère clásico sobre las 26 letras inglesas; A=0, ..., Z=25."""

from .validacion import ALFABETO, normalizar_letras


def validar_clave(clave: str) -> str:
    """Preprocesa la clave de letras y devuelve únicamente A-Z."""
    return normalizar_letras(clave, "La clave de Vigenère")


def _transformar(texto: str, clave: str, direccion: int) -> str:
    """Suma la clave al cifrar (1) y la resta al descifrar (-1)."""
    clave = validar_clave(clave)
    texto = normalizar_letras(texto)
    desplazamientos = [ord(letra) - ord("A") for letra in clave]
    resultado = []

    for indice, letra in enumerate(texto):
        # Cada letra consume una posición de la clave; esta se repite completa.
        desplazamiento = desplazamientos[indice % len(clave)]
        posicion = ord(letra) - ord("A")
        # El módulo 26 hace que el desplazamiento vuelva a A después de Z.
        resultado.append(ALFABETO[(posicion + direccion * desplazamiento) % 26])

    return "".join(resultado)


def cifrar(texto: str, clave: str) -> str:
    """Cifra un mensaje de letras inglesas y devuelve únicamente A-Z."""
    return _transformar(texto, clave, 1)


def descifrar(texto: str, clave: str) -> str:
    """Recupera el texto en mayúsculas con la misma clave del cifrado."""
    return _transformar(texto, clave, -1)

"""Vigenère clásico o ampliado a bytes UTF-8, con salida Base64 en modo ampliado."""

import base64
import binascii

from interfaz import ejecutar


ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFABETO_ESPANOL = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"


def validar_clave(clave: str, espanol: bool = False, ampliado: bool = False) -> str:
    """En modo ampliado conserva todos los caracteres de la clave, incluidos espacios."""
    if ampliado:
        if espanol:
            raise ValueError("Elige un solo modo: ampliado o español clásico.")
        if not clave:
            raise ValueError("La clave no puede estar vacía; puede contener letras, números, símbolos y espacios.")
        return clave
    alfabeto = ALFABETO_ESPANOL if espanol else ALFABETO
    clave = clave.strip()
    permitidas = alfabeto + alfabeto.lower()
    if not clave or any(letra not in permitidas for letra in clave):
        detalle = "A-Z y Ñ" if espanol else "A-Z"
        raise ValueError(f"La clave debe contener únicamente letras {detalle}, sin espacios ni tildes.")
    return clave.upper()


def _transformar(texto: str, clave: str, direccion: int, espanol: bool) -> str:
    alfabeto = ALFABETO_ESPANOL if espanol else ALFABETO
    clave = validar_clave(clave, espanol)
    posiciones = {letra: indice for indice, letra in enumerate(alfabeto)}
    permitidas = alfabeto + alfabeto.lower()
    desplazamientos = [posiciones[letra] for letra in clave]
    resultado = []
    indice_clave = 0
    for caracter in texto:
        mayuscula = caracter.upper()
        if caracter not in permitidas:
            resultado.append(caracter)
            continue
        desplazamiento = desplazamientos[indice_clave % len(clave)]
        indice = (posiciones[mayuscula] + direccion * desplazamiento) % len(alfabeto)
        nueva_letra = alfabeto[indice]
        resultado.append(nueva_letra.lower() if caracter.islower() else nueva_letra)
        indice_clave += 1
    return "".join(resultado)


def _transformar_bytes(datos: bytes, clave: bytes, direccion: int) -> bytes:
    """Vigenère sobre un alfabeto de 256 valores: suma/resta modular de bytes."""
    return bytes((valor + direccion * clave[indice % len(clave)]) % 256 for indice, valor in enumerate(datos))


def cifrar(texto: str, clave: str, espanol: bool = False, ampliado: bool = False) -> str:
    """Cifra letras en modo clásico o todos los bytes UTF-8 en modo ampliado."""
    if ampliado:
        clave = validar_clave(clave, espanol, ampliado)
        cifrado = _transformar_bytes(texto.encode("utf-8"), clave.encode("utf-8"), 1)
        representacion = base64.b64encode(cifrado).decode("ascii")
        return "\n".join(representacion[inicio:inicio + 80] for inicio in range(0, len(representacion), 80))
    return _transformar(texto, clave, 1, espanol)


def descifrar(texto: str, clave: str, espanol: bool = False, ampliado: bool = False) -> str:
    """Descifra con el mismo modo y clave; el ampliado espera el cifrado en Base64."""
    if ampliado:
        clave = validar_clave(clave, espanol, ampliado)
        try:
            compacto = "".join(texto.split())
            datos = base64.b64decode(compacto, validate=True)
            if base64.b64encode(datos).decode("ascii") != compacto:
                raise ValueError("Representación Base64 no canónica")
        except (ValueError, binascii.Error) as error:
            raise ValueError("El cifrado ampliado debe ser Base64 válido. Copia el resultado completo o lee su archivo.") from error
        original = _transformar_bytes(datos, clave.encode("utf-8"), -1)
        try:
            return original.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("No se pudo recuperar texto UTF-8. Revisa la clave, el modo y que el cifrado esté completo.") from error
    return _transformar(texto, clave, -1, espanol)


if __name__ == "__main__":
    ejecutar(
        nombre="Vigenère",
        prefijo_cifrado="cV",
        prefijo_descifrado="dV",
        descripcion="Cifra letras en modo clásico o todos los caracteres en modo ampliado (UTF-8 y Base64).",
        ayuda_clave="Una palabra sin espacios ni tildes, por ejemplo LIMON.",
        cifrar=cifrar,
        descifrar=descifrar,
        validar_clave=validar_clave,
        admite_espanol=True,
    )

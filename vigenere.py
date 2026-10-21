"""Programa de consola para Vigenère."""

from cifrados.vigenere import (
    ALFABETO,
    ALFABETO_ESPANOL,
    cifrar,
    descifrar,
    validar_clave,
)
from cifrados.interfaz import ejecutar


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

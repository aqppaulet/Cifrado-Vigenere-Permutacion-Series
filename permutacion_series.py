"""Programa de consola para la permutación por bloques."""

from cifrados.interfaz import ejecutar
from cifrados.permutacion import cifrar, descifrar, validar_clave


if __name__ == "__main__":
    ejecutar(
        nombre="Permutación de series",
        prefijo_cifrado="cP",
        prefijo_descifrado="dP",
        descripcion="Reordena posiciones en bloques según una clave.",
        ayuda_clave="Posiciones del 1 al N, sin repetir, por ejemplo: 3 1 4 2 o 3,1,4,2.",
        cifrar=cifrar,
        descifrar=descifrar,
        validar_clave=validar_clave,
    )

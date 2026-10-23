"""Interfaz de permutación con instrucciones para su clave de posiciones."""

from .interfaz import ejecutar
from .permutacion import cifrar, descifrar, preparar_texto, validar_clave


def main() -> None:
    ejecutar(
        nombre="Permutación de series",
        prefijo_cifrado="cP",
        prefijo_descifrado="dP",
        descripcion=(
            "Reordena letras en bloques del tamaño de la clave. "
            "En el último bloque omite posiciones inexistentes, sin relleno."
        ),
        ayuda_clave=(
            "Clave de permutación: posiciones del 1 al N sin repetir, mínimo 2. "
            "Ejemplos: 3 1 4 2 o 3,1,4,2. La clave numérica se conserva completa."
        ),
        ejemplo="Ejemplo: ABCDEFGHIJ + clave 3 1 4 2 -> CADBGEHFIJ.",
        cifrar=cifrar,
        descifrar=descifrar,
        validar_clave=validar_clave,
        preparar_texto=preparar_texto,
        reglas_texto=(
            "Al cifrar: elimina espacios y dígitos 0-9; normaliza ñ, acentos y "
            "mayúsculas a A-Z. Al descifrar: solo letras. Sin signos ni saltos de línea."
        ),
    )


if __name__ == "__main__":
    main()

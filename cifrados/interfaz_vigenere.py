"""Interfaz de Vigenère con instrucciones para su clave de letras."""

from .interfaz import ejecutar
from .vigenere import cifrar, descifrar, validar_clave


def main() -> None:
    ejecutar(
        nombre="Vigenère",
        prefijo_cifrado="cV",
        prefijo_descifrado="dV",
        descripcion="Desplaza cada letra con una clave repetida: A=0, B=1, ..., Z=25.",
        ayuda_clave=(
            "Clave de Vigenère: letras; ñ y tildes se preprocesan igual que el mensaje. "
            "Sin espacios, números ni símbolos. Ejemplo: LIMÓN -> LIMON."
        ),
        ejemplo="Ejemplo: ATTACKATDAWN + clave LEMON -> LXFOPVEFRNHR.",
        cifrar=cifrar,
        descifrar=descifrar,
        validar_clave=validar_clave,
    )


if __name__ == "__main__":
    main()

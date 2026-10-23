"""Punto de entrada de consola y funciones públicas de Vigenère A-Z."""

from cifrados.interfaz_vigenere import main
from cifrados.vigenere import ALFABETO, cifrar, descifrar, validar_clave


if __name__ == "__main__":
    main()

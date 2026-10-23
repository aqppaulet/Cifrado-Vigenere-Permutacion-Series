"""Preprocesamiento común: letras españolas de entrada a letras inglesas A-Z."""

import unicodedata

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
REGLAS_TEXTO = (
    "Preprocesamiento: minúsculas a mayúsculas, ñ/Ñ a N y áéíóúü a AEIOUU. "
    "El algoritmo recibe solo A-Z. Sin espacios, saltos de línea, números ni símbolos."
)
EQUIVALENCIAS = str.maketrans(
    "áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN"
)


def normalizar_letras(valor: str, campo: str = "El texto") -> str:
    """Quita tildes españolas y normaliza Ñ y mayúsculas antes del algoritmo.

    NFC admite tanto «é» como «e + acento combinado». La tabla explícita evita
    convertir otros caracteres Unicode, como ß a SS, fuera del contrato.
    El descifrado recupera el texto preprocesado, sin restaurar tildes ni Ñ.
    """
    if not isinstance(valor, str):
        raise ValueError(f"{campo} debe ser una cadena de letras A-Z.")
    if not valor:
        raise ValueError(f"{campo} no puede estar vacío; escribe al menos una letra A-Z.")
    resultado = []
    for posicion, caracter in enumerate(unicodedata.normalize("NFC", valor), start=1):
        equivalente = caracter.translate(EQUIVALENCIAS)
        if equivalente not in ALFABETO and equivalente not in "abcdefghijklmnopqrstuvwxyz":
            raise ValueError(
                f"{campo} contiene {caracter!r} en la posición {posicion}. "
                "Usa letras A-Z/a-z, Ñ/ñ o áéíóúü (también en mayúsculas); "
                "sin espacios, saltos de línea, números ni símbolos."
            )
        resultado.append(equivalente.upper())
    return "".join(resultado)

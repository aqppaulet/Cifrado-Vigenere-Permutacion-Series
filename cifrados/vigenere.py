"""Implementación de Vigenère clásico, español y ampliado."""

import base64
import binascii


ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFABETO_ESPANOL = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"


def validar_clave(clave: str, espanol: bool = False, ampliado: bool = False) -> str:
    """Valida y normaliza una clave según el modo seleccionado."""
    if ampliado:
        if espanol:
            raise ValueError("Elige un solo modo: ampliado o español clásico.")
        if not clave:
            raise ValueError("La clave no puede estar vacía; puede contener letras, números, símbolos y espacios.")
        return clave

    if espanol:
        alfabeto = ALFABETO_ESPANOL
    else:
        alfabeto = ALFABETO

    clave = clave.strip()
    permitidas = alfabeto + alfabeto.lower()

    clave_invalida = not clave
    for letra in clave:
        if letra not in permitidas:
            clave_invalida = True
            break

    if clave_invalida:
        detalle = "A-Z y Ñ" if espanol else "A-Z"
        raise ValueError(f"La clave debe contener únicamente letras {detalle}, sin espacios ni tildes.")

    return clave.upper()


def _obtener_alfabeto(espanol: bool) -> str:
    """Devuelve el alfabeto que usará el modo clásico."""
    if espanol:
        return ALFABETO_ESPANOL
    return ALFABETO


def _crear_posiciones(alfabeto: str) -> dict[str, int]:
    """Crea una tabla que relaciona cada letra con su posición."""
    posiciones = {}
    indice = 0

    for letra in alfabeto:
        posiciones[letra] = indice
        indice += 1

    return posiciones


def _transformar(texto: str, clave: str, direccion: int, espanol: bool) -> str:
    """Aplica el desplazamiento de Vigenère a las letras del texto.

    ``direccion`` vale 1 para cifrar y -1 para descifrar.
    Los caracteres que no pertenecen al alfabeto se conservan.
    """
    alfabeto = _obtener_alfabeto(espanol)
    clave = validar_clave(clave, espanol)
    posiciones = _crear_posiciones(alfabeto)
    permitidas = alfabeto + alfabeto.lower()
    desplazamientos = []

    for letra in clave:
        desplazamientos.append(posiciones[letra])

    resultado = []
    indice_clave = 0

    for caracter in texto:
        if caracter not in permitidas:
            resultado.append(caracter)
            continue

        letra_mayuscula = caracter.upper()
        posicion_original = posiciones[letra_mayuscula]
        posicion_clave = indice_clave % len(clave)
        desplazamiento = desplazamientos[posicion_clave]

        posicion_nueva = posicion_original + direccion * desplazamiento
        posicion_nueva = posicion_nueva % len(alfabeto)

        nueva_letra = alfabeto[posicion_nueva]
        if caracter.islower():
            nueva_letra = nueva_letra.lower()

        resultado.append(nueva_letra)
        indice_clave += 1

    return "".join(resultado)


def _transformar_bytes(datos: bytes, clave: bytes, direccion: int) -> bytes:
    """Aplica suma o resta modular a cada byte del texto."""
    resultado = []

    for indice, valor in enumerate(datos):
        posicion_clave = indice % len(clave)
        desplazamiento = clave[posicion_clave]
        nuevo_valor = valor + direccion * desplazamiento
        nuevo_valor = nuevo_valor % 256
        resultado.append(nuevo_valor)

    return bytes(resultado)


def _dividir_base64_en_lineas(texto: str) -> str:
    """Divide Base64 en líneas de 80 caracteres para mostrarlo y guardarlo."""
    lineas = []
    inicio = 0

    while inicio < len(texto):
        fin = inicio + 80
        lineas.append(texto[inicio:fin])
        inicio = fin

    return "\n".join(lineas)


def cifrar(texto: str, clave: str, espanol: bool = False, ampliado: bool = False) -> str:
    """Cifra texto en modo clásico o todos sus bytes UTF-8 en modo ampliado."""
    if not ampliado:
        return _transformar(texto, clave, 1, espanol)

    clave_validada = validar_clave(clave, espanol, ampliado)
    texto_bytes = texto.encode("utf-8")
    clave_bytes = clave_validada.encode("utf-8")
    bytes_cifrados = _transformar_bytes(texto_bytes, clave_bytes, 1)
    texto_base64 = base64.b64encode(bytes_cifrados).decode("ascii")

    return _dividir_base64_en_lineas(texto_base64)


def _decodificar_base64(texto: str) -> bytes:
    """Valida que el Base64 sea válido y tenga la forma que genera el programa."""
    texto_sin_espacios = "".join(texto.split())

    try:
        datos = base64.b64decode(texto_sin_espacios, validate=True)
        base64_generado = base64.b64encode(datos).decode("ascii")
    except (ValueError, binascii.Error) as error:
        raise ValueError(
            "El cifrado ampliado debe ser Base64 válido. "
            "Copia el resultado completo o lee su archivo."
        ) from error

    if base64_generado != texto_sin_espacios:
        raise ValueError(
            "El cifrado ampliado debe ser Base64 válido. "
            "Copia el resultado completo o lee su archivo."
        )

    return datos


def descifrar(texto: str, clave: str, espanol: bool = False, ampliado: bool = False) -> str:
    """Descifra texto usando el mismo modo y la misma clave."""
    if not ampliado:
        return _transformar(texto, clave, -1, espanol)

    clave_validada = validar_clave(clave, espanol, ampliado)
    datos_cifrados = _decodificar_base64(texto)
    clave_bytes = clave_validada.encode("utf-8")
    datos_originales = _transformar_bytes(datos_cifrados, clave_bytes, -1)

    try:
        return datos_originales.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(
            "No se pudo recuperar texto UTF-8. "
            "Revisa la clave, el modo y que el cifrado esté completo."
        ) from error
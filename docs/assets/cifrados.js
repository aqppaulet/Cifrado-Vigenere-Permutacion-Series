/* Algoritmos educativos independientes de la interfaz y sin dependencias. */
"use strict";

(function (global) {
  const ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const equivalencias = Object.fromEntries(
    Array.from("áéíóúüñÁÉÍÓÚÜÑ", (letra, i) => [letra, "aeiouunAEIOUUN"[i]])
  );

  function normalizar(texto, campo = "El texto", eliminarEspacios = false) {
    // Solo se quita el espacio común del texto claro; no tabulaciones o saltos.
    if (eliminarEspacios && typeof texto === "string") texto = texto.replace(/ /g, "");
    if (typeof texto !== "string" || !texto.length) {
      throw new Error(`${campo} debe contener al menos una letra.`);
    }
    let resultado = "";
    // NFC también acepta e + acento combinado. La tabla limita las conversiones
    // al acuerdo español de entrada; por ejemplo, ß no se transforma en SS.
    let posicion = 0;
    for (const caracter of texto.normalize("NFC")) {
      posicion += 1;
      const letra = equivalencias[caracter] || caracter;
      if (!/^[A-Za-z]$/.test(letra)) {
        throw new Error(
          `${campo}: carácter ${JSON.stringify(caracter)} en la posición ${posicion}. ` +
          "Usa letras, ñ o áéíóúü. No se admiten " +
          (eliminarEspacios ? "" : "espacios, ") + "saltos de línea, números ni símbolos."
        );
      }
      resultado += letra.toUpperCase();
    }
    return resultado;
  }

  function validarPermutacion(clave) {
    if (typeof clave !== "string") throw new Error("Escribe las posiciones de la clave.");
    const limpia = clave.replace(/^ +| +$/g, "");
    if (!/^[0-9]+(?:(?: +| *, *)[0-9]+)*$/.test(limpia)) {
      throw new Error("Separa las posiciones con espacios o comas. Ejemplo: 3 1 4 2.");
    }
    const posiciones = limpia.split(/[ ,]+/).map(Number);
    const n = posiciones.length;
    if (n < 2 || new Set(posiciones).size !== n || posiciones.some(p => !Number.isSafeInteger(p) || p < 1 || p > n)) {
      throw new Error("La clave debe incluir una vez cada número del 1 al N, con mínimo dos posiciones.");
    }
    return posiciones;
  }

  function vigenere(texto, clave, descifrar = false) {
    const preparada = normalizar(clave, "La clave");
    const mensaje = normalizar(texto, "El texto", !descifrar);
    const direccion = descifrar ? -1 : 1;
    let salida = "";
    for (let i = 0; i < mensaje.length; i += 1) {
      const posicion = mensaje.charCodeAt(i) - 65;
      const desplazamiento = preparada.charCodeAt(i % preparada.length) - 65;
      salida += ALFABETO[(posicion + direccion * desplazamiento + 26) % 26];
    }
    return salida;
  }

  function prepararPermutacion(texto, descifrar = false) {
    // Esta eliminación corresponde solo al texto claro de permutación, nunca a su clave.
    if (!descifrar && typeof texto === "string") texto = texto.replace(/[0-9]/g, "");
    return normalizar(texto, "El texto", !descifrar);
  }

  function permutacion(texto, clave, descifrar = false) {
    const posiciones = validarPermutacion(clave);
    const mensaje = prepararPermutacion(texto, descifrar);
    const salida = [];
    for (let inicio = 0; inicio < mensaje.length; inicio += posiciones.length) {
      const bloque = mensaje.slice(inicio, inicio + posiciones.length);
      // En el último bloque se omiten posiciones inexistentes; no hay relleno.
      const orden = posiciones.filter(p => p <= bloque.length);
      if (descifrar) {
        const original = Array(bloque.length);
        orden.forEach((p, i) => { original[p - 1] = bloque[i]; });
        salida.push(original.join(""));
      } else {
        salida.push(orden.map(p => bloque[p - 1]).join(""));
      }
    }
    return salida.join("");
  }

  global.Cifrados = Object.freeze({ ALFABETO, normalizar, validarPermutacion, prepararPermutacion, vigenere, permutacion });
})(globalThis);

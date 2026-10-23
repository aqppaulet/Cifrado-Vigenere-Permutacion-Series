/* La entrada, los archivos y las claves se procesan solo en este navegador. */
"use strict";

(function () {
  const $ = id => document.getElementById(id);
  const algoritmo = document.body.dataset.algoritmo;
  if (!algoritmo) return;
  const esVigenere = algoritmo === "vigenere";
  const form = $("formulario");
  const clave = $("clave");
  const texto = $("texto");
  const archivo = $("archivo");
  const salida = $("resultado");
  const previo = $("preprocesado");
  const estado = $("estado");
  const procesar = $("procesar");
  const contadores = { cifrar: 0, descifrar: 0 };
  let resultado = "";
  let revision = 0;
  let revisionResultado = -1;
  let operacionResultado = "";

  const operacion = () => form.elements.operacion.value;
  const fuente = () => form.elements.fuente.value;

  function avisar(mensaje, error = false) {
    estado.textContent = mensaje;
    estado.dataset.tipo = error ? "error" : "info";
  }

  function invalidar() {
    revision += 1;
    resultado = "";
    salida.value = "";
    previo.textContent = "El texto que recibirá el algoritmo aparecerá aquí.";
    $("cantidad").textContent = "0 letras";
    $("copiar").disabled = true;
    $("descargar").disabled = true;
    procesar.textContent = operacion() === "cifrar" ? "Cifrar mensaje" : "Descifrar mensaje";
    $("titulo-resultado").textContent = operacion() === "cifrar" ? "Texto cifrado" : "Texto descifrado";
    const esArchivo = fuente() === "archivo";
    $("entrada-linea").hidden = esArchivo;
    $("entrada-archivo").hidden = !esArchivo;
    texto.disabled = esArchivo;
    archivo.disabled = !esArchivo;
    avisar("Introduce tu clave y el mensaje para comenzar.");
    if (!esArchivo && texto.value) {
      try { previo.textContent = Cifrados.normalizar(texto.value); }
      catch (error) { previo.textContent = error.message; }
    }
  }

  async function leerEntrada() {
    if (fuente() === "linea") return texto.value;
    const seleccionado = archivo.files[0];
    if (!seleccionado) throw new Error("Selecciona un archivo de texto UTF-8.");
    const datos = await seleccionado.arrayBuffer();
    try {
      // ignoreBOM conserva el BOM como carácter: se rechaza, igual que en Python.
      return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(datos);
    } catch (_) {
      throw new Error("El archivo no es texto UTF-8 válido. Vuelve a guardarlo con esa codificación.");
    }
  }

  form.addEventListener("input", invalidar);
  form.addEventListener("change", invalidar);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    invalidar();
    const actual = revision;
    const op = operacion();
    const llave = clave.value;
    procesar.disabled = true;
    procesar.textContent = "Procesando…";
    try {
      // Validar antes de leer un archivo evita trabajo innecesario con claves inválidas.
      if (esVigenere) Cifrados.normalizar(llave, "La clave");
      else Cifrados.validarPermutacion(llave);
      const entrada = await leerEntrada();
      if (actual !== revision) return;
      const preparado = Cifrados.normalizar(entrada);
      const transformar = esVigenere ? Cifrados.vigenere : Cifrados.permutacion;
      resultado = transformar(preparado, llave, op === "descifrar");
      revisionResultado = actual;
      operacionResultado = op;
      previo.textContent = preparado;
      salida.value = resultado;
      $("cantidad").textContent = `${resultado.length} letras`;
      $("copiar").disabled = false;
      $("descargar").disabled = false;
      const detalle = entrada !== preparado ? " Se aplicó el preprocesamiento a A-Z." : "";
      avisar(`Mensaje ${op === "cifrar" ? "cifrado" : "descifrado"} correctamente.${detalle}`);
    } catch (error) {
      if (actual === revision) avisar(error.message, true);
    } finally {
      procesar.disabled = false;
      procesar.textContent = operacion() === "cifrar" ? "Cifrar mensaje" : "Descifrar mensaje";
    }
  });

  $("limpiar").addEventListener("click", () => {
    form.reset();
    invalidar();
    clave.focus();
  });

  $("ejemplo").addEventListener("click", () => {
    form.elements.fuente.value = "linea";
    form.elements.operacion.value = "cifrar";
    clave.value = esVigenere ? "LIMÓN" : "3 1 4 2";
    texto.value = esVigenere ? "NiñoÁgil" : "ABCDEFGHIJK";
    invalidar();
    texto.focus();
  });

  $("copiar").addEventListener("click", async () => {
    if (!resultado) return;
    try {
      await navigator.clipboard.writeText(resultado);
      avisar("Resultado completo copiado.");
    } catch (_) {
      salida.focus();
      salida.select();
      avisar("Seleccionamos el resultado: usa Ctrl+C o la opción Copiar de tu dispositivo.");
    }
  });

  $("descargar").addEventListener("click", () => {
    if (!resultado || revisionResultado !== revision) return;
    const prefijo = (operacionResultado === "cifrar" ? "c" : "d") + (esVigenere ? "V" : "P");
    const nombre = `${prefijo}${++contadores[operacionResultado]}.txt`;
    const url = URL.createObjectURL(new Blob([resultado], { type: "text/plain;charset=utf-8" }));
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = nombre;
    document.body.append(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    avisar(`Descarga solicitada: ${nombre}. Contiene el resultado completo, sin salto final.`);
  });

  procesar.disabled = false;
  invalidar();
})();

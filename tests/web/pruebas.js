"use strict";
(async function () {
  const pruebas = [];
  const assert = (condicion, mensaje = "Aserción fallida") => { if (!condicion) throw new Error(mensaje); };
  const igual = (real, esperado) => assert(real === esperado, `${JSON.stringify(real)} != ${JSON.stringify(esperado)}`);
  const pausa = ms => new Promise(resolve => setTimeout(resolve, ms));
  async function test(nombre, funcion) {
    try { await funcion(); pruebas.push({ nombre, ok: true }); }
    catch (error) { pruebas.push({ nombre, ok: false, error: error.stack || String(error) }); }
  }
  async function esperar(condicion) {
    for (let i = 0; i < 200; i++) { if (condicion()) return; await pausa(10); }
    throw new Error("Tiempo de espera agotado");
  }
  const marco = document.getElementById("app");
  async function cargar(pagina) {
    await new Promise((resolve, reject) => {
      marco.onload = resolve;
      marco.onerror = reject;
      marco.src = `../../docs/${pagina}`;
    });
    await esperar(() => marco.contentWindow.Cifrados && !marco.contentDocument.getElementById("procesar").disabled);
    return marco.contentWindow;
  }
  function escribir(win, id, valor) {
    const campo = win.document.getElementById(id);
    campo.value = valor;
    campo.dispatchEvent(new win.Event("input", { bubbles: true }));
  }
  function radio(win, nombre, valor) {
    const campo = win.document.querySelector(`input[name="${nombre}"][value="${valor}"]`);
    campo.click();
  }
  async function procesar(win) {
    win.document.getElementById("formulario").requestSubmit();
    await esperar(() => !win.document.getElementById("procesar").disabled);
  }
  function fichero(win, bytes, nombre = "mensaje.txt") {
    const transferencia = new win.DataTransfer();
    transferencia.items.add(new win.File([bytes], nombre, { type: "text/plain" }));
    const campo = win.document.getElementById("archivo");
    campo.files = transferencia.files;
    campo.dispatchEvent(new win.Event("change", { bubbles: true }));
  }

  try {
    const fixtures = await (await fetch("/__fixtures__")).json();
    await test("Vectores y 200 casos comparados con Python", () => {
      for (const caso of fixtures) {
        const funcion = Cifrados[caso.algoritmo];
        igual(caso.algoritmo === "permutacion" ? Cifrados.prepararPermutacion(caso.texto)
          : Cifrados.normalizar(caso.texto, "El texto", true), caso.normalizado);
        igual(funcion(caso.texto, caso.clave), caso.cifrado);
        igual(funcion(caso.cifrado, caso.clave, true), caso.normalizado);
      }
    });
    await test("Rechazo de caracteres ajenos, tipos y vacío", () => {
      for (const valor of ["", " ", " ABC", "A B", "ABC\n", "123", "!", "ß", "ﬃ", "ı", "Ａ", "🙂", "\ufeffABC", null, 123]) {
        let rechazo = false;
        try { Cifrados.normalizar(valor); } catch (_) { rechazo = true; }
        assert(rechazo, `Se aceptó ${JSON.stringify(valor)}`);
      }
    });
    await test("Claves de permutación inválidas", () => {
      for (const valor of ["", "1", "0 1", "1 1", "2 3", "1 2 4", "1,,2", "1,2,", "1\t2", "١ ٢", "9".repeat(5000)]) {
        let rechazo = false;
        try { Cifrados.validarPermutacion(valor); } catch (_) { rechazo = true; }
        assert(rechazo, `Se aceptó ${valor.slice(0, 30)}`);
      }
    });

    for (const [pagina, clave, texto, preparado, esperado] of [
      ["index.html", "LIMÓN", "NiñoÁgil", "NINOAGIL", "YQZCNRQX"],
      ["permutacion.html", "3 1 4 2", "ABCDEFGHIJK", "ABCDEFGHIJK", "CADBGEHFKIJ"]
    ]) {
      const win = await cargar(pagina);
      const d = win.document;
      await test(`${pagina}: cifrar, preprocesado y descifrar desde línea`, async () => {
        escribir(win, "clave", clave);
        escribir(win, "texto", texto);
        await procesar(win);
        igual(d.getElementById("resultado").value, esperado);
        igual(d.getElementById("preprocesado").textContent, preparado);
        assert(!d.getElementById("descargar").disabled);
        radio(win, "operacion", "descifrar");
        igual(d.getElementById("resultado").value, "");
        escribir(win, "texto", esperado.toLowerCase());
        await procesar(win);
        igual(d.getElementById("resultado").value, preparado);
      });
      await test(`${pagina}: archivo UTF-8 y preprocesamiento`, async () => {
        radio(win, "operacion", "cifrar");
        radio(win, "fuente", "archivo");
        assert(d.getElementById("entrada-linea").hidden);
        fichero(win, texto.normalize("NFD"));
        await procesar(win);
        igual(d.getElementById("resultado").value, esperado);
        igual(d.getElementById("preprocesado").textContent, preparado);
      });
      await test(`${pagina}: descarga completa, nombre y ausencia de salto final`, async () => {
        let blob, nombre;
        const original = win.URL.createObjectURL;
        win.URL.createObjectURL = datos => { blob = datos; return original.call(win.URL, datos); };
        win.HTMLAnchorElement.prototype.click = function () { nombre = this.download; };
        d.getElementById("descargar").click();
        igual(await blob.text(), esperado);
        igual(nombre, pagina === "index.html" ? "cV1.txt" : "cP1.txt");
      });
      await test(`${pagina}: cambiar la clave elimina el resultado anterior`, () => {
        escribir(win, "clave", "!");
        igual(d.getElementById("resultado").value, "");
        assert(d.getElementById("copiar").disabled);
        assert(d.getElementById("descargar").disabled);
      });
      await test(`${pagina}: archivos inválidos y UTF-8 defectuoso`, async () => {
        escribir(win, "clave", clave);
        for (const datos of ["", "   ", "ABC\n", "\ufeffABC", new Uint8Array([255])]) {
          fichero(win, datos);
          await procesar(win);
          igual(d.getElementById("resultado").value, "");
          igual(d.getElementById("estado").dataset.tipo, "error");
          assert(d.getElementById("descargar").disabled);
        }
      });
      await test(`${pagina}: limpiar y cargar ejemplo`, async () => {
        d.getElementById("limpiar").click();
        igual(d.getElementById("clave").value, "");
        igual(d.getElementById("texto").value, "");
        assert(!d.getElementById("entrada-linea").hidden);
        d.getElementById("ejemplo").click();
        await procesar(win);
        igual(d.getElementById("resultado").value, esperado);
      });
      await test(`${pagina}: elimina espacios solo al cifrar, desde línea y archivo`, async () => {
        radio(win, "operacion", "cifrar");
        escribir(win, "clave", clave);
        escribir(win, "texto", `  ${texto.split("").join(" ")}  `);
        igual(d.getElementById("preprocesado").textContent, preparado);
        await procesar(win);
        igual(d.getElementById("resultado").value, esperado);
        radio(win, "fuente", "archivo");
        fichero(win, ` ${texto}  `);
        await procesar(win);
        igual(d.getElementById("resultado").value, esperado);
        radio(win, "operacion", "descifrar");
        fichero(win, ` ${esperado} `);
        await procesar(win);
        igual(d.getElementById("estado").dataset.tipo, "error");
        igual(d.getElementById("resultado").value, "");
        radio(win, "fuente", "linea");
        escribir(win, "texto", ` ${esperado} `);
        await procesar(win);
        igual(d.getElementById("estado").dataset.tipo, "error");
        escribir(win, "texto", esperado);
        await procesar(win);
        igual(d.getElementById("resultado").value, preparado);
        if (pagina === "index.html") {
          radio(win, "operacion", "cifrar");
          escribir(win, "clave", "LI MON");
          await procesar(win);
          igual(d.getElementById("estado").dataset.tipo, "error");
          escribir(win, "clave", clave);
        }
      });
      await test(`${pagina}: pretratamiento de números exclusivo de permutación al cifrar`, async () => {
        radio(win, "operacion", "cifrar");
        radio(win, "fuente", "linea");
        escribir(win, "clave", clave);
        escribir(win, "texto", `01 ${texto} 23456789`);
        await procesar(win);
        if (pagina === "permutacion.html") {
          igual(d.getElementById("preprocesado").textContent, preparado);
          igual(d.getElementById("resultado").value, esperado);
        } else {
          igual(d.getElementById("resultado").value, "");
          igual(d.getElementById("estado").dataset.tipo, "error");
        }
        radio(win, "fuente", "archivo");
        fichero(win, `01 ${texto} 23456789`);
        await procesar(win);
        if (pagina === "permutacion.html") igual(d.getElementById("resultado").value, esperado);
        else igual(d.getElementById("estado").dataset.tipo, "error");
        radio(win, "operacion", "descifrar");
        fichero(win, `${esperado}1`);
        await procesar(win);
        igual(d.getElementById("estado").dataset.tipo, "error");
        igual(d.getElementById("resultado").value, "");
        radio(win, "operacion", "cifrar");
        fichero(win, " 0123456789 ");
        await procesar(win);
        igual(d.getElementById("estado").dataset.tipo, "error");
        radio(win, "fuente", "linea");
        escribir(win, "texto", texto);
      });
      if (pagina === "permutacion.html") {
        await test("Regresión jos1223: pretratamiento JOS y cifrado SJO", async () => {
          radio(win, "operacion", "cifrar");
          radio(win, "fuente", "linea");
          escribir(win, "clave", "3 1 4 2");
          escribir(win, "texto", "jos1223");
          igual(d.getElementById("preprocesado").textContent, "JOS");
          await procesar(win);
          igual(d.getElementById("resultado").value, "SJO");
          assert(d.getElementById("ayuda-texto").textContent.includes("dígitos 0-9"));
        });
      }
      await test(`${pagina}: disposición sin desbordamiento en móvil y escritorio`, async () => {
        for (const ancho of [360, 390, 768, 1366]) {
          marco.width = ancho;
          await pausa(50);
          assert(d.documentElement.scrollWidth <= d.documentElement.clientWidth + 1, `Desbordamiento con ${ancho}px`);
          for (const id of ["clave", "texto", "procesar", "resultado", "copiar", "descargar"]) {
            const caja = d.getElementById(id).getBoundingClientRect();
            assert(caja.left >= 0 && caja.right <= ancho + 1, `${id} fuera de ${ancho}px`);
            assert(caja.width > 0 && caja.height > 0, `${id} no visible`);
          }
        }
      });
      await test(`${pagina}: acciones visibles en portátil de 1366×768`, async () => {
        marco.width = 1366;
        marco.height = 768;
        await pausa(50);
        for (const id of ["clave", "texto", "procesar", "copiar", "descargar"]) {
          const caja = d.getElementById(id).getBoundingClientRect();
          assert(caja.top >= 0 && caja.bottom <= 768, `${id} requiere desplazamiento en portátil`);
        }
      });
    }
    await test("JavaScript de permutación versionado según su contenido para evitar caché anterior", async () => {
      const scripts = Array.from(marco.contentDocument.scripts);
      igual(scripts.length, 2);
      for (const script of scripts) {
        const url = new URL(script.src);
        const respuesta = await fetch(url);
        igual(respuesta.status, 200);
        const digest = await crypto.subtle.digest("SHA-256", await respuesta.arrayBuffer());
        const hash = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, "0")).join("");
        igual(url.searchParams.get("v"), hash.slice(0, 12));
      }
    });
    await test("Navegación, límites y recursos bajo una subruta de proyecto", async () => {
      const respuesta = await fetch("../../docs/limites.html");
      igual(respuesta.status, 200);
      assert((await respuesta.text()).includes("YQZCNRQX"));
      const acuerdo = await (await fetch("../../docs/limitaciones.txt")).text();
      assert(acuerdo.includes("preprocesado"));
    });
  } catch (error) {
    pruebas.push({ nombre: "Infraestructura", ok: false, error: error.stack || String(error) });
  }
  const resultado = { ok: pruebas.every(p => p.ok), pruebas };
  document.getElementById("informe").textContent = JSON.stringify(resultado, null, 2);
  document.title = resultado.ok ? "PRUEBAS OK" : "PRUEBAS FALLIDAS";
  await fetch("/__resultados__", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(resultado) });
})();

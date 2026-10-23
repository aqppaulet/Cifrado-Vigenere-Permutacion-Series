"""Pruebas de botones y archivos con Tk real; requieren escritorio o Xvfb."""

from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from cifrados import interfaz_permutacion, interfaz_vigenere

try:
    import tkinter as tk
except ImportError:
    tk = None


def configuracion(modulo):
    with patch.object(modulo, "ejecutar") as ejecutar:
        modulo.main()
        return ejecutar.call_args.kwargs


class PruebasInicio(unittest.TestCase):
    def test_sin_argumentos_abre_la_ventana_de_cada_algoritmo(self):
        for modulo in (interfaz_vigenere, interfaz_permutacion):
            with self.subTest(modulo=modulo.__name__), patch.object(sys, "argv", ["programa.py"]), patch("cifrados.ventana.abrir_ventana") as abrir:
                modulo.main()
                abrir.assert_called_once()
                opciones = abrir.call_args.kwargs
                self.assertIn("Clave de", opciones["ayuda_clave"])
                self.assertIn("Ejemplo:", opciones["ejemplo"])


@unittest.skipIf(tk is None, "Tkinter no está instalado")
class PruebasVentana(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Se necesita un escritorio o Xvfb: {error}")
        self.raiz.withdraw()
        self.addCleanup(self.raiz.destroy)
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)
        self.error = self.enterContext(patch("tkinter.messagebox.showerror"))
        self.aviso = self.enterContext(patch("tkinter.messagebox.showwarning"))

    def crear(self, modulo=interfaz_vigenere):
        from cifrados.ventana import AplicacionCifrado
        self.app = AplicacionCifrado(self.raiz, **configuracion(modulo), carpeta=self.carpeta)
        self.raiz.update_idletasks()
        return self.app

    def procesar(self):
        with redirect_stdout(io.StringIO()):
            self.app.boton_procesar.invoke()

    def test_linea_minuscula_cifrar_descifrar_y_copiar(self):
        app = self.crear()
        app.clave.set("lemon")
        app.texto.set("attackatdawn")
        self.procesar()
        self.assertEqual(app.resultado, "LXFOPVEFRNHR")
        self.assertEqual((self.carpeta / "cV1.txt").read_bytes(), b"LXFOPVEFRNHR")
        app.boton_copiar.invoke()
        self.assertEqual(self.raiz.clipboard_get(), "LXFOPVEFRNHR")
        app.operacion.set("descifrar")
        self.assertEqual(app.boton_procesar.cget("text"), "Descifrar y guardar")
        app.texto.set("lxfopvefrnhr")
        self.procesar()
        self.assertEqual(app.resultado, "ATTACKATDAWN")
        self.assertEqual((self.carpeta / "dV1.txt").read_bytes(), b"ATTACKATDAWN")
        self.error.assert_not_called()

    def test_permutacion_tiene_su_propia_ventana_y_procesa_restos(self):
        app = self.crear(interfaz_permutacion)
        self.assertIn("Permutación", self.raiz.title())
        app.clave.set("3,1,4,2")
        app.texto.set("abcdefghijk")
        self.procesar()
        self.assertEqual(app.resultado, "CADBGEHFKIJ")
        app.operacion.set("descifrar")
        app.texto.set("CADBGEHFKIJ")
        self.procesar()
        self.assertEqual(app.resultado, "ABCDEFGHIJK")
        self.assertTrue((self.carpeta / "cP1.txt").is_file())
        self.assertTrue((self.carpeta / "dP1.txt").is_file())

    def test_preprocesado_visible_en_linea_y_archivo(self):
        app = self.crear()
        app.clave.set("LIMÓN")
        app.texto.set(" Niño ÁéíóúÜ ")
        self.procesar()
        esperado = app.resultado
        self.assertTrue(esperado)
        self.assertEqual(app.preprocesado.get(), "NINOAEIOUU")
        ruta = self.carpeta / "entrada.txt"
        ruta.write_text(" Nin\u0303o ÁéíóúÜ ", encoding="utf-8")
        app.fuente.set("archivo")
        app.archivo.set(str(ruta))
        self.procesar()
        self.assertEqual(app.preprocesado.get(), "NINOAEIOUU")
        self.assertEqual(app.resultado, esperado)
        self.assertIn("preprocesamiento", app.estado.get())
        app.operacion.set("descifrar")
        app.fuente.set("linea")
        app.texto.set(esperado)
        self.procesar()
        self.assertEqual(app.resultado, "NINOAEIOUU")
        self.error.assert_not_called()

    def test_selector_acepta_archivo_fuera_de_la_carpeta_del_programa(self):
        app = self.crear()
        with tempfile.TemporaryDirectory() as otra:
            ruta = Path(otra) / "mensaje de profesora.txt"
            ruta.write_text("attackatdawn", encoding="utf-8")
            app.fuente.set("archivo")
            self.assertEqual(str(app.entrada_texto.cget("state")), "disabled")
            self.assertEqual(str(app.ruta_archivo.cget("state")), "readonly")
            with patch("tkinter.filedialog.askopenfilename", return_value=str(ruta)):
                app.boton_archivo.invoke()
            self.assertEqual(app.archivo.get(), str(ruta))
            app.clave.set("LEMON")
            self.procesar()
            self.assertEqual(app.resultado, "LXFOPVEFRNHR")
            self.assertEqual(ruta.read_text(), "attackatdawn")

    def test_cancelar_selector_no_cambia_la_entrada(self):
        app = self.crear()
        app.fuente.set("archivo")
        app.archivo.set("anterior.txt")
        with patch("tkinter.filedialog.askopenfilename", return_value=""):
            app.boton_archivo.invoke()
        self.assertEqual(app.archivo.get(), "anterior.txt")

    def test_errores_de_clave_y_texto_permiten_corregir_sin_guardar(self):
        app = self.crear()
        for clave, texto in (("", "ABC"), ("A!", "ABC"), ("B", ""), ("B", "   "), ("B", "123"), ("B", "ABC\n")):
            with self.subTest(clave=clave, texto=texto):
                app.clave.set(clave)
                app.texto.set(texto)
                self.procesar()
                self.assertEqual(app.resultado, "")
                self.assertEqual(str(app.boton_copiar.cget("state")), "disabled")
                self.assertFalse(list(self.carpeta.glob("cV*.txt")))
        self.assertEqual(self.error.call_count, 6)
        app.texto.set("ABC")
        self.procesar()
        self.assertEqual(app.resultado, "BCD")

    def test_archivos_invalidos_no_generan_resultados(self):
        app = self.crear()
        app.clave.set("B")
        app.fuente.set("archivo")
        self.procesar()
        for datos in (b"", b"ABC\n", b"ABC\r\n", b"   ", "🙂".encode(), b"\xef\xbb\xbfABC", b"\xff"):
            with self.subTest(datos=datos):
                ruta = self.carpeta / "entrada.txt"
                ruta.write_bytes(datos)
                app.archivo.set(str(ruta))
                self.procesar()
                self.assertEqual(app.resultado, "")
                self.assertFalse(list(self.carpeta.glob("cV*.txt")))
        self.assertEqual(self.error.call_count, 8)

    def test_cambiar_entrada_invalida_el_resultado_anterior(self):
        app = self.crear()
        app.clave.set("B")
        app.texto.set("ABC")
        for variable, valor in ((app.clave, "C"), (app.texto, "DEF"), (app.operacion, "descifrar"), (app.fuente, "archivo")):
            self.procesar()
            self.assertTrue(app.resultado)
            variable.set(valor)
            self.assertEqual(app.resultado, "")
            self.assertEqual(app.salida.get("1.0", "end-1c"), "")
            self.assertEqual(str(app.boton_copiar.cget("state")), "disabled")

    def test_vista_previa_acotada_copia_y_archivo_completos(self):
        app = self.crear()
        app.clave.set("B")
        app.texto.set("A" * 10000)
        self.procesar()
        self.assertLess(len(app.salida.get("1.0", "end-1c")), 2200)
        self.assertIn("Vista previa", app.salida.get("1.0", "end-1c"))
        self.assertEqual((self.carpeta / "cV1.txt").read_text(), "B" * 10000)
        app.boton_copiar.invoke()
        self.assertEqual(self.raiz.clipboard_get(), "B" * 10000)

    def test_si_falla_guardado_se_puede_copiar_el_resultado(self):
        app = self.crear()
        app.clave.set("B")
        app.texto.set("ABC")
        with patch("cifrados.ventana.guardar_resultado", side_effect=PermissionError("Sin permiso")):
            self.procesar()
        self.aviso.assert_called_once()
        self.assertEqual(app.resultado, "BCD")
        app.boton_copiar.invoke()
        self.assertEqual(self.raiz.clipboard_get(), "BCD")
        self.assertFalse(list(self.carpeta.iterdir()))

    def test_limpiar_deja_formulario_listo(self):
        app = self.crear()
        app.clave.set("B")
        app.texto.set("ABC")
        self.procesar()
        app.limpiar()
        self.assertEqual(app.clave.get(), "")
        self.assertEqual(app.texto.get(), "")
        self.assertEqual(app.archivo.get(), "")
        self.assertEqual(app.resultado, "")
        self.assertEqual(app.fuente.get(), "linea")

    def test_controles_visibles_en_tamano_minimo(self):
        app = self.crear(interfaz_permutacion)
        app.clave.set("3 1 4 2")
        app.texto.set("ABCDEFGHIJK")
        self.procesar()
        self.raiz.geometry("740x700")
        self.raiz.deiconify()
        self.raiz.update()
        for control in (app.entrada_clave, app.entrada_texto, app.boton_archivo, app.boton_procesar, app.salida, app.boton_copiar, app.etiqueta_estado):
            with self.subTest(control=control):
                x = control.winfo_rootx() - self.raiz.winfo_rootx()
                y = control.winfo_rooty() - self.raiz.winfo_rooty()
                self.assertGreaterEqual(x, 0)
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(x + control.winfo_width(), 740)
                self.assertLessEqual(y + control.winfo_height(), 700)

    def test_inicio_dentro_de_pantallas_pequenas_y_grandes(self):
        app = self.crear(interfaz_permutacion)
        self.raiz.deiconify()
        for ancho, alto in ((1366, 768), (1024, 600), (800, 600)):
            with self.subTest(pantalla=(ancho, alto)), patch.object(self.raiz, "winfo_screenwidth", return_value=ancho), patch.object(self.raiz, "winfo_screenheight", return_value=alto):
                app._centrar_en_pantalla()
                self.raiz.update()
                self.assertGreaterEqual(self.raiz.winfo_x(), 0)
                self.assertGreaterEqual(self.raiz.winfo_y(), 0)
                self.assertLessEqual(self.raiz.winfo_x() + self.raiz.winfo_width(), ancho)
                self.assertLessEqual(self.raiz.winfo_y() + self.raiz.winfo_height() + 30, alto)
                if alto >= 768:
                    self.assertFalse(app.desplazamiento.winfo_ismapped())
                    y = app.boton_copiar.winfo_rooty() - self.raiz.winfo_rooty()
                    self.assertLessEqual(y + app.boton_copiar.winfo_height(), self.raiz.winfo_height())
                # Si el formulario supera el alto disponible, su final sigue accesible.
                app.lienzo.yview_moveto(1)
                self.raiz.update()
                y = app.boton_copiar.winfo_rooty() - self.raiz.winfo_rooty()
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(y + app.boton_copiar.winfo_height(), self.raiz.winfo_height())


if __name__ == "__main__":
    unittest.main()

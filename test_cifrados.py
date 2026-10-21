"""Verifica vectores conocidos, entradas especiales y el flujo real con archivos."""

import itertools
from pathlib import Path
import shutil
import string
import subprocess
import sys
import tempfile
import unittest

import permutacion_series
import vigenere


class PruebasVigenere(unittest.TestCase):
    def test_vector_conocido(self):
        self.assertEqual(vigenere.cifrar("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")
        self.assertEqual(vigenere.descifrar("LXFOPVEFRNHR", "LEMON"), "ATTACKATDAWN")

    def test_formato_y_avance_de_clave(self):
        self.assertEqual(vigenere.cifrar("Attack at dawn! 123", "lemon"), "Lxfopv ef rnhr! 123")
        self.assertEqual(vigenere.cifrar("á🙂ñ A\nB", "BC"), "á🙂ñ B\nD")

    def test_alfabeto_espanol(self):
        self.assertEqual(vigenere.cifrar("NnÑñOoZz", "B", espanol=True), "ÑñOoPpAa")

    def test_recuperacion(self):
        for espanol, clave in ((False, "LIMON"), (True, "AÑO")):
            for texto in ("", "123🙂", "¡Hola, señor! Áéíóú\n\n\tZz  ", "ßıﬃ"):
                with self.subTest(espanol=espanol, texto=texto):
                    resultado = vigenere.cifrar(texto, clave, espanol)
                    self.assertEqual(vigenere.descifrar(resultado, clave, espanol), texto)

    def test_claves_invalidas(self):
        for clave in ("", "  ", "A B", "123", "ÁRBOL", "AÑO", "ß", "ı"):
            with self.subTest(clave=clave), self.assertRaises(ValueError):
                vigenere.cifrar("Hola", clave)


class PruebasVigenereAmpliado(unittest.TestCase):
    def test_vectores_conocidos_incluyen_simbolos_y_utf8(self):
        self.assertEqual(vigenere.cifrar("A !", "B", ampliado=True), "g2Jj")
        self.assertEqual(vigenere.descifrar("g2Jj", "B", ampliado=True), "A !")
        self.assertEqual(vigenere.cifrar("é", "K", ampliado=True), "DvQ=")
        self.assertEqual(vigenere.descifrar("DvQ=", "K", ampliado=True), "é")

    def test_recuperacion_unicode_y_claves_sin_normalizar(self):
        textos = (
            "", " \t\r\n  ", string.printable,
            "¡Áéíóú Ññ! 🙂👩🏽‍💻 中文 العربية e\u0301\r\n\x00\ud7ff\ue000\uffff\U0010ffff  ",
            "Una línea con símbolos @#$ y espacios\n" * 50,
        )
        for clave in ("K", "k", " Mi clave #2026 🔑 ", " ", "\x00"):
            for texto in textos:
                with self.subTest(clave=clave, longitud=len(texto)):
                    cifrado = vigenere.cifrar(texto, clave, ampliado=True)
                    self.assertTrue(all(len(linea) <= 80 for linea in cifrado.splitlines()))
                    self.assertTrue(all(caracter in string.ascii_letters + string.digits + "+/=\n" for caracter in cifrado))
                    self.assertEqual(vigenere.descifrar(cifrado, clave, ampliado=True), texto)
        self.assertNotEqual(vigenere.cifrar("Hola", "K", ampliado=True), vigenere.cifrar("Hola", "k", ampliado=True))
        self.assertNotEqual(vigenere.cifrar("Hola", "K", ampliado=True), vigenere.cifrar("Hola", " K ", ampliado=True))

    def test_errores_ampliados(self):
        with self.assertRaisesRegex(ValueError, "vacía"):
            vigenere.cifrar("Hola", "", ampliado=True)
        with self.assertRaisesRegex(ValueError, "solo modo"):
            vigenere.cifrar("Hola", "A", espanol=True, ampliado=True)
        for invalido in ("!!", "abcd=!?", "á", "A"):
            with self.subTest(cifrado=invalido), self.assertRaisesRegex(ValueError, "Base64"):
                vigenere.descifrar(invalido, "K", ampliado=True)
        cifrado = vigenere.cifrar("🙂", "X", ampliado=True)
        with self.assertRaisesRegex(ValueError, "Revisa la clave"):
            vigenere.descifrar(cifrado, "A", ampliado=True)


class PruebasPermutacion(unittest.TestCase):
    def test_vector_conocido_y_bloque_incompleto(self):
        self.assertEqual(permutacion_series.cifrar("ABCDEFGHIJ", "3 1 4 2"), "CADBGEHFIJ")
        self.assertEqual(permutacion_series.descifrar("CADBGEHFIJ", "3,1,4,2"), "ABCDEFGHIJ")

    def test_todas_las_permutaciones_y_restos(self):
        texto = "¡a Ñ🙂\r\n\tZ  "
        for tamano in range(2, 6):
            for orden in itertools.permutations(range(1, tamano + 1)):
                clave = " ".join(map(str, orden))
                for longitud in range(len(texto) + 1):
                    original = texto[:longitud]
                    resultado = permutacion_series.cifrar(original, clave)
                    self.assertEqual(len(resultado), len(original))
                    self.assertEqual(permutacion_series.descifrar(resultado, clave), original)

    def test_claves_invalidas(self):
        for clave in ("", "1", "0 1", "1 1", "2 3", "1 2 4", "a b", "1.0 2", "-1 2", "1,2,", "1,2x"):
            with self.subTest(clave=clave), self.assertRaises(ValueError):
                permutacion_series.cifrar("Hola", clave)


class PruebasConsola(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.proyecto = Path(temporal.name) / "proyecto"
        self.proyecto.mkdir()
        self.otra_carpeta = Path(temporal.name) / "otra carpeta"
        self.otra_carpeta.mkdir()
        for nombre in ("interfaz.py", "vigenere.py", "permutacion_series.py"):
            shutil.copyfile(Path(__file__).resolve().parent / nombre, self.proyecto / nombre)

    def ejecutar(self, programa, *argumentos, entrada=None):
        script = self.proyecto / programa
        return subprocess.run(
            [sys.executable, str(script), *argumentos],
            input=entrada, capture_output=True, text=True, encoding="utf-8", check=False,
            cwd=self.otra_carpeta, timeout=10,
        )

    def test_teclado_acepta_caracteres_variados_y_recupera_espacios(self):
        textos = (
            "  MAYÚSCULAS minúsculas AaZz Ññ 0123456789 " + string.punctuation
            + " áéíóúü ÁÉÍÓÚÜ 🙂👩🏽‍💻 中文 العربية e\u0301\t  ",
            "   \t   ",
            "",
        )
        for programa, clave, prefijo, alfabeto in (
            ("vigenere.py", "MiXtA", "V", "1\n"),
            ("permutacion_series.py", "3 1 4 2", "P", ""),
        ):
            for indice, texto in enumerate(textos):
                with self.subTest(programa=programa, texto=texto):
                    cifrar = self.ejecutar(
                        programa, entrada=f"1\n{alfabeto}{clave}\n1\n{texto}\n0\n",
                    )
                    self.assertEqual(cifrar.returncode, 0, cifrar.stderr)
                    nombre_cifrado = f"c{prefijo}{indice + 1}.txt"
                    descifrar = self.ejecutar(programa, "--descifrar", "-k", clave, "-a", nombre_cifrado)
                    self.assertEqual(descifrar.returncode, 0, descifrar.stderr)
                    recuperado = self.proyecto / f"d{prefijo}{indice + 1}.txt"
                    self.assertEqual(recuperado.read_bytes(), texto.encode("utf-8"))

    def test_archivos_utf8_con_saltos_y_espacios_exactos(self):
        contenido = "¡Hola, señor!\r\n\nPython 123 👋\t  ".encode("utf-8")
        origen = self.proyecto / "mensaje con espacios.txt"
        origen.write_bytes(contenido)
        for programa, clave, prefijo in (
            ("vigenere.py", "LIMON", "V"),
            ("permutacion_series.py", "3 1 4 2", "P"),
        ):
            with self.subTest(programa=programa):
                cifrado = self.proyecto / f"c{prefijo}1.txt"
                recuperado = self.proyecto / f"d{prefijo}1.txt"
                for operacion, entrada in (
                    ("--cifrar", origen), ("--descifrar", cifrado),
                ):
                    proceso = self.ejecutar(programa, operacion, "-k", clave, "-a", entrada.name)
                    self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertEqual(recuperado.read_bytes(), contenido)
                self.assertFalse((self.otra_carpeta / cifrado.name).exists())

    def test_errores_sin_traceback(self):
        for argumentos in (
            ("--cifrar", "-k", "123", "-t", "Hola"),
            ("--cifrar", "-k", "ABC"),
            ("--cifrar", "-k", "ABC", "-a", "/archivo/que/no/existe.txt"),
        ):
            proceso = self.ejecutar("vigenere.py", *argumentos)
            self.assertNotEqual(proceso.returncode, 0)
            self.assertNotIn("Traceback", proceso.stderr)

    def test_menu_reintenta_clave_y_cifra(self):
        proceso = self.ejecutar("vigenere.py", entrada="1\n1\n123\nLEMON\n1\nATTACKATDAWN\n0\n")
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("Clave inválida", proceso.stdout)
        self.assertIn("LXFOPVEFRNHR", proceso.stdout)
        self.assertEqual((self.proyecto / "cV1.txt").read_text(), "LXFOPVEFRNHR")

    def test_resultados_numerados_independientes_sin_preguntar(self):
        for programa, operacion, clave, esperado, nombre in (
            ("vigenere.py", "--cifrar", "B", "BCDE", "cV1.txt"),
            ("permutacion_series.py", "--cifrar", "3 1 4 2", "CADB", "cP1.txt"),
            ("vigenere.py", "--descifrar", "B", "ZABC", "dV1.txt"),
            ("permutacion_series.py", "--descifrar", "3 1 4 2", "BDAC", "dP1.txt"),
            ("vigenere.py", "--cifrar", "C", "CDEF", "cV2.txt"),
            ("permutacion_series.py", "--cifrar", "2 1", "BADC", "cP2.txt"),
            ("vigenere.py", "--descifrar", "C", "YZAB", "dV2.txt"),
            ("permutacion_series.py", "--descifrar", "2 1", "BADC", "dP2.txt"),
            ("vigenere.py", "--cifrar", "D", "DEFG", "cV3.txt"),
            ("permutacion_series.py", "--cifrar", "4 3 2 1", "DCBA", "cP3.txt"),
        ):
            with self.subTest(programa=programa):
                proceso = self.ejecutar(programa, operacion, "-k", clave, "-t", "ABCD")
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertNotIn("Nombre del archivo de salida", proceso.stdout)
                self.assertIn(str(self.proyecto / nombre), proceso.stdout)
                self.assertEqual((self.proyecto / nombre).read_text(), esperado)
        self.assertEqual((self.proyecto / "cV1.txt").read_text(), "BCDE")
        self.assertEqual((self.proyecto / "cP1.txt").read_text(), "CADB")
        self.assertEqual((self.proyecto / "dV1.txt").read_text(), "ZABC")
        self.assertEqual((self.proyecto / "dP1.txt").read_text(), "BDAC")

    def test_rechaza_rutas_fuera_del_proyecto(self):
        for nombre in ("../fuera.txt", str(self.otra_carpeta / "fuera.txt"), "carpeta/archivo.txt"):
            proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", nombre)
            self.assertNotEqual(proceso.returncode, 0)
            self.assertIn("sin carpetas ni rutas", proceso.stderr)
        enlace = self.proyecto / "enlace.txt"
        enlace.symlink_to(self.otra_carpeta / "fuera.txt")
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", enlace.name)
        self.assertNotEqual(proceso.returncode, 0)
        self.assertFalse((self.otra_carpeta / "fuera.txt").exists())

    def test_menu_lee_por_nombre_y_numera_si_existe(self):
        (self.proyecto / "entrada.txt").write_text("CADB", encoding="utf-8")
        (self.proyecto / "dP1.txt").write_text("Conservar", encoding="utf-8")
        proceso = self.ejecutar(
            "permutacion_series.py",
            entrada="2\n3 1 4 2\n3\nentrada\n0\n",
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("Nombre del archivo de entrada", proceso.stdout)
        self.assertEqual((self.proyecto / "dP2.txt").read_text(), "ABCD")
        self.assertEqual((self.proyecto / "dP1.txt").read_text(), "Conservar")

    def test_guardado_omite_carpetas_y_enlaces_existentes(self):
        destino = self.otra_carpeta / "conservar.txt"
        destino.write_text("Conservar", encoding="utf-8")
        (self.proyecto / "cV1.txt").symlink_to(destino)
        (self.proyecto / "cV2.txt").mkdir()
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-t", "ABCD")
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertEqual((self.proyecto / "cV3.txt").read_text(), "BCDE")
        self.assertEqual(destino.read_text(), "Conservar")

    def test_teclado_multilinea_muestra_todo_y_guarda(self):
        texto = "\n".join(f"Linea {numero}: Hola Python" for numero in range(1, 9))
        for programa, modulo, clave, prefijo, alfabeto in (
            ("vigenere.py", vigenere, "B", "V", "1\n"),
            ("permutacion_series.py", permutacion_series, "3 1 4 2", "P", ""),
        ):
            for numero, operacion, funcion in ((1, "1", modulo.cifrar), (2, "2", modulo.descifrar)):
                with self.subTest(programa=programa, operacion=operacion):
                    esperado = funcion(texto, clave)
                    proceso = self.ejecutar(
                        programa, entrada=f"{operacion}\n{alfabeto}{clave}\n2\n{texto}\nFIN\n0\n",
                    )
                    self.assertEqual(proceso.returncode, 0, proceso.stderr)
                    self.assertIn(esperado, proceso.stdout)
                    self.assertNotIn("vista previa", proceso.stdout)
                    salida = f"{'c' if operacion == '1' else 'd'}{prefijo}1.txt"
                    self.assertEqual((self.proyecto / salida).read_text(), esperado)

    def test_archivo_muestra_cinco_lineas_y_guarda_todo(self):
        texto = "\n".join(f"Linea {numero}: Texto de ejemplo" for numero in range(1, 9))
        (self.proyecto / "entrada.txt").write_text(texto, encoding="utf-8")
        for programa, modulo, clave, prefijo in (
            ("vigenere.py", vigenere, "B", "V"),
            ("permutacion_series.py", permutacion_series, "3 1 4 2", "P"),
        ):
            for numero, operacion, funcion, tipo in (
                (1, "--cifrar", modulo.cifrar, "cifrado"),
                (2, "--descifrar", modulo.descifrar, "descifrado"),
            ):
                with self.subTest(programa=programa, operacion=operacion):
                    esperado = funcion(texto, clave)
                    proceso = self.ejecutar(programa, operacion, "-k", clave, "-a", "entrada.txt")
                    self.assertEqual(proceso.returncode, 0, proceso.stderr)
                    self.assertIn(f"Texto {tipo}: vista previa (primeras 5 líneas)", proceso.stdout)
                    self.assertIn("".join(esperado.splitlines(keepends=True)[:5]), proceso.stdout)
                    self.assertNotIn(esperado, proceso.stdout)
                    self.assertIn("Vista previa truncada", proceso.stdout)
                    salida = f"{'c' if operacion == '--cifrar' else 'd'}{prefijo}1.txt"
                    self.assertEqual((self.proyecto / salida).read_text(), esperado)

    def test_menu_archivo_corto_o_vacio_muestra_vista_previa(self):
        for numero, texto in enumerate(("ABCD", ""), start=1):
            with self.subTest(texto=texto):
                (self.proyecto / "entrada.txt").write_text(texto, encoding="utf-8")
                proceso = self.ejecutar("permutacion_series.py", entrada="1\n3 1 4 2\n3\nentrada\n0\n")
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertIn("vista previa (primeras 5 líneas)", proceso.stdout)
                self.assertNotIn("Vista previa truncada", proceso.stdout)
                self.assertIn("CADB" if texto else "(Texto vacío)", proceso.stdout)
                self.assertEqual(
                    (self.proyecto / f"cP{numero}.txt").read_text(),
                    permutacion_series.cifrar(texto, "3 1 4 2"),
                )

    def test_ampliado_menu_predeterminado_y_descifrado_desde_archivo(self):
        texto = "  ¡Hola! 123 @#$ Ññ 🙂  "
        clave = " Mi clave #2026 🔑 "
        cifrar = self.ejecutar("vigenere.py", entrada=f"1\n\n{clave}\n1\n{texto}\n0\n")
        self.assertEqual(cifrar.returncode, 0, cifrar.stderr)
        cifrado = (self.proyecto / "cV1.txt").read_text()
        self.assertEqual(cifrado, vigenere.cifrar(texto, clave, ampliado=True))
        self.assertIn(cifrado, cifrar.stdout)
        descifrar = self.ejecutar("vigenere.py", entrada=f"2\n3\n{clave}\n3\ncV1\n0\n")
        self.assertEqual(descifrar.returncode, 0, descifrar.stderr)
        self.assertIn(texto, descifrar.stdout)
        self.assertEqual((self.proyecto / "dV1.txt").read_bytes(), texto.encode("utf-8"))

    def test_ampliado_archivos_completos_y_vista_previa(self):
        texto = "  Áé Ññ 123 @#$ 🙂 Línea con texto.\r\n" * 40
        clave = "Símbolos ! 🔑"
        (self.proyecto / "entrada.txt").write_bytes(texto.encode("utf-8"))
        cifrar = self.ejecutar("vigenere.py", "--cifrar", "--ampliado", "-k", clave, "-a", "entrada.txt")
        self.assertEqual(cifrar.returncode, 0, cifrar.stderr)
        cifrado = (self.proyecto / "cV1.txt").read_text()
        self.assertIn("\n".join(cifrado.splitlines()[:5]), cifrar.stdout)
        self.assertNotIn(cifrado, cifrar.stdout)
        self.assertIn("Vista previa truncada", cifrar.stdout)
        descifrar = self.ejecutar("vigenere.py", "--descifrar", "--ampliado", "-k", clave, "-a", "cV1.txt")
        self.assertEqual(descifrar.returncode, 0, descifrar.stderr)
        self.assertIn("primeras 5 líneas", descifrar.stdout)
        self.assertEqual((self.proyecto / "dV1.txt").read_bytes(), texto.encode("utf-8"))

    def test_ampliado_argumentos_y_errores_sin_traceback(self):
        cifrar = self.ejecutar("vigenere.py", "--cifrar", "--ampliado", "-k", "B", "-t", "A !")
        self.assertEqual(cifrar.returncode, 0, cifrar.stderr)
        self.assertIn("g2Jj", cifrar.stdout)
        for argumentos in (
            ("--descifrar", "--ampliado", "-k", "B", "-t", "!!"),
            ("--cifrar", "--ampliado", "-k", "", "-t", "Hola"),
            ("--cifrar", "--ampliado", "--espanol", "-k", "B", "-t", "Hola"),
        ):
            with self.subTest(argumentos=argumentos):
                proceso = self.ejecutar("vigenere.py", *argumentos)
                self.assertNotEqual(proceso.returncode, 0)
                self.assertNotIn("Traceback", proceso.stderr)
        self.assertFalse((self.proyecto / "cV2.txt").exists())
        self.assertFalse((self.proyecto / "dV1.txt").exists())


if __name__ == "__main__":
    unittest.main()

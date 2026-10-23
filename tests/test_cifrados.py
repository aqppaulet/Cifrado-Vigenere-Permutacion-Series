"""Contrato A-Z, vectores de referencia e interfaces reales en temporales."""

import itertools
from pathlib import Path
import shutil
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

    def test_minusculas_se_normalizan(self):
        self.assertEqual(vigenere.cifrar("AttackAtDawn", "lemon"), "LXFOPVEFRNHR")
        self.assertEqual(vigenere.descifrar("lxfopvefrnhr", "LeMoN"), "ATTACKATDAWN")
        self.assertEqual(vigenere.validar_clave("lemon"), "LEMON")

    def test_modulo_y_longitudes_de_clave(self):
        self.assertEqual(vigenere.cifrar("AZ", "B"), "BA")
        self.assertEqual(vigenere.descifrar("BA", "B"), "AZ")
        self.assertEqual(vigenere.cifrar("ABC", "A"), "ABC")
        self.assertEqual(vigenere.cifrar("A", "LEMON"), "L")

    def test_claves_invalidas(self):
        for clave in ("", " ", " A", "A ", "A B", "123", "ß", "ı", "ﬃ", "Ａ", "A\n", None, 12):
            for funcion in (vigenere.cifrar, vigenere.descifrar):
                with self.subTest(clave=clave, funcion=funcion.__name__), self.assertRaises(ValueError):
                    funcion("ABC", clave)


class PruebasTexto(unittest.TestCase):
    def test_preprocesamiento_de_enie_acentos_y_mayusculas(self):
        for modulo, clave in ((vigenere, "LIMÓN"), (permutacion_series, "3 1 4 2")):
            for texto, esperado in (("niÑo", "NINO"), ("áÉíÓúÜ", "AEIOUU"), ("camión", "CAMION"), ("nin\u0303o", "NINO"), ("cafe\u0301", "CAFE")):
                with self.subTest(modulo=modulo.__name__, texto=texto):
                    cifrado = modulo.cifrar(texto, clave)
                    self.assertTrue(set(cifrado) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
                    self.assertEqual(modulo.descifrar(cifrado, clave), esperado)
        self.assertEqual(vigenere.validar_clave("aÑó"), "ANO")
        self.assertEqual(vigenere.cifrar("niño", "limón"), vigenere.cifrar("NINO", "LIMON"))

    def test_ambos_algoritmos_rechazan_caracteres_ajenos_y_vacio(self):
        for modulo, clave in ((vigenere, "LEMON"), (permutacion_series, "3 1 4 2")):
            for texto in ("", " ", "A\nB", "ABC\n", "A\r\n", "A\tB", "A\u00a0B", "1", "!", "🙂", "ß", "ı", "ﬃ", "Ａ", "\ufeffABC", "A\x00", None, 123):
                for funcion in (modulo.cifrar, modulo.descifrar):
                    with self.subTest(modulo=modulo.__name__, texto=texto, funcion=funcion.__name__), self.assertRaises(ValueError):
                        funcion(texto, clave)

    def test_espacios_solo_se_eliminan_al_cifrar(self):
        for modulo, clave in ((vigenere, "LIMÓN"), (permutacion_series, "3 1 4 2")):
            for texto in ("Niño Ágil", " Niño  Ágil ", "N I N O A G I L"):
                with self.subTest(modulo=modulo.__name__, texto=texto):
                    cifrado = modulo.cifrar(texto, clave)
                    self.assertEqual(cifrado, modulo.cifrar("NINOAGIL", clave))
                    self.assertEqual(modulo.descifrar(cifrado, clave), "NINOAGIL")
            for texto in (" ABC", "ABC ", "A B"):
                with self.subTest(modulo=modulo.__name__, cifrado=texto), self.assertRaises(ValueError):
                    modulo.descifrar(texto, clave)

    def test_error_identifica_caracter_y_posicion(self):
        for modulo, clave in ((vigenere, "B"), (permutacion_series, "2 1")):
            with self.assertRaisesRegex(ValueError, "'!' en la posición 3"):
                modulo.cifrar("AB!C", clave)


class PruebasPermutacion(unittest.TestCase):
    def test_vector_conocido_y_bloques_incompletos(self):
        for texto, esperado in (("ABCDEFGHIJ", "CADBGEHFIJ"), ("ABCDEFGHIJK", "CADBGEHFKIJ"), ("AB", "AB"), ("ABC", "CAB"), ("A", "A")):
            with self.subTest(texto=texto):
                self.assertEqual(permutacion_series.cifrar(texto, "3 1 4 2"), esperado)
                self.assertEqual(permutacion_series.descifrar(esperado, "3,1,4,2"), texto)

    def test_todas_las_permutaciones_y_restos(self):
        texto = "ABCDEFGHIJK"
        for tamano in range(2, 6):
            for orden in itertools.permutations(range(1, tamano + 1)):
                clave = " ".join(map(str, orden))
                for longitud in range(1, len(texto) + 1):
                    original = texto[:longitud]
                    resultado = permutacion_series.cifrar(original, clave)
                    self.assertCountEqual(resultado, original)
                    self.assertEqual(permutacion_series.descifrar(resultado, clave), original)

    def test_minusculas_y_formatos_de_clave_equivalentes(self):
        for clave in ("3 1 4 2", "3,1,4,2", " 3, 1, 4, 2 ", "3  1,4 2"):
            with self.subTest(clave=clave):
                self.assertEqual(permutacion_series.cifrar("abcd", clave), "CADB")
                self.assertEqual(permutacion_series.descifrar("cadb", clave), "ABCD")

    def test_claves_invalidas(self):
        for clave in ("", "1", "0 1", "1 1", "2 3", "1 2 4", "a b", "1.0 2", "-1 2", "1,2,", "1,,2", "1, ,2", "1\t2", "1\n2", "١ ٢", "１ ２", "9" * 5000, None, [2, 1]):
            for funcion in (permutacion_series.cifrar, permutacion_series.descifrar):
                with self.subTest(clave=str(clave)[:30], funcion=funcion.__name__), self.assertRaises(ValueError):
                    funcion("ABCD", clave)


class PruebasConsola(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.proyecto = Path(temporal.name) / "proyecto"
        self.proyecto.mkdir()
        self.otra_carpeta = Path(temporal.name) / "otra carpeta"
        self.otra_carpeta.mkdir()
        raiz = Path(__file__).resolve().parent.parent
        for nombre in ("vigenere.py", "permutacion_series.py"):
            shutil.copyfile(raiz / nombre, self.proyecto / nombre)
        shutil.copytree(raiz / "cifrados", self.proyecto / "cifrados")

    def ejecutar(self, programa, *argumentos, entrada=None):
        return subprocess.run(
            [sys.executable, str(self.proyecto / programa), *argumentos],
            input=entrada, capture_output=True, text=True, encoding="utf-8", check=False,
            cwd=self.otra_carpeta, timeout=10,
        )

    def test_ayuda_de_cada_interfaz_explica_reglas_y_ejemplos(self):
        for programa, ejemplo in (("vigenere.py", "LXFOPVEFRNHR"), ("permutacion_series.py", "CADBGEHFIJ")):
            ayuda = self.ejecutar(programa, "--help")
            self.assertEqual(ayuda.returncode, 0, ayuda.stderr)
            self.assertIn("A-Z", ayuda.stdout)
            self.assertIn(ejemplo, ayuda.stdout)
            self.assertNotIn("--ampliado", ayuda.stdout)
            self.assertNotIn("--espanol", ayuda.stdout)

    def test_archivos_minusculas_se_normalizan_y_no_se_modifican(self):
        origen = self.proyecto / "mensaje con espacios.txt"
        origen.write_bytes(b"AttackAtDawn")
        for programa, clave, prefijo in (("vigenere.py", "lemon", "V"), ("permutacion_series.py", "3 1 4 2", "P")):
            for operacion, nombre in (("--cifrar", origen.name), ("--descifrar", f"c{prefijo}1.txt")):
                proceso = self.ejecutar(programa, operacion, "-k", clave, "-a", nombre)
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
            self.assertEqual((self.proyecto / f"d{prefijo}1.txt").read_bytes(), b"ATTACKATDAWN")
        self.assertEqual(origen.read_bytes(), b"AttackAtDawn")
        self.assertFalse(list(self.otra_carpeta.glob("*.txt")))

    def test_preprocesamiento_identico_en_argumentos_y_archivos(self):
        texto = " NiÑo ÁéíóúÜ "
        (self.proyecto / "entrada.txt").write_text(texto, encoding="utf-8")
        for programa, clave, prefijo in (("vigenere.py", "LIMÓN", "V"), ("permutacion_series.py", "3 1 4 2", "P")):
            for numero, entrada in enumerate((("-t", texto), ("-a", "entrada.txt")), start=1):
                proceso = self.ejecutar(programa, "--cifrar", "-k", clave, *entrada)
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                proceso = self.ejecutar(programa, "--descifrar", "-k", clave, "-a", f"c{prefijo}{numero}.txt")
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertEqual((self.proyecto / f"d{prefijo}{numero}.txt").read_text(), "NINOAEIOUU")
            self.assertEqual((self.proyecto / f"c{prefijo}1.txt").read_bytes(), (self.proyecto / f"c{prefijo}2.txt").read_bytes())
        self.assertEqual((self.proyecto / "entrada.txt").read_text(), texto)

    def test_argumentos_y_archivos_rechazan_texto_invalido_sin_guardar(self):
        for programa, clave in (("vigenere.py", "B"), ("permutacion_series.py", "2 1")):
            for operacion in ("--cifrar", "--descifrar"):
                for texto in ("", "   ", "123", "A!", "ABC\n", "\ufeffABC", "ß"):
                    (self.proyecto / "entrada.txt").write_text(texto, encoding="utf-8")
                    for entrada in (("-t", texto), ("-a", "entrada.txt")):
                        with self.subTest(programa=programa, operacion=operacion, texto=texto, entrada=entrada[0]):
                            proceso = self.ejecutar(programa, operacion, "-k", clave, *entrada)
                            self.assertNotEqual(proceso.returncode, 0)
                            self.assertNotIn("Traceback", proceso.stderr)
                            self.assertIn("Error:", proceso.stderr)
        self.assertFalse(list(self.proyecto.glob("[cd][VP]*.txt")))

    def test_errores_de_argumentos_y_modos_eliminados(self):
        for argumentos in (("--cifrar", "-k", "123", "-t", "Hola"), ("--cifrar", "-k", "ABC"), ("--texto", "ABC"), ("--cifrar", "--descifrar", "-k", "A", "-t", "ABC"), ("--cifrar", "--ampliado", "-k", "B", "-t", "ABC"), ("--espanol",)):
            proceso = self.ejecutar("vigenere.py", *argumentos)
            self.assertNotEqual(proceso.returncode, 0)
            self.assertNotIn("Traceback", proceso.stderr)
        self.assertFalse(list(self.proyecto.glob("[cd]V*.txt")))

    def test_resultados_numerados_independientes_sin_sobrescribir(self):
        for programa, operacion, clave, esperado, nombre in (
            ("vigenere.py", "--cifrar", "B", "BCDE", "cV1.txt"),
            ("permutacion_series.py", "--cifrar", "3 1 4 2", "CADB", "cP1.txt"),
            ("vigenere.py", "--descifrar", "B", "ZABC", "dV1.txt"),
            ("permutacion_series.py", "--descifrar", "3 1 4 2", "BDAC", "dP1.txt"),
            ("vigenere.py", "--cifrar", "C", "CDEF", "cV2.txt"),
            ("permutacion_series.py", "--cifrar", "2 1", "BADC", "cP2.txt"),
        ):
            proceso = self.ejecutar(programa, operacion, "-k", clave, "-t", "ABCD")
            self.assertEqual(proceso.returncode, 0, proceso.stderr)
            self.assertIn(str(self.proyecto / nombre), proceso.stdout)
            self.assertEqual((self.proyecto / nombre).read_text(), esperado)
        self.assertEqual((self.proyecto / "cV1.txt").read_text(), "BCDE")
        self.assertEqual((self.proyecto / "cP1.txt").read_text(), "CADB")

    def test_rechaza_rutas_fuera_del_proyecto(self):
        for nombre in ("../fuera.txt", str(self.otra_carpeta / "fuera.txt"), "carpeta/archivo.txt"):
            proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", nombre)
            self.assertNotEqual(proceso.returncode, 0)
            self.assertIn("sin carpetas ni rutas", proceso.stderr)
        (self.proyecto / "enlace.txt").symlink_to(self.otra_carpeta / "fuera.txt")
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", "enlace.txt")
        self.assertNotEqual(proceso.returncode, 0)
        self.assertFalse((self.otra_carpeta / "fuera.txt").exists())

    def test_guardado_omite_carpetas_y_enlaces_existentes(self):
        destino = self.otra_carpeta / "conservar.txt"
        destino.write_text("Conservar", encoding="utf-8")
        (self.proyecto / "cV1.txt").symlink_to(destino)
        (self.proyecto / "cV2.txt").mkdir()
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-t", "ABCD")
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertEqual((self.proyecto / "cV3.txt").read_text(), "BCDE")
        self.assertEqual(destino.read_text(), "Conservar")

if __name__ == "__main__":
    unittest.main()

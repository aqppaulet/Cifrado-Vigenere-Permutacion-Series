"""Casos límite reproducibles; los archivos de prueba se crean solo en temporales."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import errno
import io
import os
from pathlib import Path
import random
import shutil
import string
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from cifrados import interfaz
import permutacion_series
import vigenere


class PruebasAleatorias(unittest.TestCase):
    def test_500_mensajes_ingleses_y_claves(self):
        azar = random.Random(20261023)
        for caso in range(500):
            texto = "".join(azar.choice(string.ascii_letters) for _ in range(azar.randrange(1, 257)))
            clave = "".join(azar.choice(string.ascii_letters) for _ in range(azar.randrange(1, 41)))
            with self.subTest(caso=caso, modo="vigenere"):
                cifrado = vigenere.cifrar(texto, clave)
                self.assertTrue(set(cifrado) <= set(string.ascii_uppercase))
                self.assertEqual(len(cifrado), len(texto))
                self.assertEqual(vigenere.descifrar(cifrado, clave), texto.upper())
            orden = list(range(1, azar.randrange(2, 65) + 1))
            azar.shuffle(orden)
            clave = ", ".join(map(str, orden))
            with self.subTest(caso=caso, modo="permutacion"):
                cifrado = permutacion_series.cifrar(texto, clave)
                self.assertCountEqual(cifrado, texto.upper())
                self.assertEqual(permutacion_series.descifrar(cifrado, clave), texto.upper())

    def test_mensaje_grande_en_ambos_algoritmos(self):
        texto = "AaZz" * 250000
        for modulo, clave in ((vigenere, "Clave"), (permutacion_series, "7 1 6 2 5 3 4")):
            with self.subTest(modulo=modulo.__name__):
                cifrado = modulo.cifrar(texto, clave)
                self.assertEqual(modulo.descifrar(cifrado, clave), texto.upper())

    def test_permutacion_clave_mayor_que_el_texto(self):
        clave = " ".join(map(str, range(100, 0, -1)))
        self.assertEqual(permutacion_series.cifrar("ABC", clave), "CBA")
        self.assertEqual(permutacion_series.descifrar("CBA", clave), "ABC")


class PruebasArchivosYConsola(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.proyecto = Path(temporal.name) / "proyecto"
        self.proyecto.mkdir()
        self.otra_carpeta = Path(temporal.name) / "otra"
        self.otra_carpeta.mkdir()
        raiz = Path(__file__).resolve().parent.parent
        for nombre in ("vigenere.py", "permutacion_series.py"):
            shutil.copyfile(raiz / nombre, self.proyecto / nombre)
        shutil.copytree(raiz / "cifrados", self.proyecto / "cifrados")

    def ejecutar(self, programa="vigenere.py", *argumentos, entrada=None, timeout=10):
        return subprocess.run(
            [sys.executable, str(self.proyecto / programa), *argumentos],
            input=entrada, text=True, encoding="utf-8", capture_output=True,
            cwd=self.otra_carpeta, timeout=timeout, check=False,
        )

    @unittest.skipUnless(hasattr(os, "mkfifo"), "El sistema no tiene tuberías con nombre")
    def test_tuberias_se_rechazan_sin_bloquear(self):
        os.mkfifo(self.proyecto / "tuberia.txt")
        for programa, clave in (("vigenere.py", "B"), ("permutacion_series.py", "2 1")):
            with self.subTest(programa=programa):
                proceso = self.ejecutar(programa, "--cifrar", "-k", clave, "-a", "tuberia.txt", timeout=2)
                self.assertNotEqual(proceso.returncode, 0)
                self.assertNotIn("Traceback", proceso.stderr)
                self.assertIn("archivo", proceso.stderr.lower())

    def test_archivo_inexistente_carpeta_y_enlace_circular(self):
        (self.proyecto / "carpeta.txt").mkdir()
        (self.proyecto / "enlace1.txt").symlink_to("enlace2.txt")
        (self.proyecto / "enlace2.txt").symlink_to("enlace1.txt")
        for nombre in ("inexistente.txt", "carpeta.txt", "enlace1.txt"):
            proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", nombre)
            self.assertNotEqual(proceso.returncode, 0)
            self.assertNotIn("Traceback", proceso.stderr)
        self.assertFalse(list(self.proyecto.glob("cV*.txt")))

    def test_archivo_no_utf8_muestra_mensaje_claro(self):
        (self.proyecto / "invalido.txt").write_bytes(b"\xff\xfe\x00\x80")
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", "invalido.txt")
        self.assertNotEqual(proceso.returncode, 0)
        self.assertNotIn("Traceback", proceso.stderr)
        self.assertIn("UTF-8", proceso.stderr)
        self.assertFalse((self.proyecto / "cV1.txt").exists())

    def test_una_linea_enorme_tiene_vista_previa_acotada(self):
        (self.proyecto / "grande.txt").write_text("A" * 20000, encoding="utf-8")
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-a", "grande.txt")
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertLess(len(proceso.stdout), 2000)
        self.assertIn("Vista previa truncada", proceso.stdout)
        self.assertEqual((self.proyecto / "cV1.txt").read_text(), "B" * 20000)

    def test_doce_ejecuciones_simultaneas_no_sobrescriben(self):
        (self.proyecto / "cV1.txt").write_text("Conservar", encoding="utf-8")

        def cifrar(indice):
            texto = "MENSAJE" + string.ascii_uppercase[indice] + "AaZz"
            return texto, self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-t", texto)

        with ThreadPoolExecutor(max_workers=6) as grupo:
            resultados = list(grupo.map(cifrar, range(12)))
        for _, proceso in resultados:
            self.assertEqual(proceso.returncode, 0, proceso.stderr)
        esperados = {vigenere.cifrar(texto, "B") for texto, _ in resultados}
        reales = {(self.proyecto / f"cV{numero}.txt").read_text() for numero in range(2, 14)}
        self.assertEqual(reales, esperados)
        self.assertEqual((self.proyecto / "cV1.txt").read_text(), "Conservar")
        self.assertFalse(list(self.otra_carpeta.glob("*.txt")))

    def test_huecos_numeracion_y_series_independientes(self):
        for nombre in ("cV1.txt", "cV3.txt", "dV1.txt", "cP1.txt", "dP1.txt"):
            (self.proyecto / nombre).write_text("Conservar", encoding="utf-8")
        proceso = self.ejecutar("vigenere.py", "--cifrar", "-k", "B", "-t", "ABCD")
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertEqual((self.proyecto / "cV2.txt").read_text(), "BCDE")
        for nombre in ("cV1.txt", "cV3.txt", "dV1.txt", "cP1.txt", "dP1.txt"):
            self.assertEqual((self.proyecto / nombre).read_text(), "Conservar")

class PruebasEscrituraFallida(unittest.TestCase):
    def test_fallo_de_escritura_elimina_solo_el_resultado_parcial(self):
        for error in (OSError(errno.ENOSPC, "Sin espacio disponible"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as carpeta:
                proyecto = Path(carpeta)
                existente = proyecto / "cV1.txt"
                existente.write_text("Conservar", encoding="utf-8")
                abrir_original = Path.open

                def abrir_con_fallo(ruta, *argumentos, **opciones):
                    archivo = abrir_original(ruta, *argumentos, **opciones)

                    class Escritor:
                        def __enter__(self):
                            return self

                        def __exit__(self, *_):
                            archivo.close()

                        def write(self, texto):
                            archivo.write(texto[:3])
                            archivo.flush()
                            raise error

                    return Escritor()

                with patch.object(interfaz, "CARPETA_PROYECTO", proyecto), patch.object(Path, "open", abrir_con_fallo):
                    with self.assertRaises(type(error)), redirect_stdout(io.StringIO()):
                        interfaz._guardar_resultado("Texto completo", "cV")
                self.assertFalse((proyecto / "cV2.txt").exists())
                self.assertEqual(existente.read_text(), "Conservar")

    def test_sin_permiso_no_crea_archivos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with patch.object(interfaz, "CARPETA_PROYECTO", Path(carpeta)), patch.object(Path, "open", side_effect=PermissionError("Sin permiso")):
                with self.assertRaises(PermissionError):
                    interfaz._guardar_resultado("Texto", "cV")
            self.assertFalse(list(Path(carpeta).iterdir()))


class PruebasLimitaciones(unittest.TestCase):
    """Los formatos válidos no garantizan la clave correcta ni la integridad."""

    def test_clave_equivocada_puede_producir_texto_valido(self):
        cifrado = vigenere.cifrar("HOLA", "B")
        self.assertEqual(vigenere.descifrar(cifrado, "C"), "GNKZ")
        cifrado = permutacion_series.cifrar("ABCD", "2 1")
        self.assertEqual(permutacion_series.descifrar(cifrado, "1 2"), "BADC")

    def test_recorte_de_letras_puede_pasar_desapercibido(self):
        cifrado = vigenere.cifrar("HOLAMUNDO", "B")
        self.assertEqual(vigenere.descifrar(cifrado[:3], "B"), "HOL")


if __name__ == "__main__":
    unittest.main()

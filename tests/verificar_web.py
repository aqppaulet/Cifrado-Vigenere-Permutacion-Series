"""Prueba JavaScript y formularios en Firefox real, sin paquetes de Python extra.

Ejecutar: python3 tests/verificar_web.py
Requiere Firefox. Usa un perfil temporal y un servidor accesible solo en localhost.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import threading

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from cifrados import permutacion, vigenere
from cifrados.validacion import normalizar_letras


def fixtures():
    azar = random.Random(20261023)
    casos = [
        ("vigenere", "ATTACKATDAWN", "LEMON"),
        ("vigenere", "NiñoÁgil", "LIMÓN"),
        ("vigenere", " Niño Ágil ", "LIMÓN"),
        ("permutacion", "ABCDEFGHIJK", "3 1 4 2"),
        ("permutacion", " ABCD EFGH IJK ", "3 1 4 2"),
        ("permutacion", " A0B1C2D3 E4F5G6H7 I8J9K ", "3 1 4 2"),
    ]
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúüñÁÉÍÓÚÜÑ"
    for _ in range(100):
        texto = "".join(azar.choice(letras) for _ in range(azar.randrange(1, 301)))
        clave = "".join(azar.choice(letras) for _ in range(azar.randrange(1, 31)))
        casos.append(("vigenere", texto, clave))
        posiciones = list(range(1, azar.randrange(3, 22)))
        azar.shuffle(posiciones)
        casos.append(("permutacion", texto + "0123456789", ", ".join(map(str, posiciones))))
    return [dict(algoritmo=nombre, texto=texto, clave=clave,
                 normalizado=(permutacion.preparar_texto(texto) if nombre == "permutacion"
                              else normalizar_letras(texto, eliminar_espacios=True)),
                 cifrado=(vigenere if nombre == "vigenere" else permutacion).cifrar(texto, clave))
            for nombre, texto, clave in casos]


def main():
    firefox = shutil.which("firefox")
    if not firefox:
        raise SystemExit("Se necesita Firefox para ejecutar las pruebas web.")
    terminado = threading.Event()
    resultado = {}
    vectores = json.dumps(fixtures(), ensure_ascii=False).encode("utf-8")

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            if self.path == "/__fixtures__":
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(vectores)))
                self.end_headers()
                self.wfile.write(vectores)
                return
            # La subruta comprueba enlaces compatibles con un sitio de proyecto.
            if not self.path.startswith(("/laboratorio/docs/", "/laboratorio/tests/web/")):
                self.send_error(404)
                return
            self.path = self.path.removeprefix("/laboratorio")
            super().do_GET()

        def do_POST(self):
            if self.path != "/__resultados__":
                self.send_error(404)
                return
            resultado.update(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            self.send_response(200)
            self.end_headers()
            terminado.set()

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=RAIZ))
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    try:
        with tempfile.TemporaryDirectory(prefix="cifrados-firefox-") as temporal:
            perfil = Path(temporal) / "perfil"
            perfil.mkdir()
            registro = Path(temporal) / "firefox.log"
            url = f"http://127.0.0.1:{servidor.server_port}/laboratorio/tests/web/index.html"
            entorno = dict(os.environ, MOZ_CRASHREPORTER_DISABLE="1")
            with registro.open("w") as salida:
                proceso = subprocess.Popen([firefox, "--headless", "--no-remote", "--profile", str(perfil), url],
                                           stdout=salida, stderr=subprocess.STDOUT, env=entorno)
                try:
                    if not terminado.wait(45):
                        raise RuntimeError("Firefox no terminó las pruebas. " + registro.read_text()[-2000:])
                finally:
                    proceso.terminate()
                    try:
                        proceso.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proceso.kill()
                        proceso.wait()
    finally:
        servidor.shutdown()
        servidor.server_close()
    for prueba in resultado["pruebas"]:
        print(("OK" if prueba["ok"] else "FALLO") + " " + prueba["nombre"])
        if not prueba["ok"]:
            print(prueba.get("error", ""))
    print(f"{sum(p['ok'] for p in resultado['pruebas'])}/{len(resultado['pruebas'])} pruebas web aprobadas.")
    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

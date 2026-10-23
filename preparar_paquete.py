"""Crea un ZIP de distribución con archivos explícitos y sin datos personales."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


RAIZ = Path(__file__).resolve().parent


def main() -> None:
    archivos = [
        RAIZ / nombre for nombre in (
            "README.md", "LIMITACIONES_DESCIFRADO.md", "INFORME_PRUEBAS.md",
            "Vigenere.pyw", "Permutacion.pyw", "vigenere.py",
            "permutacion_series.py", "preparar_paquete.py",
            "PUBLICAR_WEB.md", "tests/verificar_web.py",
        )
    ]
    archivos += sorted((RAIZ / "cifrados").glob("*.py"))
    archivos += sorted((RAIZ / "tests").glob("test_*.py"))
    archivos += sorted((RAIZ / "ejemplos").glob("*.txt"))
    archivos_web = sorted(p for p in (RAIZ / "docs").rglob("*") if p.is_file())
    archivos += archivos_web
    archivos += sorted(p for p in (RAIZ / "tests" / "web").rglob("*") if p.is_file())
    destino = RAIZ / "Cifrados_AZ.zip"
    with ZipFile(destino, "w", compression=ZIP_DEFLATED) as paquete:
        for archivo in archivos:
            paquete.write(archivo, Path("Cifrados_AZ") / archivo.relative_to(RAIZ))
    print(f"Paquete listo: {destino} ({destino.stat().st_size / 1024:.1f} KB)")
    destino_web = RAIZ / "Cifrados_Web.zip"
    with ZipFile(destino_web, "w", compression=ZIP_DEFLATED) as paquete:
        for archivo in archivos_web:
            paquete.write(archivo, archivo.relative_to(RAIZ / "docs"))
    print(f"Web lista: {destino_web} ({destino_web.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

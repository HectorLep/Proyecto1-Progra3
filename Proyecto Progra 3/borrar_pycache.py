import os
import shutil

def borrar_pycache(directorio_base):
    contador = 0
    for carpeta_actual, subcarpetas, archivos in os.walk(directorio_base):
        for subcarpeta in subcarpetas:
            if subcarpeta == "__pycache__":
                ruta_pycache = os.path.join(carpeta_actual, subcarpeta)
                try:
                    shutil.rmtree(ruta_pycache)
                    print(f"Eliminado: {ruta_pycache}")
                    contador += 1
                except Exception as e:
                    print(f"Error eliminando {ruta_pycache}: {e}")
    print(f"\nTotal de carpetas '__pycache__' eliminadas: {contador}")

if __name__ == "__main__":
    ruta = os.path.dirname(os.path.abspath(__file__))  # carpeta actual
    borrar_pycache(ruta)

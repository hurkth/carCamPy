#!/usr/bin/env python3
import sys
from cameras.camera import Camera, MainLensCamera, FisheyeCamera, InfraredCamera, list_available_cameras
from recognition import FaceRecognizer
from config import CameraConfig


def main():
    print("=== CarVidPY - Face Recognition ===\n")
    
    print("Buscando camaras...")
    devices = list_available_cameras()
    for dev in devices:
        print(f"  {dev}")
    print()
    
    if not devices:
        print("No se encontro camara. Verifica la conexion.")
        sys.exit(1)
    
    print("Selecciona lente:")
    print("  [1] Principal")
    print("  [2] Ojo de pez")
    print("  [3] Infrarrojo")
    
    choice = input("\nOpcion (1-3): ").strip()
    
    lens_map = {"1": MainLensCamera, "2": FisheyeCamera, "3": InfraredCamera}
    camera_class = lens_map.get(choice, MainLensCamera)
    
    print("\nIniciando camara...")
    cam = camera_class(CameraConfig(width=640, height=480), device=0)
    cam.start()
    print("OK")
    
    recognizer = FaceRecognizer(tolerance=0.6)
    known = len(set(name for name, _ in recognizer.known_faces))
    print(f"Rostros conocidos: {known} personas\n")
    
    print("Iniciando interfaz grafica...")
    
    from gui import App
    app = App(cam, recognizer)
    app.run()
    
    print("Listo.")


if __name__ == "__main__":
    main()

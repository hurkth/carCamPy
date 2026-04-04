#!/usr/bin/env python3
import os
import sys
from cameras.camera import Camera, MainLensCamera, FisheyeCamera, InfraredCamera, list_available_cameras
from recognition import FaceRecognizer
from config import CameraConfig


def main():
    print("=== CarVidPY - Face Recognition ===\n")
    
    has_display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    
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
    
    if has_display:
        print("Iniciando interfaz grafica...")
        from gui import App
        app = App(cam, recognizer)
        app.run()
    else:
        print("Sin display disponible. Modo CLI.")
        print("Controles: [r] Registrar rostro | [q] Salir")
        import cv2
        while True:
            frame = cam.read()
            if frame is not None:
                results = recognizer.recognize(frame)
                frame = recognizer.draw_results(frame, results)
                cv2.imshow("CarVidPY", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                if frame is not None:
                    name = input("Nombre: ").strip()
                    if name:
                        if recognizer.register_face(frame, name):
                            print(f"OK - '{name}' registrado!")
        cv2.destroyAllWindows()
    
    cam.stop()
    print("Listo.")


if __name__ == "__main__":
    main()

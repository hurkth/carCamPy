#!/usr/bin/env python3
import cv2
import sys
from cameras.camera import Camera, MainLensCamera, FisheyeCamera, InfraredCamera, list_available_cameras
from recognition import FaceRecognizer
from config import CameraConfig


def main():
    print("=== CarVidPY - Face Recognition ===\n")
    
    print("Buscando camaras...")
    devices = list_available_cameras()
    for dev in devices:
        print(f"  - {dev}")
    print()
    
    if not devices:
        print("No se encontro camara. Verifica la conexion.")
        sys.exit(1)
    
    print("Selecciona lente:")
    print("  [1] Principal")
    print("  [2] Ojo de pez")
    print("  [3] Infrarrojo")
    
    choice = input("\nOpcion (1-3): ").strip()
    
    lens_map = {"1": ("Principal", MainLensCamera), "2": ("Ojo de pez", FisheyeCamera), "3": ("Infrarrojo", InfraredCamera)}
    
    if choice not in lens_map:
        print("Invalido, usando Principal.")
        choice = "1"
    
    name, camera_class = lens_map[choice]
    print(f"\nIniciando {name}...")
    
    try:
        cam = camera_class(CameraConfig(width=640, height=480), device=0)
        cam.start()
        print("OK")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    recognizer = FaceRecognizer(tolerance=0.6)
    known = len(set(name for name, _ in recognizer.known_faces))
    print(f"Rostros conocidos: {known} personas\n")
    
    print("Controles: [r] Registrar | [q] Salir")
    print("-" * 40)
    
    register_mode = False
    
    while True:
        frame = cam.read()
        if frame is not None:
            cv2.imshow("CarVidPY", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            if frame is not None:
                if recognizer.register_face(frame, ""):
                    pass
                else:
                    print("Sin rostro detectado")
    
    cam.stop()
    cv2.destroyAllWindows()
    print("Listo.")


if __name__ == "__main__":
    main()

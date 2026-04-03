#!/usr/bin/env python3
import cv2
import sys
import time
from cameras.camera import Camera, list_available_cameras
from cameras.main_lens import MainLensCamera
from cameras.fisheye import FisheyeCamera
from cameras.infrared import InfraredCamera
from recognition import FaceRecognizer
from config import CameraConfig


def main():
    print("=== CarVidPY - Face Recognition System ===\n")
    print("Dispositivos disponibles:")
    for dev in list_available_cameras():
        print(f"  - {dev}")
    print()
    
    cameras = {}
    
    print("Selecciona lente a usar:")
    print("  [1] Principal (dia)")
    print("  [2] Ojo de pez (360)")
    print("  [3] Infrarrojo (noche)")
    
    choice = input("\nOpcion (1-3): ").strip()
    
    lens_map = {"1": ("main", MainLensCamera), "2": ("fisheye", FisheyeCamera), "3": ("infrared", InfraredCamera)}
    
    if choice not in lens_map:
        print("Opcion invalida, usando lente principal.")
        choice = "1"
    
    name, camera_class = lens_map[choice]
    print(f"\nIniciando camara {name}...")
    
    try:
        cam = camera_class(CameraConfig(width=640, height=480))
        cam.start()
        cameras[name] = cam
        print("OK")
    except Exception as e:
        print(f"Error: {e}")
        print("Intentando modo genérico...")
        cam = Camera("unicam", CameraConfig(width=640, height=480))
        cam.start()
        cameras["camera"] = cam
        name = "camera"
    
    selected_cam = name
    cam = cameras[selected_cam]
    
    recognizer = FaceRecognizer(tolerance=0.5)
    known_count = len(set(recognizer.known_names))
    print(f"\nRostros conocidos cargados: {known_count} personas")
    
    print("\nControles:")
    print("  [r] Registrar rostro (captura actual)")
    print("  [q] Salir")
    print("-" * 40)
    
    register_mode = False
    
    while True:
        frame = cam.read()
        if frame is not None:
            if register_mode:
                results = recognizer.recognize(frame)
                frame = recognizer.draw_results(frame, results)
            
            cv2.imshow("CarVidPY", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            register_mode = not register_mode
            print(f"Modo registro: {'ON' if register_mode else 'OFF'}")
            if register_mode and frame is not None:
                results = recognizer.recognize(frame)
                if results:
                    name = input("Nombre: ").strip()
                    if name and recognizer.register_face(frame, name):
                        print(f"OK - '{name}' registrado!")
                        register_mode = False
                else:
                    print("Sin rostro detectado")
    
    cam.stop()
    cv2.destroyAllWindows()
    print("Sistema detenido.")


if __name__ == "__main__":
    main()

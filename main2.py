import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import subprocess

# Configuración de pines para el cambio de cámara (Modo Físico/BOARD)
# Ajusta estos números si tu manual indica otros pines
PINS_SELECCION = [7, 11, 12]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in PINS_SELECCION:
    GPIO.setup(pin, GPIO.OUT)

def activar_lente(indice):
    """Cambia los estados de los pines para seleccionar una de las 3 lentes"""
    if indice == 0: # Lente Central
        GPIO.output(7, False); GPIO.output(11, False); GPIO.output(12, True)
    elif indice == 1: # Lente Lateral 1
        GPIO.output(7, True); GPIO.output(11, False); GPIO.output(12, True)
    elif indice == 2: # Lente Lateral 2 (Ojo de Pez)
        GPIO.output(7, False); GPIO.output(11, True); GPIO.output(12, False)
    # Pausa crítica: El hardware necesita un momento para conmutar la señal
    time.sleep(0.1)

# Abrimos la captura usando el backend V4L2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Usamos una resolución moderada para que el mosaico sea fluido
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Proyecto carCamPy: Iniciando 3 lentes en cable 206224...")
print("Presiona 'q' para salir.")

try:
    while True:
        vistas = []
        
        for i in range(3):
            activar_lente(i)
            
            # Limpiar el buffer: descartamos los primeros frames porque 
            # suelen contener "sobras" de la cámara anterior
            for _ in range(2):
                cap.grab()
            
            ret, frame = cap.read()
            if ret:
                # Redimensionar para el mosaico (400x300)
                frame_res = cv2.resize(frame, (400, 300))
                # Etiquetado básico
                label = f"Lente {i+1}" if i < 2 else "Ojo de Pez"
                cv2.putText(frame_res, label, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                vistas.append(frame_res)
            else:
                vistas.append(np.zeros((300, 400, 3), np.uint8))

        # Crear mosaico [1 y 2 arriba, 3 y negro abajo]
        negro = np.zeros((300, 400, 3), np.uint8)
        superior = np.hstack((vistas[0], vistas[1]))
        inferior = np.hstack((vistas[2], negro))
        mosaico_final = np.vstack((superior, inferior))

        cv2.imshow("Monitor carCamPy - RPi 4B", mosaico_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
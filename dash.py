import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import time

# Configuración del tema de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class E36Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("E36 OS - Sistema de Visión")
        self.geometry("1024x600")

        # --- GRID PRINCIPAL ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR (Reloj y Voltaje) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="E36 OS", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.clock_label = ctk.CTkLabel(self.sidebar_frame, text="00:00", font=ctk.CTkFont(size=40))
        self.clock_label.grid(row=1, column=0, padx=20, pady=10)

        self.voltage_label = ctk.CTkLabel(self.sidebar_frame, text="⚡ 13.8V", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00FF00")
        self.voltage_label.grid(row=2, column=0, padx=20, pady=10)

        # --- ÁREA CENTRAL (Solo Cámara) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1) 
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Etiqueta donde irá el video
        self.camera_label = ctk.CTkLabel(self.main_frame, text="Iniciando cámara...", font=ctk.CTkFont(size=18))
        self.camera_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # --- INICIALIZACIÓN DE CÁMARA ---
        # Cambia este 0 por 1 o 2 si estás apuntando a la cámara equivocada del set
        self.camera_index = 0
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Detector de rostros de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Arrancar bucles
        self.update_clock()
        self.update_camera()

    def update_clock(self):
        current_time = time.strftime("%H:%M")
        self.clock_label.configure(text=current_time)
        self.after(1000, self.update_clock)

    def update_camera(self):
        ret, frame = self.cap.read()
        
        if ret:
            # Procesamiento de imagen: Voltear y convertir color
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detección de rostros
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(rgb_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Convertir para CustomTkinter
            img = Image.fromarray(rgb_frame)
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            
            # Borrar el texto de error y poner la imagen
            self.camera_label.configure(image=imgtk, text="")
            self.camera_label.image = imgtk
        else:
            # Si el código llega aquí, OpenCV no está recibiendo cuadros del hardware
            self.camera_label.configure(text=f"Error: No se recibe video en índice {self.camera_index}")
        
        # Refrescar a ~30 fps
        self.after(30, self.update_camera)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = E36Dashboard()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
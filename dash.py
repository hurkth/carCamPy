import customtkinter as ctk
from PIL import Image
import time
# Importamos el motor nativo en lugar de cv2
from picamera2 import Picamera2

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class E36Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("E36 OS - Sistema de Visión")
        self.geometry("1024x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="E36 OS", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.clock_label = ctk.CTkLabel(self.sidebar_frame, text="00:00", font=ctk.CTkFont(size=40))
        self.clock_label.grid(row=1, column=0, padx=20, pady=10)

        # --- ÁREA CENTRAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1) 
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(self.main_frame, text="Iniciando motor óptico...", font=ctk.CTkFont(size=18))
        self.camera_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # --- INICIALIZACIÓN DE CÁMARA (NATIVA) ---
        try:
            self.picam2 = Picamera2()
            # Configuramos la resolución directamente en el hardware
            config = self.picam2.create_preview_configuration(main={"size": (640, 480)})
            self.picam2.configure(config)
            self.picam2.start()
        except Exception as e:
            self.camera_label.configure(text=f"Fallo de hardware: {e}")

        self.update_clock()
        self.update_camera()

    def update_clock(self):
        current_time = time.strftime("%H:%M")
        self.clock_label.configure(text=current_time)
        self.after(1000, self.update_clock)

    def update_camera(self):
        try:
            # Picamera2 entrega la imagen ya procesada en RGB, lista para usar
            rgb_frame = self.picam2.capture_array()

            # La pasamos a CustomTkinter
            img = Image.fromarray(rgb_frame)
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            
            self.camera_label.configure(image=imgtk, text="")
            self.camera_label.image = imgtk
        except Exception as e:
            pass # Ignorar cuadros vacíos si el sensor parpadea
        
        self.after(30, self.update_camera)

    def on_closing(self):
        try:
            self.picam2.stop()
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = E36Dashboard()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
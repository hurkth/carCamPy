import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import requests
import threading
import time

# Configuración del tema de la interfaz (Estilo E36: Oscuro con acentos azules)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class E36Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("E36 OS - Sistema Central")
        self.geometry("1024x600")
        # self.attributes('-fullscreen', True) # Descomenta esto para la pantalla táctil final

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

        # --- ÁREA CENTRAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=3) # Espacio para cámara
        self.main_frame.grid_rowconfigure(1, weight=2) # Espacio para chat
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 1. Módulo de Cámara (Arriba)
        self.camera_label = ctk.CTkLabel(self.main_frame, text="")
        self.camera_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # 2. Módulo de Chat de IA (Abajo)
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.textbox_chat = ctk.CTkTextbox(self.chat_frame, state="disabled", font=ctk.CTkFont(size=14))
        self.textbox_chat.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.entry_chat = ctk.CTkEntry(self.chat_frame, placeholder_text="Habla con la Compañera...")
        self.entry_chat.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.entry_chat.bind("<Return>", self.send_message) # Permite enviar con Enter

        self.btn_send = ctk.CTkButton(self.chat_frame, text="Enviar", width=80, command=self.send_message)
        self.btn_send.grid(row=1, column=1, padx=(5, 10), pady=10)

        # --- INICIALIZACIÓN DE CÁMARA (V4L2 y MJPG para Pi 4B en 64-bit) ---
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Detector de rostros de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Arrancar bucles
        self.update_clock()
        self.update_camera()

        # Mensaje inicial del sistema
        self.insert_chat("Sistema", "E36 OS Iniciado. Motores en línea. IA conectada.")

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
            
            self.camera_label.configure(image=imgtk)
            self.camera_label.image = imgtk
        
        # Refrescar a ~30 fps
        self.after(30, self.update_camera)

    def insert_chat(self, sender, message):
        self.textbox_chat.configure(state="normal")
        self.textbox_chat.insert("end", f"{sender}: {message}\n\n")
        self.textbox_chat.see("end")
        self.textbox_chat.configure(state="disabled")

    def send_message(self, event=None):
        user_text = self.entry_chat.get().strip()
        if not user_text: return
        
        # Mostrar el mensaje del usuario
        self.insert_chat("Kevin", user_text)
        self.entry_chat.delete(0, "end")

        # Iniciar hilo para no congelar la cámara
        threading.Thread(target=self.ask_ollama, args=(user_text,), daemon=True).start()

    def ask_ollama(self, prompt):
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "e36_companion",
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            reply = data.get("response", "Error de red neuronal.")
            
            # Usar .after para actualizar la interfaz desde el hilo secundario
            self.after(0, self.insert_chat, "Compañera", reply)
            
        except requests.exceptions.RequestException:
            self.after(0, self.insert_chat, "Sistema", "Sistemas de IA fuera de línea. Revisa Ollama.")

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = E36Dashboard()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
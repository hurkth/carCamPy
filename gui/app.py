import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
import threading
from PIL import Image, ImageTk
from pathlib import Path
from typing import Optional, List, Tuple
from config import KNOWN_FACES_DIR


class App:
    def __init__(self, camera, recognizer):
        self.camera = camera
        self.recognizer = recognizer
        
        self.root = tk.Tk()
        self.root.title("CarVidPY - Face Recognition")
        self.root.geometry("900x600")
        self.root.configure(bg="#1a1a2e")
        
        self.running = True
        self.frame: Optional[cv2.Mat] = None
        self.current_lens = 0
        self.lens_names = ["Principal", "Ojo de pez", "Infrarrojo"]
        self.known_faces_list = []
        
        self._load_known_faces()
        self._setup_ui()
        self._start_video_thread()
        
    def _setup_ui(self):
        title = tk.Label(
            self.root, text="CarVidPY", 
            font=("Arial", 24, "bold"), 
            bg="#1a1a2e", fg="#00d9ff"
        )
        title.pack(pady=10)
        
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.video_label = tk.Label(main_frame, bg="#16213e", width=640, height=480)
        self.video_label.pack(side=tk.LEFT, padx=5)
        
        control_panel = tk.Frame(main_frame, bg="#16213e", width=220)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        control_panel.pack_propagate(False)
        
        lens_label = tk.Label(
            control_panel, text="LENTE", 
            font=("Arial", 10, "bold"), 
            bg="#16213e", fg="#00d9ff"
        )
        lens_label.pack(pady=(10, 5))
        
        self.lens_buttons = []
        for i, name in enumerate(self.lens_names):
            btn = tk.Button(
                control_panel, text=name,
                font=("Arial", 10),
                bg="#0f3460", fg="white",
                activebackground="#00d9ff",
                command=lambda idx=i: self._change_lens(idx)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.lens_buttons.append(btn)
        self.lens_buttons[0].config(bg="#00d9ff", fg="black")
        
        sep = tk.Frame(control_panel, height=2, bg="#00d9ff")
        sep.pack(fill=tk.X, padx=10, pady=15)
        
        reg_label = tk.Label(
            control_panel, text="REGISTRAR", 
            font=("Arial", 10, "bold"), 
            bg="#16213e", fg="#00d9ff"
        )
        reg_label.pack(pady=(0, 5))
        
        self.register_btn = tk.Button(
            control_panel, text="Capturar Rostro",
            font=("Arial", 12, "bold"),
            bg="#e94560", fg="white",
            activebackground="#ff6b6b",
            command=self._register_face
        )
        self.register_btn.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            control_panel, text="", 
            font=("Arial", 9), 
            bg="#16213e", fg="#00ff00"
        )
        self.status_label.pack(pady=5)
        
        sep2 = tk.Frame(control_panel, height=2, bg="#00d9ff")
        sep2.pack(fill=tk.X, padx=10, pady=15)
        
        known_label = tk.Label(
            control_panel, text=f"CONOCIDOS ({len(self.known_faces_list)})", 
            font=("Arial", 10, "bold"), 
            bg="#16213e", fg="#00d9ff"
        )
        known_label.pack(pady=(0, 5))
        
        list_frame = tk.Frame(control_panel, bg="#0f3460")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.known_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            bg="#0f3460", fg="white",
            font=("Arial", 9),
            selectbackground="#00d9ff"
        )
        self.known_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.known_listbox.yview)
        
        sep3 = tk.Frame(control_panel, height=2, bg="#00d9ff")
        sep3.pack(fill=tk.X, padx=10, pady=15)
        
        quit_btn = tk.Button(
            control_panel, text="SALIR",
            font=("Arial", 10, "bold"),
            bg="#333", fg="white",
            command=self._quit
        )
        quit_btn.pack(fill=tk.X, padx=10, pady=10)
        
    def _load_known_faces(self):
        self.known_faces_list = []
        if KNOWN_FACES_DIR.exists():
            for person_dir in KNOWN_FACES_DIR.iterdir():
                if person_dir.is_dir():
                    self.known_faces_list.append(person_dir.name)
        self._update_known_list()
        
    def _update_known_list(self):
        self.known_listbox.delete(0, tk.END)
        for name in sorted(set(self.known_faces_list)):
            self.known_listbox.insert(tk.END, name)
            
    def _change_lens(self, idx):
        self.current_lens = idx
        for i, btn in enumerate(self.lens_buttons):
            if i == idx:
                btn.config(bg="#00d9ff", fg="black")
            else:
                btn.config(bg="#0f3460", fg="white")
        self.status_label.config(text=f"Lente: {self.lens_names[idx]}")
        
    def _register_face(self):
        if self.frame is None:
            messagebox.showwarning("Error", "Sin frame disponible")
            return
            
        results = self.recognizer.recognize(self.frame)
        if not results:
            messagebox.showwarning("Sin rostro", "No se detectó ningún rostro")
            return
            
        name = simpledialog.askstring("Registrar", "Nombre de la persona:")
        if name and name.strip():
            if self.recognizer.register_face(self.frame, name.strip()):
                self.known_faces_list.append(name.strip())
                self._update_known_list()
                messagebox.showinfo("OK", f"Rostro de '{name.strip()}' registrado!")
            else:
                messagebox.showerror("Error", "No se pudo registrar")
                
    def _start_video_thread(self):
        self.thread = threading.Thread(target=self._video_loop, daemon=True)
        self.thread.start()
        self._update_frame()
        
    def _video_loop(self):
        while self.running:
            frame = self.camera.read()
            if frame is not None:
                self.frame = frame.copy()
                results = self.recognizer.recognize(frame)
                for name, box in results:
                    top, right, bottom, left = box
                    color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.putText(frame, name, (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                self.frame = frame
                
    def _update_frame(self):
        if self.frame is not None:
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480))
            photo = ImageTk.PhotoImage(img)
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
        if self.running:
            self.root.after(30, self._update_frame)
            
    def _quit(self):
        self.running = False
        self.camera.stop()
        self.root.quit()
        
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.mainloop()

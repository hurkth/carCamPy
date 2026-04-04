import customtkinter as ctk

# 1. Configuración global (El tema oscuro le va perfecto al interior de un auto)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 2. Inicializar la ventana principal
app = ctk.CTk()
app.geometry("800x480") # La resolución exacta de tu pantalla táctil
app.title("BMW E36 - Carputer")
app.attributes('-fullscreen', True) # Opcional: Descomenta esto para pantalla completa real

# 3. Estructurar la interfaz (El equivalente a tus contenedores div)
# Creamos un marco lateral para los botones
sidebar_frame = ctk.CTkFrame(app, width=200, corner_radius=0)
sidebar_frame.pack(side="left", fill="y")

logo_label = ctk.CTkLabel(sidebar_frame, text="E36 OS", font=ctk.CTkFont(size=20, weight="bold"))
logo_label.pack(padx=20, pady=(20, 10))

# 4. Funciones de los botones (Tus Event Listeners)
def encender_camara():
    print("Iniciando módulo de cámara infrarroja y reconocimiento facial...")
    # Aquí irá el código de OpenCV más adelante

# 5. Instanciar los botones
btn_camara = ctk.CTkButton(sidebar_frame, text="Cámara Trasera", command=encender_camara)
btn_camara.pack(padx=20, pady=10)

btn_musica = ctk.CTkButton(sidebar_frame, text="Reproductor")
btn_musica.pack(padx=20, pady=10)

btn_salir = ctk.CTkButton(sidebar_frame, text="Apagar Pantalla", fg_color="red", hover_color="#aa0000", command=app.quit)
btn_salir.pack(padx=20, pady=(200, 10))

# 6. El bucle principal (Mantiene la aplicación viva y escuchando la pantalla táctil)
if __name__ == "__main__":
    app.mainloop()
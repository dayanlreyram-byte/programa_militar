"""CAPA DE PRESENTACIÓN — Vista de inicio de sesión."""
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_autenticacion as auth


class VistaLogin(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame")
        self.controlador = controlador

        contenedor = ttk.Frame(self, style="Fondo.TFrame")
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        tarjeta_frame, interior = est.tarjeta(contenedor)
        tarjeta_frame.pack(padx=10, pady=10)

        ttk.Label(interior, text="🔐 Control de Acceso Militar",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(interior, text="Dirección General del Ejército",
                  style="Texto.TLabel").pack(anchor="w", pady=(0, 14))
        ttk.Separator(interior, orient="horizontal").pack(fill="x", pady=(0, 16))

        # --- Panel de credenciales ---
        panel_credenciales = tk.Frame(interior, bg=est.GRIS_CLARO,
                                       highlightbackground=est.DORADO, highlightthickness=1)
        panel_credenciales.pack(fill="x", pady=(0, 16))

        tk.Label(panel_credenciales, text="🔑 Credenciales de acceso", bg=est.GRIS_CLARO,
                 fg=est.VERDE_OSCURO, font=est.FUENTE_TEXTO_BOLD, anchor="w").pack(
            fill="x", padx=14, pady=(12, 10))

        tk.Label(panel_credenciales, text="Usuario", bg=est.GRIS_CLARO,
                 fg=est.TEXTO_OSCURO, font=est.FUENTE_TEXTO, anchor="w").pack(fill="x", padx=14)
        self.entrada_usuario = ttk.Entry(panel_credenciales, width=30, font=est.FUENTE_TEXTO)
        self.entrada_usuario.pack(padx=14, pady=(4, 12), ipady=3)

        tk.Label(panel_credenciales, text="Contraseña", bg=est.GRIS_CLARO,
                 fg=est.TEXTO_OSCURO, font=est.FUENTE_TEXTO, anchor="w").pack(fill="x", padx=14)
        self.entrada_password = ttk.Entry(panel_credenciales, width=30, show="•",
                                           font=est.FUENTE_TEXTO)
        self.entrada_password.pack(padx=14, pady=(4, 14), ipady=3)
        self.entrada_password.bind("<Return>", lambda _e: self._iniciar_sesion())

        ttk.Label(interior,
                  text="Una contraseña segura tiene: " + ", ".join(auth.REQUISITOS_PASSWORD),
                  style="Info.TLabel", wraplength=300, justify="left").pack(anchor="w", pady=(0, 4))

        self.etiqueta_mensaje = ttk.Label(interior, text="", style="Error.TLabel",
                                           wraplength=300)
        self.etiqueta_mensaje.pack(anchor="w", pady=(8, 14))

        ttk.Button(interior, text="Iniciar sesión", style="Primario.TButton",
                   command=self._iniciar_sesion).pack(fill="x", pady=(0, 8))
        ttk.Button(interior, text="Crear una cuenta nueva", style="Secundario.TButton",
                   command=lambda: controlador.mostrar_vista("registro")).pack(fill="x")
        ttk.Button(interior, text="¿Olvidaste tu contraseña?", style="Secundario.TButton",
                   command=lambda: controlador.mostrar_vista("recuperar")).pack(fill="x", pady=(6, 0))

    def _iniciar_sesion(self):
        usuario = self.entrada_usuario.get()
        password = self.entrada_password.get()
        try:
            rol = auth.iniciar_sesion(usuario, password)
            self.etiqueta_mensaje.configure(text="")
            self.controlador.iniciar_sesion_exitosa(usuario.strip(), rol)
        except auth.ErrorAutenticacion as error:
            self.etiqueta_mensaje.configure(text=str(error))

    def al_mostrar(self):
        self.entrada_usuario.delete(0, tk.END)
        self.entrada_password.delete(0, tk.END)
        self.etiqueta_mensaje.configure(text="")
        self.entrada_usuario.focus_set()

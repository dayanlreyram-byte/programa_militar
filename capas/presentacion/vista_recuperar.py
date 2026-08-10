"""CAPA DE PRESENTACIÓN — Recuperación de contraseña con la clave
generada en el registro."""
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_autenticacion as auth


class VistaRecuperar(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame")
        self.controlador = controlador

        contenedor = ttk.Frame(self, style="Fondo.TFrame")
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        tarjeta_frame, interior = est.tarjeta(contenedor)
        tarjeta_frame.pack(padx=10, pady=10)

        ttk.Label(interior, text="🔑 Recuperar contraseña",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(interior,
                  text="Ingresa tu usuario y la clave de recuperación\n"
                       "que se te mostró al registrarte.",
                  style="Texto.TLabel", justify="left").pack(anchor="w", pady=(0, 16))

        ttk.Label(interior, text="Usuario", style="Texto.TLabel").pack(anchor="w")
        self.entrada_usuario = ttk.Entry(interior, width=32, font=est.FUENTE_TEXTO)
        self.entrada_usuario.pack(pady=(2, 12))

        ttk.Label(interior, text="Clave de recuperación", style="Texto.TLabel").pack(anchor="w")
        self.entrada_clave = ttk.Entry(interior, width=32, font=est.FUENTE_TEXTO)
        self.entrada_clave.pack(pady=(2, 12))

        ttk.Label(interior, text="Nueva contraseña", style="Texto.TLabel").pack(anchor="w")
        self.entrada_nueva = ttk.Entry(interior, width=32, show="•", font=est.FUENTE_TEXTO)
        self.entrada_nueva.pack(pady=(2, 8))
        self.entrada_nueva.bind("<KeyRelease>", self._actualizar_checklist)

        marco_checklist = tk.Frame(interior, bg=est.GRIS_CLARO)
        marco_checklist.pack(fill="x", pady=(0, 12), ipady=8, ipadx=8)
        self.etiquetas_requisitos = []
        for requisito in auth.REQUISITOS_PASSWORD:
            etiqueta = tk.Label(marco_checklist, text=f"○ {requisito}", bg=est.GRIS_CLARO,
                                 fg=est.TEXTO_OSCURO, font=est.FUENTE_TEXTO, anchor="w")
            etiqueta.pack(fill="x", padx=8)
            self.etiquetas_requisitos.append(etiqueta)

        ttk.Label(interior, text="Confirmar nueva contraseña", style="Texto.TLabel").pack(anchor="w")
        self.entrada_nueva2 = ttk.Entry(interior, width=32, show="•", font=est.FUENTE_TEXTO)
        self.entrada_nueva2.pack(pady=(2, 4))

        self.etiqueta_mensaje = ttk.Label(interior, text="", style="Error.TLabel",
                                           wraplength=280)
        self.etiqueta_mensaje.pack(anchor="w", pady=(8, 12))

        ttk.Button(interior, text="Restablecer contraseña", style="Primario.TButton",
                   command=self._restablecer).pack(fill="x", pady=(4, 8))
        ttk.Button(interior, text="Volver a iniciar sesión", style="Secundario.TButton",
                   command=lambda: controlador.mostrar_vista("login")).pack(fill="x")

    def _actualizar_checklist(self, _evento=None):
        password = self.entrada_nueva.get()
        faltantes = set(auth.validar_fortaleza_password(password))
        for etiqueta, requisito in zip(self.etiquetas_requisitos, auth.REQUISITOS_PASSWORD):
            if requisito in faltantes:
                etiqueta.configure(text=f"○ {requisito}", fg=est.TEXTO_OSCURO)
            else:
                etiqueta.configure(text=f"✓ {requisito}", fg=est.VERDE_EXITO)

    def _restablecer(self):
        usuario = self.entrada_usuario.get()
        clave = self.entrada_clave.get()
        nueva = self.entrada_nueva.get()
        nueva2 = self.entrada_nueva2.get()

        if nueva != nueva2:
            self.etiqueta_mensaje.configure(text="Las contraseñas nuevas no coinciden.")
            return
        try:
            auth.recuperar_password(usuario, clave, nueva)
            self.etiqueta_mensaje.configure(text="")
            self._mostrar_exito()
        except auth.ErrorAutenticacion as error:
            self.etiqueta_mensaje.configure(text=str(error))

    def _mostrar_exito(self):
        self.etiqueta_mensaje.configure(
            text="✅ Contraseña actualizada. Ya puedes iniciar sesión.", style="Exito.TLabel")

    def al_mostrar(self):
        self.entrada_usuario.delete(0, tk.END)
        self.entrada_clave.delete(0, tk.END)
        self.entrada_nueva.delete(0, tk.END)
        self.entrada_nueva2.delete(0, tk.END)
        self.etiqueta_mensaje.configure(text="", style="Error.TLabel")
        self._actualizar_checklist()
        self.entrada_usuario.focus_set()

"""CAPA DE PRESENTACIÓN — Vista de registro de nuevos usuarios, con
checklist en vivo de los requisitos de una contraseña segura."""
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_autenticacion as auth


class VistaRegistro(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame")
        self.controlador = controlador

        contenedor = ttk.Frame(self, style="Fondo.TFrame")
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        tarjeta_frame, self.interior = est.tarjeta(contenedor)
        tarjeta_frame.pack(padx=10, pady=10)

        self.etiquetas_requisitos = []
        self._construir_formulario()

    def _construir_formulario(self):
        for hijo in self.interior.winfo_children():
            hijo.destroy()

        ttk.Label(self.interior, text="Crear cuenta de acceso",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(self.interior,
                  text="La contraseña se guarda con hashing (PBKDF2-SHA256 + salt),\nnunca en texto plano.",
                  style="Texto.TLabel", justify="left").pack(anchor="w", pady=(0, 16))

        ttk.Label(self.interior, text="Usuario", style="Texto.TLabel").pack(anchor="w")
        self.entrada_usuario = ttk.Entry(self.interior, width=32, font=est.FUENTE_TEXTO)
        self.entrada_usuario.pack(pady=(2, 12))

        ttk.Label(self.interior, text="Contraseña", style="Texto.TLabel").pack(anchor="w")
        self.entrada_password = ttk.Entry(self.interior, width=32, show="•", font=est.FUENTE_TEXTO)
        self.entrada_password.pack(pady=(2, 8))
        self.entrada_password.bind("<KeyRelease>", self._actualizar_checklist)

        # --- Checklist en vivo de una contraseña segura ---
        marco_checklist = tk.Frame(self.interior, bg=est.GRIS_CLARO)
        marco_checklist.pack(fill="x", pady=(0, 12), ipady=8, ipadx=8)
        self.etiquetas_requisitos = []
        for requisito in auth.REQUISITOS_PASSWORD:
            etiqueta = tk.Label(marco_checklist, text=f"○ {requisito}", bg=est.GRIS_CLARO,
                                 fg=est.TEXTO_OSCURO, font=est.FUENTE_TEXTO, anchor="w")
            etiqueta.pack(fill="x", padx=8)
            self.etiquetas_requisitos.append(etiqueta)

        ttk.Label(self.interior, text="Confirmar contraseña", style="Texto.TLabel").pack(anchor="w")
        self.entrada_password2 = ttk.Entry(self.interior, width=32, show="•", font=est.FUENTE_TEXTO)
        self.entrada_password2.pack(pady=(2, 4))

        self.etiqueta_mensaje = ttk.Label(self.interior, text="", style="Error.TLabel",
                                           wraplength=280)
        self.etiqueta_mensaje.pack(anchor="w", pady=(8, 12))

        ttk.Button(self.interior, text="Registrarme", style="Primario.TButton",
                   command=self._registrar).pack(fill="x", pady=(4, 8))
        ttk.Button(self.interior, text="Ya tengo cuenta — Iniciar sesión",
                   style="Secundario.TButton",
                   command=lambda: self.controlador.mostrar_vista("login")).pack(fill="x")

    def _actualizar_checklist(self, _evento=None):
        password = self.entrada_password.get()
        faltantes = set(auth.validar_fortaleza_password(password))
        for etiqueta, requisito in zip(self.etiquetas_requisitos, auth.REQUISITOS_PASSWORD):
            if requisito in faltantes:
                etiqueta.configure(text=f"○ {requisito}", fg=est.TEXTO_OSCURO)
            else:
                etiqueta.configure(text=f"✓ {requisito}", fg=est.VERDE_EXITO)

    def _mostrar_clave_generada(self, rol, clave):
        for hijo in self.interior.winfo_children():
            hijo.destroy()

        ttk.Label(self.interior, text="✅ Cuenta creada", style="Subtitulo.TLabel").pack(
            anchor="w", pady=(0, 4))
        ttk.Label(self.interior, text=f"Rol asignado: {rol}", style="Texto.TLabel").pack(
            anchor="w", pady=(0, 16))
        ttk.Label(self.interior,
                  text="Guarda esta clave de recuperación generada de forma segura\n"
                       "(módulo 'secrets'). Solo se muestra una vez, y la necesitarás\n"
                       "si olvidas tu contraseña:",
                  style="Texto.TLabel", justify="left").pack(anchor="w", pady=(0, 8))

        campo_clave = tk.Entry(self.interior, font=est.FUENTE_MONO, justify="center",
                                fg=est.VERDE_OSCURO, relief="solid", bd=1)
        campo_clave.insert(0, clave)
        campo_clave.configure(state="readonly", readonlybackground=est.GRIS_CLARO)
        campo_clave.pack(fill="x", pady=(0, 16), ipady=6)

        ttk.Button(self.interior, text="Ir a iniciar sesión", style="Primario.TButton",
                   command=lambda: self.controlador.mostrar_vista("login")).pack(fill="x")

    def _registrar(self):
        usuario = self.entrada_usuario.get()
        password = self.entrada_password.get()
        password2 = self.entrada_password2.get()

        if password != password2:
            self.etiqueta_mensaje.configure(text="Las contraseñas no coinciden.")
            return
        try:
            rol, clave = auth.registrar_usuario(usuario, password)
            self._mostrar_clave_generada(rol, clave)
        except auth.ErrorAutenticacion as error:
            self.etiqueta_mensaje.configure(text=str(error))

    def al_mostrar(self):
        self._construir_formulario()

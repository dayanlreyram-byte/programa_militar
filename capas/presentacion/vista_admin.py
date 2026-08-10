"""CAPA DE PRESENTACIÓN — Panel de administración: usuarios, roles,
bitácora de inicios de sesión y una leyenda clara de qué puede hacer
cada rol (el admin tiene MENOS restricciones que el operador)."""
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_autenticacion as auth
from config import ROL_ADMIN, ROL_OPERADOR


class VistaAdmin(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame", padding=24)
        self.controlador = controlador

        ttk.Label(self, text="Panel de Administración y Permisos",
                  style="Titulo.TLabel").pack(anchor="w", pady=(0, 12))

        # --- Leyenda de permisos por rol (colores distintos por rol) ---
        leyenda, interior_leyenda = est.tarjeta(self)
        leyenda.pack(fill="x", pady=(0, 16))
        ttk.Label(interior_leyenda, text="Niveles de acceso", style="Subtitulo.TLabel").pack(
            anchor="w", pady=(0, 10))

        fila_admin = tk.Frame(interior_leyenda, bg=est.BLANCO)
        fila_admin.pack(fill="x", pady=(0, 8))
        est.crear_insignia_rol(fila_admin, ROL_ADMIN).pack(side="left")
        ttk.Label(fila_admin,
                  text="  Acceso completo: ve todos los datos desencriptados (personal,\n"
                       "  hoja de vida, apartados de verificación) y administra usuarios/roles.\n"
                       "  → MENOS restricciones.",
                  style="Texto.TLabel", justify="left").pack(side="left")

        fila_operador = tk.Frame(interior_leyenda, bg=est.BLANCO)
        fila_operador.pack(fill="x")
        est.crear_insignia_rol(fila_operador, ROL_OPERADOR).pack(side="left")
        ttk.Label(fila_operador,
                  text="  Acceso restringido: puede capturar personal e ingresos, pero ve\n"
                       "  los campos sensibles enmascarados (••••••••) y NO entra a este panel.\n"
                       "  → MÁS restricciones.",
                  style="Texto.TLabel", justify="left").pack(side="left")

        # --- Notebook con dos pestañas: usuarios / bitácora ---
        pestañas = ttk.Notebook(self)
        pestañas.pack(fill="both", expand=True)

        tab_usuarios = ttk.Frame(pestañas, style="Fondo.TFrame", padding=(0, 12, 0, 0))
        tab_bitacora = ttk.Frame(pestañas, style="Fondo.TFrame", padding=(0, 12, 0, 0))
        pestañas.add(tab_usuarios, text="👤 Usuarios y roles")
        pestañas.add(tab_bitacora, text="📜 Bitácora de accesos")

        self._construir_tab_usuarios(tab_usuarios)
        self._construir_tab_bitacora(tab_bitacora)

    def _construir_tab_usuarios(self, padre):
        tarjeta_frame, interior = est.tarjeta(padre)
        tarjeta_frame.pack(fill="both", expand=True)

        cabecera = ttk.Frame(interior, style="Tarjeta.TFrame")
        cabecera.pack(fill="x", pady=(0, 8))
        ttk.Label(cabecera, text="Usuarios del sistema", style="Subtitulo.TLabel").pack(
            side="left")
        ttk.Button(cabecera, text="🔄 Actualizar", style="Secundario.TButton",
                   command=self._refrescar_usuarios).pack(side="right")

        columnas = ("username", "rol", "fecha")
        self.tabla_usuarios = ttk.Treeview(interior, columns=columnas, show="headings", height=10)
        for col, titulo, ancho in [("username", "Usuario", 200), ("rol", "Rol", 120),
                                    ("fecha", "Registrado", 180)]:
            self.tabla_usuarios.heading(col, text=titulo)
            self.tabla_usuarios.column(col, width=ancho, anchor="w")
        self.tabla_usuarios.pack(fill="both", expand=True, pady=(0, 12))

        barra_acciones = ttk.Frame(interior, style="Tarjeta.TFrame")
        barra_acciones.pack(fill="x")
        ttk.Label(barra_acciones, text="Cambiar rol del usuario seleccionado a:",
                  style="Texto.TLabel").pack(side="left", padx=(0, 12))
        ttk.Button(barra_acciones, text="👑 admin", style="Primario.TButton",
                   command=lambda: self._cambiar_rol(ROL_ADMIN)).pack(side="left", padx=4)
        ttk.Button(barra_acciones, text="🔒 operador", style="Info.TButton",
                   command=lambda: self._cambiar_rol(ROL_OPERADOR)).pack(side="left", padx=4)

        self.etiqueta_mensaje = ttk.Label(interior, text="", style="Texto.TLabel")
        self.etiqueta_mensaje.pack(anchor="w", pady=(12, 0))

    def _construir_tab_bitacora(self, padre):
        tarjeta_frame, interior = est.tarjeta(padre)
        tarjeta_frame.pack(fill="both", expand=True)

        cabecera = ttk.Frame(interior, style="Tarjeta.TFrame")
        cabecera.pack(fill="x", pady=(0, 8))
        ttk.Label(cabecera, text="Bitácora de inicios de sesión", style="Subtitulo.TLabel").pack(
            side="left")
        ttk.Button(cabecera, text="🔄 Actualizar", style="Secundario.TButton",
                   command=self._refrescar_bitacora).pack(side="right")
        ttk.Label(interior, text="Se registra cada intento de login, exitoso o fallido.",
                  style="Texto.TLabel").pack(anchor="w", pady=(0, 8))

        columnas = ("usuario", "rol", "resultado", "fecha")
        self.tabla_bitacora = ttk.Treeview(interior, columns=columnas, show="headings", height=14)
        for col, titulo, ancho in [("usuario", "Usuario", 160), ("rol", "Rol", 100),
                                    ("resultado", "Resultado", 100), ("fecha", "Fecha/hora", 180)]:
            self.tabla_bitacora.heading(col, text=titulo)
            self.tabla_bitacora.column(col, width=ancho, anchor="w")
        self.tabla_bitacora.pack(fill="both", expand=True)
        self.tabla_bitacora.tag_configure("exitoso", foreground=est.VERDE_EXITO)
        self.tabla_bitacora.tag_configure("fallido", foreground=est.ROJO_ALERTA)

    def _refrescar_usuarios(self):
        for fila in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(fila)
        for u in auth.listar_usuarios():
            self.tabla_usuarios.insert("", "end", values=(u["username"], u["rol"], u["fecha_registro"]))

    def _refrescar_bitacora(self):
        for fila in self.tabla_bitacora.get_children():
            self.tabla_bitacora.delete(fila)
        for acceso in auth.listar_bitacora_accesos():
            exitoso = bool(acceso["exitoso"])
            self.tabla_bitacora.insert(
                "", "end",
                values=(acceso["username"], acceso["rol"],
                        "✅ Exitoso" if exitoso else "❌ Fallido", acceso["fecha_hora"]),
                tags=("exitoso" if exitoso else "fallido",))

    def _cambiar_rol(self, nuevo_rol):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            self.etiqueta_mensaje.configure(text="Selecciona un usuario de la tabla.",
                                             style="Error.TLabel")
            return
        username = self.tabla_usuarios.item(seleccion[0])["values"][0]
        try:
            auth.cambiar_rol(username, nuevo_rol)
            self.etiqueta_mensaje.configure(text=f"Rol de '{username}' actualizado a {nuevo_rol}.",
                                             style="Exito.TLabel")
            self._refrescar_usuarios()
        except auth.ErrorAutenticacion as error:
            self.etiqueta_mensaje.configure(text=str(error), style="Error.TLabel")

    def al_mostrar(self):
        self.etiqueta_mensaje.configure(text="")
        self._refrescar_usuarios()
        self._refrescar_bitacora()

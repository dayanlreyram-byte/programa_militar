"""
CAPA DE PRESENTACIÓN — Ventana principal.

Controla la navegación entre vistas (login/registro antes de
autenticarse; personal/verificación/admin después) y mantiene el
estado de sesión (usuario y rol actuales). No contiene lógica de
negocio: cada vista delega en los servicios de la capa de negocio.
"""
import tkinter as tk
from tkinter import ttk

from capas.presentacion import estilos as est
from capas.presentacion.vista_login import VistaLogin
from capas.presentacion.vista_registro import VistaRegistro
from capas.presentacion.vista_recuperar import VistaRecuperar
from capas.presentacion.vista_personal import VistaPersonal
from capas.presentacion.vista_hoja_vida import VistaHojaVida
from capas.presentacion.vista_verificacion import VistaVerificacion
from capas.presentacion.vista_admin import VistaAdmin
from capas.negocio import servicio_permisos as permisos
from config import APP_TITLE


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1080x680")
        self.minsize(920, 600)
        est.aplicar_tema(self)

        self.usuario_actual = None
        self.rol_actual = None
        self.ventana_hoja_vida = None

        # --- Contenedor de vistas previas al login (sin sidebar) ---
        self.contenedor_publico = ttk.Frame(self, style="Fondo.TFrame")
        self.contenedor_publico.pack(fill="both", expand=True)

        self.vistas_publicas = {
            "login": VistaLogin(self.contenedor_publico, self),
            "registro": VistaRegistro(self.contenedor_publico, self),
            "recuperar": VistaRecuperar(self.contenedor_publico, self),
        }
        for vista in self.vistas_publicas.values():
            vista.place(relx=0, rely=0, relwidth=1, relheight=1)

        # --- Estructura post-login (sidebar + contenido) ---
        self.contenedor_privado = ttk.Frame(self, style="Fondo.TFrame")
        self._construir_shell_privado()

        self.vista_publica_actual = None
        self.mostrar_vista("login")

    # ------------------------------------------------------------------
    # Navegación pública (antes de iniciar sesión)
    # ------------------------------------------------------------------
    def mostrar_vista(self, nombre):
        self.contenedor_privado.pack_forget()
        self.contenedor_publico.pack(fill="both", expand=True)
        vista = self.vistas_publicas[nombre]
        vista.tkraise()
        vista.al_mostrar()
        self.vista_publica_actual = nombre

    # ------------------------------------------------------------------
    # Sesión
    # ------------------------------------------------------------------
    def iniciar_sesion_exitosa(self, usuario, rol):
        self.usuario_actual = usuario
        self.rol_actual = rol
        self._actualizar_sidebar()
        self.contenedor_publico.pack_forget()
        self.contenedor_privado.pack(fill="both", expand=True)
        self.mostrar_seccion("personal")

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.rol_actual = None
        self.mostrar_vista("login")

    # ------------------------------------------------------------------
    # Shell privado (sidebar + área de contenido)
    # ------------------------------------------------------------------
    def _construir_shell_privado(self):
        self.contenedor_privado.columnconfigure(1, weight=1)
        self.contenedor_privado.rowconfigure(0, weight=1)

        self.barra_lateral = tk.Frame(self.contenedor_privado, bg=est.VERDE_OSCURO, width=230)
        self.barra_lateral.grid(row=0, column=0, sticky="ns")
        self.barra_lateral.grid_propagate(False)

        ttk.Label(self.barra_lateral, text="🎖️\nControl de Acceso\nDirección Gral. del Ejército",
                  style="TituloBarra.TLabel").pack(pady=(28, 24), padx=16)

        self.etiqueta_usuario = ttk.Label(self.barra_lateral, text="", style="TextoBarra.TLabel")
        self.etiqueta_usuario.pack(pady=(0, 6), padx=16)

        self.marco_insignia = tk.Frame(self.barra_lateral, bg=est.VERDE_OSCURO)
        self.marco_insignia.pack(pady=(0, 20), padx=16)

        self.botones_menu = {}
        self._agregar_boton_menu("personal", "👤  Personal Militar")
        ttk.Button(self.barra_lateral, text="📋  Hoja de Vida", style="Menu.TButton",
                   command=self.abrir_ventana_hoja_vida).pack(fill="x", padx=10, pady=2)
        self._agregar_boton_menu("verificacion", "🛡️  Verificación de Ingreso")
        self._agregar_boton_menu("admin", "⚙️  Administración")

        ttk.Separator(self.barra_lateral, orient="horizontal").pack(fill="x", padx=16, pady=16)
        ttk.Button(self.barra_lateral, text="Cerrar sesión", style="Secundario.TButton",
                   command=self.cerrar_sesion).pack(padx=16, fill="x")

        self.area_contenido = ttk.Frame(self.contenedor_privado, style="Fondo.TFrame")
        self.area_contenido.grid(row=0, column=1, sticky="nsew")

        self.vistas_privadas = {
            "personal": VistaPersonal(self.area_contenido, self),
            "verificacion": VistaVerificacion(self.area_contenido, self),
            "admin": VistaAdmin(self.area_contenido, self),
        }
        for vista in self.vistas_privadas.values():
            vista.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.seccion_actual = None

    def _agregar_boton_menu(self, nombre, texto):
        boton = ttk.Button(self.barra_lateral, text=texto, style="Menu.TButton",
                            command=lambda: self.mostrar_seccion(nombre))
        boton.pack(fill="x", padx=10, pady=2)
        self.botones_menu[nombre] = boton

    def _actualizar_sidebar(self):
        self.etiqueta_usuario.configure(text=f"👋 {self.usuario_actual}")
        for hijo in self.marco_insignia.winfo_children():
            hijo.destroy()
        est.crear_insignia_rol(self.marco_insignia, self.rol_actual).pack()
        admin_permitido = permisos.puede_administrar_usuarios(self.rol_actual)
        estado = "normal" if admin_permitido else "disabled"
        self.botones_menu["admin"].configure(state=estado)

    def abrir_ventana_hoja_vida(self):
        """Abre la Hoja de Vida en una ventana propia (Toplevel), separada
        del resto de secciones del menú lateral."""
        if self.ventana_hoja_vida is not None and self.ventana_hoja_vida.winfo_exists():
            self.ventana_hoja_vida.deiconify()
            self.ventana_hoja_vida.lift()
            self.ventana_hoja_vida.focus_force()
            return

        self.ventana_hoja_vida = tk.Toplevel(self)
        self.ventana_hoja_vida.title("Hoja de Vida del Personal")
        self.ventana_hoja_vida.geometry("980x640")
        self.ventana_hoja_vida.minsize(860, 560)
        self.ventana_hoja_vida.configure(bg=est.GRIS_CLARO)
        self.ventana_hoja_vida.transient(self)

        vista = VistaHojaVida(self.ventana_hoja_vida, self)
        vista.pack(fill="both", expand=True)
        vista.al_mostrar()

    def mostrar_seccion(self, nombre):
        if nombre == "admin" and not permisos.puede_administrar_usuarios(self.rol_actual):
            return
        for clave, boton in self.botones_menu.items():
            boton.configure(style="MenuActivo.TButton" if clave == nombre else "Menu.TButton")
        vista = self.vistas_privadas[nombre]
        vista.tkraise()
        vista.al_mostrar()
        self.seccion_actual = nombre


def iniciar_aplicacion():
    app = App()
    app.mainloop()

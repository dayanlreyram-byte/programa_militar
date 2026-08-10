"""
CAPA DE PRESENTACIÓN — Paleta de colores, fuentes y utilidades de estilo
compartidas por todas las vistas, para que la app tenga una identidad
visual consistente sin depender de librerías externas (solo ttk).
"""
import tkinter as tk
from tkinter import ttk

# Paleta "militar / institucional"
VERDE_OSCURO = "#14231a"     # fondo de la barra lateral / headers
VERDE_MEDIO = "#1f3a28"      # paneles secundarios
VERDE_ACENTO = "#2f5233"     # botones primarios
DORADO = "#c9a227"           # acentos, títulos importantes
GRIS_CLARO = "#f4f5f2"       # fondo general de contenido
BLANCO = "#ffffff"
TEXTO_OSCURO = "#20261f"
TEXTO_CLARO = "#e9ecec"
ROJO_ALERTA = "#8b2e2e"
VERDE_EXITO = "#2f6b3a"
AZUL_INFO = "#2c5f8a"
AMBAR = "#b8721b"
DORADO_CLARO = "#e9c25c"
VERDE_CLARO_BADGE = "#3f7a4a"

FUENTE_TITULO = ("Georgia", 20, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_TEXTO = ("Segoe UI", 10)
FUENTE_TEXTO_BOLD = ("Segoe UI", 10, "bold")
FUENTE_MONO = ("Consolas", 12, "bold")


def aplicar_tema(root: tk.Tk):
    """Configura un tema ttk consistente para toda la aplicación."""
    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=GRIS_CLARO)

    estilo.configure("Fondo.TFrame", background=GRIS_CLARO)
    estilo.configure("Barra.TFrame", background=VERDE_OSCURO)
    estilo.configure("Tarjeta.TFrame", background=BLANCO, relief="flat")
    estilo.configure("Encabezado.TFrame", background=VERDE_MEDIO)

    estilo.configure("Titulo.TLabel", background=GRIS_CLARO, foreground=VERDE_OSCURO,
                      font=FUENTE_TITULO)
    estilo.configure("TituloBarra.TLabel", background=VERDE_OSCURO, foreground=DORADO,
                      font=("Georgia", 14, "bold"), wraplength=200, justify="center")
    estilo.configure("Subtitulo.TLabel", background=BLANCO, foreground=VERDE_OSCURO,
                      font=FUENTE_SUBTITULO)
    estilo.configure("Texto.TLabel", background=BLANCO, foreground=TEXTO_OSCURO,
                      font=FUENTE_TEXTO)
    estilo.configure("TextoBarra.TLabel", background=VERDE_OSCURO, foreground=TEXTO_CLARO,
                      font=FUENTE_TEXTO)
    estilo.configure("TextoEncabezado.TLabel", background=VERDE_MEDIO, foreground=BLANCO,
                      font=FUENTE_SUBTITULO)
    estilo.configure("Error.TLabel", background=BLANCO, foreground=ROJO_ALERTA,
                      font=FUENTE_TEXTO_BOLD)
    estilo.configure("Exito.TLabel", background=BLANCO, foreground=VERDE_EXITO,
                      font=FUENTE_TEXTO_BOLD)
    estilo.configure("Info.TLabel", background=BLANCO, foreground=AZUL_INFO,
                      font=FUENTE_TEXTO)
    estilo.configure("Advertencia.TLabel", background=BLANCO, foreground=AMBAR,
                      font=FUENTE_TEXTO_BOLD)

    estilo.configure("TEntry", fieldbackground=BLANCO, padding=6)
    estilo.configure("TCombobox", fieldbackground=BLANCO, padding=6)

    estilo.configure("Primario.TButton", background=VERDE_ACENTO, foreground=BLANCO,
                      font=FUENTE_TEXTO_BOLD, padding=10, borderwidth=0)
    estilo.map("Primario.TButton",
               background=[("active", DORADO)],
               foreground=[("active", VERDE_OSCURO)])

    estilo.configure("Secundario.TButton", background=GRIS_CLARO, foreground=VERDE_OSCURO,
                      font=FUENTE_TEXTO, padding=8, borderwidth=1)
    estilo.map("Secundario.TButton", background=[("active", "#e2e4dd")])

    estilo.configure("Peligro.TButton", background=ROJO_ALERTA, foreground=BLANCO,
                      font=FUENTE_TEXTO_BOLD, padding=10, borderwidth=0)
    estilo.map("Peligro.TButton", background=[("active", "#6f2323")])

    estilo.configure("Info.TButton", background=AZUL_INFO, foreground=BLANCO,
                      font=FUENTE_TEXTO_BOLD, padding=10, borderwidth=0)
    estilo.map("Info.TButton", background=[("active", "#1f4666")])

    estilo.configure("Menu.TButton", background=VERDE_OSCURO, foreground=TEXTO_CLARO,
                      font=FUENTE_TEXTO_BOLD, padding=12, borderwidth=0, anchor="w")
    estilo.map("Menu.TButton",
               background=[("active", VERDE_ACENTO)],
               foreground=[("active", BLANCO)])

    estilo.configure("MenuActivo.TButton", background=VERDE_ACENTO, foreground=BLANCO,
                      font=FUENTE_TEXTO_BOLD, padding=12, borderwidth=0, anchor="w")

    estilo.configure("Treeview", background=BLANCO, fieldbackground=BLANCO,
                      foreground=TEXTO_OSCURO, rowheight=26, font=FUENTE_TEXTO)
    estilo.configure("Treeview.Heading", background=VERDE_MEDIO, foreground=BLANCO,
                      font=FUENTE_TEXTO_BOLD)
    estilo.map("Treeview", background=[("selected", DORADO)],
               foreground=[("selected", VERDE_OSCURO)])

    estilo.configure("TNotebook", background=GRIS_CLARO, borderwidth=0)
    estilo.configure("TNotebook.Tab", background="#e2e4dd", foreground=VERDE_OSCURO,
                      font=FUENTE_TEXTO_BOLD, padding=(16, 8))
    estilo.map("TNotebook.Tab",
               background=[("selected", VERDE_ACENTO)],
               foreground=[("selected", BLANCO)])

    return estilo


def tarjeta(padre, **kwargs):
    """Crea un frame tipo 'tarjeta' (fondo blanco, borde suave, padding)."""
    contenedor = tk.Frame(padre, bg=BLANCO, highlightbackground="#d8dad2",
                           highlightthickness=1, bd=0)
    interior = ttk.Frame(contenedor, style="Tarjeta.TFrame", padding=24)
    interior.pack(fill="both", expand=True)
    return contenedor, interior


def crear_insignia_rol(padre, rol):
    """Insignia de color según el rol: dorada (acceso completo) para
    admin, verde para operador (acceso restringido) — para que el
    nivel de permisos se distinga de un vistazo en toda la app."""
    if rol == "admin":
        fondo, texto = DORADO, f"👑 ADMIN — acceso completo"
    else:
        fondo, texto = VERDE_CLARO_BADGE, f"🔒 OPERADOR — acceso restringido"
    insignia = tk.Label(padre, text=texto, bg=fondo, fg=VERDE_OSCURO if rol == "admin" else BLANCO,
                         font=FUENTE_TEXTO_BOLD, padx=10, pady=4)
    return insignia

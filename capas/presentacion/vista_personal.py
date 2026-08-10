"""CAPA DE PRESENTACIÓN — Registro de datos militares del personal.
La Hoja de Vida (cédula, teléfono, ciudad, dirección, barrio, género,
edad) se completa en su propia ventana: ver vista_hoja_vida.py."""
import re
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_personal as servicio


GRADOS = ["Soldado", "Cabo", "Sargento", "Subteniente", "Teniente",
          "Capitán", "Mayor", "Teniente Coronel", "Coronel", "General"]

TIPOS_CAMPO = {
    "nombres":    (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]*$", 40),
    "apellidos":  (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]*$", 40),
    "id_militar": (r"^[A-Za-z0-9\-]*$", 15),
    "unidad":     (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ]*$", 40),
}


class VistaPersonal(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame", padding=24)
        self.controlador = controlador

        ttk.Label(self, text="Registro Militar del Personal",
                  style="Titulo.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(self, text="Después de registrar aquí, completa la Hoja de Vida "
                              "de la persona en la sección '📋 Hoja de Vida'.",
                  style="Texto.TLabel").pack(anchor="w", pady=(0, 16))

        cuerpo = ttk.Frame(self, style="Fondo.TFrame")
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=0)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        # --- Formulario (tarjeta izquierda) ---
        tarjeta_form, interior = est.tarjeta(cuerpo)
        tarjeta_form.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        ttk.Label(interior, text="Datos militares", style="Subtitulo.TLabel").pack(
            anchor="w", pady=(0, 4))
        ttk.Label(interior, text="Se encriptan con AES antes de guardarse.",
                  style="Texto.TLabel").pack(anchor="w", pady=(0, 16))

        self.campos = {}
        self._agregar_campo(interior, "nombres", "Nombres (solo letras, máx. 40)")
        self._agregar_campo(interior, "apellidos", "Apellidos (solo letras, máx. 40)")
        self._agregar_campo(interior, "id_militar", "N.º identificación militar (máx. 15)")

        ttk.Label(interior, text="Grado / Rango", style="Texto.TLabel").pack(anchor="w")
        self.combo_grado = ttk.Combobox(interior, values=GRADOS, state="readonly",
                                         width=29, font=est.FUENTE_TEXTO)
        self.combo_grado.pack(pady=(2, 12))

        self._agregar_campo(interior, "unidad", "Unidad de asignación (máx. 40)")

        self.etiqueta_mensaje = ttk.Label(interior, text="", style="Error.TLabel",
                                           wraplength=280)
        self.etiqueta_mensaje.pack(anchor="w", pady=(4, 12))

        ttk.Button(interior, text="Guardar (encriptado)", style="Primario.TButton",
                   command=self._guardar).pack(fill="x")

        # --- Listado (tarjeta derecha) ---
        tarjeta_lista, interior_lista = est.tarjeta(cuerpo)
        tarjeta_lista.grid(row=0, column=1, sticky="nsew")

        cabecera_lista = ttk.Frame(interior_lista, style="Tarjeta.TFrame")
        cabecera_lista.pack(fill="x", pady=(0, 8))
        ttk.Label(cabecera_lista, text="Personal registrado", style="Subtitulo.TLabel").pack(
            side="left")
        ttk.Button(cabecera_lista, text="🔄 Actualizar", style="Secundario.TButton",
                   command=self._refrescar_lista).pack(side="right")

        columnas = ("id", "nombre", "id_militar", "grado", "unidad", "hoja_vida")
        self.tabla = ttk.Treeview(interior_lista, columns=columnas, show="headings", height=14)
        for col, titulo, ancho in [
            ("id", "ID", 40), ("nombre", "Nombre completo", 180),
            ("id_militar", "ID militar", 120), ("grado", "Grado", 120),
            ("unidad", "Unidad", 130), ("hoja_vida", "Hoja de Vida", 110),
        ]:
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.tag_configure("completa", foreground=est.VERDE_EXITO)
        self.tabla.tag_configure("pendiente", foreground=est.AMBAR)

        self.etiqueta_permiso = ttk.Label(interior_lista, text="", style="Texto.TLabel")
        self.etiqueta_permiso.pack(anchor="w", pady=(8, 0))

    def _validar_tecla(self, tipo_campo, texto_propuesto):
        patron, largo_max = TIPOS_CAMPO[tipo_campo]
        if len(texto_propuesto) > largo_max:
            return False
        return re.match(patron, texto_propuesto) is not None

    def _agregar_campo(self, padre, clave, etiqueta):
        ttk.Label(padre, text=etiqueta, style="Texto.TLabel").pack(anchor="w")
        vcmd = (self.register(lambda texto, c=clave: self._validar_tecla(c, texto)), "%P")
        entrada = ttk.Entry(padre, width=32, font=est.FUENTE_TEXTO,
                             validate="key", validatecommand=vcmd)
        entrada.pack(pady=(2, 12))
        self.campos[clave] = entrada

    def _guardar(self):
        datos = {clave: entrada.get() for clave, entrada in self.campos.items()}
        datos["grado"] = self.combo_grado.get()
        try:
            servicio.registrar_personal(datos, self.controlador.usuario_actual)
            self.etiqueta_mensaje.configure(text="")
            for entrada in self.campos.values():
                entrada.delete(0, tk.END)
            self.combo_grado.set("")
            self._refrescar_lista()
        except servicio.ErrorPersonal as error:
            self.etiqueta_mensaje.configure(text=str(error))

    def _refrescar_lista(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        personas = servicio.listar_personal(self.controlador.rol_actual)
        for p in personas:
            estado = "✅ Completa" if p.hoja_vida_completa else "⏳ Pendiente"
            etiqueta_tag = "completa" if p.hoja_vida_completa else "pendiente"
            self.tabla.insert("", "end", values=(p.id, p.nombre_completo, p.id_militar,
                                                   p.grado, p.unidad, estado),
                               tags=(etiqueta_tag,))
        if self.controlador.rol_actual != "admin":
            self.etiqueta_permiso.configure(
                text="🔒 Rol operador: nombre e ID militar aparecen enmascarados.")
        else:
            self.etiqueta_permiso.configure(text="🔓 Rol admin: acceso completo.")

    def al_mostrar(self):
        self.etiqueta_mensaje.configure(text="")
        self._refrescar_lista()

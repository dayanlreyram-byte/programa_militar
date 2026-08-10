"""CAPA DE PRESENTACIÓN — Ventana aparte para capturar la Hoja de Vida
(cédula, teléfono, ciudad, dirección, barrio, género, edad) de una
persona que ya fue registrada en '👤 Personal Militar'."""
import re
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_personal as servicio


GENEROS = ["Masculino", "Femenino", "Otro"]

TIPOS_CAMPO = {
    "cedula":     (r"^[0-9]*$", 10),
    "telefono":   (r"^[0-9]*$", 10),
    "ciudad":     (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]*$", 30),
    "direccion":  (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9#\-.,° ]*$", 60),
    "barrio":     (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ]*$", 30),
    "edad":       (r"^[0-9]*$", 3),
}


class VistaHojaVida(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame", padding=24)
        self.controlador = controlador
        self._mapa_opciones = {}

        ttk.Label(self, text="Hoja de Vida del Personal",
                  style="Titulo.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(self, text="Selecciona a una persona ya registrada en 'Personal Militar' "
                              "para completar o actualizar su hoja de vida.",
                  style="Texto.TLabel").pack(anchor="w", pady=(0, 16))

        cuerpo = ttk.Frame(self, style="Fondo.TFrame")
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=0)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        # --- Formulario (tarjeta izquierda) ---
        tarjeta_form = tk.Frame(cuerpo, bg=est.BLANCO, highlightbackground=est.DORADO,
                                 highlightthickness=2, bd=0, width=340)
        tarjeta_form.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        tarjeta_form.grid_propagate(False)

        lienzo = tk.Canvas(tarjeta_form, bg=est.BLANCO, highlightthickness=0, width=316)
        barra_scroll = ttk.Scrollbar(tarjeta_form, orient="vertical", command=lienzo.yview)
        interior = ttk.Frame(lienzo, style="Tarjeta.TFrame", padding=24)

        interior.bind("<Configure>", lambda _e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        lienzo.create_window((0, 0), window=interior, anchor="nw", width=316)
        lienzo.configure(yscrollcommand=barra_scroll.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra_scroll.pack(side="right", fill="y")

        def _rueda_raton(evento):
            lienzo.yview_scroll(int(-1 * (evento.delta / 120)), "units")
        lienzo.bind_all("<MouseWheel>", _rueda_raton, add="+")

        ttk.Label(interior, text="📋 Datos de Hoja de Vida", style="Subtitulo.TLabel").pack(
            anchor="w", pady=(0, 4))
        ttk.Label(interior, text="Se encriptan con AES antes de guardarse.",
                  style="Texto.TLabel").pack(anchor="w", pady=(0, 16))

        ttk.Label(interior, text="Persona", style="Texto.TLabel").pack(anchor="w")
        self.combo_personal = ttk.Combobox(interior, state="readonly", width=32,
                                            font=est.FUENTE_TEXTO)
        self.combo_personal.bind("<<ComboboxSelected>>", self._al_seleccionar_persona)
        self.combo_personal.pack(pady=(2, 16))

        self.campos = {}
        self._agregar_campo(interior, "cedula", "Cédula (solo números, 6 a 10 dígitos)")
        self._agregar_campo(interior, "telefono", "Teléfono (solo números, 7 a 10 dígitos)")
        self._agregar_campo(interior, "ciudad", "Ciudad (solo letras, máx. 30)")
        self._agregar_campo(interior, "direccion", "Dirección (máx. 60)")
        self._agregar_campo(interior, "barrio", "Barrio (máx. 30)")

        ttk.Label(interior, text="Género", style="Texto.TLabel").pack(anchor="w")
        self.combo_genero = ttk.Combobox(interior, values=GENEROS, state="readonly",
                                          width=29, font=est.FUENTE_TEXTO)
        self.combo_genero.pack(pady=(2, 12))

        self._agregar_campo(interior, "edad", f"Edad ({servicio.EDAD_MINIMA} a {servicio.EDAD_MAXIMA})")

        self.etiqueta_mensaje = ttk.Label(interior, text="", style="Error.TLabel",
                                           wraplength=280)
        self.etiqueta_mensaje.pack(anchor="w", pady=(4, 12))

        ttk.Button(interior, text="Guardar Hoja de Vida (encriptada)", style="Primario.TButton",
                   command=self._guardar).pack(fill="x")

        # --- Listado (tarjeta derecha) ---
        tarjeta_lista, interior_lista = est.tarjeta(cuerpo)
        tarjeta_lista.grid(row=0, column=1, sticky="nsew")

        cabecera_lista = ttk.Frame(interior_lista, style="Tarjeta.TFrame")
        cabecera_lista.pack(fill="x", pady=(0, 8))
        ttk.Label(cabecera_lista, text="Hojas de vida registradas", style="Subtitulo.TLabel").pack(
            side="left")
        ttk.Button(cabecera_lista, text="🔄 Actualizar", style="Secundario.TButton",
                   command=self._refrescar_lista).pack(side="right")

        columnas = ("id", "nombre", "cedula", "telefono", "ciudad", "genero", "edad", "estado")
        self.tabla = ttk.Treeview(interior_lista, columns=columnas, show="headings", height=14)
        for col, titulo, ancho in [
            ("id", "ID", 36), ("nombre", "Nombre completo", 150), ("cedula", "Cédula", 90),
            ("telefono", "Teléfono", 90), ("ciudad", "Ciudad", 90), ("genero", "Género", 80),
            ("edad", "Edad", 50), ("estado", "Estado", 100),
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

    def _refrescar_combo_personal(self):
        opciones = servicio.listar_opciones_para_combo()
        self._mapa_opciones = {etiqueta: pid for pid, etiqueta in opciones}
        self.combo_personal.configure(values=list(self._mapa_opciones.keys()))

    def _al_seleccionar_persona(self, _evento=None):
        etiqueta_sel = self.combo_personal.get()
        personal_id = self._mapa_opciones.get(etiqueta_sel)
        if personal_id is None or self.controlador.rol_actual != "admin":
            # El operador no ve datos ya cargados (evita exponer datos sensibles);
            # solo puede escribir/actualizar, no ver lo existente enmascarado.
            for entrada in self.campos.values():
                entrada.delete(0, tk.END)
            self.combo_genero.set("")
            return
        try:
            persona = servicio.obtener_personal_desencriptado(personal_id)
            for clave, entrada in self.campos.items():
                entrada.delete(0, tk.END)
                valor = getattr(persona, clave)
                if valor:
                    entrada.insert(0, valor)
            self.combo_genero.set(persona.genero if persona.genero else "")
        except servicio.ErrorPersonal:
            pass

    def _guardar(self):
        etiqueta_sel = self.combo_personal.get()
        personal_id = self._mapa_opciones.get(etiqueta_sel)
        if personal_id is None:
            self.etiqueta_mensaje.configure(text="Selecciona una persona registrada.")
            return

        datos = {clave: entrada.get() for clave, entrada in self.campos.items()}
        datos["genero"] = self.combo_genero.get()
        try:
            servicio.actualizar_hoja_vida(personal_id, datos, self.controlador.usuario_actual)
            self.etiqueta_mensaje.configure(text="")
            for entrada in self.campos.values():
                entrada.delete(0, tk.END)
            self.combo_genero.set("")
            self.combo_personal.set("")
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
            self.tabla.insert("", "end", values=(
                p.id, p.nombre_completo, p.cedula, p.telefono, p.ciudad,
                p.genero, p.edad, estado), tags=(etiqueta_tag,))
        if self.controlador.rol_actual != "admin":
            self.etiqueta_permiso.configure(
                text="🔒 Rol operador: datos sensibles enmascarados y no se precargan al editar.")
        else:
            self.etiqueta_permiso.configure(text="🔓 Rol admin: acceso completo, datos desencriptados.")

    def al_mostrar(self):
        self.etiqueta_mensaje.configure(text="")
        for entrada in self.campos.values():
            entrada.delete(0, tk.END)
        self.combo_genero.set("")
        self.combo_personal.set("")
        self._refrescar_combo_personal()
        self._refrescar_lista()

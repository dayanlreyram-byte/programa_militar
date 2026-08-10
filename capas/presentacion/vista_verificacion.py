"""CAPA DE PRESENTACIÓN — Apartado 1 (identidad) y Apartado 2 (propósito)
para registrar ingresos, más el flujo de autorización: solo el admin
puede autorizar o rechazar un ingreso; el operador únicamente lo
registra y queda 'pendiente'."""
import tkinter as tk
from tkinter import ttk
from capas.presentacion import estilos as est
from capas.negocio import servicio_personal as servicio_personal
from capas.negocio import servicio_verificacion as servicio
from capas.negocio import servicio_permisos as permisos


class VistaVerificacion(ttk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, style="Fondo.TFrame", padding=24)
        self.controlador = controlador

        ttk.Label(self, text="Apartados de Verificación de Ingreso",
                  style="Titulo.TLabel").pack(anchor="w", pady=(0, 16))

        cuerpo = ttk.Frame(self, style="Fondo.TFrame")
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=0)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        # --- Formulario ---
        tarjeta_form, interior = est.tarjeta(cuerpo)
        tarjeta_form.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        ttk.Label(interior, text="Apartado 1 — Identidad", style="Subtitulo.TLabel").pack(
            anchor="w", pady=(0, 4))
        ttk.Label(interior, text="Selecciona a la persona; el código único\n"
                                  "de verificación se genera automáticamente.",
                  style="Texto.TLabel", justify="left").pack(anchor="w", pady=(0, 10))

        self.combo_personal = ttk.Combobox(interior, state="readonly", width=32,
                                            font=est.FUENTE_TEXTO)
        self.combo_personal.pack(pady=(2, 16))

        ttk.Label(interior, text="Apartado 2 — Propósito del ingreso",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 4))

        ttk.Label(interior, text="Área de visita", style="Texto.TLabel").pack(anchor="w")
        self.entrada_area = ttk.Entry(interior, width=32, font=est.FUENTE_TEXTO)
        self.entrada_area.pack(pady=(2, 12))

        ttk.Label(interior, text="Propósito", style="Texto.TLabel").pack(anchor="w")
        self.combo_proposito = ttk.Combobox(interior, values=servicio.PROPOSITOS_VALIDOS,
                                             state="readonly", width=29, font=est.FUENTE_TEXTO)
        self.combo_proposito.pack(pady=(2, 4))

        self.etiqueta_mensaje = ttk.Label(interior, text="", style="Error.TLabel",
                                           wraplength=280)
        self.etiqueta_mensaje.pack(anchor="w", pady=(8, 12))

        ttk.Button(interior, text="Registrar ingreso (queda pendiente)", style="Primario.TButton",
                   command=self._registrar).pack(fill="x")
        ttk.Label(interior, text="Todo ingreso nace en estado 'pendiente' hasta\n"
                                  "que un admin lo autorice o lo rechace.",
                  style="Texto.TLabel", justify="left").pack(anchor="w", pady=(6, 0))

        self.marco_codigo = ttk.Frame(interior, style="Tarjeta.TFrame")
        self.marco_codigo.pack(fill="x", pady=(16, 0))

        # --- Verificación manual de código ---
        ttk.Separator(interior, orient="horizontal").pack(fill="x", pady=16)
        ttk.Label(interior, text="Verificar código de un ingreso",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 8))
        self.entrada_codigo_verificar = ttk.Entry(interior, width=32, font=est.FUENTE_TEXTO)
        self.entrada_codigo_verificar.pack(pady=(2, 8))
        ttk.Button(interior, text="Verificar identidad", style="Secundario.TButton",
                   command=self._verificar).pack(fill="x")
        self.etiqueta_verificacion = ttk.Label(interior, text="", style="Texto.TLabel",
                                                wraplength=280)
        self.etiqueta_verificacion.pack(anchor="w", pady=(8, 0))

        # --- Historial + autorización ---
        tarjeta_lista, interior_lista = est.tarjeta(cuerpo)
        tarjeta_lista.grid(row=0, column=1, sticky="nsew")

        cabecera = ttk.Frame(interior_lista, style="Tarjeta.TFrame")
        cabecera.pack(fill="x", pady=(0, 8))
        ttk.Label(cabecera, text="Historial de ingresos", style="Subtitulo.TLabel").pack(
            side="left")
        ttk.Button(cabecera, text="🔄 Actualizar", style="Secundario.TButton",
                   command=self._refrescar_lista).pack(side="right")

        columnas = ("id", "persona", "area", "proposito", "codigo", "estado", "fecha")
        self.tabla = ttk.Treeview(interior_lista, columns=columnas, show="headings", height=12)
        for col, titulo, ancho in [
            ("id", "ID", 36), ("persona", "Personal", 140), ("area", "Área", 90),
            ("proposito", "Propósito", 90), ("codigo", "Código único", 100),
            ("estado", "Estado", 100), ("fecha", "Fecha/hora", 130),
        ]:
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.pack(fill="both", expand=True, pady=(0, 10))
        self.tabla.tag_configure("pendiente", foreground=est.AMBAR)
        self.tabla.tag_configure("autorizado", foreground=est.VERDE_EXITO)
        self.tabla.tag_configure("rechazado", foreground=est.ROJO_ALERTA)

        # Barra de autorización — solo tiene efecto real si el rol es admin
        self.barra_autorizacion = ttk.Frame(interior_lista, style="Tarjeta.TFrame")
        self.barra_autorizacion.pack(fill="x")
        ttk.Label(self.barra_autorizacion, text="Ingreso seleccionado:",
                  style="Texto.TLabel").pack(side="left", padx=(0, 8))
        self.boton_autorizar = ttk.Button(self.barra_autorizacion, text="✅ Autorizar",
                                           style="Primario.TButton", command=self._autorizar)
        self.boton_autorizar.pack(side="left", padx=4)
        self.boton_rechazar = ttk.Button(self.barra_autorizacion, text="❌ Rechazar",
                                          style="Peligro.TButton", command=self._rechazar)
        self.boton_rechazar.pack(side="left", padx=4)

        self.etiqueta_permiso_autorizacion = ttk.Label(interior_lista, text="",
                                                         style="Texto.TLabel", wraplength=420)
        self.etiqueta_permiso_autorizacion.pack(anchor="w", pady=(8, 0))

    def _refrescar_combo_personal(self):
        opciones = servicio_personal.listar_opciones_para_combo()
        self._mapa_opciones = {etiqueta: pid for pid, etiqueta in opciones}
        self.combo_personal.configure(values=list(self._mapa_opciones.keys()))

    def _refrescar_lista(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for ingreso in servicio.listar_ingresos(self.controlador.rol_actual):
            self.tabla.insert("", "end", values=(
                ingreso.id, ingreso.nombre_completo_personal, ingreso.area_visita,
                ingreso.proposito, ingreso.codigo_unico, ingreso.estado.capitalize(),
                ingreso.fecha_hora), tags=(ingreso.estado,))

        puede_autorizar = permisos.puede_autorizar_ingresos(self.controlador.rol_actual)
        estado_botones = "normal" if puede_autorizar else "disabled"
        self.boton_autorizar.configure(state=estado_botones)
        self.boton_rechazar.configure(state=estado_botones)
        if puede_autorizar:
            self.etiqueta_permiso_autorizacion.configure(
                text="👑 Como admin puedes autorizar o rechazar cualquier ingreso pendiente.")
        else:
            self.etiqueta_permiso_autorizacion.configure(
                text="🔒 Rol operador: solo un admin puede autorizar o rechazar ingresos.")

    def _registrar(self):
        etiqueta_sel = self.combo_personal.get()
        personal_id = self._mapa_opciones.get(etiqueta_sel)
        if personal_id is None:
            self.etiqueta_mensaje.configure(text="Selecciona una persona registrada.")
            return
        try:
            codigo = servicio.registrar_ingreso(
                personal_id, self.entrada_area.get(), self.combo_proposito.get(),
                self.controlador.usuario_actual)
            self.etiqueta_mensaje.configure(text="")
            self._mostrar_codigo_generado(codigo)
            self.entrada_area.delete(0, tk.END)
            self.combo_proposito.set("")
            self._refrescar_lista()
        except servicio.ErrorVerificacion as error:
            self.etiqueta_mensaje.configure(text=str(error))

    def _mostrar_codigo_generado(self, codigo):
        for hijo in self.marco_codigo.winfo_children():
            hijo.destroy()
        ttk.Label(self.marco_codigo, text="Código único generado (Apartado 1):",
                  style="Texto.TLabel").pack(anchor="w")
        campo = tk.Entry(self.marco_codigo, font=est.FUENTE_MONO, justify="center",
                          fg=est.VERDE_OSCURO, relief="solid", bd=1)
        campo.insert(0, codigo)
        campo.configure(state="readonly", readonlybackground=est.GRIS_CLARO)
        campo.pack(fill="x", pady=(4, 0), ipady=6)

    def _verificar(self):
        etiqueta_sel = self.combo_personal.get()
        personal_id = self._mapa_opciones.get(etiqueta_sel)
        codigo = self.entrada_codigo_verificar.get().strip()
        if personal_id is None or not codigo:
            self.etiqueta_verificacion.configure(
                text="Selecciona la persona e ingresa el código.", style="Error.TLabel")
            return
        try:
            valido = servicio.verificar_identidad(personal_id, codigo, self.controlador.rol_actual)
            if valido:
                self.etiqueta_verificacion.configure(text="✅ Identidad verificada correctamente.",
                                                       style="Exito.TLabel")
            else:
                self.etiqueta_verificacion.configure(text="❌ Código no coincide para esa persona.",
                                                       style="Error.TLabel")
        except servicio.ErrorVerificacion as error:
            self.etiqueta_verificacion.configure(text=str(error), style="Error.TLabel")

    def _ingreso_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.etiqueta_permiso_autorizacion.configure(
                text="Selecciona un ingreso de la tabla primero.", style="Error.TLabel")
            return None
        return self.tabla.item(seleccion[0])["values"][0]

    def _autorizar(self):
        ingreso_id = self._ingreso_seleccionado()
        if ingreso_id is None:
            return
        try:
            servicio.autorizar_ingreso(ingreso_id, self.controlador.usuario_actual,
                                        self.controlador.rol_actual)
            self._refrescar_lista()
        except servicio.ErrorVerificacion as error:
            self.etiqueta_permiso_autorizacion.configure(text=str(error), style="Error.TLabel")

    def _rechazar(self):
        ingreso_id = self._ingreso_seleccionado()
        if ingreso_id is None:
            return
        try:
            servicio.rechazar_ingreso(ingreso_id, self.controlador.usuario_actual,
                                       self.controlador.rol_actual)
            self._refrescar_lista()
        except servicio.ErrorVerificacion as error:
            self.etiqueta_permiso_autorizacion.configure(text=str(error), style="Error.TLabel")

    def al_mostrar(self):
        self.etiqueta_mensaje.configure(text="")
        self.etiqueta_verificacion.configure(text="")
        for hijo in self.marco_codigo.winfo_children():
            hijo.destroy()
        self._refrescar_combo_personal()
        self._refrescar_lista()

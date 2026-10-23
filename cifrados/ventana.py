"""Ventana nativa compartida; cada algoritmo aporta sus reglas y funciones."""

from pathlib import Path

from .archivos import guardar_resultado, leer_ruta_archivo
from .validacion import REGLAS_TEXTO, normalizar_letras


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
LIMITE_VISTA_PREVIA = 2000


class AplicacionCifrado:
    """Formulario de una línea o archivo, con resultado copiable y guardado."""

    def __init__(
        self, raiz, *, nombre, descripcion, ayuda_clave, ejemplo,
        prefijo_cifrado, prefijo_descifrado, cifrar, descifrar, validar_clave,
        carpeta=CARPETA_PROYECTO,
    ):
        # Importar Tk aquí permite probar los algoritmos en equipos sin escritorio.
        import tkinter as tk
        from tkinter import ttk

        self.raiz = raiz
        self.carpeta = Path(carpeta)
        self.cifrar = cifrar
        self.descifrar = descifrar
        self.validar_clave = validar_clave
        self.prefijos = {"cifrar": prefijo_cifrado, "descifrar": prefijo_descifrado}
        self.resultado = ""
        self._ajustando = False
        self.operacion = tk.StringVar(value="cifrar")
        self.fuente = tk.StringVar(value="linea")
        self.clave = tk.StringVar()
        self.texto = tk.StringVar()
        self.archivo = tk.StringVar()
        self.preprocesado = tk.StringVar()
        self.estado = tk.StringVar(value="Introduce la clave y el mensaje para empezar.")

        raiz.title(f"{nombre} | A-Z")
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)
        # El tamaño inicial respeta la pantalla; en pantallas pequeñas se permite
        # desplazar el formulario en vez de dejar botones fuera de la ventana.
        self.lienzo = tk.Canvas(raiz, highlightthickness=0, borderwidth=0)
        self.lienzo.grid(row=0, column=0, sticky="nsew")
        self.desplazamiento = ttk.Scrollbar(raiz, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=self.desplazamiento.set)
        cuerpo = self.cuerpo = ttk.Frame(self.lienzo, padding=8)
        self.contenido = self.lienzo.create_window(0, 0, window=cuerpo, anchor="nw")
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.rowconfigure(7, weight=1)

        cabecera = ttk.Frame(cuerpo)
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(cabecera, text=nombre, font=("TkDefaultFont", 18, "bold")).pack(anchor="w")
        ttk.Label(cabecera, text=descripcion, wraplength=700).pack(anchor="w", pady=(4, 0))

        reglas = ttk.LabelFrame(cuerpo, text="Alfabeto inglés de trabajo: A-Z (26 letras)", padding=6)
        reglas.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(reglas, text=REGLAS_TEXTO, wraplength=680).pack(anchor="w", pady=4)
        ttk.Label(reglas, text=ejemplo, wraplength=680).pack(anchor="w")

        operacion = ttk.Frame(cuerpo)
        operacion.grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Label(operacion, text="1. Operación:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(operacion, text="Cifrar", variable=self.operacion, value="cifrar").pack(side="left")
        ttk.Radiobutton(operacion, text="Descifrar", variable=self.operacion, value="descifrar").pack(side="left", padx=12)

        bloque_clave = ttk.LabelFrame(cuerpo, text="2. Clave", padding=8)
        bloque_clave.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        bloque_clave.columnconfigure(0, weight=1)
        self.entrada_clave = ttk.Entry(bloque_clave, textvariable=self.clave)
        self.entrada_clave.grid(row=0, column=0, sticky="ew")
        ttk.Label(bloque_clave, text=ayuda_clave, wraplength=680).grid(row=1, column=0, sticky="w", pady=(5, 0))

        entrada = ttk.LabelFrame(cuerpo, text="3. Mensaje (claro al cifrar, cifrado al descifrar)", padding=8)
        entrada.grid(row=4, column=0, sticky="ew", pady=(0, 4))
        entrada.columnconfigure(1, weight=1)
        ttk.Radiobutton(entrada, text="Una línea", variable=self.fuente, value="linea").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.entrada_texto = ttk.Entry(entrada, textvariable=self.texto)
        self.entrada_texto.grid(row=0, column=1, columnspan=2, sticky="ew")
        ttk.Radiobutton(entrada, text="Archivo .txt", variable=self.fuente, value="archivo").grid(row=1, column=0, sticky="w", pady=6)
        self.ruta_archivo = ttk.Entry(entrada, textvariable=self.archivo, state="disabled")
        self.ruta_archivo.grid(row=1, column=1, sticky="ew", padx=(0, 8))
        self.boton_archivo = ttk.Button(entrada, text="Elegir archivo…", command=self.elegir_archivo, state="disabled")
        self.boton_archivo.grid(row=1, column=2)
        ttk.Label(
            entrada, text="Archivo UTF-8: solo letras, sin BOM ni saltos de línea (tampoco al final).",
            wraplength=680,
        ).grid(row=2, column=0, columnspan=3, sticky="w")
        ttk.Label(entrada, text="Preprocesado:").grid(row=3, column=0, sticky="w", pady=(4, 0))
        self.entrada_preprocesada = ttk.Entry(entrada, textvariable=self.preprocesado, state="readonly")
        self.entrada_preprocesada.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(4, 0))

        acciones = ttk.Frame(cuerpo)
        acciones.grid(row=5, column=0, sticky="ew", pady=(2, 8))
        self.boton_procesar = ttk.Button(acciones, text="Cifrar y guardar", command=self.procesar)
        self.boton_procesar.pack(side="left")
        ttk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left", padx=8)
        ttk.Label(cuerpo, text="4. Resultado en A-Z", font=("TkDefaultFont", 11, "bold")).grid(row=6, column=0, sticky="w")

        marco_resultado = ttk.Frame(cuerpo)
        marco_resultado.grid(row=7, column=0, sticky="nsew", pady=5)
        marco_resultado.rowconfigure(0, weight=1)
        marco_resultado.columnconfigure(0, weight=1)
        self.salida = tk.Text(marco_resultado, height=3, wrap="char", state="disabled", font="TkFixedFont")
        self.salida.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(marco_resultado, orient="vertical", command=self.salida.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.salida.configure(yscrollcommand=barra.set)

        pie = ttk.Frame(cuerpo)
        pie.grid(row=8, column=0, sticky="ew")
        self.boton_copiar = ttk.Button(pie, text="Copiar resultado completo", command=self.copiar, state="disabled")
        self.boton_copiar.pack(anchor="w")
        self.etiqueta_estado = ttk.Label(pie, textvariable=self.estado, wraplength=700)
        self.etiqueta_estado.pack(anchor="w", pady=(6, 0))

        self.etiquetas_ajustables = []
        pendientes = [cuerpo]
        while pendientes:
            widget = pendientes.pop()
            pendientes.extend(widget.winfo_children())
            if isinstance(widget, ttk.Label) and int(widget.cget("wraplength") or 0):
                self.etiquetas_ajustables.append(widget)
                widget.bind("<Configure>", lambda _evento: self.raiz.after_idle(self._ajustar_desplazamiento))
        self.lienzo.bind("<Configure>", self._redimensionar)
        cuerpo.bind("<Configure>", lambda _evento: self._ajustar_desplazamiento())

        # Un resultado deja de corresponder al formulario si cambia cualquier dato.
        for variable in (self.operacion, self.fuente, self.clave, self.texto, self.archivo):
            variable.trace_add("write", self._entrada_modificada)
        raiz.bind("<Control-Return>", lambda _evento: self.procesar())
        self.entrada_clave.focus_set()
        self._centrar_en_pantalla()

    def _centrar_en_pantalla(self):
        self.raiz.update_idletasks()
        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla = self.raiz.winfo_screenheight()
        ancho = min(820, max(320, ancho_pantalla - 80))
        # Reservamos espacio para la barra de título y los paneles del escritorio.
        alto = min(self.cuerpo.winfo_reqheight() + 16, max(240, alto_pantalla - 110))
        x = max(0, (ancho_pantalla - ancho) // 2)
        y = max(20, (alto_pantalla - alto) // 2 - 15)
        self.raiz.minsize(min(640, ancho), min(480, alto))
        self.raiz.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _redimensionar(self, evento):
        self.lienzo.itemconfigure(self.contenido, width=evento.width)
        for etiqueta in self.etiquetas_ajustables:
            etiqueta.configure(wraplength=max(200, evento.width - 50))
        self.raiz.after_idle(self._ajustar_desplazamiento)

    def _ajustar_desplazamiento(self):
        if self._ajustando:
            return
        self._ajustando = True
        try:
            # Esperamos la redistribución de etiquetas antes de medir. Medir antes
            # conserva un alto obsoleto y puede esconder el botón de copia.
            self.cuerpo.update_idletasks()
            alto = max(self.cuerpo.winfo_reqheight(), self.lienzo.winfo_height())
            self.lienzo.itemconfigure(self.contenido, height=alto)
            self.lienzo.configure(scrollregion=(0, 0, self.lienzo.winfo_width(), alto))
            if alto > self.lienzo.winfo_height():
                self.desplazamiento.grid(row=0, column=1, sticky="ns")
            else:
                self.desplazamiento.grid_remove()
                self.lienzo.yview_moveto(0)
        finally:
            self._ajustando = False

    def _mostrar(self, texto):
        self.salida.configure(state="normal")
        self.salida.delete("1.0", "end")
        self.salida.insert("1.0", texto)
        self.salida.configure(state="disabled")

    def _entrada_modificada(self, *_):
        self.resultado = ""
        self.preprocesado.set("")
        self._mostrar("")
        self.boton_copiar.configure(state="disabled")
        self.etiqueta_estado.configure(foreground="")
        self.estado.set("Listo. Se preprocesarán minúsculas, ñ y acentos a A-Z.")
        desde_archivo = self.fuente.get() == "archivo"
        self.entrada_texto.configure(state="disabled" if desde_archivo else "normal")
        self.ruta_archivo.configure(state="readonly" if desde_archivo else "disabled")
        self.boton_archivo.configure(state="normal" if desde_archivo else "disabled")
        verbo = "Cifrar" if self.operacion.get() == "cifrar" else "Descifrar"
        self.boton_procesar.configure(text=f"{verbo} y guardar")

    def elegir_archivo(self):
        from tkinter import filedialog

        ruta = filedialog.askopenfilename(
            parent=self.raiz, title="Selecciona el mensaje de entrada",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*")],
        )
        if ruta:
            self.archivo.set(ruta)

    def procesar(self):
        from tkinter import messagebox

        self._entrada_modificada()
        try:
            self.validar_clave(self.clave.get())
            if self.fuente.get() == "archivo":
                if not self.archivo.get():
                    raise ValueError("Selecciona un archivo con el botón Elegir archivo.")
                texto = leer_ruta_archivo(Path(self.archivo.get()))
            else:
                texto = self.texto.get()
            normalizado = normalizar_letras(texto)
            self.preprocesado.set(normalizado)
            funcion = self.cifrar if self.operacion.get() == "cifrar" else self.descifrar
            resultado = funcion(normalizado, self.clave.get())
        except (ValueError, OSError) as error:
            self.estado.set(f"Revisa la entrada: {error}")
            self.etiqueta_estado.configure(foreground="#b91c1c")
            messagebox.showerror("No se pudo procesar", str(error), parent=self.raiz)
            return

        # La vista previa se limita para mantener ligera la ventana con archivos grandes.
        # Copiar siempre usa el resultado completo, sin el aviso de truncamiento.
        self.resultado = resultado
        self.boton_copiar.configure(state="normal")
        vista = resultado[:LIMITE_VISTA_PREVIA]
        if len(resultado) > LIMITE_VISTA_PREVIA:
            vista += "\n\n[Vista previa: 2000 letras. El archivo y la copia incluyen todo el resultado.]"
        self._mostrar(vista)
        try:
            ruta = guardar_resultado(resultado, self.prefijos[self.operacion.get()], self.carpeta)
        except OSError as error:
            self.estado.set(f"Resultado calculado, pero no guardado: {error}. Puedes copiarlo.")
            self.etiqueta_estado.configure(foreground="#b91c1c")
            messagebox.showwarning("No se pudo guardar", self.estado.get(), parent=self.raiz)
            return
        conversion = " Se aplicó el preprocesamiento a A-Z." if normalizado != texto else ""
        self.estado.set(f"{len(resultado)} letras. Guardado en: {ruta}.{conversion}")
        self.etiqueta_estado.configure(foreground="#166534")

    def copiar(self):
        if self.resultado:
            self.raiz.clipboard_clear()
            self.raiz.clipboard_append(self.resultado)

    def limpiar(self):
        self.clave.set("")
        self.texto.set("")
        self.archivo.set("")
        self.fuente.set("linea")
        self.entrada_clave.focus_set()


def abrir_ventana(**opciones):
    """Abre la interfaz; comunica requisitos faltantes sin un traceback."""
    try:
        import tkinter as tk
    except ImportError:
        raise SystemExit(
            "Falta Tkinter. En Debian/Ubuntu instala python3-tk. "
            "En Windows usa Python con la opción Tcl/Tk. Consulta README.md."
        )
    try:
        raiz = tk.Tk()
    except tk.TclError as error:
        raise SystemExit(f"No se pudo abrir la ventana: {error}. Ejecuta el programa en un escritorio gráfico.")
    raiz.withdraw()
    AplicacionCifrado(raiz, **opciones)
    raiz.deiconify()
    raiz.mainloop()

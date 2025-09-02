import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
import asyncio
import threading
import sys
import os
from pathlib import Path

# Importar las funciones necesarias del proyecto
from webtoon_downloader.cmd.cli import cli as download_webtoon
from webtoon_downloader.cmd.exceptions import (
    CLIInvalidConcurrentCountError,
    CLIInvalidQualityError,
    CLIInvalidStartAndEndRangeError,
    CLILatestWithStartOrEndError,
    CLISeparateOptionWithNonImageSaveAsError,
)

class WebtoonDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Webtoon Downloader")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Configurar el tema oscuro
        self.setup_theme()
        
        # Variables
        self.url_var = tk.StringVar()
        self.start_chapter_var = tk.StringVar()
        self.end_chapter_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.image_format_var = tk.StringVar(value="jpg")
        self.quality_var = tk.IntVar(value=80)
        self.export_metadata_var = tk.BooleanVar(value=False)
        self.export_format_var = tk.StringVar(value="json")
        self.latest_chapter_var = tk.BooleanVar(value=False)
        self.downloading = False
        
        self.setup_ui()
    
    def setup_theme(self):
        """Configura el tema oscuro para la aplicación"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colores mejorados con mayor contraste
        self.bg_color = "#121212"
        self.fg_color = "#e0e0e0"
        self.accent_color = "#1e88e5"
        self.entry_bg = "#1e1e1e"
        self.entry_fg = "#ffffff"
        self.button_bg = "#0d47a1"
        self.highlight_color = "#424242"
        self.text_color = "#f5f5f5"
        self.disabled_color = "#616161"
        
        # Configurar estilos
        self.root.configure(bg=self.bg_color)
        
        # Frame
        self.style.configure('TFrame', 
                           background=self.bg_color,
                           borderwidth=0)
        
        # LabelFrame
        self.style.configure('TLabelframe',
                           background=self.bg_color,
                           foreground=self.fg_color,
                           bordercolor=self.highlight_color,
                           borderwidth=1)
        self.style.configure('TLabelframe.Label',
                           background=self.bg_color,
                           foreground=self.accent_color,
                           font=('Segoe UI', 10, 'bold'))
        
        # Label
        self.style.configure('TLabel', 
                           background=self.bg_color, 
                           foreground=self.fg_color,
                           font=('Segoe UI', 10))
        
        # Entry
        self.style.configure('TEntry',
                           fieldbackground=self.entry_bg,
                           foreground=self.entry_fg,
                           insertcolor=self.fg_color,
                           borderwidth=1,
                           relief='solid')
        
        # Button
        self.style.configure('TButton',
                           background=self.button_bg,
                           foreground=self.text_color,
                           borderwidth=0,
                           font=('Segoe UI', 10, 'bold'),
                           padding=6)
                           
        self.style.map('TButton',
                     background=[('active', self.accent_color),
                                ('disabled', self.disabled_color)],
                     foreground=[('active', self.text_color),
                                ('disabled', self.text_color)])
        
        # Checkbutton
        self.style.configure('TCheckbutton',
                           background=self.bg_color,
                           foreground=self.fg_color,
                           font=('Segoe UI', 10))
        
        # Combobox
        self.style.map('TCombobox',
                     fieldbackground=[('readonly', self.entry_bg)],
                     selectbackground=[('readonly', self.accent_color)],
                     selectforeground=[('readonly', self.text_color)],
                     background=[('readonly', self.entry_bg)],
                     foreground=[('readonly', self.fg_color)])
        
        # Progressbar
        self.style.configure('TProgressbar',
                           background=self.accent_color,
                           troughcolor=self.highlight_color,
                           bordercolor=self.bg_color,
                           lightcolor=self.accent_color,
                           darkcolor=self.accent_color)
        
        # Scrollbar
        self.style.configure('Vertical.TScrollbar',
                           background=self.bg_color,
                           troughcolor=self.highlight_color,
                           bordercolor=self.bg_color,
                           arrowcolor=self.fg_color,
                           arrowsize=15)
        
        # Scale
        self.style.configure('Horizontal.TScale',
                           background=self.bg_color,
                           troughcolor=self.highlight_color,
                           bordercolor=self.bg_color,
                           gripcount=0,
                           sliderthickness=10)
        
        # Configurar el estilo del botón de descarga
        self.style.configure('Accent.TButton',
                           background=self.accent_color,
                           foreground=self.text_color,
                           font=('Segoe UI', 12, 'bold'),
                           padding=10)
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y Scrollbar
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = ttk.Label(
            scrollable_frame, 
            text="Webtoon Downloader",
            font=('Segoe UI', 24, 'bold'),
            foreground=self.accent_color
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de entrada de URL
        url_frame = ttk.Frame(scrollable_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="URL del Webtoon:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Frame de opciones de capítulos
        chapter_frame = ttk.LabelFrame(scrollable_frame, text="Opciones de Capítulos", padding=15)
        chapter_frame.pack(fill=tk.X, pady=10, ipady=5)
        
        # Checkbutton para último capítulo
        latest_cb = ttk.Checkbutton(
            chapter_frame, 
            text="Descargar solo el último capítulo",
            variable=self.latest_chapter_var,
            command=self.toggle_chapter_range,
            style='TCheckbutton'
        )
        latest_cb.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # Rango de capítulos
        ttk.Label(chapter_frame, text="Desde capítulo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        start_entry = ttk.Entry(chapter_frame, textvariable=self.start_chapter_var, width=10)
        start_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(chapter_frame, text="Hasta capítulo:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        end_entry = ttk.Entry(chapter_frame, textvariable=self.end_chapter_var, width=10)
        end_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Frame de opciones de salida
        output_frame = ttk.LabelFrame(scrollable_frame, text="Opciones de Salida", padding=15)
        output_frame.pack(fill=tk.X, pady=10, ipady=5)
        
        # Directorio de salida
        ttk.Label(output_frame, text="Directorio de salida:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW, columnspan=2)
        output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=50)
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        
        browse_btn = ttk.Button(output_dir_frame, text="Examinar...", command=self.browse_output_dir)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Formato de salida
        ttk.Label(output_frame, text="Formato de salida:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Frame para los botones de formato
        format_frame = ttk.Frame(output_frame)
        format_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        
        # Variable para los botones de radio
        self.output_format = tk.StringVar(value="images")  # Por defecto, guardar como imágenes
        
        # Botones de radio para seleccionar el formato
        ttk.Radiobutton(
            format_frame, 
            text="Imágenes (JPG/PNG)",
            variable=self.output_format,
            value="images"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            format_frame,
            text="Archivo CBZ",
            variable=self.output_format,
            value="cbz"
        ).pack(side=tk.LEFT, padx=5)
        
        # Formato de imagen (solo visible cuando se selecciona "Imágenes")
        self.image_format_frame = ttk.Frame(output_frame)
        self.image_format_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        
        ttk.Label(self.image_format_frame, text="Formato de imagen:").pack(side=tk.LEFT, padx=(0, 10))
        format_combo = ttk.Combobox(
            self.image_format_frame, 
            textvariable=self.image_format_var,
            values=["jpg", "png"],
            state="readonly",
            width=10
        )
        format_combo.pack(side=tk.LEFT)
        
        # Calidad
        ttk.Label(output_frame, text="Calidad (40-100, múltiplos de 10):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        quality_frame = ttk.Frame(output_frame)
        quality_frame.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        
        quality_scale = ttk.Scale(
            quality_frame,
            from_=40, 
            to=100, 
            variable=self.quality_var,
            length=200,
            style='Horizontal.TScale'
        )
        quality_scale.pack(side=tk.LEFT)
        
        # Mostrar el valor actual de la calidad
        quality_value = ttk.Label(quality_frame, text=f"{self.quality_var.get()}%")
        quality_value.pack(side=tk.LEFT, padx=10)
        
        # Actualizar el valor mostrado cuando cambia el slider
        def update_quality_value(*args):
            quality_value.config(text=f"{int(self.quality_var.get())}%")
        
        self.quality_var.trace_add('write', update_quality_value)
        
        # Opciones de metadatos
        meta_frame = ttk.Frame(output_frame)
        meta_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        meta_cb = ttk.Checkbutton(
            meta_frame, 
            text="Exportar metadatos",
            variable=self.export_metadata_var
        )
        meta_cb.pack(side=tk.LEFT, padx=5)
        
        format_combo = ttk.Combobox(
            meta_frame, 
            textvariable=self.export_format_var,
            values=["json", "text", "all"],
            state="readonly",
            width=10
        )
        format_combo.pack(side=tk.LEFT, padx=5)
        
        # Botón de descarga
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=20)
        
        self.download_btn = ttk.Button(
            button_frame, 
            text="Descargar Webtoon",
            command=self.start_download,
            style='Accent.TButton',
            width=25
        )
        self.download_btn.pack(pady=10, ipady=8)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            scrollable_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=10)
        
        # Estado
        self.status_var = tk.StringVar(value="Listo")
        status_label = ttk.Label(
            scrollable_frame, 
            textvariable=self.status_var,
            foreground=self.accent_color,
            font=('Segoe UI', 9, 'italic')
        )
        status_label.pack(pady=5)
        
        # Configurar el grid para que se expanda correctamente
        for i in range(3):
            output_frame.columnconfigure(i, weight=1 if i == 1 else 0)
        
        # Actualizar la visibilidad del frame de formato de imagen según la selección
        def update_image_format_visibility(*args):
            if hasattr(self, 'image_format_frame'):
                if self.output_format.get() == 'images':
                    self.image_format_frame.grid()
                else:
                    self.image_format_frame.grid_remove()
        
        self.output_format.trace_add('write', update_image_format_visibility)
        update_image_format_visibility()
    
    def toggle_chapter_range(self):
        """Habilita/deshabilita los campos de rango de capítulos"""
        state = 'disabled' if self.latest_chapter_var.get() else 'normal'
        self.start_chapter_var.set('' if self.latest_chapter_var.get() else self.start_chapter_var.get())
        self.end_chapter_var.set('' if self.latest_chapter_var.get() else self.end_chapter_var.get())
        
        for widget in [w for w in self.root.winfo_children() if 'entry' in str(w).lower()]:
            if widget.winfo_parent().endswith('!labelframe2'):  # Frame de opciones de capítulos
                widget.configure(state=state)
    
    def browse_output_dir(self):
        """Abre un diálogo para seleccionar el directorio de salida"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def validate_inputs(self) -> bool:
        """Valida los campos de entrada"""
        if not self.url_var.get().strip():
            messagebox.showerror("Error", "Por favor ingresa la URL del webtoon")
            return False
            
        if not self.latest_chapter_var.get():
            try:
                start = self.start_chapter_var.get().strip()
                end = self.end_chapter_var.get().strip()
                
                if start and not start.isdigit():
                    messagebox.showerror("Error", "El capítulo inicial debe ser un número")
                    return False
                    
                if end and not end.isdigit():
                    messagebox.showerror("Error", "El capítulo final debe ser un número")
                    return False
                    
                if start and end and int(start) > int(end):
                    messagebox.showerror("Error", "El capítulo inicial no puede ser mayor al final")
                    return False
                    
            except ValueError:
                messagebox.showerror("Error", "Error al validar los capítulos")
                return False
        
        return True
    
    def start_download(self):
        """Inicia la descarga en un hilo separado"""
        if self.downloading:
            return
            
        if not self.validate_inputs():
            return
            
        self.downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.status_var.set("Preparando descarga...")
        self.progress_var.set(0)
        
        # Crear y ejecutar el hilo de descarga
        download_thread = threading.Thread(target=self.run_download, daemon=True)
        download_thread.start()
        
        # Iniciar el monitoreo de progreso
        self.monitor_progress()
    
    def run_download(self):
        """Ejecuta la descarga del webtoon"""
        try:
            # Construir los argumentos para la línea de comandos
            args = [self.url_var.get()]
            
            # Opciones de capítulos
            if self.latest_chapter_var.get():
                args.append("--latest")
            else:
                if self.start_chapter_var.get().strip():
                    args.extend(["--start", self.start_chapter_var.get().strip()])
                if self.end_chapter_var.get().strip():
                    args.extend(["--end", self.end_chapter_var.get().strip()])
            
            # Opciones de salida
            args.extend(["--out", self.output_dir_var.get()])
            
            # Formato de salida
            if self.output_format.get() == "cbz":
                args.extend(["--save-as", "cbz"])
            else:
                args.extend(["--image-format", self.image_format_var.get()])
                args.extend(["--quality", str(self.quality_var.get())])
            
            # Metadatos
            if self.export_metadata_var.get():
                args.append("--export-metadata")
                args.extend(["--export-format", self.export_format_var.get()])
            
            # Configurar sys.argv para la función cli
            import sys
            import os
            import subprocess
            
            # Crear un nuevo proceso en lugar de un hilo
            def run_download_process():
                try:
                    # Usar el mismo intérprete de Python que está ejecutando la aplicación
                    python_exec = sys.executable
                    
                    # Construir el comando con todos los argumentos necesarios
                    cmd = [python_exec, "-m", "webtoon_downloader"] + args
                    
                    # Mostrar el comando que se va a ejecutar (para depuración)
                    print("Ejecutando:", " ".join(cmd))
                    
                    # Configurar el entorno
                    env = os.environ.copy()
                    
                    # Ejecutar el comando
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        env=env,
                        shell=True  # Usar shell=True para manejar mejor los comandos en Windows
                    )
                    
                    # Leer la salida en tiempo real
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(output.strip())
                            self.root.after(0, lambda o=output.strip(): self.status_var.set(o))
                    
                    # Verificar si hubo errores
                    _, stderr = process.communicate()
                    if process.returncode != 0:
                        error_msg = stderr if stderr else "Error desconocido en la descarga"
                        raise Exception(error_msg)
                    
                    # Actualizar la interfaz de usuario en el hilo principal
                    self.root.after(0, lambda: self.status_var.set("¡Descarga completada!"))
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error durante la descarga: {error_msg}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", 
                        f"Error durante la descarga: {error_msg}"
                    ))
                    self.root.after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
                finally:
                    # Restaurar el estado
                    self.root.after(0, lambda: setattr(self, 'downloading', False))
                    self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
            
            # Iniciar el proceso en un hilo separado
            import threading
            download_thread = threading.Thread(target=run_download_process, daemon=True)
            download_thread.start()
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error al iniciar la descarga: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error al iniciar la descarga: {error_msg}"
            ))
            self.root.after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
            self.root.after(0, lambda: setattr(self, 'downloading', False))
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
    
    def monitor_progress(self):
        """Actualiza la barra de progreso"""
        if self.downloading:
            # Aquí podrías implementar la lógica para actualizar el progreso
            # basado en el progreso real de la descarga
            current = self.progress_var.get()
            if current < 90:  # Simular progreso
                self.progress_var.set(current + 1)
            
            self.root.after(100, self.monitor_progress)

def main():
    root = tk.Tk()
    app = WebtoonDownloaderGUI(root)
    
    # Manejar el cierre de la ventana
    def on_closing():
        if app.downloading:
            if messagebox.askokcancel("Salir", "La descarga está en progreso. ¿Estás seguro de que quieres salir?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

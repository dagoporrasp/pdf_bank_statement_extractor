from ttkbootstrap.constants import *
import ttkbootstrap as tb
from tkinter import filedialog
import tkinter as tk
import webbrowser
from bank_parsers.bank_pdf_parsers import bank_parsers_list
from parsers_pdf import ProcesadorExtractosBancarios
from pathlib import Path
import ctypes

# TODO:
# 1. Aplicar el backend -> ProcesadorExtractosBancarios
myappid = "mycompany.myproduct.ProcesadorExtractosBancarios.v1"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def callback(url):
    webbrowser.open_new(url)


def set_obj_text(obj, text):
    # my_label.config(text=f"You selected {x}")
    obj.config(text=f"{text}")


class GUIExtractosBancarios(tb.Window):
    def __init__(self, *args, **kwargs):
        tb.Window.__init__(self, themename="darkly")
        self.geometry("450x500")
        self.resizable(False, False)
        self.title("Procesador de Extractos Bancarios")
        icono_16 = tb.PhotoImage(file="hamburguesa.png")
        icono_32 = tb.PhotoImage(file="hamburguesax32.png")
        self.iconphoto(False, icono_32, icono_16)

        # creating a container
        container = tb.Frame(self, bootstyle=DARK)
        container.pack(side="top", fill="both", expand=True)

        container.configure(width=550, height=550)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (HomePage, Page1):  # , Page1
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky=NS)

        self.show_frame(HomePage)

        # Footer
        link1 = tk.Label(
            container, text="Desarrollado por @dago.porras\n 2023", cursor="hand2"
        )
        link1.bind("<Button-1>", lambda e: callback("https://twitter.com/DagoPorras"))
        link1.grid(row=1, column=0, padx=0, pady=(0, 7))
        # link1.pack(side=BOTTOM)
        link1.config(bg="#303030", font=("Calibri", 8))

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def destroy_frame(self, cont):
        frame = self.frames[cont]
        try:
            frame.grid_forget()
            frame.destroy()
        except tk._tkinter.TclError as e:
            pass

    def show_destroy_frame(self, show_cont, destroy_cont):
        # s_frame = self.frames[show_cont]
        # d_frame = self.frames[destroy_cont]
        self.destroy_frame(destroy_cont)
        self.show_frame(show_cont)


# first window frame startpage


class HomePage(tb.Frame):
    def __init__(self, parent, controller):
        tb.Frame.__init__(self, parent, bootstyle=DARK)
        # home_frame = Frame(root)
        label1 = tk.Label(self, text="Procesador de \nExtractos \nBancarios PDF")
        label2 = tk.Label(
            self,
            text="El procesador permite llevar\n tu extracto bancario en PDF\n a un Excel. Dale Empezar\n y sigue las instrucciones.",
        )
        label1.grid(row=0, column=0, padx=0, pady=15)
        label2.grid(row=1, column=0, padx=0, pady=10)
        # Footer---------------
        # year_label = tk.Label(self, text="2023")
        # year_label.grid(row=8, column=0, padx=0, pady=(0, 0))
        # link1 = tk.Label(
        #     self, text="Desarrollado por @dago.porras\n 2023", cursor="hand2"
        # )
        # link1.bind("<Button-1>", lambda e: callback("https://twitter.com/DagoPorras"))
        # ------------------------------
        start_btb = tb.Button(
            self,
            text="Empezar",
            bootstyle=LIGHT,
            command=lambda: controller.show_destroy_frame(Page1, HomePage),
        )

        # --------------------------
        # PACKS & CONFIGS
        # print(label1.configure().keys())
        # home_frame.pack(fill=BOTH, anchor=W, expand=True)
        # self.pack(fill=BOTH, anchor=W, expand=True)
        # label2.pack(side=TOP)
        # label1.pack(side=TOP, pady=30)
        label1.config(bg="#303030", font=("Calibri", 25, "bold"), justify=LEFT)

        # label2.pack(side=TOP)
        label2.config(bg="#303030", font=("Calibri", 12), justify=LEFT)

        # start_btb.pack(side=TOP, pady=85)
        start_btb.grid(row=4, column=0, padx=0, pady=40)

        # year_label.pack(side=BOTTOM)
        # year_label.config(bg="#303030", font=("Calibri", 8))
        # link1.pack(side=BOTTOM)
        # link1.grid(row=5, column=0, padx=0, pady=(100,))
        # # link1.pack(side=BOTTOM)
        # link1.config(bg="#303030", font=("Calibri", 8))

        # label3.pack(side=BOTTOM)
        # label3.config(bg="#303030", font=("Calibri", 10), justify=LEFT)
        # print(label2.configure().keys())
        # tb.Entry(container).pack()
        self.pack_propagate(False)
        # home_frame.pack_propagate(False)
        self.configure(width=550, height=550)


# second window frame page1
class Page1(tb.Frame):
    def __init__(self, parent, controller):
        tb.Frame.__init__(self, parent, bootstyle=DARK)
        # ---------------------> Track variables
        # bank_acc_type = tk.StringVar()
        # bank_acc_type.trace_add("write", process)
        # ---------------------> 1. PROCESADOR DE EXTRACTOS INPUT
        labelb1 = tk.Label(self, text="1. Procesador de Extractos PDF:")
        labelb1.config(bg="#303030", font=("Calibri", 12), justify=LEFT)
        labelb1.grid(row=0, column=0, padx=0, pady=(20, 0))
        b1 = tb.Menubutton(
            self,
            text="Selecciona una opción",
            bootstyle=LIGHT,
        )
        b1.grid(row=1, column=0, pady=0)
        inside_b1 = tb.Menu(b1)
        item_var = tb.StringVar()
        for banco, parser in bank_parsers_list.items():
            for tipo_cuenta in parser.keys():
                label = banco + " - " + tipo_cuenta
                inside_b1.add_radiobutton(
                    label=label,
                    variable=item_var,
                    command=lambda label=label: set_obj_text(b1, label),
                )
                b1["menu"] = inside_b1
        # print(b1.keys())
        # labelb1 = tk.Label(self, text="1. Procesador de Extractos PDF:")
        # labelb1.config(bg="#303030", font=("Calibri", 12), justify=LEFT)
        # labelb1.grid(row=0, column=0, padx=0, pady=(20, 0))
        # ---------------------> 2. CONTRASEÑA PDF INPUT
        labelpwd = tk.Label(self, text="2. Contraseña de PDF:")
        labelpwd.config(bg="#303030", font=("Calibri", 12), justify=LEFT)
        labelpwd.grid(row=2, column=0, padx=0, pady=(20, 0))
        # pwd_input = tb.Entry(self, show="*", bootstyle=LIGHT)
        pwd_input = tk.Entry(
            self,
            show="*",
        )
        pwd_input.config(
            highlightcolor="white", bg="#ADB5BD", font=("Calibri", 12), justify=LEFT
        )
        # pwd_input["textvariable"] =
        pwd_input.grid(row=3, pady=0)

        # ----------------------> 3. Carga tu archivo
        # labelfile = tk.Label(self, text="3. Elige un extracto en PDF:")
        # labelfile.config(bg="#303030", font=("Calibri", 12), justify=LEFT)
        # labelfile.grid(row=4, column=0, padx=0, pady=(5, 0))
        # dirVar = tk.StringVar()
        # filet_btn = tb.Button(
        #     self, text="Examinar", bootstyle=LIGHT, command=self.ask_dir_input
        # )
        # filet_btn.grid(row=5, pady=5)
        # -----------------------> 4. Guardar Como
        labeloutput = tk.Label(self, text="3. Guardar como:")
        labeloutput.config(bg="#303030", font=("Calibri", 12), justify=LEFT)
        labeloutput.grid(row=6, column=0, padx=0, pady=(5, 0))
        b2 = tb.Menubutton(self, text="Selecciona una opción", bootstyle=LIGHT)
        b2.grid(row=7, column=0, padx=0, pady=(5, 0))
        # b2.pack(side=TOP, padx=5, pady=10)
        inside_b2 = tb.Menu(b2)
        item_var_2 = tb.StringVar()
        for format in ProcesadorExtractosBancarios.output_formats:
            inside_b2.add_radiobutton(
                label=format,
                variable=item_var_2,
                command=lambda format=format: set_obj_text(b2, format),
            )
            b2["menu"] = inside_b2

        # ------------------------> 5. Procesar Archivo | Procesar Directorio
        processlabel = tk.Label(self, text="4. Procesar:")
        processlabel.config(bg="#303030", font=("Calibri", 12), justify=LEFT)
        processlabel.grid(row=8, column=0, padx=0, pady=(5, 0))

        btn_container = tb.Frame(self, bootstyle=DARK)
        btn_container.configure(width=50, height=50)
        # btn_container.grid_rowconfigure(1, weight=1)
        btn_container.grid_columnconfigure(2, weight=1)

        process_file_btn = tb.Button(
            btn_container,
            text="Archivo",
            bootstyle=LIGHT,
            command=lambda: process_file(item_var, pwd_input, item_var_2),
        )
        process_file_btn.grid(row=0, column=0, pady=5, padx=4)
        process_dir_btn = tb.Button(
            btn_container,
            text="Directorio",
            bootstyle=LIGHT,
            command=lambda: process_directory(item_var, pwd_input, item_var_2),
        )
        process_dir_btn.grid(row=0, column=1, pady=5)

        btn_container.grid(row=9, pady=5)

        #  ----------------------------------------->
        self.pack_propagate(False)
        # home_frame.pack_propagate(False)
        self.configure(
            width=550,
            height=550,
        )


def ask_dir_input():
    dirname = filedialog.askdirectory()
    if dirname:
        return dirname


def ask_file_input():
    filename = filedialog.askopenfilename()
    if filename:
        return filename


def process_file(bank_acc_type, password, outputFormat):
    filename = ask_file_input()
    if filename:
        filename = Path(filename)
        process_flag = tk.messagebox.askquestion(
            "confirmacion", f"Estas seguro de procesar {filename.name}?"
        )
        if process_flag == "yes":
            bank, acc_type = bank_acc_type.get().split(" - ")
            password = password.get()
            print("procesando...")
            processor = ProcesadorExtractosBancarios(bank, acc_type)
            results = processor.process_bank_pdf(filename, password)
            processor.save(outputFormat.get(), results, Path("temp"))
            output_str = f"Archivo procesados: {filename.name}\n"
            output_str += f"Salida\n"
            for i, result in enumerate(results.keys()):
                output_str += f"[-] {result}\n"
            tk.messagebox.showinfo(message=output_str)


def process_directory(bank_acc_type, password, outputFormat):
    dirname = ask_dir_input()
    if dirname:
        dirname = Path(dirname)
        n_pdf_files = len(list(dirname.glob("*.pdf")))
        process_flag = tk.messagebox.askquestion(
            "confirmacion",
            f"Estas seguro de procesar\nArchivos PDF: {n_pdf_files}\ncarpeta: {dirname.name}",
        )
        if process_flag == "yes":
            bank, acc_type = bank_acc_type.get().split(" - ")
            password = password.get()
            print("procesando...")
            processor = ProcesadorExtractosBancarios(bank, acc_type)
            results = processor.process_bank_pdf_dir(dirname, password)
            processor.save(outputFormat.get(), results, Path("temp"))
            output_str = f"Archivos procesados: {n_pdf_files}\n"
            output_str += f"Salida\n"
            for i, result in enumerate(results.keys()):
                output_str += f"[-] {result}\n"
            tk.messagebox.showinfo(message=output_str)
        # print(password.get())
        # print(dirname)
        # print(outputFormat.get())
    # file = request.files.get("file")
    # bank_acc_type = b1
    # print(bank_acc_type)
    # password = request.form.get("password")
    # output_format = request.form.get("output_format")
    # flexRadioDefault1 = request.form.get("flexRadioDefault")


# Driver Code
app = GUIExtractosBancarios()
app.mainloop()

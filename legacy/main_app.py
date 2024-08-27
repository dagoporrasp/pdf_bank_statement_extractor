from tkinter import filedialog
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from bank_parsers.bank_pdf_parsers import bank_parsers_list
from parsers_pdf import ProcesadorExtractosBancarios
import webbrowser


def set_obj_text(obj, text):
    # my_label.config(text=f"You selected {x}")
    obj.config(text=f"{text}")


root = tb.Window(themename="darkly")
# root = Tk()
root.title("Procesador de Extractos Bancarios v1.0")
root.geometry("500x350")

# -------- INPUT PROCESADOR DE EXTRACTOS
b1 = tb.Menubutton(root, text="1. Procesador de Extractos PDF", bootstyle=LIGHT)
b1.pack(side=TOP, padx=5, pady=10)
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
# -------- INPUT Pdf password
pwd_input = tb.Entry(root, bootstyle="light")
# pwd_input["textvariable"] =
pwd_input.insert(END, "Contraseña")
pwd_input.pack(side=TOP, pady=5)


# -------- TIPO de PRocesamiento: ARCHIVO / DIR
# dir_input =
def ask_dir_input():
    filedialog.askdirectory()


three = tb.Button(root, text="Elegir archivo", bootstyle=LIGHT, command=ask_dir_input)
three.pack(side=TOP, pady=5)

# -------- INPUT Output format
label2 = tb.Label(root, text="Formato de Salida")
label2.pack(side=TOP)
b2 = tb.Menubutton(root, text="Selecciona una opción", bootstyle=LIGHT)
b2.pack(side=TOP, padx=5, pady=10)
inside_b2 = tb.Menu(b2)
item_var_2 = tb.StringVar()
for format in ProcesadorExtractosBancarios.output_formats:
    inside_b2.add_radiobutton(
        label=format,
        variable=item_var_2,
        command=lambda format=format: set_obj_text(b2, format),
    )
b2["menu"] = inside_b2


# -------- File / Path
# ----->Procesar
def process():
    print("procesando...")


process_btb = tb.Button(root, text="procesar", bootstyle=LIGHT, command=process)
process_btb.pack(side=TOP, pady=5)


# Function Declaration
def callback(url):
    webbrowser.open_new(url)


# Button Declaration
year_label = tb.Label(root, text="2023")
year_label.pack(side=BOTTOM, pady=2)
link1 = tb.Label(root, text="Desarrollado por @dago.porras", cursor="hand2")
link1.bind("<Button-1>", lambda e: callback("https://twitter.com/DagoPorras"))
link1.pack(side=BOTTOM, pady=2)

root.mainloop()

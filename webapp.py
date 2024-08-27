from flask import Flask, render_template, request
from bank_parsers.bank_pdf_parsers import bank_parsers_list
from parsers_pdf import ProcesadorExtractosBancarios

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./data"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/procesador", methods=["GET", "POST"])
def procesador():
    if request.method == "POST":
        file = request.files.get("file")
        bank_acc_type = request.form.get("bank_acc_type")
        password = request.form.get("password")
        output_format = request.form.get("output_format")
        flexRadioDefault1 = request.form.get("flexRadioDefault")
        # flexRadioDefault2 = request.form.get("flexRadioDefault")
        print(file.filename)
        print(bank_acc_type)
        # print(password)
        # print(output_format)
        # print(dir(flexRadioDefault1))
        # print(flexRadioDefault2)
        print(dir(file))
        # if request.form.get("ProcesarArchivoBttn") == "Archivo":
        #     # data_path = Path("data", "davivienda")
        #     app = ProcesadorExtractosBancarios(bank_acc_type.split("_"))
        #     results = app.process_bank_pdf_dir(data_path, _PASSWORD)
        #     app.save("Excel", results, Path("temp"))
        # if request.form.get("ProcesarDirBttn") == "Directorio":
        #     print("Directorio")
    return render_template(
        "procesador.html", bancos_dict=bank_parsers_list, output_format=["Excel"]
    )


if __name__ == "__main__":
    print(bank_parsers_list)
    app.run(debug=True)

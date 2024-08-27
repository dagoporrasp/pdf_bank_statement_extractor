import pdfplumber
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from bank_parsers.bank_pdf_parsers import make_bank_parser


# ---- TODO
# ---- APP-procesador de extractos
# funciones
# export -> excel()


class ProcesadorExtractosBancarios:
    output_formats = ["Excel"]

    def __init__(self, Bank: str, acc_type: str) -> None:
        self.acc_type = acc_type
        self.Bank = Bank
        self.bank_pdf_parser = make_bank_parser(Bank, acc_type)
        # print(self.bank_pdf_parser.resultados_list)

    def process_bank_pdf(self, input_path: Path, password: str) -> list[pd.DataFrame]:
        bank_data = self.bank_pdf_parser.parse_pdf(input_path, password)
        results_labels = self.bank_pdf_parser.resultados_list
        processing_results = self.bank_pdf_parser.process(bank_data)
        results = {
            label: result for label, result in zip(results_labels, processing_results)
        }
        return results

    def process_bank_pdf_dir(self, dir_path: Path, password: str) -> list[pd.DataFrame]:
        pdf_files = dir_path.glob("*.pdf")
        results_labels = self.bank_pdf_parser.resultados_list
        historic_results = {label: [] for label in results_labels}
        for file in pdf_files:
            print(file.name)
            results = self.process_bank_pdf(file, password)
            for label, result in results.items():
                historic_results[label].append(result)
        for label in results_labels:
            print(label)
            # print(historic_results)
            for result in historic_results[label]:
                print(result.info())
            print(len(historic_results[label]))
            historic_results[label] = pd.concat(historic_results[label])
        return historic_results

    def save(
        self, format: str, results: dict[str, pd.DataFrame], out_dir: Path
    ) -> None:
        if format == "Excel":
            for label, result in results.items():
                output = out_dir / f"{self.Bank}_{self.acc_type}_{label}.xlsx"
                print(f"Exportando {output}")
                result.to_excel(output, index=False, sheet_name=label)

import pdfplumber
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from bank_parsers.bank_pdf_parser_class import BankPDFParser
from itertools import chain


@dataclass
class Rappi_cc_data:
    resumen: pd.DataFrame
    cash_back: pd.DataFrame
    detalle_pago_minimo: pd.DataFrame
    detalle_pago_total: pd.DataFrame
    detalle_transacciones: pd.DataFrame
    year: str
    month: str


def find_inv_vertical_line_by_ch(page, ch):
    for char in page.chars:
        if char["text"] == ch:
            return char["bottom"]


def format_money_column(money_col):
    money_col = money_col.str.replace("$", "")
    money_col = money_col.str.replace(".", "")
    money_col = money_col.str.replace(",", ".")
    # money_col = money_col.str.replace(r"N/A", pd.NA)
    return pd.to_numeric(money_col, errors="coerce")


class RappiPDFParser(BankPDFParser):
    resultados_list = [
        "resumen",
        "cash_back",
        "detalle_pago_minimo",
        "detalle_pago_total",
        "detalle_transacciones",
    ]

    def parse_pdf(self, input_path, password):
        with pdfplumber.open(input_path, password=password) as pdf:
            # print(pdf.pages)
            # RESUMEN
            text_content = pdf.pages[0].extract_text()
            if text_content.find("Dirección") == -1:
                y0 = 250
            else:
                y0 = 275
            y1 = y0 + 100
            c1 = pdf.pages[0].crop((0, y0, 160, y1)).extract_text().split("\n")
            c1 = [t.split(":") for t in c1]
            c11 = list(chain(*c1[:2]))
            c1 = c1[2:]
            c1.append(c11)
            c2 = pdf.pages[0].crop((170, y0, 285, y1)).extract_text().split("\n")
            # print(c2)
            c2 = [[c2[0], c2[1]], [c2[2], c2[3]]]
            c3 = pdf.pages[0].crop((300, y0, 400, y1)).extract_text().split("\n")
            c3 = [
                [c3[0] + " " + c3[1][:5], c3[1][5:]],
                [c3[0] + " " + c3[2][:5], c3[2][5:]],
            ]
            c4 = pdf.pages[0].crop((420, 250, 550, 350)).extract_text().split("\n")
            c4 = c4[:2]
            date_str = c3[-1][-1].split(" ")
            year = date_str[-1]
            month = date_str[-2].upper()
            # print(year, month)
            c = c1 + c2 + c3 + [c4]

            # CASH BACK
            cs1 = pdf.pages[0].crop((0, 400, 130, 450)).extract_text().split("\n")
            cs2 = pdf.pages[0].crop((150, 400, 255, 450)).extract_text().split("\n")
            cs3 = pdf.pages[0].crop((275, 385, 415, 450)).extract_text().split("\n")
            cs3 = [[cs3[0] + " " + cs3[2], cs3[1]], cs3[3].split("$")]
            cs4 = pdf.pages[0].crop((450, 400, 550, 450)).extract_text().split("\n")
            cs = [cs2, cs4] + cs3

            # Detalle de pago minimo
            dt1 = (
                pdf.pages[0]
                .crop((0, 475, 275, 820))
                .extract_table(
                    table_settings={
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }
                )
            )
            dt11 = [dt1[-5][0] + " " + dt1[-3][0], dt1[-4][-1]]
            dt1.pop(-5)
            dt1.pop(-4)
            dt1.pop(-3)
            dt1.insert(-2, dt11)
            dt12 = [dt1[-7][0] + " " + dt1[-5][0], dt1[-6][-1]]
            dt1.pop(-7)
            dt1.pop(-6)
            dt1.pop(-5)
            dt1.insert(-3, dt12)

            # Detalle de pago total
            dt2 = (
                pdf.pages[0]
                .crop((300, 475, 550, 820))
                .extract_table(
                    table_settings={
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }
                )
            )
            dt22 = [dt2[-7][0] + " " + dt2[-5][0], dt2[-6][-1]]
            dt2.pop(-7)
            dt2.pop(-6)
            dt2.pop(-5)
            dt2.insert(-3, dt22)

            #  Detalle de transacciones
            # dt3 = pdf.pages[1].extract_table(
            #     table_settings={
            #         "vertical_strategy": "text",
            #         "horizontal_strategy": "lines",
            #         "explicit_horizontal_lines": [149],
            #     }
            # )
            lv = find_inv_vertical_line_by_ch(pdf.pages[1], "j")
            # lv2 = find_inv_vertical_line_by_ch(pdf.pages[1], "j")

            dt3 = pdf.pages[1].extract_table(
                table_settings={
                    "vertical_strategy": "explicit",
                    "horizontal_strategy": "lines",
                    "explicit_vertical_lines": [
                        45,
                        75,
                        115,
                        190,
                        275,
                        350,
                        400,
                        475,
                        525,
                        550,
                    ],
                    "explicit_horizontal_lines": [lv + 5],
                }
            )

            # print(dt3)

            resumen = pd.DataFrame(c)
            cash_back = pd.DataFrame(cs)
            detalle_pago_minimo = pd.DataFrame(dt1)
            detalle_pago_total = pd.DataFrame(dt2)
            detalle_transacciones = pd.DataFrame(dt3)
            return Rappi_cc_data(
                resumen,
                cash_back,
                detalle_pago_minimo,
                detalle_pago_total,
                detalle_transacciones,
                year,
                month,
            )

    def process_rappi_resumen(self, rappi_data):
        resumen = rappi_data.resumen.T
        resumen.columns = resumen.iloc[0, :]
        resumen = resumen.drop(resumen.iloc[0, :].name).reset_index(drop=True)
        resumen[["Cupo total", "Cupo utilizado", "Pago mínimo", "Pago total"]] = (
            resumen[
                ["Cupo total", "Cupo utilizado", "Pago mínimo", "Pago total"]
            ].apply(format_money_column)
        )
        return resumen

    def process_rappi_cash_back(self, rappi_data):
        cash_back = rappi_data.cash_back.T
        cash_back.columns = cash_back.iloc[0, :]
        cash_back = cash_back.drop(cash_back.iloc[0, :].name).reset_index(drop=True)
        cash_back = cash_back.apply(format_money_column)
        cash_back["Año"] = rappi_data.year
        cash_back["mes"] = rappi_data.month
        return cash_back

    def process_rappi_detalle_pago_minimo(self, rappi_data):
        detalle_pago_minimo = rappi_data.detalle_pago_minimo
        detalle_pago_minimo = detalle_pago_minimo.replace("", pd.NA).dropna(how="all")
        detalle_pago_minimo = detalle_pago_minimo.iloc[1:].T
        detalle_pago_minimo.columns = detalle_pago_minimo.iloc[0, :]
        detalle_pago_minimo = detalle_pago_minimo.drop(
            detalle_pago_minimo.iloc[0, :].name
        ).reset_index(drop=True)
        detalle_pago_minimo = detalle_pago_minimo.apply(format_money_column)
        detalle_pago_minimo["Año"] = rappi_data.year
        detalle_pago_minimo["mes"] = rappi_data.month
        return detalle_pago_minimo

    def process_rappi_detalle_pago_total(self, rappi_data):
        detalle_pago_total = rappi_data.detalle_pago_total.replace("", pd.NA).dropna(
            how="all"
        )
        detalle_pago_total = detalle_pago_total.iloc[1:].T
        detalle_pago_total.columns = detalle_pago_total.iloc[0, :]
        detalle_pago_total = detalle_pago_total.drop(
            detalle_pago_total.iloc[0, :].name
        ).reset_index(drop=True)
        detalle_pago_total = detalle_pago_total.apply(format_money_column)
        detalle_pago_total["Año"] = rappi_data.year
        detalle_pago_total["mes"] = rappi_data.month
        return detalle_pago_total

    def process_rappi_detalle_transacciones(self, rappi_data):
        detalle_transacciones = rappi_data.detalle_transacciones
        detalle_transacciones = detalle_transacciones.apply(
            lambda x: x.str.replace("$", "")
        )
        detalle_transacciones = detalle_transacciones.apply(
            lambda x: x.str.replace("\n", "")
        )
        detalle_transacciones = detalle_transacciones.replace("", pd.NA).dropna(
            how="all"
        )
        detalle_transacciones = detalle_transacciones.dropna(how="all", axis=1)
        if detalle_transacciones[3].isna().sum() >= 0.8 * len(detalle_transacciones):
            detalle_transacciones.pop(3)
        if len(detalle_transacciones.columns) == 9:
            detalle_transacciones.columns = [
                "Tarjeta",
                "Fecha",
                "Descripcion",
                "Valor transaccion",
                "Capital facturado del periodo",
                "Cuotas",
                "Capital pendiented por facturar",
                "Tasa MV",
                "Tasa EA",
            ]
        detalle_transacciones = detalle_transacciones.loc[
            detalle_transacciones["Tarjeta"].isin(["Virtual", "Fisica", "-"])
        ]
        detalle_transacciones[
            [
                "Valor transaccion",
                "Capital facturado del periodo",
                "Capital pendiented por facturar",
            ]
        ] = detalle_transacciones[
            [
                "Valor transaccion",
                "Capital facturado del periodo",
                "Capital pendiented por facturar",
            ]
        ].apply(
            format_money_column
        )
        return detalle_transacciones

    def process(self, rappi_data: Rappi_cc_data) -> list[pd.DataFrame]:
        resumen = self.process_rappi_resumen(rappi_data)
        cash_back = self.process_rappi_cash_back(rappi_data)
        detalle_pago_minimo = self.process_rappi_detalle_pago_minimo(rappi_data)
        detalle_pago_total = self.process_rappi_detalle_pago_total(rappi_data)
        detalle_transacciones = self.process_rappi_detalle_transacciones(rappi_data)
        return (
            resumen,
            cash_back,
            detalle_pago_minimo,
            detalle_pago_total,
            detalle_transacciones,
        )


# # TODO:
# pdf_files = data_path.glob("*.pdf")
# historic_resumen = []
# historic_cash_back = []
# historic_detalle_pago_minimo = []
# historic_detalle_pago_total = []
# historic_detalle_transacciones = []

# for file in pdf_files:
#     print(file.name)

#     historic_resumen.append(resumen)
#     historic_cash_back.append(cash_back)
#     historic_detalle_pago_minimo.append(detalle_pago_minimo)
#     historic_detalle_pago_total.append(detalle_pago_total)
#     historic_detalle_transacciones.append(detalle_transacciones)
# historic_resumen = pd.concat(historic_resumen).reset_index(drop=True)
# historic_cash_back = pd.concat(historic_cash_back).reset_index(drop=True)
# historic_detalle_pago_minimo = pd.concat(historic_detalle_pago_minimo).reset_index(
#     drop=True
# )
# historic_detalle_pago_total = pd.concat(historic_detalle_pago_total).reset_index(
#     drop=True
# )
# historic_detalle_transacciones = pd.concat(historic_detalle_transacciones).reset_index(
#     drop=True
# )
# print(f"EXTRACTOS RAPPI ENCONTRADOS: {len(list(pdf_files))}")

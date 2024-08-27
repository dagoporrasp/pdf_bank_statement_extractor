import pdfplumber
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from itertools import chain
from bank_parsers.bank_pdf_parser_class import BankPDFParser
import re


@dataclass
class Nu_cc_data:
    resumen: pd.DataFrame  # [x]
    fechas: pd.DataFrame
    detalle_transacciones: pd.DataFrame

    def get_month_year(self) -> str:
        fecha_corte = self.fechas["Fecha de corte"].values[0].split(" ")
        month = fecha_corte[1]
        year = fecha_corte[2]
        return month, year


def find_idx_by(txt, pattern):
    idxs = [i for i, item in enumerate(txt) if item.startswith(pattern)]
    print(pattern)
    print(txt)
    return idxs[0]


def transpose_with_headers(df):
    df = df.T
    df.columns = df.iloc[0, :]
    df = df.drop(df.iloc[0, :].name).reset_index(drop=True)
    return df


def format_money_column(money_col):
    money_col = money_col.str.replace("$", "")
    money_col = money_col.str.replace(".", "")
    money_col = money_col.str.replace(",", ".")
    # money_col = money_col.str.replace(r"N/A", pd.NA)
    money_col = pd.to_numeric(money_col, errors="coerce")
    return money_col


class NuPDFParser(BankPDFParser):
    resultados_list = ["resumen", "detalle_transacciones", "fechas"]

    def crop_fdetail_page(self, page):
        page_cropped = page.crop((0, 0, 575, 761), relative=False, strict=True)
        details_table = page_cropped.extract_table(
            table_settings={
                "vertical_strategy": "lines",
                "snap_x_tolerance": 8,
                "snap_y_tolerance": 3,
                "horizontal_strategy": "lines",
                "explicit_vertical_lines": [
                    30,
                    77,
                    147,
                    207,
                    255,
                    315,
                    415,
                    485,
                ],
                "explicit_horizontal_lines": [45],
            }
        )
        return details_table

    def rename_dup_columns(self, df):
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [
                dup + "." + str(i) if i != 0 else dup for i in range(sum(cols == dup))
            ]
            df.columns = cols
        return df

    def parse_pdf(self, input_path, password):
        with pdfplumber.open(input_path, password=password) as pdf:
            # RESUMEN - Page1
            print(pdf.pages)

            fechas_pdf = pdf.pages[0].crop(
                (135, 235, 535, 315), relative=False, strict=True
            )
            fechas_table = fechas_pdf.extract_table(
                table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "explicit_vertical_lines": [150, 260, 390, 500],
                    "explicit_horizontal_lines": [270],
                }
            )
            fechas_df = pd.DataFrame(fechas_table[1:], columns=fechas_table[0])
            resumen_pdf = pdf.pages[0].crop(
                (275, 325, 575, 700), relative=False, strict=True
            )

            resumen_table = resumen_pdf.extract_table(
                table_settings={
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    # "explicit_vertical_lines": [275, 575],
                    # "explicit_horizontal_lines": [270],
                }
            )
            # print(resumen_pdf)
            # -----------------OLD
            # # RESUMEN - Page1
            # txt = pdf.pages[0].extract_text().split("\n")
            # txtr = pdf.pages[0].extract_text()
            # print(repr(txtr))
            # idx0 = find_idx_by(txt, "Periodo facturado")
            # idx1 = find_idx_by(txt, "COMO PAGAR")
            # resumen = txt[idx0:idx1]
            # resumen = [t.split(":") for t in resumen]
            # resumen.append([resumen[0][0], resumen[0][1].split("-")])
            # resumen.pop(0)
            # resumen.append(re.findall(r"\w+\s\w+", resumen[1][0]))
            # resumen.pop(1)
            # resumen.append(resumen[1][0].split())
            # resumen.pop(1)
            # resumen += [[resumen[2][0], resumen[3][0]], [resumen[2][1], resumen[3][1]]]
            # resumen.pop(2)
            # resumen.pop(2)
            # # Fechas de pago
            # year = resumen[0][1].split()[-1]
            # month = resumen[0][1].split()[-2].upper()

            # # Detalles de Pago - Page2
            # t1 = pdf.pages[1].extract_tables(
            #     table_settings={
            #         "vertical_strategy": "lines",
            #         "horizontal_strategy": "text",
            #         "explicit_vertical_lines": [
            #             450,
            #         ],
            #     }
            # )
            # t1[0][0] = ("").join(t1[0][0] + t1[0][-1]).split("$")
            # t1[0].pop(-1)
            # t1[1][0] = ("").join(list(t1[1][0][0][:10]) + t1[1][-1]).split("$")
            # t1[1].pop(-1)

            # Detalle de Transacciones - Page3--->Page-1
            pages_trx_details = pdf.pages[1:]
            detalle_transacciones = []

            for i, page in enumerate(pages_trx_details):
                if i == 0:
                    details_table = self.crop_fdetail_page(page)
                    columns = details_table[0]
                    transacciones = details_table[1:]
                    if len(columns) < 8:
                        details_table = self.crop_fdetail_page(pages_trx_details[i + 1])
                        columns = details_table[0]

                else:
                    page_cropped = page.crop(
                        (0, 75, 575, 761), relative=False, strict=True
                    )
                    details_table = page_cropped.extract_table(
                        table_settings={
                            "vertical_strategy": "lines",
                            "snap_x_tolerance": 8,
                            "snap_y_tolerance": 4,
                            "horizontal_strategy": "lines",
                            "explicit_vertical_lines": [
                                30,
                                77,
                                147,
                                207,
                                255,
                                315,
                                415,
                                485,
                            ],
                            "explicit_horizontal_lines": [45],
                        }
                    )
                    transacciones = details_table
                # print(transacciones)
                try:
                    if len(transacciones[0]) == 8:
                        detalle_transacciones.append(
                            pd.DataFrame(transacciones, columns=columns)
                        )
                except IndexError:
                    pass
            # Salida
            resumen = pd.DataFrame(resumen_table)
            fechas = fechas_df
            detalle_transacciones = pd.concat(detalle_transacciones)
            return Nu_cc_data(resumen, fechas, detalle_transacciones)

    # process--> resumen
    # ---------------------------------------
    def process_nu_resumen(self, nu_data):
        # resumen = nu_data.resumen.explode(1, ignore_index=True)
        # resumen.loc[1, 0] += " Desde"
        # resumen.loc[2, 0] += " Hasta"
        month, year = nu_data.get_month_year()
        resumen = transpose_with_headers(nu_data.resumen)
        resumen = resumen.drop([""], axis=1)
        resumen.rename(
            columns={resumen.columns[-1]: "PAGO HASTA Fecha Minima de Pago"},
            inplace=True,
        )
        resumen = self.rename_dup_columns(resumen)
        if len(resumen.columns) == 8:
            resumen["Abonos.1"] = 0
        resumen["MES"] = month
        resumen["AÑO"] = year
        # resumen.iloc[:, -2:] = resumen.iloc[:, -2:].apply(format_money_column)
        return resumen

    # process--> detalle de pago minimo
    # def process_nu_detalle_pago_minimo(self, nu_data):
    #     detalle_pago_minimo = nu_data.detalle_pago_minimo.replace("", pd.NA).dropna(
    #         how="all"
    #     )
    #     detalle_pago_minimo = transpose_with_headers(detalle_pago_minimo)
    #     detalle_pago_minimo = detalle_pago_minimo.apply(format_money_column)
    #     detalle_pago_minimo["Año"] = nu_data.year
    #     detalle_pago_minimo["Mes"] = nu_data.month
    #     return detalle_pago_minimo

    # # process--> detalle de pago total
    # def process_nu_detalle_pago_total(self, nu_data):
    #     detalle_pago_total = nu_data.detalle_pago_total.replace("", pd.NA).dropna(
    #         how="all"
    #     )
    #     detalle_pago_total = transpose_with_headers(detalle_pago_total)
    #     detalle_pago_total = detalle_pago_total.apply(format_money_column)
    #     detalle_pago_total["Año"] = nu_data.year
    #     detalle_pago_total["Mes"] = nu_data.month
    #     return detalle_pago_total

    # process--> detalle de transacciones
    def process_nu_detalle_transacciones(self, nu_data):
        detalle_transacciones = nu_data.detalle_transacciones
        # print(detalle_transacciones)
        # detalle_transacciones[0] = detalle_transacciones[0].replace("", pd.NA)
        # detalle_transacciones[4] = detalle_transacciones[4].map(
        #     lambda x: x.split()[2], na_action="ignore"
        # )
        # # cuota
        # detalle_transacciones[7] = detalle_transacciones[7].map(
        #     lambda x: x.split("(")[-1] if x.endswith(")") else pd.NA,
        #     na_action="ignore",
        # )
        # detalle_transacciones = detalle_transacciones.replace("", pd.NA).dropna(
        #     how="all"
        # )
        # detalle_transacciones = detalle_transacciones.dropna(how="all", axis=1)
        # detalle_transacciones = detalle_transacciones.drop(
        #     columns=detalle_transacciones.columns[-2]
        # )

        detalle_transacciones = detalle_transacciones.reset_index(drop=True)
        indx_end = (
            detalle_transacciones.loc[
                detalle_transacciones[detalle_transacciones.columns[-2]].str.contains(
                    "Pago mínimo", na=False
                )
            ].index.values[0]
            - 1
        )
        detalle_transacciones = detalle_transacciones.loc[:indx_end]
        # detalle_transacciones.columns = [
        #     "Fecha Transaccion",
        #     "Transaccion",
        #     "Total",
        #     "Tasa Interes M.V",
        #     "Intereses",
        #     "Cuota",
        #     "Saldo a pagar este mes",
        #     "Saldo pendiente para prox meses",
        # ]
        month, year = nu_data.get_month_year()
        detalle_transacciones["AÑO"] = year
        detalle_transacciones["MES"] = month
        detalle_transacciones[
            ["Interés del mes Porcentaje", "Interés del mes valor"]
        ] = detalle_transacciones[detalle_transacciones.columns[5]].str.split(
            " ", expand=True
        )
        detalle_transacciones.drop(
            detalle_transacciones.columns[5], axis=1, inplace=True
        )
        return detalle_transacciones

    def process(self, nu_data: Nu_cc_data) -> list[pd.DataFrame]:
        resumen = self.process_nu_resumen(nu_data)
        detalle_transacciones = self.process_nu_detalle_transacciones(nu_data)
        fechas = nu_data.fechas
        month, year = nu_data.get_month_year()
        fechas["MES"] = month
        fechas["AÑO"] = year
        return (resumen, detalle_transacciones, fechas)

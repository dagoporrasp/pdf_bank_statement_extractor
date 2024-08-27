import pdfplumber
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from itertools import chain
from bank_parsers.bank_pdf_parser_class import BankPDFParser
import re


@dataclass
class Bancolombia_data:
    balance_data: pd.DataFrame  # [x]
    cash_flow: pd.DataFrame
    year: str
    month: str


def find_idx_by(txt, pattern):
    idxs = [i for i, item in enumerate(txt) if pattern in item]
    # print(idxs)
    return idxs[0]


def transpose_with_headers(df):
    df = df.T
    df.columns = df.iloc[0, :]
    df = df.drop(df.iloc[0, :].name).reset_index(drop=True)
    return df


def format_money_column(money_col):
    # money_col = money_col.str.replace("s", "")
    # money_col = money_col.str.replace("$", "")
    money_col = money_col.str.replace(r"^\D*", "", regex=True)
    # money_col = money_col.str.replace(".", "")
    money_col = money_col.str.replace(",", "")
    money_col = money_col.str.replace(" ", "")
    # money_col = money_col.str.replace(r"N/A", pd.NA)
    # (r'\D+', '', regex=True)
    money_col = pd.to_numeric(money_col, errors="coerce")
    return money_col


def split_r(x):
    if "\n" in x:
        # print(x)
        return x.split("\n")
    else:
        return x


class BancolombiaPDFParser(BankPDFParser):
    resultados_list = ["balance_data", "cash_flow_data"]

    def parse_pdf(self, input_path, password):
        with pdfplumber.open(input_path, password=password) as pdf:
            # print(pdf.pages)
            # print(type(pdf.pages[0]))
            # print(dir(pdf.pages[0]))
            txt = pdf.pages[0].extract_text().split("\n")
            # print(txt)
            txt_fechas = txt[find_idx_by(txt, "DESDE:")]
            txt_fechas = txt_fechas.split()
            year = txt_fechas[3][:4]
            month = txt_fechas[3][5:7]
            page_height = pdf.pages[0].height
            page_width = pdf.pages[0].width
            # print(f"shape ({page_height},{page_width})")
            # resumen-balance
            resumen_blck = pdf.pages[0].crop((0, 310, page_width, 365))
            txt_resumen = resumen_blck.extract_text()
            table = resumen_blck.extract_table(
                table_settings={
                    "horizontal_strategy": "text",
                    "vertical_strategy": "lines",
                    "explicit_vertical_lines": [
                        45,
                        130,
                        310,
                        445,
                        574,
                    ],
                }
            )
            # cash flow
            cash_flow = []
            for i, page in enumerate(pdf.pages):
                if i == 0:
                    cash_flow_blck = page.crop((10, 375, 600, 755))
                    cash_flow_page = cash_flow_blck.extract_table(
                        table_settings={
                            "horizontal_strategy": "text",
                            "vertical_strategy": "lines",
                            "explicit_vertical_lines": [
                                30,
                                75,
                                250,
                                345,
                                395,
                                500,
                                595,
                            ],
                        }
                    )
                    cash_flow_page0 = cash_flow_page
                    txt_cash_flow = cash_flow_blck.extract_text()
                else:
                    cash_flow_blck = page.crop((10, 180, 600, 755))
                    cash_flow_page = cash_flow_blck.extract_table(
                        table_settings={
                            "horizontal_strategy": "text",
                            "vertical_strategy": "lines",
                            "explicit_vertical_lines": [
                                30,
                                75,
                                250,
                                345,
                                395,
                                500,
                                595,
                            ],
                        }
                    )
                cash_flow_page_df = pd.DataFrame(
                    cash_flow_page[1:],
                    columns=[
                        "FECHA",
                        "DESCRIPCION",
                        "SUCURSAL",
                        "DTO.",
                        "VALOR",
                        "SALDO",
                    ],
                )
                # print(cash_flow_page_df)
                cash_flow.append(cash_flow_page_df)

            balance_data = pd.DataFrame(table)
            cash_flow = pd.concat(cash_flow).reset_index(drop=True)
            return Bancolombia_data(balance_data, cash_flow, year, month)

    def process_bancolombia_balance_data(self, bancolombia_data):
        # process resumen
        new_cols = {x: y for x, y in zip([2, 3], [0, 1])}
        balance_data = bancolombia_data.balance_data.rename(columns=new_cols)
        balance_data = pd.concat(
            [balance_data.iloc[:, :2], balance_data.iloc[:, 2:4]], axis=0
        )
        balance_data = balance_data.replace("", pd.NA).dropna(how="all")
        balance_data = transpose_with_headers(balance_data)
        balance_data = balance_data.apply(format_money_column)
        balance_data["Año"] = bancolombia_data.year
        balance_data["Mes"] = bancolombia_data.month
        return balance_data

    def process_bancolombia_cash_flow(self, bancolombia_data):
        # quizas quitar última fila-.. FIN ESTADO DE CUENTAhistoric_bancolombia_data
        cash_flow = bancolombia_data.cash_flow
        cash_flow = cash_flow.replace("", pd.NA).dropna(how="all")
        cash_flow = cash_flow.map(split_r, na_action="ignore")
        cash_flow = cash_flow.explode(
            ["FECHA", "DESCRIPCION", "VALOR", "SALDO"], ignore_index=True
        )
        cash_flow[["VALOR", "SALDO"]] = cash_flow[["VALOR", "SALDO"]].apply(
            format_money_column
        )
        # print(len(cash_flow))
        cash_flow = cash_flow[~cash_flow["DESCRIPCION"].isin(["FIN ESTADO DE CUENTA"])]
        cash_flow["Año"] = bancolombia_data.year
        return cash_flow

    def process(self, bancolombia_data):
        balance_data = self.process_bancolombia_balance_data(bancolombia_data)
        cash_flow_data = self.process_bancolombia_cash_flow(bancolombia_data)
        self.resultados = {
            "balance_data": balance_data,
            "cash_flow_data": cash_flow_data,
        }
        return balance_data, cash_flow_data

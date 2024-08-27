import pdfplumber
from pathlib import Path
import pandas as pd
from bank_parsers.bank_pdf_parser_class import BankPDFParser
from dataclasses import dataclass


@dataclass
class Account_Data:
    balance: pd.DataFrame
    cash_flow: pd.DataFrame
    pocket: pd.DataFrame
    year: str
    month: str


class DaviviendaPDFParser(BankPDFParser):
    resultados_list = ["balance", "cash_flow", "pocket_balance", "pockets_clash_flow"]

    def parse_pdf(self, input_path: Path, password: str) -> Account_Data:
        """a method for parsing pdf files"""
        with pdfplumber.open(input_path, password=password) as pdf:
            print(pdf.pages)
            text_file = pdf.pages[0].extract_text().split("\n")
            date_report = (
                [m for m in text_file if "INFORME DEL MES" in m][0]
                .split(":")[-1]
                .replace("/", "")
            )
            year = date_report[-4:]
            month = date_report[:-4]
            tables_page1 = pdf.pages[0].find_tables()
            tables_page2 = pdf.pages[1].find_tables()
            try:
                tables_page3 = pdf.pages[2].find_tables()
            except:
                tables_page3 = None
            # test1 = pdf.pages[0].extract_table(table_settings={"vertical_strategy": "text", "horizontal_strategy": "lines"})
            # df_t1 = pd.DataFrame(test1)
            balance_content = tables_page1[0].extract()
            cash_flow_content = []
            cash_flow_content_p1 = tables_page1[1].extract()
            cash_flow_content_p2 = tables_page2[0].extract()
            cash_flow_headers = cash_flow_content_p1[1]
            cash_flow_content.append(
                pd.DataFrame(cash_flow_content_p1[2:], columns=cash_flow_headers)
            )
            cash_flow_content.append(
                pd.DataFrame(cash_flow_content_p2[1:], columns=cash_flow_headers)
            )
            if tables_page3:
                pocket_content_p3 = tables_page3[0].extract()
                df_pocket = pd.DataFrame(pocket_content_p3[5:])
            else:
                df_pocket = pd.DataFrame({})
            df_balance = pd.DataFrame(balance_content)
            df_cash_flow = pd.concat(cash_flow_content).reset_index(drop=True)
            return Account_Data(df_balance, df_cash_flow, df_pocket, year, month)

    def process_balance_data(self, davivienda_data: Account_Data) -> pd.DataFrame:
        # TODO: pasarlo a centavos
        data = davivienda_data.balance
        data = data.replace("", pd.NA)
        data = data.dropna(how="all")
        data = data.dropna(how="all", axis=1)
        data = data.rename(columns={1: "Cantidad"})
        data["Cantidad"] = data["Cantidad"].str.replace("$", "")
        data["Cantidad"] = data["Cantidad"].str.replace(",", "")
        data["Cantidad"] = pd.to_numeric(data["Cantidad"])
        data = data.T
        if len(data.columns) == 6:
            data.columns = [
                "Saldo Anterior",
                "Mas Creditos",
                "Menos Debitos",
                "Nuevo Saldo",
                "Saldo Promedio",
                "Saldo Total Bolsillo",
            ]
            data = data.reset_index(drop=True)
        data["Mes"] = davivienda_data.month
        data["Año"] = davivienda_data.year
        return data

    def format_cash_flow_table(self, davivienda_data: Account_Data) -> pd.DataFrame:
        # TODO: pasarlo a centavos
        data = davivienda_data.rename(columns={"Fecha": "Dia", None: "Mes"})
        # print(data)
        data["Fecha"] = data["Dia"] + data["Mes"] + data["Año"]
        data["Fecha"] = pd.to_datetime(data["Fecha"], format="%d%m%Y")
        data["Valor"] = data["Valor"].str.replace("$", "")
        data["Valor"] = data["Valor"].str.replace(",", "")
        data["Signo de movimiento"] = data["Valor"].str[-1]
        data["Tipo de movimiento"] = data["Signo de movimiento"].apply(
            lambda x: "Ingreso" if x == "+" else "Egreso"
        )
        data["Valor"] = pd.to_numeric(data["Valor"].str[:-1])
        return data

    def process_cash_flow_data(self, davivienda_data: Account_Data) -> pd.DataFrame:
        data = davivienda_data.cash_flow
        data["Año"] = davivienda_data.year
        data = self.format_cash_flow_table(data)
        return data

    def format_money_column(self, money_col):
        money_col = money_col.str.replace("$", "")
        money_col = money_col.str.replace(",", "")
        return pd.to_numeric(money_col)

    def process_pocket_data(self, davivienda_data):
        data = davivienda_data.pocket
        pocket_idx = data[data[0].str.contains("BOLSILLO")].index.to_list()
        data = data.replace("", pd.NA)

        # pocket-balance
        pocket_balance = data.loc[: pocket_idx[0] - 1]
        pocket_balance = pocket_balance.dropna(how="all", axis=0)
        pocket_balance = pocket_balance.dropna(how="all", axis=1)
        pocket_balance = pocket_balance.T
        pocket_balance_header = pocket_balance.iloc[0, :].to_list()
        pocket_balance = pocket_balance.drop(pocket_balance.iloc[0, :].name)
        pocket_balance.columns = pocket_balance_header
        pocket_balance["Año"] = davivienda_data.year
        pocket_balance["mes"] = davivienda_data.month
        pocket_balance[["Saldo Anterior", "Nuevo Saldo", "Saldo Promedio"]] = (
            pocket_balance[["Saldo Anterior", "Nuevo Saldo", "Saldo Promedio"]].apply(
                self.format_money_column
            )
        )
        # pocket_balance['Saldo Anterior'] = pd.to_numeric(pocket_balance['Saldo Anterior'])
        # pocket_balance['Nuevo Saldo'] = pd.to_numeric(pocket_balance['Nuevo Saldo'])
        # pocket_balance['Saldo Promedio'] = pd.to_numeric(pocket_balance['Saldo Promedio'])

        # pocket-cash-flow
        pockets = []
        pockets.append(data.loc[pocket_idx[0] :])
        # print(pockets)
        # pockets.append(data.loc[pocket_idx[0] : pocket_idx[1] - 1])
        # pockets.append(data.loc[pocket_idx[1] :])
        pockets_cash_flow = []

        for idx, pocket in zip(pocket_idx, pockets):
            pocket = pocket.dropna(how="all", axis=0)
            pocket = pocket.dropna(how="all", axis=1)
            pocket_name = pocket.iloc[0, 0]
            print(pocket_name)
            pocket_header = pocket.iloc[1, :].to_list()
            # print(pocket)
            # pocket.drop(pocket.iloc[0, :].name, inplace=True)
            pocket.drop([pocket.iloc[0, :].name, pocket.iloc[1, :].name], inplace=True)
            pocket.columns = pocket_header
            pocket["Año"] = davivienda_data.year
            pocket = self.format_cash_flow_table(pocket)
            pocket["Bolsillo"] = pocket_name
            pockets_cash_flow.append(pocket)
            print(pocket)
        pockets_clash_flow = pd.concat(pockets_cash_flow).reset_index(drop=True)
        return pocket_balance, pockets_clash_flow

    def process(self, davivienda_data: Account_Data) -> list[pd.DataFrame]:
        """a method for cleaning the data from parse_pdf method"""
        balance_data = self.process_balance_data(davivienda_data)
        cash_flow_data = self.process_cash_flow_data(davivienda_data)
        if davivienda_data.pocket.empty:
            pocket_balance = pd.DataFrame({})
            pockets_clash_flow = pd.DataFrame({})
        else:
            pocket_balance, pockets_clash_flow = self.process_pocket_data(
                davivienda_data
            )
        return balance_data, cash_flow_data, pocket_balance, pockets_clash_flow

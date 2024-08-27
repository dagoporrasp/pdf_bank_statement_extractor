from bank_parsers.bank_pdf_parser_class import BankPDFParser
from bank_parsers.davivienda_pdf_parser import DaviviendaPDFParser
from bank_parsers.rappi_pdf_parser import RappiPDFParser
from bank_parsers.nu_pdf_parser import NuPDFParser
from bank_parsers.bancolombia_pdf_parser import BancolombiaPDFParser

bank_parsers_list = {
    "Davivienda": {
        "Ahorros": DaviviendaPDFParser(),
    },
    "Rappi": {
        "Credito": RappiPDFParser(),
    },
    "Nu": {
        "Credito": NuPDFParser(),
    },
    "Bancolombia": {
        "Ahorros": BancolombiaPDFParser(),
    },
}


def make_bank_parser(bank, acc_type) -> BankPDFParser:
    return bank_parsers_list[bank][acc_type]

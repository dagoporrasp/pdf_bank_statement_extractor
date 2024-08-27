from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod


class BankPDFParser(ABC):
    @property
    def resultados_list(self):
        "output list names"

    @abstractmethod
    def parse_pdf(self, input_path: Path, password: str):
        """a method for parsing pdf files"""

    @abstractmethod
    def process(self):
        """a method for cleaning the data from parse_pdf method"""

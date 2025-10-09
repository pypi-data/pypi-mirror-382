import os
from typing import Optional

import pandas as pd

from ..common.logger import logger
from .base_handler import BaseHandler


class TabularHandler(BaseHandler):
    """Handler for .csv, .tsv, .xls, .xlsx files."""

    extensions = frozenset([".csv", ".tsv", ".xls", ".xlsx"])

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        logger.info(f"Processing tabular file: {file_path}")
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".csv", ".tsv"]:
                delimiter = "\t" if ext == ".tsv" else ","
                df = pd.read_csv(file_path, delimiter=delimiter)
            elif ext in [".xls", ".xlsx"]:
                df = pd.read_excel(file_path)
            else:
                raise RuntimeError("Unsupported tabular format")

            md = df.to_markdown(index=False)
            return md
        except Exception as e:
            logger.error(f"Error processing tabular file {file_path}: {e}")
            return None

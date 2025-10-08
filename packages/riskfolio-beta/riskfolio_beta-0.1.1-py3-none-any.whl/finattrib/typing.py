# typing.py
from typing import TypedDict, Dict
import pandas as pd

DataFrame = pd.DataFrame

class RWTable(TypedDict):
    product: Dict[str, float]
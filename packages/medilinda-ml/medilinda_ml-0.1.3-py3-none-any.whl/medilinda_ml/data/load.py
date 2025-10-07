import pandas as pd
from pathlib import Path


def load_csv(file_path: Path) -> pd.DataFrame:
    """Load CSV into DataFrame."""
    return pd.read_csv(file_path)

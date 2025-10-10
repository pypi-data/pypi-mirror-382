from typing import Any, Optional

import pandas as pd

from ..constants import DTYPE_CATEGORICAL_LIST, VALIDATION_TABLE_COLUMNS_MIN


def get_target_variable(
    data: pd.DataFrame, settings: Optional[Any] = None
) -> Optional[str]:
    """Auto-detect the best target variable for visualization"""
    if settings is None:
        from .settings import settings as config_settings

        settings = config_settings

    max_categories = settings.get("visualization.config.max_categories_for_target", 10)

    categorical_cols = data.select_dtypes(
        include=DTYPE_CATEGORICAL_LIST
    ).columns.tolist()

    for col in categorical_cols:
        if data[col].nunique() <= max_categories:
            return str(col)

    if len(data.columns) > VALIDATION_TABLE_COLUMNS_MIN:
        last_col = data.columns[-1]
        if last_col in categorical_cols or data[last_col].nunique() <= max_categories:
            return str(last_col)

    return None

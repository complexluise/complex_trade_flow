import numpy as np
from scipy import stats
from pandas import DataFrame

from .constants import BACIColumnsTradeData


def calculate_marginal_probabilities(category: str, data: DataFrame, column: str) -> np.ndarray:
    """
    Calculates the marginal probabilities for a specific category within trade data.

    Args:
        category (str): The name of the category column in the trade data.
        data (DataFrame): The trade data DataFrame.
        column (str): Column name used to get the distribution

    Returns:
        np.ndarray: A NumPy array containing the marginal probabilities.
    """
    distribution = data.groupby(category)[column].sum().values
    return distribution / np.sum(distribution)


def calculate_diversity_index(
        data: DataFrame,
        category: str = BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value,
        column: str = BACIColumnsTradeData.MONEY.value
    ) -> float:
    """
    Calculates the diversity index for trade data based on a classification scheme.

    Args:
        data (DataFrame):
        category (str):
        column (str):
    Returns:
        float: diversity index.
    """
    probabilities = calculate_marginal_probabilities(
        category=category,
        data=data,
        column=column
    )
    return 2 ** stats.entropy(probabilities, base=2)

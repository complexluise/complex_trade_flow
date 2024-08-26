import pandas as pd


def append_yearly_csv():
    pass


class ClassificationScheme:
    """
    Handles loading and applying different classification schemes to countries.

    This class can load classification data from different sources and map countries
    to their respective classifications (e.g., regions, income levels).
    """
    def __init__(
            self,
            name: str,
            file_path: str | None = None,
            key_column: str | None = None,
            value_column: str | None = None
    ):
        self.name = name
        self.file_path = file_path
        self.key_column = key_column
        self.value_column = value_column
        self.classification_data = self._load_classification_data()

    def __str__(self):
        return self.name

    def _load_classification_data(self) -> dict[str, str]:
        """
        Loads classification data from a CSV file, or returns an empty dictionary for NoClassification.

        Returns:
            dict[str, str]: A dictionary mapping country codes to classification values.
        """
        if self.file_path and self.key_column and self.value_column:
            classification_df = pd.read_csv(self.file_path)
            return classification_df.set_index(self.key_column)[self.value_column].to_dict()
        else:
            return {}  # For NoClassification, return an empty dictionary

    def apply_classification(self, countries: set[str]) -> dict[str, str]:
        """
        Maps each country to its classification value or to itself if no classification is provided.
         Si el país no está clasificado el valor obtenido es "Unknown"

        Args:
            countries (set[str]): A set of country codes.

        Returns:
            dict[str, str]: A dictionary mapping each country to its classification value or to itself.
        """
        if not self.file_path:
            return {country: country for country in countries}  # NoClassification behavior
        return {country: self.classification_data.get(country, 'Unknown') for country in countries}



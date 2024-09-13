import os
import pandas as pd


def combine_csv_files(folder_path):
    """
    Combines CSV files in a given folder into a single DataFrame.

    Args:
        folder_path (str): The path to the folder containing the CSV files.

    Returns:
        pandas.DataFrame: A DataFrame containing the combined data.
    """

    combined_df = pd.DataFrame()

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            year = filename.split(".")[0].split("_")[-1]
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            df["year"] = year
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df


if __name__ == '__main__':
    classification_schema = "by_advanced_not-advanced"
    folder_path = f"data/processed_data/BACI_HS92_V202401b/{classification_schema}/diversity"  # Replace with the actual path to your folder
    combined_data = combine_csv_files(folder_path)
    combined_data.to_csv(f"data/processed_data/BACI_HS92_V202401b/diversity_{classification_schema}.csv", index=False)
    print(combined_data.shape)

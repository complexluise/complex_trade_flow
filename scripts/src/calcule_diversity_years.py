import pandas as pd

if __name__ =='__main__':

    df_list: list = []
    start_year = 1995
    end_year = 2022
    for year in range(start_year, end_year + 1):
        data = pd.read_csv(f"data/processed_data/BACI_HS92_V202401b/diversity_regions/regions_diversity_HS92_Y{year}_V202401b.csv")
        data["year"] = year
        df_list.append(data)

    # outside for
    df = pd.concat(df_list)

    df.to_csv("data/processed_data/BACI_HS92_V202401b/diversity_by_year_region.csv", index=False)




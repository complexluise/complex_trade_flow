import numpy as np
import plotly.express as px
import pandas as pd
import streamlit as st

from pandas import DataFrame

years = np.arange(1995, 2023)


@st.cache_data
def load_data() -> DataFrame:
    ruta_datos = "data/processed_data/BACI_HS92_V202401b/"
    df_list = []
    for year in years:
        df = pd.read_csv(
            ruta_datos + f"countries_diversity_HS92_Y{year}_V202401b.csv",
            sep=",")
        df["year"] = year
        df.drop(
            labels="Unnamed: 0",
            axis=1,
            inplace=True
        )
        df_list.append(df)

    return pd.concat(df_list)


df_diversidad_paises = load_data()


def filter_dataframe(df, year):
    return df[df['year'] == year]


def update_figure(year):
    filtered_df = filter_dataframe(df_diversidad_paises, year)
    fig = px.scatter(filtered_df, x="export_product_diversity", y="import_product_diversity", marginal_y="violin", color='is_latinoamerica',
                     marginal_x="histogram", trendline="ols", template="simple_white", title='Diversidad de exportaciones e importaciones - {}'.format(year),
                     hover_data='countries')

    fig.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        legend_title_font_color="black"
    )
    fig.update_xaxes(title_font_family="Arial")
    return fig


st.title("Diversidad de Exportaciones e Importaciones")
year = st.selectbox("Seleccione un año:", years)
fig = update_figure(year)
st.plotly_chart(fig, use_container_width=True)

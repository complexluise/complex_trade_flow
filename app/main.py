import numpy as np
import plotly.express as px
import pandas as pd
import streamlit as st

from pandas import DataFrame

st.set_page_config(
    page_title="Diversidad Económica",
    page_icon="🐲",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

years = np.arange(1995, 2023)


@st.cache_data
def load_data_diversity_countries() -> DataFrame:
    ruta_datos = "data/processed_data/BACI_HS92_V202401b/"
    df = pd.read_csv(
        ruta_datos + f"countries_diversity_HS92_V202401b.csv",
        sep=",")
    df.drop(
        labels="Unnamed: 0",
        axis=1,
        inplace=True
    )

    return df


df_diversidad_paises = load_data_diversity_countries()


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
st.plotly_chart(fig, use_container_width=True, height=1200)

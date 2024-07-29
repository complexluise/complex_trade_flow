import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
def load_data_diversity_countries() -> tuple[DataFrame, DataFrame]:
    ruta_datos = "data/processed_data/BACI_HS92_V202401b/"
    df_1 = pd.read_csv(
        ruta_datos + f"countries_diversity_HS92_V202401b.csv",
        sep=",")
    df_1.drop(
        labels="Unnamed: 0",
        axis=1,
        inplace=True
    )

    df_2 = pd.read_csv(
        ruta_datos + f"diversity_by_year_HS92_V202401b.csv",
        sep=",")

    return df_1, df_2


df_diversidad_paises, df_diversidad_tiempo = load_data_diversity_countries()


def filter_dataframe(df, year):
    return df[df['year'] == year]


def update_figure(year):
    filtered_df = filter_dataframe(df_diversidad_paises, year)

    fig = px.scatter(filtered_df, x="export_product_diversity", y="import_product_diversity", marginal_y="violin",
                     color='is_latinoamerica', marginal_x="histogram", trendline="ols", template="simple_white",
                     title='Diversidad de exportaciones e importaciones - {}'.format(year), hover_data='countries',
                     labels={
                         "export_product_diversity": "Diversidad de exportación de productos",
                         "import_product_diversity": "Diversidad de importación de productos"
                     }
                     )

    fig.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        legend_title_font_color="black",
        xaxis=dict(range=[0, 1200]),
        yaxis=dict(range=[0, 1500]),

    )
    fig.update_xaxes(title_font_family="Arial")
    return fig


st.title("Diversidad de Exportaciones e Importaciones por País en cada Año")
year = st.slider("Seleccione un año:", min_value=min(years), max_value=max(years), value=min(years))
fig = update_figure(year)
st.plotly_chart(fig, use_container_width=True)

st.title("Diversidad a lo largo de tiempo Latinoamerica y Mundo")
df_melted = df_diversidad_tiempo.melt(id_vars=["tiempo"], var_name="Variable", value_name="Valor")
# Máscara aplicada para excluir las diversidades de importación
mask = ~df_melted["Variable"].isin(["import_diversity_w", "import_diversity_lan"])
df_filtered = df_melted[mask]

# Creamos el gráfico interactivo
fig_2 = px.line(df_melted[mask], x="tiempo", y="Valor", color="Variable",
              title="Diversidad de Importaciones y Exportaciones a lo Largo del Tiempo",
              labels={"Valor": "Diversidad", "tiempo": "Año"})

# Personalizamos el diseño del gráfico
fig_2.update_layout(
    template="plotly_white",
    xaxis_title="Año",
    yaxis_title="Diversidad",
    legend_title="Indicadores",
    font=dict(size=12),
    hovermode="x unified",
    xaxis=dict(
        tickmode='linear',
        tick0=0.5,
        dtick=0.75
    )
)

st.plotly_chart(fig_2, use_container_width=True)




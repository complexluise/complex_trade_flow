import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        ruta_datos + f"countries_diversity.csv",
        sep=",")
    df_1.drop(
        labels="Unnamed: 0",
        axis=1,
        inplace=True
    )

    df_2 = pd.read_csv(
        ruta_datos + f"diversity_by_year_region.csv",
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


def diversity_over_time_plot(df):
    color_palette = {
        'Latin America & Caribbean ': '#1f77b4',
        'Aggregates': '#ff7f0e',
        'South Asia': '#2ca02c',
        'Sub-Saharan Africa ': '#d62728',
        'Europe & Central Asia': '#9467bd',
        'Middle East & North Africa': '#8c564b',
        'East Asia & Pacific': '#e377c2',
        'North America': '#7f7f7f'
    }

    # Create the figure
    fig = go.Figure()

    # Add traces for each region and diversity type
    for region in df['region'].unique():
        region_data = df[df['region'] == region]

        # Export diversity
        fig.add_trace(go.Scatter(
            x=region_data['year'],
            y=region_data['export_product_diversity'],
            mode='lines',
            name=f'{region} - Export',
            line=dict(color=color_palette[region], dash='solid'),
            legendgroup=region
        ))

        # Import diversity
        fig.add_trace(go.Scatter(
            x=region_data['year'],
            y=region_data['import_product_diversity'],
            mode='lines',
            name=f'{region} - Import',
            line=dict(color=color_palette[region], dash='dash'),
            legendgroup=region
        ))

    # Update layout
    fig.update_layout(
        title="Export and Import Product Diversity Across Regions Over Time",
        xaxis_title="Year",
        yaxis_title="Product Diversity",
        legend_title="Region and Diversity Type",
        hovermode="closest",
        legend=dict(groupclick="toggleitem")
    )
    return fig


st.title("Diversidad de Exportaciones e Importaciones por País en cada Año")
year = st.slider("Seleccione un año:", min_value=min(years), max_value=max(years), value=min(years))
fig = update_figure(year)
st.plotly_chart(fig, use_container_width=True)

st.title("Diversidad a lo largo de tiempo Latinoamerica y Mundo")
df_melted = df_diversidad_tiempo.melt(
    id_vars=["year", "region"],
    value_vars=["export_product_diversity", "import_product_diversity"],
    var_name="Variable",
    value_name="Value")

fig_2 = diversity_over_time_plot(df_diversidad_tiempo)

st.plotly_chart(fig_2, use_container_width=True)




import os

import folium
import geopandas as gpd
import streamlit as st
from components.layout import configure_page_settings
from components.tables import stylized_table
from shapely import wkt
from shapely.geometry import Point
from streamlit_folium import st_folium


def swap_coordinates(point_str):
    """Fix for error in stac items, need to fix in catalog and return wkt.loads(point_str)"""
    point = wkt.loads(point_str)
    return Point(point.x, point.y)


def app():
    configure_page_settings("Storm Viewer")

    st.markdown("## Storm Viewer")

    df = st.storms.rename(
        columns={
            "block_group": "Block",
            "historic_storm_date": "Date",
            "historic_storm_season": "Season",
            "historic_storm_max_precip_inches": "Max Precip (in)",
            "realization": "Realization",
            "date": "Date",
        }
    )

    search_col1, search_col2 = st.columns(2)

    with search_col1:
        sieve1 = df.copy()
        st.session_state["realization"] = st.multiselect("Select by Realization",
                                                         sieve1["Realization"].unique(),
                                                         default=list(sieve1["Realization"].unique())[0])
        sieve1 = sieve1[sieve1["Realization"].isin(st.session_state["realization"])]
        st.session_state["block"] = st.slider("Select by Block Range",
                                              min_value=sieve1["Block"].min(),
                                              max_value=sieve1["Block"].max(),
                                              value=(122, 255))
        sieve1 = sieve1[(sieve1["Block"] >= st.session_state["block"][0]) & (sieve1["Block"] <= st.session_state["block"][1])]

        st.session_state["search_id"] = st.multiselect("Search by ID", sieve1["ID"].unique())
        if len(st.session_state["search_id"]) > 0:
            st.write("filtering by search_id")
            sieve1 = sieve1[sieve1["ID"].isin(st.session_state["search_id"])]

    with search_col2:
        #sieve2 = sieve1.copy()
        if sieve1["Max Precip (in)"].min() != sieve1["Max Precip (in)"].max():
            st.session_state["max_precip"] = st.slider("Search by Max Precipitation (inches)",
                                                    min_value=sieve1["Max Precip (in)"].min(),
                                                    max_value=sieve1["Max Precip (in)"].max(),
                                                    value=sieve1["Max Precip (in)"].mean(),
                                                    step=0.1)
            sieve1 = sieve1[sieve1["Max Precip (in)"] >= st.session_state["max_precip"]]

        st.session_state["storm_season"] = st.multiselect("Search for Seasonal Storms",
                                                        ["All", "spring", "summer", "fall", "winter"],
                                                        default=["All"])
        if "All" not in st.session_state["storm_season"]:
            sieve1 = sieve1[sieve1["Season"].isin(st.session_state["storm_season"])]

        st.session_state["storm_date"] = st.multiselect("Search by Storm Date",
                                                        ["All", *sieve1["Date"].unique()],
                                                        default=["All"])
        if "All" not in st.session_state["storm_date"]:
            sieve1 = sieve1[sieve1["Date"].isin(st.session_state["storm_date"])]

    st.write("Filtered Dataset")
    st.dataframe(sieve1)

    if len(sieve1) > 0:
        # Create a gdf for the SST storm center points
        sst_gdf = sieve1.copy()
        sst_gdf["geometry"] = sst_gdf["SST_storm_center"].apply(swap_coordinates)
        sst_gdf = gpd.GeoDataFrame(sst_gdf, geometry="geometry")

        # Create a gdf for the historic storm center points
        historic_gdf = sieve1.copy()
        historic_gdf["geometry"] = historic_gdf["historic_storm_center"].apply(swap_coordinates)
        historic_gdf = gpd.GeoDataFrame(historic_gdf, geometry="geometry")

        # initialize the maps
        m1 = folium.Map(location=[37.75153, -80.94911], zoom_start=6)
        folium.GeoJson(f"{st.stac_url}/collections/Kanawha-0505-R001/items/R001-E2044").add_to(m1)
        m2 = folium.Map(location=[37.75153, -80.94911], zoom_start=6)
        folium.GeoJson(f"{st.stac_url}/collections/Kanawha-0505-R001/items/R001-E2044").add_to(m2)
        
        # create a heatmap for the historic storm center points
        folium.plugins.HeatMap(data=historic_gdf["geometry"].apply(lambda pt: [pt.y, pt.x]).tolist()).add_to(m1)
        # create a heatmap for the SST storm center points
        folium.plugins.HeatMap(data=sst_gdf["geometry"].apply(lambda pt: [pt.y, pt.x]).tolist()).add_to(m2)

        col3, col4 = st.columns(2)
        with col3:
            st.write("Historic Storm Centers Heatmap")
            st_folium(m1, width=700, height=700)
        with col4:
            st.write("SST Storm Centers Heatmap")
            st_folium(m2, width=700, height=700)


if __name__ == "__main__":
    app()

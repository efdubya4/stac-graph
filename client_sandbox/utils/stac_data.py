import pandas as pd
import streamlit as st


def generate_stac_item_link(base_url, collection_id, item_id):
    return (
        f"https://radiantearth.github.io/stac-browser/#/external/{base_url}/collections/{collection_id}/items/{item_id}"
    )


def fetch_collection_data(collection_id, _progress_bar):
    items = list(st.session_state.stac_client.search(collections=[collection_id]).items())
    item_data = []
    total_items = len(items)

    for idx, item in enumerate(items):
        stac_item_link = f"https://radiantearth.github.io/stac-browser/#/external/{st.session_state.stac_url}/collections/{collection_id}/items/{item.id}"

        event = item.properties.get("event", "N/A")
        block_group = item.properties.get("block_group", "N/A")
        realization = item.properties.get("realization", "N/A")
        SST_storm_center = item.properties.get("SST_storm_center", "N/A")
        historic_storm_date = item.properties.get("historic_storm_date", "N/A")
        historic_storm_center = item.properties.get("historic_storm_center", "N/A")
        historic_storm_season = item.properties.get("historic_storm_season", "N/A")
        historic_storm_max_precip_inches = item.properties.get("historic_storm_max_precip_inches", "N/A")

        item_data.append(
            {
                "ID": item.id,
                "Link": f'<a href="{stac_item_link}" target="_blank">See in Catalog</a>',
                "event": event,
                "block_group": block_group,
                "realization": realization,
                "SST_storm_center": SST_storm_center,
                "historic_storm_date": historic_storm_date,
                "historic_storm_center": historic_storm_center,
                "historic_storm_season": historic_storm_season,
                "historic_storm_max_precip_inches": historic_storm_max_precip_inches,
            }
        )
        # Update the progress bar
        _progress_bar.progress((idx + 1) / total_items)

    df = pd.DataFrame(item_data)
    return df

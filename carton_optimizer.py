
import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from io import BytesIO
from fpdf import FPDF
import tempfile
import os
from datetime import datetime
import sys

# Constants
LANGUAGES = ["Čeština", "English"]
DEFAULT_LANG = LANGUAGES[0]

# Language toggle
lang = st.sidebar.selectbox("🌐 Jazyk / Language", LANGUAGES)

# Language dictionary
from pathlib import Path
import json
# In production: load this from a separate file
T = json.loads(Path("language_strings.json").read_text()) if Path("language_strings.json").exists() else {
    "Čeština": {
        "title": "🧮 Optimalizace balení",
        "description": "Zadej rozměry retail balení, master kartonu a palety. Aplikace najde nejlepší uspořádání a rozvržení na paletu.",
        "product": "Název produktu nebo zákazníka",
        "retail_w": "Šířka retail krabičky (mm)",
        "retail_d": "Hloubka retail krabičky (mm)",
        "retail_h": "Výška retail krabičky (mm)",
        "retail_weight": "Hmotnost 1 retail krabičky (g)",
        "master_w": "Šířka master kartonu (mm)",
        "master_d": "Hloubka master kartonu (mm)",
        "master_h": "Výška master kartonu (mm)",
        "pallet_w": "Max. šířka palety (mm)",
        "pallet_d": "Max. hloubka palety (mm)",
        "pallet_h": "Max. výška palety (mm)",
        "weight": "Hmotnost 1 master kartonu (kg)",
        "price": "Cena za 1 master karton (Kč)",
        "run": "Spustit výpočet",
        "reset": "🔄 Nový výpočet",
        "best": "Nejlepší varianta",
        "pallet_summary": "Na paletu se vejde {m} master kartonů → {r} retail krabiček",
        "error": "Retail balení je větší než master karton – nelze vložit.",
        "viz_title": "Rozložení master kartonů na paletě (1 vrstva)"
    },
    "English": {
        "title": "🧮 Packaging Optimization",
        "description": "Enter retail box, master carton and pallet dimensions. The app will find the optimal configuration and pallet layout.",
        "product": "Product or customer name",
        "retail_w": "Retail box width (mm)",
        "retail_d": "Retail box depth (mm)",
        "retail_h": "Retail box height (mm)",
        "retail_weight": "Weight of 1 retail box (g)",
        "master_w": "Master carton width (mm)",
        "master_d": "Master carton depth (mm)",
        "master_h": "Master carton height (mm)",
        "pallet_w": "Max pallet width (mm)",
        "pallet_d": "Max pallet depth (mm)",
        "pallet_h": "Max pallet height (mm)",
        "weight": "Weight of 1 master carton (kg)",
        "price": "Price per 1 master carton (CZK)",
        "run": "Run calculation",
        "reset": "🔄 New calculation",
        "best": "Best variant",
        "pallet_summary": "Pallet fits {m} master cartons → {r} retail boxes",
        "error": "Retail box is larger than master carton – cannot fit.",
        "viz_title": "Master carton layout on pallet (1 layer)"
    }
}

L = T.get(lang, T[DEFAULT_LANG])

product_name = st.sidebar.text_input(L["product"], value="produkt")

now_str = datetime.now().strftime("%Y%m%d_%H%M")
name_clean = product_name.replace(" ", "_").replace("/", "-")
file_prefix = f"baleni_{name_clean}_{now_str}"

st.title(L["title"])
col_reset = st.columns([8, 2])[1]
with col_reset:
    if st.button(L["reset"]):
        st.cache_data.clear()
        st.rerun()

st.markdown(L["description"])

col1, col2 = st.columns(2)

with col1:
    retail_width = st.number_input(L["retail_w"], min_value=1, value=130)
    retail_depth = st.number_input(L["retail_d"], min_value=1, value=40)
    retail_height = st.number_input(L["retail_h"], min_value=1, value=194)
    retail_weight = st.number_input(L["retail_weight"], min_value=0.1, value=20.0, step=0.1)

with col2:
    master_width = st.number_input(L["master_w"], min_value=1, value=600)
    master_depth = st.number_input(L["master_d"], min_value=1, value=400)
    master_height = st.number_input(L["master_h"], min_value=1, value=300)
    pallet_width = st.number_input(L["pallet_w"], min_value=1, value=1200)
    pallet_depth = st.number_input(L["pallet_d"], min_value=1, value=800)
    pallet_height = st.number_input(L["pallet_h"], min_value=1, value=1800)

def generate_packing_options(rw, rd, rh, mw, md, mh):
    options = []
    index = 0
    for x in range(1, mw // rw + 1):
        for y in range(1, md // rd + 1):
            for z in range(1, mh // rh + 1):
                if x * rw <= mw and y * rd <= md and z * rh <= mh:
                    count = x * y * z
                    options.append({
                        "Varianta": f"V{index+1}",
                        "Rozměry retail boxu": f"{rw}x{rd}x{rh}",
                        "Rozložení počtu": f"{x}x{y}x{z}",
                        "Celkem krabiček": count,
                        "Odhadovaná cena": round(count * 0.3, 2)
                    })
                    index += 1
    return options

if st.button(L["run"]):
    df_result = pd.DataFrame(generate_packing_options(retail_width, retail_depth, retail_height, master_width, master_depth, master_height))

    if not df_result.empty:
        df_result = df_result.sort_values(by="Celkem krabiček", ascending=False)
        best = df_result.iloc[0]
        computed_master_weight = (best['Celkem krabiček'] * retail_weight) / 1000  # g to kg

        master_per_layer = (pallet_width // master_width) * (pallet_depth // master_depth)
        layers_on_pallet = pallet_height // master_height
        total_on_pallet = master_per_layer * layers_on_pallet

        total_retail_on_pallet = int(best['Celkem krabiček']) * total_on_pallet
        total_weight = computed_master_weight * total_on_pallet

        st.success(f"{L['best']}: {best['Varianta']} – {best['Celkem krabiček']} ks / master karton")
        st.info(L["pallet_summary"].format(m=total_on_pallet, r=total_retail_on_pallet))
        st.dataframe(df_result.reset_index(drop=True))
    else:
        st.error(L["error"])

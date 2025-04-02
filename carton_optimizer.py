import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import product

# Jazykové přepínání
LANGUAGES = ["Čeština", "English"]
DEFAULT_LANG = LANGUAGES[0]
lang = st.sidebar.selectbox("🌐 Jazyk / Language", LANGUAGES)

T = {
    "Čeština": {
        "title": "🧮 Optimalizace balení",
        "description": "Zadej rozměry retail balení, master kartonu a palety...",
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
        "run": "Spustit výpočet",
        "reset": "🔄 Nový výpočet",
        "best": "Nejlepší varianta",
        "pallet_summary": "Na paletu se vejde {m} master kartonů → {r} retail krabiček",
        "show_unused": "Zobrazit nevyužitý prostor",
        "layout_box": "Retail balení v kartonu",
        "layout_pallet": "Master kartony na paletě",
        "error": "Retail balení je větší než master karton – nelze vložit."
    },
    "English": {
        "title": "🧮 Packaging Optimization",
        "description": "Enter dimensions of retail, master carton and pallet...",
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
        "run": "Run calculation",
        "reset": "🔄 New calculation",
        "best": "Best variant",
        "pallet_summary": "Pallet fits {m} master cartons → {r} retail boxes",
        "show_unused": "Show unused space",
        "layout_box": "Retail layout inside carton",
        "layout_pallet": "Master cartons layout on pallet",
        "error": "Retail box is larger than master carton – cannot fit."
    }
}

L = T.get(lang, T[DEFAULT_LANG])
product_name = st.sidebar.text_input(L["product"], value="produkt")

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

# Výpočet nejlepšího layoutu retail balení v kartonu
def calculate_retail_fit_in_carton(rw, rd, rh, mw, md, mh):
    orientations = list(product([rw, rd, rh], repeat=3))
    orientations = [o for o in orientations if len(set(o)) == 3]
    best_fit = None
    max_count = 0
    for w, d, h in orientations:
        count_w = mw // w
        count_d = md // d
        count_h = mh // h
        total = count_w * count_d * count_h
        if total > max_count:
            max_count = total
            best_fit = (count_w, count_d, count_h, w, d, h)
    return best_fit, max_count

# Hlavní výpočet
best_fit, max_count = calculate_retail_fit_in_carton(
    retail_width, retail_depth, retail_height,
    master_width, master_depth, master_height
)

if best_fit:
    count_w, count_d, count_h, rw_final, rd_final, rh_final = best_fit
    count_x = pallet_width // master_width
    count_y = pallet_depth // master_depth
    count_z = pallet_height // master_height
    total_master_cartons = count_x * count_y * count_z
    total_retail_boxes = total_master_cartons * max_count

    st.success(f"Retail krabiček v kartonu: {max_count} ({count_w}x{count_d}x{count_h})")
    st.info(L["pallet_summary"].format(m=total_master_cartons, r=total_retail_boxes))

    show_unused = st.checkbox(L["show_unused"], value=False)

    st.subheader(L["layout_box"])
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, projection='3d')
    for x in range(count_w):
        for y in range(count_d):
            for z in range(count_h):
                ax.bar3d(x * rw_final, y * rd_final, z * rh_final, rw_final, rd_final, rh_final, alpha=0.6, color='skyblue', edgecolor='gray')
    if show_unused:
        for x in np.arange(count_w * rw_final, master_width, rw_final):
            for y in np.arange(0, master_depth, rd_final):
                for z in np.arange(0, master_height, rh_final):
                    ax.bar3d(x, y, z, rw_final, rd_final, rh_final, alpha=0.1, color='gray', edgecolor='lightgray')
        for x in np.arange(0, master_width, rw_final):
            for y in np.arange(count_d * rd_final, master_depth, rd_final):
                for z in np.arange(0, master_height, rh_final):
                    ax.bar3d(x, y, z, rw_final, rd_final, rh_final, alpha=0.1, color='gray', edgecolor='lightgray')
        for x in np.arange(0, master_width, rw_final):
            for y in np.arange(0, master_depth, rd_final):
                for z in np.arange(count_h * rh_final, master_height, rh_final):
                    ax.bar3d(x, y, z, rw_final, rd_final, rh_final, alpha=0.1, color='gray', edgecolor='lightgray')
    ax.set_xlim([0, master_width])
    ax.set_ylim([0, master_depth])
    ax.set_zlim([0, master_height])
    ax.set_xlabel("Šířka (mm)")
    ax.set_ylabel("Hloubka (mm)")
    ax.set_zlabel("Výška (mm)")
    ax.set_title(L["layout_box"])
    st.pyplot(fig)

    st.subheader(L["layout_pallet"])
    fig2 = plt.figure(figsize=(7, 6))
    ax2 = fig2.add_subplot(111, projection='3d')
    for x in range(count_x):
        for y in range(count_y):
            for z in range(count_z):
                ax2.bar3d(x * master_width, y * master_depth, z * master_height, master_width, master_depth, master_height, alpha=0.6, color='orange', edgecolor='black')
    if show_unused:
        for x in np.arange(count_x * master_width, pallet_width, master_width):
            for y in np.arange(0, pallet_depth, master_depth):
                for z in np.arange(0, pallet_height, master_height):
                    ax2.bar3d(x, y, z, master_width, master_depth, master_height, alpha=0.1, color='gray', edgecolor='lightgray')
        for x in np.arange(0, pallet_width, master_width):
            for y in np.arange(count_y * master_depth, pallet_depth, master_depth):
                for z in np.arange(0, pallet_height, master_height):
                    ax2.bar3d(x, y, z, master_width, master_depth, master_height, alpha=0.1, color='gray', edgecolor='lightgray')
        for x in np.arange(0, pallet_width, master_width):
            for y in np.arange(0, pallet_depth, master_depth):
                for z in np.arange(count_z * master_height, pallet_height, master_height):
                    ax2.bar3d(x, y, z, master_width, master_depth, master_height, alpha=0.1, color='gray', edgecolor='lightgray')
    ax2.set_xlim([0, pallet_width])
    ax2.set_ylim([0, pallet_depth])
    ax2.set_zlim([0, pallet_height])
    ax2.set_xlabel("Šířka (mm)")
    ax2.set_ylabel("Hloubka (mm)")
    ax2.set_zlabel("Výška (mm)")
    ax2.set_title(L["layout_pallet"])
    st.pyplot(fig2)
else:
    st.error(L["error"])

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import permutations

# Jazykové přepínání
LANGUAGES = ["Čeština", "English"]
DEFAULT_LANG = LANGUAGES[0]
lang = st.sidebar.selectbox("\ud83c\udf10 Jazyk / Language", LANGUAGES)

T = {
    "Čeština": {
        "title": "\ud83e\uddae Optimalizace balení",
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
        "reset": "\ud83d\udd04 Nový výpočet",
        "best": "Nejlepší varianta",
        "pallet_summary": "Na paletu se vejde {m} master kartonů → {r} retail krabiček",
        "show_unused": "Zobrazit nevyužitý prostor",
        "layout_box": "Retail balení v kartonu",
        "layout_pallet": "Master kartony na paletě",
        "error": "Retail balení je větší než master karton – nelze vložit."
    },
    "English": {
        "title": "\ud83e\uddae Packaging Optimization",
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
        "reset": "\ud83d\udd04 New calculation",
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

# Výpočet nejlepší rotace a počtu balení / kartonů

def calculate_best_fit(product_dims, container_dims):
    max_units = 0
    best_fit = None
    for orientation in permutations(product_dims):
        fits = [container_dims[i] // orientation[i] for i in range(3)]
        total = np.prod(fits)
        if total > max_units:
            max_units = total
            best_fit = (*fits, orientation)
    return best_fit, max_units

retail_fit, retail_total = calculate_best_fit(
    (retail_width, retail_depth, retail_height),
    (master_width, master_depth, master_height)
)

carton_fit, carton_total = calculate_best_fit(
    (master_width, master_depth, master_height),
    (pallet_width, pallet_depth, pallet_height)
)

total_retail = retail_total * carton_total

if retail_fit and carton_fit:
    rw, rd, rh = retail_fit[3]
    cx, cy, cz = carton_fit[0], carton_fit[1], carton_fit[2]
    mw, md, mh = carton_fit[3]

    st.success(f"Retail krabiček v kartonu: {retail_total} ({retail_fit[0]}x{retail_fit[1]}x{retail_fit[2]})")
    st.info(L["pallet_summary"].format(m=carton_total, r=total_retail))

    show_unused = st.checkbox(L["show_unused"], value=False)

    st.subheader(L["layout_box"])
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, projection='3d')
    for x in range(retail_fit[0]):
        for y in range(retail_fit[1]):
            for z in range(retail_fit[2]):
                ax.bar3d(x * rw, y * rd, z * rh, rw, rd, rh, alpha=0.6, color='skyblue', edgecolor='gray')
    if show_unused:
        unused_x = master_width - (retail_fit[0] * rw)
        unused_y = master_depth - (retail_fit[1] * rd)
        unused_z = master_height - (retail_fit[2] * rh)
        if unused_x > 0:
            ax.bar3d(retail_fit[0]*rw, 0, 0, unused_x, master_depth, master_height, alpha=0.1, color='gray')
        if unused_y > 0:
            ax.bar3d(0, retail_fit[1]*rd, 0, master_width, unused_y, master_height, alpha=0.1, color='gray')
        if unused_z > 0:
            ax.bar3d(0, 0, retail_fit[2]*rh, master_width, master_depth, unused_z, alpha=0.1, color='gray')
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
    for x in range(cx):
        for y in range(cy):
            for z in range(cz):
                ax2.bar3d(x * mw, y * md, z * mh, mw, md, mh, alpha=0.6, color='orange', edgecolor='black')
    if show_unused:
        unused_x = pallet_width - (cx * mw)
        unused_y = pallet_depth - (cy * md)
        unused_z = pallet_height - (cz * mh)
        if unused_x > 0:
            ax2.bar3d(cx * mw, 0, 0, unused_x, pallet_depth, pallet_height, alpha=0.1, color='gray')
        if unused_y > 0:
            ax2.bar3d(0, cy * md, 0, pallet_width, unused_y, pallet_height, alpha=0.1, color='gray')
        if unused_z > 0:
            ax2.bar3d(0, 0, cz * mh, pallet_width, pallet_depth, unused_z, alpha=0.1, color='gray')
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


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations

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

show_unused = st.checkbox(L["show_unused"], value=True)

def generate_packing_options(rw, rd, rh, mw, md, mh):
    options = []
    for x in range(1, mw // rw + 1):
        for y in range(1, md // rd + 1):
            for z in range(1, mh // rh + 1):
                if x * rw <= mw and y * rd <= md and z * rh <= mh:
                    count = x * y * z
                    options.append({
                        "Rozložení počtu": f"{x}x{y}x{z}",
                        "Celkem krabiček": count
                    })
    return options

def draw_boxes_in_carton(size, layout, show_empty=True):
    rw, rd, rh = size
    nx, ny, nz = layout
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection='3d')
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                ax.bar3d(x*rw, y*rd, z*rh, rw, rd, rh, color='skyblue', edgecolor='k', alpha=0.9)
    if show_empty:
        w, d, h = rw*nx, rd*ny, rh*nz
        r = [[0, w], [0, d], [0, h]]
        for s, e in combinations(np.array(list(product(*r))), 2):
            if np.sum(np.abs(s - e) == np.array([w, d, h])) == 1:
                ax.plot3D(*zip(s, e), color="gray", linewidth=1.2, alpha=0.5)
    ax.set_xlabel("Šířka")
    ax.set_ylabel("Hloubka")
    ax.set_zlabel("Výška")
    return fig

def draw_cartons_on_pallet(pw, pd, ph, cw, cd, ch):
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111, projection='3d')
    per_row = pw // cw
    per_col = pd // cd
    layers = ph // ch
    for z in range(layers):
        for x in range(per_row):
            for y in range(per_col):
                ax.bar3d(x*cw, y*cd, z*ch, cw, cd, ch, color='orange', edgecolor='k', alpha=0.8)
    ax.set_xlabel("Šířka")
    ax.set_ylabel("Hloubka")
    ax.set_zlabel("Výška")
    return fig

if st.button(L["run"]):
    df = pd.DataFrame(generate_packing_options(retail_width, retail_depth, retail_height, master_width, master_depth, master_height))
    if not df.empty:
        df = df.sort_values(by="Celkem krabiček", ascending=False)
        best = df.iloc[0]
        layout = tuple(map(int, best["Rozložení počtu"].split("x")))
        st.success(f"{L['best']}: {best['Rozložení počtu']} → {best['Celkem krabiček']} ks")

        st.subheader(L["layout_box"])
        fig1 = draw_boxes_in_carton((retail_width, retail_depth, retail_height), layout, show_unused)
        st.pyplot(fig1)

        st.subheader(L["layout_pallet"])
        fig2 = draw_cartons_on_pallet(pallet_width, pallet_depth, pallet_height, master_width, master_depth, master_height)
        st.pyplot(fig2)

        total_master = (pallet_width // master_width) * (pallet_depth // master_depth) * (pallet_height // master_height)
        total_retail = total_master * best["Celkem krabiček"]
        st.info(L["pallet_summary"].format(m=total_master, r=total_retail))
    else:
        st.error(L["error"])

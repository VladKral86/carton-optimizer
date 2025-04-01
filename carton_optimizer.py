
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations

# Jazykové přepínání
LANGUAGES = ["Čeština", "English"]
DEFAULT_LANG = LANGUAGES[0]
lang = st.sidebar.selectbox("Jazyk / Language", LANGUAGES)

# Texty dle zvoleného jazyka
T = {
    "Čeština": {
        "title": "Optimalizace balení",
        "description": "Zadej rozměry retail balení, master kartonu a palety.",
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
        "reset": "Nový výpočet",
        "best": "Nejlepší varianta",
        "pallet_summary": "Na paletu se vejde {m} master kartonů → {r} retail krabiček",
        "show_unused": "Zobrazit nevyužitý prostor",
        "layout_box": "Retail balení v kartonu",
        "layout_pallet": "Master kartony na paletě",
        "error": "Retail balení je větší než master karton – nelze vložit."
    },
    "English": {
        "title": "Packaging Optimization",
        "description": "Enter dimensions of retail, master carton and pallet.",
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
        "reset": "New calculation",
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

if "best_result" not in st.session_state:
    st.session_state.best_result = None
    st.session_state.layout = None

if st.button(L["run"]):
    options = []
    for x in range(1, master_width // retail_width + 1):
        for y in range(1, master_depth // retail_depth + 1):
            for z in range(1, master_height // retail_height + 1):
                if x * retail_width <= master_width and y * retail_depth <= master_depth and z * retail_height <= master_height:
                    count = x * y * z
                    options.append({"Rozložení počtu": f"{x}x{y}x{z}", "Celkem krabiček": count})

    df = pd.DataFrame(options).sort_values(by="Celkem krabiček", ascending=False)
    if not df.empty:
        best = df.iloc[0]
        st.session_state.best_result = best
        st.session_state.layout = tuple(map(int, best["Rozložení počtu"].split("x")))
        st.success(f"{L['best']}: {best['Rozložení počtu']} → {best['Celkem krabiček']} ks")
        st.dataframe(df.reset_index(drop=True))
    else:
        st.error(L["error"])

if st.session_state.best_result:
    st.subheader(L["layout_box"])
    nx, ny, nz = st.session_state.layout
    fig1 = plt.figure(figsize=(7, 5))
    ax1 = fig1.add_subplot(111, projection='3d')
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                ax1.bar3d(x*retail_width, y*retail_depth, z*retail_height, retail_width, retail_depth, retail_height, color='skyblue', edgecolor='k', alpha=0.9)
    if show_unused:
        w, d, h = retail_width*nx, retail_depth*ny, retail_height*nz
        r = [[0, w], [0, d], [0, h]]
        for s, e in combinations(np.array(list(product(*r))), 2):
            if np.sum(np.abs(s - e) == np.array([w, d, h])) == 1:
                ax1.plot3D(*zip(s, e), color="gray", linewidth=1.2, alpha=0.5)
    ax1.set_xlim(0, retail_width*nx)
    ax1.set_ylim(0, retail_depth*ny)
    ax1.set_zlim(0, retail_height*nz)
    ax1.set_xlabel("Šířka")
    ax1.set_ylabel("Hloubka")
    ax1.set_zlabel("Výška")
    st.pyplot(fig1)

    st.subheader(L["layout_pallet"])
    fig2 = plt.figure(figsize=(8, 5))
    ax2 = fig2.add_subplot(111, projection='3d')
    per_row = pallet_width // master_width
    per_col = pallet_depth // master_depth
    layers = pallet_height // master_height
    for z in range(layers):
        for x in range(per_row):
            for y in range(per_col):
                ax2.bar3d(x*master_width, y*master_depth, z*master_height, master_width, master_depth, master_height, color='orange', edgecolor='k', alpha=0.8)
    ax2.set_xlim(0, pallet_width)
    ax2.set_ylim(0, pallet_depth)
    ax2.set_zlim(0, pallet_height)
    ax2.set_xlabel("Šířka")
    ax2.set_ylabel("Hloubka")
    ax2.set_zlabel("Výška")
    st.pyplot(fig2)

    total_master = per_row * per_col * layers
    total_retail = total_master * st.session_state.best_result["Celkem krabiček"]
    st.info(L["pallet_summary"].format(m=total_master, r=total_retail))

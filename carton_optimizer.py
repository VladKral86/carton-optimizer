import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# Constants
LANGUAGES = ["Čeština", "English"]
DEFAULT_LANG = LANGUAGES[0]

lang = st.sidebar.selectbox("🌐 Jazyk / Language", LANGUAGES)

T = {
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
        "run": "Spustit výpočet",
        "reset": "🔄 Nový výpočet",
        "best": "Nejlepší varianta",
        "pallet_summary": "Na paletu se vejde {m} master kartonů → {r} retail krabiček",
        "show_unused": "Zobrazit nevyužitý prostor",
        "layout_box": "Rozložení retail balení v master kartonu",
        "layout_pallet": "Rozložení master kartonů na paletě",
        "export_pdf": "📄 Exportovat výstup do PDF",
        "error": "Retail balení je větší než master karton – nelze vložit."
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
        "run": "Run calculation",
        "reset": "🔄 New calculation",
        "best": "Best variant",
        "pallet_summary": "Pallet fits {m} master cartons → {r} retail boxes",
        "show_unused": "Show unused space",
        "layout_box": "Retail layout inside master carton",
        "layout_pallet": "Master cartons layout on pallet",
        "export_pdf": "📄 Export results to PDF",
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
    index = 0
    for x in range(1, mw // rw + 1):
        for y in range(1, md // rd + 1):
            for z in range(1, mh // rh + 1):
                if x * rw <= mw and y * rd <= md and z * rh <= mh:
                    count = x * y * z
                    options.append({
                        "Varianta": f"V{index+1}",
                        "Rozložení počtu": f"{x}x{y}x{z}",
                        "Celkem krabiček": count
                    })
                    index += 1
    return options

def draw_boxes_in_master_carton(retail_size, layout_xyz, show_empty=True):
    rw, rd, rh = retail_size
    x_count, y_count, z_count = layout_xyz
    total_width = rw * x_count
    total_depth = rd * y_count
    total_height = rh * z_count
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection='3d')
    for x in range(x_count):
        for y in range(y_count):
            for z in range(z_count):
                ax.bar3d(x*rw, y*rd, z*rh, rw, rd, rh, color='skyblue', edgecolor='k', alpha=0.9)
    if show_empty:
        r = [[0, total_width], [0, total_depth], [0, total_height]]
        for s, e in combinations(np.array(list(product(*r))), 2):
            if np.sum(np.abs(s - e) == np.array([total_width, total_depth, total_height])) == 1:
                ax.plot3D(*zip(s, e), color="gray", linewidth=1.2, alpha=0.5)
    ax.set_xlim(0, total_width)
    ax.set_ylim(0, total_depth)
    ax.set_zlim(0, total_height)
    ax.set_xlabel("Šířka")
    ax.set_ylabel("Hloubka")
    ax.set_zlabel("Výška")
    return fig

def export_to_pdf(product_name, best_variant, retail_count, master_count):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Výsledek optimalizace balení", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Produkt: {product_name}", ln=True)
    pdf.cell(200, 10, txt=f"Varianta: {best_variant}", ln=True)
    pdf.cell(200, 10, txt=f"Retail balení celkem: {retail_count}", ln=True)
    pdf.cell(200, 10, txt=f"Master kartonů na paletu: {master_count}", ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer

if st.button(L["run"]):
    df_result = pd.DataFrame(generate_packing_options(retail_width, retail_depth, retail_height, master_width, master_depth, master_height))
    if not df_result.empty:
        df_result = df_result.sort_values(by="Celkem krabiček", ascending=False)
        best = df_result.iloc[0]
        counts = best["Rozložení počtu"].split("x")
        layout_xyz = (int(counts[0]), int(counts[1]), int(counts[2]))

        st.success(f"{L['best']}: {best['Varianta']} – {best['Celkem krabiček']} ks / master karton")
        st.dataframe(df_result.reset_index(drop=True))

        st.subheader(L["layout_box"])
        fig1 = draw_boxes_in_master_carton((retail_width, retail_depth, retail_height), layout_xyz, show_unused)
        st.pyplot(fig1)

        master_per_layer = (pallet_width // master_width) * (pallet_depth // master_depth)
        layers_on_pallet = pallet_height // master_height
        total_on_pallet = master_per_layer * layers_on_pallet
        total_retail_on_pallet = int(best['Celkem krabiček']) * total_on_pallet

        st.subheader(L["layout_pallet"])
        st.info(L["pallet_summary"].format(m=total_on_pallet, r=total_retail_on_pallet))

        if st.button(L["export_pdf"]):
            pdf_buffer = export_to_pdf(product_name, best["Varianta"], total_retail_on_pallet, total_on_pallet)
            st.download_button(label="📥 Stáhnout PDF", data=pdf_buffer, file_name="baleni_vystup.pdf")

    else:
        st.error(L["error"])

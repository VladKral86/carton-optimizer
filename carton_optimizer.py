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

# Dummy fallback variables for first run
best = {'Varianta': 'N/A', 'Celkem krabiček': 0}
total_price = 0.0
total_retail_on_pallet = 0
total_weight = 0.0
pallet_price = 0.0
calculation_done = False

# Scroll to top function
def scroll_to_top():
    st.markdown("""
        <script>
            window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
    """, unsafe_allow_html=True)

# Sidebar input
product_name = st.sidebar.text_input("Název produktu nebo zákazníka", value="produkt")

# File name generation
now_str = datetime.now().strftime("%Y%m%d_%H%M")
name_clean = product_name.replace(" ", "_").replace("/", "-")
file_prefix = f"baleni_{name_clean}_{best['Varianta']}_retail{best['Celkem krabiček']}_{now_str}"

# Dummy dataframe fallback
if 'df_result' not in locals():
    df_result = pd.DataFrame({
        "Varianta": [],
        "Rozměry retail boxu": [],
        "Rozložení počtu": [],
        "Celkem krabiček": [],
        "Odhadovaná cena": []
    })

# MAIN SECTION – Výpočet a rozvržení
st.title("🧮 Optimalizace balení")
st.markdown("Zadej rozměry retail balení, master kartonu a palety. Aplikace najde nejlepší uspořádání a rozvržení na paletu.")

col1, col2 = st.columns(2)

with col1:
    retail_width = st.number_input("Šířka retail krabičky (mm)", min_value=1, value=130)
    retail_depth = st.number_input("Hloubka retail krabičky (mm)", min_value=1, value=40)
    retail_height = st.number_input("Výška retail krabičky (mm)", min_value=1, value=194)
    master_weight = st.number_input("Hmotnost 1 master kartonu (kg)", min_value=0.1, value=7.0, step=0.1)
    master_price = st.number_input("Cena za 1 master karton (Kč)", min_value=0.0, value=89.0, step=1.0)

with col2:
    master_width = st.number_input("Šířka master kartonu (mm)", min_value=1, value=600)
    master_depth = st.number_input("Hloubka master kartonu (mm)", min_value=1, value=400)
    master_height = st.number_input("Výška master kartonu (mm)", min_value=1, value=300)
    pallet_width = st.number_input("Max. šířka palety (mm)", min_value=1, value=1200)
    pallet_depth = st.number_input("Max. hloubka palety (mm)", min_value=1, value=800)
    pallet_height = st.number_input("Max. výška palety (mm)", min_value=1, value=1800)

if st.button("Spustit výpočet"):
    calculation_done = True
    options = []
    index = 0
    for x in range(1, master_width // retail_width + 1):
        for y in range(1, master_depth // retail_depth + 1):
            for z in range(1, master_height // retail_height + 1):
                if x * retail_width <= master_width and y * retail_depth <= master_depth and z * retail_height <= master_height:
                    count = x * y * z
                    options.append({
                        "Varianta": f"V{index+1}",
                        "Rozměry retail boxu": f"{retail_width}x{retail_depth}x{retail_height}",
                        "Rozložení počtu": f"{x}x{y}x{z}",
                        "Celkem krabiček": count,
                        "Odhadovaná cena": count * 0.3,
                        "Rozměr": (x * retail_width, y * retail_depth, z * retail_height)
                    })
                    index += 1

    if options:
        df_result = pd.DataFrame(options)
        df_result = df_result.sort_values(by="Celkem krabiček", ascending=False)
        best = df_result.iloc[0]

        master_per_layer = (pallet_width // master_width) * (pallet_depth // master_depth)
        layers_on_pallet = pallet_height // master_height
        total_on_pallet = master_per_layer * layers_on_pallet

        total_retail_on_pallet = int(best['Celkem krabiček']) * total_on_pallet
        total_weight = master_weight * total_on_pallet
        pallet_price = master_price * total_on_pallet

        st.success(f"Nejlepší varianta: {best['Varianta']} – {best['Celkem krabiček']} krabiček / karton")
        st.info(f"Na paletu se vejde {total_on_pallet} master kartonů → {total_retail_on_pallet} retail krabiček")
        st.dataframe(df_result.reset_index(drop=True))

        # 3D náhled (jen horní vrstva)
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title("Rozložení master kartonů na paletě (1 vrstva)")

        for i in range(pallet_width // master_width):
            for j in range(pallet_depth // master_depth):
                x, y, z = i * master_width, j * master_depth, 0
                dx, dy, dz = master_width, master_depth, master_height
                ax.bar3d(x, y, z, dx, dy, dz, shade=True, alpha=0.6)

        ax.set_xlim(0, pallet_width)
        ax.set_ylim(0, pallet_depth)
        ax.set_zlim(0, master_height)
        st.pyplot(fig)
    else:
        st.error("Retail balení je větší než master karton – nelze vložit.")

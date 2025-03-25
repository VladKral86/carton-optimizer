
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

# Uživatelský vstup pro název produktu nebo zákazníka
product_name = st.sidebar.text_input("Název produktu nebo zákazníka", value="produkt")

# Generování názvu souboru
now_str = datetime.now().strftime("%Y%m%d_%H%M")
name_clean = product_name.replace(" ", "_").replace("/", "-")
file_prefix = f"baleni_{name_clean}_{best['Varianta']}_retail{best['Celkem krabiček']}_{now_str}"

# Export do Excelu
if st.sidebar.button("Exportovat výsledky do Excelu"):
    excel_buffer = BytesIO()
    export_df = df_result.drop(columns=["Rozměry retail boxu", "Rozložení počtu"])
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, sheet_name="Varianty balení", index=False)
        summary_data = pd.DataFrame({
            "Parametr": [
                "Nejlepší varianta",
                "Retail krabiček v master kartonu",
                "Cena za 1 master karton (Kč)",
                "Retail krabiček na paletě",
                "Hmotnost palety (kg)",
                "Hodnota palety (Kč)"
            ],
            "Hodnota": [
                best['Varianta'],
                best['Celkem krabiček'],
                f"{total_price:.2f}",
                total_retail_on_pallet,
                f"{total_weight:.2f}",
                f"{pallet_price:.2f}"
            ]
        })
        summary_data.to_excel(writer, sheet_name="Souhrn logistika", index=False)
    st.download_button(
        label="📥 Stáhnout Excel",
        data=excel_buffer.getvalue(),
        file_name=f"{file_prefix}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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

# Excel export
if st.sidebar.button("Exportovat výsledky do Excelu"):
    if best['Varianta'] == 'N/A':
        st.warning("❗ Nejprve proveďte výpočet optimálního balení.")
        scroll_to_top()
    else:
        excel_buffer = BytesIO()
        export_df = pd.DataFrame()  # fallback if df_result is not defined
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

# PDF export
if st.sidebar.button("Exportovat výsledky do PDF"):
    if best['Varianta'] == 'N/A':
        st.warning("❗ Nejprve proveďte výpočet optimálního balení.")
        scroll_to_top()
    else:
        temp_dir = tempfile.mkdtemp()

        def save_plot_as_image(fig, filename):
            fig.savefig(filename, bbox_inches='tight')

        # Save dummy plots
        fig_master = plt.figure(figsize=(8, 6))
        ax1 = fig_master.add_subplot(111, projection='3d')
        ax1.set_title("Master karton")
        master_img_path = os.path.join(temp_dir, "master_karton.png")
        save_plot_as_image(fig_master, master_img_path)

        fig_pallet = plt.figure(figsize=(8, 6))
        ax2 = fig_pallet.add_subplot(111, projection='3d')
        ax2.set_title("Paleta")
        pallet_img_path = os.path.join(temp_dir, "paleta.png")
        save_plot_as_image(fig_pallet, pallet_img_path)

        # PDF generation
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Optimalizace balení - Souhrn", ln=True, align='C')
        pdf.ln(10)

        rows = [
            ("Produkt / zákazník", product_name),
            ("Nejlepší varianta", best['Varianta']),
            ("Retail krabiček v master kartonu", best['Celkem krabiček']),
            ("Cena za 1 master karton (Kč)", f"{total_price:.2f}"),
            ("Retail krabiček na paletě", total_retail_on_pallet),
            ("Hmotnost palety (kg)", f"{total_weight:.2f}"),
            ("Hodnota palety (Kč)", f"{pallet_price:.2f}")
        ]
        for param, val in rows:
            pdf.cell(0, 10, f"{param}: {val}", ln=True)

        pdf.ln(5)
        pdf.image(master_img_path, w=170)
        pdf.ln(5)
        pdf.image(pallet_img_path, w=170)

        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        st.download_button(
            label="📄 Stáhnout PDF",
            data=pdf_buffer.getvalue(),
            file_name=f"{file_prefix}.pdf",
            mime="application/pdf"
        )

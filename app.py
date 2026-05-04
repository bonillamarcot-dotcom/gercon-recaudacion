import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF

st.set_page_config(page_title="Gercon - Auditoría Blindada", layout="wide")

# --- LOGO DE INGENIERÍA GERCON ---
logo_path = "logo_gercon.png" 
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("GRUPO GERCON")

st.title("📊 Auditoría de Recaudación y Generación")
st.markdown("---")

# --- ÚNICO CAMPO MODIFICABLE ---
with st.sidebar:
    st.header("⚙️ Entrada de Datos")
    poblacion = st.number_input("Población Total (Habitantes)", value=28900, step=100)
    st.info("Este modelo calcula automáticamente las viviendas, comercios e industrias de forma proporcional a la población.")

# --- LÓGICA DE CÁLCULO TÉCNICO (FACTORES EXACTOS DEL EXCEL) ---
ppc = 0.623 # kg/hab/día
ton_dia = (poblacion * ppc) / 1000
ton_mes = ton_dia * 30

# Factores exactos por habitante extraídos de tu Excel
f_pop = 4644.9 / 28900
f_med = 4644 / 28900
f_alt = 2580 / 28900
f_com = 413 / 28900
f_ind = 258 / 28900

# Unidades Calculadas (BLOQUEADAS PARA EDICIÓN)
cant_pop = int(poblacion * f_pop)
cant_med = int(poblacion * f_med)
cant_alt = int(poblacion * f_alt)
cant_com = int(poblacion * f_com)
cant_ind = int(poblacion * f_ind)

# Tarifas Fijas
t_pop, t_med, t_alt, t_com, t_ind = 1.5, 3.0, 5.0, 30.0, 350.0

# Recaudación por categoría
rec_pop, rec_med, rec_alt = cant_pop * t_pop, cant_med * t_med, cant_alt * t_alt
rec_com, rec_ind = cant_com * t_com, cant_ind * t_ind
total = rec_pop + rec_med + rec_alt + rec_com + rec_ind

# --- PANTALLA PRINCIPAL ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Generación Diaria", f"{ton_dia:.2f} Ton")
m2.metric("Generación Mensual", f"{ton_mes:.2f} Ton")
m3.metric("Total Suscriptores", f"{cant_pop + cant_med + cant_alt + cant_com + cant_ind:,}")
m4.metric("Recaudación Mensual", f"${total:,.2f}")

st.markdown("---")
st.subheader("📋 Detalle de Unidades y Recaudación (Cálculo Automático)")

# TABLA COMPLETA CON VIVIENDAS, COMERCIOS E INDUSTRIAS
data = {
    "Categoría": [
        "Vivienda Sector Popular", 
        "Vivienda Sector Medio", 
        "Vivienda Sector Alto", 
        "Comercial", 
        "Industrial"
    ],
    "Unidades Arrojadas": [cant_pop, cant_med, cant_alt, cant_com, cant_ind],
    "Tarifa Fija ($)": [t_pop, t_med, t_alt, t_com, t_ind],
    "Recaudación Estimada ($)": [rec_pop, rec_med, rec_alt, rec_com, rec_ind]
}
df_resumen = pd.DataFrame(data)

# Formateo para visualización en la web
df_visual = df_resumen.copy()
df_visual["Recaudación Estimada ($)"] = df_visual["Recaudación Estimada ($)"].map("${:,.2f}".format)
st.table(df_visual)

# --- EXPORTACIÓN A PDF ---
def generate_pdf(df, p, td, tt):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="REPORTE TÉCNICO - INGENIERÍA GERCON C.A.", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Análisis para Población de {p} Habitantes", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Indicadores Operativos:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Generación Diaria: {td:.2f} Toneladas", ln=True)
    pdf.cell(0, 10, f"- Recaudación Mensual: ${tt:,.2f}", ln=True)
    pdf.ln(10)
    
    # Tabla en el PDF
    pdf.set_font("Arial", "B", 10)
    pdf.cell(55, 10, "Categoría", 1)
    pdf.cell(35, 10, "Unidades", 1)
    pdf.cell(35, 10, "Tarifa ($)", 1)
    pdf.cell(50, 10, "Subtotal ($)", 1)
    pdf.ln()
    
    pdf.set_font("Arial", "", 10)
    for i in range(len(df)):
        pdf.cell(55, 10, str(df.iloc[i, 0]), 1)
        pdf.cell(35, 10, str(df.iloc[i, 1]), 1)
        pdf.cell(35, 10, f"{df.iloc[i, 2]:.2f}", 1)
        pdf.cell(50, 10, f"{df.iloc[i, 3]:.2f}", 1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin-1")

pdf_data = generate_pdf(df_resumen, poblacion, ton_dia, total)
st.download_button("📥 Descargar Reporte en PDF", pdf_data, f"Gercon_{poblacion}_hab.pdf", "application/pdf")

st.bar_chart(df_resumen.set_index("Categoría")["Recaudación Estimada ($)"])
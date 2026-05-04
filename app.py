import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF

st.set_page_config(page_title="Gercon - Auditoría Dinámica", layout="wide")

# --- LOGO DE INGENIERÍA GERCON ---
logo_path = "logo_gercon.png" 
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("GRUPO GERCON")

st.title("📊 Auditoría de Recaudación y Generación")
st.markdown("---")

# --- BARRA LATERAL: ENTRADAS MODIFICABLES ---
with st.sidebar:
    st.header("⚙️ Configuración del Modelo")
    poblacion = st.number_input("Población Total (Habitantes)", value=28900, step=100)
    
    st.subheader("💰 Editar Tarifas ($)")
    t_pop = st.number_input("Tarifa Sector Popular", value=1.5)
    t_med = st.number_input("Tarifa Sector Medio", value=3.0)
    t_alt = st.number_input("Tarifa Sector Alto", value=5.0)
    t_com = st.number_input("Tarifa Comercial Promedio", value=30.0)
    t_ind = st.number_input("Tarifa Industrial Promedio", value=350.0)
    
    st.info("Nota: Las cantidades de unidades son arrojadas automáticamente por el cálculo poblacional.")

# --- LÓGICA DE CÁLCULO TÉCNICO ---
ppc = 0.623 
ton_dia = (poblacion * ppc) / 1000
ton_mes = ton_dia * 30

# Factores exactos de tu Excel (blindados)
f_pop, f_med, f_alt = 4644.9/28900, 4644/28900, 2580/28900
f_com, f_ind = 413/28900, 258/28900

# Unidades Arrojadas (No editables)
cant_pop = int(poblacion * f_pop)
cant_med = int(poblacion * f_med)
cant_alt = int(poblacion * f_alt)
cant_com = int(poblacion * f_com)
cant_ind = int(poblacion * f_ind)

# Recaudación (Dinámica según las tarifas que elijas)
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
st.subheader("📋 Detalle Operativo y Financiero")

data = {
    "Categoría": ["Vivienda Popular", "Vivienda Medio", "Vivienda Alto", "Comercial", "Industrial"],
    "Unidades (Auto)": [cant_pop, cant_med, cant_alt, cant_com, cant_ind],
    "Tarifa Aplicada ($)": [t_pop, t_med, t_alt, t_com, t_ind],
    "Subtotal Mensual ($)": [rec_pop, rec_med, rec_alt, rec_com, rec_ind]
}
df_resumen = pd.DataFrame(data)

# Formateo visual
df_visual = df_resumen.copy()
df_visual["Subtotal Mensual ($)"] = df_visual["Subtotal Mensual ($)"].map("${:,.2f}".format)
st.table(df_visual)

# --- EXPORTACIÓN A PDF ---
def generate_pdf(df, p, td, tt):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="REPORTE DE AUDITORÍA - INGENIERÍA GERCON C.A.", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Población: {p} Habitantes", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(0, 10, f"Generación Diaria: {td:.2f} Toneladas", ln=True)
    pdf.cell(0, 10, f"Recaudación Total: ${tt:,.2f}", ln=True)
    pdf.ln(10)
    # Tabla
    pdf.set_font("Arial", "B", 10)
    cols = ["Categoría", "Unidades", "Tarifa ($)", "Total ($)"]
    for col in cols: pdf.cell(45, 10, col, 1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for i in range(len(df)):
        pdf.cell(45, 10, str(df.iloc[i, 0]), 1)
        pdf.cell(45, 10, str(df.iloc[i, 1]), 1)
        pdf.cell(45, 10, f"{df.iloc[i, 2]:.2f}", 1)
        pdf.cell(45, 10, f"{df.iloc[i, 3]:.2f}", 1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin-1")

pdf_data = generate_pdf(df_resumen, poblacion, ton_dia, total)
st.download_button("📥 Descargar Reporte PDF", pdf_data, f"Gercon_{poblacion}.pdf", "application/pdf")

st.bar_chart(df_resumen.set_index("Categoría")["Subtotal Mensual ($)"])
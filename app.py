import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF

st.set_page_config(page_title="Gercon - Calculadora de Gestión", layout="wide")

# --- IDENTIDAD CORPORATIVA ---
logo_path = "logo_gercon.png" 
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("GRUPO GERCON")

st.title("📊 Calculadora de Generación y Estimado de Recaudación")
st.markdown("---")

# --- ENTRADAS DE DATOS (BARRA LATERAL) ---
with st.sidebar:
    st.header("⚙️ Configuración de Parámetros")
    poblacion = st.number_input("Población Total (Habitantes)", value=28900, step=100)
    
    st.subheader("💰 Tarifas Mensuales ($)")
    t_pop = st.number_input("Tarifa Popular", value=1.5)
    t_med = st.number_input("Tarifa Medio", value=3.0)
    t_alt = st.number_input("Tarifa Alto", value=5.0)
    t_com = st.number_input("Tarifa Comercial", value=30.0)
    t_ind = st.number_input("Tarifa Industrial", value=350.0)
    
    st.markdown("---")
    st.subheader("🎯 Efectividad de Cobranza (%)")
    efec_res = st.slider("Efectividad Residencial", 0, 100, 70)
    efec_com = st.slider("Efectividad Comercial", 0, 100, 85)
    efec_ind = st.slider("Efectividad Industrial", 0, 100, 95)

# --- LÓGICA TÉCNICA (BASADA EN EL MODELO GERCON) ---

# 1. GENERACIÓN DE DESECHOS (LIMITADO A 2 DECIMALES)
factor_gen = 18 / 28900
ton_total_dia = round(poblacion * factor_gen, 2)

# Distribución técnica de generación
f_gen_res, f_gen_com, f_gen_ind = 0.81, 0.12, 0.07 
ton_res = round(ton_total_dia * f_gen_res, 2)
ton_com = round(ton_total_dia * f_gen_com, 2)
ton_ind = round(ton_total_dia * f_gen_ind, 2)

# 2. CENSO FÍSICO INTEGRADO (60-30-10 + Especiales)
viviendas_censo_total = poblacion * (5161 / 28900)
u_pop_censo = int(viviendas_censo_total * 0.60)
u_med_censo = int(viviendas_censo_total * 0.30)
u_alt_censo = int(viviendas_censo_total * 0.10)
u_com_censo = int(poblacion * (413 / 28900))
u_ind_censo = int(poblacion * (258 / 28900))

# 3. BASE DE RECAUDACIÓN (Unidades Financieras)
u_pop_rec = poblacion * (4644.9 / 28900)
u_med_rec = poblacion * (4644 / 28900)
u_alt_rec = poblacion * (2580 / 28900)
u_com_rec = poblacion * (413 / 28900)
u_ind_rec = poblacion * (258 / 28900)

# 4. CÁLCULO FINANCIERO
r_res_pot = (u_pop_rec * t_pop) + (u_med_rec * t_med) + (u_alt_rec * t_alt)
r_res_real = r_res_pot * (efec_res / 100)
r_com_pot = u_com_rec * t_com
r_com_real = r_com_pot * (efec_com / 100)
r_ind_pot = u_ind_rec * t_ind
r_ind_real = r_ind_pot * (efec_ind / 100)

total_potencial = r_res_pot + r_com_pot + r_ind_pot
total_real = r_res_real + r_com_real + r_ind_real

# --- INTERFAZ DE RESULTADOS ---

# SECCIÓN 1: GENERACIÓN (2 DECIMALES)
st.subheader("🚛 1. Cálculo de Generación de Desechos")
col_g1, col_g2 = st.columns([1, 2])
with col_g1:
    st.metric("Total General", f"{ton_total_dia:.2f} Ton/Día")
with col_g2:
    data_gen = {
        "Sector": ["Residencial", "Comercial", "Industrial"],
        "Generación (Ton/Día)": [f"{ton_res:.2f}", f"{ton_com:.2f}", f"{ton_ind:.2f}"]
    }
    st.table(pd.DataFrame(data_gen).set_index("Sector"))

st.markdown("---")

# SECCIÓN 2: CENSO FÍSICO INTEGRADO
st.subheader("🏠 2. Censo Físico de Unidades")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Pop (60%)", f"{u_pop_censo:,}")
c2.metric("Med (30%)", f"{u_med_censo:,}")
c3.metric("Alt (10%)", f"{u_alt_censo:,}")
c4.metric("Comercial", f"{u_com_censo:,}")
c5.metric("Industrial", f"{u_ind_censo:,}")

st.markdown("---")

# SECCIÓN 3: ESTIMACIÓN DE RECAUDACIÓN (RESALTADA)
st.subheader("💵 3. Estimación de Recaudación Mensual")
st.caption(f"Aplicando efectividad: Residencial {efec_res}% | Comercial {efec_com}% | Industrial {efec_ind}%")

# Encabezados con formato Markdown para resaltar títulos
st.markdown("""
| Sector | Recaudación Potencial (100%) | Recaudación Real Estimada |
| :--- | :---: | :---: |
| **Residencial** | $ {:,.2f} | **$ {:,.2f}** |
| **Comercial** | $ {:,.2f} | **$ {:,.2f}** |
| **Industrial** | $ {:,.2f} | **$ {:,.2f}** |
| --- | --- | --- |
| ### **TOTAL** | ### **$ {:,.2f}** | ### **$ {:,.2f}** |
""".format(r_res_pot, r_res_real, r_com_pot, r_com_real, r_ind_pot, r_ind_real, total_potencial, total_real))

st.markdown("---")

# --- EXPORTACIÓN PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A. - REPORTE TÉCNICO", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. GENERACIÓN DE DESECHOS", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Total General: {ton_total_dia:.2f} Ton/Día (Res: {ton_res:.2f} | Com: {ton_com:.2f} | Ind: {ton_ind:.2f})", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. CENSO DE UNIDADES", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Viviendas: {u_pop_censo+u_med_censo+u_alt_censo} | Comercial: {u_com_censo} | Industrial: {u_ind_censo}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. RECAUDACIÓN MENSUAL (CON EFECTIVIDAD)", ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"TOTAL REAL ESTIMADO: $ {total_real:,.2f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte (PDF)", generate_pdf(), f"Gercon_Reporte_{poblacion}.pdf", "application/pdf")
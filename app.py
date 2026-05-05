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

# --- ENTRADAS DE DATOS ---
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

# --- LÓGICA TÉCNICA ---

# 1. GENERACIÓN DE DESECHOS (Lógica de cascada solicitada)
ton_res_dia = round(poblacion * 0.0005, 2)
ton_com_dia = round(ton_res_dia * 0.20, 2)
ton_ind_dia = round(ton_res_dia * 0.05, 2)
ton_total_dia = round(ton_res_dia + ton_com_dia + ton_ind_dia, 2)
ton_total_mes_26 = round(ton_total_dia * 26, 2)

# 2. CENSO FÍSICO
viviendas_censo_total = poblacion * (5161 / 28900)
u_pop_censo = int(viviendas_censo_total * 0.60)
u_med_censo = int(viviendas_censo_total * 0.30)
u_alt_censo = int(viviendas_censo_total * 0.10)
total_viviendas_censo = u_pop_censo + u_med_censo + u_alt_censo # Totalización solicitada
u_com_censo = int(poblacion * (413 / 28900))
u_ind_censo = int(poblacion * (258 / 28900))

# 3. BASE DE RECAUDACIÓN (Unidades Financieras Excel)
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

# --- INTERFAZ ---

# SECCIÓN 1: GENERACIÓN
st.subheader("🚛 1. Cálculo de Generación de Desechos")
g1, g2 = st.columns(2)
g1.metric("Generación Diaria Total", f"{ton_total_dia:.2f} Ton")
g2.metric("Generación Mensual (26 días)", f"{ton_total_mes_26:.2f} Ton")

data_gen = {
    "Sector": ["Residencial", "Comercial", "Industrial", "TOTAL"],
    "Generación Diaria (Ton)": [f"{ton_res_dia:.2f}", f"{ton_com_dia:.2f}", f"{ton_ind_dia:.2f}", f"{ton_total_dia:.2f}"]
}
st.table(pd.DataFrame(data_gen).set_index("Sector"))

st.markdown("---")

# SECCIÓN 2: CENSO FÍSICO CON TOTALIZACIÓN
st.subheader("🏠 2. Censo Físico de Unidades")
col_res, col_esp = st.columns(2)
with col_res:
    st.markdown("### **Bloque Residencial**")
    st.write(f"- Sector Popular (60%): **{u_pop_censo:,} Uds**")
    st.write(f"- Sector Medio (30%): **{u_med_censo:,} Uds**")
    st.write(f"- Sector Alto (10%): **{u_alt_censo:,} Uds**")
    st.divider()
    st.write(f"**TOTAL VIVIENDAS: {total_viviendas_censo:,} Uds**")

with col_esp:
    st.markdown("### **Bloque Especial**")
    st.write(f"- Sector Comercial: **{u_com_censo:,} Uds**")
    st.write(f"- Sector Industrial: **{u_ind_censo:,} Uds**")

st.markdown("---")

# SECCIÓN 3: RECAUDACIÓN (SIN NUMERALES)
st.subheader("💵 3. Estimación de Recaudación Mensual")
st.info(f"Salvedad: Aplicando Efectividad Res: {efec_res}% | Com: {efec_com}% | Ind: {efec_ind}%")

# Construcción de la tabla para evitar errores de ancho de columna (#)
df_recaudacion = pd.DataFrame({
    "Sector": ["Residencial", "Comercial", "Industrial", "TOTAL"],
    "Potencial (100%)": [f"$ {r_res_pot:,.2f}", f"$ {r_com_pot:,.2f}", f"$ {r_ind_pot:,.2f}", f"$ {total_potencial:,.2f}"],
    "Real Estimado": [f"$ {r_res_real:,.2f}", f"$ {r_com_real:,.2f}", f"$ {r_ind_real:,.2f}", f"$ {total_real:,.2f}"]
})
st.table(df_recaudacion.set_index("Sector"))

st.success(f"### TOTAL REAL ESTIMADO MENSUAL: $ {total_real:,.2f}")

# --- EXPORTACIÓN PDF (FORMATO ESPEJO DE LA APP) ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A.", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 7, "Reporte de Gestión y Proyección de Recaudación", ln=True, align="C")
    pdf.ln(5)
    
    # 1. Generación
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 1. GENERACIÓN DE DESECHOS", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Generación Diaria Total: {ton_total_dia:.2f} Ton", ln=True)
    pdf.cell(0, 8, f" Generación Mensual Efectiva (26 días): {ton_total_mes_26:.2f} Ton", ln=True)
    pdf.cell(0, 8, f" Desglose: Res: {ton_res_dia:.2f} | Com: {ton_com_dia:.2f} | Ind: {ton_ind_dia:.2f}", ln=True)
    pdf.ln(5)
    
    # 2. Censo
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 2. CENSO FÍSICO DE UNIDADES", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Residencial: Pop: {u_pop_censo} | Med: {u_med_censo} | Alt: {u_alt_censo}", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f" TOTAL VIVIENDAS: {total_viviendas_censo}", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Especiales: Comercial: {u_com_censo} | Industrial: {u_ind_censo}", ln=True)
    pdf.ln(5)
    
    # 3. Financiero
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 3. ESTIMACIÓN DE RECAUDACIÓN MENSUAL", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Recaudación Potencial (100%): $ {total_potencial:,.2f}", ln=True)
    pdf.cell(0, 8, f" Efectividad Aplicada: Res {efec_res}% | Com {efec_com}% | Ind {efec_ind}%", ln=True)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 12, f" TOTAL REAL ESTIMADO: $ {total_real:,.2f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte Profesional (PDF)", generate_pdf(), f"Gercon_Reporte_{poblacion}.pdf", "application/pdf")
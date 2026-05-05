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

# 1. GENERACIÓN DE DESECHOS DESGLOSADA
# Factor base: 18 Ton / 28900 hab
factor_gen = 18 / 28900
ton_total_dia = poblacion * factor_gen

# Proporciones de generación por sector (según distribución de suscriptores del modelo)
f_gen_res, f_gen_com, f_gen_ind = 0.81, 0.12, 0.07 # Basado en la carga operativa del Excel
ton_res = ton_total_dia * f_gen_res
ton_com = ton_total_dia * f_gen_com
ton_ind = ton_total_dia * f_gen_ind

# 2. CENSO FÍSICO (Distribución 60-30-10)
viviendas_censo_total = poblacion * (5161 / 28900)
u_pop_censo = viviendas_censo_total * 0.60
u_med_censo = viviendas_censo_total * 0.30
u_alt_censo = viviendas_censo_total * 0.10

# 3. BASE DE RECAUDACIÓN (Unidades Financieras)
u_pop_rec = poblacion * (4644.9 / 28900)
u_med_rec = poblacion * (4644 / 28900)
u_alt_rec = poblacion * (2580 / 28900)
u_com = poblacion * (413 / 28900)
u_ind = poblacion * (258 / 28900)

# 4. CÁLCULO FINANCIERO (POTENCIAL VS REAL)
# Residencial
r_res_pot = (u_pop_rec * t_pop) + (u_med_rec * t_med) + (u_alt_rec * t_alt)
r_res_real = r_res_pot * (efec_res / 100)

# Comercial
r_com_pot = u_com * t_com
r_com_real = r_com_pot * (efec_com / 100)

# Industrial
r_ind_pot = u_ind * t_ind
r_ind_real = r_ind_pot * (efec_ind / 100)

total_potencial = r_res_pot + r_com_pot + r_ind_pot
total_real = r_res_real + r_com_real + r_ind_real

# --- INTERFAZ DE RESULTADOS ---

# SECCIÓN 1: GENERACIÓN DESGLOSADA
st.subheader("🚛 1. Cálculo de Generación de Desechos")
col_g1, col_g2 = st.columns([1, 2])
with col_g1:
    st.metric("Total General", f"{ton_total_dia:.2f} Ton/Día")
with col_g2:
    data_gen = {
        "Sector": ["Residencial", "Comercial", "Industrial"],
        "Generación Estimada (Ton/Día)": [ton_res, ton_com, ton_ind]
    }
    st.table(pd.DataFrame(data_gen).set_index("Sector"))

st.markdown("---")

# SECCIÓN 2: CENSO FÍSICO
st.subheader("🏠 2. Censo Físico de Viviendas (Distribución 60-30-10)")
c1, c2, c3 = st.columns(3)
c1.metric("Sector Popular", f"{u_pop_censo:,.0f} Uds")
c2.metric("Sector Medio", f"{u_med_censo:,.0f} Uds")
c3.metric("Sector Alto", f"{u_alt_censo:,.0f} Uds")

st.markdown("---")

# SECCIÓN 3: RECAUDACIÓN CON SALVEDAD DE EFECTIVIDAD
st.subheader("💵 3. Estimado de Recaudación Mensual")
st.info(f"Nota: Los montos reales se calculan aplicando los porcentajes de efectividad seleccionados: Res ({efec_res}%), Com ({efec_com}%), Ind ({efec_ind}%).")

data_rec = {
    "Sector": ["Residencial", "Comercial", "Industrial", "TOTAL"],
    "Recaudación Potencial (100%)": [f"$ {r_res_pot:,.2f}", f"$ {r_com_pot:,.2f}", f"$ {r_ind_pot:,.2f}", f"$ {total_potencial:,.2f}"],
    "Recaudación Real (Con Efectividad)": [f"$ {r_res_real:,.2f}", f"$ {r_com_real:,.2f}", f"$ {r_ind_real:,.2f}", f"$ {total_real:,.2f}"]
}
st.table(pd.DataFrame(data_rec).set_index("Sector"))

st.success(f"### Proyección Final Mensual: $ {total_real:,.2f}")

# --- EXPORTACIÓN PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A. - REPORTE DE CÁLCULO", ln=True, align="C")
    pdf.ln(5)
    
    # Tabla Generación
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. GENERACIÓN DE DESECHOS (TON/DÍA)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Residencial: {ton_res:.2f} | Comercial: {ton_com:.2f} | Industrial: {ton_ind:.2f}", ln=True)
    pdf.cell(0, 8, f"TOTAL GENERAL: {ton_total_dia:.2f} Ton/Día", ln=True)
    pdf.ln(5)
    
    # Tabla Recaudación
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. ESTIMADO DE RECAUDACIÓN (SALVEDAD POR EFECTIVIDAD)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Residencial (Efec. {efec_res}%): $ {r_res_real:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Comercial (Efec. {efec_com}%): $ {r_com_real:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Industrial (Efec. {efec_ind}%): $ {r_ind_real:,.2f}", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL MENSUAL ESTIMADO: $ {total_real:,.2f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte (PDF)", generate_pdf(), f"Gercon_Reporte_{poblacion}.pdf", "application/pdf")
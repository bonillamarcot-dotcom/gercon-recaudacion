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
    st.header("⚙️ Configuración")
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

# --- LÓGICA TÉCNICA (SEPARADA) ---

# 1. Generación de Desechos (18 Ton / 28900 hab)
ton_dia_total = poblacion * (18 / 28900)

# 2. BLOQUE 1: CENSO DE UNIDADES (Distribución 60-30-10)
# Basado en el total de viviendas estimadas (5161 para 28900 hab)
viviendas_censo_total = poblacion * (5161 / 28900)
u_pop_censo = viviendas_censo_total * 0.60
u_med_censo = viviendas_censo_total * 0.30
u_alt_censo = viviendas_censo_total * 0.10

# 3. BLOQUE 2: BASE DE RECAUDACIÓN (Cifras financieras C14-C16)
# Estas cifras son las que generan el dinero en tu Excel
u_pop_rec = poblacion * (4644.9 / 28900)
u_med_rec = poblacion * (4644 / 28900)
u_alt_rec = poblacion * (2580 / 28900)

# Unidades Especiales
u_com = poblacion * (413 / 28900)
u_ind = poblacion * (258 / 28900)

# 4. CÁLCULO FINANCIERO (Usando el Bloque de Recaudación)
r_pop_t = u_pop_rec * t_pop
r_med_t = u_med_rec * t_med
r_alt_t = u_alt_rec * t_alt
r_com_t = u_com * t_com
r_ind_t = u_ind * t_ind

total_teorico = r_pop_t + r_med_t + r_alt_t + r_com_t + r_ind_t
total_estimado = (r_pop_t+r_med_t+r_alt_t)*(efec_res/100) + (r_com_t*efec_com/100) + (r_ind_t*efec_ind/100)

# --- INTERFAZ ---

st.subheader("🚛 1. Generación de Desechos")
st.metric("Total Diario", f"{ton_dia_total:.2f} Ton")

st.markdown("---")

# MOSTRANDO EL CENSO FÍSICO
st.subheader("🏠 2. Censo Físico de Viviendas (Distribución 60-30-10)")
c1, c2, c3 = st.columns(3)
c1.metric("Popular", f"{u_pop_censo:,.0f}")
c2.metric("Medio", f"{u_med_censo:,.0f}")
c3.metric("Alto", f"{u_alt_censo:,.0f}")

st.markdown("---")

# MOSTRANDO LA RECAUDACIÓN (FORMATO MONEDA)
st.subheader("💵 3. Estimado de Recaudación Mensual")
col_res, col_esp = st.columns(2)

with col_res:
    st.write("**Base de Cálculo Residencial (Unidades Financieras):**")
    st.write(f"- Popular: {u_pop_rec:,.1f} uds | Tarifa: ${t_pop}")
    st.write(f"- Medio: {u_med_rec:,.1f} uds | Tarifa: ${t_med}")
    st.write(f"- Alto: {u_alt_rec:,.1f} uds | Tarifa: ${t_alt}")

with col_esp:
    st.write("**Base de Cálculo Especial:**")
    st.write(f"- Comercial: {u_com:,.1f} uds | Tarifa: ${t_com}")
    st.write(f"- Industrial: {u_ind:,.1f} uds | Tarifa: ${t_ind}")

st.success(f"### RECAUDACIÓN TOTAL ESTIMADA: ${total_estimado:,.2f}")

# --- EXPORTACIÓN PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A. - REPORTE DE GESTIÓN", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. CENSO FÍSICO (VIVIENDAS)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Popular: {u_pop_censo:,.0f} | Medio: {u_med_censo:,.0f} | Alto: {u_alt_censo:,.0f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. RECAUDACIÓN ESTIMADA (AJUSTADA)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"TOTAL MENSUAL ESTIMADO: ${total_estimado:,.2f}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte (PDF)", generate_pdf(), f"Gercon_Calculo_{poblacion}.pdf", "application/pdf")
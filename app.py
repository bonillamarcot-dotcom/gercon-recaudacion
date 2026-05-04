import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF

st.set_page_config(page_title="Gercon - Auditoría de Recaudación", layout="wide")

# --- IDENTIDAD CORPORATIVA ---
logo_path = "logo_gercon.png" 
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("GRUPO GERCON")

st.title("📊 Auditoría de Gestión: Unidades y Recaudación")
st.markdown("---")

# --- ENTRADAS DE DATOS (TARIFAS EDITABLES) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    poblacion = st.number_input("Población Total (Habitantes)", value=28900, step=100)
    
    st.subheader("💰 Tarifas por Estrato ($)")
    t_pop = st.number_input("Sector Popular", value=1.5)
    t_med = st.number_input("Sector Medio", value=3.0)
    t_alt = st.number_input("Sector Alto", value=5.0)
    t_com = st.number_input("Comercial", value=30.0)
    t_ind = st.number_input("Industrial", value=350.0)

# --- LÓGICA TÉCNICA (BLOQUEADA POR POBLACIÓN) ---
ppc = 0.623 
ton_dia = (poblacion * ppc) / 1000
ton_mes = ton_dia * 30

# Factores proporcionales según el modelo original
f_pop, f_med, f_alt = 4644.9/28900, 4644/28900, 2580/28900
f_com, f_ind = 413/28900, 258/28900

# Cálculo de Unidades
u_pop, u_med, u_alt = int(poblacion * f_pop), int(poblacion * f_med), int(poblacion * f_alt)
u_com, u_ind = int(poblacion * f_com), int(poblacion * f_ind)
total_viviendas = u_pop + u_med + u_alt

# Cálculo de Recaudación
r_pop, r_med, r_alt = u_pop * t_pop, u_med * t_med, u_alt * t_alt
r_com, r_ind = u_com * t_com, u_ind * t_ind
total_rec_residencial = r_pop + r_med + r_alt
total_general = total_rec_residencial + r_com + r_ind

# --- INTERFAZ DE RESULTADOS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Generación Diaria", f"{ton_dia:.2f} Ton")
m2.metric("Total Viviendas", f"{total_viviendas:,}")
m3.metric("Total Comercios", f"{u_com:,}")
m4.metric("Recaudación Total", f"${total_general:,.2f}")

st.markdown("---")

# --- SECCIÓN 1: RESUMEN DE UNIDADES ---
st.subheader("🏠 1. Censo Estimado de Unidades")
col_u1, col_u2 = st.columns(2)

with col_u1:
    st.write("**Desglose Residencial:**")
    st.write(f"- Sector Popular: {u_pop:,} unidades")
    st.write(f"- Sector Medio: {u_med:,} unidades")
    st.write(f"- Sector Alto: {u_alt:,} unidades")

with col_u2:
    st.write("**Sectores Especiales:**")
    st.write(f"- Total Comercios: {u_com:,} unidades")
    st.write(f"- Total Industrias: {u_ind:,} unidades")

st.markdown("---")

# --- SECCIÓN 2: RESUMEN DE RECAUDACIÓN ---
st.subheader("💵 2. Recaudación Estimada Mensual")
col_r1, col_r2 = st.columns(2)

with col_r1:
    st.write("**Recaudación Residencial:**")
    st.write(f"- Popular: ${r_pop:,.2f}")
    st.write(f"- Medio: ${r_med:,.2f}")
    st.write(f"- Alto: ${r_alt:,.2f}")
    st.info(f"Subtotal Residencial: ${total_rec_residencial:,.2f}")

with col_r2:
    st.write("**Recaudación No Residencial:**")
    st.write(f"- Comercial: ${r_com:,.2f}")
    st.write(f"- Industrial: ${r_ind:,.2f}")
    st.success(f"Recaudación Total: ${total_general:,.2f}")

# --- EXPORTACIÓN A PDF ESTRUCTURADO ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A. - REPORTE DE AUDITORÍA", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Población: {poblacion} habitantes | Generación: {ton_dia:.2f} Ton/día", ln=True, align="C")
    pdf.ln(10)
    
    # Bloque Unidades
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "1. ESTIMACIÓN DE UNIDADES (CENSO)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Total Viviendas: {total_viviendas:,} (Pop: {u_pop} | Med: {u_med} | Alt: {u_alt})", ln=True)
    pdf.cell(0, 8, f"- Total Comercios: {u_com:,}", ln=True)
    pdf.cell(0, 8, f"- Total Industrias: {u_ind:,}", ln=True)
    pdf.ln(5)
    
    # Bloque Recaudación
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "2. RESUMEN DE RECAUDACIÓN ESTIMADA", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Residencial Popular: ${r_pop:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Residencial Medio: ${r_med:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Residencial Alto: ${r_alt:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Comercial Total: ${r_com:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Industrial Total: ${r_ind:,.2f}", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL RECAUDACIÓN MENSUAL: ${total_general:,.2f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte Estructurado (PDF)", generate_pdf(), f"Gercon_Auditoria_{poblacion}.pdf", "application/pdf")
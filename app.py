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
    
    st.subheader("💰 Tarifas por Estrato ($)")
    t_pop = st.number_input("Sector Popular", value=1.5)
    t_med = st.number_input("Sector Medio", value=3.0)
    t_alt = st.number_input("Sector Alto", value=5.0)
    t_com = st.number_input("Comercial", value=30.0)
    t_ind = st.number_input("Industrial", value=350.0)
    
    st.markdown("---")
    # EFECTIVIDAD POR TIPO DE GENERADOR
    st.subheader("🎯 Efectividad de Cobranza (%)")
    efec_res = st.slider("Efectividad Residencial", 0, 100, 70)
    efec_com = st.slider("Efectividad Comercial", 0, 100, 85)
    efec_ind = st.slider("Efectividad Industrial", 0, 100, 95)

# --- LÓGICA TÉCNICA (BLOQUEADA POR POBLACIÓN) ---
ppc = 0.623 
ton_dia_total = (poblacion * ppc) / 1000

# Factores proporcionales según el modelo original de Gercon
f_pop, f_med, f_alt = 4644.9/28900, 4644/28900, 2580/28900
f_com, f_ind = 413/28900, 258/28900

# Cálculo de Unidades
u_pop, u_med, u_alt = int(poblacion * f_pop), int(poblacion * f_med), int(poblacion * f_alt)
u_com, u_ind = int(poblacion * f_com), int(poblacion * f_ind)
total_viviendas = u_pop + u_med + u_alt

# Estimación de Generación por Sector
total_suscriptores = total_viviendas + u_com + u_ind
ton_res = (total_viviendas / total_suscriptores) * ton_dia_total
ton_com = (u_com / total_suscriptores) * ton_dia_total
ton_ind = (u_ind / total_suscriptores) * ton_dia_total

# Cálculo de Recaudación Teórica (100%)
r_pop_t, r_med_t, r_alt_t = u_pop * t_pop, u_med * t_med, u_alt * t_alt
r_com_t, r_ind_t = u_com * t_com, u_ind * t_ind
total_teorico = r_pop_t + r_med_t + r_alt_t + r_com_t + r_ind_t

# Cálculo de Recaudación Estimada (con Efectividad Variable)
r_res_est = (r_pop_t + r_med_t + r_alt_t) * (efec_res / 100)
r_com_est = r_com_t * (efec_com / 100)
r_ind_est = r_ind_t * (efec_ind / 100)
total_estimado = r_res_est + r_com_est + r_ind_est

# --- SECCIÓN 1: GENERACIÓN (TONELADAS) ---
st.subheader("🚛 1. Generación de Desechos (Toneladas Diarias)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Diario", f"{ton_dia_total:.2f} Ton")
m2.metric("Residencial", f"{ton_res:.2f} Ton")
m3.metric("Comercial", f"{ton_com:.2f} Ton")
m4.metric("Industrial", f"{ton_ind:.2f} Ton")

st.markdown("---")

# --- SECCIÓN 2: CENSO DE UNIDADES ---
st.subheader("🏠 2. Censo Estimado de Suscriptores")
col_u1, col_u2 = st.columns(2)
with col_u1:
    st.write(f"**Total Viviendas: {total_viviendas:,}**")
    st.write(f"- Popular: {u_pop:,} | Medio: {u_med:,} | Alto: {u_alt:,}")
with col_u2:
    st.write(f"**Sectores Especiales:**")
    st.write(f"- Comercios: {u_com:,} | Industrias: {u_ind:,}")

st.markdown("---")

# --- SECCIÓN 3: RECAUDACIÓN CON EFECTIVIDAD VARIABLE ---
st.subheader("💵 3. Estimado de Recaudación Mensual (Ajustado por Efectividad)")
col_r1, col_r2 = st.columns(2)
with col_r1:
    st.write("**Recaudación Real Estimada por Sector:**")
    st.write(f"- Residencial ({efec_res}%): ${r_res_est:,.2f}")
    st.write(f"- Comercial ({efec_com}%): ${r_com_est:,.2f}")
    st.write(f"- Industrial ({efec_ind}%): ${r_ind_est:,.2f}")
with col_r2:
    st.write("**Proyección Final:**")
    st.write(f"Potencial Total (100%): ${total_teorico:,.2f}")
    st.success(f"Recaudación Total Estimada: ${total_estimado:,.2f}")

# --- EXPORTACIÓN A PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A. - REPORTE DE CÁLCULO", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Población: {poblacion} hab | Reporte con Efectividad Variable", ln=True, align="C")
    pdf.ln(10)
    
    # Bloque Unidades
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "1. RESUMEN DE UNIDADES", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Viviendas: {total_viviendas:,} | Comercios: {u_com:,} | Industrias: {u_ind:,}", ln=True)
    pdf.ln(5)
    
    # Bloque Finanzas
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "2. ESTIMADO DE RECAUDACIÓN (EFECTIVIDAD APLICADA)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Residencial ({efec_res}%): ${r_res_est:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Comercial ({efec_com}%): ${r_com_est:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Industrial ({efec_ind}%): ${r_ind_est:,.2f}", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL RECAUDACIÓN REAL ESTIMADA: ${total_estimado:,.2f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte Completo (PDF)", generate_pdf(), f"Gercon_Calculo_{poblacion}.pdf", "application/pdf")
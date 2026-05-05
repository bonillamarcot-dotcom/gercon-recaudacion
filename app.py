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
    t_pop = st.number_input("Sector Popular (60%)", value=1.5)
    t_med = st.number_input("Sector Medio (30%)", value=3.0)
    t_alt = st.number_input("Sector Alto (10%)", value=5.0)
    t_com = st.number_input("Comercial", value=30.0)
    t_ind = st.number_input("Industrial", value=350.0)
    
    st.markdown("---")
    st.subheader("🎯 Efectividad de Cobranza (%)")
    efec_res = st.slider("Efectividad Residencial", 0, 100, 70)
    efec_com = st.slider("Efectividad Comercial", 0, 100, 85)
    efec_ind = st.slider("Efectividad Industrial", 0, 100, 95)

# --- LÓGICA TÉCNICA CORREGIDA (PROPORCIÓN 60-30-10) ---
ppc = 0.623 
ton_dia_total = (poblacion * ppc) / 1000

# 1. Universo Total de Viviendas (Mantenemos el factor técnico del modelo Gercon)
total_viviendas_calc = poblacion * (11868.9 / 28900)

# 2. Distribución Solicitada: 60% Bajo, 30% Medio, 10% Alto
u_pop = int(total_viviendas_calc * 0.60)
u_med = int(total_viviendas_calc * 0.30)
u_alt = int(total_viviendas_calc * 0.10)
total_viviendas = u_pop + u_med + u_alt

# 3. Unidades Especiales
u_com = int(poblacion * (413 / 28900))
u_ind = int(poblacion * (258 / 28900))

# 4. Generación y Recaudación
total_suscriptores = total_viviendas + u_com + u_ind
ton_res = (total_viviendas / total_suscriptores) * ton_dia_total
ton_com = (u_com / total_suscriptores) * ton_dia_total
ton_ind = (u_ind / total_suscriptores) * ton_dia_total

r_pop_t, r_med_t, r_alt_t = u_pop * t_pop, u_med * t_med, u_alt * t_alt
r_com_t, r_ind_t = u_com * t_com, u_ind * t_ind
total_teorico = r_pop_t + r_med_t + r_alt_t + r_com_t + r_ind_t

r_res_est = (r_pop_t + r_med_t + r_alt_t) * (efec_res / 100)
r_com_est = r_com_t * (efec_com / 100)
r_ind_est = r_ind_t * (efec_ind / 100)
total_estimado = r_res_est + r_com_est + r_ind_est

# --- INTERFAZ ---
st.subheader("🚛 1. Generación de Desechos (Toneladas Diarias)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Diario", f"{ton_dia_total:.2f} Ton")
m2.metric("Residencial", f"{ton_res:.2f} Ton")
m3.metric("Comercial", f"{ton_com:.2f} Ton")
m4.metric("Industrial", f"{ton_ind:.2f} Ton")

st.markdown("---")
st.subheader("🏠 2. Censo de Suscriptores (Distribución 60-30-10)")
col_u1, col_u2 = st.columns(2)
with col_u1:
    st.write(f"**Total Viviendas: {total_viviendas:,}**")
    st.write(f"- Sector Popular (60%): {u_pop:,} unidades")
    st.write(f"- Sector Medio (30%): {u_med:,} unidades")
    st.write(f"- Sector Alto (10%): {u_alt:,} unidades")
with col_u2:
    st.write(f"**Sectores Especiales:**")
    st.write(f"- Comercios: {u_com:,} | Industrias: {u_ind:,}")

st.markdown("---")
st.subheader(f"💵 3. Estimado de Recaudación Mensual")
col_r1, col_r2 = st.columns(2)
with col_r1:
    st.write("**Recaudación Real Estimada:**")
    st.write(f"- Residencial: ${r_res_est:,.2f}")
    st.write(f"- Comercial: ${r_com_est:,.2f}")
    st.write(f"- Industrial: ${r_ind:,.2f}")
with col_r2:
    st.write("**Proyección Final:**")
    st.write(f"Recaudación Potencial (100%): ${total_teorico:,.2f}")
    st.success(f"Recaudación Total Estimada: ${total_estimado:,.2f}")

# --- EXPORTACIÓN PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INGENIERÍA GERCON C.A. - CALCULADORA DE GESTIÓN", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Distribución Residencial: 60% Popular | 30% Medio | 10% Alto", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. RESUMEN DE UNIDADES", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Viviendas Populares: {u_pop} | Medias: {u_med} | Altas: {u_alt}", ln=True)
    pdf.cell(0, 8, f"- Comercios: {u_com} | Industrias: {u_ind}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. RECAUDACIÓN AJUSTADA", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"- Potencial al 100%: ${total_teorico:,.2f}", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL ESTIMADO CON EFECTIVIDAD: ${total_estimado:,.2f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Descargar Reporte (PDF)", generate_pdf(), f"Gercon_Calculo_{poblacion}.pdf", "application/pdf")
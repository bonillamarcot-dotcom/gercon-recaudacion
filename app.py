import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Gercon - Auditoría de Recaudación", layout="wide")

# --- GESTIÓN DEL LOGO ---
logo_path = "logo_gercon.png" # Nombre de tu archivo de imagen
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("GRUPO GERCON")

st.title("📊 Sistema Integral de Gestión y Recaudación")
st.markdown("---")

# --- BARRA LATERAL: PARÁMETROS DE ENTRADA ---
with st.sidebar:
    st.header("⚙️ Configuración del Municipio")
    poblacion = st.number_input("Población Total (Habitantes)", value=28900)
    
    st.subheader("🏡 Tarifas Residenciales ($)")
    t_pop = st.number_input("Sector Popular", value=1.5)
    t_med = st.number_input("Sector Medio", value=3.0)
    t_alt = st.number_input("Sector Alto", value=5.0)
    
    st.subheader("🏢 Unidades Comerciales e Industriales")
    cant_comercio = st.number_input("Cantidad de Comercios", value=413)
    t_com = st.number_input("Tarifa Comercial Promedio ($)", value=30.0)
    
    cant_industry = st.number_input("Cantidad de Industrias", value=258)
    t_ind = st.number_input("Tarifa Industrial Promedio ($)", value=350.0)

# --- LÓGICA DE CÁLCULO TÉCNICO ---
ppc = 0.623 # kg/hab/día
ton_dia = (poblacion * ppc) / 1000
ton_mes = ton_dia * 30

cant_popular = int(poblacion * 0.16) 
cant_medio = int(poblacion * 0.16)
cant_alto = int(poblacion * 0.08)

rec_pop = cant_popular * t_pop
rec_med = cant_medio * t_med
rec_alt = cant_alto * t_alt
rec_comercial = cant_comercio * t_com
rec_industrial = cant_industry * t_ind
total_general = rec_pop + rec_med + rec_alt + rec_comercial + rec_industrial

# --- VISUALIZACIÓN DE RESULTADOS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Generación Diaria", f"{ton_dia:.2f} Ton")
m2.metric("Generación Mensual", f"{ton_mes:.2f} Ton")
m3.metric("Total Suscriptores", f"{cant_popular + cant_medio + cant_alto + cant_comercio + cant_industry:,}")
m4.metric("Recaudación Total", f"${total_general:,.2f}")

st.markdown("---")

st.subheader("📋 Detalle de Suscriptores y Recaudación")
data = {
    "Categoría": ["Residencial Popular", "Residencial Medio", "Residencial Alto", "Comercial", "Industrial"],
    "Unidades": [cant_popular, cant_medio, cant_alto, cant_comercio, cant_industry],
    "Tarifa ($)": [t_pop, t_med, t_alt, t_com, t_ind],
    "Recaudación Mensual ($)": [rec_pop, rec_med, rec_alt, rec_comercial, rec_industrial]
}
df_resumen = pd.DataFrame(data)

df_tablero = df_resumen.copy()
df_tablero["Recaudación Mensual ($)"] = df_tablero["Recaudación Mensual ($)"].map("${:,.2f}".format)
st.table(df_tablero)

# --- FUNCIÓN PARA EXPORTAR A EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Recaudacion')
    return output.getvalue()

excel_data = to_excel(df_resumen)

st.download_button(
    label="📥 Descargar Reporte en Excel",
    data=excel_data,
    file_name=f"Reporte_Gercon_{poblacion}_hab.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.subheader("📈 Análisis Visual de Ingresos")
st.bar_chart(df_resumen.set_index("Categoría")["Recaudación Mensual ($)"])

st.info("Ingeniería Gercon C.A. - Reporte generado basado en modelos de gestión de desechos sólidos.")
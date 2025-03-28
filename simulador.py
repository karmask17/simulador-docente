# simulador.py
import streamlit as st
import json
import os
from fpdf import FPDF

st.set_page_config(page_title="Simulador Docente", layout="centered")
st.title("🧑‍🏫 Simulador Docente")

idioma = st.radio("Elige tu idioma / Choose your language:", ("es", "en"))

TEXTO = {
    "es": {
        "resumen": "RESUMEN FINAL DE TU EXPERIENCIA DOCENTE",
        "perfil": "Este es tu perfil como docente al finalizar el simulador:",
        "indicadores": "Indicadores de desempeño docente:",
        "evaluacion": "Evaluación cualitativa:",
        "final": "Gracias por participar. ¡Sigue creciendo como educador!",
        "excelente": "Excelente",
        "bueno": "Bueno",
        "aceptable": "Aceptable",
        "atencion": "Necesita atención",
        "iniciar": "Iniciar Simulador"
    },
    "en": {
        "resumen": "FINAL SUMMARY OF YOUR TEACHING EXPERIENCE",
        "perfil": "This is your profile as a teacher at the end of the simulation:",
        "indicadores": "Teaching performance indicators:",
        "evaluacion": "Qualitative evaluation:",
        "final": "Thank you for participating. Keep growing as an educator!",
        "excelente": "Excellent",
        "bueno": "Good",
        "aceptable": "Acceptable",
        "atencion": "Needs attention",
        "iniciar": "Start Simulator"
    }
}[idioma]

indicadores = {
    "bienestar": 50,
    "dominio": 50,
    "ambiente": 50,
    "relacion": 50,
    "carga": 50
}

def mostrar_indicadores():
    st.subheader(TEXTO['indicadores'])
    for clave, valor in indicadores.items():
        st.progress(valor / 100, text=f"{clave.capitalize()}: {valor}%")

@st.cache_data
def cargar_escenarios():
    archivo = "escenarios_en.json" if idioma == "en" else "escenarios_es.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def mostrar_resumen_final():
    st.header("📋 " + TEXTO['resumen'])
    st.write(TEXTO['perfil'])
    mostrar_indicadores()

    st.subheader("💬 " + TEXTO['evaluacion'])
    for clave, valor in indicadores.items():
        if valor >= 85:
            nivel = TEXTO['excelente']
        elif valor >= 70:
            nivel = TEXTO['bueno']
        elif valor >= 50:
            nivel = TEXTO['aceptable']
        else:
            nivel = TEXTO['atencion']
        st.write(f"**{clave.capitalize()}:** {nivel}")

    st.success(TEXTO['final'])

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=TEXTO['resumen'], ln=True)
    for clave, valor in indicadores.items():
        pdf.cell(200, 10, txt=f"{clave.capitalize()}: {valor}%", ln=True)
    pdf.output("resumen_final.pdf")
    with open("resumen_final.pdf", "rb") as f:
        st.download_button("📄 Descargar resumen en PDF", f, file_name="resumen_final.pdf")

if st.button(TEXTO['iniciar']):
    escenarios = cargar_escenarios()
    for esc in escenarios:
        st.subheader(esc['titulo'])
        st.write(esc['narrativa'])
        opciones = esc['opciones']
        eleccion = st.radio("Selecciona una opción:", list(opciones.keys()), format_func=lambda k: opciones[k]['texto'], key=esc['id'])

        if eleccion:
            resultado = opciones[eleccion]
            st.write("✏️ ", resultado['consecuencia'])
            st.info("📚 " + resultado['retroalimentacion'])
            st.write("📊 Impacto: ", resultado.get("impacto", "Sin cambios"))

            if "mejora" in resultado['impacto'].lower() or "improves" in resultado['impacto'].lower():
                indicadores['ambiente'] += 5
            elif "aumenta la carga" in resultado['impacto'].lower() or "increases workload" in resultado['impacto'].lower():
                indicadores['carga'] += 10

    mostrar_resumen_final()

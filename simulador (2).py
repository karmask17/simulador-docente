
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
        "crear_perfil": "Crea tu perfil docente"
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
        "crear_perfil": "Create your teacher profile"
    }
}[idioma]

indicadores = {
    "bienestar": 50,
    "dominio": 50,
    "ambiente": 50,
    "relacion": 50,
    "carga": 50
}

@st.cache_data
def cargar_escenarios():
    archivo = "escenarios_en.json" if idioma == "en" else "escenarios_es.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def mostrar_indicadores():
    st.subheader(TEXTO['indicadores'])
    for clave, valor in indicadores.items():
        st.progress(valor / 100, text=f"{clave.capitalize()}: {valor}%")

def mostrar_resumen_final(perfil):
    st.header("📋 " + TEXTO['resumen'])
    st.write(TEXTO['perfil'])
    for k, v in perfil.items():
        st.write(f"**{k.capitalize()}:** {v}")
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

def personalizar_texto(texto, perfil):
    for clave, valor in perfil.items():
        texto = texto.replace(f"{{{clave}}}", str(valor))
    return texto

# Crear perfil docente
st.header("📝 " + TEXTO['crear_perfil'])
with st.form("perfil_form"):
    materia = st.text_input("Materia / Subject")
    nivel_educativo = st.selectbox("Nivel educativo / Educational level", ["Primaria", "Secundaria", "Preparatoria", "Universidad"])
    numero_alumnos = st.slider("Número de alumnos / Number of students", 5, 60, 30)
    experiencia = st.slider("Años de experiencia / Years of experience", 0, 30, 1)
    enviar = st.form_submit_button("Guardar perfil")

if enviar:
    perfil = {
        "materia": materia,
        "nivel_educativo": nivel_educativo,
        "numero_alumnos": numero_alumnos,
        "experiencia": experiencia
    }

    escenarios = cargar_escenarios()
    for esc in escenarios:
        st.subheader(esc['titulo'])
        narrativa = personalizar_texto(esc['narrativa'], perfil)
        st.write(narrativa)
        opciones = esc['opciones']
        eleccion = st.radio("Selecciona una opción:", list(opciones.keys()), format_func=lambda k: opciones[k]['texto'], key=esc['id'])

        if eleccion:
            resultado = opciones[eleccion]
            st.write("✏️ ", resultado['consecuencia'])
            st.info("📚 " + resultado['retroalimentacion'])
            st.write("📊 Impacto: ", resultado.get("impacto", "Sin cambios"))

            impacto = resultado.get("impacto", "")
            if isinstance(impacto, str):
                impacto_lower = impacto.lower()
                if "mejora" in impacto_lower or "improves" in impacto_lower:
                    indicadores["ambiente"] += 5
                    indicadores["relacion"] += 5
                elif "aumenta la carga" in impacto_lower or "increases workload" in impacto_lower:
                    indicadores["carga"] += 10
                elif "estrés" in impacto_lower or "stress" in impacto_lower:
                    indicadores["bienestar"] -= 5

    mostrar_resumen_final(perfil)

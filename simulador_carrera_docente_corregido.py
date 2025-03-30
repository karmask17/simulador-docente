
import streamlit as st
import json
import os
from fpdf import FPDF
import random

st.set_page_config(page_title="Simulador Carrera Docente", layout="centered")
st.title("🧑‍🏫 Simulador de Carrera Docente")

# Idioma
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

idioma = st.radio("Elige tu idioma / Choose your language:", ("es", "en"), index=0 if st.session_state.idioma == "es" else 1)
st.session_state.idioma = idioma

# Textos por idioma
TEXTO = {
    "es": {
        "resumen": "RESUMEN FINAL DE TU EXPERIENCIA DOCENTE",
        "perfil": "Perfil docente:",
        "indicadores": "Indicadores de desempeño:",
        "evaluacion": "Evaluación cualitativa:",
        "final": "Gracias por construir tu historia docente.",
        "excelente": "Excelente",
        "bueno": "Bueno",
        "aceptable": "Aceptable",
        "atencion": "Necesita atención",
        "crear_perfil": "Crea tu perfil docente",
        "guardar": "Guardar perfil",
        "continuar": "Continuar",
        "opcion": "Selecciona una opción:",
        "terminar": "Terminar simulador"
    },
    "en": {
        "resumen": "FINAL SUMMARY OF YOUR TEACHING EXPERIENCE",
        "perfil": "Teaching Profile:",
        "indicadores": "Performance Indicators:",
        "evaluacion": "Qualitative Evaluation:",
        "final": "Thank you for building your teaching journey.",
        "excelente": "Excellent",
        "bueno": "Good",
        "aceptable": "Acceptable",
        "atencion": "Needs improvement",
        "crear_perfil": "Create your teaching profile",
        "guardar": "Save profile",
        "continuar": "Continue",
        "opcion": "Choose an option:",
        "terminar": "End simulator"
    }
}[idioma]

# Estado inicial
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "escenario_actual" not in st.session_state:
    st.session_state.escenario_actual = 0
if "respuestas" not in st.session_state:
    st.session_state.respuestas = []
if "historia" not in st.session_state:
    st.session_state.historia = []
if "indicadores" not in st.session_state:
    st.session_state.indicadores = {
        "bienestar": 50,
        "dominio": 50,
        "ambiente": 50,
        "relacion": 50,
        "carga": 50
    }

@st.cache_data
def cargar_base():
    archivo = "escenarios_es.json" if idioma == "es" else "escenarios_en.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

base = cargar_base()

def personalizar(texto):
    for k, v in st.session_state.perfil.items():
        texto = texto.replace(f"{{{k}}}", str(v))
    return texto

def impacto_valores(impacto):
    texto = impacto.lower()
    if "mejora" in texto or "improves" in texto:
        st.session_state.indicadores["ambiente"] += 5
        st.session_state.indicadores["relacion"] += 5
    if "aumenta la carga" in texto or "increases workload" in texto:
        st.session_state.indicadores["carga"] += 10
    if "estrés" in texto or "stress" in texto:
        st.session_state.indicadores["bienestar"] -= 5

def mostrar_indicadores():
    st.subheader(TEXTO["indicadores"])
    for k, v in st.session_state.indicadores.items():
        st.progress(v / 100, text=f"{k.capitalize()}: {v}%")

def resumen_final():
    st.header("📋 " + TEXTO["resumen"])
    st.write("### " + TEXTO["perfil"])
    for k, v in st.session_state.perfil.items():
        st.write(f"**{k.capitalize()}:** {v}")
    mostrar_indicadores()
    st.subheader("💬 " + TEXTO["evaluacion"])
    for k, v in st.session_state.indicadores.items():
        if v >= 85:
            nivel = TEXTO["excelente"]
        elif v >= 70:
            nivel = TEXTO["bueno"]
        elif v >= 50:
            nivel = TEXTO["aceptable"]
        else:
            nivel = TEXTO["atencion"]
        st.write(f"**{k.capitalize()}:** {nivel}")
    st.success(TEXTO["final"])
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=TEXTO["resumen"], ln=True)
    for k, v in st.session_state.indicadores.items():
        pdf.cell(200, 10, txt=f"{k.capitalize()}: {v}%", ln=True)
    pdf.output("resumen_final.pdf")
    with open("resumen_final.pdf", "rb") as f:
        st.download_button("📄 Descargar PDF", f, file_name="resumen_final.pdf")

# Crear perfil
if not st.session_state.perfil:
    st.header("📝 " + TEXTO["crear_perfil"])
    materia = st.text_input("Materia / Subject")
    nivel = st.selectbox("Nivel educativo / Level", ["Primaria", "Secundaria", "Preparatoria", "Universidad"])
    alumnos = st.slider("Número de alumnos", 5, 60, 30)
    experiencia = st.slider("Años de experiencia", 0, 30, 1)
    if st.button(TEXTO["guardar"]):
        st.session_state.perfil = {
            "materia": materia,
            "nivel_educativo": nivel,
            "numero_alumnos": alumnos,
            "experiencia": experiencia
        }
        st.rerun()

# Simulación de escenarios
else:
    idx = st.session_state.escenario_actual
    if idx < len(base):
        escenario = base[idx]
    else:
        n = idx + 1
        decision_previa = st.session_state.historia[-1] if st.session_state.historia else "inicio"
        escenario = {
            "id": f"auto_{n}",
            "titulo": f"Etapa {n} - Consecuencia de tu decisión",
            "narrativa": f"Después de {decision_previa}, te enfrentas a una nueva situación en tu clase de {st.session_state.perfil['materia']} con {st.session_state.perfil['numero_alumnos']} alumnos.",
            "opciones": {
                "a": {
                    "texto": "Adaptas tu planeación a los intereses del grupo.",
                    "consecuencia": "El grupo responde mejor y hay más participación.",
                    "retroalimentacion": "Adaptar la planeación mejora el engagement.",
                    "impacto": "Mejora el ambiente de clase"
                },
                "b": {
                    "texto": "Sigues tu plan original sin ajustes.",
                    "consecuencia": "Algunos alumnos se desconectan del contenido.",
                    "retroalimentacion": "Flexibilizarse ayuda a mantener la atención.",
                    "impacto": "Aumenta la carga de trabajo"
                }
            }
        }

    st.subheader(escenario["titulo"])
    st.write(personalizar(escenario["narrativa"]))
    opciones = escenario["opciones"]
    eleccion = st.radio(TEXTO["opcion"], list(opciones.keys()), format_func=lambda k: opciones[k]["texto"], key=escenario["id"])

    if st.button(TEXTO["continuar"]):
        resultado = opciones[eleccion]
        st.session_state.historia.append(resultado["texto"])
        st.session_state.respuestas.append((escenario["id"], eleccion))
        impacto_valores(resultado.get("impacto", ""))
        st.success("✏️ " + resultado["consecuencia"])
        st.info("📚 " + resultado["retroalimentacion"])
        st.session_state.escenario_actual += 1
        st.rerun()

    if st.button("🛑 " + TEXTO["terminar"]):
        resumen_final()


# ✅ Simulador funcional listo para correr en Streamlit
import streamlit as st
import json
import os

st.set_page_config(page_title="Simulador de Carrera Docente", layout="centered")

# Textos multilenguaje
TEXT = {
    "es": {
        "titulo": "Simulador de Carrera Docente",
        "crear": "Crea tu perfil docente",
        "materia": "Materia",
        "nivel": "Nivel educativo",
        "alumnos": "Número de alumnos",
        "experiencia": "Años de experiencia",
        "guardar": "Guardar perfil",
        "continuar": "Continuar",
        "opcion": "Selecciona una opción",
        "retro": "🧑‍🏫 Mentor virtual",
        "consecuencia": "🎭 Consecuencia",
        "impacto": "📊 Impacto",
        "siguiente": "Siguiente escenario",
        "terminar": "Terminar simulador",
        "resumen": "📄 Resumen final",
        "descargar": "📥 Descargar resumen",
        "indicadores": "Indicadores acumulados"
    },
    "en": {
        "titulo": "Teaching Career Simulator",
        "crear": "Create your teaching profile",
        "materia": "Subject",
        "nivel": "Educational level",
        "alumnos": "Number of students",
        "experiencia": "Years of experience",
        "guardar": "Save profile",
        "continuar": "Continue",
        "opcion": "Choose an option",
        "retro": "🧑‍🏫 Mentor says",
        "consecuencia": "🎭 Consequence",
        "impacto": "📊 Impact",
        "siguiente": "Next scenario",
        "terminar": "End simulator",
        "resumen": "📄 Final summary",
        "descargar": "📥 Download summary",
        "indicadores": "Performance indicators"
    }
}

# Idioma
if "lang" not in st.session_state:
    st.session_state.lang = "es"
lang = st.radio("Idioma / Language", ["es", "en"], index=0 if st.session_state.lang == "es" else 1)
st.session_state.lang = lang
T = TEXT[lang]

# Estado inicial
for key, value in {
    "perfil": None,
    "indice": 0,
    "historial": [],
    "impacto": {
        "relacion": 50,
        "ambiente": 50,
        "carga": 50,
        "bienestar": 50,
        "dominio": 50
    },
    "mostrar": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Función para personalizar texto
def personalizar(texto):
    for k, v in st.session_state.perfil.items():
        texto = texto.replace(f"{{{k}}}", str(v))
    return texto

# Función de impacto
def aplicar_impacto(txt):
    t = txt.lower()
    if "mejora" in t or "improve" in t:
        st.session_state.impacto["ambiente"] += 5
        st.session_state.impacto["relacion"] += 5
    if "estrés" in t or "stress" in t:
        st.session_state.impacto["bienestar"] -= 5
    if "carga" in t or "workload" in t:
        st.session_state.impacto["carga"] += 5
    if "dominio" in t or "mastery" in t:
        st.session_state.impacto["dominio"] += 10

# Crear perfil
if not st.session_state.perfil:
    st.title(T["titulo"])
    st.header("📝 " + T["crear"])
    m = st.text_input(T["materia"])
    n = st.selectbox(T["nivel"], ["Primaria", "Secundaria", "Preparatoria", "Universidad"])
    a = st.slider(T["alumnos"], 5, 60, 30)
    e = st.slider(T["experiencia"], 0, 30, 1)
    if st.button(T["guardar"]):
        st.session_state.perfil = {
            "materia": m,
            "nivel": n,
            "alumnos": a,
            "experiencia": e
        }
        st.rerun()

else:
    def cargar_escenarios():
        archivo = "escenarios_es.json" if lang == "es" else "escenarios_en.json"
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    escenarios = cargar_escenarios()
    idx = st.session_state.indice

    # Mostrar resultado anterior
    if st.session_state.mostrar:
        r = st.session_state.mostrar
        st.success(f'{T["consecuencia"]}: {r["consecuencia"]}')
        st.info(f'{T["retro"]}: {r["retroalimentacion"]}')
        st.caption(f'{T["impacto"]}: {r["impacto"]}')
        st.session_state.mostrar = None
        st.session_state.indice += 1

    if idx < len(escenarios):
        esc = escenarios[idx]
    else:
        texto_prev = st.session_state.historial[-1]["texto"] if st.session_state.historial else "inicio del ciclo"
        esc = {
            "id": f"g{idx}",
            "titulo": f"Etapa {idx+1}",
            "narrativa": f"A raíz de tu decisión anterior ('{texto_prev}'), enfrentas una nueva situación en {st.session_state.perfil['materia']}.",
            "opciones": {
                "a": {
                    "texto": "Implementas una dinámica grupal participativa.",
                    "consecuencia": "El grupo responde con entusiasmo.",
                    "retroalimentacion": "Incluir estrategias activas fortalece el clima de aula.",
                    "impacto": "Mejora el ambiente de clase"
                },
                "b": {
                    "texto": "Decides continuar con tu método habitual.",
                    "consecuencia": "La clase mantiene la rutina sin mejoras.",
                    "retroalimentacion": "Cambiar de vez en cuando puede revitalizar la motivación.",
                    "impacto": "Aumenta la carga de trabajo"
                }
            }
        }

    st.subheader(esc["titulo"])
    st.write(personalizar(esc["narrativa"]))
    opciones = esc["opciones"]
    eleccion = st.radio(T["opcion"], list(opciones.keys()), format_func=lambda k: opciones[k]["texto"], key=esc["id"])
    if st.button(T["continuar"]):
        resultado = opciones[eleccion]
        st.session_state.historial.append(resultado)
        aplicar_impacto(resultado.get("impacto", ""))
        st.session_state.mostrar = resultado
        st.rerun()

    if st.button("🛑 " + T["terminar"]):
        st.header(T["resumen"])
        for k, v in st.session_state.perfil.items():
            st.write(f"**{k.capitalize()}**: {v}")
        st.subheader(T["indicadores"])
        for k, v in st.session_state.impacto.items():
            st.write(f"{k.capitalize()}: {v}%")

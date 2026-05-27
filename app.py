"""
RSA Quiz Interactivo - Starbucks
Archivo: app.py
Descripción: Quiz interactivo RSA para colaboradores con registro en Google Sheets.
"""

import streamlit as st
import random
import uuid
import hashlib
import json
from datetime import datetime
import time

# ── Importaciones opcionales ──────────────────────────────────────────────────
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    HAS_RAPIDFUZZ = False

try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RSA Quiz",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS PREMIUM  (sin cambios)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --green:   #00704A;
  --green-l: #1e8f62;
  --yellow:  #CBA135;
  --orange:  #D4783A;
  --copper:  #B87333;
  --bg:      #F5F0E8;
  --card:    rgba(255,255,255,0.82);
  --text:    #1C1C1C;
  --muted:   #6B6B6B;
  --radius:  14px;
  --shadow:  0 4px 24px rgba(0,112,74,0.10);
}

html, body, .stApp {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1rem 4rem !important; max-width: 720px !important; }

.quiz-card {
  background: var(--card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,112,74,0.15);
  border-radius: var(--radius);
  padding: 2rem 2.2rem;
  margin: 1rem 0;
  box-shadow: var(--shadow);
  animation: slideUp .45s ease both;
}

.top-bar {
  background: linear-gradient(135deg, var(--green) 0%, var(--green-l) 100%);
  border-radius: var(--radius);
  padding: 1rem 1.5rem;
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  box-shadow: var(--shadow);
}
.top-bar .logo { font-size: 1.5rem; }
.top-bar .title-text { font-size: 1.1rem; font-weight: 700; letter-spacing: .02em; }
.top-bar .sub   { font-size: .78rem; opacity: .85; }

.code-badge {
  background: linear-gradient(135deg, #fff7e6, #fff3d6);
  border: 2px solid var(--yellow);
  border-radius: 10px;
  padding: .6rem 1.2rem;
  text-align: center;
  margin-bottom: 1rem;
  animation: fadeIn .6s ease both;
}
.code-badge .code-num {
  font-size: 2.6rem;
  font-weight: 800;
  color: var(--orange);
  letter-spacing: .12em;
  line-height: 1;
}
.code-badge .code-label {
  font-size: .72rem;
  color: var(--muted);
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-top: .15rem;
}
.code-badge .code-warn {
  font-size: .75rem;
  color: var(--orange);
  margin-top: .25rem;
  font-weight: 500;
}

.progress-wrap { margin-bottom: 1rem; }
.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: .78rem;
  color: var(--muted);
  margin-bottom: .3rem;
}
.progress-track {
  background: rgba(0,112,74,0.12);
  border-radius: 99px;
  height: 8px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--green), var(--yellow));
  border-radius: 99px;
  transition: width .5s ease;
}

.q-number {
  font-size: .75rem;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--green);
  margin-bottom: .3rem;
}
.q-text {
  font-size: 1.08rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.5;
  margin-bottom: 1.1rem;
}

.drag-item {
  background: var(--card);
  border: 1.5px solid rgba(0,112,74,0.2);
  border-radius: 10px;
  padding: .6rem 1rem;
  margin-bottom: .4rem;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
  transition: box-shadow .18s;
}

.feedback-correct {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border-left: 4px solid #28a745;
  border-radius: 8px;
  padding: .7rem 1rem;
  color: #155724;
  font-weight: 500;
  margin: .6rem 0;
  animation: slideUp .3s ease both;
}
.feedback-wrong {
  background: linear-gradient(135deg, #fff3cd, #ffeeba);
  border-left: 4px solid var(--orange);
  border-radius: 8px;
  padding: .7rem 1rem;
  color: #856404;
  font-weight: 500;
  margin: .6rem 0;
  animation: slideUp .3s ease both;
}
.feedback-bonus {
  background: linear-gradient(135deg, #fff8e1, #fff3cd);
  border-left: 4px solid var(--yellow);
  border-radius: 8px;
  padding: .7rem 1rem;
  color: #5a4000;
  font-weight: 600;
  margin: .6rem 0;
  animation: slideUp .3s ease both;
}

.comodin-box {
  background: linear-gradient(135deg, #fff8e1, #fff3cd);
  border: 1.5px solid var(--yellow);
  border-radius: 10px;
  padding: .8rem 1.1rem;
  margin: .6rem 0;
  font-size: .9rem;
  color: #5a4000;
  animation: fadeIn .4s ease both;
}
.comodin-box strong { color: var(--orange); }

div[data-testid="stButton"] > button {
  background: linear-gradient(135deg, var(--green), var(--green-l)) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .95rem !important;
  padding: .6rem 1.6rem !important;
  transition: all .2s ease !important;
  box-shadow: 0 3px 12px rgba(0,112,74,0.25) !important;
}
div[data-testid="stButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 5px 18px rgba(0,112,74,0.35) !important;
}
div[data-testid="stButton"] > button:active { transform: scale(.98) !important; }

.score-card {
  background: linear-gradient(135deg, var(--green) 0%, var(--green-l) 100%);
  border-radius: 18px;
  padding: 2.5rem 2rem;
  text-align: center;
  color: white;
  box-shadow: 0 8px 40px rgba(0,112,74,0.3);
  animation: popIn .5s cubic-bezier(.34,1.56,.64,1) both;
}
.score-card .big-score { font-size: 5rem; font-weight: 800; line-height: 1; letter-spacing: -.02em; }
.score-card .score-pct { font-size: 1.5rem; font-weight: 300; opacity: .9; margin-top: .2rem; }
.score-card .score-msg { font-size: 1.05rem; margin-top: .8rem; opacity: .95; font-weight: 500; }

.breakdown-row {
  display: flex;
  justify-content: space-between;
  padding: .45rem 0;
  border-bottom: 1px solid rgba(0,112,74,0.1);
  font-size: .9rem;
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-pts { font-weight: 700; color: var(--green); }

.intro-hero { text-align: center; padding: 2rem 1rem 1.5rem; animation: fadeIn .8s ease both; }
.intro-hero h1 { font-size: 2rem !important; font-weight: 800 !important; color: var(--green) !important; margin-bottom: .4rem !important; }
.intro-hero .sub { font-size: 1rem; color: var(--muted); }

@keyframes fadeIn  { from { opacity:0 } to { opacity:1 } }
@keyframes slideUp { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
@keyframes popIn   { from { opacity:0; transform:scale(.85) } to { opacity:1; transform:scale(1) } }

div[data-testid="stRadio"] label { font-size: .95rem !important; }
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  border-radius: 8px !important;
  border: 1.5px solid rgba(0,112,74,0.25) !important;
  font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 2px rgba(0,112,74,0.15) !important;
}
.confetti-msg { font-size: 2.5rem; text-align: center; animation: popIn .6s ease both; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PREGUNTAS
#  Solo se mantienen: P1, P2, P11, P12, P15
#  P3+P4 combinadas → nueva pregunta open con evaluación flexible
#  P15 con lógica bonus para no-gerencial
# ─────────────────────────────────────────────────────────────────────────────

PREGUNTAS = [
    # ── P1 (sin cambios)
    {
        "id": 1,
        "texto": "¿Qué significa RSA?",
        "tipo": "radio",
        "opciones": [
            "Responsabilidad Social Activa",
            "Responsible Service of Alcohol",
            "Regulación de Servicio Alcohólico",
            "Registro de Seguridad Alimentaria",
        ],
        "correcta": "Responsible Service of Alcohol",
        "puntos": 5,
        "comodin": None,
    },
    # ── P2 (sin cambios)
    {
        "id": 2,
        "texto": "¿Cuál es la edad mínima legal para consumir alcohol en México?",
        "tipo": "radio",
        "opciones": ["16 años", "17 años", "18 años", "21 años"],
        "correcta": "18 años",
        "puntos": 5,
        "comodin": None,
    },
    # ── P3+P4 COMBINADAS → nueva pregunta open flexible
    {
        "id": 3,
        "texto": "¿Qué tipos de riesgos de contaminación existen en alimentos y bebidas? Da algunos ejemplos.",
        "tipo": "open_flexible",
        "puntos": 8,
        # Categorías que suman puntos (cada una vale parte del puntaje)
        "categorias": {
            "física":         ["física", "fisico", "físico", "fisicas", "físicas", "physical",
                               "polvo", "cabello", "cabellos", "pelo", "residuo", "piedra",
                               "acrílico", "acrilico", "vidrio", "metal", "astilla", "madera",
                               "horno", "fragmento", "objeto", "partícula"],
            "química":        ["química", "quimica", "químico", "chemical", "quimico",
                               "detergente", "pesticida", "plaguicida", "cloro", "veneno",
                               "tóxico", "toxico", "producto de limpieza"],
            "microbiológica": ["microbiológica", "microbiologica", "microbio", "bacteria",
                               "bacterias", "virus", "hongo", "hongos", "microorganismo",
                               "germen", "gérmenes", "patógeno", "biologica", "biológica"],
        },
        "comodin": "Existen 3 tipos: contaminación Física (polvo, cabellos, objetos), Química (detergentes, pesticidas) y Microbiológica (bacterias, hongos, virus).",
    },
    # ── P11 (sin cambios)
    {
        "id": 11,
        "texto": "Ordena los siguientes pasos del protocolo RSA cuando un cliente parece en estado de ebriedad (de primero a último):",
        "tipo": "drag",
        "items_ordenados": [
            "Observar señales de embriaguez",
            "Hablar con el cliente con respeto",
            "Ofrecer agua o alimentos",
            "Negar más alcohol si es necesario",
            "Notificar al gerente",
            "Ayudar a conseguir transporte seguro",
        ],
        "puntos": 7,
        "comodin": None,
    },
    # ── P12 (sin cambios)
    {
        "id": 12,
        "texto": "¿Cuál de estas frases es la más adecuada para negar el servicio de alcohol a un cliente?",
        "tipo": "radio",
        "opciones": [
            "'No te voy a servir porque ya estás borracho.'",
            "'Lo siento, por política del establecimiento no puedo servirte más alcohol en este momento. ¿Puedo ofrecerte agua o algo de comer?'",
            "'Mi jefe dice que ya no te sirva.'",
            "'Ya tomaste mucho, mejor vete a tu casa.'",
        ],
        "correcta": "'Lo siento, por política del establecimiento no puedo servirte más alcohol en este momento. ¿Puedo ofrecerte agua o algo de comer?'",
        "puntos": 5,
        "comodin": None,
    },
    # ── P15 — fill-in con bonus para no-gerencial
    {
        "id": 15,
        "texto": "Completa los espacios en blanco de nuestra política RSA:",
        "tipo": "fill",
        "template": "No servimos alcohol a menores de ___ años. Siempre pedimos ___ oficial. Si hay duda, ___.",
        "campos": [
            {"label": "Edad mínima", "correcta": "18", "clave": "edad"},
            {"label": "Tipo de documento", "correcta": "identificación", "clave": "doc",
             "alternativas": ["id", "ine", "pasaporte", "credencial", "documento"]},
            {"label": "Acción a tomar", "correcta": "no servimos", "clave": "accion",
             "alternativas": ["negamos", "no servir", "rechazamos", "no se sirve", "negar"]},
        ],
        "puntos": 6,
        "puntos_bonus_no_gerencial": 3,   # puntos extra si no-gerencial responde bien
        "comodin": None,
        "gerencial": True,                # marca que es pregunta avanzada
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def generar_codigo() -> str:
    return str(random.randint(100, 999))

def generar_uuid() -> str:
    return str(uuid.uuid4())

def device_hash() -> str:
    raw = f"{time.time()}-{uuid.uuid4()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]

def similarity_score(respuesta: str, validas: list) -> float:
    resp = respuesta.strip().lower()
    best = 0.0
    for v in validas:
        v_lower = v.lower()
        if v_lower in resp or resp in v_lower:
            return 1.0
        if HAS_RAPIDFUZZ:
            score = fuzz.partial_ratio(resp, v_lower) / 100
        else:
            score = difflib.SequenceMatcher(None, resp, v_lower).ratio()
        best = max(best, score)
    return best

def respuesta_abierta_correcta(respuesta: str, validas: list, umbral=0.45) -> bool:
    if not respuesta or len(respuesta.strip()) < 3:
        return False
    return similarity_score(respuesta, validas) >= umbral

def mezclar_preguntas(preguntas: list) -> list:
    """Mezcla todas las preguntas sin fijar ninguna al final (quiz corto)."""
    mezclables = preguntas[:]
    random.shuffle(mezclables)
    return mezclables


# ─────────────────────────────────────────────────────────────────────────────
#  EVALUACIÓN POR TIPO
# ─────────────────────────────────────────────────────────────────────────────

def evaluar_open_flexible(respuesta: str, pregunta: dict) -> tuple[bool, int, int]:
    """
    Evaluación flexible progresiva para la pregunta combinada de contaminación.
    Retorna (correcto_total, puntos_ganados, categorias_encontradas).
    - Cada categoría identificada suma puntos proporcionales.
    - Ejemplos físicos también suman aunque no mencionen 'física'.
    - No penaliza respuestas parciales.
    """
    pts       = pregunta["puntos"]
    categorias = pregunta["categorias"]
    resp_lower = respuesta.strip().lower()

    encontradas = set()
    for nombre_cat, keywords in categorias.items():
        for kw in keywords:
            if kw in resp_lower:
                encontradas.add(nombre_cat)
                break
        # fuzzy fallback si no matcheó exacto
        if nombre_cat not in encontradas:
            if similarity_score(resp_lower, keywords) >= 0.55:
                encontradas.add(nombre_cat)

    n = len(encontradas)
    total_cats = len(categorias)

    if n == 0:
        puntos_ganados = 0
    elif n == 1:
        puntos_ganados = round(pts * 0.35)   # ~35% por una categoría/ejemplo
    elif n == 2:
        puntos_ganados = round(pts * 0.70)   # ~70% por dos
    else:
        puntos_ganados = pts                  # 100% por las tres

    correcto = n == total_cats
    return correcto, puntos_ganados, n


def evaluar_fill_con_bonus(pregunta: dict, respuesta: dict, rol: str) -> tuple[bool, int, bool]:
    """
    Evalúa fill-in. Si es no-gerencial y responde bien → bonus.
    Retorna (correcto, puntos_ganados, es_bonus).
    """
    campos   = pregunta["campos"]
    pts      = pregunta["puntos"]
    aciertos = 0

    for campo in campos:
        val = str(respuesta.get(campo["clave"], "")).strip().lower()
        correcta_lower = campo["correcta"].lower()
        alternativas   = [a.lower() for a in campo.get("alternativas", [])]
        if val == correcta_lower or val in alternativas or respuesta_abierta_correcta(val, [correcta_lower] + alternativas):
            aciertos += 1

    correcto      = aciertos == len(campos)
    pts_parciales = round((aciertos / len(campos)) * pts)

    # Bonus solo si no-gerencial Y responde bien (al menos 2/3 campos)
    es_bonus = False
    if rol != "Gerencial" and aciertos >= 2:
        es_bonus = True
        pts_parciales += pregunta.get("puntos_bonus_no_gerencial", 0)

    # No penalizar: nunca dar negativo
    pts_parciales = max(0, pts_parciales)
    return correcto, pts_parciales, es_bonus


def evaluar_respuesta(pregunta: dict, respuesta) -> tuple[bool, int, dict]:
    """
    Retorna (correcto, puntos_ganados, meta).
    meta es un dict con info extra para el feedback (bonus, categorias, etc.)
    """
    tipo = pregunta["tipo"]
    pts  = pregunta["puntos"]
    meta = {}

    if tipo == "radio":
        correcto = respuesta == pregunta["correcta"]
        return correcto, pts if correcto else 0, meta

    elif tipo == "multi":
        seleccion = set(respuesta) if respuesta else set()
        correctas = set(pregunta["correctas"])
        aciertos  = len(seleccion & correctas)
        errores   = len(seleccion - correctas)
        total_c   = len(correctas)
        parcial   = max(0, aciertos - errores)
        puntos_parciales = round((parcial / total_c) * pts)
        correcto  = seleccion == correctas
        return correcto, puntos_parciales, meta

    elif tipo == "open":
        correcto = respuesta_abierta_correcta(str(respuesta), pregunta["respuestas_validas"])
        return correcto, pts if correcto else 0, meta

    elif tipo == "open_flexible":
        correcto, pts_ganados, n_cats = evaluar_open_flexible(str(respuesta), pregunta)
        meta["categorias_encontradas"] = n_cats
        meta["total_categorias"]       = len(pregunta["categorias"])
        return correcto, pts_ganados, meta

    elif tipo == "drag":
        correcto = list(respuesta) == pregunta["items_ordenados"]
        return correcto, pts if correcto else 0, meta

    elif tipo == "fill":
        correcto, pts_ganados, es_bonus = evaluar_fill_con_bonus(
            pregunta, respuesta, st.session_state.rol
        )
        meta["es_bonus"] = es_bonus
        return correcto, pts_ganados, meta

    elif tipo == "open_list":
        items    = [str(r).strip() for r in (respuesta if respuesta else []) if str(r).strip()]
        aciertos = sum(1 for r in items if respuesta_abierta_correcta(r, pregunta["respuestas_validas"]))
        num_req  = (pregunta["num_respuestas_gerencial"]
                    if st.session_state.rol == "Gerencial"
                    else pregunta["num_respuestas_no_gerencial"])
        correcto = aciertos >= num_req
        return correcto, round((min(aciertos, num_req) / num_req) * pts), meta

    return False, 0, meta


# ─────────────────────────────────────────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────────────────────────────────────────

def guardar_en_sheets(datos: dict):
    if not HAS_GSPREAD:
        return False
    try:
        creds_dict = st.secrets.get("gcp_service_account", None)
        if not creds_dict:
            return False
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(dict(creds_dict), scopes=scopes)
        gc    = gspread.authorize(creds)
        sheet_id = st.secrets.get("google_sheet_id", "")
        if not sheet_id:
            return False
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        existing = ws.row_values(1)
        if not existing:
            ws.append_row([
                "Nombre", "Rol", "Código", "Score", "%",
                "Fecha", "Hora", "UUID", "Respuestas"
            ])
        row = [
            datos.get("nombre", ""),
            datos.get("rol", ""),
            datos.get("codigo", ""),
            datos.get("score", 0),
            datos.get("porcentaje", "0%"),
            datos.get("fecha", ""),
            datos.get("hora", ""),
            datos.get("uuid", ""),
            json.dumps(datos.get("respuestas", {}), ensure_ascii=False),
        ]
        ws.append_row(row)
        return True
    except Exception as e:
        st.warning(f"No se pudo guardar en Sheets: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "pantalla": "intro",
        "nombre": "",
        "rol": "",
        "codigo": generar_codigo(),
        "uuid": generar_uuid(),
        "device": device_hash(),
        "timestamp": datetime.now().isoformat(),
        "preguntas_orden": [],
        "idx_actual": 0,
        "puntaje": 0,
        "bonus_suma": 0,
        "respuestas": {},
        "comodin_usado": False,
        "chips_por_pregunta": {},
        "drag_orden": [],
        "guardado": False,
        "mostrar_feedback": False,
        "ultimo_feedback": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def mostrar_top_bar():
    st.markdown("""
    <div class="top-bar">
      <div><div class="logo">☕</div></div>
      <div>
        <div class="title-text">RSA Quiz</div>
        <div class="sub">Responsible Service of Alcohol</div>
      </div>
      <div style="font-size:.75rem; opacity:.8;">Starbucks</div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_codigo():
    st.markdown(f"""
    <div class="code-badge">
      <div class="code-num">{st.session_state.codigo}</div>
      <div class="code-label">Tu código de validación único</div>
      <div class="code-warn">⚠️ No compartas capturas de pantalla con otros compañeros.</div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_progreso():
    total  = len(st.session_state.preguntas_orden)
    actual = st.session_state.idx_actual
    pct    = int((actual / total) * 100) if total else 0
    st.markdown(f"""
    <div class="progress-wrap">
      <div class="progress-label">
        <span>Pregunta {actual + 1} de {total}</span>
        <span>{pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:{pct}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  RENDERIZADO POR TIPO
# ─────────────────────────────────────────────────────────────────────────────

def render_radio(pregunta, key_prefix, disabled=False):
    opciones_key = f"{key_prefix}_opciones"
    if opciones_key not in st.session_state:
        opciones = pregunta["opciones"][:]
        random.shuffle(opciones)
        st.session_state[opciones_key] = opciones
    opciones = st.session_state[opciones_key]
    return st.radio("Selecciona tu respuesta:", opciones, key=f"{key_prefix}_radio",
                    index=None, disabled=disabled)


def render_multi(pregunta, key_prefix, disabled=False):
    st.markdown("**Selecciona todas las que apliquen:**")
    opciones_key = f"{key_prefix}_opciones_orden"
    if opciones_key not in st.session_state:
        opciones = pregunta["opciones"][:]
        random.shuffle(opciones)
        st.session_state[opciones_key] = opciones
    opciones  = st.session_state[opciones_key]
    q_id      = pregunta["id"]
    previos   = st.session_state.chips_por_pregunta.get(q_id, [])
    seleccionados = []
    for i, opcion in enumerate(opciones):
        checked = st.checkbox(opcion, key=f"{key_prefix}_cb_{i}",
                              value=(opcion in previos), disabled=disabled)
        if checked:
            seleccionados.append(opcion)
    st.session_state.chips_por_pregunta[q_id] = seleccionados
    return seleccionados


def render_open(pregunta, key_prefix, disabled=False):
    return st.text_area("Tu respuesta:", key=f"{key_prefix}_open",
                        height=90, placeholder="Escribe tu respuesta aquí…",
                        disabled=disabled)


def render_open_flexible(pregunta, key_prefix, disabled=False):
    """Textarea con hint de categorías esperadas."""
    st.markdown("💡 *Puedes mencionar los tipos y/o dar ejemplos concretos.*")
    return st.text_area(
        "Tu respuesta:",
        key=f"{key_prefix}_open_flex",
        height=110,
        placeholder="Ej: contaminación física como polvo o cabellos, química, microbiológica…",
        disabled=disabled,
    )


def render_drag(pregunta, key_prefix, disabled=False):
    st.markdown("**Ordena los pasos (1 = primero, último = al final):**")
    init_key = f"{key_prefix}_drag_init"
    if init_key not in st.session_state:
        shuffled = pregunta["items_ordenados"][:]
        random.shuffle(shuffled)
        st.session_state[init_key] = shuffled
        st.session_state.drag_orden = shuffled[:]
    orden_actual = st.session_state.drag_orden or st.session_state[init_key][:]
    st.session_state.drag_orden = orden_actual
    for i, item in enumerate(orden_actual):
        cols = st.columns([6, 1, 1])
        cols[0].markdown(f"<div class='drag-item'>{i+1}. {item}</div>", unsafe_allow_html=True)
        if not disabled:
            if i > 0 and cols[1].button("▲", key=f"{key_prefix}_up_{i}"):
                orden_actual[i], orden_actual[i-1] = orden_actual[i-1], orden_actual[i]
                st.session_state.drag_orden = orden_actual[:]
                st.rerun()
            if i < len(orden_actual)-1 and cols[2].button("▼", key=f"{key_prefix}_dn_{i}"):
                orden_actual[i], orden_actual[i+1] = orden_actual[i+1], orden_actual[i]
                st.session_state.drag_orden = orden_actual[:]
                st.rerun()
    return st.session_state.drag_orden


def render_fill(pregunta, key_prefix, disabled=False):
    st.markdown(f"**{pregunta['template']}**")
    respuestas = {}
    for campo in pregunta["campos"]:
        val = st.text_input(campo["label"], key=f"{key_prefix}_fill_{campo['clave']}",
                            placeholder=f"Completa: {campo['label']}…", disabled=disabled)
        respuestas[campo["clave"]] = val
    return respuestas


# ─────────────────────────────────────────────────────────────────────────────
#  PANTALLAS
# ─────────────────────────────────────────────────────────────────────────────

def pantalla_intro():
    mostrar_top_bar()
    st.markdown("""
    <div class="intro-hero">
      <h1>Hola compañero,<br>hacemos esto por tu bien ☕</h1>
      <div class="sub">Evaluación RSA — Responsible Service of Alcohol</div>
    </div>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        nombre = st.text_input("Déjanos tu nombre", placeholder="Escribe tu nombre completo…", key="input_nombre")
        st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Comenzar ▶", key="btn_comenzar"):
        if not nombre or len(nombre.strip()) < 2:
            st.warning("Por favor ingresa tu nombre para continuar.")
        else:
            st.session_state.nombre   = nombre.strip()
            st.session_state.pantalla = "rol"
            st.rerun()


def pantalla_rol():
    mostrar_top_bar()
    st.markdown(f"""
    <div class="quiz-card" style="text-align:center;">
      <div style="font-size:1.5rem; margin-bottom:.3rem;">👋</div>
      <div style="font-size:1.2rem; font-weight:700; color:#00704A;">¡Hola, {st.session_state.nombre}!</div>
      <div style="font-size:.9rem; color:#6B6B6B; margin-top:.3rem;">Selecciona tu rol para continuar</div>
    </div>
    """, unsafe_allow_html=True)
    mostrar_codigo()
    rol = st.radio("Selecciona tu rol:", ["Partner", "Gerencial"], key="radio_rol", horizontal=True)
    if st.button("Continuar →", key="btn_rol"):
        st.session_state.rol              = rol
        st.session_state.preguntas_orden  = mezclar_preguntas(PREGUNTAS)
        st.session_state.idx_actual       = 0
        st.session_state.pantalla         = "quiz"
        st.rerun()


def pantalla_quiz():
    mostrar_top_bar()
    mostrar_codigo()
    mostrar_progreso()

    preguntas = st.session_state.preguntas_orden
    idx       = st.session_state.idx_actual

    if idx >= len(preguntas):
        st.session_state.pantalla = "resultado"
        st.rerun()
        return

    pregunta   = preguntas[idx]
    q_id       = pregunta["id"]
    tipo       = pregunta["tipo"]
    key_prefix = f"q{q_id}"
    ya_respondida = st.session_state.mostrar_feedback

    # ── Card pregunta
    st.markdown(f"""
    <div class="quiz-card">
      <div class="q-number">Pregunta {idx + 1} / {len(preguntas)}</div>
      <div class="q-text">{pregunta["texto"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Comodín
    tiene_comodin = bool(pregunta.get("comodin"))
    if tiene_comodin and not ya_respondida:
        if not st.session_state.comodin_usado:
            if st.button("💡 Usar ayuda (comodín)", key=f"{key_prefix}_comodin"):
                st.session_state.comodin_usado = True
                st.rerun()
        else:
            st.markdown(f"""
            <div class="comodin-box">
              💡 <strong>Ayuda:</strong> {pregunta['comodin']}
            </div>
            """, unsafe_allow_html=True)

    # ── Renderizar
    respuesta = None
    if tipo == "radio":
        respuesta = render_radio(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "multi":
        respuesta = render_multi(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "open":
        respuesta = render_open(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "open_flexible":
        respuesta = render_open_flexible(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "drag":
        respuesta = render_drag(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "fill":
        respuesta = render_fill(pregunta, key_prefix, disabled=ya_respondida)

    st.markdown("---")

    # ── CONFIRMAR
    if not ya_respondida:
        if st.button("Confirmar respuesta ✓", key=f"{key_prefix}_confirmar", use_container_width=True):
            correcto, pts_ganados, meta = evaluar_respuesta(pregunta, respuesta)

            st.session_state.respuestas[q_id] = {
                "respuesta": str(respuesta),
                "correcto":  correcto,
                "pts":       pts_ganados,
                "meta":      meta,
            }
            st.session_state.puntaje      += pts_ganados
            st.session_state.mostrar_feedback = True
            st.session_state.ultimo_feedback  = {
                "correcto": correcto,
                "pts":      pts_ganados,
                "max":      pregunta["puntos"],
                "meta":     meta,
                "tipo":     tipo,
            }
            st.rerun()

    # ── FEEDBACK + SIGUIENTE
    else:
        fb   = st.session_state.ultimo_feedback
        meta = fb.get("meta", {})

        # Feedback especial para open_flexible (progresivo)
        if fb["tipo"] == "open_flexible":
            n     = meta.get("categorias_encontradas", 0)
            total = meta.get("total_categorias", 3)
            if n == 0:
                st.markdown(f"""
                <div class="feedback-wrong">
                  ❌ No se identificaron tipos de contaminación. Obtuviste {fb['pts']}/{fb['max']} pts.<br>
                  <small>Recuerda: Física, Química y Microbiológica.</small>
                </div>
                """, unsafe_allow_html=True)
            elif n < total:
                st.markdown(f"""
                <div class="feedback-wrong">
                  ⚠️ Identificaste {n} de {total} tipos. Obtuviste {fb['pts']}/{fb['max']} pts. ¡Bien encaminado!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feedback-correct">
                  ✅ ¡Excelente! Identificaste los {total} tipos de contaminación. {fb['pts']}/{fb['max']} pts.
                </div>
                """, unsafe_allow_html=True)

        # Feedback especial para fill con bonus no-gerencial
        elif fb["tipo"] == "fill" and meta.get("es_bonus"):
            st.markdown(f"""
            <div class="feedback-bonus">
              ⭐ Bonus por conocimiento avanzado — ¡Respondiste una pregunta gerencial!<br>
              Obtuviste {fb['pts']} pts (incluye puntos extra).
            </div>
            """, unsafe_allow_html=True)

        # Feedback estándar
        elif fb["correcto"]:
            st.markdown(f"""
            <div class="feedback-correct">
              ✅ ¡Correcto! Obtuviste {fb['pts']} / {fb['max']} puntos.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="feedback-wrong">
              ❌ Incorrecto. Obtuviste {fb['pts']} / {fb['max']} puntos.
            </div>
            """, unsafe_allow_html=True)

        siguiente_label = "Finalizar ✓" if idx == len(preguntas) - 1 else "Siguiente →"
        if st.button(siguiente_label, key=f"{key_prefix}_next", use_container_width=True):
            st.session_state.idx_actual       += 1
            st.session_state.mostrar_feedback  = False
            st.session_state.ultimo_feedback   = None
            st.session_state.comodin_usado     = False
            st.session_state.drag_orden        = []
            keys_del = [k for k in st.session_state.keys()
                        if k.startswith(f"q{q_id}_") and
                        any(k.endswith(s) for s in ("_opciones_orden", "_drag_init", "_opciones"))]
            for k in keys_del:
                del st.session_state[k]
            st.rerun()


def pantalla_resultado():
    mostrar_top_bar()

    score_final = min(100, st.session_state.puntaje)
    pct         = score_final

    st.markdown("""
    <div class="quiz-card" style="text-align:center; border: 2px solid #CBA135;">
      <div style="font-size:1.5rem;">🧴</div>
      <div style="font-size:1.05rem; font-weight:600; margin:.4rem 0;">Falta ver tu lavado de manos.</div>
      <div style="color:#6B6B6B;">Eso será calificado en tienda.</div>
      <div style="font-size:1.2rem; margin-top:.5rem;">¡Suerte! 🍀</div>
    </div>
    """, unsafe_allow_html=True)

    if score_final >= 70:
        st.markdown('<div class="confetti-msg">🎉🎊✨🎉🎊</div>', unsafe_allow_html=True)

    if score_final == 100:
        msg = "🏆 Excelente estimado, ganaste un abrazo de tu líder RSA. ¡Canjéalo cuando quieras!"
    elif score_final >= 90:
        msg = "⭐ Excelente resultado. ¡Dominas el RSA!"
    elif score_final >= 70:
        msg = "👍 Buen trabajo. Sigue reforzando tus conocimientos."
    elif score_final >= 50:
        msg = "📚 Debes reforzar algunos conceptos RSA."
    else:
        msg = "⚠️ Urgente reforzar conocimientos RSA. ¡Pide apoyo a tu líder!"

    st.markdown(f"""
    <div class="score-card">
      <div class="big-score">{score_final}</div>
      <div class="score-pct">{pct}% de 100 puntos</div>
      <div class="score-msg">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Detalle de tu evaluación")

    for p in st.session_state.preguntas_orden:
        reg         = st.session_state.respuestas.get(p["id"], {})
        correcto    = reg.get("correcto", False)
        pts_ganados = reg.get("pts", 0)
        icono       = "✅" if correcto else ("⚠️" if pts_ganados > 0 else "❌")
        texto       = p["texto"][:55] + ("…" if len(p["texto"]) > 55 else "")
        # Etiqueta bonus
        meta        = reg.get("meta", {})
        bonus_tag   = " ⭐" if meta.get("es_bonus") else ""
        st.markdown(f"""
        <div class="breakdown-row">
          <span>{icono} {texto}{bonus_tag}</span>
          <span class="breakdown-pts">{pts_ganados}/{p['puntos']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin:1rem 0; font-size:1rem; font-weight:600; color:#00704A;">
      📸 Sácale captura a tu resultado
    </div>
    """, unsafe_allow_html=True)

    mostrar_codigo()

    if not st.session_state.guardado:
        now = datetime.now()
        datos = {
            "nombre":     st.session_state.nombre,
            "rol":        st.session_state.rol,
            "codigo":     st.session_state.codigo,
            "score":      score_final,
            "porcentaje": f"{pct}%",
            "fecha":      now.strftime("%Y-%m-%d"),
            "hora":       now.strftime("%H:%M:%S"),
            "uuid":       st.session_state.uuid,
            "respuestas": st.session_state.respuestas,
        }
        guardado_ok = guardar_en_sheets(datos)
        st.session_state.guardado = True
        if guardado_ok:
            st.success("✅ Resultados registrados correctamente.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Volver a intentar", key="btn_reiniciar"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────

pantalla = st.session_state.pantalla
if pantalla == "intro":
    pantalla_intro()
elif pantalla == "rol":
    pantalla_rol()
elif pantalla == "quiz":
    pantalla_quiz()
elif pantalla == "resultado":
    pantalla_resultado()

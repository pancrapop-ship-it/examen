"""
RSA Quiz Interactivo - Starbucks
Archivo: app.py
"""

import streamlit as st
import random
import uuid
import hashlib
import json
import io
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

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders
    HAS_EMAIL = True
except ImportError:
    HAS_EMAIL = False

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
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --brown:    #4A2C17;
  --brown-m:  #6B3F22;
  --brown-l:  #8B5E3C;
  --green:    #2D6A4F;
  --green-l:  #40916C;
  --green-xl: #52B788;
  --cream:    #F8F3EE;
  --card:     rgba(255,252,248,0.88);
  --text:     #1A1208;
  --muted:    #6B5744;
  --border:   rgba(74,44,23,0.15);
  --shadow:   0 4px 24px rgba(74,44,23,0.10);
  --radius:   14px;
  --accent:   #2D6A4F;
}

@media (prefers-color-scheme: dark) {
  :root {
    --cream:  #1C1208;
    --card:   rgba(38,22,10,0.90);
    --text:   #F5EDE4;
    --muted:  #C4A882;
    --border: rgba(139,94,60,0.25);
    --shadow: 0 4px 24px rgba(0,0,0,0.35);
  }
}

html, body, .stApp {
  background: var(--cream) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1rem 4rem !important; max-width: 720px !important; }

.quiz-card {
  background: var(--card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 2.2rem;
  margin: 1rem 0;
  box-shadow: var(--shadow);
  animation: slideUp .45s ease both;
}

.top-bar {
  background: linear-gradient(135deg, var(--brown) 0%, var(--brown-m) 60%, var(--green) 100%);
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
.top-bar .sub { font-size: .78rem; opacity: .85; }

.code-badge {
  background: linear-gradient(135deg, rgba(45,106,79,0.10), rgba(45,106,79,0.05));
  border: 2px solid var(--green-l);
  border-radius: 10px;
  padding: .6rem 1.2rem;
  text-align: center;
  margin-bottom: 1rem;
  animation: fadeIn .6s ease both;
}
.code-badge .code-num { font-size: 2.6rem; font-weight: 800; color: var(--green); letter-spacing: .12em; line-height: 1; }
.code-badge .code-label { font-size: .72rem; color: var(--muted); letter-spacing: .1em; text-transform: uppercase; margin-top: .15rem; }
.code-badge .code-warn { font-size: .75rem; color: var(--brown-l); margin-top: .25rem; font-weight: 500; }

.progress-wrap { margin-bottom: 1rem; }
.progress-label { display: flex; justify-content: space-between; font-size: .78rem; color: var(--muted); margin-bottom: .3rem; }
.progress-track { background: rgba(45,106,79,0.12); border-radius: 99px; height: 8px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--green), var(--green-xl)); border-radius: 99px; transition: width .5s ease; }

.q-number { font-size: .75rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--green); margin-bottom: .3rem; }
.q-text { font-size: 1.08rem; font-weight: 600; color: var(--text); line-height: 1.5; margin-bottom: 1.1rem; }

/* sub-sección dentro de una pregunta compuesta */
.sub-section {
  background: rgba(45,106,79,0.05);
  border-left: 3px solid var(--green-l);
  border-radius: 0 8px 8px 0;
  padding: .7rem 1rem;
  margin: .8rem 0 .4rem;
}
.sub-section-label {
  font-size: .78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--green);
  margin-bottom: .3rem;
}
.sub-section-pts {
  font-size: .72rem;
  color: var(--muted);
}

.drag-item {
  background: var(--card);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  padding: .6rem 1rem;
  margin-bottom: .4rem;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(74,44,23,.06);
  transition: box-shadow .18s;
  color: var(--text);
}

.feedback-correct {
  background: linear-gradient(135deg, rgba(45,106,79,0.15), rgba(64,145,108,0.10));
  border-left: 4px solid var(--green);
  border-radius: 8px;
  padding: .7rem 1rem;
  color: var(--green);
  font-weight: 500;
  margin: .6rem 0;
  animation: slideUp .3s ease both;
}
.feedback-wrong {
  background: linear-gradient(135deg, rgba(139,94,60,0.15), rgba(107,63,34,0.10));
  border-left: 4px solid var(--brown-l);
  border-radius: 8px;
  padding: .7rem 1rem;
  color: var(--brown-m);
  font-weight: 500;
  margin: .6rem 0;
  animation: slideUp .3s ease both;
}
.feedback-bonus {
  background: linear-gradient(135deg, rgba(82,183,136,0.18), rgba(64,145,108,0.12));
  border-left: 4px solid var(--green-xl);
  border-radius: 8px;
  padding: .7rem 1rem;
  color: var(--green);
  font-weight: 600;
  margin: .6rem 0;
  animation: slideUp .3s ease both;
}

.comodin-box {
  background: linear-gradient(135deg, rgba(74,44,23,0.07), rgba(139,94,60,0.05));
  border: 1.5px solid var(--brown-l);
  border-radius: 10px;
  padding: .8rem 1.1rem;
  margin: .6rem 0;
  font-size: .9rem;
  color: var(--text);
  animation: fadeIn .4s ease both;
}
.comodin-box strong { color: var(--brown-m); }

div[data-testid="stButton"] > button {
  background: linear-gradient(135deg, var(--brown) 0%, var(--green) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .95rem !important;
  padding: .6rem 1.6rem !important;
  transition: all .2s ease !important;
  box-shadow: 0 3px 12px rgba(45,106,79,0.25) !important;
}
div[data-testid="stButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 5px 18px rgba(45,106,79,0.35) !important;
}
div[data-testid="stButton"] > button:active { transform: scale(.98) !important; }

.score-card {
  background: linear-gradient(135deg, var(--brown) 0%, var(--brown-m) 40%, var(--green) 100%);
  border-radius: 18px;
  padding: 2.5rem 2rem;
  text-align: center;
  color: white;
  box-shadow: 0 8px 40px rgba(74,44,23,0.30);
  animation: popIn .5s cubic-bezier(.34,1.56,.64,1) both;
}
.score-card .big-score { font-size: 5rem; font-weight: 800; line-height: 1; letter-spacing: -.02em; }
.score-card .score-pct { font-size: 1.5rem; font-weight: 300; opacity: .9; margin-top: .2rem; }
.score-card .score-msg { font-size: 1.05rem; margin-top: .8rem; opacity: .95; font-weight: 500; }

.breakdown-row {
  display: flex;
  justify-content: space-between;
  padding: .45rem 0;
  border-bottom: 1px solid var(--border);
  font-size: .9rem;
  color: var(--text);
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-pts { font-weight: 700; color: var(--green); }

.intro-hero { text-align: center; padding: 2rem 1rem 1.5rem; animation: fadeIn .8s ease both; }
.intro-hero h1 { font-size: 2rem !important; font-weight: 800 !important; color: var(--brown) !important; margin-bottom: .4rem !important; }
.intro-hero .sub { font-size: 1rem; color: var(--muted); }

div[data-testid="stRadio"] label { font-size: .95rem !important; color: var(--text) !important; }
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  border-radius: 8px !important;
  border: 1.5px solid var(--border) !important;
  font-family: 'Inter', sans-serif !important;
  background: var(--card) !important;
  color: var(--text) !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 2px rgba(45,106,79,0.15) !important;
}

@keyframes fadeIn  { from { opacity:0 } to { opacity:1 } }
@keyframes slideUp { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
@keyframes popIn   { from { opacity:0; transform:scale(.85) } to { opacity:1; transform:scale(1) } }

.confetti-msg { font-size: 2.5rem; text-align: center; animation: popIn .6s ease both; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PREGUNTAS
#  FIX: P3 es ahora tipo "contaminacion_compuesta" (tipos + ejemplos en una pantalla)
#       P5 fill: los campos correctos son internos, NO se muestran al jugador
# ─────────────────────────────────────────────────────────────────────────────
PREGUNTAS = [
    # ── P1
    {
        "id": 1,
        "texto": "Menciona los rangos de temperatura de refrigeradores.",
        "tipo": "radio",
        "opciones": ["1 a 4°C", "1 a 3°C", "2 a 4°C", "3 a 6°C"],
        "correcta": "1 a 4°C",
        "puntos": 5,
        "comodin": None,
    },
    # ── P2
    {
        "id": 2,
        "texto": "¿La concentración de sanitizante que maneja Starbucks es de 100-200 ppm?",
        "tipo": "verdadero_falso",
        "correcta": "Verdadero",
        "puntos": 5,
        "comodin": None,
    },
    # ── P3  COMPUESTA: tipos (75%) + ejemplos (25%)
    {
        "id": 3,
        "texto": "¿Qué tipos de contaminación cruzada existen en bebidas y alimentos?",
        "tipo": "contaminacion_compuesta",
        "puntos": 8,
        # Sub-parte 1 — tipos (75 % de los puntos = 6 pts)
        "categorias_tipos": {
            "física": [
                "física","fisico","físico","fisicas","físicas",
                "polvo","cabello","cabellos","pelo","residuo","piedra",
                "acrílico","acrilico","vidrio","metal","astilla","madera",
                "horno","fragmento","objeto","partícula",
            ],
            "química": [
                "química","quimica","químico","quimico",
                "detergente","pesticida","plaguicida","cloro","veneno",
                "tóxico","toxico","limpieza","químicos",
            ],
            "microbiológica": [
                "microbiológica","microbiologica","microbio","bacteria",
                "bacterias","virus","hongo","hongos","microorganismo",
                "germen","gérmenes","patógeno","biologica","biológica",
            ],
        },
        # Sub-parte 2 — ejemplos concretos (25 % de los puntos = 2 pts)
        # Basta con que mencione al menos 1 ejemplo reconocible
        "ejemplos_keywords": [
            "polvo","cabello","pelo","vidrio","metal","astilla","residuo",
            "detergente","pesticida","cloro","veneno","químico",
            "bacteria","virus","hongo","microorganismo","germen",
            "suciedad","tierra","objeto","fragmento","partícula",
        ],
        "comodin": "Piensa en los 3 grandes grupos de riesgos que pueden contaminar un alimento.",
    },
    # ── P4
    {
        "id": 4,
        "texto": "Explique los procedimientos para lavado de utensilios a mano.",
        "tipo": "drag",
        "items_ordenados": ["Lavar", "Enjuagar", "Sanitizar", "Secar al aire"],
        "puntos": 7,
        "comodin": None,
    },
    # ── P5  FIX: campos internos, sin mostrar "correcta" al jugador
    {
        "id": 5,
        "texto": "El cambio de agua y solución sanitizante debe realizarse cada ___ horas.",
        "tipo": "fill",
        "template": "Cada ___ horas.",
        "campos": [
            {
                "label": "¿Cada cuántas horas?",
                # INTERNO: nunca se muestra en pantalla
                "correcta": "2",
                "clave": "horas",
                "alternativas": ["dos", "2 horas", "cada 2"],
            }
        ],
        "puntos": 5,
        "comodin": None,
    },
    # ── P6
    {
        "id": 6,
        "texto": "¿Cuáles son los síntomas de enfermedad que excluirían a una persona de venir a trabajar?",
        "tipo": "open_flexible_bonus",
        "puntos": 8,
        "puntos_bonus_no_gerencial": 3,
        "gerencial": True,
        "categorias": {
            "diarrea":   ["diarrea","evacuaciones","estomago","estómago","intestinal"],
            "vómito":    ["vómito","vomito","nausea","náusea","vomitar","arcadas"],
            "fiebre":    ["fiebre","temperatura alta","calentura","febril"],
            "ictericia": ["ictericia","piel amarilla","ojos amarillos","amarillo","amarilla"],
            "lesión":    ["lesión","lesion","herida","herida abierta","cortada","llaga","úlcera"],
        },
        "comodin": "Recuerda: son 5 síntomas. Piensa en los que afectan el sistema digestivo, la temperatura corporal y la piel.",
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
    if not respuesta or len(respuesta.strip()) < 2:
        return False
    return similarity_score(respuesta, validas) >= umbral

def mezclar_preguntas(preguntas: list) -> list:
    mezclables = preguntas[:]
    random.shuffle(mezclables)
    return mezclables

# ─────────────────────────────────────────────────────────────────────────────
#  EVALUACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def evaluar_open_flexible_categorias(respuesta: str, categorias: dict, pts: int):
    """
    Evaluación por categorías con umbral estricto.
    - Respuesta menor a 3 chars → 0 pts siempre.
    - Solo suma categoría si hay coincidencia EXACTA de substring (keyword in texto).
    - Fuzzy solo como último recurso con umbral alto (0.75).
    - Puntuación: 1 cat = 30%, 2 cat = proporcional, todas = 100%.
    """
    resp_lower = respuesta.strip().lower()

    # Respuesta demasiado corta = 0 puntos sin importar nada
    if len(resp_lower) < 3:
        return False, 0, 0, len(categorias)

    encontradas = set()
    for nombre_cat, keywords in categorias.items():
        # Coincidencia exacta de substring (más fiable)
        for kw in keywords:
            if kw in resp_lower:
                encontradas.add(nombre_cat)
                break
        # Fuzzy solo si no encontró por substring y umbral alto
        if nombre_cat not in encontradas:
            if similarity_score(resp_lower, keywords) >= 0.75:
                encontradas.add(nombre_cat)

    n     = len(encontradas)
    total = len(categorias)

    if n == 0:
        pts_ganados = 0
    elif n == 1:
        pts_ganados = round(pts * 0.30)
    elif n < total:
        pts_ganados = round(pts * (n / total))
    else:
        pts_ganados = pts

    return n == total, pts_ganados, n, total


def evaluar_contaminacion_compuesta(resp_tipos: str, resp_ejemplos: str, pregunta: dict):
    """
    Evalúa la pregunta P3 compuesta:
      - Tipos:    75% de los puntos (pts_tipos)
      - Ejemplos: 25% de los puntos (pts_ejemplos)
    """
    pts_total   = pregunta["puntos"]
    pts_tipos_max    = round(pts_total * 0.75)   # 6 pts
    pts_ejemplos_max = pts_total - pts_tipos_max  # 2 pts

    # ── Tipos
    _, pts_tipos_ganados, n, total = evaluar_open_flexible_categorias(
        resp_tipos, pregunta["categorias_tipos"], pts_tipos_max
    )

    # ── Ejemplos (basta 1 ejemplo reconocible — solo por substring exacto)
    resp_ej_lower = resp_ejemplos.strip().lower()
    ejemplo_ok = False
    if len(resp_ej_lower) >= 3:
        ejemplo_ok = any(kw in resp_ej_lower for kw in pregunta["ejemplos_keywords"])
        if not ejemplo_ok:
            ejemplo_ok = similarity_score(resp_ej_lower, pregunta["ejemplos_keywords"]) >= 0.75
    pts_ejemplos_ganados = pts_ejemplos_max if ejemplo_ok else 0

    pts_total_ganados = pts_tipos_ganados + pts_ejemplos_ganados
    correcto = (n == total) and ejemplo_ok

    meta = {
        "n": n,
        "total": total,
        "pts_tipos": pts_tipos_ganados,
        "pts_ejemplos": pts_ejemplos_ganados,
        "pts_tipos_max": pts_tipos_max,
        "pts_ejemplos_max": pts_ejemplos_max,
        "ejemplo_ok": ejemplo_ok,
    }
    return correcto, pts_total_ganados, meta


def evaluar_respuesta(pregunta: dict, respuesta) -> tuple:
    """Retorna (correcto, puntos_ganados, meta_dict)."""
    tipo = pregunta["tipo"]
    pts  = pregunta["puntos"]
    meta = {}

    if tipo == "radio":
        correcto = respuesta == pregunta["correcta"]
        return correcto, pts if correcto else 0, meta

    elif tipo == "verdadero_falso":
        opcion = respuesta.get("opcion", "") if isinstance(respuesta, dict) else str(respuesta)
        correcto = opcion == pregunta["correcta"]
        return correcto, pts if correcto else 0, meta

    elif tipo == "open":
        correcto = respuesta_abierta_correcta(str(respuesta), pregunta["respuestas_validas"])
        return correcto, pts if correcto else 0, meta

    elif tipo == "open_flexible":
        correcto, pts_ganados, n, total = evaluar_open_flexible_categorias(
            str(respuesta), pregunta["categorias"], pts
        )
        meta["n"] = n
        meta["total"] = total
        return correcto, pts_ganados, meta

    elif tipo == "open_flexible_bonus":
        correcto, pts_ganados, n, total = evaluar_open_flexible_categorias(
            str(respuesta), pregunta["categorias"], pts
        )
        meta["n"] = n
        meta["total"] = total
        es_bonus = False
        if st.session_state.rol != "Gerencial" and n >= 3:
            es_bonus = True
            pts_ganados = min(pts + pregunta.get("puntos_bonus_no_gerencial", 0), pts + 5)
        meta["es_bonus"] = es_bonus
        return correcto, pts_ganados, meta

    elif tipo == "contaminacion_compuesta":
        # respuesta es dict: {"tipos": str, "ejemplos": str}
        resp_tipos    = str(respuesta.get("tipos", ""))
        resp_ejemplos = str(respuesta.get("ejemplos", ""))
        correcto, pts_ganados, meta = evaluar_contaminacion_compuesta(
            resp_tipos, resp_ejemplos, pregunta
        )
        return correcto, pts_ganados, meta

    elif tipo == "drag":
        correcto = list(respuesta) == pregunta["items_ordenados"]
        return correcto, pts if correcto else 0, meta

    elif tipo == "fill":
        campos   = pregunta["campos"]
        aciertos = 0
        for campo in campos:
            val = str(respuesta.get(campo["clave"], "")).strip().lower()
            # Comparar solo internamente — correcta no se muestra al jugador
            correcta_lower = campo["correcta"].lower()
            alternativas   = [a.lower() for a in campo.get("alternativas", [])]
            if val == correcta_lower or val in alternativas or respuesta_abierta_correcta(val, [correcta_lower] + alternativas):
                aciertos += 1
        correcto = aciertos == len(campos)
        return correcto, round((aciertos / len(campos)) * pts), meta

    return False, 0, meta

# ─────────────────────────────────────────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────────────────────────────────────────

def guardar_en_sheets(datos: dict) -> bool:
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
        ws = gc.open_by_key(sheet_id).sheet1
        if not ws.row_values(1):
            ws.append_row(["Nombre","Rol","Código","Score","%","Fecha","Hora","UUID","Respuestas"])
        ws.append_row([
            datos.get("nombre",""),
            datos.get("rol",""),
            datos.get("codigo",""),
            datos.get("score", 0),
            datos.get("porcentaje","0%"),
            datos.get("fecha",""),
            datos.get("hora",""),
            datos.get("uuid",""),
            json.dumps(datos.get("respuestas",{}), ensure_ascii=False),
        ])
        return True
    except Exception as e:
        st.warning(f"No se pudo guardar en Sheets: {e}")
        return False


def obtener_todos_resultados() -> list:
    if not HAS_GSPREAD:
        return []
    try:
        creds_dict = st.secrets.get("gcp_service_account", None)
        if not creds_dict:
            return []
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(dict(creds_dict), scopes=scopes)
        gc    = gspread.authorize(creds)
        sheet_id = st.secrets.get("google_sheet_id", "")
        if not sheet_id:
            return []
        ws = gc.open_by_key(sheet_id).sheet1
        return ws.get_all_records()
    except Exception:
        return []

# ─────────────────────────────────────────────────────────────────────────────
#  PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generar_pdf_resumen(registros: list) -> bytes:
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=letter,
                               leftMargin=0.75*inch, rightMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    brown  = colors.HexColor("#4A2C17")
    green  = colors.HexColor("#2D6A4F")
    cream  = colors.HexColor("#F8F3EE")

    title_style   = ParagraphStyle("Title", parent=styles["Heading1"],
                                   textColor=brown, fontSize=20, spaceAfter=4)
    sub_style     = ParagraphStyle("Sub", parent=styles["Normal"],
                                   textColor=green, fontSize=11, spaceAfter=12)
    body_style    = ParagraphStyle("Body", parent=styles["Normal"],
                                   fontSize=9, spaceAfter=4,
                                   textColor=colors.HexColor("#1A1208"))
    section_style = ParagraphStyle("Section", parent=styles["Heading2"],
                                   textColor=green, fontSize=12,
                                   spaceBefore=14, spaceAfter=6)

    story = []
    story.append(Paragraph("☕ RSA Quiz — Reporte de Resultados", title_style))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
        f"Total de participantes: {len(registros)}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=brown, spaceAfter=14))

    story.append(Paragraph("Resumen General", section_style))
    header_row = ["Nombre", "Rol", "Código", "Score", "%", "Fecha", "Hora"]
    tabla_data = [header_row]
    for r in registros:
        tabla_data.append([
            str(r.get("Nombre",""))[:30],
            str(r.get("Rol","")),
            str(r.get("Código","")),
            str(r.get("Score","")),
            str(r.get("%","")),
            str(r.get("Fecha","")),
            str(r.get("Hora","")),
        ])

    tabla = Table(tabla_data, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), brown),
        ("TEXTCOLOR",      (0,0), (-1,0), colors.white),
        ("FONTNAME",       (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",       (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [cream, colors.white]),
        ("GRID",           (0,0), (-1,-1), 0.5, colors.HexColor("#D4C4B0")),
        ("ALIGN",          (3,0), (4,-1), "CENTER"),
        ("TOPPADDING",     (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 4),
        ("LEFTPADDING",    (0,0), (-1,-1), 6),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=1, color=green, spaceAfter=10))
    story.append(Paragraph("Detalle por Participante", section_style))

    for i, r in enumerate(registros, 1):
        story.append(Paragraph(
            f"<b>{i}. {r.get('Nombre','')} — {r.get('Rol','')} — Código: {r.get('Código','')}</b>",
            ParagraphStyle("P", parent=styles["Normal"], textColor=brown,
                           fontSize=10, spaceBefore=10, spaceAfter=3)
        ))
        story.append(Paragraph(
            f"Score: {r.get('Score','')} pts | {r.get('%','')} | "
            f"{r.get('Fecha','')} {r.get('Hora','')}",
            body_style
        ))
        try:
            respuestas = json.loads(r.get("Respuestas","{}"))
            for q_id, reg in respuestas.items():
                icono    = "✓" if reg.get("correcto") else "✗"
                pts      = reg.get("pts", 0)
                resp_str = str(reg.get("respuesta",""))[:80]
                story.append(Paragraph(
                    f"  {icono} P{q_id}: {resp_str} → {pts} pts",
                    ParagraphStyle("R", parent=styles["Normal"], fontSize=8,
                                   textColor=green if reg.get("correcto")
                                   else colors.HexColor("#6B3F22"), spaceAfter=2)
                ))
        except Exception:
            pass
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#D4C4B0"), spaceAfter=4))

    doc.build(story)
    return buf.getvalue()


def enviar_pdf_por_email(pdf_bytes: bytes, destinatario: str) -> bool:
    if not HAS_EMAIL:
        return False
    try:
        smtp_host = st.secrets.get("smtp_host", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("smtp_port", 587))
        smtp_user = st.secrets.get("smtp_user", "")
        smtp_pass = st.secrets.get("smtp_pass", "")
        if not smtp_user or not smtp_pass:
            return False
        msg = MIMEMultipart()
        msg["From"]    = smtp_user
        msg["To"]      = destinatario
        msg["Subject"] = f"RSA Quiz — Reporte Completo {datetime.now().strftime('%d/%m/%Y')}"
        body = MIMEText(
            f"Hola,\n\nAdjunto el reporte completo del RSA Quiz.\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Correo generado automáticamente.", "plain"
        )
        msg.attach(body)
        part = MIMEBase("application", "octet-stream")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",
                        'attachment; filename="RSA_Quiz_Reporte.pdf"')
        msg.attach(part)
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, destinatario, msg.as_string())
        return True
    except Exception as e:
        st.warning(f"No se pudo enviar el correo: {e}")
        return False

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "pantalla":          "intro",
        "nombre":            "",
        "rol":               "",
        "codigo":            generar_codigo(),
        "uuid":              generar_uuid(),
        "device":            device_hash(),
        "timestamp":         datetime.now().isoformat(),
        "preguntas_orden":   [],
        "idx_actual":        0,
        "puntaje":           0,
        "respuestas":        {},
        "comodin_usado":     False,
        "drag_orden":        [],
        "guardado":          False,
        "mostrar_feedback":  False,
        "ultimo_feedback":   None,
        # FIX: panel admin — no visible para participantes
        "admin_autenticado": False,
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
      <div><div class="title-text">Evaluación RSA</div></div>
      <div style="font-size:.75rem; opacity:.8;">Starbucks</div>
    </div>""", unsafe_allow_html=True)

def mostrar_codigo():
    st.markdown(f"""
    <div class="code-badge">
      <div class="code-num">{st.session_state.codigo}</div>
      <div class="code-label">Tu código de validación único</div>
      <div class="code-warn">⚠️ No compartas capturas de pantalla con otros compañeros.</div>
    </div>""", unsafe_allow_html=True)

def mostrar_progreso():
    total  = len(st.session_state.preguntas_orden)
    actual = st.session_state.idx_actual
    pct    = int((actual / total) * 100) if total else 0
    st.markdown(f"""
    <div class="progress-wrap">
      <div class="progress-label">
        <span>Pregunta {actual+1} de {total}</span>
        <span>{pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:{pct}%"></div>
      </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  RENDER POR TIPO
# ─────────────────────────────────────────────────────────────────────────────

def render_radio(pregunta, key_prefix, disabled=False):
    ok = f"{key_prefix}_opciones"
    if ok not in st.session_state:
        ops = pregunta["opciones"][:]
        random.shuffle(ops)
        st.session_state[ok] = ops
    return st.radio("Selecciona tu respuesta:", st.session_state[ok],
                    key=f"{key_prefix}_radio", index=None, disabled=disabled)


def render_verdadero_falso(pregunta, key_prefix, disabled=False):
    opcion = st.radio(
        "Selecciona tu respuesta:",
        ["Verdadero", "Falso"],
        key=f"{key_prefix}_vf",
        index=None,
        disabled=disabled,
    )
    texto_si_falso = ""
    if opcion == "Falso" and not disabled:
        texto_si_falso = st.text_input(
            "Escribe la respuesta correcta:",
            key=f"{key_prefix}_vf_texto",
            placeholder="¿Cuál crees que es la concentración correcta?",
        )
        st.caption("⚠️ Los puntos corresponden a seleccionar Verdadero.")
    return {"opcion": opcion, "texto_si_falso": texto_si_falso}


def render_open(pregunta, key_prefix, disabled=False):
    return st.text_area("Tu respuesta:", key=f"{key_prefix}_open",
                        height=90, placeholder="Escribe tu respuesta aquí…",
                        disabled=disabled)


def render_open_flexible(pregunta, key_prefix, disabled=False):
    st.markdown("💡 *Menciona los tipos que recuerdes.*")
    return st.text_area("Tu respuesta:", key=f"{key_prefix}_flex",
                        height=110,
                        placeholder="Escribe tu respuesta…",
                        disabled=disabled)


def render_open_flexible_bonus(pregunta, key_prefix, disabled=False):
    st.markdown("💡 *Menciona los síntomas que recuerdes.*")
    return st.text_area("Tu respuesta:", key=f"{key_prefix}_bonus",
                        height=110,
                        placeholder="Escribe tu respuesta…",
                        disabled=disabled)


def render_contaminacion_compuesta(pregunta, key_prefix, disabled=False):
    """
    FIX P3: dos campos en una sola pantalla.
    Campo 1 — tipos de contaminación (75% puntos)
    Campo 2 — ejemplos (25% puntos)
    """
    pts_tipos_max    = round(pregunta["puntos"] * 0.75)
    pts_ejemplos_max = pregunta["puntos"] - pts_tipos_max

    # ── Sub-sección 1: tipos
    st.markdown(f"""
    <div class="sub-section">
      <div class="sub-section-label">Parte 1 — Tipos de contaminación</div>
      <div class="sub-section-pts">Vale {pts_tipos_max} de {pregunta['puntos']} puntos</div>
    </div>""", unsafe_allow_html=True)
    resp_tipos = st.text_area(
        "¿Qué tipos de contaminación cruzada existen?",
        key=f"{key_prefix}_tipos",
        height=80,
        placeholder="Escribe tu respuesta…",
        disabled=disabled,
    )

    # ── Sub-sección 2: ejemplos
    st.markdown(f"""
    <div class="sub-section">
      <div class="sub-section-label">Parte 2 — Ejemplos concretos</div>
      <div class="sub-section-pts">Vale {pts_ejemplos_max} de {pregunta['puntos']} puntos · Da al menos 1 ejemplo</div>
    </div>""", unsafe_allow_html=True)
    resp_ejemplos = st.text_area(
        "Escribe al menos un ejemplo de cualquier tipo:",
        key=f"{key_prefix}_ejemplos",
        height=80,
        placeholder="Escribe tu respuesta…",
        disabled=disabled,
    )

    return {"tipos": resp_tipos or "", "ejemplos": resp_ejemplos or ""}


def render_drag(pregunta, key_prefix, disabled=False):
    st.markdown("**Ordena los pasos con los botones ▲ ▼:**")
    init_key = f"{key_prefix}_drag_init"
    if init_key not in st.session_state:
        shuffled = pregunta["items_ordenados"][:]
        random.shuffle(shuffled)
        st.session_state[init_key] = shuffled
        st.session_state.drag_orden = shuffled[:]

    # Asegurar lista válida
    if not st.session_state.drag_orden or \
       set(st.session_state.drag_orden) != set(pregunta["items_ordenados"]):
        st.session_state.drag_orden = st.session_state[init_key][:]

    orden = st.session_state.drag_orden

    for i, item in enumerate(orden):
        cols = st.columns([7, 1, 1])
        cols[0].markdown(f"<div class='drag-item'>{i+1}. {item}</div>",
                         unsafe_allow_html=True)
        if not disabled:
            if i > 0 and cols[1].button("▲", key=f"{key_prefix}_up_{i}"):
                orden[i], orden[i-1] = orden[i-1], orden[i]
                st.session_state.drag_orden = orden[:]
                st.rerun()
            if i < len(orden)-1 and cols[2].button("▼", key=f"{key_prefix}_dn_{i}"):
                orden[i], orden[i+1] = orden[i+1], orden[i]
                st.session_state.drag_orden = orden[:]
                st.rerun()

    return st.session_state.drag_orden


def render_fill(pregunta, key_prefix, disabled=False):
    """
    FIX P5: muestra solo el template con ___ y el label genérico del campo.
    La respuesta correcta es INTERNA y nunca se muestra al jugador.
    """
    st.markdown(f"**{pregunta['template']}**")
    respuestas = {}
    for campo in pregunta["campos"]:
        val = st.text_input(
            campo["label"],          # label genérico ("¿Cada cuántas horas?")
            key=f"{key_prefix}_fill_{campo['clave']}",
            placeholder="Escribe tu respuesta…",   # sin pista de la correcta
            disabled=disabled,
        )
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
    </div>""", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        nombre = st.text_input("Déjanos tu nombre",
                               placeholder="Escribe tu nombre completo…",
                               key="input_nombre")
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
      <div style="font-size:1.2rem; font-weight:700; color:var(--brown);">
        ¡Hola, {st.session_state.nombre}!
      </div>
      <div style="font-size:.9rem; color:var(--muted); margin-top:.3rem;">
        Selecciona tu rol para continuar
      </div>
    </div>""", unsafe_allow_html=True)
    mostrar_codigo()
    rol = st.radio("Selecciona tu rol:", ["Partner", "Gerencial"],
                   key="radio_rol", horizontal=True)
    if st.button("Continuar →", key="btn_rol"):
        st.session_state.rol             = rol
        st.session_state.preguntas_orden = mezclar_preguntas(PREGUNTAS)
        st.session_state.idx_actual      = 0
        st.session_state.pantalla        = "quiz"
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

    st.markdown(f"""
    <div class="quiz-card">
      <div class="q-number">Pregunta {idx+1} / {len(preguntas)}</div>
      <div class="q-text">{pregunta["texto"]}</div>
    </div>""", unsafe_allow_html=True)

    # Comodín (solo antes de responder)
    if pregunta.get("comodin") and not ya_respondida:
        if not st.session_state.comodin_usado:
            if st.button("💡 Usar ayuda", key=f"{key_prefix}_comodin"):
                st.session_state.comodin_usado = True
                st.rerun()
        else:
            st.markdown(f"""
            <div class="comodin-box">
              💡 <strong>Ayuda:</strong> {pregunta['comodin']}
            </div>""", unsafe_allow_html=True)

    # ── Render según tipo
    respuesta = None
    if tipo == "radio":
        respuesta = render_radio(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "verdadero_falso":
        respuesta = render_verdadero_falso(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "open":
        respuesta = render_open(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "open_flexible":
        respuesta = render_open_flexible(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "open_flexible_bonus":
        respuesta = render_open_flexible_bonus(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "contaminacion_compuesta":
        respuesta = render_contaminacion_compuesta(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "drag":
        respuesta = render_drag(pregunta, key_prefix, disabled=ya_respondida)
    elif tipo == "fill":
        respuesta = render_fill(pregunta, key_prefix, disabled=ya_respondida)

    st.markdown("---")

    # ── Confirmar respuesta
    if not ya_respondida:
        if st.button("Confirmar respuesta ✓", key=f"{key_prefix}_confirmar",
                     use_container_width=True):

            # GUARD: bloquear respuesta vacía
            respuesta_vacia = False
            if tipo == "radio" and respuesta is None:
                respuesta_vacia = True
            elif tipo == "verdadero_falso":
                opcion_vf = respuesta.get("opcion", "") if isinstance(respuesta, dict) else ""
                if not opcion_vf:
                    respuesta_vacia = True
            elif tipo in ("open", "open_flexible", "open_flexible_bonus"):
                if not respuesta or not str(respuesta).strip():
                    respuesta_vacia = True
            elif tipo == "contaminacion_compuesta":
                t = str(respuesta.get("tipos","")).strip() if respuesta else ""
                e = str(respuesta.get("ejemplos","")).strip() if respuesta else ""
                if not t and not e:
                    respuesta_vacia = True
            elif tipo == "fill":
                vals = [str(v).strip() for v in (respuesta or {}).values()]
                if not any(vals):
                    respuesta_vacia = True

            if respuesta_vacia:
                st.warning("⚠️ Debes escribir o seleccionar una respuesta antes de continuar.")
                st.stop()

            correcto, pts_ganados, meta = evaluar_respuesta(pregunta, respuesta)
            st.session_state.respuestas[q_id] = {
                "respuesta": str(respuesta),
                "correcto":  correcto,
                "pts":       pts_ganados,
                "meta":      meta,
            }
            st.session_state.puntaje         += pts_ganados
            st.session_state.mostrar_feedback = True
            st.session_state.ultimo_feedback  = {
                "correcto": correcto,
                "pts":      pts_ganados,
                "max":      pregunta["puntos"],
                "meta":     meta,
                "tipo":     tipo,
            }
            st.rerun()

    # ── Mostrar feedback y botón Siguiente
    else:
        fb   = st.session_state.ultimo_feedback
        meta = fb.get("meta", {})

        if fb["tipo"] == "contaminacion_compuesta":
            n             = meta.get("n", 0)
            total         = meta.get("total", 1)
            pts_tipos     = meta.get("pts_tipos", 0)
            pts_ej        = meta.get("pts_ejemplos", 0)
            pts_tipos_max = meta.get("pts_tipos_max", 0)
            pts_ej_max    = meta.get("pts_ejemplos_max", 0)
            ejemplo_ok    = meta.get("ejemplo_ok", False)

            if n == 0 and not ejemplo_ok:
                st.markdown(f"""
                <div class="feedback-wrong">
                  ❌ No se identificaron respuestas válidas. Obtuviste {fb['pts']}/{fb['max']} pts.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="{'feedback-correct' if fb['correcto'] else 'feedback-wrong'}">
                  {'✅' if fb['correcto'] else '⚠️'} Tipos: {n}/{total} identificados
                  → {pts_tipos}/{pts_tipos_max} pts &nbsp;|&nbsp;
                  Ejemplos: {'✅' if ejemplo_ok else '❌'} → {pts_ej}/{pts_ej_max} pts<br>
                  <strong>Total: {fb['pts']}/{fb['max']} pts</strong>
                </div>""", unsafe_allow_html=True)

        elif fb["tipo"] in ("open_flexible", "open_flexible_bonus"):
            n        = meta.get("n", 0)
            total    = meta.get("total", 1)
            es_bonus = meta.get("es_bonus", False)
            if es_bonus:
                st.markdown(f"""
                <div class="feedback-bonus">
                  ⭐ ¡Bonus por conocimiento avanzado! Obtuviste {fb['pts']} pts.
                </div>""", unsafe_allow_html=True)
            elif n == 0:
                st.markdown(f"""
                <div class="feedback-wrong">
                  ❌ No se identificaron síntomas válidos. {fb['pts']}/{fb['max']} pts.
                </div>""", unsafe_allow_html=True)
            elif n < total:
                st.markdown(f"""
                <div class="feedback-wrong">
                  ⚠️ Identificaste {n} de {total}. {fb['pts']}/{fb['max']} pts. ¡Bien encaminado!
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feedback-correct">
                  ✅ ¡Excelente! Respuesta completa. {fb['pts']}/{fb['max']} pts.
                </div>""", unsafe_allow_html=True)

        elif fb["correcto"]:
            st.markdown(f"""
            <div class="feedback-correct">
              ✅ ¡Correcto! Obtuviste {fb['pts']} / {fb['max']} puntos.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="feedback-wrong">
              ❌ Incorrecto. Obtuviste {fb['pts']} / {fb['max']} puntos.
            </div>""", unsafe_allow_html=True)

        siguiente_label = "Finalizar ✓" if idx == len(preguntas)-1 else "Siguiente →"
        if st.button(siguiente_label, key=f"{key_prefix}_next",
                     use_container_width=True):
            st.session_state.idx_actual      += 1
            st.session_state.mostrar_feedback = False
            st.session_state.ultimo_feedback  = None
            st.session_state.comodin_usado    = False
            st.session_state.drag_orden       = []
            # Limpiar keys de esta pregunta
            to_del = [k for k in st.session_state.keys()
                      if k.startswith(f"q{q_id}_") and
                      any(k.endswith(s) for s in ("_opciones","_drag_init"))]
            for k in to_del:
                del st.session_state[k]
            st.rerun()


def pantalla_resultado():
    mostrar_top_bar()

    score_final = min(100, st.session_state.puntaje)
    pct         = score_final

    st.markdown("""
    <div class="quiz-card" style="text-align:center; border: 2px solid var(--green-l);">
      <div style="font-size:1.5rem;">🧴</div>
      <div style="font-size:1.05rem; font-weight:600; margin:.4rem 0;">Falta ver tu lavado de manos.</div>
      <div style="color:var(--muted);">Eso será calificado en tienda.</div>
      <div style="font-size:1.2rem; margin-top:.5rem;">¡Suerte! 🍀</div>
    </div>""", unsafe_allow_html=True)

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
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Breakdown
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Detalle de tu evaluación")
    for p in st.session_state.preguntas_orden:
        reg   = st.session_state.respuestas.get(p["id"], {})
        ok    = reg.get("correcto", False)
        pts   = reg.get("pts", 0)
        icono = "✅" if ok else ("⚠️" if pts > 0 else "❌")
        txt   = p["texto"][:55] + ("…" if len(p["texto"]) > 55 else "")
        bonus = " ⭐" if reg.get("meta", {}).get("es_bonus") else ""
        st.markdown(f"""
        <div class="breakdown-row">
          <span>{icono} {txt}{bonus}</span>
          <span class="breakdown-pts">{pts}/{p['puntos']}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin:1rem 0; font-size:1rem;
                font-weight:600; color:var(--green);">
      📸 Sácale captura a tu resultado
    </div>""", unsafe_allow_html=True)
    mostrar_codigo()

    # ── Guardar (una sola vez)
    if not st.session_state.guardado:
        now   = datetime.now()
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
        ok = guardar_en_sheets(datos)
        st.session_state.guardado = True
        if ok:
            st.success("✅ Resultados registrados correctamente.")

    # ─────────────────────────────────────────────────────────────────────
    #  PANEL ADMIN — FIX: oculto con contraseña, invisible para participantes
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")

    if not st.session_state.admin_autenticado:
        # Solo muestra el botón de acceso — sin hint visible para el participante
        with st.expander("🔐 Acceso administrador"):
            pwd_input = st.text_input(
                "Contraseña de administrador",
                type="password",
                key="admin_pwd_input",
                placeholder="Solo para el líder RSA",
            )
            if st.button("Entrar", key="btn_admin_login"):
                # Contraseña configurada en st.secrets["admin_password"]
                # o por defecto "rsa2024admin" si no está configurada
                admin_pwd = st.secrets.get("admin_password", "rsa2024admin")
                if pwd_input == admin_pwd:
                    st.session_state.admin_autenticado = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
    else:
        # Panel visible solo tras autenticación
        with st.expander("🔐 Panel de administración — Líder RSA", expanded=True):
            st.markdown("*Usa esta sección cuando todos los participantes hayan completado el quiz.*")
            registros   = obtener_todos_resultados()
            n_registros = len(registros)
            st.info(f"Participantes registrados: **{n_registros}**")

            if st.button("📄 Generar PDF y enviar reporte", key="btn_pdf"):
                if not HAS_REPORTLAB:
                    st.error("reportlab no está instalado. Revisa requirements.txt.")
                elif n_registros == 0:
                    st.warning("No hay registros en Google Sheets aún.")
                else:
                    with st.spinner("Generando PDF…"):
                        pdf_bytes = generar_pdf_resumen(registros)
                    destinatario = st.secrets.get("admin_email", "pancrapop@gmail.com")
                    enviado = enviar_pdf_por_email(pdf_bytes, destinatario)
                    if enviado:
                        st.success(f"✅ PDF enviado a {destinatario} con {n_registros} participantes.")
                    else:
                        st.warning("No se pudo enviar por correo. Descarga el PDF manualmente:")
                    st.download_button(
                        "⬇️ Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"RSA_Quiz_Reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        key="btn_dl_pdf",
                    )

            if st.button("🔒 Cerrar sesión admin", key="btn_admin_logout"):
                st.session_state.admin_autenticado = False
                st.rerun()

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

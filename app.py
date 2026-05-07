"""
RSA Quiz Interactivo - Starbucks
Archivo: app.py
Descripción: Quiz interactivo RSA para 14 colaboradores con registro en Google Sheets.
"""

import streamlit as st
import random
import uuid
import hashlib
import json
from datetime import datetime
import time
import re

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
#  CSS PREMIUM
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

/* ── Glassmorphism card ── */
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

/* ── Header strip ── */
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

/* ── Validation code badge ── */
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

/* ── Progress bar ── */
.progress-wrap {
  margin-bottom: 1rem;
}
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

/* ── Question card ── */
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

/* ── Chips (lluvia de cuadros) ── */
.chips-grid {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
  margin-bottom: .8rem;
}
.chip {
  background: rgba(0,112,74,0.08);
  border: 1.5px solid rgba(0,112,74,0.25);
  border-radius: 8px;
  padding: .45rem .9rem;
  font-size: .88rem;
  cursor: pointer;
  transition: all .18s ease;
  user-select: none;
  font-weight: 500;
}
.chip:hover { background: rgba(0,112,74,0.15); border-color: var(--green); }
.chip.selected {
  background: var(--green);
  color: white;
  border-color: var(--green);
  transform: scale(1.04);
}

/* ── Drag & drop ── */
.drag-item {
  background: var(--card);
  border: 1.5px solid rgba(0,112,74,0.2);
  border-radius: 10px;
  padding: .6rem 1rem;
  margin-bottom: .4rem;
  cursor: grab;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
  transition: box-shadow .18s;
}
.drag-item:hover { box-shadow: 0 4px 16px rgba(0,112,74,.14); }

/* ── Feedback toasts ── */
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

/* ── Comodín ── */
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

/* ── Buttons ── */
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

/* ── Secondary button ── */
.btn-secondary div[data-testid="stButton"] > button {
  background: transparent !important;
  color: var(--green) !important;
  border: 1.5px solid var(--green) !important;
  box-shadow: none !important;
}

/* ── Score card final ── */
.score-card {
  background: linear-gradient(135deg, var(--green) 0%, var(--green-l) 100%);
  border-radius: 18px;
  padding: 2.5rem 2rem;
  text-align: center;
  color: white;
  box-shadow: 0 8px 40px rgba(0,112,74,0.3);
  animation: popIn .5s cubic-bezier(.34,1.56,.64,1) both;
}
.score-card .big-score {
  font-size: 5rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -.02em;
}
.score-card .score-pct {
  font-size: 1.5rem;
  font-weight: 300;
  opacity: .9;
  margin-top: .2rem;
}
.score-card .score-msg {
  font-size: 1.05rem;
  margin-top: .8rem;
  opacity: .95;
  font-weight: 500;
}
.breakdown-row {
  display: flex;
  justify-content: space-between;
  padding: .45rem 0;
  border-bottom: 1px solid rgba(0,112,74,0.1);
  font-size: .9rem;
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-pts { font-weight: 700; color: var(--green); }

/* ── Intro ── */
.intro-hero {
  text-align: center;
  padding: 2rem 1rem 1.5rem;
  animation: fadeIn .8s ease both;
}
.intro-hero h1 {
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: var(--green) !important;
  margin-bottom: .4rem !important;
}
.intro-hero .sub {
  font-size: 1rem;
  color: var(--muted);
}

/* ── Keyframes ── */
@keyframes fadeIn    { from { opacity:0 } to { opacity:1 } }
@keyframes slideUp   { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
@keyframes popIn     { from { opacity:0; transform:scale(.85) } to { opacity:1; transform:scale(1) } }

/* ── Radio & inputs ── */
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

/* ── Selectbox ── */
div[data-testid="stSelectbox"] select {
  border-radius: 8px !important;
}

/* Confetti placeholder */
.confetti-msg {
  font-size: 2.5rem;
  text-align: center;
  animation: popIn .6s ease both;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PREGUNTAS (18 preguntas RSA)
#  Formato: dict con claves estandarizadas
# ─────────────────────────────────────────────────────────────────────────────
"""
TIPO DE PREGUNTA:
  radio       → opción única
  multi       → chips seleccionables (lluvia de cuadros)
  open        → texto libre (fuzzy match)
  drag        → drag & drop ordenamiento
  fill        → rellenar campos
  open_list   → múltiples campos de texto (lista libre)
"""

PREGUNTAS = [
    # ── P1
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
    # ── P2
    {
        "id": 2,
        "texto": "¿Cuál es la edad mínima legal para consumir alcohol en México?",
        "tipo": "radio",
        "opciones": ["16 años", "17 años", "18 años", "21 años"],
        "correcta": "18 años",
        "puntos": 5,
        "comodin": None,
    },
    # ── P3
    {
        "id": 3,
        "texto": "¿Cuáles de las siguientes señales indican que un cliente puede estar en estado de ebriedad? (Selecciona todas las correctas)",
        "tipo": "multi",
        "opciones": [
            "Habla con dificultad",
            "Pide agua",
            "Ojos rojos o vidriosos",
            "Está muy animado y sonriente",
            "Problemas de equilibrio",
            "Comportamiento agresivo",
            "Pide la cuenta",
            "Olor a alcohol",
        ],
        "correctas": [
            "Habla con dificultad",
            "Ojos rojos o vidriosos",
            "Problemas de equilibrio",
            "Comportamiento agresivo",
            "Olor a alcohol",
        ],
        "puntos": 6,
        "comodin": None,
    },
    # ── P4
    {
        "id": 4,
        "texto": "¿Cuáles son razones válidas para NEGAR el servicio de alcohol? (Selecciona todas las que apliquen)",
        "tipo": "multi",
        "opciones": [
            "El cliente parece menor de edad",
            "El cliente es conocido del gerente",
            "El cliente muestra signos de embriaguez",
            "El cliente tiene prisa",
            "No presenta identificación",
            "El cliente pide el trago 'del chef'",
            "El cliente está en un evento privado",
            "El cliente tiene comportamiento violento",
        ],
        "correctas": [
            "El cliente parece menor de edad",
            "El cliente muestra signos de embriaguez",
            "No presenta identificación",
            "El cliente tiene comportamiento violento",
        ],
        "puntos": 6,
        "comodin": None,
    },
    # ── P5
    {
        "id": 5,
        "texto": "¿Qué debes hacer si un cliente menor de edad intenta comprar alcohol con una identificación falsa?",
        "tipo": "radio",
        "opciones": [
            "Venderle si parece adulto",
            "Negar la venta y reportar al gerente",
            "Pedir otra identificación y si no tiene, vender igual",
            "Ignorarlo y continuar con el siguiente cliente",
        ],
        "correcta": "Negar la venta y reportar al gerente",
        "puntos": 5,
        "comodin": None,
    },
    # ── P6
    {
        "id": 6,
        "texto": "¿Qué identificaciones son válidas para verificar la edad de un cliente en México?",
        "tipo": "multi",
        "opciones": [
            "INE / IFE",
            "Pasaporte",
            "Tarjeta de crédito",
            "Licencia de conducir",
            "Credencial escolar",
            "Acta de nacimiento",
        ],
        "correctas": ["INE / IFE", "Pasaporte", "Licencia de conducir"],
        "puntos": 5,
        "comodin": None,
    },
    # ── P7
    {
        "id": 7,
        "texto": "Un cliente dice: 'Solo tomé dos cervezas, dame otra.' ¿Qué factores debes considerar antes de servir?",
        "tipo": "open",
        "respuestas_validas": [
            "apariencia física", "signos de ebriedad", "comportamiento",
            "tiempo transcurrido", "peso corporal", "tolerancia",
            "cómo se ve", "estado físico", "cómo habla",
        ],
        "puntos": 6,
        "comodin": None,
    },
    # ── P8
    {
        "id": 8,
        "texto": "¿Cuál es el porcentaje de alcohol en sangre (BAC) considerado el límite legal para conducir en la mayoría de los estados de México?",
        "tipo": "radio",
        "opciones": ["0.04%", "0.08%", "0.05%", "0.10%"],
        "correcta": "0.08%",
        "puntos": 5,
        "comodin": "El límite legal en la mayoría de los estados de México es 0.08% de alcohol en sangre (BAC).",
    },
    # ── P9
    {
        "id": 9,
        "texto": "¿Qué es el 'efecto de tolerancia' al alcohol y cómo afecta el servicio responsable?",
        "tipo": "open",
        "respuestas_validas": [
            "el cuerpo se acostumbra", "necesita más alcohol para sentir el efecto",
            "mayor resistencia", "acostumbrado al alcohol", "tolerancia desarrollada",
            "no se nota borracho pero sí lo está", "puede parecer sobrio pero estar ebrio",
        ],
        "puntos": 6,
        "comodin": "La tolerancia ocurre cuando el cuerpo se acostumbra al alcohol y la persona necesita más cantidad para sentir el mismo efecto. Puede parecer sobria aunque su BAC sea alto.",
    },
    # ── P10 (BONUS)
    {
        "id": 10,
        "texto": "PREGUNTA BONUS: ¿Cuántas unidades de alcohol (UBEs) contiene aproximadamente una copa de vino de 150ml al 12%?",
        "tipo": "radio",
        "opciones": ["0.5 UBEs", "1.4 UBEs", "2 UBEs", "3 UBEs"],
        "correcta": "1.4 UBEs",
        "puntos": 5,  # bonus, tope 100
        "bonus": True,
        "comodin": None,
    },
    # ── P11 (DRAG & DROP)
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
    # ── P12
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
    # ── P13 (CHIPS MULTI)
    {
        "id": 13,
        "texto": "¿Cuáles de las siguientes acciones forman parte del servicio responsable de alcohol? (Elige todas las correctas)",
        "tipo": "multi",
        "opciones": [
            "Verificar identificación",
            "Ofrecer agua entre bebidas",
            "Servir rondas dobles si el cliente insiste",
            "Monitorear el comportamiento del cliente",
            "Ignorar si el cliente pide 'solo uno más'",
            "Conocer el menú de alimentos para sugerirlos",
            "Tener contacto de taxis/Uber disponible",
            "Llevar la cuenta de bebidas servidas",
        ],
        "correctas": [
            "Verificar identificación",
            "Ofrecer agua entre bebidas",
            "Monitorear el comportamiento del cliente",
            "Conocer el menú de alimentos para sugerirlos",
            "Tener contacto de taxis/Uber disponible",
            "Llevar la cuenta de bebidas servidas",
        ],
        "puntos": 7,
        "comodin": None,
    },
    # ── P14
    {
        "id": 14,
        "texto": "¿Qué responsabilidad legal puede enfrentar el establecimiento si sirve alcohol a un menor de edad?",
        "tipo": "open",
        "respuestas_validas": [
            "multa", "clausura", "cierre", "sanción", "demanda",
            "responsabilidad civil", "responsabilidad penal", "consecuencias legales",
            "pérdida de licencia", "penalización",
        ],
        "puntos": 6,
        "comodin": None,
    },
    # ── P15 (FILL IN)
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
        "comodin": None,
    },
    # ── P16 (SIEMPRE PENÚLTIMA)
    {
        "id": 16,
        "texto": "Describe con tus propias palabras qué harías si un cliente llega ya en estado de ebriedad y pide alcohol.",
        "tipo": "open",
        "respuestas_validas": [
            "negar", "no servir", "avisar", "gerente", "agua", "taxi",
            "transporte", "seguridad", "protocolo", "respetuoso",
            "amablemente", "no le sirvo", "rechazar",
        ],
        "puntos": 8,
        "comodin": None,
    },
    # ── P17 (SIEMPRE ÚLTIMA — lógica por rol)
    {
        "id": 17,
        "texto": "¿Cuáles son las acciones que debe tomar tu equipo/tú ante un incidente RSA?",
        "tipo": "open_list",
        "num_respuestas_gerencial": 4,
        "num_respuestas_no_gerencial": 3,
        "respuestas_validas": [
            "documentar", "reportar", "notificar", "gerente", "incidente",
            "protocolo", "seguridad", "autoridades", "registro", "acción correctiva",
            "seguimiento", "avisar", "no servir", "capacitar",
        ],
        "puntos": 8,
        "comodin_no_gerencial": "Recuerda: son 3 acciones clave que debe tomar tu equipo.",
    },
    # ── P18
    {
        "id": 18,
        "texto": "¿Cuál es el procedimiento si un cliente se niega a salir del establecimiento después de que le negaste el servicio?",
        "tipo": "open",
        "respuestas_validas": [
            "llamar al gerente", "seguridad", "policía", "autoridades",
            "no confrontar", "mantener la calma", "pedir ayuda",
            "no escalar solo", "avisar", "gerente",
        ],
        "puntos": 5,
        "comodin": "Mantén la calma, no confrontes al cliente directamente. Llama al gerente o a seguridad. Si es necesario, contacta a las autoridades.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def generar_codigo() -> str:
    """Genera código de 3 dígitos único por sesión."""
    return str(random.randint(100, 999))

def generar_uuid() -> str:
    return str(uuid.uuid4())

def device_hash() -> str:
    """Fingerprint ligero basado en timestamp + uuid."""
    raw = f"{time.time()}-{uuid.uuid4()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]

def similarity_score(respuesta: str, validas: list) -> float:
    """Calcula similitud entre respuesta del usuario y lista de respuestas válidas."""
    resp = respuesta.strip().lower()
    best = 0.0
    for v in validas:
        v_lower = v.lower()
        # Contiene directamente
        if v_lower in resp or resp in v_lower:
            return 1.0
        if HAS_RAPIDFUZZ:
            score = fuzz.partial_ratio(resp, v_lower) / 100
        else:
            score = difflib.SequenceMatcher(None, resp, v_lower).ratio()
        best = max(best, score)
    return best

def respuesta_abierta_correcta(respuesta: str, validas: list, umbral=0.45) -> bool:
    """Retorna True si la respuesta libre supera el umbral de similitud."""
    if not respuesta or len(respuesta.strip()) < 3:
        return False
    return similarity_score(respuesta, validas) >= umbral

def mezclar_preguntas(preguntas: list) -> list:
    """
    Mezcla aleatoriamente las preguntas con EXCEPCIÓN:
    P16 y P17 siempre al final.
    """
    fijas_final = [p for p in preguntas if p["id"] in (16, 17)]
    mezclables  = [p for p in preguntas if p["id"] not in (16, 17)]
    random.shuffle(mezclables)
    # P16 antes de P17
    fijas_final.sort(key=lambda p: p["id"])
    return mezclables + fijas_final

def puntos_totales_posibles(preguntas: list, bonus=False) -> int:
    total = sum(p["puntos"] for p in preguntas if not p.get("bonus"))
    if bonus:
        total += sum(p["puntos"] for p in preguntas if p.get("bonus"))
    return total

# ─────────────────────────────────────────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────────────────────────────────────────

def guardar_en_sheets(datos: dict):
    """Guarda resultados en Google Sheets vía service account."""
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
        sh    = gc.open_by_key(sheet_id)
        ws    = sh.sheet1
        # Encabezados si es la primera fila
        if ws.row_count < 2 or not ws.row_values(1):
            ws.append_row([
                "Nombre", "Rol", "Código", "Score", "%",
                "Fecha", "Hora", "Navegador", "UUID",
                "Respuestas"
            ])
        row = [
            datos.get("nombre", ""),
            datos.get("rol", ""),
            datos.get("codigo", ""),
            datos.get("score", 0),
            datos.get("porcentaje", "0%"),
            datos.get("fecha", ""),
            datos.get("hora", ""),
            datos.get("navegador", ""),
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
        "pantalla": "intro",        # intro | rol | quiz | resultado
        "nombre": "",
        "rol": "",
        "codigo": generar_codigo(),
        "uuid": generar_uuid(),
        "device": device_hash(),
        "timestamp": datetime.now().isoformat(),
        "preguntas_orden": [],      # lista mezclada de preguntas
        "idx_actual": 0,            # índice de pregunta actual
        "puntaje": 0,
        "bonus_suma": 0,
        "respuestas": {},           # {id_pregunta: {"respuesta": ..., "correcto": ...}}
        "feedback_mostrado": False,
        "comodin_usado": False,
        "chips_seleccionados": [],  # para preguntas multi
        "drag_orden": [],           # para drag & drop
        "fill_respuestas": {},      # para fill
        "open_list_items": [],      # para open_list
        "guardado": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────────────────────────────────────
#  UI HELPER COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def mostrar_top_bar():
    st.markdown("""
    <div class="top-bar">
      <div>
        <div class="logo">☕</div>
      </div>
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
    total = len(st.session_state.preguntas_orden)
    actual = st.session_state.idx_actual
    pct = int((actual / total) * 100) if total else 0
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
#  PANTALLA: INTRO
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
            st.session_state.nombre = nombre.strip()
            st.session_state.pantalla = "rol"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  PANTALLA: SELECCIÓN DE ROL
# ─────────────────────────────────────────────────────────────────────────────

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

    rol = st.radio(
        "Selecciona tu rol:",
        ["Partner", "Gerencial"],
        key="radio_rol",
        horizontal=True,
    )

    if st.button("Continuar →", key="btn_rol"):
        st.session_state.rol = rol
        # Mezclar preguntas y guardar orden
        st.session_state.preguntas_orden = mezclar_preguntas(PREGUNTAS)
        st.session_state.idx_actual = 0
        st.session_state.pantalla = "quiz"
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  EVALUACIÓN POR TIPO DE PREGUNTA
# ─────────────────────────────────────────────────────────────────────────────

def evaluar_respuesta(pregunta: dict, respuesta) -> tuple[bool, int]:
    """
    Retorna (correcto: bool, puntos_ganados: int).
    respuesta puede ser str, list, dict según tipo.
    """
    tipo = pregunta["tipo"]
    pts  = pregunta["puntos"]

    if tipo == "radio":
        correcto = respuesta == pregunta["correcta"]
        return correcto, pts if correcto else 0

    elif tipo == "multi":
        seleccion = set(respuesta) if respuesta else set()
        correctas = set(pregunta["correctas"])
        # Puntuación parcial: proporcional a aciertos
        aciertos = len(seleccion & correctas)
        errores  = len(seleccion - correctas)
        total_c  = len(correctas)
        parcial  = max(0, aciertos - errores)
        puntos_parciales = round((parcial / total_c) * pts)
        correcto = seleccion == correctas
        return correcto, puntos_parciales

    elif tipo == "open":
        correcto = respuesta_abierta_correcta(str(respuesta), pregunta["respuestas_validas"])
        return correcto, pts if correcto else 0

    elif tipo == "drag":
        correcto = list(respuesta) == pregunta["items_ordenados"]
        return correcto, pts if correcto else 0

    elif tipo == "fill":
        campos  = pregunta["campos"]
        aciertos = 0
        for campo in campos:
            val = str(respuesta.get(campo["clave"], "")).strip().lower()
            correcta_lower = campo["correcta"].lower()
            alternativas   = [a.lower() for a in campo.get("alternativas", [])]
            if val == correcta_lower or val in alternativas or respuesta_abierta_correcta(val, [correcta_lower] + alternativas):
                aciertos += 1
        correcto = aciertos == len(campos)
        pts_parciales = round((aciertos / len(campos)) * pts)
        return correcto, pts_parciales

    elif tipo == "open_list":
        # Evalúa lista de respuestas libres
        items = [str(r).strip() for r in (respuesta if respuesta else []) if str(r).strip()]
        aciertos = sum(1 for r in items if respuesta_abierta_correcta(r, pregunta["respuestas_validas"]))
        num_req  = (pregunta["num_respuestas_gerencial"]
                    if st.session_state.rol == "Gerencial"
                    else pregunta["num_respuestas_no_gerencial"])
        correcto = aciertos >= num_req
        pts_parciales = round((min(aciertos, num_req) / num_req) * pts)
        return correcto, pts_parciales

    return False, 0

# ─────────────────────────────────────────────────────────────────────────────
#  RENDERIZADO DE CADA TIPO DE PREGUNTA
# ─────────────────────────────────────────────────────────────────────────────

def render_radio(pregunta: dict, key_prefix: str):
    opciones = pregunta["opciones"][:]
    random.shuffle(opciones)   # orden aleatorio visual
    return st.radio("Selecciona tu respuesta:", opciones, key=f"{key_prefix}_radio", index=None)

def render_multi(pregunta: dict, key_prefix: str):
    """Chips clickeables con session_state."""
    st.markdown("**Selecciona todas las que apliquen:**")

    opciones = pregunta["opciones"][:]
    random.shuffle(opciones)  # solo para primera renderización

    if f"{key_prefix}_opciones_orden" not in st.session_state:
        st.session_state[f"{key_prefix}_opciones_orden"] = opciones

    opciones_orden = st.session_state[f"{key_prefix}_opciones_orden"]
    seleccionados  = st.session_state.chips_seleccionados

    cols_per_row = 2
    for i in range(0, len(opciones_orden), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(opciones_orden):
                opcion = opciones_orden[i + j]
                selected = opcion in seleccionados
                label = f"✓ {opcion}" if selected else opcion
                if col.button(label, key=f"{key_prefix}_chip_{i+j}",
                               use_container_width=True):
                    if opcion in st.session_state.chips_seleccionados:
                        st.session_state.chips_seleccionados.remove(opcion)
                    else:
                        st.session_state.chips_seleccionados.append(opcion)
                    st.rerun()

    if seleccionados:
        st.caption(f"Seleccionados: {', '.join(seleccionados)}")
    return seleccionados

def render_open(pregunta: dict, key_prefix: str):
    return st.text_area("Tu respuesta:", key=f"{key_prefix}_open", height=90,
                        placeholder="Escribe tu respuesta aquí…")

def render_drag(pregunta: dict, key_prefix: str):
    """Simulación de drag & drop mediante selectboxes de posición."""
    st.markdown("**Ordena los pasos (1 = primero, 6 = último):**")

    items = pregunta["items_ordenados"][:]

    if f"{key_prefix}_drag_init" not in st.session_state:
        shuffled = items[:]
        random.shuffle(shuffled)
        st.session_state[f"{key_prefix}_drag_init"] = shuffled
        st.session_state.drag_orden = shuffled[:]

    orden_actual = st.session_state.drag_orden
    if not orden_actual:
        orden_actual = st.session_state[f"{key_prefix}_drag_init"][:]
        st.session_state.drag_orden = orden_actual[:]

    st.markdown("**Arrastra (usa los botones ▲ ▼ para reordenar):**")
    for i, item in enumerate(orden_actual):
        cols = st.columns([6, 1, 1])
        cols[0].markdown(f"<div class='drag-item'>{i+1}. {item}</div>", unsafe_allow_html=True)
        if i > 0 and cols[1].button("▲", key=f"{key_prefix}_up_{i}"):
            orden_actual[i], orden_actual[i-1] = orden_actual[i-1], orden_actual[i]
            st.session_state.drag_orden = orden_actual[:]
            st.rerun()
        if i < len(orden_actual)-1 and cols[2].button("▼", key=f"{key_prefix}_dn_{i}"):
            orden_actual[i], orden_actual[i+1] = orden_actual[i+1], orden_actual[i]
            st.session_state.drag_orden = orden_actual[:]
            st.rerun()

    return st.session_state.drag_orden

def render_fill(pregunta: dict, key_prefix: str):
    """Campos rellenables inline."""
    st.markdown(f"**{pregunta['template']}**")
    respuestas = {}
    for campo in pregunta["campos"]:
        val = st.text_input(
            campo["label"],
            key=f"{key_prefix}_fill_{campo['clave']}",
            placeholder=f"Completa: {campo['label']}…",
        )
        respuestas[campo["clave"]] = val
    return respuestas

def render_open_list(pregunta: dict, key_prefix: str):
    """Múltiples campos de texto para lista de acciones."""
    rol = st.session_state.rol
    num = (pregunta["num_respuestas_gerencial"]
           if rol == "Gerencial"
           else pregunta["num_respuestas_no_gerencial"])

    st.markdown(f"**Escribe {num} acciones:**")
    respuestas = []
    for i in range(num):
        val = st.text_input(f"Acción {i+1}:", key=f"{key_prefix}_ol_{i}",
                            placeholder=f"Acción {i+1}…")
        respuestas.append(val)
    return respuestas

# ─────────────────────────────────────────────────────────────────────────────
#  PANTALLA: QUIZ
# ─────────────────────────────────────────────────────────────────────────────

def pantalla_quiz():
    mostrar_top_bar()
    mostrar_codigo()
    mostrar_progreso()

    preguntas = st.session_state.preguntas_orden
    idx       = st.session_state.idx_actual

    # ── Fin del quiz
    if idx >= len(preguntas):
        st.session_state.pantalla = "resultado"
        st.rerun()
        return

    pregunta   = preguntas[idx]
    q_id       = pregunta["id"]
    tipo       = pregunta["tipo"]
    key_prefix = f"q{q_id}"

    # ── Card de pregunta
    st.markdown(f"""
    <div class="quiz-card">
      <div class="q-number">Pregunta {idx + 1} / {len(preguntas)}</div>
      <div class="q-text">{pregunta["texto"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Comodín (P8, P9, P18, P17 no-gerencial)
    tiene_comodin = bool(pregunta.get("comodin") or
                         (tipo == "open_list" and pregunta.get("comodin_no_gerencial") and
                          st.session_state.rol != "Gerencial"))

    if tiene_comodin:
        if not st.session_state.comodin_usado:
            if st.button("💡 Usar ayuda (comodín)", key=f"{key_prefix}_comodin"):
                st.session_state.comodin_usado = True
                st.rerun()
        else:
            texto_comodin = (pregunta.get("comodin") or
                             pregunta.get("comodin_no_gerencial", ""))
            st.markdown(f"""
            <div class="comodin-box">
              💡 <strong>Ayuda:</strong> {texto_comodin}
            </div>
            """, unsafe_allow_html=True)

    # ── Renderizar según tipo
    respuesta = None
    if tipo == "radio":
        respuesta = render_radio(pregunta, key_prefix)
    elif tipo == "multi":
        respuesta = render_multi(pregunta, key_prefix)
    elif tipo == "open":
        respuesta = render_open(pregunta, key_prefix)
    elif tipo == "drag":
        respuesta = render_drag(pregunta, key_prefix)
    elif tipo == "fill":
        respuesta = render_fill(pregunta, key_prefix)
    elif tipo == "open_list":
        respuesta = render_open_list(pregunta, key_prefix)

    # ── Botón Siguiente
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        siguiente_label = "Finalizar ✓" if idx == len(preguntas) - 1 else "Siguiente →"
        if st.button(siguiente_label, key=f"{key_prefix}_next", use_container_width=True):
            # Evaluar
            correcto, pts_ganados = evaluar_respuesta(pregunta, respuesta)

            # Guardar respuesta
            st.session_state.respuestas[q_id] = {
                "respuesta": str(respuesta),
                "correcto": correcto,
                "pts": pts_ganados,
            }

            # Sumar puntaje (bonus con tope)
            if pregunta.get("bonus"):
                st.session_state.bonus_suma += pts_ganados
            else:
                st.session_state.puntaje += pts_ganados

            # Avanzar
            st.session_state.idx_actual += 1
            st.session_state.comodin_usado = False
            st.session_state.chips_seleccionados = []
            st.session_state.drag_orden = []
            # Limpiar opciones guardadas de chips
            for k in list(st.session_state.keys()):
                if k.startswith(f"q{q_id}_") and k.endswith("_opciones_orden"):
                    del st.session_state[k]
                if k.startswith(f"q{q_id}_") and k.endswith("_drag_init"):
                    del st.session_state[k]

            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  PANTALLA: RESULTADO
# ─────────────────────────────────────────────────────────────────────────────

def pantalla_resultado():
    mostrar_top_bar()

    # ── Calcular score final (tope 100)
    score_base  = st.session_state.puntaje
    score_bonus = st.session_state.bonus_suma
    score_final = min(100, score_base + score_bonus)
    pct         = score_final

    # ── Mensaje previo
    st.markdown("""
    <div class="quiz-card" style="text-align:center; border: 2px solid #CBA135;">
      <div style="font-size:1.5rem;">🧴</div>
      <div style="font-size:1.05rem; font-weight:600; margin:.4rem 0;">Falta ver tu lavado de manos.</div>
      <div style="color:#6B6B6B;">Eso será calificado en tienda.</div>
      <div style="font-size:1.2rem; margin-top:.5rem;">¡Suerte! 🍀</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Confetti emoji
    if score_final >= 70:
        st.markdown('<div class="confetti-msg">🎉🎊✨🎉🎊</div>', unsafe_allow_html=True)

    # ── Mensaje según score
    if score_final == 100:
        msg = "🏆 Excelente estimado, ganaste un abrazo de tu líder RSA. ¡Canjéalo cuando quieras!"
        color = "#00704A"
    elif score_final >= 90:
        msg = "⭐ Excelente resultado. ¡Dominas el RSA!"
        color = "#00704A"
    elif score_final >= 70:
        msg = "👍 Buen trabajo. Sigue reforzando tus conocimientos."
        color = "#CBA135"
    elif score_final >= 50:
        msg = "📚 Debes reforzar algunos conceptos RSA."
        color = "#D4783A"
    else:
        msg = "⚠️ Urgente reforzar conocimientos RSA. ¡Pide apoyo a tu líder!"
        color = "#c0392b"

    # ── Score card principal
    st.markdown(f"""
    <div class="score-card">
      <div class="big-score">{score_final}</div>
      <div class="score-pct">{pct}% de 100 puntos</div>
      <div class="score-msg">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Breakdown
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Detalle de tu evaluación")

    for p in st.session_state.preguntas_orden:
        reg = st.session_state.respuestas.get(p["id"], {})
        correcto   = reg.get("correcto", False)
        pts_ganados = reg.get("pts", 0)
        icono = "✅" if correcto else "❌"
        st.markdown(f"""
        <div class="breakdown-row">
          <span>{icono} P{p['id']}: {p['texto'][:55]}…</span>
          <span class="breakdown-pts">{pts_ganados}/{p['puntos']}</span>
        </div>
        """, unsafe_allow_html=True)

    if score_bonus:
        st.markdown(f"""
        <div class="breakdown-row" style="border-top:2px solid #CBA135; margin-top:.5rem; padding-top:.5rem;">
          <span>⭐ Bonus</span>
          <span class="breakdown-pts">+{score_bonus}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Captura
    st.markdown("""
    <div style="text-align:center; margin:1rem 0; font-size:1rem; font-weight:600; color:#00704A;">
      📸 Sácale captura a tu resultado
    </div>
    """, unsafe_allow_html=True)

    mostrar_codigo()

    # ── Guardar en Sheets (una sola vez)
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
            "navegador":  st.session_state.get("_browser", "N/A"),
            "uuid":       st.session_state.uuid,
            "respuestas": st.session_state.respuestas,
        }
        guardado_ok = guardar_en_sheets(datos)
        st.session_state.guardado = True
        if guardado_ok:
            st.success("✅ Resultados registrados correctamente.")

    # ── Botón reiniciar (nuevo intento)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Volver a intentar", key="btn_reiniciar"):
        # Limpiar todo menos defaults
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER PRINCIPAL
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

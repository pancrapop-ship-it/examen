"""
RSA Quiz Interactivo - Starbucks
Quiz de inocuidad alimentaria para 14 colaboradores.
"""

import streamlit as st
import random
import uuid
import hashlib
import json
import datetime
import platform
from difflib import SequenceMatcher

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(
    page_title="RSA Quiz | Starbucks",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS Premium ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

:root {
    --green-dark:   #00704A;
    --green-mid:    #1E3932;
    --green-light:  #D4E9E2;
    --gold:         #CBA258;
    --copper:       #C47B37;
    --amber:        #F5A623;
    --cream:        #FAF7F2;
    --white:        #FFFFFF;
    --text-dark:    #1E3932;
    --text-mid:     #3D5A52;
    --text-light:   #6B8F85;
    --card-bg:      rgba(255,255,255,0.72);
    --glass:        rgba(255,255,255,0.55);
    --shadow:       0 8px 32px rgba(30,57,50,0.13);
    --radius:       18px;
    --radius-sm:    10px;
}

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f5ef 0%, #f5efe6 50%, #fdf8f0 100%) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-dark) !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}

[data-testid="stHeader"] { background: transparent !important; }

/* Ocultar menú hamburguesa y pie */
#MainMenu, footer, header { visibility: hidden; }

/* ── Tarjeta principal ── */
.quiz-card {
    background: var(--card-bg);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1.5px solid rgba(203,162,88,0.22);
    border-radius: var(--radius);
    padding: 2.2rem 2.4rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.4rem;
    animation: fadeUp 0.45s ease both;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Encabezado logo-like ── */
.app-header {
    text-align: center;
    padding: 2rem 0 1.2rem;
}
.app-header .logo-ring {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--green-dark), var(--green-mid));
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 2rem;
    box-shadow: 0 4px 20px rgba(0,112,74,0.3);
    margin-bottom: 0.7rem;
}
.app-header h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--green-mid) !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}
.app-header p {
    color: var(--text-mid) !important;
    font-size: 1rem !important;
    margin: 0.3rem 0 0 !important;
}

/* ── Código de validación ── */
.validation-badge {
    background: linear-gradient(135deg, var(--green-mid), var(--green-dark));
    color: white !important;
    border-radius: 14px;
    padding: 0.9rem 1.4rem;
    text-align: center;
    margin-bottom: 1.2rem;
    border: 1.5px solid var(--gold);
    box-shadow: 0 4px 16px rgba(0,112,74,0.22);
}
.validation-badge .code-number {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: var(--amber) !important;
    display: block;
    line-height: 1.1;
    text-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.validation-badge .code-label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.85;
    margin-top: 0.2rem;
    display: block;
}

/* ── Barra de progreso ── */
.progress-wrap {
    background: var(--green-light);
    border-radius: 99px;
    height: 8px;
    margin-bottom: 1.4rem;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--green-dark), var(--amber));
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
}

/* ── Número de pregunta ── */
.q-meta {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.9rem;
}
.q-num {
    background: var(--green-dark);
    color: white !important;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    padding: 0.28rem 0.75rem;
    border-radius: 99px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.q-type {
    color: var(--copper);
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}

/* ── Texto de pregunta ── */
.q-text {
    font-family: 'Syne', sans-serif;
    font-size: 1.18rem;
    font-weight: 700;
    color: var(--text-dark) !important;
    line-height: 1.45;
    margin-bottom: 1.3rem;
}

/* ── Chips (lluvia de cuadros) ── */
.chips-area {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-bottom: 1.1rem;
}
.chip {
    background: var(--green-light);
    color: var(--green-mid) !important;
    border: 2px solid transparent;
    border-radius: 99px;
    padding: 0.45rem 1.1rem;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.22s ease;
    user-select: none;
}
.chip:hover { border-color: var(--green-dark); background: #c5e0d6; }
.chip.selected {
    background: var(--green-dark);
    color: white !important;
    border-color: var(--green-dark);
    box-shadow: 0 2px 12px rgba(0,112,74,0.25);
}

/* ── Comodín/Ayuda ── */
.joker-box {
    background: linear-gradient(135deg, rgba(245,166,35,0.12), rgba(196,123,55,0.1));
    border: 1.5px solid var(--amber);
    border-radius: var(--radius-sm);
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: var(--text-dark) !important;
    animation: fadeUp 0.3s ease;
}
.joker-box strong { color: var(--copper) !important; }

/* ── Botones principales ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 99px !important;
    padding: 0.65rem 2rem !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.22s ease !important;
    border: none !important;
}

/* Botón primario (verde) */
div[data-testid="stButton"]:not(.btn-secondary) > button {
    background: linear-gradient(135deg, var(--green-dark), #005c3b) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(0,112,74,0.28) !important;
}
div[data-testid="stButton"]:not(.btn-secondary) > button:hover {
    box-shadow: 0 6px 24px rgba(0,112,74,0.38) !important;
    transform: translateY(-2px) !important;
}

/* ── Radio y checkboxes ── */
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label {
    font-size: 0.95rem !important;
    color: var(--text-dark) !important;
}

/* ── Text inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid rgba(30,57,50,0.2) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    background: rgba(255,255,255,0.8) !important;
    color: var(--text-dark) !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--green-dark) !important;
    box-shadow: 0 0 0 3px rgba(0,112,74,0.1) !important;
}

/* ── Score final ── */
.score-big {
    text-align: center;
    padding: 2rem 1.5rem;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.score-label {
    font-size: 1.05rem;
    color: var(--text-mid) !important;
    margin-bottom: 1.2rem;
}
.score-msg {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    padding: 0.9rem 1.5rem;
    border-radius: var(--radius-sm);
    display: inline-block;
    margin-bottom: 1rem;
}

.breakdown-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(30,57,50,0.08);
    font-size: 0.88rem;
    color: var(--text-mid) !important;
}
.breakdown-row .pts {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--green-dark) !important;
}

/* ── Alert / feedback ── */
.feedback-correct {
    background: rgba(0,112,74,0.1);
    border-left: 4px solid var(--green-dark);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.7rem 1rem;
    font-size: 0.88rem;
    margin-top: 0.5rem;
    color: var(--green-dark) !important;
}
.feedback-wrong {
    background: rgba(196,123,55,0.1);
    border-left: 4px solid var(--copper);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.7rem 1rem;
    font-size: 0.88rem;
    margin-top: 0.5rem;
    color: var(--copper) !important;
}

/* ── Confetti canvas ── */
#confetti-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 9999;
}

/* ── Drag & drop order list ── */
.order-item {
    background: var(--card-bg);
    border: 1.5px solid rgba(30,57,50,0.15);
    border-radius: var(--radius-sm);
    padding: 0.7rem 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 0.93rem;
    font-weight: 500;
    cursor: grab;
}
.order-handle {
    color: var(--text-light);
    font-size: 1.1rem;
}

/* ── Aviso handwash ── */
.handwash-notice {
    background: linear-gradient(135deg, var(--green-mid), var(--green-dark));
    color: white !important;
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    text-align: center;
    margin-bottom: 1.2rem;
}
.handwash-notice h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: var(--amber) !important;
    margin-bottom: 0.5rem !important;
}
.handwash-notice p {
    font-size: 1rem !important;
    opacity: 0.92 !important;
    color: white !important;
}

/* ── Responsive ── */
@media (max-width: 600px) {
    .quiz-card { padding: 1.4rem 1.2rem; }
    .app-header h1 { font-size: 1.5rem !important; }
    .score-number { font-size: 3.5rem; }
}
</style>
""", unsafe_allow_html=True)

# ─── Utilidades ──────────────────────────────────────────────────────────────

def similarity(a: str, b: str) -> float:
    """Similitud entre dos cadenas (0–1)."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def flexible_match(response: str, keywords: list, threshold: float = 0.55) -> bool:
    """Verdadero si la respuesta contiene al menos uno de los keywords con similitud suficiente."""
    resp = response.lower().strip()
    for kw in keywords:
        kw_l = kw.lower()
        if kw_l in resp:
            return True
        words = resp.split()
        for w in words:
            if similarity(w, kw_l) >= threshold:
                return True
    return False

def count_keywords(response: str, keywords: list, threshold: float = 0.55) -> int:
    """Cuenta cuántos keywords distintos aparecen en la respuesta."""
    found = 0
    resp = response.lower()
    for kw in keywords:
        kw_l = kw.lower()
        if kw_l in resp:
            found += 1
        else:
            for w in resp.split():
                if similarity(w, kw_l) >= threshold:
                    found += 1
                    break
    return found

def generate_code() -> str:
    """Genera código de 3 dígitos único."""
    return str(random.randint(100, 999))

def header_html():
    st.markdown("""
    <div class="app-header">
        <div class="logo-ring">☕</div>
        <h1>RSA Quiz</h1>
        <p>Inocuidad Alimentaria · Starbucks</p>
    </div>
    """, unsafe_allow_html=True)

def validation_badge():
    code = st.session_state.get("unique_code", "---")
    st.markdown(f"""
    <div class="validation-badge">
        <span class="code-number">{code}</span>
        <span class="code-label">Código de validación único · No compartas capturas</span>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(current: int, total: int):
    pct = int((current / total) * 100)
    st.markdown(f"""
    <div class="progress-wrap">
        <div class="progress-fill" style="width:{pct}%"></div>
    </div>
    <p style="text-align:right;font-size:0.78rem;color:var(--text-light);margin-top:-0.8rem;margin-bottom:0.6rem;">
        Pregunta {current} de {total}
    </p>
    """, unsafe_allow_html=True)

# ─── Definición de preguntas ──────────────────────────────────────────────────
# Cada pregunta es un dict con: id, type, text, points, y datos específicos.

QUESTIONS_POOL = [
    # ── P1 ──────────────────────────────────────────────────────────────────
    {
        "id": 1,
        "type": "multiple_choice",
        "text": "Menciona los rangos de temperatura de refrigeradores.",
        "options": ["1 a 4°C", "1 a 3°C", "2 a 4°C", "3 a 6°C"],
        "correct": "1 a 4°C",
        "points": 5,
    },
    # ── P2 ──────────────────────────────────────────────────────────────────
    {
        "id": 2,
        "type": "true_false",
        "text": "¿La concentración de sanitizante que maneja Starbucks es de 100–200 ppm?",
        "correct": "Verdadero",
        "points": 5,
    },
    # ── P3 ──────────────────────────────────────────────────────────────────
    {
        "id": 3,
        "type": "chips_select",
        "text": "¿Qué tipo de riesgos de contaminación existen en alimentos y bebidas?",
        "instruction": "Selecciona exactamente 3 correctas.",
        "correct": ["Física", "Química", "Microbiológica"],
        "distractors": ["Astronomía", "Botánica", "Anatomía", "Zoología", "Genética", "Ecología"],
        "select_count": 3,
        "points": 6,
    },
    # ── P4 ──────────────────────────────────────────────────────────────────
    {
        "id": 4,
        "type": "chips_select",
        "text": "Menciona algún tipo de contaminación física dentro de la tienda.",
        "instruction": "Selecciona todas las correctas.",
        "correct": ["Polvo", "Cabellos", "Residuos de piedra de horno", "Acrílicos rotos"],
        "distractors": ["Uñas", "Plástico roto", "Vapor", "Humo", "Residuos líquidos"],
        "select_count": 4,
        "points": 6,
    },
    # ── P5 ──────────────────────────────────────────────────────────────────
    {
        "id": 5,
        "type": "open",
        "text": "Menciona un tipo de contaminación química.",
        "keywords": ["químicos no autorizados", "químicos", "guardar producto", "producto cerca", "autorizado", "quimico"],
        "points": 5,
    },
    # ── P6 ──────────────────────────────────────────────────────────────────
    {
        "id": 6,
        "type": "fill_blank",
        "text": "Descomposición del alimento y desarrollo ________",
        "keywords": ["microorganismos", "microorganismo", "bacterias", "bacteria"],
        "points": 5,
    },
    # ── P7 ──────────────────────────────────────────────────────────────────
    {
        "id": 7,
        "type": "open",
        "text": "¿Qué es un riesgo de inocuidad de alimentos?",
        "keywords": ["contaminación", "física", "química", "biológica", "riesgo", "consumidor", "vida", "ponga en riesgo"],
        "points": 5,
    },
    # ── P8 ──────────────────────────────────────────────────────────────────
    {
        "id": 8,
        "type": "open_joker",
        "text": "¿Cuál es la manera correcta de lavarse las manos?",
        "joker": "Utilizar la estación específica de lavado de manos, emplear agua corriente a temperatura mínima de 35°C…",
        "joker_label": "Comodín",
        "keywords": ["frotar", "jabón", "20 segundos", "codos", "uñas", "secar", "toalla", "agua", "lavado"],
        "points": 6,
    },
    # ── P9 ──────────────────────────────────────────────────────────────────
    {
        "id": 9,
        "type": "open_joker",
        "text": "¿Cuál es el documento de control de temperaturas dentro de tu tienda?",
        "joker": "En español sería: sección de control de temperaturas.",
        "joker_label": "Ayuda",
        "keywords": ["duty roaster", "duty roster", "duty", "roaster"],
        "points": 5,
    },
    # ── P10 ─────────────────────────────────────────────────────────────────
    {
        "id": 10,
        "type": "open_bonus",
        "text": "¿Cuáles son los 3 puntos fundamentales para mantener la tienda fuera del riesgo de plagas?",
        "base_keywords": ["orden", "limpieza", "defectos estructurales", "fumigación", "mensual"],
        "bonus_keywords": ["BOH", "basura", "drenaje", "grietas", "hoyos", "tapar"],
        "points": 7,
        "bonus_points": 2,
    },
    # ── P11 ─────────────────────────────────────────────────────────────────
    {
        "id": 11,
        "type": "order",
        "text": "Explique los procedimientos para lavado de utensilios.",
        "items": ["Lavar", "Enjuagar", "Sanitizar", "Secar al aire"],
        "correct_order": ["Lavar", "Enjuagar", "Sanitizar", "Secar al aire"],
        "points": 6,
    },
    # ── P12 ─────────────────────────────────────────────────────────────────
    {
        "id": 12,
        "type": "fill_blank",
        "text": "Los utensilios deben lavarse cada ____ horas.",
        "keywords": ["2", "dos"],
        "points": 4,
    },
    # ── P13 ─────────────────────────────────────────────────────────────────
    {
        "id": 13,
        "type": "chips_select",
        "text": "¿Cuáles son los utensilios que deben ser lavados, enjuagados y desinfectados cada 2 horas?",
        "instruction": "Selecciona todos los correctos.",
        "correct": ["Jarras de vaporización", "Termómetros", "Cucharas", "Jarras/tapas blender", "Palas hielo", "Pinzas", "Cuchillos"],
        "distractors": ["Bandejas", "Servilletas", "Vasos", "Cucharones"],
        "select_count": 7,
        "points": 7,
    },
    # ── P14 ─────────────────────────────────────────────────────────────────
    {
        "id": 14,
        "type": "multiple_choice",
        "text": "¿Cuál es la temperatura de enjuague que debe alcanzar la sanitizadora?",
        "options": ["170°F", "185°F", "190°F", "180°F", "200°F"],
        "correct": "180°F",
        "points": 5,
    },
    # ── P15 ─────────────────────────────────────────────────────────────────
    {
        "id": 15,
        "type": "fill_multiple",
        "text": "¿Cuáles son los síntomas de enfermedad que excluirían a una persona de venir a trabajar?",
        "given": ["Diarrea", "Vómito"],
        "blanks": 3,
        "blank_keywords": [
            ["fiebre", "temperatura"],
            ["ictericia", "amarilla", "amarillo", "ictericia"],
            ["lesión", "lesion", "herida", "expuesta", "cortada"],
        ],
        "points": 7,
    },
    # ── P16 (SIEMPRE AL FINAL - posición -2) ────────────────────────────────
    {
        "id": 16,
        "type": "open_joker",
        "text": "¿Cuáles son las dos acciones que se deben tomar si una persona informa que ha sido diagnosticada con una enfermedad y tiene todos los síntomas?",
        "joker": "Tranquila/o, tú puedes. Piénsalo con calma.",
        "joker_label": "Pista",
        "hint_prefix": "S______________ y S______________",
        "keywords": ["excluye", "excluir", "retira", "turno", "reporta", "reportar", "gerente", "zona"],
        "points": 8,
    },
    # ── P17 (SIEMPRE AL FINAL - posición -1, adaptativa por rol) ────────────
    {
        "id": 17,
        "type": "open_role",
        "text": "¿PROPORCIONE SUS PROCEDIMIENTOS ESCRITOS INDICANDO QUÉ HACER EN CASO DE DIARREA/VÓMITO? (RIESGO BIOLÓGICO)",
        "keywords_gerencial": ["procedimientos escritos", "digitales", "impresos", "mostrador", "visita", "cercar", "EPPs", "bolsa roja", "riesgo biológico", "tacho"],
        "keywords_base": ["cercar", "zona", "EPPs", "equipos de proteccion", "bolsa roja", "riesgo biológico", "tacho", "desechar"],
        "joker_non_gerencial": "Son 3 acciones.",
        "points": 10,
    },
    # ── P18 ─────────────────────────────────────────────────────────────────
    {
        "id": 18,
        "type": "open_joker",
        "text": "¿Cuál es el procedimiento si identificas una condición insegura en la tienda?",
        "joker": "Son 3 acciones.",
        "joker_label": "Comodín",
        "keywords": ["OT", "orden de trabajo", "gerente zonal", "gerente", "correo", "área correspondiente", "avisar", "generar"],
        "points": 8,
    },
]

# Puntos que faltan para llegar a 100 si hay bonus → sumamos correctamente
TOTAL_POINTS = sum(q.get("points", 0) for q in QUESTIONS_POOL)  # base

def build_question_order(role: str) -> list:
    """
    Orden de preguntas:
    - P16 y P17 siempre al final (en ese orden).
    - El resto (1–15 + 18) mezclado aleatoriamente.
    """
    fixed_end = [16, 17]
    pool_ids = [q["id"] for q in QUESTIONS_POOL if q["id"] not in fixed_end]
    random.shuffle(pool_ids)
    return pool_ids + fixed_end

def get_question(qid: int) -> dict:
    for q in QUESTIONS_POOL:
        if q["id"] == qid:
            return q
    return {}

# ─── Guardar en Google Sheets ─────────────────────────────────────────────────
def save_to_sheets(data: dict):
    """
    Guarda resultados en Google Sheets vía service account.
    Requiere secrets: gcp_service_account y spreadsheet_id configurados en Streamlit Cloud.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = st.secrets.get("gcp_service_account", None)
        spreadsheet_id = st.secrets.get("spreadsheet_id", None)

        if not creds_dict or not spreadsheet_id:
            return  # No configurado → silencioso

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(dict(creds_dict), scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id).sheet1

        # Encabezados si hoja vacía
        if sheet.row_count < 1 or not sheet.row_values(1):
            sheet.append_row([
                "Nombre", "Rol", "Código", "Score", "%", "Fecha", "Hora",
                "Navegador", "UUID", "Respuestas"
            ])

        sheet.append_row([
            data.get("nombre", ""),
            data.get("rol", ""),
            data.get("codigo", ""),
            data.get("score", 0),
            data.get("porcentaje", 0),
            data.get("fecha", ""),
            data.get("hora", ""),
            data.get("browser", ""),
            data.get("uuid", ""),
            json.dumps(data.get("respuestas", {}), ensure_ascii=False),
        ])
    except Exception:
        pass  # Falla silenciosa si no está configurado

# ─── Init session state ───────────────────────────────────────────────────────
def init_state():
    defaults = {
        "stage": "intro",           # intro | role | quiz | handwash | result
        "nombre": "",
        "rol": "",
        "unique_code": generate_code(),
        "session_uuid": str(uuid.uuid4()),
        "q_order": [],
        "q_index": 0,
        "scores": {},               # {qid: points_earned}
        "answers": {},              # {qid: answer_text}
        "joker_used": {},           # {qid: bool}
        "chip_selections": {},      # {qid: [selected]}
        "order_state": {},          # {qid: [current_order]}
        "started_at": datetime.datetime.now().isoformat(),
        "saved": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── PANTALLA: INTRO ─────────────────────────────────────────────────────────
def screen_intro():
    header_html()

    st.markdown("""
    <div class="quiz-card" style="text-align:center;padding-top:2.5rem;padding-bottom:2.5rem;">
        <p style="font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;color:var(--green-mid);margin-bottom:0.5rem;">
            Hola compañero, hacemos esto por tu bien ☀️
        </p>
        <p style="color:var(--text-mid);font-size:0.97rem;">
            Completa el quiz de inocuidad y demuestra tu conocimiento RSA.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        nombre = st.text_input("Déjanos tu nombre", placeholder="Tu nombre completo…", key="input_nombre")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅  Continuar", use_container_width=True):
            if nombre.strip():
                st.session_state.nombre = nombre.strip()
                st.session_state.stage = "role"
                st.rerun()
            else:
                st.warning("Por favor ingresa tu nombre para continuar.")

# ─── PANTALLA: ROL ────────────────────────────────────────────────────────────
def screen_role():
    header_html()

    st.markdown("""
    <div class="quiz-card">
        <div class="q-text" style="text-align:center;">Selecciona tu rol</div>
    """, unsafe_allow_html=True)

    rol = st.radio(
        "",
        ["Partner", "Gerencial"],
        key="radio_rol",
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀  Comenzar Quiz", use_container_width=True):
        st.session_state.rol = rol
        st.session_state.q_order = build_question_order(rol)
        st.session_state.stage = "quiz"
        st.rerun()

# ─── PANTALLA: QUIZ ───────────────────────────────────────────────────────────
def screen_quiz():
    header_html()
    validation_badge()

    order = st.session_state.q_order
    idx   = st.session_state.q_index
    total = len(order)

    if idx >= total:
        st.session_state.stage = "handwash"
        st.rerun()
        return

    qid = order[idx]
    q   = get_question(qid)

    progress_bar(idx + 1, total)

    # ── Encabezado de pregunta ──
    st.markdown(f"""
    <div class="q-meta">
        <span class="q-num">Pregunta {idx + 1}</span>
        <span class="q-type">{q.get('type','').replace('_',' ').title()}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Render según tipo ──
    answered = render_question(q, qid)

    # ── Botón siguiente ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️  Siguiente pregunta", use_container_width=True, key=f"next_{qid}"):
        if answered:
            st.session_state.q_index += 1
            st.rerun()
        else:
            st.warning("Por favor responde la pregunta antes de continuar.")

def render_question(q: dict, qid: int) -> bool:
    """Renderiza la pregunta y retorna True si fue respondida."""
    t = q["type"]

    if t == "multiple_choice":
        return render_multiple_choice(q, qid)
    elif t == "true_false":
        return render_true_false(q, qid)
    elif t == "chips_select":
        return render_chips(q, qid)
    elif t == "open":
        return render_open(q, qid)
    elif t == "fill_blank":
        return render_fill_blank(q, qid)
    elif t == "open_joker":
        return render_open_joker(q, qid)
    elif t == "open_bonus":
        return render_open_bonus(q, qid)
    elif t == "order":
        return render_order(q, qid)
    elif t == "fill_multiple":
        return render_fill_multiple(q, qid)
    elif t == "open_role":
        return render_open_role(q, qid)
    return False

# ── Helpers de tarjeta ──
def card_open(extra_style=""):
    st.markdown(f'<div class="quiz-card" style="{extra_style}">', unsafe_allow_html=True)
def card_close():
    st.markdown('</div>', unsafe_allow_html=True)

def qtext(text):
    st.markdown(f'<div class="q-text">{text}</div>', unsafe_allow_html=True)

def already_scored(qid):
    return qid in st.session_state.scores

def mark_score(qid, pts):
    if qid not in st.session_state.scores:
        st.session_state.scores[qid] = pts

# ─── Tipo: Selección múltiple ─────────────────────────────────────────────────
def render_multiple_choice(q, qid):
    card_open()
    qtext(q["text"])
    key = f"mc_{qid}"
    options = q["options"]
    sel = st.radio("", options, key=key, index=None)
    card_close()

    if sel is not None and not already_scored(qid):
        if sel == q["correct"]:
            mark_score(qid, q["points"])
            st.session_state.answers[qid] = sel
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            mark_score(qid, 0)
            st.session_state.answers[qid] = sel
            st.markdown(f'<div class="feedback-wrong">❌ Respuesta incorrecta. La correcta: <strong>{q["correct"]}</strong></div>', unsafe_allow_html=True)
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts > 0:
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-wrong">❌ La correcta era: <strong>{q["correct"]}</strong></div>', unsafe_allow_html=True)

    return sel is not None or already_scored(qid)

# ─── Tipo: Verdadero/Falso ────────────────────────────────────────────────────
def render_true_false(q, qid):
    card_open()
    qtext(q["text"])
    key = f"tf_{qid}"
    sel = st.radio("", ["Verdadero", "Falso"], key=key, index=None)

    extra_text = ""
    if sel == "Falso":
        extra_text = st.text_input("Escribe la respuesta correcta:", key=f"tf_extra_{qid}")
        st.caption("Nota: la respuesta correcta era Verdadero — no se suman puntos por esta opción.")

    card_close()

    if sel is not None and not already_scored(qid):
        if sel == q["correct"]:
            mark_score(qid, q["points"])
            st.session_state.answers[qid] = sel
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            mark_score(qid, 0)
            st.session_state.answers[qid] = f"Falso → {extra_text}"
            st.markdown('<div class="feedback-wrong">❌ La respuesta correcta era <strong>Verdadero</strong>.</div>', unsafe_allow_html=True)
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts > 0:
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">❌ La respuesta correcta era <strong>Verdadero</strong>.</div>', unsafe_allow_html=True)

    return sel is not None or already_scored(qid)

# ─── Tipo: Chips (lluvia de cuadros) ─────────────────────────────────────────
def render_chips(q, qid):
    card_open()
    qtext(q["text"])
    st.caption(q.get("instruction", "Selecciona las opciones correctas."))

    # Construir lista completa mezclada (una vez por sesión)
    all_key = f"chips_all_{qid}"
    if all_key not in st.session_state:
        all_items = q["correct"] + q["distractors"]
        random.shuffle(all_items)
        st.session_state[all_key] = all_items

    all_items = st.session_state[all_key]
    sel_key   = f"chips_{qid}"
    if sel_key not in st.session_state.chip_selections:
        st.session_state.chip_selections[sel_key] = []

    selected = st.session_state.chip_selections[sel_key]

    # Renderizar checkboxes como chips visuales
    cols = st.columns(3)
    for i, item in enumerate(all_items):
        is_sel = item in selected
        col = cols[i % 3]
        with col:
            checked = st.checkbox(item, value=is_sel, key=f"chip_{qid}_{i}", disabled=already_scored(qid))
            if checked and item not in selected:
                selected.append(item)
            elif not checked and item in selected:
                selected.remove(item)

    st.session_state.chip_selections[sel_key] = selected
    card_close()

    responded = len(selected) > 0

    if responded and not already_scored(qid):
        correct_set = set(q["correct"])
        sel_set     = set(selected)
        correct_hits = len(sel_set & correct_set)
        total_correct = len(correct_set)
        pts = round((correct_hits / total_correct) * q["points"])
        mark_score(qid, pts)
        st.session_state.answers[qid] = list(selected)
        if sel_set == correct_set:
            st.markdown('<div class="feedback-correct">✅ ¡Perfecto!</div>', unsafe_allow_html=True)
        else:
            missed = correct_set - sel_set
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto. Faltaron: {", ".join(missed)}</div>', unsafe_allow_html=True)
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts == q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Perfecto!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({pts}/{q["points"]} pts)</div>', unsafe_allow_html=True)

    return responded or already_scored(qid)

# ─── Tipo: Pregunta abierta ───────────────────────────────────────────────────
def render_open(q, qid):
    card_open()
    qtext(q["text"])
    ans = st.text_area("Tu respuesta:", key=f"open_{qid}", height=100, disabled=already_scored(qid))
    card_close()

    has_ans = bool(ans.strip()) or already_scored(qid)

    if ans.strip() and not already_scored(qid):
        hits = count_keywords(ans, q["keywords"])
        ratio = hits / max(len(q["keywords"]), 1)
        if ratio >= 0.4:
            mark_score(qid, q["points"])
            st.markdown('<div class="feedback-correct">✅ ¡Bien respondido!</div>', unsafe_allow_html=True)
        else:
            mark_score(qid, 0)
            st.markdown('<div class="feedback-wrong">Respuesta incompleta o incorrecta.</div>', unsafe_allow_html=True)
        st.session_state.answers[qid] = ans
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts > 0:
            st.markdown('<div class="feedback-correct">✅ ¡Bien respondido!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incompleta.</div>', unsafe_allow_html=True)

    return has_ans

# ─── Tipo: Completar espacio en blanco ───────────────────────────────────────
def render_fill_blank(q, qid):
    card_open()
    qtext(q["text"])
    ans = st.text_input("Completa:", key=f"fill_{qid}", disabled=already_scored(qid))
    card_close()

    has_ans = bool(ans.strip()) or already_scored(qid)

    if ans.strip() and not already_scored(qid):
        if flexible_match(ans, q["keywords"]):
            mark_score(qid, q["points"])
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            mark_score(qid, 0)
            st.markdown('<div class="feedback-wrong">Respuesta incorrecta.</div>', unsafe_allow_html=True)
        st.session_state.answers[qid] = ans
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts > 0:
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incorrecta.</div>', unsafe_allow_html=True)

    return has_ans

# ─── Tipo: Abierta con comodín/ayuda ─────────────────────────────────────────
def render_open_joker(q, qid):
    card_open()
    qtext(q["text"])

    # Hint prefix si existe (P16)
    if "hint_prefix" in q:
        st.markdown(f"<p style='font-size:0.95rem;color:var(--text-mid);margin-bottom:0.7rem;'>{q['hint_prefix']}</p>", unsafe_allow_html=True)

    # Botón comodín
    joker_key = f"joker_{qid}"
    if joker_key not in st.session_state.joker_used:
        st.session_state.joker_used[joker_key] = False

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(f"🎁 {q['joker_label']}", key=f"jbtn_{qid}", disabled=st.session_state.joker_used[joker_key]):
            st.session_state.joker_used[joker_key] = True
            st.rerun()

    if st.session_state.joker_used[joker_key]:
        st.markdown(f'<div class="joker-box"><strong>💡 Pista:</strong> {q["joker"]}</div>', unsafe_allow_html=True)

    ans = st.text_area("Tu respuesta:", key=f"openj_{qid}", height=100, disabled=already_scored(qid))
    card_close()

    has_ans = bool(ans.strip()) or already_scored(qid)

    if ans.strip() and not already_scored(qid):
        hits = count_keywords(ans, q["keywords"])
        ratio = hits / max(len(q["keywords"]), 1)
        if ratio >= 0.35:
            mark_score(qid, q["points"])
            st.markdown('<div class="feedback-correct">✅ ¡Bien respondido!</div>', unsafe_allow_html=True)
        else:
            mark_score(qid, 0)
            st.markdown('<div class="feedback-wrong">Respuesta incompleta.</div>', unsafe_allow_html=True)
        st.session_state.answers[qid] = ans
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts > 0:
            st.markdown('<div class="feedback-correct">✅ ¡Bien respondido!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incompleta.</div>', unsafe_allow_html=True)

    return has_ans

# ─── Tipo: Abierta con bonus ──────────────────────────────────────────────────
def render_open_bonus(q, qid):
    card_open()
    qtext(q["text"])
    ans = st.text_area("Tu respuesta:", key=f"bonus_{qid}", height=120, disabled=already_scored(qid))
    card_close()

    has_ans = bool(ans.strip()) or already_scored(qid)

    if ans.strip() and not already_scored(qid):
        base_hits  = count_keywords(ans, q["base_keywords"])
        bonus_hits = count_keywords(ans, q["bonus_keywords"])
        ratio = base_hits / max(len(q["base_keywords"]), 1)
        pts = round(ratio * q["points"])
        if bonus_hits >= 2:
            pts = min(pts + q["bonus_points"], q["points"] + q["bonus_points"])
        mark_score(qid, min(pts, q["points"] + q["bonus_points"]))
        st.session_state.answers[qid] = ans
        if pts >= q["points"]:
            extra = " ⭐ ¡Bonus obtenido!" if bonus_hits >= 2 else ""
            st.markdown(f'<div class="feedback-correct">✅ ¡Excelente!{extra}</div>', unsafe_allow_html=True)
        elif pts > 0:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({pts} pts).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incompleta.</div>', unsafe_allow_html=True)
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts >= q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Excelente!</div>', unsafe_allow_html=True)
        elif pts > 0:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({pts} pts).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incompleta.</div>', unsafe_allow_html=True)

    return has_ans

# ─── Tipo: Ordenar pasos ──────────────────────────────────────────────────────
def render_order(q, qid):
    card_open()
    qtext(q["text"])
    st.caption("Ordena los pasos arrastrando con los selectores de posición.")

    order_key = f"order_{qid}"
    if order_key not in st.session_state.order_state:
        shuffled = q["items"].copy()
        random.shuffle(shuffled)
        st.session_state.order_state[order_key] = shuffled

    current = st.session_state.order_state[order_key]

    for i, item in enumerate(current):
        c1, c2, c3 = st.columns([0.5, 3, 1])
        with c1:
            st.markdown(f"<span style='font-size:1.1rem;'>{'①②③④'[i]}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='order-item'><span class='order-handle'>☰</span> {item}</div>", unsafe_allow_html=True)
        with c3:
            if not already_scored(qid):
                if i > 0 and st.button("▲", key=f"up_{qid}_{i}"):
                    current[i], current[i-1] = current[i-1], current[i]
                    st.session_state.order_state[order_key] = current
                    st.rerun()
                if i < len(current)-1 and st.button("▼", key=f"dn_{qid}_{i}"):
                    current[i], current[i+1] = current[i+1], current[i]
                    st.session_state.order_state[order_key] = current
                    st.rerun()

    card_close()

    if not already_scored(qid):
        if st.button("✔ Confirmar orden", key=f"confirm_order_{qid}"):
            if current == q["correct_order"]:
                mark_score(qid, q["points"])
                st.markdown('<div class="feedback-correct">✅ ¡Orden correcto!</div>', unsafe_allow_html=True)
            else:
                # Puntaje parcial por pasos en posición correcta
                hits = sum(1 for a, b in zip(current, q["correct_order"]) if a == b)
                pts  = round((hits / len(q["correct_order"])) * q["points"])
                mark_score(qid, pts)
                st.markdown(f'<div class="feedback-wrong">Orden incorrecto. Correcto: {" → ".join(q["correct_order"])}</div>', unsafe_allow_html=True)
            st.session_state.answers[qid] = current
    else:
        pts = st.session_state.scores[qid]
        if pts == q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Orden correcto!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-wrong">Orden incorrecto ({pts}/{q["points"]} pts).</div>', unsafe_allow_html=True)

    return already_scored(qid)

# ─── Tipo: Completar múltiples faltantes ─────────────────────────────────────
def render_fill_multiple(q, qid):
    card_open()
    qtext(q["text"])
    st.markdown(f"<p style='font-size:0.88rem;color:var(--text-mid);'>Ya dados: <strong>{', '.join(q['given'])}</strong></p>", unsafe_allow_html=True)
    st.caption("Completa los campos faltantes:")

    answers_blanks = []
    for i in range(q["blanks"]):
        val = st.text_input(f"Síntoma {i+1}:", key=f"blank_{qid}_{i}", disabled=already_scored(qid))
        answers_blanks.append(val)

    card_close()

    all_filled = all(v.strip() for v in answers_blanks)

    if all_filled and not already_scored(qid):
        hits = 0
        for i, val in enumerate(answers_blanks):
            if flexible_match(val, q["blank_keywords"][i]):
                hits += 1
        pts = round((hits / q["blanks"]) * q["points"])
        mark_score(qid, pts)
        st.session_state.answers[qid] = answers_blanks
        if pts == q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        elif pts > 0:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({hits}/{q["blanks"]}).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incorrecta.</div>', unsafe_allow_html=True)
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts == q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Correcto!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({pts}/{q["points"]} pts).</div>', unsafe_allow_html=True)

    return all_filled or already_scored(qid)

# ─── Tipo: Abierta adaptativa por rol (P17) ───────────────────────────────────
def render_open_role(q, qid):
    card_open()
    qtext(q["text"])

    rol = st.session_state.rol
    is_gerencial = (rol == "Gerencial")

    if not is_gerencial:
        st.markdown('<div class="joker-box"><strong>💡 Ayuda:</strong> Son 3 acciones.</div>', unsafe_allow_html=True)
        keywords = q["keywords_base"]
        required_hits = 2
    else:
        keywords = q["keywords_gerencial"]
        required_hits = 3

    ans = st.text_area("Tu respuesta:", key=f"role_q_{qid}", height=130, disabled=already_scored(qid))
    card_close()

    has_ans = bool(ans.strip()) or already_scored(qid)

    if ans.strip() and not already_scored(qid):
        hits = count_keywords(ans, keywords)
        pts  = round(min(hits / max(len(keywords), 1), 1.0) * q["points"])
        if hits >= required_hits:
            pts = q["points"]
        mark_score(qid, pts)
        st.session_state.answers[qid] = ans
        if pts >= q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Muy bien!</div>', unsafe_allow_html=True)
        elif pts > 0:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({pts} pts).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-wrong">Respuesta incompleta.</div>', unsafe_allow_html=True)
    elif already_scored(qid):
        pts = st.session_state.scores[qid]
        if pts >= q["points"]:
            st.markdown('<div class="feedback-correct">✅ ¡Muy bien!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-wrong">Parcialmente correcto ({pts} pts).</div>', unsafe_allow_html=True)

    return has_ans

# ─── PANTALLA: LAVADO DE MANOS ────────────────────────────────────────────────
def screen_handwash():
    header_html()
    validation_badge()

    st.markdown("""
    <div class="handwash-notice">
        <h2>🙌 ¡Ya casi terminas!</h2>
        <p>Falta ver tu lavado de manos.</p>
        <p>Eso será calificado en tienda.</p>
        <p style="font-size:1.1rem;font-weight:600;margin-top:0.8rem;">¡Suerte! ☘️</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📊  Ver mi puntaje final", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()

# ─── PANTALLA: RESULTADO ──────────────────────────────────────────────────────
def screen_result():
    header_html()
    validation_badge()

    # Calcular score
    total_pts   = TOTAL_POINTS
    earned      = sum(st.session_state.scores.values())
    # Bonus puede hacer superar el tope por un momento → cap a 100
    max_possible = total_pts + sum(q.get("bonus_points", 0) for q in QUESTIONS_POOL)
    pct = round((earned / max_possible) * 100)
    pct = min(pct, 100)
    # Normalizar a 100
    score_100 = round((earned / max_possible) * 100)
    score_100 = min(score_100, 100)

    # Guardar en Sheets (una vez)
    if not st.session_state.saved:
        data = {
            "nombre":    st.session_state.nombre,
            "rol":       st.session_state.rol,
            "codigo":    st.session_state.unique_code,
            "score":     score_100,
            "porcentaje": f"{score_100}%",
            "fecha":     datetime.date.today().isoformat(),
            "hora":      datetime.datetime.now().strftime("%H:%M:%S"),
            "browser":   platform.platform(),
            "uuid":      st.session_state.session_uuid,
            "respuestas": st.session_state.answers,
        }
        save_to_sheets(data)
        st.session_state.saved = True

    # Mensaje según score
    if score_100 == 100:
        color = "#00704A"
        msg = "🏆 Excelente estimado, ganaste un abrazo de tu líder RSA. ¡Canjéalo cuando quieras!"
    elif score_100 >= 90:
        color = "#00704A"
        msg = "⭐ ¡Excelente! Dominas muy bien los temas RSA."
    elif score_100 >= 70:
        color = "#C47B37"
        msg = "👍 ¡Buen trabajo! Sigue reforzando."
    elif score_100 >= 50:
        color = "#CBA258"
        msg = "📚 Debes reforzar algunos temas RSA."
    else:
        color = "#C0392B"
        msg = "🚨 Urgente: reforzar conocimientos RSA."

    st.markdown(f"""
    <div class="quiz-card score-big">
        <div class="score-number" style="color:{color};">{score_100}</div>
        <div class="score-label">puntos de 100</div>
        <div class="score-msg" style="background:{color}22;color:{color};">{msg}</div>
        <p style="font-size:0.95rem;color:var(--text-mid);">📸 Sácale captura a tu resultado</p>
    </div>
    """, unsafe_allow_html=True)

    # Breakdown
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Syne,sans-serif;font-weight:700;font-size:1rem;margin-bottom:0.8rem;">Detalle por pregunta</p>', unsafe_allow_html=True)
    for q in QUESTIONS_POOL:
        qid    = q["id"]
        earned_q = st.session_state.scores.get(qid, 0)
        max_q  = q["points"] + q.get("bonus_points", 0)
        label  = f"P{qid}: {q['text'][:55]}…" if len(q['text']) > 55 else f"P{qid}: {q['text']}"
        pct_q  = "✅" if earned_q >= q["points"] else ("⚡" if earned_q > 0 else "❌")
        st.markdown(f"""
        <div class="breakdown-row">
            <span>{pct_q} {label}</span>
            <span class="pts">{earned_q}/{max_q}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Confetti si score alto
    if score_100 >= 70:
        st.markdown("""
        <canvas id="confetti-canvas"></canvas>
        <script>
        (function(){
          var canvas = document.getElementById('confetti-canvas');
          if(!canvas) return;
          var ctx = canvas.getContext('2d');
          canvas.width = window.innerWidth;
          canvas.height = window.innerHeight;
          var pieces = [];
          var colors = ['#00704A','#CBA258','#F5A623','#C47B37','#D4E9E2','#1E3932'];
          for(var i=0;i<160;i++){
            pieces.push({
              x: Math.random()*canvas.width,
              y: Math.random()*canvas.height - canvas.height,
              r: Math.random()*6+4,
              d: Math.random()*160+80,
              color: colors[Math.floor(Math.random()*colors.length)],
              tilt: Math.floor(Math.random()*10)-10,
              speed: Math.random()*3+1
            });
          }
          var angle = 0;
          function draw(){
            ctx.clearRect(0,0,canvas.width,canvas.height);
            angle += 0.01;
            pieces.forEach(function(p,i){
              ctx.beginPath();
              ctx.lineWidth = p.r/2;
              ctx.strokeStyle = p.color;
              ctx.moveTo(p.x+p.tilt+p.r/4, p.y);
              ctx.lineTo(p.x+p.tilt, p.y+p.tilt+p.r/4);
              ctx.stroke();
              p.y += p.speed;
              p.tilt = Math.sin(angle+i)*15;
              if(p.y > canvas.height) p.y = -10;
            });
            requestAnimationFrame(draw);
          }
          draw();
          setTimeout(function(){ canvas.remove(); }, 6000);
        })();
        </script>
        """, unsafe_allow_html=True)

    # Info de validación
    st.markdown(f"""
    <div style="background:rgba(30,57,50,0.05);border-radius:12px;padding:1rem 1.2rem;font-size:0.8rem;color:var(--text-light);margin-top:1rem;">
        👤 {st.session_state.nombre} · {st.session_state.rol} ·
        Código: <strong>{st.session_state.unique_code}</strong> ·
        {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """, unsafe_allow_html=True)

# ─── Router principal ─────────────────────────────────────────────────────────
stage = st.session_state.stage

if stage == "intro":
    screen_intro()
elif stage == "role":
    screen_role()
elif stage == "quiz":
    screen_quiz()
elif stage == "handwash":
    screen_handwash()
elif stage == "result":
    screen_result()

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
import json

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="BioReact Engine · Google Lab",
    page_icon="🧬",
    layout="wide",
)

# =========================================================
# MATERIAL DESIGN CSS (Google palette)
# =========================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">

<style>
/* ── Root tokens ─────────────────────────────────────────── */
:root {
    --g-blue:   #4285F4;
    --g-red:    #EA4335;
    --g-yellow: #FBBC05;
    --g-green:  #34A853;
    --bg:       #F8F9FA;
    --surface:  #FFFFFF;
    --border:   #E0E0E0;
    --border-focus: #4285F4;
    --text-primary:   #202124;
    --text-secondary: #5F6368;
    --shadow-sm: 0 1px 3px rgba(60,64,67,0.12), 0 1px 2px rgba(60,64,67,0.08);
    --shadow-md: 0 4px 12px rgba(60,64,67,0.15), 0 2px 4px rgba(60,64,67,0.08);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}

/* ── Global typography & background ─────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Roboto', 'Google Sans', Arial, sans-serif;
    background: var(--bg) !important;
    color: var(--text-primary);
}

/* Ocultar toolbar nativo de Streamlit — sustituido por hc-header fijo */
[data-testid="stHeader"] { display: none !important; }

/* Contenido principal: empieza bajo el header fijo (88px) y
   termina sobre el footer fijo (56px)                        */
.block-container {
    padding-top: 104px !important;   /* 88px header + 16px gap  */
    padding-bottom: 5rem !important;
}

/* ── Sidebar contenido entre header (88px) y footer (56px) ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
    top: 88px !important;
    bottom: 56px !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 0.8rem !important;
}

/* Botón para re-expandir la sidebar cuando está colapsada */
[data-testid="collapsedControl"] {
    top: 96px !important;
    z-index: 1000 !important;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-top: 1.4rem;
    margin-bottom: 0.2rem;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
}

/* ── Google header ───────────────────────────────────────── */
.g-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 0 18px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.g-logo {
    width: 48px; height: 48px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px;
    padding: 8px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    flex-shrink: 0;
}

.g-dot {
    border-radius: 50%;
    width: 100%; height: 100%;
}

.g-brand h1 {
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.g-brand p {
    font-size: 0.83rem;
    color: var(--text-secondary);
    margin: 4px 0 0 0;
    font-weight: 400;
}

.g-chip {
    display: inline-flex;
    align-items: center;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #E8F0FE;
    color: var(--g-blue);
    border: 1px solid #C5D9FB;
    margin-left: 8px;
    vertical-align: middle;
}

.g-chip-green {
    background: #E6F4EA;
    color: #137333;
    border-color: #A8D5B5;
}

/* ── Cards ───────────────────────────────────────────────── */
.g-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.1rem 0.6rem 1.1rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
    transition: box-shadow 0.18s ease;
}

.g-card:hover { box-shadow: var(--shadow-md); }

.g-card-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--g-blue);
    margin-bottom: 0.45rem;
    display: block;
}

/* ── Metric strip ────────────────────────────────────────── */
.g-metric {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--g-blue);
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem 0.75rem 1rem;
    box-shadow: var(--shadow-sm);
    text-align: center;
}

.g-metric-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
    margin-bottom: 4px;
}

.g-metric-value {
    font-family: 'Google Sans', 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
}

/* ── Status badges ───────────────────────────────────────── */
.g-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}

.g-badge-stable   { background:#E6F4EA; color:#137333; border:1px solid #A8D5B5; }
.g-badge-unstable { background:#FCE8E6; color:#C5221F; border:1px solid #F5B8B5; }
.g-badge-warning  { background:#FEF7E0; color:#B06000; border:1px solid #F8D775; }

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--surface);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    padding: 6px 8px 0 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    padding: 0.5rem 1.1rem;
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-weight: 500;
    font-size: 0.87rem;
    color: var(--text-secondary);
    background: transparent;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    color: var(--g-blue) !important;
    border-bottom: 2px solid var(--g-blue) !important;
    background: transparent !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 0.45rem 1.3rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--g-blue);
    box-shadow: var(--shadow-sm);
    transition: all 0.15s ease;
}

.stButton > button:hover {
    background: #E8F0FE;
    border-color: var(--g-blue);
    box-shadow: var(--shadow-md);
}

.stDownloadButton > button {
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-weight: 500;
    border-radius: var(--radius-sm);
    background: var(--g-blue);
    color: white !important;
    border: none;
    box-shadow: var(--shadow-sm);
    transition: all 0.15s ease;
}

.stDownloadButton > button:hover {
    background: #3367D6 !important;
    box-shadow: var(--shadow-md);
}

/* ── Inputs / number inputs ──────────────────────────────── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Roboto', sans-serif;
}

[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: var(--g-blue) !important;
    box-shadow: 0 0 0 2px rgba(66,133,244,0.15) !important;
}

/* ── Slider accent ───────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
    background: var(--g-blue) !important;
}

/* ── DataFrame ───────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden;
}

/* ── Alerts ──────────────────────────────────────────────── */
.stAlert { border-radius: var(--radius-md); }

/* ── Divider ─────────────────────────────────────────────── */
hr { border-color: var(--border); margin: 1.2rem 0; }

/* ── Spinner ─────────────────────────────────────────────── */
[data-testid="stSpinner"] > div > div {
    border-top-color: var(--g-blue) !important;
}

/* ══════════════════════════════════════════════════════════
   HOSTCELL SUITE — banners CONSTANTES entre herramientas
   ══════════════════════════════════════════════════════════ */

/* ── Padding inferior: el contenido no queda bajo el footer  */
.block-container { padding-bottom: 5rem !important; }

/* ── Sidebar: acotado visualmente por el footer ─────────── */
[data-testid="stSidebar"] {
    bottom: 56px !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

/* ── Header fijo — altura explícita 88px ─────────────────── */
.hc-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 88px;
    z-index: 1001;
    background: rgba(255, 255, 255, 0.97);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    box-shadow: 0 1px 8px rgba(60,64,67,0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1.6rem;
    box-sizing: border-box;
}

.hc-header-brand {
    display: flex;
    align-items: center;
    gap: 13px;
    min-width: 0;
    flex: 1 1 auto;
    overflow: hidden;
}

.hc-header-text { min-width: 0; line-height: 1.2; flex: 1 1 auto; overflow: hidden; }

.hc-supertitle {
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-size: 0.62rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    color: var(--g-blue);
    margin: 0 0 2px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.hc-supertitle .sep { opacity: 0.4; margin: 0 4px; }

.hc-header h1 {
    font-family: 'Google Sans', 'Roboto', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 2px 0;
    letter-spacing: -0.02em;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.hc-tagline {
    font-size: 0.72rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.hc-header-right {
    display: flex;
    align-items: center;
    flex-shrink: 0;
}

/* ── Footer (CONSTANTE — igual estructura en toda la suite) */
.hc-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 56px;
    background: rgba(248, 249, 250, 0.96);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-top: 1px solid var(--border);
    box-shadow: 0 -1px 8px rgba(60,64,67,0.07);
    z-index: 9999;
    box-sizing: border-box;
}

.hc-footer-inner {
    height: 100%;
    padding: 0 1.6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    font-family: 'Roboto', 'Google Sans', sans-serif;
}

.hc-footer-suite { display: flex; flex-direction: column; gap: 1px; min-width: 0; }

.hc-footer-name {
    font-size: 0.83rem;
    font-weight: 700;
    color: var(--g-blue);
    white-space: nowrap;
}

.hc-footer-slogan {
    font-size: 0.67rem;
    color: var(--text-secondary);
    white-space: nowrap;
    font-style: italic;
}

.hc-footer-author {
    font-size: 0.78rem;
    color: var(--text-secondary);
    white-space: nowrap;
    margin-left: auto;
}

.hc-footer-github {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 0.44rem 1.05rem;
    border-radius: 999px;
    background: #1e2330;
    color: #FFFFFF !important;
    font-size: 0.78rem;
    font-weight: 600;
    text-decoration: none !important;
    transition: background 130ms ease, transform 110ms ease, box-shadow 130ms ease;
    box-shadow: 0 1px 4px rgba(0,0,0,0.20);
    flex-shrink: 0;
    font-family: 'Google Sans', 'Roboto', sans-serif;
}

.hc-footer-github:hover {
    background: #2d3348;
    transform: translateY(-1px);
    box-shadow: 0 3px 9px rgba(0,0,0,0.25);
}

.hc-footer-github svg { flex-shrink: 0; }
</style>

<!-- ══ HEADER ══ -->
<div class="hc-header">
    <div class="hc-header-brand">
        <div class="g-logo">
            <div class="g-dot" style="background:#4285F4"></div>
            <div class="g-dot" style="background:#EA4335"></div>
            <div class="g-dot" style="background:#FBBC05"></div>
            <div class="g-dot" style="background:#34A853"></div>
        </div>
        <div class="hc-header-text">
            <p class="hc-supertitle">HostCell Suite</p>
            <h1>BioReact Engine</h1>
            <p class="hc-tagline">Simulación de quimiostato con cinética de Monod &nbsp;·&nbsp; Análisis de estabilidad local</p>
        </div>
    </div>
    <div class="hc-header-right">
        <span class="g-chip">Live App</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# PLOTLY GOOGLE THEME
# =========================================================
GOOGLE_LAYOUT = dict(
    font=dict(family="Roboto, Google Sans, Arial, sans-serif", size=12, color="#202124"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    legend=dict(
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#E0E0E0",
        borderwidth=1,
        font=dict(size=11, color="#202124"),
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="left", x=0,
    ),
    margin=dict(l=45, r=20, t=45, b=45),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#E0E0E0",
        font=dict(family="Roboto, sans-serif", size=12),
    ),
)

def google_axis(title=None, **extra):
    """Estilo de eje Google Material — pasar title (str) y kwargs adicionales (range, etc.)."""
    axis = dict(
        showgrid=True, gridcolor="#F1F3F4", gridwidth=1,
        linecolor="#E0E0E0", linewidth=1,
        tickfont=dict(size=11, color="#5F6368"),
    )
    if title is not None:
        axis["title"] = dict(
            text=title,
            font=dict(size=12, color="#5F6368", family="Roboto, sans-serif"),
        )
    axis.update(extra)
    return axis

# =========================================================
# UTILIDADES DE UI
# =========================================================
def _sync_from_slider(name: str):
    st.session_state[f"{name}_num"] = st.session_state[f"{name}_slider"]

def _sync_from_num(name: str, min_value: float, max_value: float):
    val = float(st.session_state[f"{name}_num"])
    val = max(min_value, min(max_value, val))
    st.session_state[f"{name}_num"] = val
    st.session_state[f"{name}_slider"] = val

def slider_with_exact_input(
    label: str,
    name: str,
    min_value: float,
    max_value: float,
    default: float,
    step: float,
    fmt: str = "%.3f",
):
    if f"{name}_slider" not in st.session_state:
        st.session_state[f"{name}_slider"] = default
    if f"{name}_num" not in st.session_state:
        st.session_state[f"{name}_num"] = default

    c1, c2 = st.sidebar.columns([3.0, 1.55])

    with c1:
        st.slider(
            label,
            min_value=min_value,
            max_value=max_value,
            step=step,
            key=f"{name}_slider",
            on_change=_sync_from_slider,
            args=(name,),
        )

    with c2:
        st.number_input(
            "Valor",
            min_value=min_value,
            max_value=max_value,
            step=step,
            format=fmt,
            key=f"{name}_num",
            on_change=_sync_from_num,
            args=(name, min_value, max_value),
            label_visibility="collapsed",
        )

    return float(st.session_state[f"{name}_num"])

# =========================================================
# FUNCIONES MATEMÁTICAS
# =========================================================
def kinetics_monod(S, mu_max, Ks):
    S = max(float(S), 0.0)
    denom = Ks + S
    return (mu_max * S / denom) if denom > 0 else 0.0

def dmu_dS_monod(S, mu_max, Ks):
    S = max(float(S), 0.0)
    denom = (Ks + S) ** 2
    return (mu_max * Ks / denom) if denom > 0 else 0.0

def f1(X, S, D, mu_max, Ks):
    mu = kinetics_monod(S, mu_max, Ks)
    return X * (mu - D)

def f2(X, S, D, mu_max, Ks, Sr, Yxs):
    mu = kinetics_monod(S, mu_max, Ks)
    return D * (Sr - S) - (mu * X / Yxs)

def rk4_one_step(X, S, p, dt):
    k1X = dt * f1(X, S, p["D"], p["mu_max"], p["Ks"])
    k1S = dt * f2(X, S, p["D"], p["mu_max"], p["Ks"], p["Sr"], p["Yxs"])

    k2X = dt * f1(X + 0.5 * k1X, S + 0.5 * k1S, p["D"], p["mu_max"], p["Ks"])
    k2S = dt * f2(X + 0.5 * k1X, S + 0.5 * k1S, p["D"], p["mu_max"], p["Ks"], p["Sr"], p["Yxs"])

    k3X = dt * f1(X + 0.5 * k2X, S + 0.5 * k2S, p["D"], p["mu_max"], p["Ks"])
    k3S = dt * f2(X + 0.5 * k2X, S + 0.5 * k2S, p["D"], p["mu_max"], p["Ks"], p["Sr"], p["Yxs"])

    k4X = dt * f1(X + k3X, S + k3S, p["D"], p["mu_max"], p["Ks"])
    k4S = dt * f2(X + k3X, S + k3S, p["D"], p["mu_max"], p["Ks"], p["Sr"], p["Yxs"])

    X_next = X + (k1X + 2*k2X + 2*k3X + k4X) / 6.0
    S_next = S + (k1S + 2*k2S + 2*k3S + k4S) / 6.0

    return max(0.0, X_next), max(0.0, S_next), {
        "k1X": k1X, "k1S": k1S,
        "k2X": k2X, "k2S": k2S,
        "k3X": k3X, "k3S": k3S,
        "k4X": k4X, "k4S": k4S,
    }

def runge_kutta4(X0, S0, p, dt, t_final):
    X_vals = [max(0.0, X0)]
    S_vals = [max(0.0, S0)]
    times = [0.0]

    X, S = float(X0), float(S0)
    n_steps = int(np.ceil(t_final / dt))
    first_step_debug = None

    for i in range(n_steps):
        current_t = i * dt
        h = min(dt, t_final - current_t)
        if h <= 0:
            break

        X_new, S_new, debug = rk4_one_step(X, S, p, h)

        if first_step_debug is None:
            first_step_debug = {
                "X0": X, "S0": S, "dt": h, **debug,
                "X1": X_new, "S1": S_new,
            }

        X, S = X_new, S_new
        X_vals.append(X)
        S_vals.append(S)
        times.append(current_t + h)

    df = pd.DataFrame({"t": times, "X": X_vals, "S": S_vals})
    df["mu"] = df["S"].apply(lambda s: kinetics_monod(s, p["mu_max"], p["Ks"]))
    return df, first_step_debug

# =========================================================
# EQUILIBRIOS Y ESTABILIDAD
# =========================================================
def equilibria_monod(p):
    mu_max = p["mu_max"]
    Ks = p["Ks"]
    D = p["D"]
    Sr = p["Sr"]
    Yxs = p["Yxs"]

    washout = {"name": "Washout", "X": 0.0, "S": Sr, "physical": True}
    positive = None

    if mu_max > D:
        S_star = (D * Ks) / (mu_max - D)
        X_star = Yxs * (Sr - S_star)
        if S_star >= 0 and X_star >= 0:
            positive = {
                "name": "Equilibrio positivo",
                "X": float(X_star),
                "S": float(S_star),
                "physical": bool(S_star <= Sr and X_star >= 0),
            }

    return washout, positive

def jacobian_monod(X, S, p):
    D = p["D"]
    Yxs = p["Yxs"]
    mu = kinetics_monod(S, p["mu_max"], p["Ks"])
    mu_p = dmu_dS_monod(S, p["mu_max"], p["Ks"])

    return np.array([
        [mu - D, X * mu_p],
        [-mu / Yxs, -D - (X * mu_p) / Yxs]
    ], dtype=float)

def classify_eigenvalues(evals):
    re = np.real(evals)
    im = np.imag(evals)

    if np.any(re > 0) and np.any(re < 0):
        return "Inestable (silla)"
    if np.all(re < 0):
        if np.all(np.abs(im) < 1e-10):
            return "Estable (nodo)"
        return "Estable (foco/espiral)"
    if np.all(re > 0):
        if np.all(np.abs(im) < 1e-10):
            return "Inestable (nodo)"
        return "Inestable (foco/espiral)"
    return "Marginal / indeterminado"

def normalize_eigenvectors(evecs):
    normalized = []
    for i in range(evecs.shape[1]):
        v = evecs[:, i].astype(complex)
        if abs(v[0]) > 1e-12:
            v = v / v[0]
        else:
            norm = np.linalg.norm(v)
            if norm > 0:
                v = v / norm
        normalized.append(v)
    return normalized

def analyze_equilibrium(eq, p):
    J = jacobian_monod(eq["X"], eq["S"], p)
    evals, evecs = np.linalg.eig(J)
    evecs_norm = normalize_eigenvectors(evecs)

    return {
        "J": J,
        "evals": evals,
        "evecs": evecs_norm,
        "classification": classify_eigenvalues(evals),
    }

# =========================================================
# PLANO DE FASE — helpers
# =========================================================
def trajectory_tends_to_washout(sim_df, washout_eq):
    final_X = float(sim_df["X"].iloc[-1])
    final_S = float(sim_df["S"].iloc[-1])

    x_scale = max(1.0, float(sim_df["X"].max()))
    s_scale = max(1.0, washout_eq["S"])

    x_tol = max(0.05 * x_scale, 0.05)
    s_tol = max(0.05 * s_scale, 0.25)

    return (final_X <= x_tol) and (abs(final_S - washout_eq["S"]) <= s_tol)

def add_eigenvector_lines(fig, eq, analysis):
    Xs, Ss = eq["X"], eq["S"]
    colors = ["#4285F4", "#34A853"]
    labels = ["v1", "v2"]

    x_scale = max(1.5, 0.16 * max(Xs, 1.0))
    s_scale = max(1.5, 0.16 * max(Ss, 1.0))

    for i, v in enumerate(analysis["evecs"][:2]):
        vx = np.real(v[0])
        vs = np.real(v[1])

        x1 = Xs - x_scale * vx
        x2 = Xs + x_scale * vx
        y1 = Ss - s_scale * vs
        y2 = Ss + s_scale * vs

        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines",
            name=f"Eigenvector {i+1}",
            line=dict(color=colors[i], width=2, dash="dash"),
            showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=[x2], y=[y2],
            mode="markers+text",
            text=[labels[i]],
            textposition="top right",
            marker=dict(size=7, color=colors[i]),
            name=f"Etiqueta {labels[i]}",
            showlegend=False,
        ))

# =========================================================
# SIDEBAR — parámetros
# =========================================================
st.sidebar.markdown(
    "<div style='border-bottom:1px solid #E8EAED;padding:4px 0 12px 0;margin-bottom:2px;'>"
    "<span style='font-family:Google Sans,Roboto,sans-serif;font-size:0.95rem;"
    "font-weight:700;color:#202124;'>⚙️ Parámetros</span></div>",
    unsafe_allow_html=True,
)

st.sidebar.header("Fisiológicos")
mu_max = slider_with_exact_input("μmax (h⁻¹)", "mu_max", 0.001, 2.000, 1.000, 0.001)
Ks     = slider_with_exact_input("Ks (g/L)",   "Ks",     0.001, 10.000, 1.000, 0.001)
Yxs    = slider_with_exact_input("Rendimiento Yx/s", "Yxs", 0.001, 1.000, 0.500, 0.001)

st.sidebar.header("Operación del reactor")
Sr = slider_with_exact_input("Sr alimentación (g/L)", "Sr", 1.000, 200.000, 100.000, 0.001)
D  = slider_with_exact_input("Dilución D (h⁻¹)",      "D",  0.001,   1.500,   0.500, 0.001)

st.sidebar.header("Simulación RK4")
x0  = st.sidebar.number_input("X inicial (g/L)",   min_value=0.0,   value=0.200,  step=0.001, format="%.3f")
s0  = st.sidebar.number_input("S inicial (g/L)",   min_value=0.0,   value=15.000, step=0.001, format="%.3f")
dt  = st.sidebar.number_input("Paso RK4 Δt (h)",   min_value=0.001, value=0.010,  step=0.001, format="%.3f")
t_f = st.sidebar.number_input("Tiempo final (h)",  min_value=0.1,   value=80.0,   step=0.1,   format="%.3f")

params = {
    "mu_max": mu_max,
    "Ks": Ks,
    "Sr": Sr,
    "Yxs": Yxs,
    "D": D,
}

# =========================================================
# CÁLCULOS con spinner
# =========================================================
with st.spinner("Ejecutando simulación RK4..."):
    sim_df, first_step = runge_kutta4(x0, s0, params, dt, t_f)

    washout_eq, positive_eq       = equilibria_monod(params)
    washout_analysis               = analyze_equilibrium(washout_eq, params)
    positive_analysis              = (
        analyze_equilibrium(positive_eq, params)
        if positive_eq is not None and positive_eq["physical"]
        else None
    )
    show_washout_on_phase = trajectory_tends_to_washout(sim_df, washout_eq)

final_X  = sim_df["X"].iloc[-1]
final_S  = sim_df["S"].iloc[-1]
final_mu = sim_df["mu"].iloc[-1]

# ── Toast: notificar solo cuando cambian parámetros ──────
_params_key = hash((mu_max, Ks, Yxs, Sr, D, x0, s0, dt, t_f))
if st.session_state.get("_last_params_key") != _params_key:
    st.session_state["_last_params_key"] = _params_key
    if positive_eq is not None and positive_eq["physical"]:
        st.toast(
            f"Equilibrio estable · X*={positive_eq['X']:.3f} g/L, S*={positive_eq['S']:.3f} g/L",
            icon="✅",
        )
    else:
        st.toast("Washout detectado con los parámetros actuales", icon="⚠️")

# =========================================================
# MÉTRICAS — barra superior
# =========================================================
st.markdown(
    f"""
    <div style="display:flex; gap:12px; margin-bottom:1.3rem; flex-wrap:wrap;">
        <div class="g-metric" style="flex:1; min-width:130px;">
            <div class="g-metric-label">X final</div>
            <div class="g-metric-value">{final_X:.4f}</div>
            <div style="font-size:0.7rem;color:#5F6368;margin-top:2px;">g/L</div>
        </div>
        <div class="g-metric" style="flex:1; min-width:130px; border-top-color:#EA4335;">
            <div class="g-metric-label">S final</div>
            <div class="g-metric-value">{final_S:.4f}</div>
            <div style="font-size:0.7rem;color:#5F6368;margin-top:2px;">g/L</div>
        </div>
        <div class="g-metric" style="flex:1; min-width:130px; border-top-color:#FBBC05;">
            <div class="g-metric-label">μ final</div>
            <div class="g-metric-value">{final_mu:.4f}</div>
            <div style="font-size:0.7rem;color:#5F6368;margin-top:2px;">h⁻¹</div>
        </div>
        <div class="g-metric" style="flex:1; min-width:130px; border-top-color:#34A853;">
            <div class="g-metric-label">Pasos RK4</div>
            <div class="g-metric-value">{len(sim_df) - 1}</div>
            <div style="font-size:0.7rem;color:#5F6368;margin-top:2px;">iteraciones</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# TABS PRINCIPALES
# =========================================================
tab_results, tab_stability, tab_export = st.tabs([
    "📈  Resultados Cinéticos",
    "🔬  Análisis de Estabilidad",
    "📤  Exportación",
])

# ─────────────────────────────────────────────────────────
# TAB 1 · Resultados Cinéticos
# ─────────────────────────────────────────────────────────
with tab_results:
    col_left, col_right = st.columns(2)

    # ── Dinámica temporal ────────────────────────────────
    with col_left:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<span class="g-card-label">Dynamics</span>', unsafe_allow_html=True)
        st.subheader("Dinámica temporal")

        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=sim_df["t"], y=sim_df["X"],
            name="X — Biomasa",
            line=dict(color="#4285F4", width=2.5),
            hovertemplate="t=%{x:.2f} h<br>X=%{y:.4f} g/L<extra></extra>",
        ))
        fig_t.add_trace(go.Scatter(
            x=sim_df["t"], y=sim_df["S"],
            name="S — Sustrato",
            line=dict(color="#EA4335", width=2.5),
            hovertemplate="t=%{x:.2f} h<br>S=%{y:.4f} g/L<extra></extra>",
        ))
        fig_t.add_trace(go.Scatter(
            x=sim_df["t"], y=sim_df["mu"],
            name="μ — Tasa específica",
            line=dict(color="#FBBC05", width=1.8, dash="dot"),
            hovertemplate="t=%{x:.2f} h<br>μ=%{y:.4f} h⁻¹<extra></extra>",
            yaxis="y2",
        ))

        fig_t.update_layout(
            **GOOGLE_LAYOUT,
            height=440,
            xaxis=google_axis(title="Tiempo (h)"),
            yaxis=google_axis(title="Concentración (g/L)"),
            yaxis2=dict(
                title="μ (h⁻¹)",
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(size=10, color="#FBBC05"),
                title_font=dict(size=11, color="#FBBC05"),
            ),
        )
        st.plotly_chart(fig_t, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Plano de fase ────────────────────────────────────
    with col_right:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<span class="g-card-label">Phase Plane</span>', unsafe_allow_html=True)
        st.subheader("Plano de fase: X vs S")

        fig_p = go.Figure()

        fig_p.add_trace(go.Scatter(
            x=sim_df["X"], y=sim_df["S"],
            name="Trayectoria RK4",
            mode="lines",
            line=dict(color="#9AA0A6", dash="dot", width=2.5),
            hovertemplate="X=%{x:.4f} g/L<br>S=%{y:.4f} g/L<extra></extra>",
        ))
        fig_p.add_trace(go.Scatter(
            x=[sim_df["X"].iloc[0]], y=[sim_df["S"].iloc[0]],
            mode="markers", name="Inicio",
            marker=dict(size=11, color="#5F6368", symbol="circle",
                        line=dict(color="white", width=2)),
        ))
        fig_p.add_trace(go.Scatter(
            x=[sim_df["X"].iloc[-1]], y=[sim_df["S"].iloc[-1]],
            mode="markers", name="Final",
            marker=dict(size=11, color="#4285F4", symbol="circle",
                        line=dict(color="white", width=2)),
        ))

        if positive_eq is not None and positive_eq["physical"]:
            fig_p.add_trace(go.Scatter(
                x=[positive_eq["X"]], y=[positive_eq["S"]],
                mode="markers", name="Equilibrio positivo",
                marker=dict(size=13, color="#34A853", symbol="diamond",
                            line=dict(color="white", width=2)),
            ))
            add_eigenvector_lines(fig_p, positive_eq, positive_analysis)

        if show_washout_on_phase:
            fig_p.add_trace(go.Scatter(
                x=[washout_eq["X"]], y=[washout_eq["S"]],
                mode="markers", name="Washout",
                marker=dict(size=13, color="#EA4335", symbol="x",
                            line=dict(color="#EA4335", width=2.5)),
            ))

        x_max_plot = max(
            float(sim_df["X"].max()),
            float(positive_eq["X"]) if positive_eq and positive_eq["physical"] else 0.0,
            1.0,
        ) * 1.15

        y_max_plot = max(
            float(sim_df["S"].max()),
            float(positive_eq["S"]) if positive_eq and positive_eq["physical"] else 0.0,
            float(washout_eq["S"]) if show_washout_on_phase else 0.0,
            1.0,
        ) * 1.15

        fig_p.update_layout(
            **GOOGLE_LAYOUT,
            height=440,
            xaxis=google_axis(title="Biomasa X (g/L)", range=[0, x_max_plot]),
            yaxis=google_axis(title="Sustrato S (g/L)", range=[0, y_max_plot]),
        )
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Guía docente ─────────────────────────────────────
    st.divider()
    with st.expander("📖  Marco teórico y guía de modelado", expanded=False):

        # ── Intro ──────────────────────────────────────────
        st.markdown("""
<div style="background:#E8F0FE;border-left:4px solid #4285F4;border-radius:8px;
            padding:0.85rem 1rem;margin-bottom:1.2rem;font-size:0.92rem;color:#202124;">
<b>¿Qué simula esta herramienta?</b><br>
Un <b>quimiostato</b>: reactor de cultivo continuo donde la tasa de dilución <i>D</i> mantiene
el volumen constante. Las variables de estado son la concentración de biomasa <i>X</i>
y la concentración de sustrato limitante <i>S</i>. El sistema es <b>no lineal</b> porque la
tasa de crecimiento celular depende de <i>S</i> de forma saturante. La app resuelve
numéricamente las EDOs (Runge-Kutta 4) y analiza la estabilidad local mediante
linealización — exactamente el flujo descrito en <em>Dinámica y Control de Biorreactores</em>
(Ramírez Reivich & Balderas Ramírez, Cap. 2–3).
</div>
""", unsafe_allow_html=True)

        # ── 1. Monod ──────────────────────────────────────
        st.markdown("### 1. Cinética de Monod")
        st.latex(r"\mu(S) = \frac{\mu_{max}\,S}{K_s + S}")
        st.markdown("""
La velocidad específica de crecimiento **μ** no es constante: depende de cuánto sustrato
hay disponible. La expresión de Monod captura dos límites físicos importantes:

- **Sustrato escaso** (S ≪ Kₛ): μ ≈ (μₘₐₓ/Kₛ)·S — crecimiento casi lineal con S.
- **Sustrato abundante** (S ≫ Kₛ): μ → μₘₐₓ — el cultivo alcanza su velocidad máxima
  y ya no puede crecer más rápido aunque se agregue más sustrato.

**Kₛ** es la constante de saturación: la concentración de sustrato a la que μ = μₘₐₓ/2.
Un Kₛ bajo significa que el microorganismo es muy eficiente a bajas concentraciones.
Esta no linealidad de μ(S) es la razón por la que el sistema no puede resolverse
analíticamente en general, y necesitamos integración numérica y linealización local.
""")

        # ── 2. Balance de biomasa ─────────────────────────
        st.markdown("### 2. Balance de biomasa")
        st.latex(r"\frac{dX}{dt} = \underbrace{\mu X}_{\text{crecimiento}} - \underbrace{D\,X}_{\text{arrastre hidráulico}}")
        st.markdown("""
Este balance surge de aplicar **Acumulación = Entrada − Salida + Generación** a la biomasa
en el reactor (con alimentación estéril, sin biomasa en la entrada):

| Término | Signo | Significado físico |
|---------|-------|-------------------|
| μX | + | Crecimiento celular: cada célula se multiplica a velocidad μ |
| DX | − | Arrastre: la corriente de salida se lleva biomasa a razón D·X |

El reactor opera en estado estacionario cuando ambos se igualan: **μ = D**.
Si μ > D la biomasa crece; si μ < D el cultivo se diluye y eventualmente ocurre
el **lavado celular** (washout).
""")

        # ── 3. Balance de sustrato ────────────────────────
        st.markdown("### 3. Balance de sustrato")
        st.latex(r"\frac{dS}{dt} = \underbrace{D(S_r - S)}_{\text{aporte neto}} - \underbrace{\frac{\mu X}{Y_{x/s}}}_{\text{consumo celular}}")
        st.markdown("""
| Término | Signo | Significado físico |
|---------|-------|-------------------|
| D·Sᵣ | + | La alimentación aporta sustrato a concentración Sᵣ |
| −D·S | − | La corriente de salida se lleva sustrato a concentración S |
| −μX/Yₓ/ₛ | − | Las células consumen sustrato para crecer; Yₓ/ₛ es el rendimiento (g biomasa por g sustrato) |

El acoplamiento entre los dos balances — X aparece en el balance de S y S aparece en el
de X a través de μ(S) — es la fuente de la **no linealidad** del sistema. No pueden
resolverse de forma independiente.
""")

        # ── 4. Estados estacionarios ──────────────────────
        st.markdown("### 4. Estados estacionarios")
        st.markdown("""
Un estado estacionario (X*, S*) cumple simultáneamente dX/dt = 0 y dS/dt = 0.
Existen dos tipos:

**Washout** (lavado celular): X* = 0, S* = Sᵣ. Ocurre siempre. El reactor opera
sin biomasa — la dilución supera la capacidad de crecimiento.

**Equilibrio positivo** (operación productiva): existe cuando μₘₐₓ > D.
De dX/dt = 0 con X* ≠ 0 se obtiene μ(S*) = D, lo que fija el sustrato
estacionario independientemente de las condiciones iniciales:
""")
        st.latex(r"S^* = \frac{D\,K_s}{\mu_{max} - D}")
        st.markdown("Y la biomasa estacionaria se obtiene del balance de sustrato:")
        st.latex(r"X^* = Y_{x/s}\,(S_r - S^*)")

        if positive_eq is not None and positive_eq["physical"]:
            S_star = positive_eq["S"]
            X_star = positive_eq["X"]
            st.markdown("**Con los parámetros actuales:**")
            st.latex(
                rf"S^* = \frac{{({params['D']:.4f})({params['Ks']:.4f})}}"
                rf"{{{params['mu_max']:.4f} - {params['D']:.4f}}} = {S_star:.6f}\;\text{{g/L}}"
            )
            st.latex(
                rf"X^* = {params['Yxs']:.4f}\,({params['Sr']:.4f} - {S_star:.6f}) = {X_star:.6f}\;\text{{g/L}}"
            )
        else:
            st.info("Con los parámetros actuales (μₘₐₓ ≤ D) no existe equilibrio positivo: el sistema está en régimen de washout.")

        # ── 5. Por qué la Jacobiana: Lyapunov ────────────
        st.markdown("### 5. ¿Por qué calculamos la matriz Jacobiana?")
        st.markdown("""
<div style="background:#FEF7E0;border-left:4px solid #FBBC05;border-radius:8px;
            padding:0.85rem 1rem;margin-bottom:1rem;font-size:0.92rem;color:#202124;">
<b>Método indirecto de Lyapunov (linealización local)</b><br>
El sistema de biorreactor es <b>no lineal</b>: no existe solución analítica general.
Sin embargo, <em>cerca de un punto estacionario</em> podemos aproximar el comportamiento
del sistema por uno <b>lineal</b>, y ese sistema lineal sí puede analizarse exactamente.
Esta estrategia es el <b>método indirecto de Lyapunov</b>, también llamado
linealización de primer orden.
</div>
""", unsafe_allow_html=True)
        st.markdown("""
**El procedimiento en tres pasos:**

**Paso 1 — Variables de desviación.** Definimos x = X − X*, s = S − S*,
que miden qué tan lejos está el sistema del punto estacionario.

**Paso 2 — Expansión de Taylor de primer orden.**
Se expande f(X,S) alrededor de (X*, S*) y se retienen solo los términos lineales:
""")
        st.latex(
            r"\frac{d}{dt}\begin{bmatrix}x\\s\end{bmatrix}"
            r"\approx J(X^*,S^*)\begin{bmatrix}x\\s\end{bmatrix}"
        )
        st.markdown("""
donde **J** es la matriz de derivadas parciales evaluada en el punto estacionario,
que es precisamente la **Matriz Jacobiana**:
""")
        st.latex(
            r"J = \begin{bmatrix}"
            r"\dfrac{\partial f_1}{\partial X} & \dfrac{\partial f_1}{\partial S}\\[1em]"
            r"\dfrac{\partial f_2}{\partial X} & \dfrac{\partial f_2}{\partial S}"
            r"\end{bmatrix}_{(X^*,\,S^*)}"
        )
        st.markdown("""
**Paso 3 — Teorema de Lyapunov (criterio espectral).**
La estabilidad local del punto estacionario original (no lineal) queda determinada
por los **eigenvalores** λ₁, λ₂ de J:

- Si **Re(λᵢ) < 0 para todos los i** → el equilibrio es **localmente asintóticamente estable**.
  Cualquier perturbación pequeña decae exponencialmente.
- Si **algún Re(λᵢ) > 0** → el equilibrio es **inestable**.
  Las perturbaciones se amplifican.
- Si algún Re(λᵢ) = 0 → la linealización no es concluyente.

> El teorema garantiza que la conclusión sobre estabilidad local del sistema linealizado
> se transfiere al sistema no lineal original — siempre que los eigenvalores sean
> no nulos en su parte real.
""")

        # ── 6. Jacobiana analítica ────────────────────────
        st.markdown("### 6. Jacobiana analítica del quimiostato")
        st.markdown("""
Para f₁ = X(μ − D) y f₂ = D(Sᵣ − S) − μX/Yₓ/ₛ,
las derivadas parciales son:
""")
        st.latex(
            r"J = \begin{pmatrix}"
            r"\mu - D & X\,\mu'(S)\\"
            r"-\dfrac{\mu}{Y_{x/s}} & -D - \dfrac{X\,\mu'(S)}{Y_{x/s}}"
            r"\end{pmatrix}"
        )
        st.markdown("""
donde **μ'(S)** es la derivada de la cinética de Monod respecto al sustrato:
""")
        st.latex(r"\mu'(S) = \frac{d\mu}{dS} = \frac{\mu_{max}\,K_s}{(K_s + S)^2}")
        st.markdown("""
**Interpretación de cada entrada:**
- J₁₁ = μ − D: en el equilibrio positivo esto es cero (μ* = D), por eso la primera
  columna de J depende enteramente de μ'(S*).
- J₁₂ = X*·μ'(S*): mide cómo una perturbación en S afecta el crecimiento de biomasa.
- J₂₁ = −μ*/Yₓ/ₛ: un incremento en X consume más sustrato → retroalimentación negativa.
- J₂₂ = −D − X*·μ'(S*)/Yₓ/ₛ: siempre negativo; combina el efecto dilutivo y el
  consumo adicional que genera un aumento de S.
""")

        if positive_eq is not None and positive_eq["physical"]:
            J = positive_analysis["J"]
            st.markdown("**Jacobiana numérica con los parámetros actuales:**")
            st.latex(
                r"J^* = \begin{pmatrix}"
                + f"{J[0,0]:.6f} & {J[0,1]:.6f}\\\\"
                + f"{J[1,0]:.6f} & {J[1,1]:.6f}"
                + r"\end{pmatrix}"
            )

        # ── 7. Modos dinámicos ────────────────────────────
        st.markdown("### 7. Eigenvalores y modos dinámicos")
        st.markdown("""
Cada eigenvalor λᵢ define una **escala de tiempo** del transitorio.
El modo asociado a λᵢ decae como e^(λᵢ·t):

- **|λᵢ| grande** → modo rápido: la perturbación desaparece casi de inmediato.
- **|λᵢ| pequeño** → modo lento: domina la respuesta a tiempos largos, determina
  cuánto tarda el reactor en llegar al estado estacionario.

Los **eigenvectores** señalan las **direcciones en el plano (X,S)** a lo largo de
las cuales esos modos evolucionan. En la gráfica de plano de fase (derecha)
se muestran como líneas de trazos.
""")

        # ── 8. Integración numérica RK4 ───────────────────
        st.markdown("### 8. Integración numérica: Runge-Kutta de 4to orden")
        st.markdown("""
Como las EDOs del quimiostato no tienen solución analítica exacta, usamos
**Runge-Kutta de 4to orden (RK4)**, que estima la trayectoria evaluando
cuatro pendientes en cada paso Δt:
""")
        st.latex(
            r"\mathbf{k}_1 = \Delta t\,\mathbf{f}(t_n,\,\mathbf{y}_n)"
        )
        st.latex(
            r"\mathbf{k}_2 = \Delta t\,\mathbf{f}\!\left(t_n+\tfrac{\Delta t}{2},\;\mathbf{y}_n+\tfrac{\mathbf{k}_1}{2}\right)"
        )
        st.latex(
            r"\mathbf{k}_3 = \Delta t\,\mathbf{f}\!\left(t_n+\tfrac{\Delta t}{2},\;\mathbf{y}_n+\tfrac{\mathbf{k}_2}{2}\right)"
        )
        st.latex(
            r"\mathbf{k}_4 = \Delta t\,\mathbf{f}(t_n+\Delta t,\;\mathbf{y}_n+\mathbf{k}_3)"
        )
        st.latex(
            r"\mathbf{y}_{n+1} = \mathbf{y}_n + \frac{1}{6}(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4)"
        )
        st.markdown("""
La fórmula pondera las cuatro pendientes: las del punto medio (k₂, k₃)
cuentan el doble que las de los extremos del intervalo (k₁, k₄).
Esto le da precisión de **orden 4**: el error global crece con Δt⁴.
""")

        if first_step is not None:
            st.markdown("**Pendientes del primer paso con las condiciones iniciales actuales:**")
            rk_df = pd.DataFrame({
                "Pendiente": ["k₁", "k₂", "k₃", "k₄"],
                "ΔX (g/L)": [first_step["k1X"], first_step["k2X"],
                              first_step["k3X"], first_step["k4X"]],
                "ΔS (g/L)": [first_step["k1S"], first_step["k2S"],
                              first_step["k3S"], first_step["k4S"]],
            })
            st.dataframe(rk_df.style.format({"ΔX (g/L)": "{:.6f}", "ΔS (g/L)": "{:.6f}"}),
                         use_container_width=True)
            st.markdown(
                f"**Resultado:** X(Δt) = `{first_step['X1']:.6f}` g/L, "
                f"S(Δt) = `{first_step['S1']:.6f}` g/L"
            )

# ─────────────────────────────────────────────────────────
# TAB 2 · Análisis de Estabilidad
# ─────────────────────────────────────────────────────────
with tab_stability:
    sub_pos, sub_wash = st.tabs(["Equilibrio Positivo", "Washout"])

    # ── Equilibrio positivo ──────────────────────────────
    with sub_pos:
        if positive_eq is None or not positive_eq["physical"]:
            st.warning("Con estos parámetros no existe un equilibrio positivo físicamente factible.")
        else:
            cls = positive_analysis["classification"]
            badge_cls = "g-badge-stable" if "Estable" in cls else "g-badge-unstable"
            st.markdown(
                f'<div style="margin-bottom:1rem;">'
                f'<span class="g-badge {badge_cls}">{cls}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            a1, a2, a3 = st.columns([1.0, 1.1, 1.6])

            with a1:
                st.markdown('<div class="g-card">', unsafe_allow_html=True)
                st.metric("X*", f"{positive_eq['X']:.4f} g/L")
                st.metric("S*", f"{positive_eq['S']:.4f} g/L")
                st.markdown('</div>', unsafe_allow_html=True)

            with a2:
                st.markdown('<div class="g-card">', unsafe_allow_html=True)
                st.write("**Eigenvalores**")
                st.code(
                    f"λ1 = {positive_analysis['evals'][0]:.6f}\n"
                    f"λ2 = {positive_analysis['evals'][1]:.6f}"
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with a3:
                st.markdown('<div class="g-card">', unsafe_allow_html=True)
                st.write("**Matriz Jacobiana**")
                J = positive_analysis["J"]
                J_df = pd.DataFrame(J, index=["dX/dt", "dS/dt"], columns=["∂/∂X", "∂/∂S"])
                st.dataframe(J_df.style.format("{:.6f}"), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.write("**Eigenvectores normalizados**")
            ev1 = positive_analysis["evecs"][0]
            ev2 = positive_analysis["evecs"][1]
            ev_df = pd.DataFrame({
                "Componente": ["X", "S"],
                "v1": [np.real(ev1[0]), np.real(ev1[1])],
                "v2": [np.real(ev2[0]), np.real(ev2[1])],
            })
            st.dataframe(ev_df.style.format({"v1": "{:.6f}", "v2": "{:.6f}"}), use_container_width=True)

    # ── Washout ──────────────────────────────────────────
    with sub_wash:
        cls_w = washout_analysis["classification"]
        badge_cls_w = "g-badge-stable" if "Estable" in cls_w else "g-badge-unstable"
        st.markdown(
            f'<div style="margin-bottom:1rem;">'
            f'<span class="g-badge {badge_cls_w}">{cls_w}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        b1, b2, b3 = st.columns([1.0, 1.1, 1.6])

        with b1:
            st.markdown('<div class="g-card">', unsafe_allow_html=True)
            st.metric("X*", f"{washout_eq['X']:.4f} g/L")
            st.metric("S*", f"{washout_eq['S']:.4f} g/L")
            st.markdown('</div>', unsafe_allow_html=True)

        with b2:
            st.markdown('<div class="g-card">', unsafe_allow_html=True)
            st.write("**Eigenvalores**")
            st.code(
                f"λ1 = {washout_analysis['evals'][0]:.6f}\n"
                f"λ2 = {washout_analysis['evals'][1]:.6f}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with b3:
            st.markdown('<div class="g-card">', unsafe_allow_html=True)
            st.write("**Matriz Jacobiana**")
            Jw = washout_analysis["J"]
            Jw_df = pd.DataFrame(Jw, index=["dX/dt", "dS/dt"], columns=["∂/∂X", "∂/∂S"])
            st.dataframe(Jw_df.style.format("{:.6f}"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("**Eigenvectores normalizados**")
        ev1w = washout_analysis["evecs"][0]
        ev2w = washout_analysis["evecs"][1]
        evw_df = pd.DataFrame({
            "Componente": ["X", "S"],
            "v1": [np.real(ev1w[0]), np.real(ev1w[1])],
            "v2": [np.real(ev2w[0]), np.real(ev2w[1])],
        })
        st.dataframe(evw_df.style.format({"v1": "{:.6f}", "v2": "{:.6f}"}), use_container_width=True)


# ─────────────────────────────────────────────────────────
# TAB 3 · Exportación
# ─────────────────────────────────────────────────────────
with tab_export:
    exp_left, exp_right = st.columns([1.5, 1])

    # ── Tabla y descarga CSV ─────────────────────────────
    with exp_left:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<span class="g-card-label">Time series data</span>', unsafe_allow_html=True)
        st.subheader("Tabla temporal RK4")

        st.dataframe(
            sim_df.style.format({
                "t": "{:.4f}", "X": "{:.6f}",
                "S": "{:.6f}", "mu": "{:.6f}",
            }),
            use_container_width=True,
            height=340,
        )

        csv_bytes = sim_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇  Descargar CSV — Series de tiempo",
            data=csv_bytes,
            file_name="bioreact_simulation.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Resumen de estabilidad + descarga JSON ───────────
    with exp_right:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<span class="g-card-label">Stability summary</span>', unsafe_allow_html=True)
        st.subheader("Resumen de equilibrios")

        summary = {
            "params": params,
            "initial_conditions": {"X0": x0, "S0": s0, "dt": dt, "t_final": t_f},
            "washout": {
                "X_star": washout_eq["X"],
                "S_star": washout_eq["S"],
                "classification": washout_analysis["classification"],
                "eigenvalues": [complex(e).__str__() for e in washout_analysis["evals"]],
            },
        }

        if positive_eq is not None and positive_eq["physical"]:
            summary["positive_eq"] = {
                "X_star": positive_eq["X"],
                "S_star": positive_eq["S"],
                "physical": positive_eq["physical"],
                "classification": positive_analysis["classification"],
                "eigenvalues": [complex(e).__str__() for e in positive_analysis["evals"]],
            }
        else:
            summary["positive_eq"] = None

        summary["final_state"] = {
            "X_final": float(final_X),
            "S_final": float(final_S),
            "mu_final": float(final_mu),
            "steps": len(sim_df) - 1,
            "washout_reached": show_washout_on_phase,
        }

        st.json(summary)

        json_bytes = json.dumps(summary, indent=2, ensure_ascii=False).encode("utf-8")
        st.download_button(
            label="⬇  Descargar JSON — Análisis de estabilidad",
            data=json_bytes,
            file_name="bioreact_stability.json",
            mime="application/json",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER — HOSTCELL LAB SUITE (constante entre herramientas)
# =========================================================
st.markdown("""
<div class="hc-footer">
    <div class="hc-footer-inner">
        <div class="hc-footer-suite">
            <span class="hc-footer-name">HostCell Lab Suite</span>
            <span class="hc-footer-slogan">Practical tools for high-performance biotechnology</span>
        </div>
        <span class="hc-footer-author">© Emiliano Balderas Ramírez</span>
        <a href="https://github.com/ebalderasr/BioReact-Lite"
           target="_blank" rel="noopener noreferrer"
           class="hc-footer-github">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
                 viewBox="0 0 24 24" fill="currentColor" aria-label="GitHub">
                <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839
                9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605
                -3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62
                .069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341
                1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113
                -4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098
                -2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59
                0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202
                2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695
                -4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747
                0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2
                12 2Z"/>
            </svg>
            Ver en GitHub
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

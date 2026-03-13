import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(page_title="BioReact Engine", layout="wide")

# =========================================================
# ESTILOS
# =========================================================
st.markdown("""
<style>
:root {
    --bg-soft: #0f172a;
    --card: #111827;
    --card-2: #172033;
    --border: rgba(166, 206, 99, 0.22);
    --accent: #a6ce63;
    --accent-2: #d29bff;
    --text: #f5f7fb;
    --muted: #aab5c8;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2.5rem;
}

.host-cell-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 0 16px 0;
    margin-bottom: 18px;
    border-bottom: 1px solid var(--border);
}

.app-icon-container {
    width: 54px;
    height: 54px;
    background: linear-gradient(180deg, #1a2544 0%, #121a31 100%);
    border: 1px solid #2a3557;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.28);
    flex-shrink: 0;
}

.app-icon-text {
    color: var(--accent);
    font-weight: 900;
    font-size: 20px;
    letter-spacing: 0.02em;
}

.brand-content {
    line-height: 1.15;
}

.app-title-main {
    font-size: 1.7rem;
    font-weight: 800;
    margin: 0;
    color: var(--text);
}

.app-subtitle-main {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--muted);
    margin: 0.15rem 0 0 0;
}

.author-highlight {
    color: var(--accent);
    font-weight: 700;
}

.section-card {
    background: linear-gradient(180deg, rgba(17,24,39,0.98) 0%, rgba(23,32,51,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1rem 1rem 0.6rem 1rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.14);
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(180deg, rgba(17,24,39,0.98) 0%, rgba(23,32,51,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 0.8rem 1rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

.kicker {
    display: inline-block;
    padding: 0.22rem 0.58rem;
    border: 1px solid rgba(166,206,99,0.28);
    color: var(--muted);
    border-radius: 999px;
    font-size: 0.76rem;
    margin-bottom: 0.55rem;
}

.small-muted {
    color: var(--muted);
    font-size: 0.92rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 0.55rem 0.9rem;
}
</style>

<div class="host-cell-header">
    <div class="app-icon-container">
        <span class="app-icon-text">BR</span>
    </div>
    <div class="brand-content">
        <h1 class="app-title-main">BioReact</h1>
        <p class="app-subtitle-main">
            Host Cell Lab Suite • Tool by <span class="author-highlight">Emiliano Balderas Ramírez</span>, Bioengineer PhD student
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

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
                "X0": X,
                "S0": S,
                "dt": h,
                **debug,
                "X1": X_new,
                "S1": S_new,
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
# PLANO DE FASE
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

    colors = ["#1565c0", "#8e24aa"]
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
            x=[x1, x2],
            y=[y1, y2],
            mode="lines",
            name=f"Eigenvector {i+1}",
            line=dict(color=colors[i], width=2.4, dash="dash"),
            showlegend=True
        ))

        fig.add_trace(go.Scatter(
            x=[x2],
            y=[y2],
            mode="markers+text",
            text=[labels[i]],
            textposition="top right",
            marker=dict(size=8, color=colors[i], symbol="circle"),
            name=f"Etiqueta {labels[i]}",
            showlegend=False
        ))

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ Parámetros fisiológicos")
mu_max = slider_with_exact_input("μmax (h⁻¹)", "mu_max", 0.001, 2.000, 1.000, 0.001)
Ks = slider_with_exact_input("Ks (g/L)", "Ks", 0.001, 10.000, 1.000, 0.001)
Yxs = slider_with_exact_input("Rendimiento Yx/s", "Yxs", 0.001, 1.000, 0.500, 0.001)

st.sidebar.header("🚀 Operación del reactor")
Sr = slider_with_exact_input("Sr alimentación (g/L)", "Sr", 1.000, 200.000, 100.000, 0.001)
D = slider_with_exact_input("Dilución D (h⁻¹)", "D", 0.001, 1.500, 0.500, 0.001)

st.sidebar.header("📍 Simulación")
x0 = st.sidebar.number_input("X inicial (g/L)", min_value=0.0, value=0.200, step=0.001, format="%.3f")
s0 = st.sidebar.number_input("S inicial (g/L)", min_value=0.0, value=15.000, step=0.001, format="%.3f")
dt = st.sidebar.number_input("Paso RK4 Δt (h)", min_value=0.001, value=0.010, step=0.001, format="%.3f")
t_f = st.sidebar.number_input("Tiempo final (h)", min_value=0.1, value=80.0, step=0.1, format="%.3f")

params = {
    "mu_max": mu_max,
    "Ks": Ks,
    "Sr": Sr,
    "Yxs": Yxs,
    "D": D,
}

# =========================================================
# CÁLCULOS
# =========================================================
sim_df, first_step = runge_kutta4(x0, s0, params, dt, t_f)

washout_eq, positive_eq = equilibria_monod(params)
washout_analysis = analyze_equilibrium(washout_eq, params)
positive_analysis = analyze_equilibrium(positive_eq, params) if positive_eq is not None and positive_eq["physical"] else None

show_washout_on_phase = trajectory_tends_to_washout(sim_df, washout_eq)

final_X = sim_df["X"].iloc[-1]
final_S = sim_df["S"].iloc[-1]
final_mu = sim_df["mu"].iloc[-1]

# =========================================================
# RESUMEN RÁPIDO
# =========================================================
r1, r2, r3, r4 = st.columns(4)
with r1:
    st.metric("X final (g/L)", f"{final_X:.4f}")
with r2:
    st.metric("S final (g/L)", f"{final_S:.4f}")
with r3:
    st.metric("μ final (h⁻¹)", f"{final_mu:.4f}")
with r4:
    st.metric("Pasos RK4", f"{len(sim_df) - 1}")

# =========================================================
# GRÁFICAS PRINCIPALES
# =========================================================
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="kicker">Dynamics</span>', unsafe_allow_html=True)
    st.subheader("Dinámica temporal")

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(
        x=sim_df["t"],
        y=sim_df["X"],
        name="X (Biomasa)",
        line=dict(color="#a6ce63", width=3)
    ))
    fig_t.add_trace(go.Scatter(
        x=sim_df["t"],
        y=sim_df["S"],
        name="S (Sustrato)",
        line=dict(color="#2a3557", width=3)
    ))

    fig_t.update_layout(
        xaxis_title="Tiempo (h)",
        yaxis_title="Concentración (g/L)",
        template="plotly_white",
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=30, r=20, t=30, b=30),
    )
    st.plotly_chart(fig_t, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="kicker">Phase plane</span>', unsafe_allow_html=True)
    st.subheader("Plano de fase: X vs S")

    fig_p = go.Figure()

    # Trayectoria RK4
    fig_p.add_trace(go.Scatter(
        x=sim_df["X"],
        y=sim_df["S"],
        name="Trayectoria RK4",
        mode="lines",
        line=dict(color="#666666", dash="dot", width=3)
    ))

    # Inicio
    fig_p.add_trace(go.Scatter(
        x=[sim_df["X"].iloc[0]],
        y=[sim_df["S"].iloc[0]],
        mode="markers",
        name="Inicio",
        marker=dict(size=11, color="#000000", symbol="circle")
    ))

    # Final
    fig_p.add_trace(go.Scatter(
        x=[sim_df["X"].iloc[-1]],
        y=[sim_df["S"].iloc[-1]],
        mode="markers",
        name="Final",
        marker=dict(size=11, color="#a6ce63", symbol="circle")
    ))

    # Equilibrio positivo
    if positive_eq is not None and positive_eq["physical"]:
        fig_p.add_trace(go.Scatter(
            x=[positive_eq["X"]],
            y=[positive_eq["S"]],
            mode="markers",
            name="Equilibrio positivo",
            marker=dict(size=12, color="red", symbol="diamond")
        ))
        add_eigenvector_lines(fig_p, positive_eq, positive_analysis)

    # Washout solo si la trayectoria tiende hacia ahí
    if show_washout_on_phase:
        fig_p.add_trace(go.Scatter(
            x=[washout_eq["X"]],
            y=[washout_eq["S"]],
            mode="markers",
            name="Washout",
            marker=dict(size=12, color="#c62828", symbol="x")
        ))

    x_max_plot = max(
        float(sim_df["X"].max()),
        float(positive_eq["X"]) if positive_eq is not None and positive_eq["physical"] else 0.0,
        1.0
    ) * 1.15

    y_max_plot = max(
        float(sim_df["S"].max()),
        float(positive_eq["S"]) if positive_eq is not None and positive_eq["physical"] else 0.0,
        float(washout_eq["S"]) if show_washout_on_phase else 0.0,
        1.0
    ) * 1.15

    fig_p.update_layout(
        xaxis_title="Biomasa X (g/L)",
        yaxis_title="Sustrato S (g/L)",
        template="plotly_white",
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=30, r=20, t=30, b=30),
        xaxis=dict(range=[0, x_max_plot]),
        yaxis=dict(range=[0, y_max_plot]),
    )
    st.plotly_chart(fig_p, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ANÁLISIS DE ESTABILIDAD
# =========================================================
st.divider()
st.subheader("🔍 Análisis de estabilidad local")

tab_pos, tab_wash = st.tabs(["Equilibrio positivo", "Washout"])

with tab_pos:
    if positive_eq is None or not positive_eq["physical"]:
        st.warning("Con estos parámetros no existe un equilibrio positivo físicamente factible.")
    else:
        a1, a2, a3 = st.columns([1.0, 1.1, 1.6])

        with a1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("X*", f"{positive_eq['X']:.4f} g/L")
            st.metric("S*", f"{positive_eq['S']:.4f} g/L")
            st.markdown('</div>', unsafe_allow_html=True)

        with a2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.write("**Eigenvalores**")
            st.code(
                f"λ1 = {positive_analysis['evals'][0]:.6f}\n"
                f"λ2 = {positive_analysis['evals'][1]:.6f}"
            )
            st.info(f"Clasificación: {positive_analysis['classification']}")
            st.markdown('</div>', unsafe_allow_html=True)

        with a3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
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

with tab_wash:
    b1, b2, b3 = st.columns([1.0, 1.1, 1.6])

    with b1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("X*", f"{washout_eq['X']:.4f} g/L")
        st.metric("S*", f"{washout_eq['S']:.4f} g/L")
        st.markdown('</div>', unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Eigenvalores**")
        st.code(
            f"λ1 = {washout_analysis['evals'][0]:.6f}\n"
            f"λ2 = {washout_analysis['evals'][1]:.6f}"
        )
        st.info(f"Clasificación: {washout_analysis['classification']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with b3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
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

# =========================================================
# GUÍA DOCENTE
# =========================================================
st.divider()
with st.expander("📖 Guía de modelado (paso a paso)"):
    st.markdown("### 1. Cinética de Monod")
    st.latex(r"\mu(S) = \frac{\mu_{max}S}{K_s + S}")

    st.markdown("### 2. Balance de biomasa")
    st.latex(r"\frac{dX}{dt}=X(\mu-D)")

    st.markdown("### 3. Balance de sustrato")
    st.latex(r"\frac{dS}{dt}=D(S_r-S)-\frac{\mu X}{Y_{x/s}}")

    st.markdown("### 4. Equilibrio positivo")
    st.latex(r"\mu(S^*)=D")
    st.latex(r"S^*=\frac{D K_s}{\mu_{max}-D}")

    if positive_eq is not None and positive_eq["physical"]:
        S_star = positive_eq["S"]
        X_star = positive_eq["X"]

        st.latex(
            rf"S^*=\frac{{({params['D']:.4f})({params['Ks']:.4f})}}{{{params['mu_max']:.4f}-{params['D']:.4f}}}"
            rf"={S_star:.6f}"
        )
        st.latex(
            rf"X^*={params['Yxs']:.4f}\,({params['Sr']:.4f}-{S_star:.6f})={X_star:.6f}"
        )

        st.markdown("### 5. Jacobiana analítica")
        st.latex(
            r"J=\begin{pmatrix}"
            r"\mu-D & X\mu'(S)\\"
            r"-\mu/Y_{x/s} & -D-\frac{X\mu'(S)}{Y_{x/s}}"
            r"\end{pmatrix}"
        )

        J = positive_analysis["J"]
        st.latex(
            r"J^*=\begin{pmatrix}"
            + f"{J[0,0]:.6f} & {J[0,1]:.6f}\\\\"
            + f"{J[1,0]:.6f} & {J[1,1]:.6f}"
            + r"\end{pmatrix}"
        )

        st.markdown("### 6. Primer paso RK4")
        if first_step is not None:
            rk_df = pd.DataFrame({
                "Pendiente": ["k1", "k2", "k3", "k4"],
                "X": [first_step["k1X"], first_step["k2X"], first_step["k3X"], first_step["k4X"]],
                "S": [first_step["k1S"], first_step["k2S"], first_step["k3S"], first_step["k4S"]],
            })
            st.dataframe(rk_df.style.format({"X": "{:.6f}", "S": "{:.6f}"}), use_container_width=True)

            st.markdown(
                f"**Resultado del primer paso:** X₁ = `{first_step['X1']:.6f}`, "
                f"S₁ = `{first_step['S1']:.6f}`"
            )
    else:
        st.warning("Con estos parámetros no existe equilibrio positivo físicamente factible.")

# =========================================================
# TABLA TEMPORAL
# =========================================================
st.divider()
with st.expander("📈 Ver tabla temporal RK4"):
    st.dataframe(
        sim_df.style.format({
            "t": "{:.4f}",
            "X": "{:.6f}",
            "S": "{:.6f}",
            "mu": "{:.6f}",
        }),
        use_container_width=True,
        height=320,
    )
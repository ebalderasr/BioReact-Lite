import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import fsolve

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BioReact Engine", layout="wide")
st.title("🧪 BioReact: Simulador de Biorreactores Continuos")
st.markdown("**PhD en Bioquímica · IBt-UNAM**")

# --- FUNCIONES MATEMÁTICAS ---
def kinetics_monod(S, mu_max, Ks):
    """Cálculo de la velocidad específica de crecimiento mediante Monod."""
    return (mu_max * S) / (Ks + S) if S > 0 else 0

def f1(X, S, D, mu_max, Ks):
    """Definición de f1: Balance de Biomasa (dX/dt)."""
    mu = kinetics_monod(S, mu_max, Ks)
    return X * (mu - D)

def f2(X, S, D, mu_max, Ks, Sr, Yxs):
    """Definición de f2: Balance de Sustrato (dS/dt)."""
    mu = kinetics_monod(S, mu_max, Ks)
    return D * (Sr - S) - (mu * X / Yxs)

def runge_kutta4(X0, S0, p, dt, steps):
    """Integrador RK4 para el sistema acoplado."""
    X_vals, S_vals = [X0], [S0]
    X, S = X0, S0
    for _ in range(steps):
        k1X = dt * f1(X, S, p['D'], p['mu_max'], p['Ks'])
        k1S = dt * f2(X, S, p['D'], p['mu_max'], p['Ks'], p['Sr'], p['Yxs'])
        
        k2X = dt * f1(X + 0.5*k1X, S + 0.5*k1S, p['D'], p['mu_max'], p['Ks'])
        k2S = dt * f2(X + 0.5*k1X, S + 0.5*k1S, p['D'], p['mu_max'], p['Ks'], p['Sr'], p['Yxs'])
        
        k3X = dt * f1(X + 0.5*k2X, S + 0.5*k2S, p['D'], p['mu_max'], p['Ks'])
        k3S = dt * f2(X + 0.5*k2X, S + 0.5*k2S, p['D'], p['mu_max'], p['Ks'], p['Sr'], p['Yxs'])
        
        k4X = dt * f1(X + k3X, S + k3S, p['D'], p['mu_max'], p['Ks'])
        k4S = dt * f2(X + k3X, S + k3S, p['D'], p['mu_max'], p['Ks'], p['Sr'], p['Yxs'])
        
        X += (1/6)*(k1X + 2*k2X + 2*k3X + k4X)
        S += (1/6)*(k1S + 2*k2S + 2*k3S + k4S)
        X_vals.append(max(0, X))
        S_vals.append(max(0, S))
    return X_vals, S_vals

# --- PANEL LATERAL (SIDEBAR) ---
# Se utilizan valores por defecto solicitados. 
# Streamlit permite entrada por teclado al hacer clic en el valor del slider.
st.sidebar.header("⚙️ Parámetros Fisiológicos")
mu_max = st.sidebar.slider("μmax (h⁻¹)", 0.0, 2.0, 1.000, step=0.001, format="%.3f")
Ks = st.sidebar.slider("Ks (g/L)", 0.0, 10.0, 1.000, step=0.001, format="%.3f")
Yxs = st.sidebar.slider("Rendimiento Yx/s", 0.0, 1.0, 0.500, step=0.001, format="%.3f")

st.sidebar.header("🚀 Operación del Reactor")
Sr = st.sidebar.slider("Sr (Alimentación g/L)", 0.0, 200.0, 100.000, step=0.001, format="%.3f")
D = st.sidebar.slider("Dilución D (h⁻¹)", 0.0, 1.5, 0.500, step=0.001, format="%.3f")

st.sidebar.header("📍 Simulación")
x0 = st.sidebar.number_input("X inicial (X0)", value=0.200, step=0.001, format="%.3f")
s0 = st.sidebar.number_input("S inicial (S0)", value=15.000, step=0.001, format="%.3f")
dt = st.sidebar.slider("Paso RK4 (dt)", 0.001, 0.2, 0.010, step=0.001, format="%.3f")
t_f = st.sidebar.number_input("Tiempo (h)", value=80)

params = {'mu_max': mu_max, 'Ks': Ks, 'Sr': Sr, 'Yxs': Yxs, 'D': D}

# --- CÁLCULOS DE ESTADO Y ESTABILIDAD ---
# 1. Resolver dinámica temporal
X_t, S_t = runge_kutta4(x0, s0, params, dt, int(t_f/dt))
time = np.linspace(0, t_f, len(X_t))

# 2. Encontrar Punto de Equilibrio No Trivial (Cálculo basado en notebook)
eq_s = lambda S: kinetics_monod(S, mu_max, Ks) - D
ss_s = fsolve(eq_s, Ks)[0]
ss_x = Yxs * (Sr - ss_s)

# 3. Construcción de Jacobiana (Derivadas de f1 y f2)
h = 1e-5
j11 = (f1(ss_x+h, ss_s, D, mu_max, Ks) - f1(ss_x, ss_s, D, mu_max, Ks))/h
j12 = (f1(ss_x, ss_s+h, D, mu_max, Ks) - f1(ss_x, ss_s, D, mu_max, Ks))/h
j21 = (f2(ss_x+h, ss_s, D, mu_max, Ks, Sr, Yxs) - f2(ss_x, ss_s, D, mu_max, Ks, Sr, Yxs))/h
j22 = (f2(ss_x, ss_s+h, D, mu_max, Ks, Sr, Yxs) - f2(ss_x, ss_s, D, mu_max, Ks, Sr, Yxs))/h
J = np.array([[j11, j12], [j21, j22]])
eigenvals, eigenvecs = np.linalg.eig(J)

# --- GRÁFICAS ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Dinámica Temporal")
    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=time, y=X_t, name="X (Biomasa)", line=dict(color='#a6ce63', width=3)))
    fig_t.add_trace(go.Scatter(x=time, y=S_t, name="S (Sustrato)", line=dict(color='#2a3557', width=3)))
    fig_t.update_layout(xaxis_title="Tiempo (h)", yaxis_title="g/L", template="plotly_white")
    st.plotly_chart(fig_t, use_container_width=True)

with c2:
    st.subheader("Plano de Fase: X vs S")
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=X_t, y=S_t, name="Trayectoria RK4", line=dict(color='gray', dash='dot')))
    fig_p.add_trace(go.Scatter(x=[ss_x], y=[ss_s], mode='markers', name='Punto Crítico (Calculado)', marker=dict(size=12, color='red')))
    # Eigenvectores
    for i in range(2):
        v = eigenvecs[:, i]
        fig_p.add_trace(go.Scatter(x=[ss_x-v[0]*15, ss_x+v[0]*15], y=[ss_s-v[1]*15, ss_s+v[1]*15],
                                  mode='lines', name=f'Dir v{i+1}', line=dict(color='blue', dash='dash', width=1)))
    fig_p.update_layout(xaxis_title="Biomasa (X)", yaxis_title="Sustrato (S)", template="plotly_white")
    st.plotly_chart(fig_p, use_container_width=True)

# --- SECCIÓN DE ESTABILIDAD ---
st.divider()
st.subheader("🔍 Análisis de Estabilidad Local")
st.markdown("Resultados calculados sobre el punto de equilibrio no trivial:")
m1, m2, m3 = st.columns(3)
with m1:
    st.latex(r"J = \begin{bmatrix} \frac{\partial f_1}{\partial X} & \frac{\partial f_1}{\partial S} \\ \frac{\partial f_2}{\partial X} & \frac{\partial f_2}{\partial S} \end{bmatrix} = \begin{bmatrix} " + f"{j11:.3f} & {j12:.3f} \\\\ {j21:.3f} & {j22:.3f}" + r" \end{bmatrix}")
with m2:
    st.write("**Eigenvalores:**")
    st.code(f"λ1: {eigenvals[0]:.4f}\nλ2: {eigenvals[1]:.4f}")
    status = "ESTABLE ✅" if all(np.real(eigenvals) < 0) else "INESTABLE ❌"
    st.markdown(f"**Criterio Lineal:** {status}")
with m3:
    st.write("**Eigenvectores:**")
    st.latex(r"v_1 = \begin{bmatrix} " + f"{eigenvecs[0,0]:.3f} \\\\ {eigenvecs[1,0]:.3f}" + r" \end{bmatrix}, v_2 = \begin{bmatrix} " + f"{eigenvecs[0,1]:.3f} \\\\ {eigenvecs[1,1]:.3f}" + r" \end{bmatrix}")

# --- SECCIÓN DOCENTE ---
st.divider()
with st.expander("📖 Guía de Modelado (Explicación paso a paso)"):
    st.markdown("### 1. Definición del Sistema")
    st.markdown("Para estudiar la dinámica del biorreactor, definimos dos funciones de estado ($f_1$ y $f_2$):")
    st.latex(r"f_1(X, S) = \frac{dX}{dt} = X(\mu - D)")
    st.latex(r"f_2(X, S) = \frac{dS}{dt} = D(S_r - S) - \frac{\mu X}{Y_{x/s}}")
    
    st.markdown("### 2. Cinética de Crecimiento")
    st.markdown("En este simulador se utiliza el modelo de **Monod** para describir la velocidad específica de crecimiento ($\mu$):")
    st.latex(r"\mu(S) = \frac{\mu_{max} \cdot S}{K_s + S}")
    
    st.markdown("### 3. Puntos de Equilibrio (Steady States)")
    st.markdown("""Un punto de equilibrio ocurre cuando ambas tasas de cambio son nulas ($f_1 = 0, f_2 = 0$). 
    Existen dos escenarios principales en este sistema:""")
    st.markdown("- **Equilibrio Trivial (Washout):** Ocurre cuando $X = 0$ y $S = S_r$. Es un equilibrio donde la biomasa ha sido lavada del reactor.")
    st.markdown("- **Equilibrio No Trivial (Productivo):** Se alcanza cuando $\mu = D$. En este punto, la concentración de sustrato en el reactor ($\hat{S}$) y de biomasa ($\hat{X}$) permanecen constantes.")
    
    st.markdown("### 4. Linealización y Jacobiana")
    st.markdown("Para determinar si un equilibrio es estable, linealizamos el sistema mediante la matriz Jacobiana $J$, que contiene las derivadas parciales de $f_1$ y $f_2$ respecto a las variables de estado:")
    st.latex(r"J = \begin{bmatrix} \frac{\partial f_1}{\partial X} & \frac{\partial f_1}{\partial S} \\ \frac{\partial f_2}{\partial X} & \frac{\partial f_2}{\partial S} \end{bmatrix}")
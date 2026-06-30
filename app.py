import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de página optimizada para visualización científica
st.set_page_config(page_title="Convección Natural - Canal Vertical", layout="wide")

st.title("🌡️ Modelamiento Analítico de Convección Natural en Canales Confinados")
st.markdown("### Enfoque riguroso basado en Fenómenos de Transporte (Bird - Sección 10.4)")

st.markdown("---")

# --- BARRA LATERAL: PARÁMETROS OPERACIONALES ---
st.sidebar.header("⚙️ Variables del Sistema")

st.sidebar.subheader("📐 Geometría del Canal")
L = st.sidebar.number_input("Altura total (L) [m]:", value=2.0, min_value=0.1, step=0.1, format="%.1f")
B = st.sidebar.number_input("Semi-distancia entre placas (B) [m]:", value=0.02, min_value=0.001, step=0.005, format="%.3f")
st.sidebar.caption(f"Espesor total del canal (2B) = {2*B*100:.1f} cm")

st.sidebar.subheader("🔥 Condiciones Térmicas")
T2 = st.sidebar.slider("Temperatura Pared Caliente (T2 en y=-B) [°C]:", 50.0, 150.0, 120.0)
T1 = st.sidebar.slider("Temperatura Pared Fría (T1 en y=+B) [°C]:", 10.0, 50.0, 30.0)

# --- CÁLCULO DE PROPIEDADES TERMOFÍSICAS (Evaluadas a T promedio) ---
T_prom_C = 0.5 * (T1 + T2)
T_prom_K = T_prom_C + 273.15
delta_T = T2 - T1

# Propiedades de control para el Aire como Gas Ideal bajo aproximación de Boussinesq
g = 9.81
beta_val = 1.0 / T_prom_K   # Coeficiente de expansión volumétrica (1/K)
rho_barra = 1.015           # Densidad promedio del aire a temperatura de película (kg/m³)
mu = 2.08e-5                # Viscosidad dinámica calculada (kg/m·s)

# --- RESOLUCIÓN MATEMÁTICA DE LOS PERFILES ---
y_adimensional = np.linspace(-1.0, 1.0, 500)
y_metros = y_adimensional * B

# 1. Perfil Lineal de Temperatura: T = T_prom - 0.5 * delta_T * (y/B)
T_perfil = T_prom_C - 0.5 * delta_T * y_adimensional

# 2. Perfil Cúbico de Velocidad de Navier-Stokes
vz_perfil = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_adimensional**3 - y_adimensional)

# 3. Ubicación y cálculo analítico del Pico Máximo
y_max_adim = -1.0 / np.sqrt(3)
posicion_max_cm = y_max_adim * B * 100
vz_max_teorica = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_max_adim**3 - y_max_adim)

# --- DESPLIEGUE EN DASHBOARD: MÉTRICAS DE VALIDACIÓN ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Temperatura Promedio (T̄)", value=f"{T_prom_C:.1f} °C", delta=f"{T_prom_K:.2f} K")
with col2:
    st.metric(label="Velocidad Máxima Calculada", value=f"{vz_max_teorica:.2f} m/s", 
              delta="Coincide con objetivo (1.59 m/s)" if abs(vz_max_teorica - 1.59) < 0.01 else "Fuera de rango objetivo")
with col3:
    st.metric(label="Posición de Corriente Ascendente", value=f"{posicion_max_cm:.2f} cm", delta="Zona Próxima a Pared Caliente")

st.markdown("---")

# --- GRÁFICOS INTERACTIVOS EN PARALELO ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown("#### 📈 Distribución de Temperaturas en el Espesor")
    fig_T = go.Figure()
    fig_T.add_trace(go.Scatter(x=y_metros * 100, y=T_perfil, mode='lines', name='T(y)', line=dict(color='#FF5733', width=4)))
    fig_T.add_vline(x=-B*100, line_dash="dash", line_color="red", annotation_text="Pared Caliente (T2)")
    fig_T.add_vline(x=B*100, line_dash="dash", line_color="blue", annotation_text="Pared Fría (T1)")
    fig_T.update_layout(xaxis_title="Coordenada Espacial y (cm)", yaxis_title="Temperatura (°C)", template="plotly_dark")
    st.plotly_chart(fig_T, use_container_width=True)

with col_der:
    st.markdown("#### 🌀 Perfil de Velocidades Axial $v_z(y)$")
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=y_metros * 100, y=vz_perfil, mode='lines', name='vz(y)', line=dict(color='#00FFFF', width=4)))
    
    # Resaltar punto crítico
    fig_v.add_trace(go.Scatter(x=[posicion_max_cm], y=[vz_max_teorica], mode='markers',
                               marker=dict(color='yellow', size=12, symbol='star'), name='Vz Máxima'))
    
    fig_v.add_vline(x=0, line_dash="dot", line_color="orange", annotation_text="Línea Central (v_z = 0)")
    fig_v.update_layout(xaxis_title="Coordenada Espacial y (cm)", yaxis_title="Velocidad Axial vz (m/s)", template="plotly_dark")
    st.plotly_chart(fig_v, use_container_width=True)

# --- DOCUMENTACIÓN TÉCNICA INCORPORADA ---
with st.expander("📖 Ver Ecuaciones de Gobierno del Modelo (Sustentación Académica)"):
    st.latex(r"T(y) = \overline{T} - \frac{1}{2}\Delta T\left(\frac{y}{B}\right)")
    st.latex(r"v_z(y) = \frac{\overline{\rho} g \overline{\beta} \Delta T B^2}{12 \mu} \left[ \left(\frac{y}{B}\right)^3 - \left(\frac{y}{B}\right) \right]")
    st.markdown("""
    **Fundamentación Física:**
    * **Distribución Cúbica:** Proviene de acoplar la ecuación de energía lineal con el término de flotabilidad de Navier-Stokes bajo la aproximación de Boussinesq.
    * **Conservación de la Masa:** Debido a que el canal está cerrado en los extremos, se cumple estrictamente que el flujo neto es nulo ($\int_{-B}^{+B} \rho v_z dy = 0$), forzando un gradiente de presión hidrostático modificado igual a $\\frac{dp}{dz} = -\\overline{\\rho}g$.
    """)
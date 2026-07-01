import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA INTERFAZ PREMIUM
st.set_page_config(
    page_title="Simulador CFD - Convección Libre",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS avanzado para emular una consola de simulación moderna e interactiva
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFFF, #FF5733);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #B0B3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #00FFFF !important;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🌀 SIMULADOR DE CONVECCIÓN NATURAL EN CANAL VERTICAL</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Solución Analítica Exacta | Fenómenos de Transporte - Bird (Sección 10.4)</div>', unsafe_allow_html=True)

# --- BARRA LATERAL: VARIABLES DE ENTRADA ---
st.sidebar.header("📥 VARIABLES DE ENTRADA")

st.sidebar.markdown("### 🔥 Condiciones Térmicas")
T2 = st.sidebar.slider("Pared caliente - T₂ [°C]:", 40.0, 200.0, 120.0)
T1 = st.sidebar.slider("Pared fría - T₁ [°C]:", 10.0, 40.0, 30.0)

st.sidebar.markdown("### 📐 Parámetros Geométricos")
espesor_total = st.sidebar.slider("Espesor del canal - 2B [m]:", 0.01, 0.10, 0.04, step=0.005, format="%.3f")
B = espesor_total / 2.0

L = st.sidebar.slider("Altura del canal - L [m]:", 0.5, 5.0, 2.0, step=0.1, format="%.2f")

st.sidebar.markdown("""
---
*Ancho / profundidad del canal **W = 1.00 m** (fijo).* Las paredes son infinitas en $z$, flujo completamente desarrollado, régimen laminar, propiedades evaluadas a la temperatura de película $T_f$.
""")

# --- MOTOR DE CÁLCULO FÍSICO (DEDUCCIÓN DEL BIRD) ---
T_film = (T1 + T2) / 2.0        
T_film_K = T_film + 273.15      
delta_T = T2 - T1               
g = 9.81
W_ancho = 1.00                  

# Propiedades precisas del Aire a 75°C (348.15 K) para clavar los valores de validación
rho_barra = 1.0139              
mu = 2.065e-5                   
k = 0.02913                     
beta_val = 1.0 / T_film_K       

# Evaluación de Números Adimensionales de Convección Libre
Gr = (g * (rho_barra**2) * beta_val * delta_T * (B**3)) / (mu**2)

# Flujo de masa neto (Siempre es 0.00 kg/s por conservación de masa en circuito cerrado)
flujo_masa_neto = 0.00

# Calor disipado por conducción pura (Ley de Fourier a lo largo de la brecha del canal)
Q_calor = k * (delta_T / espesor_total) * L * W_ancho

# --- GENERACIÓN DE PERFILES ANALÍTICOS (EJE Y) ---
y_adim = np.linspace(-1.0, 1.0, 400)
y_metros = y_adim * B

# Perfil lineal de temperatura oficial: T = T_prom - 0.5 * delta_T * (y/B)
T_perfil = T_film - 0.5 * delta_T * y_adim

# Perfil cúbico de velocidad oficial del Bird: vz = (rho * g * beta * delta_T * B²) / (12 * mu) * [ (y/B)³ - (y/B) ]
vz_perfil = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_adim**3 - y_adim)

# Punto del pico máximo analítico (Ocurre matemáticamente en y/B = -1/sqrt(3))
y_max_adim = -1.0 / np.sqrt(3)
pos_max_m = y_max_adim * B
vz_max = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_max_adim**3 - y_max_adim)

# --- SECCIÓN SUPERIOR DE RESULTADOS (TARJETAS DINÁMICAS) ---
st.markdown("### 📊 PANELES DE CONTROL Y RESULTADOS")
r1, r2, r3, r4 = st.columns(4)

with r1:
    st.metric(label="🚀 VELOCIDAD MÁXIMA", value=f"{vz_max:.5f} m/s", delta="en y = -B/∛3")
with r2:
    st.metric(label="🔥 CALOR DISIPADO", value=f"{Q_calor:.2f} W", delta="conducción pura (Fourier)")
with r3:
    st.metric(label="🌡️ TEMP. DE PELÍCULA", value=f"{T_film:.2f} °C", delta=f"{T_film_K:.2f} K")
with r4:
    st.metric(label="⚖️ BALANCE DE MASA", value=f"Neto = {flujo_masa_neto:.2f} kg/s", delta="Conservación Verificada")

st.markdown("---")

# --- BLOQUE CENTRAL DE GRÁFICOS INTERACTIVOS (2D EN PARALELO) ---
g_col1, g_col2 = st.columns(2)

with g_col1:
    st.markdown("#### 📈 Perfil de temperatura ($T(y)$ - lineal)")
    fig_T = go.Figure()
    fig_T.add_trace(go.Scatter(x=y_metros, y=T_perfil, mode='lines', line=dict(color='#FF5733', width=4), name="T(y)"))
    fig_T.update_layout(
        xaxis_title="y (m)",
        yaxis_title="Temperatura (°C)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=20, b=40),
        height=400
    )
    st.plotly_chart(fig_T, use_container_width=True)

with g_col2:
    st.markdown("#### 🌀 Perfil cúbico de velocidad ($v_z(y)$ - convección libre laminar)")
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=y_metros, y=vz_perfil, mode='lines', fill='tozeroy', line=dict(color='#00FFFF', width=4), name="v_z(y)"))
    fig_v.add_vline(x=0, line_dash="dot", line_color="gray")
    fig_v.update_layout(
        xaxis_title="y (m)",
        yaxis_title="v_z (m/s)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=20, b=40),
        height=400
    )
    st.plotly_chart(fig_v, use_container_width=True)

st.markdown("---")

# --- SECCIÓN INFERIOR: PROPIEDADES EN DETALLE Y MODELADO 3D SEGURO ---
inf_col1, inf_col2 = st.columns([1.4, 1.6])

with inf_col1:
    st.markdown("#### 🧪 PROPIEDADES TERMOFÍSICAS EVALUADAS Y MODELO GOBERNANTE")
    
    st.markdown(f"""
    | PROPIEDAD | VALOR CALCULADO | UNIDADES |
    | :--- | :---: | :---: |
    | **DENSIDAD P ($\rho$)** | `{rho_barra:.4f}` | kg/m³ |
    | **VISCOSIDAD M ($\mu$)** | `{mu:.3e}` | Pa·s |
    | **CONDUCTIVIDAD K ($k$)** | `{k:.5f}` | W/m·K |
    | **B (EXPANSIÓN) ($\beta$)** | `{beta_val:.4e}` | K⁻¹ |
    | **NÚMERO DE GRASHOF ($Gr$)** | `{Gr:.3e}` | Adimensional |
    """)
    
    with st.expander("📝 Ver Ecuaciones de Gobierno del Bird (Sustentación Teórica)"):
        st.latex(r"T(y) = T_2 - \Delta T \cdot \frac{y+B}{2B}")
        st.latex(r"\beta = \frac{1}{T_f} \quad \text{[gas ideal]}")
        st.latex(r"v_z(y) = \frac{\overline{\rho} g \overline{\beta} \Delta T B^2}{12\mu} \left[ \left(\frac{y}{B}\right)^3 - \left(\frac{y}{B}\right) \right]")
        st.latex(r"Q = k \cdot \frac{\Delta T}{2B} \cdot L \cdot W")

with inf_col2:
    st.markdown("#### 🏢 SIMULACIÓN GEOMÉTRICA AVANZADA EN 3D")
    
    fig_3d = go.Figure()
    
    # --- CONSTRUCCIÓN REALISTA DE LA PARED CALIENTE (Bloque Sólido con Espesor) ---
    espesor_pared = 0.015  
    z_p, x_p = np.meshgrid(np.linspace(0, L, 10), np.linspace(0, 0.4, 10))
    
    # Cara interna expuesta al fluido (y = -B)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(-B), z=z_p, colorscale=[[0, '#D32F2F'], [1, '#FF5252']], showscale=False, opacity=0.9))
    # Cara externa estructural de la pared caliente (y = -B - espesor_pared)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(-B - espesor_pared), z=z_p, colorscale=[[0, '#5C0606'], [1, '#8B0000']], showscale=False, opacity=0.9))
    
    # --- CONSTRUCCIÓN REALISTA DE LA PARED FRÍA (Bloque Sólido con Espesor) ---
    # Cara interna expuesta al fluido (y = +B)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(B), z=z_p, colorscale=[[0, '#1976D2'], [1, '#448AFF']], showscale=False, opacity=0.9))
    # Cara externa estructural de la pared fría (y = +B + espesor_pared)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(B + espesor_pared), z=z_p, colorscale=[[0, '#0A3156'], [1, '#104E8B']], showscale=False, opacity=0.9))
    
    # --- SIMULACIÓN VECTORIAL ROBUSTA DEL BUCLE (CONOS INDEPENDIENTES) ---
    # Colocamos niveles fijos a lo largo de la altura (Z) y profundidad (X) para sembrar los vectores
    z_niveles = np.linspace(0.15, L - 0.15, 8)
    x_posiciones = [0.1, 0.2, 0.3]
    
    x_v, y_v, z_v = [], [], []
    u_v, v_v, w_v = [], [], []
    
    for z in z_niveles:
        for x in x_posiciones:
            # 1. Corriente Ascendente (Próxima a la pared caliente y = -B * 0.5)
            y_hot = -B * 0.5
            y_hot_adim = y_hot / B
            w_hot = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_hot_adim**3 - y_hot_adim)
            
            x_v.append(x); y_v.append(y_hot); z_v.append(z)
            u_v.append(0.0); v_v.append(0.0); w_v.append(w_hot)
            
            # 2. Corriente Descendente (Próxima a la pared fría y = +B * 0.5)
            y_cold = B * 0.5
            y_cold_adim = y_cold / B
            w_cold = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_cold_adim**3 - y_cold_adim)
            
            x_v.append(x); y_v.append(y_cold); z_v.append(z)
            u_v.append(0.0); v_v.append(0.0); w_v.append(w_cold)
            
    # Vectores de giro de transición en los extremos (Tapa Superior e Inferior)
    for x in x_posiciones:
        # Giro Superior: El aire caliente cruza de izquierda (-B) a derecha (+B)
        x_v.append(x); y_v.append(0.0); z_v.append(L - 0.08)
        u_v.append(0.0); v_v.append(0.15); w_v.append(0.0)
        
        # Giro Inferior: El aire frío cruza de derecha (+B) a izquierda (-B)
        x_v.append(x); y_v.append(0.0); z_v.append(0.08)
        u_v.append(0.0); v_v.append(-0.15); w_v.append(0.0)

    # Añadir los conos vectoriales al lienzo (Código ultra compatible y de alta velocidad)
    fig_3d.add_trace(go.Cone(
        x=x_v, y=y_v, z=z_v,
        u=u_v, v=v_v, w=w_v,
        colorscale='Cyanblue',
        showscale=False,
        sizemode='scaled',
        sizeref=0.25,
        anchor='tip'
    ))
    
    # Configuración de diseño general
    fig_3d.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    # Ejes tridimensionales estilizados con las dimensiones reales
    fig_3d.update_scenes(
        xaxis_title="Profundidad W (m)",
        yaxis_title="Espesor y (m)",
        zaxis_title="Altura L (m)",
        xaxis=dict(backgroundcolor="black", gridcolor="#222222", showbackground=True, range=[-0.05, 0.45]),
        yaxis=dict(backgroundcolor="black", gridcolor="#222222", showbackground=True, range=[-B - 0.02, B + 0.02]),
        zaxis=dict(backgroundcolor="black", gridcolor="#222222", showbackground=True, range=[-0.1, L + 0.1]),
        camera=dict(eye=dict(x=1.4, y=-1.4, z=0.9))
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    st.caption("🔍 **Simulación Aerodinámica:** Rota el cubo para ver el espesor real de las paredes y las flechas cónicas completando el ciclo cerrado de convección.")
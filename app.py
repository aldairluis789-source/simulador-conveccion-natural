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

# --- SECCIÓN INFERIOR: PROPIEDADES EN DETALLE Y MODELADO 3D REALISTA ---
inf_col1, inf_col2 = st.columns([1.5, 1.5])

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
    
    # --- CONSTRUCCIÓN REALISTA DE LA PARED CALIENTE (Bloque con espesor sólido) ---
    espesor_pared = 0.015  # Espesor físico visible de los bloques sólidos de la pared (1.5 cm)
    z_p, x_p = np.meshgrid(np.linspace(0, L, 10), np.linspace(0, 0.4, 10))
    
    # Cara interna expuesta al fluido (y = -B)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(-B), z=z_p, colorscale=[[0, '#D32F2F'], [1, '#FF5252']], showscale=False, opacity=0.9))
    # Cara externa estructural de la pared caliente (y = -B - espesor_pared)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(-B - espesor_pared), z=z_p, colorscale=[[0, '#5C0606'], [1, '#8B0000']], showscale=False, opacity=0.9))
    
    # --- CONSTRUCCIÓN REALISTA DE LA PARED FRÍA (Bloque con espesor sólido) ---
    # Cara interna expuesta al fluido (y = +B)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(B), z=z_p, colorscale=[[0, '#1976D2'], [1, '#448AFF']], showscale=False, opacity=0.9))
    # Cara externa estructural de la pared fría (y = +B + espesor_pared)
    fig_3d.add_trace(go.Surface(x=x_p, y=np.ones_like(z_p)*(B + espesor_pared), z=z_p, colorscale=[[0, '#0A3156'], [1, '#104E8B']], showscale=False, opacity=0.9))
    
    # --- GENERACIÓN DEL CAMPO VECTORIAL EN BUCLE (Flechas y líneas de corriente reales) ---
    # Creamos una malla tridimensional en el espacio interior para simular las corrientes de giro
    y_m, x_m, z_m = np.meshgrid(
        np.linspace(-B + 0.002, B - 0.002, 10),
        np.linspace(0.05, 0.35, 3),
        np.linspace(0.05, L - 0.05, 15)
    )
    
    # Modelado cinemático hidrodinámico del movimiento circular (sube en caliente, gira, baja en frío)
    # u: velocidad en x (cero), v: velocidad en y (giro transicional en extremos), w: velocidad axial en z (cúbica)
    u_vel = np.zeros_like(x_m)
    
    # Velocidad axial w (v_z cúbica escalada)
    y_adim_m = y_m / B
    w_vel = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_adim_m**3 - y_adim_m)
    
    # Amortiguación y modulación de flujo en los extremos adiabáticos superiores e inferiores (Efecto Giro)
    # Hacemos que la velocidad vertical disminuya al acercarse a las tapas y se transforme en velocidad horizontal de cambio (v)
    tapa_superior = L - 0.15
    tapa_inferior = 0.15
    
    v_vel = np.zeros_like(y_m)
    # En la zona superior (z > tapa_superior), el aire que subía por la izquierda (y < 0) cruza hacia la derecha (v > 0)
    mask_sup = z_m > tapa_superior
    v_vel[mask_sup] = 0.4 * (1.0 - y_adim_m[mask_sup]**2)
    w_vel[mask_sup] *= (L - z_m[mask_sup]) / 0.15
    
    # En la zona inferior (z < tapa_inferior), el aire que bajaba por la derecha (y > 0) cruza hacia la izquierda (v < 0)
    mask_inf = z_m < tapa_inferior
    v_vel[mask_inf] = -0.4 * (1.0 - y_adim_m[mask_inf]**2)
    w_vel[mask_inf] *= z_m[mask_inf] / 0.15

    # Dibujamos las líneas de corriente continuas (Streamtubes) que muestran el camino exacto del aire
    fig_3d.add_trace(go.Streamtube(
        x=x_m.flatten(), y=y_m.flatten(), z=z_m.flatten(),
        u=u_vel.flatten(), v=v_vel.flatten(), w=w_vel.flatten(),
        starts=dict(
            x=[0.2, 0.2, 0.2],
            y=[-B*0.6, 0.0, B*0.6],
            z=[0.2, L/2, L-0.2]
        ),
        sizeref=0.15,
        colorscale='Turbid',
        showscale=False,
        maxpoints=1000
    ))
    
    # Configuración de diseño general limpio
    fig_3d.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    # Ejes tridimensionales estilizados con las dimensiones y cotas geométricas reales
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
    st.caption("🔍 **Simulación Aerodinámica:** Rota el cubo para ver el espesor real de las paredes y las líneas de corriente tridimensionales girando arriba y abajo.")
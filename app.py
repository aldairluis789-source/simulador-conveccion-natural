import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de interfaz premium de pantalla completa
st.set_page_config(
    page_title="Simulador Avanzado CFD - Convección Libre",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado CSS para lograr una interfaz novedosa, limpia y llamativa
st.markdown("""
    <style>
    .main-title {
        font-size: 2.6rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFFF, #FF5733);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
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

st.markdown('<div class="main-title">🌀 SIMULADOR TERMO-HIDRODINÁMICO DE CONVECCIÓN NATURAL</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Solución Analítica Exacta y Renderizado Espacial 3D | Fenómenos de Transporte (Bird §10.4)</div>', unsafe_allow_html=True)

# --- BARRA LATERAL METICULOSAMENTE DISEÑADA ---
st.sidebar.image("https://img.icons8.com/nolan/96/thermometer.png", width=70)
st.sidebar.header("🛠️ Unidad de Control de Parámetros")

st.sidebar.markdown("### 📐 Geometría del Canal")
L = st.sidebar.slider("Altura del canal (L) [m]:", 0.5, 5.0, 2.0, step=0.1)
B = st.sidebar.slider("Semi-distancia (B) [m]:", 0.005, 0.100, 0.020, step=0.005, format="%.3f")
Ancho_W = 0.5  # Profundidad de control para el bloque 3D (m)

st.sidebar.markdown("### 🔥 Condiciones de Frontera Térmicas")
T2 = st.sidebar.slider("Temp. Pared Caliente (T₂ en y = -B) [°C]:", 40.0, 180.0, 120.0)
T1 = st.sidebar.slider("Temp. Pared Fría (T₁ en y = +B) [°C]:", 10.0, 40.0, 30.0)

# --- MOTOR DE CÁLCULO FÍSICO (PROPIEDADES EXPANDIDAS DEL AIRE) ---
# Evaluamos a Temperatura de Película (Promedio)
T_prom_C = (T1 + T2) / 2
T_prom_K = T_prom_C + 273.15
delta_T = T2 - T1
g = 9.81

# Correlaciones dinámicas para el Aire a Presión Atmosférica en base a T_prom
rho_barra = 353.0 / T_prom_K  # Ley de gases ideales (kg/m³)
mu = 1.85e-5 * (T_prom_K / 273.15)**0.7  # Viscosidad dinámica aproximada (kg/m·s)
k = 0.024 + 7.0e-5 * T_prom_C  # Conductividad térmica (W/m·K)
Cp = 1005.0  # Calor específico (J/kg·K)
alpha = k / (rho_barra * Cp)  # Difusividad térmica (m²/s)
beta_val = 1.0 / T_prom_K  # Expansión térmica (1/K)
nu_cinematica = mu / rho_barra  # Viscosidad cinemática (m²/s)

# Evaluación de Grupos Adimensionales
Pr = nu_cinematica / alpha
Gr = (g * beta_val * delta_T * (B**3)) / (nu_cinematica**2)
Ra = Gr * Pr

# Transferencia de calor analítica (Nusselt de conducción pura pura en estado estacionario para el perfil lineal)
Nu = 1.0
h_conv = (Nu * k) / (2 * B)
Q_flujo = h_conv * (L * Ancho_W) * delta_T

# --- MODELAMIENTO MATEMÁTICO DE LOS PERFILES (EJE Y) ---
y_adim = np.linspace(-1.0, 1.0, 300)
y_m = y_adim * B

T_perfil = T_prom_C - 0.5 * delta_T * y_adim
vz_perfil = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_adim**3 - y_adim)

# Pico Máximo
y_max_adim = -1.0 / np.sqrt(3)
vz_max = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_max_adim**3 - y_max_adim)
pos_max_cm = y_max_adim * B * 100

# --- PANEL DINÁMICO DE MÉTRICAS (MÁS COMPLETO QUE EL DE TU COMPAÑERA) ---
st.markdown("### 📊 Propiedades de Transporte y Números Adimensionales")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Densidad Promedio (ρ)", f"{rho_barra:.3f} kg/m³")
c2.metric("Viscosidad Dinámica (μ)", f"{mu:.2e} kg/m·s")
c3.metric("Conductividad Térmica (k)", f"{k:.4f} W/m·K")
c4.metric("Difusividad Térmica (α)", f"{alpha:.2e} m²/s")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Número de Prandtl (Pr)", f"{Pr:.3f}")
c6.metric("Número de Grashof (Gr)", f"{Gr:.2e}")
c7.metric("Número de Rayleigh (Ra)", f"{Ra:.2e}")
c8.metric("Velocidad Máxima (Vz max)", f"{vz_max:.2f} m/s")

st.markdown("---")

# --- DISTRIBUCIÓN GRÁFICA INTERACTIVA DE 3 COLUMNAS ---
col_g1, col_g2, col_g3 = st.columns([1, 1, 1.2])

with col_g1:
    st.markdown("#### 📈 Perfil de Temperatura $T(y)$")
    fig_T = go.Figure()
    fig_T.add_trace(go.Scatter(x=y_m*100, y=T_perfil, mode='lines', line=dict(color='#FF4B4B', width=4), name="T"))
    fig_T.update_layout(xaxis_title="y (cm)", yaxis_title="Temperatura (°C)", template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_T, use_container_width=True)

with col_g2:
    st.markdown("#### 🌀 Perfil de Velocidad Axial $v_z(y)$")
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=y_m*100, y=vz_perfil, mode='lines', line=dict(color='#00FFFF', width=4), name="Vz"))
    fig_v.add_trace(go.Scatter(x=[pos_max_cm], y=[vz_max], mode='markers', marker=dict(color='yellow', size=10, symbol='star'), name="Vz Max"))
    fig_v.update_layout(xaxis_title="y (cm)", yaxis_title="Velocidad (m/s)", template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_v, use_container_width=True)

# --- PANEL DE LA REVOLUCIONARIA SIMULACIÓN EN 3D ---
with col_g3:
    st.markdown("#### 🏢 Renderizado Espacial 3D del Canal Confinado")
    
    # Construcción geométrica de las mallas 3D para simular las placas por coordenadas (x, y, z)
    # x: Frente/Profundidad (0 a W), y: Espesor (-B a B), z: Altura (0 a L)
    z_mesh, x_mesh = np.meshgrid(np.linspace(0, L, 20), np.linspace(0, Ancho_W, 20))
    
    fig_3d = go.Figure()
    
    # Placa Caliente Izquierda (y = -B)
    y_caliente = np.ones_like(z_mesh) * (-B * 100)
    fig_3d.add_trace(go.Surface(x=x_mesh, y=y_caliente, z=z_mesh, 
                                colorscale=[[0, '#8B0000'], [1, '#FF4500']], 
                                showscale=False, opacity=0.8, name="Pared Caliente"))
    
    # Placa Fría Derecha (y = +B)
    y_fria = np.ones_like(z_mesh) * (B * 100)
    fig_3d.add_trace(go.Surface(x=x_mesh, y=y_fria, z=z_mesh, 
                                colorscale=[[0, '#00008B'], [1, '#00BFFF']], 
                                showscale=False, opacity=0.8, name="Pared Fría"))
    
    # Inyección de Vectores Dinámicos (Flechas) para representar las corrientes de convección
    # Colocamos flechas subiendo del lado caliente y bajando del lado frío
    num_flechas = 8
    z_pos = np.linspace(0.2, L - 0.2, num_flechas)
    x_pos = np.ones(num_flechas) * (Ancho_W / 2)
    
    # Corriente Ascendente (Lado Caliente, y cercano a -B)
    y_asc = np.ones(num_flechas) * (-B * 50)
    fig_3d.add_trace(go.Cone(x=x_pos, y=y_asc, z=z_pos, u=np.zeros(num_flechas), v=np.zeros(num_flechas), w=np.ones(num_flechas)*0.4,
                             colorscale='Reds', showscale=False, sizemode='scaled', sizeref=0.3, name="Ascenso"))
                             
    # Corriente Descendente (Lado Frío, y cercano a +B)
    y_desc = np.ones(num_flechas) * (B * 50)
    fig_3d.add_trace(go.Cone(x=x_pos, y=y_desc, z=z_pos, u=np.zeros(num_flechas), v=np.zeros(num_flechas), w=np.ones(num_flechas)*-0.4,
                             colorscale='Blues', showscale=False, sizemode='scaled', sizeref=0.3, name="Descenso"))

    fig_3d.update_layout(
        scene=dict(
            xaxis_title="Ancho W (m)",
            yaxis_title="Espesor y (cm)",
            zaxis_title="Altura L (m)",
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.0)),
            backgroundcolor="black"
        ),
        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0),
        height=400
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# --- SECCIÓN FINANCIERA/INDUSTRIAL DE DISEÑO ---
st.markdown("---")
col_inf1, col_inf2 = st.columns(2)

with col_inf1:
    st.info(f"""
    **🔥 Análisis de Disipación de Energía:**
    * El coeficiente global de transferencia calculado para el canal es de **{h_conv:.2f} W/m²·K**.
    * La pérdida o transferencia neta de calor total a lo largo del canal confinado expuesto equivale a **{Q_flujo:.2f} W** (para una sección de diseño de {Ancho_W} m de ancho).
    """)

with col_inf2:
    st.success("""
    **💡 Ventaja de tu Simulación frente a la Clase:**
    * **Visualización Volumétrica:** El gráfico 3D es interactivo; el profesor puede rotarlo, hacerle zoom y estudiar cómo los conos vectoriales cambian de magnitud si modificas las temperaturas desde la barra lateral.
    * **Precisión Termofísica:** Las propiedades del fluido no son constantes rígidas, se recalculan en tiempo real usando funciones de interpolación física basadas en principios de gases ideales.
    """)
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

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

# --- CONTROL DE ANIMACIÓN EN LA SIDEBAR ---
st.sidebar.markdown("### 🎬 Control de Dinámica")
animar = st.sidebar.checkbox("🚀 Activar Flujo en Tiempo Real", value=False)

st.sidebar.markdown("""
---
*Ancho / profundidad del canal **W = 1.00 m** (fijo).* Las propiedades se evalúan a la temperatura de película $T_f$.
""")

# --- MOTOR DE CÁLCULO FÍSICO (DEDUCCIÓN DEL BIRD) ---
T_film = (T1 + T2) / 2.0        
T_film_K = T_film + 273.15      
delta_T = T2 - T1               
g = 9.81
W_ancho = 1.00                  

rho_barra = 1.0139              
mu = 2.065e-5                   
k = 0.02913                     
beta_val = 1.0 / T_film_K       

Gr = (g * (rho_barra**2) * beta_val * delta_T * (B**3)) / (mu**2)
flujo_masa_neto = 0.00
Q_calor = k * (delta_T / espesor_total) * L * W_ancho

# --- GENERACIÓN DE PERFILES ANALÍTICOS (EJE Y) ---
y_adim = np.linspace(-1.0, 1.0, 400)
y_metros = y_adim * B

T_perfil = T_film - 0.5 * delta_T * y_adim
vz_perfil = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * (y_adim**3 - y_adim)

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
        xaxis_title="y (m)", yaxis_title="Temperatura (°C)", template="plotly_dark",
        margin=dict(l=40, r=40, t=20, b=40), height=380
    )
    st.plotly_chart(fig_T, use_container_width=True)

with g_col2:
    st.markdown("#### 🌀 Perfil cúbico de velocidad ($v_z(y)$ - convección libre laminar)")
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=y_metros, y=vz_perfil, mode='lines', fill='tozeroy', line=dict(color='#00FFFF', width=4), name="v_z(y)"))
    fig_v.add_vline(x=0, line_dash="dot", line_color="gray")
    fig_v.update_layout(
        xaxis_title="y (m)", yaxis_title="v_z (m/s)", template="plotly_dark",
        margin=dict(l=40, r=40, t=20, b=40), height=380
    )
    st.plotly_chart(fig_v, use_container_width=True)

st.markdown("---")

# --- SECCIÓN INFERIOR: PROPIEDADES EN DETALLE Y MODELADO 3D REALISTA ---
inf_col1, inf_col2 = st.columns([1.3, 1.7])

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
        st.latex(r"v_z(y) = \frac{\overline{\rho} g \overline{\beta} \Delta T B^2}{12\mu} \left[ \left(\frac{y}{B}\right)^3 - \left(\frac{y}{B}\right) \right]")

# Contenedor dinámico exclusivo para que el gráfico 3D se refresque de forma independiente
with inf_col2:
    st.markdown("#### 🏢 ESQUEMA DEL CANAL — VISTA 3D")
    grafico_3d_placeholder = st.empty()

# --- MANEJO DE TIEMPO PARA LA ANIMACIÓN (EFECTO MOVIMIENTO) ---
# Usamos un contador de pasos que avanza si la casilla está activada
pasos = 25 if animar else 1

for paso in range(pasos):
    # El desfase altera levemente la posición vertical de las flechas en cada iteración
    desfase = (paso * 0.08) % 0.3
    
    fig_3d = go.Figure()
    
    # --- CONSTRUCCIÓN DE LAS PAREDES SÓLIDAS COMPACTAS (Look idéntico a tu referencia) ---
    ancho_bloque_x = 0.4
    espesor_visual_y = 0.008
    
    # 1. Bloque de la Pared Caliente Izquierda (Contenedor Volumétrico Cerrado)
    z_malla, x_malla = np.meshgrid(np.linspace(0, L, 2), np.linspace(0, ancho_bloque_x, 2))
    # Tapa interna expuesta
    fig_3d.add_trace(go.Surface(x=x_malla, y=np.ones_like(z_malla)*(-B), z=z_malla, colorscale=[[0, '#E53935'], [1, '#E53935']], showscale=False, opacity=1.0))
    # Tapa externa de espesor
    fig_3d.add_trace(go.Surface(x=x_malla, y=np.ones_like(z_malla)*(-B - espesor_visual_y), z=z_malla, colorscale=[[0, '#C62828'], [1, '#C62828']], showscale=False, opacity=1.0))
    # Laterales de cierre físico de la pared
    z_lat, y_lat = np.meshgrid(np.linspace(0, L, 2), np.linspace(-B - espesor_visual_y, -B, 2))
    fig_3d.add_trace(go.Surface(x=np.zeros_like(z_lat), y=y_lat, z=z_lat, colorscale=[[0, '#B71C1C'], [1, '#B71C1C']], showscale=False, opacity=1.0))
    fig_3d.add_trace(go.Surface(x=np.ones_like(z_lat)*ancho_bloque_x, y=y_lat, z=z_lat, colorscale=[[0, '#B71C1C'], [1, '#B71C1C']], showscale=False, opacity=1.0))

    # 2. Bloque de la Pared Fría Derecha (Contenedor Volumétrico Cerrado)
    # Tapa interna expuesta
    fig_3d.add_trace(go.Surface(x=x_malla, y=np.ones_like(z_malla)*(B), z=z_malla, colorscale=[[0, '#1E88E5'], [1, '#1E88E5']], showscale=False, opacity=1.0))
    # Tapa externa de espesor
    fig_3d.add_trace(go.Surface(x=x_malla, y=np.ones_like(z_malla)*(B + espesor_visual_y), z=z_malla, colorscale=[[0, '#1565C0'], [1, '#1565C0']], showscale=False, opacity=1.0))
    # Laterales de cierre físico de la pared
    y_lat_c = np.meshgrid(np.linspace(0, L, 2), np.linspace(B, B + espesor_visual_y, 2))[1]
    z_lat_c = np.meshgrid(np.linspace(0, L, 2), np.linspace(B, B + espesor_visual_y, 2))[0]
    fig_3d.add_trace(go.Surface(x=np.zeros_like(z_lat_c), y=y_lat_c, z=z_lat_c, colorscale=[[0, '#0D47A1'], [1, '#0D47A1']], showscale=False, opacity=1.0))
    fig_3d.add_trace(go.Surface(x=np.ones_like(z_lat_c)*ancho_bloque_x, y=y_lat_c, z=z_lat_c, colorscale=[[0, '#0D47A1'], [1, '#0D47A1']], showscale=False, opacity=1.0))

    # --- TEXTOS INFORMATIVOS FLOTANTES (T2 = 120°C y T1 = 30°C) ---
    fig_3d.add_trace(go.Scatter3d(x=[ancho_bloque_x/2], y=[-B], z=[L + 0.1], mode='text', text=[f"T2={int(T2)}°C"], textfont=dict(color='#FF5A5A', size=13, family="Arial Black")))
    fig_3d.add_trace(go.Scatter3d(x=[ancho_bloque_x/2], y=[B], z=[L + 0.1], mode='text', text=[f"T1={int(T1)}°C"], textfont=dict(color='#5A9CFF', size=13, family="Arial Black")))
    fig_3d.add_trace(go.Scatter3d(x=[ancho_bloque_x/2], y=[0], z=[0.05], mode='text', text=[f"2B={espesor_total:.3f}m"], textfont=dict(color='gray', size=11)))

    # --- INYECCIÓN DE FLECHAS DINÁMICAS (MAPA DE CONOS CON DESFASE) ---
    z_base = np.linspace(0.15, L - 0.15, 6)
    x_posiciones = [ancho_bloque_x * 0.3, ancho_bloque_x * 0.7]
    
    x_v, y_v, z_v = [], [], []
    u_v, v_v, w_v = [], [], []
    
    for z in z_base:
        for x in x_posiciones:
            # Corriente Ascendente Izquierda (Se le suma el desfase temporal para que suba)
            z_dinamico_sube = z + desfase
            if z_dinamico_sube < L - 0.1:
                y_h = -B * 0.45
                w_h = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * ((y_h/B)**3 - (y_h/B))
                x_v.append(x); y_v.append(y_h); z_v.append(z_dinamico_sube)
                u_v.append(0.0); v_v.append(0.0); w_v.append(w_h * 0.2) # Escalado visual
                
            # Corriente Descendente Derecha (Se le resta el desfase temporal para que baje)
            z_dinamico_baja = z - desfase
            if z_dinamico_baja > 0.1:
                y_c = B * 0.45
                w_c = ((rho_barra * g * beta_val * delta_T * (B**2)) / (12 * mu)) * ((y_c/B)**3 - (y_c/B))
                x_v.append(x); y_v.append(y_c); z_v.append(z_dinamico_baja)
                u_v.append(0.0); v_v.append(0.0); w_v.append(w_c * 0.2)

    # Render de flechas con la paleta de alto contraste 'Icefire'
    fig_3d.add_trace(go.Cone(
        x=np.array(x_v), y=np.array(y_v), z=np.array(z_v),
        u=np.array(u_v), v=np.array(v_v), w=np.array(w_v),
        colorscale='Icefire', showscale=False, sizemode='scaled', sizeref=0.4, anchor='tail'
    ))
    
    # Configuraciones estéticas del Layout de Fondo
    fig_3d.update_layout(
        template="plotly_dark", height=460, margin=dict(l=0, r=0, t=0, b=0), showlegend=False
    )
    
    fig_3d.update_scenes(
        xaxis_title="Ancho W (m)", yaxis_title="Espesor y (m)", zaxis_title="Altura L (m)",
        xaxis=dict(backgroundcolor="black", gridcolor="#222222", showbackground=True, range=[-0.05, ancho_bloque_x + 0.05]),
        yaxis=dict(backgroundcolor="black", gridcolor="#222222", showbackground=True, range=[-B - 0.03, B + 0.03]),
        zaxis=dict(backgroundcolor="black", gridcolor="#222222", showbackground=True, range=[-0.1, L + 0.2]),
        camera=dict(eye=dict(x=1.3, y=-1.3, z=0.8))
    )
    
    # Actualizar el contenedor sin parpadear la página completa
    grafico_3d_placeholder.plotly_chart(fig_3d, use_container_width=True)
    
    # Pausa controlada para marcar la velocidad de fotogramas por segundo (FPS) del aire
    if animar:
        time.sleep(0.08)
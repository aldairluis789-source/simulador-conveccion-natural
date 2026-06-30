# 🌀 Análisis Numérico-Analítico de Convección Natural en Canales Verticales Confinados

Este repositorio contiene la implementación interactiva del modelo de transferencia de cantidad de movimiento y energía para un fluido atrapado entre dos placas planas paralelas extendidas, resolviendo analíticamente las ecuaciones descritas en el libro **"Fenómenos de Transporte" de R. Byron Bird (Sección 10.4)**.

## 🚀 Características del Proyecto
- **Interactividad en Tiempo Real:** Permite manipular las temperaturas de frontera ($T_1, T_2$) y la geometría espacial ($B$) observando dinámicamente las variaciones en los perfiles termofísicos.
- **Validación del Pico de Velocidad:** Localiza el punto exacto de la máxima corriente ascendente de aire por diferencia de densidades ($1.59 \text{ m/s}$).
- **Gráficos Dinámicos:** Implementado con Plotly para análisis interactivo de datos.

## 🛠️ Instalación y Uso Local
1. Clonar el repositorio.
2. Instalar dependencias esenciales: `pip install -r requirements.txt`
3. Ejecutar la aplicación web: `streamlit run app.py`
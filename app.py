import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

st.set_page_config(
    page_title="GLINSA | Inventarios",
    page_icon="📦",
    layout="wide"
)
# ==========================================
# CARGA DE DATOS
# ==========================================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("inventario_demo_glinsa.csv")
    df["caducidad"] = pd.to_datetime(
        df["caducidad"],
        errors="coerce"
    )
    return df

df = cargar_datos()
# ==========================================
# CÁLCULO DE INDICADORES
# ==========================================

hoy = pd.Timestamp.today().normalize()

# Productos únicos
total_productos = df["producto"].nunique()

# Lotes con existencia mayor a cero
lotes_activos = df.loc[
    df["existencia"] > 0,
    "lote"
].nunique()

# Días restantes para caducidad
df["dias_para_caducar"] = (
    df["caducidad"] - hoy
).dt.days

# Lotes que caducan en los próximos 90 días
proximos_caducar = df[
    (df["dias_para_caducar"] >= 0) &
    (df["dias_para_caducar"] <= 90) &
    (df["existencia"] > 0)
]["lote"].nunique()
# ==========================================
# MENÚ LATERAL
# ==========================================

st.sidebar.title("GLINSA")
st.sidebar.caption("Sistema Inteligente de Inventarios")

modulo = st.sidebar.radio(
    "Navegación",
    [
        "Dashboard",
        "Inventario",
        "Recepción y Calidad",
        "Entradas y Salidas",
        "Caducidades",
        "Predicción y Reabasto",
        "IA Documental"
    ]
)

st.sidebar.divider()

st.sidebar.caption("Prototipo de automatización de inventarios")


# ==========================================
# DASHBOARD
# ==========================================

if modulo == "Dashboard":

    st.title("📊 Dashboard de Inventarios")
    st.caption("Monitoreo general de la operación de almacén")

    st.divider()

    # KPIs principales

    col1, col2, col3, col4 = st.columns(4)

    with col1:
    st.metric(
        label="Productos",
        value=total_productos
    )

with col2:
    st.metric(
        label="Lotes activos",
        value=lotes_activos
    )

with col3:
    st.metric(
        label="Próximos a caducar",
        value=proximos_caducar
    )

with col4:
    st.metric(
        label="Productos por reabastecer",
        value="--"
    )

    st.divider()

    # Segunda sección

    col_izquierda, col_derecha = st.columns(2)

    with col_izquierda:

        st.subheader("⚠️ Alertas de inventario")

        st.info(
            "Aquí aparecerán automáticamente los productos "
            "con inventario bajo, próximos a caducar o con "
            "alguna inconsistencia."
        )

    with col_derecha:

        st.subheader("📦 Estado del almacén")

        st.info(
            "Aquí visualizaremos el estado general del "
            "inventario de GLINSA."
        )

    st.divider()

    st.subheader("📈 Movimiento de inventario")

    st.info(
        "Esta sección mostrará las entradas y salidas "
        "históricas del almacén."
    )


# ==========================================
# INVENTARIO
# ==========================================

elif modulo == "Inventario":

    st.title("📦 Inventario")

    st.write(
        "Consulta de existencias por producto, lote, "
        "ubicación y fecha de caducidad."
    )

    st.info("Módulo en construcción")


# ==========================================
# RECEPCIÓN Y CALIDAD
# ==========================================

elif modulo == "Recepción y Calidad":

    st.title("🔍 Recepción y Calidad")

    st.write(
        "Validación de productos recibidos, lotes, "
        "caducidades y documentación de calidad."
    )

    st.info("Módulo en construcción")


# ==========================================
# ENTRADAS Y SALIDAS
# ==========================================

elif modulo == "Entradas y Salidas":

    st.title("🚚 Entradas y Salidas")

    st.write(
        "Registro y monitoreo de movimientos del almacén."
    )

    st.info("Módulo en construcción")


# ==========================================
# CADUCIDADES
# ==========================================

elif modulo == "Caducidades":

    st.title("⏳ Control de Caducidades")

    st.write(
        "Monitoreo de lotes y productos próximos a caducar."
    )

    st.info("Módulo en construcción")


# ==========================================
# PREDICCIÓN
# ==========================================

elif modulo == "Predicción y Reabasto":

    st.title("📈 Predicción y Reabasto")

    st.write(
        "Análisis de consumo histórico y recomendaciones "
        "de reabastecimiento."
    )

    st.info("Módulo en construcción")


# ==========================================
# IA DOCUMENTAL
# ==========================================

elif modulo == "IA Documental":

    st.title("🤖 IA Documental")

    st.write(
        "Validación inteligente de certificados de calidad "
        "y documentación de recepción."
    )

    st.info("Módulo en construcción")

import streamlit as st
import pandas as pd

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

    # Convertir caducidad a formato fecha
    df["caducidad"] = pd.to_datetime(
        df["caducidad"],
        errors="coerce"
    )

    # Convertir existencia a número
    df["existencia"] = pd.to_numeric(
        df["existencia"],
        errors="coerce"
    ).fillna(0)

    return df


df = cargar_datos()


# ==========================================
# CÁLCULO DE INDICADORES
# ==========================================

hoy = pd.Timestamp.today().normalize()

# Productos únicos
total_productos = df["producto"].nunique()

# Lotes activos
lotes_activos = df.loc[
    df["existencia"] > 0,
    "lote"
].nunique()

# Días restantes para caducidad
df["dias_para_caducar"] = (
    df["caducidad"] - hoy
).dt.days


# ==========================================
# CLASIFICACIÓN DE CADUCIDADES
# ==========================================

def clasificar_caducidad(dias):

    if pd.isna(dias):
        return "⚪ Sin fecha"

    elif dias < 0:
        return "⚫ Vencido"

    elif dias <= 30:
        return "🔴 Crítico"

    elif dias <= 90:
        return "🟡 Atención"

    else:
        return "🟢 Vigente"


df["estado_caducidad"] = df["dias_para_caducar"].apply(
    clasificar_caducidad
)


# ==========================================
# LOTES PRÓXIMOS A CADUCAR
# ==========================================

proximos_caducar = df[
    (df["dias_para_caducar"] >= 0) &
    (df["dias_para_caducar"] <= 90) &
    (df["existencia"] > 0)
]["lote"].nunique()


# ==========================================
# INDICADORES DEL SEMÁFORO
# ==========================================

lotes_criticos = df[
    (df["dias_para_caducar"] >= 0) &
    (df["dias_para_caducar"] <= 30) &
    (df["existencia"] > 0)
]["lote"].nunique()

lotes_atencion = df[
    (df["dias_para_caducar"] > 30) &
    (df["dias_para_caducar"] <= 90) &
    (df["existencia"] > 0)
]["lote"].nunique()

lotes_vigentes = df[
    (df["dias_para_caducar"] > 90) &
    (df["existencia"] > 0)
]["lote"].nunique()

lotes_vencidos = df[
    (df["dias_para_caducar"] < 0) &
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

st.sidebar.caption(
    "Prototipo de automatización de inventarios"
)


# ==========================================
# DASHBOARD
# ==========================================

if modulo == "Dashboard":

    st.title("📊 Dashboard de Inventarios")

    st.caption(
        "Monitoreo general de la operación de almacén"
    )

    st.divider()

    # --------------------------------------
    # KPIs PRINCIPALES
    # --------------------------------------

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

    # --------------------------------------
    # SEMÁFORO DE CADUCIDADES
    # --------------------------------------

      st.subheader("🚦 Semáforo de caducidades")

    sem1, sem2, sem3, sem4 = st.columns(4)

    with sem1:
        st.metric(
            "🔴 Críticos (0–30 días)",
            lotes_criticos
        )

    with sem2:
        st.metric(
            "🟡 Atención (31–90 días)",
            lotes_atencion
        )

    with sem3:
        st.metric(
            "🟢 Vigentes (+90 días)",
            lotes_vigentes
        )

    with sem4:
        st.metric(
            "⚫ Vencidos",
            lotes_vencidos
        )

    # --------------------------------------
    # ALERTAS DE INVENTARIO
    # --------------------------------------

    st.subheader("⚠️ Alertas de caducidad")

    alertas = df[
        (
            (df["dias_para_caducar"] <= 90) |
            (df["dias_para_caducar"] < 0)
        ) &
        (df["existencia"] > 0)
    ].copy()

    if len(alertas) > 0:

        alertas = alertas.sort_values(
            by="dias_para_caducar",
            ascending=True
        )

        tabla_alertas = alertas[
            [
                "estado_caducidad",
                "producto",
                "lote",
                "existencia",
                "unidad",
                "caducidad",
                "dias_para_caducar"
            ]
        ].copy()

        tabla_alertas.columns = [
            "Estado",
            "Producto",
            "Lote",
            "Existencia",
            "Unidad",
            "Caducidad",
            "Días restantes"
        ]

        tabla_alertas["Caducidad"] = (
            tabla_alertas["Caducidad"]
            .dt.strftime("%d/%m/%Y")
        )

        st.dataframe(
            tabla_alertas,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No existen lotes con caducidad menor a 90 días."
        )

    st.divider()

    # --------------------------------------
    # ESTADO DEL ALMACÉN
    # --------------------------------------

    st.subheader("📦 Estado del almacén")

    st.info(
        "En esta sección incorporaremos posteriormente "
        "el análisis de existencias, stock mínimo y "
        "necesidades de reabastecimiento."
    )

    st.divider()

    # --------------------------------------
    # MOVIMIENTO DE INVENTARIO
    # --------------------------------------

    st.subheader("📈 Movimiento de inventario")

    st.info(
        "Esta sección mostrará posteriormente las entradas "
        "y salidas históricas del almacén."
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

    st.caption(
        "Monitoreo de lotes y productos según su fecha "
        "de caducidad."
    )

    st.divider()

    # Filtro por estado
    estado_seleccionado = st.selectbox(
        "Filtrar por estado",
        [
            "Todos",
            "🔴 Crítico",
            "🟡 Atención",
            "🟢 Vigente",
            "⚫ Vencido",
            "⚪ Sin fecha"
        ]
    )

    inventario_activo = df[
        df["existencia"] > 0
    ].copy()

    if estado_seleccionado != "Todos":

        inventario_activo = inventario_activo[
            inventario_activo["estado_caducidad"]
            == estado_seleccionado
        ]

    inventario_activo = inventario_activo.sort_values(
        by="dias_para_caducar",
        ascending=True,
        na_position="last"
    )

    tabla_caducidades = inventario_activo[
        [
            "estado_caducidad",
            "producto",
            "lote",
            "existencia",
            "unidad",
            "caducidad",
            "dias_para_caducar"
        ]
    ].copy()

    tabla_caducidades.columns = [
        "Estado",
        "Producto",
        "Lote",
        "Existencia",
        "Unidad",
        "Caducidad",
        "Días restantes"
    ]

    tabla_caducidades["Caducidad"] = (
        tabla_caducidades["Caducidad"]
        .dt.strftime("%d/%m/%Y")
    )

    st.dataframe(
        tabla_caducidades,
        use_container_width=True,
        hide_index=True
    )


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
# PREDICCIÓN Y REABASTO
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

    






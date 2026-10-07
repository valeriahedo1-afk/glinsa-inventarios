import streamlit as st
import pandas as pd

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="GLINSA | Inventarios",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("inventario_demo_glinsa.csv")

    # Convertir fecha de caducidad
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


# ============================================================
# CÁLCULOS GENERALES
# ============================================================

hoy = pd.Timestamp.today().normalize()

# Días restantes para caducidad
df["dias_para_caducar"] = (
    df["caducidad"] - hoy
).dt.days


# ============================================================
# CLASIFICACIÓN DE CADUCIDAD
# ============================================================

def clasificar_caducidad(dias):

    if pd.isna(dias):
        return "⚪ Sin fecha"

    if dias < 0:
        return "⚫ Vencido"

    if dias <= 30:
        return "🔴 Crítico"

    if dias <= 90:
        return "🟡 Atención"

    return "🟢 Vigente"


df["estado_caducidad"] = df["dias_para_caducar"].apply(
    clasificar_caducidad
)


# ============================================================
# INVENTARIO ACTIVO
# ============================================================

df_activo = df[
    df["existencia"] > 0
].copy()


# ============================================================
# KPIs GENERALES
# ============================================================

total_productos = df["producto"].nunique()

lotes_activos = df_activo["lote"].nunique()

proximos_caducar = df_activo[
    (df_activo["dias_para_caducar"] >= 0) &
    (df_activo["dias_para_caducar"] <= 90)
]["lote"].nunique()


# ============================================================
# KPIs DEL SEMÁFORO
# ============================================================

lotes_criticos = df_activo[
    (df_activo["dias_para_caducar"] >= 0) &
    (df_activo["dias_para_caducar"] <= 30)
]["lote"].nunique()


lotes_atencion = df_activo[
    (df_activo["dias_para_caducar"] > 30) &
    (df_activo["dias_para_caducar"] <= 90)
]["lote"].nunique()


lotes_vigentes = df_activo[
    df_activo["dias_para_caducar"] > 90
]["lote"].nunique()


lotes_vencidos = df_activo[
    df_activo["dias_para_caducar"] < 0
]["lote"].nunique()


# ============================================================
# MENÚ LATERAL
# ============================================================

st.sidebar.title("GLINSA")

st.sidebar.caption(
    "Sistema Inteligente de Inventarios"
)

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


# ============================================================
# DASHBOARD
# ============================================================

if modulo == "Dashboard":

    st.title("📊 Dashboard de Inventarios")

    st.caption(
        "Monitoreo general de la operación de almacén"
    )

    st.divider()


    # --------------------------------------------------------
    # KPIs PRINCIPALES
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SEMÁFORO DE CADUCIDADES
    # --------------------------------------------------------

    st.subheader("🚦 Semáforo de caducidades")

    sem1, sem2, sem3, sem4 = st.columns(4)

    with sem1:
        st.metric(
            label="🔴 Críticos (0–30 días)",
            value=lotes_criticos
        )

    with sem2:
        st.metric(
            label="🟡 Atención (31–90 días)",
            value=lotes_atencion
        )

    with sem3:
        st.metric(
            label="🟢 Vigentes (+90 días)",
            value=lotes_vigentes
        )

    with sem4:
        st.metric(
            label="⚫ Vencidos",
            value=lotes_vencidos
        )

    st.divider()


    # --------------------------------------------------------
    # ALERTAS DE CADUCIDAD
    # --------------------------------------------------------

    st.subheader("⚠️ Alertas de caducidad")

    alertas = df_activo[
        df_activo["dias_para_caducar"] <= 90
    ].copy()

    alertas = alertas.sort_values(
        by="dias_para_caducar",
        ascending=True
    )

    if not alertas.empty:

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
            "No existen lotes con caducidad menor "
            "o igual a 90 días."
        )


    st.divider()


    # --------------------------------------------------------
    # ESTADO DEL ALMACÉN
    # --------------------------------------------------------

    st.subheader("📦 Estado del almacén")

    st.info(
        "En esta sección incorporaremos el análisis "
        "de existencias, stock mínimo y necesidades "
        "de reabastecimiento."
    )


    st.divider()


    # --------------------------------------------------------
    # MOVIMIENTO DE INVENTARIO
    # --------------------------------------------------------

    st.subheader("📈 Movimiento de inventario")

    st.info(
        "Esta sección mostrará las entradas y salidas "
        "históricas del almacén."
    )


# ============================================================
# INVENTARIO
# ============================================================

elif modulo == "Inventario":

    st.title("📦 Inventario")

    st.caption(
        "Consulta de existencias por producto y lote"
    )

    st.divider()

    # Buscador
    busqueda = st.text_input(
        "🔎 Buscar producto",
        placeholder="Escribe el nombre del producto..."
    )

    inventario_mostrar = df_activo.copy()

    if busqueda:

        inventario_mostrar = inventario_mostrar[
            inventario_mostrar["producto"]
            .astype(str)
            .str.contains(
                busqueda,
                case=False,
                na=False
            )
        ]

    inventario_mostrar = inventario_mostrar.sort_values(
        by="producto"
    )

    tabla_inventario = inventario_mostrar[
        [
            "producto",
            "lote",
            "existencia",
            "unidad",
            "caducidad",
            "estado_caducidad"
        ]
    ].copy()

    tabla_inventario.columns = [
        "Producto",
        "Lote",
        "Existencia",
        "Unidad",
        "Caducidad",
        "Estado"
    ]

    tabla_inventario["Caducidad"] = (
        tabla_inventario["Caducidad"]
        .dt.strftime("%d/%m/%Y")
    )

    st.dataframe(
        tabla_inventario,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RECEPCIÓN Y CALIDAD
# ============================================================

elif modulo == "Recepción y Calidad":

    st.title("🔍 Recepción y Calidad")

    st.write(
        "Validación de productos recibidos, lotes, "
        "caducidades y documentación de calidad."
    )

    st.info(
        "Módulo en construcción"
    )


# ============================================================
# ENTRADAS Y SALIDAS
# ============================================================

elif modulo == "Entradas y Salidas":

    st.title("🚚 Entradas y Salidas")

    st.write(
        "Registro y monitoreo de movimientos "
        "del almacén."
    )

    st.info(
        "Módulo en construcción"
    )


# ============================================================
# CADUCIDADES
# ============================================================

elif modulo == "Caducidades":

    st.title("⏳ Control de Caducidades")

    st.caption(
        "Monitoreo de productos y lotes según "
        "su fecha de caducidad"
    )

    st.divider()


    # --------------------------------------------------------
    # KPIs DE CADUCIDAD
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🔴 Críticos",
            lotes_criticos
        )

    with c2:
        st.metric(
            "🟡 Atención",
            lotes_atencion
        )

    with c3:
        st.metric(
            "🟢 Vigentes",
            lotes_vigentes
        )

    with c4:
        st.metric(
            "⚫ Vencidos",
            lotes_vencidos
        )

    st.divider()


    # --------------------------------------------------------
    # FILTRO
    # --------------------------------------------------------

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

    tabla_filtrada = df_activo.copy()

    if estado_seleccionado != "Todos":

        tabla_filtrada = tabla_filtrada[
            tabla_filtrada["estado_caducidad"]
            == estado_seleccionado
        ]


    # Ordenar por caducidad
    tabla_filtrada = tabla_filtrada.sort_values(
        by="dias_para_caducar",
        ascending=True,
        na_position="last"
    )


    tabla_caducidades = tabla_filtrada[
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


# ============================================================
# PREDICCIÓN Y REABASTO
# ============================================================

elif modulo == "Predicción y Reabasto":

    st.title("📈 Predicción y Reabasto")

    st.write(
        "Análisis de consumo histórico y recomendaciones "
        "de reabastecimiento."
    )

    st.info(
        "Módulo en construcción"
    )


# ============================================================
# IA DOCUMENTAL
# ============================================================

elif modulo == "IA Documental":

    st.title("🤖 IA Documental")

    st.write(
        "Validación inteligente de certificados de calidad "
        "y documentación de recepción."
    )

    st.info(
        "Módulo en construcción"
    )

    






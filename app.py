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

    df["caducidad"] = pd.to_datetime(
        df["caducidad"],
        errors="coerce"
    )

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
            "Productos",
            total_productos
        )

    with col2:
        st.metric(
            "Lotes activos",
            lotes_activos
        )

    with col3:
        st.metric(
            "Próximos a caducar",
            proximos_caducar
        )

    with col4:
        st.metric(
            "Productos por reabastecer",
            "--"
        )

    st.divider()

    # --------------------------------------------------------
    # SEMÁFORO DE CADUCIDADES
    # --------------------------------------------------------

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
        "Posteriormente incorporaremos aquí el análisis "
        "de existencias, stock mínimo y necesidades "
        "de reabastecimiento."
    )

    st.divider()

    # --------------------------------------------------------
    # MOVIMIENTO DE INVENTARIO
    # --------------------------------------------------------

    st.subheader("📈 Movimiento de inventario")

    st.info(
        "Posteriormente incorporaremos las entradas "
        "y salidas históricas."
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

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    st.subheader("🔎 Consulta de inventario")

    filtro1, filtro2 = st.columns(2)

    with filtro1:

        buscar_producto = st.text_input(
            "Buscar por producto",
            placeholder="Escribe el nombre del producto..."
        )

    with filtro2:

        buscar_lote = st.text_input(
            "Buscar por lote",
            placeholder="Escribe el número o código del lote..."
        )

    inventario_mostrar = df_activo.copy()

    # Filtro por producto
    if buscar_producto:

        inventario_mostrar = inventario_mostrar[
            inventario_mostrar["producto"]
            .astype(str)
            .str.contains(
                buscar_producto,
                case=False,
                na=False
            )
        ]

    # Filtro por lote
    if buscar_lote:

        inventario_mostrar = inventario_mostrar[
            inventario_mostrar["lote"]
            .astype(str)
            .str.contains(
                buscar_lote,
                case=False,
                na=False
            )
        ]

    st.divider()

    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    st.subheader("Resultados")

    st.caption(
        f"Se encontraron {len(inventario_mostrar)} registros."
    )

    inventario_mostrar = inventario_mostrar.sort_values(
        by=["producto", "lote"]
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

    if not tabla_inventario.empty:

        st.dataframe(
            tabla_inventario,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No se encontraron registros con "
            "los filtros seleccionados."
        )


# ============================================================
# RECEPCIÓN Y CALIDAD
# ============================================================

elif modulo == "Recepción y Calidad":

    st.title("🔍 Recepción y Calidad")

    st.caption(
        "Registro y validación inicial de materiales recibidos"
    )

    st.divider()

    st.subheader("📥 Nueva recepción")

    st.write(
        "Captura los datos del material recibido para "
        "realizar la validación antes de su ingreso "
        "al inventario."
    )

    with st.form("formulario_recepcion"):

        col1, col2 = st.columns(2)

        with col1:

            producto_recepcion = st.text_input(
                "Producto *"
            )

            proveedor = st.text_input(
                "Proveedor *"
            )

            lote_recepcion = st.text_input(
                "Lote *"
            )

            cantidad_recepcion = st.number_input(
                "Cantidad recibida *",
                min_value=0.0,
                step=1.0
            )

        with col2:

            unidad_recepcion = st.selectbox(
                "Unidad *",
                [
                    "KG",
                    "L",
                    "GAL",
                    "PZA",
                    "TAMBOR",
                    "OTRA"
                ]
            )

            fecha_fabricacion = st.date_input(
                "Fecha de fabricación"
            )

            fecha_caducidad = st.date_input(
                "Fecha de caducidad"
            )

            numero_documento = st.text_input(
                "Factura / Orden de compra"
            )

        st.divider()

        st.subheader("🧪 Validación de Calidad")

        certificado = st.checkbox(
            "Certificado de calidad recibido"
        )

        producto_coincide = st.checkbox(
            "El producto físico coincide con la documentación"
        )

        lote_coincide = st.checkbox(
            "El lote físico coincide con el certificado"
        )

        caducidad_coincide = st.checkbox(
            "La fecha de caducidad coincide con el certificado"
        )

        documentacion_completa = st.checkbox(
            "La documentación está completa"
        )

        observaciones = st.text_area(
            "Observaciones"
        )

        validar = st.form_submit_button(
            "Validar recepción"
        )

    # --------------------------------------------------------
    # RESULTADO DE VALIDACIÓN
    # --------------------------------------------------------

    if validar:

        campos_obligatorios = (
            producto_recepcion.strip() != "" and
            proveedor.strip() != "" and
            lote_recepcion.strip() != "" and
            cantidad_recepcion > 0
        )

        validaciones_calidad = (
            certificado and
            producto_coincide and
            lote_coincide and
            caducidad_coincide and
            documentacion_completa
        )

        if not campos_obligatorios:

            st.error(
                "❌ Faltan datos obligatorios para "
                "procesar la recepción."
            )

        elif fecha_caducidad <= fecha_fabricacion:

            st.error(
                "❌ La fecha de caducidad debe ser posterior "
                "a la fecha de fabricación."
            )

        elif validaciones_calidad:

            st.success(
                "✅ RECEPCIÓN LIBERADA"
            )

            st.write(
                "El material cumple con las validaciones "
                "registradas y puede continuar al proceso "
                "de ingreso al almacén."
            )

            resumen = pd.DataFrame(
                {
                    "Campo": [
                        "Producto",
                        "Proveedor",
                        "Lote",
                        "Cantidad",
                        "Unidad",
                        "Fabricación",
                        "Caducidad",
                        "Documento"
                    ],
                    "Información": [
                        producto_recepcion,
                        proveedor,
                        lote_recepcion,
                        cantidad_recepcion,
                        unidad_recepcion,
                        fecha_fabricacion.strftime("%d/%m/%Y"),
                        fecha_caducidad.strftime("%d/%m/%Y"),
                        numero_documento
                    ]
                }
            )

            st.dataframe(
                resumen,
                use_container_width=True,
                hide_index=True
            )

            st.info(
                "En la siguiente etapa conectaremos esta "
                "liberación con el registro de entrada "
                "del inventario."
            )

        else:

            st.error(
                "🚫 RECEPCIÓN NO LIBERADA"
            )

            st.write(
                "Se detectaron validaciones pendientes "
                "o inconsistencias."
            )

            problemas = []

            if not certificado:
                problemas.append(
                    "Falta certificado de calidad."
                )

            if not producto_coincide:
                problemas.append(
                    "El producto no ha sido validado "
                    "contra la documentación."
                )

            if not lote_coincide:
                problemas.append(
                    "El lote no coincide o no ha sido validado."
                )

            if not caducidad_coincide:
                problemas.append(
                    "La caducidad no coincide o no ha sido validada."
                )

            if not documentacion_completa:
                problemas.append(
                    "La documentación está incompleta."
                )

            for problema in problemas:
                st.warning(problema)


# ============================================================
# ENTRADAS Y SALIDAS
# ============================================================

elif modulo == "Entradas y Salidas":

    st.title("🚚 Entradas y Salidas")

    st.caption(
        "Registro y monitoreo de movimientos del almacén"
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
    # KPIs
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
    # FILTRO POR ESTADO
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

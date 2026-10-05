import streamlit as st

st.set_page_config(
    page_title="GLINSA | Inventarios",
    page_icon="📦",
    layout="wide"
)

st.title("📦 GLINSA | Sistema Inteligente de Inventarios")

st.write(
    "Prototipo para la automatización, monitoreo y análisis "
    "del área de almacén e inventarios."
)

st.success("¡La aplicación está funcionando correctamente!")

st.subheader("Panel de inventarios")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Productos", "125")

with col2:
    st.metric("Lotes activos", "86")

with col3:
    st.metric("Próximos a caducar", "12")

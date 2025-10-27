import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ===============================
# Configurazione pagina
# ===============================
st.set_page_config(page_title="Precios de carburante en Europa", layout="wide")

# Titolo grande e centrato
st.markdown("<h1 style='text-align: center; font-size: 50px;'>🌍 Precios de carburante en Europa</h1>", unsafe_allow_html=True)

# Testo descrittivo subito sotto
st.markdown(
    "<p style='text-align: center; font-size:18px;'>Visualiza y compara la evolución de los precios de carburante en distintos países europeos, explora mapas y KPIs de tendencia.</p>",
    unsafe_allow_html=True
)

# ===============================
# Función para cargar datos
# ===============================
@st.cache_data
def cargar_datos(ruta_csv):
    if not os.path.exists(ruta_csv):
        st.error(f"❌ Archivo no encontrado: {ruta_csv}")
        return pd.DataFrame()
    
    df = pd.read_csv(ruta_csv)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    
    # Biblioteca ISO2 -> ISO3
    iso2_to_iso3 = {
        "AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP",
        "CZ": "CZE", "DK": "DNK", "EE": "EST", "FI": "FIN", "FR": "FRA",
        "DE": "DEU", "GR": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA",
        "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD",
        "PL": "POL", "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN",
        "ES": "ESP", "SE": "SWE", "EU": "EUU", "EUR": "EUR"
    }
    df["iso_alpha"] = df["Country"].map(iso2_to_iso3)
    
    return df

# Cambia qui con la ruta correcta del CSV
ruta_csv = "carbur_10pais_prod.csv"
df = cargar_datos(ruta_csv)

if df.empty:
    st.stop()  # Termina se non ci sono dati globali

# ===============================
# Sidebar: filtros e download
# ===============================
st.sidebar.header("Filtros y descarga")

# Producto
productos = sorted(df["Product"].dropna().unique())
producto_seleccionado = st.sidebar.selectbox("Selecciona tipo de carburante", productos)

# País individual
paises = sorted(df["Country"].unique())
pais_seleccionado = st.sidebar.selectbox("Selecciona un país", paises, index=0)

# Países múltiples para comparar
paises_multiple = st.sidebar.multiselect(
    "Selecciona países para comparar",
    paises,
    default=[pais_seleccionado]
)

# Botón para descargar datos filtrados
df_filtrado = df[(df["Product"] == producto_seleccionado) & (df["Country"].isin(paises_multiple))]
st.sidebar.download_button(
    label="📥 Descargar datos filtrados",
    data=df_filtrado.to_csv(index=False),
    file_name='precios_filtrados.csv',
    mime='text/csv'
)

# ===============================
# Filtrar datos
# ===============================
df_producto = df[df["Product"] == producto_seleccionado]
df_pais = df_producto[df_producto["Country"] == pais_seleccionado]

# ===============================
# Gráfico a línea por país seleccionado
# ===============================
st.subheader(f"📈 Evolución de {producto_seleccionado} en {pais_seleccionado}")
if not df_pais.empty:
    fig_line = px.line(
        df_pais,
        x="Date",
        y="Price",
        markers=True,
        title=f"Evolución de {producto_seleccionado} en {pais_seleccionado}"
    )
    fig_line.update_layout(yaxis_title="Precio (€ por litro)", xaxis_title="Fecha", height=500)
    st.plotly_chart(fig_line, use_container_width=True)

# ===============================
# Comparación entre múltiples países
# ===============================
st.subheader(f"📊 Comparación de {producto_seleccionado} entre países seleccionados")
if not df_filtrado.empty:
    fig_compare = px.line(
        df_filtrado,
        x="Date",
        y="Price",
        color="Country",
        markers=True,
        title=f"Evolución de {producto_seleccionado} por país"
    )
    fig_compare.update_layout(yaxis_title="Precio (€ por litro)", xaxis_title="Fecha", height=500)
    st.plotly_chart(fig_compare, use_container_width=True)

# ===============================
# Mappa interattiva
# ===============================
st.subheader(f"🗺️ Precios medios de {producto_seleccionado} en Europa")
df_map = df_producto.groupby("Country").agg({"Price": "mean", "iso_alpha": "first"}).reset_index()
media_europa = df_map["Price"].mean()
df_map["RelativoEuropa"] = df_map["Price"] / media_europa * 100
df_map.rename(columns={"Price": "PrecioMedio"}, inplace=True)

fig_map = px.choropleth(
    df_map,
    locations="iso_alpha",
    color="PrecioMedio",
    hover_name="Country",
    hover_data={"PrecioMedio": ':.2f', "RelativoEuropa": ':.1f', "iso_alpha": False},
    color_continuous_scale="YlOrRd",
    range_color=[df_map["PrecioMedio"].min(), df_map["PrecioMedio"].max()],
    scope="europe",
    title=f"Precios medios de {producto_seleccionado} en Europa"
)
fig_map.update_layout(height=600, margin={"r":0,"t":30,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# Mapa de calor mensual
st.subheader(f"🔥 Mapa de calor mensual de {producto_seleccionado}")
df_heat = df_producto.copy()
df_heat["Mes"] = df_heat["Date"].dt.to_period("M").astype(str)
df_heat = df_heat.groupby(["Country", "Mes"])["Price"].mean().reset_index()

fig_heat = px.density_heatmap(
    df_heat,
    x="Mes",
    y="Country",
    z="Price",
    color_continuous_scale="YlOrBr",
    title=f"Mapa de calor de precios medios mensuales de {producto_seleccionado}"
)
fig_heat.update_layout(height=600)
st.plotly_chart(fig_heat, use_container_width=True)

# Indicatore de tendencia (Sparkline / Mini-linea)
st.subheader("📉 Tendencia general europea")
df_europa = df.groupby("Date")["Price"].mean().reset_index()
fig_trend = px.line(df_europa, x="Date", y="Price", title="Tendencia media europea de precios")
fig_trend.update_layout(height=300, yaxis_title="Precio medio (€)", xaxis_title="Fecha")
st.plotly_chart(fig_trend, use_container_width=True)

# ===============================
# KPIs + grafico a torta
# ===============================
st.subheader(f"📊 Distribución de precios medios de {producto_seleccionado} entre países y KPIs")
df_pie = df_producto.groupby("Country")["Price"].mean().reset_index()

col1, col2 = st.columns([2,1])

with col1:
    if not df_pie.empty:
        fig_pie = px.pie(
            df_pie,
            names="Country",
            values="Price",
            title=f"Distribución de precios medios de {producto_seleccionado}",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(
            hovertemplate="<b>%{label}</b><br>Precio medio: €%{value:.2f}/L<extra></extra>",
            textposition="inside"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    if not df_pie.empty:
        precio_medio = df_pie["Price"].mean()
        precio_min = df_pie["Price"].min()
        precio_max = df_pie["Price"].max()
        st.metric("Precio medio (€ por litro)", f"{precio_medio:.2f}")
        st.metric("Precio mínimo (€ por litro)", f"{precio_min:.2f}")
        st.metric("Precio máximo (€ por litro)", f"{precio_max:.2f}")

variacion = (df_europa["Price"].iloc[-1] - df_europa["Price"].iloc[-2]) / df_europa["Price"].iloc[-2] * 100
volatilidad = df_europa["Price"].pct_change().std() * 100

st.metric("📈 Variación última semana (%)", f"{variacion:.2f}%")
st.metric("📊 Volatilidad mensual (%)", f"{volatilidad:.2f}%")

# ===============================
# Top 5 países caros y baratos
# ===============================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔝 Top 5 países más caros")
    for idx, row in df_map.sort_values(by="PrecioMedio", ascending=False).head(5).iterrows():
        st.write(f"**{row['Country']}**: €{row['PrecioMedio']:.2f}/L")

with col2:
    st.markdown("### 💸 Top 5 países más baratos")
    for idx, row in df_map.sort_values(by="PrecioMedio", ascending=True).head(5).iterrows():
        st.write(f"**{row['Country']}**: €{row['PrecioMedio']:.2f}/L")

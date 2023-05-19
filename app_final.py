import pandas as pd
import itertools
import streamlit as st

st.set_page_config(page_title="Optimizador de Sabores - Koandina", layout="wide")

def normalize_product_name(name):
    return name.replace(" ", "").replace("-", "")

def calcular_consumo(secuencia, limpieza):
    consumo = 0
    for i in range(1, len(secuencia)):
        key = normalize_product_name(secuencia[i-1]) + normalize_product_name(secuencia[i])
        consumo += limpieza.get(key, 0)
    return consumo

def calcular_consumo_df(df, limpieza):
    secuencia = df["Producto"].tolist()
    return calcular_consumo(secuencia, limpieza)

def agrupar_bloques(df):
    productos = [df.loc[0, "Producto"]]
    horas = [[df.loc[0, "Hora"]]]
    for i in range(1, len(df)):
        if df.loc[i, "Producto"] == productos[-1]:
            horas[-1].append(df.loc[i, "Hora"])
        else:
            productos.append(df.loc[i, "Producto"])
            horas.append([df.loc[i, "Hora"]])
    return list(zip(productos, horas))

def buscar_orden_optimo(bloques, limpieza):
    orden_optimo = None
    menor_consumo = float('inf')
    for secuencia in itertools.permutations(bloques):
        consumo = calcular_consumo([bloque[0] for bloque in secuencia], limpieza)
        if consumo < menor_consumo:
            menor_consumo = consumo
            orden_optimo = secuencia
    return orden_optimo

limpieza = {
    "CocaColaSprite": 10, "SpriteCocaCola": 5,
    "CocaColaFanta": 12, "FantaCocaCola": 8,
    "CocaColaGuarana": 15, "GuaranaCocaCola": 9,
    "SpriteFanta": 13, "FantaSprite": 9,
    "SpriteGuarana": 14, "GuaranaSprite": 10,
    "FantaGuarana": 16, "GuaranaFanta": 10,
}

# Agregar color personalizado para encabezado
st.markdown(
    """
    <style>
    .header {
        color: white;
        padding: 10px;
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Mostrar el logo
st.image("koandina.png")

# Mostrar el título de la aplicación
st.markdown('<div class="header"><h1>Optimizador de sabores</h1></div>', unsafe_allow_html=True)


file_upload = st.file_uploader("Sube el archivo Excel del plan de producción para el día", type=["xlsx"])
if file_upload is not None:
    df = pd.read_excel(file_upload)
    consumo_original = calcular_consumo_df(df, limpieza)

    with st.spinner('Optimizando el plan de producción...'):
        bloques = agrupar_bloques(df)
        orden_optimo = buscar_orden_optimo(bloques, limpieza)

        sabores_agregados = set()  
        orden_optimo_sin_repeticiones = []  

        for bloque in orden_optimo:
            sabor = bloque[0]
            if sabor not in sabores_agregados:  
                orden_optimo_sin_repeticiones.append(sabor)
                sabores_agregados.add(sabor)

        st.success('¡La optimización ha terminado!')

        sabores_str = ', '.join(orden_optimo_sin_repeticiones)
        st.subheader(f"El orden óptimo de sabores es: {sabores_str}")

        df_optimizado = pd.concat([pd.DataFrame({"Hora": bloque[1], "Producto": [bloque[0]] * len(bloque[1])}) for bloque in orden_optimo])
        df_optimizado.reset_index(drop=True, inplace=True)
        df_optimizado.update(df["Hora"])

        consumo_optimizado = calcular_consumo_df(df_optimizado, limpieza)

    # Mostrar el consumo de agua con el componente st.metric
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Consumo de agua (Original)", f"{consumo_original} litros")
    with col2:
        st.metric("Consumo de agua (Optimizado)", f"{consumo_optimizado} litros", delta=f"{consumo_original - consumo_optimizado} litros")

    with st.expander('Ver plan de producción original'):
        st.subheader("Plan de producción original:")
        st.dataframe(df)

    with st.expander('Ver plan de producción optimizado'):
        st.subheader("Plan de producción optimizado:")
        st.dataframe(df_optimizado)

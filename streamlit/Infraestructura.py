import streamlit as st
import pandas as pd
import plotly.express as px

def show_infraestructura_tab():
    st.title("🏫 Infraestructura Educativa por Municipio")

    if 'df_infra' not in st.session_state:
        st.warning("Primero debes cargar la base de infraestructura en la pestaña 'Carga de Datos'.")
        return

    df = st.session_state['df_infra'].copy()

    # Normalizar nombres de columnas para facilidad
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')

    # Información descriptiva interactiva
    st.markdown("### 📊 Información General de la Base")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", f"{len(df):,}")
    col2.metric("Departamentos", df['nombre_depto'].nunique())
    col3.metric("Municipios", df['nombre_municipio'].nunique())

    st.info(
        "Esta base contiene información sobre el estado de infraestructura educativa, "
        "incluyendo la cantidad de aulas nuevas y mejoradas, y el estado general de las obras."
    )

    st.markdown("### 🧱 Resumen General")
    st.dataframe(df[['nombre_depto', 'nombre_municipio', 'nombre_sede', 'aulas_nuevas', 'aulas_mejoradas', 'estado_general']].head(10))

    st.markdown("---")
    st.subheader("🏗️ Total de aulas nuevas y mejoradas por departamento")

    df_grouped = df.groupby('nombre_depto')[['aulas_nuevas', 'aulas_mejoradas']].sum().reset_index()

    fig = px.bar(
        df_grouped.melt(id_vars='nombre_depto', value_vars=['aulas_nuevas', 'aulas_mejoradas']),
        x='nombre_depto',
        y='value',
        color='variable',
        barmode='group',
        title="Aulas Nuevas y Mejoradas por Departamento"
    )
    fig.update_layout(xaxis_title="Departamento", yaxis_title="Cantidad de Aulas", height=500)
    st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")
    st.subheader("🏆 Top 10 Municipios con Mayor Inversión en Aulas")

    df['total_aulas'] = df[['aulas_nuevas', 'aulas_mejoradas']].sum(axis=1)
    top_municipios = (
        df.groupby(['nombre_depto', 'nombre_municipio'])['total_aulas']
        .sum()
        .reset_index()
        .sort_values(by='total_aulas', ascending=False)
        .head(10)
    )

    fig_top = px.bar(
        top_municipios,
        x='total_aulas',
        y='nombre_municipio',
        color='nombre_depto',
        orientation='h',
        title="Top 10 Municipios con más aulas nuevas o mejoradas",
        height=500
    )
    fig_top.update_layout(
        xaxis_title="Total de Aulas",
        yaxis_title="Municipio",
        yaxis=dict(categoryorder='total ascending')
    )
    st.plotly_chart(fig_top, use_container_width=True)





    st.markdown("---")
    st.subheader("🔎 Tabla Interactiva: Proyectos por Departamento y Estado")

    deptos = sorted(df['nombre_depto'].dropna().unique())
    estados = sorted(df['estado_general'].dropna().unique())

    col1, col2 = st.columns(2)
    filtro_depto = col1.selectbox("Selecciona un Departamento", deptos)
    filtro_estado = col2.selectbox("Selecciona un Estado de Obra", estados)

    df_filtro = df[
        (df['nombre_depto'] == filtro_depto) &
        (df['estado_general'] == filtro_estado)
    ][['nombre_municipio', 'nombre_sede', 'aulas_nuevas', 'aulas_mejoradas', 'estado_general']]

    st.dataframe(df_filtro.reset_index(drop=True), use_container_width=True)



    st.markdown("---")
    st.subheader("🏙️ Comparativa de Aulas por Municipio (Top 10 con más inversión)")

    # Crear variable total de aulas
    df['total_aulas'] = df[['aulas_nuevas', 'aulas_mejoradas']].sum(axis=1)

    # Agrupar por municipio
    df_mun = df.groupby(['nombre_municipio', 'nombre_depto'])['total_aulas'].sum().reset_index()

    # Top 10 municipios
    top_mun = df_mun.sort_values(by='total_aulas', ascending=False).head(10)
    municipios_disp = top_mun['nombre_municipio'].tolist()

    selected_mun = st.multiselect("Selecciona municipios a comparar", municipios_disp, default=municipios_disp[:3])

    df_filtered = df[df['nombre_municipio'].isin(selected_mun)].copy()
    df_filtered['total_aulas'] = df_filtered[['aulas_nuevas', 'aulas_mejoradas']].sum(axis=1)

    # Contar cuántas sedes aportan al total por municipio
    df_grouped = df_filtered.groupby(['nombre_municipio', 'nombre_sede'])['total_aulas'].sum().reset_index()

    fig_municipios = px.line(
        df_grouped,
        x='nombre_sede',
        y='total_aulas',
        color='nombre_municipio',
        markers=True,
        title="Comparativa de Aulas por Municipio y Sede Educativa",
        height=600
    )
    fig_municipios.update_layout(
        xaxis_title="Sede Educativa",
        yaxis_title="Total de Aulas (Nuevas + Mejoradas)",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_municipios, use_container_width=True)

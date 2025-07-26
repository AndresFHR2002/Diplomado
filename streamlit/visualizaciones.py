import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import unidecode
 
def show_visualization_tab():
    st.header("📈 Visualizaciones por Departamento")
 
    if 'df_fact' not in st.session_state:
        st.warning("Primero debes construir la tabla de hechos en la pestaña 'Transformación y Métricas'.")
        return
 
    df_fact = st.session_state['df_fact']
    dim_geo = st.session_state['dim_geo']
    dim_tiempo = st.session_state['dim_tiempo']
 
    df = df_fact.merge(dim_geo, on='id_geo').merge(dim_tiempo, on='id_tiempo')
 
    # 🔴 Limpieza robusta del nombre del departamento
    df['departamento'] = (
        df['departamento']
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r'\.', '', regex=True)
        .apply(unidecode.unidecode)
    )
 
    df['departamento'] = df['departamento'].replace({
        'BOGOTA D.C.': 'Bogotá D.C.',
        'BOGOTA, D.C.': 'Bogotá D.C.',
        'ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA': 'San Andrés',
        'ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA': 'San Andrés'
    })
 
    # Asegurar tipo entero en año
    df['a_o'] = pd.to_numeric(df['a_o'], errors='coerce').astype('Int64')
 
    # ================================
    # PRIMER GRÁFICO
    # ================================
    st.subheader("📊 Serie de tiempo: Tasa de Matriculación vs Cobertura Neta")
 
    deptos = sorted(df['departamento'].dropna().unique())
    selected_depto_1 = st.selectbox("Selecciona un departamento (Gráfico 1)", deptos)
 
    df_1 = df[df['departamento'] == selected_depto_1]
    df_1 = df_1.groupby('a_o')[['tasa_matriculaci_n_5_16', 'cobertura_neta']].mean().reset_index()
 
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_1['a_o'],
        y=df_1['tasa_matriculaci_n_5_16'],
        name='Tasa de matriculación (5-16)',
        mode='lines+markers',
        yaxis='y1',
        line=dict(color='blue')
    ))
    fig1.add_trace(go.Scatter(
        x=df_1['a_o'],
        y=df_1['cobertura_neta'],
        name='Cobertura neta',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='orange')
    ))
    fig1.update_layout(
        title=f"Serie de tiempo - {selected_depto_1}",
        xaxis=dict(title='Año'),
        yaxis=dict(
            title=dict(text='Tasa de Matriculación (%)', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Cobertura Neta (%)', font=dict(color='orange')),
            tickfont=dict(color='orange'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig1, use_container_width=True)
 
    # ================================
    # SEGUNDO GRÁFICO
    # ================================
    st.subheader("📊 Serie de tiempo: Cobertura Bruta vs Otra Métrica")
 
    selected_depto_2 = st.selectbox("Selecciona un departamento (Gráfico 2)", deptos, index=deptos.index(selected_depto_1))
 
    df_2 = df[df['departamento'] == selected_depto_2]
    df_2 = df_2.groupby('a_o')[['cobertura_bruta']].mean().reset_index()
 
    if 'repitencia_secundaria' in df.columns:
        df_2['otra_metrica'] = df[df['departamento'] == selected_depto_2].groupby('a_o')['repitencia_secundaria'].mean().values
        nombre_metrica = 'Repitencia secundaria'
    else:
        df_2['otra_metrica'] = df[df['departamento'] == selected_depto_2].groupby('a_o')['tasa_matriculaci_n_5_16'].mean().values
        nombre_metrica = 'Tasa de Matriculación (5-16)'
 
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_2['a_o'],
        y=df_2['cobertura_bruta'],
        name='Cobertura Bruta',
        mode='lines+markers',
        yaxis='y1',
        line=dict(color='green')
    ))
    fig2.add_trace(go.Scatter(
        x=df_2['a_o'],
        y=df_2['otra_metrica'],
        name=nombre_metrica,
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='purple')
    ))
    fig2.update_layout(
        title=f"Cobertura Bruta vs {nombre_metrica} - {selected_depto_2}",
        xaxis=dict(title='Año'),
        yaxis=dict(
            title=dict(text='Cobertura Bruta (%)', font=dict(color='green')),
            tickfont=dict(color='green')
        ),
        yaxis2=dict(
            title=dict(text=nombre_metrica, font=dict(color='purple')),
            tickfont=dict(color='purple'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)


        # ================================
    # GRÁFICO 3: Boxplot de cobertura neta por departamento con filtro individual
    # ================================
    st.subheader("📊 Distribución de Cobertura Neta por Departamento")

    selected_depto_3 = st.selectbox("Selecciona un departamento (Gráfico 3)", deptos)

    df_3 = df[df['departamento'] == selected_depto_3]

    fig3 = px.box(df_3, x='departamento', y='cobertura_neta', points='all', color='departamento')
    fig3.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Cobertura Neta (%)",
        height=500
    )
    st.plotly_chart(fig3, use_container_width=True)


    # ================================
    # GRÁFICO 4: Ranking de cobertura neta promedio
    # ================================
    st.subheader("📊 Ranking: Cobertura Neta Promedio por Departamento")
    cobertura_prom = df.groupby('departamento')['cobertura_neta'].mean().reset_index()
    cobertura_prom = cobertura_prom.sort_values(by='cobertura_neta', ascending=False)
    fig5 = px.bar(
        cobertura_prom,
        x='departamento',
        y='cobertura_neta',
        color='cobertura_neta',
        color_continuous_scale='Oranges'
    )
    fig5.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Cobertura Neta Promedio (%)",
        height=500
    )
    st.plotly_chart(fig5, use_container_width=True)


      # Gráfico 5 - Violin plot
    st.subheader("\U0001F4CA Distribución tipo Violin: Tasa de Matriculación")
    selected = st.multiselect("Selecciona departamentos para comparar", deptos, default=deptos[:5])
    df_violin = df[df['departamento'].isin(selected)]
    fig4 = px.violin(df_violin, x='departamento', y='tasa_matriculaci_n_5_16', box=True, points='all')
    st.plotly_chart(fig4, use_container_width=True)


    # Gráfico 6 - Treemap: Proporción de matrícula total por departamento
    st.subheader("\U0001F4CA Treemap: Participación Total en Matrícula (5-16)")
    df_treemap = df.groupby('departamento')['tasa_matriculaci_n_5_16'].mean().reset_index()
    fig2 = px.treemap(df_treemap, path=['departamento'], values='tasa_matriculaci_n_5_16',
                      color='tasa_matriculaci_n_5_16', color_continuous_scale='RdBu')
    st.plotly_chart(fig2, use_container_width=True)

     # Gráfico 7 - Dispersión: Relación entre cobertura neta y población
    st.subheader("\U0001F4CA Dispersión: Cobertura Neta vs Población (5-16)")
    df_scatter = df.groupby('departamento')[['cobertura_neta', 'poblaci_n_5_16']].mean().reset_index()
    fig1 = px.scatter(
        df_scatter,
        x='poblaci_n_5_16',
        y='cobertura_neta',
        size='cobertura_neta',
        color='departamento',
        hover_name='departamento',
        size_max=40,
        title="Relación entre Cobertura Neta y Población Promedio (5-16)"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # ================================
    # GRÁFICO 8: Serie de tiempo animada por departamento
    # ================================
    st.subheader("📈 Evolución Anual: Tasa de Matriculación por Departamento")

    df_linea = df.groupby(['a_o', 'departamento'])['tasa_matriculaci_n_5_16'].mean().reset_index()

    fig_line = px.line(
        df_linea,
        x='a_o',
        y='tasa_matriculaci_n_5_16',
        color='departamento',
        markers=True,
        title='Tasa de Matriculación (5-16 años) por Departamento - Serie de Tiempo',
        height=600
    )
    fig_line.update_layout(
        xaxis_title="Año",
        yaxis_title="Tasa de Matriculación (%)"
    )
    st.plotly_chart(fig_line, use_container_width=True)


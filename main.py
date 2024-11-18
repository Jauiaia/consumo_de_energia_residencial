import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial
st.set_page_config(page_title="Analisador de Consumo de Energia", layout="wide")

st.title("Analisador de Consumo de Energia Residencial")
st.markdown("""
Carregue seu arquivo CSV para visualizar e analisar o consumo de energia ao longo do tempo. 
A análise inclui gráficos interativos e filtros para períodos específicos.
""")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])

if uploaded_file:
    # Leitura dos dados
    df = pd.read_csv(uploaded_file)
    
    # Conversão da coluna de data/hora
    df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
    df['Data'] = df['Data/Hora'].dt.date
    df['Hora'] = df['Data/Hora'].dt.hour

    # Exibição dos dados brutos
    st.subheader("Dados Carregados")
    st.dataframe(df)

    # Filtros de período
    st.sidebar.subheader("Filtros")
    start_date = st.sidebar.date_input("Data de Início", value=min(df['Data']))
    end_date = st.sidebar.date_input("Data de Fim", value=max(df['Data']))
    
    if start_date > end_date:
        st.error("A data de início não pode ser maior que a data de fim.")
    else:
        # Filtrar os dados
        filtered_df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]
        
        # Consumo diário total
        daily_consumption = filtered_df.groupby('Data').sum(numeric_only=True).reset_index()
        st.subheader("Gráfico: Consumo Total por Dia")
        bar_fig = px.bar(
            daily_consumption,
            x='Data',
            y='Consumo em kWh',
            title='Consumo Total por Dia',
            labels={'Consumo em kWh': 'Consumo (kWh)'},
            color='Consumo em kWh',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        # Consumo médio por hora
        hourly_consumption = filtered_df.groupby('Hora').mean(numeric_only=True).reset_index()
        st.subheader("Gráfico: Consumo Médio por Hora")
        line_fig = px.line(
            hourly_consumption,
            x='Hora',
            y='Consumo em kWh',
            title='Consumo Médio por Hora',
            labels={'Consumo em kWh': 'Consumo Médio (kWh)', 'Hora': 'Hora do Dia'}
        )
        st.plotly_chart(line_fig, use_container_width=True)

        # Distribuição percentual por categorias
        st.subheader("Gráfico: Distribuição Percentual")
        conditions = [
            (filtered_df['Hora'] >= 6) & (filtered_df['Hora'] < 18),
            (filtered_df['Hora'] >= 18) & (filtered_df['Hora'] < 23),
            (filtered_df['Hora'] >= 23) | (filtered_df['Hora'] < 6),
        ]
        categories = ['Pico', 'Noturno', 'Madrugada']
        filtered_df['Categoria'] = pd.cut(filtered_df['Hora'], bins=[-1, 5, 17, 22, 23], labels=['Madrugada', 'Pico', 'Noturno'], right=False)

        category_consumption = filtered_df.groupby('Categoria').sum(numeric_only=True).reset_index()
        pie_fig = px.pie(
            category_consumption,
            values='Consumo em kWh',
            names='Categoria',
            title='Distribuição Percentual do Consumo'
        )
        st.plotly_chart(pie_fig, use_container_width=True)

        # Resumo dos resultados
        st.sidebar.markdown("### Resumo")
        st.sidebar.write(f"*Consumo Total (kWh):* {filtered_df['Consumo em kWh'].sum():.2f}")
        st.sidebar.write(f"*Custo Total (R$):* {filtered_df['Custo Total'].sum():.2f}")

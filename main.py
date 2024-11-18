import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial
st.set_page_config(page_title="Analisador de Consumo de Energia", layout="wide")

st.title("Analisador de Consumo de Energia Residencial")
st.markdown("""
Este webapp permite que você analise seu consumo de energia residencial ao longo de um mês.
Carregue um arquivo CSV com os dados de consumo para começar!
""")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])

if uploaded_file:
    # Leitura do arquivo
    df = pd.read_csv(uploaded_file)

    # Normalização dos nomes das colunas
    df.columns = [col.strip().lower() for col in df.columns]  # Remove espaços e converte para minúsculas

    # Nomes esperados
    required_columns = ['data/hora', 'consumo em kwh', 'custo total']

    # Verificação de colunas
    if not all(col in df.columns for col in required_columns):
        st.error(f"O arquivo deve conter as colunas: {', '.join(required_columns)}. Colunas encontradas: {', '.join(df.columns)}")
    else:
        # Processamento de dados
        df['data/hora'] = pd.to_datetime(df['data/hora'], errors='coerce')
        df = df.dropna(subset=['data/hora'])  # Remove linhas inválidas
        df['data'] = df['data/hora'].dt.date
        df['hora'] = df['data/hora'].dt.hour

        # Exibição dos dados
        st.subheader("Dados Carregados")
        st.dataframe(df)

        # Filtro de período
        st.sidebar.header("Filtros de Período")
        start_date = st.sidebar.date_input("Data de Início", value=min(df['data']))
        end_date = st.sidebar.date_input("Data de Fim", value=max(df['data']))

        if start_date > end_date:
            st.error("A data de início não pode ser maior que a data de fim.")
        else:
            # Filtragem dos dados
            filtered_df = df[(df['data'] >= start_date) & (df['data'] <= end_date)]
            
            # Consumo total por dia
            daily_consumption = filtered_df.groupby('data').sum(numeric_only=True).reset_index()
            max_consumption_day = daily_consumption.loc[daily_consumption['consumo em kwh'].idxmax()]
            
            st.subheader("Gráfico: Consumo Total por Dia")
            bar_fig = px.bar(
                daily_consumption,
                x='data',
                y='consumo em kwh',
                title='Consumo Total por Dia',
                labels={'consumo em kwh': 'Consumo (kWh)'},
                color='consumo em kwh',
                color_continuous_scale='Viridis',
            )
            bar_fig.add_annotation(
                x=max_consumption_day['data'],
                y=max_consumption_day['consumo em kwh'],
                text="Maior Consumo",
                showarrow=True,
                arrowhead=3
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # Consumo médio por hora
            hourly_consumption = filtered_df.groupby('hora').mean(numeric_only=True).reset_index()
            st.subheader("Gráfico: Consumo Médio por Hora")
            line_fig = px.line(
                hourly_consumption,
                x='hora',
                y='consumo em kwh',
                title='Consumo Médio por Hora',
                labels={'consumo em kwh': 'Consumo Médio (kWh)', 'hora': 'Hora do Dia'},
            )
            st.plotly_chart(line_fig, use_container_width=True)

            # Distribuição percentual por categorias
            st.subheader("Gráfico: Distribuição Percentual")
            bins = [-1, 5, 17, 22, 24]
            labels = ['Madrugada', 'Pico', 'Noturno', 'Madrugada']
            filtered_df['categoria'] = pd.cut(
                filtered_df['hora'], bins=bins, labels=labels, right=False
            )
            category_consumption = filtered_df.groupby('categoria').sum(numeric_only=True).reset_index()
            pie_fig = px.pie(
                category_consumption,
                values='consumo em kwh',
                names='categoria',
                title='Distribuição Percentual do Consumo'
            )
            st.plotly_chart(pie_fig, use_container_width=True)

            # Comparação entre consumo médio e consumo diário no período filtrado
            st.subheader("Comparação de Consumo")
            overall_daily_avg = df.groupby('data')['consumo em kwh'].sum().mean()
            period_daily_avg = filtered_df.groupby('data')['consumo em kwh'].sum().mean()
            st.write(f"**Consumo Médio Diário Geral:** {overall_daily_avg:.2f} kWh")
            st.write(f"**Consumo Médio Diário no Período Filtrado:** {period_daily_avg:.2f} kWh")

            # Consumo total e custo total no período filtrado
            st.sidebar.header("Resumo do Período")
            st.sidebar.write(f"*Consumo Total (kWh):* {filtered_df['consumo em kwh'].sum():.2f}")
            st.sidebar.write(f"*Custo Total (R$):* {filtered_df['custo total'].sum():.2f}")

else:
    st.info("Por favor, carregue um arquivo CSV para começar.")

# Rodapé
st.markdown("""
---
*Desenvolvido por Iaia Jau | Analisador de Consumo de Energia Residencial*
""")

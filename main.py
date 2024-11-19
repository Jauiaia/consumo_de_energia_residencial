import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial da página
st.set_page_config(page_title="Analisador de Consumo de Energia", layout="wide")

# Título e descrição
st.title("Analisador de Consumo de Energia Residencial")
st.markdown("""
    Este webapp permite que você analise seu consumo de energia ao longo de um mês.
    Carregue um arquivo CSV com os dados de consumo para começar!
""")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])

# Exemplo de CSV para download
if not uploaded_file:
    st.info("Se não possui um arquivo CSV, clique abaixo para baixar um exemplo:")
    st.download_button(
        label="Baixar Exemplo de CSV",
        data="data/hora,consumo_kwh,custo_total\n2024-01-01 00:00,1.2,0.30\n2024-01-01 01:00,1.1,0.28\n2024-01-02 12:00,2.3,0.50",
        file_name="exemplo_consumo.csv",
        mime="text/csv"
    )

if uploaded_file:
    # Leitura do arquivo CSV
    df = pd.read_csv(uploaded_file)

    # Normalização dos nomes das colunas
    df.columns = [col.strip().lower() for col in df.columns]  # Remove espaços e converte para minúsculas
    required_columns = ['data/hora', 'consumo_kwh', 'custo_total']

    if not all(col in df.columns for col in required_columns):
        st.error(f"O arquivo deve conter as colunas: {', '.join(required_columns)}.")
    else:
        # Processamento de dados
        df['data/hora'] = pd.to_datetime(df['data/hora'], errors='coerce')
        df = df.dropna(subset=['data/hora'])  # Remove linhas inválidas
        df['data'] = df['data/hora'].dt.date
        df['hora'] = df['data/hora'].dt.hour

        # Filtros de período
        st.sidebar.header("Filtros de Período")
        start_date = st.sidebar.date_input("Data de Início", value=min(df['data']))
        end_date = st.sidebar.date_input("Data de Fim", value=max(df['data']))

        if start_date > end_date:
            st.error("A data de início não pode ser maior que a data de fim.")
        else:
            filtered_df = df[(df['data'] >= start_date) & (df['data'] <= end_date)]

            # Gráfico: Consumo total por dia
            st.subheader("Consumo Total por Dia")
            daily_consumption = filtered_df.groupby('data').sum(numeric_only=True).reset_index()
            max_consumption_day = daily_consumption.loc[daily_consumption['consumo_kwh'].idxmax()]
            bar_fig = px.bar(
                daily_consumption,
                x='data',
                y='consumo_kwh',
                title='Consumo Total por Dia',
                labels={'consumo_kwh': 'Consumo (kWh)', 'data': 'Data'},
                color='consumo_kwh',
                color_continuous_scale='Viridis',
            )
            bar_fig.add_annotation(
                x=max_consumption_day['data'],
                y=max_consumption_day['consumo_kwh'],
                text="Maior Consumo",
                showarrow=True,
                arrowhead=3
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # Gráfico: Consumo horário médio
            st.subheader("Consumo Médio por Hora")
            hourly_consumption = filtered_df.groupby('hora').mean(numeric_only=True).reset_index()
            line_fig = px.line(
                hourly_consumption,
                x='hora',
                y='consumo_kwh',
                title='Consumo Médio por Hora',
                labels={'consumo_kwh': 'Consumo Médio (kWh)', 'hora': 'Hora do Dia'},
            )
            st.plotly_chart(line_fig, use_container_width=True)

            # Gráfico: Distribuição percentual por categorias
            st.subheader("Distribuição Percentual do Consumo por Categorias")
            bins = [-1, 5, 17, 22, 24]
            labels = ['Madrugada', 'Dia', 'Pico', 'Noturno']
            filtered_df['categoria'] = pd.cut(
                filtered_df['hora'], bins=bins, labels=labels, right=False
            )
            category_consumption = filtered_df.groupby('categoria').sum(numeric_only=True).reset_index()
            pie_fig = px.pie(
                category_consumption,
                values='consumo_kwh',
                names='categoria',
                title='Distribuição Percentual do Consumo'
            )
            st.plotly_chart(pie_fig, use_container_width=True)

            # Comparação entre consumo médio geral e período filtrado
            st.subheader("Comparação de Consumo Diário")
            overall_daily_avg = df.groupby('data')['consumo_kwh'].sum().mean()
            period_daily_avg = filtered_df.groupby('data')['consumo_kwh'].sum().mean()
            st.write(f"**Consumo Médio Diário Geral:** {overall_daily_avg:.2f} kWh")
            st.write(f"**Consumo Médio Diário no Período Filtrado:** {period_daily_avg:.2f} kWh")

            # Consumo total e custo total no período filtrado
            st.sidebar.header("Resumo do Período")
            st.sidebar.write(f"*Consumo Total (kWh):* {filtered_df['consumo_kwh'].sum():.2f}")
            st.sidebar.write(f"*Custo Total (R$):* {filtered_df['custo_total'].sum():.2f}")

# Rodapé
st.markdown("""
---
*Desenvolvido por Iaia Jau | Analisador de Consumo de Energia Residencial*
""")

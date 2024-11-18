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
    try:
        # Leitura dos dados
        df = pd.read_csv(uploaded_file)

        # Validação de colunas essenciais
        required_columns = ['Data/Hora', 'Consumo em kWh', 'Custo Total']
        if not all(col in df.columns for col in required_columns):
            st.error(f"O arquivo deve conter as colunas: {', '.join(required_columns)}")
        else:
            # Conversão da coluna de data/hora
            df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], errors='coerce')
            df = df.dropna(subset=['Data/Hora'])  # Remove linhas com erros na conversão
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

                # Adicionar taxa de energia personalizada
                taxa = st.sidebar.number_input("Taxa por kWh (R$)", value=0.5, step=0.1)
                filtered_df['Custo Estimado'] = filtered_df['Consumo em kWh'] * taxa

                # Consumo diário total
                daily_consumption = filtered_df.groupby('Data').sum(numeric_only=True).reset_index()
                st.subheader("Gráfico: Consumo Total por Dia")
                theme = st.sidebar.selectbox("Escolha o tema do gráfico", ['Plotly', 'Seaborn', 'GGPlot2'])
                bar_fig = px.bar(
                    daily_consumption,
                    x='Data',
                    y='Consumo em kWh',
                    title='Consumo Total por Dia',
                    labels={'Consumo em kWh': 'Consumo (kWh)'},
                    color='Consumo em kWh',
                    color_continuous_scale='Viridis',
                    template=theme.lower()
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
                    labels={'Consumo em kWh': 'Consumo Médio (kWh)', 'Hora': 'Hora do Dia'},
                    template=theme.lower()
                )
                st.plotly_chart(line_fig, use_container_width=True)

                # Distribuição percentual por categorias
                st.subheader("Gráfico: Distribuição Percentual")
                bins = [-1, 5, 17, 22, 24]
                labels = ['Madrugada', 'Pico', 'Noturno', 'Madrugada']
                filtered_df['Categoria'] = pd.cut(
                    filtered_df['Hora'], bins=bins, labels=labels, right=False
                )
                category_consumption = filtered_df.groupby('Categoria').sum(numeric_only=True).reset_index()
                pie_fig = px.pie(
                    category_consumption,
                    values='Consumo em kWh',
                    names='Categoria',
                    title='Distribuição Percentual do Consumo',
                    template=theme.lower()
                )
                st.plotly_chart(pie_fig, use_container_width=True)

                # Estatísticas descritivas
                st.sidebar.markdown("### Estatísticas")
                total_consumo = filtered_df['Consumo em kWh'].sum()
                total_custo = filtered_df['Custo Estimado'].sum()
                st.sidebar.write(f"*Consumo Total (kWh):* {total_consumo:.2f}")
                st.sidebar.write(f"*Custo Estimado (R$):* {total_custo:.2f}")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé com o nome do site
st.markdown("""
---
*Desenvolvido por Iaia Jau | Consumo de Energia Residencial*
""")

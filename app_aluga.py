import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

# Configurar o layout da página como wide (tela cheia)
st.set_page_config(layout="wide")

# Carregar os dados
df = pd.read_csv("casas_para_aluguel.csv")


# Filtro lateral para cidades, incluindo a opção "Todas as Cidades"
cidade = st.sidebar.selectbox('Selecione a Cidade', ['Todas as Cidades'] + list(df['city'].unique()))

# Filtros laterais para número de quartos e valor de aluguel
quartos = st.sidebar.slider('Número de Quartos', int(df['rooms'].min()), int(df['rooms'].max()), (int(df['rooms'].min()), int(df['rooms'].max())))
valor_aluguel = st.sidebar.slider('Valor do Aluguel (R$)', int(df['rent amount (R$)'].min()), int(df['rent amount (R$)'].max()), 
                                  (int(df['rent amount (R$)'].min()), int(df['rent amount (R$)'].max())))

# Aplicar filtro de cidade (se não for "Todas as Cidades")
if cidade != 'Todas as Cidades':
    df_filtrado = df[(df['city'] == cidade)]
else:
    df_filtrado = df.copy()

# Aplicar outros filtros (número de quartos e valor do aluguel)
df_filtrado = df_filtrado[(df_filtrado['rooms'] >= quartos[0]) & (df_filtrado['rooms'] <= quartos[1]) &
                          (df_filtrado['rent amount (R$)'] >= valor_aluguel[0]) & (df_filtrado['rent amount (R$)'] <= valor_aluguel[1])]

# Filtro para aceitação de animais
animal_option = st.sidebar.selectbox('Aceita Animais?', ['Todos', 'Aceita', 'Não Aceita'])
if animal_option == 'Aceita':
    df = df[df['animal'] == 'acept']
elif animal_option == 'Não Aceita':
    df = df[df['animal'] == 'not acept']

# Criar coluna de valor do aluguel por metro quadrado
df_filtrado['aluguel_m2'] = df_filtrado['rent amount (R$)'] / df_filtrado['area']

# Layout em colunas (4 gráficos, um abaixo do outro)
# Gráfico 1: Distribuição do valor do aluguel (histograma)
st.subheader('Distribuição do Valor de Aluguel')
x_aluguel = df_filtrado['rent amount (R$)']

# Criar o histograma manualmente
hist_data_aluguel = np.histogram(x_aluguel, bins=30)
bin_edges_aluguel = hist_data_aluguel[1]
bin_counts_aluguel = hist_data_aluguel[0]

# Cores gradientes (Blues), invertidas para deixar as cores escuras para valores maiores
colors_aluguel = px.colors.sequential.Blues
color_gradient_aluguel = [colors_aluguel[int(i * (len(colors_aluguel) - 1) / (len(bin_edges_aluguel) - 1))] for i in range(len(bin_edges_aluguel) - 1)]
color_gradient_aluguel.reverse()  # Inverter para que os valores maiores tenham cores mais escuras

# Criar o histograma com cores gradientes
fig_aluguel = go.Figure(data=[go.Bar(
    x=(bin_edges_aluguel[:-1] + bin_edges_aluguel[1:]) / 2,  # Ponto central de cada bin
    y=bin_counts_aluguel,
    marker_color=color_gradient_aluguel,  # Aplicar o gradiente de cores
    marker_line_width=1.5,
    marker_line_color="black"
)])

fig_aluguel.update_layout(
    xaxis_title="Valor de Aluguel (R$)",
    yaxis_title="Frequência",
    bargap=0.1
)

st.plotly_chart(fig_aluguel, use_container_width=True)

# Gráfico 2: Aluguel Médio por Cidade (gráfico de barras horizontal)
st.subheader('Aluguel Médio por Cidade')
media_aluguel = df.groupby('city')['rent amount (R$)'].mean().reset_index()
fig_media_aluguel = px.bar(media_aluguel, y='city', x='rent amount (R$)', title="Aluguel Médio por Cidade",
                           orientation='h', color='city', color_discrete_sequence=px.colors.qualitative.Bold)
fig_media_aluguel.update_layout(xaxis_title='Aluguel Médio (R$)', yaxis_title='Cidade')
st.plotly_chart(fig_media_aluguel, use_container_width=True)

# Gráfico 3: Valor do aluguel por metro quadrado para cada cidade
st.subheader('Aluguel por Metro Quadrado por Cidade')
aluguel_m2_data = df_filtrado.groupby('city')['aluguel_m2'].mean().reset_index()
fig_aluguel_m2 = px.bar(aluguel_m2_data, x='city', y='aluguel_m2', title="Valor de Aluguel por Metro Quadrado por Cidade",
                        labels={'aluguel_m2': 'Valor de Aluguel por m² (R$)', 'city': 'Cidade'},
                        color='city', color_discrete_sequence=px.colors.qualitative.Bold)
fig_aluguel_m2.update_layout(xaxis_title='Cidade', yaxis_title='Valor de Aluguel por m² (R$)')
st.plotly_chart(fig_aluguel_m2, use_container_width=True)

# Gráfico 4: Gráfico de barras empilhadas para a distribuição de número de quartos (cores invertidas)
st.subheader('Distribuição do Número de Quartos')
quartos_data = df_filtrado['rooms'].value_counts().reset_index()
quartos_data.columns = ['rooms', 'count']

fig_quartos_barra = px.bar(quartos_data, x='rooms', y='count', title="Distribuição do Número de Quartos",
                           labels={'rooms': 'Número de Quartos', 'count': 'Quantidade'},
                           color='rooms', color_continuous_scale=px.colors.sequential.Greens_r, text='count')
fig_quartos_barra.update_layout(barmode='stack', xaxis_title='Número de Quartos', yaxis_title='Quantidade')
st.plotly_chart(fig_quartos_barra, use_container_width=True)

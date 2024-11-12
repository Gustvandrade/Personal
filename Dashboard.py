import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
import time 
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Configuração da página para layout "wide"
st.set_page_config(layout="wide")


# Define a estilização do plano de fundo e do conteúdo
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=FS+Industrie:wght@700&display=swap');

    /* Estilo para o fundo de tela */
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
        url("https://i.ibb.co/jTBWwG3/Sem-t-tulo.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        margin-top: -50px; /* Ajuste este valor se necessário */
}
}
    /* Remove padding e margem do Streamlit */
    .main .block-container {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* Estilo do cabeçalho */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0px 10px 10px 10px; /* Remove o espaçamento superior */
        background-color: #F9F9F9; /* Remove o fundo cinza */
        border-radius: 8px;
        color: #000000;
    }
    .header-left {
        display: flex;
        align-items: center;
    }
    .header-left img {
        width: 50px;
        height: 50px;
        margin-right: 15px;
    }
    .header-center {
        flex-grow: 1;
        text-align: center;
    }
    .header-center h1 {
        font-size: 30px;
        font-weight: bold;
        text-transform: uppercase;
        font-family: 'FS Industrie', sans-serif;
        color: black; /* Define o texto como branco */
    }
    .header-right img {
        width: 150px;
        height: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Conteúdo do cabeçalho da aplicação
st.markdown(
    """
    <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
        }
        .header-left img,
        .header-right img {
            width: 110px;  /* Define uma largura fixa para as imagens */
            height: auto;   /* Mantém a proporção da imagem */
        }
        .header-center {
            flex-grow: 1;
            text-align: center;
        }
    </style>
    <div class="header-container">
        <div class="header-left">
            <img src="https://www.straumann.com/content/dam/sites/group/xy/home/logos/Logo_Neodent.png" alt="Ícone">
        </div>
        <div class="header-center">
            <h1>Torre de Controle Logístico</h1>
        </div>
        <div class="header-right">
            <img src="https://www.elcedrobarcelona.com/wp-content/uploads/logo-straumann.png" alt="Logo">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



# Função para obter a conexão com o banco de dados
def get_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=supply-chain-prod.database.windows.net;'
            'DATABASE=logistics_bi;'
            'UID=logistics_bi_rw;'
            'PWD=Llt7J#4x(08'
        )
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao servidor SQL: {e}")
        return None

# PackID-----------------------------------------------------------------------------------------------------
# Função para obter os dados do banco de dados
def get_data_packid():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(), 0

    try:
        count_query = "SELECT COUNT(DISTINCT label2) AS distinct_count FROM dbo.TESTE01;"
        distinct_count_df = pd.read_sql_query(count_query, conn)
        distinct_count = distinct_count_df['distinct_count'].iloc[0]

        query = """
            SELECT 
                t1.label2 AS [Cód PackID], 
                t1.Local, 
                t1.Filial, 
                t1.alert_acima, 
                t1.alert_abaixo, 
                t1.[sum] AS [Tempo em Alerta], 
                t1.date_hour AS [Última Atualização]
            FROM dbo.TESTE01 t1
            INNER JOIN (
                SELECT label2, MAX(date_hour) AS MaxDateHour
                FROM dbo.TESTE01
                GROUP BY label2
            ) t2
            ON t1.label2 = t2.label2 AND t1.date_hour = t2.MaxDateHour
            WHERE t1.alert_geral = 1;
        """

        df = pd.read_sql_query(query, conn)
        return df, distinct_count
    finally:
        conn.close()

# Função para atribuir ícones com base em condições de tempo como string
def assign_icons(val):
    if pd.isnull(val):
        return ""
    
    if "00:00:00" < val < "00:10:00":
        return "🟨"
    elif "00:10:00" <= val < "00:20:00":
        return "🟧"
    elif val >= "00:20:00":
        return "🟥"
    else:
        return ""

# Função para exibir barra de porcentagem
def display_percentage_bar(df, distinct_count):
    if distinct_count == 0:
        st.warning("Nenhum dado disponível para calcular as porcentagens.")
        return

    count_yellow = df[df['Tempo em Alerta'] < "00:10:00"].shape[0]
    count_orange = df[(df['Tempo em Alerta'] >= "00:10:00") & 
                      (df['Tempo em Alerta'] < "00:20:00")].shape[0]
    count_red = df[df['Tempo em Alerta'] >= "00:20:00"].shape[0]

    total_count = count_yellow + count_orange + count_red
    count_green = distinct_count - total_count

    percentage_yellow = (count_yellow / distinct_count) * 100
    percentage_orange = (count_orange / distinct_count) * 100
    percentage_red = (count_red / distinct_count) * 100
    percentage_green = (count_green / distinct_count) * 100

    st.write("Situação Atual dos PackIDs:")
    bar_html = f"""
    <div style='width: 100%; background-color: #e0e0e0; border-radius: 5px;'>
        <div style='width: {percentage_green}%; background-color: #196B24; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_yellow}%; background-color: #FFC34A; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_orange}%; background-color: #F66443; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_red}%; background-color: #D83E66; height: 20px; border-radius: 5px; float: left;'></div>
    </div>
    """
    
    st.markdown(bar_html, unsafe_allow_html=True)
    st.write(
        "<div style='text-align: center;'>"
        f"<span style='color: #196B24;'><strong>Sensores Ok: {count_green}</strong></span> | "
        f"<span style='color: #FFC34A;'><strong>0 min a 10 min: {count_yellow}</strong></span> | "
        f"<span style='color: #F66443;'><strong>10 min a 20 min: {count_orange}</strong></span> | "
        f"<span style='color: #D83E66;'><strong>Acima de 20 min: {count_red}</strong></span>"
        "</div>",
        unsafe_allow_html=True
    )

# Função principal para exibir os dados do PackID
def main_packid():
    df_packid, distinct_count_packid = get_data_packid()

    if not df_packid.empty:
        df_packid['Cód PackID'] = df_packid['Cód PackID'].str.slice(0, 20)
        df_packid['Local'] = df_packid['Local'].str.slice(0, 20)
        df_packid['Filial'] = df_packid['Filial'].str.slice(0, 20)
        
        # Adiciona ícones diretamente à coluna `Tempo em Alerta`
        df_packid['Ícone Alerta'] = df_packid['Tempo em Alerta'].apply(assign_icons)
        
        # Combina `Tempo em Alerta` e `Ícone Alerta`
        df_packid['Tempo em Alerta'] = df_packid['Tempo em Alerta'] + " " + df_packid['Ícone Alerta']
        
        # Seleciona colunas para exibição
        df_packid = df_packid[['Cód PackID', 'Filial', 'Local', 'alert_acima', 'alert_abaixo', 'Tempo em Alerta', 'Última Atualização']]
        
        display_percentage_bar(df_packid, distinct_count_packid)
        
        # Ordenação pela coluna `Tempo em Alerta` usando string
        df_packid = df_packid.sort_values(by='Tempo em Alerta', ascending=False)
        
        st.dataframe(df_packid, use_container_width=True)
    else:
        st.write("Nenhum dado disponível para exibir.")


# APILocker-----------------------------------------------------------------------------------------------------
def get_data_apilocker():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    try:
        # Query SQL para buscar os dados da tabela APILocker
        query = """
        SELECT 
            Data,
            Filial,
            Conexao,
            Ocupacao,
            Validador
        FROM dbo.APILocker;
        """
        
        df_apilocker = pd.read_sql_query(query, conn)

        # Remover o símbolo de porcentagem e converter para float
        df_apilocker['Ocupacao'] = df_apilocker['Ocupacao'].str.replace('%', '').astype(float)

        return df_apilocker
    finally:
        conn.close()  # Fechando a conexão

def plot_apilocker_data(df_apilocker):
    # Mapeamento de códigos para nomes de filiais
    mapping = {
        'NEO_REC_FLR': 'Recife',
        'NEO_SAL_FLS': 'Salvador',
        'NEO_MT_TTC': 'Cuiabá',
        'NEO_JOI_ADB': 'Joinville',
        'NEO_RJ_EPB': 'Rio de Janeiro',
        'NEO_CWB_NEO': 'Curitiba',
        'NEO_BRA_FL1': 'Brasilia',
        'NEO_FLN_TOA': 'Florianópolis',
        'NEO_SP_HUB': 'São Paulo',
        'NEO_POA_FLP': 'Porto Alegre',
        'NEO_BHZ_MCA': 'Belo Horizonte',
        'NEO_GOI_FLG': 'Goiania'
    }
    
    # Substituir os valores na coluna 'Filial' usando o mapeamento
    df_apilocker['Filial'] = df_apilocker['Filial'].map(mapping)

    # Plotando o gráfico de barras para a porcentagem de ocupação por filial
    plt.figure(figsize=(10, 6))
    
    # Agrupando por Filial e obtendo a média de Ocupacao (caso haja mais de um registro por filial)
    df_grouped = df_apilocker.groupby('Filial', as_index=False)['Ocupacao'].mean()

    # Criando as barras
    bars = plt.bar(df_grouped['Filial'], df_grouped['Ocupacao'], color='skyblue')
    
    # Títulos (se desejado, pode remover o título)
    # plt.title('Porcentagem de Ocupação por Filial no APILocker')
    plt.ylabel('Porcentagem de Ocupação (%)')  # Removido o título do eixo Y
    plt.ylim(0, 100)  # Limitar o eixo Y para representar porcentagem (0 a 100)

    # Definindo os rótulos do eixo X como verticais
    plt.xticks(rotation=90)  # Alterado para rotação de 90 graus

    # Remover linhas de grade
    # plt.grid(axis='y')  # Esta linha foi removida

    # Adicionar valores nas barras com uma casa decimal, separando por vírgula e com sinal de porcentagem
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:,.1f}%", ha='center', va='bottom')

    st.pyplot(plt)


def main_apilocker():
    # Obtendo os dados do APILocker
    df_apilocker = get_data_apilocker()

    if not df_apilocker.empty:
        plot_apilocker_data(df_apilocker)
    else:
        st.write("Nenhum dado disponível para exibir.")

# TMA-----------------------------------------------------------------------------------------------------
# Função para atribuir ícones com base no valor de tempo para "Loja"
def assign_icons_loja(val):
    if pd.isnull(val):  # Verifica se o valor é None ou NaT
        return f"{val} "  # Retorna o valor sem ícone se for None ou NaT
    
    sum_value = pd.to_timedelta(val)
    
    if pd.Timedelta("00:00:00") <= sum_value < pd.Timedelta("00:07:00"):
        return f"{val} 🟩"  # Verde
    elif pd.Timedelta("00:07:00") <= sum_value < pd.Timedelta("00:10:00"):
        return f"{val} 🟨"  # Amarelo
    elif sum_value >= pd.Timedelta("00:10:00"):
        return f"{val} 🟥"  # Vermelho
    else:
        return f"{val} "  # Sem ícone para outros casos

# Função para atribuir ícones com base no valor de tempo para "Locker"
def assign_icons_locker(val):
    if pd.isnull(val):  # Verifica se o valor é None ou NaT
        return f"{val} "  # Retorna o valor sem ícone se for None ou NaT
    
    sum_value = pd.to_timedelta(val)
    
    if pd.Timedelta("00:00:00") <= sum_value < pd.Timedelta("00:09:00"): 
        return f"{val} 🟩"  # Verde
    elif pd.Timedelta("00:09:00") <= sum_value < pd.Timedelta("00:15:00"): 
        return f"{val} 🟨"  # Amarelo
    elif sum_value >= pd.Timedelta("00:15:00"): 
        return f"{val} 🟥"  # Vermelho
    else:
        return f"{val} "  # Sem ícone para outros casos

# Função para atribuir ícones com base na condição
def assign_icons_based_on_condition(row):
    if row['Condição'] == 'Loja':
        return assign_icons_loja(row['Tempo em Aberto'])  # Aplique a função correta para "Loja"
    elif row['Condição'] == 'Locker':
        return assign_icons_locker(row['Tempo em Aberto'])  # Aplique a função correta para "Locker"
    else:
        return row['Tempo em Aberto']  # Retorna o valor original se não for "Loja" ou "Locker"
    
filial_mapping = {
    '4400': 'Neodent',
    '4401': 'ClearCorerct',
    '4402': 'Bauru',
    '4403': 'Belo Horizonte',
    '4404': 'Porto Alegre',
    '4405': 'Rio de Janeiro',
    '4406': 'Goiania',
    '4407': 'Vitória',
    '4408': 'Recife',
    '4409': 'Fortaleza',
    '4410': 'Uberlândia',
    '4411': 'Campinas',
    '4412': 'Passo Fundo',
    '4413': 'São Paulo - Nações',
    '4414': 'Maringa',
    '4415': 'Salvador',
    '4416': 'Cuiabá',
    '4417': 'Florianopolis',
    '4418': 'Brasilia',
    '4420': 'Curitiba',
    '4421': 'Joinville',
    '4423': 'HUB São Paulo',
    '4424': 'Joinville',
    '4425': 'HUB Belo Horizonte'
}    

# Função para obter os dados do TMA
def get_data_TMA():
    conn = get_connection()  # Certifique-se de que esta função esteja definida
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    try:
        # Query SQL com DISTINCT para trazer apenas valores distintos da coluna "Delivery"
        query = """
        SELECT DISTINCT 
            Delivery,
            [Shipping Point/Receiving Point],
            [Shipping Conditions],
            [Document Number of the Reference Document],
            DateTime_Local,
            [Last Updated],
            TMA_Time
        FROM dbo.TC_TMA;
        """
        df_TMA = pd.read_sql_query(query, conn)

        # Renomeando as colunas conforme o mapeamento solicitado
        df_TMA = df_TMA.rename(columns={
            'Shipping Point/Receiving Point': 'Filial',
            'Shipping Conditions': 'Condição',
            'Document Number of the Reference Document': 'No Pedido',
            'Last Updated': 'Última Atualização',
            'TMA_Time': 'Tempo em Aberto',
            'DateTime_Local': 'Criação Delivery'
        })

        # Aplicando a lógica de substituição para a coluna "Condição"
        df_TMA['Condição'] = df_TMA['Condição'].replace({
            '1B': 'Locker',
            'BN': 'Loja',
            'BX': 'Loja'
        })


        # Substituindo os valores na coluna "Filial" usando o dicionário de mapeamento
        df_TMA['Filial'] = df_TMA['Filial'].replace(filial_mapping)


        # Atribuindo ícones com base na condição
        df_TMA['Tempo em Aberto'] = df_TMA.apply(assign_icons_based_on_condition, axis=1)

        return df_TMA
    finally:
        conn.close()  # Fechando a conexão

# Função para exibir a barra de porcentagens
def display_percentage_bar2(df):
    if df.empty:
        st.warning("Nenhum dado disponível para calcular as porcentagens.")
        return

    # Contagem de amarelos, vermelhos e verdes com base nos ícones presentes
    count_green = df[df['Tempo em Aberto'].str.contains("🟩")].shape[0]
    count_yellow = df[df['Tempo em Aberto'].str.contains("🟨")].shape[0]
    count_red = df[df['Tempo em Aberto'].str.contains("🟥")].shape[0]

    # Calcula as porcentagens para as três cores
    total_count = df.shape[0]
    percentage_green = (count_green / total_count) * 100 if total_count > 0 else 0
    percentage_yellow = (count_yellow / total_count) * 100 if total_count > 0 else 0
    percentage_red = (count_red / total_count) * 100 if total_count > 0 else 0

    # Exibe a barra de progresso com as três cores
    st.write("Situação Atual dos TMA:")
    bar_html2 = f"""
    <div style='width: 100%; background-color: #e0e0e0; border-radius: 5px;'>
        <div style='width: {percentage_green}%; background-color: #196B24; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_yellow}%; background-color: #FFC34A; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_red}%; background-color: #D83E66; height: 20px; border-radius: 5px; float: left;'></div>
    </div>
    """
    st.markdown(bar_html2, unsafe_allow_html=True)

    # Exibe a contagem para verde, amarelo e vermelho
    st.write(
        "<div style='text-align: center;'>"
        f"<span style='color: #196B24;'><strong>Delivery Ok: {count_green}</strong></span> | "
        f"<span style='color: #FFC34A;'><strong>Prazo Iminente: {count_yellow}</strong></span> | "
        f"<span style='color: #D83E66;'><strong>Prazo Vencido: {count_red}</strong></span>"
        "</div>",
        unsafe_allow_html=True
    )

def main_TMA():
    df_TMA = get_data_TMA()

    if not df_TMA.empty:
        display_percentage_bar2(df_TMA)
        #st.write("Acompanhamento TMA:")

        # Adicionando o filtro de Filial logo abaixo da barra de porcentagem
        selected_filial = st.selectbox("", options=['Filiais'] + sorted(df_TMA['Filial'].unique()))
        if selected_filial != 'Filiais':
            df_TMA = df_TMA[df_TMA['Filial'] == selected_filial]

        st.dataframe(df_TMA, use_container_width=True)
    else:
        st.write("Nenhum dado disponível para exibir.")

# Senior-----------------------------------------------------------------------------------------------------
# Função para exibir a barra de porcentagens baseada no Status
def display_percentage_bar_status(df):
    if df.empty:
        st.warning("Nenhum dado disponível para calcular as porcentagens.")
        return

    # Contagem de verdes, amarelos e vermelhos com base nos ícones presentes na coluna "Status"
    count_green = df[df['Status'].str.contains("🟩")].shape[0]
    count_yellow = df[df['Status'].str.contains("🟨")].shape[0]
    count_red = df[df['Status'].str.contains("🟥")].shape[0]

    # Calcula as porcentagens para as três cores
    total_count = df.shape[0]
    percentage_green = (count_green / total_count) * 100 if total_count > 0 else 0
    percentage_yellow = (count_yellow / total_count) * 100 if total_count > 0 else 0
    percentage_red = (count_red / total_count) * 100 if total_count > 0 else 0

    # Exibe a barra de progresso com as três cores
    st.write("Situação Atual das Entregas em Andamento:")
    bar_html = f"""
    <div style='width: 100%; background-color: #e0e0e0; border-radius: 5px;'>
        <div style='width: {percentage_green}%; background-color: #196B24; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_yellow}%; background-color: #FFC34A; height: 20px; border-radius: 5px; float: left;'></div>
        <div style='width: {percentage_red}%; background-color: #D83E66; height: 20px; border-radius: 5px; float: left;'></div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

    # Exibe a contagem para verde, amarelo e vermelho
    st.write(
        "<div style='text-align: center;'>"
        f"<span style='color: #196B24;'><strong>Entrega Dentro do Prazo: {count_green}</strong></span> | "
        f"<span style='color: #FFC34A;'><strong>Atrasado < 30min: {count_yellow}</strong></span> | "
        f"<span style='color: #D83E66;'><strong>Atrasado > 30min: {count_red}</strong></span>"
        "</div>",
        unsafe_allow_html=True
    )

def get_data_Senior():
    conn = get_connection()  
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    try:
        # Query SQL para selecionar dados específicos da tabela TC_SeniorAll
        query = """
        SELECT DISTINCT 
            nrCNPJFilial,
            cdRoteiro,
            dtInicio,
            dtPrevEntr,
            dsNrDocto,
            situacao,
            cdAtividade,
            Status
        FROM dbo.TC_SeniorAll;
        """
        
        df_Senior = pd.read_sql_query(query, conn)

        # Renomeando as colunas conforme o mapeamento necessário
        df_Senior = df_Senior.rename(columns={
            'nrCNPJFilial': 'Filial',
            'cdRoteiro': 'Roteiro',
            'dtInicio': 'Início',
            'dtExecucao': 'Data Execução',
            'cdAtividade': 'Motorista',
            'dtPrevEntr': 'Previsão',
            'dsDestinatario': 'Destinatário',
            'dsNrDocto': 'Delivery',
            'situacao': 'Situação',
            'dsOcorrencia': 'Ocorrência',
            'dsComplementoOcorr': 'Complemento Ocorrência',
            'dtRealizado': 'Data Realizada',
            'Status': 'Status',
            'cdAtividade': 'Motorista',
            'Status2': 'Status Detalhado'
        })

        df_Senior['Motorista'] = df_Senior['Motorista'].str.split().str[0]

        # Filtrando para mostrar apenas registros onde a Situação é "EM_ANDAMENTO"
        df_Senior = df_Senior.loc[df_Senior['Situação'] == 'EM_ANDAMENTO']

        # Aplicando a lógica para a coluna "Situação" com base na coluna "Status"
        df_Senior['Situação'] = np.where(df_Senior['Status'].str.startswith('-'), "No Prazo", "Fora do Prazo")

        # Convertendo a coluna "Previsão de entrega" para o formato dd/mm/yy hh:mm:ss
        df_Senior['Previsão'] = pd.to_datetime(df_Senior['Previsão']).dt.strftime('%d/%m/%y %H:%M:%S')

        # Função para atribuir ícones à coluna "Status"
        def assign_icons_status(val):
            if pd.isnull(val):  # Verifica se o valor é None ou NaT
                return f"{val} "  # Retorna o valor sem ícone se for None ou NaT
            
            # Converte o valor para timedelta
            try:
                sum_value = pd.to_timedelta(val)
            except Exception:
                return f"{val} "  # Retorna o valor original se a conversão falhar
            
            # Lógica para atribuição de ícones
            total_width = 15
            total_width2 = 15
            if str(val).startswith('-'):
                return f"{val} 🟩".rjust(total_width)  # Verde
            elif pd.Timedelta("00:00:00") < sum_value < pd.Timedelta("00:30:00"):
                return f"{val} 🟨".rjust(total_width2)  # Amarelo
            elif sum_value >= pd.Timedelta("00:30:00"):
                return f"{val} 🟥".rjust(total_width2)  # Vermelho
            else:
                return f"{val}".rjust(total_width)  # Sem ícone para outros casos

        # Função para ordenar a coluna Status corretamente (valores positivos antes de negativos)
        def sort_status_column(df):
            # Extraindo os valores de tempo e convertendo para timedelta
            df['Status_Timedelta'] = pd.to_timedelta(df['Status'].str.extract(r'([-\d:]+)')[0])

            # Ordenando primeiro pelos valores de timedelta (do maior para o menor), depois removendo a coluna auxiliar
            df = df.sort_values(by='Status_Timedelta', ascending=False).drop(columns='Status_Timedelta')

            return df

        # Chamando a função logo após atribuir os ícones
        df_Senior['Status'] = df_Senior['Status'].apply(assign_icons_status)
        df_Senior = sort_status_column(df_Senior)

        # Exibir a barra de porcentagens **antes** da tabela
        display_percentage_bar_status(df_Senior)

        # Adicionando o filtro de Filial logo abaixo da barra de porcentagem
        selected_filial = st.selectbox("", options=['Filiais'] + sorted(df_Senior['Filial'].unique()))
        if selected_filial != 'Filiais':
            df_Senior = df_Senior[df_Senior['Filial'] == selected_filial]

        # Reorganizando as colunas conforme a ordem desejada
        df_Senior = df_Senior[[ 
            'Filial', 
            'Roteiro', 
            'Motorista', 
            'Delivery', 
            'Início', 
            'Previsão', 
            'Situação', 
            'Status'
        ]]

        return df_Senior  # Retornando o DataFrame final
    finally:
        conn.close()  # Fechando a conexão

# ClearCorrect-----------------------------------------------------------------------------------------------------
# Função para obter os dados do Clear
def get_data_ClearCorrect():
    conn = get_connection()  
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    try:
        query = """
        SELECT DISTINCT 
            [J_1BNFDOC-DOCDAT],
            [ZZPONUM],
            [CTE],
            [time],
            [Refresh],
            [VBRK-VSBED],
            [J_1BNFLIN-WERKS]
        FROM dbo.TC_SD_BR_FAT_DIA;
        """
        df_Clear = pd.read_sql_query(query, conn)

        df_Clear = df_Clear.rename(columns={
            'J_1BNFDOC-DOCDAT': 'Data doc',
            'ZZPONUM': 'Caso',
            'CTE': 'Rastreio',
            'time': 'Hora',  # Nome alterado para 'Hora'
            'Refresh': 'Última atualização',
            'VBRK-VSBED': 'Condição de expedição',
            'J_1BNFLIN-WERKS': 'Planta'
        })
        return df_Clear
    finally:
        conn.close()  # Fechando a conexão

def get_data_ClearCorrect2():
    conn = get_connection()  
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    try:
        query = """
        SELECT DISTINCT 
            Document,
            Refresh
            FROM dbo.TC_VF04;
        """
        df_Clear2 = pd.read_sql_query(query, conn)

        df_Clear2 = df_Clear2.rename(columns={
            'Document': 'Delivery',
            'Refresh': 'Última atualização'
            })
        return df_Clear2
    finally:
        conn.close()  # Fechando a conexão


def display_clear_correct_chart(df_Clear, df_Clear2):
    """
    Displays a time series chart showing case counts, delivery counts, and target line per hour and day,
    filtered to show only the last 24 hours.
    """
    try:
        # Processar dados do df_Clear (casos)
        df_Clear['Data_Hora'] = pd.to_datetime(
            df_Clear['Data doc'].astype(str) + ' ' + df_Clear['Hora'].astype(str), 
            format='%d.%m.%Y %H:%M:%S'
        )
        df_Clear['Hora_Fecha'] = df_Clear['Data_Hora'].dt.floor('H')
        df_Clear['Data'] = df_Clear['Data_Hora'].dt.date

        # Processar dados do df_Clear2 (deliveries)
        df_Clear2['Data_Hora'] = pd.to_datetime(df_Clear2['Última atualização'])
        df_Clear2['Hora_Fecha'] = df_Clear2['Data_Hora'].dt.floor('H')
        df_Clear2['Data'] = df_Clear2['Data_Hora'].dt.date

        # Filtrar dados para exibir apenas as últimas 24 horas
        last_24_hours = pd.Timestamp.now() - timedelta(hours=27)  # Remover fuso horário
        df_Clear = df_Clear[df_Clear['Data_Hora'] >= last_24_hours]
        df_Clear2 = df_Clear2[df_Clear2['Data_Hora'] >= last_24_hours]

        # Contar casos e deliveries por hora
        df_count_casos = df_Clear.groupby(['Data', 'Hora_Fecha'])['Caso'].nunique().reset_index()
        df_count_casos['Data_Hora'] = pd.to_datetime(
            df_count_casos['Data'].astype(str) + ' ' + 
            df_count_casos['Hora_Fecha'].dt.hour.astype(str) + ':00:00'
        )

        df_count_deliveries = df_Clear2.groupby(['Data', 'Hora_Fecha'])['Delivery'].nunique().reset_index()
        df_count_deliveries['Data_Hora'] = pd.to_datetime(
            df_count_deliveries['Data'].astype(str) + ' ' + 
            df_count_deliveries['Hora_Fecha'].dt.hour.astype(str) + ':00:00'
        )

        # Verificar se há dados válidos
        if (df_count_casos['Data_Hora'].min() is pd.NaT or 
            df_count_casos['Data_Hora'].max() is pd.NaT or
            df_count_deliveries['Data_Hora'].min() is pd.NaT or 
            df_count_deliveries['Data_Hora'].max() is pd.NaT):
            st.write("Base atualizando")
            return

        # Obter intervalo de tempo correto para o eixo X
        min_date = max(df_count_casos['Data_Hora'].min(), last_24_hours)
        max_date = pd.Timestamp.now()

        # Criar figura com dois traces
        fig = go.Figure()

        # Adicionar linha para casos com rótulos de dados
        fig.add_trace(go.Scatter(
            x=df_count_casos['Data_Hora'],
            y=df_count_casos['Caso'],
            name='Casos Faturados',
            line=dict(color='blue'),
            mode='lines+text',
            text=df_count_casos['Caso'],
            textposition='top center',
            textfont=dict(size=14)
        ))

        # Adicionar linha para deliveries com rótulos de dados
        fig.add_trace(go.Scatter(
            x=df_count_deliveries['Data_Hora'],
            y=df_count_deliveries['Delivery'],
            name='Casos Pendentes',
            line=dict(color='red'),
            mode='lines+markers+text',
            text=df_count_deliveries['Delivery'],
            textposition='top center',
            textfont=dict(size=14)
        ))

        # Adicionar linha de target
        fig.add_trace(go.Scatter(
            x=[min_date, max_date],
            y=[12, 12],
            name='Target (12/hora)',
            line=dict(
                color='gray',
                dash='dash'
            )
        ))

        # Obter a data do dia atual e filtrar as divisões dos dias
        today = pd.to_datetime("today").normalize()  # A data de hoje à meia-noite

        # Adicionar marcadores de divisão de dias a partir das 00:00 do dia atual
        for date in pd.date_range(start=today, end=df_count_casos['Data_Hora'].max(), freq='D'):
            # Adicionar linha vertical para cada dia a partir das 00:00
            fig.add_vline(
                x=date,
                line_width=1,
                line_dash="dash",
                line_color="rgba(128, 128, 128, 0.5)"
            )
            
            # Adicionar anotação de data
            fig.add_annotation(
                x=date,
                yref="paper",
                y=1.05,
                text=date.strftime('%d/%m'),
                showarrow=False,
                font=dict(size=12)
            )

        # Determinar o intervalo de datas para o eixo X
        min_date = min(df_count_casos['Data_Hora'].min(),
                      df_count_deliveries['Data_Hora'].min())
        max_date = max(df_count_casos['Data_Hora'].max(),
                      df_count_deliveries['Data_Hora'].max())

        fig.update_layout(
            title="",
            yaxis_title='Quantidade Casos',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=pd.date_range(start=min_date, end=max_date, freq='H'),
                ticktext=[(x).strftime('%H - %d/%m') for x in pd.date_range(start=min_date, end=max_date, freq='H')],
                tickangle=45,
                tickfont=dict(size=12)
            ),
            margin=dict(t=100, r=20, b=100, l=50),
            height=500
        )

        # Forçar autoscale no eixo Y
        fig.update_yaxes(
            automargin=True,
            rangemode='tozero',  # Garante que o gráfico comece do zero se necessário
        )     

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao gerar o gráfico: {str(e)}")
        st.write("Por favor, verifique se os dados estão no formato correto.")


#Divisão da pág e exibição-----------------------------------------------------------------------------------------------------
# Função para criar um link com parâmetro para cada aba
def get_link_for_indicador(indicador):
    return f"?indicador={indicador}"

# Adicionando CSS para esconder a mensagem de aviso e remover o sublinhado dos links
st.markdown("""
    <style>
        .stAlert {
            display: none;
        }
        .css-1v0mbdj a {
            text-decoration: none;  /* Remove o sublinhado */
        }
    </style>
""", unsafe_allow_html=True)

# Função para atualizar o indicador no session_state
def set_indicador(indicador):
    st.session_state.indicador = indicador

# Função para carregar o conteúdo de acordo com o indicador
def display_indicators(indicador):
    if indicador == 'Tempo Médio de Atendimento':
        st.markdown("<h3 style='text-align: center; font-size: 24px;'>Tempo Médio de Atendimento</h3>", unsafe_allow_html=True)
        main_TMA()
    elif indicador == 'Entregas Motoboy':
        st.markdown("<h3 style='text-align: center; font-size: 24px;'>Entregas Motoboy</h3>", unsafe_allow_html=True)
        st.dataframe(get_data_Senior(), use_container_width=True)
    elif indicador == 'Faturamento ClearCorrect':
        st.markdown("<h3 style='text-align: center; font-size: 24px;'>Faturamento ClearCorrect</h3>", unsafe_allow_html=True)
        df_Clear = get_data_ClearCorrect()
        df_Clear2 = get_data_ClearCorrect2()
        display_clear_correct_chart(df_Clear, df_Clear2)
    elif indicador == 'Sensores de Temperatura':
        st.markdown("<h3 style='text-align: center; font-size: 24px;'>Sensores de Temperatura</h3>", unsafe_allow_html=True)
        main_packid()

# Função para pegar o parâmetro da URL
def get_indicador_from_url():
    params = st.experimental_get_query_params()  # Método para obter parâmetros da URL
    return params.get("indicador", [None])[0]

# Verificar se o indicador já está armazenado no session_state
if 'indicador' not in st.session_state:
    st.session_state.indicador = 'Tempo Médio de Atendimento'  # Valor padrão

# Atualiza o session_state com o valor do parâmetro de URL, se presente
indicador_url = get_indicador_from_url()
if indicador_url and indicador_url in ['Tempo Médio de Atendimento', 'Entregas Motoboy', 'Faturamento ClearCorrect', 'Sensores de Temperatura']:
    set_indicador(indicador_url)

# Criando as "abas" com links na sidebar
st.sidebar.markdown("### Selecione um indicador:")

# Links para cada aba com o parâmetro na URL (usando a tag <a> para links clicáveis)
st.sidebar.markdown(f'<a href="{get_link_for_indicador("Tempo Médio de Atendimento")}">Tempo Médio de Atendimento</a>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{get_link_for_indicador("Entregas Motoboy")}">Entregas Motoboy</a>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{get_link_for_indicador("Faturamento ClearCorrect")}">Faturamento ClearCorrect</a>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{get_link_for_indicador("Sensores de Temperatura")}">Sensores de Temperatura</a>', unsafe_allow_html=True)

# Exibindo o indicador baseado no session_state
display_indicators(st.session_state.indicador)

# Atualizando a página automaticamente a cada 20 segundos
st.markdown('<meta http-equiv="refresh" content="120">', unsafe_allow_html=True)
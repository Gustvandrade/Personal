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

# Função para processar e unir as tabelas
def process_and_merge_data():
    df1 = get_data_ClearCorrect()
    df2 = get_data_ClearCorrect2()

    # Convertendo as colunas de data e hora para o formato desejado
    df1['Data'] = pd.to_datetime(df1['Data doc'], format='%d.%m.%Y').dt.strftime('%d/%m')
    df1['Hora'] = pd.to_datetime(df1['Hora'], format='%H:%M:%S').dt.hour

    df2['Data'] = pd.to_datetime(df2['Última atualização'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%d/%m')
    df2['Hora'] = pd.to_datetime(df2['Última atualização'], format='%Y-%m-%d %H:%M:%S').dt.hour

    # Agrupando e contando as ocorrências distintas de "Caso" e "Delivery"
    df1_grouped = df1.groupby(['Data', 'Hora']).agg(Faturados=('Caso', 'nunique')).reset_index()
    df2_grouped = df2.groupby(['Data', 'Hora']).agg(Pendentes=('Delivery', 'nunique')).reset_index()

    # Criando um DataFrame com todas as combinações possíveis de "Data" e "Hora"
    all_times = pd.MultiIndex.from_product([df1['Data'].unique(), range(24)], names=['Data', 'Hora'])
    all_data = pd.DataFrame(index=all_times).reset_index()

    # Mesclando as duas tabelas com todas as combinações possíveis de Data e Hora
    merged_df = pd.merge(all_data, df1_grouped, on=['Data', 'Hora'], how='left')
    merged_df = pd.merge(merged_df, df2_grouped, on=['Data', 'Hora'], how='left')

    # Preenchendo valores ausentes com 0
    merged_df['Faturados'] = merged_df['Faturados'].fillna(0)
    merged_df['Pendentes'] = merged_df['Pendentes'].fillna(0)

    # Criando uma coluna "DataHora" combinando "Data" e "Hora" para garantir a ordenação
    merged_df['DataHora'] = pd.to_datetime(merged_df['Data'] + ' ' + merged_df['Hora'].astype(str) + 'h', format='%d/%m %Hh')

    # Filtrando para remover os horários futuros do dia atual
    now = datetime.now() - timedelta(hours=3)
    now_plus_one_hour = now + timedelta(hours=1)  # Adiciona uma hora à hora atual

    today_str = now.strftime('%d/%m')

    # Modifica a condição para considerar a hora acrescida de 1
    merged_df = merged_df[(merged_df['Data'] < today_str) | 
                        ((merged_df['Data'] == today_str) & (merged_df['Hora'] <= now_plus_one_hour.hour))]

    # Ordenando pela coluna "DataHora"
    merged_df = merged_df.sort_values('DataHora').reset_index(drop=True)

    # Ordenando pela coluna "DataHora"
    merged_df['DataHora'] = pd.to_datetime(merged_df['Data'] + ' ' + merged_df['Hora'].astype(str) + ':00', format='%d/%m %H:%M')
    merged_df = merged_df.sort_values('DataHora').reset_index(drop=True)

    return merged_df

# Função para exibir o gráfico no Streamlit
def display_graph():
    merged_df = process_and_merge_data()

    # Criando o gráfico de linhas com "Faturados" e "Pendentes"
    fig = px.line(merged_df,
                  x='DataHora',  # Eixo X contínuo com data e hora
                  y=['Faturados', 'Pendentes'],  # Definindo as linhas para "Faturados" e "Pendentes"
                  title="Pendentes e Faturados por Hora",
                  labels={'DataHora': 'Data e Hora', 'Pendentes': 'Pendentes', 'Faturados': 'Faturados'},
                  color_discrete_map={'Pendentes': '#DCDCDC', 'Faturados': '#90F8E4'})  # Definindo as cores das linhas

    # Adicionando rótulos para a linha "Faturados"
    fig.update_traces(
        selector=dict(name='Faturados'),  # Seleciona apenas a linha "Faturados"
        mode="lines+markers+text",  # Exibe as linhas, marcadores e texto
        text=merged_df['Faturados'],  # Passa os valores de "Faturados"
        textposition="top center",  # Posição do rótulo (em cima do ponto)
        texttemplate="%{text}",  # Mostra o valor de cada ponto
        textfont=dict(size=12, color="black")  # Define a fonte e cor do texto
    )

    # Adicionando rótulos para a linha "Pendentes" apenas quando o valor for maior que zero
    fig.update_traces(
        selector=dict(name='Pendentes'),  # Seleciona apenas a linha "Pendentes"
        mode="lines+markers+text",  # Exibe as linhas, marcadores e texto
        text=merged_df['Pendentes'].apply(lambda x: x if x > 0 else ""),  # Aplica a condição (só exibe o valor se maior que zero)
        textposition="top center",  # Posição do rótulo (em cima do ponto)
        texttemplate="%{text}",  # Mostra o valor de cada ponto
        textfont=dict(size=12, color="black")  # Define a fonte e cor do texto
    )

    # Adicionando a linha de target (12/hora) ao gráfico com legenda
    fig.add_traces(go.Scatter(
        x=merged_df['DataHora'],  # Pega todos os valores no eixo X
        y=[12] * len(merged_df),  # Repete o valor do target
        mode='lines',  # Apenas linhas
        line=dict(color='#F4B490', width=2, dash='dash'),  # Estilo da linha (vermelha e tracejada)
        name='Target (12/hora)'  # Nome que aparecerá na legenda
    ))
    
    # Atualizando o eixo X para exibir as horas no formato "08h", "09h", etc.
    fig.update_xaxes(
        tickformat="%Hh",  # Formato de hora (ex: 08h, 09h)
        tickmode="array",  # Agora usando "array" para definir os valores e os rótulos
        tickvals=merged_df['DataHora'],  # Usando os valores contínuos de "DataHora"
        ticktext=merged_df['DataHora'].dt.strftime('%Hh - %d/%m'),
        tickangle=90,  # Rotaciona os rótulos do eixo X em 90 graus
        
    )

    # Atualizando a posição da legenda para abaixo do eixo X
    fig.update_layout(
        legend=dict(
            orientation="h",  # Define a legenda horizontal
            yanchor="bottom",  # Ancla a legenda ao fundo
            y=-0.5,  # Coloca a legenda abaixo do gráfico (ajuste conforme necessário)
            xanchor="center",  # Alinha a legenda ao centro
            x=0.5,  # Define a posição da legenda no eixo X
            title=None  # Remove qualquer título da legenda, incluindo "Variable"
        )
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig)
   

# Função para exibir a tabela no Streamlit
def display_table():
    final_df = process_and_merge_data()
    
    # Exibindo a tabela no Streamlit
    st.title("Contagem de Pendentes e Faturados por Hora")
    st.dataframe(final_df)

# Função para identificar a última atualização para cada delivery
def identificar_ultima_atualizacao(df_Clear2):
    # Convertendo a coluna 'Última atualização' para datetime
    df_Clear2['Última atualização'] = pd.to_datetime(df_Clear2['Última atualização'])

    # Ordenar por Delivery e por Última atualização (mais recente primeiro)
    df_Clear2 = df_Clear2.sort_values(by=['Delivery', 'Última atualização'], ascending=[True, False])

    # Encontrar a última atualização para cada 'Delivery'
    ultima_atualizacao = df_Clear2.drop_duplicates(subset='Delivery', keep='first')

    return ultima_atualizacao

# Função para encontrar deliveries que atendem ao critério
def encontrar_deliveries_validas(df_Clear2, ultima_atualizacao):
    # Encontrar a última data e hora de atualização
    ultima_data_hora = ultima_atualizacao['Última atualização'].max()

    # Filtrando as deliveries da última atualização
    deliveries_ultima_atualizacao = df_Clear2[df_Clear2['Última atualização'] == ultima_data_hora]['Delivery'].unique()

    # Filtrando registros de dias anteriores (excluindo qualquer atualização do dia atual)
    registros_anteriores = df_Clear2[df_Clear2['Última atualização'].dt.date < ultima_data_hora.date()]

    # Encontrar deliveries presentes em dias anteriores
    deliveries_em_dias_anteriores = registros_anteriores['Delivery'].unique()

    # Interseção: deliveries presentes na última atualização **e** em dias anteriores
    deliveries_validas = set(deliveries_ultima_atualizacao).intersection(deliveries_em_dias_anteriores)

    # Retornar as deliveries válidas (não o tamanho, mas o conjunto de deliveries)
    return deliveries_validas

# Função para exibir o cartão com a lógica de cor
def display_metric_card(total_deliveries_distintas):
    # Garantir que total_deliveries_distintas seja um inteiro
    if isinstance(total_deliveries_distintas, int):
        # Definir a classe de cor com base no valor
        if total_deliveries_distintas > 0:
            color_class = 'positive'
        else:
            color_class = 'zero'

        # Exibindo o cartão com o estilo
        st.markdown(f"""
        <style>
            .metric-card {{
                background-color: #FDFDFD;
                padding: 05px 05px;
                border-radius: 1px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                width: 210px;
                text-align: center;
                font-family: Arial, sans-serif;
                margin-top: 5px; /* Ajuste para empurrar para cima */
            }}

            .metric-card .title {{
                font-size: 16px;
                color: #333;
                margin-bottom: 10px;
            }}

            .metric-card .value {{
                font-size: 32px;
                font-weight: normal;
            }}

            .metric-card .positive {{
                color: red;
            }}

            .metric-card .zero {{
                color: green;
            }}
        </style>
        <div class="metric-card">
            <div class="title">Casos Pendentes &gt; 24h</div>
            <div class="value {color_class}">{total_deliveries_distintas}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Erro: 'total_deliveries_distintas' não é um número inteiro.")

# Obter os dados
df_Clear2 = get_data_ClearCorrect2()

# Identificar a última atualização
ultima_atualizacao = identificar_ultima_atualizacao(df_Clear2)

# Encontrar as deliveries válidas
deliveries_validas = encontrar_deliveries_validas(df_Clear2, ultima_atualizacao)

# Verificar o número de deliveries válidas (tamanho do conjunto)
total_deliveries_distintas = len(deliveries_validas)  # Isso deve ser um número inteiro

# Criar o dataframe com as deliveries válidas para download
df_deliveries_validas = df_Clear2[df_Clear2['Delivery'].isin(deliveries_validas)]



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
        # Verificar se o DataFrame não está vazio
        if not df_Clear2.empty:
            # Identificar a última atualização para cada delivery
            ultima_atualizacao = identificar_ultima_atualizacao(df_Clear2)

            # Contar as deliveries válidas
            deliveries_validas = encontrar_deliveries_validas(df_Clear2, ultima_atualizacao)
            total_deliveries_distintas = len(deliveries_validas)
            
            # Exibir o cartão de contagem
            display_metric_card(total_deliveries_distintas)
        else:
            display_metric_card(0)
        
        st.markdown("<h3 style='text-align: center; font-size: 24px;'>Faturamento ClearCorrect</h3>", unsafe_allow_html=True) 

        display_graph()  # Exibe o gráfico

        # Botão de download para as deliveries válidas
        st.download_button(
            label="Download casos pendentes",
            data=df_deliveries_validas.to_csv(index=False).encode('utf-8'),
            file_name='deliveries_validas.csv',
            mime='text/csv'
        )

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


# Estilizando a largura da sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 300px; /* Define a largura desejada */
            min-width: 300px; /* Garante que a largura mínima seja respeitada */
        }
    </style>
""", unsafe_allow_html=True)

# Criando as "abas" com links na sidebar
st.sidebar.markdown("### Selecione um indicador:")

# Links com imagens ajustadas e efeito de destaque ao passar o mouse
st.sidebar.markdown("""
    <style>
        a {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #000000;
            margin: 16px 0;
            font-size: 14px;
            transition: all 0.3s ease; /* Suaviza o efeito de destaque */
        }

        a:hover {
            color: #000000; /* Cor azul ao passar o mouse */
            font-weight: bold; /* Deixa o texto em negrito */
        }

        img {
            width: auto;
            height: 20px;
            margin-right: 20px;
        }
    </style>
    <div style="text-align: left;">
        <a href='?indicador=Tempo Médio de Atendimento'>
            <img src='https://investidorpreguicoso.com.br/wp-content/uploads/2019/08/white-clock-icon-png-12.png' 
                 alt='Ícone Tempo Médio'>
            Tempo Médio de Atendimento
        </a>
        <a href='?indicador=Entregas Motoboy'>
            <img src='https://cdn-icons-png.flaticon.com/512/93/93381.png' 
                 alt='Ícone Motoboy'>
            Entregas Motoboy
        </a>
        <a href='?indicador=Faturamento ClearCorrect'>
            <img src='https://cdn-icons-png.flaticon.com/512/193/193508.png' 
                 alt='Ícone Faturamento'>
            Faturamento ClearCorrect
        </a>
        <a href='?indicador=Sensores de Temperatura'>
            <img src='https://cdn-icons-png.flaticon.com/512/3222/3222629.png' 
                 alt='Ícone Sensores'>
            Sensores de Temperatura
        </a>
    </div>
""", unsafe_allow_html=True)

# Exibindo o indicador baseado no session_state
display_indicators(st.session_state.indicador)

# Atualizando a página automaticamente a cada 20 segundos
st.markdown('<meta http-equiv="refresh" content="120">', unsafe_allow_html=True)
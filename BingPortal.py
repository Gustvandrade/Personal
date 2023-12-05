import requests
import pandas as pd
import os


# Get username PC
us = os.getlogin()
print(us)


# Leitura da planilha
dataframe1 = pd.read_excel(r'C:\Users\%s\Desktop\Distancia\CalculoDistancia.xlsx' % us, dtype=str)

# Função para calcular a distância terrestre
def calcular_distancia_terrestre(origem, destino, key):
    url = f"https://dev.virtualearth.net/REST/v1/Routes/Driving?wp.0={origem}&wp.1={destino}&key={key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data["resourceSets"][0]["estimatedTotal"] > 0:
        distancia = data["resourceSets"][0]["resources"][0]["travelDistance"]
        return distancia
    else:
        return None

# Solicitar que o usuário insira a chave API
API_KEY = input("Digite sua chave API do Bing Maps: ")

# Atualização da coluna "Distancia" na planilha
for index, row in dataframe1.iterrows():
    origem = row['Origem']
    destino = row['Destino']
    distancia = calcular_distancia_terrestre(origem, destino, API_KEY)
    
    # Verificar se a distância é None
    if distancia is None:
        print("Insira outra KEY.")
        
        # Pausa para o usuário ler a mensagem
        input("Pressione Enter para fechar o programa.")
        exit()

    # Atualiza a coluna "Distancia" na própria planilha
    dataframe1.at[index, 'Distancia'] = distancia

# Salvar o dataframe atualizado de volta no arquivo Excel
dataframe1.to_excel(r'C:\Users\%s\Desktop\Distancia\CalculoDistancia.xlsx' % us, index=False)
print("Distancias calculadas com sucesso")
input("Pressione Enter para fechar o programa.")
exit()
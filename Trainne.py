import requests
 
def calcular_distancia_terrestre(origem, destino, key):
    url = f"https://dev.virtualearth.net/REST/v1/Routes/Driving?wp.0={origem}&wp.1={destino}&key={key}"
    response = requests.get(url)
    data = response.json()
 
    if response.status_code == 200 and data["resourceSets"][0]["estimatedTotal"] > 0:
        distancia = data["resourceSets"][0]["resources"][0]["travelDistance"]
        return distancia
    else:
        return None
 
# Chave de API do Bing Maps
API_KEY = "AgVGRn5UuVi85_mFNI6w6WJToQ9Dw11NiE9GYBa-ovxQOME_6sFB9l8RE33EEqoR"
 
# Coordenadas de origem e destino
origem = "Curitiba"
destino = "São Paulo"
 
# Chamada da função para calcular a distância por via terrestre
distancia = calcular_distancia_terrestre(origem, destino, API_KEY)
print(distancia)
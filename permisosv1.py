import requests
import json

# Parámetros iniciales
BASE_URL = "https://developer.api.autodesk.com/bim360/docs/v1/projects"
ACCESS_TOKEN = "TU_ACCESS_TOKEN"  # Reemplaza con tu token válido
PROJECT_ID = "b.8cd48a5f-70e9-4cef-abbb-56c2b35f1f47"  # Reemplaza con tu ID de proyecto

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Función para obtener permisos de una carpeta
def fetch_permissions(project_id, folder_id):
    url = f"{BASE_URL}/{project_id}/folders/{folder_id}/permissions"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            else:
                print(f"Respuesta inesperada para permisos de {folder_id}: {data}")
                return None
        except json.JSONDecodeError:
            print(f"Error al decodificar la respuesta JSON para {folder_id}: {response.text}")
            return None
    elif response.status_code == 404:
        print(f"Error 404: Permisos no encontrados para {folder_id}.")
    else:
        print(f"Error {response.status_code}: {response.text} al obtener permisos de {folder_id}.")
    return None

# Ejemplo de ejecución para un folder ID específico
if __name__ == "__main__":
    folder_id = "urn:adsk.wipprod:fs.folder:co.uGXwLi2QTfaDaLKJWCFLaQ"
    permissions = fetch_permissions(PROJECT_ID, folder_id)
    
    if permissions:
        print(f"Permisos para {folder_id}:")
        print(json.dumps(permissions, indent=4, ensure_ascii=False))
    else:
        print(f"No se obtuvieron permisos para {folder_id}.")

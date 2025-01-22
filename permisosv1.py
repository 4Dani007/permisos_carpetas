import requests
import json
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración
BASE_URL = "https://developer.api.autodesk.com"

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("El ACCESS_TOKEN no se ha encontrado en el archivo .env")

PROJECT_ID = "b.ce995672-9fc3-417e-bc92-d1579b0c5e68"  # ID del proyecto
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

PERMISSIONS_OUTPUT_FILE = "folder_permissions.json"

def fetch_permissions(folder_urn):
    """
    Realiza la solicitud para obtener los permisos de una carpeta específica.
    """
    url = f"{BASE_URL}/bim360/docs/v1/projects/{PROJECT_ID}/folders/{folder_urn}/permissions"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener permisos de la carpeta {folder_urn}: {response.status_code} {response.text}")
        return {"error": f"HTTP {response.status_code}", "details": response.text}

def load_subfolders(file_path):
    """
    Carga los URN y nombres de las carpetas desde un archivo JSON.
    """
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

def save_permissions(data, file_path):
    """
    Guarda los permisos en un archivo JSON.
    """
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Permisos exportados a {file_path}")

if __name__ == "__main__":
    SUBFOLDERS_FILE = "subfolders.json"  # Archivo con los URN de las carpetas
    
    # Cargar URN de subcarpetas
    subfolders = load_subfolders(SUBFOLDERS_FILE)
    permissions_data = {}

    # Iterar sobre cada carpeta para obtener sus permisos
    print(f"Obteniendo permisos para {len(subfolders)} carpetas...")
    for folder_name, folder_info in subfolders.items():
        folder_urn = folder_info["urn"]
        folder_path = folder_info["path"]
        print(f"Procesando permisos de la carpeta: {folder_name} (URN: {folder_urn})")
        
        # Obtener permisos
        permissions = fetch_permissions(folder_urn)
        permissions_data[folder_name] = {
            "urn": folder_urn,
            "path": folder_path,
            "permissions": permissions,
        }

    # Guardar los permisos en un archivo JSON
    save_permissions(permissions_data, PERMISSIONS_OUTPUT_FILE)

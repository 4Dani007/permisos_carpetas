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

PROJECT_ID = "b.8cd48a5f-70e9-4cef-abbb-56c2b35f1f47"  # ID del proyecto
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_folder_contents(project_id, folder_id):
    """
    Obtiene el contenido de una carpeta específica.
    """
    url = f"{BASE_URL}/data/v1/projects/{project_id}/folders/{folder_id}/contents"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error al obtener contenido de la carpeta {folder_id}: {response.status_code} {response.text}")
        return []

def get_all_subfolders(project_id, folder_id, folder_path="Root"):
    """
    Obtiene todas las subcarpetas de manera recursiva y devuelve una lista.
    """
    all_folders = []
    print(f"Procesando carpeta: {folder_path} (URN: {folder_id})")

    # Obtener contenido de la carpeta actual
    folder_contents = fetch_folder_contents(project_id, folder_id)
    
    # Filtrar subcarpetas
    subfolders = [item for item in folder_contents if item["type"] == "folders"]
    
    for folder in subfolders:
        folder_name = folder["attributes"]["name"]
        folder_urn = folder["id"]
        folder_full_path = f"{folder_path}/{folder_name}"
        
        # Agregar la subcarpeta a la lista
        all_folders.append({"urn": folder_urn, "name": folder_name, "path": folder_full_path})
        
        # Recursivamente obtener subcarpetas de esta carpeta
        subfolder_contents = get_all_subfolders(project_id, folder_urn, folder_full_path)
        all_folders.extend(subfolder_contents)
    
    return all_folders

if __name__ == "__main__":
    ROOT_FOLDER_ID = "urn:adsk.wipprod:fs.folder:co.qDmF8Q_aR0CqcWHX_aELpg"  # URN de la carpeta raíz
    
    # Obtener todas las subcarpetas
    subfolders = get_all_subfolders(PROJECT_ID, ROOT_FOLDER_ID)
    
    # Mostrar resultado
    print(f"Total de subcarpetas encontradas: {len(subfolders)}")
    for folder in subfolders:
        print(f"Carpeta: {folder['path']} (URN: {folder['urn']})")

from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Cargar variables de entorno
load_dotenv()

# Configuración de Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS

# Configuración API de Autodesk
BASE_URL = "https://developer.api.autodesk.com"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PROJECT_ID = "b.ce995672-9fc3-417e-bc92-d1579b0c5e68"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_folder_contents(project_id, folder_id):
    """Obtiene el contenido de una carpeta específica."""
    url = f"{BASE_URL}/data/v1/projects/{project_id}/folders/{folder_id}/contents"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

def fetch_folder_permissions(project_id, folder_urn):
    """Obtiene los permisos de una carpeta específica."""
    url = f"{BASE_URL}/bim360/docs/v1/projects/{project_id}/folders/{folder_urn}/permissions"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return {"error": f"HTTP {response.status_code}", "details": response.text}

@app.route("/api/folders", methods=["GET"])
def get_folders():
    """Devuelve las carpetas raíz."""
    ROOT_FOLDER_ID = "urn:adsk.wipprod:fs.folder:co.QnFFSo5MTG67ciJr0UtSAw"
    folder_contents = fetch_folder_contents(PROJECT_ID, ROOT_FOLDER_ID)
    folders = [{"name": folder["attributes"]["name"], "urn": folder["id"]} for folder in folder_contents if folder["type"] == "folders"]
    return jsonify(folders)

@app.route("/api/subfolders", methods=["GET"])
def get_subfolders():
    """Devuelve las subcarpetas de una carpeta específica."""
    folder_urn = request.args.get("urn")
    if not folder_urn:
        return jsonify({"error": "No URN provided"}), 400
    subfolder_contents = fetch_folder_contents(PROJECT_ID, folder_urn)
    subfolders = [{"name": folder["attributes"]["name"], "urn": folder["id"]} for folder in subfolder_contents if folder["type"] == "folders"]
    return jsonify(subfolders)

@app.route("/api/permissions", methods=["GET"])
def get_permissions():
    """Devuelve los permisos de una carpeta específica."""
    folder_urn = request.args.get("urn")
    if not folder_urn:
        return jsonify({"error": "No URN provided"}), 400
    permissions = fetch_folder_permissions(PROJECT_ID, folder_urn)
    return jsonify(permissions)

if __name__ == "__main__":
    app.run(debug=True)

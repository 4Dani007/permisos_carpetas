from flask import Flask, redirect, request, session, url_for, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)

# Cargar las credenciales de Autodesk desde el archivo .env
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URL = "https://developer.api.autodesk.com/authentication/v2/authorize"
TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token"
SCOPES = "data:read account:read"
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
HUB_ID = os.getenv("HUB_ID")

@app.route('/')
def home():
    return '<a href="/login">Autenticar con Autodesk</a>'

@app.route('/login')
def login():
    auth_url = (
        f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No se recibió el código de autorización."
    
    token_response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
        },
    )
    
    token_data = token_response.json()
    session['access_token'] = token_data.get('access_token')
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))
    
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get("https://developer.api.autodesk.com/userprofile/v1/users/@me", headers=headers)
    
    return user_info.json()

@app.route('/projects', methods=['GET'])
def projects():
    """Obtiene todos los proyectos disponibles."""
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No hay un token de acceso. Inicia sesión."}), 401
    
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://developer.api.autodesk.com/construction/admin/v1/accounts/{ACCOUNT_ID}/projects"
    all_projects = []

    while url:
        response = requests.get(url, headers=headers)  # Usar headers locales
        if response.status_code != 200:
            return jsonify({"error": "No se pudieron obtener los proyectos"}), 500

        data = response.json()
        all_projects.extend(data.get("results", []))
        url = data.get("pagination", {}).get("nextUrl")

    return jsonify(all_projects)

@app.route('/project-folders', methods=['GET'])
def get_project_folders():
    """Obtiene las carpetas principales de un proyecto específico."""
    project_id = request.args.get('project_id')
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No hay un token de acceso. Inicia sesión."}), 401
    
    headers = {"Authorization": f"Bearer {access_token}"}

    if not project_id:
        return jsonify({"error": "Se requiere un project_id"}), 400

    hub_id = "b.dc461e11-029c-49b8-8a95-d76fee4928e8"
    url = f"https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects/b.{project_id}/topFolders"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "No se pudieron obtener las carpetas del proyecto"}), 500

    folders = response.json().get("data", [])
    project_folder = next(
        (folder for folder in folders if folder["attributes"]["name"].lower() in ["archivos de proyecto", "project files"]),
        None
    )

    return jsonify({"folder_id": project_folder["id"] if project_folder else None})

@app.route('/subfolders', methods=['GET'])
def get_subfolders():
    """Obtiene las subcarpetas de una carpeta específica."""
    folder_id = request.args.get('folder_id')
    project_id = request.args.get('project_id')
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No hay un token de acceso. Inicia sesión."}), 401
    
    headers = {"Authorization": f"Bearer {access_token}"}

    if not folder_id or not project_id:
        return jsonify({"error": "Se requieren folder_id y project_id"}), 400

    url = f"https://developer.api.autodesk.com/data/v1/projects/b.{project_id}/folders/{folder_id}/contents"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        folders = response.json().get("data", [])

        return jsonify([
            {"id": folder["id"], "name": folder["attributes"]["name"]}
            for folder in folders if folder["type"] == "folders"
        ])
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener subcarpetas: {e}")
        return jsonify({"error": "No se pudieron obtener las subcarpetas"}), 500

@app.route("/api/permissions", methods=["GET"])
def get_permissions():
    """Devuelve los permisos de una carpeta específica."""
    folder_urn = request.args.get("urn")
    project_id = request.args.get("project_id")
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No hay un token de acceso. Inicia sesión."}), 401
    
    headers = {"Authorization": f"Bearer {access_token}"}

    if not folder_urn or not project_id:
        return jsonify({"error": "Se requieren project_id y urn"}), 400

    url = f"https://developer.api.autodesk.com/bim360/docs/v1/projects/b.{project_id}/folders/{folder_urn}/permissions"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener permisos: {e}")
        return jsonify({"error": "No se pudieron obtener los permisos"}), 500


if __name__ == '__main__':
    app.run(debug=True)

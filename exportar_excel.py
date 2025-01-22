import json
import pandas as pd

def json_to_excel(json_file, excel_file):
    # Cargar datos del archivo JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Lista para almacenar filas
    rows = []
    
    # Iterar sobre cada carpeta
    for folder_name, folder_data in data.items():
        urn = folder_data.get("urn", "")
        path = folder_data.get("path", "")
        permissions = folder_data.get("permissions", [])
        
        # Iterar sobre cada permiso en la carpeta
        for permission in permissions:
            rows.append({
                "Folder Name": folder_name,
                "path": path,
                "URN": urn,
                "Subject Name": permission.get("name", ""),
                "Email": permission.get("email", ""),
                "User Type": permission.get("userType", ""),
                "Subject Status": permission.get("subjectStatus", ""),
                "Subject Type": permission.get("subjectType", ""),
                "Actions": ", ".join(permission.get("actions", [])),
                "Inherit Actions": ", ".join(permission.get("inheritActions", [])),
            })
    
    # Crear DataFrame
    df = pd.DataFrame(rows)
    
    # Exportar a Excel
    df.to_excel(excel_file, index=False, engine="openpyxl")
    print(f"Datos exportados exitosamente a {excel_file}")

# Uso del script
json_file = "folder_permissions.json"  # Nombre del archivo JSON
excel_file = "folder_permissions.xlsx"  # Nombre del archivo Excel

json_to_excel(json_file, excel_file)

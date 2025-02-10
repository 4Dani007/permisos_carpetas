import React, { useState, useEffect } from "react";
import { Select, Spin, Card, Table } from "antd";
import axios from "axios";

const FolderSelector = () => {
  const [folders, setFolders] = useState([]);
  const [subfolders, setSubfolders] = useState([]);
  const [permissions, setPermissions] = useState(null);
  const [loadingFolders, setLoadingFolders] = useState(true);
  const [loadingSubfolders, setLoadingSubfolders] = useState(false);
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState(null);

  useEffect(() => {
    // Obtener carpetas principales
    axios.get("http://localhost:5000/api/folders")
      .then(response => {
        setFolders(response.data);
        setLoadingFolders(false);
      })
      .catch(error => {
        console.error("Error al obtener carpetas", error);
        setLoadingFolders(false);
      });
  }, []);

  const handleFolderChange = (urn) => {
    setSelectedFolder(urn);
    setSubfolders([]); // Limpiar subcarpetas al cambiar de carpeta
    setPermissions(null); // Limpiar permisos
    setLoadingSubfolders(true);

    // Obtener subcarpetas
    axios.get(`http://localhost:5000/api/subfolders?urn=${urn}`)
      .then(response => {
        setSubfolders(response.data);
        setLoadingSubfolders(false);
      })
      .catch(error => {
        console.error("Error al obtener subcarpetas", error);
        setLoadingSubfolders(false);
      });

    // Obtener permisos de la carpeta seleccionada
    fetchPermissions(urn);
  };

  const fetchPermissions = (urn) => {
    setLoadingPermissions(true);
    axios.get(`http://localhost:5000/api/permissions?urn=${urn}`)
      .then(response => {
        setPermissions(response.data);
        setLoadingPermissions(false);
      })
      .catch(error => {
        console.error("Error al obtener permisos", error);
        setLoadingPermissions(false);
      });
  };

  const handleSubfolderChange = (urn) => {
    setPermissions(null); // Limpiar permisos al seleccionar nueva subcarpeta
    fetchPermissions(urn); // Obtener permisos de la subcarpeta seleccionada
  };

  // Formatear JSON
  const parsePermissionsToTableData = (permissions) => {
    if (!permissions) return { columns: [], data: [] };

    // Propiedades que se excluirán de la tabla
    const excludedProperties = ["autodeskId", "subjectId", "subjectStatus"];

    // Filtrar las columnas basándose en las claves del primer objeto, excluyendo las no deseadas
    const columns = Object.keys(permissions[0] || {})
      .filter(key => !excludedProperties.includes(key)) // Excluir propiedades no deseadas
      .map(key => ({
        title: key,
        dataIndex: key,
        key: key,
      }));

    // Filtrar los datos para excluir las propiedades no deseadas
    const data = permissions.map((perm, index) => {
      const filteredPerm = {};
      Object.keys(perm).forEach(key => {
        if (!excludedProperties.includes(key)) {
          filteredPerm[key] = perm[key];
        }
      });
      return {
        key: index,
        ...filteredPerm,
      };
    });

    return { columns, data };
  };

  const { columns, data } = parsePermissionsToTableData(permissions);

  return (
    <div className="p-4">
      <h2 className="text-xl mb-4">Selecciona una Carpeta</h2>
      {loadingFolders ? (
        <Spin size="large" />
      ) : (
        <Select
          className="w-full mb-4"
          placeholder="Seleccione una carpeta"
          onChange={handleFolderChange}
          options={folders.map(folder => ({ value: folder.urn, label: folder.name }))}
        />
      )}

      {selectedFolder && (
        <>
          <h3 className="text-lg mb-2">Selecciona una Subcarpeta</h3>
          {loadingSubfolders ? (
            <Spin size="large" />
          ) : (
            <Select
              className="w-full mb-4"
              placeholder="Seleccione una subcarpeta"
              onChange={handleSubfolderChange}
              options={subfolders.map(subfolder => ({ value: subfolder.urn, label: subfolder.name }))}
            />
          )}
        </>
      )}

      {loadingPermissions ? (
        <Spin size="large" />
      ) : permissions && (
        <Card title="Permisos" className="mt-4">
          <Table
            columns={columns}
            dataSource={data}
            pagination={false}
            bordered
          />
        </Card>
      )}
    </div>
  );
};

export default FolderSelector;